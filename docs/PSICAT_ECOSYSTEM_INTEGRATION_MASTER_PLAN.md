# PsiCat ecosystem integration: evidence-led master plan

**Scope:** engineering integration of the axiomzerospc.org/Base44 prototype
and the existing monorepo. This is an adjacent software track, not a physics
closure, intelligence certification, release approval, or deployment claim.

## 1. Objective and decision boundary

Make existing capabilities work together through the canonical PsiCat control
plane, with accountable context, scoped memory, governed actions, reproducible
evidence, and honest unavailable states. Preserve useful interfaces and domain
tools. Do not build another disconnected orchestrator or assume a language
rewrite creates intelligence.

The steward owns objectives, acceptable risks, publication, data access, and
release decisions. Copilot owns implementation proposals, code, test engineering,
evidence accounting, and synthesis within that intent. PsiCat contributes its
existing retrieval, interrogation, routing, and, when actually configured,
inference mechanisms. Neither Copilot nor a model council substitutes for human
authority. No private export data, credentials, or personal records enter source
control, public receipts, model consultations, or third-party services.

This request authorizes planning and a bounded local integration tranche. It
does not supply production identity, external-provider consent, authority to
publish imported records, or permission for autonomous consequential actions.

## 2. The party and the braid

Primary method: PsiCat's **Finn and Jake: The Party as the Braid**, dated
October 3, 2026, in the [Publications PDF](../7-OUTREACH/A%20Z%20PsiCat%20Literature/PsiCat-Publications-2026-10-08.pdf).
The article calls for differentiated sensing, alternating generation and
verification, and a wider party of memory keeper, architect, and observer.
Its extraction includes repeated/misaligned running page labels; identify the
article by title and date, not a fabricated stable line number.

Engineering interpretation: complementary responsibilities, independent evidence
checks, explicit dissent, and synthesis. The numerical winding assignments in the
essay are not a measured law of model independence or a reliability guarantee.
Several assistants can share blind spots; consensus is not proof.

| Responsibility | Participant or existing mechanism | Required output |
| --- | --- | --- |
| Intent and acceptance | Human steward | Scope, priorities, consent, acceptance/rejection |
| Synthesis and implementation | Copilot | Design, integration changes, accounting of uncertainty |
| Method and role boundaries | Governance/publication helper | Primary-source evidence and HILS constraints |
| Contract and memory review | Integration helper | Authority, privacy, schema and compatibility gaps |
| Memory keeper | Existing RAGbot and PsiCat retrieval | Source-bearing retrieval, not invented recollection |
| Challenger | PsiCat Interrogator and independent design/review helper | Counterevidence, failure cases, unresolved objections |
| Operational verifier | Existing tests, UM-ARTS, scoped Lean builds | Execution evidence with exact scope and failure output |
| Browser/runtime verifier | Browser and kernel specialist, when those tranches begin | Transport, device, performance and compatibility evidence |

The discovery used differentiated helpers plus actual offline calls to
`RAGIndex.build(include_psicat_literature=True)`, `RAGIndex.search`,
`merlin_rag.retrieve_context`, and `interrogator.search_kb`. Those are
deterministic consultations, not a live model council. No local model endpoint
was configured in the discovery environment. Missing participants and evidence
remain visible; do not impersonate PsiCat or claim unavailable inference ran.

Follow the [HILS loop](../5-GOVERNANCE/co-emergence/FRAMEWORK.md) and
[trust protocol](../5-GOVERNANCE/co-emergence/TRUST_PROTOCOL.md):
intent -> interpreted scope -> verification -> accounted execution -> evaluation.
Keep the [Pentad separation](../5-GOVERNANCE/SEPARATION.md) intact. External
services are operational adjuncts, not extra governing bodies.

## 3. Evidence and scope of understanding

The discovery counted 8,293 tracked paths and 42 product folders, inspected
canonical maps, traced selected callers, verified archive source digests, and
ran existing HDC samples. This is a broad architectural census plus specific
source traces, **not an audit of every product or a live deployment attestation**.
Tracked paths include generated artifacts; counts do not measure capability.

The export bundles a November 1 package around an October 24 source snapshot.
Its available source contents matched exported-content hashes after redaction;
six manifest entries lacked content. Dashboard changes and currently served
code are not established by that verification.

