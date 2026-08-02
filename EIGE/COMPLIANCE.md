# AxiomZero EIGE v21.0 — Compliance Reference Document

**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)  
**Version:** 21.0.0 | **Date:** 2026-07-17

---

## Applicable Standards

| Standard | Scope |
|----------|-------|
| **NIST VVSG 2.0** | Voting System Verification and Validation — data integrity, audit trails, chain of custody |
| **NIST SP 800-53 Rev 5** | Security and Privacy Controls — AC, SI, AU, CA, PS control families |
| **OSCAL 1.5.0** | Open Security Controls Assessment Language — machine-readable security posture (SSP, POA&M, SAR) |
| **FIPS 140-3** | Cryptographic module requirements — hash integrity, certificate chains |
| **EAC HAVA** | Help America Vote Act — audit trail, accessible records, federal certification framework |
| **WAC 434** | Washington Administrative Code — county-level ballot processing and public records requirements |
| **RCW 29A** | Revised Code of Washington — elections administration, candidate filing, canvassing |

---

## NIST SP-800-53 R5 Control Mapping

### Access Control (AC)

| Control | EIGE Implementation |
|---------|---------------------|
| AC-1 (Policy) | `metric_closure.py` enforces algorithmic access boundary via `ClosureStatus`; any drift triggers `SentinelLoadBalancer` dossier |
| AC-2 (Account Management) | Multi-party authentication required for ingestion node provisioning (Phase 2) |
| AC-3 (Access Enforcement) | `FederalAuditor.__getattr__` raises `RawDataAccessAttempt` for any non-allowlisted attribute; structural, not configurable |
| AC-6 (Least Privilege) | Federal tier receives zero raw ballot data; county tier shares only shard telemetry |

### Audit and Accountability (AU)

| Control | EIGE Implementation |
|---------|---------------------|
| AU-2 (Event Logging) | Every override attempt, drift event, and threshold violation logged to OSCAL dossier |
| AU-3 (Audit Record Content) | Dossier includes: timestamp, operator_id, hardware_id, drift_value, action_type, k_cs_observed, phi_observed |
| AU-9 (Audit Integrity) | Atomic write via POSIX rename; append-only; written to hardware-backed log before in-memory state update |
| AU-12 (Audit Generation) | `SentinelLoadBalancer.intercept_override()` auto-generates OSCAL 1.5.0 blob on every interception event |

### System and Information Integrity (SI)

| Control | EIGE Implementation |
|---------|---------------------|
| SI-3 (Malware Protection) | Input validation: all ballot integers are type-enforced `int64`; no eval, no exec, no shell injection surface |
| SI-7 (Software, Firmware, Integrity) | `ChernSimonChain`: path-dependent rolling hash makes retroactive ballot insertion cryptographically infeasible |
| SI-10 (Information Input Validation) | `BallotRecord`: int64 type enforcement; values outside `[0, BALLOT_INT_MAX]` raise `ValueError` before insertion |
| SI-12 (Information Management) | `ShardedChernSimonChain` persists across 8 independent shards; 5-of-8 threshold tolerates 3 simultaneous failures |

### Contingency Planning (CP)

| Control | EIGE Implementation |
|---------|---------------------|
| CP-2 (Contingency Plan) | `disaster_recovery.py`: full snapshot envelope + inter-county peer replication + retry queue |
| CP-6 (Alternate Processing Site) | Cold-storage snapshots replicated to peer county nodes; K8s CronJob (`eige-backup-cron.yaml`) |
| CP-9 (System Backup) | Hourly automated snapshots via `ColdStorageManager.create_snapshot()` |
| CP-10 (Recovery) | `RecoveryKernel.cold_start_integrity_assertion()` validates hash chain on boot before accepting new ballots |

### Security Assessment (CA)

| Control | EIGE Implementation |
|---------|---------------------|
| CA-2 (Assessments) | `FederalAuditor`: accepts only `HolonZeroCert` structs; runs `validate_holon_zero_cert()` on every audit call |
| CA-7 (Continuous Monitoring) | `BackgroundAuditThread`: runs 512-bit mpmath validation continuously in background, separate from ingest thread |
| CA-8 (Penetration Testing) | Phase 2 deliverable: 3rd-party red-team assessment of CS hash inversion resistance |

---

## OSCAL 1.5.0 Compliance

EIGE produces machine-readable OSCAL 1.5.0 Security Assessment Reports (SAR):

```
oscal_schema.py:
  - OscarControlStatus (dataclass) → individual NIST SP-800-53 R5 control record
  - OscarSystemSecurityPlan (dataclass) → SSP document structure
  - build_override_dossier() → factory for instantaneous dossier emission
  - Supported NIST controls: AC-1, AC-2, AC-3, AU-2, AU-3, AU-9, SI-7, SI-10, CA-2, CA-7
```

**Dossier structure (JSON-serializable dataclass):**
```
OverrideDossier:
  schema_version: "OSCAL-1.5.0"
  system_id: "EIGE-WA-{county_id}"
  timestamp: ISO-8601
  operator_id: str
  hardware_id: str
  action_type: "ADMINISTRATIVE_OVERRIDE"
  phi_observed: float
  phi_expected: π/4
  k_cs_observed: int
  k_cs_expected: 74
  drift_value: float
  metric_status: STABLE|DRIFTED|VIOLATED
  nist_controls_triggered: [AC-3, AU-2, AU-9, SI-7, ...]
  escalation_required: bool
```

---

## Cryptographic Assumptions

| Primitive | Algorithm | Notes |
|-----------|-----------|-------|
| Block hash | SHA-512 | Block digests before CS accumulation |
| HMAC | HMAC-SHA-256 | Shard telemetry authentication |
| CS hash | Polynomial accumulation mod k_CS=74 | Path-dependent; not cryptographically secure alone |
| ZK cert | Holon Zero protocol | Proves (φ_eff ≈ π/4 AND k_CS=74) without revealing ballot data |
| Shard distribution | 8-of-k_CS=74 braid topology | 5-of-8 Shamir-like threshold |

> **Note:** The Chern-Simons rolling hash is NOT a cryptographic hash and should not
> be used as a standalone secret-preserving commitment scheme.  It is a tamper-detection
> invariant — a structural guard against *unauthorized reordering* of ballot events.
> Full cryptographic audit trail relies on the SHA-512 block hashes and HMAC signatures
> over each shard telemetry packet.

---

## Washington State Specific Requirements (WAC 434 / RCW 29A)

- All ballot audit logs must be retained for 22 months minimum post-election
- Canvassing board must receive certified paper chain-of-custody report
- Any system override must be logged in the public records request-accessible audit trail
- EIGE OSCAL dossiers constitute the machine-readable layer of this paper trail

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
