# Mathematical Formulation: Quantum-Behaved Particle Swarm Optimization (QPSO) for Vehicle Routing & Disruption Management

This document provides the complete, self-contained mathematical formulation of the **QPSO routing engine** implemented in `QRoute23`, synthesizing the theoretical models from Sun et al. (2004/2012), Li, Li & Wang (2012), Ning, Wang & Hu (2019), and Lim, Chin, Chai & Bose (2020).

---

## 1. Problem Formulation: Multi-Vehicle Routing Problem with Time Windows & Congestion (VRPTW-C)

Let $G = (V, E)$ be a complete directed graph where:
- $V = \{0, 1, 2, \dots, N\}$ is the set of nodes, with node $0$ denoting the central depot / hub and $V' = \{1, \dots, N\}$ denoting customer stops.
- $E = \{(i, j) : i, j \in V, i \neq j\}$ is the set of directed road edges.
- $K = \{1, 2, \dots, M_v\}$ is the set of available vehicles in the fleet.

### 1.1 Parameters
- $d_{ij} \ge 0$: Road network distance from node $i$ to node $j$ (km).
- $\tau_{ij} \ge 0$: Base free-flow travel time from node $i$ to node $j$ (hours).
- $w_{ij}^{\text{cong}} \ge 1.0$: Dynamic congestion multiplier for edge $(i, j)$.
- $[e_i, l_i]$: Hard/soft time window for node $i$, where $e_i$ is the earliest service start and $l_i$ is the latest acceptable service start.
- $s_i$: Service duration at node $i$ ($s_0 = 0$).
- $q_i$: Demand / payload required at node $i$ ($q_0 = 0$).
- $Q_k$: Maximum capacity of vehicle $k$.

### 1.2 Decision Variables
- $x_{ijk} \in \{0, 1\}$: $1$ if vehicle $k$ traverses edge $(i, j)$, $0$ otherwise.
- $t_{ik} \ge 0$: Arrival / service start time of vehicle $k$ at node $i$.

### 1.3 Objective Function
The routing cost combines travel distance, dynamic travel time, congestion penalties, and time-window violation penalties:

