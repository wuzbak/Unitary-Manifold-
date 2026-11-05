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
| `tokenizer_interchange.py` | Canonical Unicode-scalar character tokenizer and actual P43 metadata layouts, preserving token-ID order and identity normalization | No BPE/SentencePiece, normalizer changes, added/special tokens, unknown replacement or universal losslessness. |
| `model_interchange.py` | Bounded inference NPZ -> original AZMQ with explicit lossy opt-in; reverse NPZ preserves reconstructed weights exactly and binds a tokenizer manifest | Not training-state interchange, model-quality qualification, runtime optimization or universal ONNX/GGUF translation. |
| `research_quality_audit.py` | Exhaustive audit of the original arithmetic fixture, split overlap and answer-label distributions | Confounding is measured; causation of model failure is not established. |
| `arithmetic_generalization.py` | Source-bound preregistration, actual answer-only P43 training and validation-selected inference checkpoint with immutable predictions | Both bounded attempts failed 0/30; the separate modulo-11 task also failed unseen-computation validation. No useful-model or 30/30 claim. |
| `p43_training_reference.py` | Independently written NumPy forward/reverse equations and stateful Adam comparison against every P43 parameter gradient and update, including positional wraparound | Constructed CPU float64 parity and failed-checkpoint training data only; no new holdout, external-framework parity or generalization pass. |
| `quantization_calibration.py` | Fixed six-group-size, validation-only calibration of the retained native model with complete sub-4-bit size accounting and unchanged relative-fidelity limits | The original test is exposed and diagnostic only; no native-weight training, fresh quality qualification or repaired 30/30 gate. |
| `checkpoint_bundle.py` | Bounded content-addressed opaque shards, manifest-as-commit publication, interrupted-write recovery and synchronized multi-process same/distinct bundle tests | One local POSIX directory; no semantic tensor/optimizer/RNG serializer, distributed transport, storage-service qualification or production durability. |
| `p43_checkpoint_bundle.py` | Actual bounded P43 NPZ split into exactly one model/Adam/PCG64 shard each; validated non-pickle reconstruction, exact next-step continuation, and local fresh-process restoration after writer termination immediately after commit | Constructed CPU float64 fixture and one local filesystem restart path; no arithmetic training quality, large training checkpoints, authenticated store, distributed workers, network storage, mid-commit interruption or power-loss durability. |
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

