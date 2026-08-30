"""
VRP Encoding and Decoding Routines for QPSO
Translates continuous particle positions in [0, 1]^D to discrete vehicle routes.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np


def continuous_to_permutation(vector: np.ndarray, offset: int = 1) -> List[int]:
    """
    Decodes a continuous vector into a discrete permutation using Smallest Position Value (SPV).
    Args:
        vector: 1D array of floats of length D
        offset: Base index offset (default 1, representing non-depot customer stops)
    Returns:
        List of stop indices, e.g., [1, 3, 2, 4]
    """
    sorted_indices = np.argsort(vector)
    return [int(idx + offset) for idx in sorted_indices]


def permutation_to_continuous(permutation: List[int], offset: int = 1, bounds: Tuple[float, float] = (0.0, 1.0)) -> np.ndarray:
    """
    Encodes a discrete permutation of stops into a continuous vector in [lower, upper]^D.
    Used for warm-starting particles from prior routes or heuristics.
    """
    D = len(permutation)
    lower, upper = bounds
    vector = np.zeros(D, dtype=float)
    
    # Place values such that argsort(vector) + offset recovers the exact permutation
    for rank, stop_idx in enumerate(permutation):
        arr_idx = stop_idx - offset
        if 0 <= arr_idx < D:
            # Map rank to equidistant points in the domain
            norm_val = lower + (rank + 0.5) / D * (upper - lower)
            vector[arr_idx] = norm_val
            
    return vector


def decode_routes_from_vector(
    vector: np.ndarray,
    n_stops: int,
    fleet_size: int = 1,
    start_idx: int = 0,
    round_trip: bool = False,
    capacities: Optional[List[float]] = None,
    demands: Optional[List[float]] = None
) -> List[List[int]]:
    """
    Splits continuous permutation into individual vehicle routes.
    
    Args:
        vector: Continuous position vector for n_stops
        n_stops: Number of customer stops
        fleet_size: Number of vehicles
        start_idx: Depot node index (typically 0)
        round_trip: Whether vehicles must return to depot
        capacities: Optional vehicle capacity list
        demands: Optional stop demand list (length n_stops + 1)
        
    Returns:
        List of vehicle routes, where each route is a list of node indices.
    """
    if n_stops == 0:
        return [[start_idx] + ([start_idx] if round_trip else [])]
        
    perm = continuous_to_permutation(vector[:n_stops], offset=1)
    
    if fleet_size <= 1:
        route = [start_idx] + perm
        if round_trip:
            route.append(start_idx)
        return [route]
        
    # Multi-vehicle partitioning
    routes = []
    if capacities is not None and demands is not None:
        # Capacity-constrained partitioning
        curr_route = [start_idx]
        curr_cap = 0.0
        v_idx = 0
        max_cap = capacities[min(v_idx, len(capacities) - 1)]
        
        for stop in perm:
            d = demands[stop] if stop < len(demands) else 0.0
            if curr_cap + d > max_cap and len(curr_route) > 1 and v_idx < fleet_size - 1:
                if round_trip:
                    curr_route.append(start_idx)
                routes.append(curr_route)
                v_idx += 1
                max_cap = capacities[min(v_idx, len(capacities) - 1)]
                curr_route = [start_idx, stop]
                curr_cap = d
            else:
                curr_route.append(stop)
                curr_cap += d
                
        if round_trip:
            curr_route.append(start_idx)
        routes.append(curr_route)
        
        # Pad with empty routes if fleet exceeds needed partitions
        while len(routes) < fleet_size:
            routes.append([start_idx] + ([start_idx] if round_trip else []))
            
    else:
        # Balanced slice partitioning
        sub_lists = np.array_split(perm, fleet_size)
        for sub in sub_lists:
            r = [start_idx] + [int(x) for x in sub]
            if round_trip or fleet_size > 1:
                r.append(start_idx)
            routes.append(r)
            
    return routes
