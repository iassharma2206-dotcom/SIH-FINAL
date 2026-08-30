import pytest
import numpy as np
from qpso import optimize_route_qpso_v2, QPSOConfig
from logic import optimize_route_algo

def test_qpso_v2_end_to_end_single_vehicle():
    """Verify QPSO v2 solves a realistic VRP problem and returns correct route structure."""
    start = {"name": "Depot NYC", "coords": (40.7488, -73.9854)}
    stops = [
        {"name": "Empire State", "coords": (40.7484, -73.9857), "window": (8.5, 12.0)},
        {"name": "Chrysler Bldg", "coords": (40.7516, -73.9755), "window": (9.0, 14.0)},
        {"name": "Rockefeller", "coords": (40.7587, -73.9787), "window": (10.0, 16.0)},
        {"name": "Central Park", "coords": (40.7851, -73.9683), "window": (11.0, 17.0)},
    ]
    cfg = QPSOConfig(swarm_size=30, max_iter=100, seed=42)
    routes, stats = optimize_route_qpso_v2(start, stops, round_trip=True, fleet_size=1, qpso_config=cfg)
    
    assert len(routes) == 1
    route = routes[0]
    assert len(route) == 6 # Depot + 4 stops + Depot
    assert route[0]["name"] == "Depot NYC"
    assert route[-1]["name"] == "Depot NYC"
    assert stats["total_cost"] > 0
    assert stats["iterations"] > 0
    assert len(stats["history"]) > 0

def test_logic_py_feature_flag():
    """Verify logic.py correctly switches solver when use_qpso_v2 is toggled."""
    start = {"name": "Depot", "coords": (40.7488, -73.9854)}
    stops = [
        {"name": "Stop 1", "coords": (40.7580, -73.9855)},
        {"name": "Stop 2", "coords": (40.7614, -73.9776)},
    ]
    
    # 1. Default (Legacy SA solver)
    routes_legacy, stats_legacy = optimize_route_algo(start, stops, round_trip=True, use_qpso_v2=False)
    assert len(routes_legacy) == 1
    assert len(routes_legacy[0]) == 4
    
    # 2. Opt-in QPSO v2
    routes_v2, stats_v2 = optimize_route_algo(start, stops, round_trip=True, use_qpso_v2=True)
    assert len(routes_v2) == 1
    assert len(routes_v2[0]) == 4
    assert stats_v2.get("algorithm") == "QPSO v2 (Sun/Li/Ning/Lim Formulation)"
