# CLAIM_LABEL_STANDARD.md — Universal Epistemic Label Taxonomy
# Unitary Manifold v10.28+

*Effective: 2026-05-08 — Applies repo-wide to every scientific statement,
parameter prediction, structural claim, and architectural limit.*

*No unlabeled scientific statement is permitted in any document, module
docstring, or tracker row after this date.*

---

## Purpose

This document defines the six canonical epistemic labels used across the
Unitary Manifold repository.  Labels exist at two coexistent layers:

| Layer | Audience | Content |
|-------|----------|---------|
| **GATEKEEPER LAYER** | Scientific referees, journals | Concise PASS / TENSION / FALSIFIED verdict; no hidden information, maximum parsimony |
| **TRUTH LAYER** | All users, public domain | Full derivation chain, all open tensions, complete falsification conditions; no downplaying |

**The difference between layers is framing depth, not substance.**
A claim rated PASS in the gatekeeper layer must be accompanied by its
complete derivation status in the truth layer.  A TENSION in the gatekeeper
layer must have its precise σ-level and routing condition in the truth layer.

---

## The Six Labels

### 1. `DERIVED` / `ALGEBRAIC`
**Definition:** The quantity follows as a mathematical theorem or algebraic
identity from the 5D metric ansatz and topology alone.  Zero free parameters.
Zero observational inputs.

**Gatekeeper verdict:** PASS — mathematical necessity, not an empirical claim.

**Promotion criteria:**
- A complete, checkable proof exists in `src/`
- The corresponding test passes with 0 failures
- The derivation chain is documented in FALLIBILITY.md

**Examples:** N_gen = 3 (T²/Z₃ orbifold), k_CS = 74 (= 5² + 7²),
n_w = 5 (Z₂ orbifold uniqueness theorem, Pillars 39/67/70-B/70-D)

**Falsification condition:** A proof that the derivation contains a logical
error, or an experiment that contradicts the derived value at ≥ 3σ.

---

### 2. `GEOMETRIC_PREDICTION`
**Definition:** The quantity is predicted from the 5D geometry with no free
parameters, and the prediction lies within 5% of the current PDG / experimental
central value.

**Gatekeeper verdict:** PASS — geometrically derived prediction consistent with data.

**Promotion criteria:**
- Residual ≤ 5% vs PDG central value
- Derivation trace is auditable (pillar + source file cited)
- Prediction pre-dates or is independent of the observational value (no fitting)

**Examples:** n_s = 0.9635 (P1), r = 0.0315 (P2), sin²θ_W (P4),
m_H (P5), M_W (P21), M_Z (P22), top/bottom/tau/electron Yukawa (P7–P10)

**Falsification condition:** Experimental measurement more than 5% from
prediction at ≥ 3σ, OR demonstration that the derivation used an
observational input as a hidden free parameter.

---

### 3. `CONSTRAINED`
**Definition:** The quantity has a geometric estimate within 50% of the
PDG value, or is bounded by framework arguments without a complete derivation.
Honest residual documented.

**Gatekeeper verdict:** TENSION (if residual > 5%) or PASS (if residual ≤ 5%
with documented systematic).

**Promotion criteria to GEOMETRIC_PREDICTION:**
- Reduce residual below 5% via a genuine derivation (not parameter fitting)
- Document the derivation in a hardgate artifact

**Demotion criteria:**
- If new data moves the central value so that the constraint no longer applies

**Examples:** Δm²₂₁ solar splitting (P16), neutrino mass scale m_ν (P26),
Λ_QCD from AdS/QCD soft-wall (Path B, ~194 MeV, factor 1.7 from PDG)

---

### 4. `SCAFFOLD`
**Definition:** The quantity has a placeholder derivation or
order-of-magnitude estimate; the closing mechanism is identified but
not yet executed.  Explicitly not promoted and not scored.

**Gatekeeper verdict:** OPEN — derivation pending; prediction not claimed.

**Truth layer requirement:** The specific missing derivation step must be
named, with the blocking dependency clearly identified.

**Demotion from SCAFFOLD:**
- If the blocking dependency is not resolved within a defined program arc,
  the claim must be reclassified OPEN and removed from score tables.

**Examples:** Sub-leading CS corrections to c_L (Pillar 183 pending),
exact UV-brane α_GW value for A_s normalization closure

---

