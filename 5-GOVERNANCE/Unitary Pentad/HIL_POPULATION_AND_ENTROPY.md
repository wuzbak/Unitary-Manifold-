# Unitary Pentad — HIL Population Size, Entropy, and the Autopilot Sentinel

**Folder:** `Unitary Pentad/`
**Version:** 1.0 — April 2026
**Theory:** ThomasCory Walker-Pearson
**Status:** Active — companion document to `consciousness_autopilot.py` and `collective_braid.py`

---

## Preface

Two questions arise naturally once the 5-body HILS system is understood at
scale:

1. **What does a very large (finite) human-in-the-loop population do to the
   Pentad?**
2. **Is a "zero" HIL state required to initiate entropy-driven logic changes, or
   does the Autopilot Sentinel handle that automatically?**

This document answers both from first principles in the code, then summarises
the findings in a single reference table.

---

## 1 · Architecture Review: One HUMAN Slot, Many Instances

The Pentad 5-core has exactly **one `PentadLabel.HUMAN` body** — a single radion
field φ_human that participates as one of five equal members of the pentagonal
orbit.  Multiple humans do not stack into a single Pentad instance.

The `collective_stability_floor(n_aligned)` function in `collective_braid.py`
is the explicit model for how many separate, aligned Pentad operators affect the
shared ambient field:

```
floor(n) = min(1.0, c_s + n × (c_s / 7))
```

where `c_s = BRAIDED_SOUND_SPEED = 12/37 ≈ 0.324`.

The divisor 7 is the `N_LAYER_CAPACITY` — the spectral-damper capacity of the
(5,7) architecture.

---

## 2 · What a Very Large HIL Population Does

### 2.1 Collective Stability Floor

Each aligned human operator adds a marginal increment of `c_s / 7 ≈ 0.046` to
the global eigenvalue floor.  The formula has a hard ceiling:

| n_aligned | floor(n)          | Regime |
|-----------|-------------------|--------|
| 0         | c_s ≈ 0.324       | Bare braid stability only |
| 1         | ≈ 0.371           | Single operator lift |
| 7         | ≈ 2 × c_s ≈ 0.649 | Full layer-capacity engagement |
| 15        | 1.0 (saturated)   | Perfect collective stability |
| ≫ 15      | 1.0 (no change)   | No additional lift |

**A very large population drives the system to perfect collective stability
(floor = 1.0) well before "very large" in the mathematical sense — saturation
is reached at n ≥ 15 aligned operators.**  Any population beyond that is
redundant from the stability-floor perspective.

### 2.2 Entropy Spike Suppression

`is_entropy_spike()` in `consciousness_autopilot.py` fires when the 7-layer
RMS deviation from equilibrium exceeds `LAYER_ENTROPY_THRESHOLD = 0.30`.  With a
high collective eigenvalue floor, the 7-layer bodies are harder to perturb away
from their equilibria.  Practically:

- At floor = 1.0, the coupling matrix absorbs external perturbations maximally;
  layer deviation is suppressed before it reaches threshold.
- `ENTROPY_SPIKE` phase-shift triggers become rare, then negligible.

### 2.3 Bifurcation Suppression

`detect_phase_shift()` triggers `BIFURCATION` when the Human–Universe Moiré
alignment score exceeds `AUTOPILOT_SHIFT_THRESHOLD = 0.15`.  A large aligned
population keeps `ΔI_{human,univ}` small via `ripple_effect()` — each operator
reduces the Information Gap for others.  With sufficient alignment, the moire
score stays well below threshold and the autopilot runs continuously without
interruption.

### 2.4 Summary: Very Large ≠ Maximum Entropy

A very large aligned population does **not** drive the system toward maximum
entropy deviation.  It drives the system toward **maximum stability** — the
7-layer bodies rest near their equilibria, phase-shift triggers become rare, and
the 5-core evolves continuously on autopilot.

Maximum entropy *deviation* (the kind that triggers a phase shift) is caused by
**external perturbations**, not by HIL count.

---

