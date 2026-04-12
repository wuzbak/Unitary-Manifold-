# Claim: 5D bulk Chern–Simons term generates the axion-photon coupling via anomaly inflow

## What is claimed

When the 5D bulk Chern–Simons term κ₅ A∧F∧F is Kaluza–Klein-reduced on the
flat S¹/Z₂ orbifold, the A₅ zero-mode plays the rôle of a 4D pseudo-scalar
(axion φ).  Its 4D photon coupling is:

```
g_aγγ = k_CS · α_EM / (2π² r_c)
```

where **k_CS = 74** is the integer topological charge (Chern–Simons level)
counting the total 5D bulk anomaly.  This is the **anomaly inflow** mechanism:
the 5D bulk anomaly flows to the 4D boundary and manifests as the axion-photon
coupling that rotates CMB polarisation.

The chain from k_CS → g_aγγ → β is:

```
k_CS = 74
 ↓
g_aγγ = 74 · (1/137.036) / (2π² · 12) ≈ 2.280 × 10⁻³  [M_Pl⁻¹]
 ↓
β = (g_aγγ / 2) · |Δφ| ≈ (2.280e-3 / 2) · 5.38 ≈ 0.00613 rad ≈ 0.351°
```

## Why this claim matters

The coupling g_aγγ is **not a free parameter**.  It is fixed by:
1. The integer k_CS (derived from β, see `claims/integer_derivation/`)
2. The fine-structure constant α_EM (known to 12 significant figures)
3. The compactification radius r_c (geometric parameter, fixed by the hierarchy problem)

There is no remaining freedom to adjust β without changing k_CS or r_c.

## What would falsify this claim

1. **Birefringence null result**: β = 0 measured at 3σ removes the
   observational motivation for k_CS = 74 and eliminates the coupling.

2. **Non-integer k_CS required**: If the physical birefringence angle demands
   k_CS = 73.7 (not an integer), the topological quantisation of the CS level
   is violated — a fundamental break of the mechanism.

3. **Wrong formula for g_aγγ**: If the KK reduction of the 5D CS term yields
   a different coupling formula (e.g., with a different volume factor), the
   entire chain is invalidated.

## Minimal code path

```python
from src.core.inflation import cs_axion_photon_coupling, birefringence_angle
import math

g_agg    = cs_axion_photon_coupling(k_cs=74, alpha_em=1/137.036, r_c=12.0)
beta_deg = math.degrees(birefringence_angle(g_agg, delta_phi=5.38))
print(f"g_aγγ = {g_agg:.4e}")  # ≈ 2.280e-3
print(f"β     = {beta_deg:.4f}°")  # ≈ 0.351°
```

## Delete-power test

Set `k_cs = 1` (no anomaly inflow) and observe that g_aγγ drops by ×74 and β
no longer matches the target.  Run `python test_claim.py` — the test
`test_zero_anomaly_gives_wrong_beta` will confirm this explicitly.

## Source

- `src/core/inflation.py`: `cs_axion_photon_coupling()`, `birefringence_angle()`
- `claims/integer_derivation/` — k_CS=74 derivation
- Kaplan & Nelson (1986) / Choi & Kim (1985) — original CS reduction mechanism
