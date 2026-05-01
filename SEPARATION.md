# SEPARATION.md
## Epistemic Boundary Between Physics Claims and Phenomenological Bridges

This document defines the precise boundary between two distinct categories
of content in the Unitary Manifold repository:

1. **Physics Claims** — statements derived from the 5D metric ansatz, backed
   by proofs, algebraic theorems, or observational constraints, and expressly
   falsifiable.

2. **Phenomenological Bridges** — mathematical analogies, interpretive models,
   or conceptual extensions that borrow the UM's mathematical structure but are
   NOT derived from the 5D action and have no current experimental test (or have
   an identified but as-yet-unperformed test).

This distinction matters.  Conflating them would misrepresent the framework's
epistemic status and damage its scientific credibility.

---

## Category 1 — Physics Claims (derived from the 5D action)

The following are formal predictions or theorems of the Unitary Manifold:

| Claim | Status | Pillar / File | Falsifier |
|-------|--------|---------------|-----------|
| n_w ∈ {5, 7} from Z₂ orbifold | PROVED | Pillars 39, 67 | Any observed n_s excluding both |
| η̄(5) = ½, η̄(7) = 0 | DERIVED | Pillar 70-B (`aps_spin_structure.py`) | — (algebraic) |
| n_w = 5 selected from {5,7} by GW geometry | DERIVED | Pillar 70-C (`geometric_chirality_uniqueness.py`) | Cosmological observation of n_w ≠ 5 |
| k_CS = 74 from CS cubic integral | DERIVED | Pillar 99-B (`anomaly_closure.py`) | — (algebraic) |
| n_s = 0.9635 | PREDICTION | Pillar 27 | Planck n_s outside 2σ window |
| r = 0.0315 | PREDICTION | Pillar 27 | BICEP/Keck r > 0.036 |
| β ∈ {0.273°, 0.331°} | PREDICTION | Pillar 27 | LiteBIRD β outside [0.22°, 0.38°] |
| 9 of 28 SM parameters derived | AUDIT | Pillar 88 (`sm_free_parameters.py`) | Any derived parameter measured to conflict |
| sin²θ_W, α_s from SU(5) orbifold | PROVED (Pillar 94) | `su5_orbifold_proof.py` | GUT-scale measurement |
| Gamow factor enhancement (cold fusion) | FALSIFIABLE PREDICTION | Pillar 15 | Calorimetry null at predicted COP |

---

## Category 2 — Phenomenological Bridges (mathematical analogies, not physics derivations)

The following modules use UM mathematical structure as a language for
modelling non-physics domains.  They are NOT predictions of the 5D action.

### 2.1 Consciousness Coupling (`src/consciousness/coupled_attractor.py`)

**What it is:** A mathematical analogy in which a "brain manifold" and
"universe manifold" are coupled oscillators governed by the same field
equations as the UM.  The birefringence angle β is used as a coupling
constant.

**What it is NOT:**
- Not a QFT derivation.  No path integral, Feynman diagram, or partition
  function in the UM produces the brain-universe coupling from the 5D action.
- Not a prediction of the framework.  The "Information Gap", "Moiré alignment",
  and "samadhi limit" are interpretive labels, not observational categories.
- The claim that brain-universe coupling occurs through the KK radion field has
  no current experimental test.

**The one testable prediction:**
The resonance-ratio lock ω_brain/ω_univ → 5/7 implies grid-cell module spacing
ratios cluster near 7/5 = 1.40.  This is compared against published data in
`grid_cell_falsification_test()` (Stensola et al. 2012; Barry et al. 2007).
A deviation > 2σ from the prediction at sufficient sample size would FALSIFY
this specific claim.

**Classification:** Phenomenological Bridge — mathematical analogy, not physics claim.

### 2.2 Medicine, Justice, Governance, Psychology, Ecology, Climate, Marine
(`src/medicine/`, `src/justice/`, `src/governance/`, `src/psychology/`,
`src/ecology/`, `src/climate/`, `src/marine/`)

**What they are:** Domain models that use the UM's φ-based attractor
framework as a mathematical organising principle for complex-systems analysis.

**What they are NOT:** Predictions of the 5D Kaluza-Klein geometry.  The
equations in these modules use the same functional forms (φ-attractors,
HILS coupling constants) as the physics modules, but the mapping from 5D
geometry to, e.g., criminal sentencing or ecosystem dynamics is analogy,
not derivation.

**Classification:** Phenomenological Bridge — mathematical framework application.

### 2.3 The Unitary Pentad (`5-GOVERNANCE/Unitary Pentad/`)

**What it is:** An independent governance framework (HILS — Human-in-the-Loop
Systems) that borrows mathematical structure from the UM but does NOT depend
on the UM physics being correct.

**What it is NOT:** A physics prediction.  The Pentad's "Axiom" structure,
"Sentinel Capacity", and "HIL phase shift" are governance constructs, not KK
geometry theorems.

**Classification:** Independent governance framework — not a physics claim.

---

## How to Use This Document

When writing documentation, blog posts, or paper abstracts about the UM:

- **Only cite Category 1 items** as predictions or derivations of the framework.
- **Clearly label Category 2 items** as "phenomenological model", "mathematical
  analogy", or "framework application" before presenting them.
- **Do not** describe the consciousness coupling, domain models, or Pentad as
  "derived from the 5D action" or "predicted by the UM geometry".

When adding new modules:

- Determine which category the new work falls into *before* writing the code.
- Add the module to the appropriate table above.
- If it is Category 2, add the `EPISTEMIC STATUS — PHENOMENOLOGICAL BRIDGE`
  disclaimer to the module docstring.

---

## Why This Matters

The Unitary Manifold's scientific credibility rests entirely on the honesty
and precision of its Category 1 claims.  Those claims are falsifiable,
derivation-backed, and numerically verifiable.  Conflating them with Category 2
analogies would:

1. Make the framework unfalsifiable in practice (which specific claim is being
   tested?).
2. Damage the credibility of the genuine physics predictions.
3. Misrepresent the framework to scientists and the public.

The phenomenological bridges are valuable as mathematical languages for complex
systems thinking.  They do not need to be physics claims to be useful.

---

*SEPARATION.md — version 1.0 — May 2026*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
