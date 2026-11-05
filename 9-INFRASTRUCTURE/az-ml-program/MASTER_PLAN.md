# AxiomZero ML master plan

**Authorized scope: all 21 capabilities. Started: 2026-11-05.**

The steward requested an expert-assisted, complete program and explicitly asked
that none of the planning or implementation work be lost. All capabilities
remain in scope; sequencing is not cancellation. This document preserves the
architecture and decisions. The adjacent JSON register preserves workstream
dependencies and gates; the execution board preserves the current handoff.

## 1. Architecture and boundaries

Build one coherent platform inside existing product ownership:

```text
PC Suite / Browser / Journalist / scientific and domain products
                           |
        PsiCat control plane: identity, policy, approvals, budgets
                           |
        Existing execution spine: artifacts, receipts, promotion
                           |
       +-------------------+-------------------+
       |                   |                   |
 Agent / retrieval     Model execution    Governed data assets
 memory, RAG, tools    serving, batching  snapshots, features,
 vector search         compression       indexes, checkpoints
       +-------------------+-------------------+
                           |
         Cross-cutting evaluation, monitoring and rollback
```

Canonical constraints come from
`9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md:27-35,78-95,136-145`.
Reuse `src/infrastructure/execution_spine.py:170-228`; extend its referenced
payload schemas only where necessary. Do not introduce a parallel controller,
tensor framework, product-status ledger, or automatic authority.

The capability register tracks **program deliverables**, not deployment
promotion or scientific truth. Production promotion remains separately governed.

Keep the two model lanes explicit:

- **Research:** Product 43's NumPy toroidal transformer. Compare architecture
  changes against conventional positional mechanisms with matched resources.
- **Applications:** pinned, supported pretrained backends supplying practical
  language capabilities through governed execution.

These lanes can share artifact/evaluation contracts but are not interchangeable.
No physics-derived speed, alignment, or reasoning advantage is assumed.

## 2. Expert consultation and observed starting point

Three specialist helper agents examined runtime engineering, data/assurance,
and actual local PsiCat/RAG tool use. The runtime specialist also challenged
the integrated ordering. This was source assessment and bounded retrieval,
not independent empirical validation of all products.

Actual local consultation performed during planning:

- `RAGIndex.build(repo_root=Path.cwd())` indexed 1,893 chunks;
  `search("PsiCat control plane execution spine", top_k=3)` retrieved portfolio,
  Product 20 and Weave context.
- Product 34 materials/spectroscopy experts built 71/37 documentation chunks.
  Their ML-architecture queries produced weak keyword overlaps, not expert
  architecture advice.
- `python -B 12-AZ-IP/44-axiomzero-weave/run.py query
  'PsiCat execution spine control plane reflective memory' --limit 3`
  and its `capabilities` command returned grounded retrieval with
  `model_inference=false`, `effects_authorized=false`, `persisted=false`.
- Normal PsiCat imports initially failed on missing `httpx`. Standalone
  interrogator/local-provider calls were possible, but the provider assembles
  deterministic text. No independent PsiCat model reasoning was obtained.

Source-based findings that shape implementation:

| Asset | Reusable starting point | Boundary |
|---|---|---|
| P20 PsiCat | Control plane, retrieval, memory and tool adapters | Import availability and reasoning quality need separate verification. |
| P44 Weave | Existing evidence/memory/computation composition; spine receipts | Local owner boundaries are not production authentication. |
| P01 Axiom OS | Persistent agent state and resource admission | Persistence is not validated reflective learning. |
| P43 Tori Transformer | Custom autograd, dense attention, local checkpoints | Float64 NumPy research model, not sparse/low-bit serving. |
| P45 PC Suite | Pinned backend lifecycle and desktop integration in source | Shipping success and quality are not established by wiring. |
| P21/P40 | Public-feed ingestion and harness patterns | No demonstrated point-in-time feature store. |
| P03 EIGE | Reproducible domain synthetic workloads | No established general synthetic-data fidelity/privacy. |
| P32 | Capacity/debt accounting | Not statistical prediction drift. |
| P26/P38/P39 | Regression receipts, bounded constraints, debt tracking | Not universal safety, authenticity or deployment certification. |

Important evidence pointers:

