# Quantum-Inspired Particle Swarm Optimization (QPSO) Mathematical Specification

## 1. Overview & Physics Formulation
QPSO is a quantum-inspired metaheuristic based on quantum mechanical principles (Sun, Feng, Xu formulation). Unlike Classical Particle Swarm Optimization (CPSO) which relies on Newtonian mechanics and velocity vectors, QPSO models particles in a quantum delta-potential-well with bound state solutions.

In QPSO, a particle has no trajectory or velocity vector $v_{ij}$. Instead, its position probability distribution is governed by the wave function $\psi(x)$, enabling non-zero probability of tunneling through high-energy energy barriers (local minima).

## 2. Mathematical Equations

For a swarm of size $M$, particle $i \in \{1..M\}$, dimension $j \in \{1..n\}$ at iteration $t$:

### 2.1 Mean Best Position ($mbest$)
$$mbest(t) = \frac{1}{M} \sum_{i=1}^M pbest_i(t)$$

### 2.2 Stochastic Attractor ($p_{ij}$)
$$p_{ij}(t) = \phi_j \cdot pbest_{ij}(t) + (1 - \phi_j) \cdot gbest_j(t), \quad \phi_j \sim \text{Uniform}(0, 1)$$

### 2.3 Position Update (Delta-Potential Well Equation)
$$u_{ij} \sim \text{Uniform}(0, 1)$$
$$\text{sign} = \begin{cases} +1 & \text{with probability } 0.5 \\ -1 & \text{with probability } 0.5 \end{cases}$$
$$x_{ij}(t+1) = p_{ij}(t) \pm \beta(t) \cdot |mbest_j(t) - x_{ij}(t)| \cdot \ln\left(\frac{1}{u_{ij}}\right)$$

### 2.4 Contraction-Expansion Coefficient ($\beta$)
Linear annealing schedule:
$$\beta(t) = \beta_{start} - (\beta_{start} - \beta_{end}) \cdot \frac{t}{t_{max}}$$
Default: $\beta_{start} = 1.0 \rightarrow \beta_{end} = 0.5$.

## 3. Discretization via Smallest Position Value (SPV) Rule
Continuous particle vector $X_i \in \mathbb{R}^n \rightarrow$ Discrete permutation sequence $\pi$:
$$\pi = \text{argsort}(X_i) + 1$$
Depot node $0$ is prepended/appended after decoding.
