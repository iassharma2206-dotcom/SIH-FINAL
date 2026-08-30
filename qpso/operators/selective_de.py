"""
Selective Differential Evolution (SDE) Operator for QPSO (Lim et al., 2020)
Applies DE mutation and binomial crossover to stagnated particles only.
"""
from typing import Tuple, Callable
import numpy as np
from qpso.config import SelectiveDEConfig


def selective_de_operator(
    X: np.ndarray,
    pbest: np.ndarray,
    stagnation_counters: np.ndarray,
    config: SelectiveDEConfig,
    fitness_fn: Callable[[np.ndarray], float],
    bounds: Tuple[float, float] = (0.0, 1.0),
    rng: np.random.Generator = None
) -> np.ndarray:
    """
    Identifies particles with stagnation >= k and applies DE/rand/1/bin exploration.
    
    Args:
        X: Current particle positions (M, dim)
        pbest: Swarm personal best positions (M, dim)
        stagnation_counters: Array of consecutive non-improving iterations (M,)
        config: SelectiveDEConfig containing stagnation_k, f_weight, crossover_rate
        fitness_fn: Objective evaluation function
        bounds: (lower, upper)
        rng: Optional NumPy random generator
        
    Returns:
        Updated particle positions matrix (M, dim)
    """
    if rng is None:
        rng = np.random.default_rng()
        
    M, dim = X.shape
    if M < 4:
        return X  # Need at least 4 particles for DE/rand/1 (target + 3 distinct donors)
        
    lower, upper = bounds
    X_out = np.copy(X)
    
    # Identify stagnating particles
    stagnated_indices = np.where(stagnation_counters >= config.stagnation_k)[0]
    
    for i in stagnated_indices:
        # Select 3 mutually distinct donor indices distinct from i
        available = [idx for idx in range(M) if idx != i]
        r1, r2, r3 = rng.choice(available, size=3, replace=False)
        
        # 1. DE Mutation: v_i = pbest_r1 + F * (pbest_r2 - pbest_r3)
        v_i = pbest[r1] + config.f_weight * (pbest[r2] - pbest[r3])
        v_i = np.clip(v_i, lower, upper)
        
        # 2. Binomial Crossover
        j_rand = rng.integers(0, dim)
        cr_mask = rng.uniform(0.0, 1.0, size=dim) <= config.crossover_rate
        cr_mask[j_rand] = True  # Ensure at least one dimension is crossed
        
        trial_vector = np.where(cr_mask, v_i, X_out[i])
        
        # 3. Selection
        trial_fit = fitness_fn(trial_vector)
        curr_fit = fitness_fn(X_out[i])
        
        if trial_fit < curr_fit:
            X_out[i] = trial_vector
            stagnation_counters[i] = 0  # Reset stagnation counter upon successful DE intervention
            
    return X_out
