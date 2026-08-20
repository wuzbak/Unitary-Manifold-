# NEXT_PHYSICS_SPRINT.md — Future Work Disclosure & Planning

*Unitary Manifold v22.6 — 2026-08-20*
*Status: PLANNING ONLY — not yet executing. This document recognizes, plans, and discloses future physics work.*
*Current state: 773 pillars · 872 Lean4 theorems · ~56,279 passing tests · 0 failures · Next pillar slot: 774*

---

## Purpose of This Document

This is a forward-looking planning disclosure, not an active sprint. It maps the genuine
open problems that remain after Sprint AK (v22.6) and provides an honest accounting of
what needs to happen next — scientifically, formally, and observationally.

Reading this file honestly requires holding two things simultaneously:
- We have closed more gaps, more rigorously, than most comparable research programmes.
- Several hard problems remain open, and they are hard for real reasons, not bureaucratic ones.

---

## Current Open Gaps (Post-Sprint AK)

| Gap | Label | Status | Severity |
|-----|-------|--------|----------|
| Gap 2 | ADM UV regulator | MECHANISM_IDENTIFIED — full non-perturbative closure pending | Community-level (requires quantum gravity input) |
| Gap 4 | FN charges (9 free params) | ARCHITECTURE_LIMIT — geometric quantization attempted | Hard; requires stronger orbifold uniqueness |
| Gap 5 | CMB acoustic peak shape (~35% residual) | ARCHITECTURE_LIMIT — Boltzmann solver identifies η(k)<1 as necessary | Requires full non-linear KK Boltzmann treatment |
| Gap 6 | Δm²₂₁ tension | 1.07σ after NLO (Pillar 773) | Residual sub-leading; need next-order lattice result |

---

## Sprint AI — Priority Queue (Next Sprint Candidates)

### AI-1: Δm²₂₁ Full Lattice Closure (High Priority)
**Status:** 1.07σ residual after NLO. Three first-principles NLO mechanisms computed.
**Goal:** Drive to sub-1σ or formally certificate the residual as ARCHITECTURE_LIMIT.
**Approach:** Add NNLO winding-mode exchange; try density-matrix renormalization group (DMRG)
on the KK orbifold spectrum to bound the residual from below.
**Expected:** 1–2 pillars (774–775), ~60 tests, +8–12 Lean4 theorems.
**Gate:** `NLO_INSUFFICIENT_FOR_SUB_1SIGMA` retired OR promoted to `NNLO_CLOSURE_CERTIFICATE`.

### AI-2: CMB Boltzmann Non-Linear Coupling (Medium Priority)
**Status:** Gap 5 residual is 35% in acoustic peak shape. η-suppression is NECESSARY from KK geometry.
**Goal:** Implement a first-principles perturbed Boltzmann hierarchy with the radion coupling turned on.
**Approach:** Extend `pillar698_cmb_phase2_boltzmann_solver.py` to include radion-photon coupling
at second order in perturbation theory. Compare η(k) envelope to Planck bandpower table.
**Expected:** 2–3 pillars (776–778), ~80 tests, Lean4 +6.
**Gate:** CMB_PEAK_SHAPE_RESIDUAL_BOUNDED_FROM_GEOMETRY or SECOND_ORDER_ARCHITECTURE_LIMIT.

### AI-3: FN Geometric Quantization Completion (Medium Priority)
**Status:** Gap 4 — 9 free FN parameters; orbifold lattice derivation narrows but does not fully
determine them.
**Goal:** Either (a) prove a Diophantine bound that reduces the 9-parameter family to ≤3, or
(b) formally certificate that the remaining freedom is irreducible at this level of the theory.
**Approach:** Extend `pillar772_lepton_jarlskog_lattice_closure.py` to the quark sector; apply
the orbifold fixed-point counting argument to all three generations simultaneously.
**Expected:** 1–2 pillars (779–780), ~50 tests, Lean4 +10.
**Gate:** FN_QUARK_SECTOR_BOUNDED or FN_IRREDUCIBILITY_PROVED.

