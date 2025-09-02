import os
import glob
import pandas as pd

FOLDER = "temperatures"

# ------------- helpers -------------
def get_season(month: int) -> str:
    # Australian seasons
    if month in (12, 1, 2):
        return "Summer"
    elif month in (3, 4, 5):
        return "Autumn"
    elif month in (6, 7, 8):
        return "Winter"
    else:
        return "Spring"

# ------------- load data -------------
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)

csv_paths = glob.glob(os.path.join(FOLDER, "*.csv"))

if not csv_paths:
    print("No CSV files found in the 'temperatures' folder.")
    print("Add some .csv files and run again.")
    raise SystemExit

frames = []
for path in csv_paths:
    try:
        df = pd.read_csv(path)
        # basic column check
        required = {"Date", "Station", "Temperature"}
        if not required.issubset(df.columns):
            print(f"Skipping {os.path.basename(path)}: missing one of {required}")
            continue

        # make sure Date is datetime, Temperature numeric
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df["Temperature"] = pd.to_numeric(df["Temperature"], errors="coerce")

        # drop rows with missing values we need
        df = df.dropna(subset=["Date", "Temperature", "Station"])

        frames.append(df)
    except Exception as e:
        print(f"Skipping {os.path.basename(path)} due to read error: {e}")

if not frames:
    print("No valid data could be loaded from the CSV files.")
    raise SystemExit

data = pd.concat(frames, ignore_index=True)

# add Season column
data["Season"] = data["Date"].dt.month.apply(get_season)

# ------------- 1) seasonal average across all stations & years -------------
seasonal_avg = data.groupby("Season")["Temperature"].mean()

# write in Australian season order
season_order = ["Summer", "Autumn", "Winter", "Spring"]
with open("average_temp.txt", "w", encoding="utf-8") as f:
    for s in season_order:
        if s in seasonal_avg.index:
            f.write(f"{s}: {seasonal_avg.loc[s]:.1f}°C\n")

# ------------- 2) largest temperature range per station -------------
# range = max - min per station
station_stats = data.groupby("Station")["Temperature"].agg(["max", "min"])
station_stats["range"] = station_stats["max"] - station_stats["min"]

if station_stats["range"].empty:
    print("No station range data.")
else:
    max_range_value = station_stats["range"].max()
    winners = station_stats[station_stats["range"] == max_range_value]

    with open("largest_temp_range_station.txt", "w", encoding="utf-8") as f:
        for station, row in winners.iterrows():
            f.write(
                f"{station}: Range {row['range']:.1f}°C "
                f"(Max: {row['max']:.1f}°C, Min: {row['min']:.1f}°C)\n"
            )

# ------------- 3) temperature stability (std dev) -------------
std_per_station = data.groupby("Station")["Temperature"].std(ddof=1).dropna()

if std_per_station.empty:
    # happens if every station only has one reading
    with open("temperature_stability_stations.txt", "w", encoding="utf-8") as f:
        f.write("Not enough data to compute standard deviations.\n")
else:
    min_std = std_per_station.min()
    max_std = std_per_station.max()

    most_stable = std_per_station[std_per_station == min_std].index.tolist()
    most_variable = std_per_station[std_per_station == max_std].index.tolist()

    with open("temperature_stability_stations.txt", "w", encoding="utf-8") as f:
        for st in most_stable:
            f.write(f"Most Stable: {st}: StdDev {min_std:.1f}°C\n")
        for st in most_variable:
            f.write(f"Most Variable: {st}: StdDev {max_std:.1f}°C\n")

print("✅ Done. Created: average_temp.txt, largest_temp_range_station.txt, temperature_stability_stations.txt")
