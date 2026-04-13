# Python API — Unitary Manifold

The repository contains a Python implementation of the full theory. The
test suite has 1153 passing tests and 0 failures (1165 total: 1153 fast passed · 1 skipped (guard) · 11 slow-deselected).

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
python -m pytest tests/ -v
# Expected: 1153 passed, 0 failed
```

Individual test modules:

```bash
python -m pytest tests/test_metric.py -v
python -m pytest tests/test_evolution.py -v
python -m pytest tests/test_boundary.py -v
python -m pytest tests/test_fixed_point.py -v
python -m pytest tests/test_quantum_unification.py -v
python -m pytest tests/test_fiber_bundle.py -v
python -m pytest tests/test_uniqueness.py -v
python -m pytest tests/test_boltzmann.py -v
python -m pytest tests/test_cosmological_predictions.py -v
```
