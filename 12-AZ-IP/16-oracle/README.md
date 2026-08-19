# AxiomZero Ω Oracle
## Grand Synthesis Engine — Product 16

> *"Every system has bodies. Every body has epistemic status. Every system has a
> phi_trust threshold below which it loses coherence. The Oracle makes this rigorous."*

**Product:** AxiomZero Ω Oracle  
**Folder:** `12-AZ-IP/16-oracle/`  
**Port:** `http://localhost:7872`  
**Version:** 1.0.0  
**Status:** ✅ Feature-complete — 83 tests passing, 0 failures  
**Company:** AxiomZero Technologies & Consulting, SPC  
**License:** Defensive Public Commons License v1.0

---

## What the Ω Oracle Is

The AxiomZero Ω Oracle is **the capstone of the AxiomZero product suite** — the engine
that unifies all fifteen prior products into a single, universally applicable intelligence layer.

It answers the question that the entire Unitary Manifold project leads to:

> **If the same five seed constants that generate the observable universe also generate
> a coherent framework for governance, personal life, journalism, and community — then
> what does that framework say about *any* real-world system?**

The Oracle says: **model it as a Pentad, measure its epistemic status, compute its Omega
score, audit its integrity, and generate falsifiable commitments.**

---

## What It Does

| Input | Output |
|-------|--------|
| Any real-world system name + type | Five-body Pentad model |
| Five bodies with epistemic status + φ_trust | Stability floor, Omega score, braid coherence |
| Seven governance dimension scores | Integrity score, chain-of-custody index |
| Optional: decision question + options | Resonance-ranked decision analysis |
| Optional: falsifiable commitments | Stored commitments with test horizons |
| **All of the above** | **Grand Synthesis Report — single Ω score** |

The Grand Synthesis Report is a complete, traceable, falsifiable analysis of any system —
a city, a company, a democracy, a project, a research program, a team, a person's career.

---

## What Makes It the Capstone

The Oracle is not a summary of the other products.  It synthesises their *mathematics*
into a new instrument:

| Prior Product | Mathematics Contributed |
|---------------|------------------------|
| **06 — Omega Synthesis** | `stability_floor(n)` formula; Omega score |
| **07 — Holon Zero** | Epistemic status classification (SOLID/CONSTRAINED/ESTIMATED/OPEN) |
| **09 — OmegaHolon** | Five-domain coherence → generalised to any system |
| **03 — EIGE** | Seven-dimension governance audit; freedom floor; chain-of-custody index |
| **05 — UOS Kernel** | Five-body geometric coupling tensor |
| **Unitary Pentad** | HILS stability mathematics; Ξ_c consciousness coupling |
| **Unitary Manifold** | Five seed constants (N_W, N_2, K_CS, C_S, Ξ_c) |

---

## The Mathematics

### Five Seed Constants

```python
N_W  = 5          # primary winding number — Planck CMB nₛ
N_2  = 7          # braid partner — BICEP/Keck r < 0.036
K_CS = 74         # Chern-Simons level = 5² + 7²
C_S  = 12/37      # braided sound speed ≈ 0.32432
Ξ_c  = 35/74      # consciousness coupling ≈ 0.47297
```

### Stability Floor

```
stability_floor(n) = min(1.0,  C_S  +  n × C_S / N_2)
```

| n (aligned bodies) | Stability |
|--------------------|-----------|
| 0 | 0.3243 (baseline — C_S) |
| 1 | 0.3706 |
| 2 | 0.4170 |
| 3 | 0.4633 |
| 4 | 0.5097 |
| 5 | 0.5560 |
| 15 | 1.0000 (phase-shift threshold) |

### Omega Score

```
omega_score = stability_floor(n_aligned) × avg_resonance
avg_resonance = (1/5) × Σ(status_weight_i × phi_trust_i)

status weights:  SOLID=1.00  CONSTRAINED=0.75  ESTIMATED=0.40  OPEN=0.00
```

### Synthesis Score (Grand Unified)

