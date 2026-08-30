import pytest
import numpy as np
from qpso.benchmark.harness import BenchmarkHarness
from qpso.benchmark.metrics import compute_solution_metrics

def test_benchmark_harness_single_instance():
    """Verify benchmark harness evaluates multiple algorithms on a small test instance."""
    nodes = [
        {"name": "Depot", "coords": (40.7488, -73.9854)},
        {"name": "Stop 1", "coords": (40.7580, -73.9855)},
        {"name": "Stop 2", "coords": (40.7614, -73.9776)},
        {"name": "Stop 3", "coords": (40.7505, -73.9934)},
    ]
    harness = BenchmarkHarness(seed=123)
    results = harness.evaluate_instance(nodes, instance_name="Test 4-Nodes", round_trip=True)
    
    assert len(results) >= 4
    algo_names = [m.algorithm for m in results]
    assert "Held-Karp Exact DP" in algo_names
    assert "Greedy Nearest Neighbor" in algo_names
    assert "Simulated Annealing" in algo_names
    assert "Quantum-Behaved PSO v2" in algo_names
    
    for m in results:
        assert m.total_distance_km > 0
        assert m.execution_time_ms >= 0
        assert m.is_valid
