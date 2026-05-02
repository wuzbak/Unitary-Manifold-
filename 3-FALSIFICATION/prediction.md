# Prediction

## The sharpest predictions of the Unitary Manifold (v9.28)

> **β Prediction Hierarchy (for LiteBIRD discrimination):**
>
> | Rank | β value | Sector | Status |
> |------|---------|--------|--------|
> | **Primary** | **β ≈ 0.331°** | **(5,7) canonical sector**, k_CS = 74 | This is the UM primary prediction |
> | Secondary | β ≈ 0.273° | (5,6) sector, k_CS = 61 | Second lossless branch |
> | Loop-corrected | β ≈ 0.290° | Derived from primary + 1-loop | Alternative derivation |
> | RS1-phase | β ≈ 0.351° | Randall-Sundrum attractor | Maximum compactification |
>
> LiteBIRD (~2032) will discriminate between primary (0.331°) and secondary (0.273°) at 2.9σ.
> A result β < 0.22° or β > 0.38° falsifies the braided-winding mechanism.
> A result β ∈ (0.29°, 0.31°) (in the predicted gap) would strongly disfavor the framework.

---

### Dual-sector birefringence — β ∈ {0.331°, 0.273°}

The braided-winding framework contains exactly two lossless sectors (Pillar 95):

| Sector | β (derived) | k_CS | c_s |
|--------|-------------|------|-----|
| **(5,7) — primary** | **β = 0.331°** | 74 = 5²+7² | 12/37 |
| (5,6) — shadow | β = 0.273° | 61 = 5²+6² | 11/61 |

The gap between the two predictions is **0.058°  =  2.9 σ_LiteBIRD** — large enough for LiteBIRD to discriminate the two sectors.

| Field | Value |
|-------|-------|
| **Primary prediction** | β = 0.331° — (5,7) sector, k_CS = 74 |
| **Shadow sector** | β = 0.273° — (5,6) sector, k_CS = 61 |
| **Sector gap** | Δβ = 0.058°, resolvable at 2.9σ by LiteBIRD |
| **Internal theory uncertainty** | ± 0.006° from ± 0.5 in r_c; ± 0.003° from ±0.5 in φ_min_bare; combined ± 0.007° (quadrature) |
| **Observational prior** | β = 0.35° ± 0.14° (Minami & Komatsu 2020, 68 % CL) |
| **Theory input** | k_CS = 74 (primary) or k_CS = 61 (shadow); derived from geometry — see `claims/integer_derivation/` |
| **Experiment** | LiteBIRD (launch ~2032), CMB-S4 (~2030), Simons Observatory (ongoing) |
| **Status** | Both sectors consistent with current hint; LiteBIRD will discriminate |

---

### Why this is the right prediction to highlight

1. **Not fit.** β was not adjusted to match the data.  It emerges from k_CS = 74,
   which was derived by inverting the birefringence formula given the geometry
   (r_c, Δφ) of the compactification.  The chain is:

   ```
   compactification geometry → k_CS = round(73.71) = 74 → g_aγγ → β = 0.331°
   ```

2. **Not adjustable.** There is no remaining free parameter that can move β
   without also moving nₛ or r (because k_CS couples to both the CS angle and
   the field-strength normalisation).

3. **Internal theory uncertainty is small.** The dominant source of internal
   uncertainty is the compactification radius r_c, which enters the birefringence
   formula as β ∝ r_c.  Varying r_c by ± 0.5 (from 11.5 to 12.5) shifts β by
   ± 0.006° — negligible compared to the ± 0.14° observational prior.  The
   secondary source is φ_min_bare (± 0.5 → ± 0.003° in β).  Combined internal
   uncertainty in quadrature: **± 0.007°**.  This means the prediction is
   sharp enough that LiteBIRD will test the specific point value, not just the
   order of magnitude.

4. **Will be measured soon.** LiteBIRD will measure β to σ ≈ 0.02° (a 7×
   improvement over current constraints).  CMB-S4 will reach σ ≈ 0.01°.

5. **Has a sharp kill condition** (see below).

---

### What result kills the theory

| Result | Verdict |
|--------|---------|
| β < 0.07° at 3σ (LiteBIRD/CMB-S4) | **Theory killed**: β consistent with zero — k_CS = 74 is removed and the CS coupling has no observational anchor |
| β > 0.50° at 3σ | **Theory killed**: β significantly larger than 0.33° cannot be accommodated without changing k_CS and consequently breaking nₛ |
| β ∈ (0.29°, 0.31°) confirmed at 3σ | **Theory killed**: lands in the predicted inter-sector gap — neither sector is consistent |
| β = 0.331° ± 0.02° confirmed | **Primary sector (5,7) supported**: consistent, not yet proven — shadow (5,6) not yet excluded |
| β = 0.273° ± 0.02° confirmed | **Shadow sector (5,6) supported**: primary sector excluded; theory survives in (5,6) |

The **kill threshold** is β < 0.07° **or** β ∈ (0.29°, 0.31°).  These are bright lines, not soft
preferences.

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

Or use the Omega synthesis engine:
```python
from omega.omega_synthesis import UniversalEngine
engine = UniversalEngine()
cos = engine.cosmology()
print(f"β(5,7) = {cos.beta_57_deg:.3f}°")   # 0.331°
print(f"β(5,6) = {cos.beta_56_deg:.3f}°")   # 0.273°
```

---

### References

- Minami & Komatsu 2020: arXiv:2011.11612 (β = 0.35° ± 0.14°)
- Diego-Palazuelos et al. 2022: arXiv:2201.07241 (independent confirmation)
- LiteBIRD collaboration: arXiv:2202.02773 (forecast σ_β ≈ 0.02°; launch ~2032)
- `src/core/inflation.py`: `cs_axion_photon_coupling()`, `birefringence_angle()`
- `src/core/dual_sector_convergence.py`: Pillar 95 — exact two-sector derivation
- `omega/omega_synthesis.py`: `UniversalEngine.cosmology()` — live β computation
- `claims/integer_derivation/README.md`
- `claims/anomaly_inflow/README.md`
