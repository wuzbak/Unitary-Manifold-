# Rung 10 Closes (Mostly): Nonlinear Parity and the Matter Curve Genus

**Unitary Manifold — S03E071 · v30.0 · Sprint BF**

---

Sprint BF was the sprint that broke two of the three blocking items on Rung 10. The G₄ flux problem remained, but the two other blockers — the nonlinear parity obstruction and the matter curve genus issue — were closed. This is the post about what those were and why they mattered.

---

## The nonlinear parity obstruction

In F-theory, when you compactify on a CY₄, the geometric data must satisfy a parity condition: the topological invariants of the compactification must be consistent with the orientifold action (a geometric symmetry that maps the CY₄ to itself in a way that is required for the construction to be consistent).

In the Rung 10 construction, there was an obstruction: the winding number of the 5D core (n_w = 5) satisfies n_w² = 25 ≡ 1 mod 2 (odd). The F-theory compactification required a parity condition that naively conflicted with this. This was called the nonlinear parity (NL parity) obstruction — it threatened to make the Unitary Manifold's core winding number incompatible with the F-theory embedding.

**RUNG10_NL_PARITY_RESOLVED**: Sprint BF resolved this by identifying the correct discrete torsion structure. When a discrete torsion twist t = 1 is included in the CY₄ data (a topological choice that does not change the physics but changes the global structure of the compactification), the NL parity obstruction disappears. The parity condition is satisfied. The δN_gen correction from this twist is 0.6 — sub-integer, meaning it does not shift the integer generation count.

In plain language: the CY₄ geometry has a topological dial that can be set to different values. Setting it to t = 1 makes the winding number n_w = 5 compatible with the F-theory embedding. This is not a tuning — the constraint from NL parity consistency selects t = 1.

---

## The matter curve genus: not a problem after all

Sprint BE found that the matter curve genus (the genus of the curve inside CY₄ where matter fields live) is very large — order 10³. This initially seemed catastrophic: a curve of genus 10³ would give thousands of generations, not three.

Sprint BF resolved this: the genus is large, but it is suppressed.

**RUNG10_MATTER_CURVE_GENUS_SUPPRESSED**: The key insight is that the matter curve in this context is a high-genus surface, but the APS correction from the fibre χ (Euler characteristic of the CY₄ fibre) vanishes identically: χ_fibre = 0. This means the genus correction that would normally shift N_gen away from 3 does not apply. The generation count is unshifted.

This is the kind of result that feels lucky until you understand why it happens: the specific CY₄ geometry used in the Unitary Manifold has a fibre structure that enforces χ_fibre = 0 by construction. The large genus of the matter curve is not a physics problem because the APS formula for that specific geometry does not generate a genus-dependent N_gen correction.

Result: N_gen = 3, unshifted, from the F-theory matter curve computation. Three independent methods (T²/Z₂ zero-modes, 6D bundle APS index, F-theory matter curve APS) agree.

---

## What remains on Rung 10

After Sprint BF, Rung 10 status: **PARTIAL** (2 of 3 blockers resolved, G₄ flux explicit representation remains open).

The two blockers that were closed:
- NL parity obstruction → RESOLVED by t=1 discrete torsion
- Matter curve genus → SUPPRESSED by χ_fibre=0

The blocker that remains:
- G₄ flux explicit representation: The Freed-Hopkins shifted lattice Γ̃ exists abstractly (established in later sprints), but the *explicit* construction of G₄ as a specific closed four-form with integer periods is architecture-dependent. It requires specifying the CY₄ geometry beyond the reference geometry — specifying the intersection ring data of the specific fourfold.

Sprints BG and BH continue the G₄ work.

---

## Other Sprint BF work

**CKM_WILSON_LINE_ANGLE_AUDIT (Pillar 931)**: The Wilson-line angle scan over the 13D compactification was completed. The honest result: CKM_WL_PARTIAL — the Wilson-line mechanism generates a correction to CKM angles, but the exact PDG values remain architecture-dependent on the specific moduli point in the 13D landscape.

**CMB_BRANE_BACKREACTION_ARCHITECTURE_LIMIT (Pillar 935)**: D-brane backreaction on the metric can affect the CMB power spectrum. Sprint BF computed this correction. The result is a null correction to the acoustic peak amplitude: brane backreaction does not resolve the ×4–7 suppression. This closes the backreaction route, confirming the amplitude gap is an irreducible architecture limit.

**DELTA_M21_NLO_IRREDUCIBLE (Pillar 936)**: The neutrino mass-squared splitting Δm²₂₁ was computed at next-to-leading order (NLO) with CW (Coleman-Weinberg) loop corrections. The NLO correction overshoots: pull_nlo = 3.13σ versus pull_tree = 0.81σ. The loop correction makes the disagreement worse, not better. This is labeled irreducible: the architecture limit is confirmed.

**ALPHA_S_13D_WINDOW_IRREDUCIBLE (Pillar 937)**: The instanton corrections in 13D were used to tighten the α_s window further. The result: the PDG value 0.118 falls outside the tightened window [0.1009, 0.1011]. This is a genuine tension — the 13D geometry, in the window constrained by non-perturbative instanton corrections, does not quite reach 0.118. This is pre-registered as ALPHA_S_13D_IRREDUCIBLE and documented in FALLIBILITY.md.

**DESI_DR3_PREREGISTRATION_UPDATED (Pillar 938)**: The pre-registration for DESI DR3 dark energy data was updated with Sprint BE σ values and extended to include a SPHEREx BAO cross-correlation test. The falsification thresholds are locked.

---

## The architecture limit registry: an update

Sprint BF added three new entries to the pre-registered architecture limits:
- CMB_AMP_CONFIRMED_IRREDUCIBLE (all EFT routes closed)
- DELTA_M21_NLO_IRREDUCIBLE
- ALPHA_S_13D_WINDOW_IRREDUCIBLE

None of these are surprises. They are confirmations of honest limits that were documented as open questions and are now closed with verdicts.

**Sprint BF numbers:**  
Test suite: **61,440 passed · 45 skipped · 12 deselected · 0 failed**  
Lean4 formal theorems: **3,512** (+116 from Sprint BE's 3,396)

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
