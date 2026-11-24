
import pandas as pd

input_file = "data/processed/hourly_demand.csv"
output_file = "data/processed/demand_with_lags.csv"

print("Loading hourly demand data...")

df = pd.read_csv(input_file)

# Create a timestamp using the date and hour
df["period"] = (
    pd.to_datetime(df["date"])
    + pd.to_timedelta(df["hour"], unit="h")
)

df = df.sort_values(["route", "period"])

# Find the earliest available time in the dataset
first_period = df["period"].min()

# Create historical demand features
lag_features = {
    "lag_1_hour": 1,
    "lag_24_hour": 24,
    "lag_168_hour": 168
}

for feature_name, hours in lag_features.items():

    print("Creating", feature_name)

    # Prepare previous demand records
    previous = df[["route", "period", "passenger_demand"]].copy()

    # Match previous records with their future prediction time
    previous["period"] += pd.Timedelta(hours=hours)

    previous = previous.rename(
        columns={"passenger_demand": feature_name}
    )

    # Match records by route and timestamp
    df = df.merge(
        previous,
        on=["route", "period"],
        how="left",
        validate="one_to_one"
    )

    # If the previous time is within our dataset,
    # no ticket record means zero recorded ticket demand.
    previous_period = df["period"] - pd.Timedelta(hours=hours)

    available = previous_period >= first_period

    df.loc[available, feature_name] = (
        df.loc[available, feature_name].fillna(0)
    )

# Remove temporary timestamp column
df = df.drop(columns=["period"])

# Save the new dataset
df.to_csv(output_file, index=False)

print("\nHistorical features created successfully!")
print("Total records:", len(df))
print("\nFirst 10 records:")
print(df.head(10))

print("\nMissing values in lag features:")
print(df[list(lag_features.keys())].isna().sum())

print("\nSaved to:", output_file)