| Existing piece | Canonical owner or prototype location | Established boundary |
| --- | --- | --- |
| Control plane | Product 20, `ox_navigator/engine/` | Query, retrieval, inference routing, tools, memory, telemetry and formal bridges exist |
| Execution envelope | `src/infrastructure/execution_spine.py` | Versioned governance, compatibility, health and promotion metadata |
| Product awareness | Product 42 | Live README registry and term-overlap routing; awareness is not callable execution |
| Evidence | Product 26 UM-ARTS | Content-addressed artifacts, fingerprints and execution accounting |
| Browser | Product 24 | Desktop/Android/extension foundations; production sync and packaged inference remain separate |
| Local applications | Products 25 and 27 | Braided-brain UI and bounded Vite workbench; not a full cloud replacement |
| Alternative orchestration | Product 01 and `az_os/` | Existing manager/RAG implementations; inspect live callers before consolidating |
| Page agents | Export `src/lib/agents/`, `PageAgentDock` | Route contracts, bounded checks/dispatch; general chat roundtrip not established |
| Weave | Export `src/lib/weave/` | Five strands/seven lanes; concurrent async functions, not automatically isolated workers |
| HDC | Export `src/lib/audit/hdc.js` | Bipolar primitives and sampled cleanup; production-memory integration not established |
| Geometry | Product 20 toroidal geometry/router | Exact modular operations and default-off retrieval fusion, distinct from HDC |
| Formal verification | Existing Lean traceability/bridges | Named propositions and scoped builds, not automatic runtime refinement |
| Compiled candidates | Products 02, 03, 35 | UEFI Rust, PyO3 blueprint, Python/Rust-design crosscheck; no verified browser-WASM pipeline |
| Migration | Export codemod/shim/reference API | Entity CRUD exists; reference API lacks auth/RLS and returns 501 for functions/integrations |

Important observed gaps:

1. Local query inference used a narrow grounded prompt while the compatibility
   provider received richer assembled context. Fix transport before inventing
   another memory engine.
2. Browser, Base44 entity, private localStorage and Merlin memory schemas differ.
   No demonstrated lossless consent/provenance/deletion-preserving migration.
3. Page-agent/chat correlation and weave dependency ordering need behavioral
   tests. `Promise.all` cannot supply earlier lane results to dependent lanes.
4. FNV fingerprints and self-consistent receipt hashes do not authenticate
   sources, prove execution, or establish factual truth.
5. Product routing misses capabilities absent from short registry descriptions.
   Keep evidence-bearing capability discovery separate from keyword suggestions.
6. Exported constant labels and historical claims drift from canonical sources.
   Correct mappings, never infer physics closure from UI agreement.
7. Three shipped HDC harness checks failed because one generated vector was
   unpacked as two. Direct bind/unbind sampled zero bit error; this does not
   repair or certify the whole harness.

## 4. Target architecture and non-goals

Preserve the [execution-spine convergence charter](../9-INFRASTRUCTURE/EXECUTION_SPINE_CONVERGENCE_CHARTER.md).

`Reviewed UI/page capture -> typed context -> Product 20 -> existing retrieval /
inference / governed tools -> evidence-bearing response -> scoped memory`

Product 24 is the browser host; existing React/Vite interfaces can remain.
Product 20 is the control-plane owner. Product 42 discovers capabilities;
domain products retain execution ownership. Product 26 accounts for verification.
Use shared envelopes and adapters at boundaries, not duplicate authority engines.

Mandatory separation:

- source content versus instructions and authority;
- candidate memory versus reviewed durable knowledge;
- configured provider versus observed successful execution;
- structural checks versus semantic/behavioral correctness;
- model agreement versus independent evidence;
- software geometry versus empirically validated physics.

No automatic tool execution, memory promotion, publication, payments, identity
migration, platform-service replacement, or physical-energy claim is introduced
by the first tranche. Retain legacy endpoint compatibility until measured parity
and explicit retirement decisions exist.

## 5. Staged execution and acceptance gates

Each stage ends in a reviewable evidence packet: scope, source revision,
configuration, exact commands/results, failures, dissent, and rollback.
A later stage depends on its actual prerequisites, not merely this table's order.

