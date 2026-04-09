# Getting Started

This page covers installing the Unitary Manifold package and running the built-in examples.

---

## Requirements

- Python 3.9+
- NumPy ≥ 1.24
- SciPy ≥ 1.10 (for advanced holographic utilities)

All dependencies are listed in [`requirements.txt`](../requirements.txt).

---

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-.git
cd Unitary-Manifold-
pip install -r requirements.txt
```

No build step is required — the package is importable directly from the repository root.

---

## Quickstart Examples

### 1. Bulk Field Simulation

Evolve the Walker–Pearson fields ($g_{\mu\nu}$, $B_\mu$, $\phi$) on a flat Minkowski background:

```python
from src.core.evolution import FieldState, run_evolution

# Flat Minkowski background, 64 grid points, spacing dx=0.1
state = FieldState.flat(N=64, dx=0.1)

# Evolve for 200 steps with dt=1e-3
history = run_evolution(state, dt=1e-3, steps=200)

print(f"Final time: {history[-1].t:.3f}")
print(f"Final phi range: [{history[-1].phi.min():.4f}, {history[-1].phi.max():.4f}]")
```

### 2. Curvature Computation

Compute Christoffel symbols, Riemann tensor, Ricci tensor, and scalar curvature:

```python
from src.core.metric import compute_curvature
import numpy as np

N, dx = 64, 0.1
eta = np.diag([-1., 1., 1., 1.])
g   = np.tile(eta, (N, 1, 1))
B   = np.zeros((N, 4))
phi = np.ones(N)

Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
print("Scalar curvature (flat space):", R.mean())   # ≈ 0
```

### 3. Holographic Boundary (Pillar 4)

Project the bulk onto its holographic boundary screen and track entropy:

```python
from src.holography.boundary import BoundaryState, entropy_area, evolve_boundary
from src.core.evolution import FieldState, step

bulk  = FieldState.flat(N=64, dx=0.1)
bdry  = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)

print(f"Initial boundary entropy S = {entropy_area(bdry.h):.4f}")

bulk_evolved = step(bulk, dt=1e-3)
bdry_evolved = evolve_boundary(bdry, bulk_evolved, dt=1e-3)
print(f"Evolved boundary entropy S = {entropy_area(bdry_evolved.h):.4f}")
```

### 4. Multiverse Fixed-Point (Pillar 5)

Run the FTUM (Final Theorem of the Unitary Manifold) iteration on a chain of coupled universes:

```python
from src.multiverse.fixed_point import MultiverseNetwork, fixed_point_iteration

network = MultiverseNetwork.chain(n=5, coupling=0.05)
result, residuals, converged = fixed_point_iteration(network, max_iter=300, tol=1e-6)

print(f"Converged: {converged}  after {len(residuals)} iterations")
print(f"Final residual: {residuals[-1]:.2e}")
```

---

## Numerical Recommendations

| Setting | Recommended value | Notes |
|---------|-------------------|-------|
| Grid points `N` | 64 – 256 | Larger N = more spatial resolution |
| Grid spacing `dx` | 0.05 – 0.1 | Smaller dx improves derivative accuracy |
| Timestep `dt` | ≤ 1e-3 | CFL-like stability for explicit Euler |
| KK coupling `lam` | 1.0 | Can be varied to explore coupling strength |
| Nonminimal coupling `alpha` | 0.1 | Controls $\alpha R \phi$ scalar source term |
| Constraint-damping coeff | ≥ 0.1 | Recommended for runs > 500 steps |

---

## Project Structure

```
.
├── README.md
├── requirements.txt
├── THEBOOKV9a (1).pdf          ← full monograph
├── manuscript/
│   └── ch02_mathematical_preliminaries.md
├── discussions/
│   └── AI-Automated-Review-Invitation.md
├── arxiv/
│   ├── main.tex
│   └── references.bib
└── src/
    ├── core/
    │   ├── metric.py           ← KK ansatz, curvature tensors
    │   └── evolution.py        ← Walker–Pearson field evolution
    ├── holography/
    │   └── boundary.py         ← entropy-area, boundary dynamics
    └── multiverse/
        └── fixed_point.py      ← UEUM, operator U, FTUM iteration
```
