import pytest
import numpy as np
from qpso.operators.chaos import ChaoticGenerator

def test_logistic_and_tent_sequence_properties():
    """Verify that chaotic maps produce bounded, non-trivial, distinct numbers in (0, 1)."""
    for map_type in ["logistic", "tent"]:
        cg = ChaoticGenerator(map_type=map_type, seed=0.314)
        seq = [cg.next_value() for _ in range(200)]
        
        assert all(0.0 < v < 1.0 for v in seq)
        # Verify sequence is non-constant with good ergodicity
        assert len(set(np.round(seq, 4))) > 100
        # Verify mean is reasonably dispersed in the middle
        assert 0.25 < np.mean(seq) < 0.75

def test_chaos_array_generation():
    """Verify matrix/tensor shape generation."""
    cg = ChaoticGenerator(map_type="logistic")
    arr = cg.next_array((10, 5))
    assert arr.shape == (10, 5)
    assert np.all(arr > 0.0) and np.all(arr < 1.0)

def test_chaotic_local_search():
    """Verify CLS can improve upon a sub-optimal candidate."""
    def sphere(x): return float(np.sum(x ** 2))
    
    cg = ChaoticGenerator(map_type="logistic", seed=0.456)
    suboptimal_gbest = np.array([2.0, 2.0, 2.0])
    best_cand, best_fit = cg.local_search(
        suboptimal_gbest, sphere, bounds=(-3.0, 3.0), steps=20, iter_idx=0, max_iter=100
    )
    assert best_fit <= sphere(suboptimal_gbest)
