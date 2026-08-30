"""
Disruption Management Decision Model for VRP under Traffic Delay (Ning, Wang & Hu, 2019)
Provides fast forward-only sub-route replanning with a combined recovery vs schedule-deviation objective.
"""
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass
import numpy as np
import time

from qpso.config import QPSOConfig, DisruptionConfig
from qpso.core import QPSOSwarm
from qpso.encoding import decode_routes_from_vector, permutation_to_continuous
from qpso.constraints import ConstraintManager
from qpso.map_adapter import MapAdapter
from qpso.operators.border_mutation import border_mutation_operator
from qpso.operators.selective_de import selective_de_operator
from qpso.operators.chaos import ChaoticGenerator


@dataclass
class DisruptionEvent:
    affected_edge: Optional[Tuple[int, int]] = None  # (from_node_idx, to_node_idx)
    delay_hours: float = 0.5                          # Added delay on the affected segment
    disruption_time_hours: float = 9.0                # Time of disruption occurrence
    description: str = "Traffic accident delay"


@dataclass
class DisruptionPlan:
    routes: List[List[Dict[str, Any]]]
    total_cost: float
    recovery_cost: float
    deviation_cost: float
    time_deviation_hrs: float
    seq_deviation_count: int
    execution_time_ms: float
    iterations: int