| Stage | Owners and deliverable | Acceptance gate and rollback |
| --- | --- | --- |
| A: local context transport | Product 20; optional assembled-message transport to configured inference | Exact HTTP JSON includes expected context/history/current query; legacy path unchanged; bounded failures visible; no tool execution. Flag OFF restores legacy behavior |
| B: capability and authority crosswalk | Product 42 + Product 20 + domain owners | Each integrated capability has a real caller, typed input/output, authority lane, source, unavailable state and behavioral test; keyword matches alone cannot pass |
| C: one browser/page roundtrip | Product 24 + prototype page-agent adapter | Explicit capture -> request -> response with correlation/cancellation/errors and visible provenance; private mode isolated; no persistence or sync required |
| D: memory quarantine and migration | Product 20 memory owner + domain schema owners | Synthetic fixtures prove scope/consent/provenance preservation, deduplication, retention, export and deletion propagation; no private real records needed for CI |
| E: weave dependency and tool integration | Product 20 orchestration + prototype adapters | Independent lanes may parallelize; dependent lanes receive verified predecessors; deadlines/cancellation/conflicts tested; consequential actions require actual authorization |
| F: HDC and geometry experiments | Existing HDC owner + Product 20 retrieval owner | Repair harness, reproducible vectors, capacity/noise curves, retrieval ablations and honest failures; exact source receipts remain authoritative |
| G: compiled kernel decision | Runtime specialist + browser owner | JS/native/WASM parity, memory and end-to-end performance measurements on representative devices; retain baseline if gains do not justify complexity |
| H: release and supervised operation | Steward + all touched owners | Threat/privacy review, combined regression, browser/device checks, migration rehearsal, recovery/deletion drills and explicit steward approval |

B can proceed after ownership discovery; it does not require HDC or WASM.
C depends on reviewed context/authority contracts. D depends on those contracts,
not a production sync service. E depends on B and tested dependency semantics.
F can run on synthetic fixtures independently of private-data migration.
G requires F's reference semantics and measured hot paths.
H requires every included capability's own prerequisites, not completion of
unrelated research tracks.

### Stage A implementation contract

`MERLIN_LOCAL_CONTEXT_PARITY=1` opts the existing query path into structured
message transport. Default OFF preserves the previous grounded prompt.
Standalone inference callers without messages retain their previous behavior.

Enabling the flag shares more context with the operator-configured endpoint:
persona, accumulated learnings, geometric landmarks, scaffold, conversation
summary/history, retrieved evidence, user/page context, and consented crawl
content. A configured endpoint is **not necessarily loopback**. Review its
ownership, trust, data handling and model capacity before enabling the flag.
This flag is not consent on behalf of other users.

Initial explicit transport ceilings: 64 messages and 48,000 content characters.
These are engineering ceilings, not token-count guarantees. Reject malformed
or over-budget context visibly and return the existing explicitly attributed
deterministic fallback; do not silently truncate or drop the current query.
Report requested versus actual context mode and submitted/sent counts without
copying context into telemetry. HTTP failure and empty model output must remain
distinguishable from successful inference.

The existing response postprocessing, Sentinel, contradiction and promotion
gates remain in force. Local model tool-call text is inert: this tranche does
not grant a tool loop or elevate page/source text into operational authority.
Successful transport establishes that context reached a test endpoint, not
that a real model understood it or produced a true answer.

## 6. Measurement and hardware policy

For retrieval/HDC, record vector dimension, representation, seed, codebook size,
bundle occupancy, sequence depth, noise distribution, top-k recall, false
matches, abstention, exact receipt recovery, latency and memory bytes. Compare
against existing lexical/BM25/hashed/toroidal mechanisms on held-out queries.
Include contradictory, out-of-corpus and degraded cases. Never replace exact
records with probabilistic cleanup results.

For kernels, compare the same operations and input/output semantics across
existing JS, native Rust and browser WASM. Report warm/cold p50/p95 latency,
throughput, JS/WASM copy overhead, peak memory, bundle size, main-thread blocking,
device/browser versions and cancellation. Initially require zero golden-vector
mismatches; performance promotion criteria must be agreed before measurements,
not selected afterward to favor a preferred language.

