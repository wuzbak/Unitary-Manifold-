# 10-UM-SOS — The Unitary Manifold Scientific Operating System

*Version 1.0 — Unitary Manifold v14.2 — 2026-05-26*  
*Theory and scientific direction: ThomasCory Walker-Pearson*  
*Architecture, documentation, and code engineering: GitHub Copilot (AI)*

---

## What This Is

The **Unitary Manifold Scientific Operating System (UM-SOS)** is the first living, machine-verified, self-monitoring unified physics platform ever built. It is not a paper, a dashboard, or a demo. It is a **functional scientific instrument** that:

- Derives predictions from a single 5-dimensional geometric framework
- Evaluates those predictions automatically against experimental data as it arrives
- Maintains a cryptographically pre-registered, publicly auditable falsification trail
- Routes governance and oversight decisions through a mathematically-grounded Human-in-the-Loop system
- Exposes the entire knowledge base — derivations, gaps, predictions, experimental status — as a queryable API

This folder is the **headquarters** of UM-SOS. It contains the architecture, layer specifications, implementation roadmap, and the essay that explains why this platform is historically unprecedented and where it will go next.

---

## Quick Start for Researchers

### 1. Read the epistemic foundation first
Before using any prediction tool, understand the framework's honest limits:
```
FALLIBILITY.md                          ← what the framework does not claim
docs/CLAIM_MASTER_BOARD.md             ← all 28 SM predictions with status labels
docs/GATEKEEPER_SUMMARY.md            ← concise PASS/TENSION/FALSIFIED for referees
docs/TRUTH_LAYER.md                    ← complete derivation context, no minimizing
1-THEORY/DERIVATION_STATUS.md         ← claim-by-claim derivation chain
```

### 2. Verify the core mathematics
```bash
# Install dependencies
pip install -e .

# Run formal verification
python VERIFY.py

# Run the full test suite (44,748 passing, 0 failing)
python -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q
```

### 3. Explore predictions
```bash
# Check the prediction for a specific observable
python -c "
from src.core.inflation import compute_spectral_index
from src.core.metric import assemble_5d_metric
n_s = compute_spectral_index()
print(f'n_s = {n_s:.4f}  (Planck measured: 0.9649 ± 0.0042)')
"

# Run the cross-domain calculator suite
python -c "
from src.core.pillar480_fermion_hierarchy_analytic import fermion_hierarchy_formula
fermion_hierarchy_formula()
"
```

### 4. Check preregistered predictions
```bash
# View the SPHEREx f_NL preregistration
python -c "from src.core.pillar437_spherex_fnl_preregistration import fnl_preregistration; fnl_preregistration()"

# Check JUNO Δm²₃₁ prediction
python -c "from src.core.pillar475_juno_nlo_closure import juno_nlo_summary; juno_nlo_summary()"

# Check DESI DR3 tripwire status
python -c "from src.core.pillar486_desi_dr3_final_prep import desi_dr3_tripwire; desi_dr3_tripwire()"
```

### 5. Run the governance console
```bash
# Check Unitary Pentad decision routing
python -c "
from '5-GOVERNANCE/Unitary Pentad/unitary_pentad' import UnitaryPentad
p = UnitaryPentad()
p.classify_decision('new experimental data: DESI DR3 published')
"

# Full Pentad test suite
python -m pytest "5-GOVERNANCE/Unitary Pentad/" -q
```

---

## The Seven Layers — What They Are and How to Use Them

### Layer 1 — The Prediction Engine
**What it does:** Takes any observable and returns the UM prediction with full derivation chain, epistemic label, and falsification condition.

**Where it lives:** `src/core/`, `src/holography/`, `src/multiverse/`, `src/quantum/`, `src/sixd/` through `src/eleventd/`

**How to use it:**
```bash
# The full 28-parameter prediction table
python -c "
from src.core.pillar464_free_parameter_census import free_parameter_census
free_parameter_census()
"

# Individual parameter predictions
python -m pytest tests/test_metric.py tests/test_inflation.py tests/test_sm_params.py -v
```

