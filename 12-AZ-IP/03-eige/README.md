# AxiomZero EIGE — Election Integrity Governance Engine

**Version:** 21.0.0 | **Status:** Phase 1-B Complete — 449 tests passing, 0 failures  
**Epistemic label:** 🔵 ADJACENT TRACK — governance application (not a physics claim)  
**Theory & scientific direction:** ThomasCory Walker-Pearson  
**Code architecture & implementation:** GitHub Copilot (AI)

---

## What Is EIGE?

EIGE is a **deterministic, mathematically verifiable chain-of-custody engine for elections**.

Existing election auditing tools — Benford's Law analysis, risk-limiting audits (RLAs), post-election sampling — share a structural flaw: they are retroactive, sampling-based, and probabilistic. They produce p-values, not proof. When both sides of a dispute cite the same heuristic tools and reach different conclusions, the dispute resolves by political weight, not technical certainty.

EIGE takes a different approach: it encodes the **entire ballot sequence as a mathematical invariant** that is computed in real time and verified continuously. Any structural manipulation — ballot stuffing, retroactive deletion, sequence reordering, administrative override — produces an immediate, machine-verifiable deviation from the invariant. This deviation is not a statistical signal; it is a deterministic cryptographic event.

> **An election is a field evolution, not a database.**

---

## A Note on the Math

EIGE's tamper-detection invariants (`k_CS = 74`, `φ₀ = π/4`) are drawn from the [Unitary Manifold](https://github.com/wuzbak/Unitary-Manifold-) physics framework. **You do not need to evaluate the cosmological physics to evaluate EIGE.**

The constants function as:
1. Seeds for a path-dependent rolling hash (tamper-detection)
2. Shard placement parameters for holographic persistence (resilience)
3. Anchors for zero-knowledge compliance certificates (federal audit)

Their operational validity requires only their mathematical properties — not verification of the underlying physical theory. See [BOOK.md §3](BOOK.md#3-the-philosophy-from-physics-to-governance) for the full "Analogical Sandbox" treatment. For a physics-free evaluation, see [`src/constants_engineering.py`](src/constants_engineering.py).

---

## What EIGE Detects

| Attack | Detection Mechanism |
|--------|---------------------|
| Ballot stuffing (inserting extra records) | Chern-Simons rolling hash disruption |
| Retroactive ballot deletion | Same — sequence-dependent hash encodes count |
| Sequence reordering | Non-commutativity of CS hash |
| Administrative override | SentinelLoadBalancer intercepts; OSCAL dossier emitted < 500ms |
| Infrastructure attack (ransomware, power loss) | 8-shard holographic persistence; inter-county peer replication |
| Precision attack (floating-point bias) | 512-bit mpmath out-of-band audit worker |
| Participation suppression (rural county zeroing) | Freedom Floor kill-switch |

## What EIGE Does NOT Detect

- Manipulation of the physical ballot before it enters the scanner
- Compromised scanner hardware that emits false integers
- Colluding operators who collectively suppress the audit trail before EIGE is activated
- Attacks below the HMAC-SHA-512 key management layer

See [BOOK.md §17](BOOK.md#17-known-limitations-and-open-problems) for the full limitations chapter.

---

## Quick Start

### Prerequisites

```bash
Python 3.11+
pip install -r requirements.txt
```

### Run the full test suite

```bash
cd EIGE/
python -m pytest tests/ -v
# Expected: 449 passed, 0 failed
```

### Run via Docker (one command)

```bash
docker build -t axiomzero-eige .
docker run --rm axiomzero-eige
# Runs full 449-test suite inside container
```

### Run the end-to-end synthetic election demo

```bash
python run_demo.py
# Simulates: 5 counties × 1,000 ballots → state mesh → federal audit → Public Trust Report
```

### Interactive Jupyter notebook

```bash
pip install jupyter
jupyter notebook notebooks/01_eige_quickstart.ipynb
```

---

## Architecture Overview

```
[COUNTY TIER — 39 nodes]
  ballot integer → CS rolling hash → 8 shards → φ_eff, k_CS
  [NO raw ballots leave the county tier]
       │
       ▼  Encrypted shard telemetry (TLS 1.3 mTLS)
[STATE TIER — aggregation]
  Cross-county braid sync → Holon Zero Certificate emission
       │
       ▼  OSCAL 1.5.0 ZK certificates only
[FEDERAL TIER — compliance window]
  Zero-knowledge certificate validation only
  RawDataAccessAttempt raised on any raw data query
```

Full system block diagram: [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Repository Structure

```
EIGE/
  README.md           ← You are here
  BOOK.md             ← 21-chapter full technical & operational reference
  ARCHITECTURE.md     ← System architecture and block diagrams
  COMPLIANCE.md       ← NIST VVSG 2.0 / SP-800-53 R5 / OSCAL 1.5.0 mapping
  ROADMAP.md          ← Phase 1 → 3 deployment schedule
  CHANGELOG.md        ← Version history
  SECURITY.md         ← Security policy and bug bounty
  EXPLAINER.md        ← 5-minute plain-English explainer
  FAQ.md              ← Skeptic FAQ (4 audiences)
  requirements.txt    ← Python dependencies
  Dockerfile          ← One-command test runner
  run_demo.py         ← End-to-end synthetic election demo
  src/                ← 13 Python modules (core engine)
  tests/              ← 449-test suite
  notebooks/          ← Jupyter quickstart
  blueprint/          ← Rust ingestion engine + Next.js UI blueprints
  infra/              ← Kubernetes / Istio deployment YAML
  outreach/           ← Engagement letters (King County, EAC/CISA, academic)
  paper/              ← arXiv preprint draft
  docs/               ← GitHub Pages landing page
```

---

## NIST Compliance

EIGE maps to NIST VVSG 2.0 and NIST SP-800-53 Rev 5:

| Component | NIST Control |
|-----------|-------------|
| CS rolling hash | SI-7 (Software Integrity) |
| 5D metric closure | AC-1 (Access Control Policy) |
| Override dossier (< 500ms) | AU-12 (Audit Generation) |
| Federal blind audit gate | AC-3 (Access Enforcement) |
| 8-shard holographic backup | CP-9 (System Backup) |
| 512-bit mpmath audit thread | CA-7 (Continuous Monitoring) |

Full control mapping: [COMPLIANCE.md](COMPLIANCE.md)

---

## Versioning & Release Artifacts

| Version | Tests | Status |
|---------|-------|--------|
| v21.0.0 (Phase 1-B complete) | 449 | ✅ All passing |
| v20.x (Phase 1 TRL-7) | 312 | ✅ Superseded |

---

## Authorship

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
