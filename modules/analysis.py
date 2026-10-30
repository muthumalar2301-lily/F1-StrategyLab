import pandas as pd
import numpy as np


def driver_performance(laps: pd.DataFrame) -> pd.DataFrame:
    """
    Computes aggregated driver metrics: total valid laps, mean lap duration,
    and fastest single lap recorded.
    """
    clean = laps.copy()
    clean["lap_duration"] = pd.to_numeric(clean["lap_duration"], errors="coerce")
    clean = clean[clean["lap_duration"] > 0]

    # Exclude severe outliers (e.g. red flags or pit in-laps) for reliable average pace
    q_high = clean["lap_duration"].quantile(0.90)
    clean_pace = clean[clean["lap_duration"] <= q_high]

    result = clean.groupby(
        ["driver_number", "full_name", "team_name"]
    ).agg(
        total_laps=("lap_number", "count"),
        fastest_lap=("lap_duration", "min")
    ).reset_index()

    # Calculate mean on representative laps
    avg_times = clean_pace.groupby("driver_number")["lap_duration"].mean().reset_index(name="average_lap_time")
    result = result.merge(avg_times, on="driver_number", how="left")

    return result.sort_values("average_lap_time")


def tyre_analysis(stints: pd.DataFrame) -> pd.DataFrame:
    """
    Analyzes tyre compound usage across stints and calculates true average stint lengths.
    Avoids deprecated pandas groupby.apply syntax.
    """
    stints_clean = stints.copy()
    stints_clean["compound"] = stints_clean["compound"].astype(str).str.upper()
    stints_clean["stint_length"] = stints_clean["lap_end"] - stints_clean["lap_start"] + 1

    result = stints_clean.groupby("compound").agg(
        total_stints=("stint_number", "count"),
        average_stint_length=("stint_length", "mean"),
        total_drivers=("driver_number", "nunique")
    ).reset_index()

    result["average_stint_length"] = result["average_stint_length"].round(1)
    return result


def pitstop_analysis(pitstops: pd.DataFrame) -> pd.DataFrame:
    """
    Evaluates pit stop execution per driver, isolating pit lane durations.
    """
    clean = pitstops.copy()
    clean["pit_duration"] = pd.to_numeric(clean["pit_duration"], errors="coerce")
    clean = clean.dropna(subset=["pit_duration"])

    result = clean.groupby("driver_number").agg(
        total_pitstops=("lap_number", "count"),
        average_pit_duration=("pit_duration", "mean"),
        fastest_pitstop=("pit_duration", "min")
    ).reset_index()

    result["average_pit_duration"] = result["average_pit_duration"].round(2)
    result["fastest_pitstop"] = result["fastest_pitstop"].round(2)

    return result.sort_values("total_pitstops", ascending=False)


