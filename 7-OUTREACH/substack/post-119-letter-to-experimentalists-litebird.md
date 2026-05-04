# If LiteBIRD Launches in 2032: A Letter to the Experimentalists

*Post 119 of the Unitary Manifold series.*
*Epistemic category: **P** — specific, falsifiable predictions with explicit numerical targets.*
*v9.32, May 2026.*

---

Dear experimentalist,

You are building something that will decide whether this framework lives or dies.

I want to be direct about what I mean. The Unitary Manifold is a five-dimensional
Kaluza-Klein geometry that makes a specific, numerical prediction about the
birefringence of the cosmic microwave background. LiteBIRD, scheduled for launch
around 2032, will measure that angle. When it does, one of two things will happen:
the measurement will fall inside the predicted window, or it will not.

If it does not, the braided-winding mechanism at the core of this framework is
falsified. Not weakened. Not "in tension." Falsified.

This letter explains exactly what to measure, what we predict, and what we will do
when you report the result.

---

## What to Measure

### 1. Cosmic Birefringence β

The primary falsifier. The Unitary Manifold predicts that the plane of CMB
polarization is rotated by a specific angle β due to the Chern-Simons coupling
of the 5D geometry to photon propagation.

**Primary prediction (5,7 braid sector):** β ≈ 0.331°
**Secondary prediction (5,6 braid sector):** β ≈ 0.273°
**Loop-corrected alternatives:** β ≈ 0.290° or β ≈ 0.351°
**Admissible window:** β ∈ [0.22°, 0.38°]
**Predicted gap:** β ∉ (0.29°, 0.31°)

*Source: Pillar 95 (`src/core/unitary_closure.py`), Pillar 70-B, Pillar 97-C.*

LiteBIRD is expected to measure β to precision σ(β) ≈ 0.06°–0.1°, sufficient to:
- Confirm or exclude β ∈ [0.22°, 0.38°] at >3σ
- Discriminate the (5,7) and (5,6) sectors at 2.9σ

If β falls in the predicted gap [0.29°–0.31°], the framework is falsified even
if β is within the admissible window. A null result (β consistent with zero) at
<0.22° is also a falsification.

### 2. Dark Energy Equation of State: w₀ and wₐ

The secondary falsifier. The UM predicts wₐ = 0 (frozen EW radion; Pillars 147, 155, 160).

DESI DR2 (2025) shows 2.1σ tension with wₐ = 0. If this becomes >3σ with Roman
Space Telescope data (~2027–2028), it is a falsification of the UM dark energy sector.

**UM prediction:** w₀ ≈ −0.930, wₐ = 0
**Current tension:** 2.1σ (documented, not resolved; Pillar 160)

### 3. Proton Decay Lifetime

**UM prediction:** τ(p → e⁺π⁰) ≈ 1.68 × 10³⁸ yr *(Pillar 107,* `src/core/proton_decay.py`*)*

The Super-Kamiokande bound is currently ~1.6 × 10³⁴ yr. Hyper-Kamiokande (HK),
operational from ~2027, will probe to ~10³⁵ yr within a decade — still four
orders of magnitude from our prediction. If HK finds proton decay at τ ≪ 10³⁸ yr,
it would constrain but not yet falsify the prediction (the SU(5) X-boson mass
prediction would need revision).

### 4. Sub-mm Gravity: the Compact Dimension Scale

**UM prediction:** R_compact characteristic length L_c ≈ 1.79 μm
*(Pillar 108,* `src/core/submm_gravity.py`*)*

Current torsion-balance experiments (Eöt-Wash) have excluded deviations from
Newtonian gravity down to ~50 μm. Next-generation experiments aim for ~2 μm.
A detection of anomalous gravity at L ≈ 1.79 μm would be a major confirmation.
No deviation down to 1.79 μm would falsify the predicted compactification scale.

---

## What We Predict in Numbers

