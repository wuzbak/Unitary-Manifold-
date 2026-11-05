# AZ ML execution board

**Program opened: 2026-11-05. Scope: all 21 capabilities.**

This board is a durable work handoff under the existing execution spine, not a
deployment status authority. No capability is production-qualified by this
launch. See [the master plan](MASTER_PLAN.md) and [the register](capabilities.json).

## Launch tranche (historical)

| Package | Owner role | State | Deliverable / limitation |
|---|---|---|---|
| Expert architecture and tool consultation | Runtime, data/assurance, PsiCat/RAG helpers plus coordinating engineer | Assessed | Findings and actual retrieval outcomes preserved in the master plan; not a performance benchmark. |
| Complete program preservation | Coordinating engineer | Written | All 21 workstreams, dependencies, gates, ownership and resumption instructions. |
| Executable program inventory | Capability-register helper | Implemented and focused-tested | Validated JSON register and read-only CLI projecting planning evidence into the existing spine. |
| Temporal snapshot/replay foundation | Temporal-data helper | Implemented and focused-tested | Local immutable snapshots and scoped event/availability-time selection; live adapters, feature service and drift not claimed. |
| Independent implementation review | Reviewer separate from builders | Findings addressed | Added directory synchronization and explicit integration dependencies; final focused suite passed. |
| Validation and Git checkpoint | Coordinating engineer | Committed and pushed | Source/tests/docs preserved in the first checkpoint. Full core regression was incomplete and remained a release blocker at that checkpoint. |

## Environment and baseline

Initial default-Python command `python -m pytest tests/ -q` could not start:
`No module named pytest`. System installation was rejected by the managed
environment. An isolated validation virtual environment was therefore created
outside the repository; no system Python overrides were used.

Subsequent baseline attempts exposed missing `numpy`, then `httpx`. Installing
pytest, numpy, scipy and httpx into the isolated environment allowed collection
to proceed. The next `python -m pytest tests/ -q` attempt stopped at **13
collection errors**, including missing PyYAML and SymPy, with 22 skipped and 36
deselected. These are environment-blocked attempts, not passing regressions.

The inspected host had two available logical CPUs, no NVIDIA device nodes and
no `nvidia-smi`/`nvcc` on PATH. No GPU, distributed, serverless or production
performance result is claimed.

## Launch validation receipts (historical)

Commands below use the isolated validation environment's `python` where pytest
is needed. No environment-specific absolute paths are required by the source.

