import os
import glob
import pandas as pd

FOLDER = "temperatures"

# ------------- helpers -------------
def get_season(month: str) -> str:
    month = month.lower()
    if month in ("december", "january", "february"):
        return "Summer"
    elif month in ("march", "april", "may"):
        return "Autumn"
    elif month in ("june", "july", "august"):
        return "Winter"
    else:
        return "Spring"

# ------------- load data -------------
csv_paths = glob.glob(os.path.join(FOLDER, "*.csv"))
if not csv_paths:
    print("No CSV files found in the 'temperatures' folder.")
    raise SystemExit

frames = []
for path in csv_paths:
    try:
        df = pd.read_csv(path)

        # Reshape from wide (months as columns) to long format
        df_long = df.melt(
            id_vars=["STATION_NAME"], 
            value_vars=[
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ],
            var_name="Month",
            value_name="Temperature"
        )

        # Drop missing values
        df_long = df_long.dropna(subset=["Temperature"])

        frames.append(df_long)
    except Exception as e:
        print(f"Skipping {os.path.basename(path)} due to error: {e}")

if not frames:
    print("No valid data could be loaded from the CSV files.")
    raise SystemExit

data = pd.concat(frames, ignore_index=True)

# Add Season column
data["Season"] = data["Month"].apply(get_season)

# -------------------------------------------------
# 1. Seasonal Average (all stations, all years)
# -------------------------------------------------
seasonal_avg = data.groupby("Season")["Temperature"].mean()

with open("average_temp.txt", "w", encoding="utf-8") as f:
    for season in ["Summer", "Autumn", "Winter", "Spring"]:
        if season in seasonal_avg.index:
            f.write(f"{season}: {seasonal_avg.loc[season]:.1f}°C\n")

# -------------------------------------------------
# 2. Largest Temperature Range per Station
# -------------------------------------------------
station_groups = data.groupby("STATION_NAME")["Temperature"]
ranges = station_groups.max() - station_groups.min()

max_range = ranges.max()
stations_with_max = ranges[ranges == max_range].index

with open("largest_temp_range_station.txt", "w", encoding="utf-8") as f:
    for station in stations_with_max:
        max_temp = station_groups.max()[station]
        min_temp = station_groups.min()[station]
        f.write(f"{station}: Range {max_range:.1f}°C (Max: {max_temp:.1f}°C, Min: {min_temp:.1f}°C)\n")

# -------------------------------------------------
# 3. Temperature Stability (StdDev)
# -------------------------------------------------
stddevs = station_groups.std()

min_std = stddevs.min()
max_std = stddevs.max()

most_stable = stddevs[stddevs == min_std].index
most_variable = stddevs[stddevs == max_std].index

with open("temperature_stability_stations.txt", "w", encoding="utf-8") as f:
    for station in most_stable:
        f.write(f"Most Stable: {station}: StdDev {min_std:.1f}°C\n")
    for station in most_variable:
        f.write(f"Most Variable: {station}: StdDev {max_std:.1f}°C\n")

print("\n--- average_temp.txt ---")
!cat average_temp.txt

print("\n--- largest_temp_range_station.txt ---")
!cat largest_temp_range_station.txt

print("\n--- temperature_stability_stations.txt ---")
!cat temperature_stability_stations.txt
