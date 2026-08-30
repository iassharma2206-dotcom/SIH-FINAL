"""
Central Configuration & Tunables for QPSO Routing Engine
Consolidates hyperparameters, operator toggles, and feature flags.
"""
from dataclasses import dataclass, field
from typing import Optional, Literal

@dataclass
class ChaosConfig:
    enabled: bool = True
    map_type: Literal["logistic", "tent"] = "logistic"
    mu: float = 4.0               # Logistic map parameter (4.0 for full chaos)
    tent_alpha: float = 0.5       # Tent map symmetry parameter
    cls_interval: int = 25        # Chaotic Local Search (CLS) every N iterations
    cls_steps: int = 10           # Number of search steps per CLS event

@dataclass
class SelectiveDEConfig:
    enabled: bool = True
    stagnation_k: int = 15        # Trigger DE if particle fails to improve for k iterations
    f_weight: float = 0.6         # Differential weight F in [0.4, 0.9]
    crossover_rate: float = 0.7   # Crossover probability CR in [0.5, 0.9]

@dataclass
class BorderMutationConfig:
    enabled: bool = True
    mutation_rate: float = 0.15   # Perturbation strength when bouncing off boundaries

@dataclass
class DisruptionConfig:
    alpha: float = 0.7                     # Weight of recovery cost vs deviation cost in [0, 1]
    weight_time_deviation: float = 10.0    # Penalty per hour of customer ETA shift
    weight_seq_deviation: float = 5.0      # Penalty per rank shift in stop visitation order
    warm_start_ratio: float = 0.35         # Fraction of swarm initialized from original plan
    reduced_max_iter: int = 100            # Truncated iteration budget for fast real-time response

@dataclass
class QPSOConfig:
    swarm_size: int = 40
    max_iter: int = 300
    beta_start: float = 1.0
    beta_end: float = 0.5
    plateau_window: int = 50      # Convergence early stop if no gbest improvement
    tolerance: float = 1e-6
    seed: Optional[int] = None
    
    # Nested configs
    border_mutation: BorderMutationConfig = field(default_factory=BorderMutationConfig)
    chaos: ChaosConfig = field(default_factory=ChaosConfig)
    selective_de: SelectiveDEConfig = field(default_factory=SelectiveDEConfig)
    disruption: DisruptionConfig = field(default_factory=DisruptionConfig)
    
    # Feature flag (default = OFF for zero regression)
    feature_flag_enabled: bool = False

    @classmethod
    def from_dict(cls, d: Optional[dict]) -> "QPSOConfig":
        if not d:
            return cls()
        cfg = cls()
        if "swarm_size" in d: cfg.swarm_size = int(d["swarm_size"])
        if "max_iter" in d: cfg.max_iter = int(d["max_iter"])
        if "beta_start" in d: cfg.beta_start = float(d["beta_start"])
        if "beta_end" in d: cfg.beta_end = float(d["beta_end"])
        if "plateau_window" in d: cfg.plateau_window = int(d["plateau_window"])
        if "seed" in d: cfg.seed = int(d["seed"]) if d["seed"] is not None else None
        if "feature_flag_enabled" in d: cfg.feature_flag_enabled = bool(d["feature_flag_enabled"])
        return cfg