| Command | Actual outcome / scope |
|---|---|
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/test_program.py -q` | Final builder run: 109 passed. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/test_temporal_data.py -q` | Final builder run: 21 passed, including publication order and synchronization-failure propagation. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/ COMPACTIFICATION/test_maps.py tests/test_execution_spine.py -q` | Final integrated run: 152 passed. Covers local foundations, existing spine compatibility and generated-map consistency; not full capability completion. |
| `python -S -m src.infrastructure.ml_program check` | Passed; 21 entries, promotion ineligible. Confirms standard-library-only CLI. |
| `python -S -m src.infrastructure.ml_program next` | Passed; planning candidates expose external prerequisites and `execution_ready: false`. |
| `python TOOLS/audit/check_internal_links.py` | Passed: 2,053 Markdown files, all internal file links resolved on initial launch audit. |
| `python -m pytest recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` | 3,404 passed, 3 skipped. |
| `python -m pytest tests/ -q` | After restoring observed missing dependencies, execution progressed to approximately 42% and was stopped before completion for this bounded foundation tranche. No complete core result is claimed; rerun to completion before merge/release qualification. |
| `python COMPACTIFICATION/build_maps.py --check` | Passed after staging the new paths and regenerating the inventory. |

## Continuation tranche: original references and connected data

Separate specialist builders implemented low-bit packing, exact indexing,
distribution monitoring, lineage and real CPU profiling. A distinct reviewer
examined the integration and found no significant remaining issues in its
reviewed scope. The coordinator connected existing RAG and P40 transport,
consolidated publication, and repaired the actual regression failure below.
Expert review is not a production or scientific certificate.

| Delivered package | Earned, bounded result | Remaining boundary |
|---|---|---|
| Original low-bit reference (1) | 2/3/4-bit symmetric/asymmetric groups, cross-byte packing and verified format. The declared 32,768-value 3-bit fixture occupies 13,227 bytes: **3.229248046875 total bits/weight**, max error 0.16666666666666663. | Constructed flat weights, not trained-model quality or runtime benefit. |
| Exact vectors and existing RAG (7/8) | Exact cosine/L2, pinned generations and evaluation; source-verified adaptation of actual bot RAG, stale-source rejection and no-overlap abstention. | Three-axis oracle and two repository queries do not qualify semantic retrieval; no ANN or governed repair executor. |
| Connected temporal capture (11/14) | Existing USGS transport wired through P40 CLI/API into availability-aware snapshots and code/config-pinned source-to-snapshot lineage. | Live attempt failed DNS explicitly; no raw archive, authenticated scope, serverless service or predictive consumer. |
| Original lineage and publication (14) | Closed content-addressed DAGs, owner/origin/parent constraints, immutable POSIX publication and advisory deletion closures. | Rights are assertions; snapshot/graph files are individually atomic, not one transaction; no actual deletion, DVC integration or unlearning. |
| Distribution monitoring (13) | Exact tied KS with conservative union-DKW bounds; declared seeded replay yielded 0/20 stationary false alerts and 20/20 detections of a +3 Gaussian shift. | Constructed IID, single-comparison reference; no repeated-monitoring guarantee or labeled performance-drift evidence. |
| Actual CPU profiling (18) | One warmup/five measured quantization calls, wall/process CPU samples, nearest-rank p50/p95 and Python allocation peaks; no retained callable outputs. | Process/profiler overhead and concurrent regression are included; not isolated performance, native/GPU memory or serving-latency evidence. |

The immutable measured receipt is
[`evidence/a335542da4f1a7c17bf6a9f058652f06c23772d263e912084c3a2ced1630be02.json`](evidence/a335542da4f1a7c17bf6a9f058652f06c23772d263e912084c3a2ced1630be02.json).
Its filename matches its SHA-256 and all 14 pinned implementation/corpus source
identities were verified against the working files after publication.
Promotion remains explicitly disabled.

## Continuation validation and release gate

| Command | Actual outcome / scope |
|---|---|
| `python -m pytest tests/ -q` | Completed after the initially interrupted launch run: **1 failed, 62,031 passed, 63 skipped, 52 deselected**. The sole failure was canonical UM-ARTS coverage omitting the new P40 temporal test. |
| `python -m pytest tests/ -m slow -q` | **44 passed, 18 skipped, 62,085 deselected**. Separate marker run; do not aggregate shared skips into a canonical total. |
| `python -m pytest tests/test_um_arts_inventory.py 9-INFRASTRUCTURE/az-ml-program/tests/ 12-AZ-IP/40-az-live-data-harness/tests/ -q` | Inventory repair iteration: **367 passed**. P40 now selects its canonical directory; the ML reference suite has explicit canonical policy. Unrelated infrastructure is not implicitly trusted. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/ 12-AZ-IP/40-az-live-data-harness/tests/ tests/test_execution_spine.py tests/test_um_arts_inventory.py recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` | **3,824 passed, 3 skipped** before adding the CPU workload to the benchmark runner. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/test_reference_benchmarks.py -q` | **2 passed** after integrating the actual CPU workload/profile receipt. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/ 12-AZ-IP/40-az-live-data-harness/tests/ tests/test_execution_spine.py tests/test_um_arts_inventory.py COMPACTIFICATION/test_maps.py recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` | Final integrated run: **3,830 passed, 3 skipped** after profiler integration and staging/regenerating canonical maps. These scopes overlap selected core tests; do not sum them into a unique repository total. |
| `python -S -m src.infrastructure.ml_reference_benchmarks --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence` | Passed and published the immutable receipt above; complete representation, drift replay, exact retrieval, lineage, actual RAG and CPU-profile observations recorded. |
| `python -S -m src.infrastructure.ml_program check` | Passed: all 21 source-backed entries valid, promotion ineligible. |
| `python COMPACTIFICATION/build_maps.py --check` | Passed after staging all new implementation/test/evidence paths and regenerating the checked-in map. |
| `python TOOLS/audit/check_internal_links.py` | Passed: 2,053 Markdown files, all internal file links resolved. |
| `python TOOLS/checks/check_licensing_policy.py` | Passed existing structural evidence checks; this is not legal certification. |
| `python 12-AZ-IP/40-az-live-data-harness/run.py --temporal --owner-scope az-ml-validation` | Failed explicitly on DNS resolution; no synthetic substitution and no live success claimed. |
| `python -m pytest tests/ -m "" -q` | **62,077 passed, 71 skipped, 0 failed, 0 deselected**, 931.71 seconds. Completed unfiltered, including slow tests. The earlier full-core execution blocker is cleared for this checkpoint; unavailable optional integrations and production capability gates remain unqualified. Two existing collection/return-value warnings remain. |

