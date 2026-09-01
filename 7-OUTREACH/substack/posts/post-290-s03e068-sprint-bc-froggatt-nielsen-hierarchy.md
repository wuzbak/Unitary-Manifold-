# Froggatt-Nielsen: How Geometry Explains Why Particles Are Light

**Unitary Manifold — S03E068 · v27.0 · Sprint BC**

---

There is a pattern in the Standard Model that nobody put there on purpose. The particle masses — quarks, leptons, the three families — are not random. They follow a rough geometric progression: each generation is roughly 10–100 times heavier than the one before. The top quark is about 40,000 times heavier than the up quark. The muon is about 200 times heavier than the electron.

In 1979, Christopher Froggatt and Helaine Nielsen proposed an answer: there is a new global symmetry (a "flavour symmetry"), and particles have different charges under it. The Yukawa couplings that generate masses are suppressed by powers of a small parameter ε for each unit of this charge. This is the Froggatt-Nielsen (FN) mechanism — it explains hierarchies as the result of a symmetry, not a coincidence.

Sprint BC asks: where do the FN charges come from? In the Unitary Manifold, the answer is the 7D monodromy of the compactification. The charges are not inputs. They are geometric outputs.

---

## What monodromy is

When you wrap a field around the extra dimensions, it can come back to itself rotated by a phase. This rotation is the monodromy. Different fields have different monodromies depending on how they couple to the geometry. In 7D, the monodromy around the compactification cycle assigns each fermion a specific "winding charge." Sprint BC showed that these winding charges are exactly the FN charges needed to reproduce the observed fermion mass hierarchy.

This is a genuinely surprising result. The FN mechanism was invented as a phenomenological tool — a way to parametrize ignorance about why masses are hierarchical. Sprint BC gives it a geometric derivation.

**FN_CHARGE_ASSIGNMENT_FROM_7D_MONODROMY**: The FN charge of each quark and lepton generation is equal to its 7D monodromy winding number. This is a zero-parameter statement: given the geometry, the charges are fixed.

---

## The CKM matrix with FN corrections

Once you have the FN charges, you can write down the Yukawa texture — the pattern of which entries in the mass matrix are large, which are suppressed, and by how much. Sprint BC applied the FN charges from 7D monodromy to the CKM matrix computation.

**CKM_7D_FN_CORRECTION**: With FN corrections, the CKM angles improve. θ₁₂ and θ₂₃ come within 20% of PDG values. θ₁₃ improves from Sprint BB's partial residual but remains architecture-dependent.

**JARLSKOG_7D_NLO_FN**: The Jarlskog invariant J (the measure of CP violation) is computed at NLO with FN corrections. It lands within a factor of 2 of the PDG value J ≈ 3.18 × 10⁻⁵. This is labeled as partial because factor-of-2 is not the same as exact derivation.

---

## Neutrino mixing: the PMNS matrix

The equivalent of the CKM matrix for neutrinos is the PMNS matrix (Pontecorvo-Maki-Nakagawa-Sakata). It encodes how neutrino mass states mix with the flavour states (electron, muon, tau neutrinos) that appear in weak interactions. The mixing angles are strikingly different from the CKM matrix: where CKM angles are all small, the PMNS matrix has two large angles and one small one.

**PMNS_FN_BRIDGE**: Sprint BC extended the FN mechanism to the neutrino sector. The 7D monodromy assigns FN charges to lepton doublets as well as quark doublets. The resulting PMNS texture — the pattern of large and small entries — is qualitatively consistent with the observed pattern (two large angles, one Cabibbo-sized angle) without being tuned to match it precisely.

---

## N_gen = 3 from the bundle: closing a gap

Sprint BA established N_gen = 3 from the orbifold zero-mode count. Sprint BC added a second independent derivation using bundle data in 6D.

**NGEN_6D_BUNDLE_THIRD_FILTER**: A third filtering criterion on the gauge bundle — that it must carry the FN charges derived from 7D monodromy and be consistent with the APS index — reduces the set of consistent bundles substantially. After this filter, the bundles that give N_gen ≠ 3 are eliminated by additional consistency requirements. This is not a proof that N_gen = 3 uniquely from first principles, but it is a demonstration that the geometry strongly prefers 3 after all constraints are applied.

**E8_BREAKING_THIRD_FILTER**: The E8 gauge group must break to the Standard Model gauge group via the orbifold projection. Sprint BA found a two-fold degeneracy in E8 breaking patterns. Sprint BC's third filter reduces this to a smaller set.

---

## α_s volume pinning

The strong coupling constant depends on the compactification volume. Sprint BC added a volume pinning step:

**ALPHA_S_M7_VOL_PINNING**: The 7D volume must satisfy both (a) a lower bound from swampland distance conjecture, (b) an upper bound from the weak gravity conjecture applied to KK modes, and (c) consistency with the Kähler cone. Combining these three constraints narrows the volume window. The resulting α_s window contains the PDG value 0.118. This is progress: the PDG value is not excluded, and the window is consistent.

---

## Inflation: NLO audit

**TCC_EFOLD_NLO_AUDIT**: The Trans-Planckian Censorship Conjecture (TCC) imposes a bound on the number of e-folds of inflation: too many e-folds would push inflation into the regime where quantum gravity corrections become uncontrollable. Sprint BC audited the e-fold count at next-to-leading order in the KK tower expansion. The result: the NLO correction shifts the e-fold bound slightly but does not violate it. The inflationary sector of the framework remains consistent with the TCC.

---

## Scale of this sprint

Sprint BC was a large sprint: 24 pillars (887–910), Lean4 +435 theorems (from 2,741 to 3,176). The Lean4 work included three major files:
- **FNHierarchyTheorems.lean**: The formal derivation of FN charges from 7D monodromy, and the Yukawa texture theorems.
- **BundleDegeneracyResolution.lean**: The resolution of the E8 breaking degeneracy using the third-filter criterion.
- **SprintBCMasterBridge.lean**: The master bridge connecting all Sprint BC results into a single coherent set of formal propositions.

The test suite at Sprint BC: **60,848 passed · 45 skipped · 12 deselected · 0 failed**.

---

## Why this matters beyond the math

The Standard Model has 19 free parameters. (Or 26 if you include neutrino masses and mixing.) These parameters are not derived from any deeper principle in the Standard Model itself — they are measured. If the Unitary Manifold can derive them from the geometry of extra dimensions, that would be a significant unification: replacing 19+ arbitrary inputs with a handful of geometric parameters.

Sprint BC does not achieve this completely. What it does is show that the *structure* of the parameter pattern (the hierarchical organization, the FN charge assignments, the distinction between large PMNS angles and small CKM angles) has a geometric explanation. The exact numerical values are partially computed. The honest status of each is documented.

This is how science should work: claim precisely what you can show, and mark clearly what you cannot.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
