
import pandas as pd
from pathlib import Path

input_file = Path("data/raw/October-Delhi.csv")
output_file = Path("data/processed/October-Delhi-cleaned.csv")

chunk_size = 100000
first_chunk = True

total_records = 0
invalid_dates = 0
invalid_passengers = 0
invalid_fares = 0

print("Starting data cleaning...\n")

for chunk in pd.read_csv(input_file, chunksize=chunk_size):

    # 1. Remove unnecessary spaces from text columns
    text_columns = [
        "vehicle_number",
        "route",
        "start_stop_name",
        "end_stop_name"
    ]

    for column in text_columns:
        chunk[column] = chunk[column].str.strip()

    # 2. Convert timestamps to Indian Standard Time
    dates = pd.to_datetime(
        chunk["created_at"],
        errors="coerce",
        utc=True
    )

    invalid_dates += dates.isna().sum()

    dates = dates.dt.tz_convert("Asia/Kolkata")

    chunk["created_at"] = dates.astype("string")

    # 3. Check passenger counts
    invalid_passengers += (
        chunk["passenger_count"].isna()
        | (chunk["passenger_count"] <= 0)
    ).sum()

    # 4. Check ticket fares
    invalid_fares += (
        chunk["amount"].isna()
        | (chunk["amount"] < 0)
    ).sum()

    # 5. Save the cleaned chunk
    chunk.to_csv(
        output_file,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False
    )

    total_records += len(chunk)
    first_chunk = False

    print(f"Processed {total_records:,} records")

print("\n========== CLEANING SUMMARY ==========")
print("Total records processed:", total_records)
print("Invalid timestamps:", invalid_dates)
print("Invalid passenger counts:", invalid_passengers)
print("Invalid fares:", invalid_fares)

print("\nCleaned dataset saved to:", output_file)
print("Data cleaning completed!")
