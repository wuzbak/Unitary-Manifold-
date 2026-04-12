# Simulation Runs — Unitary Manifold

This document records the reproducible simulation scripts in `scripts/`, the
parameter regimes used, and the expected outputs with numerical tolerances.
All scripts use fixed random seeds and produce structured JSON output.

---

## How to run

```bash
pip install -r requirements.txt
python scripts/run_metric.py
python scripts/run_evolution.py
python scripts/run_boundary.py
python scripts/run_fixed_point.py
```

Each script prints human-readable progress, then a JSON block with all
parameter values, measured metrics, tolerances, and a `"status": "PASS"` or
exception on failure.

---

## 1. `scripts/run_metric.py` — KK metric and curvature

### What is being tested

- The 5-D Kaluza–Klein metric `G_AB` is assembled from a near-flat 4-D metric,
  a small gauge field `B_μ`, and a scalar `φ ≈ 1`.
- The field-strength tensor `H_μν = ∂_μ B_ν − ∂_ν B_μ` is computed.
- The full curvature hierarchy `(Γ, Riemann, Ricci, R)` is computed.
- A second run on the *exact* Minkowski background verifies that `Ricci = 0`
  and `R = 0` analytically.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Grid points `N` | 64 |
| Spacing `dx` | 0.1 |
| KK coupling `λ` | 1.0 |
| Perturbation amplitude `ε` | 1e-3 |
| Random seed | 0 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| `max |G_AB − G_BA|` (symmetry) | < 1e-14 |
| `max |H_μν + H_νμ|` (antisymmetry) | < 1e-10 |
| Ricci Frobenius norm mean (near-flat) | < 1.0 |
| Scalar curvature `R_max` (near-flat) | < 5.0 |
| Ricci (exact flat), `R` (exact flat) | = 0.0 (machine precision) |

### Reproducibility

Re-running with `SEED=0` always produces the same JSON output.

---

## 2. `scripts/run_evolution.py` — Walker–Pearson field evolution

### What is being tested

- `FieldState.flat` initialises a reproducible near-flat background.
- `run_evolution` advances the metric `g_μν`, gauge field `B_μ`, and scalar
  `φ` for `STEPS=50` steps using the semi-implicit Walker–Pearson integrator.
- The constraint monitor is evaluated every 10 steps:
  - `R_max`, `phi_max`, `B_norm_mean`, `ricci_frob_mean`
  - `T_div_max` (new stress-energy divergence diagnostic)
- Determinism is verified: two runs from the same seed produce identical output.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Grid points `N` | 64 |
| Spacing `dx` | 0.1 |
| Timestep `dt` | 1e-3 |
| Steps | 50 |
| KK coupling `λ` | 1.0 |
| Nonminimal coupling `α` | 0.1 |
| Random seed | 42 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| `phi_max` at `t=0.05` | < 100 |
| `R_max` at `t=0.05` | < 10 |
| `T_div_max` | finite |
| Determinism residual | = 0.0 (exact) |

### Known limitations

Beyond approximately `t=0.05` (50 steps at `dt=1e-3`) the explicit `α R φ`
reaction term can drive instability when `R` grows large.  The semi-implicit
Laplacian treatment (introduced in the bug fix) stabilises the diffusion
component but not the reaction component.  Longer stable runs require either
a smaller `dt`, a smaller `α`, or a fully implicit treatment of the reaction
term.

---

## 3. `scripts/run_boundary.py` — Holographic boundary dynamics

### What is being tested

- `BoundaryState.from_bulk` projects bulk fields onto the holographic screen.
- `entropy_area` computes the Bekenstein–Hawking entropy `S = A / 4G`.
- `evolve_boundary` co-evolves the boundary metric alongside the bulk for
  `STEPS=50` steps.
