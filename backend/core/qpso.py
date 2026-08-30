import numpy as np
import time
from backend.core.encoding import spv_decode
from backend.core.fitness import calculate_route_fitness

def run_qpso(nodes, dist_matrix, time_matrix, round_trip=False, qpso_params=None, telemetry_callback=None):
    """
    True Quantum-Behaved Particle Swarm Optimization (QPSO)
    Formulation: Sun, Feng, Xu (Quantum Delta-Potential Well Model)
    NO velocity vector. Continuous particles discretized via SPV rule.
    
    Parameters:
    - nodes: list of dicts with stop info
    - dist_matrix: NxN distance matrix in km
    - time_matrix: NxN time matrix in hours
    - round_trip: boolean
    - qpso_params: dict containing swarm_size (M), max_iter, beta_start, beta_end, plateau_window
    - telemetry_callback: optional function(iter_idx, best_fitness, diversity, mbest, elapsed_ms)
    """
    n_nodes = len(nodes)
    if n_nodes <= 1:
        return [0], {"history": [0], "tunnels": 0, "final_temp": 0, "diversity": 0, "iterations": 0}
        
    n_stops = n_nodes - 1 # Non-depot stops
    
    if qpso_params is None:
        qpso_params = {}
        
    M = int(qpso_params.get("swarm_size", 30))
    max_iter = int(qpso_params.get("max_iter", 300))
    beta_start = float(qpso_params.get("beta_start", 1.0))
    beta_end = float(qpso_params.get("beta_end", 0.5))
    plateau_window = int(qpso_params.get("plateau_window", 50))
    
    # Initialization: Random continuous positions in [0, 1]^n_stops
    X = np.random.uniform(0.0, 1.0, (M, n_stops))
    pbest = np.copy(X)
    
    # Evaluate initial swarm
    pbest_fitness = np.zeros(M)
    for i in range(M):
        route = spv_decode(X[i], n_stops, start_idx=0, round_trip=round_trip)
        fit, _, _, _ = calculate_route_fitness(route, dist_matrix, time_matrix, nodes)
        pbest_fitness[i] = fit
        
    gbest_idx = np.argmin(pbest_fitness)
    gbest = np.copy(pbest[gbest_idx])
    gbest_fitness = pbest_fitness[gbest_idx]
    
    history = [gbest_fitness]
    diversity_history = []
    tunnels = 0
    plateau_count = 0
    start_time = time.time()
    
    for it in range(max_iter):
        # Beta linear annealing: contraction-expansion coefficient
        beta = beta_start - (beta_start - beta_end) * (it / max_iter)
        
        # Mean best (mbest) = average of all personal bests
        mbest = np.mean(pbest, axis=0)
        
        for i in range(M):
            # Stochastic attractor p_ij
            phi = np.random.uniform(0.0, 1.0, n_stops)
            p_i = phi * pbest[i] + (1.0 - phi) * gbest
            
            # Quantum potential well sampling (Sun et al.)
            u = np.random.uniform(0.0, 1.0, n_stops)
            u = np.maximum(u, 1e-10) # avoid log(0)
            sign = np.where(np.random.rand(n_stops) < 0.5, 1.0, -1.0)
            
            # Position update step
            X[i] = p_i + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / u)
            
            # Evaluate new position
            route = spv_decode(X[i], n_stops, start_idx=0, round_trip=round_trip)
            fit, _, _, _ = calculate_route_fitness(route, dist_matrix, time_matrix, nodes)
            
            # Track quantum tunneling events (accepting temporary exploratory states)
            if fit > pbest_fitness[i] and np.random.rand() < 0.05:
                tunnels += 1
                
            if fit < pbest_fitness[i]:
                pbest[i] = np.copy(X[i])
                pbest_fitness[i] = fit
                if fit < gbest_fitness:
                    gbest = np.copy(X[i])
                    gbest_fitness = fit
                    plateau_count = 0
                    
        plateau_count += 1
        history.append(float(gbest_fitness))
        
        # Swarm diversity metric: mean distance to mbest
        diversity = float(np.mean(np.linalg.norm(X - mbest, axis=1)))
        diversity_history.append(diversity)
        
        elapsed_ms = (time.time() - start_time) * 1000.0
        
        if telemetry_callback:
            telemetry_callback({
                "iteration": it + 1,
                "best_fitness": round(float(gbest_fitness), 2),
                "swarm_diversity": round(diversity, 4),
                "mbest": [round(val, 4) for val in mbest[:5]],
                "elapsed_ms": round(elapsed_ms, 1)
            })
            
        # Early stopping on plateau
        if plateau_count >= plateau_window and it > 100:
            break
            
    best_route_indices = spv_decode(gbest, n_stops, start_idx=0, round_trip=round_trip)
    best_route_nodes = [nodes[idx] for idx in best_route_indices]
    
    stats = {
        "history": history,
        "diversity_history": diversity_history,
        "tunnels": tunnels,
        "final_beta": beta,
        "iterations": len(history),
        "execution_time_ms": (time.time() - start_time) * 1000.0,
        "gbest_fitness": gbest_fitness
    }
    
    return best_route_nodes, stats
