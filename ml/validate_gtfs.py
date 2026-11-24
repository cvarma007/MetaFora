
import pandas as pd

# Load GTFS files
routes = pd.read_csv("data/raw/routes.txt", dtype=str)
trips = pd.read_csv("data/raw/trips.txt", dtype=str)
stops = pd.read_csv("data/raw/stops.txt", dtype=str)

# Collect trip IDs and stop IDs from stop_times
stop_time_trip_ids = set()
stop_time_stop_ids = set()

total_stop_times = 0

for chunk in pd.read_csv(
    "data/raw/stop_times.txt",
    dtype=str,
    chunksize=200000
):
    total_stop_times += len(chunk)

    stop_time_trip_ids.update(chunk["trip_id"].dropna())
    stop_time_stop_ids.update(chunk["stop_id"].dropna())

# Create valid ID sets
valid_route_ids = set(routes["route_id"])
valid_trip_ids = set(trips["trip_id"])
valid_stop_ids = set(stops["stop_id"])

trip_route_ids = set(trips["route_id"])

# Check relationships
orphan_trip_ids = stop_time_trip_ids - valid_trip_ids
orphan_stop_ids = stop_time_stop_ids - valid_stop_ids
orphan_route_ids = trip_route_ids - valid_route_ids

# Check trips without stop times
trips_without_stop_times = valid_trip_ids - stop_time_trip_ids

print("\n========== GTFS RELATIONSHIP VALIDATION ==========")

print("Routes:", len(valid_route_ids))
print("Trips:", len(valid_trip_ids))
print("Stops:", len(valid_stop_ids))
print("Stop-time records:", total_stop_times)

print("\nStop times referring to unknown trips:", len(orphan_trip_ids))
print("Stop times referring to unknown stops:", len(orphan_stop_ids))
print("Trips referring to unknown routes:", len(orphan_route_ids))
print("Trips without stop-time records:", len(trips_without_stop_times))

print("\nSample orphan trip IDs:", list(orphan_trip_ids)[:10])
print("Sample orphan stop IDs:", list(orphan_stop_ids)[:10])
print("Sample orphan route IDs:", list(orphan_route_ids)[:10])

# Inspect duplicate route names
print("\n========== DUPLICATE ROUTE DETAILS ==========")

duplicates = routes[
    routes["route_short_name"].isin(["106ADOWN", "106AUP"])
]

print(
    duplicates[
        ["agency_id", "route_id", "route_short_name", "route_long_name"]
    ].to_string(index=False)
)

print("\nValidation completed!")