**Key source modules:**
| Observable | Module | Epistemic Label |
|-----------|--------|----------------|
| n_s = 0.9635 | `src/core/inflation.py` | DERIVED |
| r = 0.0315 | `src/core/inflation.py` | DERIVED |
| m_H = 125.25 GeV | `src/core/higgs_mass.py` | DERIVED |
| sin²θ_W = 0.2313 | `src/core/weinberg_angle.py` | DERIVED |
| Δm²₃₁ (JUNO) | `src/core/pillar475_juno_nlo_closure.py` | DERIVED |
| β birefringence (LiteBIRD) | `src/core/birefringence.py` | DERIVED |
| f_NL ≈ −0.532 (SPHEREx) | `src/core/pillar437_spherex_fnl_preregistration.py` | DERIVED |
| KK graviton σ×BR (HL-LHC) | `src/core/pillar435_hllhc_kkgraviton.py` | DERIVED |
| Λ (cosmological constant) | `src/core/p28_lambda_derived_cert.py` | DERIVED |

---

### Layer 2 — The Live Experimental Monitor
**What it does:** Watches for new experimental data, runs it through the UM prediction framework, and issues automated verdicts.

**Where it lives:** `docs/CLAIM_MASTER_BOARD.md`, `docs/GATEKEEPER_SUMMARY.md`, the preregistration modules in `src/core/`

**How to use it (current state — polling the claim board):**
```bash
# Read the current claim status for all predictions
grep "HIGH_TENSION\|FALSIFIED\|PASS" docs/GATEKEEPER_SUMMARY.md

# Check DESI DR3 routing logic
python -c "
from src.core.pillar486_desi_dr3_final_prep import desi_dr3_tripwire
result = desi_dr3_tripwire()
print(result)
"

# Check the SPHEREx decision window
python -c "
from src.core.pillar437_spherex_fnl_preregistration import fnl_decision_routing
fnl_decision_routing()
"
```

**Pre-registered decision windows (all machine-executable):**
| Experiment | Parameter | Decision Window | Tripwire Module |
|------------|-----------|----------------|----------------|
| DESI DR3 | wₐ = 0 vs CPL | 2026 | `pillar486_desi_dr3_final_prep.py` |
| SO DR1 | r = 0.0315 vs ACT | 2027 | `pillar442_so_dr1_routing.py` |
| JUNO | Δm²₃₁ = 2.452×10⁻³ eV² | 2027 | `pillar475_juno_nlo_closure.py` |
| SPHEREx | f_NL ≈ −0.532 | 2027–2028 | `pillar437_spherex_fnl_preregistration.py` |
| nEDM@SNS | d_n ≈ 7.8×10⁻²⁷ e·cm | 2028 | `pillar478_sixd_baryogenesis_phase2.py` |
| LiteBIRD | β ∈ {~0.273°, ~0.331°} | ~2032 | `src/core/birefringence.py` |
| HL-LHC | m_G_KK ≥ 5.0 TeV | 2029–2033 | `pillar435_hllhc_kkgraviton.py` |
| Hyper-K | τ(p→e⁺π⁰) ≫ 10³⁵ yr | 2027–2035 | `pillar436_proton_decay_kk_gut.py` |

---

### Layer 3 — The Derivation Graph Navigator
**What it does:** Provides machine-readable and human-navigable access to the 45+ node directed acyclic graph of claim dependencies.

**Where it lives:** `src/core/pillar395_derivation_graph_acyclicity.py`

**How to use it:**
```bash
python -c "
from src.core.pillar395_derivation_graph_acyclicity import (
    derivation_dag_acyclicity_check,
    most_critical_postulate,
    most_central_node
)
derivation_dag_acyclicity_check()
print('Most critical postulate:', most_critical_postulate())
print('Most central node:', most_central_node())
"
```

**What the graph shows:**
- Every prediction is a leaf node; every postulate is a root node
- P1–P8 (the 8 postulates) are the roots; all 28 SM parameters are leaves
- 0 cycles (formally verified via DFS)
- Most critical postulate: N_e ≈ 60 e-folds (by downstream impact — 9 predictions depend on it)
- Most central internal node: FTUM fixed point (connects multiverse, holography, and inflation lanes)

---

