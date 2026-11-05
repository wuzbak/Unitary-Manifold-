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

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
