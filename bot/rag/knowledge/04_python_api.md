# Python API — Unitary Manifold

The repository contains a Python implementation of the full theory. The
test suite has 9933 passing tests and 0 failures (9946 total: 9933 fast passed · 2 skipped · 11 slow-deselected) in `tests/`; plus 316 in `recycling/` and 1234 in `Unitary Pentad/` — **11483 total passing, 0 failures**.

## Installation

```bash
pip install -r requirements.txt   # numpy>=1.24, scipy>=1.11
```

## Module Overview

| Module | Key functions / classes |
|--------|------------------------|
| `src/core/metric.py` | `compute_curvature()`, `field_strength()`, `extract_alpha_from_curvature()` |
| `src/core/evolution.py` | `FieldState`, `step()`, `run_evolution()`, `Z_kinetic()`, `epsilon_eff()`, `renormalize_slow_roll()` |
| `src/holography/boundary.py` | `entropy_area()`, `fefferman_graham_expansion()`, `boundary_counterterms()`, `holographic_renormalized_action()`, `derive_kcs_anomaly_inflow()` |
| `src/multiverse/fixed_point.py` | `fixed_point_iteration()`, `prove_banach_contraction()`, FTUM convergence |
| `src/core/boltzmann.py` | `baryon_loading_factor()`, `baryon_corrected_rs()`, `baryon_loaded_spectrum()`, `dl_baryon()`, `accuracy_vs_tight_coupling()` |
| `src/core/derivation.py` | `derive_winding_number()`, `derive_cs_level()`, `derive_integers()`, `check_round_trip_closure()`, `check_anomaly_cancellation()` |
| `src/core/fiber_bundle.py` | `build_bundle_catalog()`, `compute_characteristic_classes()`, `classify_bundle()`, `check_global_anomaly_cancellation()`, `bundle_topology_scan()` |
| `src/core/uniqueness.py` | `uniqueness_scan()`, `lcdm_nogo_comparison()`, `joint_prediction_overlap()`, `integer_quantization_discriminant()`, `full_uniqueness_report()` |

---

## `src/core/evolution.py` — Field Evolution

### `FieldState`

Represents the state of the Walker-Pearson field at a given time step.

```python
from src.core.evolution import FieldState, step, run_evolution

# Create a default initial state
state = FieldState.default()
print(state.metric)      # 4D metric tensor (4×4 numpy array)
print(state.dilaton)     # scalar φ field value
print(state.entropy)     # current entropy value
```

### `step(state, dt)`

Advance the field state by one time step.

```python
new_state = step(state, dt=0.01)
```

### `run_evolution(state, steps, dt)`

Run a full evolution from an initial state.

```python
result = run_evolution(state, steps=1000, dt=0.01)
print(result.entropy)          # final entropy
print(result.entropy_history)  # list of entropy values at each step
```

Entropy should be monotonically non-decreasing (the geometric Second Law).

---

## `src/core/metric.py` — Metric and Curvature

### `compute_curvature(metric)`

Compute the Riemann curvature tensor, Ricci tensor, and Ricci scalar from
a given metric.

```python
from src.core.metric import compute_curvature
import numpy as np

# Flat Minkowski metric
g = np.diag([-1, 1, 1, 1])
curvature = compute_curvature(g)
print(curvature.ricci_scalar)     # should be 0 for flat space
print(curvature.einstein_tensor)  # 4×4 array
```

### `field_strength(B)`

Compute the irreversibility field strength tensor H_μν from the vector
field B_μ.

```python
from src.core.metric import field_strength
import numpy as np

B = np.zeros(4)  # vacuum — no irreversibility field
H = field_strength(B)
print(H)  # 4×4 antisymmetric tensor
```

### `extract_alpha_from_curvature(state)`

Extract the effective coupling α = φ₀⁻² from the current field state.

```python
from src.core.metric import extract_alpha_from_curvature

alpha = extract_alpha_from_curvature(state)
print(f"α = {alpha:.6f}")  # should be near φ₀⁻²
```

---

## `src/holography/boundary.py` — Holographic Boundary

### `entropy_area(surface)`

Compute the Bekenstein-Hawking entropy of a boundary surface:
S = A / 4G (in Planck units).

```python
from src.holography.boundary import entropy_area

area = 100.0  # Planck units²
entropy = entropy_area(area)
print(f"S = {entropy:.4f}")
```

The holographic boundary module implements the geometric version of the
holographic principle: bulk entropy is encoded on the boundary, consistent
with Theorem XII (black hole information preservation).

---

## `src/multiverse/fixed_point.py` — FTUM Fixed Point

### `fixed_point_iteration(psi_0, max_iter, tol)`

Iterate the FTUM operator U = I + H + T until convergence to the fixed
point Ψ*.

