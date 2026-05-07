# Predictions You Can Break: Proton Decay, Gravity at 0.1mm, and Space Interferometers

*Post 103 of the Unitary Manifold series.*  
*Pillars 107–109 — Proton decay from SU(5)×orbifold, sub-mm gravity tests, KK stochastic GW background.*  
*v9.32, May 2026.*

**Epistemic category:** P. These are hard, quantitative predictions with explicit falsification conditions. No analogies. No approximations undisclosed. If the numbers are wrong, the framework is wrong.

---

## Three Ways to Kill a Theory

Science advances by falsification. A theory that cannot be broken is not a theory — it is a preference. The Unitary Manifold has committed, since its first post, to a precise birefringence prediction awaiting LiteBIRD. But birefringence is not the only target.

Pillars 107, 108, and 109 add three more. Not three vague gestures toward future experiments. Three specific numbers: a proton lifetime in years, a compactification length in microns, and a gravitational wave frequency in hertz. Each one comes with an experiment, a timeline, and a condition under which the framework is falsified.

Read these carefully. If you have access to the relevant instruments, these are the tests worth running.

---

## Pillar 107: Proton Decay

### Background

In a Grand Unified Theory, quarks and leptons are placed in the same representation of a larger symmetry group. SU(5), the simplest GUT, unifies the strong and electroweak forces at a scale M_GUT ∼ 10¹⁶ GeV. The unification implies the existence of new gauge bosons — called X and Y bosons — that mediate processes like:

    p → e⁺ + π⁰

A proton can convert into a positron and a neutral pion. This has never been observed. The Super-Kamiokande experiment in Japan has watched roughly 50,000 tonnes of water for decades and measured a lower bound on the proton lifetime in this channel:

    τ(p → e⁺π⁰) > 1.6 × 10³⁴ years (Super-Kamiokande, 95% CL)

For context: the age of the universe is 1.38 × 10¹⁰ years. A proton that decays in 10³⁴ years does so on a timescale 10²⁴ times the age of the universe. The experiment is sensitive to this because it contains 10³³ protons, and if even one decays per year, it is detectable.

### The Unitary Manifold Prediction

The framework predicts the proton lifetime through two ingredients (`src/core/proton_decay.py`, Pillar 107):

**1. The GUT scale:**

    M_GUT = φ₀ × 2 × 10¹⁶  GeV  =  2 × 10¹⁶ GeV  (at φ₀ = 1)

This is the standard SU(5) GUT scale. The factor φ₀ = 1 in Planck units reflects the FTUM fixed point.

**2. The orbifold suppression factor:**

The Z₂ orbifold geometry of the compact fifth dimension introduces a geometrical suppression of the X/Y boson propagator. The suppression factor is:

    f_orb = (1 / n_w) × cos²(π / n_w)

For n_w = 5:

    f_orb = (1/5) × cos²(36°)  =  0.2 × (0.8090)²  =  0.1309

This factor reflects the orbifold boundary conditions that modify the overlap integral between the quark/lepton wavefunctions and the GUT gauge boson in the compact dimension.

**The decay rate:**

    Γ_p = f_orb² × α_GUT² × m_p⁵ / M_GUT⁴

with α_GUT = 1/25 (the GUT coupling) and m_p = 0.938 GeV.

**The predicted lifetime:**

    τ_p = ħ / Γ_p  =  **1.676 × 10³⁸ years**

This is four orders of magnitude above the Super-Kamiokande lower bound of 1.6 × 10³⁴ years. The prediction is consistent with current non-observation.

| Quantity | Value |
|----------|-------|
| M_GUT | 2 × 10¹⁶ GeV |
| f_orb (n_w = 5) | 0.1309 |
| α_GUT | 1/25 |
| τ_p predicted | 1.68 × 10³⁸ yr |
| SK lower bound | 1.6 × 10³⁴ yr |
| Viable | ✅ Yes (4 orders of margin) |

### The Falsification Condition

The DUNE experiment (Deep Underground Neutrino Experiment at Fermilab, beginning operations ~2027) and the proposed Hyper-Kamiokande detector will push the proton lifetime sensitivity to approximately τ > 10³⁵ years within a decade, and eventual upgrades target ∼10³⁶ years.

