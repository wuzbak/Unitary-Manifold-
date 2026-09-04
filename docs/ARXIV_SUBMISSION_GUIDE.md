# arXiv Submission Readiness Guide — Unitary Manifold

*Theory and scientific direction: ThomasCory Walker-Pearson.*  
*Document engineering: GitHub Copilot (AI).*

---

## Current canonical submission state

- Canonical status surfaces: `STATUS.md`, `FALLIBILITY.md`, `docs/mas_tracker.yml`, `docs/CLAIM_MASTER_BOARD.md`, `docs/TRUTH_LAYER.md`, `docs/GATEKEEPER_SUMMARY.md`, `docs/WAVE_CHANGELOG.md`, `docs/SPRINT_PLAN.md`
- Current branch-wide verified regression marker: **63,732 passed · 23 skipped · 12 deselected · 0 failed**
- Current tracked slot marker: **next pillar slot 1051**
- Canonical live status JSON: `9-INFRASTRUCTURE/um_live_status.json`

---

## Pre-submission checklist

1. Confirm title/abstract and scope language match the current canonical claim state.
2. Confirm open lanes and residual limits match `FALLIBILITY.md` and `docs/CLAIM_MASTER_BOARD.md`.
3. Keep falsification language exact and unweakened:
   - LiteBIRD birefringence decision window and kill conditions
   - DESI `w_a` monitoring/falsification routing
4. Confirm no stale historical status snapshots are presented as current state.
5. Run full regression:
   - `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`
6. Confirm metadata alignment:
   - `CITATION.cff`
   - `.zenodo.json`
   - `6-MONOGRAPH/zenodo/.zenodo.json`
   - `9-INFRASTRUCTURE/schema.jsonld`

---

## Submission strategy

- Use one canonical manuscript packet that matches the live claim registry.
- Keep explicit boundaries: internal mathematical self-consistency is not external empirical confirmation.
- Keep open limits, unresolved lanes, and external decision windows visible.

---

## Final gate before upload

1. Regression green.
2. Canonical surfaces synchronized.
3. No stale status strings in submission docs.
4. Archive and DOI metadata aligned with current release state.

---

*Document version: 5.0 — 2026-09-04 (v35.7 sync)*
