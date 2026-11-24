
import pandas as pd
from pathlib import Path

input_file = "data/processed/October-Delhi-cleaned.csv"

print("Loading cleaned dataset...")

df = pd.read_csv(input_file)

# Convert timestamps
df["created_at"] = pd.to_datetime(
    df["created_at"],
    errors="coerce",
    utc=True
)

# Remove records with invalid timestamps
df = df.dropna(subset=["created_at"])

# Convert to Indian Standard Time
df["created_at"] = df["created_at"].dt.tz_convert(
    "Asia/Kolkata"
)

# Extract hour from timestamp
df["hour"] = df["created_at"].dt.hour

# Group hours into time slots
def get_time_slot(hour):
    if 5 <= hour < 9:
        return "Morning Peak"
    elif 9 <= hour < 12:
        return "Late Morning"
    elif 12 <= hour < 16:
        return "Afternoon"
    elif 16 <= hour < 20:
        return "Evening Peak"
    else:
        return "Night"

df["time_slot"] = df["hour"].apply(get_time_slot)

# Total passenger demand by route
route_demand = (
    df.groupby("route")["passenger_count"]
    .sum()
    .sort_values(ascending=False)
)

# Total passenger demand by time slot
time_demand = (
    df.groupby("time_slot")["passenger_count"]
    .sum()
    .reindex([
        "Morning Peak",
        "Late Morning",
        "Afternoon",
        "Evening Peak",
        "Night"
    ])
)

# Route and hour demand
route_hour_demand = (
    df.groupby(["route", "hour"])["passenger_count"]
    .sum()
    .reset_index()
)

# Save results
Path("data/processed").mkdir(exist_ok=True)

route_demand.to_csv(
    "data/processed/route_demand.csv"
)

time_demand.to_csv(
    "data/processed/time_demand.csv"
)

route_hour_demand.to_csv(
    "data/processed/route_hour_demand.csv",
    index=False
)

print("\n========== TOP 10 ROUTES ==========")
print(route_demand.head(10))

print("\n========== DEMAND BY TIME SLOT ==========")
print(time_demand)

print("\n========== ANALYSIS SUMMARY ==========")
print("Total passengers:", df["passenger_count"].sum())
print("Routes analysed:", df["route"].nunique())
print("Records analysed:", len(df))

print("\nDemand analysis completed!")