- P43 `az_tori_transformer/tensor.py:34-45`,
  `attention.py:99-123`, `checkpoint.py:115-140`.
- P45 `main.cjs:659-678`, `lib/instruction-model.cjs:511-533,601-605`.
  This source integration supersedes the older P43 README statement that
  Product 45 has not integrated the candidate; neither proves a shipped build.
- P44 `az_weave/receipts.py:9-26`; README `:48-50`.
- P16 `oracle/engine/multi_model_consensus.py:34-55`: hash-driven simulation
  is not independent-model agreement.
- P32 `az_phi_debt_early_warning/debt_monitor.py:92-149`.
- P40 `az_live_data_harness/harness.py:25-54,79-121`.

Exclude prototype kernel filesystems as durable checkpoint foundations.
P05 `UOS/filesystem.py:123-133,176-180,273-332` uses in-memory storage,
a 74-key addressing scheme and incomplete missing-shard reconstruction.
P02 `src/fs/mod.rs:21-38` is a RAM filesystem; P35's adapter is not storage
transport. This is a dependency exclusion, not authorization for an OS rewrite.

## 3. Complete workstream map

Numbers preserve the steward's original 21-item list. Owners below are proposed
engineering roles, not assertions that personnel or infrastructure are assigned.

| # | Capability | Canonical integration / engineering owner | First deliverable and graduation requirement |
|---|---|---|---|
| 1 | Own sub-4-bit quantization | Model optimization; P43 research and supported application adapters | Packing/calibration reference, effective bits including metadata, quality ceiling and separately measured runtime benefit. |
| 2 | Serving with dynamic KV | Runtime; PsiCat and P45 backend lifecycle | Persistent backend, budgeted KV accounting, ownership, eviction, cancellation and cache/reference parity. |
| 3 | Intelligent dynamic batching | Runtime scheduler behind existing control plane | Trace-driven policy and concurrent requests; throughput gains without declared tail-latency/memory violations. |
| 4 | Sparse CUDA kernels | Accelerator engineering; profiled model operators | Explicit useful sparsity, CPU reference, hardware support matrix and end-to-end benefit over tuned dense baselines. |
| 5 | Distributed checkpoint storage | Artifact infrastructure; P43 checkpoint adapter | Verified manifests, atomic local publication, established remote-storage adapter; multi-client failure recovery before distributed claims. |
| 6 | Reflective-memory agents | Agent engineering; P01/P20/P44 | Scoped observations/hypotheses/decisions with source, correction, expiry and restart replay. Reflection cannot silently rewrite trusted facts. |
| 7 | Vector indexing | Retrieval engineering; P20 and corpus consumers | Exact-search reference, labeled workload, approximate-index comparison, deletion and isolation semantics. Novel algorithms need measured value. |
| 8 | Self-healing RAG | Retrieval engineering; P20/bot/P44 | Failure classification and bounded repair with citation support, negative-query handling and unchanged authority boundaries. |
| 9 | Safety/alignment evaluation | Assurance; P20/P22/P26 | Frozen task-specific benign/adversarial suites measuring utility, abstention, attack success and escalation; no universal alignment claim. |
| 10 | Lossless tokenizer converter | Model interoperability | Preserve tokenizer assets and publish supported equivalence classes. Reject unsupported conversions; arbitrary universal equivalence is impossible. |
| 11 | Serverless real-time feature store | Data engineering; P21/P40 then measurement products | Event/availability-aware replay, online/offline parity, freshness and cold-start-inclusive serving evidence. Actual model consumers must be identified. |
| 12 | Domain-adaptive synthetic data | Data/model engineering; P03 first | Seeded generators, ancestry, split isolation and downstream utility on untouched real holdouts, with applicable privacy evaluation. |
| 13 | Prediction drift detection | Monitoring; P21/P40 and later model consumers | Separate quality/distribution/prediction/performance detectors with false-alarm and delay evidence; label absence remains explicit. |
| 14 | Data versioning and feature lineage | Data/artifact infrastructure | Snapshot -> transform -> feature -> run -> model/index -> deployment lineage, rights and deletion propagation. Reuse existing DVC/provenance where suitable. |
| 15 | Adversarial defenses | Assurance/security integration; P22/P20 | Threat-scoped prevention/detection and measured attacks, including poisoned retrieval and cross-owner access; no attack-proof label. |
| 16 | Fairness auditing | Assurance with domain steward | Defined decisions/harms, lawful group data, intersectional sample sizes, uncertainty and domain-approved tolerances. |
| 17 | GPU explainability | Model interpretability/accelerators | Faithful CPU/reference explanations first; perturbation/randomization checks, then GPU parity and measured acceleration. |
| 18 | Hardware-aware profiling | Runtime observability; P01/P45 | Actual workload memory, latency, throughput and contention; hardware inventory is not a performance result. |
| 19 | Modular RL environments | Agent research; P20 test environments | Versioned observations/actions/rewards, deterministic replay, seed variance, baseline, termination and operator override. Production learning separate. |
| 20 | Optimizing model translation | Model interoperability; P43/P45 adapters | Versioned architecture/format support matrix; distinguish serialization, quantization, optimization and distillation. Unsupported cases fail explicitly. |
| 21 | Multimodal vector database | Data/retrieval; P41 extraction plus P20 consumers | Shared asset/index lifecycle with modality-specific encoders, aligned retrieval evaluation, access/deletion and generation-safe rebuilds. |

