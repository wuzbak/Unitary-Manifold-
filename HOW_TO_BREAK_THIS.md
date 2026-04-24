# How to Break This

A guide for adversarial reviewers.  Each section describes a specific,
mechanical way to break the theory — and the exact test or code line that
will confirm you have broken it.

If you cannot break it via these handles, that is evidence of robustness.
If you find a new break-point not listed here, open an issue.

---

## 1. Break the birefringence derivation (k_CS = 74)

**Handle:** Change `CS_LEVEL_PLANCK_MATCH` in `src/core/inflation.py` from
74 to any other integer (e.g., 73).

**Expected result:** `claims/integer_derivation/test_claim.py` fails at
`test_cs_level_is_unique_minimiser` — proving that k=74 is not arbitrary.

**What this tests:** The claim that 74 is derived, not chosen.

```bash
# Mutant: set CS_LEVEL_PLANCK_MATCH = 73, then:
python -m pytest claims/integer_derivation/test_claim.py -v
# → FAIL (test_cs_level_is_unique_minimiser)
```

---

## 2. Break the KK Jacobian (nₛ leaves the Planck window)

**Handle:** In `src/core/inflation.py`, change `effective_phi0_kk()` to return
`phi0_bare` instead of `n_winding * 2 * pi * sqrt(phi0_bare)`.

**Expected result:** `ns_from_phi0(phi0_bare=1.0)` gives nₛ ≈ 0.75, far
outside the Planck 1σ window.  `tests/test_inflation.py` fails at dozens of
spectral-index tests.

**What this tests:** The claim that the KK Jacobian is essential for nₛ.

```bash
# Mutant: return phi0_bare in effective_phi0_kk, then:
python -m pytest tests/test_inflation.py -v -k "planck or spectral"
# → FAIL (multiple tests)
```

---

## 3. Break the r-tension documentation (hide the conflict)

**Handle:** In `src/core/inflation.py`, replace the n_w=5 path with n_w=9
(which satisfies r < 0.036 but pushes nₛ to +4σ from Planck).

**Expected result:**
- `claims/tensor_ratio_fix/test_claim.py::test_canonical_r_exceeds_bicep_keck_bound` FAILS
  (r is now < 0.036 — but then nₛ is broken)
- `claims/tensor_ratio_fix/test_claim.py::test_canonical_ns_within_planck_1sigma` FAILS
  (nₛ is now outside 1σ)

Only one of the two constraints can be satisfied at a time.

```bash
# Mutant: use n_winding=9 as canonical, then:
python -m pytest claims/tensor_ratio_fix/test_claim.py -v
# → FAIL (cannot satisfy both constraints simultaneously)
```

---

## 4. Break the amplitude normalisation (make λ affect nₛ)

**Handle:** In `src/core/inflation.py`, add a small λ-dependent correction to
`spectral_index()`:

```python
# mutant:
return 1.0 - 6.0 * epsilon + 2.0 * eta + 1e-4 * lam
```

**Expected result:** `claims/amplitude_normalization/test_claim.py::test_ns_lambda_independent`
FAILS because nₛ(λ=1) ≠ nₛ(λ=λ_COBE).

**What this tests:** The claim that COBE normalisation introduces no tuning
of the spectral observables.

```bash
python -m pytest claims/amplitude_normalization/test_claim.py -v
# → FAIL (test_ns_lambda_independent)
```

---

## 5. Break the anomaly inflow coupling (wrong volume factor)

**Handle:** In `cs_axion_photon_coupling()`, change the denominator from
`2 * math.pi**2 * r_c` to `2 * math.pi * r_c` (wrong KK reduction).

**Expected result:** g_aγγ increases by π and β ≈ 1.1°, far outside the
1σ window.  `claims/anomaly_inflow/test_claim.py::test_coupling_formula_correct`
and `test_beta_within_observational_window` both FAIL.

```bash
python -m pytest claims/anomaly_inflow/test_claim.py -v
# → FAIL (test_coupling_formula_correct, test_beta_within_observational_window)
```

---

## 6. Break the FTUM fixed-point convergence

**Handle:** In `src/multiverse/fixed_point.py`, increase the iteration step
size to force non-convergence.

