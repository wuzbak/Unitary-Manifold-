# 12-AZ-IP/os — AxiomZero Operating Systems

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Overview

This folder registers all **AxiomZero operating system IP** — bare-metal kernels, cognitive OS
layers, and scientific operating systems developed under the AxiomZero technology stack.

---

## Registered Operating Systems

### 1 · AZ-OS — AxiomZero Cognitive Operating System
| Field | Value |
|-------|-------|
| **Source path** | `az-os/` |
| **Key files** | `agent_core.py`, `hils.py`, `state.py`, `phi_decision_engine.py`, `phi_field_interface.py`, `managers/m1_geometry.py` … `m7_interface.py` |
| **Language** | Python 3.12+ |
| **Description** | A Python-based cognitive operating system built on the 5D Kaluza-Klein physics framework. AZ-OS implements a 7-manager × 5-sub-agent AI network where every decision is weighted by φ-field alignment scores derived from the Walker-Pearson metric. It integrates HILS (Human-in-the-Loop Systems) at the kernel level, making this the first known operating system with formal human-AI oversight as a primitive. |
| **Architecture** | 7 managers × 5 sub-agents; φ-field decision routing; HILS state machine; shared cognitive/kernel state |
| **Registered SHA-256s** | See `../FINGERPRINT_MANIFEST.md` for `agent_core.py`, `hils.py`, `state.py` |
| **Status** | REGISTERED |
| **Category** | Cognitive OS |

#### AZ-OS Manager Network

| Manager | File | Responsibility |
|---------|------|---------------|
| M1 | `managers/m1_geometry.py` | KK geometry queries, metric evaluation |
| M2 | `managers/m2_fields.py` | Field evolution, constraint propagation |
| M3 | `managers/m3_symbolic.py` | Symbolic math (SymPy / Lean4 bridge) |
| M4 | `managers/m4_test_guard.py` | Live test guard, 0-failure enforcement |
| M5 | `managers/m5_corpus.py` | Pillar corpus indexing, RAG retrieval |
| M6 | `managers/m6_research.py` | Autonomous research, adjacent track exploration |
| M7 | `managers/m7_interface.py` | External interface (API, MCP, web) |

---

### 2 · AZ-KERNEL — AxiomZero Bare-Metal Kernel
| Field | Value |
|-------|-------|
| **Source path** | `az-kernel/` |
| **Key files** | `Cargo.toml`, `rust-toolchain.toml`, `src/main.rs`, `src/framebuffer.rs`, `src/mm/`, `src/sched/`, `src/ipc/`, `src/fs/`, `src/drv/`, `src/panic_handler.rs` |
| **Language** | Rust (`no_std`, UEFI target) |
| **Description** | A Rust `no_std` bare-metal UEFI kernel whose scheduler, memory allocator, and IPC primitives are derived from the 5D Kaluza-Klein geometric structure. Winding number n_w = 5 informs the 5-level priority queue; the φ-ratio governs memory page alignment. The only known OS kernel with first-principles derivation from a unified physics theory. |
| **Architecture** | UEFI boot; bare-metal Rust; physics-derived 5-level scheduler; KK-geometric memory management |
| **Registered SHA-256s** | See `../FINGERPRINT_MANIFEST.md` for `Cargo.toml`, `rust-toolchain.toml` |
| **Status** | REGISTERED |
| **Category** | Bare-Metal Kernel |

---

### 3 · UM-SOS — Unitary Manifold Scientific Operating System
| Field | Value |
|-------|-------|
| **Source path** | `10-UM-SOS/` |
| **Key files** | `backend/`, `frontend/`, `graph/dag.json`, `graph/index.html`, `layers/`, `registry/predictions.json`, `scripts/build_registry.py`, `scripts/build_graph.py` |
| **Description** | A 7-layer scientific operating system for managing the Unitary Manifold research environment. Layers range from a prediction API (Layer 1) through experimental monitoring (Layer 2), derivation graph (Layer 3), preregistration (Layer 4), browser frontend (Layer 5), AI governance query (Layer 6), and full deployment bridge (Layer 7). Implements a tamper-evident, append-only preregistration registry. |
| **Architecture** | 7-layer stack; D3.js derivation DAG; REST API; GitHub Pages deployable |
| **Status** | REGISTERED |
| **Category** | Scientific OS |

---

### 4 · AxiomZero Full-Stack OS Environment
| Field | Value |
|-------|-------|
| **Source path** | `AxiomZero/` |
| **Key files** | `axiomzero.sh`, `axiomzero_bootstrap.py`, `docker-compose.yml`, `core/`, `api/`, `ui/`, `android/`, `memory/`, `mcp/`, `governance/`, `config/`, `tests/` |
| **Description** | The complete AxiomZero technology stack as an integrated OS environment. Includes bootstrap scripting, Docker containerization, persistent AI memory, MCP server integration, governance modules, and the full test suite. Designed for single-command deployment (`./axiomzero.sh`). |
| **Status** | REGISTERED |
| **Category** | Full-Stack OS Environment |

---

## Assets Pending Integration from `wuzbak/Private`

> **Note:** Additional OS assets from `wuzbak/Private` (additional kernels, OS variants, or
> platform-specific builds) should be copied here by the owner and registered in
> `../IP_REGISTRY.json`.

---

## Authorship

- **Scientific direction, OS architecture:** ThomasCory Walker-Pearson
- **Code architecture, test suites:** GitHub Copilot (AI)

---

*AxiomZero OS Registry v1.0 — 2026-08-18*
