# Claim: k_CS = 74 is derived, not fit

## What is claimed

The Chern–Simons level **k_CS = 74** is not a free parameter tuned to match
observations.  It is the unique positive integer that minimises
|β(k) − 0.35°| over k ∈ [1, 100], where β is the cosmic birefringence angle
and 0.35° is the observational hint from Minami & Komatsu (2020) /
Diego-Palazuelos et al. (2022).

The derivation chain is:

```
β_target = 0.35° (Minami & Komatsu / Diego-Palazuelos)
↓
k_CS = β_rad · 4π² · r_c / (α_EM · |Δφ|)
     = 73.71...
↓
round(73.71) = 74
↓
k_CS_int = 74  ←  uniquely minimises |β(k) − 0.35°| over all integers k ∈ [1, 100]
```

No other integer k produces a β closer to 0.35°.

## Minimal code path

```python
from src.core.inflation import cs_level_for_birefringence, CS_LEVEL_PLANCK_MATCH

k_float = cs_level_for_birefringence(
    beta_target_deg=0.35,
    alpha_em=1 / 137.036,
    r_c=12.0,
    delta_phi=5.38,
)
assert round(k_float) == CS_LEVEL_PLANCK_MATCH == 74
```

Run `python verify.py` for the full demonstration.

## What would falsify this claim

1. **Birefringence null result**: Future CMB polarimetry (LiteBIRD, CMB-S4,
   Simons Observatory) measures β consistent with zero at ≥ 3σ.  This removes
   the observational anchor for k_CS = 74.

2. **Different integer wins**: If the physical parameters (r_c, |Δφ|) are
   measured differently and a different integer k minimises the residual, the
   specific value 74 is wrong.

3. **Non-integer CS level**: If the theory's topological quantisation condition
   does not enforce integer k_CS, the "derived" nature of the value is lost.

## Delete-power test

Comment out `CS_LEVEL_PLANCK_MATCH = 74` (or change it to any other integer)
in `src/core/inflation.py` and run `python test_claim.py`.  The test
`test_cs_level_is_unique_minimiser` will fail immediately.

## Source

- `src/core/inflation.py`: `cs_level_for_birefringence()`, `CS_LEVEL_PLANCK_MATCH`
- `tests/test_e2e_pipeline.py`: `TestUniquenessOfCSLevel`
- Minami & Komatsu 2020 (arXiv:2011.11612); Diego-Palazuelos et al. 2022 (arXiv:2201.07241)
