
import pandas as pd
import os

gtfs_folder = "data/raw"

files = [
    "agency.txt",
    "routes.txt",
    "stops.txt",
    "trips.txt",
    "stop_times.txt",
    "calendar.txt",
    "shapes.txt",
    "feed_info.txt"
]

for filename in files:
    path = os.path.join(gtfs_folder, filename)

    if not os.path.exists(path):
        print(f"\n{filename}: FILE NOT FOUND")
        continue

    print("\n" + "=" * 60)
    print(f"FILE: {filename}")
    print("=" * 60)

    # Read column names and first five records
    sample = pd.read_csv(path, nrows=5, low_memory=False)

    print("\nColumns:")
    print(sample.columns.tolist())

    print("\nFirst 5 records:")
    print(sample.to_string(index=False))

    # Count total records without loading the entire file
    total_rows = 0

    for chunk in pd.read_csv(path, chunksize=100000, low_memory=False):
        total_rows += len(chunk)

    print(f"\nTotal records: {total_rows}")
