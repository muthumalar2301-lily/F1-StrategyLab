import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from modules.recommendation import generate_recommendations
from modules.analysis import (
    driver_performance,
    tyre_analysis,
    pitstop_analysis,
    strategy_comparison,
    calculate_tyre_degradation,
    fit_fuel_corrected_degradation,
    compare_driver_strategies,
    analyze_pitstop_timing
)

st.set_page_config(
    page_title="F1 StrategyLab | Telemetry & Intelligence",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)


COMPOUND_COLORS = {
    "SOFT": "#FF1801",
    "MEDIUM": "#FFD12E",
    "HARD": "#FFFFFF",
    "INTERMEDIATE": "#39B54A",
    "WET": "#00AEEF"
}

def format_laptime(seconds):
    if pd.isna(seconds) or seconds <= 0:
        return "-"
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins}:{secs:06.3f}"


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Titillium Web', -apple-system, BlinkMacSystemFont, sans-serif;
}

.stApp {
    background-color: #0c0d12;
    color: #e2e4ea;
}

/* Metric Card Containers */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, #161821 0%, #111218 100%);
    padding: 16px 20px;
    border-radius: 10px;
    border: 1px solid #232634;
    border-left: 4px solid #e10600;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}

[data-testid="stMetricLabel"] p {
    color: #8c90a2 !important;
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    font-weight: 700;
}

[data-testid="stMetricValue"] div {
    font-size: 24px !important;
    font-weight: 800 !important;
    color: #ffffff !important;
}

/* Modern Sidebar Aesthetics */
[data-testid="stSidebar"] {
    background-color: #08090d;
    border-right: 1px solid #1a1c26;
}

