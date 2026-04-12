# Claim: COBE normalisation uniquely fixes λ — amplitude is a constraint, not a prediction

## What is claimed

The Goldberger–Wise potential V(φ) = λ(φ² − φ₀²)² has one free dimensionful
parameter: the self-coupling **λ**.  All dimensionless CMB observables
(nₛ, r, αₛ, β) are **independent of λ** because they are ratios of V and its
derivatives evaluated at the same field value, and λ cancels exactly.

The single Planck 2018 scalar amplitude measurement:

```
Aₛ = 2.101 × 10⁻⁹   (Planck 2018 TT,TE,EE+lowE+lensing, Table 2)
```

uniquely determines:

```
λ_COBE = 6.988 × 10⁻¹⁵
```

after which the inflationary sector has **no remaining free parameters**.

The energy scale of inflation is a consequence:

```
E_inf = V^{1/4}(φ*) = 1.806 × 10¹⁶ GeV  ≈ 0.15 M_GUT
```

## Why λ-independence matters

If nₛ or r changed when λ changed, the theory would have a hidden tuning
freedom.  The tests below verify that nₛ and r are identical (to floating-point
precision) at λ = 1 and λ = λ_COBE.

## What would falsify this claim

1. **Improved Aₛ measurement rules out the COBE value**: If future CMB
   experiments shift Aₛ significantly, λ_COBE shifts proportionally.  The
   theory accommodates any Aₛ by rescaling λ — so Aₛ itself does not falsify
   the theory.  What falsifies it is if the resulting energy scale E_inf is
   inconsistent with independent measurements (e.g., gravitational-wave
   background from inflation).

2. **λ-dependence found in observables**: If a higher-order correction makes nₛ
   or r depend on λ, the factorisation breaks and a new free parameter appears.

## Minimal code path

```python
from src.core.inflation import cobe_normalization

result = cobe_normalization(phi0_bare=1.0, n_winding=5)
print(result["lam_cobe"])     # ≈ 6.988e-15
print(result["ns"])           # ≈ 0.9635  (same regardless of λ)
print(result["r"])            # ≈ 0.0973  (same regardless of λ)
```

## Delete-power test

Set `lam = 1.0` instead of `lam_cobe` in `slow_roll_amplitude()` and observe
that Aₛ shifts by 14 orders of magnitude while nₛ and r are unchanged.
Run `python test_claim.py` — `test_as_proportional_to_lambda` will fail if the
linear λ-scaling is broken, and `test_ns_r_lambda_independent` will fail if nₛ
or r drift with λ.

## Source

- `src/core/inflation.py`: `cobe_normalization()`, `slow_roll_amplitude()`
- `BIG_QUESTIONS.md`: Q15 (amplitude gap), Q16 (COBE normalization)
- Planck 2018: arXiv:1807.06211 Table 2