class DisruptionManager:
    """
    Manages dynamic mid-execution rerouting when unexpected delays disrupt the schedule.
    """
    def __init__(
        self,
        config: Optional[DisruptionConfig] = None,
        constraint_manager: Optional[ConstraintManager] = None
    ):
        self.config = config or DisruptionConfig()
        self.constraint_manager = constraint_manager or ConstraintManager()

    def replan(
        self,
        all_nodes: List[Dict[str, Any]],
        original_routes: List[List[Dict[str, Any]]],
        completed_stops_per_vehicle: List[List[Dict[str, Any]]],
        disruption: DisruptionEvent,
        dist_matrix: np.ndarray,
        time_matrix: np.ndarray,
        round_trip: bool = True,
        fleet_size: int = 1,
        qpso_config: Optional[QPSOConfig] = None
    ) -> DisruptionPlan:
        """
        Executes forward-only rescheduling from the disruption point.
        
        Args:
            all_nodes: Master list of all stop dictionaries (depot at index 0)
            original_routes: Planned vehicle routes before disruption
            completed_stops_per_vehicle: Stops already completed by each vehicle
            disruption: DisruptionEvent specifying delay and timestamp
            dist_matrix: NxN distance matrix in km
            time_matrix: NxN free-flow time matrix in hours
            round_trip: Whether vehicles return to depot
            fleet_size: Number of vehicles
            qpso_config: Optional optimizer config overrides
            
        Returns:
            DisruptionPlan containing spliced routes and deviation analytics.
        """
        start_exec = time.time()
        
        # 1. Identify served stop names vs unserved stops
        served_names = set()
        for completed in completed_stops_per_vehicle:
            for s in completed:
                if s.get("name") != all_nodes[0].get("name"):
                    served_names.add(s["name"])
                    
        # Extract unserved customer stops
        unserved_stops = [
            s for s in all_nodes[1:] if s["name"] not in served_names
        ]
        
        if not unserved_stops:
            # All stops already served, return completed routes with return to depot
            return DisruptionPlan(
                routes=completed_stops_per_vehicle,
                total_cost=0.0,
                recovery_cost=0.0,
                deviation_cost=0.0,
                time_deviation_hrs=0.0,
                seq_deviation_count=0,
                execution_time_ms=0.0,
                iterations=0
            )
            
        # 2. Build Sub-Problem Node List
        # Node 0 in sub-problem is the current position / depot
        # For simplicity, if vehicles have a last completed stop, use depot or last stop as root
        depot_node = all_nodes[0]
        sub_nodes = [depot_node] + unserved_stops
        n_unserved = len(unserved_stops)
        
        # Build sub-matrices
        sub_dist, sub_time, sub_cong = MapAdapter.build_cost_matrices(sub_nodes)
        
        # Inject traffic delay into time matrix if affected edge is present
        if disruption.affected_edge is not None:
            u_sub, v_sub = disruption.affected_edge
            if 0 <= u_sub < len(sub_nodes) and 0 <= v_sub < len(sub_nodes):
                sub_time[u_sub, v_sub] += disruption.delay_hours
                
        # 3. Extract Baseline Planned ETAs and Order for Deviation Term
        orig_order_map = {}
        for r in original_routes:
            for rank, s in enumerate(r):
                orig_order_map[s["name"]] = rank
                
        # 4. Define Bi-Criterion Objective Function
        alpha = self.config.alpha
        adapter = MapAdapter(constraint_manager=self.constraint_manager)
        
        def disruption_fitness(vector: np.ndarray) -> float:
            sub_routes_idx = decode_routes_from_vector(
                vector, n_stops=n_unserved, fleet_size=fleet_size, start_idx=0, round_trip=round_trip
            )
            # A. Recovery Cost
            rec_cost, metrics = adapter.evaluate_routes(
                sub_routes_idx, sub_dist, sub_time, sub_cong, sub_nodes
            )
            
            # B. Deviation Cost relative to original plan
            seq_deviation = 0
            for r in sub_routes_idx:
                for rank, idx in enumerate(r):
                    if idx > 0 and idx < len(sub_nodes):
                        s_name = sub_nodes[idx]["name"]
                        orig_rank = orig_order_map.get(s_name, rank)
                        if rank != orig_rank:
                            seq_deviation += abs(rank - orig_rank)
                            
            dev_cost = (
                self.config.weight_seq_deviation * seq_deviation
            )
            
            return alpha * rec_cost + (1.0 - alpha) * dev_cost
            
        # 5. Warm-Start Swarm Initialization from Original Plan
        cfg = qpso_config or QPSOConfig()
        cfg.max_iter = self.config.reduced_max_iter
        M = cfg.swarm_size
        
        # Build initial positions array
        init_positions = np.random.uniform(0.0, 1.0, (M, n_unserved))
        n_warm = int(M * self.config.warm_start_ratio)
        
        if n_warm > 0:
            # Sort unserved stops by their original sequence order
            orig_sorted_perm = sorted(
                range(1, n_unserved + 1),
                key=lambda idx: orig_order_map.get(sub_nodes[idx]["name"], idx)
            )
            base_vec = permutation_to_continuous(orig_sorted_perm, offset=1)
            for i in range(n_warm):
                # Add slight Gaussian jitter to warm-started particles
                jitter = np.random.normal(0.0, 0.05, size=n_unserved)
                init_positions[i] = np.clip(base_vec + jitter, 0.0, 1.0)
                
        # 6. Execute Fast QPSO Optimization
        swarm = QPSOSwarm(
            dim=n_unserved,
            fitness_fn=disruption_fitness,
            bounds=(0.0, 1.0),
            config=cfg,
            initial_positions=init_positions
        )
        
        chaos_gen = ChaoticGenerator(map_type=cfg.chaos.map_type) if cfg.chaos.enabled else None
        best_pos, best_fit, stats = swarm.optimize(
            border_mutation_op=border_mutation_operator if cfg.border_mutation.enabled else None,
            chaos_generator=chaos_gen,
            selective_de_op=selective_de_operator if cfg.selective_de.enabled else None
        )
        
        # 7. Decode and Splice Sub-Routes with Completed Legs
        sub_node_routes = adapter.decode_to_node_routes(
            best_pos, sub_nodes, round_trip=round_trip, fleet_size=fleet_size
        )
        
        final_routes = []
        for v_idx in range(fleet_size):
            completed = completed_stops_per_vehicle[v_idx] if v_idx < len(completed_stops_per_vehicle) else [depot_node]
            new_leg = sub_node_routes[v_idx] if v_idx < len(sub_node_routes) else []
            
            # Avoid repeating depot if completed ends at depot and new_leg starts with depot
            if completed and new_leg and completed[-1]["name"] == new_leg[0]["name"]:
                spliced = completed[:-1] + new_leg
            else:
                spliced = completed + new_leg
            final_routes.append(spliced)
            
        exec_ms = (time.time() - start_exec) * 1000.0
        
        # Compute pure recovery and deviation components for reporting
        pure_rec_routes = decode_routes_from_vector(
            best_pos, n_stops=n_unserved, fleet_size=fleet_size, start_idx=0, round_trip=round_trip
        )
        pure_rec_cost, _ = adapter.evaluate_routes(pure_rec_routes, sub_dist, sub_time, sub_cong, sub_nodes)
        
        dev_cost_val = (best_fit - alpha * pure_rec_cost) / max(1e-5, (1.0 - alpha))
        
        return DisruptionPlan(
            routes=final_routes,
            total_cost=float(best_fit),
            recovery_cost=float(pure_rec_cost),
            deviation_cost=float(max(0.0, dev_cost_val)),
            time_deviation_hrs=disruption.delay_hours,
            seq_deviation_count=int(dev_cost_val / max(1.0, self.config.weight_seq_deviation)),
            execution_time_ms=float(exec_ms),
            iterations=stats["iterations"]
        )
