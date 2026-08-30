"""
Benchmark Metrics Calculator for Route Optimizers
Computes distance, duration, congestion cost, convergence iterations, and wall-clock execution time.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


@dataclass
class BenchmarkMetrics:
    algorithm: str
    category: str
    total_distance_km: float
    total_time_hrs: float
    congestion_penalty: float
    total_fitness_cost: float
    execution_time_ms: float
    iterations: int
    converged_iteration: int
    optimality_gap_pct: float
    is_valid: bool


def compute_solution_metrics(
    route_indices: List[int],
    dist_matrix: np.ndarray,
    time_matrix: np.ndarray,
    cong_matrix: np.ndarray,
    nodes: List[Dict[str, Any]],
    execution_time_ms: float,
    iterations: int,
    history: Optional[List[float]] = None,
    exact_cost: Optional[float] = None,
    algo_name: str = "Optimizer",
    category: str = "Metaheuristic"
) -> BenchmarkMetrics:
    """
    Computes rigorous performance metrics for a single vehicle route solution.
    """
    total_dist = 0.0
    total_time = 0.0
    cong_penalty = 0.0
    current_time = 8.0  # 8 AM start
    
    for i in range(len(route_indices) - 1):
        u, v = route_indices[i], route_indices[i + 1]
        d = dist_matrix[u, v]
        base_t = time_matrix[u, v]
        cong_mult = cong_matrix[u, v]
        
        actual_t = base_t * cong_mult
        if cong_mult > 1.0:
            cong_penalty += (actual_t - base_t) * 50.0  # $50/hr congestion delay cost
            
        total_dist += d
        current_time += actual_t
        total_time += actual_t
        
        # Time window check
        if v < len(nodes) and "window" in nodes[v] and nodes[v]["window"] is not None:
            sw, ew = nodes[v]["window"]
            if current_time < sw:
                current_time = sw
            elif current_time > ew:
                overdue = current_time - ew
                cong_penalty += overdue * 100.0
                
    total_fitness = total_dist + 2.0 * total_time * 25.0 + cong_penalty
    
    # Identify iteration where 98% of improvement was achieved
    converged_iter = iterations
    if history and len(history) > 1:
        initial = history[0]
        final = history[-1]
        span = initial - final
        if span > 1e-4:
            target = initial - 0.98 * span
            for idx, val in enumerate(history):
                if val <= target:
                    converged_iter = idx + 1
                    break
                    
    # Optimality gap
    if exact_cost is not None and exact_cost > 0:
        gap_pct = ((total_fitness - exact_cost) / exact_cost) * 100.0
    else:
        gap_pct = 0.0
        
    return BenchmarkMetrics(
        algorithm=algo_name,
        category=category,
        total_distance_km=round(total_dist, 2),
        total_time_hrs=round(total_time, 2),
        congestion_penalty=round(cong_penalty, 2),
        total_fitness_cost=round(total_fitness, 2),
        execution_time_ms=round(execution_time_ms, 2),
        iterations=iterations,
        converged_iteration=converged_iter,
        optimality_gap_pct=round(max(0.0, gap_pct), 2),
        is_valid=True
    )
