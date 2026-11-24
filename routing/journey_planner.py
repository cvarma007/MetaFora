import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import joblib
import heapq
from ml.route_prediction import predict_gtfs_route

G = joblib.load("data/processed/metafora_bus_graph.pkl")

import pandas as pd

stops_df = pd.read_csv("data/raw/stops.txt")

STOP_NAMES = dict(
    zip(stops_df["stop_id"].astype(str), stops_df["stop_name"])
)
STOP_COORDS = {
    str(row["stop_id"]): {
        "latitude": row["stop_lat"],
        "longitude": row["stop_lon"]
    }
    for _, row in stops_df.iterrows()
}
from math import radians, sin, cos, sqrt, atan2

def calculate_distance(coord1, coord2):
    lat1 = radians(coord1["latitude"])
    lon1 = radians(coord1["longitude"])
    lat2 = radians(coord2["latitude"])
    lon2 = radians(coord2["longitude"])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return 6371 * c
def calculate_fare(distance_km):
    if distance_km <= 4:
        return {
            "non_ac": 5,
            "ac": 10
        }
    elif distance_km <= 8:
        return {
            "non_ac": 10,
            "ac": 15
        }
    elif distance_km <= 10:
        return {
            "non_ac": 10,
            "ac": 20
        }
    elif distance_km <= 12:
        return {
            "non_ac": 15,
            "ac": 20
        }
    else:
        return {
            "non_ac": 15,
            "ac": 25
        }
def plan_journey(source, destination, date, hour, preference="balanced"):

    if source not in G or destination not in G:
        return None

    distances = {}
    previous = {}
    predictions = {}

    start_state = (source, None)
    distances[start_state] = 0

    queue = [(0, source, None)]
    final_state = None

    while queue:
        current_cost, stop, current_route = heapq.heappop(queue)
        state = (stop, current_route)

        if current_cost > distances.get(state, float("inf")):
            continue

        if stop == destination:
            final_state = state
            break

        for neighbor in G.successors(stop):
            edges = G.get_edge_data(stop, neighbor)

            for edge in edges.values():
                route_id = str(edge["route_id"])
                travel_time = edge["travel_time_minutes"]

                if route_id not in predictions:
                    predictions[route_id] = predict_gtfs_route(
                        route_id, date, hour
                    )

                prediction = predictions[route_id]

                demand = (
                    prediction["predicted_demand"]
                    if prediction else 10
                )

                if preference == "fastest":
                    crowd_penalty = 0
                elif preference == "least_crowded":
                    crowd_penalty = demand * 3
                else:
                    crowd_penalty = demand * 0.5

                transfer_penalty = (
                    5 if current_route is not None
                    and current_route != route_id else 0
                )

                edge_cost = (
                    travel_time + crowd_penalty + transfer_penalty
                )

                new_cost = current_cost + edge_cost
                next_state = (neighbor, route_id)

                if new_cost < distances.get(next_state, float("inf")):
                    distances[next_state] = new_cost
                    previous[next_state] = (
                        state, route_id, travel_time
                    )

                    heapq.heappush(
                        queue,
                        (new_cost, neighbor, route_id)
                    )

    if final_state is None:
        return None

    segments = []
    current = final_state
    total_time = 0
    total_distance = 0

    while current != start_state:
        parent, route_id, travel_time = previous[current]
        segment_distance = calculate_distance(
            STOP_COORDS[parent[0]],
            STOP_COORDS[current[0]]
        )

        total_distance += segment_distance
        prediction = predictions.get(route_id)

        segments.append({
            "from_stop": parent[0],
            "from_stop_name": STOP_NAMES.get(parent[0], "Unknown"),
            "to_stop": current[0],
            "to_stop_name": STOP_NAMES.get(current[0], "Unknown"),
            "route_id": route_id,
            "travel_time": round(travel_time, 2),
            "distance_km": round(segment_distance, 2),
            "predicted_demand": (
                prediction["predicted_demand"] if prediction else None
            ),
            "crowd_level": (
                prediction["crowd_level"] if prediction else "Unknown"
            ),
            "from_coordinates": STOP_COORDS.get(parent[0]),
            "to_coordinates": STOP_COORDS.get(current[0]),
        })

        total_time += travel_time
        current = parent

    segments.reverse()

    fare = calculate_fare(total_distance)

    return {
        "source": source,
        "destination": destination,
        "preference": preference,
        "total_travel_time": round(total_time, 2),
        "total_distance_km": round(total_distance, 2),
        "route_score": round(distances[final_state], 2),
        "estimated_fare": {
            "non_ac": fare["non_ac"],
            "ac": fare["ac"],
            "currency": "INR"
        },
        "segments": segments
    }


if __name__ == "__main__":
    for preference in ["fastest", "least_crowded", "balanced"]:

        result = plan_journey(
            source="1",
            destination="4470",
            date="2026-11-25",
            hour=9,
            preference=preference
        )

        print("\n==========", preference.upper(), "==========")
        print(result)
