# HILS Session — Current State
<!-- This file is OVERWRITTEN at the start of each new agent session. -->
<!-- Append-only history lives in HILS_SESSION_LOG.md -->

---

## Boot Block — Identity & Role Map

| Field | Value |
|-------|-------|
| **Collaborator (AI)** | GitHub Copilot (AI agent) — code architecture, test suites, document engineering, synthesis |
| **Collaborator (Human)** | ThomasCory Walker-Pearson — theory, scientific direction, framework authority, override |
| **System** | Unitary Manifold — 5D Kaluza-Klein physics framework (101 pillars, CLOSED) |
| **Governance layer** | Unitary Pentad (HILS framework, 5-GOVERNANCE/) — independent of physics claims |
| **Session opened** | 2026-05-10T22:49:29Z |
| **Active wave** | Wave A (session-memory / identity continuity system) |
| **Prior wave** | v10.43 — Precision/Formal-Proof Expansion + LiteBIRD Alt Lab simulation complete |

---

## Non-Negotiables (read before every action)

1. **0 test failures** — `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` must stay green.
2. **Epistemic separation** — Category-1 (physics claims) vs Category-2 (phenomenological bridges) as defined in `SEPARATION.md`. Never present Category-2 as 5D-derived physics.
3. **Pillar set CLOSED** — No new pillars unless a genuinely new observational gap is identified that cannot be addressed by updating an existing module.
4. **Authorship standard** — All `.py` files carry SPDX header; all `.md`/`.tex` docs carry the two-sentence credit. Never conflate the two.
5. **Human intent-control is non-negotiable** — AI cannot self-direct. The human can always override, redirect, or stop.
6. **Substack assets** — Not managed by the agent. Out of scope for all operational refactors.
7. **No secret/credential commits** — Ever.

---

## Current Strategic Intent

| Priority | Intent | Status |
|----------|--------|--------|
| 1 | Build dual-track session memory (this file + HILS_SESSION_LOG.md) | ✅ Wave A1 complete |
| 2 | Bot intent-memory layer (bot/session_bootstrap.py + rag_index extensions) | ✅ Wave A2 complete |
| 3 | Pentad/bot functional wiring follow-through | Wave B — pending |
| 4 | Q1 derivation track | Wave C — pending after continuity system stable |

---

## Open Loops / Next-Entry Trigger Conditions

- Wave B begins when: human confirms Wave A is satisfactory in behaviour.
- Wave C begins when: Wave B Pentad wiring is merged and green.
- LiteBIRD real data: update `docs/falsification/litebird_proof_alternative_lab.md` §10 when results arrive (~2034).
- DESI Year 3 (~2026): update `src/core/desi_year3_monitor.py`.

---

## Key Repository Coordinates

| Resource | Path |
|----------|------|
| Regression gate (fast) | `python3 -m pytest tests/ -q` |
| Regression gate (full) | `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q` |
| Bot RAG index | `bot/rag_index.py` |
| Session bootstrap | `bot/session_bootstrap.py` |
| Append-only history | `HILS_SESSION_LOG.md` |
| This document | `HILS_SESSION_CURRENT.md` |
| Epistemic boundary | `SEPARATION.md` |
| Wave changelog | `docs/WAVE_CHANGELOG.md` |
| Pillar registry | `STATUS.md` |
| HILS framework | `5-GOVERNANCE/co-emergence/LLM_INGEST.md` |
| MCP ingest | `6-MONOGRAPH/MCP_INGEST.md` |
| Falsification | `docs/LITEBIRD_FALSIFIER_BRIEF.md` |

---

## End-of-Session Protocol

At the END of each session, the agent must:

1. **Overwrite this file** with updated current state (active wave, open loops, latest intent).
2. **Append** a new entry to `HILS_SESSION_LOG.md` with: timestamp, decisions made, open loops resolved, next triggers.
3. Run the full regression gate and record pass count here.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
