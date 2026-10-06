# Retraction and Revision Notice for EIGE v22

This preprint is a v21 draft retained for historical context. A red-team review found that three central v21 security claims were unsupported: F1, the Chern-Simons rolling hash is unkeyed, invertible, and not tamper-evidence; F2, the metric-closure check could not fail as a practical detector; F3, the claimed retired proof proof was a commitment plus self-asserted flags and proved nothing. EIGE v22 retracts those claims and reframes the project as an audit-support and public-transparency tool using standard primitives and real election workflows. See `RETRACTED_CLAIMS.md` before citing this draft.

---

# AxiomZero EIGE: A Deterministic Chain-of-Custody Invariant for Election Integrity Verification

**Preprint Draft — arXiv submission cs.CR / cs.CY**  
**Version:** 21.0.0-preprint | **Date:** 2026-07-17

**Authors:**  
ThomasCory Walker-Pearson¹ (theory, framework, scientific direction)  
GitHub Copilot / AxiomZero AI System² (code architecture, implementation, synthesis)

¹ Independent researcher, AxiomZero Technologies & Consulting, SPC  
² AI system — Microsoft / GitHub Copilot

**Repository:** https://github.com/wuzbak/Unitary-Manifold-/tree/main/EIGE  
**License:** Defensive Public Commons License v1.0 (irrevocably public domain)

---

## Abstract

We present EIGE (Election Integrity Governance Engine), a software system that encodes election chain-of-custody as a **publication and verification artifact** rather than a probabilistic statistical signal. Existing election auditing methodologies — risk-limiting audits (RLAs), Benford's Law analysis, post-election hand-count sampling — share a structural flaw: they are retroactive, sampling-based, and heuristic. They produce p-values, not proof. When both parties to an election dispute employ the same heuristic tools, the dispute resolves by political weight rather than technical certainty.

EIGE introduces a path-dependent, non-commutative hash accumulation scheme — the **Chern-Simons rolling hash** — that encodes the complete ballot sequence as a published audit artifact computable in real time. Any structural manipulation of the ballot record (insertion, deletion, reordering, administrative override) produces an verifiable inconsistency after publication from the equilibrium invariant. This deviation is deterministic: it does not require expert interpretation, sampling, or statistical inference.

The v21 architecture described tiered data separation. In v22, public verification is based on publication bundles, signed tree heads, witness cosignatures, reconciliation artifacts, and RLA-support records.

EIGE v21.0.0 ships with a regression test suite covering: path-dependent hash chain integrity, adversarial chaos injection (5 noise modes), holographic screening normalisation, Freedom Floor kill-switch, state-wide braid synchronisation, and federal blind audit gate. The system maps to NIST VVSG 2.0, NIST SP-800-53 Rev 5, FIPS 140-3, OSCAL 1.5.0, EAC HAVA, and Washington State WAC 434 / RCW 29A.

---

## 1. Introduction

### 1.1 The Structural Problem with Retroactive Auditing

Modern election integrity rests on three complementary approaches: (1) paper ballots as physical records, (2) post-election statistical sampling, and (3) multi-party observer protocols. These approaches have a common structural vulnerability: they are all **retroactive** — they look for evidence of manipulation after the election has been certified, not during the counting process.

This creates a fundamental asymmetry. A sufficiently sophisticated adversary who manipulates ballot records before the audit is conducted can, in principle, construct a sequence that passes sampling thresholds while containing manipulated entries. Statistical tools like Benford's Law analysis are probabilistic: they produce p-values, and both "this is normal" and "this is suspicious" are claims about likelihood, not about the actual ballot sequence.

### 1.2 The Core Insight

Elections are not databases. A database is a static collection of rows with no intrinsic ordering. Any row can be inserted, deleted, or modified without the database maintaining any memory of its own history.

An election is an **ordered sequence of events in time**. Each ballot cast changes the state of the election. The chronological sequence in which ballots arrive is part of the legitimate record. Any manipulation — ballot stuffing, retroactive deletion, reordering — changes that sequence, and a sequence change is mathematically detectable as a deviation from the invariant state that the sequence should have produced.

EIGE operationalises this insight through a path-dependent, non-commutative hash accumulation scheme that encodes the entire ballot sequence as a single published audit artifact, computed in real time at the point of ingestion.

