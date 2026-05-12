# Five-Cores Architecture

**Folder:** `5-GOVERNANCE/Unitary Pentad/five_cores/`  
**Version:** 1.0 — May 2026  
**Theory:** ThomasCory Walker-Pearson  
**Implementation:** GitHub Copilot (AI)  
**Status:** Active

> *Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
> *Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## What This Is

The **Five-Cores** architecture is a functional decomposition of mission-system
cognition into five autonomous-but-coupled operational cores, governed by the
AxiomZero HILS (Human-in-the-Loop Systems) constitutional framework.

Each core is a φ-field radion subsystem sharing the Unitary Pentad trust field
β·C and operating within the (5,7)-braid stability bounds
(c_s = 12/37 ≈ 0.3243).

---

## The Five Cores

| # | Core | Role |
|---|------|------|
| 1 | **Strategic** | Long-horizon goals, doctrine, resource allocation, escalation rules |
| 2 | **Operational** | Real-time task routing, workflow execution, cross-domain coordination |
| 3 | **Real-Time Safety** | Continuous guardrails, trust thresholds, hard-stop/hold logic |
| 4 | **Real-Time Sciences** | Live data ingestion, automatic Bayesian model updates, answer readiness |
| 5 | **Biological Logics** | Crew health and medicine, triage prioritisation, care pathways |

---

## Quick Start

```python
from five_cores.five_cores_system import FiveCoresSystem

# Create the default system (all five cores at full trust)
sys_ = FiveCoresSystem.default()

# Tick the system forward one step
report = sys_.tick()

print(f"Status: {report.status}")
print(f"Health: {report.health_score:.3f}")
print(f"Safety: {report.safety_layer}")
print(f"HIL needed: {report.hil_requested}")
```

### Run a multi-step mission

```python
reports = sys_.run(n_steps=100)
health_scores = [r.health_score for r in reports]
```

### Submit an operational task

```python
from five_cores.operational_core import TaskDomain

task = sys_.operational.submit_task(
    domain=TaskDomain.NAVIGATION,
    criticality=0.5,
    description="Orbital correction burn",
)
print(f"Task mode: {task.mode}")  # AUTO / SUPERVISED / HOLD / HALT
```

### Monitor crew health

```python
plan = sys_.biological.care_plan("C001")
print(f"Triage: {plan['triage_priority']}")
print(f"Pathway: {plan['care_pathway']}")
```

### Ingest new science data

```python
from five_cores.realtime_sciences_core import Observation, DataDomain
import numpy as np

obs = Observation(DataDomain.ASTROPHYSICS, np.array([0.8, 0.05, 0.05, 0.05, 0.05]))
sys_.sciences.ingest(obs)
result = sys_.sciences.query(DataDomain.ASTROPHYSICS)
print(f"Ready: {result['query_ready']}  Confidence: {result['confidence']:.3f}")
```

### Run the simulation suite

```bash
python five_cores/simulation_five_cores.py
```

---

## Tests

```bash
# From repository root:
python3.12 -m pytest "5-GOVERNANCE/Unitary Pentad/five_cores/" -q

# Expected: 224 passed, 3 skipped (JAX-conditional), 0 failed
```

---

## Files

| File | Purpose |
|------|---------|
| `strategic_core.py` | Strategic Core — doctrine and escalation |
| `operational_core.py` | Operational Core — routing and execution |
| `realtime_safety_core.py` | Real-Time Safety Core — guardrails |
| `realtime_sciences_core.py` | Real-Time Sciences Core — JAX Bayesian engine |
| `biological_logics_core.py` | Biological Logics Core — crew health |
| `five_cores_system.py` | Integrated system — inter-core protocol |
| `test_*.py` | Test suites (224 tests total) |
| `simulation_five_cores.py` | Three canonical simulation scenarios |
| `FINDINGS.md` | Full simulation results and analysis |
| `__init__.py` | Package re-exports |

---

## Connection to the Unitary Pentad

The Five-Cores architecture is a functional service decomposition of the
Pentad's operational layer.  The shared trust field φ_trust and the (5,7)-braid
stability bound c_s = 12/37 are inherited directly from the Pentad framework.

- `../unitary_pentad.py` — the parent 5-body system
- `../consciousness_autopilot.py` — the 5-core / 7-layer autopilot
- `../sentinel_load_balance.py` — the per-axiom entropy load-balancer
- `FINDINGS.md` — simulation results and mathematical derivations

---

## Epistemic Status

This package is an **independent governance framework** inspired by the
mathematical structure of the Unitary Manifold.  It does not depend on the
5D physics being correct.  See `../../SEPARATION.md`.