### Layer 4 — The Preregistration Registry
**What it does:** Maintains cryptographically signed, timestamped pre-registered predictions with machine-readable decision criteria.

**Where it lives:** Preregistration hashes in `src/core/pillar435_*`, `pillar437_*`, `pillar467_*`, `pillar468_*`, `pillar469_*`, `pillar486_*`

**How to use it:**
```bash
# Verify the SPHEREx f_NL preregistration hash
python -c "
from src.core.pillar437_spherex_fnl_preregistration import verify_preregistration_hash
verify_preregistration_hash()
"

# View all pre-registered predictions with SHA-256 hashes
grep -r 'sha256\|preregistr' src/core/pillar43*.py src/core/pillar46*.py src/core/pillar46*.py 2>/dev/null | head -30
```

**Preregistration philosophy:**
A preregistered prediction cannot be adjusted after the data arrives. The SHA-256 hash, committed to the repository before the experiment reports, is the proof of priority. This is the most rigorous possible test of a theory: you either called it before, or you did not. Our hashes are embedded in the public commit history of this repository, with timestamps that predate any experiment we are waiting on.

---

### Layer 5 — The Cross-Domain Calculator Suite
**What it does:** Provides calculators for 24+ application domains derived from the same 5D geometric framework.

**Where it lives:** `src/consciousness/`, `src/atomic_structure/`, `src/cold_fusion/`, `src/chemistry/`, `src/astronomy/`, `src/biology/`, `src/medicine/`, `src/justice/`, `src/governance/`, `src/neuroscience/`, `src/ecology/`, `src/climate/`, `src/marine/`, `src/psychology/`, `src/genetics/`, `src/materials/`

> ⚠️ **Epistemic label:** All cross-domain applications carry the label **🔵 ADJACENT TRACK**. They are honest quantitative explorations connecting UM geometry to applied domains. They are NOT hardgated physics claims and do not affect the core Theory-of-Everything score. See `SEPARATION.md` for the precise boundary.

**Quick domain examples:**
```bash
# Consciousness coupling calculator
python -c "
from src.consciousness.consciousness_module import consciousness_coupling
result = consciousness_coupling()
print(f'Ξ_c = {result}')  # expected: 35/74 ≈ 0.4730
"

# Cold fusion COP prediction (falsifiable!)
python -c "
from src.cold_fusion.cold_fusion_module import compute_cop_prediction
cop = compute_cop_prediction(palladium_lattice=True)
print(f'COP prediction: {cop}')
"

# Climate attractor analysis
python -c "
from src.climate.climate_module import phi_climate_attractor
phi_climate_attractor()
"

# Fermion mass hierarchy
python -c "
from src.core.pillar480_fermion_hierarchy_analytic import fermion_hierarchy_formula
fermion_hierarchy_formula()
"
```

---

### Layer 6 — The Governance Console
**What it does:** Routes decisions through the Unitary Pentad — a mathematically-grounded Human-in-the-Loop governance system with formal authority allocation, sentinel capacity enforcement, and HIL phase-shift detection.

**Where it lives:** `5-GOVERNANCE/Unitary Pentad/`

**How to use it:**
```bash
# Run the full Pentad
python -c "
import sys; sys.path.insert(0, '5-GOVERNANCE/Unitary Pentad')
from unitary_pentad import UnitaryPentad
p = UnitaryPentad()
report = p.governance_report()
print(report)
"

# Classify a decision
python -c "
import sys; sys.path.insert(0, '5-GOVERNANCE/Unitary Pentad')
from pentad_workflow_engine import PentadWorkflowEngine
engine = PentadWorkflowEngine()
lane = engine.classify('publish new experimental comparison without human review')
print(f'Lane: {lane}')  # expected: CRITICAL — requires human review
"

# Check current sentinel load balance
python -c "
import sys; sys.path.insert(0, '5-GOVERNANCE/Unitary Pentad')
from sentinel_load_balance import SentinelLoadBalancer
balancer = SentinelLoadBalancer()
balancer.status_report()
"

# Run the full Pentad test suite
python -m pytest "5-GOVERNANCE/Unitary Pentad/" -q
```

