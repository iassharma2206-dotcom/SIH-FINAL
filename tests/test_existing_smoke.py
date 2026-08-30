import pytest
import numpy as np

def test_existing_backend_imports():
    """Verify backend modules import cleanly."""
    from backend.api import routes_geocode, routes_graph, routes_optimize, websocket
    from backend.clustering.kmeans_dispatch import cluster_stops_for_fleet
    from backend.core.qpso import run_qpso
    from backend.core.benchmarks.simulated_annealing import run_simulated_annealing
    from backend.core.benchmarks.classical_pso import run_classical_pso
    from backend.core.benchmarks.exact_solver import run_held_karp_exact
    from backend.maps.osm_graph import load_preset_stops
    from backend.maps.distance_matrix import build_distance_matrix
    assert routes_optimize.router is not None

def test_existing_distance_matrix_and_qpso():
    """Verify existing QPSO and distance matrix pipeline works on preset data."""
    from backend.maps.osm_graph import load_preset_stops
    from backend.maps.distance_matrix import build_distance_matrix
    from backend.core.qpso import run_qpso

    start_node, stops = load_preset_stops("manhattan-core")
    assert start_node is not None
    assert len(stops) > 0

    nodes = [start_node] + stops[:5]
    dist_mat, time_mat = build_distance_matrix(nodes)
    assert dist_mat.shape == (6, 6)
    assert time_mat.shape == (6, 6)

    opt_nodes, stats = run_qpso(nodes, dist_mat, time_mat, round_trip=False)
    assert len(opt_nodes) == len(nodes)
    assert "gbest_fitness" in stats
    assert stats["gbest_fitness"] > 0

def test_existing_logic_and_app():
    """Verify legacy logic.py and app.py run without error."""
    import logic
    start = {"name": "Depot", "coords": (40.7488, -73.9854)}
    stops = [
        {"name": "Stop 1", "coords": (40.7580, -73.9855), "window": (9.0, 12.0)},
        {"name": "Stop 2", "coords": (40.7614, -73.9776), "window": (10.0, 14.0)},
    ]
    routes, stats = logic.optimize_route_algo(start, stops, round_trip=True, fleet_size=1)
    assert len(routes) == 1
    assert len(routes[0]) == 4  # Start -> Stop1 -> Stop2 -> Start
