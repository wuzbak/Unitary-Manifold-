# Architecture Limits: The Geometry's Honest Confession

*Thematic post — not tied to a specific sprint.*
*Epistemic category: **META** — Repository-wide honest accounting of what 5D geometry cannot explain.*
*v21.0-S, 2026-08-18.*

---

## Introduction: What an Architecture Limit Is

Most scientific frameworks are criticized for overclaiming. Physics papers are occasionally retracted for understating uncertainty. The Unitary Manifold aims to do something unusual: it formally documents, in machine-readable form, not just what it claims to explain but **what it cannot explain**.

An architecture limit is a named, certified gap in the framework's explanatory reach that follows from the structure of the theory itself — not from a missing calculation, a numerical error, or insufficient effort, but from the geometry.

Architecture limits are different from open problems. An open problem might eventually be closed by more work within the current framework. An architecture limit cannot be closed without changing the framework's core structure.

This post catalogs every architecture limit currently certified in the Unitary Manifold, explains what each one means, and documents the extension path if one exists.

---

## Tier 1 Architecture Limits: Observational Tensions

These are predictions where the framework's zero-parameter result is in tension with current data.

### A.L. 1 — r-Tension: The Tensor-to-Scalar Ratio

**Prediction:** r = 0.0315  
**Source:** Pillar 303, Pillar 396  
**Status:** ARCHITECTURE_LIMIT_CERTIFIED (IRREDUCIBLE_IN_BRAIDED_5D_EFT)

The UM predicts r = 0.0315 from the (5,7) braid geometry:

```
r_braided = (32 n_w c_s) / φ₀² × (1 + ρ²/(2(1−ρ²)))⁻¹
```

where n_w = 5, c_s = 12/37, φ₀ fixed by FTUM, ρ = 70/74.

**Current tension:** ACT DR6 + Planck gives r < 0.016 (95% CL) — the UM prediction exceeds this by a factor of ~2, at approximately 2σ tension.

**Why it is irreducible:** Pillar 303 proved that 87 WZW loop corrections would be needed to drive r from 0.0315 to 0.016. Perturbativity breaks at N_loops ~ 176. The loop expansion cannot rescue the prediction.

**What decides it:** CMB-S4 (~2030, σ_r ≈ 0.003). If CMB-S4 measures r > 0.020, the ACT DR6 result is incompatible and the UM prediction survives. If CMB-S4 confirms r < 0.016, the 5D braided EFT is falsified for this prediction.

---

### A.L. 2 — wₐ-Tension: Dark Energy Equation of State

**Prediction:** w₀ = −1, wₐ = 0  
**Source:** Pillar 301  
**Status:** ARCHITECTURE_LIMIT_CERTIFIED

The FTUM fixed-point freezes the radion: dφ/dt = 0. A frozen radion produces a cosmological constant with no time variation. wₐ = 0 is an exact prediction, not a choice.

**Current tension:** DESI DR2 CPL-corrected: 2.30σ against wₐ = 0.

**Why it is irreducible:** Pillar 301 proved that any rolling-radion mechanism sufficient to produce wₐ ≈ −0.55 (DESI best fit) requires ε_GW ~ 10⁻⁸⁸ fine-tuning in the Gauss-Bonnet coefficient — so extreme as to constitute a new fine-tuning problem worse than the cosmological constant.

**What decides it:** DESI DR3 (~2026). Three-branch decision tree is preregistered and machine-executable (Pillar 631).

---

## Tier 2 Architecture Limits: Quantitative Gaps

These are cases where the framework's prediction has the right qualitative structure but the quantitative agreement requires extensions beyond 5D.

### A.L. 3 — α_s Residual (Factor ~2.5)

**Predicted:** α_s(M_Z) in correct ballpark from RS1 KK threshold  
**Residual:** Factor ~2.5 in α_s(M_KK) relative to 5D expectation  
**Source:** Pillar 218, Pillar 52  
**Status:** ARCHITECTURE_LIMIT (10D required)

The strong coupling constant at the Z mass, α_s(M_Z) ≈ 0.118, is derived from the RS1 KK threshold and the 5D β-function. The geometric prediction is qualitatively correct (order of magnitude, correct running) but carries a factor-~2.5 residual.

The residual arises because the full α_s running requires the Calabi-Yau sector: 10D string theory compactified on CY₃ or CY₄ modifies the 5D β-function through KK threshold corrections. Within pure 5D RS1, these corrections cannot be computed.

**Extension path:** CY₄ moduli stabilization sprint (Pillar 685 roadmap, Steps 1–4). Expected to reduce residual significantly; full closure at ~10% level requires Rungs 11–12 of F-theory DBP.

---

### A.L. 4 — ΛQCD Moduli Gap

**Predicted:** Λ_QCD^scaffold ≈ 332 MeV (from RS1 AdS/QCD geometry)  
**Measured:** Λ_QCD ≈ 200 MeV  
**Residual:** Factor ~1.66  
**Source:** Pillar 685  
**Status:** ARCHITECTURE_LIMIT (4-step CY₄ moduli roadmap)

