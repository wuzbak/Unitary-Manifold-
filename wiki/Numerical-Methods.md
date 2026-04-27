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
│     (RK4 integrator — 4th-order Runge–Kutta)        │
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

### RK4 (default)

The default integrator is the classical fourth-order Runge–Kutta (RK4) scheme,
giving O(Δt⁴) local truncation error per step:

$$\Psi^{n+1} = \Psi^n + \frac{\Delta t}{6}(k_1 + 2k_2 + 2k_3 + k_4)$$

where $k_1 = F(\Psi^n)$, $k_2 = F(\Psi^n + \tfrac{\Delta t}{2}k_1)$, etc.

This is implemented in `step(state, dt)` in `src/core/evolution.py`.

**CFL guidance:** Use `cfl_timestep(state)` to estimate the largest stable Δt.
For $\Delta x = 0.1$, the CFL limit is $\Delta t_{\rm max} \approx 0.004$.
Recommended value: $\Delta t = 10^{-3}$.

### Legacy Euler Integrator (benchmarking only)

A first-order explicit Euler integrator is retained for accuracy benchmarking:

$$\Psi^{n+1} = \Psi^n + \Delta t \cdot F(\Psi^n)$$

Available via `step_euler(state, dt)`. For production use, prefer `step` (RK4).

### Richardson Extrapolation (slow tests)

Eleven `@pytest.mark.slow` tests in `tests/test_richardson_multitime.py` verify second-order convergence rate in time step. Run with:

```bash
python -m pytest tests/ -m slow
```

---

## 4. Curvature Computation

Implemented in `src/core/metric.py`. The pipeline is:

1. **Christoffel symbols** $\Gamma^\sigma_{\mu\nu}$: computed from first spatial derivatives of $g_{\mu\nu}$ (x-direction only in the 1D reduction).
2. **Riemann tensor** $R^\rho{}_{\sigma\mu\nu}$: computed from first derivatives of $\Gamma$ plus quadratic terms.
3. **Ricci tensor** $R_{\mu\nu} = R^\rho{}_{\mu\rho\nu}$: contraction over first and third indices.
4. **Ricci scalar** $R = g^{\mu\nu}R_{\mu\nu}$: full contraction with inverse metric.

> **Performance note:** The nested loops over 4D indices scale as $O(N \cdot 4^k)$. For `N = 64`, a single `compute_curvature` call typically takes < 0.5 s. For `N = 256`, expect ~5–10 s per call; use callbacks to monitor progress.

---

## 5. Scalar Stabilisation (Goldberger–Wise)

The scalar field equation includes a **Goldberger–Wise stabilisation** term:

$$\partial_t\phi = \Delta\phi + \alpha R\phi + S[H] - m_\phi^2(\phi - \phi_0)$$

The restoring force $-m_\phi^2(\phi - \phi_0)$ keeps $\phi$ bounded away from zero, ensuring $G_{55} = \phi^2 > 0$ (non-degenerate metric) throughout the evolution. This is the same stabilisation used in the Goldberger–Wise mechanism for moduli stabilisation in extra-dimension models.

The stabilised value $\phi_0$ is determined by `src/core/phi0_closure.py` (Pillar 56):

$$\phi_0^{\rm FTUM} = n_w \cdot 2\pi \cdot \sqrt{1 + c_s^2} \approx 33.03 \quad (n_w=5,\ c_s=12/37)$$

---

## 6. Holographic Boundary Projection (Pillar 4)

Implemented in `src/holography/boundary.py`.

The boundary state `BoundaryState` stores the induced metric $h_{ab}$ on the 2D holographic screen. It is initialised from a bulk `FieldState` via `BoundaryState.from_bulk(...)`.

The boundary entropy is computed as:

$$S = \frac{A}{4G_4}, \qquad A = \int_{\partial\mathcal{M}} \sqrt{h}\, d^2x$$

approximated numerically as `entropy_area(h)`.

Boundary evolution is driven by the bulk via `evolve_boundary(bdry, bulk, dt)`, which propagates metric perturbations from the bulk to the boundary screen.

---

## 7. Multiverse Fixed-Point Iteration (Pillar 5)

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

A formal Banach fixed-point proof is available via `fixed_point.analytic_banach_proof()`.

---

## 8. CMB Transfer Function (Pillar 63)

Implemented in `src/core/cmb_transfer.py`. Uses the Eisenstein–Hu (1998) transfer function approximation.

Key functions:

| Function | Description |
|----------|-------------|
| `eh_transfer_no_baryon(k, params)` | Eisenstein–Hu transfer function (no-baryon limit) |
| `baryon_acoustic_source(k, params)` | Baryon loading factor |
| `angular_power_spectrum_eh(ell, params)` | $C_\ell$ from E-H transfer |
| `um_dl_spectrum(ell, params)` | UM-corrected $D_\ell$ spectrum |
| `acoustic_peak_positions(params)` | Predicted peak positions |
| `suppression_gap_audit(params)` | Documents the ×4–7 amplitude suppression |

> **Known limitation:** The UM $D_\ell$ spectrum is suppressed by ×4–7 at acoustic peaks relative to Planck observations. The spectral shape ($n_s$) matches; the overall amplitude does not yet. This is a real unresolved discrepancy — see `FALLIBILITY.md §IV.9`.

---

## 9. Recommended Settings Summary

| Parameter | Symbol | Recommended | Notes |
|-----------|--------|-------------|-------|
| Grid points | `N` | 64 – 256 | Larger = more resolution, slower |
| Grid spacing | `dx` | 0.05 – 0.1 | |
| Timestep | `dt` | 1e-3 | Obey CFL: `dt < cfl_timestep(state)` |
| KK coupling | `lam` (λ) | 1.0 | |
| Nonminimal coupling | `alpha` (α) | $\phi_0^{-2}$ (derived) | Do not set as a free parameter |
| Winding number | `n_w` | 5 | Selected by Planck $n_s$ data |
| CS level | `k_cs` | 74 | Selected by birefringence; = $5^2 + 7^2$ |
| Braided sound speed | `c_s` | 12/37 | From (5,7) braid resonance |
| Constraint damping | `kappa_damp` | ≥ 0.1 for > 500 steps | |
| Max evolution steps | `steps` | 200 – 1000 | Monitor constraints |
| FTUM tolerance | `tol` | 1e-6 | Tighten if coupling > 0.1 |
| FTUM max iterations | `max_iter` | 300 | Increase for strong coupling |
