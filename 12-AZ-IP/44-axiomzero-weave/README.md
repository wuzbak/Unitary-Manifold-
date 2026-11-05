# Product 44 - AxiomZero Weave

**Version 0.1.0 - adjacent software integration, not a physics claim.**

Weave makes the existing five-strand, seven-operation design executable through
PsiCat's control plane. It connects current repository evidence, owner-scoped
memory, the actual Product 16 Oracle, and Product 43 computation. It does not
replace those products or turn their agreement into authority.

The useful distinction is **circulation with correction, not circulation as
confirmation**. Evidence can change; memory can be wrong; a model can fail;
an Oracle score can be high while an independent obligation blocks execution.

## Five strands, seven operations

| Strand | Implemented responsibility |
|---|---|
| Cognition | Source-grounded retrieval, explicit-input Oracle synthesis, optional real character-model inference, controlled model experiments |
| Repository | Bounded current source contents, exact line citations, SHA-256 identity and freshness checks |
| Senses | Explicit user observations and local computations, with provider/task labels; no invented live telemetry |
| Memory | Private candidates and explicitly promoted shared lessons; owner isolation, provenance, deletion and read-only snapshot federation |
| Governance | Independent Pentad obligations, exact pre-effect authorization, durable intent/outcome accounting and ambiguity reconciliation |

`perceive -> ground -> recall -> reason -> challenge -> reconcile -> record`

The scheduler has explicit producer/consumer dependencies. Grounding and recall
can run concurrently; reasoning consumes their actual outputs. Failed
prerequisites block descendants with `blocked_by`, rather than passing empty
successes or stale arguments. Workers receive isolated copies of their declared
inputs. At most five workers and 32 nodes are supported; there is no claim of
hard cancellation of arbitrary Python workers.

Ordinary queries are deterministic retrieval, **not LLM reasoning**. Seven-stage
receipts disclose that provider, source hashes, dissent, unsupported claims and
HOLD states. Pure queries create no persistent state. Semantic content hashes
exclude receipt clocks and random run identifiers. Execution-spine records reuse
the monorepo's existing contract; its governance metadata alone is not enforcement.

### Optional point-in-time feature context

The in-process `Weave.query` API can attach deterministic feature values from an
already loaded `TemporalSnapshot`. Callers supply its owner and content hash,
entity, feature names, timezone-aware decision time, and an explicit freshness
TTL (`None` means no age cutoff). Only `real` origin is allowed by default;
synthetic or fallback values require an explicit origin policy. Feature results
remain separate from repository evidence and memory, preserve missing/stale
reasons, and bind the snapshot hash and decision time. This uses the shared
availability-aware replay primitive; it does not load caller-selected paths,
persist query results, infer an answer, authorize effects, or qualify a feature
service.

Temporal infrastructure is imported only when this context is constructed or
used; ordinary read-only API imports still work outside the repository root.

```python
from datetime import datetime, timezone
from pathlib import Path
import sys

sys.path.insert(0, str(Path("12-AZ-IP/44-axiomzero-weave").resolve()))
from az_weave.api import TemporalQueryContext, Weave
from src.infrastructure.temporal_data import load_snapshot

owner = "local-operator"
snapshot = load_snapshot(
    Path("approved-snapshot-directory"),
    "SNAPSHOT_SHA256",
    owner_scope=owner,
)
query = TemporalQueryContext(
    snapshot=snapshot,
    owner_scope=owner,
    snapshot_hash=snapshot.content_hash,
    entity_id="ENTITY_ID",
    feature_names=("FEATURE_NAME",),
    decision_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
    freshness_ttl_seconds=3600,
)
receipt = Weave(Path(".axiomzero-weave")).query(
    "question for repository retrieval", owner, temporal=query,
)
print(receipt["temporal_context"])
```

### Pentad is the foundation, not a sixth worker

The Pentad's reality, observer, human intent, AI precision and coupling roles are
not interchangeable with the five software strands or five physical dimensions.
All effect routes require independent `NO_LIES`, `NO_HARM`, `NO_COERCION`,
`TRANSPARENCY` and `SOVEREIGNTY` verdicts. Only explicit `PASS` for every
obligation permits approval. UNKNOWN, pending, failure and high aggregate scores
cannot compensate for one another.

The host establishes identity: the CLI uses the local OS operator; the HTTP host
requires a private bearer token and binds to loopback only. These are local
operator trust boundaries, **not production multi-user authentication**.
Neither source text, imported approvals, memory notes, nor model output can
issue a host approval.

