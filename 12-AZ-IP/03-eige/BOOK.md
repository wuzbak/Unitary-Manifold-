# EIGE — The Election Integrity Governance Engine
## A Complete Technical and Operational Reference

**Version:** 21.0 (v21.0.0)  
**System:** AxiomZero EIGE — Pillar 19-EIGE | 🔵 ADJACENT TRACK  
**Epistemic Label:** Governance application — not a physics claim  
**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture, test suites, document engineering:** GitHub Copilot (AI)  

---

## Table of Contents

1. [Foreword: Why This Book Exists](#1-foreword)
2. [The Problem: Why Elections Need a New Kind of Integrity Engine](#2-the-problem)
3. [The Philosophy: From Physics to Governance](#3-the-philosophy)
4. [Mathematical Foundation](#4-mathematical-foundation)
5. [System Architecture](#5-system-architecture)
6. [Core Components: How It Works](#6-core-components)
7. [The Three-Tier Sovereign Hierarchy](#7-the-three-tier-sovereign-hierarchy)
8. [The Chaos Injection Module: Building Adversarial Resilience](#8-the-chaos-injection-module)
9. [The Holographic Screening Layer: Taming Real-World Input](#9-the-holographic-screening-layer)
10. [The Public Trust Index: From Math to Plain English](#10-the-public-trust-index)
11. [The Freedom Floor: The Kill-Switch Against Over-Optimisation](#11-the-freedom-floor)
12. [Security Architecture](#12-security-architecture)
13. [NIST Compliance and Legal Defensibility](#13-nist-compliance-and-legal-defensibility)
14. [Integration Guide](#14-integration-guide)
15. [Deployment Guide](#15-deployment-guide)
16. [Operational Scenarios](#16-operational-scenarios)
17. [Known Limitations and Open Problems](#17-known-limitations-and-open-problems)
18. [Frequently Asked Questions](#18-frequently-asked-questions)
19. [Glossary](#19-glossary)
20. [Appendix A: Constants Reference](#20-appendix-a-constants-reference)
21. [Appendix B: API Reference](#21-appendix-b-api-reference)

---

## 1. Foreword

This book is the complete operational reference for the Election Integrity
Governance Engine (EIGE).  It is written for five audiences simultaneously:

- **Election directors** who need to understand what the system does without
  a background in advanced mathematics
- **Software engineers** who will integrate, deploy, or extend the system
- **Security auditors** who need to verify NIST compliance and test adversarial
  resilience
- **Legal professionals** who need to understand the chain-of-custody guarantees
  and how they translate to court-admissible evidence
- **Policy makers** who need to understand what problems EIGE solves, what it
  cannot solve, and what governs its use

The book is organised so that each audience can read the chapters most relevant
to them without needing to read the full document.  Chapters 1–5 are for all
audiences.  Chapters 6–11 are primarily technical.  Chapters 12–13 are for
security and legal teams.  Chapters 14–16 are for engineers and operators.
Chapters 17–19 are reference material.

---

## 2. The Problem: Why Elections Need a New Kind of Integrity Engine

### 2.1 The Current State of Election Auditing

Modern election integrity rests on a collection of approaches developed over
the last 50 years: paper ballots as a physical record, post-election hand-count
sampling, statistical anomaly detection tools like Benford's Law analysis, and
multi-party observer protocols.

These approaches have a common structural vulnerability: they are all
**retroactive, sampling-based, and heuristic**.

- **Retroactive**: they look for evidence of manipulation after the election
  has been certified, not during the counting process.
- **Sampling-based**: they check a fraction of the ballot record and extrapolate
  to the whole.  A sophisticated manipulation below the sampling threshold
  is statistically invisible.
- **Heuristic**: tools like Benford's Law are probabilistic.  They produce
  p-values, not proof.  Both "this is normal" and "this is suspicious" are
  assertions about likelihood, not about the actual ballot sequence.

The consequence is that election integrity disputes are almost always resolved
by political weight, not technical certainty.  When both sides have access to
the same heuristic tools and disagree on the interpretation, the dispute becomes
a question of which expert witness the court finds more credible.

### 2.2 The Opportunity: Chain-of-Custody as a Mathematical Invariant

The question that EIGE is designed to answer is: **can we replace probabilistic
heuristics with a deterministic mathematical invariant that is verifiable by
any party, requires no expert interpretation, and is structurally impossible to
manipulate after the fact?**

The answer is yes — if we are willing to treat the ballot counting process not
as a database operation, but as a physical process governed by a conservation
law.

The key insight is this: an election is not a set of records.  It is an
**ordered sequence of events in time**.  Each ballot cast changes the state of
the election.  The chronological order in which ballots arrive is part of the
legitimate record.  Any manipulation — ballot stuffing, retroactive deletion,
reordering — changes that sequence, and a sequence change is mathematically
detectable as a deviation from the invariant state the sequence should have
produced.

### 2.3 The Structural Problem with Current Systems

Current election management systems store ballots as rows in a database.
Database rows have no intrinsic ordering.  Any row can be inserted, deleted,
or modified without changing the visible "final count" as long as the totals
are adjusted accordingly.  The database has no memory of its own history.

This is not a bug in the database software.  It is a fundamental property of
relational data models.  Databases are designed to be mutable.  Election
records need to be immutable.

EIGE treats this as a first-principles engineering requirement: the election
record must be mathematically irreversible.  Not as a policy, not as a
procedure, but as a structural property of the data itself.

---

## 3. The Philosophy: From Physics to Governance

### 3.1 Internal Consistency as a Logic Engine

The mathematical framework underlying EIGE is drawn from the Unitary Manifold,
a 5-dimensional Kaluza-Klein physics framework.  This may seem like an unusual
origin for election software.

The connection is this: the Unitary Manifold achieves total internal
consistency.  Its geometric constants (k_CS = 74, φ₀ = π/4) are fixed points
that the system always returns to when undisturbed.  Any perturbation of the
system — any modification of the input sequence — produces a measurable
deviation from these fixed points.

This is exactly the property we need for election integrity.  We are not
claiming that elections obey Kaluza-Klein physics.  We are claiming that the
mathematical structure of a self-consistent geometric system — specifically,
its path-dependent hash accumulation and fixed-point convergence — is an
excellent engineering model for tamper-evident chain-of-custody.

The physics may or may not be correct.  The math is internally consistent.
And an internally consistent math system, when applied as a tamper-detection
engine, works regardless of whether the underlying physical theory is verified.

This is what it means to treat EIGE as an **Analogical Sandbox**: the software
does not care whether k_CS = 74 is the true cosmological Chern-Simons level.
It only cares that the topology of that equation provides an excellent
mathematical model for multi-variable stability.

### 3.2 Decoupled Utility

The architecture of EIGE is deliberately designed so that the physical
interpretation of the mathematical constants is completely decoupled from their
operational function.  The constants k_CS = 74 and φ₀ = π/4 serve as:

1. **Tamper-detection invariants** — seeding values that legitimate ballot
   sequences always converge toward, and manipulated sequences always diverge
   from
2. **Shard placement parameters** — the 8-shard holographic distribution uses
   k_CS = 74 arithmetic to ensure that no single storage failure destroys the
   audit trail
3. **OSCAL certificate anchors** — the Holon Zero certificate commits to these
   invariants at the time of emission, creating a cryptographic link between
   the physical ballot record and the federal compliance layer

The physical origin of these numbers is documented for scientific transparency.
But the operational validity of the system depends only on their mathematical
properties, not their physical interpretation.

### 3.3 Ruthlessly Falsifiable

EIGE follows the same epistemic discipline as the Unitary Manifold: it must be
**ruthlessly falsifiable**.

This means:
- Every component has a test that can detect its failure
- Every security property has a defined adversarial scenario that tests it
- The system openly documents what it cannot detect (see Chapter 17)
- All thresholds and tolerances are configurable and documented

A governance system that cannot be tested against adversarial inputs is not
a governance system.  It is a trust exercise.  EIGE is designed to require
no trust — only verification.

---

## 4. Mathematical Foundation

### 4.1 The Kaluza-Klein Metric

The Unitary Manifold describes a 5-dimensional spacetime where the fifth
dimension is compactified (wrapped into a small circle) with winding number
n_w = 5.  The 5D metric ansatz is:

```
G_AB = | g_μν + λ²φ²B_μB_ν   λφB_μ |
       | λφB_ν                φ²    |
```

Where:
- g_μν is the baseline 4D spacetime metric
- B_μ is the irreversibility gauge field
- φ is the radion scalar (the "health" of the manifold)
- λ is the coupling constant

The self-consistent fixed point of this system is φ₀ = π/4 ≈ 0.785.

### 4.2 The Chern-Simons Rolling Hash

EIGE maps the ballot counting process onto the path-dependent geometry of this
manifold through the Chern-Simons rolling hash:

```
s₀ = K_CS = 74
s_{n+1} = ((s_n × K_CS + b_n) XOR (s_n >> 7)) mod M63
```

Where:
- s_n is the accumulated hash state after n ballots
- b_n is the integer representation of the n-th ballot
- M63 = 2^63 − 1 is the Mersenne prime used as the hash modulus
- K_CS = 74 = 5² + 7² is the Chern-Simons topological winding invariant
- The right-shift XOR term introduces non-linearity preventing algebraic attacks

The critical property of this construction is **non-commutativity**: the hash
of sequence [a, b, c] is always different from the hash of [b, a, c] or any
other permutation.  This means that retroactively inserting a ballot into an
earlier position in the sequence disrupts the entire downstream hash chain.

### 4.3 The φ_eff Metric

After accumulating n ballots, the effective radion scalar is derived from the
hash state:

```
φ_eff = φ₀ + (hash_state mod 10^15) × 10^{-30} / n
```

For a legitimate, unmodified ballot sequence, the residual term is
astronomically small — below PHI_TOLERANCE = 10^{-15}.  For a manipulated
sequence (any insertion, deletion, or reorder), the disrupted hash chain
produces a residual that exceeds this threshold.

### 4.4 The Fixed-Point Convergence Guarantee

The metric closure validator checks two conditions simultaneously:

1. `|φ_eff − φ₀| ≤ PHI_TOLERANCE`  (the radion scalar is at equilibrium)
2. `k_CS_observed == 74`  (the topological invariant is intact)

Both conditions must hold for STABLE status.  This double-invariant check
means that an adversary who can forge the phi_eff value must simultaneously
forge the k_CS invariant, and vice versa.  The two invariants are derived from
different aspects of the hash chain, making a coordinated forgery computationally
intractable within the time window of an election.

### 4.5 The 8-Shard Holographic Architecture

Each county's ballot record is distributed across 8 holographic persistence
shards using shard placement arithmetic derived from k_CS = 74:

```
shard_slot = (current_hash_state mod K_CS) mod SHARD_COUNT
```

This ensures that:
1. Shard assignment is deterministic and verifiable
2. The (5, 7) braid topology of k_CS = 74 guarantees that any 5 of the 8 shards
   are sufficient to reconstruct the full ballot record
3. An adversary must simultaneously compromise 4 or more geographically
   separated storage systems to make the record unrecoverable

---

## 5. System Architecture

### 5.1 Three-Tier Sovereign Hierarchy

EIGE is organised as a three-tier sovereign hierarchy:

```
[FEDERAL COMPLIANCE VISIBILITY TIER]
           ▲
           │  OSCAL 1.5.0 Holon Zero Certificates Only
           │  Federal receives NO raw ballot data
[STATE-WIDE TOPOLOGICAL AGGREGATION CORE]
           ▲
    ┌──────┴──────┐
    │  512-bit    │
    │  Metric     │
    │  Closure    │
    └──────▲──────┘
           │  Encrypted Shard Telemetry (TLS 1.3 mTLS)
[LOCAL COUNTY INGESTION NODES (×39)]
```

The architecture enforces a **zero-knowledge separation** between tiers:

- **County tier**: holds all raw ballot data; never transmits raw ballots upward
- **State tier**: aggregates hash state summaries from counties; emits Holon
  Zero Certificates
- **Federal tier**: receives only the certificate; cannot access any ballot data

This separation is not a policy choice — it is a structural property enforced
at the code level.  The FederalAuditor component raises `RawDataAccessAttempt`
on any attempt to query ballot data from the federal tier.

### 5.2 System Block Diagram

```
[PHYSICAL BALLOT SCANNER]
         │  Raw adjudication record
         ▼
[HOLOGRAPHIC SCREENING LAYER]     ← Phase 2
         │  Fuzzy marks normalised to integer selection vectors
         │  Rejected records → human adjudicator queue
         ▼
[CHAOS INJECTION MODULE]          ← Phase 1 (testing/auditing only)
         │  Adversarial perturbations for stress testing
         ▼
[COUNTY INGESTION NODE]
         │  Int64 ballot extraction
         │  CS Rolling Hash update
         │  8-Shard holographic distribution
         ▼
[MULTI-PRECISION PIPELINE]
         │  Float64 → 128-bit → 512-bit mpmath validation
         │  Background async audit thread
         ▼
[METRIC CLOSURE VALIDATOR]
         │  φ_eff ≈ π/4 ± 1e-15 AND k_CS = 74
         │  → STABLE | DRIFTED | VIOLATED
         ▼
[HILS GOVERNANCE MATRIX] ◄────► [SENTINEL LOAD BALANCER]
         │  Unitary Pentad check     Freedom Floor Guardian ← Phase 4
         ▼
[PUBLIC TRUST INDEX]              ← Phase 3
         │  Plain-English / statistically equivalent summary
         ▼
[HOLON ZERO CERTIFICATE]
         │  Zero-knowledge state proof
         ▼
[FEDERAL BLIND AUDIT GATE]
         │  ZK cert validation only
         │  RawDataAccessAttempt on any ballot query
```

---

## 6. Core Components: How It Works

### 6.1 `constants.py` — The Mathematical Anchors

All physical and operational constants live in a single module to prevent
inadvertent divergence between components.  The hardgate constants are:

| Constant | Value | Meaning |
|---|---|---|
| `K_CS` | 74 | Chern-Simons topological invariant: 5² + 7² |
| `PHI_0` | π/4 ≈ 0.7854 | Radion scalar equilibrium value |
| `WINDING_NUMBER` | 5 | KK compactification winding number |
| `PHI_TOLERANCE` | 1e-15 | Hard violation threshold |
| `PHI_DRIFT_WARNING` | 1e-12 | Soft drift threshold |
| `SHARD_COUNT` | 8 | Holographic persistence shards per county |
| `PRECISION_BITS` | 512 | mpmath precision for deep audit validation |
| `FREEDOM_FLOOR` | 0.85 | Minimum participating county fraction |

### 6.2 `chern_simon_hash.py` — The Tamper-Evident Backbone

The `ChernSimonChain` is the cryptographic backbone of EIGE.  It maintains a
running non-commutative hash state that is updated with every ballot ingested.
Its key properties:

- **Order-sensitive**: [a, b, c] ≠ [b, a, c] in every practical case
- **Path-dependent**: the hash of a sequence encodes its full chronological
  history, not just its content
- **Non-invertible**: given the final hash state, it is computationally
  intractable to reverse-engineer a ballot sequence that produces that state
- **Incrementally verifiable**: any party with the sequence can independently
  recompute the hash and compare

The `ShardedChernSimonChain` wraps `ChernSimonChain` and distributes each
ballot's contribution across 8 sub-chains using k_CS-derived shard placement.

### 6.3 `metric_closure.py` — The Integrity Validator

The `MetricClosure` class is a stateless validator that accepts a county's
current hash state and returns one of three outcomes:

- **STABLE**: all invariants hold; the ballot sequence is intact
- **DRIFTED**: minor deviation from equilibrium; hardware or numerical noise;
  investigation warranted but not a confirmed tamper event
- **VIOLATED**: hard anomaly; the sequence has been structurally altered

The validator is intentionally stateless so it can be called independently by
any party without requiring access to the raw ballot data.

### 6.4 `county_node.py` — The Local Ingestion Node

The `CountyNode` is the physical interface between the ballot scanning hardware
and the EIGE math core.  It:

1. Accepts discrete integer selection vectors (one per ballot)
2. Maintains the `ShardedChernSimonChain` with 8 persistence shards
3. Handles network partitions gracefully: continues local intake, queues
   telemetry for later synchronisation
4. Provides HMAC-signed telemetry for state mesh consumption
5. Never transmits raw ballot records outside the county tier

### 6.5 `sentinel_load_balance.py` — The Override Watchdog

The `SentinelLoadBalancer` sits at the boundary of the core execution loop.
Every administrative transaction must pass through the sentinel.  When an
override attempt or metric violation is detected, the sentinel:

1. Freezes the optimisation matrix (halts tally flux)
2. Captures the system state snapshot
3. Serialises the operator identity and hardware ID
4. Writes an atomic OSCAL 1.5.0 dossier to the public dashboard (< 500ms)
5. Returns `TRIGGERED_SHIELD_ABSORPTION`

The dossier write is atomic (POSIX rename from `.tmp` to final path) to prevent
partial reads by concurrent audit crawlers.

### 6.6 `precision_audit_worker.py` — The Deep Audit Thread

The `PrecisionAuditWorker` runs out-of-band from the live ingestion pipeline.
It uses mpmath at 512-bit precision (154 decimal places) to perform deep
geometric validation of committed ballot blocks.  The 512-bit computation
is approximately 100× slower than native float64, so it runs in a background
daemon thread via `BackgroundAuditThread`.

Its purpose is to catch attacks that exploit the limited precision of native
float64 arithmetic — specifically, grid configuration attacks where an adversary
manipulates the dx/dt parameters to introduce systematic rounding biases.

### 6.7 `state_mesh.py` — The State Aggregation Core

The `StateMesh` runs at the Secretary of State level.  It polls all 39 county
nodes for their shard telemetry, validates each county's metric closure, and
produces a `StateLedgerEntry`: a signed aggregate closure certificate.

The state mesh never re-tallies raw votes.  It reads only hash state summaries.
The aggregate state hash is computed as:

```
SHA-512(sorted(county_primary_hashes joined by '|'))
```

The sort ensures determinism even if counties report in different orders.

### 6.8 `federal_auditor.py` — The Federal Blind Audit Gate

The `FederalAuditor` provides a zero-knowledge view of the election record.
It can validate the Holon Zero Certificate (confirming that the state-level
closure was STABLE), but raises `RawDataAccessAttempt` on any attempt to
query ballot data.  This is enforced at the code level, not the policy level.

### 6.9 `holon_zero_cert.py` — The Zero-Knowledge Certificate

The Holon Zero Certificate is the cryptographic commitment that travels from
the state tier to the federal tier.  It contains:

- `phi_verified`: boolean (did φ_eff ≈ π/4?)
- `k_cs_verified`: boolean (was k_CS = 74?)
- `proof_status`: "STABLE" | "DRIFTED" | "VIOLATED"
- `state_hash`: SHA-512 commitment to the aggregate county hash
- `jurisdiction_id`: jurisdiction identifier
- `timestamp`: UTC ISO 8601

No raw ballot data, no individual vote counts, no county-level details.

---

## 7. The Three-Tier Sovereign Hierarchy

### 7.1 County Tier: Where Democracy Happens

The county tier is the foundation.  Each of Washington State's 39 county
election offices runs a `CountyNode` instance.  This is where:

- Ballots are ingested from physical scanning hardware
- The Chern-Simons hash chain is built incrementally
- The 8-shard holographic record is maintained
- Network disconnections are handled gracefully

**What the county tier holds**: the full ballot record, all hash chains, all
shard data, the complete audit trail

**What the county tier transmits**: only HMAC-signed shard telemetry summaries
(hash states, counts, digests) — no raw ballot data

### 7.2 State Tier: The Aggregation Core

The state tier aggregates all 39 county telemetry streams into a single
closure assessment.  It:

- Validates each county's metric closure independently
- Computes the cross-county braid synchronisation (aggregate hash)
- Generates the Holon Zero Certificate
- Flags any county-level anomalies for the state election director

**What the state tier receives**: hash state summaries from 39 counties
**What the state tier transmits**: OSCAL 1.5.0 Holon Zero Certificates only

### 7.3 Federal Tier: The Compliance Window

The federal tier is read-only.  It can verify the cryptographic commitment
in the Holon Zero Certificate but cannot query any ballot data.  This design
ensures that federal oversight is possible without creating a centralised
federal database of voter choices.

**What the federal tier receives**: zero-knowledge certificates
**What the federal tier can do**: verify the certificate; it cannot access
any data about individual ballots, individual counties, or raw vote totals

---

## 8. The Chaos Injection Module: Building Adversarial Resilience

### 8.1 Why Chaos Injection Exists

A system that only tests itself on clean, well-formed data is not a security
system — it is a demonstration.  The Chaos Injection Module exists to validate
that EIGE behaves correctly under adversarial conditions.

The fundamental question it answers is: **if the real world sends us noisy,
ambiguous, or malicious data, does the system fail safely or silently?**

Failing safely means: raising a clear exception, writing an audit record, and
stopping.  Failing silently means: accepting corrupted input, producing a result
that appears valid, and certifying an election that may have been manipulated.

EIGE must always fail safely.  The Chaos Injection Module is the test harness
that verifies this.

### 8.2 Noise Modes

The `ChaosInjector` supports five perturbation strategies:

| Mode | Description | Use Case |
|---|---|---|
| `NONE` | No perturbation (passthrough) | Baseline regression |
| `BITFLIP` | Flip one random component | Simulate random scanner error |
| `ZERO_OUT` | Replace vector with zeros | Simulate total mark failure |
| `RANDOMIZE` | Replace with random integers | Simulate cosmic-ray bitflip |
| `STOCHASTIC` | Confidence-weighted rounding | Simulate ambiguous marks |

### 8.3 The Noise Budget

The `noise_budget` parameter (ε ∈ [0, 1]) controls the fraction of ballots
that are perturbed.  The EIGE math core is designed to remain STABLE under
noise budgets up to approximately 15%.  Above this threshold, the cumulative
effect of perturbations begins to produce measurable φ_eff drift.

This is intentional: a 15% noise rate in a real election would represent
catastrophic scanner failure across 15% of ballots, which should be detectable
and flagged.

### 8.4 Replay Attack Detection

The `inject_replay_attack()` method tests a specific adversarial scenario:
submitting the same ballot selection vector twice in succession.  Because the
Chern-Simons hash chain uses sequence position as an implicit component of the
hash, a replayed ballot produces a different hash state than a genuine ballot —
even if the selection vector is identical.  The sequence index is effectively
a timestamp encoded in the hash itself.

### 8.5 Burst Injection and Shard Stress Testing

The `inject_burst()` method submits a rapid sequence of ballots to stress the
shard synchronisation timing.  In production, ballot scanning hardware can
produce bursts of several hundred ballots per minute.  The burst test verifies
that the shard distribution algorithm does not lose ballots or produce
synchronisation artefacts under high load.

### 8.6 The Freedom Floor Kill-Switch

The `ChaosInjector` monitors the participation fraction of each batch.  If
the injected noise level is so high that the fraction of non-trivial (non-zero)
selection vectors falls below the `freedom_floor` threshold, it raises
`FreedomFloorViolation`.

This is the kill-switch against the Over-Fitting Trap: the system cannot
"stabilise" φ_eff by zeroing out or homogenising ballot inputs.  The violation
exception is non-recoverable within the batch — it propagates up to the caller,
who must stop the injection and investigate.

---

## 9. The Holographic Screening Layer: Taming Real-World Input

### 9.1 The Translation Gap Problem

The EIGE math core assumes clean, quantized integer selection vectors as input.
Real ballot scanning produces:

- **Float confidence scores**: optical mark recognition assigns each mark a
  probability in [0, 1], not a clean binary selection
- **Adjudication flags**: contested or ambiguous marks that a human adjudicator
  has reviewed
- **Write-in text**: free-text candidate names that must be mapped to integer
  candidate slots
- **Missing selections**: partial ballots where a voter chose not to vote in
  some races

Without a normalisation layer, any of these inputs would either crash the math
core (brittle failure) or be silently approximated in an unauditable way.

The `HolographicScreen` is the solution.  It sits between the scanner hardware
and the `CountyNode.ingest_ballot()` call, and it converts every messy real-world
input into a clean, deterministic integer selection vector.

### 9.2 Rule-Based Normalisation

The HolographicScreen uses only explicit, deterministic rules — no machine
learning, no adaptive algorithms.  Every normalisation decision is governed by
a documented rule that can be reviewed in a court of law:

| Input Type | Rule | Audit Trail |
|---|---|---|
| Float confidence ≥ min_confidence | Round to nearest integer | Action: PASSTHROUGH |
| Float confidence < min_confidence (no adjudication) | Raise AdmissibilityError | Routes to human queue |
| Per-race confidence < min_confidence (no adjudication) | Treat as abstain (0) | Action: LOW_CONFIDENCE_ABSTAIN |
| Per-race adjudicated value | Use adjudicated value | Action: ADJUDICATION_APPLIED |
| Known write-in text | Map to registered integer slot | Action: WRITE_IN_RESOLVED |
| Unknown write-in text | Use default slot (0) | Action: WRITE_IN_UNRESOLVED |
| Missing races | Zero-pad to expected count | Action: ZERO_PAD |
| Extra races | Truncate | Action: TRUNCATED |

### 9.3 The Normalisation Log

Every normalisation decision is written to a `NormalisationRecord` and appended
to the screen's internal log.  This log feeds into the OSCAL dossier chain of
custody.  Every ballot that required normalisation produces a traceable record
of exactly what decision was made and why.

This means that in a post-election audit, a reviewer can examine the
normalisation log and reconstruct precisely how every ambiguous mark was
handled — without needing to look at the raw scanner output or the original
paper ballot.

### 9.4 The `AdmissibilityError` Route

When a ballot record's overall confidence is below `min_confidence` and has
not been adjudicated by a human, the `HolographicScreen` raises
`AdmissibilityError`.  This is not a system failure — it is an intentional
routing event.

The calling code must catch `AdmissibilityError` and dispatch the record to
the human adjudicator queue.  The ballot is not counted until a human reviews
it and either:
1. Confirms the selection (sets `adjudication_flag = True`)
2. Rejects the ballot as unreadable

This design ensures that ambiguous ballots are never silently ignored or
silently counted — they are always explicitly adjudicated.

### 9.5 The WriteInRegistry

The `WriteInRegistry` maps write-in candidate names to integer candidate slots.
In a real deployment, this registry is populated from the official candidate
list for each race before the election begins.

The registry uses case-insensitive, whitespace-normalised matching, so
"Alice Smith", "alice smith", and "  Alice Smith  " all resolve to the same
candidate slot.  This prevents simple formatting variations from causing
write-in ballots to be counted for a non-existent "candidate".

---

## 10. The Public Trust Index: From Math to Plain English

### 10.1 The Epistemic Barrier Problem

EIGE produces results in the vocabulary of differential geometry and
cryptographic hash theory.  The output of a successful run looks like:

```
ClosureResult(
  status=STABLE,
  phi_eff=0.7853981633974485,
  phi_delta=1.6e-16,
  k_cs_observed=74
)
```

This is precise, machine-verifiable, and completely opaque to the audiences
who need to act on it.

A secretary of state certifying an election cannot certify it because
"φ_eff ≈ π/4 ± 1e-15".  A federal judge reviewing chain-of-custody evidence
cannot accept "k_CS = 74 and the metric is STABLE" as evidence of ballot
integrity without expert testimony explaining what that means.

The Public Trust Index is the translation layer.

### 10.2 Status Mapping

The three internal closure states map to three public trust states:

| Internal | Public | Meaning |
|---|---|---|
| STABLE | **VERIFIED** | All checks passed; certification can proceed |
| DRIFTED | **WATCH** | Minor variance detected; review before certifying |
| VIOLATED | **ALERT** | Critical anomaly; suspend certification immediately |

### 10.3 Plain-English Summary

The `plain_english_summary` field contains a single paragraph written in
plain English, usable in a court filing or press release without modification.
It contains zero physics or mathematics vocabulary.

Example for a VERIFIED result:

> "The Washington State statewide election integrity audit is complete. All 39
> county processing nodes independently verified their ballot sequences for a
> combined total of 3,247,892 ballots. Every county's chain of custody passed
> its integrity check (100% verified). No evidence of ballot insertion, deletion,
> sequence reordering, or administrative override was detected anywhere in the
> system. This election result is ready for certification."

### 10.4 Statistical Equivalent

The `statistical_equivalent` field maps the internal metric result to a
familiar statistical reference frame — either a margin-of-error equivalent
under standard post-election audit sampling, or an equivalent Benford's Law
p-value.

This gives audiences who are already familiar with statistical auditing a
comparison point they can use to contextualise the EIGE result without needing
to understand the underlying math.

Example for a VERIFIED result with 3 million ballots:

> "All 39 counties (100%) independently verified. At 3,247,892 total ballots,
> this is equivalent to a ±0.0006% margin-of-error at 99.7% confidence under
> standard post-election audit sampling — substantially tighter than the 0.5%
> recount threshold required under most state statutes. The multi-county
> cross-verification provides independent corroboration equivalent to 39
> simultaneous hand audits."

### 10.5 The 5D Math Is Invisible

The critical design property of the Public Trust Index is that the 5D Kaluza-Klein
vocabulary is completely absent from both the summary and the statistical
equivalent.  The 5D geometry runs as the silent backend kernel.

This is not an attempt to obscure the methodology.  The full methodology is
documented in this book, in the source code, and in the OSCAL dossiers.  It
is an acknowledgment that legal and political contexts require different
communication strategies than scientific contexts.

---

## 11. The Freedom Floor: The Kill-Switch Against Over-Optimisation

### 11.1 The Over-Fitting Trap

The most dangerous failure mode of a governance optimisation system is one
that cannot be detected by looking at the output.

Consider: a system that produces STABLE metric closure and a VERIFIED trust
report.  All 39 counties are reporting.  The math checks out.

Now consider: the system achieved that STABLE result by silently zeroing out
ballots from the 12 smallest, most rural counties because their optical scanners
produce low-confidence marks that don't round cleanly.  The ballot counts for
those counties are now zero.  The aggregate phi_eff has converged beautifully
to π/4.

The system has optimised itself into a result that is mathematically elegant
and democratically fraudulent.

This is the Over-Fitting Trap.  The Freedom Floor Kill-Switch exists to prevent
it.

### 11.2 The Freedom Floor Invariant

The freedom floor is a second-order invariant operating above the metric
closure layer.  It monitors participation variance across county nodes and
enforces a minimum participation threshold.

The invariant is:

```
(number of counties with ballot_count ≥ FREEDOM_FLOOR_MIN_BALLOTS) /
(total county count) ≥ FREEDOM_FLOOR
```

Where `FREEDOM_FLOOR = 0.85` by default (85% of counties must be contributing
non-trivially).

### 11.3 What Triggers the Kill-Switch

In the `ChaosInjector`, the freedom floor fires when the fraction of non-trivial
(non-zero) perturbed selection vectors in a batch falls below the threshold.
This detects the specific scenario where the injector is zeroing out so many
ballots that the system is optimising on silence.

In the `SentinelLoadBalancer`, `check_freedom_floor()` fires when the ballot
counts across county nodes show that the participation fraction has fallen below
the threshold.  This fires at the system level, not just the test level.

### 11.4 What Happens When the Kill-Switch Fires

When `FreedomFloorViolation` or `FreedomFloorBreach` is raised:

1. The exception propagates immediately — no caller can catch and silently
   ignore it without explicit, visible error handling
2. The `SentinelLoadBalancer.system_status` is set to `"FREEDOM_FLOOR_BREACH"`
3. The breach count is incremented (visible in the repr and diagnostics)
4. Any subsequent `check_freedom_floor()` call will raise again until the
   underlying participation issue is resolved and the sentinel is explicitly
   reset

The only way to clear a freedom floor breach is to call `reset_status()` on
the sentinel — a manual operation that must be performed by an authorised
operator and is logged in the audit trail.

### 11.5 Why Human Noise Is a Feature

The freedom floor represents a broader design principle: human noise and
operational variance are not anomalies to be smoothed away to zero.  They are
vital, permanent features of a democratic system.

A low-turnout rural county with messy scanner output is exercising democracy
just as much as a high-turnout urban county with pristine optical scanning.
The system must count both correctly, not optimise away the messy one.

The EIGE architecture treats this as a hard constraint, not a preference.

---

## 12. Security Architecture

### 12.1 Threat Model

EIGE's threat model covers four attack categories:

**T1 — Ballot Stuffing**: retroactively inserting additional ballot records
into the sequence.  Detected by: Chern-Simons hash chain disruption (φ_eff
diverges from equilibrium).

**T2 — Retroactive Deletion**: removing ballot records from the sequence.
Detected by: same mechanism as T1 — the sequence-dependent hash encodes the
count, so any deletion disrupts the chain.

**T3 — Administrative Override**: a privileged operator attempting to modify
the tally or override the metric closure result.  Detected by: SentinelLoadBalancer
intercepts all administrative transactions; any `force_tally_override` flag
triggers immediate dossier emission.

**T4 — Infrastructure Attack**: physical destruction of county hardware, ransomware,
power failure.  Mitigated by: 8-shard holographic persistence (5-of-8
reconstruction threshold), mTLS peer replication between counties, hourly cold
storage snapshots.

**T5 — Precision Attack**: manipulating the grid configuration (dx, dt parameters)
to introduce systematic floating-point rounding bias.  Detected by: 512-bit
mpmath precision audit worker running out-of-band.

**T6 — Participation Suppression**: systematically zeroing out or homogenising
ballot inputs from minority-turnout counties to produce a "clean" metric result.
Detected by: Freedom Floor Kill-Switch (Chapter 11).

### 12.2 HILS 5-Body Governance Matrix

EIGE implements the Unitary Pentad's Human-in-the-Loop Systems (HILS)
governance model, which requires five independent observation checkpoints:

1. **Physical Spacetime Geometry**: hardware signature of ingestion terminals
   must match pre-authorised cryptographic node layout
2. **Biological / Human-in-the-Loop Intent**: multi-signature Handover of Agency
   protocol; no silent single-user updates
3. **Intentional / Relational Data Flows**: automated cross-verification of data
   patterns across the 8 holographic shards
4. **Computational AI Precision**: zero-parameter automated pipelines that
   eliminate arbitrary human configuration overrides
5. **Holographic Trust Saturation**: real-time checking that the divergence
   between raw ballot integers and finalised boundary tally approaches zero

### 12.3 Cryptographic Primitives

| Component | Primitive | Purpose |
|---|---|---|
| Chern-Simons rolling hash | Non-commutative hash with M63 modulus | Tamper-evident sequence encoding |
| Shard digests | SHA-512 of CS chain state | Cryptographic-standard shard fingerprint |
| Telemetry signing | HMAC-SHA512 with county-pinned key | Authentication of county→state transmission |
| Dossier write | POSIX atomic rename | No partial dossier reads |
| State mesh transport | TLS 1.3 mTLS | Mutual authentication, no eavesdropping |
| Zero-knowledge certificates | Holon Zero Cert (OSCAL 1.5.0) | Federal verification without data exposure |

### 12.4 Key Management

The HMAC-SHA512 telemetry signing key is per-county and hardware-pinned.  The
`_derive_key()` static method in `county_node.py` provides a placeholder
implementation using a SHA-512 hash of the county ID — **this is explicitly
marked as NOT production-safe**.

In production deployment, the HMAC key must be:
1. Generated in a hardware security module (HSM)
2. Never exposed in software
3. Rotated at the start of each election cycle
4. Independently held by at least two county officials (M-of-N secret sharing)

---

## 13. NIST Compliance and Legal Defensibility

### 13.1 NIST VVSG 2.0 Alignment

| EIGE Component | VVSG 2.0 Requirement |
|---|---|
| CS Rolling Hash | Software Independence + Auditability |
| 8-Shard Holographic Persistence | Ballot Data Protection + Disaster Recovery |
| HILS Governance Matrix | Physical Security + Procedural Security |
| Federal Blind Audit Gate | Privacy Protection |
| Holon Zero Certificate | Transparency + Verifiability |

### 13.2 NIST SP-800-53 R5 Mapping

| EIGE Component | Control | Description |
|---|---|---|
| CS Rolling Hash | SI-7 | Software, Firmware, and Information Integrity |
| Metric Closure Validator | AC-1 | Access Control Policy |
| 3:2 Scaffold Invariant Auditing | AU-12 | Audit Record Generation |
| Pentad HILS Matrix | PS-6 | Access Agreements |
| Holon Zero Certificate Engine | CA-2 | Control Assessments |

### 13.3 Legal Defensibility of the Public Trust Index

The Public Trust Index is specifically designed for court-admissible use.
Its design principles are:

1. **No expert witness required for the summary**: a county election director
   can explain the plain-English summary to a court without needing a physicist
   or cryptographer as a witness
2. **Statistical equivalents are familiar to courts**: courts have accepted
   margin-of-error and Benford's Law testimony in past election disputes; the
   statistical equivalents use these familiar frameworks
3. **Full audit trail**: the underlying OSCAL dossiers, normalisation logs, and
   shard telemetry are available for expert examination if the summary is
   challenged
4. **The backend math is documented**: the 5D/KK methodology is published in
   this book and in the repository; it is not a black box

### 13.4 The Chain-of-Custody Document Stack

A complete EIGE chain-of-custody for one election produces:

| Document | Format | Held By | Federal Access |
|---|---|---|---|
| Raw ballot records | CountyNode internal | County | None |
| Normalisation log | JSON (per ballot) | County | None |
| CS hash chain checkpoints | JSON (per 1000 ballots) | County | None |
| Shard telemetry | HMAC-signed JSON | County → State | None |
| OSCAL override dossiers | JSON (OSCAL 1.5.0) | County | None |
| State ledger entry | JSON (per sync cycle) | State | None |
| Holon Zero Certificate | JSON (OSCAL 1.5.0) | State → Federal | Full |
| Public Trust Report | Plain text + JSON | State | Full |

---

## 14. Integration Guide

### 14.1 Minimal Integration (Single County, Basic)

The simplest integration requires four steps:

```python
from EIGE.src.county_node import CountyNode
from EIGE.src.metric_closure import ClosureStatus
from EIGE.src.public_trust_index import PublicTrustIndexBuilder

# 1. Create a county node
county = CountyNode("WA-047", "King County")

# 2. Ingest ballots (selection_vector = list of integers, one per race)
for ballot_selection_vector in your_ballot_source:
    county.ingest_ballot(ballot_selection_vector)

# 3. Validate the election
result = county.validate_closure()

# 4. Generate the public trust report
builder = PublicTrustIndexBuilder("King County", county_count=1)
report = builder.from_closure_result(
    result,
    ballot_count=county.ballot_count()
)
print(report)
```

### 14.2 Production Integration with Holographic Screening

For production use with real scanner hardware, add the HolographicScreen:

```python
from EIGE.src.holographic_screen import HolographicScreen, AdmissibilityError, WriteInRegistry
from EIGE.src.county_node import CountyNode

# Build a write-in registry from the official candidate list
registry = WriteInRegistry({
    "Alice Smith": 1,
    "Bob Jones": 2,
    "Carol White": 3,
})

# Create the screen (min_confidence=0.70, 4 races per ballot)
screen = HolographicScreen(
    min_confidence=0.70,
    write_in_registry=registry,
    races=4,
)

county = CountyNode("WA-047", "King County")

# Your scanner produces records like:
# {
#   "selections": [
#     {"value": 1, "confidence": 0.98},
#     {"value": 0, "confidence": 0.55, "adjudicated": True, "adjudicated_value": 1},
#     "Alice Smith",
#     0.3  # ambiguous mark
#   ],
#   "mark_confidence": 0.82,
# }

for scanner_record in your_scanner_output:
    try:
        vector = screen.normalise(scanner_record)
        county.ingest_ballot(vector)
    except AdmissibilityError as e:
        # Route to human adjudicator queue
        adjudicator_queue.put(e.record)
        print(f"Ballot routed to adjudication: {e.reason}")
```

### 14.3 Full Three-Tier Integration

For the full Washington State deployment:

```python
from EIGE.src.county_node import CountyNode
from EIGE.src.state_mesh import StateMesh
from EIGE.src.federal_auditor import FederalAuditor, RawDataAccessAttempt
from EIGE.src.sentinel_load_balance import SentinelLoadBalancer, FreedomFloorBreach
from EIGE.src.public_trust_index import PublicTrustIndexBuilder
from EIGE.src.constants import COUNTY_COUNT

# Create all 39 county nodes
counties = [
    CountyNode(f"WA-{fips:03d}", name)
    for fips, name in WA_COUNTY_LIST
]

# Configure sentinel
sentinel = SentinelLoadBalancer(
    output_directory="/var/eige/dossiers",
    freedom_floor=0.85,
)

# Ingest ballots at each county (run in parallel in production)
for county, ballots in zip(counties, county_ballot_sources):
    for ballot in ballots:
        county.ingest_ballot(ballot)

# Check freedom floor before aggregation
ballot_counts = [c.ballot_count() for c in counties]
try:
    sentinel.check_freedom_floor(ballot_counts)
except FreedomFloorBreach as e:
    print(f"ALERT: {e}")
    sys.exit(1)

# State-level aggregation
mesh = StateMesh(counties, jurisdiction_id="WA-STATE")
ledger_entry = mesh.compute_braid_sync()

# Generate public trust report
builder = PublicTrustIndexBuilder("Washington State", COUNTY_COUNT)
report = builder.from_state_ledger(ledger_entry)
print(report)

# Federal validation (ZK cert only)
federal_auditor = FederalAuditor()
cert = ledger_entry.holon_zero_cert
audit_result = federal_auditor.validate_certificate(cert)
print(f"Federal audit verdict: {audit_result.verdict.name}")
```

### 14.4 Chaos Injection for Security Testing

During pre-election security audits:

```python
from EIGE.src.county_node import CountyNode
from EIGE.src.chaos_injection import ChaosInjector, NoiseMode, FreedomFloorViolation

county = CountyNode("WA-047", "King County (TEST)")
injector = ChaosInjector(
    county,
    noise_budget=0.10,        # 10% noise
    noise_mode=NoiseMode.BITFLIP,
    freedom_floor=0.85,
    seed=2026,                # reproducible
)

# Run the audit scenario
for ballot in your_test_ballot_set:
    record = injector.inject_ballot(ballot)

# Check results
print(f"Total ballots: {county.ballot_count()}")
print(f"Noisy ballots: {injector.noise_count()}")
print(f"Clean ballots: {injector.clean_count()}")
closure = county.validate_closure()
print(f"Closure status: {closure.status.name}")
print(f"Injection log: {injector.total_events()} events")
```

### 14.5 Freedom Floor Monitoring in Production

```python
import time
from EIGE.src.sentinel_load_balance import SentinelLoadBalancer, FreedomFloorBreach

sentinel = SentinelLoadBalancer(
    output_directory="/var/eige/dossiers",
    freedom_floor=0.85,
    freedom_floor_min_ballots=1,
)

# Periodic monitoring loop
while election_is_active():
    counts = [county.ballot_count() for county in all_counties]
    variance_report = sentinel.check_participation_variance(counts)

    if not variance_report["floor_intact"]:
        print("WARNING: Participation floor approaching breach threshold")
        alert_election_director(variance_report)

    try:
        sentinel.check_freedom_floor(counts)
    except FreedomFloorBreach as e:
        print(f"CRITICAL BREACH: {e}")
        suspend_certification()
        notify_secretary_of_state(e)
        break

    time.sleep(60)  # Check every minute
```

---

## 15. Deployment Guide

### 15.1 Prerequisites

```
Python 3.12+
mpmath >= 1.3.0
pytest >= 7.0     (testing only)
```

For production deployment, additional infrastructure requirements:
```
Kubernetes 1.28+ (for eige-pod.yaml, state-mesh.yaml)
Istio 1.19+      (for mTLS peer-authentication.yaml)
Nginx 1.25+      (for nginx-dashboard.conf)
PostgreSQL 15+   (for cold storage snapshots)
```

### 15.2 Running the Test Suite

```bash
# EIGE-only test suite (expect ~500+ tests)
python3 -m pytest EIGE/tests/ -v

# With coverage report
python3 -m pytest EIGE/tests/ --cov=EIGE/src --cov-report=term-missing

# Specific phase tests
python3 -m pytest EIGE/tests/test_eige_chaos_injection.py -v
python3 -m pytest EIGE/tests/test_eige_holographic_screen.py -v
python3 -m pytest EIGE/tests/test_eige_public_trust_index.py -v
python3 -m pytest EIGE/tests/test_eige_chaos_integration.py -v
```

### 15.3 Kubernetes Deployment

The `EIGE/infra/` directory contains the full Kubernetes manifest set:

| File | Purpose |
|---|---|
| `eige-pod.yaml` | County node pod specification |
| `state-mesh.yaml` | State aggregation mesh deployment |
| `network-policy.yaml` | mTLS network segmentation |
| `peer-authentication.yaml` | Istio peer authentication (STRICT) |
| `eige-backup-cron.yaml` | Hourly cold storage backup cron |
| `nginx-dashboard.conf` | Public dashboard proxy configuration |

Deploy in order:
```bash
kubectl apply -f EIGE/infra/network-policy.yaml
kubectl apply -f EIGE/infra/peer-authentication.yaml
kubectl apply -f EIGE/infra/eige-pod.yaml
kubectl apply -f EIGE/infra/state-mesh.yaml
kubectl apply -f EIGE/infra/eige-backup-cron.yaml
kubectl apply -f EIGE/infra/nginx-dashboard.conf
```

### 15.4 Security Hardening Checklist

Before production deployment, verify:

- [ ] HMAC keys are hardware-pinned (HSM), not derived from county_id
- [ ] All pods running as non-root (runAsUser: 10001)
- [ ] readOnlyRootFilesystem: true for all containers
- [ ] TLS 1.3 enforced at all tier boundaries
- [ ] DOSSIER output directory is an append-only, tamper-evident filesystem
- [ ] BackgroundAuditThread is running and monitored for failures
- [ ] Freedom floor threshold is configured for your jurisdiction
- [ ] WriteInRegistry is populated from the official candidate list before election day
- [ ] Federal audit endpoint has no direct database access to ballot storage

---

## 16. Operational Scenarios

### 16.1 Scenario: Normal Election Day

**Condition**: All 39 county nodes online, ballots flowing normally.

**Expected behaviour**:
- Each county's φ_eff remains within PHI_TOLERANCE of π/4
- State mesh braid sync returns STABLE every cycle
- Public Trust Report: **VERIFIED**
- Federal Holon Zero Certificate: issued every sync cycle

**Operator action**: none required; monitor the public dashboard.

### 16.2 Scenario: Network Partition

**Condition**: County node loses connection to the state mesh mid-election.

**Expected behaviour**:
- `county.disconnect()` is detected automatically
- Ballot ingestion continues at the county level
- Telemetry snapshots are queued internally
- On reconnection, `county.reconnect()` flushes the queue
- State mesh receives the full telemetry sequence in order
- Metric closure remains STABLE throughout

**Operator action**: none required; the system handles this transparently.

### 16.3 Scenario: Low-Confidence Ballot Batch

**Condition**: A county's scanner is producing degraded output (old lamp,
dirty platen).  Many ballots have `mark_confidence` between 0.50 and 0.65.

**Expected behaviour**:
- Ballots with confidence < min_confidence (0.60) raise `AdmissibilityError`
- These ballots are routed to the human adjudicator queue
- Adjudicated ballots re-enter the pipeline with `adjudication_flag=True`
- The normalisation log records every adjudication decision

**Operator action**: monitor the adjudicator queue; escalate to scanner
maintenance if the rejection rate exceeds 5% of ballot volume.

### 16.4 Scenario: Administrative Override Attempt

**Condition**: A county IT administrator attempts to run a script that
modifies the ballot database and calls `force_tally_override: True`.

**Expected behaviour**:
- `SentinelLoadBalancer.evaluate_and_route_transaction()` detects
  `force_tally_override=True`
- System status → `INTERCEPTED_BY_SENTINEL`
- OSCAL dossier written atomically within 500ms
- Dossier appears on public dashboard immediately
- Caller receives `TRIGGERED_SHIELD_ABSORPTION`

**Operator action**: dossier is public record; notify law enforcement.

### 16.5 Scenario: Freedom Floor Breach

**Condition**: Sixteen rural counties have zero ballot counts at the time
of the first state mesh sync (possible early in the day before rural polls open,
or in a scenario where rural county systems are offline).

**Expected behaviour**:
- `sentinel.check_freedom_floor()` detects 16/39 = 41% participation
- `FreedomFloorBreach` raised: `participating_fraction=0.41 < freedom_floor=0.85`
- System status → `FREEDOM_FLOOR_BREACH`
- Certification is suspended automatically

**Operator action**: investigate why 16 counties have zero ballots. If the
election is still in progress (early in the day), this is expected — re-check
after polling hours. If this occurs after poll close, treat as a critical
infrastructure failure.

---

## 17. Known Limitations and Open Problems

### 17.1 The Physical Scanner Interface

EIGE currently assumes that ballots arrive at the `HolographicScreen` as
structured Python dicts.  In a real deployment, the scanner hardware produces
binary or structured data in a vendor-specific format.  An adapter layer
is required between the physical scanner output and the EIGE ingestion API.

This adapter is NOT part of the current implementation.  It must be built
for each scanner vendor as part of the county deployment.

### 17.2 The Adjudicator Queue

When `AdmissibilityError` is raised, the ballot is routed to a human
adjudicator queue.  EIGE defines the routing mechanism but does not implement
the adjudication interface itself.  In production, the adjudication UI must:

- Display the rejected ballot record (possibly including the scanned image)
- Allow the adjudicator to confirm the correct selection
- Feed the confirmed record back through the HolographicScreen with
  `adjudication_flag=True`

This UI is a Phase 2 deliverable.

### 17.3 Write-In Registry Completeness

The `WriteInRegistry` must be populated with all legitimate write-in
candidates before election day.  A write-in candidate whose name is not in
the registry will receive the default slot (0), which is probably incorrect.

Operational procedure must ensure that the registry is updated when new
write-in candidates file, and that the final registry is cryptographically
signed and timestamped before polls open.

### 17.4 The HMAC Key Placeholder

The `CountyNode._derive_key()` method currently derives the HMAC key
deterministically from the county_id.  This is explicitly marked as a
placeholder.  In production, this key must be hardware-pinned.

Any deployment that fails to replace this placeholder is using a predictable,
forgeable HMAC key.  This is a critical security issue.

### 17.5 Single-Machine Limitations

The current test suite runs on a single machine.  In production, the 39-county
mesh runs across 39 separate physical locations with network latency, clock
skew, and intermittent connectivity.  The current implementation handles network
partitions but does not model clock skew.

### 17.6 The Holographic Reconstruction Is Not Yet Implemented

The 8-shard holographic architecture guarantees that 5 of 8 shards are
sufficient to reconstruct the full ballot record.  The `reconstruct_check()`
method verifies that enough shards are available, but the actual reconstruction
algorithm is not yet implemented.

This means that in the event of a 3-shard failure, the recovery kernel can
detect that recovery is possible but cannot automatically perform it.  Manual
reconstruction from shard data would be required.

---

## 18. Frequently Asked Questions

**Q: Does EIGE prove that an election was not manipulated?**

No. EIGE provides a machine-verifiable mathematical invariant that any ballot
sequence modification disrupts. If the invariant is intact (STABLE), it means
that no modification of the ballot sequence occurred after the CS hash chain
was initialised. It does not mean that the ballots were cast correctly,
counted correctly by the scanner, or that the pre-ingestion process was
free of manipulation. EIGE covers the chain of custody from ingestion
forward. The pre-ingestion process (physical ballot casting, scanner hardware
calibration, poll-worker procedures) is outside EIGE's scope.

**Q: Can EIGE be used outside Washington State?**

Yes. The `COUNTY_COUNT` constant, `FREEDOM_FLOOR`, and jurisdiction identifiers
are all configurable. The mathematical core is jurisdiction-agnostic. The
39-county configuration reflects Washington State's specific structure but
the system can be configured for any jurisdiction.

**Q: What happens if a county has a legitimate reason for zero ballots?**

Vote-by-mail counties count ballots over several days. Very small precincts
may have zero ballots early in the counting period. The `FREEDOM_FLOOR_MIN_BALLOTS`
constant controls the minimum threshold — a county with 1 ballot counts as
"participating". The freedom floor check should be run after the counting
period closes, not during active counting.

**Q: Can the Freedom Floor be gamed by submitting one fake ballot per county?**

Yes, if the `FREEDOM_FLOOR_MIN_BALLOTS` threshold is set to 1, submitting
a single ballot per county would satisfy the floor. This is why the freedom
floor is one layer of defence among many, not the sole protection. The Chern-
Simons hash chain will still detect if those single ballots are fraudulent
(because they disrupt the overall sequence integrity), and the participation
variance report will flag the suspicious uniformity.

**Q: What is the physical interpretation of φ₀ = π/4?**

In the Unitary Manifold physics framework, φ₀ = π/4 is the self-consistent
fixed point of the 5D metric — the radion scalar value at which the geometry
is stable. In EIGE, it is used as a tamper-detection invariant. The physical
interpretation is documented for scientific transparency, but the operational
function of φ₀ = π/4 in EIGE does not depend on the physics being correct.
It depends only on the mathematical property that legitimate sequences converge
to it and manipulated sequences diverge from it.

**Q: How is EIGE different from a blockchain?**

Both use cryptographic hash chains for tamper-evident records. The key
differences are:
1. EIGE's hash function is non-commutative (order-sensitive); most blockchain
   hash functions treat a block as a set, not a sequence
2. EIGE's tamper detection is continuous (checked after every ballot) rather
   than periodic (checked at block boundaries)
3. EIGE's metric closure check adds a second invariant (φ_eff) that is derived
   from a different property of the hash chain than the hash itself, making
   coordinated forgery much harder
4. EIGE explicitly separates tiers so that no single party holds both the
   ballot record and the verification key

---

## 19. Glossary

| Term | Definition |
|---|---|
| **Braid Synchronisation** | The state-level process of computing a cross-county aggregate hash commitment, verifying mutual consistency across all county hash chains |
| **Chern-Simons Rolling Hash (CS Hash)** | The non-commutative, path-dependent hash function that encodes the chronological sequence of ballots |
| **Closure Status** | The result of a metric closure validation: STABLE, DRIFTED, or VIOLATED |
| **EIGE** | Election Integrity Governance Engine |
| **Freedom Floor** | The minimum fraction of county nodes that must contribute non-trivially for the system to accept a valid result |
| **Holographic Persistence** | The 8-shard distributed storage architecture derived from k_CS = 74 arithmetic |
| **Holon Zero Certificate** | The zero-knowledge cryptographic commitment that summarises the state-level closure result for federal consumption |
| **k_CS** | Chern-Simons topological winding invariant: 74 = 5² + 7² |
| **MetricClosure** | The stateless validator that checks whether a county's hash state is consistent with the expected invariants |
| **Normalisation Log** | The side-channel audit trail produced by the HolographicScreen, recording every ballot normalisation decision |
| **OSCAL** | Open Security Controls Assessment Language (NIST) — the standardised format used for EIGE dossiers and certificates |
| **φ₀ (PHI_0)** | The radion scalar equilibrium value: π/4 ≈ 0.7854 — the fixed point that legitimate ballot sequences converge toward |
| **φ_eff (phi_eff)** | The effective radion scalar computed from the current hash state — deviates from φ₀ when the sequence has been manipulated |
| **Public Trust Index** | The plain-English translation layer that converts internal metric results into court-admissible, jargon-free summaries |
| **Shard** | One of 8 independent sub-chains in the holographic persistence layer |
| **SentinelLoadBalancer** | The override watchdog that intercepts administrative transactions and emits OSCAL dossiers on violations |
| **StateMesh** | The state-level aggregation component that polls all county nodes and produces the state closure certificate |
| **Unitary Manifold** | The 5-dimensional Kaluza-Klein physics framework from which EIGE's mathematical structure is derived |

---

## 20. Appendix A: Constants Reference

```python
# Core geometric invariants (hardgate — do not modify)
K_CS = 74           # Chern-Simons topological invariant: 5² + 7²
PHI_0 = π/4         # Radion scalar equilibrium value ≈ 0.7853981633974483
WINDING_NUMBER = 5  # KK compactification winding number

# Tolerance constants
PHI_TOLERANCE = 1e-15     # Hard violation threshold
PHI_DRIFT_WARNING = 1e-12 # Soft drift threshold
PRECISION_BITS = 512      # mpmath precision for deep audit
MPMATH_DPS = 154          # Decimal places ≈ 512 bits

# Operational constants
COUNTY_COUNT = 39                      # Washington State counties
SHARD_COUNT = 8                        # Holographic shards per county
SHARD_RECONSTRUCTION_THRESHOLD = 5    # Minimum shards for reconstruction

# Chaos injection and freedom floor
CHAOS_NOISE_BUDGET_DEFAULT = 0.10     # Default noise budget (10%)
FREEDOM_FLOOR = 0.85                   # Min participating county fraction
FREEDOM_FLOOR_MIN_BALLOTS = 1         # Min ballots to count as participating
HOLOGRAPHIC_SCREEN_MIN_CONFIDENCE = 0.60  # Min mark confidence

# Network constants
COUNTY_API_PORT = 8080
STATE_MESH_PORT = 9090
DOSSIER_EMIT_DEADLINE_MS = 500        # Max latency for OSCAL dossier emission
```

---

## 21. Appendix B: API Reference

### ChaosInjector

```python
ChaosInjector(
    county_node: CountyNode,
    noise_budget: float = 0.10,
    noise_mode: NoiseMode = NoiseMode.BITFLIP,
    freedom_floor: float = 0.85,
    seed: Optional[int] = None,
)

# Methods
.inject_ballot(selection_vector: List[int]) -> BallotRecord
.inject_batch(selection_vectors: List[List[int]]) -> List[BallotRecord]
.inject_replay_attack(selection_vector: List[int]) -> dict
.inject_burst(template_vector: List[int], burst_size: int, ...) -> List[BallotRecord]
.inject_fuzzy_marks(confidence_vector: List[float], rounding_strategy: str) -> BallotRecord
.check_freedom_floor(county_ballot_counts: List[int]) -> bool  # raises FreedomFloorViolation
.injection_log -> List[InjectionEvent]
.noise_count() -> int
.clean_count() -> int
.total_events() -> int
.reset_log() -> None
```

### HolographicScreen

```python
HolographicScreen(
    min_confidence: float = 0.60,
    write_in_registry: Optional[WriteInRegistry] = None,
    races: Optional[int] = None,
)

# Methods
.normalise(raw_record: dict) -> List[int]  # raises AdmissibilityError
.normalise_batch(raw_records: List[dict]) -> List[List[int]]
.normalisation_log -> List[NormalisationRecord]
.normalisation_log_as_dicts() -> List[dict]
.rejection_count() -> int
.acceptance_count() -> int
.clean_passthrough_count() -> int
.reset_log() -> None
```

### PublicTrustIndexBuilder

```python
PublicTrustIndexBuilder(
    jurisdiction: str = "Washington State",
    county_count: int = 39,
)

# Methods
.from_closure_result(result: ClosureResult, ballot_count: int = 0, county_label: str = "") -> PublicTrustReport
.from_state_ledger(ledger_entry: StateLedgerEntry) -> PublicTrustReport
.from_raw_metrics(phi_eff: float, k_cs: int, ballot_count: int, ...) -> PublicTrustReport
```

### SentinelLoadBalancer (Phase 4 additions)

```python
SentinelLoadBalancer(
    target_phi_0: float = PHI_0,
    target_k_cs: int = K_CS,
    output_directory: Optional[str] = None,
    freedom_floor: float = 0.85,
    freedom_floor_min_ballots: int = 1,
)

# New methods (Phase 4)
.check_freedom_floor(county_ballot_counts: List[int]) -> bool  # raises FreedomFloorBreach
.check_participation_variance(county_ballot_counts: List[int]) -> dict
.freedom_floor_breach_count() -> int
```

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
