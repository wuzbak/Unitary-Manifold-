# arXiv Submission Readiness Guide — Unitary Manifold

*Theory and scientific direction: ThomasCory Walker-Pearson.*  
*Document engineering: GitHub Copilot (AI).*

---

## 1 · Current Submission Readiness (v10.51)

| Item | Status |
|------|--------|
| Theory manuscript | `6-MONOGRAPH/arxiv/main.tex` updated through v10.51 |
| References | `6-MONOGRAPH/arxiv/references.bib` updated through v10.51 |
| ToE score | **27.8/28.0 = 99.3%** (canonical: `docs/TOE_SCORE_AUDIT.md`) |
| Primary falsifier | LiteBIRD birefringence β ∈ {0.273°, 0.331°}; falsified in gap [0.29°, 0.31°] or outside [0.22°, 0.38°] |
| Canonical claim layer | `docs/CLAIM_MASTER_BOARD.md`, `docs/TRUTH_LAYER.md`, `docs/GATEKEEPER_SUMMARY.md` |
| Regression gate | `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` |

## 2 · Pre-Submission Checklist

### 2.1 Manuscript Sync
- [ ] Ensure manuscript title page and abstract match v10.51 claim state
- [ ] Ensure ToE score statements use 27.8/28.0 (99.3%) and cite `docs/TOE_SCORE_AUDIT.md`
- [ ] Ensure P1–P28 labels match `docs/CLAIM_MASTER_BOARD.md`
- [ ] Ensure active tensions/falsifiers match `FALLIBILITY.md` and `3-FALSIFICATION/OBSERVATION_TRACKER.md`
- [ ] Ensure all module references point to current file paths in `src/core/`

### 2.2 Falsification Integrity
- [ ] Keep LiteBIRD falsifier wording exact (no weakened bounds)
- [ ] Keep DESI wₐ lane honest (TENSION/FALSIFIED routing policy)
- [ ] Keep epistemic boundary aligned with `SEPARATION.md`

### 2.3 Metadata & Packaging
- [ ] Confirm category routing (`hep-th`, cross-lists as appropriate)
- [ ] Confirm release version/tag and DOI metadata (`CITATION.cff`, `9-INFRASTRUCTURE/schema.jsonld`)
- [ ] Confirm no stale v10.18/v10.4 score language remains

## 3 · Submission Strategy

### Option A — Single canonical submission (recommended)
- Submit one v10.51 manuscript with full canonical truth-sync
- Anchor all claim statuses to claim board + truth layer + gatekeeper summary
- Keep active tensions explicit rather than deferred

### Option B — Split delivery
- Technical derivation paper first, governance/operations companion second
- Use same canonical falsifier/score language in both

## 4 · Final Gate Before Upload

1. Run full regression.
2. Confirm docs truth-sync (ToE score, labels, falsifiers, tensions).
3. Confirm no stale historical score snapshots are presented as current.
4. Freeze submission artifacts and publish.

---

*Document version: 2.0 — 2026-05-11 (v10.51 sync)*
