import pytest
import numpy as np
from qpso.core import QPSOSwarm
from qpso.config import QPSOConfig

def sphere(x: np.ndarray) -> float:
    """Sphere benchmark function: min at 0 with f(0)=0."""
    return float(np.sum(x ** 2))

def rastrigin(x: np.ndarray) -> float:
    """Rastrigin multimodal benchmark: min at 0 with f(0)=0."""
    return float(10 * len(x) + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x)))

def test_qpso_sphere_convergence():
    """Verify QPSO reaches near-zero on 5D Sphere function."""
    dim = 5
    config = QPSOConfig(swarm_size=40, max_iter=200, seed=42)
    swarm = QPSOSwarm(dim=dim, fitness_fn=sphere, bounds=(-5.12, 5.12), config=config)
    
    best_pos, best_fit, stats = swarm.optimize()
    assert best_fit < 1e-3, f"Expected Sphere fitness < 1e-3, got {best_fit}"
    assert len(stats["history"]) > 1
    assert stats["history"][-1] <= stats["history"][0]

def test_qpso_rastrigin_convergence():
    """Verify QPSO optimizes multimodal 3D Rastrigin function."""
    dim = 3
    config = QPSOConfig(swarm_size=50, max_iter=250, seed=42)
    swarm = QPSOSwarm(dim=dim, fitness_fn=rastrigin, bounds=(-5.12, 5.12), config=config)
    
    best_pos, best_fit, stats = swarm.optimize()
    assert best_fit < 1.0, f"Expected Rastrigin fitness < 1.0, got {best_fit}"
    assert stats["iterations"] > 0
