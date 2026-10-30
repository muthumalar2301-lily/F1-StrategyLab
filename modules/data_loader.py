import requests
import pandas as pd
import os

BASE_URL = "https://api.openf1.org/v1"

# Ensure output directories exist
os.makedirs("data/raw", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)


def fetch_data(endpoint: str, params: dict) -> pd.DataFrame:
    """Fetch endpoint JSON from OpenF1 API and convert to DataFrame."""
    url = f"{BASE_URL}/{endpoint}"
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    return pd.DataFrame(payload) if payload else pd.DataFrame()


def load_race_data():
    """
    Extracts 2024 British Grand Prix data from OpenF1, normalizes fields,
    casts numeric types, merges driver profiles, and caches datasets locally.
    """
    print("Fetching 2024 British Grand Prix metadata...")

    meetings = fetch_data("meetings", {"year": 2024})
    if meetings.empty:
        raise ValueError("Failed to retrieve 2024 meetings schedule.")

    meeting = meetings[meetings["meeting_name"].str.contains("British Grand Prix", case=False, na=False)]
    if meeting.empty:
        raise ValueError("British Grand Prix meeting not found.")

    meeting_key = int(meeting.iloc[0]["meeting_key"])

    sessions = fetch_data("sessions", {"meeting_key": meeting_key, "session_name": "Race"})
    if sessions.empty:
        raise ValueError("Race session not found for Silverstone 2024.")

    session_key = int(sessions.iloc[0]["session_key"])
    print(f"Race session identified (Key: {session_key}). Fetching telemetry streams...")

    # Fetch primary streams
    laps = fetch_data("laps", {"session_key": session_key})
    stints = fetch_data("stints", {"session_key": session_key})
    pitstops = fetch_data("pit", {"session_key": session_key})
    weather = fetch_data("weather", {"session_key": session_key})
    drivers = fetch_data("drivers", {"session_key": session_key})

    # Save raw mirrors
    raw_datasets = {
        "laps": laps,
        "stints": stints,
        "pitstops": pitstops,
        "weather": weather,
        "drivers": drivers
    }
    for name, df in raw_datasets.items():
        df.to_csv(f"data/raw/{name}.csv", index=False)

    # ----------------------------------------------------
    # DATA NORMALIZATION & NUMERIC CASTING
    # ----------------------------------------------------

    # 1. Driver info merge
    if not drivers.empty:
        driver_info = drivers[
            ["driver_number", "full_name", "team_name"]
        ].drop_duplicates("driver_number")

        laps = laps.merge(driver_info, on="driver_number", how="left")

    # 2. Laps normalization
    if not laps.empty:
        laps["lap_number"] = pd.to_numeric(laps["lap_number"], errors="coerce")
        laps["lap_duration"] = pd.to_numeric(laps["lap_duration"], errors="coerce")
        laps["driver_number"] = pd.to_numeric(laps["driver_number"], errors="coerce")
        laps = laps.dropna(subset=["lap_number"])

    # 3. Stints normalization
    if not stints.empty:
        stints["stint_number"] = pd.to_numeric(stints["stint_number"], errors="coerce")
        stints["lap_start"] = pd.to_numeric(stints["lap_start"], errors="coerce")
        stints["lap_end"] = pd.to_numeric(stints["lap_end"], errors="coerce")
        stints["tyre_age_at_start"] = pd.to_numeric(stints["tyre_age_at_start"], errors="coerce").fillna(0)
        stints["compound"] = stints["compound"].astype(str).str.upper()

    # 4. Pit stops normalization
    if not pitstops.empty:
        pitstops["pit_duration"] = pd.to_numeric(pitstops["pit_duration"], errors="coerce")
        pitstops["lap_number"] = pd.to_numeric(pitstops["lap_number"], errors="coerce")

    # 5. Weather normalization
    if not weather.empty:
        weather["track_temperature"] = pd.to_numeric(weather["track_temperature"], errors="coerce")
        weather["air_temperature"] = pd.to_numeric(weather["air_temperature"], errors="coerce")

    # Save processed outputs
    processed_datasets = {
        "lap_data": laps,
        "stint_data": stints,
        "pitstop_data": pitstops,
        "weather_data": weather
    }
    for name, df in processed_datasets.items():
        df.to_csv(f"data/processed/{name}.csv", index=False)

    print("\nDATA EXTRACTION & CLEANING COMPLETE!")
    for name, df in processed_datasets.items():
        print(f"✓ {name}: {len(df)} records cached")

    return laps, stints, pitstops, weather, drivers


if __name__ == "__main__":
    load_race_data()