
import pandas as pd

from ml.predict import (
    predict_demand,
    classify_crowd,
    history
)

MAPPING_PATH = "data/processed/gtfs_route_mapping.csv"
mapping = pd.read_csv(MAPPING_PATH)


def predict_gtfs_route(route_id, date, hour):

    matched = mapping[
        mapping["route_id"].astype(str) == str(route_id)
    ]

    if matched.empty:
        return None

    route_name = matched.iloc[0]["route_short_name"]

    route_history = history[
        history["route"].astype(str) == str(route_name)
    ]

    if route_history.empty:
        return None

    demand = predict_demand(route_name, date, hour)

    if demand is None:
        return None

    record_count = len(route_history)
    observed_days = route_history["date"].nunique()

    if record_count >= 500:
        coverage_status = "High"
    elif record_count >= 100:
        coverage_status = "Moderate"
    else:
        coverage_status = "Limited"

    return {
        "route_id": str(route_id),
        "route_name": route_name,
        "predicted_demand": demand,
        "crowd_level": classify_crowd(demand),
        "data_coverage": {
            "historical_records": int(record_count),
            "observed_days": int(observed_days),
            "historical_start_date": str(
                route_history["date"].min().date()
            ),
            "historical_end_date": str(
                route_history["date"].max().date()
            ),
            "coverage_status": coverage_status
        }
    }