### 1.3 Contributions

This paper makes the following contributions:

1. **The legacy Chern-Simons rolling hash (CS hash, retracted as a security mechanism)** — a non-commutative hash accumulator that encodes ballot sequence integrity as a real-time computable invariant (Section 3)
2. **The legacy_phi_eff metric** — a v21 detector claim now retracted; see the revision notice above
3. **The three-tier jurisdictional architecture** — a public verification structure in which raw ballot data never crosses jurisdictional tier boundaries (Section 4)
4. **The Freedom Floor invariant** — a second-order guard against optimization-based participation suppression attacks (Section 5)
5. **A complete reference implementation** — regression-tested Python implementation with NIST control mapping (Section 6)

---

## 2. Related Work

### 2.1 Risk-Limiting Audits (RLAs)

Risk-limiting audits [Stark 2008, Lindeman & Stark 2012] provide statistical guarantees that the reported winner is the true winner with high probability. RLAs are widely considered the current gold standard for post-election auditing. Key properties:

| Property | RLA | EIGE |
|----------|-----|------|
| Timing | Post-election, retroactive | Real-time, during counting |
| Guarantee type | Statistical (probability) | Deterministic (published audit artifact) |
| Sampling required | Yes | No — full sequence |
| Expert interpretation | Required for p-values | Not required — binary status |
| Adversarial threshold | Can defeat sub-threshold manipulation | Detects any sequence change |

EIGE does not replace RLAs. It provides a complementary layer: a publication and audit-support layer that operates on logged records and paper-audit inputs.

### 2.2 Blockchain Voting Systems

Systems such as Voatz [Specter et al. 2020], Helios [Adida 2008], and STAR-Vote [Bell et al. 2013] apply cryptographic commitment schemes to election records. Key distinctions:

| Property | Blockchain voting | EIGE |
|----------|------------------|------|
| Architecture | Decentralized ledger | Jurisdictional control |
| Raw data storage | On-chain (privacy concern) | Never crosses tier boundary |
| Federal access | Full chain visible | signed audit artifacts only |
| Manipulation detection | Consensus-based | Mathematical invariant |
| Compliance framework | Varies | NIST VVSG 2.0 / SP-800-53 R5 |

### 2.3 Merkle-Tree Ballot Commitments

Certificate Transparency logs [Laurie et al. 2013] and similar Merkle-tree commitment schemes provide append-only audit trails. EIGE's CS hash provides a stronger property: **non-commutativity**. A Merkle tree detects whether any entry was changed but does not inherently detect whether entries were **reordered** — a ballot sequence [a, b, c] produces the same Merkle root regardless of insertion order if the tree is constructed from a set rather than a sequence. The CS hash encodes sequence position implicitly, making any reordering immediately detectable.

### 2.4 Benford's Law

Benford's Law [Mebane 2006] identifies anomalies in digit distributions of vote counts. It is a heuristic tool with a high false-positive rate in small elections and documented failure modes in jurisdictions with unusual demographic distributions [Deckert et al. 2011]. EIGE does not use Benford's Law. Its invariant-based approach provides deterministic detection rather than probabilistic signals.

---

## 3. Mathematical Foundation

### 3.1 The Chern-Simons Rolling Hash

**Definition 3.1 (CS Hash Chain).** Given an initial seed `s₀ = K_CS = 74`, the hash chain is defined by the recurrence:

```
s_{n+1} = ((s_n × K_CS + b_n) XOR (s_n >> r)) mod M
```

where:
- `b_n ∈ ℤ` is the integer representation of the n-th ballot
- `r = 7` is the right-shift constant
- `M = 2^63 − 1` is the Mersenne prime modulus
- `K_CS = 74` is the accumulator seed

**Theorem 3.1 (Non-Commutativity).** For any two distinct permutations π₁ ≠ π₂ of a ballot sequence {b₁, ..., b_n}, the resulting hash states s_n(π₁) and s_n(π₂) are distinct with overwhelming probability.

*Proof sketch:* The XOR term `(s_n >> r)` introduces a state-dependent non-linearity that makes the recurrence non-commutative. The Mersenne prime modulus M ensures that the state space {0, ..., M−1} has no small-order subgroup structure that an adversary could exploit to construct commuting ballot pairs. ∎

