"""
Constraint Validation and Penalty Evaluation for VRP
Handles Time Windows (VRPTW), Vehicle Capacities (CVRP), and Precedence Constraints.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


class ConstraintManager:
    """
    Evaluates soft/hard constraints and computes penalties for route fitness.
    """
    def __init__(
        self,
        time_penalty_per_hour: float = 100.0,
        capacity_penalty_per_unit: float = 500.0,
        precedence_penalty: float = 1000.0,
        start_hour: float = 8.0,
        default_service_time_hrs: float = 0.0
    ):
        self.time_penalty_per_hour = time_penalty_per_hour
        self.capacity_penalty_per_unit = capacity_penalty_per_unit
        self.precedence_penalty = precedence_penalty
        self.start_hour = start_hour
        self.default_service_time_hrs = default_service_time_hrs

    def evaluate_time_windows(
        self,
        route: List[int],
        time_matrix: np.ndarray,
        nodes: List[Dict[str, Any]],
        congestion_matrix: Optional[np.ndarray] = None
    ) -> Tuple[float, List[float], float]:
        """
        Calculates time progression and lateness penalties along a single vehicle route.
        
        Args:
            route: List of node indices, e.g. [0, 2, 1, 3, 0]
            time_matrix: NxN matrix of free-flow travel times in hours
            nodes: List of stop dicts with optional 'window' and 'service_time'
            congestion_matrix: Optional NxN congestion multiplier matrix
            
        Returns:
            (penalty_cost, arrival_times, total_route_duration_hrs)
        """
        if len(route) <= 1:
            return 0.0, [self.start_hour], 0.0
            
        current_time = self.start_hour
        arrival_times = [current_time]
        penalty = 0.0
        
        for i in range(len(route) - 1):
            u, v = route[i], route[i + 1]
            
            # Service duration at current stop u
            svc = float(nodes[u].get("service_time", self.default_service_time_hrs)) if u < len(nodes) else 0.0
            current_time += svc
            
            # Edge travel time with congestion multiplier
            travel_t = time_matrix[u, v]
            if congestion_matrix is not None:
                travel_t *= congestion_matrix[u, v]
                
            current_time += travel_t
            arrival_times.append(current_time)
            
            # Evaluate time window for destination v
            if v < len(nodes) and "window" in nodes[v] and nodes[v]["window"] is not None:
                start_w, end_w = nodes[v]["window"]
                
                # Early arrival: vehicle waits at customer until window opens (no penalty, clock advances)
                if current_time < start_w:
                    current_time = start_w
                # Late arrival: penalty proportional to overdue duration
                elif current_time > end_w:
                    overdue = current_time - end_w
                    penalty += overdue * self.time_penalty_per_hour
                    
        total_duration = current_time - self.start_hour
        return penalty, arrival_times, total_duration

    def evaluate_capacity(
        self,
        route: List[int],
        nodes: List[Dict[str, Any]],
        max_capacity: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Calculates total demand and overload penalty along a route.
        """
        if max_capacity is None or len(route) <= 2:
            return 0.0, 0.0
            
        total_demand = 0.0
        for idx in route[1:-1] if route[-1] == route[0] else route[1:]:
            if idx < len(nodes):
                total_demand += float(nodes[idx].get("demand", 1.0))
                
        overload = max(0.0, total_demand - max_capacity)
        penalty = overload * self.capacity_penalty_per_unit
        return penalty, total_demand

    def evaluate_precedence(
        self,
        route: List[int],
        precedence_pairs: Optional[List[Tuple[int, int]]] = None
    ) -> Tuple[float, int]:
        """
        Checks if required stop precedence order is preserved (e.g. pickup before delivery).
        """
        if not precedence_pairs or len(route) <= 2:
            return 0.0, 0
            
        pos_map = {node_idx: pos for pos, node_idx in enumerate(route)}
        violations = 0
        
        for u, v in precedence_pairs:
            if u in pos_map and v in pos_map:
                if pos_map[u] > pos_map[v]:
                    violations += 1
                    
        penalty = violations * self.precedence_penalty
        return penalty, violations