The full-core result is earned, not inferred from focused tests or a file-count
supervisor. It does not validate skipped integrations, a GPU, live feed access,
trained-model quality, distributed operation or production readiness.

## Trained-model and serving tranche

The steward selected an existing repository-trained checkpoint if present,
otherwise a clearly labeled local research baseline. Initial tracked-file
inspection found no NPZ/NPY/safetensors/PT/PTH/GGUF checkpoint. A specialist
builder therefore trained the existing P43 architecture on original constructed
arithmetic rows. Separate reviewers examined quality/artifact loading and the
serving implementation. The coordinator added answer-only scoring, fixed report
hash publication, and addressed the review's pre-validation allocation defect.

The protocol fixes 60 training, 10 validation and 30 test operand pairs, a
predeclared character vocabulary, seed, architecture, 160 training steps and
group calibration. No held-out rows fit the model or quantizer. Every native,
FP16-roundtrip, 3-bit and 4-bit result is retained.

**Model utility failed, and the 3-bit fidelity gate failed.** The native model
answers **0/30** held-out arithmetic questions correctly. Aggregate
teacher-forced token accuracy includes punctuation and cannot hide that result.
The 3-bit model answers 1/30, which does not establish improved arithmetic.
The relative tolerance requires a cross-entropy increase no greater than 0.25
nats and token-accuracy delta no worse than -0.10. No thresholds were changed
after observing these results.

| Weight representation | Test token CE (nats) | Test token accuracy | Test answer accuracy | Total stored bits/parameter | Relative tolerance |
|---|---:|---:|---:|---:|---|
| Native float64 | 2.121831 | 58.67% | 0/30 | Raw-weight baseline, no container comparison | Reference only |
| FP16-rounded, evaluated in float64 | 2.122105 | 58.67% | 0/30 | Raw-weight baseline, no container comparison | Passed; not FP16 execution |
| Original 3-bit complete model | 2.887404 | 46.00% | 1/30 | **3.396636** | **Failed** |
| Original 4-bit complete model | 2.320601 | 58.00% | 0/30 | 4.397933 | Passed relative fidelity; task utility still failed |

The 39,293-parameter native checkpoint is 309,904 bytes. Its tokenizer, splits,
training protocol and source identities are embedded in metadata. Its 3/4-bit
variants occupy 16,683/21,601 bytes, including names, shapes, config, quantizer
metadata, framing and checksums. These are tiny original synthetic research
artifacts, not downloaded application-model weights. The NPZ retains inference
weights and metadata, not an optimizer/RNG training-resume checkpoint.

