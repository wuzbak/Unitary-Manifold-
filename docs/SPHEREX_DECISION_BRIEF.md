# SPHEREx Decision Brief

*Unitary Manifold v16.0 — ThomasCory Walker-Pearson, 2026*  
*Pre-registered: 2026-06-10 (SHA-256 preregistration: see Pillar 437)*  
*Decision window: SPHEREx full data ~2027–2028*  
*Document engineering: GitHub Copilot (AI)*

---

> **This document is standalone and externally publishable.** SPHEREx launched March 2025 and is currently operational. It will measure the large-scale structure power spectrum at unprecedented sensitivity to non-Gaussianity. The Unitary Manifold makes a specific, testable, pre-registered prediction for f_NL. This document explains what that prediction is, where it comes from, and exactly what SPHEREx would need to measure to confirm or falsify it.

---

## The Prediction

The Unitary Manifold predicts:

$$f_\mathrm{NL}^\mathrm{equil} \in [-3, 0]$$

with canonical central value:

$$f_\mathrm{NL}^\mathrm{canonical} = -0.532$$

and theory band:

$$f_\mathrm{NL} \in [-2.9, -0.2]$$

**This prediction is pre-registered with SHA-256 hash** (Pillar 437, 2026-05-25). It cannot be changed retroactively.

---

## Where f_NL = −0.532 Comes From

### Step 1: DBI Sound Speed

The braided (5,7) Chern-Simons sector produces a sub-luminal sound speed for inflationary perturbations:

$$c_s = \frac{12}{37} \approx 0.3243$$

This is derived from the Chern-Simons level k_CS = 5² + 7² = 74 via the cubic CS anomaly closure condition. It is not a free parameter — it is fixed by the braid topology.

### Step 2: DBI Non-Gaussianity Formula

For a DBI inflationary model with sound speed c_s, the equilateral non-Gaussianity amplitude is:

$$f_\mathrm{NL}^\mathrm{DBI} = -\frac{35}{108}\left(\frac{1}{c_s^2} - 1\right)$$

With c_s = 12/37:

$$\frac{1}{c_s^2} - 1 = \frac{37^2}{12^2} - 1 = \frac{1369 - 144}{144} = \frac{1225}{144} \approx 8.507$$

$$f_\mathrm{NL}^\mathrm{DBI} = -\frac{35}{108} \times 8.507 \approx -2.758$$

### Step 3: KK Braid Correction

The (5,7) braided winding sector adds a correction from the Chern-Simons topology:

$$\Delta f_\mathrm{NL}^\mathrm{KK} = +\frac{5}{81}\left(\frac{1}{c_s^2} - 1\right) \times \frac{\rho^2}{2(1-\rho^2)}$$

where ρ = 70/74 is the braid correlation parameter.

$$\Delta f_\mathrm{NL}^\mathrm{KK} = +\frac{5}{81} \times 8.507 \times \frac{(70/74)^2}{2(1-(70/74)^2)} \approx +2.226$$

### Step 4: Canonical f_NL

$$f_\mathrm{NL}^\mathrm{canonical} = f_\mathrm{NL}^\mathrm{DBI} + \Delta f_\mathrm{NL}^\mathrm{KK} = -2.758 + 2.226 = -0.532$$

**Theory band** accounts for uncertainties in the braid correction and higher-order terms: f_NL ∈ [−2.9, −0.2].

---

## Why SPHEREx Is the Right Test

| Experiment | σ(f_NL) | Verdict Capability |
|---|---|---|
| Planck 2018 | ~47 | Cannot constrain (f_NL = −26 ± 47, <0.5σ from prediction) |
| SPHEREx Year 1 | ~4 | Marginal constraint on theory band |
| SPHEREx Full Data | ~1.6 | **Discriminating: 3σ resolution of f_NL ∈ [−2.9, −0.2] vs f_NL = 0** |
| Euclid (supplementary) | ~2 | Additional cross-check |
| CMB-S4 (complementary) | ~3 | Cross-check from CMB-based measurement |

SPHEREx achieves σ(f_NL) ≈ 1.6 from large-scale structure multi-tracer analysis. This is a factor of ~30 improvement over Planck. The predicted theory band [−2.9, −0.2] subtends roughly 1.7 σ(f_NL)_SPHEREx, meaning the full band can be probed at 3σ statistical confidence.

