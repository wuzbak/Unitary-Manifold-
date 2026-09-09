# Merlin Validation Resilience Packet

This packet defines the fail-closed operating doctrine for Merlin whenever validation coverage is degraded by hosted review outages, repository-scale limits, or CodeQL database oversize failures.

## Core truth

- A skipped CodeQL run is not a completed security scan.
- Zero alerts from an incomplete scan is not clean clearance.
- Manual review and targeted tests are compensating controls, not substitutes for missing security-analysis signal.
- Merlin must say this plainly in every review packet, execution board, and promotion conversation.

## Repo-size mitigation actions

1. **Changed-surface-first scanning.** Start with the executable surfaces touched by the change set, especially Product 20 application and engine paths.
2. **Language-separated matrix jobs.** Run one CodeQL job per language so Python, Rust, C/C++, and Java/Kotlin databases do not stack on one runner disk.
3. **Subdomain slicing.** Run smaller validation slices for Product 20, core `src/`, governance, and infrastructure instead of one oversized repository database.
4. **DuckDB preflight inventory.** Generate fast language/path/size telemetry before CodeQL to rebalance matrix slices proactively.
5. **Non-executable bulk exclusion.** Remove mirrored documentation, large static assets, and generated artifacts from security-analysis scope when they do not affect execution.
6. **PR scope manifest.** Retain a small manifest of changed executable paths so reruns stay targeted and reproducible.
7. **Persistent blocker visibility.** Keep the missing-scan warning open until a complete scoped or full scan lands.

## CodeQL scope-reduction strategy

### Phase 1 — Changed executable surface

Prefer the smallest honest slice that contains the changed attack surface:

- `12-AZ-IP/20-psicat-navigator/ox_navigator/`
- `12-AZ-IP/20-psicat-navigator/tests/`
- `TOOLS/checks/copilot_review_orchestrator.py`

If this completes, record it as **scoped evidence** rather than full-repository evidence.

### Phase 2 — Product/domain slices

If the first slice still oversizes, split by repository domain:

- Product 20 application/runtime slice
- core physics `src/` slice
- governance slice
- infrastructure/tooling slice

The purpose is to replace one non-result with several completed partial results.

### Phase 3 — Analysis-budget hygiene

Remove non-executable bulk from the CodeQL slice when it is not part of the live code path:

- mirrored documentation trees
- generated outputs
- static deployment assets with no runtime execution role

This is a scope-control action, not a truth-suppression action.

### Phase 4 — Rerun doctrine

- Re-run after every meaningful scope reduction.
- Preserve the reason for the previous skip.
- Distinguish **completed scoped scan** from **pending full-repository scan**.
- Do not promote a lane to “clean” while the full-scope signal is still missing.

## Matrix workflow + telemetry

- Workflow path: `.github/workflows/codeql-language-matrix.yml`
- Matrix axes: `language` × `path_slice`
- PR mode: changed-surface-first
- Scheduled mode: broad slice sweep
- DuckDB artifact: `codeql-slice-inventory` (language/domain size telemetry used to rebalance future slices)

## Hosted review outage doctrine

When the hosted review tool is unavailable:

- route to the repository-side review orchestrator and fallback model policy
- run targeted local tests on the changed surface
- perform explicit changed-file inspection
- preserve the missing hosted-review signal in the review packet

## Immediate investment priorities

### Biggest push for least effort

- Teach Merlin to emit this packet automatically whenever validation is incomplete.
- Keep the packet linked from the execution board and sprint review packet.
- Train on examples where incomplete signals must remain visible.

### Highest-effort investment

- Establish reliable repository-slice security scanning that consistently finishes on large PRs and large repository domains.
- Convert scoped reruns into routine CI receipts without blurring the boundary between partial and full evidence.

## Required language

Merlin must use language equivalent to:

> “CodeQL was skipped because the repository analysis database was too large. This is an unresolved missing signal, not a clean security result. The next action is a scope-reduced rerun on the changed executable surfaces.”