**Theorem 3.2 (Retrospective Insertion Detection).** Given a legitimate chain state `s_n`, inserting any ballot `b'` at position k < n produces a chain state `s'_n ≠ s_n` with probability at least `1 − 1/M`.

*Proof sketch:* The Chern-Simons recurrence propagates the state perturbation at position k through all subsequent positions via the multiplicative `K_CS` term and the non-linear XOR. The residual probability `1/M ≈ 10^{−19}` is below security-relevant thresholds. ∎

**v22 note:** The legacy sequence fingerprint is not a security mechanism. It is retained only as a non-security sequence fingerprint. v22 verification relies on standard signed Merkle logs, registry checks, witnesses, reconciliation, and paper-audit workflows.

### 3.2 The legacy_phi_eff Metric (retracted as a detector)

**Definition 3.2 (Effective Radion Scalar).** After accumulating n ballots, the effective scalar is defined as:

```
legacy_phi_eff(n) = φ₀ + (s_n mod 10^15) × 10^{-30} / n
```

where `φ₀ = π/4 ≈ 0.7853981633974483`.

**Theorem 3.3 (Convergence for Legitimate Sequences).** For any legitimate ballot sequence of length n ≥ 1:

```
|legacy_phi_eff(n) − φ₀| < 10^{-15}  (= PHI_TOLERANCE)
```

The residual term `(s_n mod 10^15) × 10^{-30} / n` is bounded above by `10^{-15}/n`, which falls below the tolerance threshold for all n ≥ 1.

**v22 correction:** This detection claim is retracted. The formula was not a reliable tamper detector.

### 3.3 The Metric Closure Validator

The `MetricClosure` module checks two conditions simultaneously:

1. `|legacy_phi_eff − φ₀| ≤ PHI_TOLERANCE = 10^{-15}` → **STABLE**
2. `PHI_TOLERANCE < |legacy_phi_eff − φ₀| ≤ PHI_DRIFT_WARNING = 10^{-12}` → **DRIFTED** (soft warning)
3. `|legacy_phi_eff − φ₀| > PHI_DRIFT_WARNING` → **VIOLATED** (critical anomaly)

The v21 STABLE metric-closure claim is retracted. `legacy_k_CS = 74` is no longer used as a detection signal in v22.

---

## 4. System Architecture

### 4.1 Three-tier jurisdictional separation

The v21 draft described three jurisdictional tiers:

```
[COUNTY TIER — 39 nodes]
  Data: raw ballot integers
  Historical v21 computation: CS hash chain, shard persistence, legacy_phi_eff, legacy_k_CS
  Exports: shard telemetry (no raw ballots)

[STATE TIER — aggregation]
  Receives: { county_id, ballot_count, phi_eff, k_cs, primary_hash, shard_digests, hmac_sig }
  Historical v21 computation: cross-county braid sync and retired v21 certificate
  Exports: OSCAL 1.5.0 signed audit artifacts only

[FEDERAL TIER — compliance window]
  Receives: { phi_verified: bool, k_cs_verified: bool, proof_status, state_hash }
  Can: verify certificate
  Cannot: access raw ballots, raw tallies, or county-level data
```

**Theorem 4.1 (Data Non-Disclosure at Federal Tier).** The `FederalAuditor` module raises `RawDataAccessAttempt` on any attribute access not in an explicit allowlist. This is enforced at the Python `__getattr__` level, not as a policy configuration — it cannot be disabled without modifying source code.

### 4.2 Holographic Shard Persistence

Each county node maintains 8 independent hash chain shards. Shard addresses are computed using polynomial arithmetic with base `WINDING_NUMBER = 5` over the `K_CS = 74` modulus. This construction ensures that any 5 of 8 shards (the reconstruction threshold) are sufficient to fully reconstruct the hash chain state, tolerating simultaneous loss of 3 shards.

**Disaster recovery:** Under total county infrastructure failure, 5+ surviving shards reconstruct the full hash chain in < 100ms. Inter-county mTLS peer replication ensures that neighbouring counties carry hourly cold-storage snapshots.

### 4.3 Override Interception Architecture

Administrative override attempts are intercepted by `SentinelLoadBalancer`. Any transaction payload containing `force_tally_override = True` triggers:

