
import joblib
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.route_prediction import predict_gtfs_route


def get_route_cost(
    travel_time,
    route_id,
    date,
    hour,
    preference="balanced"
):
    prediction = predict_gtfs_route(route_id, date, hour)

    if prediction is None:
        crowd_penalty = 5
        crowd_level = "Unknown"
        demand = None
    else:
        demand = prediction["predicted_demand"]
        crowd_level = prediction["crowd_level"]
        crowd_penalty = demand * 0.5

    if preference == "fastest":
        cost = travel_time
    elif preference == "least_crowded":
        cost = travel_time + crowd_penalty * 3
    else:
        cost = travel_time + crowd_penalty

    return {
        "route_id": str(route_id),
        "travel_time": round(travel_time, 2),
        "predicted_demand": demand,
        "crowd_level": crowd_level,
        "cost": round(cost, 2)
    }


if __name__ == "__main__":
    for preference in ["fastest", "least_crowded", "balanced"]:
        result = get_route_cost(
            travel_time=15,
            route_id="2171",
            date="2026-11-25",
            hour=9,
            preference=preference
        )

        print("\nPreference:", preference)
        print(result)
