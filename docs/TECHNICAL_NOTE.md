# MetaFora – Technical Note

## 1. Project Overview

MetaFora is a crowd-aware bus journey planner that combines graph-based route optimization and machine-learning-based passenger demand prediction to recommend suitable bus journeys.

The system provides three journey preferences:
- **Fastest:** Prioritizes lower travel time.
- **Least Crowded:** Gives greater importance to predicted passenger demand.
- **Balanced:** Considers both travel time and predicted crowd levels.

## 2. Data Sources and Processing

The project uses Delhi bus ticketing data and General Transit Feed Specification (GTFS) data.

The data is processed to generate:
- Hourly passenger demand records.
- Route and stop mappings.
- Historical demand features and lag features.
- A bus network graph for route planning.

## 3. Machine Learning Methodology

A Random Forest regression model is used to estimate passenger demand.

**Input features include:**
- Route information.
- Time and weekday information.
- Historical demand.
- Lag-based demand features.

**Model evaluation results:**

| Metric | Result |
|---|---:|
| MAE | 2.651 |
| RMSE | 4.581 |
| R² Score | 0.794 |

The model is evaluated using a held-out test dataset. These results describe performance on the available dataset and do not guarantee real-world prediction accuracy.

## 4. Route Optimization

The bus network is represented using a NetworkX graph.

The graph contains:
- 6,862 nodes.
- 80,802 route-specific edges.
- 2,574 routes.

The journey planner evaluates possible paths using:
- Travel time.
- Predicted passenger demand.
- Transfer penalties.

A transfer penalty of five minutes is applied when changing routes. Different scoring weights are used for the three journey preferences.

## 5. Distance and Fare Estimation

The Haversine formula is used to estimate the geographical distance between consecutive bus stops using their latitude and longitude coordinates.

Fare estimates are calculated using distance-based fare brackets for AC and Non-AC services.

These are approximate estimates and may differ from actual transport fares.

## 6. System Architecture

The application consists of three main components:

1. **Frontend:** React and Vite provide the user interface, stop search, journey selection and interactive map.
2. **Backend:** FastAPI handles API requests, journey planning and prediction operations.
3. **ML and Routing Modules:** Scikit-learn performs demand prediction, while NetworkX supports graph-based route planning.

Leaflet and OpenStreetMap are used to display recommended journeys.

## 7. Assumptions

- Historical ticketing records are used as a proxy for passenger demand.
- Historical demand patterns provide useful information for estimating future demand.
- Stop coordinates represent the geographical locations of bus stops.
- The fare calculation uses predefined distance-based brackets.
- A fixed transfer penalty is used during route evaluation.

## 8. Limitations

- Predictions represent estimated demand, not exact real-time passenger occupancy.
- The model is trained on a limited historical period and may not capture seasonal or unusual travel patterns.
- The current prediction approach uses historical records and does not provide live passenger updates.
- Haversine distance is a straight-line geographical estimate, not actual road distance.
- Fare estimates may differ from official or updated fares.
- Route recommendations depend on the available GTFS network and processed data.

## 9. Future Enhancements

- Integration with live bus tracking systems.
- Real-time passenger occupancy information.
- More extensive historical training data.
- Improved fare estimation using official fare information.
- Public deployment and mobile accessibility.