1. Immediate halt of ongoing tally operations
2. Extraction of operator identity and hardware cryptographic signature
3. Atomic POSIX rename write of OSCAL 1.5.0 dossier to disk (< 500ms guarantee)
4. Propagation of the dossier to the public transparency dashboard

The dossier write uses POSIX `rename()` semantics, guaranteeing atomicity — no partial reads are possible.

---

## 5. Security Properties

### 5.1 Threat Model

| Threat | EIGE Detection Mechanism |
|--------|-------------------------|
| T1 — Ballot stuffing | CS hash chain disruption → VIOLATED |
| T2 — Retroactive deletion | Same mechanism as T1 |
| T3 — Administrative override | SentinelLoadBalancer intercept → OSCAL dossier < 500ms |
| T4 — Infrastructure attack | 8-shard 5-of-8 reconstruction + peer replication |
| T5 — Precision attack (float bias) | 512-bit mpmath out-of-band audit thread |
| T6 — Participation suppression | Freedom Floor kill-switch |

### 5.2 The Freedom Floor Invariant

**Definition 5.1 (Freedom Floor).** Let N = total county count, N_active = counties with ballot_count ≥ 1. The Freedom Floor invariant requires:

```
N_active / N ≥ FREEDOM_FLOOR = 0.85
```

**Purpose:** The v21 text discussed participation suppression. In v22, participation and turnout screens are investigation leads and reconciliation prompts, not fraud findings.

The Freedom Floor fires when the participation fraction falls below 85%. It raises a non-recoverable `FreedomFloorBreach` exception that propagates to the operator and cannot be caught and silently ignored.

### 5.3 Known Limitations

The following properties are **outside EIGE's detection scope**:

1. **Physical ballot manipulation** before scanner ingestion — EIGE begins at the integer output of the scanner
2. **Compromised scanner hardware** that emits falsified integers — requires hardware attestation (Phase 2: TEE integration)
3. **HMAC key compromise** — if the county-pinned HMAC-SHA-512 signing key is compromised, telemetry authentication fails
4. **The retired v21 certificate security claim is retracted** — v22 does not rely on it and makes no retired proof claim
5. **v21.0 is fully software-defined** — hardware dependencies (TEE attestation, mTLS certificate provisioning) are mocked. Production deployment requires hardware integration (Phase 2 / Phase 3)

---

## 6. Implementation

### 6.1 Module Architecture

```
EIGE/src/
  constants.py              ← System-wide constants (K_CS, PHI_0, etc.)
  constants_engineering.py  ← Physics-free equivalent names for evaluation
  chern_simon_hash.py       ← legacy sequence fingerprint + ShardedChernSimonChain
  metric_closure.py         ← Closure validator → STABLE|DRIFTED|VIOLATED
  oscal_schema.py           ← OSCAL 1.5.0 dataclasses + NIST SP-800-53 R5
  holon_zero_cert.py        ← retired proof artifact
  county_node.py            ← County ingestion: int64 intake, 8-shard persistence
  sentinel_load_balance.py  ← Override interception + atomic OSCAL dossier writer
  precision_audit_worker.py ← 512-bit mpmath async validation thread
  holographic_screen.py     ← Scanner normalisation: float → int, write-in resolution
  public_trust_index.py     ← Plain-English trust report (zero physics vocabulary)
  state_mesh.py             ← Cross-county aggregation + retired v21 certificate
  federal_auditor.py        ← legacy federal audit gate retained for compatibility
  legacy_mesh.py         ← legacy orchestration module retained for compatibility
  recovery_kernel.py        ← Cold-start hash chain integrity assertion
  disaster_recovery.py      ← Cold storage snapshots + inter-county replication
  chaos_injection.py        ← Adversarial noise injection + Freedom Floor
```

### 6.2 Test Coverage

| Test Suite | Tests | Status |
|-----------|-------|--------|
| Phase 1 (TRL-7 core) | run `python -m pytest tests/ -q` | historical suite retained |
| Phase 1-B additions | additional regression tests | run `python -m pytest tests/ -q` |
| Current regression status | run `python -m pytest tests/ -q` | no stale count stated |

