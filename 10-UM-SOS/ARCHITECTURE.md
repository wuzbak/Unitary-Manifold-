# UM-SOS Architecture Reference
## Unitary Manifold Scientific Operating System — Technical Design

*Version 1.0 — 2026-05-26*  
*Theory and scientific direction: ThomasCory Walker-Pearson*  
*Architecture, documentation, and code engineering: GitHub Copilot (AI)*

---

## Overview

UM-SOS is a seven-layer platform built on top of the Unitary Manifold physics framework (v14.2, 487+ pillars, 44,748 tests). Each layer is independently useful; together they constitute a unified scientific instrument with no equivalent anywhere in theoretical physics.

The architecture follows a clean separation of concerns:
- **Physics kernel** (`src/`) — the derivation engine, never modified for platform purposes
- **Evaluation layer** — reads predictions from the kernel, never writes to it
- **Presentation layer** — exposes results via API, UI, and queryable interfaces
- **Governance layer** — the Pentad enforces authority allocation across all cross-layer decisions

```
┌─────────────────────────────────────────────────────────────────┐
│                        UM-SOS PLATFORM                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 7: Scientific AI Interface (RAG + epistemic gate)  │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Layer 6: Governance Console (Unitary Pentad)             │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ┌────────────────────┐  ┌───────────────┐  ┌──────────────┐   │
│  │ Layer 3: Derivation│  │Layer 4: Prereg│  │Layer 5: Calc │   │
│  │ Graph Navigator    │  │istry Registry  │  │ Suite        │   │
│  └────────────────────┘  └───────────────┘  └──────────────┘   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Layer 2: Live Experimental Monitor                         │  │
│  └────────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  Layer 1: Prediction Engine (src/ physics kernel)           │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 1 — Prediction Engine

### Purpose
The derivation-to-prediction pipeline. Takes the 5D metric ansatz and 8 postulates as input; produces 28 Standard Model parameter predictions, CMB observables, neutrino parameters, gravitational wave signatures, and particle physics cross-sections as output.

### Current State
Fully operational. 487+ pillars implemented in `src/core/` (665 Python modules). Every prediction has a named source module, an epistemic label, and a corresponding test.

### Key Interfaces
```python
# Core derivation chain
from src.core.metric import assemble_5d_metric, compute_curvature
from src.core.evolution import FieldState, walker_pearson_step
from src.core.inflation import compute_spectral_index, compute_tensor_ratio
from src.multiverse.fixed_point import ftum_fixed_point
from src.holography.boundary import holographic_entropy

# SM parameter predictions
from src.core.sm_parameters import all_sm_predictions
from src.core.fermion_mass_absolute import fermion_mass_table
from src.core.pillar480_fermion_hierarchy_analytic import fermion_hierarchy_formula

# Experimental routing
from src.core.pillar486_desi_dr3_final_prep import desi_dr3_tripwire
from src.core.pillar437_spherex_fnl_preregistration import fnl_preregistration
from src.core.pillar475_juno_nlo_closure import juno_nlo_summary
```

### Architecture Principles
- **Immutable kernel:** The physics src/ modules are never modified to make predictions more convenient to access. The platform reads them; it does not reshape them.
- **Epistemic labels propagate:** Every prediction carries its label (DERIVED / CONSTRAINED / CONJECTURAL / ARCHITECTURE_LIMIT) from the source module to the API surface.
- **Test coverage is not optional:** 44,748 tests. 0 failures. Every new pillar requires a corresponding test file before it ships.

### Data Flow
```
8 Postulates (P1–P8)
    ↓
5D Metric Ansatz
    ↓
Kaluza-Klein Dimensional Reduction
    ↓
4D Effective Field Theory
    ↓  ↓  ↓  ↓
SM params | CMB | Neutrinos | GW signatures
    ↓
Epistemic labeling (DERIVED / CONSTRAINED / etc.)
    ↓
Falsification conditions attached
    ↓
Layer 2 (monitoring) + Layer 4 (preregistration)
```

---

## Layer 2 — Live Experimental Monitor

### Purpose
Automated evaluation of new experimental data against pre-registered UM predictions. Issues machine-readable verdicts (PASS / TENSION / FALSIFIED). Cannot be gamed — the prediction hashes predate the data.

### Current State
Machine-readable tripwires implemented for all eight major decision windows (DESI DR3, SO DR1, JUNO 2027, SPHEREx f_NL, nEDM@SNS, LiteBIRD, HL-LHC, Hyper-K). Verdict routing logic is executable Python, not prose. Rehearsal drills complete (Pillar 477: all 30 scenarios pass).

### Key Interfaces
```python
# Decision routing
from src.core.pillar367_desi_escalation import desi_routing_matrix
from src.core.pillar368_so_dr1_routing import so_dr1_joint_routing
from src.core.pillar369_juno_preregistration import juno_2027_routing
from src.core.pillar392_decision_readiness import decision_readiness_package_v12_8

