
"""
Chaotic Sequence Generator and Chaos-Based Local Search (Li, Li & Wang, 2012)
Implements Logistic and Tent map ergodic sequence generators and chaotic local search (CLS).
"""
from typing import Tuple, Callable, Literal
import numpy as np


class ChaoticGenerator:
    """
    Ergodic chaotic sequence generator for replacing pseudo-random numbers
    and performing Chaos Local Search (CLS) around optimal swarm positions.
    """
    def __init__(
        self,
        map_type: Literal["logistic", "tent"] = "logistic",
        mu: float = 4.0,
        tent_alpha: float = 0.49999,  # Slight asymmetry prevents dyadic rational fixed-point collapse in IEEE-754
        seed: float = 0.7135
    ):
        self.map_type = map_type
        self.mu = mu
        self.tent_alpha = tent_alpha
        
        # Ensure seed avoids fixed/cycle points (0, 0.25, 0.5, 0.75, 1.0)
        s = float(seed)
        while s in [0.0, 0.25, 0.5, 0.75, 1.0] or s <= 0.0 or s >= 1.0:
            s = (s + 0.137) % 1.0
        self.state = s

    def next_value(self) -> float:
        """Generates next chaotic float in (0, 1)."""
        if self.map_type == "logistic":
            self.state = self.mu * self.state * (1.0 - self.state)
        elif self.map_type == "tent":
            if self.state <= self.tent_alpha:
                self.state = self.state / self.tent_alpha
            else:
                self.state = (1.0 - self.state) / (1.0 - self.tent_alpha)
                
        # Safeguard against numeric degeneration / fixed point traps in finite precision
        if self.state <= 1e-6 or self.state >= 1.0 - 1e-6 or np.isnan(self.state):
            self.state = (self.state * 1000.0 + 0.6180339887) % 1.0
            if self.state <= 1e-6:
                self.state = 0.381966
            
        return float(self.state)

    def next_array(self, shape: Tuple[int, ...]) -> np.ndarray:
        """Generates an array of chaotic values matching given shape."""
        count = int(np.prod(shape))
        vals = np.empty(count, dtype=float)
        for i in range(count):
            vals[i] = self.next_value()
        return vals.reshape(shape)

    def local_search(
        self,
        gbest: np.ndarray,
        fitness_fn: Callable[[np.ndarray], float],
        bounds: Tuple[float, float] = (0.0, 1.0),
        steps: int = 10,
        iter_idx: int = 0,
        max_iter: int = 300
    ) -> Tuple[np.ndarray, float]:
        """
        Applies Chaotic Local Search (CLS) around the global best position.
        
        Args:
            gbest: Current global best position (dim,)
            fitness_fn: Objective evaluation function
            bounds: (lower_bound, upper_bound)
            steps: Number of chaotic search trials
            iter_idx: Current outer iteration
            max_iter: Total iteration budget
            
        Returns:
            (best_position, best_fitness)
        """
        dim = len(gbest)
        lower, upper = bounds
        span = upper - lower
        
        best_cand = np.copy(gbest)
        best_cand_fit = fitness_fn(best_cand)
        
        # Anneal chaotic search radius as iterations progress
        # lambda shrinks from 1.0 to near 0.0
        lam = 1.0 - (iter_idx / max(1, max_iter)) ** 2
        lam = max(0.01, min(1.0, lam))
        
        for _ in range(steps):
            # Generate chaotic perturbation vector z in [0, 1]^dim
            z = self.next_array((dim,))
            z_scaled = lower + z * span
            
            # Linear combination: g_cand = (1 - lam) * gbest + lam * z_scaled
            cand = (1.0 - lam) * gbest + lam * z_scaled
            cand = np.clip(cand, lower, upper)
            
            fit = fitness_fn(cand)
            if fit < best_cand_fit:
                best_cand = np.copy(cand)
                best_cand_fit = fit
                
        return best_cand, best_cand_fit
