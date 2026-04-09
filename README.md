# The Unitary Manifold (v9.0 — Academic Edition)

> *"Collapse entropy early. Gate compute. Enforce structure. Reduce variance."*

---

## 1 · Project Overview

The **Unitary Manifold** is a 5-dimensional gauge-geometric framework that
resolves the *dimensional misalignment* in modern physics.  Where traditional
theory treats irreversibility and the arrow of time as statistical accidents,
this work geometrises them as a 5D parent structure whose 4D projection
manifests as thermodynamics and information flow.

**Core objective:** derive 4D effective field equations — the
*Walker–Pearson field equations* — from a 5D Einstein–Hilbert action,
providing a unified geometric origin for gravity, irreversibility, and quantum
information.

---

## 2 · Mathematical Structure

### 5-D Metric Ansatz (Kaluza–Klein)

The irreversibility field $B_\mu$ is encoded as an off-diagonal metric component:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & 1 \end{pmatrix}$$

so that $G_{\mu 5} = \lambda B_\mu$.

### Key Fields

| Symbol | Name | Role |
|--------|------|------|
| $g_{\mu\nu}$ | 4-D metric | spacetime geometry |
| $B_\mu$ | irreversibility field | gauge field for the arrow of time |
| $\phi$ | entanglement-capacity scalar | nonminimal coupling to curvature |
| $H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$ | field strength | drives dissipation |

### Walker–Pearson Field Equations

$$G_{\mu\nu} + \lambda^2 \left( H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2 \right) + \alpha R \phi^2 g_{\mu\nu} = 8\pi G_4\, T_{\mu\nu}$$

### Conserved Information Current

$$\nabla_\mu J^\mu_{\inf} = 0, \qquad J^\mu_{\inf} = \phi^2 u^\mu$$

### Unified Equation of the Unitary Manifold (UEUM)

$$\ddot{X}^a + \Gamma^a_{bc}\dot{X}^b\dot{X}^c = G_U^{ab}\nabla_b S_U + \frac{\delta}{\delta X^a}\!\left(\sum_i \frac{A_{\partial,i}}{4G} + Q_{\rm top}\right)$$

### Final Theorem (FTUM)

There exists a fixed point $\Psi^*$ of the combined operator
$U = \mathbf{I} + \mathbf{H} + \mathbf{T}$
(Irreversibility + Holography + Topology) such that $U\Psi^* = \Psi^*$.

---

## 3 · Repository Structure

```
.
├── README.md
├── requirements.txt
├── THEBOOKV9a (1).pdf        ← full monograph
├── manuscript/
│   └── ch02_mathematical_preliminaries.md
├── discussions/
│   └── AI-Automated-Review-Invitation.md
└── src/
    ├── core/
    │   ├── metric.py         ← KK ansatz, curvature tensors
    │   └── evolution.py      ← Walker–Pearson field evolution
    ├── holography/
    │   └── boundary.py       ← Pillar 4: entropy-area, boundary dynamics
    └── multiverse/
        └── fixed_point.py    ← Pillar 5: UEUM, operator U, FTUM iteration
```

---

## 4 · Quickstart

### Install

```bash
pip install -r requirements.txt
```

### Run a bulk field simulation

```python
from src.core.evolution import FieldState, run_evolution

# Flat Minkowski background, 64 grid points, spacing dx=0.1
state = FieldState.flat(N=64, dx=0.1)

# Evolve for 200 steps with dt=1e-3
history = run_evolution(state, dt=1e-3, steps=200)

print(f"Final time: {history[-1].t:.3f}")
print(f"Final phi range: [{history[-1].phi.min():.4f}, {history[-1].phi.max():.4f}]")
```

### Compute curvature

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

### Holographic boundary (Pillar 4)

```python
from src.holography.boundary import BoundaryState, entropy_area, evolve_boundary
from src.core.evolution import FieldState

bulk = FieldState.flat(N=64, dx=0.1)
bdry = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)

print(f"Boundary entropy S = {entropy_area(bdry.h):.4f}")

bulk_evolved = __import__('src.core.evolution', fromlist=['step']).step(bulk, 1e-3)
bdry_evolved = evolve_boundary(bdry, bulk_evolved, dt=1e-3)
```

### Multiverse fixed-point (Pillar 5)

```python
from src.multiverse.fixed_point import MultiverseNetwork, fixed_point_iteration

network = MultiverseNetwork.chain(n=5, coupling=0.05)
result, residuals, converged = fixed_point_iteration(network, max_iter=300, tol=1e-6)

print(f"Converged: {converged}  after {len(residuals)} iterations")
print(f"Final residual: {residuals[-1]:.2e}")
```

---

## 5 · Numerical Pipeline (Appendix D)

```
┌─────────────────────────────────────────────────────┐
│              Numerical Evolution Pipeline            │
│                                                     │
│  1. Initialise  g_μν, B_μ, φ  (flat + perturbation)│
│  2. Compute curvature  (Γ, Riemann, Ricci, R)       │
│  3. Update fields  via Walker–Pearson equations     │
│  4. Enforce constraints  (monitor ‖R‖, ‖∇·J‖)      │
│  5. Project onto boundary  (holographic screen)     │
│  6. Apply U = I + H + T  (multiverse update)        │
│  7. Check FTUM convergence  ‖Ψⁿ⁺¹ − Ψⁿ‖ < ε       │
└─────────────────────────────────────────────────────┘
```

Recommended numerical settings:
- Staggered grids for $B_\mu$ (gauge field)
- Semi-implicit schemes for $\phi$ (scalar)
- Constraint damping coefficient ≥ 0.1 for long runs

---

## 6 · Monograph Structure

The full monograph (*74 chapters, XXIII parts*) is included as
`THEBOOKV9a (1).pdf`.  Key chapters:

| Chapters | Topic |
|----------|-------|
| 1–2 | Motivation & Mathematical Preliminaries |
| 3–6 | 5D Metric Construction & Dimensional Reduction |
| 7–9 | Walker–Pearson Field Equations |
| 49–55 | Irreversible Friedmann Equations & Holographic Fate |
| 56–62 | Multiverse Topology & Inter-Manifold Information Flow |
| 63–74 | Observers, Mind & Co-emergence of Classical Reality |

---

## 7 · License — Defensive Public Commons License v1.0 (2026)

This work is irrevocably dedicated to the **public domain**.

- **Universal Rights:** All persons have the perpetual, royalty-free right to
  study, reproduce, and modify this work.
- **Anti-Enclosure:** Exclusive claims, commercial patenting of the core
  equations, or proprietary gatekeeping are **strictly prohibited**.
- Attribution is requested but not legally required.

---

## 8 · Credits

| Role | Name / System |
|------|--------------|
| Principal Architect | ThomasCory Walker-Pearson |
| Synthesis & Verification | Gemini · ChatGPT · Microsoft Copilot |
| Version | 9.0 — Academic Edition |

For technical inquiries or peer-review submissions, use the LaTeX source files
and BibLaTeX citations provided in the accompanying documentation.
