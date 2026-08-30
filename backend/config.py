import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_DIR = os.path.join(BASE_DIR, "data")
CACHE_DIR = os.path.join(DATA_DIR, "cached_graphs")

# Default physics & algorithm hyperparameters
DEFAULT_QPSO_PARAMS = {
    "swarm_size": 30,
    "max_iter": 300,
    "beta_start": 1.0,
    "beta_end": 0.5,
    "plateau_window": 50
}