**Expected result:** `tests/test_fixed_point.py` fails at convergence tests.
The fixed point of the UEUM operator no longer exists within the search space.

```bash
python -m pytest tests/test_fixed_point.py -v
# → FAIL (convergence tests)
```

---

## 7. Break holographic entropy growth (arrow of time)

**Handle:** In `src/holography/boundary.py`, negate the entropy production
term so entropy decreases.

**Expected result:** `tests/test_arrow_of_time.py::TestEntropyMonotonicity`
FAILS — entropy is no longer increasing.

```bash
python -m pytest tests/test_arrow_of_time.py -v
# → FAIL (entropy monotonicity tests)
```

---

## 8. Break Pillar 14: atomic structure (φ-corrected spectroscopy)

**Handle:** In `src/core/atomic_structure.py`, remove the φ-correction factor
from `phi_corrected_energy()` so it returns the bare Bohr energy unchanged.

**Expected result:** `tests/test_atomic_structure.py` fails at tests that
verify the φ-shift produces measurable fine-structure corrections — e.g.
`test_phi_correction_nonzero` and `test_hydrogen_1s_phi_shift`.

**What this tests:** The claim that the 5D radion leaves a signature in
atomic spectra at the level of the measured fine-structure constant.

```bash
# Mutant: return bare_energy in phi_corrected_energy, then:
python -m pytest tests/test_atomic_structure.py -v -k "phi"
# → FAIL (phi-correction tests)
```

---

## 9. Break Pillar 15: cold-fusion φ-enhanced tunnelling

**Handle:** In `src/core/cold_fusion.py`, set the φ-enhancement factor to 1.0
(no enhancement) in `phi_enhanced_tunneling_probability()`.

**Expected result:** `tests/test_cold_fusion.py` fails at tests that verify
excess-heat predictions exceed the bare quantum-tunnelling baseline — e.g.
`test_enhancement_exceeds_bare` and `test_excess_heat_positive`.

**What this tests:** The claim that the 5D geometry amplifies sub-barrier
fusion rates in Pd-D lattices beyond the bare WKB prediction.

```bash
# Mutant: set phi_factor = 1.0 in phi_enhanced_tunneling_probability, then:
python -m pytest tests/test_cold_fusion.py -v -k "enhancement or excess"
# → FAIL
```

---



| Break point | Failing test file | Key test name |
|-------------|-------------------|---------------|
| k_CS ≠ 74 | `claims/integer_derivation/test_claim.py` | `test_cs_level_is_unique_minimiser` |
| KK Jacobian removed | `tests/test_inflation.py` | spectral index tests |
| r-tension hidden | `claims/tensor_ratio_fix/test_claim.py` | `test_canonical_r_exceeds_bicep_keck_bound` |
| λ affects nₛ | `claims/amplitude_normalization/test_claim.py` | `test_ns_lambda_independent` |
| Wrong coupling formula | `claims/anomaly_inflow/test_claim.py` | `test_coupling_formula_correct` |
| FTUM non-convergent | `tests/test_fixed_point.py` | convergence tests |
| Entropy decreases | `tests/test_arrow_of_time.py` | entropy monotonicity |
| φ-correction removed (atomic) | `tests/test_atomic_structure.py` | phi-correction tests |
| φ-enhancement removed (cold fusion) | `tests/test_cold_fusion.py` | enhancement/excess-heat tests |
| φ₀ closure fails (Pillar 56) | `tests/test_phi0_closure.py` | `test_closure_audit_all_consistent` |
| Acoustic peak gap unclosed (Pillar 57) | `tests/test_cmb_peaks.py` | `test_suppression_audit_corrected_less_than_raw` |
| LiteBIRD prediction gap wrong | `tests/test_litebird_forecast.py` | `test_forecast_scenarios_falsification` |

---

## What would constitute a real break

A break that matters is one where:

1. The test clearly corresponds to a physical claim (not just a numerical check).
2. The failure cannot be "fixed" by adjusting a free parameter.
3. The failure is reproducible from a clean clone.

If you find such a break, please open a GitHub issue with the title
**"Break report: [claim name]"** and include the output of the failing test.
