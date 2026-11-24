
import networkx as nx
import joblib

# Load the saved graph
G = joblib.load("data/processed/metafora_bus_graph.pkl")

# Choose two stops for testing
source = "1"
destination = "4470"

print("Source stop:", source)
print("Destination stop:", destination)

try:
    # Find shortest path based on scheduled travel time
    path = nx.shortest_path(
        G,
        source=source,
        target=destination,
        weight="travel_time_minutes"
    )

    print("\nPath found!")

    print("\nStop sequence:")
    for stop in path:
        print(stop, "->", G.nodes[stop]["name"])

    # Calculate total travel time
    total_time = 0

    for i in range(len(path) - 1):
        edges = G.get_edge_data(path[i], path[i + 1])

        # Choose the fastest available route-specific edge
        best_edge = min(
            edges.values(),
            key=lambda edge: edge["travel_time_minutes"]
        )

        total_time += best_edge["travel_time_minutes"]

        print(
            f"{path[i]} -> {path[i+1]} | "
            f"Route: {best_edge['route_id']} | "
            f"Time: {best_edge['travel_time_minutes']:.2f} min"
        )

    print("\nTotal estimated travel time:", round(total_time, 2), "minutes")

except nx.NetworkXNoPath:
    print("\nNo path exists between these stops.")

except nx.NodeNotFound as error:
    print("\nInvalid stop ID:", error)
