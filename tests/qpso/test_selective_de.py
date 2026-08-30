import pytest
import numpy as np
from qpso.operators.selective_de import selective_de_operator
from qpso.config import SelectiveDEConfig

def test_selective_de_stagnation_trigger():
    """Verify Selective DE only mutates particles whose stagnation counter >= k."""
    def fitness_fn(x): return float(np.sum(x ** 2))
    
    # 5 particles in 2D
    X = np.array([
        [1.0, 1.0],  # particle 0: fit = 2.0
        [2.0, 2.0],  # particle 1: fit = 8.0 (stagnated)
        [0.5, 0.5],  # particle 2: fit = 0.5
        [0.2, 0.2],  # particle 3: fit = 0.08
        [0.1, 0.1],  # particle 4: fit = 0.02
    ])
    pbest = np.copy(X)
    stagnation_counters = np.array([0, 15, 0, 0, 0])  # only particle 1 has stagnated (k=15)
    
    cfg = SelectiveDEConfig(stagnation_k=15, f_weight=0.5, crossover_rate=1.0)
    rng = np.random.default_rng(42)
    
    X_updated = selective_de_operator(
        X, pbest, stagnation_counters, cfg, fitness_fn, bounds=(0.0, 5.0), rng=rng
    )
    
    # Particles 0, 2, 3, 4 must remain strictly untouched
    assert np.array_equal(X_updated[0], X[0])
    assert np.array_equal(X_updated[2], X[2])
    assert np.array_equal(X_updated[3], X[3])
    assert np.array_equal(X_updated[4], X[4])
    
    # Particle 1 either improved or stayed same
    assert fitness_fn(X_updated[1]) <= fitness_fn(X[1])

def test_selective_de_improves_stagnated_swarm():
    """Verify that integrating Selective DE helps swarm escape local minima."""
    from qpso.core import QPSOSwarm
    from qpso.config import QPSOConfig
    from qpso.operators.selective_de import selective_de_operator
    from qpso.operators.border_mutation import border_mutation_operator
    
    # Rastrigin function
    def rastrigin(x):
        return float(10 * len(x) + np.sum(x ** 2 - 10 * np.cos(2 * np.pi * x)))
        
    cfg = QPSOConfig(swarm_size=40, max_iter=150, seed=123)
    cfg.selective_de.enabled = True
    cfg.selective_de.stagnation_k = 10
    
    swarm = QPSOSwarm(dim=4, fitness_fn=rastrigin, bounds=(-5.12, 5.12), config=cfg)
    best_pos, best_fit, stats = swarm.optimize(
        border_mutation_op=border_mutation_operator,
        selective_de_op=selective_de_operator
    )
    assert best_fit < 2.0