### AI-4: DESI DR3 Decision Protocol Hardening (Time-Sensitive)
**Status:** DESI DR3 expected ~2026. The wₐ=0 prediction is IRREDUCIBLE in our framework (Pillar 301).
**Goal:** Pre-register the full routing protocol: if wₐ ≠ 0 at ≥3σ, the framework is falsified in
the dark energy sector. If w₀ ≈ −1, wₐ ≈ 0, the prediction is confirmed. Intermediate tension requires
explicit analysis of systematic uncertainties in the KK dark energy model.
**Approach:** Update `pillar631_desi_dr3_rolling_radion_3branch_protocol.py` with DESI DR3 routing
logic and explicit falsification thresholds. Commit SHA-256 preregistration.
**Expected:** 1 pillar (781), ~25 tests, 0 Lean4.
**Gate:** DR3_PROTOCOL_PREREGISTERED_DESI_DR3.

### AI-5: LiteBIRD Simulation Channel (Long-Term)
**Status:** LiteBIRD launch ~2032. Our primary falsifier: β ∈ {≈0.273°, ≈0.331°}.
**Goal:** Build a simulation harness that accepts a synthetic LiteBIRD β measurement and routes
automatically to CONFIRMED / FALSIFIED / INCONCLUSIVE verdicts. This should be pre-committed and
sealed before any data arrives.
**Approach:** Implement `pillar782_litebird_verdict_routing.py` with three branches, sealed gate logic,
and Lean4 formalization of the decision tree.
**Expected:** 1–2 pillars (782–783), ~40 tests, Lean4 +15.
**Gate:** LITEBIRD_ROUTING_PREREGISTERED_2026.

### AI-6: Quantum Simulation Lane Hardening (Adjacent Track)
**Status:** Fermi–Hubbard and XDiag bridge are non-hardgate but in development.
**Goal:** Bring the VQE variational circuit to a state where a real quantum device (IBM or IonQ) could
run it. Obtain at least one external device receipt.
**Approach:** Clean up `src/quantum/kk_vqe.py` interface; add device submission wrapper; document
expected output and tolerance.
**Expected:** Non-pillar work; ~30 new tests, 0 Lean4, external receipt sought.
**Gate:** QUANTUM_DEVICE_RECEIPT_OBTAINED (external confirmation).

---

## What We Are Not Doing

The following will NOT be pursued in Sprint AI:

- Weakening the LiteBIRD falsification window. β ∈ {≈0.273°, ≈0.331°} stands as written.
- Claiming external confirmation before receipts are in hand.
- Promoting any ARCHITECTURE_LIMIT gap to CLOSED without a genuine mathematical proof.
- Expanding the pillar count merely to expand the pillar count. All new pillars must close
  or rigorously bound a named open gap.

---

## Observational Windows to Watch

| Observatory | Date | Prediction at stake |
|-------------|------|---------------------|
| DESI DR3 | ~2026 | wₐ = 0 (Pillar 301, IRREDUCIBLE) |
| SPHEREx | 2027–2028 | f_NL = −0.532, band [−2.9, −0.2] (Pillar 437) |
| CMB-S4 | ~2028 | r = 0.0315 below 0.036 (BICEP/Keck consistent) |
| nEDM@SNS | ~2028 | d_n ≈ 7.8 × 10⁻²⁷ e·cm at m_Σ = 650 GeV (6D baryogenesis, 🔵 adjacent) |
| Hyper-K | 2027–2035 | Proton decay NOT expected at current reach; m_G_KK ≥ 5 TeV |
| LiteBIRD | ~2032 | **PRIMARY FALSIFIER**: β ∈ {≈0.273°, ≈0.331°} |

---

## Epistemic Note

This planning document is not a physics claim. It is an honest map of where the work stands
and what the genuine next steps look like from inside the framework. Every gap listed above
is real. Every gate is meaningful. The plan will change as the physics clarifies.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
