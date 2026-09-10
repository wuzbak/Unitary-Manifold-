# CI_HEALTH.md — Continuous Integration Health Report

*Living operational document — use canonical live status + workflow logs, not static snapshots.*

## Canonical status sources

- Live regression/version metrics: `9-INFRASTRUCTURE/um_live_status.json`
- Human-readable sprint/status ledger: `STATUS.md`
- Cross-ledger coherence policy: `docs/SPRINT_PLAN.md` and `.github/PULL_REQUEST_TEMPLATE.md`

## What CI must enforce

1. **Zero-failure regression discipline** for scoped and full suites.
2. **Ledger coherence** across canonical truth surfaces before merge.
3. **Registry integrity** checks for fingerprinted assets.
4. **Honest falsifier routing** (open gaps remain explicit, no unearned closure labels).

## Current workflow map (authoritative names)

- `.github/workflows/ci.yml` — full combined regression gate
- `.github/workflows/tests.yml` — focused suites + ledger-consistency sweeps
- `.github/workflows/lean4-check.yml` — formal compilation lane
- `.github/workflows/staleness-honesty-gate.yml` — stale wording/surface drift gate
- `.github/workflows/um-sos-registry-check.yml` — registry consistency gate
- `.github/workflows/desi-dr3-routing.yml` — falsifier/tension routing automation

## Verification protocol (do this instead of trusting this file as a snapshot)

1. Read `9-INFRASTRUCTURE/um_live_status.json` for current version/test counts.
2. Query recent workflow runs and job logs via GitHub Actions MCP tools.
3. If any run is `failed`, `action_required`, or stalled, inspect failing job logs directly and record root cause + fix status.
4. Re-run the exact impacted local suites before merge.

## Anti-staleness policy

- Do not hardcode fixed pass-count/version claims here.
- Treat this file as process guidance only.
- Keep app/product totals aligned to `12-AZ-IP/README.md` and related deployment surfaces.

*Last updated: 2026-09-10*