def strategy_comparison(stints: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes stint structure and compound variety per driver.
    """
    result = stints.groupby("driver_number").agg(
        total_stints=("stint_number", "count"),
        total_race_laps=("lap_end", "max"),
        compounds_used=("compound", "nunique")
    ).reset_index()

    return result.sort_values("total_stints", ascending=False)


def calculate_tyre_degradation(laps: pd.DataFrame, stints: pd.DataFrame) -> pd.DataFrame:
    """
    Merges lap telemetry with active stint records and calculates exact tyre age.
    Filters non-representative running (Safety Cars, in/out laps) using quantile boundaries.
    """
    data = laps.merge(
        stints[
            [
                "driver_number",
                "stint_number",
                "compound",
                "lap_start",
                "lap_end",
                "tyre_age_at_start"
            ]
        ],
        on="driver_number",
        how="inner"
    )

    data = data[
        (data["lap_number"] >= data["lap_start"]) &
        (data["lap_number"] <= data["lap_end"])
    ].copy()

    data["lap_duration"] = pd.to_numeric(data["lap_duration"], errors="coerce")
    data["tyre_age_at_start"] = pd.to_numeric(data["tyre_age_at_start"], errors="coerce").fillna(0)

    # Tyre age represents cumulative laps driven on this rubber set
    data["tyre_age"] = (
        data["tyre_age_at_start"] +
        data["lap_number"] -
        data["lap_start"] + 1
    )

    data = data.dropna(subset=["lap_duration", "tyre_age"])

    # Strict representative lap filtering (5th to 85th percentile per race)
    q_low = data["lap_duration"].quantile(0.05)
    q_high = data["lap_duration"].quantile(0.85)
    data = data[data["lap_duration"].between(q_low, q_high)].copy()

    return data


def fit_fuel_corrected_degradation(
    laps: pd.DataFrame, 
    stints: pd.DataFrame, 
    fuel_penalty_per_lap: float = 0.035
):
    """
    Normalizes lap times against race fuel burnoff (~1.6kg / 0.035s per lap)
    and fits linear regression:
        Fuel_Adjusted_Time = Base_Pace + (Deg_Slope * Tyre_Age)

    Returns:
        points_df (pd.DataFrame): Telemetry scatter points with fuel_adjusted_time.
        models_df (pd.DataFrame): Fitted regression outputs per compound.
    """
    clean_data = calculate_tyre_degradation(laps, stints)
    if clean_data.empty:
        return pd.DataFrame(), pd.DataFrame()

    total_race_laps = clean_data["lap_number"].max()

    # Normalization: late-race laps carry less fuel, so we add back the weight advantage
    clean_data["fuel_adjusted_time"] = (
        clean_data["lap_duration"] +
        (total_race_laps - clean_data["lap_number"]) * fuel_penalty_per_lap
    )
    clean_data["compound"] = clean_data["compound"].astype(str).str.upper()

    models = []
    for compound, group in clean_data.groupby("compound"):
        # Ensure sufficient sample size and age progression for a stable regression
        if len(group) >= 10 and group["tyre_age"].nunique() >= 4:
            # Linear fit: y = mx + c
            slope, intercept = np.polyfit(group["tyre_age"], group["fuel_adjusted_time"], 1)
            
            # Compute R^2 goodness of fit
            fitted_vals = intercept + slope * group["tyre_age"]
            ss_tot = np.sum((group["fuel_adjusted_time"] - group["fuel_adjusted_time"].mean()) ** 2)
            ss_res = np.sum((group["fuel_adjusted_time"] - fitted_vals) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

            models.append({
                "compound": compound,
                "base_pace": intercept,
                "deg_per_lap": slope,
                "r_squared": round(r_squared, 3),
                "sample_count": len(group)
            })

    models_df = pd.DataFrame(models)
    return clean_data, models_df


def compare_driver_strategies(stints: pd.DataFrame, drivers: pd.DataFrame) -> pd.DataFrame:
    """
    Merges driver metadata with stint counts and tyre compounds used.
    """
    strategy = stints.groupby("driver_number").agg(
        total_stints=("stint_number", "count"),
        total_race_laps=("lap_end", "max"),
        compounds_used=("compound", "nunique")
    ).reset_index()

    strategy = strategy.merge(
        drivers[
            ["driver_number", "full_name", "team_name"]
        ].drop_duplicates("driver_number"),
        on="driver_number",
        how="left"
    )

    return strategy.sort_values("total_stints", ascending=False)


def analyze_pitstop_timing(pitstops: pd.DataFrame, drivers: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts chronological pit-lane stops and formats team/driver associations.
    """
    result = pitstops.merge(
        drivers[
            ["driver_number", "full_name", "team_name"]
        ].drop_duplicates("driver_number"),
        on="driver_number",
        how="left"
    )

    result["pit_duration"] = pd.to_numeric(result["pit_duration"], errors="coerce")
    result["lap_number"] = pd.to_numeric(result["lap_number"], errors="coerce")

    return result.dropna(subset=["pit_duration", "lap_number"]).sort_values("lap_number")