Approvals bind the exact action, arguments, operator, configured targets,
implementation hashes, evidence manifest, policy version and expiry. Revocation
works before an effect is claimed. Intent is committed before the handler runs.
Concurrent effects are serialized across processes by a durable claim and a
kernel-held executor lock (POSIX `flock`, Windows nonblocking `msvcrt` byte-range
locking). Read-only imports do not require either platform's locking module.
Other operating systems reject effect execution/reconciliation explicitly.
Reconciliation must acquire that same
lock: it cannot release a claim while a handler or its outcome recorder is live.
Process exit releases the lock, not the durable claim. Keep the executor-lock
file in place; unlinking it while running defeats inode-based exclusion.
Use local state on a filesystem that supports the host OS's locking semantics;
network filesystems with incompatible locking are not supported. On Windows,
configure private state-directory ACLs: POSIX mode bits do not enforce user
isolation there.

A successful decision replays its recorded outcome, not the effect. An exception
after a possible write is AMBIGUOUS; process interruption leaves RUNNING. Both
require explicit observed reconciliation. Even confirmed non-effects need a new
approval to retry. This is deliberately **not universal exactly-once execution**.
Audit chains are content-integrity aids, not signatures or truth certificates.
Anyone controlling the local OS can replace code or the database.
Schema, memory-target and provider-availability checks run before approval and
again before claiming an effect. Invalid requests leave no ambiguous claim;
failures after a handler may have written remain conservatively ambiguous.
Recorded successes replay without requiring their old target to remain present.

This release also closes the existing Pentad workflow's implicit batch approval:
missing handlers reject gates, and truthy strings/numbers are not Boolean approval.

## Run from this checkout

Python 3.12+ is required. Retrieval, memory and the local HTTP host use the
standard library. Product 43 computation additionally needs NumPy, as already
declared by that product and the repository requirements. No weights, external
model service or network access are supplied.
An installed wheel still uses the checkout's sibling products and sources:
pass `--repo-root /absolute/path/to/checkout` before the subcommand.

```bash
python 12-AZ-IP/44-axiomzero-weave/run.py capabilities
python 12-AZ-IP/44-axiomzero-weave/run.py query \
  "How does the geometric tori transformer encode position?"
python 12-AZ-IP/44-axiomzero-weave/run.py invoke geometry --arguments '{}'
python 12-AZ-IP/44-axiomzero-weave/run.py serve --port 8144
```

`capabilities` uses the same `--checkpoint ID=PATH` and `--state-dir` settings as
`invoke`, but never creates that state. `AZ_WEAVE_CHECKPOINTS_JSON` is native-tool
host configuration, not a substitute for explicit CLI checkpoint settings.

Open `http://127.0.0.1:8144`. Read `.axiomzero-weave/operator.token` locally and
enter it in the page; do not commit, share or embed it in URLs. The UI keeps it
only in tab memory. Cross-origin API requests are denied. HTTP is for a trusted
local machine, not public deployment. The UI supports queries, explicit inputs,
independent obligation review, approvals, invocation, decision inspection and
revocation. `/health` is public and contains no private data.

Local state defaults to Git-ignored `.axiomzero-weave/`. Use `--state-dir` before
the subcommand to choose a dedicated private directory. Do not select a directory
containing unrelated files. State is unencrypted; OS access and backups remain
the operator's responsibility.

**Public Git repositories cannot lock individual folders to an administrator.**
Anything committed can be cloned, including past versions. `/AXIOMZERO/` and
`/AXIOMZERO-SYNTHESIS/` are excluded from Git; this prevents accidental inclusion,
not access to files already published or inclusion by arbitrary ZIP tools.
Private exports need separate private storage and authenticated server access
for remote use. The local operator token protects this runtime's API, not GitHub
repository contents. No private export is made public by this release.

### Govern a real experiment

```bash
python 12-AZ-IP/44-axiomzero-weave/run.py approve experiment \
  --arguments '{"steps":8,"seed":0}' \
  --obligations '{"NO_LIES":"PASS","NO_HARM":"PASS","NO_COERCION":"PASS","TRANSPARENCY":"PASS","SOVEREIGNTY":"PASS"}'
# After independently reviewing those verdicts, use the returned decision ID:
python 12-AZ-IP/44-axiomzero-weave/run.py invoke experiment \
  --arguments '{"steps":8,"seed":0}' --decision-id REPLACE_WITH_DECISION_ID
```

An approval is not inferred from that example. The person executing it supplies
the actual verdicts. Source-dependent effects can bind the exact `evidence`
array from a query using `approve --sources 'JSON_ARRAY'`; changed, deleted,
out-of-scope or forged source content invalidates approval.

The experiment runs all four rotary-schedule / learned-bias arms with identical
initial weights, training batches, optimizer and budget: toroidal and continuous
rotary schedules, each with learned circular bias or the same allocated table
frozen at zero. It reports allocated and active parameters, actual optimizer
steps, held-out losses and accuracy on periodic and nonperiodic synthetic copy.
`{"alias_probe":true,"context_length":75,"steps":2}` additionally probes lag 74.
Defaults are small smoke computations, not a convergence or superiority result.
Bias-off arms have fewer active parameters; that limitation remains explicit.
No held-out natural-language superiority benchmark is claimed.

### Train and use an actual checkpoint

