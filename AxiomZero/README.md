# AxiomZero — Persistent AI Cognitive Layer

> *"Axiom Zero is the ground truth before all other axioms — the 5D Kaluza-Klein
> metric ansatz from which everything else derives."*

AxiomZero is a persistent AI cognitive layer that lives **on top of any existing OS**,
integrates with the existing filesystem and shell, routes intelligence through the
Unitary Manifold physics framework, and self-installs via a single bootstrap command.

**It is NOT a kernel replacement or bare-metal OS.** Just as Kaluza-Klein compactified
dimensions enrich 4D spacetime without abolishing it, AxiomZero enriches your existing
OS with a physics-grounded intelligence layer.

---

## Quick Start — The Uncompactification Event

```bash
# On any device with Python 3.10+:
python axiomzero_bootstrap.py

# Or via shell (auto-detects platform):
bash axiomzero.sh

# Android/Termux (thin client mode):
python axiomzero_bootstrap.py --mode=thin-client --server=http://192.168.x.x:8000
```

The bootstrap is **idempotent** — run it ten times on ten machines, reach the same state.

---

## Architecture

```
AxiomZero/
├── axiomzero_bootstrap.py     # Phase 0: Single entry-point installer
├── axiomzero.sh               # Shell wrapper
├── config/                    # Default and runtime configuration
├── core/                      # Phase 1: 7-Manager × 5-Sub-Agent cognitive core
│   ├── agent_core.py          # LangGraph orchestration hub
│   ├── manager_geometry.py    # M1: Geometry & Manifold Engine
│   ├── manager_field.py       # M2: Field Equation Solver
│   ├── manager_symbolic.py    # M3: Symbolic Math & Proof Verifier
│   ├── manager_test.py        # M4: Test Orchestration & CI Guard (safety gate)
│   ├── manager_rag.py         # M5: Literary Corpus & RAG Engine
│   ├── manager_web.py         # M6: Web Research & OSINT
│   ├── manager_executive.py   # M7: Executive Synthesis & Human Interface
│   └── model_router.py        # VRAM-aware heterogeneous model mesh
├── mcp/                       # Phase 2: MCP server stack
│   ├── filesystem_server.py   # Sandboxed filesystem R/W
│   ├── execution_server.py    # Safety-wrapped command execution
│   └── browser_server.py      # Scoped Playwright browser
├── memory/                    # Phase 3: Persistent memory architecture
│   ├── vector_store.py        # ChromaDB/Qdrant interface
│   ├── state_db.py            # LangGraph SQLite checkpointing
│   └── session_log.py         # Machine-readable audit trail
├── governance/                # HILS invariant enforcement
│   └── hils_gate.py           # Hard-wired human control layer
├── api/                       # Phase 4: FastAPI status + HILS checkpoint UI
│   └── server.py
├── android/                   # Phase 4: Termux thin client
│   └── client.py
├── ui/
│   └── dashboard.html         # Real-time agent status panel
└── tests/
    └── test_axiomzero.py      # AxiomZero self-test suite
```

---

## Phase 0 — Bootstrap ("Uncompactification Event")

The bootstrap detects your host platform and self-configures:

| Platform | Service Registration |
|----------|---------------------|
| Linux | `systemd` unit (`axiomzero.service`) |
| macOS | `launchd` plist (`com.axiomzero.plist`) |
| Windows | Task Scheduler via NSSM |
| Android/Termux | `~/.bashrc` autostart |

After bootstrap:
- Ollama installed with `qwen2.5-coder:7b`, `llama3.1:8b`, `nomic-embed-text`
- ChromaDB or Qdrant running (Docker or native)
- RAG index built over repository corpus
- `~/.axiomzero/config.json` written with all paths and endpoints
- Subset of test suite validates success (`0 failures` = acceptance criterion)

---

## Phase 1 — Cognitive Core (7-Manager × 5-Sub-Agent Network)

