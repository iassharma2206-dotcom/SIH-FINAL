"""
Map and Graph Adapter for QPSO Routing Engine
Interfaces graph representations, distance/time matrices, congestion multipliers, and route fitness.
"""
from typing import List, Dict, Any, Tuple, Optional, Callable
import numpy as np
import requests
from geopy.distance import geodesic

from qpso.encoding import decode_routes_from_vector
from qpso.constraints import ConstraintManager


class MapAdapter:
    """
    Adapter bridging geospatial data structures with the QPSO optimization core.
    """
    def __init__(
        self,
        constraint_manager: Optional[ConstraintManager] = None,
        distance_weight: float = 1.0,
        time_weight: float = 2.0
    ):
        self.constraint_manager = constraint_manager or ConstraintManager()
        self.distance_weight = distance_weight
        self.time_weight = time_weight

    @staticmethod
    def build_cost_matrices(
        nodes: List[Dict[str, Any]],
        graph: Any = None,
        congestion_weights: Optional[np.ndarray] = None
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Builds Distance Matrix (km), Time Matrix (hours), and Congestion Multiplier Matrix.
        
        Args:
            nodes: List of stop dicts with 'coords': (lat, lon)
            graph: Optional graph structure
            congestion_weights: Optional NxN matrix of congestion multipliers (>= 1.0)
            
        Returns:
            (dist_matrix_km, time_matrix_hrs, congestion_matrix)
        """
        n = len(nodes)
        if n == 0:
            return np.zeros((0, 0)), np.zeros((0, 0)), np.zeros((0, 0))
            
        dist_mat = np.zeros((n, n), dtype=float)
        time_mat = np.zeros((n, n), dtype=float)
        
        # 1. Attempt OSRM Table API
        osrm_success = False
        try:
            # OSRM requires Lon,Lat format
            coords_str = ";".join([f"{node['coords'][1]},{node['coords'][0]}" for node in nodes])
            url = f"http://router.project-osrm.org/table/v1/driving/{coords_str}?annotations=distance,duration"
            response = requests.get(url, timeout=2.5)
            if response.status_code == 200:
                data = response.json()
                if "distances" in data and "durations" in data:
                    raw_dist = data["distances"]
                    raw_time = data["durations"]
                    
                    for i in range(n):
                        for j in range(n):
                            d_val = raw_dist[i][j]
                            t_val = raw_time[i][j]
                            dist_mat[i, j] = 9999.0 if d_val is None else (d_val / 1000.0)
                            time_mat[i, j] = 9999.0 if t_val is None else (t_val / 3600.0)
                    osrm_success = True
        except Exception:
            osrm_success = False
            
        # 2. Fallback: Geodesic distances with standard city speed (45 km/h)
        if not osrm_success:
            for i in range(n):
                for j in range(n):
                    if i != j:
                        d = geodesic(nodes[i]["coords"], nodes[j]["coords"]).km
                        dist_mat[i, j] = d
                        time_mat[i, j] = d / 45.0  # 45 km/h avg speed
                        
        # 3. Congestion Multipliers (default = 1.0 free-flow)
        if congestion_weights is not None:
            assert congestion_weights.shape == (n, n)
            cong_mat = np.copy(congestion_weights)
        else:
            cong_mat = np.ones((n, n), dtype=float)
            
        return dist_mat, time_mat, cong_mat

    def evaluate_routes(
        self,
        routes: List[List[int]],
        dist_matrix: np.ndarray,
        time_matrix: np.ndarray,
        congestion_matrix: np.ndarray,
        nodes: List[Dict[str, Any]]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluates a set of vehicle routes for total distance, congested duration, and penalties.
        """
        total_dist = 0.0
        total_time = 0.0
        total_penalties = 0.0
        vehicle_details = []
        
        for v_idx, route in enumerate(routes):
            if len(route) <= 1:
                continue
                
            v_dist = 0.0
            for i in range(len(route) - 1):
                u, v = route[i], route[i + 1]
                v_dist += dist_matrix[u, v]
                
            # Evaluate time windows and congestion
            tw_penalty, arrivals, v_duration = self.constraint_manager.evaluate_time_windows(
                route, time_matrix, nodes, congestion_matrix
            )
            
            # Evaluate capacity
            cap_penalty, v_load = self.constraint_manager.evaluate_capacity(route, nodes)
            
            total_dist += v_dist
            total_time += v_duration
            total_penalties += (tw_penalty + cap_penalty)
            
            vehicle_details.append({
                "vehicle_id": v_idx + 1,
                "distance_km": v_dist,
                "duration_hrs": v_duration,
                "load": v_load,
                "tw_penalty": tw_penalty,
                "cap_penalty": cap_penalty
            })
            
        total_cost = (self.distance_weight * total_dist) + (self.time_weight * total_time * 25.0) + total_penalties
        
        metrics = {
            "total_distance_km": total_dist,
            "total_time_hrs": total_time,
            "total_penalties": total_penalties,
            "vehicles": vehicle_details
        }
        return total_cost, metrics

    def create_fitness_function(
        self,
        nodes: List[Dict[str, Any]],
        dist_matrix: np.ndarray,
        time_matrix: np.ndarray,
        congestion_matrix: np.ndarray,
        round_trip: bool = False,
        fleet_size: int = 1
    ) -> Callable[[np.ndarray], float]:
        """
        Factory creating a pure fitness function mapping continuous position vector -> scalar cost.
        """
        n_stops = len(nodes) - 1
        
        def fitness_fn(vector: np.ndarray) -> float:
            routes = decode_routes_from_vector(
                vector, n_stops=n_stops, fleet_size=fleet_size, start_idx=0, round_trip=round_trip
            )
            cost, _ = self.evaluate_routes(routes, dist_matrix, time_matrix, congestion_matrix, nodes)
            return cost
            
        return fitness_fn

    def decode_to_node_routes(
        self,
        vector: np.ndarray,
        nodes: List[Dict[str, Any]],
        round_trip: bool = False,
        fleet_size: int = 1
    ) -> List[List[Dict[str, Any]]]:
        """
        Decodes a continuous vector into lists of full stop dicts for each vehicle.
        """
        n_stops = len(nodes) - 1
        routes_idx = decode_routes_from_vector(
            vector, n_stops=n_stops, fleet_size=fleet_size, start_idx=0, round_trip=round_trip
        )
        
        node_routes = []
        for r in routes_idx:
            node_routes.append([nodes[idx] for idx in r if idx < len(nodes)])
        return node_routes
