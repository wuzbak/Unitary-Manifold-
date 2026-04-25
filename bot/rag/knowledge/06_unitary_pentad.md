# Unitary Pentad — HILS Governance Framework

> **Epistemic status:** The Unitary Pentad is an independent governance and
> decision-making architecture *inspired by* the Unitary Manifold's mathematical
> structure. It is NOT a physics claim. It does not depend on the 5D theory being
> physically correct. See `SEPARATION.md`.

## What Is It?

The `Unitary Pentad/` folder implements a complete **5-body HILS (Human-in-the-Loop
Systems)** governance framework — the full generalisation of the brain⊗universe
2-body system to five interacting manifolds.

**The five bodies:**

| Body | Symbol | Role |
|------|--------|------|
| 1 | Ψ_univ | 5D Physical Manifold — the (5,7) braid source |
| 2 | Ψ_brain | Biological Observer — neural integration |
| 3 | Ψ_human | Intent Layer — semantic direction / judgment |
| 4 | Ψ_AI | Operational Precision — truth machine / implementation |
| 5 | β·C | Trust / Coupling Field — the stabilising medium |

## Pentagonal Master Equation

```python
U_pentad (Ψ_univ ⊗ Ψ_brain ⊗ Ψ_human ⊗ Ψ_AI ⊗ Ψ_trust) = (same state)
```

The fixed point is the **Harmonic State**: all five bodies converge simultaneously,
all pairwise Information Gaps ΔI_{ij} → 0, all Moiré phase offsets Δφ_{ij} → 0,
trust field φ_trust > φ_trust_min.

**Braided stability bound:** The (5,7) braided sound speed c_s = 12/37 ≈ 0.324
provides a minimum eigenvalue floor for the pentagonal coupling matrix — no single
pairwise coupling can drive runaway instability.

**Consciousness coupling constant:** Ξ_c = 35/74 ≈ 0.4730; human coupling fraction
Ξ_human = 35/888 ≈ 0.0394.

## Python API

### Core system

```python
from unitary_pentad import PentadSystem, pentad_master_equation, BRAIDED_SOUND_SPEED

# Create default pentad with canonical initial conditions
ps = PentadSystem.default()

# Run master equation to convergence
final, history, converged = pentad_master_equation(ps, max_iter=1000, tol=1e-6)
print(f"Converged: {converged}, defect: {history[-1]['defect']:.6f}")

# Key constants
print(BRAIDED_SOUND_SPEED)  # 12/37 ≈ 0.3243
```

### Architecture analysis

```python
from five_seven_architecture import architecture_report, why_five_seven

# Why (5,7) and not (4,6) or (6,8)?
report = architecture_report(n_core=5, n_layer=7)
print(report.is_stable)      # True
print(report.stability_margin)
print(why_five_seven())      # full reasoning
```

### Scenarios

```python
from pentad_scenarios import (
    harmonic_state, pentagonal_collapse_scenario,
    regime_transition_signal, RegimeTransitionSignal
)

# Check if system is in Harmonic State
hs = harmonic_state(ps)
print(hs.all_gaps_closed)

# Detect regime transition
signal: RegimeTransitionSignal = regime_transition_signal(ps)
print(signal.attractor_degraded)   # current attractor no longer robust
```

### Consciousness Autopilot Sentinel

```python
from consciousness_autopilot import ConsciousnessAutopilot, AutopilotState

autopilot = ConsciousnessAutopilot.from_pentad(ps)
print(autopilot.state)    # AUTOPILOT | AWAITING_SHIFT | SETTLING

# Human-in-the-loop phase shift
autopilot.human_shift(intent_delta=0.1)
signal = autopilot.detect_phase_shift()
```

### Consciousness constant

```python
from consciousness_constant import (
    XI_C,          # 35/74 ≈ 0.4730
    XI_HUMAN,      # 35/888 ≈ 0.0394
    consciousness_coupling, human_coupling_fraction
)
```

### Distributed authority

