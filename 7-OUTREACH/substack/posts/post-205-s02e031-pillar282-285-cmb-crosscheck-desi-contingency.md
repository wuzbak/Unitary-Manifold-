# Before the Verdict: CMB Cross-Checks and the DESI Contingency Architecture

*Post 205 of the Unitary Manifold series.*  
*Series S02, Episode E031.*  
*Epistemic category: **Adjacent Track** — Pillar 282 CMB Planck crosscheck; Pillar 285 dark energy extension specification, non-hardgate.*  
*May 2026.*

---

There is a quality of scientific work that does not make headlines but is absolutely necessary: the cross-check.

After you have built a framework, derived its predictions, and committed to its falsification conditions, the next thing you must do is verify that all the pieces fit together. Do the inflationary parameters feed the CMB equations correctly? Do the acoustic peak positions come out right? When you put the UM's n_s, r, and A_s into the standard Boltzmann transfer functions, do you get peaks at ℓ ≈ 220, 540, 800 — the places where Planck measured them?

Pillar 282 is that cross-check. It is not a new claim. It is not a derivation. It is the calculation that verifies the UM's inflationary parameters are internally consistent with the CMB geometry they are supposed to produce.

And then there is Pillar 285 — which represents a different kind of scientific responsibility entirely: pre-registering what the framework would look like if its most challenged prediction turns out to be wrong.

---

## Pillar 282: CMB Acoustic Peak Position Cross-Check

The acoustic peaks in the CMB power spectrum are located at specific angular scales — specific values of the multipole number ℓ. The first peak is near ℓ ≈ 220, the second near ℓ ≈ 540, the third near ℓ ≈ 800. These positions are determined by the sound horizon at last scattering (r_s★) and the comoving angular diameter distance to the surface of last scattering (χ_★), combined with an ISW (Integrated Sachs-Wolfe) phase shift.

The peak positions in a flat universe are:

```
ℓ_n ≈ n · π · χ_★/r_s★ − Δφ
```

where Δφ ≈ 0.267π is the ISW phase shift (a quantum-mechanical effect from the gravitational potential decaying after last scattering).

Pillar 282 asks: when you plug in the UM's inflationary parameters (n_s = 0.9635, r = 0.0315, A_s ≈ 2.101 × 10⁻⁹) plus standard cosmological parameters (Planck ΛCDM background: Ω_b h², Ω_cdm h², H₀, z_★ = 1090), do you get the right peak positions?

The calculation:

**Sound horizon at last scattering:** computed from the baryon and CDM densities, the radiation-to-matter ratio, and the acoustic integral at recombination. The standard result is r_s★ ≈ 144.4 Mpc.

**Comoving angular diameter distance:** the distance to z_★ = 1090 in flat ΛCDM with Planck parameters. χ_★ ≈ 13,885 Mpc.

**Naive peak positions (no ISW):** ℓ_1 = π · 13885/144.4 ≈ 302. This is wrong — 35% above the observed ℓ ≈ 220.

**Phase-shifted peaks (with Δφ):** adding the Hu-Sugiyama ISW phase shift Δφ/π ≈ 0.267 gives ℓ_1 ≈ 220 for the first peak. The subsequent peaks (ℓ_2 ≈ 540, ℓ_3 ≈ 800, ℓ_4 ≈ 1150) all land within the Planck-measured positions.

The KK correction to the peak positions is tiny: δ_KK ~ 8 × 10⁻⁴, from the KK-modified Hubble rate at recombination. This is far below the observational precision of current CMB experiments. The KK effect on peak positions is not the story here — the story is that the standard physics (ISW phase shift + ΛCDM background) correctly places the peaks, and the UM's inflationary parameters feed into this correctly.

**Key finding from Pillar 282:** the ℓ ≈ 300 naive result for the first peak, which might alarm a reviewer, is a well-understood artifact of neglecting the ISW phase shift. With the phase shift, the predictions align with observation. The ISW effect is standard physics, not a KK effect, and Pillar 282 makes this explicit.

This is important for the framework's credibility. If someone runs the UM's inflationary parameters through a CMB calculator and gets ℓ_1 ≈ 300, they might think something is wrong with the framework. Pillar 282 documents why the naive calculation gives the wrong answer and what the correct calculation gives. The cross-check is clear; the result is correct.

---

## The DESI Context: Where We Stand

Between the CMB cross-check and the dark energy extension spec, the DESI situation is the central tension of the current moment.

DESI DR2 (2025) measured wₐ = −0.55 ± 0.20 in combined datasets — 2.75σ from the UM's prediction of wₐ = 0. This is HIGH_TENSION in the framework's vocabulary: real, non-trivial, but below the 3σ falsification threshold.

DESI DR3 is expected sometime in 2026. If the DR3 central value stays near −0.55 with a narrowing error bar, the tension will approach or cross 3σ. DESI Y5 (~2027) will deliver the measurement that will likely settle this question definitively.

The framework has made its commitment: 3σ combined tension → FALSIFIED (G3). This threshold is hardcoded in Pillar 260 (Falsifier Decision Algebra) and in the DESI DR3 publication-day runbook. It cannot be changed after the fact.

Given this commitment, the scientifically responsible thing to do before DESI DR3 is to specify — precisely, in advance, in executable form — what a revision would look like if the falsification threshold is crossed. That is what Pillar 285 provides.

