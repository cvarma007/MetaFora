import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Popup,
  useMap
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

import { useEffect, useState } from "react";
import {
  MapPin,
  Navigation,
  Clock,
  Users,
  Search,
  Bus,
  ArrowRight,
  Activity,
} from "lucide-react";
import "./App.css";

const API = "http://127.0.0.1:8000";

// BUS STOP AUTOCOMPLETE
function StopSearch({ label, icon, selected, setSelected, placeholder }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setQuery(selected ? selected.stop_name : "");
  }, [selected]);

  useEffect(() => {
    if (query.trim().length < 2 || selected?.stop_name === query) {
      setSuggestions([]);
      return;
    }

    const controller = new AbortController();

    const timer = setTimeout(async () => {
      try {
        setLoading(true);

        const response = await fetch(
          `${API}/search-stops?name=${encodeURIComponent(query)}`,
          { signal: controller.signal }
        );

        if (!response.ok) {
          throw new Error("Stop search failed");
        }

        const data = await response.json();

        // Remove duplicate stop names
        const uniqueStops = [
          ...new Map(
            data.map((stop) => [
              stop.stop_name.trim().toLowerCase(),
              stop,
            ])
          ).values(),
        ];

        setSuggestions(uniqueStops);
      } catch (error) {
        if (error.name !== "AbortError") {
          console.error(error);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }, 300);

    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, selected]);

  return (
    <div className="input-group stop-search">
      <label>
        {icon} {label}
      </label>

      <input
        value={query}
        onChange={(e) => {
          setQuery(e.target.value);
          setSelected(null);
        }}
        placeholder={placeholder}
        autoComplete="off"
      />

      {loading && (
        <small className="search-status">Searching...</small>
      )}

      {suggestions.length > 0 && (
        <div className="suggestions">
          {suggestions.map((stop) => (
            <button
              key={stop.stop_id}
              type="button"
              className="suggestion-item"
              onClick={() => {
                setSelected(stop);
                setQuery(stop.stop_name);
                setSuggestions([]);
              }}
            >
              <MapPin size={17} />
              <span>{stop.stop_name}</span>
            </button>
          ))}
        </div>
      )}

      {query.trim().length >= 2 &&
        !loading &&
        !selected &&
        suggestions.length === 0 && (
          <small className="search-status">
            No matching stops found.
          </small>
        )}

      {selected && (
        <small className="selected-status">
          Selected · Stop ID: {selected.stop_id}
        </small>
      )}
    </div>
  );
}

function JourneyMap({ segments }) {
  const map = useMap();

  const stops = [];

  segments.forEach((segment) => {
    if (stops.length === 0) {
      stops.push({
        id: segment.from_stop,
        name: segment.from_stop_name,
        coordinates: [
          segment.from_coordinates.latitude,
          segment.from_coordinates.longitude
        ]
      });
    }

    stops.push({
      id: segment.to_stop,
      name: segment.to_stop_name,
      coordinates: [
        segment.to_coordinates.latitude,
        segment.to_coordinates.longitude
      ]
    });
  });

  useEffect(() => {
    if (stops.length > 0) {
      map.fitBounds(
        stops.map((stop) => stop.coordinates),
        { padding: [40, 40] }
      );
    }
  }, [segments, map]);

  return (
    <>
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <Polyline
        positions={stops.map((stop) => stop.coordinates)}
        pathOptions={{
          color: "#087f68",
          weight: 5
        }}
      />

      {stops.map((stop, index) => (
        <CircleMarker
          key={`${stop.id}-${index}`}
          center={stop.coordinates}
          radius={index === 0 || index === stops.length - 1 ? 9 : 6}
          pathOptions={{
            color: "white",
            weight: 2,
            fillColor:
              index === 0
                ? "#087f68"
                : index === stops.length - 1
                ? "#e49b35"
                : "#2388d1",
            fillOpacity: 1
          }}
        >
          <Popup>
            <strong>{stop.name}</strong>
            <br />
            {index === 0
              ? "Starting point"
              : index === stops.length - 1
              ? "Destination"
              : "Intermediate stop"}
          </Popup>
        </CircleMarker>
      ))}
    </>
  );
}

// MAIN APPLICATION
function App() {
  const [source, setSource] = useState(null);
  const [destination, setDestination] = useState(null);
  const [preference, setPreference] = useState("Balanced");

  const [journey, setJourney] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // FIND JOURNEY USING FASTAPI
  const findRoute = async () => {
    if (!source || !destination) {
      setError("Please select both bus stops from the suggestions.");
      return;
    }

    if (source.stop_id === destination.stop_id) {
      setError("Starting point and destination cannot be the same.");
      return;
    }

    setLoading(true);
    setError("");
    setJourney(null);

    const now = new Date();

    const date = [
      now.getFullYear(),
      String(now.getMonth() + 1).padStart(2, "0"),
      String(now.getDate()).padStart(2, "0"),
    ].join("-");

    const preferenceValue = {
      Fastest: "fastest",
      "Least Crowded": "least_crowded",
      Balanced: "balanced",
    }[preference];

    try {
      const response = await fetch(`${API}/plan-journey`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          source: String(source.stop_id),
          destination: String(destination.stop_id),
          date: date,
          hour: now.getHours(),
          preference: preferenceValue,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Unable to plan your journey."
        );
      }

      if (!data.segments || data.segments.length === 0) {
        throw new Error("No journey segments were returned.");
      }

      setJourney(data);
    } catch (err) {
      setError(
        err.message || "Could not connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      {/* NAVBAR */}
      <nav className="navbar">
        <div className="logo">
          <div className="logo-icon">
            <Bus size={23} />
          </div>
          <span>
            Meta<span className="highlight">Fora</span>
          </span>
        </div>

        <div className="nav-links">
          <a href="#home">Home</a>
          <a href="#planner">Journey Planner</a>
          <a href="#about">About</a>
        </div>
        <div>
          <MapPin />
          <strong>
            {Number(journey?.total_distance_km ?? 0).toFixed(2)} km
          </strong>
          <small>Estimated distance</small>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Live Journey Planning
        </div>
      </nav>

      <main id="home">

        {/* HERO SECTION */}
        <section className="hero">
          <div className="hero-content">
            <div className="tag">
              <Activity size={15} />
              SMARTER PUBLIC TRANSPORT
            </div>

            <h1>
              Travel smarter.
              <br />
              <span>Beat the crowd.</span>
            </h1>

            <p>
              Plan your bus journey with crowd predictions,
              intelligent routing, and data-driven insights.
            </p>

            <a href="#planner" className="hero-button">
              Plan your journey <ArrowRight size={18} />
            </a>
          </div>

          <div className="hero-visual">
            <div className="visual-circle">
              <Bus size={110} strokeWidth={1.1} />

              <div className="floating-card card-one">
                <Users size={17} />
                <div>
                  <strong>Low Crowd</strong>
                  <small>Better travel experience</small>
                </div>
              </div>

              <div className="floating-card card-two">
                <Clock size={17} />
                <div>
                  <strong>Smart Routes</strong>
                  <small>Save travel time</small>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* JOURNEY PLANNER */}
        <section className="planner" id="planner">
          <div className="section-heading">
            <span>YOUR JOURNEY</span>
            <h2>Where do you want to go?</h2>
            <p>
              Search actual bus stops and choose your preference.
            </p>
          </div>

          <div className="planner-card">

            <StopSearch
              label="FROM"
              icon={<MapPin size={16} />}
              selected={source}
              setSelected={setSource}
              placeholder="Search starting bus stop..."
            />

            <StopSearch
              label="TO"
              icon={<Navigation size={16} />}
              selected={destination}
              setSelected={setDestination}
              placeholder="Search destination bus stop..."
            />

            <div className="preference-group">
              <label>TRAVEL PREFERENCE</label>

              <div className="preferences">
                {["Fastest", "Least Crowded", "Balanced"].map(
                  (item) => (
                    <button
                      key={item}
                      type="button"
                      className={
                        preference === item ? "selected" : ""
                      }
                      onClick={() => setPreference(item)}
                    >
                      {item}
                    </button>
                  )
                )}
              </div>
            </div>

            <button
              className="search-button"
              onClick={findRoute}
              disabled={loading}
            >
              <Search size={19} />
              {loading ? "Finding your route..." : "Find My Route"}
            </button>

            {error && (
              <p className="error-message">{error}</p>
            )}
          </div>

          {/* JOURNEY RESULTS */}
          {journey && (
            <div className="journey-results">

              <div className="result-heading">
                <span>YOUR ROUTE</span>
                <h2>Journey found!</h2>
              </div>

              <div className="result-summary">
                <div>
                  <Clock />
                  <strong>
                    {Number(journey.total_travel_time).toFixed(2)} min
                  </strong>
                  <small>Travel time</small>
                </div>
              
              <div className="journey-map-section">
                <h3>Journey Route Map</h3>

                <MapContainer
                  center={[
                    journey.segments[0].from_coordinates.latitude,
                    journey.segments[0].from_coordinates.longitude
                  ]}
                  zoom={14}
                  scrollWheelZoom={true}
                  style={{
                  height: "400px",
                  width: "100%",
                  borderRadius: "14px",
                  marginTop: "15px"
                  }}
                >
                <JourneyMap segments={journey.segments} />
                  </MapContainer>
              </div>


                <div>
                  <Bus />
                  <strong>
                    ₹{journey.estimated_fare.non_ac}
                  </strong>
                  <small>Non-AC fare</small>
                  <strong>
                    ₹{journey.estimated_fare.ac}
                  </strong>
                  <small>AC fare</small>
                </div>

                <div>
                  <Users />
                  <strong>{journey.segments.length}</strong>
                  <small>Journey segments</small>
                </div>
              </div>

              <h3 className="segments-title">
                Journey details
              </h3>

              {journey.segments.map((segment, index) => (
                <div className="segment-card" key={index}>

                  <div className="segment-top">
                    <span className="route-number">
                      <Bus size={16} />
                      Bus {segment.route_id}
                    </span>

                    <span
                      className={`crowd ${String(
                        segment.crowd_level
                      ).toLowerCase()}`}
                    >
                      {segment.crowd_level} Crowd
                    </span>
                  </div>

                  <div className="stop-details">
                    <div className="stop-point">
                      <span className="point-dot"></span>

                      <div>
                        <small>FROM</small>
                        <strong>{segment.from_stop_name}</strong>
                      </div>
                    </div>

                    <div className="segment-time">
                      {segment.travel_time} minutes
                    </div>

                    <div className="stop-point">
                      <span className="point-dot destination-dot"></span>

                      <div>
                        <small>TO</small>
                        <strong>{segment.to_stop_name}</strong>
                      </div>
                    </div>
                  </div>

                  <div className="demand-info">
                    Predicted passenger demand:{" "}
                    {Number(segment.predicted_demand).toFixed(2)}
                  </div>

                </div>
              ))}
            </div>
          )}
        </section>

        {/* FEATURES */}
        <section className="features" id="about">
          <div className="section-heading">
            <span>WHY METAFORA?</span>
            <h2>More than just directions.</h2>
          </div>

          <div className="feature-grid">
            <div className="feature-card">
              <Users size={28} />
              <h3>Crowd Prediction</h3>
              <p>
                Understand expected passenger demand before travelling.
              </p>
            </div>

            <div className="feature-card">
              <Navigation size={28} />
              <h3>Smart Routing</h3>
              <p>
                Compare routes based on travel time and crowd levels.
              </p>
            </div>

            <div className="feature-card">
              <Activity size={28} />
              <h3>Journey Insights</h3>
              <p>
                Make informed travel decisions using data-driven insights.
              </p>
            </div>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer>
        <div className="logo">
          <Bus size={20} />
          <span>
            Meta<span className="highlight">Fora</span>
          </span>
        </div>

        <p>Smarter journeys. Better mobility.</p>
      </footer>
    </div>
  );
}

export default App;
