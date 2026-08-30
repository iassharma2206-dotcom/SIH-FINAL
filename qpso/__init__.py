"""
QPSO - Quantum-behaved Particle Swarm Optimization Package for QRoute23
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import time

from qpso.config import (
    QPSOConfig,
    ChaosConfig,
    SelectiveDEConfig,
    BorderMutationConfig,
    DisruptionConfig
)
from qpso.core import QPSOSwarm
from qpso.map_adapter import MapAdapter
from qpso.constraints import ConstraintManager
from qpso.disruption_manager import DisruptionManager, DisruptionEvent, DisruptionPlan
from qpso.operators.border_mutation import border_mutation_operator
from qpso.operators.chaos import ChaoticGenerator
from qpso.operators.selective_de import selective_de_operator


def optimize_route_qpso_v2(
    start_node: Dict[str, Any],
    stops_data: List[Dict[str, Any]],
    round_trip: bool = False,
    fleet_size: int = 1,
    qpso_config: Optional[QPSOConfig] = None,
    congestion_weights: Optional[np.ndarray] = None
) -> Tuple[List[List[Dict[str, Any]]], Dict[str, Any]]:
    """
    Public Entry Point for QPSO v2 Optimizer.
    
    Args:
        start_node: Start depot dict {"name": str, "coords": (lat, lon)}
        stops_data: List of stop dicts [{"name": str, "coords": (lat, lon), "window": (s, e)}]
        round_trip: Whether vehicle returns to depot
        fleet_size: Number of vehicles in fleet
        qpso_config: Hyperparameter configuration
        congestion_weights: Optional NxN congestion multiplier matrix
        
    Returns:
        (routes, telemetry_stats)
        - routes: List of vehicle route node lists [[node0, node1, ...], [node0, ...]]
        - telemetry_stats: Dict with execution_time_ms, history, diversity, tunnels, etc.
    """
    start_time = time.time()
    nodes = [start_node] + stops_data
    n_nodes = len(nodes)
    
    if n_nodes <= 1:
        return [[start_node] + ([start_node] if round_trip else [])], {
            "history": [0.0], "tunnels": 0, "iterations": 0, "execution_time_ms": 0.0, "diversity": 0.0
        }
        
    cfg = qpso_config or QPSOConfig()
    adapter = MapAdapter()
    
    # 1. Build Distance, Time, and Congestion Matrices
    dist_mat, time_mat, cong_mat = adapter.build_cost_matrices(
        nodes, congestion_weights=congestion_weights
    )
    
    # 2. Build Objective Fitness Function
    fitness_fn = adapter.create_fitness_function(
        nodes, dist_mat, time_mat, cong_mat, round_trip=round_trip, fleet_size=fleet_size
    )
    
    # 3. Instantiate Swarm
    n_stops = n_nodes - 1
    swarm = QPSOSwarm(
        dim=n_stops,
        fitness_fn=fitness_fn,
        bounds=(0.0, 1.0),
        config=cfg
    )
    
    # 4. Instantiate Operators
    chaos_gen = ChaoticGenerator(map_type=cfg.chaos.map_type) if cfg.chaos.enabled else None
    
    # 5. Run Vectorized Optimization
    best_pos, best_fit, stats = swarm.optimize(
        border_mutation_op=border_mutation_operator if cfg.border_mutation.enabled else None,
        chaos_generator=chaos_gen,
        selective_de_op=selective_de_operator if cfg.selective_de.enabled else None
    )
    
    # 6. Decode Solution to Full Route Dicts
    routes = adapter.decode_to_node_routes(
        best_pos, nodes, round_trip=round_trip, fleet_size=fleet_size
    )
    
    stats["total_cost"] = float(best_fit)
    stats["total_nodes"] = n_nodes
    stats["fleet_size"] = fleet_size
    stats["algorithm"] = "QPSO v2 (Sun/Li/Ning/Lim Formulation)"
    
    return routes, stats


__all__ = [
    "QPSOConfig",
    "ChaosConfig",
    "SelectiveDEConfig",
    "BorderMutationConfig",
    "DisruptionConfig",
    "QPSOSwarm",
    "MapAdapter",
    "ConstraintManager",
    "DisruptionManager",
    "DisruptionEvent",
    "DisruptionPlan",
    "optimize_route_qpso_v2"
]