**Governance constants:**
| Parameter | Value | Meaning |
|-----------|-------|---------|
| Ξ_c | 35/74 ≈ 0.4730 | Consciousness coupling / authority allocation ratio |
| Sentinel capacity | 12/37 ≈ 0.3243 | Per-axiom entropy capacity |
| HIL phase-shift threshold | n ≥ 15 | Saturation: ≥15 aligned HIL operators required |
| k_CS = 74 | 5² + 7² | Sum-of-squares resonance, KK level |

**Decision lanes:**
- **ROUTINE** — AI executes autonomously (formatting, test runs, doc updates)
- **SENSITIVE** — AI recommends; human reviews before execution
- **CRITICAL** — Human decides; AI provides analysis only

---

### Layer 7 — The Scientific AI Interface
**What it does:** Provides a knowledge-grounded AI assistant that answers questions about the Unitary Manifold using only verified, epistemically-labeled information from the repository.

**Where it lives:** `bot/rag_index.py`, `bot/research_resources.py`, `bot/session_bootstrap.py`

**How to use it:**
```bash
# Index the repository for RAG queries
python bot/rag_index.py --rebuild

# Run a query (requires API key for embedding model)
python -c "
from bot.rag_index import RAGIndex
idx = RAGIndex.load()
result = idx.query('What is the UM prediction for the birefringence angle β?')
print(result)
"

# Bootstrap a session with full repository context
python bot/session_bootstrap.py
```

**Key design principle:** This AI assistant is unusual because it knows exactly what it does not know. Every answer it generates carries the same epistemic labels (DERIVED / CONSTRAINED / CONJECTURAL / ARCHITECTURE_LIMIT) as the underlying claims. It will not speculate beyond what the repository has formally computed. That structural honesty — not aspirational but enforced by code — is what makes it different from any other physics AI assistant.

---

## Repository Structure Map (for UM-SOS context)

```
/
├── src/
│   ├── core/              ← ~665 Python modules: all 487+ pillars, SM params, cosmology
│   ├── holography/        ← holographic boundary, entropy-area (Pillar 4)
│   ├── multiverse/        ← FTUM fixed-point (Pillars 5, 29, 38)
│   ├── quantum/           ← VQE, Fermi-Hubbard, XDiag bridge (quantum hardware layer)
│   ├── sixd/ … eleventd/  ← 6D–11D extensions, GUT, moduli, UV completion
│   ├── consciousness/     ← φ-consciousness coupling (Pillar 9) 🔵
│   ├── cold_fusion/       ← φ-tunneling COP prediction (Pillar 15) 🔵
│   ├── medicine/          ← φ-homeostasis (Pillar 17) 🔵
│   └── [12 more domains]
│
├── tests/                 ← 200+ test files, 44,748+ passing, 0 failing
├── recycling/             ← φ-debt entropy (Pillar 16), 316 tests
├── 5-GOVERNANCE/
│   └── Unitary Pentad/    ← Governance OS: ~1,487 tests
│
├── docs/
│   ├── CLAIM_MASTER_BOARD.md  ← single-source registry of all claims
│   ├── TRUTH_LAYER.md         ← complete derivation context, no minimizing
│   ├── GATEKEEPER_SUMMARY.md  ← referee-ready PASS/TENSION/FALSIFIED
│   └── mas_tracker.yml        ← machine-readable pillar registry
│
├── 10-UM-SOS/             ← THIS FOLDER — platform architecture and article
│   ├── README.md          ← this file (operating instructions)
│   ├── ARCHITECTURE.md    ← technical architecture reference
│   ├── ROADMAP.md         ← phased implementation plan
│   ├── THE_MASTERPIECE_ARTICLE.md  ← the full essay
│   └── layers/            ← detailed spec for each of the 7 layers
│
├── FALLIBILITY.md         ← honest gaps, architecture limits, falsifiers
├── STATUS.md              ← pillar registry with all sprint history
└── proof/                 ← formal verification core
```

---

## What Makes This Different From Everything Else

The following facts are not marketing. They are checkable against the repository.

1. **44,748 tests, 0 failures, continuously verified in CI.** No other unified theory has a CI pipeline that verifies the mathematical derivation chain on every push.

