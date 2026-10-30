import pandas as pd
import numpy as np

def generate_recommendations(laps, stints, pitstops, drivers, weather=None):
    """
    Rule-based strategy intelligence engine calculating:
    - Intermediate to Slick crossover points
    - Compound degradation cliffs (fuel-normalized)
    - Recommended pit windows and stationary loss benchmarks
    """
    insights = []

    # Merge lap and stint metadata
    df = laps.merge(
        stints[["driver_number", "stint_number", "compound", "lap_start", "lap_end"]],
        on="driver_number",
        how="inner"
    )
    df = df[(df["lap_number"] >= df["lap_start"]) & (df["lap_number"] <= df["lap_end"])].copy()
    df["lap_duration"] = pd.to_numeric(df["lap_duration"], errors="coerce")
    
    # Exclude outliers (pit laps, safety car neutralizations)
    q_low = df["lap_duration"].quantile(0.05)
    q_high = df["lap_duration"].quantile(0.85)
    clean_df = df[df["lap_duration"].between(q_low, q_high)].copy()

    if clean_df.empty:
        return ["⚠️ Insufficient clean lap records available to extract strategic conclusions."]

    total_race_laps = int(clean_df["lap_number"].max())

    # Apply 0.035s / lap fuel correction to isolate pure tyre grip loss
    clean_df["fuel_adjusted_time"] = (
        clean_df["lap_duration"] + (total_race_laps - clean_df["lap_number"]) * 0.035
    )
    clean_df["compound_upper"] = clean_df["compound"].astype(str).str.upper()

    # ----------------------------------------------------
    # 1. Crossover Point Analysis (Inters vs. Slicks)
    # ----------------------------------------------------
    inters = clean_df[clean_df["compound_upper"].str.contains("INTERMEDIATE|WET")]
    slicks = clean_df[clean_df["compound_upper"].str.contains("SOFT|MEDIUM|HARD")]

    if not inters.empty and not slicks.empty:
        lap_pace = clean_df.groupby(["lap_number", "compound_upper"])["lap_duration"].median().unstack()

        crossover_laps = []
        for lap in lap_pace.index:
            inter_time = None
            slick_times = []
            for col in lap_pace.columns:
                if "INTERMEDIATE" in col and pd.notna(lap_pace.loc[lap, col]):
                    inter_time = lap_pace.loc[lap, col]
                elif any(c in col for c in ["SOFT", "MEDIUM", "HARD"]) and pd.notna(lap_pace.loc[lap, col]):
                    slick_times.append(lap_pace.loc[lap, col])

            if inter_time and slick_times:
                min_slick = min(slick_times)
                # Dry tyre pace matches or overtakes intermediate pace
                if min_slick <= inter_time:
                    crossover_laps.append((lap, min_slick, inter_time))

        if crossover_laps:
            first_crossover = crossover_laps[0]
            insights.append(
                f"🌧️ ➡️ ☀️ **Slick Crossover Lap Detected (Lap {int(first_crossover[0])}):** "
                f"Dry slick pace matched/exceeded intermediate pace (~{first_crossover[1]:.2f}s vs {first_crossover[2]:.2f}s). "
                f"Drivers boxing on or immediately after Lap {int(first_crossover[0])} gained immediate phase advantage."
            )
        else:
            avg_inter = inters["lap_duration"].median()
            avg_slick = slicks["lap_duration"].median()
            insights.append(
                f"⏱️ **Compound Delta:** Median intermediate pace was {avg_inter:.2f}s compared to "
                f"{avg_slick:.2f}s on dry slicks (Net Delta: {abs(avg_slick - avg_inter):.2f}s)."
            )

    # ----------------------------------------------------
    # 2. Fuel-Corrected Degradation Cliff Detection
    # ----------------------------------------------------
    clean_df["tyre_age"] = clean_df["lap_number"] - clean_df["lap_start"] + 1

    deg_thresholds = []
    for compound, group in clean_df.groupby("compound_upper"):
        if len(group) < 15:
            continue
        age_pace = group.groupby("tyre_age")["fuel_adjusted_time"].median()
        if len(age_pace) >= 7:
            base_pace = age_pace.iloc[:3].mean()
            # A degradation cliff occurs when normalized pace falls off by > 1.20s
            cliff = age_pace[age_pace > (base_pace + 1.20)]
            if not cliff.empty:
                cliff_age = cliff.index[0]
                deg_thresholds.append((compound, cliff_age, base_pace))

    if deg_thresholds:
        for compound, cliff_age, base_pace in deg_thresholds:
            insights.append(
                f"⚠️ **{compound} Degradation Cliff:** Noticeable thermal/wear drop-off (+1.20s) observed at "
                f"**Lap {int(cliff_age)}** of tyre life. Recommended maximum tactical stint length: **{int(cliff_age - 2)} laps**."
            )
    else:
        insights.append(
            "📊 **Tyre Wear Profile:** Consistent wear slopes detected without sudden thermal cliffs under prevailing track temperatures."
        )

    # ----------------------------------------------------
    # 3. Pit Stop Efficiency & Loss Benchmark
    # ----------------------------------------------------
    if not pitstops.empty:
        valid_pits = pitstops.copy()
        valid_pits["pit_duration"] = pd.to_numeric(valid_pits["pit_duration"], errors="coerce")
        valid_pits = valid_pits.dropna(subset=["pit_duration"])

        # Exclude extended stops (e.g. wing changes, double stacks)
        pit_median = valid_pits["pit_duration"].median()
        standard_pits = valid_pits[valid_pits["pit_duration"] <= pit_median * 1.4]

        bench_loss = standard_pits["pit_duration"].mean() if not standard_pits.empty else pit_median
        insights.append(
            f"🛠️ **Silverstone Pit Lane Loss Benchmark:** Total in-lane time averaged **{bench_loss:.2f} seconds**. "
            f"Any tactical undercut must yield a fresh-tyre cumulative delta exceeding {bench_loss:.2f}s to defend track position."
        )

    return insights