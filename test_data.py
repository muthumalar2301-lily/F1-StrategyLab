from modules.data_loader import load_race_data

laps, stints, pitstops, weather, drivers = load_race_data()

print("\n========== LAP DATA ==========")
print(laps.head())

print("\n========== TYRE STINTS ==========")
print(stints.head())

print("\n========== PIT STOPS ==========")
print(pitstops.head())

print("\n========== WEATHER ==========")
print(weather.head())

print("\n========== DRIVERS ==========")
print(drivers[["full_name", "team_name"]].head())

print("\nAll datasets downloaded successfully!")