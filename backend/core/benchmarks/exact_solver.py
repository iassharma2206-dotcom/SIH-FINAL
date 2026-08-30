import time
import numpy as np
from itertools import combinations
from backend.core.fitness import calculate_route_fitness

def run_held_karp_exact(nodes, dist_matrix, time_matrix, round_trip=False):
    """
    Held-Karp Dynamic Programming Exact Solver for Single-Vehicle TSP.
    Used for small datasets (<15 stops) to compute the mathematically exact optimal baseline.
    """
    n = len(nodes)
    if n > 15:
        # Fallback to fast branch/bound or heuristic for large n
        return None, {"error": "Exact solver only supports n <= 15 nodes due to O(n^2 2^n) memory constraint"}
        
    start_time = time.time()
    
    # Memoization table: memo[(mask, last_node)] = (cost, path)
    # mask represents visited subset of nodes {1, 2, ..., n-1}
    memo = {}
    
    # Base cases: subsets of size 1
    for k in range(1, n):
        cost = time_matrix[0][k] * 60.0
        memo[(1 << k, k)] = (cost, [0, k])
        
    # Iteratively build subsets of size 2 to n-1
    for sub_size in range(2, n):
        for subset in combinations(range(1, n), sub_size):
            mask = 0
            for node in subset:
                mask |= (1 << node)
                
            for k in subset:
                prev_mask = mask ^ (1 << k)
                best_cost = float('inf')
                best_path = []
                
                for m in subset:
                    if m == k: continue
                    prev_cost, prev_path = memo[(prev_mask, m)]
                    t_cost = prev_cost + time_matrix[m][k] * 60.0
                    
                    if t_cost < best_cost:
                        best_cost = t_cost
                        best_path = prev_path + [k]
                        
                memo[(mask, k)] = (best_cost, best_path)
                
    # Final step: connect last node back to depot (if round_trip) or select min cost
    full_mask = (1 << n) - 2 # all bits 1 to n-1 set
    best_cost = float('inf')
    best_path = []
    
    for k in range(1, n):
        cost, path = memo[(full_mask, k)]
        if round_trip:
            total_c = cost + time_matrix[k][0] * 60.0
            r_path = path + [0]
        else:
            total_c = cost
            r_path = path
            
        if total_c < best_cost:
            best_cost = total_c
            best_path = r_path
            
    elapsed = (time.time() - start_time) * 1000.0
    best_nodes = [nodes[idx] for idx in best_path]
    
    # Re-evaluate fitness through standard fitness calculator
    final_fitness, d_km, t_min, pen = calculate_route_fitness(best_path, dist_matrix, time_matrix, nodes)
    
    return best_nodes, {
        "history": [final_fitness],
        "iterations": 1,
        "execution_time_ms": elapsed,
        "best_fitness": final_fitness
    }
