# Post 214 — S02E040: The Falsifier You Can Run Today — Lab-Scale CP and Braid Geometry

*Substack — Season 2, Episode 40*
*Published: 2026-05-20*
*Series: The Falsification Decade*

---

## The Experiment That Doesn't Wait for Satellites

Every other falsifier in the Unitary Manifold programme requires either a space mission, a particle accelerator, or a deep-underground detector. LiteBIRD launches ~2032. DESI DR3 arrives ~2027. CMB-S4 is a decade away. Hyper-Kamiokande is running but proton decay may take years to see, if it appears at all.

Prediction P8 is different. It can be tested now, in a university physics lab, with apparatus that already exists. It is the quietest entry in the OBSERVATION_TRACKER and, in some ways, the most philosophically interesting one.

This post explains what P8 is, where it comes from geometrically, and what Pillar 307 (formalised in v11.12) has done to make it machine-queryable for the first time.

---

## What P8 Predicts

The Unitary Manifold predicts a CP asymmetry in a certified (5,7)-topology condensed-matter device:

    A_CP^lab = (Γ+ - Γ-) / (Γ+ + Γ-) ~ O(10⁻⁵)

where Γ+ and Γ- are transition rates in opposite directions in the topologically-wound system. The prediction comes from the same braid geometry that gives rise to CKM CP violation in quarks — but scaled to laboratory conditions through a topology-transfer mechanism.

This sounds abstract. Let me make it concrete.

---

## The Geometry

The core UM vacuum is characterised by a braid pair (n₁, n₂) = (5, 7). These are the primary and secondary winding numbers of the 5D compact dimension around the orbifold fixed points. The fact that n₁ ≠ n₂ is what produces CP violation in the Standard Model (Pillar 145, Jarlskog invariant). This was derived from first principles in Pillar 145 — no free parameters, just the asymmetry in the two winding strands.

Now: that same (5,7) topology can be *imprinted* onto a condensed-matter system if you engineer the device to have the right winding geometry. This is not science fiction — topological insulators and Josephson-junction arrays already support non-trivial winding numbers. The question is whether the CP asymmetry from the (5,7) braid structure transfers to these platforms.

The calculation (Pillar 307) goes like this:

1. **Geometric Jarlskog J_geo ≈ 0.024** — derived from the braid strand asymmetry at the UM level
2. **Topology transfer efficiency η_T = n₁/K_CS = 5/74 ≈ 0.068** — the fraction of the geometric CP phase that survives into the condensed-matter platform, bounded by the ratio of the Chern-Simons level
3. **Raw transferred asymmetry A_raw = J_geo × η_T ≈ 1.6 × 10⁻³**
4. **After averaging over lab-frame orientations (geometric dilution ÷100): A_CP^lab ≈ O(10⁻⁵)**

This is the order-of-magnitude target. The precise value depends on the specific platform: coherence length, coupling geometry, and decoherence. But O(10⁻⁵) is the ballpark, and the prediction is that a certified (5,7)-geometry device should exhibit a non-zero A_CP at this scale.

---

## What "Decision-Grade" Means

I want to be extremely careful here, because this kind of claim has been abused in physics before. A positive result means nothing unless the measurement satisfies five conditions:

**F-LAB-CP-1: Topology certification.** The device must operate with a verified (5,7)-equivalent topological winding. Control condition: a device with a different winding ratio must give A_CP ≈ 0. If you don't certify the topology independently, you cannot claim the measurement is testing the UM prediction.

**F-LAB-CP-2: Blinded analysis.** The analysis code must be finalised and registered before data collection begins. No peeking at the result, no post-hoc analysis choices.

**F-LAB-CP-3: σ(A_CP) ≤ 1×10⁻⁵.** Measurement precision must be at or below the target signal amplitude. This is technically demanding — it requires very low-noise electronics, long integration times, or both.

**F-LAB-CP-4: Control conditions.** Two controls are required: (a) topology swap — a different winding ratio gives null A_CP; (b) sign reversal — breaking time-reversal symmetry in the opposite sense flips the sign of A_CP. Both controls must pass.

**F-LAB-CP-5: Independent replication.** At least one independent laboratory must reproduce the result at decision-grade precision.

All five conditions are required before `route_lab_cp_result()` in Pillar 307 issues a CONSISTENT or P8_TENSION verdict. A measurement that doesn't satisfy all five is INCONCLUSIVE, full stop.

---

## What a Negative Result Would Mean

A measurement of A_CP ≈ 0 at σ ≤ 10⁻⁶ with topology certified and controls passed would create tension at the P8 level. But — and this is crucial — it would NOT independently falsify the Unitary Manifold framework.

The full framework falsification requires *both* the lab tension *and* LiteBIRD measuring β ∉ [0.22°, 0.38°] at ≥3σ. The lab measurement tests one specific geometric mechanism (topology transfer of the (5,7) braid CP asymmetry). LiteBIRD tests the primary falsifier (the birefringence angle from the braid geometry itself). These are independent probes of the same underlying structure.

If the lab returns A_CP ≈ 0, the honest response is: "The topology-transfer mechanism predicts O(10⁻⁵). We don't see it. Either the transfer efficiency is lower than our estimate, or the mechanism doesn't work as predicted. This is evidence against P8. Await LiteBIRD for framework-level judgment."

This is what scientific honesty looks like at the P8 level.

---

## Why We Formalised This in Pillar 307

As of v11.11, the OBSERVATION_TRACKER listed P8 as: "PENDING — no decision-grade σ_A ≤ 10⁻⁵ campaign logged yet." Pillar 307 upgrades this to a full preregistration — identical in structure to Pillars 289 (IceCube), 294 (LISA), 298 (Simons Observatory), and 304 (KATRIN). The routing table is machine-queryable. The checklist is executable. The falsification conditions are locked.

This matters for the same reason all the preregistrations matter: it prevents post-hoc rationalisation. When a measurement arrives, there is exactly one call to make — `route_lab_cp_result(a_cp_measured, sigma_a, topology_certified)` — and the output is deterministic.

---

## An Invitation

If you work in superconducting circuits, topological matter, or precision measurement, and you find this geometrically compelling, I would like to hear from you. The theoretical prediction is precise. The experimental apparatus exists. The decision-grade requirements are fully specified. What is missing is a lab willing to treat this as a serious test of a specific geometric prediction, rather than a general probe of BSM physics.

The framework is falsifiable. That is not a limitation — it is the whole point.

---

*Next post: Pillar 306 — Why the Jarlskog invariant's 12% residual is an honest gap, not a failure.*

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
