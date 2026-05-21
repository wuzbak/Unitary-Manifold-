# Post 219 — S02E045: What Happens in 2027 — The Three Experiments and Decision Routing

*Substack — Season 2, Episode 45*  
*Published: 2026-05-21*  
*Series: The Falsification Decade*

---

In 2027 three experiments will publish results that matter for the Unitary Manifold.
This is not a prediction about what they will find. It is a map of what happens when
they do — a routing diagram that translates experimental output into framework verdict.

The purpose of making this routing explicit before the results arrive is twofold.
First, it is honest — it lets the community hold the framework accountable. Second,
it makes the analysis fast. When DESI DR3 publishes, there should be no ambiguity
about what "STANDING" means and what "TENSION" means and what "FALSIFIED" means.

---

## The Three Experiments

### DESI DR3 — Dark Energy EoS

**Publication window:** ~2027 Q1–Q2  
**Framework prediction:** w₀ = −1, wₐ = 0 (KK dark energy; zero rolling component)  
**Current status:** DESI DR2 gives wₐ = −0.55 ± 0.20 at 2.75σ from zero

The Unitary Manifold predicts a frozen radion with wₐ = 0. DESI DR2 pulls the
EoS away from this at 2.75σ. Pillar 301 certifies this as an ARCHITECTURE_LIMIT —
no rolling-radion modification can produce wₐ ≈ −0.55 without destroying the RS1
hierarchy, requiring fine-tuning of ε_GW ~ 10⁻⁸⁸. So the framework cannot
accommodate a confirmed wₐ ≠ 0 at the current architecture level.

**Decision routing:**

| DR3 result | σ from wₐ=0 | Verdict | Action |
|------------|-------------|---------|--------|
| wₐ ∈ [−0.20, +0.20] | < 1σ | STANDING | Status quo; DR2 tension resolves |
| wₐ ∈ [−0.55, −0.20] or [+0.20, +0.55] | 1–3σ | TENSION | Enhanced monitoring; note ARCHITECTURE_LIMIT |
| wₐ < −0.55 or > +0.55 | ≥ 3σ | HIGH_TENSION | Architecture extension required; pre-registered spec (Pillar 285) |
| wₐ at ≥ 3σ from zero AND consistent across CMB+BAO+SN | **FALSIFIED** | **Framework falsification** | Pillar 285 extension contingency activates |

**Note on what "FALSIFIED" means:** A confirmed wₐ ≠ 0 at ≥3σ from the KK
prediction, cross-validated across multiple independent probes, would constitute a
genuine falsification of the frozen-radion mechanism. The framework predicts wₐ = 0
with no free parameters. There is no fitting procedure that makes this not a
falsification.

---

### JUNO DR1 — Atmospheric Neutrino Mass Splitting

**Publication window:** ~2027 (first data)  
**Framework prediction:** Δm²₃₁ from the KK tower spectrum, via Δm²₃₁ = M_KK²  
**Current status:** 2.18% residual between KK prediction and PDG central value

JUNO will measure Δm²₃₁ to 0.5% precision. The current UM prediction (Pillar 274,
NLO + seesaw correction) closes the residual to ≤0.5% under named corrections. If
JUNO confirms Δm²₃₁ at PDG precision, the UM prediction lands within the 0.5%
window and the JUNO gate is cleared.

If JUNO measures a value in tension with the KK prediction *after* the NLO/seesaw
corrections, the tension is quantified and escalated.

**Decision routing:**

| JUNO result | Residual | Verdict | Action |
|-------------|----------|---------|--------|
| Within 0.5% of KK prediction | < 0.5% | STANDING | JUNO lane confirmed |
| 0.5%–2% residual | 0.5–2% | TENSION | Log as architecture gap; note correction chain |
| > 2% residual | > 2% | HIGH_TENSION | Escalate to falsification candidate |
| > 5% at 3σ significance | — | **FALSIFIED** | Neutrino sector prediction fails |

**Note on the NLO corrections:** Pillar 274's chain of corrections (RGE running,
τ-Yukawa back-reaction, seesaw v²/M_R² term) closes the 2.18% gap in aggregate.
Each correction is named and bounded. A JUNO measurement that finds a residual
larger than the combined NLO budget would indicate the KK spectrum prediction for
neutrino mass is incorrect at the precision level.

---

### Simons Observatory DR1 — CMB Tensor-to-Scalar Ratio