# Tripwire evaluation
from src.core.pillar486_desi_dr3_final_prep import evaluate_desi_dr3
from src.core.pillar477_rehearsal_drills import run_all_rehearsal_drills

# Gatekeeper summary update
# (reads docs/GATEKEEPER_SUMMARY.md, writes updated verdicts)
from src.core.proof_closure_formal_cert import certification_report
```

### Planned Architecture (Phase 2)
```
arXiv / INSPIRE-HEP / Experiment APIs
    ↓ (daily cron, GitHub Actions)
Data ingestion module
    ↓
Parameter extraction (publication-specific parsers)
    ↓
Tripwire evaluation (existing routing modules)
    ↓
Verdict: PASS | TENSION | FALSIFIED
    ↓
GitHub PR with updated CLAIM_MASTER_BOARD.md + GATEKEEPER_SUMMARY.md
    ↓
GPG-signed public statement (issued automatically)
    ↓
Pentad governance review (for TENSION or FALSIFIED verdicts)
```

### Falsification Protocol
A result crosses from TENSION to FALSIFIED when it meets the pre-registered threshold at ≥3σ confidence. At that point:
1. The automated system issues the FALSIFIED verdict
2. The Pentad classifies the decision as CRITICAL (requires human review)
3. The human steward (ThomasCory Walker-Pearson) reviews the full chain
4. A public statement is issued with the GPG signature of both human and AI

This protocol is not improvised. It was designed and documented before any current experimental window opened.

---

## Layer 3 — Derivation Graph Navigator

### Purpose
An interactive, explorable map of the 45+ node directed acyclic graph of claim dependencies. Every node is a checkable artifact. The graph answers: "If X experimental result arrives, what does it affect and how much?"

### Current State
Machine-readable DAG implemented in Pillar 395 (`src/core/pillar395_derivation_graph_acyclicity.py`). Acyclicity formally verified (DFS, 0 cycles). Most critical postulate (N_e ≈ 60 e-folds) and most central node (FTUM fixed point) identified and documented.

### Key Interfaces
```python
from src.core.pillar395_derivation_graph_acyclicity import (
    derivation_dag_acyclicity_check,  # returns True (0 cycles)
    build_derivation_dag,              # returns networkx DiGraph
    most_critical_postulate,           # N_e ≈ 60 e-folds
    most_central_node,                 # FTUM fixed point
    downstream_impact,                 # "if X changes, what changes?"
    upstream_dependencies,             # "what does X depend on?"
)
```

### Planned Architecture (Phase 2)
- D3.js force-directed graph, hosted as static HTML
- Node colors: blue=DERIVED, yellow=CONSTRAINED, orange=CONJECTURAL, red=ARCHITECTURE_LIMIT, grey=FITTED
- Click any node → opens the source module and corresponding test file
- Drag a node → highlights its full upstream and downstream cascade
- "Falsification explorer": input a hypothetical experimental result → graph highlights which nodes flip

### Node Taxonomy
| Node Type | Count | Color | Meaning |
|-----------|-------|-------|---------|
| Postulate (P1–P8) | 8 | White border | Input assumptions |
| Derived claim | ~30 | Blue | Follows necessarily from postulates |
| Constrained | ~8 | Yellow | Derivation + observational input |
| Conjectural | ~4 | Orange | Formally stated but not proved |
| Architecture limit | ~8 | Red | Mathematically impossible in minimal EFT |
| Adjacent track | ~24+ | Light blue | Not hardgated; honest explorations |

---

## Layer 4 — Preregistration Registry

### Purpose
A public, cryptographically signed, timestamped registry of predictions made before experimental data arrives. The chain of custody is the public commit history of this repository — timestamps that predate the experiments we await.

### Current State
SHA-256 hashes committed for: SPHEREx f_NL (Pillar 437), HL-LHC KK graviton (Pillar 435), JUNO Δm²₃₁ (Pillar 369), DESI DR3 CPL one-page statement (Pillar 486). Z3 SMT consistency of all 13 admissions verified and committed (Pillar 454).

### Key Interfaces
```python
from src.core.pillar437_spherex_fnl_preregistration import (
    preregistration_hash,    # SHA-256 of {prediction, decision_criteria, timestamp}
    verify_preregistration_hash,
    fnl_decision_routing,    # callable: takes measured f_NL, returns verdict
)

