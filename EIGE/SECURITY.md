# EIGE Security Policy

**AxiomZero EIGE v21.0 — Election Integrity Governance Engine**  
*Theory & scientific direction: ThomasCory Walker-Pearson*  
*Code architecture & implementation: GitHub Copilot (AI)*

---

## Overview

AxiomZero takes the security of EIGE seriously. This document describes our security policy, the scope of our security review program, and how to report vulnerabilities responsibly.

EIGE is an open-source election integrity system. Transparent adversarial review is a core design principle — not an afterthought. We actively welcome security researchers, cryptographers, and red-team practitioners to examine our work.

---

## Scope

### In scope (we want your reports)

| Component | What to look for |
|-----------|-----------------|
| **CS rolling hash** (`src/chern_simon_hash.py`) | Algebraic attacks, collision constructions, state-recovery from partial hash output, commutativity attacks |
| **Metric closure validator** (`src/metric_closure.py`) | False STABLE conditions, precision exploits, adversarial ballot sequences that pass closure without legitimate data |
| **Freedom Floor** (`src/sentinel_load_balance.py`) | Bypass conditions that allow participation suppression to go undetected |
| **Federal blind audit gate** (`src/federal_auditor.py`) | Raw data exfiltration paths, attribute reflection attacks, `__getattr__` bypass |
| **Override interception** (`src/sentinel_load_balance.py`) | Race conditions in dossier emission, atomicity failures, timing-based bypass |
| **Holographic shard reconstruction** (`src/chern_simon_hash.py`) | Below-threshold shard attacks, shard poisoning |
| **HMAC-SHA-512 telemetry** (`src/county_node.py`) | Key derivation weaknesses in the placeholder implementation |
| **HolographicScreen normalisation** (`src/holographic_screen.py`) | Input validation bypass, write-in injection, confidence-score manipulation |
| **Recovery kernel** (`src/recovery_kernel.py`) | Cold-start bypass conditions |

### Out of scope

- Bugs in Python itself, pytest, numpy, or mpmath
- Denial-of-service attacks that require local administrative access
- Theoretical issues that require hardware access (TEE, HSM) — Phase 2 deliverables
- The underlying cosmological physics of the Unitary Manifold — this is a separate scientific question
- Issues in the Rust/Go/Next.js blueprints (`blueprint/`) — these are reference blueprints, not production code

---

## Known Limitations (publicly documented — not vulnerabilities)

The following are **known and explicitly documented limitations**, not security vulnerabilities:

1. **The CS rolling hash is not a cryptographic hash.** It is a tamper-detection invariant. It should not be used as a standalone secret-preserving commitment scheme. Full cryptographic audit relies on SHA-512 block hashes and HMAC-SHA-512 shard signatures.

2. **The Holon Zero Certificate is a commitment-scheme architecture, not a formal ZK proof.** A formal zero-knowledge proof (zk-SNARK or Pedersen commitment) is a Phase 2 deliverable.

3. **v21.0 is fully software-defined.** Hardware dependencies (TEE attestation, mTLS certificate provisioning, hardware-pinned HMAC keys) are mocked. Production deployment requires hardware integration.

4. **The HMAC key derivation placeholder** in `county_node.py::CountyNode._derive_key()` uses a SHA-512 hash of the county ID. **This is explicitly documented as a placeholder** and must be replaced with hardware-backed key management in production.

Reporting one of the above as a new vulnerability is welcome only if you have discovered an additional attack vector beyond the documented limitation.

---

## Bug Bounty Program — CS Hash Cryptanalysis Challenge

We are offering an **open cryptanalysis challenge** focused on the Chern-Simons rolling hash:

### Challenge Description

Construct a ballot sequence `[b₁', b₂', ..., b_n']` that:

1. Differs from a given legitimate sequence `[b₁, b₂, ..., b_n]` by at least one entry
2. Produces the same final hash state `s_n` as the legitimate sequence
3. Produces a `φ_eff` value within `PHI_TOLERANCE = 10^{-15}` of `φ₀ = π/4`

### Prize

Recognition in:
- EIGE SECURITY.md Hall of Fame (below)
- EIGE arXiv preprint acknowledgements section
- EIGE v22.0 release notes

If the attack is novel and practically exploitable: we commit to a full security reassessment of the hash design and public disclosure within 30 days.

### Submission

Email: `axiomzero-security@proton.me` (or open a GitHub Issue marked `[SECURITY]`)

---

## Responsible Disclosure Policy

1. **Report privately first.** Email `axiomzero-security@proton.me` with subject `[EIGE SECURITY]`
2. **Include:** affected component, reproduction steps, version tested, your assessment of severity
3. **Response time:** We commit to an initial response within 5 business days
4. **Disclosure timeline:** We will aim to produce a fix or mitigation within 30 days of confirmation. We will coordinate public disclosure with you
5. **Credit:** We will credit you by name (or handle) in the patched release notes and in this document, unless you prefer anonymity

---

## Independent Review Status

| Component | Status |
|-----------|--------|
| CS rolling hash | Open for review — no independent review completed yet |
| Federal blind audit gate | Open for review |
| OSCAL dossier emission | Open for review |
| Full NIST SP-800-53 R5 penetration test | Phase 2 planned deliverable |
| Third-party red-team engagement | Phase 2 planned deliverable |

We are actively seeking academic cryptographers willing to co-sign an independent security assessment. If you are a researcher interested in this, contact us at the address above.

---

## Hall of Fame

*No submissions yet. Be the first.*

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