[data-testid="stSidebar"] [data-testid="stRadio"] > div {
    gap: 6px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    background: #12131b;
    border: 1px solid #1f212d;
    padding: 9px 14px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 2px;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child {
    display: none;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label p {
    font-size: 13.5px !important;
    font-weight: 600 !important;
    color: #9da1b5 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #191c28;
    border-color: #35394d;
    transform: translateX(3px);
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"],
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
    background: linear-gradient(90deg, rgba(225, 6, 0, 0.25) 0%, rgba(225, 6, 0, 0.05) 100%) !important;
    border: 1px solid #e10600 !important;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] p,
[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 700 !important;
}

/* Headers */
h1, h2, h3 {
    color: #ffffff;
    font-weight: 800;
    letter-spacing: -0.5px;
}

/* Clean Tables */
[data-testid="stDataFrame"] {
    border: 1px solid #1f212d;
    border-radius: 8px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    laps = pd.read_csv("data/processed/lap_data.csv")
    stints = pd.read_csv("data/processed/stint_data.csv")
    pitstops = pd.read_csv("data/processed/pitstop_data.csv")
    weather = pd.read_csv("data/processed/weather_data.csv")
    drivers = pd.read_csv("data/raw/drivers.csv")
    
    if "compound" in stints.columns:
        stints["compound"] = stints["compound"].astype(str).str.upper()
    return laps, stints, pitstops, weather, drivers

laps, stints, pitstops, weather, drivers = load_data()


with st.sidebar:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #181922 0%, #101117 100%); 
                    border: 1px solid #282b3a; border-radius: 12px; padding: 14px; margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 11px; font-weight: 800; color: #e10600; letter-spacing: 1.5px; text-transform: uppercase;">ROUND 12 • F1 2024</span>
                <span style="background-color: rgba(0, 230, 118, 0.15); color: #00e676; font-size: 10px; padding: 2px 8px; border-radius: 20px; font-weight: 700;">TELEMETRY ACTIVE</span>
            </div>
            <div style="font-size: 18px; font-weight: 800; color: #ffffff; margin-top: 6px;">Silverstone Circuit</div>
            <div style="font-size: 12px; color: #8e93a7; margin-top: 2px;">52 Laps • 5.891 km • Mixed Conditions</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <p style="font-size: 10.5px; font-weight: 800; color: #62667a; letter-spacing: 1.5px; margin-bottom: 8px; text-transform: uppercase;">
            TACTICAL MODULES
        </p>
    """, unsafe_allow_html=True)

    nav_options = {
        "🏁 Race Overview": "Race Overview",
        "⚡ Driver Performance": "Driver Performance",
        "🛞 Tyre Strategy & Gantt": "Tyre Strategy",
        "⏱️ Pit Stop Breakdown": "Pit Stop Analysis",
        "💡 Strategy Diagnostics": "Strategy Insights",
        "📈 Fuel-Corrected Degradation": "Advanced Analytics",
        "🧠 Undercut Simulator": "Pit Window Simulator",
        "⚔️ Driver Head-to-Head": "Driver Comparison"
    }

    selected_label = st.radio(
        label="Modules",
        options=list(nav_options.keys()),
        label_visibility="collapsed"
    )
    page = nav_options[selected_label]

    st.divider()

    st.markdown("""
        <p style="font-size: 10.5px; font-weight: 800; color: #62667a; letter-spacing: 1.5px; margin-bottom: 8px; text-transform: uppercase;">
            TRACK METRICS
        </p>
    """, unsafe_allow_html=True)

    latest_track_temp = f"{weather['track_temperature'].iloc[-1]:.1f}°C" if not weather.empty else "31.2°C"
    latest_air_temp = f"{weather['air_temperature'].iloc[-1]:.1f}°C" if not weather.empty else "18.5°C"

    col_side1, col_side2 = st.columns(2)
    with col_side1:
        st.markdown(f"""
            <div style="background-color: #12131b; border-radius: 8px; padding: 10px; border-left: 3px solid #e10600;">
                <div style="font-size: 10px; color: #7f8398; font-weight: 700;">TRACK TEMP</div>
                <div style="font-size: 16px; font-weight: 800; color: #fff; margin-top: 2px;">{latest_track_temp}</div>
            </div>
        """, unsafe_allow_html=True)
    with col_side2:
        st.markdown(f"""
            <div style="background-color: #12131b; border-radius: 8px; padding: 10px; border-left: 3px solid #00AEEF;">
                <div style="font-size: 10px; color: #7f8398; font-weight: 700;">AIR TEMP</div>
                <div style="font-size: 16px; font-weight: 800; color: #fff; margin-top: 2px;">{latest_air_temp}</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <div style="margin-top: 18px; padding: 10px 12px; background: rgba(255,255,255,0.02); border-radius: 8px; border: 1px dashed #232634;">
            <div style="font-size: 11px; color: #9da1b5;">Track Surface: <span style="color: #00e676; font-weight: 700;">DRYING OUT</span></div>
            <div style="font-size: 11px; color: #9da1b5; margin-top: 3px;">Pit Lane Delta: <span style="color: #fff; font-weight: 700;">20.5s Loss</span></div>
        </div>
    """, unsafe_allow_html=True)

# ----------------------------------
# HEADER BANNER
# ----------------------------------

st.markdown("""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px;">
        <div>
            <h1 style="margin: 0; font-size: 32px; font-weight: 900; letter-spacing: -0.5px;">
                🏎️ F1 <span style="color: #e10600;">STRATEGYLAB</span>
            </h1>
            <p style="margin: 2px 0 0 0; color: #8e93a7; font-size: 14px;">
                Formula 1 Race Engineering & Performance Intelligence Platform
            </p>
        </div>
        <div style="text-align: right;">
            <span style="font-size: 12px; background: #161821; border: 1px solid #232634; padding: 6px 12px; border-radius: 6px; font-weight: 600; color: #d0d3e2;">
                British Grand Prix 2024
            </span>
        </div>
    </div>
""", unsafe_allow_html=True)
st.divider()


if page == "Race Overview":
    st.subheader("🏁 Race Overview & Operating Parameters")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Classified Drivers", laps["driver_number"].nunique())
    col2.metric("Recorded Laps", len(laps))
    col3.metric("Total Pit Stops", len(pitstops))
    col4.metric("Tyre Compounds Run", stints["compound"].nunique())

    st.write("")

    st.subheader("Driver Lap Distribution")
    driver_counts = laps.groupby("full_name")["lap_number"].count().reset_index()
    driver_counts.columns = ["Driver", "Laps Recorded"]

    fig = px.bar(
        driver_counts.sort_values("Laps Recorded"),
        x="Laps Recorded",
        y="Driver",
        orientation="h",
        color="Laps Recorded",
        color_continuous_scale="Reds"
    )
    fig.update_layout(
        plot_bgcolor="#111218",
        paper_bgcolor="#0c0d12",
        font=dict(color="#ffffff"),
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig, width="stretch")

    st.subheader("Session Weather Evolution")
    col1, col2 = st.columns(2)

    with col1:
        fig = px.line(
            weather,
            x=weather.index,
            y="track_temperature",
            title="Track Temperature Profile (°C)",
            color_discrete_sequence=["#e10600"]
        )
        fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.line(
            weather,
            x=weather.index,
            y="air_temperature",
            title="Ambient Temperature Profile (°C)",
            color_discrete_sequence=["#00AEEF"]
        )
        fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
        st.plotly_chart(fig, width="stretch")


elif page == "Driver Performance":
    st.subheader("⚡ Driver Pace & Telemetry Metrics")

    performance = driver_performance(laps)

    display_perf = performance.copy()
    display_perf["average_lap_time_str"] = display_perf["average_lap_time"].apply(format_laptime)
    display_perf["fastest_lap_str"] = display_perf["fastest_lap"].apply(format_laptime)

    st.dataframe(
        display_perf[["full_name", "team_name", "total_laps", "average_lap_time_str", "fastest_lap_str"]].rename(
            columns={
                "full_name": "Driver",
                "team_name": "Team",
                "total_laps": "Laps",
                "average_lap_time_str": "Mean Lap Time",
                "fastest_lap_str": "Fastest Lap"
            }
        ),
        width="stretch",
        hide_index=True
    )

    fig = px.bar(
        performance.sort_values("average_lap_time"),
        x="full_name",
        y="average_lap_time",
        color="team_name",
        title="Mean Lap Time by Driver",
        labels={"full_name": "Driver", "average_lap_time": "Average Lap Time (seconds)"}
    )
    fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
    st.plotly_chart(fig, width="stretch")

    fig = px.bar(
        performance.sort_values("fastest_lap"),
        x="full_name",
        y="fastest_lap",
        color="team_name",
        title="Fastest Recorded Outright Lap",
        labels={"full_name": "Driver", "fastest_lap": "Lap Time (seconds)"}
    )
    fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
    st.plotly_chart(fig, width="stretch")


elif page == "Tyre Strategy":
    st.subheader("🛞 Tyre Compound Utilization & Stint Gantt")

    tyre_stats = tyre_analysis(stints)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(
            tyre_stats,
            names="compound",
            values="total_stints",
            hole=0.5,
            title="Tyre Compound Usage Share",
            color="compound",
            color_discrete_map=COMPOUND_COLORS
        )
        fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = px.bar(
            tyre_stats,
            x="compound",
            y="average_stint_length",
            color="compound",
            title="Mean Stint Length by Compound",
            color_discrete_map=COMPOUND_COLORS,
            labels={"average_stint_length": "Average Laps"}
        )
        fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
        st.plotly_chart(fig, width="stretch")

    st.subheader("🏁 Driver Stint Strategy Gantt Timeline")

    stints_gantt = stints.merge(
        drivers[["driver_number", "full_name", "team_name"]].drop_duplicates("driver_number"),
        on="driver_number",
        how="left"
    ).copy()

    stints_gantt["stint_length"] = stints_gantt["lap_end"] - stints_gantt["lap_start"] + 1
    stints_gantt["compound"] = stints_gantt["compound"].astype(str).str.upper()
    stints_gantt = stints_gantt.sort_values("full_name", ascending=False)

    fig_gantt = px.bar(
        stints_gantt,
        base="lap_start",
        x="stint_length",
        y="full_name",
        color="compound",
        orientation="h",
        color_discrete_map=COMPOUND_COLORS,
        hover_data=["stint_number", "lap_start", "lap_end", "compound"],
        labels={
            "full_name": "Driver",
            "stint_length": "Stint Duration (Laps)",
            "compound": "Compound"
        }
    )

    fig_gantt.update_layout(
        xaxis=dict(title="Race Lap Number", dtick=5, range=[0, 53], gridcolor="#1e202b"),
        yaxis=dict(title=""),
        plot_bgcolor="#111218",
        paper_bgcolor="#0c0d12",
        font=dict(color="white"),
        height=650,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_gantt, width="stretch")

    st.subheader("Compound Statistics Summary")
    st.dataframe(tyre_stats, width="stretch", hide_index=True)


elif page == "Pit Stop Analysis":
    st.subheader("⏱️ Pit Lane Efficiency & Duration")

    pit_stats = pitstop_analysis(pitstops)

    col1, col2 = st.columns(2)
    col1.metric("Total Pit Lane Stops", len(pitstops))
    col2.metric("Mean Pit Duration", f"{pitstops['pit_duration'].astype(float).mean():.2f} sec")

    st.subheader("Stop Count by Driver")
    fig = px.bar(
        pit_stats,
        x="driver_number",
        y="total_pitstops",
        color="total_pitstops",
        title="Pit Stop Execution Count",
        color_continuous_scale="Reds"
    )
    fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
    st.plotly_chart(fig, width="stretch")

    st.subheader("Stationary + Pit Lane Time Distribution")
    fig = px.histogram(
        pitstops,
        x="pit_duration",
        nbins=20,
        title="Pit Stop Duration Spread (seconds)",
        color_discrete_sequence=["#e10600"]
    )
    fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
    st.plotly_chart(fig, width="stretch")

    st.dataframe(pit_stats, width="stretch", hide_index=True)

elif page == "Strategy Insights":
    st.subheader("💡 Strategic Rules & Crossover Intelligence")

    strategy = strategy_comparison(stints)

    st.dataframe(strategy, width="stretch", hide_index=True)

    fig = px.scatter(
        strategy,
        x="total_stints",
        y="total_race_laps",
        size="compounds_used",
        color="compounds_used",
        hover_name="driver_number",
        title="Stint Count vs Completed Race Laps",
        labels={"total_stints": "Number of Stints", "total_race_laps": "Total Stint Laps"}
    )
    fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
    st.plotly_chart(fig, width="stretch")

    st.subheader("Automated Race Diagnostic Engine")
    if st.button("Run Strategic Diagnostic"):
        insights = generate_recommendations(laps, stints, pitstops, drivers, weather)
        for insight in insights:
            st.success(insight)

elif page == "Advanced Analytics":
    st.subheader("📈 Fuel-Corrected Degradation & Degradation Slopes")

    fuel_adjusted = st.checkbox("Apply Fuel-Load Correction (~0.035s / lap gain)", value=True)

    points_df, models_df = fit_fuel_corrected_degradation(laps, stints)

    if not points_df.empty:
        time_col = "fuel_adjusted_time" if fuel_adjusted else "lap_duration"
        y_title = "Fuel-Adjusted Lap Time (s)" if fuel_adjusted else "Raw Lap Time (s)"

        fig_deg = px.scatter(
            points_df,
            x="tyre_age",
            y=time_col,
            color="compound",
            opacity=0.35,
            color_discrete_map=COMPOUND_COLORS,
            labels={"tyre_age": "Tyre Age (Laps)", time_col: y_title, "compound": "Compound"},
            title="Compound Pace Evolution vs Tyre Life"
        )

        if fuel_adjusted and not models_df.empty:
            for _, row in models_df.iterrows():
                comp = row["compound"]
                slope = row["deg_per_lap"]
                intercept = row["base_pace"]

                comp_points = points_df[points_df["compound"] == comp]
                if not comp_points.empty:
                    x_vals = np.linspace(1, comp_points["tyre_age"].max(), 20)
                    y_vals = intercept + slope * x_vals

                    color = COMPOUND_COLORS.get(comp, "#FFFFFF")
                    fig_deg.add_trace(go.Scatter(
                        x=x_vals,
                        y=y_vals,
                        mode="lines",
                        name=f"{comp} Trend (+{slope:.3f}s/lap)",
                        line=dict(color=color, width=3)
                    ))

        fig_deg.update_layout(
            plot_bgcolor="#111218",
            paper_bgcolor="#0c0d12",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#1e202b"),
            yaxis=dict(gridcolor="#1e202b")
        )
        st.plotly_chart(fig_deg, width="stretch")

        if not models_df.empty and fuel_adjusted:
            st.markdown("#### Regression Model Outputs")
            display_models = models_df.copy()
            display_models["base_pace"] = display_models["base_pace"].apply(format_laptime)
            display_models["deg_per_lap"] = display_models["deg_per_lap"].apply(lambda x: f"+{x:.3f} s/lap")
            st.dataframe(
                display_models.rename(columns={
                    "compound": "Tyre Compound",
                    "base_pace": "Base Pace (Fresh Tyre)",
                    "deg_per_lap": "True Degradation Rate",
                    "sample_count": "Laps Analyzed"
                }),
                width="stretch",
                hide_index=True
            )

    st.divider()

    st.subheader("Driver Stint Strategy Breakdown")
    strategy = compare_driver_strategies(stints, drivers)
    st.dataframe(strategy, width="stretch", hide_index=True)

    fig = px.scatter(
        strategy,
        x="total_stints",
        y="compounds_used",
        size="total_race_laps",
        color="team_name",
        hover_name="full_name",
        title="Driver Stint & Compound Distribution"
    )
    fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
    st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("Pit Stop Timing across Race Laps")
    pit_analysis = analyze_pitstop_timing(pitstops, drivers)

    if not pit_analysis.empty:
        fig = px.scatter(
            pit_analysis,
            x="lap_number",
            y="pit_duration",
            color="team_name",
            hover_name="full_name",
            title="Pit Stop Execution vs Race Lap",
            labels={"lap_number": "Race Lap", "pit_duration": "Pit Lane Duration (Seconds)"}
        )
        fig.update_layout(plot_bgcolor="#111218", paper_bgcolor="#0c0d12", font=dict(color="#ffffff"))
        st.plotly_chart(fig, width="stretch")


elif page == "Pit Window Simulator":
    st.subheader("🧠 Tactical Undercut / Overcut Simulator")
    st.caption("Evaluate pit stop trigger points, track position retention, and undercut feasibility in real time.")

    col1, col2, col3 = st.columns(3)
    with col1:
        current_gap = st.slider("Gap to Leading Car (seconds)", min_value=0.2, max_value=6.0, value=1.8, step=0.1)
    with col2:
        pit_loss = st.number_input("Silverstone Pit Lane Loss (seconds)", min_value=15.0, max_value=30.0, value=20.5, step=0.1)
    with col3:
        fresh_tyre_delta = st.slider("New Tyre Pace Advantage (seconds/lap)", min_value=0.2, max_value=3.5, value=1.5, step=0.1)

    inlap_push = st.slider("Chasing Driver In-Lap Push Delta (seconds)", min_value=-0.5, max_value=1.5, value=0.4, step=0.1)

    net_undercut_gain = fresh_tyre_delta + inlap_push
    projected_margin = net_undercut_gain - current_gap

    st.subheader("Strategic Decision Matrix")
    if projected_margin > 0:
        st.success(
            f"🚀 **TRIGGER UNDERCUT NOW**: Total out-lap advantage is **{net_undercut_gain:.2f}s**, "
            f"exceeding the **{current_gap:.2f}s** gap. Projected track position gain by **+{projected_margin:.2f}s**."
        )
    else:
        st.warning(
            f"🛡️ **HOLD POSITION / OVERCUT**: Total out-lap advantage is **{net_undercut_gain:.2f}s**, "
            f"which cannot overcome the **{current_gap:.2f}s** gap. The car will exit **{abs(projected_margin):.2f}s** behind into dirty air."
        )

    sim_df = pd.DataFrame({
        "Stage": ["Pre-Stop Gap", "In-Lap Phase", "Pit Loss Penalty", "Out-Lap Fresh Tyre Delta", "Projected Net Gap"],
        "Delta": [-current_gap, inlap_push, -pit_loss, fresh_tyre_delta, projected_margin]
    })
    fig_waterfall = go.Figure(go.Waterfall(
        name="Pit Phase",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=sim_df["Stage"],
        textposition="outside",
        text=[f"{v:+.2f}s" for v in sim_df["Delta"]],
        y=sim_df["Delta"],
        connector={"line": {"color": "#393d4f"}},
    ))
    fig_waterfall.update_layout(
        title="Undercut Net Delta Breakdown (seconds)",
        plot_bgcolor="#111218",
        paper_bgcolor="#0c0d12",
        font=dict(color="white"),
        xaxis=dict(gridcolor="#1e202b"),
        yaxis=dict(gridcolor="#1e202b")
    )
    st.plotly_chart(fig_waterfall, width="stretch")

elif page == "Driver Comparison":
    st.subheader("⚔️ Head-to-Head Telemetry Comparison")
    st.caption("Compare telemetry pace and lap times between any two drivers.")

    available_drivers = sorted(laps["full_name"].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        driver1 = st.selectbox("Select First Driver", available_drivers, index=0, key="driver_one")
    with col2:
        driver2_options = [d for d in available_drivers if d != driver1]
        driver2 = st.selectbox("Select Second Driver", driver2_options, index=0, key="driver_two")

    comparison = laps[laps["full_name"].isin([driver1, driver2])].copy()
    comparison["lap_duration"] = pd.to_numeric(comparison["lap_duration"], errors="coerce")

    q_low = comparison["lap_duration"].quantile(0.01)
    q_high = comparison["lap_duration"].quantile(0.90)
    comparison = comparison[comparison["lap_duration"].between(q_low, q_high)]

    if not comparison.empty:
        fig = px.line(
            comparison,
            x="lap_number",
            y="lap_duration",
            color="full_name",
            markers=True,
            title=f"Head-to-Head Pace: {driver1} vs {driver2}",
            labels={"lap_number": "Race Lap", "lap_duration": "Lap Time (Seconds)", "full_name": "Driver"},
            color_discrete_sequence=["#e10600", "#FFFFFF"]
        )
        fig.update_layout(
            plot_bgcolor="#111218",
            paper_bgcolor="#0c0d12",
            font=dict(color="white"),
            xaxis=dict(gridcolor="#1e202b"),
            yaxis=dict(gridcolor="#1e202b")
        )
        st.plotly_chart(fig, width="stretch")

        st.subheader("Head-to-Head Summary")
        summary = comparison.groupby("full_name").agg(
            Average_Lap_Time=("lap_duration", "mean"),
            Fastest_Lap=("lap_duration", "min"),
            Total_Laps=("lap_number", "count")
        ).reset_index()

        summary["Formatted_Avg"] = summary["Average_Lap_Time"].apply(format_laptime)
        summary["Formatted_Fastest"] = summary["Fastest_Lap"].apply(format_laptime)

        st.dataframe(
            summary[["full_name", "Total_Laps", "Formatted_Avg", "Formatted_Fastest"]].rename(
                columns={
                    "full_name": "Driver",
                    "Total_Laps": "Valid Representative Laps",
                    "Formatted_Avg": "Average Pace",
                    "Formatted_Fastest": "Fastest Lap"
                }
            ),
            width="stretch",
            hide_index=True
        )
    else:
        st.warning("No representative lap data available for selected drivers.")

st.divider()
st.caption("F1 StrategyLab | Formula 1 Race Intelligence Platform | Built for AQX Data Bowl 4.0")