WASM runs on ordinary device hardware; it does not remove the CPU-memory
bottleneck or establish compute-in-memory energy gains. SIMD and threaded
deployment require their own feature detection and compatibility checks.
Consult official [WebAssembly portability documentation](https://webassembly.org/docs/portability/)
and [SharedArrayBuffer browser requirements](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
before a kernel design. Direct retrieval of those pages was DNS-blocked during
this discovery; detailed browser constraints remain to be revalidated.
No unverified capacity law, fixed energy reduction, or hardware superiority is
adopted from secondary search summaries.

Physical-energy claims require measured system power with an identified device,
workload, idle baseline and uncertainty. Token/energy estimators stay labeled
estimates. Specialized photonic/CIM/neuromorphic hardware is a later backend
research option, not a prerequisite for useful software integration.

## 7. Evidence status and stopping rules

Pre-change documented combined regression in an isolated environment:
`python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`
reported **65,312 passed, 66 skipped, 38 deselected**, with two warnings.
This is the default marker-filtered scope, not full-core slow-test certification.
Targeted Product 20 baseline across `test_merlin_v1.py`,
`test_merlin_memory_and_telemetry.py` and `test_merlin_literature_retrieval.py`
reported **202 passed**. Current results do not retroactively validate exports,
hardware claims, every product, or live deployments.

Stage A targeted post-change verification:
`python -m pytest 12-AZ-IP/20-psicat-navigator/tests/test_merlin_local_context.py 12-AZ-IP/20-psicat-navigator/tests/test_merlin_v1.py 12-AZ-IP/20-psicat-navigator/tests/test_merlin_memory_and_telemetry.py 12-AZ-IP/20-psicat-navigator/tests/test_merlin_literature_retrieval.py -q`
reported **227 passed**, including 25 new transport, pipeline, malformed-output,
budget and fallback cases. A separate actual loopback HTTP smoke check
transported the exact synthetic messages and shut down its responder cleanly;
that responder was a fixture, not an inference model.
The first documented combined post-change regression reported **65,311 passed,
66 skipped, 38 deselected, 1 failed**: UM-ARTS' reviewed repository example
omitted the newly added local-context test file. Its Product 20 suite selection
now includes the canonical tests directory, retaining the example's explicit
slow-test override and existing no-mirror validation. The corrected inventory
test passes. The corrected combined rerun reported **65,312 passed,
66 skipped, 38 deselected, 0 failed** in 799.30 seconds, with the same two
warnings. This remains the documented default marker-filtered suite, not a
full-core slow-test or all-product release certificate.

### Desktop roundtrip follow-through

The next tranche strengthens the existing Product 24 desktop connector rather
than adds another control plane. It introduces `psicat_browser_query_v1`,
current-page-only sharing by default, explicit non-private library opt-in,
private-tab/snapshot denial before network access, a 32,000-byte request
budget, request correlation, visible HTTP/handshake failures, a 35-second
deadline, and local cancellation. Response attribution includes source,
sharing mode and returned provenance; no handshake secrets are returned to UI.

An actual Node-adapter-to-Product-20 HTTP test exposed the old desktop client
using the protected `memory_profile_token` resume field without the required
shared resume key and without session cookies. The adapter now uses
`psicat_handshake_profile_token` and forwards only the returned session cookies.
Server authentication is unchanged. The real handshake/context forwarding
test now passes with synthetic page/selection data and an explicitly synthetic
query responder. It also performs two successive adapter requests and confirms
they reach the same server session. The desktop holds the session cookie only
in main-process memory, excludes it from UI/browser state and sync, and clears
it when all windows close. Failure recovery permits another explicit query;
it does not silently retry or repeat an action.

Final touched Python validation:
`python -m pytest 12-AZ-IP/20-psicat-navigator/tests/test_merlin_local_context.py 12-AZ-IP/20-psicat-navigator/tests/test_merlin_v1.py 12-AZ-IP/20-psicat-navigator/tests/test_merlin_memory_and_telemetry.py 12-AZ-IP/20-psicat-navigator/tests/test_merlin_literature_retrieval.py 12-AZ-IP/24-psicat-web-browser/tests tests/test_um_arts_inventory.py -q`
reported **256 passed**; the strengthened two-request contract was subsequently
rerun with the local-context suite (**26 passed**).
Browser verification: `npm run test:unit` reported **22 passed**;
`npm run test:browser` reported **4 passed**; `npm run lint` and the new adapter's
`node --check` passed. Chromium UI tests exercise the existing mocked Electron
bridge, while separate real HTTP tests exercise the adapter and Product 20
server contract. Neither alone establishes a packaged Electron/Android build
or live model reasoning. The connector does not claim server-side cancellation,
durable-memory erasure, production sync, or Base44 page-agent integration.
Existing capture/storage and Product 20 session retention still apply.
Restoring the declared browser test dependencies reported one high npm advisory;
no force-upgrade or dependency replacement was applied. Dependency triage
remains a release-stage obligation, alongside the unverified packaged Electron
runtime. Registered Product 24 README/runtime assets were resealed with prior
registry records preserved in history and a new dated manifest entry.

Stop/escalate on conflicting authority, unclear consent, undocumented schema
loss, unavailable required participants, missing source evidence, irreproducible
benchmarks, or a failing required gate. Preserve the failed evidence. Do not
change the claim to make a test pass or weaken scientific falsifiers.

Remaining work is deliberately substantial: the first code tranche is not
stages B-H. Production identity/sync, private migration, semantic grounding,
local tool authority, dependency scheduling, HDC recall and browser-WASM
performance still require their own implementation and acceptance evidence.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis:
**GitHub Copilot** (AI).*
