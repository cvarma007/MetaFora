
import pandas as pd
import re

def normalize(value):
    if pd.isna(value):
        return ""
    return re.sub(r"[^A-Z0-9]", "", str(value).upper().strip())


# Load GTFS data
routes = pd.read_csv("data/raw/routes.txt", dtype=str)
stops = pd.read_csv("data/raw/stops.txt", dtype=str)

# Create normalized matching keys
routes["match_key"] = routes["route_short_name"].apply(normalize)
stops["match_key"] = stops["stop_name"].apply(normalize)

# Check duplicate normalized route names
route_counts = routes.groupby("match_key").size()
duplicate_routes = route_counts[route_counts > 1]

# Check duplicate normalized stop names
stop_counts = stops.groupby("match_key").size()
duplicate_stops = stop_counts[stop_counts > 1]

print("\n========== GTFS DUPLICATE CHECK ==========")

print("Total GTFS routes:", len(routes))
print("Unique normalized route names:", routes["match_key"].nunique())
print("Duplicate route-name keys:", len(duplicate_routes))

print("\nSample duplicate route names:")
print(duplicate_routes.head(15).to_string())

print("\nTotal GTFS stops:", len(stops))
print("Unique normalized stop names:", stops["match_key"].nunique())
print("Duplicate stop-name keys:", len(duplicate_stops))

print("\nSample duplicate stop names:")
print(duplicate_stops.head(15).to_string())


# Build route mapping only where the normalized name is unique
unique_route_keys = route_counts[route_counts == 1].index

route_mapping = routes[
    routes["match_key"].isin(unique_route_keys)
][["match_key", "route_id", "route_short_name", "route_long_name", "agency_id"]]

route_mapping.to_csv(
    "data/processed/gtfs_route_mapping.csv",
    index=False
)


# Build stop mapping only where the normalized name is unique
unique_stop_keys = stop_counts[stop_counts == 1].index

stop_mapping = stops[
    stops["match_key"].isin(unique_stop_keys)
][["match_key", "stop_id", "stop_name", "stop_lat", "stop_lon"]]

stop_mapping.to_csv(
    "data/processed/gtfs_stop_mapping.csv",
    index=False
)

print("\n========== MAPPING TABLES ==========")
print("Unambiguous route mappings:", len(route_mapping))
print("Unambiguous stop mappings:", len(stop_mapping))

print("\nSaved:")
print("data/processed/gtfs_route_mapping.csv")
print("data/processed/gtfs_stop_mapping.csv")
