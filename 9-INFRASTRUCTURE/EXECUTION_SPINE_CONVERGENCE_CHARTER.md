# Execution Spine Convergence Charter

This charter governs the approved monorepo convergence program.

The objective is not to widen the repository with more disconnected surfaces. The
objective is to consolidate active execution, artifact, readiness, and status
work into one coherent spine that remains honest about boundaries, optional
backends, and unresolved blockers.

## Thesis

The repository should converge around:

1. one canonical truth/status spine,
2. one governed execution spine for artifacts, health checks, routing, and promotion metadata,
3. one canonical control plane in PsiCat,
4. one explicit adjacent quantum execution lane,
5. one disciplined compatibility story for legacy folders and routes.

## Canonical truth surfaces

The following surfaces remain the canonical status chain and must not drift when
status-bearing work is performed:

- `STATUS.md`
- `docs/mas_tracker.yml`
- `FALLIBILITY.md`
- `docs/CLAIM_MASTER_BOARD.md`
- `docs/GATEKEEPER_SUMMARY.md`
- `docs/TRUTH_LAYER.md`
- `docs/WAVE_CHANGELOG.md`
- `docs/SPRINT_PLAN.md`
- `9-INFRASTRUCTURE/um_live_status.json`

## Completion map

### Primary convergence targets

- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/20-psicat-navigator/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/24-psicat-web-browser/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/01-axiom-os/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/04-um-sos/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/bot/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/9-INFRASTRUCTURE/`

### Adjacent execution consumers

- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/src/quantum/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/19-falsification-observatory/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/21-geo-monitor/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/22-az-sge/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/18-um-reader/`

### Compatibility-only surfaces

- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/10-UM-SOS/`
- `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/11-AZ-OS/`
- legacy `/api/merlin/*`
- legacy `/api/ox*`

## Shared execution-spine contract

The shared execution spine must carry the following fields wherever repository
artifacts or readiness packets are emitted:

- surface identity and kind,
- lane identity,
- current status,
- summary,
- canonical paths and sources,
- fail-closed governance metadata,
- compatibility metadata,
- health checks,
- promotion metadata.

This contract exists to make heterogeneous products and adjacent execution lanes
readable through one disciplined interface without inventing competing status or
promotion languages.

## Phase map

### Phase 1 — charter and boundaries

Lock the canonical homes, consumers, compatibility shims, and non-claim
boundaries before broadening any integration work.

### Phase 2 — shared execution contract

Converge artifacts, health checks, routing/preflight, promotion metadata, and
telemetry around one repository-native execution-spine contract.

### Phase 3 — PsiCat control plane

Keep `/api/psicat` as the primary governed control plane. `/api/merlin` and
`/api/ox` remain supported compatibility routes, not competing product centers.

### Phase 4 — adjacent quantum attachment

Attach the XDiag bridge and adjacent quantum execution artifacts to the shared
execution spine while keeping optional-backend truth explicit.

### Phase 5 — consumer convergence

Shift active products toward shared status, artifact, and readiness surfaces in
place of bespoke local payload contracts.

### Phase 6 — validation and sanity

Hold the convergence program to existing tests, explicit benchmark receipts,
anti-bloat discipline, and visible blocker reporting.

## Sanity rules

1. No new competing source of truth.
2. No new product-local status ledger when a canonical status surface already exists.
3. No new orchestration path without the shared execution-spine contract.
4. No promotion language without receipt-backed benchmark evidence.
5. No optional backend presented as guaranteed capability.
6. No hardgate physics promotion as a side effect of infrastructure work.
7. No legacy compatibility route treated as a primary development center.

## Definition of completion

This convergence program is complete only when active runtime, artifact,
readiness, and adjacent execution surfaces can be read coherently through one
governed execution spine, with legacy compatibility preserved but subordinated,
and with no inflation of scientific or product status.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
