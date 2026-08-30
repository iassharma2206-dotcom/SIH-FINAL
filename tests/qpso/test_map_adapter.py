import pytest
import numpy as np
from qpso.map_adapter import MapAdapter

def test_map_adapter_matrices():
    """Verify matrix building with custom congestion multipliers."""
    nodes = [
        {"name": "Depot", "coords": (40.7488, -73.9854)},
        {"name": "Stop 1", "coords": (40.7580, -73.9855)},
        {"name": "Stop 2", "coords": (40.7614, -73.9776)},
    ]
    cong_custom = np.array([
        [1.0, 1.5, 1.0],
        [1.5, 1.0, 2.0],
        [1.0, 2.0, 1.0]
    ])
    dist_mat, time_mat, cong_mat = MapAdapter.build_cost_matrices(nodes, congestion_weights=cong_custom)
    assert dist_mat.shape == (3, 3)
    assert time_mat.shape == (3, 3)
    assert cong_mat.shape == (3, 3)
    assert cong_mat[0, 1] == 1.5

def test_map_adapter_fitness_function():
    """Verify generated fitness function correctly evaluates continuous particle."""
    adapter = MapAdapter()
    nodes = [
        {"name": "Depot", "coords": (40.7488, -73.9854)},
        {"name": "Stop 1", "coords": (40.7580, -73.9855), "window": (8.5, 12.0)},
        {"name": "Stop 2", "coords": (40.7614, -73.9776), "window": (9.0, 14.0)},
    ]
    dist_mat, time_mat, cong_mat = MapAdapter.build_cost_matrices(nodes)
    fitness_fn = adapter.create_fitness_function(
        nodes, dist_mat, time_mat, cong_mat, round_trip=True, fleet_size=1
    )
    
    vec1 = np.array([0.1, 0.9]) # Visit stop 1 then stop 2
    vec2 = np.array([0.9, 0.1]) # Visit stop 2 then stop 1
    
    cost1 = fitness_fn(vec1)
    cost2 = fitness_fn(vec2)
    assert cost1 > 0
    assert cost2 > 0
    
    # Test node decoding
    node_routes = adapter.decode_to_node_routes(vec1, nodes, round_trip=True, fleet_size=1)
    assert len(node_routes) == 1
    assert [n["name"] for n in node_routes[0]] == ["Depot", "Stop 1", "Stop 2", "Depot"]
