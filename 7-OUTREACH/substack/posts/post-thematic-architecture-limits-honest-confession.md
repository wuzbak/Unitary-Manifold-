# Architecture Limits: The Geometry's Honest Confession

*Thematic post — refreshed for Sprint BL.*
*Epistemic category: **META** — Repository-wide honest accounting of what 5D geometry cannot explain.*
*v34.0-S, 2026-09-02.*

---

## Introduction: What an Architecture Limit Is

Most scientific frameworks are criticized for overclaiming. Physics papers are occasionally retracted for understating uncertainty. The Unitary Manifold aims to do something unusual: it formally documents, in machine-readable form, not just what it claims to explain but **what it cannot explain**.

An architecture limit is a named, certified gap in the framework's explanatory reach that follows from the structure of the theory itself — not from a missing calculation, a numerical error, or insufficient effort, but from the geometry.

Architecture limits are different from open problems. An open problem might eventually be closed by more work within the current framework. An architecture limit cannot be closed without changing the framework's core structure.

This post catalogs the architecture limits currently certified in the Unitary Manifold, explains what each one means, and documents the extension path if one exists. Sprint BL adds one crucial refinement: the remaining open items are no longer a random debris field. They cluster into two families:

1. **UV flavor structures** — CKM θ₁₃, \|Vub\|, and fermion mass magnitudes.
2. **UV/global compactification geometry** — α_s Type-B and the Higgs architecture window.

That clustering matters because it tells us what kind of “more work” is still honest. More algebra inside the same 5D truncation is not the missing ingredient. New architecture is.

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

### Sprint BL family update — flavor and compactification

Sprint BL did not claim a miracle. It did something better. It turned two diffuse collections of complaints into two explicit architecture families.

On the **flavor** side, the repository now has a moduli-locked radii bridge and a joint family certificate. The verdict is not “closed.” The verdict is `FLAVOR_FAMILY_BOUNDARY_MAPPED`. The CKM θ₁₃ / \|Vub\| residual and the fermion-magnitude residual now point to the same missing UV flavor/moduli structure, with radii locking carrying the dominant unresolved burden.

On the **compactification** side, the repository now routes external PDG/FLAG α_s releases directly into the UV rerun path. That is not a closure either. It is a discipline upgrade. If α_s remains outside the tightened compactification window, the honest conclusion is still that the 5D EFT has reached its limit for that observable.

This is what a mature failure ledger looks like: fewer slogans, more structure.

### A.L. 3 — α_s Residual (Factor ~2.5)

**Predicted:** α_s(M_Z) in the right qualitative neighborhood from RS1 KK threshold  
**Residual:** tightened compactification window still excludes PDG α_s(M_Z)=0.1180  
**Source:** Pillars 937, 976, 986, 987  
**Status:** ALPHA_S_TYPE_B_FLOOR

The strong coupling constant at the Z mass, α_s(M_Z) ≈ 0.118, is not wildly wrong in the repository. It is worse, scientifically speaking: it is close enough to be interesting and still outside the tightened window. Sprint BJ exhausted one family of in-EFT routes. Sprint BL added the discipline layer that ingests PDG/FLAG α_s updates and automatically routes them back through the UV compactification machinery. The answer did not change. The gap is still structural.

The residual arises because the full α_s running is sensitive to global compactification data that the bare 5D EFT does not fix. The missing information is not “another clever coefficient.” It is the actual compactification geometry.

**Extension path:** explicit CY₃/CY₄ moduli stabilization, threshold matching, and backreaction-aware compactification data. Until then, α_s remains a named UV/global compactification boundary.

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
**Residual:** 5D/13D machinery bounds the window honestly, but does not produce a final architecture-independent mass value  
**Source:** Pillars 960, 977  
**Status:** HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW

The Higgs mass m_H ≈ 125 GeV arises from Coleman-Weinberg symmetry breaking in the 5D framework. The hierarchy problem (why is m_H ≪ M_Pl?) is addressed by the RS1 warp factor, which exponentially suppresses the KK mass scale relative to the Planck scale.

However, the full naturalness argument still leans on structure beyond the strict 5D truncation. The repository now has an honest window rather than a fake point prediction. That is progress. It is not closure. If the Higgs story tightens further, it will do so through the same compactification-facing family that α_s requires.

---

### A.L. 6 — Flavor Family Boundary

**Claim:** CKM θ₁₃, \|Vub\|, and fermion magnitudes do not currently close inside the audited EFT stack.  
**Source:** Pillars 989, 990, 991  
**Status:** FLAVOR_FAMILY_BOUNDARY_MAPPED

Before Sprint BL, the flavor sector looked like several separate complaints. After Sprint BL, it looks like one missing layer. The generation ladder behaves qualitatively correctly. CKM ordering is not nonsense. The family even survives a shared moduli/radii audit. But the final quantitative lock still fails. That failure is now localized: the dominant unresolved burden is the radii-lock / UV flavor-structure step.

That is a better scientific result than a cosmetic patch. We now know more precisely where the current architecture stops.

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

A framework with certified architecture limits is not a failing framework. It is an honest framework.

The alternative — claiming that every gap is solvable within the current structure, or not cataloging the gaps at all — is the standard in much of theoretical physics. Papers routinely present results without explicit failure conditions.

The UM's architecture limit catalogue does something unusual: it publishes the list of things the theory cannot explain, with machine-readable status tokens, extension paths where they exist, and explicit falsification conditions where they don't.

This is what scientific honesty looks like at the level of a formal framework. Sprint BL did not turn the confession into a victory speech. It turned it into a map.

That is better.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