$$\min \mathcal{F}(X) = \sum_{k \in K} \sum_{i \in V} \sum_{j \in V} x_{ijk} \left( w_d d_{ij} + w_t (\tau_{ij} \cdot w_{ij}^{\text{cong}}) \right) + \sum_{k \in K} \sum_{i \in V'} \mathcal{P}_{\text{tw}}(t_{ik}, e_i, l_i) + \sum_{k \in K} \mathcal{P}_{\text{cap}}(k)$$

Where:
1. **Time Window Penalty** (with waiting allowed for early arrivals):
   $$t_{jk} = \max(e_j, t_{ik} + s_i + \tau_{ij} \cdot w_{ij}^{\text{cong}})$$
   $$\mathcal{P}_{\text{tw}}(t_{jk}, e_j, l_j) = \lambda_{\text{late}} \cdot \max(0, t_{jk} - l_j)$$
2. **Capacity Penalty**:
   $$\mathcal{P}_{\text{cap}}(k) = \lambda_{\text{cap}} \cdot \max\left(0, \sum_{i \in V'} q_i \sum_{j \in V} x_{ijk} - Q_k\right)$$

---

## 2. Core QPSO Mechanics (Sun, Feng, Xu Formulation)

In classical PSO, a particle moves along Newtonian trajectories dictated by position and velocity vectors. In **Quantum-behaved PSO**, particles move in a quantum state governed by a Schrödinger wave equation with a delta potential well centered at local attractor $p_i$.

### 2.1 Wave Function and Potential Well Model
The wave function $\psi(x)$ in a 1D delta potential well centered at $p$ is:

$$\psi(y) = \frac{1}{\sqrt{L}} \exp\left(-\frac{|y|}{L}\right), \quad y = x - p$$

The probability density function $Q(x)$ of finding the particle at position $x$ is:

$$Q(x) = |\psi(x)|^2 = \frac{1}{L} \exp\left(-\frac{2|x - p|}{L}\right)$$

Using inverse transform sampling with random variable $u \sim U(0, 1)$:

$$x = p \pm \frac{L}{2} \ln\left(\frac{1}{u}\right)$$

### 2.2 Swarm State Equations
Let $M$ be the swarm size and $D = |V'|$ be the problem dimension. For particle $i \in \{1, \dots, M\}$ at iteration $t$:
- **Position Vector**: $X_i(t) = (X_{i1}(t), X_{i2}(t), \dots, X_{iD}(t)) \in [0, 1]^D$.
- **Personal Best**: $P_i(t) = (p_{i1}(t), p_{i2}(t), \dots, p_{iD}(t))$.
- **Global Best**: $G(t) = (g_1(t), g_2(t), \dots, g_D(t)) = \arg\min_{P_i} \mathcal{F}(P_i)$.

### 2.3 Mean Best Position ($m_{\text{best}}$)
The center of quantum potential wells across the swarm is the mean of all personal best positions:

$$m_{\text{best}}(t) = \frac{1}{M} \sum_{i=1}^M P_i(t) = \left( \frac{1}{M} \sum_{i=1}^M p_{i1}(t), \dots, \frac{1}{M} \sum_{i=1}^M p_{iD}(t) \right)$$

### 2.4 Stochastic Local Attractor ($p_{ij}$)
For dimension $j \in \{1, \dots, D\}$:

$$p_{ij}(t) = \phi_{ij}(t) p_{ij}(t) + (1 - \phi_{ij}(t)) g_j(t), \quad \phi_{ij}(t) \sim U(0, 1)$$

### 2.5 Position Update Rule
The characteristic length of the potential well is set proportional to distance from $m_{\text{best}}$:

$$X_{ij}(t+1) = p_{ij}(t) \pm \beta(t) \cdot |m_{\text{best}, j}(t) - X_{ij}(t)| \cdot \ln\left(\frac{1}{u_{ij}(t)}\right)$$

Where:
- $u_{ij}(t) \sim U(0, 1)$.
- The sign $\pm$ is selected with equal probability ($0.5$).
- $\beta(t)$ is the **Contraction–Expansion Coefficient**, linearly annealed over iterations:
  $$\beta(t) = \beta_{\text{start}} - \left( \beta_{\text{start}} - \beta_{\text{end}} \right) \cdot \frac{t}{T_{\max}}$$
  Typical values: $\beta_{\text{start}} = 1.0 \to \beta_{\text{end}} = 0.5$.

---

## 3. Border Mutation & Chaos Operators (Li, Li & Wang, 2012)

Standard clipping ($X_{ij} = \text{clamp}(X_{ij}, 0, 1)$) destroys swarm diversity at the boundaries.

### 3.1 Border Mutation Operator
When $X_{ij}(t+1) \notin [0, 1]$, instead of clamping, apply reflect-and-perturb mutation:

$$X_{ij}(t+1) = \begin{cases}
-X_{ij}(t+1) + \gamma \cdot \text{chaos}(t) & \text{if } X_{ij}(t+1) < 0 \\
2.0 - X_{ij}(t+1) - \gamma \cdot \text{chaos}(t) & \text{if } X_{ij}(t+1) > 1
\end{cases}$$

If the mutated value remains outside $[0, 1]$, re-randomize via chaotic sequence draw: $X_{ij}(t+1) \leftarrow \text{chaos}_{j}(t)$.

### 3.2 Chaotic Sequence Generators
Replace pseudo-random uniform distributions with deterministic ergodic chaotic maps:

1. **Logistic Map**:
   $$z_{n+1} = \mu \cdot z_n (1 - z_n), \quad \mu = 4.0, \quad z_0 \in (0, 1) \setminus \{0.25, 0.5, 0.75\}$$
2. **Tent Map**:
   $$z_{n+1} = \begin{cases} \frac{z_n}{\alpha} & 0 < z_n \le \alpha \\ \frac{1 - z_n}{1 - \alpha} & \alpha < z_n \le 1 \end{cases}, \quad \alpha = 0.5$$

### 3.3 Chaotic Local Search (CLS) around $g_{\text{best}}$
Every $N_{\text{cls}}$ iterations, apply CLS in neighborhood of $g_{\text{best}}$:

$$g_{\text{cand}, j} = (1 - \lambda_k) g_j + \lambda_k z_{k, j}, \quad \lambda_k = 1 - \left(\frac{k - 1}{K_{\text{cls}}}\right)^2$$

If $\mathcal{F}(g_{\text{cand}}) < \mathcal{F}(g_{\text{best}})$, accept $g_{\text{best}} \leftarrow g_{\text{cand}}$.

---

## 4. Selective Differential Evolution Hybrid (Lim et al., 2020)

To prevent premature stagnation during online replanning without the computational overhead of full swarm DE, apply **Selective DE** to stagnating particles only.

### 4.1 Stagnation Counter
For each particle $i$, maintain counter $c_i$:

$$c_i(t+1) = \begin{cases} 0 & \text{if } \mathcal{F}(X_i(t+1)) < \mathcal{F}(P_i(t)) \\ c_i(t) + 1 & \text{otherwise} \end{cases}$$

### 4.2 Stagnation-Triggered DE Mutation & Crossover
When $c_i \ge k_{\text{stagnation}}$:
1. **Mutation (DE/rand/1 or DE/pbest/1)**:
   Select three mutually distinct indices $r_1, r_2, r_3 \in \{1, \dots, M\} \setminus \{i\}$:
   $$v_i = P_{r1} + F \cdot (P_{r2} - P_{r3}), \quad F \in [0.4, 0.9]$$
2. **Binomial Crossover**:
   $$u_{ij} = \begin{cases} v_{ij} & \text{if } \text{rand}_j \le CR \text{ or } j = j_{\text{rand}} \\ X_{ij} & \text{otherwise} \end{cases}, \quad CR \in [0.5, 0.9]$$
3. **Selection**:
   If $\mathcal{F}(u_i) < \mathcal{F}(X_i)$, update $X_i \leftarrow u_i$, $P_i \leftarrow u_i$, and reset $c_i \leftarrow 0$.

---

## 5. Disruption Management Model (Ning, Wang & Hu, 2019)

When an unexpected traffic delay occurs on edge $(u, v)$ at time $t_{\text{disrupt}}$:

### 5.1 Sub-Route Isolation
- Completed legs prior to $t_{\text{disrupt}}$ are **locked and immutable**.
- The remaining unserved customer set $V_{\text{unserved}} \subseteq V'$ and active vehicles are extracted into a reduced sub-problem.

### 5.2 Bi-Criterion Recovery Objective
The optimization balances recovery operational cost against deviation from the baseline committed schedule:

$$\min \mathcal{F}_{\text{disrupt}}(\Pi_{\text{new}}) = \alpha \cdot \mathcal{C}_{\text{recovery}}(\Pi_{\text{new}}) + (1 - \alpha) \cdot \mathcal{C}_{\text{deviation}}(\Pi_{\text{new}}, \Pi_{\text{orig}})$$

Where:
- $\alpha \in [0, 1]$: Weight parameter (typically $\alpha = 0.7$).
- $\mathcal{C}_{\text{recovery}}$: Total distance and duration of the remaining routes under updated traffic conditions.
- $\mathcal{C}_{\text{deviation}}$: Measure of customer schedule disruption:
  $$\mathcal{C}_{\text{deviation}} = w_{\text{time}} \sum_{i \in V_{\text{unserved}}} |t_i^{\text{new}} - t_i^{\text{orig}}| + w_{\text{seq}} \sum_{i \in V_{\text{unserved}}} \mathbb{I}(\text{pos}_{\text{new}}(i) \neq \text{pos}_{\text{orig}}(i))$$

### 5.3 Warm-Start Initialization
The initial positions of the recovery swarm are seeded around the projected unserved order from $\Pi_{\text{orig}}$ to accelerate convergence within tight real-time response budgets ($< 200 \text{ ms}$).

---

## 6. Continuous Vector $\leftrightarrow$ Discrete Route Encoding

### 6.1 Smallest Position Value (SPV) Rule
A continuous particle $X_i = (x_{i1}, x_{i2}, \dots, x_{iD}) \in [0, 1]^D$ is mapped to a discrete permutation $\pi = (\pi_1, \pi_2, \dots, \pi_D)$ by sorting indices by their continuous values:

$$\pi = \text{argsort}(X_i) + 1$$

### 6.2 Multi-Vehicle Partitioning
For fleet size $K > 1$, the permutation $\pi$ is segmented into $K$ vehicle routes either by:
1. Equal partition: Sub-array splitting of length $\lceil D / K \rceil$.
2. Capacity-constrained greedy cutting: Accumulating demand $q_{\pi_j}$ until $Q_k$ is reached.
3. K-Means spatial pre-clustering: Routing each cluster independently with dedicated start/return depot connections.
