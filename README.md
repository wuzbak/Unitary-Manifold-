# The Unitary Manifold (v9.0 — Academic Edition)

> *"Collapse entropy early. Gate compute. Enforce structure. Reduce variance."*

[![Tests](https://github.com/wuzbak/Unitary-Manifold-/actions/workflows/tests.yml/badge.svg)](https://github.com/wuzbak/Unitary-Manifold-/actions/workflows/tests.yml)
[![MCP Ready](https://img.shields.io/badge/MCP-ready-blue)](mcp-config.json)
[![AI Ingest](https://img.shields.io/badge/AI%20Ingest-MCP__INGEST.md-green)](MCP_INGEST.md)
[![llms.txt](https://img.shields.io/badge/llms.txt-ready-orange)](llms.txt)
[![Download ZIP](https://img.shields.io/badge/Download-ZIP-brightgreen?logo=github)](https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip)

---

## ⬇ Download

| Method | Link |
|--------|------|
| **ZIP (latest main branch)** | [**Download ZIP ↓**](https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip) |
| **Tarball (latest main branch)** | [Download tar.gz ↓](https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.tar.gz) |
| **Releases page** | [GitHub Releases](https://github.com/wuzbak/Unitary-Manifold-/releases) |
| **Full download guide** | [DOWNLOAD_GUIDE.md](DOWNLOAD_GUIDE.md) |

> You can also click the green **`<> Code`** button on the repository home page and choose **Download ZIP**.

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

The irreversibility field $B_\mu$ and scalar $\phi$ are encoded in the off-diagonal and radion blocks of the 5D parent metric:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$$

The lower-right entry $G_{55} = \phi^2$ means $\phi$ plays the role of the **KK radion** — it sets the size of the compact fifth dimension and is *not* frozen to a constant.  Setting $\phi = 1$ everywhere would hide all scalar dynamics and break the dimensional reduction.

### Key Fields

| Symbol | Name | Role |
|--------|------|------|
| $g_{\mu\nu}$ | 4-D metric | spacetime geometry |
| $B_\mu$ | irreversibility field | gauge field for the arrow of time |
| $\phi$ | entanglement-capacity scalar / radion | nonminimal coupling to curvature; sets size of 5th dimension |
| $H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$ | field strength | drives dissipation |

---

## 2a · The 4D → 5D → 4D Computation Pipeline

Every call to `compute_curvature(g, B, phi, dx)` executes a three-stage
dimensional pipeline.  Understanding this pipeline is essential for interpreting
any curvature or evolution output.

### Why go through 5D at all?

Straightforward 4D curvature of $g_{\mu\nu}$ alone cannot see the
irreversibility field $B_\mu$ or the scalar $\phi$.  The Kaluza–Klein ansatz
packages all three fields into a single geometric object $G_{AB}$ so that
Einstein's equations in 5D automatically generate the coupled
Walker–Pearson equations upon dimensional reduction — no extra source terms
need to be added by hand.

### Stage 1 — Lift: 4D fields → 5D metric

The three input fields are assembled into the $5\times 5$ parent metric:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$$

```python
G5 = assemble_5d_metric(g, B, phi, lam)   # shape (N, 5, 5)
```

Key points:
- The **4×4 block** $G_{\mu\nu}$ carries the metric and the kinetic term of $B_\mu$.
- The **off-diagonal column/row** $G_{\mu 5} = \lambda\phi B_\mu$ encodes the irreversibility field.
- The **radion** $G_{55} = \phi^2$ is dynamic; it must evolve with $\phi$, not be fixed at 1.

### Stage 2 — Curve: 5D Christoffel symbols and Riemann tensor

Standard differential geometry is applied to $G_{AB}$:

$$\Gamma^C_{AB} = \tfrac{1}{2}\,G^{CD}\!\left(\partial_A G_{BD} + \partial_B G_{AD} - \partial_D G_{AB}\right)$$

$$R^D{}_{CAB} = \partial_A\Gamma^D_{BC} - \partial_B\Gamma^D_{AC} + \Gamma^D_{AE}\Gamma^E_{BC} - \Gamma^D_{BE}\Gamma^E_{AC}$$

```python
Gamma5 = christoffel(G5, dx)               # shape (N, 5, 5, 5)
Riem5  = _riemann_from_christoffel(Gamma5, dx)  # shape (N, 5, 5, 5, 5)
```

This step is where $B_\mu$ and $\phi$ contribute to the geometry — through
the derivatives of $G_{AB}$ that appear inside $\Gamma$.

### Stage 3 — Project: 5D Ricci → 4D Ricci block

The 5D Ricci tensor $\mathcal{R}_{AB} = R^C{}_{ACB}$ is contracted and its
$4\times 4$ block extracted:

$$R_{\mu\nu}^{(4D)} = \mathcal{R}_{\mu\nu}|_{A,B \in \{0,1,2,3\}}$$

$$R^{(4D)} = g^{\mu\nu}R_{\mu\nu}^{(4D)}$$

```python
# 5D Ricci (full 5×5)
Ricci5[:, A, B] = sum_C Riem5[:, C, A, C, B]

# Project: keep only the 4D block
Ricci = Ricci5[:, :4, :4]          # (N, 4, 4) — effective 4D Ricci
R     = einsum('nij,nij->n', g_inv, Ricci)  # (N,) — 4D scalar curvature
```

The returned `Gamma`, `Riemann`, `Ricci`, `R` are all the 4D blocks of the
5D tensors — they contain the full KK contribution from $B_\mu$ and $\phi$
that a naive 4D calculation would miss.

### At a glance

```
  ┌──────────────────────────────────────────────────────────────────┐
  │   4D inputs          5D geometry           4D outputs            │
  │                                                                  │
  │  g_μν (N,4,4)  ─┐                                               │
  │  B_μ  (N,4)    ──┤→  G_AB (N,5,5)  →  Γ^C_AB  →  R^D_CAB      │
  │  φ    (N,)     ─┘         ↑               ↓                     │
  │                     assemble_5d_metric   contract → Ricci5       │
  │                                               ↓                  │
  │                                         Ricci5[:,:4,:4] → Ricci │
  │                                         g⁻¹ · Ricci    → R     │
  └──────────────────────────────────────────────────────────────────┘
```

### Common pitfalls

| Mistake | Consequence |
|---------|-------------|
| Set $G_{55} = 1$ (freeze radion) | $\phi$ dynamics vanish; scalar equation decouples from geometry |
| Compute Christoffel from $g$ directly | $B_\mu$ and $\phi$ contribute nothing to curvature; Walker–Pearson equations reduce to vacuum GR |
| Apply explicit Euler to metric without Nyquist damping | High-frequency modes grow as $e^{t/dx^2}$; simulation blows up |
| Use explicit-only scalar update | Same blow-up for $\phi$ at large $dt/dx^2$ |

---

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
├── THEBOOKV9a (1).pdf        ← full monograph (READ-ONLY canonical reference)
├── manuscript/               ← LaTeX/Markdown monograph source (READ-ONLY)
│   └── ch02_mathematical_preliminaries.md
├── discussions/
│   └── AI-Automated-Review-Invitation.md
├── docs/
│   └── semantic-bridge.md    ← predicate map: theory ↔ implementation
├── .github/
│   ├── CONTEXT_SSCE.md       ← AI/Copilot Global Context Manifest (this file)
│   └── copilot-instructions.md
└── src/                      ← numerical implementation (editable)
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

### Compute curvature (via 4D→5D→4D pipeline)

```python
from src.core.metric import compute_curvature
import numpy as np

N, dx = 64, 0.1
eta = np.diag([-1., 1., 1., 1.])
g   = np.tile(eta, (N, 1, 1))
B   = np.zeros((N, 4))
phi = np.ones(N)

# Internally: assembles G_AB (5D) → 5D Christoffel/Riemann/Ricci → projects 4D block
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
┌──────────────────────────────────────────────────────────────────────┐
│                    Numerical Evolution Pipeline                      │
│                                                                      │
│  1. Initialise  g_μν, B_μ, φ  (flat Minkowski + small perturbation) │
│                                                                      │
│  2. Curvature via 4D→5D→4D pipeline  (see §2a)                      │
│       a. Lift: assemble G_AB (5×5) from g, B, φ                     │
│       b. Curve: 5D Christoffel symbols → Riemann → Ricci5           │
│       c. Project: Ricci = Ricci5[:,:4,:4],  R = g⁻¹·Ricci           │
│                                                                      │
│  3. Update fields  via Walker–Pearson equations                      │
│       g:  semi-implicit Nyquist  g_new = (g + dt·dg + dt·c·η)       │
│                                         ────────────────────────     │
│                                              1 + dt·c,  c = 4/dx²   │
│       B:  explicit  B_new = B + dt·∂_ν(λ² H^νμ)                     │
│       φ:  semi-implicit  φ_new = (φ + dt·(αRφ + S_H + lap_φ))      │
│                                  ─────────────────────────────      │
│                                         1 + dt·2/dx²                │
│                                                                      │
│  4. Enforce constraints  (monitor ‖Ricci‖, ‖∇·J‖)                   │
│  5. Project onto boundary  (holographic screen)                      │
│  6. Apply U = I + H + T  (multiverse update)                        │
│  7. Check FTUM convergence  ‖A_i/4G − S_i‖ < ε   (defect norm)     │
└──────────────────────────────────────────────────────────────────────┘
```

Recommended numerical settings:
- `dt ≤ 0.01 * dx²` for the bulk fields (CFL-like condition)
- Staggered grids for $B_\mu$ (gauge field)
- Semi-implicit schemes for both $g_{\mu\nu}$ and $\phi$ (already built-in)
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

## 7 · Semantic Bridge: Theory ↔ Implementation

The file [`.github/CONTEXT_SSCE.md`](.github/CONTEXT_SSCE.md) serves as the **Global Context
Manifest** for AI-assisted development.  It maps every abstract claim in the monograph to a
concrete engineering requirement so that GitHub Copilot and other LLM agents remain
*physics-aware* during code generation.

For the full function-level predicate map (IMPLEMENTATION / IMPLICATION / LOGIC annotations
that sit *alongside* the source without modifying it), see
[`docs/semantic-bridge.md`](docs/semantic-bridge.md).

### Functional Logic Map

| Monograph Claim (Abstract)  | Implementation (Concrete)          | AI/Copilot Instruction                              |
|-----------------------------|------------------------------------|-----------------------------------------------------|
| **Energy Conservation**     | Unitary Logic Gates                | Ensure all matrix ops are Unitary/Orthogonal.       |
| **Frequency-Mass Coupling** | High-THz Clocking                  | Optimize signal paths for phase-coherence.          |
| **Topological Invariance**  | HDI Differential Routing           | Maintain 50-ohm impedance with zero stubs.          |
| **Walker–Pearson equations**| `src/core/evolution.py`            | Field updates must conserve `‖∇·J_inf‖ ≈ 0`.       |
| **KK Metric Ansatz**        | `src/core/metric.py`               | 5D metric assembly; preserve block structure G_AB.  |
| **FTUM Fixed Point**        | `src/multiverse/fixed_point.py`    | Operator U = I + H + T must converge: `U Ψ* = Ψ*`. |
| **Holographic Boundary**    | `src/holography/boundary.py`       | Entropy-area law `S = A/4G`; no boundary leakage.   |

### Isolation Policy

| Path                  | Edit Policy   | Rationale                                      |
|-----------------------|---------------|------------------------------------------------|
| `THEBOOKV9a*.pdf`     | **READ-ONLY** | Canonical theoretical reference                |
| `manuscript/`         | **READ-ONLY** | Monograph source chapters                      |
| `src/`                | Editable      | Numerical implementation of field equations    |
| `.github/CONTEXT_SSCE.md` | Maintain  | AI context manifest                            |

---

## 8 · License — Dual-Layer Protection

This repository uses two complementary licenses to protect the work for the
global public in perpetuity.

| Layer | Scope | License |
|-------|-------|---------|
| **Theory & content** | Manuscripts, equations, datasets, PDF monograph | [Defensive Public Commons License v1.0 (2026)](LICENSE) |
| **Software** | `src/` · `scripts/` · `tests/` · `submission/` | [GNU AGPL-3.0-or-later](LICENSE-AGPL) |

**DPC v1.0** — Irrevocable public domain dedication.  No patents, no exclusive
IP claims, no paywalls, no proprietary relicensing of the core equations or theory.

**AGPL-3.0** — Strong copyleft for the software implementation.  Any company or
individual who distributes or deploys a modified version — including as a network
service or SaaS product — **must** release their modified source code under the
same open terms.  This closes the "SaaS loophole" and makes commercial lock-in
on the implementation legally impossible.

Attribution is requested but not legally required.  See [NOTICE](NOTICE) for the
full dual-license explanation.

---

## 9 · Credits

| Role | Name / System |
|------|--------------|
| Principal Architect | ThomasCory Walker-Pearson |
| Site Architect / Code Master | GitHub Copilot |
| Synthesis & Verification | Gemini · ChatGPT · Microsoft Copilot |
| Version | 9.0 — Academic Edition |

For technical inquiries or peer-review submissions, use the LaTeX source files
and BibLaTeX citations provided in the accompanying documentation.
