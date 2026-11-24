
import pandas as pd

input_file = "data/processed/demand_with_lags.csv"

print("Loading historical demand data...")

df = pd.read_csv(input_file)

# Convert date column
df["date"] = pd.to_datetime(df["date"])

# Remove records without previous-week demand
df = df.dropna(subset=["lag_168_hour"])

# Training period: October 8 to October 24
train = df[
    (df["date"] >= "2026-10-08") &
    (df["date"] <= "2026-10-24")
].copy()

# Testing period: October 25 to October 31
test = df[
    (df["date"] >= "2026-10-25") &
    (df["date"] <= "2026-10-31")
].copy()

# Save datasets
train.to_csv(
    "data/processed/train.csv",
    index=False
)

test.to_csv(
    "data/processed/test.csv",
    index=False
)

print("\nDataset preparation completed!")

print("\nTraining records:", len(train))
print("Testing records:", len(test))

print("\nTraining date range:")
print(train["date"].min(), "to", train["date"].max())

print("\nTesting date range:")
print(test["date"].min(), "to", test["date"].max())

print("\nFiles saved:")
print("data/processed/train.csv")
print("data/processed/test.csv")