Product 40 additionally supports exact raw-response archival and explicit
network-free replay through its existing temporal CLI. Replay verifies source,
snapshot and byte bindings while retaining original observation time and origin;
constructed replay is not live-feed validation. See the
[capture and replay contract](../../12-AZ-IP/40-az-live-data-harness/README.md#exact-raw-response-archives).
All 21 capabilities remain open, and the 30/30 model-quality target is unchanged.

For the independent training implementation check (including every gradient,
Adam moment and updated weight), run:

```bash
python -m src.infrastructure.p43_training_reference \
  --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence \
  --checkpoint 9-INFRASTRUCTURE/az-ml-program/evidence/a01eda39d6c3edb942c619ea9f709fc46b46f5664b9c1c64abdffa0884ac5cdc.npz
```

The optional checkpoint comparison reads only its 81 declared training rows.
The other comparisons use constructed prompts, including context beyond the
74-position rotary period. No new test holdout is opened. The reference uses
separate explicit NumPy forward/reverse equations, not P43 autograd or an
external ML framework. CPU float64 implementation parity is not arithmetic
generalization and cannot turn the recorded 0/30 outcomes into passes.

To measure calibration without using the exposed test to select a candidate:

```bash
python -m src.infrastructure.quantization_calibration \
  --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence \
  --checkpoint 9-INFRASTRUCTURE/az-ml-program/evidence/979847638ed7ec97277a0f5023515192779fc369050963048a12e0300fd8ede3.npz
```

The immutable protocol precedes all validation measurements. Only artifacts
below four complete bits/parameter and passing the unchanged validation
tolerance are eligible; the smallest byte representation wins. A missing
eligible candidate is an explicit negative outcome, not a fallback. Only after
selection is fixed are native and selected-model historical-test diagnostics
computed. CLI exit zero means measurement/publication, not model qualification.

The local checkpoint recovery fixture is separately runnable:

```bash
python -m src.infrastructure.checkpoint_bundle \
  --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence
```

The manifest is the only commit point; staged shards alone are not loadable as a
checkpoint. The current storage bounds are 2--64 shards, 256 MiB per shard, 1 GiB
total and a 64 KiB manifest. Shard roles describe opaque bytes, not validated
tensor/training-state schemas. Caller scope strings are assertions, not
authentication. Role subsets/repetitions are permitted; only the fixture has
one shard of each role. Checkpoint IDs are descriptive: different bytes yield
different manifest IDs, not a conflicting unique-name update or latest pointer.
Parent directories above the established store are trusted. Individual shard
publication and the manifest share one
validated directory descriptor; concurrent pathname replacement cannot split
one commit across directories. A returned pathname remains advisory if that
directory is moved. Neither a passing local fixture nor `fsync` establishes
multi-host, network-storage or hardware-crash durability.

The P43 adapter preserves the existing non-pickle model checkpoint format and
requires all three roles exactly once. It rejects optimizer/RNG loss, validates
config, parameter names/shapes, finite float64 weights and moments, exact PCG64
state, bounded ZIP/NPY headers, and a cross-shard content binding before
reconstruction. For the actual numeric resume receipt, it saved a 719-parameter
P43 model after three Adam updates, reloaded it from the committed shards, and
matched the uninterrupted next minibatch, logits, loss, all parameters and Adam
moments, hyperparameters/step, and PCG64 outputs/state exactly. This is a
constructed CPU fixture, not evidence from arithmetic training, an OS process
restart, distributed training, or model utility. Run the exact fixture:

```bash
python -m src.infrastructure.p43_checkpoint_bundle \
  --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence \
  --owner-scope research:checkpoint-fixture
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

## Supported interchange, not universal conversion

The character-tokenizer IR supports exactly one Unicode scalar per token,
identity normalization, no added/special tokens and explicit unknown-character
errors. Vocabulary order is token-ID order; it is never silently sorted.
Composed and decomposed Unicode remain distinct. The P43 text-workflow and
research-checkpoint metadata dialects are supported. Standalone conversion
accepts canonical `az_character` or `p43_metadata` JSON; learned segmentation
and semantic overrides fail explicitly. Losslessness means the mapping and
supported encode/decode behavior, not identical JSON whitespace or unrelated
metadata.

```bash
python -m src.infrastructure.tokenizer_interchange \
  --source /path/to/character-tokenizer.json \
  --source-format p43_metadata --target-format az_character \
  --output-dir /existing/durable/evidence

python -m src.infrastructure.model_interchange \
  --source /path/to/inference-model.npz \
  --source-format p43_npz --target-format azmq --allow-lossy \
  --output-dir /existing/durable/evidence
```

The model translator reads the tokenizer from the actual source checkpoint
and publishes the model, canonical tokenizer and binding/weight-error manifest.
Without `--allow-lossy`, quantization is refused. Training optimizer/RNG state
is also refused, not silently discarded. NPZ member/expanded-size limits and
the existing model-parameter budget are checked before model construction.

For the reverse direction, use `--source-format azmq --target-format p43_npz`
and explicitly supply `--tokenizer /path/to/canonical-tokenizer.json`, without
`--allow-lossy`. AZMQ has no embedded tokenizer; supplying one asserts its
semantic binding, not authenticated provenance. Reverse conversion preserves
the **already reconstructed** weights, not the original prequantization values.
Original task metadata and training resume are not preserved. Files are
individually atomic, not one publication transaction; errors propagate even
when earlier verified files remain. No implicit training/download or runtime
optimization occurs.

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
