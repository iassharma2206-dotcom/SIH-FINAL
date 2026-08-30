import numpy as np

def spv_decode(particle_position, stops_count, start_idx=0, round_trip=False):
    """
    Smallest Position Value (SPV) rule:
    Converts continuous particle position vector (length = stops_count) 
    into discrete permutation of stop indices (1 to stops_count).
    
    Depot (start_idx = 0) is excluded from QPSO particle dimensions
    and prepended/appended after decoding.
    """
    # Sort indices ascending according to position values
    permutation = np.argsort(particle_position) + 1  # 1-indexed for non-depot stops
    
    route = [start_idx] + list(permutation)
    if round_trip:
        route.append(start_idx)
    return route
