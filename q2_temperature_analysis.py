import os
import glob
import pandas as pd

# folder that holds all the csvs
FOLDER = "temperatures"

# function to map month to Australian season
def get_season(month_name):
    m = month_name.lower()
    if m in ["december", "january", "february"]:
        return "Summer"
    elif m in ["march", "april", "may"]:
        return "Autumn"
    elif m in ["june", "july", "august"]:
        return "Winter"
    else:
        return "Spring"

# get all csv files
csv_paths = glob.glob(os.path.join(FOLDER, "*.csv"))

if not csv_paths:
    print("No CSV files found in the temperatures folder!")
    raise SystemExit

frames = []

# loop through each csv
for path in csv_paths:
    try:
        df = pd.read_csv(path)

        # change from wide format (months as columns) to long format
        df_long = df.melt(
            id_vars=["STATION_NAME"],
            value_vars=[
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ],
            var_name="Month",
            value_name="Temperature"
        )

        # remove rows where temp is missing
        df_long = df_long.dropna(subset=["Temperature"])

        frames.append(df_long)

    except Exception as e:
        print("Skipping file:", os.path.basename(path), "Error:", e)

# join all years together
if not frames:
    print("No valid data in any csv file")
    raise SystemExit

data = pd.concat(frames, ignore_index=True)

# add Season column
data["Season"] = data["Month"].apply(get_season)

# 1. seasonal averages
seasonal_avg = data.groupby("Season")["Temperature"].mean()
with open("average_temp.txt", "w") as file:
    for season in ["Summer","Autumn","Winter","Spring"]:
        if season in seasonal_avg:
            file.write(f"{season}: {seasonal_avg[season]:.1f}°C\n")

# 2. largest temp range
station_groups = data.groupby("STATION_NAME")["Temperature"]
ranges = station_groups.max() - station_groups.min()
max_range = ranges.max()

with open("largest_temp_range_station.txt", "w") as file:
    for st in ranges[ranges == max_range].index:
        file.write(f"{st}: Range {max_range:.1f}°C (Max: {station_groups.max()[st]:.1f}°C, Min: {station_groups.min()[st]:.1f}°C)\n")

# 3. stability (std dev)
stddevs = station_groups.std()
min_std = stddevs.min()
max_std = stddevs.max()

with open("temperature_stability_stations.txt", "w") as file:
    for st in stddevs[stddevs == min_std].index:
        file.write(f"Most Stable: {st}: StdDev {min_std:.1f}°C\n")
    for st in stddevs[stddevs == max_std].index:
        file.write(f"Most Variable: {st}: StdDev {max_std:.1f}°C\n")

# show results directly in Python (instead of !cat)
print("\n--- average_temp.txt ---")
with open("average_temp.txt") as file:
    print(file.read())

print("\n--- largest_temp_range_station.txt ---")
with open("largest_temp_range_station.txt") as file:
    print(file.read())

print("\n--- temperature_stability_stations.txt ---")
with open("temperature_stability_stations.txt") as file:
    print(file.read())
