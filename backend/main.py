
import sys
import os

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
from ml.route_prediction import predict_gtfs_route
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

from routing.journey_planner import plan_journey

app = FastAPI(title="MetaFora API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JourneyRequest(BaseModel):
    source: str
    destination: str
    date: str
    hour: int
    preference: str = "balanced"


@app.get("/")
def home():
    return {"message": "Welcome to MetaFora API"}


@app.get("/health")
def health():
    return {"status": "running"}


@app.get("/stops")
def get_stops():
    stops = pd.read_csv("data/raw/stops.txt")
    return stops[["stop_id", "stop_name", "stop_lat", "stop_lon"]].to_dict(
        orient="records"
    )
@app.get("/search-stops")
def search_stops(name: str):
    stops = pd.read_csv("data/raw/stops.txt")

    result = stops[
        stops["stop_name"].str.contains(
            name, case=False, na=False
        )
    ]

    return result[
        ["stop_id", "stop_name", "stop_lat", "stop_lon"]
    ].head(20).to_dict(orient="records")

@app.get("/routes")
def get_routes():
    routes = pd.read_csv("data/raw/routes.txt")
    return routes[
        ["route_id", "route_short_name", "route_long_name"]
    ].to_dict(orient="records")


@app.post("/plan-journey")
def journey(request: JourneyRequest):
    if request.preference not in ["fastest", "least_crowded", "balanced"]:
        return {"error": "Invalid preference"}

    result = plan_journey(
        source=request.source,
        destination=request.destination,
        date=request.date,
        hour=request.hour,
        preference=request.preference
    )

    if result is None:
        return {"error": "No journey found"}

    return result    

@app.get("/predict-crowding/{route_id}")
def predict_crowding(route_id: str, date: str, hour: int):

    result = predict_gtfs_route(route_id, date, hour)

    if result is None:
        return {"error": "No prediction available"}

    return result
