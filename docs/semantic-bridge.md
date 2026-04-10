# Semantic Bridge: Theory ↔ Implementation

> This document sits **alongside** the source code without modifying it.
> It maps every abstract claim in the Unitary-Manifold monograph to a
> concrete function or module, and records the physics contract each
> implementation must honour.  See also `.github/CONTEXT_SSCE.md` for
> the AI/Copilot-optimised version of these constraints.

---

## 1. Function-Level Predicate Map

Each entry below corresponds to an **unmodified** function in `/src`.
The three predicates describe the theoretical anchor, physical consequence,
and invariant that must be preserved.

---

### `src/core/metric.py` — `field_strength(B, dx)`

```
IMPLEMENTATION : Monograph Section 3 (Irreversibility Gauge Field)
IMPLICATION    : Antisymmetry H_μν = −H_νμ encodes the arrow-of-time
                 gauge structure; any symmetric contribution breaks this
                 and introduces spurious entropy production.
LOGIC          : Computes the exterior derivative of B_μ; result must
                 remain antisymmetric to within floating-point tolerance.
```

---

### `src/core/metric.py` — `assemble_5d_metric(g, B, phi, lam)`

```
IMPLEMENTATION : Monograph Sections 3–4 (5D Metric Ansatz / KK Reduction)
IMPLICATION    : The block structure of G_AB encodes the full
                 Unitary-Manifold geometry; altering the off-diagonal
                 G_μ5 entries changes the coupling between B_μ and 4D
                 spacetime.
LOGIC          : Builds G from (g, B, φ) according to the KK ansatz;
                 the 5D metric must remain non-degenerate (det G ≠ 0)
                 to preserve invertibility.
```

---

### `src/core/metric.py` — `compute_curvature(g, B, phi, dx, lam)`

```
IMPLEMENTATION : Monograph Sections 7–9 (Walker–Pearson Field Equations)
IMPLICATION    : The Ricci tensor and scalar curvature R drive the metric
                 evolution; incorrect finite-difference stencils here
                 cascade into constraint violations in the evolution step.
LOGIC          : Returns (Γ, Riemann, Ricci, R); curvature hierarchy must
                 satisfy Bianchi identity ∇_μ G^μν = 0 up to grid error.
```

---

### `src/core/evolution.py` — `step(state, dt)`

```
IMPLEMENTATION : Monograph Appendix D (Numerical Evolution Pipeline)
IMPLICATION    : Each field update is derived from the Walker–Pearson
                 equations; the scalar φ is semi-implicitly stabilised
                 to prevent norm blow-up, preserving ‖ψ‖² = 1 in the
                 discrete system.
LOGIC          : Sequentially updates (g_μν, B_μ, φ) using curvature and
                 stress-energy evaluated at the current timestep; call
                 `constraint_monitor` after each step to verify.
```

---

### `src/core/evolution.py` — `information_current(g, phi, dx)`

```
IMPLEMENTATION : Monograph Chapter 47 (Conserved Information Current)
IMPLICATION    : ∇_μ J^μ_inf = 0 is the information-conservation law;
                 a non-zero divergence signals a numerical leak in the
                 entanglement-capacity scalar φ.
LOGIC          : Constructs J^μ = φ² u^μ; divergence norm should remain
                 ≪ 1 throughout a well-resolved simulation.
```

---

### `src/holography/boundary.py` — `entropy_area(h)`

```
IMPLEMENTATION : Monograph Pillar 4 (Holographic Boundary / Entropy-Area)
IMPLICATION    : S = A / 4G is the Bekenstein–Hawking bound; any boundary
                 evolution that reduces S without physical justification
                 violates the holographic principle.
LOGIC          : Computes entropy from the induced boundary metric h;
                 result must be non-negative and monotone under forward
                 time evolution.
```

---

### `src/multiverse/fixed_point.py` — `fixed_point_iteration(network, ...)`

```
IMPLEMENTATION : Monograph Pillar 5 / Final Theorem (FTUM)
IMPLICATION    : Convergence to Ψ* with U Ψ* = Ψ* validates the Final
                 Theorem of the Unitary Manifold; non-convergence implies
                 the coupling constants or topology need revision.
LOGIC          : Applies the operator U = I + H + T iteratively; residual
                 ‖Ψ^{n+1} − Ψ^n‖ < ε is the acceptance criterion.
```

---

## 2. How to Use This Document

- **Copilot / LLM agents** — read `.github/CONTEXT_SSCE.md` first, then
  consult this file when working on a specific function.
- **Human contributors** — before changing any function listed above,
  confirm that the corresponding `IMPLICATION` and `LOGIC` predicates
  still hold after your change.
- **Reviewers** — use the `LOGIC` field as the acceptance test for any
  PR touching `/src`.
