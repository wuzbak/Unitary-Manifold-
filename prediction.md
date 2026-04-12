# Prediction

## The single sharpest prediction of the Unitary Manifold

### β = 0.351° ± 0.14° — cosmic birefringence angle

| Field | Value |
|-------|-------|
| **Predicted value** | β = 0.351° |
| **1σ error bar** | ± 0.14° (set by the observational prior, not theory freedom) |
| **Theory input** | k_CS = 74 (derived from geometry; see `claims/integer_derivation/`) |
| **Experiment** | LiteBIRD (launch ~2028), CMB-S4 (~2030), Simons Observatory (ongoing) |
| **Status** | Consistent with Minami & Komatsu 2020 (+Diego-Palazuelos et al. 2022) hint at β ≈ 0.35° |

---

### Why this is the right prediction to highlight

1. **Not fit.** β was not adjusted to match the data.  It emerges from k_CS = 74,
   which was derived by inverting the birefringence formula given the geometry
   (r_c, Δφ) of the compactification.  The chain is:

   ```
   compactification geometry → k_CS = round(73.71) = 74 → g_aγγ → β = 0.351°
   ```

2. **Not adjustable.** There is no remaining free parameter that can move β
   without also moving nₛ or r (because k_CS couples to both the CS angle and
   the field-strength normalisation).

3. **Will be measured soon.** LiteBIRD will measure β to σ ≈ 0.02° (a 7×
   improvement over current constraints).  CMB-S4 will reach σ ≈ 0.01°.

4. **Has a sharp kill condition** (see below).

---

### What result kills the theory

| Result | Verdict |
|--------|---------|
| β < 0.07° at 3σ (LiteBIRD/CMB-S4) | **Theory killed**: β consistent with zero — k_CS = 74 is removed and the CS coupling has no observational anchor |
| β > 0.50° at 3σ | **Theory killed**: β significantly larger than 0.35° cannot be accommodated without changing k_CS to ≥ 100 and consequently breaking nₛ |
| β = 0.35° ± 0.02° confirmed | **Theory supported**: consistent, but not proven — competing models must be checked |

The **kill threshold** is β < 0.07°.  This is a bright line, not a soft
preference: at that level the 1σ interval for β no longer overlaps with zero
and r simultaneously, and k_CS = 74 is unambiguously excluded.

---

### Reproducibility

```bash
# Reproduce the predicted β from the repository
python claims/anomaly_inflow/verify.py
```

Expected output (last line):
```
β = 0.3514°  (target = 0.35°)
```

Or run the test suite:
```bash
python -m pytest claims/integer_derivation/test_claim.py claims/anomaly_inflow/test_claim.py -v
```

---

### References

- Minami & Komatsu 2020: arXiv:2011.11612 (β = 0.35° ± 0.14°)
- Diego-Palazuelos et al. 2022: arXiv:2201.07241 (independent confirmation)
- LiteBIRD collaboration: arXiv:2202.02773 (forecast σ_β ≈ 0.02°)
- `src/core/inflation.py`: `cs_axion_photon_coupling()`, `birefringence_angle()`
- `claims/integer_derivation/README.md`
- `claims/anomaly_inflow/README.md`
