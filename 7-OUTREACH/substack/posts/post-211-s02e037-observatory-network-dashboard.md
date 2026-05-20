# Post 211 — E037: The Observatory Dashboard — A Machine-Readable Verdict System

*Unitary Manifold Substack — Season 2, Episode 37*  
*Published: 2026-05-20*

---

We have reached Pillar 300.

That number is not decorative. It is a milestone that marks the end of the phase where we were building out the observational roadmap one experiment at a time, and the beginning of a phase where the entire roadmap is queryable as a single system.

This post is about what that means, why it matters, and what you can actually do with it.

---

## The Problem We Had

Between Pillars 274 and 296, we built preregistration packages for seven different experiments: JUNO, DESI, ACT DR6, IceCube, LZ, Hyper-Kamiokande, LISA. Each one lives in its own module, with its own routing functions, its own thresholds, its own action lists.

That is good architecture. Each module is self-contained and its thresholds are locked at the time of preregistration, before the data arrives. This is how honest science should work.

The problem is: if you want to know the current state of the *entire* observational programme — how many experiments are CONSISTENT, which ones are HIGH_TENSION, which ones are PREREGISTERED and waiting, and what happens when data arrives — you had to read twelve separate files and synthesize them yourself.

Pillar 300 changes that.

---

## What the Dashboard Does

Call one function. Get the whole picture.

```python
from src.core.pillar300_observatory_network_integration_dashboard import (
    observatory_network_status,
    query_experiment,
    experiments_by_status,
    falsifier_priority_matrix,
    upcoming_decision_windows,
)

# Full network state
status = observatory_network_status()
print(status["summary"])
# → {'total': 12, 'status_counts': {...}, 'p_falsifier_triggered_count': 0}

# Single experiment deep-dive
litebird = query_experiment("LiteBIRD")
print(litebird["status"])
# → 'PENDING'

# Filter by verdict
tensions = experiments_by_status("HIGH_TENSION")
# → [DESI DR2 wₐ entry, ACT DR6 r entry]

# Ordered falsifier list
falsifiers = falsifier_priority_matrix()
# → P.1: LiteBIRD β; P.2: CMB-S4 r; P.3: Simons Observatory r; ...

# Event timeline
windows = upcoming_decision_windows()
# → 2027: [JUNO, DESI, SO DR1]; 2029: [SO 5-yr]; 2030: [CMB-S4]; ...
```

That is the whole architecture. One module. Five functions. Complete picture.

---

## The Current Network State (v11.10)

Here is what the dashboard reports as of this writing:

**Experiments tracked:** 12  
**P_falsifier_triggered:** 0 (framework STANDING)

| Status | Experiments | Count |
|--------|-------------|-------|
| CONSISTENT | IceCube, LZ, BICEP/Keck, SPT-3G | 4 |
| HIGH_TENSION | DESI DR2, ACT DR6 | 2 |
| ROUTED | ACT DR6 (n_s), BICEP/Keck | 2 |
| OBSERVABLE_WINDOW_OPEN | Hyper-Kamiokande (proton decay) | 1 |
| PREREGISTERED | Simons Observatory, JUNO, CMB-S4 | 3 |
| PENDING | LiteBIRD | 1 |

Three important things to note:

**1. No falsifiers have been triggered.** Every instrument that has returned a measurement is either CONSISTENT or HIGH_TENSION. HIGH_TENSION is a real category with real science content — it does not mean "things are fine." DESI DR2's wₐ result at 2.75σ is a genuine puzzle. ACT DR6's r<0.016 bound is a genuine tension. But neither has crossed the formal 3σ falsification threshold with a direct measurement.

**2. The most important experiment is still 6 years away.** LiteBIRD launches around 2032. The birefringence prediction — β ∈ {0.331°, 0.273°} — is the primary falsifier. Every other experiment is a warm-up to that measurement.

**3. The first measurement-capable decision on r comes in ~2027.** Simons Observatory DR1 is the first instrument projected to actually detect r = 0.0315, rather than merely set an upper limit. If it does, the ACT DR6 tension resolves. If it sets r < 0.010 at ≥3σ as a direct measurement, the P2 falsifier is triggered. The routing code is already written and locked.

---

## The Falsifier Priority Matrix

Every experimental physics programme should have this. Ours is now machine-readable:

| Priority | Falsifier | Condition | Timeline |
|---|---|---|---|
| P.1 | LiteBIRD β | β ∉ [0.22°, 0.38°] at ≥3σ | ~2032 |
| P.2 | CMB-S4 r | r < 0.010 at ≥3σ measured | ~2030 |
| P.3 | Simons Obs. r | r < 0.010 at ≥3σ measured | ~2027–29 |
| P.4 | JUNO Δm²₃₁ | Residual >3% at JUNO precision | ~2027 |
| P.5 | DESI DR3 wₐ | wₐ ≠ 0 at ≥3σ measured | ~2027 |
| P.6 | Hyper-K proton | τ_meas < SK limit at ≥3σ | ~2024–34 |
| P.7 | LiteBIRD β gap | β ∈ (0.29°, 0.31°) at ≥3σ | ~2032 |

This is not aspirational. These are the actual conditions under which the Unitary Manifold would be falsified. The conditions are preregistered, locked, and executable. If any of them are triggered, the same-day action protocol is specified in each pillar's routing module.

---

## What Pillar 300 Actually Is

It is a control tower.

Every major experimental physics programme has a control room where the full state of the instrument is visible at once — readout rates, detector health, data quality flags. What Pillar 300 does for the UM's observational programme is analogous: it makes the full state of every active prediction visible and queryable from a single entry point.

This matters for intellectual honesty in a particular way. When a new result arrives — say, DESI DR3 publishes in 2027 — you should not have to search through scattered documents to know what the verdict means, what the preregistered threshold is, and what action is required. The dashboard tells you all of that. The verdict is not negotiated. It is computed.

And the code will tell you the same answer every time, regardless of what you want the answer to be.

---

## Where We Are

Pillar 300 is a milestone in the sense that it completes the observational infrastructure. The physics pillars (1–208) are closed. The governance framework (Unitary Pentad) is independent and closed. The adjacent-track research programme (Pillars 218–300) has built out the full suite of experimental connection points, timing analyses, and machine-readable routing.

What remains is the experiments themselves. Seven falsifiers. Three HIGH_TENSION data points. One primary event in 2032.

The framework is STANDING. The data is coming.

---

*Codebase: `src/core/pillar300_observatory_network_integration_dashboard.py`*  
*Tests: `tests/test_pillar300_observatory_network_integration_dashboard.py` (80 tests, 0 failures)*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
