# Federal Engagement — EAC, CISA, and NIST

**AxiomZero EIGE v21.0**  
**Engagement type:** Voluntary security disclosure and program notification  
**Target agencies:** EAC (Election Assistance Commission), CISA (Cybersecurity and Infrastructure Security Agency), NIST  
**Proposing organization:** AxiomZero Technologies & Consulting, SPC

---

## Overview

This document provides the text and context for outreach to three federal agencies:

1. **Election Assistance Commission (EAC)** — VVSG 2.0 program awareness
2. **CISA Elections Security** — voluntary security disclosure
3. **NIST** — OSCAL 1.5.0 and SP-800-53 R5 mapping notification

These are notification letters, not certification requests. EIGE v21.0 is a research prototype. We are not seeking federal certification at this stage. We are making federal agencies aware of a novel approach and requesting technical feedback.

---

## 1. EAC Notification Letter

**To:** Office of the Executive Director, Election Assistance Commission  
**Subject:** Notification — Novel Election Chain-of-Custody Invariant Technology (EIGE v21.0)

Dear EAC staff,

We are writing to notify the Election Assistance Commission of the public release of AxiomZero EIGE (Election Integrity Governance Engine) v21.0, an open-source software system that encodes election chain-of-custody as a deterministic mathematical invariant computable in real time.

EIGE is released as a research prototype under the Defensive Public Commons License (irrevocably public domain). We are not seeking VVSG 2.0 certification at this stage. We are notifying the EAC of this technology's existence and inviting technical review.

**Key technical properties:**

1. **Path-dependent rolling hash** — encodes the complete ballot sequence as a real-time mathematical invariant. Any structural manipulation (ballot stuffing, retroactive deletion, sequence reordering) produces an immediate, machine-verifiable deviation
2. **Three-tier sovereignty** — county → state → federal architecture in which raw ballot data never crosses tier boundaries; federal oversight is achieved through zero-knowledge OSCAL 1.5.0 certificates
3. **NIST VVSG 2.0 mapping** — explicit mapping to VVSG 2.0 data integrity and chain-of-custody requirements (documented in COMPLIANCE.md)
4. **NIST SP-800-53 Rev 5 mapping** — AC-3, AU-12, SI-7, CA-7, CP-9 controls explicitly implemented and tested

**Current status:**

- 449 passing tests, 0 failures (adversarial test suite included)
- Open-source: https://github.com/wuzbak/Unitary-Manifold-/tree/main/EIGE
- Phase 1-B complete (software-defined); Phase 2 (hardware TEE integration) pending

We would welcome a technical briefing with EAC staff and feedback on the VVSG 2.0 certification pathway. We are also interested in whether EIGE's zero-knowledge federal compliance layer would be of interest to the Commission's oversight work.

Respectfully,  
ThomasCory Walker-Pearson  
Scientific Director, AxiomZero Technologies & Consulting, SPC

---

## 2. CISA Elections Security Notification

**To:** CISA Elections Security Team (elections@cisa.dhs.gov)  
**Subject:** Voluntary Security Disclosure — EIGE v21.0 Open-Source Election Integrity Tool

Dear CISA Elections Security Team,

We are making a voluntary security disclosure in accordance with CISA's open-source security notification guidelines. We have released AxiomZero EIGE v21.0, an open-source election chain-of-custody verification engine, and wish to ensure CISA is aware of its security properties, design philosophy, and known limitations.

**What EIGE is:**

EIGE is a software system that encodes the ballot counting sequence as a path-dependent mathematical invariant, computed in real time at the point of ingestion. It provides:

- Real-time detection of ballot stuffing, retroactive deletion, and sequence reordering
- Administrative override interception with OSCAL 1.5.0 dossier emission < 500ms
- Federal compliance verification through zero-knowledge certificates (no raw ballot data at federal tier)
- 8-shard holographic persistence with disaster recovery (ransomware/power failure resilience)
- Adversarial test suite: 7 attack scenarios tested including chaos injection, replay attacks, and participation suppression

