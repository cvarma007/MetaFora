
import pandas as pd
from pathlib import Path

# Find CSV files inside the raw data folder
raw_folder = Path("data/raw")
csv_files = list(raw_folder.rglob("*.csv"))

if not csv_files:
    print("No CSV file found. Check the extraction.")
else:
    file_path = csv_files[0]

    print("Dataset found:", file_path)
    print("\nFile size:", round(file_path.stat().st_size / (1024 * 1024), 2), "MB")

    # Read only the first 5 records
    df = pd.read_csv(file_path, nrows=5)

    print("\nCOLUMN NAMES:")
    print(df.columns.tolist())

    print("\nDATA TYPES:")
    print(df.dtypes)

    print("\nFIRST 5 RECORDS:")
    print(df.to_string(index=False))