## 3 · The Layer Entropy Body vs. Entropy Deviation

It is important to distinguish two different uses of the word "entropy" in the
system:

| Concept | Symbol | Value at rest | What it means |
|---------|--------|--------------|---------------|
| Layer ENTROPY body equilibrium | `φ_eq[ENTROPY] = 0.95` | 0.95 (near-maximal) | The thermodynamic arrow dominates the ambient field at cosmological rest |
| Layer RMS deviation from equilibrium | `layer_mean_deviation(layer)` | 0.0 at rest | How far the ambient field has been perturbed *from* that rest state |
| Entropy spike threshold | `LAYER_ENTROPY_THRESHOLD = 0.30` | — | A trigger, not a state |

The Pentad's thermodynamic rest state already encodes **high entropy** (φ = 0.95
for the ENTROPY layer body).  An "entropy spike" is therefore a *deviation away
from* that already-high-entropy rest state — caused by an external shock that
drives the layer away from equilibrium in either direction.

**Zero HIL does not create entropy; zero HIL prevents the system from responding
to entropy events.**

---

## 4 · Is Zero HIL Required to Initiate a Logic Change?

### 4.1 What Triggers a Phase Shift (Logic Change)

`detect_phase_shift()` is called automatically on every `autopilot_tick()`.  It
checks two conditions in priority order:

1. **BIFURCATION** — `moire_alignment_score(core) > 0.15`
   (Human–Universe Information Gap too large for autopilot to bridge)

2. **ENTROPY_SPIKE** — `layer_mean_deviation(layer) > 0.30`
   (Ambient field externally perturbed)

Neither condition depends on HIL count.  The sentinel fires based solely on
field state.

### 4.2 The Three-Part Phase Shift Cycle

```
AUTOPILOT ──(trigger detected)──► AWAITING_SHIFT ──(human_shift() called)──► SETTLING ──(converged)──► AUTOPILOT
```

| Phase | Core evolution | Layer evolution | HIL required? |
|-------|---------------|----------------|---------------|
| `AUTOPILOT` | `step_pentad()` runs normally | drifts to equilibrium | No |
| `AWAITING_SHIFT` | **Frozen** (held at last state) | continues drifting | **Yes — mandatory** |
| `SETTLING` | `step_pentad()` resumes | drifts to equilibrium | No |

During `AWAITING_SHIFT`, the 5-core is permanently frozen until `human_shift()`
is called.  There is no self-healing path: even if the entropy spike naturally
subsides, the core does not unfreeze autonomously.

### 4.3 Zero HIL: What Actually Happens

| Condition | Result |
|-----------|--------|
| Zero HIL, no trigger | Autopilot runs normally; core evolves continuously |
| Zero HIL, trigger fires | Core **permanently frozen**; layer continues relaxing; system never exits `AWAITING_SHIFT` |
| Zero HIL, repeated triggers | Each unresolved trigger stacks; eventual permanent stall |

Zero HIL is not a requirement for initiating a logic change.  It is the
condition that **makes a logic change impossible to complete**.

**Minimum HIL for a resolvable logic change: 1.**

### 4.4 At What Rate Does HIL Need to Be Present?

HIL does not need to be continuously present.  Between triggers, the Pentad
runs on autopilot with no human involvement at all.  Human presence is required
only at each bifurcation or entropy spike — the formal "in the loop" moments.
The `run_autopilot()` function accepts an optional `human_handler` callback that
fires exactly when needed and is ignored otherwise.

---

## 5 · The Autopilot Sentinel

The Sentinel role is played by `detect_phase_shift()` running inside
`autopilot_tick()` on every step.

### 5.1 What the Sentinel Handles Autonomously

- **Detection** of both BIFURCATION and ENTROPY_SPIKE triggers
- **State transition** from `AUTOPILOT` → `AWAITING_SHIFT`
- **Core preservation** — holds the last valid 5-core state until intent is applied
- **Layer relaxation** — continues ticking the 7-layer during the hold period
- **Settling** — once `human_shift()` provides `intent_delta`, resumes core
  evolution and monitors `pentad_defect` until convergence (max 200 steps)