### 5. `OPEN_TENSION`
**Definition:** An acknowledged conflict between a framework prediction and
current observational data at < 3σ.  The framework prediction is stated,
the data is stated, the tension level is stated, and the routing condition
for escalation to FALSIFIED is stated.

**Gatekeeper verdict:** TENSION — < 3σ, awaiting better data.

**Truth layer requirement:**
- Exact σ-level of current tension
- Experiment and dataset that will resolve it
- Explicit routing: `if σ ≥ 3.0 → FALSIFIED`
- No minimizing language

**Examples:**
- DESI Y1: wₐ ≠ 0 at 2.1σ (UM predicts wₐ = 0, frozen radion) — G3
- CMB acoustic peak amplitude: suppressed ×4.2–6.1 vs ΛCDM — G2

---

### 6. `FALSIFIED_IF`
**Definition:** A prediction for which the exact falsification condition
is stated, the experiment is identified, and the timeline is known.  The
prediction is currently untested but the falsifier is active.

**Gatekeeper verdict:** PENDING — falsifiable prediction awaiting measurement.

**Truth layer requirement:**
- Exact numerical falsification window stated
- Experiment, dataset, and expected publication timeline
- Routing: explicit PASS / TENSION / FALSIFIED branches
- Statement is not weakened or hedged

**Examples:**
- β ∉ [0.22°, 0.38°] at ≥ 3σ → birefringence mechanism FALSIFIED (LiteBIRD ~2032)
- β ∈ (0.29°, 0.31°) at ≥ 3σ → inter-sector gap FALSIFIED (LiteBIRD ~2032)
- r < 0.010 at > 3σ → braided mechanism FALSIFIED (CMB-S4 ~2030)
- 4th light neutrino confirmed → N_gen = 3 derivation FALSIFIED

---

## Scoring Rules (ToE Score)

| Label | Points | Note |
|-------|--------|------|
| DERIVED / ALGEBRAIC | 1.0 | Mathematical theorem |
| GEOMETRIC_PREDICTION | 0.8 | ≤ 5% from PDG, no free parameters |
| CONSTRAINED | 0.5 | ≤ 50% from PDG, architecture explanation |
| GEOMETRIC_ESTIMATE_CERTIFIED | 0.3 | NLO/6D+ improved; residual documented |
| ARCHITECTURE_LIMIT_CERTIFIED | 0.1 | Closing mechanism identified |
| SCAFFOLD / OPEN | 0.0 | No prediction yet |

---

## Hard Truth-Preservation Rules

1. **No downplaying open problems.** Every gap in FALLIBILITY.md is labeled
   with its exact magnitude.  Minimizing language ("minor issue", "technical
   detail") is prohibited.

2. **No promotion without evidence artifact.** A claim may not advance from
   CONSTRAINED to GEOMETRIC_PREDICTION without a hardgate artifact: a source
   file, a passing test, and a residual calculation.

3. **No contradiction between layers.** The gatekeeper and truth layers must
   agree on the underlying facts.  Framing may differ; facts must not.

4. **Continuous correction protocol.** On any new contradictory evidence:
   immediate relabel + public changelog entry in `docs/WAVE_CHANGELOG.md`
   within 30 days.  If falsifier triggers, mark impacted claims immediately.

5. **Done means dual-published.** A claim is complete only when it appears in:
   - `docs/CLAIM_MASTER_BOARD.md` (with label + falsifier + dependency)
   - `docs/TRUTH_LAYER.md` (with full derivation context)
   - `docs/GATEKEEPER_SUMMARY.md` (with concise PASS/TENSION/FALSIFIED)

---

## Cross-Reference Index

| Document | Role |
|----------|------|
| `docs/CLAIM_MASTER_BOARD.md` | Single-source board: all claims, labels, falsifiers, dependencies |
| `docs/TRUTH_LAYER.md` | Full derivation context; all open tensions; no gatekeeping |
| `docs/GATEKEEPER_SUMMARY.md` | Concise auditable summaries; PASS/TENSION/FALSIFIED |
| `docs/TOE_SCORE_AUDIT.md` | Scored parameter table; v10.28 = 76% |
| `3-FALSIFICATION/OBSERVATION_TRACKER.md` | Observation-by-observation routing |
| `FALLIBILITY.md` | Axiomatic assumptions; known gaps; failure modes |
| `docs/mas_tracker.yml` | Machine-readable workstream and wave status |

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
