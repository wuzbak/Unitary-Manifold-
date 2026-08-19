# 12-AZ-IP/calculators — AxiomZero Interactive Calculators

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## Overview

This folder registers all **AxiomZero interactive calculator IP** — browser-based physics
calculators and simulators that expose the Unitary Manifold computation engines directly to
users with zero installation required.

Every calculator is backed by the same physics as the Python modules in `src/core/` — all
results are produced by the actual UM equations with zero approximations.

---

## Registered Calculators

### 1 · KK Mass Calculator
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/kk-mass-calculator.html` |
| **Python backing** | `src/core/metric.py` |
| **Description** | Computes the Kaluza-Klein graviton mass m_G_KK from warp factor k̃ (range: 0.01–0.15). Displays comparison to ATLAS/CMS Run 2 exclusion bounds and the UM lower bound of 5 TeV. Live slider interface with real-time output. |
| **Key physics** | m_G_KK = f(k̃, M_Pl, R₅); LHC Run 2 bound: > 4.5 TeV |
| **Status** | REGISTERED |
| **Category** | Particle Physics Calculator |

### 2 · Birefringence Predictor
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/birefringence-predictor.html` |
| **Python backing** | `src/core/` (birefringence module) |
| **Description** | Predicts CMB birefringence rotation angle β from the (n_w, k_CS) braid parameters. Displays the canonical predictions β ∈ {≈0.273°, ≈0.331°}, the admissible window [0.22°, 0.38°], and the falsifying gap [0.29°–0.31°]. LiteBIRD 2032 decision window shown. |
| **Key physics** | β = f(n_w, k_CS, c_s); n_w = 5, k_CS = 74 → β ∈ {0.273°, 0.331°} |
| **Falsifier** | β ∉ [0.22°, 0.38°] OR β ∈ [0.29°, 0.31°] → theory falsified |
| **Status** | REGISTERED |
| **Category** | CMB / Cosmology Calculator |

### 3 · ToE Score Dashboard
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/toe-score.html` |
| **Python backing** | `src/core/` (all modules) |
| **Description** | Live Theory of Everything score tracker. Displays the current score (29.0/28), all 13 admissions, 8 active predictions, 28 hardgate claims, and the 1 open measurement window (LiteBIRD 2032). Epistemic status clearly labeled for every item. |
| **Key data** | All SM derivation chains closed; 1 external measurement window open (LiteBIRD ~2032) |
| **Status** | REGISTERED |
| **Category** | Science Integrity Dashboard |

### 4 · CMB Parameters Calculator
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/cmb-parameters.html` |
| **Python backing** | `src/core/` (inflation, cmb_transfer modules) |
| **Description** | Interactive n_s, r, f_NL calculator. Adjust slow-roll parameter ε_SR and braided sound speed c_s. Compares against Planck 2018, ACT DR6, BICEP/Keck, and the SPHEREx f_NL decision window. Shows uncertainty bands and current observational constraints. |
| **Key predictions** | n_s = 0.9635 (Planck: 0.9649 ± 0.0042 ✅); r = 0.0315 (< 0.036 ✅); f_NL = −0.532 |
| **Status** | REGISTERED |
| **Category** | Cosmology Calculator |

### 5 · DESI Tension Tracker
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/desi-tracker.html` |
| **Python backing** | `data/desi/` |
| **Description** | Dark energy w₀-wₐ plane visualizer. Tracks the current 2.75σ DESI DR2 tension with the KK prediction wₐ = 0. Shows the DR3 decision tree (PASS / TENSION / FALSIFIED branches) and the frozen-radion architecture limit. Updates with each DESI data release. |
| **Key decision** | DESI DR3 (~2027): if |wₐ| > 0.15 at 3σ → tension; if > 5σ → falsification |
| **Status** | REGISTERED |
| **Category** | Cosmology Tracker |

### 6 · Lean4 Theorem Progress Tracker
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/lean4-progress.html` |
| **Python backing** | `lean4/UnitaryManifold/` |
| **Description** | Live tracker for formally verified Lean4 theorems. Shows 274 verified theorems across NP-BC-1/2/3/4 series, 12 sub-gap kernels, and progress toward the 300-theorem milestone. |
| **Current milestone** | 274/300 theorems proved; NP-BC-4 complete |
| **Status** | REGISTERED |
| **Category** | Formal Verification Tracker |

### 7 · Pentad Simulator
| Field | Value |
|-------|-------|
| **Source path** | `public-site/apps/pentad-simulator.html` |
| **Python backing** | `5-GOVERNANCE/Unitary Pentad/` |
| **Description** | 5-body HILS orbital simulator. Models the Unitary Pentad bodies (universe, brain, human, AI, trust field). Adjust coupling constants and watch the system converge to φ-ratio equilibrium or enter collapse. Real-time phase-space visualization. |
| **Key constants** | Ξ_c = 35/74; SENTINEL_CAPACITY = 12/37; HIL_PHASE_SHIFT_THRESHOLD = 15 |
| **Status** | REGISTERED |
| **Category** | Governance Simulator |

### 8 · 5D Space Explorer
| Field | Value |
|-------|-------|
| **Source path** | `public-site/explore/index.html` |
| **Python backing** | `src/core/metric.py`, `src/core/evolution.py` |
| **Description** | WebGL 3D interactive visualization of the Kaluza-Klein extra dimension. Navigate the S¹ fiber bundle, the KK tower, and the (5,7) winding strands. Real-time geometry computation via physics-engine.js. |
| **Technology** | Three.js + WebGL; `public-site/js/physics-engine.js` |
| **Status** | REGISTERED |
| **Category** | 3D Physics Visualizer |

### 9 · HILS Governance Interface
| Field | Value |
|-------|-------|
| **Source path** | `public-site/pentad/index.html` |
| **Python backing** | `5-GOVERNANCE/Unitary Pentad/` |
| **Description** | The full Unitary Pentad governance interface. Scenario runner, trust field calculator, 5-body stability analysis, and HILS Certification Protocol v1.0. |
| **Status** | REGISTERED |
| **Category** | Governance Interface |

---

## Pending Calculators (Roadmap)

| Calculator | Description | Target |
|------------|-------------|--------|
| φ-Field Decision Visualizer | Real-time visualization of φ-field routing across the 7-manager network | Q4 2026 |
| Pillar Explorer | Browse all 590 pillars with derivation links, test status, and claim board | Q4 2026 |
| Quantum Simulation Runner | Browser interface to KK-VQE and Fermi-Hubbard simulations | 2027 |
| Birefringence Live Feed | Live LiteBIRD data ingestion when available | 2032 |

---

## Assets Pending Integration from `wuzbak/Private`

> **Note:** Additional calculator assets from `wuzbak/Private` should be copied into
> `public-site/apps/` and registered here and in `../IP_REGISTRY.json`.

---

## Authorship

- **Scientific direction, calculator physics:** ThomasCory Walker-Pearson
- **Code architecture, UI implementation:** GitHub Copilot (AI)

---

*AxiomZero Calculators Registry v1.0 — 2026-08-18*