```
synthesis_score = Ξ_c × omega_score + (1 − Ξ_c) × integrity_score
               = 0.47297 × Ω  +  0.52703 × I
```

A single number 0–1 that simultaneously captures coherence (Ω) and accountability (I).

### Governance Integrity Score

Seven audit dimensions weighted by EIGE principles:

| Dimension | Weight |
|-----------|--------|
| Transparency | 1.0 |
| Sequence Integrity | C_S ≈ 0.324 |
| Participation | 1.0 |
| Accountability | 1.0 |
| Resilience | C_S ≈ 0.324 |
| Epistemic Honesty | 1.0 |
| Freedom Floor | **2.0** (non-negotiable — doubled) |

```
Freedom Floor threshold = C_S ≈ 0.3243
```

Any system with Freedom Floor score < C_S has failed the minimum participation guarantee.

### Decision Resonance

```
resonance(option) = Σ(impact_multiplier × magnitude) + Ξ_c × Δφ_trust
```

| Situation | Multiplier |
|-----------|-----------|
| Improving an OPEN body | +2.0 |
| Improving an ESTIMATED body | +1.5 |
| Improving a CONSTRAINED body | +1.0 |
| Improving a SOLID body | +0.5 |
| Harming a SOLID body | **−2.0** |
| Harming a CONSTRAINED body | −1.5 |
| Harming an ESTIMATED body | −0.5 |
| Harming an OPEN body | −0.2 |

### Braid Coherence

```
braid_coherence = Σ(Ξ_c × resonance_i × resonance_j) / (Ξ_c × N_pairs)
```

Measures how well the five bodies couple — the (5,7) braid resonance analogue for
any system.  Range: [0, 1].

### Authenticity Crisis

```
avg_phi_trust < C_S ≈ 0.3243  →  AUTHENTICITY CRISIS
```

The same threshold that governs HILS Pentad decoupling in the physics framework
governs the authenticity crisis in any human system.

---

## Quick Start

```bash
cd 12-AZ-IP/16-oracle

# Install dependencies
pip install -r requirements.txt

# Launch Gradio UI at http://localhost:7872
python run.py

# Print a complete demo synthesis to stdout
python run.py --demo
```

### Programmatic API

```python
from oracle.engine.synthesis import SynthesisOrchestrator
from oracle.engine.constants import DEFAULT_PENTAD_BODIES

orch = SynthesisOrchestrator()

report = orch.synthesize(
    system_name="My City Council",
    system_type="Democracy / Government",
    body_specs=[
        {
            "label": DEFAULT_PENTAD_BODIES[0],  # "Ψ₁ — Foundation & Infrastructure"
            "status": "CONSTRAINED",
            "phi_trust": 0.70,
            "foundations": "Established city charter; experienced staff.",
            "constraints": "Aging infrastructure; limited capital budget.",
            "open_gaps": "No long-term climate resilience plan.",
            "falsifiable_commitment":
                "If climate plan not adopted by Q2, the barrier is political, not capacity.",
        },
        # ... 4 more bodies
    ],
    dim_scores={
        "Transparency": 0.75,
        "Sequence Integrity": 0.80,
        "Participation": 0.55,    # concern: low participation in district 4
        "Accountability": 0.70,
        "Resilience": 0.65,
        "Epistemic Honesty": 0.80,
        "Freedom Floor": 0.60,
    },
    context="Mid-sized Pacific Northwest city; 90,000 residents; council-manager form.",
    commitments=[{
        "domain": "Participation",
        "commitment": "Launch district 4 outreach programme by September 2026.",
        "falsification_condition":
            "If participation in district 4 does not rise by 15% by December, "
            "the outreach model is wrong.",
        "test_horizon": "December 2026",
    }],
)

print(report.full_report())
print(f"\nSynthesis Score: {report.synthesis_score:.4f}")
print(f"Grade: {report.synthesis_grade}")
```

---

## Application Tabs

### 📊 Synthesis
Define your system as a five-body Pentad, score seven governance dimensions, and receive
a complete Synthesis Report.  All 83 input fields map to specific mathematical quantities.