The actual CPU serving slice now consumes either NPZ or the original packed
format. It snapshots weights once, performs per-layer incremental KV reuse and
uses true masked vectorized batches of heterogeneous prefix lengths. A
single-threaded round-robin scheduler enforces owner consistency, retained-KV
reservation, context, row/padding limits, cancellation and between-call
deadlines. Terminal caches are freed; retained results require explicit
forgetting. No network service, tool authorization or second control plane was
introduced. Packed models are reconstructed into float64 before serving:
compressed storage is not low-bit kernel execution.

Full-prefix greedy outputs match both cached serial and continuously batched
decoding. On the fixed four-request trace, incremental decoding evaluates 45
new token rows rather than 248 full-prefix token positions; batching uses 14
backend calls instead of 45 cached-serial calls. These work counts are not a
universal speedup or a production latency guarantee. Actual timing samples and
first-token/completion waits are preserved without timing-based promotion.

Persistent source-bound evidence:

| Artifact | Scope |
|---|---|
| [Quality report](evidence/abff87f2999f404fbdf2c40aa8dea8cc52bbd972e489dcabb0d360660918f3c4.json) | All four representation arms, failed quality result, separate answer metrics, split/source identities and exact model filenames/hashes. |
| [Native-model serving report](evidence/fbabaca6b18782ddf5b7b035b2742059600cc415473e6460826f4d72cd081401.json) | Exact retained trained NPZ -> full-prefix reference -> cached serial -> continuous batch. |
| [Packed-model serving report](evidence/7562cbde626ad82a001125b1282c3c2157ecf8086f76c75c6a2968b588e7fcdf.json) | Actual original 3-bit artifact -> float64 reconstruction -> identical scoped parity protocol. |

All three report basenames hash their complete JSON bytes; model basenames hash
their complete binary bytes. The immutable earlier reference receipt remains
historical to its prior Git checkpoint; it must not be presented as a
current-source receipt after the publisher gained explicit model suffixes.

### Trained-model tranche validation

Serving commands below show the CLI spelling of the actual `main([...])` calls
with the same arguments; those entrypoint calls produced the linked receipts.

| Command | Actual outcome / scope |
|---|---|
| `python -m pytest 12-AZ-IP/43-az-geometric-tori-transformer/tests/ 9-INFRASTRUCTURE/az-ml-program/tests/ -q` | Pre-change model/reference baseline: **506 passed, 102 subtests passed**. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/test_research_quantization.py 9-INFRASTRUCTURE/az-ml-program/tests/test_artifact_io.py -m "" -q` | **26 passed** after fixing publication suffix handling, whole-report hashes and pre-allocation model-size validation. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/test_research_serving.py 9-INFRASTRUCTURE/az-ml-program/tests/test_research_serving_benchmarks.py -m "" -q` | **34 passed**, including native/packed input, full-prefix parity through positional wraparound, actual heterogeneous batches, cache identity, owner isolation, collision rejection, cancellation, deadlines and payload release. |
| `python -m src.infrastructure.research_quantization --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence --checkpoint-dir 9-INFRASTRUCTURE/az-ml-program/evidence --artifact-dir 9-INFRASTRUCTURE/az-ml-program/evidence` | Measurement/publication completed. Exact native/packed artifacts retained; **3-bit quality tolerance failed** and native task-generalization failure is recorded, not waived. |
| `python -m src.infrastructure.research_serving_benchmarks --checkpoint 9-INFRASTRUCTURE/az-ml-program/evidence/979847638ed7ec97277a0f5023515192779fc369050963048a12e0300fd8ede3.npz --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence` | Completed; output parity and scoped work-count gates passed. Maximum prefill logit error 2.44e-15. Actual warmed CPU timing ratio is an observation, not production qualification. |
| `python -m src.infrastructure.research_serving_benchmarks --quantized-model 9-INFRASTRUCTURE/az-ml-program/evidence/58aff2c9dc295c8f912ba7a76e95ac7285d44e5ad52bed73d64edc6856af5727.azmq --output-dir 9-INFRASTRUCTURE/az-ml-program/evidence` | Completed; reconstructed-model parity and scoped work-count gates passed. Maximum prefill logit error 6.22e-15. This does not undo the separate quality-gate failure. |
| `python -m pytest 9-INFRASTRUCTURE/az-ml-program/tests/ 12-AZ-IP/43-az-geometric-tori-transformer/tests/ 12-AZ-IP/40-az-live-data-harness/tests/ tests/test_execution_spine.py tests/test_um_arts_inventory.py COMPACTIFICATION/test_maps.py recycling/ "5-GOVERNANCE/Unitary Pentad/" -m "" -q` | Final affected-scope run: **4,041 passed, 3 skipped, 102 subtests passed**, no marker deselections. Includes the real training/publication test. |
| `python TOOLS/audit/check_internal_links.py` | Passed: 2,053 Markdown files, all internal file links resolved. |
| `python TOOLS/checks/check_licensing_policy.py` | Passed existing structural checks, not legal certification. |
| `python -S -m src.infrastructure.ml_program check` | Passed: all 21 valid, promotion ineligible. |
| `python -m pytest tests/ -m "" -q` | New unfiltered core run completed: **62,077 passed, 71 skipped, 0 failed, 0 deselected**, 927.73 seconds. The same two existing warnings remain. This is a new completed run, not reuse of the prior checkpoint's result. |

