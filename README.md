# QRoute23: Quantum-Inspired Intelligent Traffic Route Optimizer

A state-of-the-art quantum-behaved route optimization and disruption management platform for dynamic Vehicle Routing Problems (VRP), Multi-Vehicle Delivery Scheduling (MTSP), and real-time traffic delay recovery.

---

## 🌟 Key Features

- ⚛️ **QPSO Mathematical Formulation & Live Engine**: Interactive educational dashboard showcasing the quantum physics mechanics of QPSO, side-by-side route trade-off calculations (Dijkstra/Average vs. QPSO), and a step-by-step numerical execution simulator.
- 🚦 **Real-Time Traffic Flow Integration**: Ingests live TomTom Traffic API data and adjusts edge travel speeds dynamically to bypass traffic bottlenecks.
- 📊 **Mission Control Dashboard**: High-impact centered command center providing real-time fleet health, flow topology, and active node synchronization.
- 🚚 **Live Vehicle Dispatch Simulation**: Real-time simulation control featuring animated vehicle routes, traffic delay calculations, and standardized transit metrics: `{minutes} min ({hours} hrs)`.
- 📄 **Automated PDF Route Audit Generator**: Generates comprehensive PDF audit reports with synchronized telemetry data, fuel savings, and route itineraries.

---

## ⚛️ Quantum-Behaved PSO (QPSO) Mathematics

Unlike classical Particle Swarm Optimization (PSO) which uses deterministic velocity vectors and risks local minima trapping, QPSO models swarm particles as quantum wavefunctions bound inside a 1D Delta-Potential Well.

### 1. Quantum Delta-Potential Position Update
$$x_i(t+1) = p_i(t) \pm \alpha \cdot | \text{mbest}(t) - x_i(t) | \cdot \ln(1 / u), \quad u \sim U(0, 1)$$

### 2. Mean Best Position ($\text{mbest}$) Center of Mass
$$\text{mbest}(t) = \frac{1}{N} \sum_{i=1}^{N} p_i(t)$$

### 3. Stochastic Local Attractor ($p_i$)
$$p_i(t) = \phi \cdot pbest_i(t) + (1 - \phi) \cdot gbest(t), \quad \phi \sim U(0, 1)$$

### 4. Smallest Position Value (SPV) Mapping
Sorts continuous position vector coordinates $x_i \in \mathbb{R}^d$ to generate discrete customer stop permutations $\pi_i$, which are split across vehicle capacity and time window constraints.

---

## 🚀 Quick Start

### 1. Requirements
- **Python**: 3.12+
- **Node.js**: 18+ (for frontend compilation)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Is-that-sneehal/qpso.git
cd qpso

# Create & activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Running the Unified Application (Recommended)

Build the React frontend distribution and start the FastAPI production server on port 8000:

```bash
# 1. Build Frontend Distribution
cd frontend
npm install
npm run build
cd ..

# 2. Start FastAPI Server
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Web Platform**: [http://localhost:8000](http://localhost:8000)
- **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Frontend Development Mode

For hot-reloading frontend development:

```bash
cd frontend
npm run dev
```
- **Vite Dev Server**: [http://localhost:3000](http://localhost:3000)

---

## 📁 Repository Structure

```
qpso/
├── backend/                  # FastAPI Application & REST Endpoints
│   ├── main.py               # Application entry point & static mount
│   ├── api/
│   │   ├── routes_optimize.py# REST optimization API
│   │   └── routes_reports.py # PDF report download routes
├── qpso/                     # Quantum Optimization Core Engine
│   ├── algorithm.py          # Delta-Potential QPSO solver
│   ├── operators/            # Chaos mutation & Differential Evolution operators
│   └── map_adapter.py        # Graph distance matrix & traffic adapter
├── frontend/                 # React 18 + Vite + Tailwind CSS Application
│   ├── src/
│   │   ├── screens/          # Dashboard, Simulation, Engine & QPSO Implementation
│   │   ├── components/       # Navbar, Footer, RouteMap & ReportModal
│   │   └── App.tsx           # Main application routing & state
├── report_generator.py       # ReportLab PDF Generation Engine
├── tests/                    # Pytest Suite (40 Passing Tests)
└── requirements.txt          # Python dependencies
```

---

## 🧪 Testing & Validation

Run the complete backend test suite:

```bash
python -m pytest tests/ -v
```

Output:
```
============================= 40 passed in 45.68s =============================
```

---

## 📜 License

Distributed under the MIT License. See `LICENSE` for details.
