# DESI Says the Universe Is Accelerating Differently. Now What?

*Post 137 of the Unitary Manifold series.*  
*Epistemic category: **P** for physics claims; **A** for the routing protocol explanation.*  
*v10.28, May 2026.*

---

In 2024, the DESI collaboration released Year 1 results suggesting that dark energy may not be a simple cosmological constant. The equation-of-state parameter w, which equals -1 for a pure cosmological constant, appeared to show time evolution — specifically, the combination (w₀, wₐ) showed tension at roughly 2.5σ with the standard ΛCDM prediction.

The Unitary Manifold has a specific prediction for this: **wₐ = 0**.

That prediction is in tension with the DESI Year 1 central values. This post explains what that tension means, how we handle it, and what the routing protocol is.

---

## The UM Prediction

**Module:** `src/core/kk_de_wa_cpl.py` (Pillar 155)

The Unitary Manifold's dark energy is not a cosmological constant introduced by hand. It arises from the geometry of the Randall-Sundrum bulk, with the KK mode spectrum and flux quantization providing the effective equation of state.

The prediction: the wₐ parameter (time evolution of dark energy) is zero to leading order in the KK expansion. The theory allows w₀ ≠ -1 at the level of subleading corrections, but wₐ = 0 is a consequence of the static RS1 geometry — the extra dimension does not evolve with cosmic time at the level of the current approximation.

---

## What DESI Year 1 Found

DESI Year 1 (BAO + CMB + SNIa combined) found:

- w₀ ≈ -0.73 (shifted from -1)
- wₐ ≈ -0.65 (nonzero time evolution)

At the time of writing, this tension with ΛCDM is approximately 2.5σ. It is not yet at the 5σ threshold conventionally required for discovery. It may be a statistical fluctuation, a systematic error, or a real signal.

---

## The Three-Route Protocol

The Unitary Manifold's observation tracker (`3-FALSIFICATION/OBSERVATION_TRACKER.md`) handles observational tensions through an explicit three-route protocol:

**PASS:** The observation is consistent with the UM prediction within uncertainties. No action required beyond recording.

**TENSION:** The observation deviates from the UM prediction at 2–5σ. Action required: (1) check whether the deviation is driven by a specific dataset subset, (2) compute whether subleading UM corrections could close the gap, (3) document the tension explicitly in FALLIBILITY.md, (4) set a monitoring deadline for updated data.

**FALSIFIED:** The observation deviates from the UM prediction at ≥5σ with no identified subleading correction that could close the gap. The prediction is retracted and the relevant parameter is demoted.

**Current status of wₐ: TENSION**

---

## What the TENSION Status Means

The wₐ = 0 prediction is not retracted. The tension is real and documented. Three things are true simultaneously:

1. The DESI Year 1 central values, taken at face value, are inconsistent with wₐ = 0.
2. The tension is below 5σ and has not been confirmed by an independent dataset at the same significance.
3. The RS1 static geometry is an approximation — a time-evolving bulk geometry would allow wₐ ≠ 0, and the subleading correction from KK mode evolution has not been fully computed.

This is not a comfortable position. It is an honest one.

---

## What DESI Year 3 Will Decide

DESI Year 3 results are expected in approximately 2026. The Year 3 dataset is substantially larger than Year 1, with better systematic control.

**If Year 3 confirms wₐ ≠ 0 at >5σ:** The static RS1 dark energy prediction is falsified. The Unitary Manifold must either extend to a time-evolving bulk (which is a substantial theoretical change) or accept that its dark energy mechanism is wrong.

**If Year 3 is consistent with wₐ = 0:** The tension was a statistical fluctuation. The prediction is confirmed and the TENSION flag is cleared.

**If Year 3 shows 2–4σ tension:** Continued monitoring. The subleading KK correction calculation becomes urgent.

The monitoring deadline is set: within 30 days of DESI Year 3 publication, the OBSERVATION_TRACKER.md will be updated with the explicit routing decision.

---

## Why This Is Healthy

A theory that cannot be put into tension is not doing science. The wₐ = 0 prediction is specific, falsifiable, and currently in tension with the best available data.

We have not softened the prediction. We have not added a free parameter to accommodate DESI. We have documented the tension honestly and set a clear falsification threshold.

That is what honest physics looks like when the data pushes back.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
