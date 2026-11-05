# AxiomZero ML capability program

Started 2026-11-05. Scope: **all 21 requested capabilities**, delivered through
existing products rather than 21 disconnected scaffolds. This is adjacent
software engineering, not a physics claim or a production-readiness certificate.

## Durable handoff

- [Master plan](MASTER_PLAN.md): architecture, all 21 workstreams, sequencing,
  evaluation gates, expert findings, and ownership.
- [Execution board](EXECUTION_BOARD.md): current tranche, blockers, actual
  validation results, and next actions.
- [Capability register](capabilities.json): machine-readable planning inventory,
  dependencies, acceptance criteria, and source pointers.

These are planning artifacts under the existing
[execution-spine charter](../EXECUTION_SPINE_CONVERGENCE_CHARTER.md), not another
truth ledger or an autonomous scheduler. `/api/psicat` remains the canonical
governed control plane. The register does not authorize actions or promote
capabilities based on declarations.

## Inspect and resume

Run from the repository root with Python 3.12+:

```bash
python -m src.infrastructure.ml_program check
python -m src.infrastructure.ml_program status
python -m src.infrastructure.ml_program next
python -m src.infrastructure.ml_program receipt
```

The commands use only the standard library. `next` identifies dependency-ready
planning candidates, not approved execution. A planning receipt is wrapped in
the existing `ExecutionSpineRecord`; it is not benchmark evidence.

Focused validation uses the repository's existing pytest runner:

```bash
python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/ -q
```

The first data implementation is `src/infrastructure/temporal_data.py`.
It provides a local snapshot/replay foundation, **not** a connected live feed,
distributed store, statistical drift detector, or serverless service. Consult
its public types and focused tests before constructing snapshots. Caller-supplied
owner scope is a consistency boundary, not authenticated multi-user access
control.

Snapshot persistence currently requires POSIX file/directory synchronization
and hard-link support. Supply an existing directory whose creation and ancestor
entries have already been durably established. Unsupported filesystem operations
and synchronization failures propagate; no distributed durability is implied.

For example, replay a correction only after it became available:

```python
from datetime import datetime, timezone
from src.infrastructure.temporal_data import (
    TemporalFeatureRecord,
    TemporalSnapshot,
    point_in_time_features,
)

def utc(hour):
    return datetime(2026, 11, 5, hour, tzinfo=timezone.utc)

snapshot = TemporalSnapshot(
    owner_scope="example-project",
    captured_at=utc(12),
    records=(
        TemporalFeatureRecord("example-project", "station-1", "reading", 10,
                              utc(8), utc(9)),
        TemporalFeatureRecord("example-project", "station-1", "reading", 12,
                              utc(8), utc(11)),
    ),
)
result = point_in_time_features(
    snapshot,
    owner_scope="example-project",
    entity_id="station-1",
    feature_names=("reading",),
    decision_time=utc(10),
)[0]
assert result.value == 10  # The correction was not available at 10:00.
```

This is a constructed fixture, not a sensor measurement. Historical timestamps
must come from trustworthy ingestion metadata before making leakage-free
claims about a real feed.

## Continuation protocol

1. Read the execution board and master plan; inspect `git status` before editing.
2. Run `check`, then `next`; inspect external prerequisites and exact scope.
3. Assign one bounded implementation owner and a distinct reviewer. Avoid
   overlapping file ownership and shared-state writes.
4. Preserve source, configuration, environment, dataset/model identities and
   actual command results. Keep unavailable/skipped checks explicit.
5. Update the board and relevant register entries only to the evidenced stage.
   Never infer completion from scaffolding or a successful bookkeeping test.
6. Preserve work in a Git checkpoint. After staging path additions, regenerate
   COMPACTIFICATION inventories and check their consistency. Follow existing
   fingerprint resealing rules if a registered asset is changed.

Do not store model weights, private corpora, API keys, runtime stores, or
machine-local environment paths in these planning files. No implicit external
upload, cloud fallback, training, or tool authorization is introduced here.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
