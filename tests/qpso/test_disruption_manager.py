import pytest
import numpy as np
from qpso.disruption_manager import DisruptionManager, DisruptionEvent
from qpso.map_adapter import MapAdapter

def test_disruption_replan_forward_only():
    """Verify that completed stops remain fixed and only unserved stops are rescheduled."""
    nodes = [
        {"name": "Depot", "coords": (40.7488, -73.9854)},
        {"name": "Stop 1", "coords": (40.7580, -73.9855)},
        {"name": "Stop 2", "coords": (40.7614, -73.9776)},
        {"name": "Stop 3", "coords": (40.7505, -73.9934)},
        {"name": "Stop 4", "coords": (40.7420, -73.9810)},
    ]
    dist_mat, time_mat, _ = MapAdapter.build_cost_matrices(nodes)
    
    original_routes = [
        [nodes[0], nodes[1], nodes[2], nodes[3], nodes[4], nodes[0]]
    ]
    # Suppose Stop 1 is already completed
    completed = [
        [nodes[0], nodes[1]]
    ]
    
    event = DisruptionEvent(
        affected_edge=(1, 2),
        delay_hours=0.8,
        disruption_time_hours=9.5,
        description="Major traffic jam on avenue"
    )
    
    dm = DisruptionManager()
    plan = dm.replan(
        all_nodes=nodes,
        original_routes=original_routes,
        completed_stops_per_vehicle=completed,
        disruption=event,
        dist_matrix=dist_mat,
        time_matrix=time_mat,
        round_trip=True,
        fleet_size=1
    )
    
    assert len(plan.routes) == 1
    rescheduled_route = plan.routes[0]
    
    # First two stops must be Depot and Stop 1 (completed)
    assert rescheduled_route[0]["name"] == "Depot"
    assert rescheduled_route[1]["name"] == "Stop 1"
    
    # All 4 stops must appear in the final route
    names = [s["name"] for s in rescheduled_route]
    assert "Stop 1" in names
    assert "Stop 2" in names
    assert "Stop 3" in names
    assert "Stop 4" in names
    assert plan.execution_time_ms > 0
