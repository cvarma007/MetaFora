
import pandas as pd
from pathlib import Path

input_file = "data/processed/October-Delhi-cleaned.csv"
output_file = "data/processed/hourly_demand.csv"

print("Preparing hourly passenger demand...")

partial_results = []

# Read only the columns we need, in chunks
for chunk in pd.read_csv(
    input_file,
    usecols=["route", "passenger_count", "created_at"],
    chunksize=100000
):
    # Convert timestamps to Indian Standard Time
    chunk["created_at"] = pd.to_datetime(
        chunk["created_at"],
        errors="coerce",
        utc=True
    ).dt.tz_convert("Asia/Kolkata")

    # Remove invalid timestamps
    chunk = chunk.dropna(subset=["created_at"])

    # Extract date and hour
    chunk["date"] = chunk["created_at"].dt.strftime("%Y-%m-%d")
    chunk["hour"] = chunk["created_at"].dt.hour

    # Calculate passenger demand for each route, date and hour
    grouped = (
        chunk.groupby(["route", "date", "hour"])["passenger_count"]
        .sum()
        .reset_index()
    )

    partial_results.append(grouped)

    print("Processed a chunk...")

# Combine results from all chunks
hourly_demand = pd.concat(partial_results, ignore_index=True)

# Combine duplicate route-date-hour groups
hourly_demand = (
    hourly_demand.groupby(["route", "date", "hour"])["passenger_count"]
    .sum()
    .reset_index()
)

# Create additional time-based features
dates = pd.to_datetime(hourly_demand["date"])

hourly_demand["day_of_week"] = dates.dt.dayofweek
hourly_demand["is_weekend"] = (
    hourly_demand["day_of_week"] >= 5
).astype(int)

# Rename target column
hourly_demand = hourly_demand.rename(
    columns={"passenger_count": "passenger_demand"}
)

# Sort records
hourly_demand = hourly_demand.sort_values(
    ["route", "date", "hour"]
)

# Save the prepared dataset
Path("data/processed").mkdir(exist_ok=True)

hourly_demand.to_csv(output_file, index=False)

print("\nHourly demand dataset created!")
print("Total records:", len(hourly_demand))
print("Unique routes:", hourly_demand["route"].nunique())
print("Saved to:", output_file)

print("\nFirst 5 records:")
print(hourly_demand.head())
