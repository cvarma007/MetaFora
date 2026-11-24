
import pandas as pd
import numpy as np
import joblib

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

print("Loading test data and trained model...")

test = pd.read_csv("data/processed/test.csv")

model = joblib.load(
    "data/predictions/random_forest_model.pkl"
)

features = [
    "route",
    "hour",
    "day_of_week",
    "is_weekend",
    "lag_1_hour",
    "lag_24_hour",
    "lag_168_hour"
]

target = "passenger_demand"

# Keep records with complete features
test = test.dropna(subset=features + [target])

X_test = test[features]
y_test = test[target]

print("Testing records:", len(test))

# Generate model predictions
print("\nGenerating predictions...")

predictions = model.predict(X_test)

# Passenger demand cannot be negative
predictions = np.maximum(predictions, 0)

# Calculate Random Forest metrics
mae = mean_absolute_error(y_test, predictions)

rmse = np.sqrt(
    mean_squared_error(y_test, predictions)
)

r2 = r2_score(y_test, predictions)

# Calculate previous-week baseline metrics
baseline = test["lag_168_hour"]

baseline_mae = mean_absolute_error(y_test, baseline)

baseline_rmse = np.sqrt(
    mean_squared_error(y_test, baseline)
)

print("\n========== RANDOM FOREST RESULTS ==========")
print("MAE:", round(mae, 3))
print("RMSE:", round(rmse, 3))
print("R2 Score:", round(r2, 4))

print("\n========== PREVIOUS-WEEK BASELINE ==========")
print("MAE:", round(baseline_mae, 3))
print("RMSE:", round(baseline_rmse, 3))

print("\n========== COMPARISON ==========")

if mae < baseline_mae:
    print("Random Forest has lower MAE than the baseline.")
else:
    print("Random Forest does not beat the baseline on MAE.")

# Save actual and predicted values
results = test[["route", "date", "hour"]].copy()
results["actual_demand"] = y_test.values
results["predicted_demand"] = predictions
results["baseline_demand"] = baseline.values

results.to_csv(
    "data/predictions/test_predictions.csv",
    index=False
)

print("\nEvaluation completed!")
print("Predictions saved to data/predictions/test_predictions.csv")
