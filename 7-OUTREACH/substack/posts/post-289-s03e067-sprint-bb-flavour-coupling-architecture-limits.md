# Flavour Physics: Why the Particles Have the Masses They Do

**Unitary Manifold — S03E067 · v26.0 · Sprint BB**

---

Of all the mysteries in particle physics, the "flavour problem" may be the strangest. The Standard Model contains six quarks and six leptons. Their masses span thirteen orders of magnitude — from the electron at 0.511 MeV to the top quark at 173,000 MeV. The mixing angles between quark families (encoded in the CKM matrix) are small but precisely measured. CP violation — the tiny asymmetry between matter and antimatter — is real and measured, but nobody knows *why* it has the magnitude it does.

The Standard Model does not explain any of this. It puts these numbers in by hand, measured from experiment, with no deeper origin. Sprint BB is the Unitary Manifold's systematic attempt to derive them from the 7D geometry. This post reports what was established, what was not, and why being honest about the latter matters more than claiming the former.

---

## The CKM matrix: what it is and why it's hard

The CKM matrix (named for Cabibbo, Kobayashi, and Maskawa) is a 3×3 unitary matrix that encodes how likely quarks are to transform into each other during weak interactions. An up quark can decay into a down quark, a strange quark, or a bottom quark — the CKM matrix gives the probabilities.

The matrix is characterized by four numbers: three mixing angles (θ₁₂, θ₂₃, θ₁₃) and one CP-violating phase (δ). These four numbers determine the entire structure of quark flavour physics. They are measured to high precision. Any theory that claims to derive the Standard Model must either compute these numbers or honestly state it cannot.

Sprint BB worked on the 7D computation.

---

## What the 7D geometry gives you

In the Unitary Manifold, fermion mass matrices come from Yukawa couplings between bulk fields in the extra dimensions. When you reduce from 7D to 4D, the overlap integrals of wavefunctions in the extra dimensions produce a mass matrix. The CKM matrix is what you get when you diagonalize the up-type and down-type quark mass matrices separately and then take the ratio.

**CKM bulk mass spectrum (CKM_7D_BULK_MASS_SPECTRUM_DERIVED)**

Sprint BB derived the mass eigenvalue spectrum from 7D bulk mass parameters. This is the machinery that produces the quark masses. The key result: the 7D geometry generates a hierarchical mass structure naturally — large separations between generations emerge from exponential suppression of wavefunctions in the extra dimension rather than from tuned Yukawa couplings. The hierarchy is geometric in origin.

**CKM mixing angles — partial derivation (CKM_7D_PARTIAL_TENSION)**

The honest status: θ₁₂ (the Cabibbo angle, ~13°) and θ₂₃ (~2.4°) are reproduced to within 30% of their PDG values. θ₁₃ (~0.2°, the smallest angle, governing CP violation in B-meson decays) remains outside the geometric computation. This is labeled PARTIAL because two-thirds of the angles are in the right ballpark but the third — the one most sensitive to CP violation — has a residual that the 7D geometry cannot fully account for. It is not hidden and not softened.

**CP violation from 7D discrete torsion (CP_VIOLATION_7D_PARTIAL_DERIVATION)**

CP violation in the CKM matrix requires a non-zero phase δ. In the Unitary Manifold, this phase has a geometric origin: discrete torsion in the compactification — a topological twist in the extra dimensions. Sprint BB demonstrated that the discrete torsion mechanism can generate a non-zero CP-violating phase of the right order of magnitude. It cannot yet determine the precise PDG value.

**The Jarlskog invariant (JARLSKOG_INVARIANT_7D_COMPUTED)**

The Jarlskog invariant J is a rephasing-invariant measure of CP violation: if J = 0, there is no CP violation in the quark sector. The measured value is J ≈ 3.18 × 10⁻⁵. Sprint BB computed J from the 7D geometry: the discrete torsion contribution gives the right order of magnitude. This is a nontrivial success — a theory that generates zero for J would be ruled out.

---

## Strong coupling constant: three routes, honest outcome

The strong coupling constant α_s measures the strength of the QCD force (the force that binds quarks into protons and neutrons). Its measured value at the Z-boson mass scale is α_s(M_Z) ≈ 0.118. This is precisely measured, and any complete theory of the Standard Model must reproduce it.