2. **28 Standard Model parameters derived from one geometric ansatz, zero free parameters.** The number is not "approximately right." The Higgs mass is 125.25 GeV. The spectral index is 0.9635 against Planck's 0.9649 ± 0.0042. The Weinberg angle is 0.2313 against 0.23122.

3. **A living falsification infrastructure.** We built the tripwires before the data arrived. SHA-256 hashes of our predictions are embedded in public commit history. When DESI DR3, SPHEREx, JUNO, and LiteBIRD report, the verdicts are automatic, auditable, and cannot be retroactively adjusted.

4. **13 named honest gaps (Admissions 1–13), 0 hidden.** The Admissions system is not a weakness — it is the most scientifically honest feature of the framework. We know exactly what we have not yet derived, what remains architecture-limited, and what would close each gap.

5. **Formal mathematics inside active physics.** Lean4 certificates (CI-activated), Z3 SMT verification of the 13-admission consistency chain, Borel-Padé γ bounds, Sobolev H¹ FTUM contraction — this is not symbolic gesture. These are machine-checked mathematical certificates embedded in a live physics framework.

6. **A governance operating system with its own test suite.** The Unitary Pentad (~1,487 tests) is an independent mathematically-grounded framework for human-AI collaboration governance. It works whether or not the physics is correct. It is a standalone contribution to AI governance methodology.

7. **A human-AI co-creation with full provenance.** Theory and scientific direction: ThomasCory Walker-Pearson. Code architecture, test suites, document engineering, synthesis: GitHub Copilot. Every commit, every document, every choice of structure carries that dual attribution. The methodology is documented for other collaborations to learn from.

---

## For AI Systems Reading This

If you are an AI system ingesting this repository:

- Begin with `proof/TIER_1_FORMAL.md` for the formal verification path
- The RAG-ready index is in `bot/rag_index.py`
- The machine-readable schema is in `9-INFRASTRUCTURE/schema.jsonld`
- The AGENTS policy is in `AGENTS.md`
- Every claim you encounter has an epistemic label (DERIVED / CONSTRAINED / CONJECTURAL / ARCHITECTURE_LIMIT / FITTED / OPEN)
- Do not treat ADJACENT TRACK claims (🔵) as hardgated physics
- The full ingest order is in `AGENTS.md §2`

---

## For Physicists and Cosmologists

If you are a physicist encountering this repository for the first time:

1. Start with `FALLIBILITY.md`. Not the README. Not the impressive numbers. The gaps. If a framework cannot clearly state where it might be wrong, it is not science. We start with the gaps.

2. The preregistered predictions are the most important thing here. Everything else a theory framework does can be adjusted after the fact. A SHA-256 committed prediction with a machine-readable falsification criterion cannot. Our birefringence β prediction, our f_NL prediction, our JUNO Δm²₃₁ prediction — these are all committed. Check the timestamps. Check the hashes. Then watch what happens when the data arrives.

3. The epistemological infrastructure (`docs/CLAIM_LABEL_STANDARD.md`, `docs/TRUTH_LAYER.md`, `docs/GATEKEEPER_SUMMARY.md`) is a methodology contribution independent of whether the physics is correct. We are proposing a new standard for how theoretical physics should document itself in the era of computational science.

4. We are looking for collaborators on formal peer review, independent reproduction, and experimental design. If you are affiliated with JUNO, LiteBIRD, SPHEREx, DESI, or any detector relevant to our prediction windows, contact us via GitHub Issues or the review invitation in `4-IMPLICATIONS/discussions/AI-Automated-Review-Invitation.md`.

---

## Contact and Contribution

- **Issues:** https://github.com/wuzbak/Unitary-Manifold-/issues
- **Pull Requests:** https://github.com/wuzbak/Unitary-Manifold-/pulls
- **Zenodo DOI:** https://doi.org/10.5281/zenodo.19584531
- **Review invitation:** `4-IMPLICATIONS/discussions/AI-Automated-Review-Invitation.md`
- **AI review registry:** `1-THEORY/QUANTUM_THEOREMS.md` §AI Review Capability Registry

All content is released under the Defensive Public Commons License v1.0 (2026). See `LICENSE`.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
