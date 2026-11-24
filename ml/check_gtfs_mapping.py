
import pandas as pd
import re

def normalize(value):
    """Standardize names for comparison."""
    if pd.isna(value):
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper().strip())


# Load GTFS routes and stops
gtfs_routes = pd.read_csv(
    "data/raw/routes.txt",
    dtype=str
)

gtfs_stops = pd.read_csv(
    "data/raw/stops.txt",
    dtype=str
)

# Collect unique ticketing values in chunks
ticket_routes = set()
ticket_stops = set()

for chunk in pd.read_csv(
    "data/processed/October-Delhi-cleaned.csv",
    usecols=["route", "start_stop_name", "end_stop_name"],
    dtype=str,
    chunksize=100000
):
    ticket_routes.update(chunk["route"].dropna().unique())
    ticket_stops.update(chunk["start_stop_name"].dropna().unique())
    ticket_stops.update(chunk["end_stop_name"].dropna().unique())


# Compare routes
gtfs_route_names = set(
    gtfs_routes["route_short_name"].dropna()
)

gtfs_route_normalized = {
    normalize(name) for name in gtfs_route_names
}

ticket_route_normalized = {
    normalize(name) for name in ticket_routes
}

matched_routes = ticket_route_normalized & gtfs_route_normalized
unmatched_routes = ticket_route_normalized - gtfs_route_normalized


# Compare stops
gtfs_stop_names = set(
    gtfs_stops["stop_name"].dropna()
)

gtfs_stop_normalized = {
    normalize(name) for name in gtfs_stop_names
}

ticket_stop_normalized = {
    normalize(name) for name in ticket_stops
}

matched_stops = ticket_stop_normalized & gtfs_stop_normalized
unmatched_stops = ticket_stop_normalized - gtfs_stop_normalized


# Display results
print("\n========== ROUTE MATCHING ==========")

print("Unique ticketing routes:", len(ticket_routes))
print("Unique GTFS route names:", len(gtfs_route_names))
print("Matched routes:", len(matched_routes))
print("Unmatched ticketing routes:", len(unmatched_routes))

print("\nSample unmatched routes:")
for route in sorted(unmatched_routes)[:20]:
    print(route)


print("\n========== STOP MATCHING ==========")

print("Unique ticketing stop names:", len(ticket_stops))
print("Unique GTFS stop names:", len(gtfs_stop_names))
print("Matched stops:", len(matched_stops))
print("Unmatched ticketing stops:", len(unmatched_stops))

print("\nSample unmatched stops:")
for stop in sorted(unmatched_stops)[:20]:
    print(stop)


# Save unmatched values for further investigation
pd.DataFrame({
    "unmatched_route": sorted(unmatched_routes)
}).to_csv("data/processed/unmatched_routes.csv", index=False)

pd.DataFrame({
    "unmatched_stop": sorted(unmatched_stops)
}).to_csv("data/processed/unmatched_stops.csv", index=False)

print("\nMapping check completed!")
