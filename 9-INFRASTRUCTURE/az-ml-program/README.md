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

## Original CPU reference libraries

These are working algorithm/reference packages, not finished model services:

| Module under `src/infrastructure/` | Supported, testable behavior | Explicit boundary |
|---|---|---|
| `lowbit_quantization.py` | Symmetric/asymmetric groupwise 2/3/4-bit packing, checksummed artifacts, error and complete serialized-size metrics | Flat numeric vectors; quantization is lossy; no transformer/CUDA speed claim. |
| `research_quantization.py` | Actual trained P43 model -> complete packed artifact -> fresh-model load -> fixed held-out comparison, with explicitly requested immutable model/evidence publication | Local constructed arithmetic only; baseline task generalization and 3-bit quality tolerance failed. |
| `vector_index.py` | Exact cosine/L2 search, pinned manifests, deterministic ties, immutable generations, retrieval evaluation | No ANN or learned encoder; old saved generations need explicit purge. |
| `repository_vectors.py` | Existing RAG chunks converted to a source-verified word-count baseline; changed sources block retrieval | Lexical, not semantic; source/chunk identity is not entailment. |
| `drift_monitor.py` | Tied empirical KS statistic, conservative single-comparison DKW bound, temporal sampling and constructed replay | IID assumptions; no repeated-monitoring or prediction-performance guarantee. |
| `data_lineage.py` | Content-addressed closed lineage DAGs, owner/origin checks, parent-kind validation and advisory deletion closures | Not execution proof, certified rights, DVC integration, artifact deletion or model unlearning. |
| `performance_profile.py` | Warmed repeated wall/process-CPU samples, nearest-rank p50/p95 and Python allocation peaks with hardware observations | Includes profiler/process overhead; not native/GPU memory or serving-latency measurement. |
| `research_serving.py` | Persistent P43 weight snapshot, incremental per-layer KV reuse, true heterogeneous-length CPU batches, bounded round-robin scheduling and explicit cancellation/deadlines | Causal toroidal P43 only, not a network server or paged GPU backend; owner strings are not authentication. |
| `artifact_io.py` | Atomic no-overwrite publication, identical-content retries, file and directory synchronization | Caller-established POSIX directory; no distributed durability claim. |

Run the measured acceptance fixtures, rather than inferring performance from a
test count:

```bash
python -m src.infrastructure.ml_reference_benchmarks
```

For an immutable JSON receipt, supply `--output-dir` with an **existing durable
directory**. The report pins source identities, records actual CPU timings and
checks declared numerical/retrieval/replay thresholds. Its low-bit experiment
includes metadata and checksum in the effective bits/weight calculation.
Three orthogonal synthetic vectors are an exact-search oracle, not a practical
retrieval-quality benchmark. The RAG integration additionally exercises two
declared queries over actual source-verified repository documents and a
no-overlap query. None authorizes capability/deployment promotion.
The low-bit workload is also profiled for five measured repetitions after one
warmup; those timings are observations, not an isolated-host speedup claim.

## Research serving, not production serving

The steward authorized a local research baseline when no tracked trained model
was found. `research_quantization` fixes the original 100-example arithmetic
fixture, character vocabulary, 60/10/30 train/validation/test partition, seed,
architecture, 160 optimizer steps, calibration and relative tolerance before
evaluation. No test/validation examples train the model or fit the quantizer.

**The negative results are part of the deliverable:** the native model answers
**0/30 held-out arithmetic questions correctly**. Its 58.7% teacher-forced token
accuracy largely reflects formatting and must not be presented as arithmetic
competence. The complete 3-bit model reaches **3.3966 total bits/parameter** but
fails its declared relative-quality tolerance: token cross-entropy rises from
2.1218 to 2.8874 nats. The 4-bit reference preserves the declared relative
tolerance but occupies 4.3979 total bits/parameter and does not fix the poor
baseline. FP16-roundtrip means rounded weights evaluated in float64, not FP16
kernels. Do not tune against this now-exposed test split.

