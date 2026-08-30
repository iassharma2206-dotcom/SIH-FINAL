# Repository Reconnaissance Notes — QRoute23

**Repository**: `pujit23/QRoute23`  
**Current Branch**: `feature/qpso-map-integration`  
**Date**: August 2026

---

## 1. Technology Stack & Frameworks

- **Backend Runtime**: Python 3.12+
- **API Framework**: FastAPI 0.141+ with Uvicorn (port 8000) & WebSockets
- **Legacy / Demo UI**: Streamlit 1.62+ (port 8501) with Folium & Streamlit-Folium
- **Modern Web Frontend**: React 19 + TypeScript + Vite + Tailwind CSS (port 3000)
- **Scientific Computing**: NumPy 2.4+, SciPy 1.17+, Scikit-Learn 1.8+, Geopy 2.5+
- **Testing**: Pytest 9.1+ / Python `unittest`

---

## 2. Directory Layout & Key Modules

```
QRoute23/
├── app.py                          # Streamlit solver logic (SA-based prototype) & matrix builder
├── logic.py                        # Router dispatch bridging Streamlit to solver
├── main.py                         # Streamlit entry point
├── config.py                       # Streamlit styling & page configuration
├── sessionstate.py                 # Streamlit session state initialization
├── api.py                          # OSRM road geometry fetching & geocoding helper
├── backend/
│   ├── main.py                     # FastAPI app entry point (serves API & mounts frontend/dist)
│   ├── config.py                   # Backend configuration
│   ├── api/
│   │   ├── routes_geocode.py       # Geocoding search endpoint (/api/geocode/search)
│   │   ├── routes_graph.py         # Network graph health & diagnostics (/api/network/health)
│   │   ├── routes_optimize.py      # Route optimization (/api/optimize) & benchmarks (/api/benchmark/{id})
│   │   └── websocket.py            # Live telemetry WebSocket manager (/ws/telemetry/{id})
│   ├── clustering/
│   │   └── kmeans_dispatch.py      # Fleet stop partitioning via KMeans
│   ├── core/
│   │   ├── qpso.py                 # Existing baseline continuous QPSO implementation
│   │   ├── encoding.py             # Smallest Position Value (SPV) permutation decoding
│   │   ├── fitness.py              # Route fitness (distance + late penalty)
│   │   └── benchmarks/
│   │       ├── classical_pso.py    # Classical velocity-based PSO baseline
│   │       ├── simulated_annealing.py # Simulated Annealing baseline
│   │       └── exact_solver.py     # Held-Karp dynamic programming exact solver (<= 13 nodes)
│   └── maps/
│       ├── distance_matrix.py      # OSRM Table API & Geodesic distance/time matrix builder
│       ├── geocode.py              # Nominatim / Photon geocoding client
│       ├── osm_graph.py            # Preset stop loaders (e.g. manhattan-core, sf-mission, etc.)
│       ├── osm_graph_bbox.py       # Scoped OSMnx Overpass graph loader
│       └── traffic_model.py        # Dynamic congestion multiplier generator
├── frontend/                       # Vite + React 19 + TypeScript modern UI
├── data/                           # Demo CSV stops & cached graphML data
└── docs/                           # Documentation
```

---

## 3. Data Structures & Routing Signatures

### 3.1 Node / Stop Representation
```python
# Stop dictionary representation
{
    "name": "Times Square",
    "coords": (40.7580, -73.9855),  # (latitude, longitude)
    "window": (9.0, 17.0)           # Optional time window [start_hour, end_hour]
}
```

### 3.2 Distance & Time Matrix Builder
`backend/maps/distance_matrix.py` / `app.py`:
```python
def build_distance_matrix(nodes: List[dict]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns:
    - dist_matrix: NxN float matrix in kilometers (km)
    - time_matrix: NxN float matrix in hours (h)
    """
```

### 3.3 Existing Optimization Public API Contract
Endpoint: `POST /api/optimize`  
Input Request Body:
```json
{
  "preset": "manhattan-core",
  "start_location": {
    "name": "Depot Hub",
    "coords": [40.748817, -73.985428]
  },
  "stops": [
    { "name": "Stop 1", "coords": [40.7580, -73.9855], "window": [9.0, 12.0] }
  ],
  "vehicle_count": 1,
  "round_trip": false,
  "mileage_kml": 12.0,
  "fuel_price_inr": 96.0,
  "qpso_params": {
    "swarm_size": 30,
    "max_iter": 300,
    "beta_start": 1.0,
    "beta_end": 0.5,
    "plateau_window": 50
  }
}
```
Output Response Body:
```json
{
  "run_id": "a1b2c3d4",
  "status": "Completed",
  "routes": [
    {
      "vehicle_id": 1,
      "stops": [{ "name": "...", "coords": [lat, lon], "window": [...] }],
      "geometry": [[lat1, lon1], [lat2, lon2]]
    }
  ],
  "metrics": {
    "total_distance_km": 15.4,
    "total_time_min": 24.2,
    "fuel_liters": 1.3,
    "cost_inr": 123.0,
    "time_saved_hrs": 0.1,
    "co2_reduction_kg": 0.5,
    "vehicles": [...]
  },
  "telemetry": {
    "execution_ms": 45.2,
    "tunnels": 12,
    "iterations": 300,
    "history": [...]
  }
}
```

### 3.4 Logic Layer Dispatch Contract
`logic.optimize_route_algo`:
```python
def optimize_route_algo(
    start: dict,
    stops: List[dict],
    round_trip: bool = False,
    fleet_size: int = 1,
    quantum_params: Optional[dict] = None
) -> Tuple[List[List[dict]], dict]:
    """
    Returns:
    - routes: List of vehicle route node lists: [[node0, node1, ...], [node0, ...]]
    - stats: Dict containing telemetry, history, tunneling count, execution time
    """
```

---

## 4. Integration Strategy for New QPSO Engine

The new `qpso` engine will be placed in `qpso/` at the repository root.
It will adhere strictly to:
1. Pure self-contained architecture — no dependencies on UI or specific endpoints.
2. An adapter `qpso/map_adapter.py` that translates node representations into distance, time, and congestion matrices.
3. Feature flag `optimizer: Optional[str] = "qpso_v2"` (defaulting to current behavior when absent or set to legacy).
4. Full compatibility with the output dictionary structure expected by frontend and Streamlit consumers.
