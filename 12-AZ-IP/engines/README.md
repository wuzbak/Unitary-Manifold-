# 12-AZ-IP/engines — AxiomZero Physics & AI Engines

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Overview

This folder registers all **AxiomZero computation engine IP** — the core physics simulation
engines, AI inference engines, and specialized computation modules that power the Unitary
Manifold framework.

---

## Registered Engines

### 1 · Walker-Pearson Field Evolution Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/core/evolution.py` |
| **Description** | The primary numerical integrator for the 5D Kaluza-Klein field equations. Implements the Walker-Pearson integrator, FieldState API, and constraint evolution for the full UM metric ansatz. Drives all pillar computations. |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 2 · KK Metric & Curvature Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/core/metric.py` |
| **Description** | Kaluza-Klein metric computation engine. Calculates the 5D metric tensor, Ricci curvature, and derived geometric quantities from the warp factor k̃ and extra-dimensional radius R₅. Foundation for all hardgated physics. |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 3 · CMB Transfer & Inflation Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/core/` (inflation, cmb_transfer modules) |
| **Description** | Computes the CMB power spectrum (Cₗ), inflationary spectral index n_s = 0.9635, tensor-to-scalar ratio r = 0.0315, and f_NL from the braided winding parameters (n_w=5, k_CS=74, c_s=12/37). |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 4 · Birefringence Prediction Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/core/` (birefringence module) |
| **Description** | Computes the CMB birefringence rotation angle β from Chern-Simons coupling. Produces the canonical prediction β ∈ {≈0.273°, ≈0.331°} testable by LiteBIRD ~2032. The primary falsifier of the Unitary Manifold. |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 5 · FTUM Fixed-Point Iteration Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/multiverse/fixed_point.py` |
| **Description** | The Finite-Temperature Unitary Manifold (FTUM) engine. Implements the UEUM operator and fixed-point iteration for multiverse landscape thermodynamics. Used in Pillars 5, 29, 38. |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 6 · Holographic Boundary Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/holography/boundary.py` |
| **Description** | Holographic boundary dynamics engine. Computes entropy-area relations (Pillar 4), boundary state evolution, and AdS/CFT projection of the KK bulk. |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 7 · φ-Debt Recycling Engine (Pillar 16)
| Field | Value |
|-------|-------|
| **Source path** | `recycling/` |
| **Description** | φ-debt entropy accounting engine. Tracks informational debt flow through the 5D geometry, implements the golden-ratio entropy recycling protocol, and produces 316-test validated output. |
| **Status** | REGISTERED — HARDGATE |
| **Category** | Physics Engine |

### 8 · Quantum Simulation Engine (KK-VQE / Fermi-Hubbard)
| Field | Value |
|-------|-------|
| **Source path** | `src/quantum/` |
| **Description** | Variational quantum eigensolver applied to KK tower states. Implements Fermi-Hubbard model with Jordan-Wigner and Bravyi-Kitaev encodings. Bridges to XDiag quantum many-body simulator. Non-hardgate adjacent track. |
| **Status** | REGISTERED — ADJACENT TRACK |
| **Category** | Quantum Engine |

### 9 · AxiomZero Cognitive AI Engine
| Field | Value |
|-------|-------|
| **Source path** | `az-os/agent_core.py`, `az-os/phi_decision_engine.py`, `az-os/phi_field_interface.py` |
| **Description** | The 7-manager × 5-sub-agent cognitive AI network. Implements φ-field decision making, HILS routing, physics-aware LLM inference, and autonomous research assistance. Core of the AZ-OS. |
| **Status** | REGISTERED |
| **Category** | AI Engine |

### 10 · AxiomZero Model Router Engine
| Field | Value |
|-------|-------|
| **Source path** | `AxiomZero/core/model_router.py` |
| **Description** | Multi-model routing engine for the AxiomZero cognitive layer. Selects the optimal LLM/engine for each query type (geometry, fields, symbolic, test, corpus, research, interface) based on φ-field alignment scores. |
| **Status** | REGISTERED |
| **Category** | AI Engine |

### 11 · MAS Wave Engine
| Field | Value |
|-------|-------|
| **Source path** | `src/meta/` |
| **Description** | Multi-Agent System wave engine for emergent self-organization. Implements the MAS ledger protocol and wave-function consensus across the 7-manager network. |
| **Status** | REGISTERED |
| **Category** | AI Engine |

### 12 · EIGE Adjudicator Engine
| Field | Value |
|-------|-------|
| **Source path** | `EIGE/src/adjudicator_api.py`, `EIGE/src/chern_simon_hash.py`, `EIGE/src/chaos_injection.py` |
| **Description** | The Emergent Intelligence Governance Engine adjudicator. Applies Chern-Simons hashing for tamper-evident governance decisions, chaos-injection adversarial testing, and φ-weighted adjudication scores. |
| **Status** | REGISTERED |
| **Category** | Governance Engine |

### 13 · RAG Physics Engine (Retrieval-Augmented Generation)
| Field | Value |
|-------|-------|
| **Source path** | `bot/`, `9-INFRASTRUCTURE/bot/` |
| **Description** | Retrieval-augmented generation engine specialized for Unitary Manifold physics. Indexes all 590 pillars, test results, claims, and theorems for AI-assisted research and Copilot Extension. |
| **Status** | REGISTERED |
| **Category** | AI Engine |

### 14 · Unitary Pentad Simulation Engine
| Field | Value |
|-------|-------|
| **Source path** | `5-GOVERNANCE/Unitary Pentad/` |
| **Description** | 5-body HILS orbital simulation engine. Models universe, brain, human, AI, and trust field coupling dynamics. Implements Ξ_c = 35/74 consciousness coupling and SENTINEL_CAPACITY = 12/37 entropy bounds. |
| **Status** | REGISTERED |
| **Category** | Governance Engine |

---

## Assets Pending Integration from `wuzbak/Private`

> **Note:** Additional engine assets from `wuzbak/Private` should be copied here by the owner
> and registered in `../IP_REGISTRY.json`.

---

## Authorship

- **Scientific direction, algorithm design:** ThomasCory Walker-Pearson
- **Code architecture, test suites:** GitHub Copilot (AI)

---

*AxiomZero Engines Registry v1.0 — 2026-08-18*
