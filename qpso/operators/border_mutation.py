"""
Border Mutation Operator for QPSO (Li, Li & Wang, 2012)
Prevents swarm boundary stagnation by reflecting and perturbing out-of-bounds coordinates.
"""
from typing import Tuple
import numpy as np


def border_mutation_operator(
    X: np.ndarray,
    bounds: Tuple[float, float] = (0.0, 1.0),
    mutation_rate: float = 0.15,
    rng: np.random.Generator = None
) -> np.ndarray:
    """
    Applies reflect-and-perturb boundary mutation to particle coordinate matrix X.
    
    Args:
        X: Particle positions matrix of shape (M, dim) or 1D array (dim,)
        bounds: (lower_bound, upper_bound)
        mutation_rate: Perturbation scaling factor
        rng: Optional NumPy random generator
        
    Returns:
        Mutated array within bounds with high diversity.
    """
    if rng is None:
        rng = np.random.default_rng()
        
    lower, upper = bounds
    span = upper - lower
    X_out = np.copy(X)
    
    # 1. Detect lower boundary breaches
    lower_mask = X_out < lower
    if np.any(lower_mask):
        # Reflect and add random perturbation
        perturb = rng.uniform(0.0, mutation_rate * span, size=np.count_nonzero(lower_mask))
        reflected = lower + (lower - X_out[lower_mask]) + perturb
        # If still outside, re-randomize uniformly within domain
        still_out = (reflected < lower) | (reflected > upper)
        reflected[still_out] = rng.uniform(lower, upper, size=np.count_nonzero(still_out))
        X_out[lower_mask] = reflected
        
    # 2. Detect upper boundary breaches
    upper_mask = X_out > upper
    if np.any(upper_mask):
        perturb = rng.uniform(0.0, mutation_rate * span, size=np.count_nonzero(upper_mask))
        reflected = upper - (X_out[upper_mask] - upper) - perturb
        still_out = (reflected < lower) | (reflected > upper)
        reflected[still_out] = rng.uniform(lower, upper, size=np.count_nonzero(still_out))
        X_out[upper_mask] = reflected
        
    return X_out
