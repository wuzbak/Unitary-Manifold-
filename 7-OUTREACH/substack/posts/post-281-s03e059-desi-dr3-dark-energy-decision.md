# DESI DR3: The Dark Energy Decision — What We're Waiting For and Why

*Post 281 of the Unitary Manifold series — Series 3, Episode 59.*
*Epistemic category: **FALSIFICATION WINDOW** — DESI DR3 preregistered decision protocol.*
*v20.5, 2026-08-01.*

---

## The Stakes

The Unitary Manifold predicts **w₀ = −1, wₐ = 0** — the cosmological constant.

This is not a free parameter. The prediction follows from the KK geometry: the radion φ is stabilized at the FTUM fixed point, and a frozen radion produces a cosmological constant with no time variation. There is no mechanism within 5D RS1 that can produce a rolling dark energy without destroying the RS1 hierarchy (Pillar 301 proves that the required fine-tuning would be ε_GW ~ 10⁻⁸⁸ — so extreme as to be physically meaningless).

DESI is measuring exactly this. And DESI has already published evidence suggesting wₐ ≠ 0.

---

## Where We Stand: The DR2 Signal

DESI Data Release 2 (2025) reported a 2.30σ tension with wₐ = 0 in the CPL (Chevallier-Polarski-Linder) parameterization:

```
w₀ = −0.55 ± 0.39    (CPL fit)
wₐ = −1.32 ± 0.72    (CPL fit, combined DESI+CMB+SNe)
```

Two important clarifications:

**First**, the 2.30σ tension is after CPL correction. The raw DR2 signal without CMB or SNe combination was 2.07σ to 2.82σ depending on the dataset combination. The canonical corrected number is 2.30σ (Pillar 428 correction, v14.2).

**Second**, 2.30σ is below the 3.0σ falsification threshold. Per the UM claim ledger policy, a claim is not FALSIFIED until an experimental result exceeds 3.0σ against it. At 2.30σ, the DESI signal is TENSION — significant and monitored, but not yet falsifying.

The wₐ = 0 architecture limit is CERTIFIED — meaning it is irreducible within the current 5D framework, not a matter of parameter adjustment. If DESI crosses 3σ, the framework requires a structural extension.

---

## The 3-Branch Decision Protocol (Pillar 631)

When DESI DR3 publishes (expected late 2026), the framework executes a preregistered 3-branch protocol:

### Branch 1: PASS (DESI DR3 tension ≤ 2.3σ)

If DR3 tension is equal to or below the DR2 corrected value, the current architecture limit is sufficient. wₐ = 0 remains consistent with DESI. The UM prediction is not under increased pressure.

Action: Update the tension register. No physics change.

### Branch 2: TENSION_INCREASED (2.3σ < DESI DR3 ≤ 3.0σ)

If DR3 tension increases but stays below 3.0σ, the architecture limit is under growing pressure. The rolling-radion extension (6D sector: radion coupled to Gauss-Bonnet curvature) is activated as an adjacent-track probe.

Action: Execute rolling-radion 6D Phase 2 (documented in Pillar 631 deliverables). Update tension register. Communicate the increased pressure honestly.

### Branch 3: FALSIFIED (DESI DR3 > 3.0σ at 95% CL)

If DR3 crosses 3.0σ, wₐ = 0 is formally FALSIFIED within the 5D-EFT architecture. The framework requires structural revision: either a new stabilization mechanism for the radion or a different compactification geometry.

Action: Issue a formal falsification notice within 72 hours. Document in FALLIBILITY.md. Activate the 6D/11D extension programme as the formal successor framework (not a fix — a genuine structural change). The framework derivation coverage for the wₐ prediction drops to FALSIFIED.

This is not hypothetical planning. The protocol is machine-executable. The tripwire condition (`desi_dr3_wA_tension > 3.0`) is coded in `src/core/pillar486_desi_dr3_final_prep.py`.

---

## Why wₐ = 0 Is an Architecture Limit

It is worth being precise about what "architecture limit" means here, because it is not the same as "we can't explain it yet."

An architecture limit is a prediction that follows necessarily from the framework's core structure and cannot be relaxed without changing the structure. In this case:

1. The FTUM fixed point requires a frozen radion: dφ/dt = 0 at the attractor.
2. A frozen radion produces a time-independent vacuum energy: Λ = const.
3. A constant vacuum energy produces wₐ = 0 exactly.

Step 3 → Step 1 is a logical chain with no free parameters. There is no lever inside 5D RS1 that can be adjusted to produce wₐ ≠ 0 while preserving the FTUM attractor. The Pillar 301 proof showed explicitly that attempts to add rolling dynamics require the Gauss-Bonnet coefficient to be fine-tuned to one part in 10⁸⁸.

This means: if DESI is right and wₐ ≠ 0, the 5D RS1 framework is wrong at the level of its stabilization mechanism. Not wrong in a detail — wrong in a structural claim. The honest response is to say so and extend the framework.

---

## Sprint I: The Preregistration Infrastructure

Sprint I (Pillars 608–612, v20.5) hardened the experimental response infrastructure ahead of DR3:

- **Pillar 608**: 3-branch DESI DR3 routing drill — tested the decision logic computationally
- **Pillar 609**: Euclid Year 1 BAO cross-check protocol — DESI is not the only dark energy probe; Euclid's independent measurement will be equally important
- **Pillar 610**: SPHEREx f_NL pre-analysis update — the f_NL prediction (Post 281b) is independent of wₐ; both can be tested in the same DESI/SPHEREx window
- **Pillar 611**: Hyper-Kamiokande Run 3 proton decay — τ > 1.6 × 10³⁵ yr is now consistent with UM's KK-GUT prediction, which bounds m_G_KK ≥ 5.0 TeV

The test suite for this sprint added ~120 tests focused on the branching logic — ensuring that the correct verdict is computed programmatically when DR3 data is ingested.

---

## What DESI DR3 Timing Means for Us

DESI's DR3 is expected in late 2026. The five-year survey (DR5) is projected for 2027–2028.

The UM's position:
- At DR2 (2.30σ): TENSION — acknowledged, documented, architecture limit certified
- At DR3 (expected 2026): decision tree executes
- At DR5 (2027–2028): if tension persists at >3σ, the falsification is robust

The experimental calendar is tighter than it appears. We are within ~12 months of a potentially decisive DESI result. This is not 2032 (LiteBIRD). This is now.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
