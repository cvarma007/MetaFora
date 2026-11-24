
import pandas as pd
import networkx as nx
import joblib

print("Loading GTFS stops and connections...")

# Load stop information
stops = pd.read_csv(
    "data/raw/stops.txt",
    dtype={"stop_id": str}
)

# Load consecutive-stop connections
connections = pd.read_csv(
    "data/processed/gtfs_stop_connections.csv",
    dtype={
        "route_id": str,
        "from_stop_id": str,
        "to_stop_id": str
    }
)

# Convert travel time to numeric values
connections["travel_time_minutes"] = pd.to_numeric(
    connections["travel_time_minutes"],
    errors="coerce"
)

# Keep only valid positive travel durations
connections = connections.dropna(
    subset=["travel_time_minutes"]
)

connections = connections[
    connections["travel_time_minutes"] > 0
].copy()

print("Valid connections:", len(connections))

# Aggregate connections for each route and stop pair
# Median is used as the initial travel-time estimate.
edge_data = connections.groupby(
    ["route_id", "from_stop_id", "to_stop_id"]
).agg(
    travel_time_minutes=("travel_time_minutes", "median"),
    trip_count=("trip_id", "nunique")
).reset_index()

# Create a directed multigraph
G = nx.MultiDiGraph()

# Add all GTFS stops as graph nodes
for _, stop in stops.iterrows():
    G.add_node(
        str(stop["stop_id"]),
        name=stop["stop_name"],
        latitude=float(stop["stop_lat"]),
        longitude=float(stop["stop_lon"])
    )

# Add route-specific directed edges
for _, edge in edge_data.iterrows():
    G.add_edge(
        edge["from_stop_id"],
        edge["to_stop_id"],
        key=edge["route_id"],
        route_id=edge["route_id"],
        travel_time_minutes=float(edge["travel_time_minutes"]),
        trip_count=int(edge["trip_count"])
    )

# Save the graph
output_path = "data/processed/metafora_bus_graph.pkl"

joblib.dump(G, output_path)

# Display graph information
print("\n========== GRAPH SUMMARY ==========")

print("Total bus stops (nodes):", G.number_of_nodes())
print("Total connections (edges):", G.number_of_edges())
print("Unique routes:", edge_data["route_id"].nunique())

print(
    "Average travel time per edge:",
    round(edge_data["travel_time_minutes"].mean(), 2),
    "minutes"
)

print("\nSample graph connections:")

for u, v, key, data in list(G.edges(keys=True, data=True))[:10]:
    print(
        f"{u} -> {v} | Route: {key} | "
        f"Time: {data['travel_time_minutes']:.2f} min | "
        f"Trips: {data['trip_count']}"
    )

print("\nGraph saved successfully:", output_path)
