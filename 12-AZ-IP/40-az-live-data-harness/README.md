# AZ Live-Data Harness — Product 40

**Folder:** `12-AZ-IP/40-az-live-data-harness/`
**Version:** 1.0.0
**TRL:** TRL-3 (generic harness; demonstrated against a real, working adapter)
**Status:** Active — Phase 1 of article-354's "Live-public-data pattern -> shared harness" roadmap

## What this is

`src/data/fetch_planck.py`, `12-AZ-IP/21-geo-monitor/geo_monitor/engine/feeds.py`,
and `12-AZ-IP/19-falsification-observatory`'s routing functions each
hand-roll the same shape: attempt a live network fetch, fall back to a
known offline value on failure, and compare the resulting measurement
against a prediction to reach a verdict. This product extracts that
shape:

- `fetch_with_fallback(fetch_fn, fallback_value) -> FetchResult` —
  attempts `fetch_fn()`, records whether the result came from `LIVE` or
  `FALLBACK`, and captures the error that triggered the fallback.
- `compute_verdict(predicted, measured, sigma, ...) -> Verdict` —
  generalizes `fetch_planck.compute_um_residuals()`'s sigma-pull check
  and `falsification_observatory`'s `AWAITING_DATA` convention into one
  `CONSISTENT` / `INCONSISTENT` / `AWAITING_DATA` verdict shape.
- `planck_adapter.py` — a **real, working adapter**, not a mock: it
  attempts a genuine network call against the ESA Planck Legacy Archive
  endpoint `fetch_planck.py` names (but never actually calls), and falls
  back to `PLANCK_2018_BESTFIT['n_s']` on failure. In this sandboxed
  environment that live call genuinely fails (no network route to the
  host), so the fallback path is exercised honestly rather than assumed.

## Epistemic status

This product does not migrate `feeds.py` or
`falsification_observatory`'s routing functions onto the new harness —
they remain independent and canonical. Only one adapter
(`fetch_planck.py`'s n_s comparison) is demonstrated end-to-end, per this
repository's established "partial Phase 1, stated honestly" pattern (see
Product 32's README for the same convention).

## Usage

```bash
python 12-AZ-IP/40-az-live-data-harness/run.py
```

## Tests

```bash
python -m pytest 12-AZ-IP/40-az-live-data-harness/tests -q
```

## Sources

- `src/data/fetch_planck.py` — `PLANCK_2018_BESTFIT`, `compute_um_residuals`
- `12-AZ-IP/21-geo-monitor/geo_monitor/engine/feeds.py` — `USGSFeedParser.fetch`
- `12-AZ-IP/19-falsification-observatory` — routing `AWAITING_DATA` convention
- `7-OUTREACH/A Z PsiCat Literature/Articles/article-354-...md` — direction #13

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
