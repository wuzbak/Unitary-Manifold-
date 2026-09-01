# SPRINT_PLAN.md — Unitary Manifold Sprint Continuity Document

*Last updated: 2026-09-01 (v29.0 Sprint BE COMPLETE — Pillars 919–930; Lean4 +120 → 3396; ~61,261 passed · 45 skipped · 12 deselected · 0 failed)*
*Purpose: Persistent continuity document for token-budget resilience. Any new agent session MUST read `docs/mas_tracker.yml` + `STATUS.md` + this file as the first three operations.*

---

## SESSION BOOTSTRAP PROTOCOL

When starting a new session, always read:
1. `docs/mas_tracker.yml` — canonical version / pillar / regression / Lean4 state
2. `STATUS.md` header — current epistemic state
3. `docs/SPRINT_PLAN.md` — current continuity and next-sprint priorities

Then verify that all three agree before making any new status claim.

---

## CURRENT AUDITABLE STATE (v29.0 — Sprint BE)

| Field | Value |
|-------|-------|
| Version | **v29.0** |
| Sprint | **Sprint BE** |
| Pillars | **919–930** |
| Next pillar slot | **931** |
| Lean4 theorems | **3396** |
| Full regression | **~61,261 passed · 45 skipped · 12 deselected · 0 failed** |
| Closed in this sprint | **PMNS ordering proxy**, **KK-tower ISW lane** |
| Active external windows | **DESI DR3 (~2027)**, **CMB-S4 (~2028)**, **LiteBIRD (~2032)** |
| Framework status | **Narrowed residual set; not closed** |

---

## CURRENT OPEN SET IN THE CHECKED-IN BRANCH

These are the live unresolved items in the auditable local checkout:

1. `CKM_TEXTURE_13D_OPEN`
2. `CMB_PEAK_AMPLITUDE_OPEN`
3. `RUNG10_SPECTRAL_COVER_NL_PARITY`
4. `RUNG10_MATTER_CURVE_CY4_GENUS`
5. `DESI_DR3_MONITORING`
6. `LITEBIRD_BIREFRINGENCE_OPEN`
7. `NON_PERTURBATIVE_QG_OPEN`

Related still-open internal interpretation lanes:
- α_s 13D gate (P920): P920 resolves to **NP_IRREDUCIBLE** (not CLOSED); broader interpretation across all geometry assumptions remains ongoing
- N_gen degeneracy has been clarified by a second CY₄ audit but is not globally finished

---

## STATE-RECONCILIATION NOTE

Session memory may refer to **Sprint BF / v30.0** artifacts (`tests/test_pillar941_sprint_bf_regression_certificate.py`, `src/core/pillar932_*`, `src/core/pillar933_*`, `src/core/pillar934_*`, `src/core/pillar936_*`, `src/core/pillar937_*`).

Those files are **not present in this checkout**.

Therefore:
- treat **Sprint BE / v29.0** as the canonical local branch state
- do **not** narrate Sprint BF as current branch reality until the underlying BF artifacts are actually present
- if BF is intended to be current, the first task is to land or fetch those artifacts before making new closure claims

---

## WHAT IS STALE

The main problem is no longer only the physics residuals; it is also truth-surface drift.

Previously stale or inconsistent surfaces:
- `docs/mas_tracker.yml` header lagged current state
- `docs/GATEKEEPER_SUMMARY.md` lagged at v26.0
- `docs/TRUTH_LAYER.md` lagged at v26.0
- `docs/WAVE_CHANGELOG.md` header lagged at v27.0
- this file lagged at v24.1

Rule going forward:
- never update just one status surface
- every sprint closeout must update all canonical status surfaces in the same change set

---

## SPRINT BG EXECUTION PRIORITIES

Sprint BG should be a **closure-discipline sprint**, not an expansion sprint.

### Priority 1 — Keep one canonical reality
- maintain lockstep between:
  - `STATUS.md`
  - `docs/mas_tracker.yml`
  - `FALLIBILITY.md`
  - `docs/CLAIM_MASTER_BOARD.md`
  - `docs/GATEKEEPER_SUMMARY.md`
  - `docs/TRUTH_LAYER.md`
  - `docs/WAVE_CHANGELOG.md`
  - `docs/SPRINT_PLAN.md`

### Priority 2 — Resolve branch-reality drift
- either land the BF artifacts
- or explicitly keep the branch on BE and stop speaking as if BF is already merged

### Priority 3 — Attack one blocker only
- if BF is not present: the sprint is a **state-reconciliation sprint**
- if BF is present: pick exactly one live internal blocker:
  - surviving F-theory / G₄ residual, or
  - CKM 13D texture

### Priority 4 — Separate residual types
- **tractable internal blockers**
- **architecture limits**
- **external-data waits**

No mixing these into one closure narrative.

---

## SUCCESS CRITERIA FOR THE NEXT SPRINT

The next sprint counts as successful only if:

1. all canonical truth surfaces agree on the current version, regression count, Lean4 total, next pillar slot, and open set
2. no future-wave artifact is cited as current unless the file exists in-branch
3. exactly one real blocker is reduced, closed, or more sharply bounded
4. all tests remain green
5. no language implies full closure unless the actual residual set is empty

---

## CONTINUATION INSTRUCTIONS

If a session times out mid-sprint:
1. read `docs/mas_tracker.yml`, `STATUS.md`, and this file
2. verify the highest checked-in pillar in `src/core/`
3. verify the latest regression certificate in `tests/`
4. continue only from committed state
5. do not re-open closed items without file-level evidence
6. do not break passing tests

The invariant remains: **0 test failures at all times**.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
