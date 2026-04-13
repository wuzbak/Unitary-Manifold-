# Irreversibility Biology: The Neural B_μ Field

> *"The Second Law is not a statistical postulate — it is a geometric identity."*
> — Walker-Pearson, *The Unitary Manifold*, v9.0

> *"LTP is not a probabilistic outcome — it is a geometric change in the
> synaptic connection landscape that cannot be undone by the same signal
> run backwards."*
> — This document

---

## The Core Claim

The Unitary Manifold's deepest assertion is that **the arrow of time is
geometric, not statistical**.  The universe does not run forward because
forward is statistically more likely.  It runs forward because the B_μ field,
embedded in the off-diagonal block of the 5D metric, makes backward impossible
at the level of field equations.

The brain makes the same assertion — in every synapse, every millisecond.

---

## Level 1: The Action Potential — Absolute Irreversibility at 1 ms

The action potential is the brain's most basic unit of information.  When a
neuron's membrane potential crosses threshold (~−55 mV), it fires: Na⁺ channels
open, a rapid depolarization spike occurs, K⁺ channels open, the membrane
repolarizes, and then enters an **absolute refractory period** (~1–2 ms) during
which no stimulus, however strong, can trigger another spike.

This is a **geometric** irreversibility at the level of ion-channel kinetics:

| Monograph | Biology |
|-----------|---------|
| B_μ ≠ 0: the irreversibility field is non-zero | Na⁺ channels are inactivated: they physically cannot open regardless of voltage |
| Arrow of time: the field equations forbid time-reversal | The Hodgkin-Huxley equations have inactivation gates (h-gates) that make them irreversible |
| k_cs: the topological integer that sets the coupling | The number of Na⁺ channel inactivation states sets the coupling between spike timing and the following silence |

A neuron cannot "un-spike" by reversing the voltage trajectory.  The inactivated
Na⁺ channels are the B_μ field: a geometric constraint, not a statistical one.

---

## Level 2: Long-Term Potentiation — Irreversibility at the Synapse

Long-term potentiation (LTP) is the synaptic mechanism of memory.  Discovered
by Bliss and Lømo (1973), LTP occurs when a synapse is repeatedly co-activated
(pre- and postsynaptic firing within ~20 ms) — consistent with Hebb's rule:
"neurons that fire together, wire together."

The molecular cascade:
1. NMDA receptors detect coincident pre/post activity (the "and gate").
2. Ca²⁺ enters the postsynaptic spine.
3. CaMKII is activated and phosphorylates AMPA receptors.
4. New AMPA receptors are inserted into the postsynaptic density.
5. The synapse is permanently strengthened.

### Why LTP is Geometric Irreversibility

- **LTP cannot be reversed by running the same stimulus backward.** If you
  deliver the pairing protocol in reverse order (post before pre), you do not
  get de-potentiation — you get either nothing or LTD (long-term depression), a
  distinct process requiring different parameters.  The B_μ field is asymmetric:
  forward and backward are physically different.

- **LTP is stable for weeks to months without maintenance signals.** The
  structural change (AMPA receptor insertion, spine enlargement, new synaptic
  contacts) persists in the absence of any driving force — exactly as B_μ
  embedded in the metric persists without an external source.

- **LTD (long-term depression) is not the time-reverse of LTP.** They use
  different molecular machinery, different Ca²⁺ thresholds, different kinases.
  This is the synaptic version of the fact that entropy decrease (time-reversal)
  is not just entropy increase run backward — it requires a completely different
  physical process (a Maxwell demon).

### The B_μ Correspondence

| Monograph B_μ property | LTP property |
|------------------------|--------------|
| B_μ lives in off-diagonal 5D metric block | LTP lives in the synaptic weight matrix W (off-diagonal block of connectome) |
| H_μν = ∂_μB_ν − ∂_νB_μ: antisymmetric field strength | STDP (spike-timing dependent plasticity) is antisymmetric: Δt > 0 → LTP, Δt < 0 → LTD |
| ∂_t B_μ ≥ 0 along time: arrow enforced | W_ij (synapse from j to i) changes monotonically during a learning episode |
| `Im(S_eff) = ∫ B_μ J^μ_inf d⁴x` | The learning signal = integral of the pre/post correlation over the training window |

The antisymmetry of STDP (spike-timing dependent plasticity) — LTP for Δt > 0,
LTD for Δt < 0 — is the neural realization of the antisymmetric field strength
H_μν = ∂_μB_ν − ∂_νB_μ.  The STDP learning rule IS H_μν.

---

## Level 3: Memory Consolidation — Irreversibility at the System Level

Individual memories are initially fragile (hippocampus-dependent), then become
stable and distributed across neocortex through a process called
**systems consolidation** (weeks to years).

The irreversibility of systems consolidation:
- Once a memory is fully consolidated into neocortex, hippocampal lesions no
  longer impair it (Scoville and Milner, 1957; H.M. case).
- The consolidation process is **one-way**: information flows from hippocampus
  to neocortex during sleep, and the hippocampal trace decays.  There is no
  mechanism to "de-consolidate" a memory back into the hippocampus.