All remain committed program scope even when dependencies or hardware block
execution. Building "our own" means owning the implementation and differentiated
algorithms; baseline adapters establish fair comparisons, not permanent surrender
of the original-library ambitions.

## 4. Dependency-driven delivery

### A. Truth, contracts and baseline

Persist all capabilities and inspect actual code. Define source-bound readiness,
workload identities and non-claims. Extend the spine minimally. Establish held-out
evaluation and resource measurements before optimizations.

### B. Two independently promotable vertical slices

**B1: governed evidence assistant.** One pinned model/tokenizer/backend, one
permitted corpus, scoped retrieval/memory, and one bounded approved tool
operation through PsiCat. Specify who approves, executes, cancels and records.
Test relevant/negative queries, supported citations, restart, refusal, failure
and unavailable backend behavior. Citation existence is not entailment or
authorization. Missing full inference blocks promotion.

**B2: temporal data replay.** P21/P40 feed snapshots and availability-aware
transforms, then a clearly identified predictive consumer. First verify local
deterministic replay, late corrections and data-quality monitoring; connect
live feeds separately. Prediction-performance drift requires actual outcomes.

The initial temporal module is a foundation for B2, not completion of B2 or
capabilities 11/13/14.

### C. Runtime and retrieval consolidation

Runtime: profile baseline -> persistent serving -> KV accounting/isolation ->
continuous batching. Retrieval: manifest corpus/encoder -> exact baseline ->
approximate index comparison -> bounded retrieval repair -> multimodal expansion.

Do not require a novel quantizer or CUDA kernel before useful serving. Do not
make a whole capability's final completion a prerequisite for exploratory work
on its consumers: minimal validated interfaces can enable bounded stages.
The register's dependency edges gate capability integration/validation, not
initial research. The execution board can authorize a bounded early-stage
package while those edges remain unfinished; `next` does not replace that board.

### D. Original algorithms and controlled experiments

Compare low-bit calibration, scheduling, indexing, toroidal architecture and
domain generation against named conventional baselines with matched workloads.
Keep real holdouts untouched. Report negative results and discontinue individual
approaches without deleting the capability from the program.

### E. Scale and deployment qualification

Add distributed storage, serverless deployment, GPU XAI, larger multimodal stores
and RL training when workload and resource evidence justify them. Require
failure recovery, rollout/rollback, retention, deletion, compatibility and
operational ownership. Set calendar/budget after hardware and staffing are known.

## 5. Shared contract references

| Contract | Minimum fields / invariants |
|---|---|
| Model | Weights, architecture, tokenizer, precision, backend, license and evaluation identities; supported operations explicit. |
| Asset | Immutable identity, owner/scope, rights/purpose, schema/units, event and availability time, real/synthetic/fallback origin, parent assets, deletion state. |
| Transform/run | Inputs, code/environment/config identity, outputs, split policy, generator/model revision and receipts. |
| Index | Corpus snapshot, encoder revision, tokenizer/chunker/preprocessing, dimension/normalization/metric, access scope and generation. |
| Feature | Entity/key, event/availability semantics, transform version, TTL/freshness, missingness and correction policy. |
| Execution | Request/owner, approval, budget/deadline/cancellation, backend configuration, effects, outputs and failures. |
| Evaluation | Immutable model/data IDs, scenarios/groups, labels, metrics/uncertainty, predeclared thresholds, environment/hardware, skipped/unsupported status. |