from src.core.pillar435_hllhc_kkgraviton import (
    kkgraviton_preregistration_hash,
    sigma_br_table,          # cross-section table for all mass points
    hllhc_routing,           # takes measured mass limit, returns verdict
)
```

### Planned Architecture (Phase 2)
- Public registry hosted as static JSON + human-readable HTML
- Each entry: `{id, observable, prediction, units, decision_criteria, sha256_hash, timestamp, gpg_signature_human, gpg_signature_ai, decision_window, module_path}`
- Registry is append-only: new predictions added, old ones never modified
- When verdict is issued: entry updated with `{verdict, data_reference, verdict_timestamp, verdict_signature}`
- Public URL for each entry (stable, citable)

### Registry Schema (v1)
```json
{
  "id": "UM-PRED-001",
  "observable": "f_NL (non-Gaussianity)",
  "prediction": -0.532,
  "uncertainty_band": [-2.9, -0.2],
  "units": "dimensionless",
  "decision_criteria": {
    "PASS": "|f_NL_measured - (-0.532)| < 2.0 * sigma_SPHEREx",
    "TENSION": "2.0 <= |f_NL - (-0.532)| / sigma_SPHEREx < 3.0",
    "FALSIFIED": "|f_NL - (-0.532)| / sigma_SPHEREx >= 3.0"
  },
  "sha256_hash": "...",
  "timestamp": "2026-05-25T00:00:00Z",
  "decision_window": "SPHEREx full data 2027-2028",
  "module": "src/core/pillar437_spherex_fnl_preregistration.py",
  "pillar": 437,
  "verdict": null
}
```

---

## Layer 5 — Cross-Domain Calculator Suite

### Purpose
Exposes the 24+ domain application modules as a clean, labeled calculator interface for researchers outside theoretical physics who want to apply UM geometry to their domain.

### Current State
All domain modules implemented and tested. ~3,000+ domain-specific tests across medicine, climate, governance, ecology, consciousness, cold fusion, genetics, materials, marine biology, psychology, neuroscience, justice, and astronomy.

### Domain Index
| Domain | Module | Pillar | Tests |
|--------|--------|--------|-------|
| Consciousness | `src/consciousness/` | 9 | ~80 |
| Atomic structure | `src/atomic_structure/` | 14 | 187 |
| Cold fusion (COP) | `src/cold_fusion/` | 15 | 240 |
| Medicine (φ-homeostasis) | `src/medicine/` | 17 | 139 |
| Justice (φ-equity) | `src/justice/` | 18 | 124 |
| Governance | `src/governance/` | 19 | 115 |
| Neuroscience | `src/neuroscience/` | 20 | 92 |
| Ecology | `src/ecology/` | 21 | 70 |
| Climate | `src/climate/` | 22 | 66 |
| Marine | `src/marine/` | 23 | 72 |
| Psychology | `src/psychology/` | 24 | 82 |
| Genetics | `src/genetics/` | 25 | 78 |
| Materials | `src/materials/` | 26 | 75 |
| Lattice braid QFT | `src/core/` | 438/479/483 | ~120 |
| 6D baryogenesis | `src/core/` | 439/478 | ~90 |
| Fermion hierarchy | `src/core/` | 411/480 | ~60 |
| A₄ symmetry | `src/core/` | 420 | ~50 |
| Talagrand geometry | `src/core/` | 413 | 71 |

> **Label discipline:** Every adjacent-track calculator outputs its epistemic label. No calculator pretends its output is a hardgated physics prediction unless it genuinely is.

### Planned Architecture (Phase 2)
- Web form interface: select domain, input parameters, get labeled output
- Each calculator page shows: domain, UM geometric origin, epistemic label, test coverage, falsification condition (if any)
- Research API: `POST /calculate/{domain}` with JSON parameters, returns labeled JSON output

---

## Layer 6 — Governance Console

### Purpose
The Unitary Pentad as a live interface — a mathematically-grounded Human-in-the-Loop system for any organization that needs principled human-AI decision governance.

### Current State
Fully implemented and tested (~1,487 tests). The Pentad is an independent framework that borrows mathematical structure from the Unitary Manifold but does not depend on the physics being correct. See `SEPARATION.md` for the precise independence boundary.

### Core Components
```
5-GOVERNANCE/Unitary Pentad/
├── unitary_pentad.py              ← main Pentad class
├── pentad_workflow_engine.py      ← three-lane decision routing
├── sentinel_load_balance.py       ← per-sentinel entropy accounting
├── distributed_authority.py       ← Ξ_c authority allocation
├── hils_thermalization.py         ← HIL phase-shift detection
├── braid_topology.py              ← braid-based authority routing
├── consciousness_constant.py      ← Ξ_c = 35/74 implementation
├── legitimacy_guard.py            ← authority-inversion detection
├── stochastic_jitter.py           ← anti-gaming noise injection
├── pentad_interrogation.py        ← adversarial stress testing
└── pentad_operator_console.py     ← live dashboard interface
```

### Decision Routing Logic
```python
def route_decision(decision_text: str, context: dict) -> RoutingResult:
    """
    Returns: lane (ROUTINE/SENSITIVE/CRITICAL), required_quorum, authority_allocation
    
    ROUTINE:   AI executes autonomously.
    SENSITIVE: AI recommends; designated human reviews before execution.
    CRITICAL:  Human decides; AI provides structured analysis.
    """