Core regression remains green, while **model-quality qualification remains
blocked by actual negative evidence**. Passing software tests validate correct
reporting and implementation behavior; they do not turn a failed experiment
into a qualified model. GPU execution, pretrained application-model quality,
authenticated production serving and live-feed validation remain outstanding.

## Tokenizer/model interchange and the 30/30 quality target

The steward explicitly selected **30/30 on a fresh preregistered holdout**, with
the original exposed 30 retained only as a diagnostic. Success on memorized
answers, renamed duplicate examples, a symbolic answer path presented as neural
inference, or a relaxed threshold does not meet that target.

Capabilities 10/20 now have actual bounded conversion implementations:

| Delivered surface | Exact supported behavior | Explicit nonclaim |
|---|---|---|
| Character tokenizer | Canonical Unicode-scalar IR and actual P43 metadata layouts, preserving vocabulary/token-ID order, identity normalization and unknown-character errors | No BPE/SentencePiece, added/special tokens, normalization changes or universal conversion. |
| P43 inference NPZ -> AZMQ | Loads bounded actual source bytes, extracts the source tokenizer, explicitly opts into lossy quantization and records complete weight errors | No quality improvement, optimizer/RNG transfer or runtime speed claim. |
| AZMQ -> inference NPZ | Explicit caller-supplied tokenizer, exact already-reconstructed weights, canonical tokenizer binding | Original prequantization weights and original task metadata are not recovered. |

A separate reviewer found two real issues, both fixed with regression tests:
NPY headers could request allocations beyond ZIP byte limits, and P43 added
special-token metadata could be discarded. Headers are now bounded and matched
to actual member sizes **before** NumPy array loading, and tokenizer semantic
overrides fail explicitly.

Actual retained-model conversions were executed and persisted:

| Receipt | Actual outcome |
|---|---|
| [Forward model translation](evidence/ce3e94ef90a31c2b0f42ee51e74ac016fdf02a242944a378baca69b43e3a1aa8.json) | Native trained NPZ -> the exact existing 3-bit AZMQ artifact; explicit loss, maximum weight error 0.18685535, complete 3.39663553 bits/parameter. The earlier failed model-quality gate is unchanged. |
| [Reverse model translation](evidence/e0b5dfc76540f8a5f817a5da45cec08b5d6ad75a3d3bb1bab7847eeb5b623394.json) | Packed model -> NPZ, zero additional weight error; source/tokenizer/implementation hashes recorded. |
| [Tokenizer conversion](evidence/d314e7736e08dbe23b54635d4f0ce52f925d8c5b2264ee21db24d0b14765addc.json) | Actual canonical research-model tokenizer -> P43 character metadata, exact mapping preserved. |

