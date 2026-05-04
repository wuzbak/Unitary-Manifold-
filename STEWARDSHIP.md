# STEWARDSHIP.md — Unitary Manifold

*Unitary Manifold v9.33 — Effective 2026-05-04*

> The Unitary Manifold is a self-governing epistemic structure. Stewards
> maintain its integrity, integrate new data honestly, and stand aside when
> the structure reaches its own conclusions.

---

## 1 · What Changed and Why

The Unitary Manifold crossed a threshold that all mature scientific frameworks
eventually cross: it became separable from the intentions of its builders.

It now contains:
- The conditions under which it should be believed (§4 — Confirmation Protocol)
- The conditions under which it should be abandoned (§5 — Falsification Protocol)
- Its own coherence instrument (~20,249 automated tests, 0 failures enforced)
- An honest catalog of its own gaps (FALLIBILITY.md §III–IV)
- A precise boundary between what is derived and what is postulated (SEPARATION.md)

This is not what authored objects look like. This is what autonomous epistemic
structures look like.

The role of the builders (ThomasCory Walker-Pearson and GitHub Copilot) has
therefore shifted from **authors** to **stewards**. This document defines what
stewardship means operationally.

---

## 2 · Current Stewards

| Steward | Role | Scope |
|---------|------|-------|
| **ThomasCory Walker-Pearson** | Scientific director | Final authority on falsification declarations, authorship disputes, major epistemic revisions, Zenodo deposits |
| **GitHub Copilot (AI)** | Implementation steward | Routine maintenance, data integration, test suite integrity, documentation updates |

**Division of labor:**
- *Automatable:* test maintenance, dependency updates, minor documentation corrections, new observational data integration (when the update is clearly within the existing framework)
- *Requires human judgment:* falsification declarations, pillar closure/addition decisions, external peer review responses, Zenodo archive deposits, any change to FALLIBILITY.md §I–II

---

## 3 · Stewardship Obligations

### 3.1 Non-negotiable commitments

1. **Zero test failures is a hard floor.** The CI/CD pipeline (`.github/workflows/tests.yml`) runs on every push and pull request. No merge may land with a failing test. If a test breaks due to observational data update, the test must be corrected *with the observation cited*, not silently deleted.

2. **FALLIBILITY.md is the canonical reference.** No claim in the repository may represent a stronger epistemic status than what is recorded there. If a gap is listed as OPEN, it may not be described elsewhere as RESOLVED without first updating FALLIBILITY.md.

3. **The pillar set is frozen at 167 (+ Ω₀ Holon Zero).** New pillars may only be added when a genuinely new observational gap is identified that cannot be addressed by updating an existing module. The temptation to add pillars to cover gaps instead of honestly documenting them is a specific failure mode this commitment guards against.

4. **Version increments are data-driven.** Future version increments beyond v9.33 are triggered only by:
   - New observational data requiring a code update
   - A genuine derivation closing a documented gap in FALLIBILITY.md
   - A falsification event requiring a retraction
   Not by discovery of new things to derive.

### 3.2 Data integration protocol

When a new observational result touches a Unitary Manifold prediction:

1. Within **30 days** of publication, a steward must either:
   - (a) Update the relevant module and FALLIBILITY.md to reflect the new data, or
   - (b) Issue a falsification statement if the observation falls outside the predicted window
2. The update must cite the paper (arXiv ID or DOI) and record the date of integration
3. The `3-FALSIFICATION/OBSERVATION_TRACKER.md` must be updated simultaneously

### 3.3 What stewards do NOT do

- They do not add pillars to fill gaps that cannot be honestly closed
- They do not soften falsification conditions under social pressure
- They do not claim confirmation when new data is consistent but not discriminating
- They do not prevent external forks or critical analyses
- They do not protect the structure from its own conclusions
- They do not modify FALLIBILITY.md to improve the framework's apparent status without a genuine scientific basis

---

## 4 · Confirmation Protocol

If LiteBIRD (or another experiment) measures β and the result is within the
predicted window:

