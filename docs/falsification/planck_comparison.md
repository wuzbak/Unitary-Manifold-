# Planck 2018 Comparison — Unitary Manifold

*Unitary Manifold v10.59 | Source: `docs/CLAIM_MASTER_BOARD.md` (P1, P2)*

## CMB Spectral Predictions

The Unitary Manifold derives its CMB inflation observables from a single integer
pair **(n₁, n₂) = (5, 7)** via the braided Kaluza-Klein winding mechanism.
No free parameters are adjusted to fit Planck data.

| Observable | Planck 2018 | UM Prediction | Residual | Status |
|------------|------------|---------------|----------|--------|
| nₛ (spectral index) | 0.9649 ± 0.0042 | **0.9635** | 0.33σ | ✅ PASS |
| r  (tensor ratio)   | < 0.056 (95% CL) | **0.0315** | consistent | ✅ PASS |
| r  (BICEP/Keck)     | < 0.036 (95% CL) | **0.0315** | consistent | ✅ PASS |

## nₛ–r Plane

![CMB ns-r plane](../../9-INFRASTRUCTURE/results/fig01_cmb_ns_r_plane.png)

*The gold circle marks the Unitary Manifold prediction. Shaded regions show the
Planck 2018 68%/95% confidence level constraints. The dashed teal line marks the
BICEP/Keck r < 0.036 upper bound. The UM point sits comfortably inside both.*

## Derivation Chain

```
(n₁,n₂) = (5,7)
  ↓
K_CS = n₁² + n₂² = 5² + 7² = 74          [Chern-Simons level]
  ↓
c_s  = 12/37                               [braided sound speed]
  ↓
nₛ   = 1 − 2/N_e  (braided slow-roll)    → 0.9635
r    = 16 ε_braided                       → 0.0315
```

Executable verification: `python VERIFY.py` (checks 1 and 2).

## CMB-S4 Future Test

CMB-S4 (~2030) is expected to measure r to σ(r) ~ 0.002. If r < 0.010 is
confirmed at >3σ, the UM prediction is falsified.
Falsifier condition (P2): *r < 0.010 measured at >3σ*.

## References

- Planck Collaboration 2018: arXiv:1807.06211
- BICEP/Keck 2021: arXiv:2110.00483
- UM derivation: `src/core/inflation.py`, `src/core/braided_winding.py`
- Test: `tests/test_inflation.py`

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
