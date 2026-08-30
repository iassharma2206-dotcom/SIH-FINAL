import numpy as np
import time
from backend.core.fitness import calculate_route_fitness

def run_simulated_annealing(nodes, dist_matrix, time_matrix, round_trip=False, params=None):
    """
    Simulated Annealing Baseline Algorithm with 2-Opt and Swap moves.
    """
    n = len(nodes)
    if n <= 1:
        return nodes, {"history": [0], "iterations": 0, "execution_time_ms": 0}
        
    start_time = time.time()
    
    # Initial route: 0, 1, 2, ..., n-1 (+ 0 if round_trip)
    curr_route = list(range(n))
    if round_trip:
        curr_route.append(0)
        
    curr_fit, _, _, _ = calculate_route_fitness(curr_route, dist_matrix, time_matrix, nodes)
    best_route = list(curr_route)
    best_fit = curr_fit
    
    iter_max = params.get("max_iter", 1000) if params else 1000
    temp = params.get("initial_temp", 100.0) if params else 100.0
    cooling_rate = params.get("cooling_rate", 0.995) if params else 0.995
    
    history = [best_fit]
    
    for it in range(iter_max):
        temp *= cooling_rate
        new_route = list(curr_route)
        
        # Non-depot indices range
        max_idx = len(new_route) - 1 if round_trip else len(new_route)
        if max_idx > 2:
            if np.random.rand() < 0.5:
                # 2-opt flip
                i, j = np.random.randint(1, max_idx), np.random.randint(1, max_idx)
                if i > j: i, j = j, i
                new_route[i:j+1] = new_route[i:j+1][::-1]
            else:
                # Swap
                i, j = np.random.randint(1, max_idx), np.random.randint(1, max_idx)
                new_route[i], new_route[j] = new_route[j], new_route[i]
                
        new_fit, _, _, _ = calculate_route_fitness(new_route, dist_matrix, time_matrix, nodes)
        
        delta = new_fit - curr_fit
        if delta < 0 or np.random.rand() < np.exp(-delta / max(temp, 1e-5)):
            curr_route = list(new_route)
            curr_fit = new_fit
            if curr_fit < best_fit:
                best_route = list(curr_route)
                best_fit = curr_fit
                
        history.append(best_fit)
        
    elapsed = (time.time() - start_time) * 1000.0
    best_nodes = [nodes[idx] for idx in best_route]
    
    return best_nodes, {
        "history": history,
        "iterations": len(history),
        "execution_time_ms": elapsed,
        "best_fitness": best_fit
    }