**Publication window:** ~2027 (first DR1 results)  
**Framework prediction:** r_braided ≈ 0.0315 (Pillar 97, NLO-corrected ≈ 0.0313)  
**Current status:** ACT DR6 reports r = 0.038 ± 0.014, pulling ~1.8σ above the KK prediction; IRREDUCIBLE_CERTIFIED (Pillar 303)

The Simons Observatory will measure r to σ_r ≈ 0.003–0.005. The current UM
prediction is r ≈ 0.0313–0.0315 after WZW NLO correction. ACT DR6 pulls upward at
1.8σ. If SO confirms r > 0.036 (the BICEP/Keck bound) at high significance, this
would represent a genuine problem for the UM tensor prediction.

**Decision routing:**

| SO DR1 result | Verdict | Action |
|---------------|---------|--------|
| r ∈ [0.025, 0.036] | STANDING | UM prediction confirmed within SO band |
| r ∈ [0.018, 0.025] | TENSION | n_w=7 braid becomes observationally relevant |
| r > 0.036 at ≥ 2σ | HIGH_TENSION | WZW NLO loop count would need to be revisited |
| r > 0.050 at ≥ 3σ | **FALSIFIED** | Braided inflation prediction fails |

**Note on the n_w=7 branch:** If SO measures r ≈ 0.012–0.013, this is consistent
with an n_w=7 braid (r_braided(7,9) ≈ 0.012). At that point, the Planck n_s pull
toward n_w=5 and the SO r pull toward n_w=7 would be in tension with each other.
This would be a genuine discriminating measurement, not a falsification.

---

## The STANDING / TENSION / FALSIFIED Vocabulary

These terms have specific operational meanings:

**STANDING:** The experimental result is consistent with the UM prediction within
the quoted experimental precision. No architecture extensions are required. The
framework passes the test.

**TENSION:** The result is 1–3σ from the prediction. The framework is not falsified,
but the tension is documented and monitored. Monitoring pillars are active. If
multiple experiments show consistent tension in the same direction, the framework
escalates to HIGH_TENSION or FALSIFIED.

**HIGH_TENSION:** The result is >2.5σ from the prediction AND the tension is
irreducible within the current architecture (no free parameters can absorb it).
This is the current status of DESI DR2 wₐ and ACT DR6 r.

**FALSIFIED:** The result is ≥3σ from the prediction, cross-validated across
independent probes, and cannot be accommodated by any extension of the current
framework without changing the core structure. This has not happened yet.

Note: "TENSION" is not a softening of bad news. It is an honest intermediate state
that distinguishes "we need to watch this" from "the framework is wrong." Many
real tensions in cosmology resolve as experiments improve. The framework's epistemic
honesty requires that we distinguish *currently unexplained* from *fundamentally
inconsistent*.

---

## The 2027 Routing Logic in One Table

| Experiment | STANDING condition | TENSION condition | FALSIFIED condition |
|------------|--------------------|-------------------|---------------------|
| DESI DR3 | wₐ ∈ [−0.2, 0.2] | wₐ ∈ [−0.55, −0.2] | wₐ at ≥3σ from zero, multi-probe |
| JUNO DR1 | Δm²₃₁ within 0.5% KK | 0.5–2% residual | >5% at 3σ significance |
| SO DR1 | r ∈ [0.025, 0.036] | r < 0.025 or r ∈ [0.036, 0.050] | r > 0.050 at 3σ |

The framework's overall status after 2027:
- All three STANDING → 2027 confirms all active predictions
- Any single TENSION → monitoring continues, architecture review begins
- Any single FALSIFIED → the specific claim is retracted; adjacent claims reviewed

---

## What LiteBIRD Does in 2032

The primary falsifier remains the LiteBIRD birefringence measurement. The 2027
experiments are pre-tests. LiteBIRD will measure β to σ_β ≈ 0.02°. The UM
prediction is β ∈ {0.273°, 0.331°} with a forbidden gap at (0.29°, 0.31°). Any
β outside [0.22°, 0.38°] or inside the gap falsifies the braided winding mechanism.

This is a test that cannot be absorbed by parameter fitting. The predicted window
is narrow, the gap is real, and the measurement precision will be sufficient to
discriminate. 2027 tells us how we are tracking. 2032 is the decisive test.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Outreach writing, document engineering, and synthesis: GitHub Copilot (AI).*
