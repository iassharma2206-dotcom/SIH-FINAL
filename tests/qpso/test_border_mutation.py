import pytest
import numpy as np
from qpso.operators.border_mutation import border_mutation_operator

def test_border_mutation_bounds_retention():
    """Verify that out-of-bound particles are reflected back inside bounds with perturbation."""
    # Array with values outside [0.0, 1.0]
    X_out = np.array([
        [-0.5, 1.5, 0.5],
        [-1.2, 0.3, 2.1]
    ])
    mutated = border_mutation_operator(X_out, bounds=(0.0, 1.0), mutation_rate=0.1)
    assert np.all(mutated >= 0.0)
    assert np.all(mutated <= 1.0)
    # Inside values are preserved
    assert mutated[0, 2] == 0.5
    assert mutated[1, 1] == 0.3

def test_border_mutation_diversity():
    """Verify border mutation produces diverse positions rather than collapsing to boundary."""
    # 50 particles all at -0.1
    X_clamped = np.full((50, 1), -0.1)
    mutated = border_mutation_operator(X_clamped, bounds=(0.0, 1.0), mutation_rate=0.2)
    # Should not all equal 0.0
    assert np.std(mutated) > 0.01
