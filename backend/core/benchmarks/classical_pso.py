import numpy as np
import time
from backend.core.encoding import spv_decode
from backend.core.fitness import calculate_route_fitness

def run_classical_pso(nodes, dist_matrix, time_matrix, round_trip=False, params=None):
    """
    Standard Classical PSO (with Velocity & Position updates)
    v_ij(t+1) = w * v_ij(t) + c1 * r1 * (pbest_ij - x_ij) + c2 * r2 * (gbest_j - x_ij)
    x_ij(t+1) = x_ij(t) + v_ij(t+1)
    """
    n_nodes = len(nodes)
    if n_nodes <= 1:
        return nodes, {"history": [0], "iterations": 0, "execution_time_ms": 0}
        
    n_stops = n_nodes - 1
    start_time = time.time()
    
    M = int(params.get("swarm_size", 30)) if params else 30
    max_iter = int(params.get("max_iter", 300)) if params else 300
    w = 0.7   # inertia weight
    c1 = 1.49 # cognitive coefficient
    c2 = 1.49 # social coefficient
    
    # Initialize positions and velocities
    X = np.random.uniform(0.0, 1.0, (M, n_stops))
    V = np.random.uniform(-0.1, 0.1, (M, n_stops))
    
    pbest = np.copy(X)
    pbest_fit = np.zeros(M)
    
    for i in range(M):
        route = spv_decode(X[i], n_stops, start_idx=0, round_trip=round_trip)
        fit, _, _, _ = calculate_route_fitness(route, dist_matrix, time_matrix, nodes)
        pbest_fit[i] = fit
        
    gbest_idx = np.argmin(pbest_fit)
    gbest = np.copy(pbest[gbest_idx])
    gbest_fit = pbest_fit[gbest_idx]
    
    history = [gbest_fit]
    
    for it in range(max_iter):
        r1 = np.random.uniform(0.0, 1.0, (M, n_stops))
        r2 = np.random.uniform(0.0, 1.0, (M, n_stops))
        
        # Velocity update equation
        V = w * V + c1 * r1 * (pbest - X) + c2 * r2 * (gbest - X)
        # Position update
        X = X + V
        
        for i in range(M):
            route = spv_decode(X[i], n_stops, start_idx=0, round_trip=round_trip)
            fit, _, _, _ = calculate_route_fitness(route, dist_matrix, time_matrix, nodes)
            
            if fit < pbest_fit[i]:
                pbest[i] = np.copy(X[i])
                pbest_fit[i] = fit
                if fit < gbest_fit:
                    gbest = np.copy(X[i])
                    gbest_fit = fit
                    
        history.append(gbest_fit)
        
    elapsed = (time.time() - start_time) * 1000.0
    best_route_indices = spv_decode(gbest, n_stops, start_idx=0, round_trip=round_trip)
    best_nodes = [nodes[idx] for idx in best_route_indices]
    
    return best_nodes, {
        "history": history,
        "iterations": len(history),
        "execution_time_ms": elapsed,
        "best_fitness": gbest_fit
    }
