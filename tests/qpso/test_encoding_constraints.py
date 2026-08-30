import pytest
import numpy as np
from qpso.encoding import continuous_to_permutation, permutation_to_continuous, decode_routes_from_vector
from qpso.constraints import ConstraintManager

def test_spv_encoding_decoding_roundtrip():
    """Verify continuous <-> permutation conversion preserves exact order."""
    perm = [3, 1, 4, 2]
    vec = permutation_to_continuous(perm, offset=1)
    decoded_perm = continuous_to_permutation(vec, offset=1)
    assert decoded_perm == perm

def test_multi_vehicle_partitioning():
    """Verify continuous vector splits cleanly across multiple vehicles."""
    vec = np.array([0.2, 0.8, 0.1, 0.6]) # permutation: [3, 1, 4, 2]
    routes = decode_routes_from_vector(vec, n_stops=4, fleet_size=2, start_idx=0, round_trip=True)
    assert len(routes) == 2
    assert routes[0][0] == 0 and routes[0][-1] == 0
    assert routes[1][0] == 0 and routes[1][-1] == 0
    # Combined non-depot stops match permutation
    combined_stops = routes[0][1:-1] + routes[1][1:-1]
    assert combined_stops == [3, 1, 4, 2]

def test_time_window_evaluation():
    """Verify early arrival waiting and late arrival penalties."""
    cm = ConstraintManager(time_penalty_per_hour=100.0, start_hour=8.0)
    time_mat = np.array([
        [0.0, 1.0, 2.0],
        [1.0, 0.0, 1.0],
        [2.0, 1.0, 0.0]
    ])
    nodes = [
        {"name": "Depot", "window": (8.0, 20.0)},
        {"name": "Stop 1", "window": (10.0, 12.0)}, # Reached at 8+1=9 -> waits till 10
        {"name": "Stop 2", "window": (8.0, 10.5)},  # Reached at 10+1=11 -> 0.5hr late
    ]
    route = [0, 1, 2, 0]
    penalty, arrivals, duration = cm.evaluate_time_windows(route, time_mat, nodes)
    # Stop 1 arrival = 9.0, waited till 10.0, departs 10.0, Stop 2 arrival = 11.0
    # Stop 2 overdue = 11.0 - 10.5 = 0.5 hr * 100 = 50.0 penalty
    assert penalty == pytest.approx(50.0, rel=1e-3)

def test_capacity_and_precedence():
    """Verify capacity overload and precedence violation penalties."""
    cm = ConstraintManager(capacity_penalty_per_unit=50.0, precedence_penalty=200.0)
    nodes = [
        {"name": "Depot", "demand": 0},
        {"name": "Pickup A", "demand": 5},
        {"name": "Delivery B", "demand": 10},
    ]
    # Route: 0 -> Delivery B -> Pickup A -> 0 (Precedence violation: B before A)
    route = [0, 2, 1, 0]
    cap_pen, load = cm.evaluate_capacity(route, nodes, max_capacity=12.0)
    assert load == 15.0
    assert cap_pen == pytest.approx(3.0 * 50.0)
    
    prec_pen, violations = cm.evaluate_precedence(route, precedence_pairs=[(1, 2)])
    assert violations == 1
    assert prec_pen == 200.0