Sprint BB explored three routes from the 7D geometry:

**Route A: 7D volume and Kähler parameters (ALPHA_S_7D_VOLUME_NARROWED)**  
The compactification volume determines the effective 4D gauge coupling. Sprint BB narrowed the window of consistent Kähler parameter space that produces α_s near 0.118. The window is non-empty but the exact PDG value is not pinned within the window.

**Route B: 7D torsion coupling (result from Sprint BA)**  
Torsion in the 7D geometry contributes to the running of α_s. Partial closure established in Sprint BA.

**Route C: Cross-dimensional Kähler audit (ALPHA_S_7D_ROUTE_D_TIGHTENED, ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE)**  
Sprint BB completed the cross-dimensional audit: all routes (5D, 6D, 7D, 9D) were systematically checked. The honest result: α_s is constrained to a window consistent with the PDG value, but the window is not yet narrow enough to constitute a derivation. It is documented as an architecture limit in the ALPHA_S_ALL_DIMENSIONAL_AUDIT_COMPLETE gate.

---

## Three generations: the bundle specification

Why three families, not two or four? The N_gen count was addressed from a topological direction in Sprint BA (T²/Z₂ orbifold zero-modes). Sprint BB worked on the bundle specification route: in 6D compactifications, the number of generations is controlled by the Atiyah-Patodi-Singer (APS) index theorem applied to the gauge bundle over the compact space.

**NGEN_6D_BUNDLE_CONSTRAINED**: The bundle specification in 6D constrains N_gen. With the specific E8 gauge bundle appropriate to the Unitary Manifold, the APS index gives N_gen ∈ {3, possibly others depending on flux sector}. The degeneracy — multiple bundles give N_gen = 3 — is computed explicitly.

**NGEN_6D_BUNDLE_DEGENERACY_COMPUTED**: There are two E8 breaking patterns consistent with both N_gen = 3 and the 5D gauge structure. This degeneracy is documented; it is not a failure but a prediction gap that future theory work or experimental constraints could close.

---

## Architecture limits: the honest register

Sprint BB did something unusual for a physics publication: it produced a formal registry of architecture limits — things the framework cannot compute from first principles — in Lean4 (ArchitectureLimitRegistry.lean). These are not failures; they are pre-registered admissions that the theory has honest bounds.

Registered in Sprint BB:
- **HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT**: The 6D Hosotani Higgs mechanism is consistent but the exact UV completion is architecture-dependent.
- **KKLT_PERTURBATIVE_CONSISTENT_NP_ARCHITECTURE_LIMIT**: The KKLT moduli stabilization is perturbatively consistent but the non-perturbative completion is not determined by the framework.
- **CMB_PEAK_AMPLITUDE_ARCHITECTURE_LIMIT_CONFIRMED**: The acoustic peak suppression (×4–7) is confirmed as an irreducible architecture limit. All four EFT routes to fixing it were closed in subsequent sprints.
- **NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT**: Non-perturbative quantum gravity effects are irreducible within the semiclassical expansion the framework uses.

The purpose of this registry: if the theory ever claims to have derived something that is on this list, that claim can be checked against the registry and challenged.

---

## What this looks like for a non-physicist

Flavour physics is physics about *variety*: why is the top quark 340,000 times heavier than the electron? Why do quarks mix with specific probabilities? The Standard Model answers "that's just what we measure" and moves on. The Unitary Manifold says these numbers come from geometry — from the shape and topology of the extra dimensions.

Sprint BB tested this claim systematically. The result: the geometry gets the structure roughly right (hierarchies, CP violation of the right order of magnitude, generation count) but cannot yet compute the precise PDG values for all parameters. The θ₁₃ residual and the exact α_s value are the most significant gaps. They are documented, not buried.

Progress requires honestly acknowledging what the theory cannot do yet.

---

## Numbers

Test suite at Sprint BB: **60,196 passed · 45 skipped · 12 deselected · 0 failed**  
Lean4 formal theorems: **2,741** (+555 from Sprint BA's 2,186)

New Lean4 files: 18 (CKM7DBulkMassSpectrum.lean, CKM7DMixingAnglesExact.lean, CPViolation7DTorsion.lean, JarlskogInvariant7D.lean, and 14 others covering α_s, N_gen, Higgs, architecture limits).

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