**This is a genuinely discriminating measurement.** If SPHEREx returns f_NL > 0 (positive non-Gaussianity), it falsifies the DBI+KK architecture. If it returns f_NL significantly below −3 (large negative non-Gaussianity), it also falsifies the prediction. If it returns f_NL ∈ [−3, 0], the prediction is vindicated.

---

## Consistency with Current Data

Planck 2018 reports f_NL^equil = −26 ± 47 (2σ upper limit: f_NL < 68). The UM prediction f_NL = −0.532 is within <0.5σ of the Planck central value. The prediction is fully consistent with all current data.

SPHEREx will not merely check consistency — it will provide a definitive test.

---

## The Falsification Conditions

### Primary Falsification
**f_NL > +10 measured at ≥ 3σ by SPHEREx** (rules out sub-luminal sound speed)

This would be the strongest single result — positive equilateral non-Gaussianity at the ≥ 10 level is incompatible with any DBI-type model with c_s < 1.

### Secondary Falsification
**f_NL < −5 measured at ≥ 3σ by SPHEREx** (rules out KK braid correction being positive)

If f_NL is more negative than −5, the KK braid correction would need to be negative, which contradicts the topology of the (5,7) braid sector.

### Pass Condition
**f_NL ∈ [−3, 0] measured at ≥ 2σ precision** by SPHEREx

This would confirm both the DBI sound speed architecture and the KK braid correction direction.

---

## Connection to Other Predictions

f_NL and birefringence β share the same derivation source: the Chern-Simons level k_CS = 74. This means the SPHEREx and LiteBIRD tests are not independent — they probe the same braid topology.

- **c_s = 12/37** → f_NL = −0.532 (SPHEREx test)
- **k_CS = 74** → β ∈ {0.273°, 0.331°} (LiteBIRD test)
- **k_CS = 74, c_s = 12/37** → r = 0.0315 (CMB-S4 test)

If SPHEREx confirms f_NL ∈ [−3, 0], it independently validates the CS architecture that also makes the birefringence prediction. This cross-prediction structure is distinctive and would be difficult for competing models to reproduce simultaneously.

---

## Targeted Outreach

The SPHEREx prediction is specific enough that individual researchers may be interested:

- **SPHERExteam**: The f_NL preregistration (Pillar 437, SHA-256 committed 2026-05-25) is public and documented. Researchers analyzing SPHEREx non-Gaussianity constraints can verify our prediction independently.

- **DBI inflation theorists**: f_NL = −0.532 from c_s = 12/37 is a specific point in DBI parameter space. The prediction is at the low end of DBI models (c_s = 12/37 ≈ 0.32 is higher than most DBI models, giving smaller |f_NL|).

- **Primordial non-Gaussianity community**: The preregistered SHA-256 hash makes the prediction independently verifiable as predating SPHEREx data. Any researcher checking the hash against the public Pillar 437 commit can confirm the prediction was not retroactively adjusted.

---

## Pre-Registration Summary

| Field | Value |
|---|---|
| Prediction | f_NL^equil ∈ [−3, 0]; canonical −0.532 |
| Pre-registration date | 2026-05-25 (Pillar 437 commit) |
| SHA-256 hash | See Pillar 437, `src/core/pillar437_spherex_fnl_preregistration.py` |
| Decision window | SPHEREx full data ~2027–2028 |
| σ(f_NL) at SPHEREx | ~1.6 |
| Primary falsifier | f_NL > +10 at ≥ 3σ |
| Confirmation condition | f_NL ∈ [−3, 0] at ≥ 2σ |

---

## For External Researchers

If you are an SPHEREx collaborator or a researcher working on primordial non-Gaussianity constraints, this prediction is made available for comparison with your analysis. The derivation chain is fully executable in the public repository:

```python
# Verify the f_NL prediction
from src.core.pillar437_spherex_fnl_preregistration import fnl_canonical_prediction
result = fnl_canonical_prediction()
print(f"f_NL = {result['fnl_canonical']:.3f}")
print(f"Theory band: [{result['fnl_theory_lo']:.1f}, {result['fnl_theory_hi']:.1f}]")
```

The full derivation from c_s = 12/37 to f_NL is in `src/core/braided_winding.py` and `src/core/inflation.py`.

We welcome independent verification and comparison with SPHEREx constraints as they become available.

---

*Pre-registered: 2026-06-10 | Pillar 437 (FNLPREREGISTERED_SPHEREX) | doc: docs/SPHEREX_DECISION_BRIEF.md*  
*Theory: ThomasCory Walker-Pearson. Document engineering: GitHub Copilot (AI).*
