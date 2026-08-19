# 12-AZ-IP/tools — AxiomZero Development Tools & Bridges

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Overview

This folder registers all **AxiomZero tooling IP** — developer tools, formal verification bridges,
audit infrastructure, CI/CD automation, and AI assistant integrations.

---

## Registered Tools

### 1 · Internal Link Auditor
| Field | Value |
|-------|-------|
| **Source path** | `TOOLS/audit/check_internal_links.py` |
| **Description** | Crawls all Markdown files in the repository and validates every internal link reference. Catches broken documentation links before they reach CI. Run: `python TOOLS/audit/check_internal_links.py`. |
| **Status** | REGISTERED |
| **Category** | Documentation Tool |

### 2 · Physics Consistency Checker
| Field | Value |
|-------|-------|
| **Source path** | `TOOLS/checks/` |
| **Description** | Suite of physics-layer consistency checkers. Validates that pillar outputs are mutually consistent, that constants are not redefined, and that physics claim labels are consistent. |
| **Status** | REGISTERED |
| **Category** | Validation Tool |

### 3 · Lean4 Formal Proof Bridge
| Field | Value |
|-------|-------|
| **Source path** | `lean4/UnitaryManifold/`, `src/core/formal_proof_hardening.py` |
| **Description** | Bridge between Python numerical modules and Lean4 formal proofs. Exports theorem statements from Python, invokes Lean4 checker, and imports proof certificates back into the Python test suite. Underpins 274 formally verified theorems (NP-BC-1/2/3/4 series). |
| **Status** | REGISTERED |
| **Category** | Formal Verification Tool |

### 4 · Z3 SMT Bounds Verifier
| Field | Value |
|-------|-------|
| **Source path** | `src/core/z3_pentad_checker.py` |
| **Description** | Applies Z3 SMT solver to verify that Unitary Pentad governance invariants are formally satisfied. Checks SENTINEL_CAPACITY ≤ 12/37, Ξ_c = 35/74, and SUM_OF_SQUARES_RESONANCE = 74 as formal SMT constraints. |
| **Status** | REGISTERED |
| **Category** | Formal Verification Tool |

### 5 · SymPy Symbolic Metric Bridge
| Field | Value |
|-------|-------|
| **Source path** | `src/core/symbolic_metric.py` |
| **Description** | SymPy-powered symbolic computation of the KK metric, Christoffel symbols, and Riemann tensor. Produces LaTeX output for arXiv and Lean4 input for formal proofs. |
| **Status** | REGISTERED |
| **Category** | Symbolic Mathematics Tool |

### 6 · JAX GPU/TPU Acceleration Backend
| Field | Value |
|-------|-------|
| **Source path** | `src/core/jax_backend.py` |
| **Description** | Optional JAX acceleration layer for GPU/TPU-accelerated field evolution and automatic differentiation of the KK metric. Falls back gracefully to NumPy when JAX is unavailable. |
| **Status** | REGISTERED |
| **Category** | Acceleration Tool |

### 7 · W&B Experiment Tracker
| Field | Value |
|-------|-------|
| **Source path** | `src/core/wandb_logger.py` |
| **Description** | Weights & Biases integration for tracking physics computation experiments. Logs pillar outputs, convergence metrics, and CMB parameter sweeps. |
| **Status** | REGISTERED |
| **Category** | Experiment Tracking Tool |

### 8 · DVC Data Version Control
| Field | Value |
|-------|-------|
| **Source path** | `.dvc/` |
| **Description** | Data Version Control integration for managing large datasets (Planck data, CMB maps, simulation outputs). Tracks dataset provenance alongside code version history. |
| **Status** | REGISTERED |
| **Category** | Data Management Tool |

### 9 · RAG Copilot Extension & Custom GPT
| Field | Value |
|-------|-------|
| **Source path** | `bot/`, `9-INFRASTRUCTURE/bot/` |
| **Description** | GitHub Copilot Extension and Custom GPT backend. Indexes all 590 pillars, theorems, test results, and claims into a RAG vector store. Enables physics-aware AI coding assistance inside any editor or ChatGPT. |
| **Status** | REGISTERED |
| **Category** | AI Assistant Tool |

### 10 · AxiomZero Guard (SM-Seed Auditor)
| Field | Value |
|-------|-------|
| **Source path** | `src/core/axiomzero_guard.py` |
| **Registered SHA-256** | `f02d92c6482484ce639d4ff00bb9d675691fe53b2268cb2d255f90e8784806ee` |
| **Description** | Standard Model seed audit tool. Verifies that SM parameters (α, mₑ, mₚ, GF, etc.) are derived from zero free parameters in the 5D geometry. Reports zero-parameter status and flags any regressions. |
| **Status** | REGISTERED |
| **Category** | Physics Audit Tool |

### 11 · SLSA Provenance Generator
| Field | Value |
|-------|-------|
| **Source path** | `9-INFRASTRUCTURE/provenance/` |
| **Description** | Supply-chain level attestation generator (SLSA Level 2). Produces signed build provenance for all registered IP assets, enabling tamper-evident verification of the AxiomZero codebase. |
| **Status** | REGISTERED |
| **Category** | Security / Supply Chain Tool |

### 12 · CI/CD Workflow Suite
| Field | Value |
|-------|-------|
| **Source path** | `.github/workflows/` |
| **Description** | GitHub Actions workflow suite: test runner (49,850+ tests), CodeQL security scan, SLSA provenance attestation, UM-SOS pages deployment, and PR review automation. Enforces 0 test failures as a hard gate on every commit. |
| **Status** | REGISTERED |
| **Category** | CI/CD Tool |

### 13 · MCP Server Integration
| Field | Value |
|-------|-------|
| **Source path** | `AxiomZero/mcp/`, `az-os/mcp/`, `9-INFRASTRUCTURE/mcp-config.json` |
| **Description** | Model Context Protocol server configuration. Enables AI agents and editors to connect to the AxiomZero physics corpus, UM-SOS API, and HILS governance layer via standardized MCP. |
| **Status** | REGISTERED |
| **Category** | Integration Tool |

---

## Assets Pending Integration from `wuzbak/Private`

> **Note:** Additional tool assets from `wuzbak/Private` should be copied here by the owner
> and registered in `../IP_REGISTRY.json`.

---

## Authorship

- **Scientific direction, tool architecture:** ThomasCory Walker-Pearson
- **Code architecture, test suites:** GitHub Copilot (AI)

---

*AxiomZero Tools Registry v1.0 — 2026-08-18*
