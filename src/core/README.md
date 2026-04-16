# src/core — Physics Core (TIER 1)

**Epistemic status: Verified mathematical physics with testable predictions**

This package contains the actual scientific claim of the Unitary Manifold:
a 5D Kaluza–Klein geometry where the irreversibility field Bμ is encoded in
the off-diagonal block of the parent metric, and whose 4D projection produces
the Walker–Pearson field equations.

## What is derived here, not assumed

- **α = φ₀⁻²** — extracted from the 5D cross-block Riemann tensor R^μ_{5ν5};
  not a free parameter
- **nₛ ≈ 0.9635** — CMB spectral index within Planck 2018 1σ window
- **β ≈ 0.331°** — CMB birefringence angle from the Chern-Simons term with
  k_cs = 74 = 5² + 7²

## Known open tension

The canonical n_w = 5 mode gives r > 0.036 (BICEP/Keck bound).  The braided
(5,7) resolution in `braided_winding.py` addresses this but is not yet
independently confirmed.  See `HOW_TO_BREAK_THIS.md` §3.

## Key modules

| Module | Contents |
|--------|----------|
| `metric.py` | KK ansatz, 4D→5D→4D curvature pipeline |
| `evolution.py` | RK4 Walker–Pearson field integrator |
| `inflation.py` | Slow-roll inflation, KK Jacobian, CMB predictions |
| `braided_winding.py` | Braided winding states, birefringence, adversarial attacks |
| `boltzmann.py` | Boltzmann entropy, H-theorem |
| `fiber_bundle.py` | Bundle topology, connection, curvature forms |
| `uniqueness.py` | Uniqueness theorems for Walker–Pearson equations |
| `particle_geometry.py` | [TIER 2] Particles as winding modes |
| `black_hole_transceiver.py` | [TIER 2] BH information via 5D topology |
| `dark_matter_geometry.py` | [TIER 2] Dark matter as Bμ geometric pressure |

## Tests

```bash
python -m pytest tests/test_metric.py tests/test_evolution.py \
    tests/test_inflation.py tests/test_braided_winding.py \
    tests/test_boundary.py tests/test_fixed_point.py -v
```
