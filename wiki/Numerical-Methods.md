# Numerical Methods

This page documents the numerical pipeline used to integrate the Walker–Pearson field equations, along with stability guidelines and diagnostic tools.

---

## 1. Overview of the Pipeline

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

Each stage corresponds to a specific module in the `src/` tree.

---

## 2. Spatial Discretisation

All fields are sampled on a uniform 1D spatial grid of `N` points with spacing `dx`.

| Field | Shape | Discretisation |
|-------|-------|---------------|
| $g_{\mu\nu}$ | `(N, 4, 4)` | Point values at grid nodes |
| $B_\mu$ | `(N, 4)` | Staggered half-grid recommended for long runs |
| $\phi$ | `(N,)` | Point values at grid nodes |

Spatial derivatives use **second-order central finite differences** via `np.gradient(..., edge_order=2)`.

The discrete Laplacian for the scalar equation uses a 3-point stencil:

$$(\Delta\phi)_n = \frac{\phi_{n+1} - 2\phi_n + \phi_{n-1}}{\Delta x^2}$$

implemented with periodic boundary conditions via `np.roll`.

---

## 3. Time Integration

### Explicit Euler (default)

The default integrator is first-order explicit Euler:

$$\Psi^{n+1} = \Psi^n + \Delta t \cdot F(\Psi^n)$$

This is implemented in `step(state, dt)` in `src/core/evolution.py`.

**CFL stability condition:** For the scalar equation, explicit stability requires:

$$\Delta t \lesssim \frac{\Delta x^2}{2}$$

For $\Delta x = 0.1$, this gives $\Delta t \lesssim 5 \times 10^{-3}$. Recommended value: $\Delta t = 10^{-3}$.

### Semi-implicit Scalar Stabilisation

To suppress high-frequency blow-up in the scalar field, a partial implicit treatment is available:

$$\phi^{n+1} = \frac{\phi^n + \Delta t\,(S[H] + \alpha R \phi^n)}{1 - \Delta t \cdot \kappa_{\rm damp}}$$

where $\kappa_{\rm damp}$ is the constraint-damping coefficient (default 0; set ≥ 0.1 for long runs).

---

## 4. Curvature Computation

Implemented in `src/core/metric.py`. The pipeline is:

1. **Christoffel symbols** $\Gamma^\sigma_{\mu\nu}$: computed from first spatial derivatives of $g_{\mu\nu}$ (x-direction only in the 1D reduction).
2. **Riemann tensor** $R^\rho{}_{\sigma\mu\nu}$: computed from first derivatives of $\Gamma$ plus quadratic terms.
3. **Ricci tensor** $R_{\mu\nu} = R^\rho{}_{\mu\rho\nu}$: contraction over first and third indices.
4. **Ricci scalar** $R = g^{\mu\nu}R_{\mu\nu}$: full contraction with inverse metric.

> **Performance note:** The nested loops over 4D indices scale as $O(N \cdot 4^k)$. For `N = 64`, a single `compute_curvature` call typically takes < 0.5 s. For `N = 256`, expect ~5–10 s per call; use callbacks to monitor progress.

---

## 5. Holographic Boundary Projection (Pillar 4)

Implemented in `src/holography/boundary.py`.

The boundary state `BoundaryState` stores the induced metric $h_{ab}$ on the 2D holographic screen. It is initialised from a bulk `FieldState` via `BoundaryState.from_bulk(...)`.

The boundary entropy is computed as:

$$S = \frac{A}{4G_4}, \qquad A = \int_{\partial\mathcal{M}} \sqrt{h}\, d^2x$$

approximated numerically as `entropy_area(h)`.

Boundary evolution is driven by the bulk via `evolve_boundary(bdry, bulk, dt)`, which propagates metric perturbations from the bulk to the boundary screen.

---

## 6. Multiverse Fixed-Point Iteration (Pillar 5)

Implemented in `src/multiverse/fixed_point.py`.

A `MultiverseNetwork` consists of $n$ coupled manifolds. The `chain(n, coupling)` factory creates a linear chain with nearest-neighbour coupling.

The iteration solves for the fixed point $\Psi^*$ of $U = \mathbf{I} + \mathbf{H} + \mathbf{T}$:

```
Ψ⁰  →  Ψ¹ = U(Ψ⁰)  →  Ψ² = U(Ψ¹)  → ...
```

until $\|\Psi^{n+1} - \Psi^n\| < \varepsilon$ or `max_iter` is reached.

**Convergence guidance:**
- Coupling ≤ 0.1: typically converges in < 100 iterations.
- Coupling > 0.2: may require `max_iter ≥ 500` and `tol ≥ 1e-5`.

---

## 7. Recommended Settings Summary

| Parameter | Symbol | Recommended | Notes |
|-----------|--------|-------------|-------|
| Grid points | `N` | 64 – 256 | Larger = more resolution, slower |
| Grid spacing | `dx` | 0.05 – 0.1 | |
| Timestep | `dt` | 1e-3 | Obey CFL: dt < dx²/2 |
| KK coupling | `lam` (λ) | 1.0 | |
| Nonminimal coupling | `alpha` (α) | 0.1 | |
| Constraint damping | `kappa_damp` | ≥ 0.1 for > 500 steps | |
| Max evolution steps | `steps` | 200 – 1000 | Monitor constraints |
| FTUM tolerance | `tol` | 1e-6 | Tighten if coupling > 0.1 |
| FTUM max iterations | `max_iter` | 300 | Increase for strong coupling |