The UM predicts τ_p ≈ 10³⁸ years. **If any experiment observes proton decay at a lifetime shorter than ∼10³⁶ years, the orbifold suppression factor is ruled out.** A detection at τ ∼ 10³⁴–10³⁵ years — which is the standard SU(5) prediction *without* the orbifold factor — would falsify the specific geometric suppression mechanism of the Unitary Manifold even while confirming SU(5) GUT physics.

A non-detection at τ > 10³⁸ years would begin to provide strong positive evidence for the orbifold factor, though distinguishing it from other high-lifetime mechanisms would require additional inputs.

Honest caveat: the GUT scale M_GUT = 2 × 10¹⁶ GeV is set by the FTUM fixed point at φ₀ = 1. The GUT scale is sensitive to how the coupling constants unify, which depends on the full KK spectrum. A first-principles derivation of M_GUT from the 5D geometry — rather than the postulated 2 × 10¹⁶ GeV — is open. The orbifold factor f_orb = 0.1309 is geometrically derived. The GUT scale factor is not.

---

## Pillar 108: Gravity at the Micron Scale

### Background

Newton's law of gravitation — F = GM₁M₂/r² — has been tested down to millimeter scales. At shorter distances, the measurement becomes experimentally challenging because gravitational forces are tiny compared to electrostatic, van der Waals, and Casimir forces that also operate between nearby objects.

If the universe has an extra compact spatial dimension, gravity leaks into that dimension at distance scales comparable to the compactification radius. Below that radius, Newton's law acquires a Yukawa correction:

    F = (GM₁M₂/r²) × [1 + α × exp(−r/L_c)]

where L_c is the compactification length and α ∼ O(1) is a coupling constant set by the number of extra dimensions. At distances r ≫ L_c, the exponential is negligible and Newton's law is recovered. At r ≲ L_c, gravity appears stronger — by a factor ∼ (1 + α).

The Eöt-Wash torsion balance at the University of Washington is the most sensitive probe of sub-millimeter gravity. Their best result (Kapner et al. 2007; Lee et al. 2020) excludes Yukawa deviations at the level α ∼ 1 for L_c ≳ 50 μm.

### The Unitary Manifold Prediction

