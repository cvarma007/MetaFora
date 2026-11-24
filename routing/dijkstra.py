
import joblib
import heapq


def dijkstra(G, source, destination):
    if source not in G or destination not in G:
        return None

    distances = {node: float("inf") for node in G.nodes}
    previous = {}

    distances[source] = 0
    priority_queue = [(0, source)]

    while priority_queue:
        current_distance, current_node = heapq.heappop(priority_queue)

        if current_distance > distances[current_node]:
            continue

        if current_node == destination:
            break

        for neighbor in G.successors(current_node):
            edges = G.get_edge_data(current_node, neighbor)

            best_edge = min(
                edges.values(),
                key=lambda edge: edge["travel_time_minutes"]
            )

            travel_time = best_edge["travel_time_minutes"]
            new_distance = current_distance + travel_time

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = (current_node, best_edge["route_id"])

                heapq.heappush(
                    priority_queue,
                    (new_distance, neighbor)
                )

    if distances[destination] == float("inf"):
        return None

    path = []
    current = destination

    while current != source:
        parent, route_id = previous[current]
        path.append({
            "stop_id": current,
            "route_id": route_id
        })
        current = parent

    path.append({
        "stop_id": source,
        "route_id": None
    })

    path.reverse()

    return {
        "path": path,
        "total_time": round(distances[destination], 2)
    }


if __name__ == "__main__":
    G = joblib.load("data/processed/metafora_bus_graph.pkl")

    result = dijkstra(G, "2", "4470")

    if result:
        print("Shortest path:")

        for item in result["path"]:
            stop_id = item["stop_id"]
            stop_name = G.nodes[stop_id]["name"]

            print(
                stop_id,
                "->",
                stop_name,
                "| Route:",
                item["route_id"]
            )

        print("\nTotal travel time:", result["total_time"], "minutes")
    else:
        print("No route found.")