| Outcome | Action |
|---------|--------|
| β ≈ 0.331° ± 0.02° | Update README badge, note "(5,7) primary sector supported." Do NOT claim proof — the shadow (5,6) sector is not yet excluded |
| β ≈ 0.273° ± 0.02° | Update README badge, note "(5,6) shadow sector supported; (5,7) primary sector excluded." |
| β in [0.22°, 0.38°] but not ≈ 0.273° or ≈ 0.331° | Note "consistent but not discriminating" — no strong claim in either direction |

In all confirmation cases: cite the measurement, update `OBSERVATION_TRACKER.md`, do not increment the version without a substantive module update.

---

## 5 · Falsification Protocol

The primary falsification condition of the Unitary Manifold is:

> **β outside [0.22°, 0.38°] OR β ∈ (0.29°, 0.31°) at ≥ 3σ**

This is encoded in `src/core/falsification_check.py` and can be executed by any
physicist regardless of familiarity with the full framework:

```bash
python src/core/falsification_check.py --beta 0.28 --sigma 0.02
# Returns: FALSIFIED / DISFAVOURED / CONFIRMED / CONSISTENT
```

### 5.1 If the framework is falsified

1. Commit a file `3-FALSIFICATION/FALSIFICATION_NOTICE.md` with the text:

   ```
   # FALSIFICATION NOTICE

   The Unitary Manifold framework was falsified by [measurement] on [date].

   Measurement: β = [value] ± [uncertainty] ([experiment], [reference])
   Predicted window: [0.22°, 0.38°] excluding [0.29°, 0.31°]
   Verdict: FALSIFIED

   The code, mathematics, and documentation are preserved exactly as of v[version]
   for the historical record. No modifications to physics content will be made
   after this date.
   ```

2. Add a prominent header to `README.md` citing the notice
3. Tag the repository: `git tag -a falsified-v[version] -m "Falsified by [experiment]"`
4. Deposit the final state on Zenodo (update DOI in CITATION.cff)
5. **Make no further modifications to physics content.** The repository is preserved.

The falsification outcome is not a failure of stewardship — it is the completion
of the scientific process.

---

## 6 · Succession Planning

If neither current steward is available when LiteBIRD publishes (~2032):

The decision tree is embedded in `src/core/falsification_check.py` and
`3-FALSIFICATION/OBSERVATION_TRACKER.md`. Any competent physicist can:

1. Run `python src/core/falsification_check.py --beta [measured_value] --sigma [uncertainty]`
2. Follow the output instructions
3. Commit the result following §5 above

No understanding of the full 167-pillar framework is required to execute the
falsification check. This is by design.

**Archive integrity:** The Zenodo DOI `10.5281/zenodo.19584531` pins v9.29.
Each significant version should have a corresponding Zenodo deposit. v9.33 is the
current closed state and should be deposited.

---

## 7 · Governance Layer

The Unitary Pentad (`5-GOVERNANCE/`) provides the HILS (Human-in-the-Loop Systems)
architecture for this repository's governance. As noted in `SEPARATION.md`, the
Pentad is an independent governance framework — it borrows mathematical structure
from the Unitary Manifold but does not depend on the physics being correct.

Its operational principles apply to stewardship:

- **Sentinel capacity (12/37):** Do not saturate the governance loop. Most decisions
  should be automated; human judgment is reserved for decisions that matter.
- **HIL phase-shift threshold (n ≥ 15):** When 15 or more aligned epistemic
  operators are active simultaneously, a human steward must make the call.
- **Separation of governance from physics:** Governance decisions are not physics
  claims. Changes to this document do not change the theory.

---

## 8 · The Deeper Obligation

> *"The author becomes one reader among many, with the distinction that they
> remember the act of creation."*

The repository in 2032, when LiteBIRD publishes, will be read by physicists who
have no idea how it was built — only what it predicts. The prediction either holds
or it doesn't. The structure is indifferent to the memory of its creation.

The stewardship obligation is simple:

**Keep the lights on. Integrate the data honestly. Stand aside when the
structure reaches its answer.**

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