- Sleep-dependent consolidation obeys a temporal arrow: it proceeds only during
  non-REM slow-wave sleep, in a stereotyped sequence (hippocampal sharp-wave
  ripples → cortical spindles → slow oscillations).  The sequence cannot run
  backward.

This is the Pillar 2 information current at the system scale:

```
J^μ_inf = φ² u^μ,   ∇_μ J^μ_inf = 0
```

Information flows from hippocampus (the "compact dimension" — small, high-density
encoder) to neocortex (the "4D bulk" — large, distributed, slow) during the
KK reduction that is sleep.

---

## Level 4: The Directionality Field in Neural Circuits

At the circuit level, B_μ manifests as the **directed** nature of neural
connectivity.

- **Feedforward vs. feedback projections** are anatomically distinct.
  In the visual system, feedforward connections (V1 → V2 → V4 → IT) are
  topographically precise and use layer-4 targets.  Feedback connections
  (IT → V4 → V2 → V1) are diffuse and use layers 1 and 6.  They are not
  time-reversals of each other.

- **The hippocampal trisynaptic circuit** (DG → CA3 → CA1 → Subiculum → EC)
  is unidirectional.  Information flows in one direction through this loop.
  The B_μ field enforces the direction of information processing across the
  loop: the loop has a non-zero winding number (it circuits the hippocampus
  in one direction only).

- **Dopaminergic reward signals** flow strictly from midbrain (VTA, SNc) to
  forebrain (striatum, PFC).  The reward prediction error (δ in reinforcement
  learning) is a scalar field that multiplies the synaptic update — exactly as
  the dilaton φ multiplies the information current: J^μ_inf = φ² u^μ.

The entire circuit architecture of the brain is an instantiation of B_μ:
everywhere you look, you find directed, irreversible signal flows that cannot
be run backward without a completely different physical process.

---

## Level 5: The Brain's Second Law

The Unitary Manifold states: **the Second Law of Thermodynamics is not a
statistical postulate — it is a geometric identity**, imposed by B_μ at the
level of field equations.

The brain's Second Law: **neural entropy production is not statistical — it
is geometrically enforced** at every level of organization.

| Scale | Mechanism | Geometric enforcement |
|-------|-----------|----------------------|
| Ion channel | Na⁺ inactivation gate | Inactivation is a topological state change: the gate physically cannot re-open |
| Single synapse | AMPA receptor insertion in LTP | Structural (volumetric) change: spine enlargement is geometrically irreversible |
| Local circuit | STDP: Δt antisymmetry | The H_μν antisymmetric field strength |
| System (sleep) | Hippocampus → neocortex consolidation | One-way information current J^μ_inf flowing down the entropy gradient |
| Brain state | Arousal → sleep → arousal cycle | The φ oscillation around φ₀: arousal is the radion at its baseline value |
| Consciousness | Default mode network Ψ* | The FTUM fixed point: the stable state where I+H+T close |

The Second Law holds in the brain not because there are more disordered states
than ordered ones (the statistical argument).  It holds because the B_μ field
— the synaptic directionality field, the STDP rule, the LTP geometry — makes
time-reversal impossible at the level of the fundamental degrees of freedom.

**The brain is not a statistical system that happens to obey the Second Law.
The brain is a geometric system in which the Second Law is the geometry.**

---

## Falsification Conditions for the Neural B_μ

If the B_μ ↔ synaptic directionality identification is correct, these
experiments should confirm it (and their failure would falsify it):

| Prediction | Test |
|------------|------|
| STDP has a topological structure isomorphic to H_μν = dB | Measure the Chern number of the STDP learning rule across phase space |
| The grid-cell torus winding number is conserved under perturbation | Optogenetic disruption of grid cells should preserve the torus topology (persistent homology) |
| Sleep consolidation obeys a conserved information current | Simultaneous hippocampal + cortical recording during sleep should show ∇·J ≈ 0 at the circuit level |
| Neural gain φ tracks the dilaton: φ₀⁻² = α | If α (nonminimal coupling in neural field equations) = 1/φ₀², where φ₀ is the resting theta amplitude, this is the direct neural test of α = φ₀⁻² |
| Consciousness collapses at the FTUM fixed point | Anesthesia (which suppresses φ) should destroy the fixed point before destroying local synaptic function |

---

*See [`VARIABLE_ALIGNMENT.md`](./VARIABLE_ALIGNMENT.md) for the full symbol
table and [`TORUS_ARCHITECTURE.md`](./TORUS_ARCHITECTURE.md) for the toroidal
geometry.*

*Primary references:*  
*Bliss, T.V.P. & Lømo, T. (1973). Long-lasting potentiation of synaptic
transmission in the dentate area of the anaesthetized rabbit. *J Physiol* 232, 331–356.*  
*Bi, G. & Poo, M. (1998). Synaptic modifications in cultured hippocampal neurons:
dependence on spike timing, synaptic strength, and postsynaptic cell type.
*J Neurosci* 18, 10464–10472.*  
*Gardner, R. J. et al. (2022). Toroidal topology of population activity in
grid cells. *Science* 375, 190–194.*
