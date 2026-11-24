# MetaFora 

### Crowd-Aware Bus Journey Planner

MetaFora is a smart bus journey planning application designed to help commuters find suitable bus journeys using route optimization and machine-learning-based crowd predictions.

## Features

- **Smart Stop Search:** Search and select bus stops using autocomplete.
- **Journey Planning:** Find routes between selected bus stops.
- **Multiple Preferences:** Choose Fastest, Least Crowded, or Balanced journeys.
- **Crowd Prediction:** Estimate passenger demand using a Random Forest model.
- **Fare Estimation:** View estimated AC and Non-AC fares.
- **Distance Calculation:** Calculate approximate journey distance.
- **Interactive Map:** Visualize the recommended route and bus stops using Leaflet and OpenStreetMap.

## Technology Stack

| Component | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn, Pandas, NumPy |
| Route Optimization | NetworkX |
| Map | Leaflet, React-Leaflet, OpenStreetMap |
| Model Storage | Joblib, Git LFS |

## Project Structure

```text
MetaFora/
├── backend/
├── data/
│   ├── predictions/
│   ├── processed/
│   └── raw/
├── docs/
├── frontend/
├── ml/
├── routing/
├── requirements.txt
├── README.md
└── .gitignore
```

## Prerequisites

- Python
- Node.js and npm
- Git
- Git LFS

## Installation and Setup

### 1. Clone the repository

```bash
git lfs install
git clone YOUR_GITHUB_REPOSITORY_URL
cd MetaFora
```

### 2. Set up the Python backend

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Start the backend

From the project root directory:

```bash
uvicorn backend.main:app --reload
```

Backend URL:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 4. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the frontend URL displayed by Vite, usually:

`http://localhost:5173`

## Application Workflow

1. Open the MetaFora web application.
2. Search for the source and destination bus stops.
3. Select a journey preference.
4. Request a journey recommendation.
5. View the suggested route, estimated travel time, distance, fare and crowd information.
6. Explore the journey using the interactive route map.

## Technical Overview

MetaFora combines graph-based route optimization with machine-learning-based passenger demand prediction.

The routing component uses a bus network graph to identify possible journeys. The machine-learning component uses a Random Forest model to estimate passenger demand. The journey planner considers travel time, predicted crowd levels and transfer penalties when evaluating routes.

## Important Notes

- The crowd prediction represents estimated passenger demand, not exact real-time bus occupancy.
- Fare values are estimates and may differ from actual transport fares.
- Distance calculations based on stop coordinates may differ from actual road distances.
- Model and graph files required at runtime must be available in their expected project paths.
- The application currently uses a local development configuration.

## Future Improvements

- Real-time bus tracking.
- Live passenger occupancy integration.
- Improved fare accuracy.
- Online deployment and public access.

---

**MetaFora — Smarter Routes, Better Journeys.**
