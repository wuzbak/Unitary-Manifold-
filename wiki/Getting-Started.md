# Getting Started

This page covers installing the Unitary Manifold package and running the built-in examples.

---

## Requirements

- **Python 3.12+** (3.12 is the reference interpreter; 3.10/3.11 should work but are not tested)
- NumPy ≥ 1.24
- SciPy ≥ 1.11 (for holographic utilities, braided-winding solvers, and CMB transfer)
- pytest ≥ 7 (for running the test suite)

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

## Running the Test Suite

```bash
# Fast suite — core physics (run first):
python -m pytest tests/ -q
# Expected: 11450 passed, 1 skipped, 11 deselected, 0 failed

# Recycling / φ-debt entropy suite (Pillar 16):
python -m pytest recycling/ -q
# Expected: 316 passed, 0 failed

# Unitary Pentad governance suite (18 modules):
python -m pytest "Unitary Pentad/" -q
# Expected: 1266 passed, 0 failed

# Full repository (takes ~90 s):
python -m pytest tests/ recycling/ "Unitary Pentad/" -q
# Expected: 13031 passed, 1 skipped, 11 deselected, 0 failed

# Slow tests (Richardson extrapolation, ~2 min):
python -m pytest tests/ -m slow
```

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

### 5. CMB Observables & Braided Winding (Pillar 27)

Compute the CMB spectral index, birefringence angle, and braided tensor-to-scalar ratio:

```python
from src.core.inflation import ns_prediction, birefringence_angle
from src.core.braided_winding import braided_sound_speed, braided_r

n_w = 5            # winding number selected by Planck data
n1, n2 = 5, 7      # braid pair
k_cs = n1**2 + n2**2   # = 74 (sum-of-squares resonance)

ns  = ns_prediction(n_w)
beta = birefringence_angle(k_cs)
c_s  = braided_sound_speed(n1, n2, k_cs)
r    = braided_r(n_w, c_s)

print(f"ns = {ns:.4f}   (Planck: 0.9649 ± 0.0042)")
print(f"beta = {beta:.4f}°  (Komatsu 2022: ~0.35° ± 0.14°)")
print(f"c_s = {c_s:.4f}  (12/37 = {12/37:.4f})")
print(f"r_braided = {r:.4f}  (BICEP/Keck < 0.036)")
```

---

## Numerical Recommendations

| Setting | Recommended value | Notes |
|---------|-------------------|-------|
| Grid points `N` | 64 – 256 | Larger N = more spatial resolution |
| Grid spacing `dx` | 0.05 – 0.1 | Smaller dx improves derivative accuracy |
| Timestep `dt` | ≤ 1e-3 | CFL-like stability; use `cfl_timestep()` to estimate |
| KK coupling `lam` | 1.0 | Can be varied to explore coupling strength |
| Nonminimal coupling `alpha` | $\phi_0^{-2}$ (derived) | Do not set as a free parameter |
| Constraint-damping coeff | ≥ 0.1 | Recommended for runs > 500 steps |

---

## Project Structure

```
.
├── README.md
├── FALLIBILITY.md                  ← honest limitations
├── WHAT_THIS_MEANS.md              ← plain-language overview
├── UNIFICATION_PROOF.md            ← formal unification derivation
├── QUANTUM_THEOREMS.md             ← BH info, CCR, Hawking T, ER=EPR
├── requirements.txt
├── THEBOOKV9a (1).pdf              ← full 74-chapter monograph
├── manuscript/
│   └── ch02_mathematical_preliminaries.md
├── arxiv/
│   ├── main.tex
│   └── references.bib
├── src/
│   ├── core/                       ← Pillars 1–5 (field theory) + 27–74
│   │   ├── metric.py               ← KK ansatz, curvature tensors
│   │   ├── evolution.py            ← Walker–Pearson field evolution
│   │   ├── inflation.py            ← CMB power spectrum, ns, r
│   │   ├── braided_winding.py      ← (5,7) braid, c_s=12/37, r_braided
│   │   ├── transfer.py             ← Matter power spectrum
│   │   ├── cmb_transfer.py         ← E-H 1998 CMB transfer function (Pillar 63)
│   │   ├── completeness_theorem.py ← k_CS=74 uniqueness (Pillar 74)
│   │   └── ... (70+ additional modules)
│   ├── holography/
│   │   └── boundary.py             ← entropy-area, boundary dynamics
│   ├── multiverse/
│   │   └── fixed_point.py          ← UEUM, operator U, FTUM iteration
│   ├── consciousness/              ← Pillar 9: coupled brain-universe attractor
│   ├── chemistry/                  ← Pillar 10: bonds, reactions, periodic table
│   ├── astronomy/                  ← Pillar 11: stellar, planetary
│   ├── earth/                      ← Pillar 12: geology, oceanography, meteorology
│   ├── biology/                    ← Pillar 13: life, evolution, morphogenesis
│   ├── atomic_structure/           ← Pillar 14: orbitals, spectroscopy, fine structure
│   ├── cold_fusion/                ← Pillar 15: φ-enhanced tunneling, Pd lattice
│   ├── medicine/                   ← Pillar 17
│   ├── justice/                    ← Pillar 18
│   ├── governance/                 ← Pillar 19
│   ├── neuroscience/               ← Pillar 20
│   ├── ecology/                    ← Pillar 21
│   ├── climate/                    ← Pillar 22
│   ├── marine/                     ← Pillar 23
│   ├── psychology/                 ← Pillar 24
│   ├── genetics/                   ← Pillar 25
│   └── materials/                  ← Pillar 26
├── recycling/                      ← Pillar 16: φ-debt entropy accounting
├── Unitary Pentad/                 ← independent HILS governance framework
├── tests/                          ← 126 test files, ~10 000 fast-passing tests
├── bot/                            ← AI assistant infrastructure (RAG, Copilot Extension)
└── notebooks/                      ← Jupyter quickstart, boundary, multiverse demos
```