**What EIGE is not (known limitations — explicitly documented):**

- v21.0 is software-defined. Hardware TEE attestation is Phase 2
- The Holon Zero Certificate is a commitment-scheme architecture, not a formal ZK proof (Phase 2)
- The CS rolling hash is a tamper-detection invariant, not a cryptographic hash function
- EIGE does not cover physical ballot manipulation before scanner ingestion

**NIST mapping:** SP-800-53 Rev 5 (AC-1, AC-3, AU-2, AU-3, AU-9, AU-12, SI-7, SI-10, CA-2, CA-7, CP-2, CP-6, CP-9, CP-10), VVSG 2.0, OSCAL 1.5.0, FIPS 140-3

**Repository:** https://github.com/wuzbak/Unitary-Manifold-/tree/main/EIGE

We are actively seeking:

1. CISA technical review of the administrative override interception architecture
2. Feedback on whether EIGE's zero-knowledge federal compliance layer addresses CISA's "no central federal ballot database" policy concern
3. Notification of any CISA elections security programs that EIGE might be appropriate to participate in

We have a public bug bounty / cryptanalysis challenge open for the CS hash component. We welcome CISA security researchers to participate.

Respectfully,  
ThomasCory Walker-Pearson  
Scientific Director, AxiomZero Technologies & Consulting, SPC

---

## 3. NIST OSCAL Program Notification

**To:** NIST OSCAL Team (oscal@nist.gov)  
**Subject:** OSCAL 1.5.0 Implementation — EIGE v21.0 Open-Source Election Security System

Dear NIST OSCAL Team,

We are writing to notify the NIST OSCAL program of an open-source implementation of OSCAL 1.5.0 in an election security context.

AxiomZero EIGE v21.0 uses OSCAL 1.5.0 as its machine-readable security posture language:

- **Override dossiers** — OSCAL 1.5.0 JSON Security Assessment Reports emitted < 500ms on any administrative override attempt, mapping to SP-800-53 R5 controls (AC-3, AU-2, AU-9, SI-7)
- **Holon Zero Certificates** — OSCAL 1.5.0 structures used as zero-knowledge federal compliance certificates
- **System Security Plan** — `OscarSystemSecurityPlan` dataclass (`oscal_schema.py`) implements the SSP document structure

We would welcome feedback from the NIST OSCAL team on whether our implementation conforms to OSCAL 1.5.0 schema requirements and any guidance on the certification pathway for OSCAL-based election security documentation.

Repository: https://github.com/wuzbak/Unitary-Manifold-/tree/main/EIGE/src/oscal_schema.py

Respectfully,  
ThomasCory Walker-Pearson  
Scientific Director, AxiomZero Technologies & Consulting, SPC

---

## 4. Academic and NGO Channels

### MIT Election Lab

**Contact:** MIT Election Data and Science Lab (electionlab.mit.edu)  
**Submission:** Submit EIGE preprint to their working paper series  
**Key message:** Novel class of deterministic tamper-detection invariant; comparison vs. RLA methodology

### Verified Voting Foundation

**Contact:** verifiedvoting.org  
**Approach:** Notify of open-source release; request technical review  
**Key message:** EIGE complements paper audit trail — does not replace it

### OSET Institute (Open Source Election Technology)

**Contact:** osetinstitute.org  
**Approach:** Submit for inclusion in their open-source election technology registry  
**Key message:** Defensive Public Commons license; irrevocably public domain; no proprietary components

### ACM / IEEE Elections Security

**Venue targets:**
- IEEE Security & Privacy (Oakland) — security properties of CS hash
- ACM CCS — override interception and zero-knowledge compliance layer
- USENIX Security — adversarial resilience evaluation
- EVT/WOTE (Electronic Voting Technology / Workshop on Trustworthy Elections) — primary venue; most directly relevant

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