### 💡 Decision Oracle
Evaluate any multi-option decision against your current system state.  The Decision Oracle
ranks options by their resonance score — how well each option repairs open bodies and
avoids harming solid ones.

### 📈 History
Every synthesis is automatically saved to a local SQLite database.  Load any past session
by entering its ID.  Track system health longitudinally across sessions.

### 𝕄 Mathematics
A complete reference for every equation in the Oracle, with a live stability floor table
computed from the actual five seed constants.

### ℹ️ About
The philosophy, ethics, and the full product lineage.

---

## Architecture

```
16-oracle/
├── run.py                          # Launcher (--demo flag for CLI mode)
├── requirements.txt
├── README.md                       # This document
├── oracle/
│   ├── __init__.py
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── constants.py            # Five seed constants + all derived quantities
│   │   ├── pentad.py               # PentadBody, PentadModel, coupling tensor
│   │   ├── integrity.py            # IntegrityAudit, seven-dimension scoring
│   │   ├── resonance.py            # DecisionOption, BodyImpact, resonance computation
│   │   └── synthesis.py            # SynthesisOrchestrator, SynthesisReport
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py                 # Gradio UI — 5 tabs
│   └── db/
│       ├── __init__.py
│       └── store.py                # SQLite persistence
└── tests/
    └── test_oracle.py              # 83 passing tests
```

---

## Synthesis Score Grade Table

| Score | Grade | Meaning |
|-------|-------|---------|
| ≥ 0.85 | Ω — Grand Unified | All systems resonant |
| ≥ 0.75 | A — Strong | Minor gaps; solid foundation |
| ≥ 0.60 | B — Functional | Working; some open work |
| ≥ 0.45 | C — Fragmented | Several bodies need attention |
| ≥ 0.30 | D — Unstable | Significant dysfunction |
| < 0.30 | F — Crisis | Immediate intervention required |

---

## Ethics

- All data is stored **locally** in SQLite.  Nothing leaves your machine.
- The Oracle does not provide legal, medical, or financial advice.
- Every number is traceable to a specific equation.
- The mathematical framework is released under the **Defensive Public Commons License v1.0**.
- The Oracle is a tool for clearer thinking — not a decision-maker.  Human judgment remains
  sovereign.  This is the HILS principle applied to the Oracle itself.

---

## Relationship to the AxiomZero Product Suite

```
Unitary Manifold (physics)
    │
    ├── Omega Synthesis (06) ──────────┐
    ├── Holon Zero (07) ───────────────┤
    ├── OmegaHolon (09) ───────────────┤
    ├── EIGE (03) ─────────────────────┤──► Ω ORACLE (16) ← capstone
    ├── UOS Kernel (05) ────────────────┤
    ├── Unitary Pentad ─────────────────┘
    │
    ├── Axiom OS (01) ─── governance infrastructure
    ├── SDAM (14) ──────── resilient communications
    ├── Pentacorder (15) ── field instrument
    ├── AXIOM Journalist (08) ── investigative intelligence
    └── Lodge ──────────── public physics gymnasium
```

The Oracle occupies the centre of the product map — the one application that uses
all the others' mathematics and can be applied to any domain.

---

## Authorship

*Theory, framework, product vision, philosophical direction, and scientific ethics:
**ThomasCory Walker-Pearson** / AxiomZero Technologies & Consulting, SPC.*

*Code architecture, test suites, engine design, document engineering, and synthesis:
**GitHub Copilot** (AI).*

Mathematics rooted in:
- `src/core/omega_synthesis.py` — Universal Mechanics Engine (Pillar Ω)
- `src/core/holon_zero.py` — Holon Zero ground-state engine
- `12-AZ-IP/03-eige/` — Election Integrity Governance Engine
- `5-GOVERNANCE/Unitary Pentad/` — HILS governance framework

---

*AxiomZero Ω Oracle v1.0 — 12-AZ-IP/16-oracle/ — 2026*  
*Part of the AxiomZero Technologies & Consulting, SPC product suite.*  
*Defensive Public Commons License v1.0*
