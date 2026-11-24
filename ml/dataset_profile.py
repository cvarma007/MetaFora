
import pandas as pd
from pathlib import Path

file_path = Path("data/raw/October-Delhi.csv")

chunk_size = 100000

total_rows = 0
total_passengers = 0

missing_values = {}
unique_values = {
    "route": set(),
    "start_stop_name": set(),
    "end_stop_name": set(),
    "vehicle_number": set(),
    "ticket_type_id": set()
}

min_date = None
max_date = None

min_passengers = float("inf")
max_passengers = float("-inf")

print("Analysing the complete dataset...\n")

for chunk in pd.read_csv(file_path, chunksize=chunk_size):

    total_rows += len(chunk)

    total_passengers += chunk["passenger_count"].sum()

    # Count missing values
    for column in chunk.columns:
        missing_values[column] = (
            missing_values.get(column, 0)
            + chunk[column].isna().sum()
        )

    # Count unique values
    for column in unique_values:
        unique_values[column].update(
            chunk[column].dropna().unique()
        )

    # Find passenger count range
    min_passengers = min(
        min_passengers,
        chunk["passenger_count"].min()
    )

    max_passengers = max(
        max_passengers,
        chunk["passenger_count"].max()
    )

    # Analyse ticket dates
    dates = pd.to_datetime(
        chunk["created_at"],
        errors="coerce",
        utc=True
    )

    chunk_min = dates.min()
    chunk_max = dates.max()

    if pd.notna(chunk_min):
        min_date = chunk_min if min_date is None else min(min_date, chunk_min)

    if pd.notna(chunk_max):
        max_date = chunk_max if max_date is None else max(max_date, chunk_max)

print("========== DATASET SUMMARY ==========")

print("Total records:", total_rows)
print("Total passengers represented by tickets:", total_passengers)

print("\n========== DATE RANGE ==========")
print("Earliest ticket:", min_date)
print("Latest ticket:", max_date)

print("\n========== UNIQUE VALUES ==========")
for column, values in unique_values.items():
    print(column, ":", len(values))

print("\n========== MISSING VALUES ==========")
for column, count in missing_values.items():
    percentage = (count / total_rows) * 100
    print(f"{column}: {count} ({percentage:.2f}%)")

print("\n========== PASSENGER COUNT ==========")
print("Minimum:", min_passengers)
print("Maximum:", max_passengers)

print("\nAnalysis completed!")
