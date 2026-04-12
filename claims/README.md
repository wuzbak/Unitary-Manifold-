# Claims

Each subdirectory isolates one big claim of the Unitary Manifold theory.

| Claim | What it asserts | Key number | Falsifier |
|-------|-----------------|------------|-----------|
| [`integer_derivation/`](integer_derivation/) | k_CS = 74 is derived, not fit | k_CS = 74 | β null result at 3σ |
| [`tensor_ratio_fix/`](tensor_ratio_fix/) | r = 0.097 is real (active tension with r < 0.036) | r = 0.097 | CMB-S4 confirms r < 0.036 |
| [`amplitude_normalization/`](amplitude_normalization/) | λ_COBE uniquely fixes amplitude; nₛ, r are λ-free | λ = 6.99×10⁻¹⁵ | λ-dependence found in nₛ/r |
| [`anomaly_inflow/`](anomaly_inflow/) | 5D CS inflow generates g_aγγ → β ≈ 0.35° | g_aγγ ≈ 2.28×10⁻³ | β null result; wrong g formula |

## Structure of each claim

```
<claim>/
  README.md        — what is claimed and what would falsify it
  verify.py        — runnable minimal code demonstrating the claim
  test_claim.py    — pytest tests that FAIL if the claim is removed
```

## Running all claim tests

```bash
# From the repository root
python -m pytest claims/ -v
```

## Running a single claim

```bash
python claims/integer_derivation/verify.py
python -m pytest claims/integer_derivation/test_claim.py -v
```

## Delete-power convention

Each `test_claim.py` contains at least one test labelled **DELETE-POWER TEST**
in its docstring.  To check that the claim is load-bearing:

1. Comment out or alter the constant / formula named in the docstring.
2. Run `python -m pytest claims/<name>/test_claim.py -v`.
3. The DELETE-POWER TEST must fail (red).

If it does not fail, the claim is not mechanically enforced and should be
strengthened.