Content hashes establish identity, not truth, consent, entailment or model
unlearning. Preserve isolation through retrieval, reranking, caching and logging.
Encoder changes require compatible generation rebuilds, not silent index reuse.

Third-party feed/model/tokenizer licenses remain controlling. Public visibility
does not grant unlimited training rights. Propagate deletion to derived stores;
state backup retention and already-trained-model limitations explicitly.

## 6. Evaluation and promotion gates

| Area | Evidence required before the corresponding claim |
|---|---|
| Low-bit | Effective bits including mixed-precision exceptions; held-out quality loss; measured peak memory; runtime assessed separately. |
| Serving | Cold/warm and first-token latency, throughput, p50/p95, concurrency, overload, cancellation, bounded memory and cache isolation. |
| Retrieval | Recall/ranking against labels and exact reference, supported citation entailment, negative queries, freshness, zero unauthorized results in the tested scenarios. |
| Features | Golden historical joins, no unavailable/future records, replayable corrections, online/offline parity and cold-start-inclusive freshness. |
| Drift | Stationary false alerts, declared shift size, detection delay, missing labels and calibration limitations. Thresholds set before the run. |
| Synthetic | Source/entity/time splits before fitting, derivative deduplication, untouched real holdouts, ancestry and applicable memorization/privacy measurements. |
| Fairness | Defined harms and groups, sample sizes/uncertainty, unknown membership, underpowered results withheld; no generic fairness badge. |
| XAI | Defined model/output/baseline, completeness/perturbation and model-randomization tests; GPU/reference parity. |
| Checkpoints | Verified content, supported-state restoration, interrupted writes, and multi-client/failure tests before distributed claims. |
| RL | Versioned environment/reward, replay, seed variance, baseline and termination/override tests before training promotion. |

Program stages and capability completion are not production status. Unit tests
of this register validate bookkeeping only. Inspection of existing test code is
not a passing-run receipt. No experimental ML infrastructure promotes physics
claims, hardgate pillars, product TRLs or legal compliance.

## 7. Team and handoff discipline

Use bounded implementation owners, source-retrieval helpers, a distinct
challenger/reviewer, and a human domain steward for consequential decisions.
PsiCat routes approved activity; RAG retrieves evidence; Weave composes existing
strands; UM-ARTS preserves scoped regression evidence. None is automatically an
independent scientific expert because its name appears in a tool registry.

Each package requires explicit file ownership, objective, prerequisites,
acceptance command, stop condition and handoff. Avoid concurrent edits to the
same files or shared runtime. Multiple agents sharing assumptions are not
independent empirical confirmation.

Preserve actual outcomes in the execution board, with exact commands and
limitations. Keep runtime/private artifacts outside Git. Checkpoint source,
tests, register and documentation together; regenerate staged-path inventories.
Never replace missing inference with a deterministic responder labeled reasoning.

## 8. Earned continuation milestones and remaining integrations

The second tranche implements original CPU references rather than only adding
plans. Capability identities and their full acceptance gates remain unchanged:

| Capabilities | Implemented, bounded milestone | Still required for the full ambition |
|---|---|---|
| 1 | Original packing plus complete P43 model format, trained synthetic baseline and fixed held-out native/FP16-roundtrip/3-bit/4-bit comparison; exact artifacts retained | Native answer accuracy 0/30 and 3-bit relative-quality gate failed; establish useful model generalization, new untouched holdout, independent quantizer baseline and accelerator evidence |
| 2/3 | Actual persistent P43 CPU decoder with incremental per-layer KV, true heterogeneous-length vectorized batches and bounded round-robin scheduling; full-prefix parity and owner/cancel/expiry checks | Pinned application backend through existing approvals, authenticated concurrency, representative arrivals, native/GPU peak memory, paged policy and production serving |
| 10/20 | Exact supported Unicode-scalar tokenizer interchange and actual bounded P43 NPZ/AZMQ inference conversion, with explicit lossy opt-in and exact reverse reconstruction | Pinned external segmentation/operator matrix, independent runtime comparison, licensed application models and measured optimizations; no universal conversion claim |
| 7/8 | Exact pinned vector generations plus a source-hash-verified adapter around actual bot RAG chunks; stale-source and no-overlap rejection | Learned encoders and labeled retrieval evaluation, ANN comparison, authorized repair execution and rollback |
| 11/14 | Actual P40 transport -> availability-aware snapshot -> source-linked DAG through CLI/API; immutable local publication with explicit errors | Network-enabled live run, retained raw-payload replay, predictive consumer, feature/run/model/index consumers, DVC interchange and serverless qualification |
| 13 | Exact tied empirical KS plus conservative two-sample union-DKW bounds and seeded stationary/shift replay | Real predictions and outcomes, delayed-label performance drift, repeated-monitoring error policy and operational response |
| 18 | Actual warmed wall/process CPU samples, nearest-rank percentiles and Python allocation peaks, integrated with the quantizer workload | Native-memory/hardware-counter adapters, representative pinned serving workloads, synchronized GPU evidence and validated bottleneck attribution |

`src/infrastructure/ml_reference_benchmarks.py` measures declared numerical,
retrieval, lineage and drift fixtures and records source identities inside the
existing spine. Synthetic weights, three-axis retrieval and Gaussian replay are
explicitly constructed fixtures; the repository RAG queries use actual checked
sources but are not a semantic-quality benchmark.

The local public-feed attempt failed DNS with an explicit error. No fixture was
substituted and no live ingestion success is claimed. A manifest records claimed
ancestry and content identities; it does not establish truth, rights, execution
or actual deletion. POSIX publication is not a distributed checkpoint system.

The execution board retains the interrupted first regression, the subsequent
single-failure regression and its tightly coupled inventory fix. Canonical
UM-ARTS selection now includes the ML reference suite and all P40 tests;
unknown infrastructure tests remain unclassified. CI adds these focused checks
without weakening the core release gate.
The replacement unfiltered core run completed with **62,077 passed, 71 skipped,
zero failed and zero deselected**. That clears the prior incomplete-core blocker
for this checkpoint, not the remaining capability/deployment gates.

The steward subsequently selected an existing tracked trained checkpoint if
available, otherwise an explicitly labeled local research baseline. No tracked
NPZ, NPY, safetensors, PT/PTH or GGUF checkpoint was found. The next research
experiment therefore uses original constructed data and the existing P43
architecture, not a secretly downloaded model or a deterministic responder
called language inference. Frozen held-out quality and representation
measurements must be distinguished from actual FP16/CUDA execution.
That experiment has now run: all 39,293 trained parameters occupy 16,683 bytes
in the complete 3-bit container, or 3.396635533 bits/parameter, but its quality
tolerance failed. Native task generalization also failed: 0/30 held-out answer
digits correct. Relative preservation of an inadequate baseline is not model
utility. Preserve these results and do not retune on the exposed test examples.
The exact synthetic checkpoint and both packed variants are retained.

The serving slice consumes either that NPZ checkpoint or the original packed
model and runs real incremental KV decoding and heterogeneous vectorized
batches. Full-prefix reference outputs are preserved. This establishes
research-backend parity and measurable scoped CPU work, not production serving,
semantic quality, authenticated control-plane integration or low-bit kernels.

The next tokenizer/model tranche preserves semantic boundaries instead of
silently converting incompatible assets. It retains token-ID order, distinguishes
normalization and special-token semantics, rejects unsupported formats, and
refuses optimizer/RNG loss. NPZ NPY headers are inspected before NumPy allocation,
not merely after ZIP size checks. Reverse quantized-model conversion restores
only the already reconstructed weights; no format translator can recover
information discarded by quantization. Receipt source/model/tokenizer hashes
bind this supported pair without asserting quality or runtime optimization.

The steward has now set an explicit target: **30/30 on a fresh preregistered
holdout**, with the original 30 kept as a diagnostic only. This does not authorize
test-set training, answer lookup presented as model inference, threshold changes,
or declaring a symbolic solver a learned language model. Diagnose the existing
split and training objective, freeze a new experiment before seeing its test
outcomes, and report any failure to meet 30/30 unchanged.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