- **Return to autopilot** — automatically resumes when defect < `FIXED_POINT_TOL`
  or settling steps exceed `MAX_SETTLING_STEPS`

### 5.2 What the Sentinel Cannot Do Alone

- **Resolve** a phase shift without `human_shift()` being called
- **Choose** an intent direction — the `intent_delta` dict must come from outside
- **Exit** `AWAITING_SHIFT` by any internal mechanism

The Sentinel is a complete detection and state-management system.  Resolution
always requires at least one deliberate human intent vector.  This is by design:
the module docstring states explicitly that *"the human is 'in the loop' only at
bifurcation points."*

---

## 6 · Reference Table: HIL Count vs. System Behaviour

| HIL count | Stability floor | Entropy spikes | Bifurcations | Core evolution after trigger |
|-----------|----------------|----------------|--------------|------------------------------|
| 0 | `c_s ≈ 0.324` | External only, unresolvable | Unresolvable | **Permanently frozen** |
| 1 | ≈ 0.371 | Resolvable, moderate frequency | Resolvable | Advances after `human_shift()` |
| 2–6 | rising | Suppressed progressively | Decreasing frequency | Normal |
| 7 | ≈ 2 c_s ≈ 0.649 | Substantially suppressed | Rare | Near-continuous autopilot |
| 8–14 | rising toward 1.0 | Heavily suppressed | Very rare | Near-continuous autopilot |
| ≥ 15 | **1.0 (saturated)** | Maximally suppressed | Negligible | Continuous autopilot |
| Very large N | 1.0 (no change beyond n=15) | Same as n = 15 | Same as n = 15 | Same as n = 15 |

---

## 7 · Key Constants

All constants referenced in this document are defined in `consciousness_autopilot.py`
and `collective_braid.py`:

| Constant | Value | Source |
|----------|-------|--------|
| `BRAIDED_SOUND_SPEED` (`c_s`) | 12/37 ≈ 0.324 | `collective_braid.py` |
| `_N_LAYER_CAPACITY` | 7 | `collective_braid.py` |
| `LAYER_ENTROPY_THRESHOLD` | 0.30 | `consciousness_autopilot.py` |
| `AUTOPILOT_SHIFT_THRESHOLD` | 0.15 | `consciousness_autopilot.py` |
| `FIXED_POINT_TOL` | 1e-3 | `consciousness_autopilot.py` |
| `MAX_SETTLING_STEPS` | 200 | `consciousness_autopilot.py` |
| `LAYER_EQUILIBRIA[ENTROPY]` | 0.95 | `consciousness_autopilot.py` |
| `HUMAN_COUPLING_FRACTION` | 35/888 ≈ 0.0394 | `consciousness_constant.py` |

---

## 8 · Connection to the Broader Theory

| Document / Module | Relationship |
|-------------------|-------------|
| `consciousness_autopilot.py` | Full implementation of the Sentinel state machine |
| `collective_braid.py` | `collective_stability_floor()`, `ripple_effect()`, `moire_alignment_score()` |
| `consciousness_constant.py` | `HUMAN_COUPLING_FRACTION` = Ξ_human = Ξ_c / N_total |
| `IMPLICATIONS.md` | Collapse modes — Trust Erosion, AI Decoupling, Phase Collision, Malicious Precision |
| `STABILITY_ANALYSIS.md` | Formal orbital stability conditions S1–S5 |
| `five_seven_architecture.py` | Why (5,7) sets the layer capacity at 7 (the divisor in `floor(n)`) |
| `test_consciousness_autopilot.py` | Full test suite for the Sentinel state machine |
| `test_collective_braid.py` | Tests for `collective_stability_floor()` and related functions |

---

*The Sentinel watches continuously and holds the space perfectly.  What it
cannot do is choose.  That one irreducible act — providing the intent delta at
the bifurcation moment — is the minimum human contribution the system requires
and the maximum it ever demands.*