The QCD confinement scale is geometrically predictable in RS1 (via AdS/QCD duality), but the numerical agreement is off by ~66%. The gap is attributed to the CY₄ compact sector volume modulus not being fixed. Sprint X formalized this with a 4-step roadmap.

**Extension path:** Fix CY₄ volume modulus via G₄ flux stabilization → compute warp-factor correction → propagate to α_s running → rederive Λ_QCD.

---

### A.L. 5 — Higgs Mass Naturalness (Partial)

**Prediction:** Higgs mass hierarchy protection from RS1 volume factor  
**Residual:** NLO KK corrections within the EFT; full closure requires 6D structure  
**Source:** Pillar 641  
**Status:** ARCHITECTURE_LIMIT (partially addressed)

The Higgs mass m_H ≈ 125 GeV arises from Coleman-Weinberg symmetry breaking in the 5D framework. The hierarchy problem (why is m_H ≪ M_Pl?) is addressed by the RS1 warp factor, which exponentially suppresses the KK mass scale relative to the Planck scale.

However, the full naturalness argument at NLO requires 6D structure (Gauss-Bonnet terms on the T²/Z₃ orbifold). Pillar 641 computed Δ^{6D,NLO} = 4.223 < 100 — the fine-tuning parameter is within natural range at NLO, but a complete calculation requires the Higgs sector at two-loop in the 6D completion.

---

## Tier 3 Architecture Limits: Structure Limits

These are cases where the framework's explanatory scope simply ends.

### A.L. 6 — Baryogenesis: 5D Mechanism Does Not Exist

**Claim:** The UM cannot produce the observed baryon asymmetry η_B ≈ 6.1 × 10⁻¹⁰ within pure 5D RS1.  
**Source:** Pillar 371, Pillar 409, Pillar 422  
**Status:** ARCHITECTURE_LIMIT_CERTIFIED (4 mechanisms excluded)

Four baryogenesis pathways were explicitly tested in the 5D framework: Leptogenesis, Resonant Leptogenesis, Affleck-Dine, and Electroweak Baryogenesis. All four are ARCHITECTURE_LIMIT:

- Standard leptogenesis: RH neutrino degeneracy ΔM_R/M_R ≈ 4 × 10⁻⁵ required; braid lattice produces ~5.0 (factor 10⁵ too large)
- Electroweak baryogenesis: EWPT in RS1 is second-order; first-order required for EWB
- Affleck-Dine: No moduli with AD flat directions in the 5D superpotential
- Thermal leptogenesis: T_RH < M_1 in the canonical KK spectrum

**Extension path:** 6D baryogenesis via T²/Z₃ heavy triplet seesaw (Pillar 439, Pillar 505, Pillar 640). η_B viable for m_Σ ~ 650 GeV; neutron EDM prediction d_n ≈ 7.76 × 10⁻²⁷ e·cm testable at nEDM@SNS 2028. This is a 🔵 ADJACENT TRACK — not a hardgate prediction.

---

### A.L. 7 — Cosmological Constant: Not Explained

**Claim:** The UM does not derive the observed value of the cosmological constant Λ_obs ≈ 10⁻¹²³ M_Pl⁴.  
**Source:** Pillar 642  
**Status:** ARCHITECTURE_LIMIT (57-order-of-magnitude residual; 4-step 10D roadmap)

The cosmological constant problem is the largest fine-tuning problem in physics. The UM does not solve it. The framework predicts a frozen radion (cosmological constant from FTUM fixed-point; wₐ = 0), but the *value* of the CC is set by the KK vacuum energy, which exceeds the observed Λ by approximately 57 orders of magnitude in the 5D EFT.

**What this means for the framework:** The UM predicts the correct *behavior* of dark energy (no time evolution) but not the correct *value* of the vacuum energy. This is honest. A full resolution requires a 10D landscape mechanism (Rung 12 of F-theory DBP) that has not yet been addressed.

---

### A.L. 8 — Non-Perturbative Braid Condensate (Full Proof Open)

**Claim:** The NP-BC sub-gap programme (203 theorems; all 6 chains) has not produced a full non-perturbative proof.  
**Status:** ARCHITECTURE_LIMIT (full proof requires: named residuals closure, external HMC, functional-space extension)

The 203 sub-gap theorems are algebraic kernels — necessary components of a full non-perturbative proof, but not sufficient. The full proof requires assembly of all 18 sub-gap kernels with their 27 named residuals, external lattice (HMC) confirmation, and extension to full functional space. These are genuine mathematical challenges.

---

## What Architecture Limits Mean for the Framework

A framework with eight certified architecture limits is not a failing framework. It is an honest framework.

The alternative — claiming that every gap is solvable within the current structure, or not cataloging the gaps at all — is the standard in much of theoretical physics. Papers routinely present results without explicit failure conditions.

The UM's architecture limit catalogue does something unusual: it publishes the list of things the theory cannot explain, with machine-readable status tokens, extension paths where they exist, and explicit falsification conditions where they don't.

This is what scientific honesty looks like at the level of a formal framework. The geometry has a confession to make. Here it is, in full.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