```

### Planned Architecture (Phase 2)
- Web dashboard for real-time Pentad status monitoring
- REST API for external governance integration
- Webhook support: POST decision requests, receive routing verdicts
- Audit log: every decision classified, every routing choice timestamped and signed
- Enterprise bridge: `pentad_enterprise_bridge.py` already implements the protocol

---

## Layer 7 — Scientific AI Interface

### Purpose
A knowledge-grounded AI assistant that answers questions about the Unitary Manifold using only verified, epistemically-labeled information from the repository. It knows exactly what it does not know — and says so.

### Current State
RAG indexing infrastructure implemented in `bot/`. Ready for backend integration with an embedding model and a query API.

### Key Design Constraint
This is not a general-purpose LLM that happens to know about physics. It is a domain-specific assistant with a closed knowledge base. Every statement it makes carries the epistemic label of its source. If asked about something that is CONJECTURAL, it says so. If asked about something that is an ARCHITECTURE_LIMIT (impossible in the minimal model), it says so rather than speculating.

### Planned Architecture (Phase 2)
```
User query
    ↓
Embedding model (text-embedding-3-large or similar)
    ↓
Vector search over indexed repository chunks
    ↓
Retrieval: top-k chunks with metadata (pillar, label, module, test file)
    ↓
Prompt construction: [system: epistemic discipline] + [retrieved chunks] + [query]
    ↓
LLM generation (Claude / GPT-4o / Gemini — user's choice)
    ↓
Response post-processing: epistemic label injection
    ↓
Governance gate: if response touches SENSITIVE/CRITICAL domain → Pentad routing
    ↓
User response with inline citations and epistemic labels
```

### Epistemic Gate
Every generated response is post-processed to:
1. Identify all claims made
2. Look up each claim in the repository index
3. Attach the epistemic label from the source module
4. Flag any claim not found in the index as UNVERIFIED
5. Route SENSITIVE/CRITICAL responses through Pentad Layer 6

This makes it structurally impossible for the AI interface to misrepresent the epistemic status of any claim in this repository.

---

## Cross-Layer Data Model

The shared data model that allows all 7 layers to interoperate:

```python
@dataclass
class UMPrediction:
    observable: str          # human-readable name
    value: float             # central value in SI or natural units
    units: str               
    uncertainty: Optional[tuple]   # (lower, upper) or None
    label: EpistemicLabel    # DERIVED | CONSTRAINED | CONJECTURAL | etc.
    pillar: int              # which pillar derived this
    source_module: str       # path to src/ module
    test_file: str           # path to tests/ file
    preregistration_hash: Optional[str]    # SHA-256 if preregistered
    decision_window: Optional[str]         # experiment + expected date
    falsification_condition: str           # what value kills this
    current_verdict: Verdict # PASS | TENSION | FALSIFIED | PENDING

@dataclass  
class UMGap:
    admission_number: int    # 1–13
    description: str
    status: GapStatus        # OPEN | ARCHITECTURE_LIMIT | CLOSED | NARROWED
    close_module: Optional[str]  # module that closes it, if any
    upstream_predictions: list[str]  # which predictions this gap blocks
```

---

## Deployment Architecture (Phase 2 Target)

```
GitHub Repository (source of truth)
    ↓
GitHub Actions CI (44,748 tests on every push)
    ↓
Docker container (FastAPI backend + React frontend)
    ↓
Fly.io / Railway / Render (hosting)
    ↓
Public endpoints:
  /api/predict?observable=n_s           → Layer 1 (prediction)
  /api/status?experiment=DESI_DR3       → Layer 2 (monitor)
  /api/graph                            → Layer 3 (derivation DAG)
  /api/preregistered                    → Layer 4 (registry)
  /api/calculate?domain=medicine        → Layer 5 (calculators)
  /api/governance/classify              → Layer 6 (Pentad)
  /api/query                            → Layer 7 (AI interface)
```

---

## Security and Trust Model

- **Source of truth:** The GitHub repository. No other system can override it.
- **Governance:** All SENSITIVE/CRITICAL decisions route through the Pentad, which requires human review.
- **Immutability:** Preregistration hashes are in the public commit history. They cannot be changed without creating a visible, timestamped audit trail.
- **Epistemic honesty:** The epistemic label system prevents overclaiming. No module can label its output as DERIVED unless the derivation chain is in the source.
- **Separation:** The physics kernel (`src/`) never calls the governance layer. The governance layer calls the physics kernel. The dependency arrow is one-directional.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