To reproduce and explicitly persist the original tiny synthetic baseline,
packed 3/4-bit models and source-bound quality report:

```bash
python -m src.infrastructure.research_quantization \
  --output-dir /existing/durable/evidence \
  --checkpoint-dir /existing/durable/evidence \
  --artifact-dir /existing/durable/evidence
```

Quality failure is recorded inside the measured report rather than discarded.
A zero CLI exit means the measurement/publication completed, not that quality
passed. Promotion is always disabled. Packed artifacts include config, stable
parameter names/shapes and checksums; the packed loader rejects inconsistent or
over-limit models before dense reconstruction/model allocation. Its limit is one
million parameters, not a general large-model loader.
The checkpoint, packed variants and report are individually atomic files, not
one transaction. A publication failure propagates and may leave previously
verified files; it must not be reported as a successful complete bundle.

The in-process `ResearchServingSession` is a backend execution component under
the existing spine, not a second control plane or an exposed HTTP endpoint.
An authorized caller submits vocabulary token IDs under its explicit scope,
then drives `tick()`, `result()`, `cancel()` and `forget()`. No model download,
training, tool invocation, cloud fallback or effect authorization happens here.

The decoder copies weights once so later training cannot mutate an active
session. One CPU batch processes one token per selected request; prompts are
prefilled incrementally and generated steps reuse actual per-layer keys and
values. Padded positions are masked, and tests compare against the existing
full-prefix P43 model, including positional wraparound. Model/context/shape and
unsupported-architecture errors fail explicitly.

Admission reserves the maximum retained KV payload before queuing, while
allocated payload grows with consumed tokens and is released on completion,
cancel, expiry or reported numerical failure. The byte limit does **not** cover
the model, staging copies, padded scratch, Python overhead or process RSS.
Active requests are rejected rather than silently evicted when reservations
are exhausted. Retained terminal results are bounded by request capacity and
must be explicitly forgotten. The scheduler is single-threaded; cancellation
and deadlines are checked between CPU calls, not preemptively inside them.

Measure an existing supported P43 checkpoint without implicit training:

```bash
python -m src.infrastructure.research_serving_benchmarks \
  --checkpoint /path/to/research-model.npz \
  --output-dir /existing/durable/evidence
```

For an original packed artifact, replace `--checkpoint` with
`--quantized-model /path/to/model.azmq`. That reconstructs float64 weights before
serving; it does not introduce low-bit execution kernels or reduced runtime
weight-memory claims.

The fixed token-ID trace compares full-prefix outputs, cached serial decoding
and true continuous batches. It checks every prefill logit and generated token,
reports actual CPU observations across warmed repetitions and counts evaluated
token rows/backend calls. Any slower case remains in the receipt. Token parity
is not semantic model quality, a production load test or a universal speedup.

Product 40 now exposes an actual transport-to-temporal adapter via its CLI and
HTTP API; see its
[guide](../../12-AZ-IP/40-az-live-data-harness/README.md#temporal-capture-and-historical-replay).
Injected HTTP tests are labeled constructed data. Network reachability is
assessed separately and must never be replaced with a fixture called live.

Focused validation uses the repository's existing pytest runner:

```bash
python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/ -q
```

The underlying data implementation is `src/infrastructure/temporal_data.py`.
It provides a local snapshot/replay foundation. The separate Product 40 adapter
connects its existing USGS transport and preserves local observation times.
Each capture also links the exact response hash to the temporal snapshot through
a code/config-pinned lineage graph. The original raw response is not retained
by this adapter, so its hash alone is not a replay archive.
The primitive itself is **not** a distributed store or serverless service. Consult
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

Do not store external model weights, private corpora, API keys, runtime stores,
or machine-local environment paths in these planning files. The explicitly
labeled tiny original synthetic research checkpoint and its packed variants
are preserved under `evidence/`, with source/tokenizer/split identities and the
P43 AGPL license context. They are not downloaded application-model weights.
No implicit external
upload, cloud fallback, training, or tool authorization is introduced here.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
