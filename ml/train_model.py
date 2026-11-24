
import pandas as pd
import joblib

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline

print("Loading training and testing data...")

train = pd.read_csv("data/processed/train.csv")
test = pd.read_csv("data/processed/test.csv")

# Features used by the model
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

# Remove rows with missing required values
train = train.dropna(subset=features + [target])
test = test.dropna(subset=features + [target])

X_train = train[features]
y_train = train[target]

X_test = test[features]
y_test = test[target]

print("Training records:", len(X_train))
print("Testing records:", len(X_test))

# Convert route names into numerical features
preprocessor = ColumnTransformer(
    transformers=[
        (
            "route_encoder",
            OneHotEncoder(handle_unknown="ignore"),
            ["route"]
        )
    ],
    remainder="passthrough"
)

# Create Random Forest model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        (
            "regressor",
            RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
        )
    ]
)

print("\nTraining Random Forest model...")
model.fit(X_train, y_train)

# Save trained model
joblib.dump(model, "data/predictions/random_forest_model.pkl")

print("\nModel training completed!")
print("Model saved successfully!")
print("Location: data/predictions/random_forest_model.pkl")
