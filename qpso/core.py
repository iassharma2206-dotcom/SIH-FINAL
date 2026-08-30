"""
Core Quantum-Behaved Particle Swarm Optimization (QPSO) Engine
Vectorized implementation based on Sun, Feng, Xu Delta-Potential Well model.
"""
from typing import Callable, Optional, Dict, Any, Tuple
import time
import numpy as np

from qpso.config import QPSOConfig


class QPSOSwarm:
    """
    Continuous QPSO Swarm Optimizer.
    Fully vectorized over swarm dimension using NumPy.
    """
    def __init__(
        self,
        dim: int,
        fitness_fn: Callable[[np.ndarray], float],
        bounds: Tuple[float, float] = (0.0, 1.0),
        config: Optional[QPSOConfig] = None,
        initial_positions: Optional[np.ndarray] = None
    ):
        self.dim = dim
        self.fitness_fn = fitness_fn
        self.lower_bound, self.upper_bound = bounds
        self.config = config or QPSOConfig()
        
        # Initialize RNG
        if self.config.seed is not None:
            self.rng = np.random.default_rng(self.config.seed)
        else:
            self.rng = np.random.default_rng()
            
        self.M = self.config.swarm_size
        self.max_iter = self.config.max_iter
        
        # Particle positions: shape (M, dim)
        if initial_positions is not None:
            assert initial_positions.shape == (self.M, self.dim)
            self.X = np.copy(initial_positions)
        else:
            self.X = self.rng.uniform(self.lower_bound, self.upper_bound, (self.M, self.dim))
            
        self.pbest = np.copy(self.X)
        self.pbest_fitness = np.zeros(self.M)
        
        # Stagnation counters for Selective DE
        self.stagnation_counters = np.zeros(self.M, dtype=int)
        
        # Initial evaluation
        for i in range(self.M):
            self.pbest_fitness[i] = self.fitness_fn(self.pbest[i])
            
        gbest_idx = int(np.argmin(self.pbest_fitness))
        self.gbest = np.copy(self.pbest[gbest_idx])
        self.gbest_fitness = float(self.pbest_fitness[gbest_idx])
        
        # Telemetry & History
        self.history = [self.gbest_fitness]
        self.diversity_history = []
        self.tunnels = 0
        self.iterations_completed = 0
        self.early_stopped = False

    def optimize(
        self,
        border_mutation_op: Optional[Callable[[np.ndarray, Tuple[float, float]], np.ndarray]] = None,
        chaos_generator = None,
        selective_de_op: Optional[Callable] = None
    ) -> Tuple[np.ndarray, float, Dict[str, Any]]:
        """
        Executes the QPSO optimization loop.
        Returns:
            best_position: np.ndarray shape (dim,)
            best_fitness: float
            stats: telemetry dictionary
        """
        start_time = time.time()
        plateau_count = 0
        
        for it in range(self.max_iter):
            self.iterations_completed = it + 1
            
            # 1. Contraction-Expansion coefficient linear annealing
            beta = self.config.beta_start - (self.config.beta_start - self.config.beta_end) * (it / max(1, self.max_iter))
            
            # 2. Mean Best Position (mbest)
            mbest = np.mean(self.pbest, axis=0) # shape (dim,)
            
            # 3. Vectorized QPSO Update
            # Attractor weights phi ~ U(0, 1)
            phi = self.rng.uniform(0.0, 1.0, (self.M, self.dim))
            # Local attractor p = phi * pbest + (1 - phi) * gbest
            p = phi * self.pbest + (1.0 - phi) * self.gbest
            
            # Quantum wave sampling u ~ U(0, 1)
            u = np.maximum(self.rng.uniform(0.0, 1.0, (self.M, self.dim)), 1e-12)
            signs = np.where(self.rng.uniform(0.0, 1.0, (self.M, self.dim)) < 0.5, 1.0, -1.0)
            
            # Update candidate position
            X_new = p + signs * beta * np.abs(mbest - self.X) * np.log(1.0 / u)
            
            # 4. Border Mutation handling
            if self.config.border_mutation.enabled and border_mutation_op is not None:
                X_new = border_mutation_op(X_new, (self.lower_bound, self.upper_bound))
            else:
                X_new = np.clip(X_new, self.lower_bound, self.upper_bound)
                
            # 5. Selective Differential Evolution (Lim et al., 2020)
            if self.config.selective_de.enabled and selective_de_op is not None:
                X_new = selective_de_op(
                    X_new, self.pbest, self.stagnation_counters,
                    self.config.selective_de, self.fitness_fn, (self.lower_bound, self.upper_bound)
                )
                
            # 6. Evaluation and pbest / gbest update
            improved_global = False
            for i in range(self.M):
                candidate_fit = self.fitness_fn(X_new[i])
                
                # Quantum tunneling metric
                if candidate_fit > self.pbest_fitness[i] and self.rng.uniform() < 0.05:
                    self.tunnels += 1
                    
                if candidate_fit < self.pbest_fitness[i]:
                    self.pbest[i] = np.copy(X_new[i])
                    self.pbest_fitness[i] = candidate_fit
                    self.stagnation_counters[i] = 0
                    
                    if candidate_fit < self.gbest_fitness - self.config.tolerance:
                        self.gbest = np.copy(X_new[i])
                        self.gbest_fitness = float(candidate_fit)
                        improved_global = True
                else:
                    self.stagnation_counters[i] += 1
                    
            self.X = X_new
            
            # 7. Chaotic Local Search (CLS) around gbest if enabled
            if (
                self.config.chaos.enabled
                and chaos_generator is not None
                and (it + 1) % self.config.chaos.cls_interval == 0
            ):
                cls_cand, cls_fit = chaos_generator.local_search(
                    self.gbest, self.fitness_fn, (self.lower_bound, self.upper_bound),
                    steps=self.config.chaos.cls_steps, iter_idx=it, max_iter=self.max_iter
                )
                if cls_fit < self.gbest_fitness:
                    self.gbest = np.copy(cls_cand)
                    self.gbest_fitness = float(cls_fit)
                    improved_global = True
                    
            # Track history and diversity
            self.history.append(float(self.gbest_fitness))
            diversity = float(np.mean(np.linalg.norm(self.X - mbest, axis=1)))
            self.diversity_history.append(diversity)
            
            # 8. Convergence Check & Early Stopping
            if improved_global:
                plateau_count = 0
            else:
                plateau_count += 1
                
            if plateau_count >= self.config.plateau_window:
                self.early_stopped = True
                break
                
        execution_time_ms = (time.time() - start_time) * 1000.0
        
        stats = {
            "gbest_fitness": float(self.gbest_fitness),
            "iterations": self.iterations_completed,
            "early_stopped": self.early_stopped,
            "execution_time_ms": float(execution_time_ms),
            "tunnels": self.tunnels,
            "history": self.history,
            "diversity_history": self.diversity_history
        }
        
        return self.gbest, self.gbest_fitness, stats