These are supported conversion milestones, not completion of either full
capability. Individual files are atomically published; multi-file publication
is not transactional. Caller-supplied AZMQ tokenizer binding remains an assertion.

### Arithmetic diagnosis and first preregistered improvement attempt

The [source-verified audit](evidence/9ec2723b7b6a5056a4e706509b36b74721d856a2933708502982532ef75a2255.json)
enumerates the original split. Training has six occurrences of every answer
digit; validation excludes all odd answers; test has two examples per even digit
and four per odd digit (label total variation from training is 1/6). Every one
of the 40 validation/test operand pairs has its reversal in training. This
establishes split confounding and weak evaluation independence, not proof that
the split alone caused the model's failure.

The [first new preregistration](evidence/9fe90aba130e3da8a4a3ef6f2ef2d37d0281bd79a81969b6717f061f9ad306b1.json)
was durably published before training/test evaluation. It changes the objective
to **answer-only** cross-entropy, uses actual P43 neural inference, fixes one
seed/trajectory and validation-only checkpoint selection, and withholds 30 unit
pairs including their reversals from the new training set. Full input strings
are new two-digit operands, sum modulo 10; all unit computations remain
historically exposed by the original fixture, so this is not independent new
arithmetic knowledge.

The [measured result](evidence/d0495292f34ef0e427c2371066cc2c5f0de93dd2371341431e26d0ff3c5656f5.json)
**failed the unchanged 30/30 gate: 0/30 fresh answers**. At step 10,000, it
memorized 4,480/4,480 training examples and got 70/70 validation examples correct,
but validation reused training's 70 underlying unit-pair computations in new
strings. That validation success did not measure unseen-computation
generalization. The original exposed 30 scored 2/30 as a diagnostic only.
Answer-only loss removed the punctuation proxy without producing arithmetic
generalization. A distinct implementation review found no scoring-position,
split-leakage or neural/oracle substitution bug explaining away this failure.

The selected 308,253-byte inference checkpoint and every recorded validation
observation are preserved; intermediate binary checkpoints are not retained.
The run completed in 86.03 seconds within its declared CPU budget. No seed,
checkpoint or threshold was selected using the new or original test outcomes.
The next alternative must validate on **unseen computations**, not just new
spellings of memorized pairs, before a fresh test is opened.

## Next bounded packages

1. Investigate the model's task-generalization failure using training/validation
   only. Preregister a fresh untouched task-family holdout before another quality
   experiment; never tune against the now-exposed 30 test questions.
2. Improve quantization/calibration on training/validation, retain the failed
   3-bit result, and compare an independent quantizer and licensed application
   model. Extend the working research KV/batch backend through existing PsiCat
   approvals only after absolute model utility and authenticated controls are
   separately qualified.
3. Add source-rebuild proposals and human-governed retrieval repair/rollback,
   learned-encoder evaluation and scoped reflective-memory replay.
4. On a network-enabled host, capture a real P40 response, retain its raw payload
   under explicit retention policy, and connect an identified prediction/label
   consumer before claiming a feature service or prediction-performance drift.
5. Continue all remaining workstreams through their original acceptance gates:
   distributed checkpoints, assurance, interoperability, synthetic data,
   fairness, GPU kernels/XAI, RL and multimodal indexing remain committed scope.

The current register records **10 planned and eleven in-progress** capabilities
(1, 2, 3, 7, 8, 10, 11, 13, 14, 18, 20); **zero full capabilities completed**. Original
algorithm milestones do not bypass their integration dependencies.
Hardware/network/dependency blockers remain visible, not scope deletions.

Before resuming, inspect Git state and the current register rather than assuming
these tranches created the full feature store, model server or 21 finished libraries.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