---

## Pillar 285: The Dark Energy Extension Specification

Pillar 285 is not a rescue mechanism. It does not weaken the 3σ falsification threshold. It does not argue that the current tension is less serious than it appears. It is a pre-registration: if wₐ ≠ 0 is confirmed at ≥ 3σ, here is what the v2.0 revision would need to look like.

**Why pre-register?** Because the alternative is improvisation under pressure. When a key prediction is falsified, there is enormous temptation to quickly produce an ad-hoc modification that salvages the number. Pre-specifying the extension space forces the framework to commit to *which* modifications are acceptable and *what constraints they must satisfy* — before the data comes in. This prevents motivated reasoning from influencing the response.

Pillar 285 specifies four candidate extensions:

**Extension 1: New Bulk Scalar (quintessence in the RS1 bulk).** A canonically normalized scalar field φ̃ rolling in the RS1 bulk, with a potential V(φ̃) that allows cosmological evolution on the Hubble timescale. Requirements: sub-Planckian displacement (Δφ̃/M_Pl < 1), Breitenlöhner-Freedman bound satisfied (m₅² > −4k² in AdS₅), no destabilization of the Goldberger-Wise stabilizer, and coupling ε_φ̃ to the GW sector < 0.01.

This is the most straightforward extension: keep the RS1 geometry, add a new field that does what the radion cannot. The hierarchy problem solution remains intact, the KK mass scale stays at ~TeV, and the new field accounts for the measured wₐ.

**Extension 2: Cosmological Radion (light-mass scenario).** Relax the Goldberger-Wise stabilization to allow a cosmologically light radion m_r ~ H₀. This is the most drastic option — it directly contradicts the hierarchy solution because if m_r ~ H₀, the separation between the TeV and Planck scales is not geometrically generated. This extension would require a new stabilization mechanism that provides the hierarchy without the GW potential, or an explicit acknowledgment that the hierarchy problem remains unsolved in the revised framework.

**Extension 3: k-Essence / Modified Kinetic Term.** A bulk scalar with non-canonical kinetic term X^n (k-essence) in the RS1 geometry. k-essence can produce wₐ ≠ 0 with sub-Planckian displacements if n > 1. Requirement: the sound speed c_s² = 1/(2n−1) must be positive (stability) and must not conflict with the braided sound speed c_s = 12/37 from Pillar 27. This is a self-consistency requirement — the dark energy sector cannot have a sound speed that contradicts the inflationary sector's sound speed, since both arise from the same geometry.

**Extension 4: Coupled Dark Energy.** Introduce an explicit coupling β_DE between the KK dark-energy sector and dark matter. This can produce an effective wₐ_eff ≠ 0 even with a frozen radion — the coupling creates an effective equation of state modification without requiring the radion to evolve. Requirements: β_DE < 0.1 from CMB growth-rate bounds, no violation of equivalence-principle tests.

Each extension is implemented as a function with parameter inputs and a feasibility report. The outputs include: theoretical wₐ prediction as a function of extension parameters, BF bound check, sub-Planckian displacement check, GW stability check, CMB growth-rate compatibility, and an overall feasibility verdict.

---

## What the extension spec is not

Pillar 285 is explicit about several things it is not:

It is **not a signal that the framework is failing.** The current tension is 2.75σ, below the 3σ threshold. The framework has not been falsified. The extension spec is preparation, not retreat.

It is **not a menu of options to pick from.** If and when DESI DR3 crosses 3σ, the revision process would begin with a rigorous assessment of which extension (if any) is consistent with all other observational constraints — LiteBIRD birefringence, CMB power spectrum, gravitational wave bounds, and the full SM parameter consistency. The extension with the most evidence would be adopted; the others would be documented as ruled out.

It is **not a weakening of the current prediction.** The wₐ = 0 prediction stands until the 3σ threshold is crossed. If DESI DR3 returns wₐ consistent with zero at 1.5σ, Pillar 285 becomes moot and is archived as successful epistemic housekeeping.

---

## The discipline of preparing for falsification

There is something philosophically important about Pillar 285 that goes beyond the specific DESI situation.

Most theories do not prepare for their own falsification. The implicit assumption is that the theory is right, and falsification — if it happens — will be dealt with when it comes. This produces a specific failure mode: when data comes in that challenges the theory, the response is improvised, motivated, and often ad-hoc.

The Unitary Manifold is trying to do something different. It is not just committing to falsification conditions in words — it is building the scaffolding for a responsible response in advance. Pillar 285 says: here are the four modifications that would be theoretically principled; here are the quantitative constraints each must satisfy; here is the execution script that evaluates each one; here is the file update protocol if DR3 forces a revision.

When the data comes in, the response will not be improvised. It will execute from the prepared specification.

That is what scientific integrity looks like under empirical pressure: not blind confidence that you are right, but careful preparation for the possibility that you are wrong.

---

## Bottom line

Pillar 282 verifies that the UM's inflationary parameters produce the correct CMB acoustic peak positions when fed through standard Boltzmann physics — including the essential ISW phase shift. The cross-check passes.

Pillar 285 pre-registers the four candidate dark energy extensions that would be theoretically principled responses to a DESI falsification of wₐ = 0, with explicit quantitative constraints, implementation functions, and decision criteria. The current prediction stands; the revision architecture is ready if it is needed.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
