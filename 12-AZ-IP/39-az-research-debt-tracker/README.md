# AZ Research-Debt Tracker — Product 39

**Folder:** `12-AZ-IP/39-az-research-debt-tracker/`
**Version:** 1.1.0
**TRL:** TRL-4 (generic library, now a runnable read-only web dashboard; dogfooded against the project's own real gap list)
**Status:** Active — Phases 1-2 of article-354's "MAS Wave Engine -> generic research-debt tracker" roadmap

## What this is

`src/meta/mas_wave_engine.py`'s `GapItem` / `FrameworkScore` /
`validate_wave_output()` already implement a working gap-tracking and
closure-scoring model, but its vocabulary (pillars, falsifiers,
physics-specific epistemic labels) is Unitary-Manifold-specific. This
product strips that vocabulary and generalizes the same shape:

- `WorkItem` — a tracked unit of debt, with a configurable `status` string.
- `StatusTaxonomy` — the project's own declaration of which status names
  count as "closed" vs "open".
- `ResearchDebtTracker` — add/query items, compute `health_score()`
  (closure fraction, breakdown by status), and `validate_closure()` an
  item against tests-passed/failed + documentation requirements.
- `um_dogfood.load_um_gaps_into_tracker()` — loads the project's own
  real, live 6-item gap list straight out of
  `MASWaveEngine().audit_all_gaps()` into the generic tracker, proving the
  generalization is faithful to at least one real consumer rather than a
  synthetic-only demo.

## Epistemic status

This is a general-purpose library; it does not replace
`src/meta/mas_wave_engine.py`, which remains canonical for UM's own pillar
tracking. The web layer below (Phase 2) serves the project's own live
`um_dogfood` tracker read-only; it is a single-project dashboard, not a
shared multi-project SaaS service — adding items or building a new tracker
still requires Python code via `ResearchDebtTracker` directly.

## Usage

```bash
python 12-AZ-IP/39-az-research-debt-tracker/run.py
```

## Running as a web product

```bash
python 12-AZ-IP/39-az-research-debt-tracker/run.py --serve --port 8139
```

Then visit `http://127.0.0.1:8139/` for the tracker dashboard, or query
the JSON API directly:

- `GET /api/status` — product metadata, dogfood source, total item count
- `GET /api/health-score` — closure fraction, breakdown by status
- `GET /api/open-items` — all open `WorkItem`s
- `GET /api/closed-items` — all closed `WorkItem`s
- `GET /api/item?item_id=` — one item by id

## Tests

```bash
python -m pytest 12-AZ-IP/39-az-research-debt-tracker/tests -q
```

## Sources

- `src/meta/mas_wave_engine.py` — `GapItem`, `FrameworkScore`, `validate_wave_output`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #12

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