```python
from src.multiverse.fixed_point import fixed_point_iteration
import numpy as np

psi_0 = np.random.randn(10)   # initial state vector
psi_star, converged, n_iter = fixed_point_iteration(
    psi_0, max_iter=1000, tol=1e-8
)
print(f"Converged: {converged} after {n_iter} iterations")
print(f"|Ψ*| = {np.linalg.norm(psi_star):.6f}")
```

The iteration converges for initial states near the physical vacuum. For
random initial states far from the vacuum, convergence is not guaranteed.

---

## Running the test suite

```bash
# Core physics (all 66 pillars):
python -m pytest tests/ -q
# Expected: 9933 passed, 2 skipped, 11 deselected, 0 failed

# Recycling / Pillar 16:
python -m pytest recycling/ -q
# Expected: 316 passed, 0 failed

# Unitary Pentad (HILS framework):
python -m pytest "Unitary Pentad/" -q
# Expected: 1234 passed, 0 failed

# All suites together:
python -m pytest tests/ recycling/ "Unitary Pentad/" -q
# Expected: 11483 passed, 2 skipped, 0 failed
```

Key individual test modules:

```bash
python -m pytest tests/test_metric.py -v
python -m pytest tests/test_evolution.py -v
python -m pytest tests/test_boundary.py -v
python -m pytest tests/test_fixed_point.py -v
python -m pytest tests/test_quantum_unification.py -v
python -m pytest tests/test_fiber_bundle.py -v
python -m pytest tests/test_uniqueness.py -v
python -m pytest tests/test_braided_winding.py -v       # adversarial attacks
python -m pytest tests/test_kk_geodesic_reduction.py -v # geodesic gap closure
python -m pytest tests/test_kk_gauge_spectrum.py -v     # KK tower spectrum
python -m pytest tests/test_im_action.py -v             # imaginary action
```

---

## New Core Modules (v9.11+)

### `src/core/braided_winding.py` — Braided (5,7) Winding & Adversarial Attacks

```python
from src.core.braided_winding import (
    braided_birefringence,
    projection_degeneracy_fraction,   # Attack 1
    birefringence_scenario_scan,      # Attack 2
    kk_tower_cs_floor,                # Attack 3
)

# Predict β for a braided (n_w=5, n_w2=7) state
beta = braided_birefringence(n_w=5, n_w2=7, k_cs=74, r_c=12)
print(f"β ≈ {beta:.3f}°")  # ≈ 0.331°

# Three adversarial attacks — all must pass
frac = projection_degeneracy_fraction(n_w=5, n_w2=7, k_cs=74)  # Attack 1: projection degeneracy
scan = birefringence_scenario_scan()                              # Attack 2: data drift
floor = kk_tower_cs_floor(k_cs=74)                               # Attack 3: KK tower consistency
```

**Attack results:**
- Attack 1 (Projection Degeneracy): A 4D EFT needs 1-in-2400 fine-tuning to fake the 5D integer lock
- Attack 2 (Birefringence Scan): Only two discrete SOS states survive the triple constraint — β ∈ {≈0.273°, ≈0.331°}
- Attack 3 (KK Tower Floor): c_s floor is invariant under KK rescaling and kinematically decoupled from higher modes

### `src/core/kk_geodesic_reduction.py` — Exact 5D→4D Geodesic Reduction

Proves that A_μ = λB_μ is a **theorem** (not an assumption), and that the 5D geodesic equation decomposes exactly:

```
acc_5D = acc_4D_from_G5 + acc_Lorentz + acc_radion
```

at machine precision.

```python
from src.core.kk_geodesic_reduction import (
    kk_geodesic_reduction,
    lorentz_acceleration,
    verify_geodesic_closure
)

result = kk_geodesic_reduction(state)
print(result.closure_error)   # machine precision (~1e-14)
print(result.a_mu_is_theorem) # True — A_μ = λB_μ derived, not assumed
```

### `src/core/kk_gauge_spectrum.py` — Kaluza-Klein Tower Spectrum

```python
from src.core.kk_gauge_spectrum import (
    kk_mass_spectrum,
    kk_tower_cs_floor,
    spectral_gap
)

masses = kk_mass_spectrum(n_max=10, phi_0=1.0)  # KK tower mass eigenvalues
gap = spectral_gap(phi_0=1.0)                    # lowest KK mass
print(f"m_KK = {gap:.4f} (Planck units)")
```

### `src/core/im_action.py` — Imaginary Part of the Effective Action

```python
from src.core.im_action import (
    im_action,
    entropy_identity_check,
    boltzmann_weight
)

# Im(S_eff) = ∫B_μ J^μ_inf d⁴x — the path-integral entropy identity
im_s = im_action(state)
print(f"Im(S_eff) = {im_s:.6f}")

# Verify: Im(S_eff) ↔ thermodynamic entropy change
ok = entropy_identity_check(state)  # True if geometric = thermodynamic
```