Configure checkpoint identifiers at process startup; request arguments cannot
choose filesystem paths. Training destinations must be inside the model state
directory, for example:

```bash
python 12-AZ-IP/44-axiomzero-weave/run.py \
  --checkpoint tiny=.axiomzero-weave/models/tiny.npz \
  approve train --arguments '{"checkpoint_id":"tiny","corpus":"abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc abc","steps":2,"context_length":4}' \
  --obligations '{"NO_LIES":"PASS","NO_HARM":"PASS","NO_COERCION":"PASS","TRANSPARENCY":"PASS","SOVEREIGNTY":"PASS"}'
```

Invoke `train` with that same configuration, exact JSON arguments and decision
ID. Then invoke `generate` with
`{"checkpoint_id":"tiny","prompt":"abc","max_new_tokens":16}`.
An absent checkpoint is unavailable, never a fallback demo. Every result names
the provider, checkpoint digest, model configuration and supported bounded task.
This is a character language model, not an established general reasoning model.
Resume uses `resume:true` and requires `expected_checkpoint_sha256` equal to the
current checkpoint digest, plus the same corpus and compatible task/model
configuration. A changed checkpoint is refused before a write; the real
optimizer and RNG state continue through Product 43's resume workflow.

### Oracle and the complete investigation

`invoke oracle --arguments JSON` requires `system_name`, `system_type`, exactly
five `body_specs` (distinct `label`, explicit `status` and `phi_trust`), and
exactly seven `dim_scores`: Transparency, Sequence Integrity, Participation,
Accountability, Resilience, Epistemic Honesty, Freedom Floor. Scores must be
finite and in [0,1]; no missing input silently defaults to an optimistic score.
These are caller assessments, not independently measured facts.

`investigate QUESTION --experiment JSON --oracle JSON` grounds the question,
recalls scoped lessons and computes actual Oracle synthesis. Without an effect
decision it returns AWAITING_APPROVAL. With `--decision-id` for those exact
experiment arguments it performs the real governed factorial computation,
records the outcome, retains objections and returns a candidate lesson.
`/api/investigate` exposes the same contract. Memory creation, promotion and
deletion are separate explicitly governed actions; the investigation cannot
self-promote its conclusion.

## PsiCat, RAG and source continuity

Product 20 exposes `getAxiomZeroWeaveCapabilities`, `queryAxiomZeroWeave` and
`computeAxiomZeroWeave`. All are read-only native tools, available through the
existing toolkit and generic Navigator/browser transport. Computation permits
only `geometry`, `oracle` and `generate`; arguments use the same validated
backend contracts. For native checkpoint inference, the operator may set
`AZ_WEAVE_CHECKPOINTS_JSON` to an identifier/path object in the Navigator's host
environment. Requests cannot supply those paths. No native tool exposes effect
approvals or training to model-generated arguments.

The accompanying RAG changes prioritize substantive product guides over path
inventory for subject questions and retain current dated truth corrections
without indexing explicitly historical sections as current. Canonical authority
is claim-specific; it is not a guarantee of freshness or correctness.
Product 44 search and citation verification share the RAG current-section
selector, including nested historical exclusions. Excerpt windows stop at
excluded spans and retain original source line numbers and whole-file digests.
Unselected truth-layer prose cannot be verified as current evidence.

The divergent webspace supplied the five strands and seven operations. Its
October 24 source snapshot and November 2 export clocks are not an attestation
of live deployment. The original webspace, mind archives and extracted records
remain in the user's private ignored workspace. No private payload, imported
approval or model weights are published, automatically migrated, or used for
training. Synthetic fixtures exercise ownership and snapshot boundaries.

The Product 43 orbit `(5p,24p) mod 74`, bank `45p mod 74`, and 74 positional
signatures are software geometry. Absolute run identity remains separate from
modular phase. This is not a continuous five-torus, all 74-squared positions, a
proof of physical information flow, or evidence that full model outputs repeat.
The [truth layer](../../docs/TRUTH_LAYER.md) and
[separation boundary](../../SEPARATION.md) remain authoritative for scope.

## Validation and remaining boundaries

```bash
python -m pytest 12-AZ-IP/44-axiomzero-weave/tests/ -q --import-mode=importlib
```

The tests execute real small training, generation, factorial and Oracle paths,
plus explicit dependency, refusal, replay, stale-source, private-memory,
deletion, HTTP authentication and interrupted-effect recovery cases.

This is a checkout-integrated local runtime, not a completed migration of
Base44 database/auth/RLS, scheduler, storage or deployed webspace. It does not
retrofit mediation around every unrelated monorepo executor. Private-memory
federation requires an explicitly supplied owner-scoped snapshot; the original
archive database is not silently loaded. Live sensors, production identity,
distributed signing/retention, hard worker cancellation and broad language-model
advantage remain outside this release.

No pillar, TOE score, epistemic physics label or falsification condition changes.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*

*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