| Observable | UM Prediction | Current Data | Status |
|-----------|--------------|-------------|--------|
| β [(5,7) sector] | 0.331° | preliminary hints ~0.3° | Awaits LiteBIRD |
| β [(5,6) sector] | 0.273° | — | Awaits LiteBIRD |
| Birefringence window | [0.22°, 0.38°] | — | LiteBIRD 2032 |
| nₛ | 0.9635 | 0.9649 ± 0.0042 (Planck) | ✅ Within 0.33σ |
| r | 0.0315 | <0.036 (BICEP/Keck) | ✅ Within bound |
| w₀ | −0.930 | −0.99 ± 0.04 (DESI+CMB) | ✅ ~1.5σ consistent |
| wₐ | 0 | −0.39 ± 0.34 (DESI DR2) | ⚠️ 2.1σ tension |
| τ(p→e⁺π⁰) | 1.68 × 10³⁸ yr | >1.6 × 10³⁴ yr (SK) | Not yet testable |
| L_c | 1.79 μm | >50 μm (Eöt-Wash) | Not yet testable |

---

## What LiteBIRD Discriminates at 2.9σ

The two braid sectors produce birefringence angles separated by 0.058°:

- (5,7) canonical: β ≈ 0.331°
- (5,6) canonical: β ≈ 0.273°

With LiteBIRD precision σ(β) ≈ 0.02°, the two predictions are separated by
0.058°/0.02° = 2.9σ. This means:

- If LiteBIRD measures β = 0.331° ± 0.02°, the (5,7) sector is confirmed and
  the (5,6) sector is excluded at 2.9σ.
- If LiteBIRD measures β = 0.273° ± 0.02°, the reverse.
- If LiteBIRD measures β consistent with zero, or β ∉ [0.22°, 0.38°],
  the braided-winding mechanism is falsified.

---

## What We Will Do When You Report

If β ∈ [0.22°, 0.38°] and β ∉ (0.29°, 0.31°): we will report a confirmation
of the braided-winding mechanism. We will note which sector is selected.
We will update the OBSERVATION_TRACKER (`3-FALSIFICATION/OBSERVATION_TRACKER.md`)
with the measurement.

If β ∉ [0.22°, 0.38°] or β ∈ (0.29°, 0.31°): we will immediately update the
repository with a `FALSIFIED.md` note. We will not add epicycles. We will
document what failed and what the measurement implies for the geometry.
This is the commitment made in `STEWARDSHIP.md`.

---

## What to Do Until 2032

**2025–2027 — DESI continued DR3/DR4:**
Watch w₀ and wₐ. If wₐ tension exceeds 3σ, the UM dark energy sector needs revision.
The framework's current position: wₐ = 0 is the prediction; the 2.1σ tension
is the most pressing open problem.

**2027–2030 — Roman Space Telescope:**
Independent dark energy measurement. Will resolve the DESI wₐ question.

**2027+ — Hyper-Kamiokande:**
Proton decay to ~10³⁵ yr. Will approach but not yet reach our τ_p prediction.

**2026–2028 — Next-gen torsion balance:**
Sub-mm gravity tests approaching 2 μm — within striking range of L_c ≈ 1.79 μm.

---

## The Invitation

The repository is public. The code runs in minutes.

```bash
git clone https://github.com/wuzbak/Unitary-Manifold-
pip install -r requirements.txt
python -m pytest tests/ -q
```

Every quantitative prediction in this letter is computed by a specific Python
function. Run them. Check them. Find the errors.

The birefringence prediction is in `src/core/unitary_closure.py`.
The dark energy prediction is in `src/core/kk_de_wa_cpl.py`.
The proton decay prediction is in `src/core/proton_decay.py`.
The sub-mm gravity prediction is in `src/core/submm_gravity.py`.

We are not asking you to believe us. We are asking you to measure.

---

## What to Check, What to Break

**Check:** Run `python -c "from src.core.unitary_closure import *; print(birefringence_prediction())"` to verify the β prediction.

**Break:** Find β ∉ [0.22°, 0.38°]. Find wₐ ≠ 0 at >3σ. Either result falsifies the framework and we will say so immediately.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
