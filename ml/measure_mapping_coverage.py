
import pandas as pd
import re

def normalize_series(series):
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"[^A-Z0-9]", "", regex=True)
    )


# Load GTFS names
routes = pd.read_csv("data/raw/routes.txt", dtype=str)
stops = pd.read_csv("data/raw/stops.txt", dtype=str)

gtfs_routes = set(normalize_series(routes["route_short_name"]))
gtfs_stops = set(normalize_series(stops["stop_name"]))

# Counters
total_records = 0
total_passengers = 0

matched_route_records = 0
matched_route_passengers = 0

matched_start_records = 0
matched_end_records = 0
matched_both_stop_records = 0

matched_start_passengers = 0
matched_end_passengers = 0
matched_both_stop_passengers = 0

# Read ticketing data in chunks
for chunk in pd.read_csv(
    "data/processed/October-Delhi-cleaned.csv",
    usecols=[
        "route",
        "start_stop_name",
        "end_stop_name",
        "passenger_count"
    ],
    chunksize=100000
):

    route_names = normalize_series(chunk["route"])
    start_names = normalize_series(chunk["start_stop_name"])
    end_names = normalize_series(chunk["end_stop_name"])

    passengers = pd.to_numeric(
        chunk["passenger_count"],
        errors="coerce"
    ).fillna(0)

    route_match = route_names.isin(gtfs_routes)
    start_match = start_names.isin(gtfs_stops)
    end_match = end_names.isin(gtfs_stops)
    both_stops_match = start_match & end_match

    total_records += len(chunk)
    total_passengers += passengers.sum()

    matched_route_records += route_match.sum()
    matched_route_passengers += passengers[route_match].sum()

    matched_start_records += start_match.sum()
    matched_end_records += end_match.sum()
    matched_both_stop_records += both_stops_match.sum()

    matched_start_passengers += passengers[start_match].sum()
    matched_end_passengers += passengers[end_match].sum()
    matched_both_stop_passengers += passengers[both_stops_match].sum()


def report(label, records, passenger_count):
    print(f"\n{label}")
    print("Matched records:", f"{records:,}")
    print("Record coverage:", f"{records / total_records * 100:.2f}%")
    print("Matched passengers:", f"{passenger_count:,.0f}")
    print(
        "Passenger coverage:",
        f"{passenger_count / total_passengers * 100:.2f}%"
    )


print("\n========== MAPPING COVERAGE ==========")
print("Total records:", f"{total_records:,}")
print("Total passengers:", f"{total_passengers:,.0f}")

report(
    "ROUTE MATCHING",
    matched_route_records,
    matched_route_passengers
)

report(
    "START STOP MATCHING",
    matched_start_records,
    matched_start_passengers
)

report(
    "END STOP MATCHING",
    matched_end_records,
    matched_end_passengers
)

report(
    "BOTH START AND END STOPS MATCH",
    matched_both_stop_records,
    matched_both_stop_passengers
)

print("\nCoverage analysis completed!")