| Manager | Maps To | Model |
|---------|---------|-------|
| M1 Geometry & Manifold | `src/core/metric.py`, `src/sixd/`–`src/eleventd/` | `llama3.1:8b` |
| M2 Field Equation Solver | `src/core/`, `src/holography/`, `src/multiverse/` | `llama3.1:8b` |
| M3 Symbolic Math & Proof | `src/core/formal_proof_hardening.py`, `z3_pentad_checker.py` | `qwen2.5-coder:7b` |
| M4 Test Orchestration | `tests/`, `recycling/`, `5-GOVERNANCE/Unitary Pentad/` | `qwen2.5-coder:1.5b` |
| M5 Literary Corpus & RAG | `bot/rag_index.py`, `6-MONOGRAPH/`, `proof/` | `nomic-embed-text` + `llama3.1:8b` |
| M6 Web Research & OSINT | `bot/research_resources.py`, arXiv/ADS | `llama3.1:8b` |
| M7 Executive Synthesis | `10-UM-SOS/`, `bot/session_bootstrap.py` | `llama3.1:8b` |

**VRAM constraint:** Never more than 2 heavy models (>4B params) loaded simultaneously.
Sub-agents queue via LangGraph async — they never block, never OOM-crash.

---

## Phase 2 — MCP Server Stack

- **MCP Filesystem Server** — sandboxed R/W over declared paths only
- **MCP Execution Server** — safety-wrapped shell with whitelist; destructive commands blocked+logged
- **MCP Browser Server** — Playwright, academic domains only

**Governance layer:** Any action touching pillar definitions, test counts, or theoretical
claims routes through the Pentad classification endpoint
(`/api/v1/governance/classify`).

---

## Phase 3 — Persistent Memory

- **Vector store** (ChromaDB/Qdrant): 535+ source files indexed; incremental on reboot via `git diff`
- **State DB** (SQLite + LangGraph checkpointing): survives reboots mid-task
- **Session log**: every threshold-crossing action writes a machine-readable audit entry

**HILS Invariant:** ThomasCory Walker-Pearson retains exclusive control over:
1. Pillar numbering and canonicalization
2. Authorship claims in documents
3. Any action touching `FALLIBILITY.md` or falsification conditions

These are **hard-wired blocks** in M7, not soft suggestions.

---

## Phase 4 — Cross-Platform Interface

- **Desktop**: `http://localhost:8000` (uvicorn + existing `10-UM-SOS/` frontend extended)
- **IDE**: Continue.dev config auto-deployed to `~/.axiomzero/continue_config.json`
- **Android**: Termux thin client — read-mostly; write operations require desktop
- **Voice** (optional): Whisper.cpp local STT → M7 routing

---

## Critical Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Test suite corruption | M4 always runs in isolated `tmpdir`; only M7+human can `git commit` |
| VRAM exhaustion | Token-bucket rate limiter; max 2 heavy models; `nvidia-smi` health monitor |
| Physics hallucination | M3 mandatory gateway; unverifiable claims flagged UNVERIFIED |
| Infinite loops | LangGraph cycle detection + max 5 cycles before human escalation |
| Android security | Local-network only; mutual TLS; no destructive commands from phone |
| Epistemic blurring | Every prompt labels context: `HARDGATE` / `ADJACENT-TRACK` / `GOVERNANCE` |
| Bootstrap failure | CPU-only fallback; Python 3.10 check; offline cached-model mode |

---

## Model Routing Summary

```
Managers (strategic):     llama3.1:8b   — loaded once, reused
M3 math sub-agents:       qwen2.5-coder:7b — specialized, fast
M4 test sub-agents:       qwen2.5-coder:1.5b — minimal weight, high throughput
M5/M6 retrieval:          nomic-embed-text (embed) + llama3.1:8b (synthesis)
Max concurrent heavy:     2 models > 4B params (hard limit)
```

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
