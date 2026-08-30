"""
qpso_vrp.py
QPSO VRP Optimization Module with traffic awareness.
"""
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import app
from traffic_aware import get_traffic_multiplier, get_traffic_label


def _spv_decode(position_vector: np.ndarray, n_stops: int) -> List[int]:
    """Discretizes continuous particle position to stop sequence."""
    if n_stops <= 0:
        return [0]
    order = np.argsort(position_vector)
    return [0] + [int(idx + 1) for idx in order]


def solve_qpso_vrp(
    start_node: Dict[str, Any],
    stops_data: List[Dict[str, Any]],
    n_vehicles: int = 1,
    q_params: Optional[Dict[str, Any]] = None
) -> Tuple[List[List[Dict[str, Any]]], Dict[str, Any]]:
    """
    Solves Vehicle Routing Problem using Quantum-Behaved PSO with live or scheduled traffic.
    """
    all_nodes = [start_node] + stops_data
    n = len(all_nodes)
    params = q_params or {}

    if n <= 1:
        return [[start_node]], {
            "history": [0.0],
            "tunnels": 0,
            "final_temp": 0.0,
            "algorithm": "QPSO-VRP"
        }

    try:
        from app import build_matrices
        dist_matrix, time_matrix = build_matrices(all_nodes)
        dist_matrix = np.array(dist_matrix, dtype=float)
        time_matrix = np.array(time_matrix, dtype=float)
    except Exception as e:
        dist_matrix = np.zeros((n, n), dtype=float)
        time_matrix = np.zeros((n, n), dtype=float)

    try:
        from traffic_aware import apply_live_or_scheduled_traffic
        # time_matrix here already has the SCHEDULE multiplier applied by
        # app.py. To avoid double-applying, undo it first, then apply the
        # live-or-scheduled version cleanly:
        current_mult = get_traffic_multiplier()
        if current_mult and current_mult > 0:
            raw_time_matrix = time_matrix / current_mult
        else:
            raw_time_matrix = time_matrix
        time_matrix = apply_live_or_scheduled_traffic(raw_time_matrix, all_nodes)
    except Exception:
        pass  # keep the schedule-adjusted time_matrix as-is if this fails

    # Core QPSO Optimization
    n_stops = n - 1
    swarm_size = int(params.get("n_particles", params.get("swarm_size", params.get("particles", 30))))
    max_iter = int(params.get("iter", params.get("max_iter", 300)))
    beta_start = float(params.get("beta_start", 1.0))
    beta_end = float(params.get("beta_end", 0.5))

    X = np.random.uniform(0.0, 1.0, (swarm_size, n_stops))
    pbest = np.copy(X)
    pbest_energy = np.zeros(swarm_size)

    for i in range(swarm_size):
        route_idx = _spv_decode(X[i], n_stops)
        pbest_energy[i] = app.calculate_energy(route_idx, dist_matrix, time_matrix, all_nodes)

    gbest_idx = int(np.argmin(pbest_energy))
    gbest = np.copy(pbest[gbest_idx])
    gbest_energy = float(pbest_energy[gbest_idx])

    history = [gbest_energy]
    tunneling_events = 0

    for it in range(max_iter):
        beta = beta_start - (beta_start - beta_end) * (it / max(max_iter, 1))
        mbest = np.mean(pbest, axis=0)

        for i in range(swarm_size):
            phi = np.random.uniform(0.0, 1.0, n_stops)
            p_i = phi * pbest[i] + (1.0 - phi) * gbest

            u = np.random.uniform(0.0, 1.0, n_stops)
            u = np.maximum(u, 1e-10)
            sign = np.where(np.random.rand(n_stops) < 0.5, 1.0, -1.0)

            X[i] = p_i + sign * beta * np.abs(mbest - X[i]) * np.log(1.0 / u)

            route_idx = _spv_decode(X[i], n_stops)
            curr_energy = app.calculate_energy(route_idx, dist_matrix, time_matrix, all_nodes)

            if curr_energy > pbest_energy[i] and np.random.rand() < 0.05:
                tunneling_events += 1

            if curr_energy < pbest_energy[i]:
                pbest[i] = np.copy(X[i])
                pbest_energy[i] = curr_energy
                if curr_energy < gbest_energy:
                    gbest = np.copy(X[i])
                    gbest_energy = float(curr_energy)

        history.append(gbest_energy)

    best_indices = _spv_decode(gbest, n_stops)
    best_nodes = [all_nodes[idx] for idx in best_indices]

    stats = {
        "history": history,
        "tunnels": tunneling_events,
        "final_temp": float(gbest_energy / max(n, 1)),
        "algorithm": "QPSO-VRP"
    }
    return [best_nodes], stats