The KK mass scale in the Unitary Manifold is M_KK ≈ 110 meV (the sub-mm gravity module uses this value, distinct from the dark matter module's ultralight graviton estimate which uses the winding-modified formula). The compactification length is (`src/core/submm_gravity.py`, Pillar 108):

    L_c = ħc / M_KK  =  197.33 MeV·fm / (110 × 10⁻⁶ MeV)  =  **1.794 μm**

This is a 1.794 micron compactification. The prediction is precise and unit-independent:

| Quantity | Value |
|----------|-------|
| M_KK | 110 meV |
| L_c predicted | **1.79 μm** |
| Current Eöt-Wash reach | 50 μm |
| Ratio (reach / L_c) | 27.9 |
| Next-gen target | ~2 μm |
| Detectable at next-gen | ✅ Yes |

The current Eöt-Wash experiments probe to 50 μm — about 28 times *larger* than the predicted compactification scale. The exponential suppression exp(−50/1.79) ≈ e^{−27.9} ≈ 10^{−12} means the current experiments are completely insensitive to the UM prediction. No current experiment can test this.

The next generation of sub-mm gravity experiments, targeting separations down to ~2 μm (see work by the Coldea group at Oxford and the Zurich Eötvös experiment), would directly probe L_c ≈ 1.79 μm. The Yukawa deviation at r = 2 μm is:

    δg/g = α × exp(−2/1.79) ≈ α × exp(−1.12) ≈ 0.33

A 33% deviation from Newton's law at 2 μm is a signal, not a fluctuation. For α = 1 (lowest KK graviton coupling to gravity), this is experimentally distinguishable.

### The Falsification Condition

**If a torsion-balance experiment achieves sensitivity to Newton's law at separations of 1–3 μm and finds no Yukawa deviation at the level α ≳ 0.01, the UM compactification scale M_KK ≈ 110 meV is ruled out.**

Conversely, if a deviation is detected consistent with L_c ≈ 1.79 μm, this would be a direct detection of the fifth dimension.

Honest caveat: the value M_KK = 110 meV comes from the submm_gravity module's convention. The dark_matter_kk module uses a different formula for M_KK (winding-corrected) that gives ≈ 33.6 meV. These two modules are computing different things — the submm module uses the Kaluza-Klein scale directly from the string-frame relation between the compactification radius and the graviton KK gap, while the dark matter module uses the field-theoretic mass formula for the lightest KK graviton *mode*. Reconciling these two conventions into a single M_KK is an open internal consistency question. The falsification condition above is stated for the submm module's value, which is the one directly linked to the gravity deviation formula.

---

## Pillar 109: LISA and the KK Gravitational-Wave Background

### Background

LISA — the Laser Interferometer Space Antenna — is a gravitational-wave observatory in space, three spacecraft in a triangular formation with 2.5 million kilometer arm lengths, scheduled for launch in the mid-2030s. It will be sensitive to gravitational waves in the millihertz to hertz frequency band: 10⁻⁴ Hz to 1 Hz.

This is exactly the band where gravitational waves from first-order phase transitions at scales between 10¹² and 10¹⁶ GeV would appear. The KK compactification is a phase transition of this type — when the universe cools through T ∼ M_KK, the extra dimension "freezes out" from the thermal plasma. If this transition is strongly first-order (bubble nucleation rather than a smooth crossover), it produces a stochastic gravitational-wave background that LISA could detect.

### The Unitary Manifold Prediction

The UM KK mass scale for the *standard* compactification is M_KK at the Planck scale ∼ M_Planck ∼ 10¹⁹ GeV. The peak frequency of the KK gravitational-wave background is (`src/core/kk_gw_background.py`, Pillar 69, extended by Pillar 109):

    f_peak = M_KK / (2π)  [natural units, converted to Hz]
           ≈ M_KK [GeV] × 1.52 × 10²⁴ Hz/GeV / (2π)

For M_KK at the Planck scale:

    f_peak ≈ 10¹⁹ × 10²⁴ / 6.28  ≈  **2.95 × 10⁴² Hz**

This is far above the LISA band (10⁻⁴–1 Hz). Planck-scale KK gravitational waves are undetectable by any existing or planned instrument. This is not a failure — it is a consistency condition. The Unitary Manifold is automatically consistent with all current GW observations precisely because the KK background peaks at frequencies 10⁴² Hz above where DESI, LISA, or NANOGrav operate.

For LISA to detect the KK background, M_KK would need to be:

    M_KK [for LISA] = f_LISA [Hz] × 2π / (1.52 × 10²⁴ Hz/GeV)
                    ≈ 10⁻² × 2π / 1.52 × 10²⁴
                    ≈ **4.1 × 10⁻²⁶ GeV**

This is 45 orders of magnitude below the Planck scale — an ultralight KK mass completely outside the UM's compactification scale. The UM does not predict a detectable KK GW signal for LISA.

What the UM *does* predict is a **primordial gravitational-wave background from inflation** at the tensor-to-scalar ratio r = 0.0315 (tree-level) or r = 0.0167 (one-loop corrected). This inflationary GW background peaks in the CMB frequency band (∼ 10⁻¹⁷–10⁻¹⁶ Hz), not the LISA band. CMB-S4 (targeting ∼2030) will probe this signal.

### The Honest LISA Prediction

The UM's LISA prediction is: **no KK stochastic background in the LISA band.** The GW energy density from KK phase transition at Planck scale is exponentially suppressed below LISA sensitivity in the 10⁻⁴–1 Hz range.

This is a prediction of absence, which is harder to frame as a falsification condition. But it becomes one if:

**Falsification condition:** If LISA detects a stochastic GW background in the 10⁻⁴–1 Hz band that is attributable to a first-order phase transition at a scale between 10¹² and 10¹⁶ GeV, this would suggest a sub-Planck KK mass scale inconsistent with the UM's canonical compactification. The UM would require a mechanism to produce a low-scale first-order transition at M_KK ∼ TeV, which is not currently present in the framework.

**Consistency confirmation:** If LISA measures a stochastic background consistent only with astrophysical sources (compact binary mergers, etc.) and sets tight upper limits on a primordial contribution at Ω_GW h² ≲ 10⁻¹², this is consistent with the UM's prediction of no sub-Planck KK GW signal.

The NANOGrav 15-year signal at f ∼ 3 × 10⁻⁹ Hz is not explained by the UM's KK mechanism — the KK background is 51 orders of magnitude higher in frequency. The UM is consistent with NANOGrav by absence of conflict, not by positive signal.

---

## The Three Predictions, Summarized

| Pillar | Prediction | Value | Current limit | Future test | Falsification condition |
|--------|-----------|-------|---------------|-------------|------------------------|
| 107 | Proton lifetime τ(p→e⁺π⁰) | **1.68 × 10³⁸ yr** | SK: > 1.6 × 10³⁴ yr | Hyper-K / DUNE | Detection at τ < 10³⁶ yr rules out orbifold suppression |
| 108 | 5th dimension compactification scale | **L_c = 1.79 μm** | Eöt-Wash: > 50 μm accessible | Next-gen torsion balance at ~2 μm | No Yukawa deviation at r < 3 μm at α > 0.01 rules out M_KK = 110 meV |
| 109 | KK GW peak frequency | **2.95 × 10⁴² Hz** (not in LISA band) | NANOGrav / LISA (no signal in band) | LISA 2030s | LISA signal from first-order transition at 10¹²–10¹⁶ GeV scale would require sub-Planck M_KK not in current UM |

---

## Why These Three Together

The point of listing these three predictions together is not that they are the most likely to be tested soon — the proton lifetime is so long that no experiment will reach it in a decade, and sub-micron gravity is technically formidable. The point is that they are *structurally independent*.

The proton decay prediction comes from the GUT scale and the orbifold suppression factor — it depends on M_GUT and n_w = 5.

The sub-mm gravity prediction comes from the KK mass scale and ħc — it depends on M_KK.

The KK GW prediction comes from the compactification scale set by M_Planck — it depends on where the KK tower is, not what the low-energy field content is.

Three predictions. Three different aspects of the same five-dimensional geometry. If any of them fail, the framework fails in a specific, diagnosable way. That is not a property all theories share.

---

## What to Check, What to Break

**Check:** Run `from src.core.proton_decay import proton_decay_summary; print(proton_decay_summary())`. Verify τ_p ≈ 1.68 × 10³⁸ yr and that `viable` is True (above the SK bound). Check the orbifold factor f_orb ≈ 0.1309.

**Check:** Run `from src.core.submm_gravity import submm_gravity_summary; print(submm_gravity_summary())`. Verify L_c ≈ 1.794 μm, current reach ≈ 50 μm, next-gen target ≈ 2 μm, and `detectable_next_gen` is True.

**Check:** Run `from src.core.kk_gw_background import gw_background_summary; import json; d = gw_background_summary(); print(d['lisa_comparison']['falsification_statement'])`. Confirm the Planck-scale KK GW peak is at ∼10⁴² Hz and outside the LISA band.

**Break the proton decay:** Show that the orbifold suppression factor f_orb = (1/n_w) cos²(π/n_w) is not the correct formula for the Z₂ orbifold modification of the X/Y boson propagator. Derive the correct wavefuncion overlap from the orbifold boundary conditions on the 5D gauge field. If the correct formula gives f_orb significantly different from 0.131, the lifetime prediction shifts accordingly.

**Break the sub-mm prediction:** The M_KK = 110 meV used in `submm_gravity.py` and the M_KK ≈ 33.6 meV from `dark_matter_kk.py` are computed from different formulas. Resolve which is the physically correct KK mass scale for the graviton sector of the UM, and recompute L_c from that. If L_c shifts outside the 1–10 μm range, the experimental strategy changes.

**Break the GW argument:** The absence of LISA signal is a consistency check, not a positive prediction. Construct a UM-compatible model in which the EW phase transition or a SUSY-breaking transition at M ∼ 10⁴ GeV is strongly first-order and produces a LISA-band GW background, then check whether it is consistent with the rest of the UM predictions. If it is, the framework gains a second GW prediction in the LISA band.

---

*Full source code, derivations, and 20,249 automated tests:*  
*https://github.com/wuzbak/Unitary-Manifold-*  
*Proton decay: `src/core/proton_decay.py` (Pillar 107)*  
*Sub-mm gravity: `src/core/submm_gravity.py` (Pillar 108)*  
*KK GW background: `src/core/kk_gw_background.py` (Pillar 109)*  
*Honest gaps: `FALLIBILITY.md`*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
