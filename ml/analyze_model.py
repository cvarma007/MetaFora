
import pandas as pd
import joblib

print("Loading model and predictions...")

# Load trained model and test predictions
model = joblib.load(
    "data/predictions/random_forest_model.pkl"
)

results = pd.read_csv(
    "data/predictions/test_predictions.csv"
)

# Calculate prediction errors
results["absolute_error"] = (
    results["actual_demand"] -
    results["predicted_demand"]
).abs()

# --------------------------------
# 1. FEATURE IMPORTANCE
# --------------------------------

print("\n========== FEATURE IMPORTANCE ==========")

preprocessor = model.named_steps["preprocessor"]
forest = model.named_steps["regressor"]

feature_names = preprocessor.get_feature_names_out()
importances = forest.feature_importances_

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
})

# Combine all individual route categories
importance_df["feature_group"] = importance_df["feature"].apply(
    lambda name: (
        "route (all categories)"
        if name.startswith("route_encoder__")
        else name.replace("remainder__", "")
    )
)

grouped_importance = (
    importance_df.groupby("feature_group")["importance"]
    .sum()
    .sort_values(ascending=False)
)

print(grouped_importance.round(4))

grouped_importance.to_csv(
    "data/predictions/feature_importance.csv"
)

# --------------------------------
# 2. PREDICTION ERROR ANALYSIS
# --------------------------------

print("\n========== PREDICTION ERROR ANALYSIS ==========")

print(
    "Overall MAE:",
    round(results["absolute_error"].mean(), 3)
)

# Calculate error for each hour
hour_errors = (
    results.groupby("hour")["absolute_error"]
    .mean()
    .sort_values(ascending=False)
)

print("\nAverage error by hour:")
print(hour_errors.round(3))

hour_errors.to_csv(
    "data/predictions/error_by_hour.csv"
)

# Display 10 largest prediction errors
print("\n========== TOP 10 LARGEST ERRORS ==========")

print(
    results.nlargest(10, "absolute_error")[
        [
            "route",
            "date",
            "hour",
            "actual_demand",
            "predicted_demand",
            "absolute_error"
        ]
    ].to_string(index=False)
)

print("\nAnalysis completed!")
print("Feature importance and error reports saved.")
