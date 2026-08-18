# AxiomZero — IP Identity & Provenance Record

> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## 1 · Identification

| Field | Value |
|-------|-------|
| **Project name** | AxiomZero |
| **Full title** | AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold |
| **Version** | 1.0 (2026-06-15) |
| **Author / IP owner** | ThomasCory Walker-Pearson |
| **Repository** | https://github.com/wuzbak/Unitary-Manifold- |
| **Directory** | `AxiomZero/` (repository root) |
| **License** | Defensive Public Commons License v1.0 (2026) |
| **SPDX identifier** | `LicenseRef-DefensivePublicCommons-1.0` |
| **Copyright line** | `Copyright (C) 2026  ThomasCory Walker-Pearson` |

---

## 2 · What AxiomZero Is

AxiomZero is an original system design and implementation — a **persistent AI cognitive
layer** that:

- Runs on top of any existing OS (Windows / macOS / Linux / Android-Termux)
- Self-installs from a single bootstrap command (`python axiomzero_bootstrap.py`)
- Routes intelligence through the **Unitary Manifold** Kaluza-Klein physics framework
- Implements a **7-Manager × 5-Sub-Agent** LangGraph cognitive network
- Enforces physics correctness via M3 (Symbolic Verifier) and M4 (Test Guard)
- Enforces human-in-the-loop invariants via the **HILS Constitutional Gate**
- Provides MCP server stack: sandboxed filesystem, safety-wrapped shell, scoped browser
- Maintains persistent memory: ChromaDB vector store + SQLite state DB + JSONL audit log
- Serves a real-time FastAPI dashboard and Android/Termux thin client

The name *AxiomZero* is precise: Axiom Zero is the ground truth before all other axioms —
the 5D KK metric ansatz from which the Unitary Manifold derives. The bootstrap is the
"uncompactification event": one compact point that unfolds into the full-dimensional system.

---

## 3 · Authorship Partition

| Contribution | Responsible party |
|---|---|
| System concept and architecture design | ThomasCory Walker-Pearson |
| Physics framework integration (UM pillars, KK metric grounding) | ThomasCory Walker-Pearson |
| HILS governance invariants (what humans must retain control over) | ThomasCory Walker-Pearson |
| Python implementation (all `.py` files) | GitHub Copilot (AI) |
| Test suite (`tests/test_axiomzero.py`) | GitHub Copilot (AI) |
| Documentation (README.md, IDENTITY.md) | GitHub Copilot (AI) |
| Bootstrap installer (`axiomzero_bootstrap.py`) | GitHub Copilot (AI) |

This partition follows the HILS (Human-in-the-Loop Systems) framework documented in
`5-GOVERNANCE/co-emergence/` and `SEPARATION.md`.

---

## 4 · File Manifest & Fingerprint

Every Python source file in `AxiomZero/` carries:

```python
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
```

### Core files

| File | Role |
|------|------|
| `axiomzero_bootstrap.py` | Phase 0: cross-platform idempotent installer |
| `axiomzero.sh` | Shell wrapper for bootstrap |
| `core/agent_core.py` | Central LangGraph orchestrator (7 managers, HILS flow) |
| `core/model_router.py` | VRAM-aware heterogeneous model mesh |
| `core/manager_geometry.py` | M1: Geometry & Manifold Engine (5D KK) |
| `core/manager_field.py` | M2: Field Equation Solver |
| `core/manager_symbolic.py` | M3: Symbolic Math & Proof Verifier (mandatory gateway) |
| `core/manager_test.py` | M4: Test Orchestration & CI Guard (gatekeeper) |
| `core/manager_rag.py` | M5: Literary Corpus & RAG Engine |
| `core/manager_web.py` | M6: Web Research & OSINT (arXiv / ADS / Brave) |
| `core/manager_executive.py` | M7: Executive Synthesis & Human Interface |
| `memory/vector_store.py` | ChromaDB/Qdrant vector store with incremental indexing |
| `memory/state_db.py` | SQLite checkpoint store (crash-resumable) |
| `memory/session_log.py` | JSONL machine-readable audit trail |
| `mcp/filesystem_server.py` | MCP: sandboxed R/W (path-traversal blocked) |
| `mcp/execution_server.py` | MCP: safety-wrapped shell (whitelist/blocklist) |
| `mcp/browser_server.py` | MCP: Playwright headless (academic domains only) |
| `governance/hils_gate.py` | Constitutional HILS enforcement (hard-wired, not configurable) |
| `api/server.py` | FastAPI server (13 endpoints, real-time streaming) |
| `ui/dashboard.html` | Real-time web dashboard |
| `android/client.py` | Termux thin-client CLI |
| `tests/test_axiomzero.py` | 153-test self-test suite (0 failures required) |
| `config/default_config.json` | Default configuration |
| `docker-compose.yml` | ChromaDB + Qdrant + API services |
| `requirements.txt` | Python dependencies |

---

## 5 · HILS Invariants (Non-Negotiable)

The following are **hard-wired** in `governance/hils_gate.py` and cannot be changed by
any agent action, including AxiomZero itself:

1. **Pillar numbering and canonicalization** — exclusive to ThomasCory Walker-Pearson
2. **Authorship claims in documents** — exclusive to ThomasCory Walker-Pearson
3. **FALLIBILITY.md and falsification conditions** — read-only to all agents
4. **git commit to main** — requires explicit human approval via HILS checkpoint
5. **Epistemic promotion** — ADJACENT-TRACK claims cannot be certified as HARDGATE

These invariants are the constitutional layer of AxiomZero. They mirror the governance
framework of the Unitary Manifold itself.

---

## 6 · Contact & Citation

**For attribution, derivative works, or verification requests:**

- Repository: https://github.com/wuzbak/Unitary-Manifold-
- Issues: https://github.com/wuzbak/Unitary-Manifold-/issues
- Preferred citation:

```
Walker-Pearson, T. (2026). AxiomZero: Persistent AI Cognitive Layer for the
Unitary Manifold. In: The Unitary Manifold v12.1+.
https://github.com/wuzbak/Unitary-Manifold-/tree/main/AxiomZero
```

---

*IDENTITY.md version: 1.0 — 2026-06-15*  
*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
