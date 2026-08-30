"""
Benchmark Comparison Harness
Runs multi-algorithm evaluations across problem instances.
"""
from typing import List, Dict, Any, Tuple, Optional
import time
import numpy as np

from qpso.config import QPSOConfig
from qpso.core import QPSOSwarm
from qpso.map_adapter import MapAdapter
from qpso.operators.border_mutation import border_mutation_operator
from qpso.operators.chaos import ChaoticGenerator
from qpso.operators.selective_de import selective_de_operator
from qpso.encoding import decode_routes_from_vector
from qpso.benchmark.metrics import BenchmarkMetrics, compute_solution_metrics

# Baseline solvers
from backend.core.benchmarks.simulated_annealing import run_simulated_annealing
from backend.core.benchmarks.classical_pso import run_classical_pso
from backend.core.benchmarks.exact_solver import run_held_karp_exact


class BenchmarkHarness:
    """
    Automated benchmark testbed for evaluating routing algorithms.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed

    def run_nearest_neighbor(
        self,
        nodes: List[Dict[str, Any]],
        dist_mat: np.ndarray,
        time_mat: np.ndarray,
        cong_mat: np.ndarray,
        round_trip: bool = True
    ) -> Tuple[List[int], float, Dict[str, Any]]:
        """Greedy Nearest Neighbor heuristic."""
        start_t = time.time()
        n = len(nodes)
        unvisited = set(range(1, n))
        route = [0]
        curr = 0
        while unvisited:
            nxt = min(unvisited, key=lambda x: dist_mat[curr, x])
            route.append(nxt)
            unvisited.remove(nxt)
            curr = nxt
        if round_trip:
            route.append(0)
        exec_ms = (time.time() - start_t) * 1000.0
        return route, exec_ms, {"iterations": n, "history": []}

    def evaluate_instance(
        self,
        nodes: List[Dict[str, Any]],
        instance_name: str = "Benchmark Instance",
        round_trip: bool = True,
        congestion_weights: Optional[np.ndarray] = None
    ) -> List[BenchmarkMetrics]:
        """
        Runs all benchmark algorithms on a single problem instance.
        """
        dist_mat, time_mat, cong_mat = MapAdapter.build_cost_matrices(
            nodes, congestion_weights=congestion_weights
        )
        n = len(nodes)
        results = []
        
        # 1. Exact Solver (if n <= 13)
        exact_cost = None
        if n <= 13:
            exact_nodes, exact_stats = run_held_karp_exact(nodes, dist_mat, time_mat, round_trip=round_trip)
            if exact_stats:
                exact_route = [nodes.index(nd) for nd in exact_nodes]
                exact_m = compute_solution_metrics(
                    exact_route, dist_mat, time_mat, cong_mat, nodes,
                    execution_time_ms=exact_stats.get("execution_time_ms", 1.0),
                    iterations=1,
                    algo_name="Held-Karp Exact DP",
                    category="Exact Mathematical"
                )
                exact_cost = exact_m.total_fitness_cost
                exact_m.optimality_gap_pct = 0.0
                results.append(exact_m)
                
        # 2. Nearest Neighbor Baseline
        nn_route, nn_ms, nn_stats = self.run_nearest_neighbor(nodes, dist_mat, time_mat, cong_mat, round_trip=round_trip)
        nn_m = compute_solution_metrics(
            nn_route, dist_mat, time_mat, cong_mat, nodes,
            execution_time_ms=nn_ms,
            iterations=nn_stats["iterations"],
            exact_cost=exact_cost,
            algo_name="Greedy Nearest Neighbor",
            category="Greedy Heuristic"
        )
        results.append(nn_m)
        
        # 3. Simulated Annealing Baseline
        sa_nodes, sa_stats = run_simulated_annealing(nodes, dist_mat, time_mat, round_trip=round_trip)
        sa_route = [nodes.index(nd) for nd in sa_nodes]
        sa_m = compute_solution_metrics(
            sa_route, dist_mat, time_mat, cong_mat, nodes,
            execution_time_ms=sa_stats.get("execution_time_ms", 10.0),
            iterations=sa_stats.get("iterations", 300),
            history=sa_stats.get("history"),
            exact_cost=exact_cost,
            algo_name="Simulated Annealing",
            category="Classical Metaheuristic"
        )
        results.append(sa_m)
        
        # 4. Classical Velocity-based PSO Baseline
        cpso_nodes, cpso_stats = run_classical_pso(nodes, dist_mat, time_mat, round_trip=round_trip)
        cpso_route = [nodes.index(nd) for nd in cpso_nodes]
        cpso_m = compute_solution_metrics(
            cpso_route, dist_mat, time_mat, cong_mat, nodes,
            execution_time_ms=cpso_stats.get("execution_time_ms", 15.0),
            iterations=cpso_stats.get("iterations", 300),
            history=cpso_stats.get("history"),
            exact_cost=exact_cost,
            algo_name="Classical PSO (v-based)",
            category="Swarm Intelligence"
        )
        results.append(cpso_m)
        
        # 5. QPSO v2 Engine (Full Suite)
        adapter = MapAdapter()
        fitness_fn = adapter.create_fitness_function(
            nodes, dist_mat, time_mat, cong_mat, round_trip=round_trip, fleet_size=1
        )
        cfg = QPSOConfig(swarm_size=40, max_iter=250, seed=self.seed)
        swarm = QPSOSwarm(dim=n - 1, fitness_fn=fitness_fn, bounds=(0.0, 1.0), config=cfg)
        chaos_gen = ChaoticGenerator(map_type=cfg.chaos.map_type)
        
        best_pos, best_fit, qpso_stats = swarm.optimize(
            border_mutation_op=border_mutation_operator,
            chaos_generator=chaos_gen,
            selective_de_op=selective_de_operator
        )
        qpso_routes_idx = decode_routes_from_vector(best_pos, n_stops=n - 1, fleet_size=1, start_idx=0, round_trip=round_trip)
        qpso_route = qpso_routes_idx[0]
        
        qpso_m = compute_solution_metrics(
            qpso_route, dist_mat, time_mat, cong_mat, nodes,
            execution_time_ms=qpso_stats["execution_time_ms"],
            iterations=qpso_stats["iterations"],
            history=qpso_stats["history"],
            exact_cost=exact_cost,
            algo_name="Quantum-Behaved PSO v2",
            category="Quantum-Inspired Metaheuristic"
        )
        results.append(qpso_m)
        
        return results
