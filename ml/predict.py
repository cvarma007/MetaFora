
import pandas as pd
import joblib

MODEL_PATH = "data/predictions/random_forest_model.pkl"
DATA_PATH = "data/processed/demand_with_lags.csv"

model = joblib.load(MODEL_PATH)

# Limit parallel workers to avoid thread overload
if hasattr(model, "get_params"):
    params = {
        key: 1
        for key in model.get_params()
        if key.endswith("n_jobs")
    }
    if params:
        model.set_params(**params)
elif hasattr(model, "n_jobs"):
    model.n_jobs = 1
history = pd.read_csv(DATA_PATH)

history["date"] = pd.to_datetime(history["date"])

history["period"] = (
    history["date"] + pd.to_timedelta(history["hour"], unit="h")
)
FORECAST_CACHE = {}


def predict_demand(route, date, hour):
    target = pd.to_datetime(date) + pd.Timedelta(hours=hour)

    if hour < 0 or hour > 23:
        raise ValueError("Hour must be between 0 and 23")

    route_history = history[
        history["route"].astype(str) == str(route)
    ].copy()

    if route_history.empty:
        return None

    route_history = route_history.sort_values("period")

    latest_period = route_history["period"].max()

    # Historical prediction: use the actual stored lag features
    if target <= latest_period:
        row = route_history[route_history["period"] == target]

        if row.empty:
            return None

        input_data = row[[
            "route", "hour", "day_of_week", "is_weekend",
            "lag_1_hour", "lag_24_hour", "lag_168_hour"
        ]].fillna(0)

        return max(0, round(float(model.predict(input_data)[0]), 2))

    # Store historical demand by timestamp
   
        # Select the latest historical record for the same weekday and hour
    matching_rows = route_history[
        (route_history["hour"] == hour) &
        (route_history["day_of_week"] == target.day_of_week)
    ]

    if matching_rows.empty:
        matching_rows = route_history[
            route_history["hour"] == hour
        ]

    if matching_rows.empty:
        return None

    row = matching_rows.sort_values("period").iloc[[-1]]

    input_data = row[[
        "route", "hour", "day_of_week", "is_weekend",
        "lag_1_hour", "lag_24_hour", "lag_168_hour"
    ]].copy()

    input_data["day_of_week"] = target.day_of_week
    input_data["is_weekend"] = int(target.day_of_week >= 5)
    input_data = input_data.fillna(0)
    prediction = model.predict(input_data)[0]

    return max(0, round(float(prediction), 2))
def classify_crowd(demand):
    if demand < 5:
        return "Low"
    elif demand < 15:
        return "Moderate"
    else:
        return "High"