- `information_conservation_check` computes the Gauss-law residual at each step.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Grid points `N` | 64 |
| Spacing `dx` | 0.1 |
| Timestep `dt` | 1e-3 |
| Co-evolution steps | 50 |
| Newton's constant `G4` | 1.0 |
| Random seed | 0 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| Initial entropy `S0` | > 0 |
| Boundary metric `h_ab` | finite throughout |
| Information flux `J_bdry` | finite throughout |
| Information conservation residual | finite throughout |

### Observation

The boundary entropy grows rapidly (exponentially) because the evolve_boundary
equation contains a `θ_ab[J_inf]` deformation sourced by the information flux,
which itself grows as the bulk evolves.  This is a known consequence of the
explicit coupling; it does not indicate a code error.  A well-posed boundary
theory should include a damping or renormalisation prescription.

---

## 4. `scripts/run_fixed_point.py` — FTUM multiverse fixed-point

### What is being tested

- `fixed_point_iteration` applies the combined operator `U = I + H + T` to a
  multiverse network and iterates until convergence.
- Two network topologies are tested: chain (`n=5`) and fully-connected (`n=4`).
- After convergence, every node is verified to satisfy `S ≤ A / 4G`
  (holographic entropy bound).
- UEUM geodesic acceleration is verified finite for all nodes.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Chain network | `n=5`, `coupling=0.05` |
| Fully-connected | `n=4`, `coupling=0.05` |
| Pseudo-timestep `dt` | 1e-3 |
| Convergence tolerance `tol` | 1e-2 |
| Max iterations | 500 (chain), 1000 (fully-connected) |
| Random seed | 42 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| `converged` flag | `True` |
| Final residual | < 1e-2 |
| All node entropies `S ≤ A/4G` | exact (up to 1e-10) |
| UEUM acceleration | finite |

### Note on convergence tolerance

The natural residual floor is `O(dt) ≈ 1e-3` because the Irreversibility
operator increases entropy by `κ A dt` per step and the Holography operator
clamps it back, creating a cyclic perturbation.  A tolerance of `1e-2` (ten
times this floor) confirms that the system has reached its steady regime.
Reducing `dt` reduces the floor proportionally.

---

## Test suite

The full automated test suite is in `tests/` and can be run with:

```bash
pip install pytest
python -m pytest tests/ -v
```

689 tests (679 fast-selected + 11 slow-deselected): 678 passed · 1 skipped (guard) · 0 failed.

> **Skip:** `test_arrow_of_time.py::TestEntropyProductionRate::test_defect_history_mostly_decreasing` uses a `pytest.skip()` guard that fires on immediate convergence — correct behaviour, not a failure.
> **Slow:** 11 tests in `test_richardson_multitime.py` marked `@pytest.mark.slow`; run with `pytest tests/ -m slow`.

| File | Tests | Topics |
|------|-------|--------|
| `test_metric.py` | 30 | flat Ricci, antisymmetry, 5D symmetry, gauge invariance, KK reduction |
| `test_evolution.py` | 49 | determinism, flat-space stability, φ boundedness, ∇T diagnostic |
| `test_boundary.py` | 21 | entropy bound, info conservation, evolve_boundary |
| `test_fixed_point.py` | 35 | IHT operators, UEUM, convergence |
| `test_convergence.py` | 10 | O(dx²) gradient, Laplacian, Christoffel convergence |
| `test_inflation.py` | 271 | CMB power spectrum, ns/r, birefringence, triple constraint, EE/TE source functions, TB/EB spectra |
| `test_parallel_validation.py` | 38 | dual-branch independence, observable decoupling, amplitude closure, transfer physics |
| `test_arrow_of_time.py` | 23 | entropy growth, backward deficit, path independence, production rates |
| `test_cmb_landscape.py` | 17 | χ² landscape, TB/EB cross-checks, amplitude analysis |
| `test_e2e_pipeline.py` | 26 | end-to-end chain closure, CS level uniqueness, α consistency loop |
| `test_observational_resolution.py` | 30 | nₛ/β/χ² tolerances, angular resolution, LiteBIRD pol-ratio bounds |
