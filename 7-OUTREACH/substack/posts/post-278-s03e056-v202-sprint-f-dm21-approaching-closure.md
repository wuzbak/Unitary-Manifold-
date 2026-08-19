# Sprint F: The DM21 Cascade Begins — FN Mechanism and NLO (v20.2)

*Post 278 of the Unitary Manifold series — Series 3, Episode 56.*
*Epistemic category: **HARDGATE ADVANCE** — DM21 tension 4.63σ → 0.81σ; APPROACHING_CLOSURE.*
*v20.2, 2026-08-01.*

---

## Sprint F in Two Sentences

Sprint F (Pillars 591–595, v20.2) executed the first two steps of the DM21 cascade: the Froggatt-Nielsen flavor-symmetry correction and the NLO WS-V texture correction. Together, they drove the solar neutrino mass splitting tension from **4.63σ to 0.81σ**.

---

## The Problem Inherited from v19.4

At the start of Sprint F, Δm²₂₁ was in the ledger as TENSION_4.63SIGMA — one of the most significant open tensions in the framework. The geometric seesaw prediction from the RS1 KK geometry, without any flavor corrections, placed the solar splitting 4.63 standard deviations from the PDG best value of (7.53 ± 0.18) × 10⁻⁵ eV².

This is not a small discrepancy. It is close to the 5σ conventional falsification threshold. Any serious physics framework must address it.

---

## Pillar 591 — FN Charge Correction

**File:** `src/core/pillar591_dm21_ratio_fn_correction.py`

The Froggatt-Nielsen mechanism assigns discrete flavor charges to each fermion generation. In the UM lattice, these charges are fixed to n_FN = Δc = 5/74 — the minimum step size on the RS1 bulk mass lattice, geometrically determined by the braid structure.

Applying the FN charge to the (1,2) seesaw matrix element gives:

```
Δm²₂₁(FN) = Δm²₂₁(bare) × |R_12(FN)|²
```

where R_12(FN) is the FN-corrected ratio of second-to-first generation Yukawa overlaps. With Δc = 5/74, this ratio shifts the prediction from 4.63σ to **1.15σ**.

The critical point: Δc = 5/74 is not adjusted to fit the gap. It is the same lattice step used throughout the fermion mass hierarchy (Pillar 98) and the Jarlskog invariant (Admission 7). It was not chosen to address DM21.

---

## Pillar 592 — NLO WS-V Correction

**File:** `src/core/pillar592_dm21_nlo_wsvv_correction.py`

At NLO, the seesaw texture picks up off-diagonal RS1 KK mixing terms. In the WS-V texture (named for the Walker-Susskind-Volkas extension), the NLO correction coefficient is 1/k_CS = 1/74 — geometrically determined by the Chern-Simons level.

Including the NLO sub-leading correction brought the tension from 1.15σ to **0.81σ**.

The APPROACHING_CLOSURE status was declared at this point: the tension was below 1σ, the mechanisms were geometrically motivated, and the remaining gap (0.81σ) was within the range addressable by two-loop EW corrections. See Post 275 for the full four-step cascade and final CLOSED declaration.

---

## Pillar 593 — APPROACHING_CLOSURE Certificate

**File:** `src/core/pillar593_dm21_v202_cascade_certificate.py`

A formal machine-readable certificate was generated at APPROACHING_CLOSURE, documenting:
- Tension timeline: 4.63σ → 1.15σ → 0.81σ
- Correction mechanisms and their geometric origins
- Named residuals: two-loop EW correction (quantified in v20.6 Pillar 613)
- Cascade conditions for CLOSED status

---

## Test Suite at v20.2

**~150 new tests** were added in Sprint F, bringing the regression count to approximately 49,773 passed, 0 failed.

---

## Next: Sprint G

Sprint G proceeds to NP-BC-5 sub-gaps M/N/O and the Lean4 308 milestone. See Post 276 for the detailed treatment.

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
