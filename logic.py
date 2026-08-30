# logic.py
import app as quantum_solver

def optimize_route_algo(start, stops, round_trip=False, fleet_size=1, quantum_params=None, use_qpso_v2=False):
    """
    Router Logic.
    Strictly calls the Hybrid Quantum Solver.
    NO Classical OR-Tools allowed.
    """
    # 0. Optional Opt-in for QPSO v2 Engine (Feature Flag, default OFF)
    if use_qpso_v2:
        from qpso import optimize_route_qpso_v2, QPSOConfig
        cfg = QPSOConfig.from_dict(quantum_params) if quantum_params else None
        return optimize_route_qpso_v2(start, stops, round_trip=round_trip, fleet_size=fleet_size, qpso_config=cfg)

    # 1. Execute Quantum-Inspired Optimization (Legacy/Baseline)
    # Returns a LIST of routes (even if just 1)
    routes, stats = quantum_solver.solve_hybrid_quantum(start, stops, n_vehicles=fleet_size, q_params=quantum_params)
    
    # 2. Handle Round Trip (Return to Warehouse)
    # If fleet > 1, round trip is mandatory (Hub -> Nodes -> Hub)
    if round_trip or fleet_size > 1:
        for i in range(len(routes)):
            # Append start node to end of each route
            routes[i].append(routes[i][0])
        
    return routes, stats


def optimize_route_qpso(start, stops, round_trip=False, fleet_size=1, quantum_params=None):
    """
    Direct QPSO VRP Router. Calls solve_qpso_vrp.
    """
    from qpso_solver import solve_qpso_vrp
    routes, stats = solve_qpso_vrp(start, stops, n_vehicles=fleet_size, q_params=quantum_params)
    if round_trip or fleet_size > 1:
        for i in range(len(routes)):
            routes[i].append(routes[i][0])
    return routes, stats


def optimize_route_qpso_traffic(start, stops, round_trip=False, fleet_size=1, quantum_params=None):
    """
    Traffic-aware QPSO router. Same interface and return shape as
    optimize_route_qpso(), plus it forces use_live_traffic=True in q_params
    and returns (routes, stats) where stats['traffic_segments'] is populated
    when traffic data was fetchable, else None.
    """
    from qpso_solver import solve_qpso_vrp
    q_params = dict(quantum_params or {})
    q_params['use_live_traffic'] = True
    routes, stats = solve_qpso_vrp(start, stops, n_vehicles=fleet_size, q_params=q_params)
    if round_trip or fleet_size > 1:
        for i in range(len(routes)):
            routes[i].append(routes[i][0])
    return routes, stats