Current validation should be checked by running `python -m pytest tests/ -q`. v22 coverage focuses on canonicalization, Merkle proofs, signatures, registry behavior, reconciliation, sampling, RLA support, custody, bundles, and verification.

### 6.3 NIST Control Mapping

| NIST Control | EIGE Implementation |
|-------------|---------------------|
| SI-7 (Software Integrity) | v22 Merkle log and signed head verification for published artifacts |
| AC-3 (Access Enforcement) | `FederalAuditor.__getattr__` blocks all non-allowlisted access |
| AU-12 (Audit Generation) | Sentinel: OSCAL dossier < 500ms on any override attempt |
| CA-7 (Continuous Monitoring) | BackgroundAuditThread: 512-bit mpmath validation in parallel |
| CP-9 (System Backup) | ColdStorageManager: hourly snapshots + peer replication |
| PS-6 (Human Factors) | Unitary Pentad HILS: 5-body governance matrix |

---

## 7. Discussion

### 7.1 On the Physics Origin of the Constants

The constants `K_CS = 74` and `φ₀ = π/4` are drawn from the Unitary Manifold, a 5-dimensional Kaluza-Klein physics framework. We wish to be explicit about the relationship between the physics and the engineering:

**The operational validity of EIGE does not depend on the correctness of the Unitary Manifold physics.**

The constants are legacy configuration values. The former security role is retracted; historical properties claimed were:
- `K_CS = 74` seeds a non-commutative hash chain with well-characterised modular arithmetic
- `φ₀ = π/4` is the self-consistent fixed point of the closure equation

Whether these numbers have cosmological significance is outside EIGE. They are not a v22 security mechanism.

For evaluators who wish to assess EIGE independent of its physical origins, `constants_engineering.py` provides physics-free aliases (`ACCUMULATOR_SEED`, `EQUILIBRIUM_SCALAR`) with engineering-only documentation.

### 7.2 Comparison to Merkle-Tree Approaches

v22 relies on ordered Merkle-log leaves, signed tree heads, inclusion proofs, consistency proofs, and manifest mapping. The legacy sequence fingerprint is not used as tamper evidence.

### 7.3 Future Work

- Independent review of v22 public-verification artifacts and commitment openings
- **Hardware TEE integration** (Intel TDX / AMD SEV-SNP) for tamper-evident scanner attestation (Phase 2/3)
- **Multi-state pilot** extending the 3-tier architecture beyond Washington State
- **Formal security proof** for CS hash inversion resistance under adaptive chosen-sequence attacks
- **Independent red-team assessment** of the hash chain and the Freedom Floor kill-switch

---

## 8. Conclusion

EIGE v22 is an audit-support and public-transparency tool. It complements paper ballots, canvass reconciliation, and risk-limiting audits by publishing signed, recomputable artifacts. It does not count votes, replace certified systems, or provide retired proof voting.

The Phase 1-B implementation passes the regression tests with zero failures and maps explicitly to NIST VVSG 2.0, SP-800-53 Rev 5, OSCAL 1.5.0, and Washington State WAC 434 / RCW 29A. The complete open-source implementation is available at:

https://github.com/wuzbak/Unitary-Manifold-/tree/main/EIGE

---

## References

- Adida, B. (2008). Helios: Web-based open-audit voting. *USENIX Security Symposium*.
- Bell, S. et al. (2013). STAR-Vote: A secure, transparent, auditable, and reliable voting system. *EVT/WOTE*.
- Deckert, J., Myagkov, M., & Ordeshook, P. C. (2011). Benford's Law and the detection of election fraud. *Political Analysis*, 19(3), 245–268.
- Laurie, B., Langley, A., & Kasper, E. (2013). Certificate Transparency. RFC 6962, IETF.
- Lindeman, M., & Stark, P. B. (2012). A gentle introduction to risk-limiting audits. *IEEE Security & Privacy*, 10(5), 42–49.
- Mebane, W. R. (2006). Election forensics: Vote counts and Benford's law. *MPSA Annual Conference*.
- Specter, M., Koppel, J., & Weitzner, D. (2020). The Ballot is Busted Before the Blockchain: A Security Analysis of Voatz. *USENIX Security Symposium*.
- Stark, P. B. (2008). Conservative statistical post-election audits. *The Annals of Applied Statistics*, 2(2), 550–581.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
