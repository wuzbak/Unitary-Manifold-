# AZ Research-Debt Tracker — Product 39

**Folder:** `12-AZ-IP/39-az-research-debt-tracker/`
**Version:** 1.0.0
**TRL:** TRL-3 (generic library; dogfooded against the project's own real gap list)
**Status:** Active — Phase 1 of article-354's "MAS Wave Engine -> generic research-debt tracker" roadmap

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
tracking. Building a shared multi-project SaaS dashboard on top of this
library (Phase 2) is out of scope here.

## Usage

```bash
python 12-AZ-IP/39-az-research-debt-tracker/run.py
```

## Tests

```bash
python -m pytest 12-AZ-IP/39-az-research-debt-tracker/tests -q
```

## Sources

- `src/meta/mas_wave_engine.py` — `GapItem`, `FrameworkScore`, `validate_wave_output`
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #12

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
