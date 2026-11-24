
import pandas as pd

print("Loading GTFS stop times...")

# Read the required columns
stop_times = pd.read_csv(
    "data/raw/stop_times.txt",
    usecols=[
        "trip_id",
        "arrival_time",
        "departure_time",
        "stop_id",
        "stop_sequence"
    ],
    dtype={
        "trip_id": str,
        "arrival_time": str,
        "departure_time": str,
        "stop_id": str
    }
)

# Convert stop sequence into numbers
stop_times["stop_sequence"] = pd.to_numeric(
    stop_times["stop_sequence"],
    errors="coerce"
)

stop_times = stop_times.dropna(subset=["stop_sequence"])

print("Sorting stops by trip and sequence...")

stop_times = stop_times.sort_values(
    ["trip_id", "stop_sequence"]
).reset_index(drop=True)


# Convert GTFS time (including hours above 24) into seconds
def time_to_seconds(value):
    try:
        hours, minutes, seconds = map(int, value.split(":"))
        return hours * 3600 + minutes * 60 + seconds
    except (ValueError, AttributeError):
        return None


stop_times["arrival_seconds"] = (
    stop_times["arrival_time"].apply(time_to_seconds)
)

stop_times["departure_seconds"] = (
    stop_times["departure_time"].apply(time_to_seconds)
)


# Get the next stop within each trip
grouped = stop_times.groupby("trip_id", sort=False)

stop_times["to_stop_id"] = grouped["stop_id"].shift(-1)
stop_times["to_sequence"] = grouped["stop_sequence"].shift(-1)

stop_times["to_arrival_time"] = (
    grouped["arrival_time"].shift(-1)
)

stop_times["to_arrival_seconds"] = (
    grouped["arrival_seconds"].shift(-1)
)


# Calculate travel time between consecutive stops
stop_times["travel_time_minutes"] = (
    stop_times["to_arrival_seconds"]
    - stop_times["departure_seconds"]
) / 60


# Keep only rows that have a following stop
connections = stop_times.dropna(
    subset=["to_stop_id", "to_sequence"]
).copy()

# Remove invalid or non-positive travel times from the duration field.
# Keep the connection itself for later investigation.
invalid_duration = (
    connections["travel_time_minutes"].isna()
    | (connections["travel_time_minutes"] <= 0)
)

invalid_count = invalid_duration.sum()

connections.loc[
    invalid_duration,
    "travel_time_minutes"
] = pd.NA


# Rename columns
connections = connections.rename(columns={
    "stop_id": "from_stop_id",
    "departure_time": "departure_time",
    "arrival_time": "from_arrival_time"
})


# Attach route ID to each trip
trips = pd.read_csv(
    "data/raw/trips.txt",
    usecols=["trip_id", "route_id"],
    dtype=str
)

connections = connections.merge(
    trips,
    on="trip_id",
    how="left",
    validate="many_to_one"
)


# Select final columns
connections = connections[[
    "route_id",
    "trip_id",
    "from_stop_id",
    "to_stop_id",
    "stop_sequence",
    "to_sequence",
    "departure_time",
    "to_arrival_time",
    "travel_time_minutes"
]]

# Save connections
output_path = "data/processed/gtfs_stop_connections.csv"

connections.to_csv(output_path, index=False)

print("\n========== CONNECTION SUMMARY ==========")

print("Total stop connections:", len(connections))
print("Connections with invalid duration:", invalid_count)
print("Unique routes:", connections["route_id"].nunique())
print("Unique trips:", connections["trip_id"].nunique())
print("Unique starting stops:", connections["from_stop_id"].nunique())
print("Unique destination stops:", connections["to_stop_id"].nunique())

print("\nSample connections:")
print(connections.head(10).to_string(index=False))

print("\nSaved successfully:", output_path)