```python
from distributed_authority import (
    beacon_entropy_score,
    elegance_attractor_depth,
    manipulation_resistance_margin,
    distributed_constitution_integrity,
    validator_node_strength
)

score = beacon_entropy_score(axioms_public=5, axioms_total=5)  # → 1.0 (fully open)
depth = elegance_attractor_depth(ps)
margin = manipulation_resistance_margin(ps)
```

### Sentinel load-balancing

```python
from sentinel_load_balance import (
    SentinelLabel, SENTINEL_CAPACITY,
    redistribute_sentinel_load, is_overloaded, sentinel_load_report
)

# SENTINEL_CAPACITY = 12/37 per sentinel (= braided sound speed)
report = sentinel_load_report(entropy_loads={
    SentinelLabel.TRUTH: 0.4,
    SentinelLabel.CARE: 0.2,
    SentinelLabel.PRECISION: 0.1,
    SentinelLabel.FAIRNESS: 0.15,
    SentinelLabel.INTEGRATION: 0.1
})
print(report.any_overloaded)
```

### Minimum Viable Manifold

```python
from mvm import mvm_search, minimum_viable_manifold, MVMConstraints

constraints = MVMConstraints(n_layer_max=10, min_stability_margin=0.1)
result = mvm_search(constraints)
print(result.n_core, result.n_layer)   # minimum stable configuration

config = minimum_viable_manifold()    # canonical MVM
```

### Stochastic jitter and non-Hermitian coupling

```python
from stochastic_jitter import apply_jitter, JitterConfig
from non_hermitian_coupling import (
    non_hermitian_coupling_matrix,
    berry_phase_accumulation,
    asymmetry_index
)

# Apply Langevin phase noise
noisy_ps = apply_jitter(ps, config=JitterConfig(sigma_human=0.05, sigma_ai=0.01))

# Asymmetric AI→Human vs Human→AI coupling
tau = non_hermitian_coupling_matrix(ps)
berry = berry_phase_accumulation(tau, n_cycles=10)
```

### Resonance dynamics

```python
from resonance_dynamics import (
    resonance_regime, SUM_OF_SQUARES_RESONANCE, HIL_PHASE_SHIFT_THRESHOLD,
    classify_resonance_state
)

# SUM_OF_SQUARES_RESONANCE = 74 (= 5² + 7²)
# HIL_PHASE_SHIFT_THRESHOLD = 15 (saturation at n ≥ 15 aligned HIL operators)

state = classify_resonance_state(ps)
print(state.regime)   # "3:2_resonant" | "2:3_resonant" | "4:1_inversion"
```

## Running the Tests

```bash
python -m pytest "Unitary Pentad/" -q
# Expected: 1234 passed, 0 failed
```

## Key Design Principles

1. **Resonance ≠ Agreement**: Total agreement (ΔI = 0 for all pairs) is Trivial Coalescence — the braid goes slack and the orbit disintegrates. The Harmonic State is a *limit cycle*, not a fixed zero. Bodies resonate; they do not merge.

2. **Transparency is stability**: The beacon_entropy_score of 1.0 (all axioms public) is not a vulnerability. It is the reason the system cannot be gamed. The architecture's stability does not depend on secrecy.

3. **Minimum HIL for resolvable logic change: 1**: Zero HIL does not initiate logic changes — it makes them impossible to complete. At least one conscious human intent_delta is always required.

4. **The (5,7) braid provides the stability floor**: c_s = 12/37 bounds the minimum eigenvalue of the coupling matrix from below, preventing any single pairwise coupling from driving singularity.

## Connection to the Physics Theory

The Unitary Pentad borrows mathematical structure from the Unitary Manifold but is epistemically independent:

| Physics concept | Pentad analogue |
|----------------|-----------------|
| FTUM fixed point Ψ* | Harmonic State — pentagonal convergence |
| Braided sound speed c_s = 12/37 | Sentinel capacity SENTINEL_CAPACITY = 12/37 |
| Birefringence angle β | Trust coupling τ_{ij} = β × φ_trust |
| Information gap ΔI → 0 | Pairwise gaps ΔI_{ij} → 0 at Harmonic State |
| k_cs = 74 = 5² + 7² | SUM_OF_SQUARES_RESONANCE = 74 |

*The physics might be wrong. The governance architecture still works.*
