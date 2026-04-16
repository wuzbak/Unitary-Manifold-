# The Unitary Manifold (v9.11 — Academic Edition)

> *"Collapse entropy early. Gate compute. Enforce structure. Reduce variance."*

[![Tests](https://github.com/wuzbak/Unitary-Manifold-/actions/workflows/tests.yml/badge.svg)](https://github.com/wuzbak/Unitary-Manifold-/actions/workflows/tests.yml)
[![3294 Tests: 3282 Pass / 1 Skip / 0 Fail](https://img.shields.io/badge/tests-3282%20passed%20%C2%B7%201%20skipped%20%C2%B7%200%20failed-brightgreen)](tests/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19584531.svg)](https://doi.org/10.5281/zenodo.19584531)
[![MCP Ready](https://img.shields.io/badge/MCP-ready-blue)](mcp-config.json)
[![AI Ingest](https://img.shields.io/badge/AI%20Ingest-MCP__INGEST.md-green)](MCP_INGEST.md)
[![llms.txt](https://img.shields.io/badge/llms.txt-ready-orange)](llms.txt)
[![Download ZIP](https://img.shields.io/badge/Download-ZIP-brightgreen?logo=github)](https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip)

---

## ⬇ Download

| Method | Link |
|--------|------|
| **ZIP (latest main branch)** | [**Download ZIP ↓**](https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.zip) |
| **Tarball (latest main branch)** | [Download tar.gz ↓](https://github.com/wuzbak/Unitary-Manifold-/archive/refs/heads/main.tar.gz) |
| **Releases page** | [GitHub Releases](https://github.com/wuzbak/Unitary-Manifold-/releases) |
| **Full download guide** | [DOWNLOAD_GUIDE.md](DOWNLOAD_GUIDE.md) |

> You can also click the green **`<> Code`** button on the repository home page and choose **Download ZIP**.

---

## 1 · Project Overview

> ⚠️ **Key framing — read this first:**  
> **This is not a higher-dimensional spacetime. It is a scaffolded reduction.**  
> The fifth dimension is not ontologically additive. It is procedural: it exists
> to encode irreversibility and enforce information flow, then is integrated out.
> The output is standard 4D physics — enriched, not replaced.

The **Unitary Manifold** is a 5-dimensional gauge-geometric framework that
resolves the *dimensional misalignment* in modern physics.  Where traditional
theory treats irreversibility and the arrow of time as statistical accidents,
this work geometrises them as a 5D parent structure whose 4D projection
manifests as thermodynamics and information flow.

**Core objective:** derive 4D effective field equations — the
*Walker–Pearson field equations* — from a 5D Einstein–Hilbert action,
providing a unified geometric origin for gravity, irreversibility, and quantum
information.

**What is preserved:** General Relativity, the Standard Model, and the Second
Law are all recovered as exact limits of this framework.  No known physics is
removed or contradicted.

---

> ### 📄 [WHAT_THIS_MEANS.md](WHAT_THIS_MEANS.md) — Start here if you want to understand the *significance*
>
> A plain-language document explaining what this work is claiming, why it matters,
> how it relates to our 4D existence, what the quantitative results mean, and
> where the honest gaps are.  Written for physicists, the public, reviewers, and AI systems equally.
> **This is the first thing to read before diving into the mathematics.**

---

## 2 · Mathematical Structure

### 5-D Metric Ansatz (Kaluza–Klein)

The irreversibility field $B_\mu$ and scalar $\phi$ are encoded in the off-diagonal and radion blocks of the 5D parent metric:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$$

The lower-right entry $G_{55} = \phi^2$ means $\phi$ plays the role of the **KK radion** — it sets the size of the compact fifth dimension and is *not* frozen to a constant.  Setting $\phi = 1$ everywhere would hide all scalar dynamics and break the dimensional reduction.

### Key Fields

| Symbol | Name | Role |
|--------|------|------|
| $g_{\mu\nu}$ | 4-D metric | spacetime geometry |
| $B_\mu$ | irreversibility field | gauge field for the arrow of time |
| $\phi$ | entanglement-capacity scalar / radion | nonminimal coupling to curvature; sets size of 5th dimension |
| $H_{\mu\nu} = \partial_\mu B_\nu - \partial_\nu B_\mu$ | field strength | drives dissipation |

---

## 2a · The 4D → 5D → 4D Computation Pipeline

Every call to `compute_curvature(g, B, phi, dx)` executes a three-stage
dimensional pipeline.  Understanding this pipeline is essential for interpreting
any curvature or evolution output.

### Why go through 5D at all?

Straightforward 4D curvature of $g_{\mu\nu}$ alone cannot see the
irreversibility field $B_\mu$ or the scalar $\phi$.  The Kaluza–Klein ansatz
packages all three fields into a single geometric object $G_{AB}$ so that
Einstein's equations in 5D automatically generate the coupled
Walker–Pearson equations upon dimensional reduction — no extra source terms
need to be added by hand.

### Stage 1 — Lift: 4D fields → 5D metric

The three input fields are assembled into the $5\times 5$ parent metric:

$$G_{AB} = \begin{pmatrix} g_{\mu\nu} + \lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$$

```python
G5 = assemble_5d_metric(g, B, phi, lam)   # shape (N, 5, 5)
```

Key points:
- The **4×4 block** $G_{\mu\nu}$ carries the metric and the kinetic term of $B_\mu$.
- The **off-diagonal column/row** $G_{\mu 5} = \lambda\phi B_\mu$ encodes the irreversibility field.
- The **radion** $G_{55} = \phi^2$ is dynamic; it must evolve with $\phi$, not be fixed at 1.

### Stage 2 — Curve: 5D Christoffel symbols and Riemann tensor

Standard differential geometry is applied to $G_{AB}$:

$$\Gamma^C_{AB} = \tfrac{1}{2}\,G^{CD}\!\left(\partial_A G_{BD} + \partial_B G_{AD} - \partial_D G_{AB}\right)$$

$$R^D{}_{CAB} = \partial_A\Gamma^D_{BC} - \partial_B\Gamma^D_{AC} + \Gamma^D_{AE}\Gamma^E_{BC} - \Gamma^D_{BE}\Gamma^E_{AC}$$

```python
Gamma5 = christoffel(G5, dx)               # shape (N, 5, 5, 5)
Riem5  = _riemann_from_christoffel(Gamma5, dx)  # shape (N, 5, 5, 5, 5)
```

This step is where $B_\mu$ and $\phi$ contribute to the geometry — through
the derivatives of $G_{AB}$ that appear inside $\Gamma$.

### Stage 3 — Project: 5D Ricci → 4D Ricci block

The 5D Ricci tensor $\mathcal{R}_{AB} = R^C{}_{ACB}$ is contracted and its
$4\times 4$ block extracted:

$$R_{\mu\nu}^{(4D)} = \mathcal{R}_{\mu\nu}|_{A,B \in \{0,1,2,3\}}$$

$$R^{(4D)} = g^{\mu\nu}R_{\mu\nu}^{(4D)}$$

```python
# 5D Ricci (full 5×5)
Ricci5[:, A, B] = sum_C Riem5[:, C, A, C, B]

# Project: keep only the 4D block
Ricci = Ricci5[:, :4, :4]          # (N, 4, 4) — effective 4D Ricci
R     = einsum('nij,nij->n', g_inv, Ricci)  # (N,) — 4D scalar curvature
```

The returned `Gamma`, `Riemann`, `Ricci`, `R` are all the 4D blocks of the
5D tensors — they contain the full KK contribution from $B_\mu$ and $\phi$
that a naive 4D calculation would miss.

### At a glance

```
  ┌──────────────────────────────────────────────────────────────────┐
  │   4D inputs          5D geometry           4D outputs            │
  │                                                                  │
  │  g_μν (N,4,4)  ─┐                                               │
  │  B_μ  (N,4)    ──┤→  G_AB (N,5,5)  →  Γ^C_AB  →  R^D_CAB      │
  │  φ    (N,)     ─┘         ↑               ↓                     │
  │                     assemble_5d_metric   contract → Ricci5       │
  │                                               ↓                  │
  │                                         Ricci5[:,:4,:4] → Ricci │
  │                                         g⁻¹ · Ricci    → R     │
  └──────────────────────────────────────────────────────────────────┘
```

### Common pitfalls

| Mistake | Consequence |
|---------|-------------|
| Set $G_{55} = 1$ (freeze radion) | $\phi$ dynamics vanish; scalar equation decouples from geometry |
| Compute Christoffel from $g$ directly | $B_\mu$ and $\phi$ contribute nothing to curvature; Walker–Pearson equations reduce to vacuum GR |
| Apply explicit Euler to metric without Nyquist damping | High-frequency modes grow as $e^{t/dx^2}$; simulation blows up |
| Use explicit-only scalar update | Same blow-up for $\phi$ at large $dt/dx^2$ |

---

## 2b · The 3:2 Scaffold Invariant

A **3:2 structural ratio** runs through every layer of the framework.
It is not a coincidence — it is the diagnostic signature of any theory built
on a scaffolded reduction.

| Context | Three | Two |
|---------|-------|-----|
| **Fields** | Three independent fields: $g_{\mu\nu}$, $B_\mu$, $\phi$ | Two sectors: geometric (metric + radion) and gauge (irreversibility field) |
| **Pipeline stages** | Three stages: Lift → Curve → Project | Two dimensional transitions: 4D→5D (up) and 5D→4D (down) |
| **Reduction equations** | Three decoupled 4D equations upon KK reduction (Einstein, Maxwell-like, Klein-Gordon-like) | Two parent structures: the 5D action and the compactification ansatz |
| **Operator $U$** | Three pillars: $\mathbf{I}$ (Irreversibility) $+$ $\mathbf{H}$ (Holography) $+$ $\mathbf{T}$ (Topology) | Two fixed-point conditions: bulk convergence $U\Psi^*=\Psi^*$ and boundary saturation $S = A/4G$ |
| **Constraints** | Three dynamic degrees of freedom ($g$, $B$, $\phi$) | Two conservation laws: $\nabla_\mu J^\mu_{\rm inf}=0$ and the Hamiltonian constraint |
| **Entropy bookkeeping** | Three-dimensional bulk area $A$ (spatial volume boundary) | Two-dimensional holographic screen (one dimension lower than the bulk slice) |

Whenever you see this ratio in the codebase — three field arrays, two
constraint monitors, three pipeline steps, two convergence checks — it is the
same scaffolded structure in a different coordinate.

---

### Walker–Pearson Field Equations

$$G_{\mu\nu} + \lambda^2 \left( H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2 \right) + \alpha R \phi^2 g_{\mu\nu} = 8\pi G_4\, T_{\mu\nu}$$

### Conserved Information Current

$$\nabla_\mu J^\mu_{\inf} = 0, \qquad J^\mu_{\inf} = \phi^2 u^\mu$$

### Unified Equation of the Unitary Manifold (UEUM)

$$\ddot{X}^a + \Gamma^a_{bc}\dot{X}^b\dot{X}^c = G_U^{ab}\nabla_b S_U + \frac{\delta}{\delta X^a}\!\left(\sum_i \frac{A_{\partial,i}}{4G} + Q_{\rm top}\right)$$

### Final Theorem (FTUM)

There exists a fixed point $\Psi^*$ of the combined operator
$U = \mathbf{I} + \mathbf{H} + \mathbf{T}$
(Irreversibility + Holography + Topology) such that $U\Psi^* = \Psi^*$.

---

## 3 · Repository Structure

> ### ⚠️ Three-Tier Structure — Read Before Interpreting Test Counts
>
> Not all Pillars are equal.  The repository contains three distinct categories
> of content, and all 3330 tests are passing in all three — but "passing" means
> different things in each:
>
> | Tier | Content | What tests prove |
> |------|---------|-----------------|
> | **1 — Physics Core** | KK geometry, CMB predictions, α derivation | Code is correct AND predictions match real observational data |
> | **2 — Speculative Extensions** | BH transceiver, particles, dark matter, cold fusion | Model is internally self-consistent; NOT empirically confirmed |
> | **3 — Analogical Applications** | Medicine, justice, governance, ecology, climate, … | Code faithfully implements the stated analogy; says NOTHING about physical truth of the analogy |
>
> The authoritative separation is in **[SEPARATION.md](SEPARATION.md)**.  
> The known limitations and falsification criteria are in **[FALLIBILITY.md](FALLIBILITY.md)**.

```
.
├── README.md
├── requirements.txt
├── THEBOOKV9a (1).pdf        ← full monograph (READ-ONLY canonical reference)
├── UNIFICATION_PROOF.md      ← formal proof: QM/EM/SM as projections of the 5D geometry
├── QUANTUM_THEOREMS.md       ← new theorems: BH info, CCR, Hawking T, ER=EPR (v9.3)
├── brain/                    ← brain-universe correspondence (structural + dynamical)
│   ├── README.md             ← overview (structural AND dynamical alignment)
│   ├── VARIABLE_ALIGNMENT.md ← symbol-by-symbol: monograph ↔ neural
│   ├── TORUS_ARCHITECTURE.md ← toroidal 5th dimension; grid cells; k_cs=74
│   ├── FIVE_PILLARS_NEUROSCIENCE.md
│   ├── IRREVERSIBILITY_BIOLOGY.md ← neural B_μ; LTP; synaptic directionality
│   └── COUPLED_MASTER_EQUATION.md ← ⭐ Pillar 9: consciousness as coupled FP
├── manuscript/               ← LaTeX/Markdown monograph source (READ-ONLY)
│   └── ch02_mathematical_preliminaries.md
├── discussions/
│   └── AI-Automated-Review-Invitation.md
├── docs/
│   └── semantic-bridge.md    ← predicate map: theory ↔ implementation
├── .github/
│   ├── CONTEXT_SSCE.md       ← AI/Copilot Global Context Manifest (this file)
│   └── copilot-instructions.md
└── src/                      ← numerical implementation (editable)
    ├── core/
    │   ├── metric.py         ← KK ansatz, curvature tensors
    │   ├── evolution.py      ← Walker–Pearson field evolution
    │   ├── boltzmann.py      ← Boltzmann entropy, H-theorem, irreversibility
    │   ├── braided_winding.py ← braided (5,7) resonance; k_cs=74; r-tension resolution ✓
    │   ├── derivation.py     ← symbolic step-by-step field-equation derivations
    │   ├── diagnostics.py    ← CMB diagnostic APIs (chi2, observables, convergence)
    │   ├── fiber_bundle.py   ← fiber-bundle geometry, connection, curvature forms
    │   ├── inflation.py      ← slow-roll inflation, KK Jacobian, birefringence
    │   ├── transfer.py       ← CMB transfer function, Planck 2018 reference spectra
    │   ├── uniqueness.py     ← uniqueness theorems for Walker–Pearson equations
    │   ├── black_hole_transceiver.py ← Pillar 6: BH transceiver, Hubble tension, GW echoes ✓
    │   ├── particle_geometry.py      ← Pillar 7: particles as geometric windings
    │   └── dark_matter_geometry.py   ← Pillar 8: dark matter as Irreversibility Field B_μ
    ├── holography/
    │   └── boundary.py       ← Pillar 4: entropy-area, boundary dynamics
    ├── multiverse/
    │   └── fixed_point.py    ← Pillar 5: UEUM, operator U, FTUM iteration
    └── consciousness/
        └── coupled_attractor.py  ← Pillar 9: Coupled Master Equation; consciousness as Ψ*_brain⊗Ψ*_univ
├── chemistry/                    ← ⭐ Pillar 10 (v9.7): Chemistry as 5D Geometry
│   ├── bonds.py                  ← φ-minimum bond model; bond energies; shell capacity
│   ├── reactions.py              ← B_μ-driven Arrhenius kinetics; reaction flux
│   └── periodic.py               ← KK winding-number periodic table; shell structure
├── astronomy/                    ← ⭐ Pillar 11 (v9.7): Astronomy as FTUM Fixed Points
│   ├── stellar.py                ← stars as FTUM fixed points; Jeans mass; stellar lifecycle
│   └── planetary.py              ← planetary orbits; Titus-Bode; Hill sphere
├── earth/                        ← ⭐ Pillar 12 (v9.7): Earth Sciences as B_μ Fluid Dynamics
│   ├── geology.py                ← plate tectonics; mantle convection; geomagnetic dynamo
│   ├── oceanography.py           ← thermohaline circulation; wave dispersion; ENSO
│   └── meteorology.py            ← atmospheric cells; Lorenz attractor; climate forcing
├── biology/                      ← ⭐ Pillar 13 (v9.7): Biology as Negentropy FTUM Attractors
│   ├── life.py                   ← negentropy fixed points; metabolism; information current
│   ├── evolution.py              ← FTUM fitness landscape; selection as ∇S_U; genetic drift
│   └── morphogenesis.py          ← Turing patterns as φ symmetry breaking; morphogen gradients
├── atomic_structure/             ← ⭐ Pillar 14 (v9.8): Atomic Structure as KK Winding Modes
│   ├── orbitals.py               ← hydrogen levels, radii, degeneracy, selection rules
│   ├── spectroscopy.py           ← Rydberg constant, series wavelengths, Einstein A, Zeeman/Stark
│   └── fine_structure.py         ← Dirac energy, Lamb shift, hyperfine, Landé g-factor
└── cold_fusion/                  ← ⭐ Pillar 15 (v9.9): Cold Fusion as φ-Enhanced Tunneling
    ├── tunneling.py              ← Gamow factor, φ-enhanced tunneling, coherence length
    ├── lattice.py                ← Pd FCC geometry, deuterium loading, B-field at site
    └── excess_heat.py            ← Q-values, COP, excess heat power, anomalous heat signature
├── medicine/                     ← ⭐ Pillar 17 (v9.10): Medicine as φ-Field Homeostasis
│   ├── diagnosis.py              ← biomarker SNR, symptom clustering, differential φ
│   ├── treatment.py              ← drug-receptor φ, dosage, pharmacokinetics
│   └── systemic.py               ← organ φ coupling, immune cascade, systemic balance
├── justice/                      ← ⭐ Pillar 18 (v9.10): Justice as φ-Field Equity
│   ├── courts.py                 ← evidence φ, verdict threshold, appeals dynamics
│   ├── sentencing.py             ← proportionality φ, recidivism, rehabilitation
│   └── reform.py                 ← systemic bias correction, φ-equity convergence
├── governance/                   ← ⭐ Pillar 19 (v9.10): Governance as φ-Field Stability
│   ├── democracy.py              ← voting φ, representation, legitimacy
│   ├── social_contract.py        ← consent φ, rights, obligation balance
│   └── stability.py              ← institutional resilience, corruption noise, φ fixed-points
├── neuroscience/                 ← ⭐ Pillar 20 (v9.11): Neuroscience as φ-Field Neural Networks
│   ├── neurons.py                ← action potential, HH model, axon velocity, synaptic weight
│   ├── synaptic.py               ← NT decay, LTP/LTD, dopamine/serotonin, GABA inhibition
│   └── cognition.py              ← working memory, attention, consolidation, IIT-Φ
├── ecology/                      ← ⭐ Pillar 21 (v9.11): Ecology as φ-Field Ecosystem Dynamics
│   ├── ecosystems.py             ← carrying capacity, entropy, energy transfer, trophic flow
│   ├── biodiversity.py           ← Shannon diversity, extinction risk, keystone effects
│   └── food_web.py               ← predator-prey, cascade, biomass pyramid, decomposer flux
├── climate/                      ← ⭐ Pillar 22 (v9.11): Climate Science as φ-Field Radiative Engine
│   ├── atmosphere.py             ← greenhouse forcing, radiative balance, albedo, ozone
│   ├── carbon_cycle.py           ← ocean uptake, terrestrial sequestration, CH₄, permafrost
│   └── feedback.py               ← ECS, ice-albedo, water vapour, tipping points
├── marine/                       ← ⭐ Pillar 23 (v9.11): Marine Biology & Deep Ocean Science
│   ├── deep_ocean.py             ← hydrothermal vents, bioluminescence, abyssal zones
│   ├── marine_life.py            ← coral bleaching, phytoplankton, whale song, kelp forests
│   └── ocean_dynamics.py         ← thermohaline, upwelling, acidification, El Niño
├── psychology/                   ← ⭐ Pillar 24 (v9.11): Psychology as φ-Field Behaviour
│   ├── cognition.py              ← load, memory trace, creativity, IEF, metacognition
│   ├── behavior.py               ← motivation, RPE, habits, altruism, conformity
│   └── social_psychology.py      ← cohesion, influence, prejudice, leadership, cooperation
├── genetics/                     ← ⭐ Pillar 25 (v9.11): Genetics as φ-Field Information Archive
│   ├── genomics.py               ← mutation rate, diversity, epigenetics, transposons
│   ├── evolution.py              ← selection, drift, fitness, speciation, bottleneck
│   └── expression.py             ← transcription, translation, folding, splicing, chromatin
└── materials/                    ← ⭐ Pillar 26 (v9.11): Materials Science as φ-Field Lattice Dynamics
    ├── condensed.py              ← band gap, phonon scattering, magnetism, defects, phase transitions
    ├── semiconductors.py         ← carrier density, p-n junction, solar cell, quantum dots
    └── metamaterials.py          ← negative index, plasmonic resonance, photonic bandgap, cloaking

---

## 4 · Quickstart

### Install

```bash
pip install -r requirements.txt
```

### Run the test suite — 0 failures (3294 tests: 3282 passed · 1 skipped · 11 slow-deselected)

```bash
python -m pytest tests/ -v
```

Expected output (3282 fast tests pass, 1 skips via guard, 11 slow tests deselected by default):

```
tests/test_inflation.py                       271 passed
tests/test_fiber_bundle.py                     96 passed  ← fiber-bundle geometry
tests/test_completions.py                      72 passed  ← completion/endpoint tests
tests/test_braided_winding.py                 108 passed  ← braided (5,7) resonance, r-tension ✓, 3 adversarial attacks
tests/test_uniqueness.py                       61 passed  ← uniqueness theorems
tests/test_derivation.py                       59 passed
tests/test_derivation_module.py                59 passed  ← Stage 0–3 constraint derivation
tests/test_higher_harmonics.py                 58 passed  ← higher harmonic (n_w=7) analysis
tests/test_fixed_point.py                      50 passed
tests/test_evolution.py                        49 passed
tests/test_boltzmann.py                        49 passed  ← Boltzmann H-theorem
tests/test_parallel_validation.py              38 passed
tests/test_metric.py                           36 passed
tests/test_closure_batch2.py                   31 passed
tests/test_observational_resolution.py         30 passed
tests/test_external_benchmarks.py              30 passed  ← external-benchmark validation
tests/test_cosmological_predictions.py         28 passed  ← cosmological predictions
tests/test_quantum_unification.py              26 passed
tests/test_e2e_pipeline.py                     26 passed
tests/test_closure_batch1.py                   25 passed
tests/test_arrow_of_time.py                    22 passed,  1 skipped ⚑
tests/test_boundary.py                         21 passed
tests/test_fuzzing.py                          20 passed
tests/test_cmb_landscape.py                    17 passed
tests/test_dimensional_reduction.py            14 passed
tests/test_discretization_invariance.py        13 passed
tests/test_convergence.py                      10 passed
# — TIER 2: Speculative physics extensions (internally consistent; NOT empirically confirmed) —
tests/test_black_hole_transceiver.py           75 passed  ← Pillar 6:  BH transceiver [TIER 2]
tests/test_particle_geometry.py                51 passed  ← Pillar 7:  particles as windings [TIER 2]
tests/test_dark_matter_geometry.py             45 passed  ← Pillar 8:  dark matter as B_μ [TIER 2]
tests/test_coupled_attractor.py                61 passed  ← Pillar 9:  Coupled Master Equation [TIER 2]
tests/test_stellar.py                          91 passed  ← Pillar 11: astronomy as FTUM fixed points [TIER 2]
tests/test_atomic_structure.py                187 passed  ← Pillar 14: atomic structure as KK modes [TIER 2]
tests/test_cold_fusion.py                     215 passed  ← Pillar 15: cold fusion as φ tunneling [TIER 2]
# — TIER 3: Analogical applications (tests confirm code correctness ONLY; not physical truth) —
tests/test_chemistry.py                       102 passed  ← Pillar 10: chemistry as 5D geometry [TIER 3]
tests/test_geology.py                          59 passed  ← Pillar 12: geology as B_μ fluid [TIER 3]
tests/test_oceanography.py                     46 passed  ← Pillar 12: oceanography [TIER 3]
tests/test_meteorology.py                      45 passed  ← Pillar 12: meteorology [TIER 3]
tests/test_biology.py                         111 passed  ← Pillar 13: biology as negentropy attractors [TIER 3]
tests/test_medicine.py                         63 passed  ← Pillar 17: medicine as φ homeostasis [TIER 3]
tests/test_justice.py                          63 passed  ← Pillar 18: justice as φ equity [TIER 3]
tests/test_governance.py                      252 passed  ← Pillar 19: governance as φ stability [TIER 3]
tests/test_neuroscience.py                    100 passed  ← Pillar 20: neuroscience as φ neural nets [TIER 3]
tests/test_ecology.py                          95 passed  ← Pillar 21: ecology as φ ecosystems [TIER 3]
tests/test_climate.py                          90 passed  ← Pillar 22: climate as φ radiative engine [TIER 3]
tests/test_marine.py                           90 passed  ← Pillar 23: marine biology & deep ocean [TIER 3]
tests/test_psychology.py                       90 passed  ← Pillar 24: psychology as φ behaviour [TIER 3]
tests/test_genetics.py                         90 passed  ← Pillar 25: genetics as φ information [TIER 3]
tests/test_materials.py                        90 passed  ← Pillar 26: materials science as φ lattice [TIER 3]
# slow (run with: pytest -m slow)
tests/test_richardson_multitime.py             11 passed
================================ 3282 passed, 1 skipped, 11 deselected ================================
```

> ⚑ **The 1 skip is not a failure.** `test_arrow_of_time.py::TestEntropyProductionRate::test_defect_history_mostly_decreasing` calls `pytest.skip("Insufficient residual history to test monotonicity")` when `fixed_point_iteration` converges in fewer than 2 iterations. Immediate convergence is the *correct* physical outcome; the guard documents that there is nothing to check monotonicity of in that case.
>
> **The 11 deselected tests** are in `test_richardson_multitime.py`, marked `@pytest.mark.slow`, and excluded from the default run by `addopts = -m "not slow"` in `pytest.ini`. They verify O(dt²) temporal convergence via Richardson extrapolation. Run with `pytest tests/ -m slow`.

### Run a bulk field simulation

```python
from src.core.evolution import FieldState, run_evolution

# Flat Minkowski background, 64 grid points, spacing dx=0.1
state = FieldState.flat(N=64, dx=0.1)

# Evolve for 200 steps with dt=1e-3
history = run_evolution(state, dt=1e-3, steps=200)

print(f"Final time: {history[-1].t:.3f}")
print(f"Final phi range: [{history[-1].phi.min():.4f}, {history[-1].phi.max():.4f}]")
```

### Compute curvature (via 4D→5D→4D pipeline)

```python
from src.core.metric import compute_curvature
import numpy as np

N, dx = 64, 0.1
eta = np.diag([-1., 1., 1., 1.])
g   = np.tile(eta, (N, 1, 1))
B   = np.zeros((N, 4))
phi = np.ones(N)

# Internally: assembles G_AB (5D) → 5D Christoffel/Riemann/Ricci → projects 4D block
Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
print("Scalar curvature (flat space):", R.mean())   # ≈ 0
```

### Holographic boundary (Pillar 4)

```python
from src.holography.boundary import BoundaryState, entropy_area, evolve_boundary
from src.core.evolution import FieldState

bulk = FieldState.flat(N=64, dx=0.1)
bdry = BoundaryState.from_bulk(bulk.g, bulk.B, bulk.phi, bulk.dx)

print(f"Boundary entropy S = {entropy_area(bdry.h):.4f}")

bulk_evolved = __import__('src.core.evolution', fromlist=['step']).step(bulk, 1e-3)
bdry_evolved = evolve_boundary(bdry, bulk_evolved, dt=1e-3)
```

### Multiverse fixed-point (Pillar 5)

```python
from src.multiverse.fixed_point import MultiverseNetwork, fixed_point_iteration

network = MultiverseNetwork.chain(n=5, coupling=0.05)
result, residuals, converged = fixed_point_iteration(network, max_iter=300, tol=1e-6)

print(f"Converged: {converged}  after {len(residuals)} iterations")
print(f"Final residual: {residuals[-1]:.2e}")
```

### Black Hole Transceiver (Pillar 6)

```python
from src.core.black_hole_transceiver import BlackHoleTransceiver

bh = BlackHoleTransceiver(mass_solar=10.0)
kappa = bh.horizon_saturation()
print(f"Horizon saturation κ_H = {kappa:.6f}")   # → 1.0 (information encoded, not destroyed)

h_ratio = bh.hubble_tension_ratio()
print(f"H_local / H_CMB = {h_ratio:.4f}")         # → ~1.083 (bridging the Hubble tension)
```

### Particles as Geometric Windings (Pillar 7)

```python
from src.core.particle_geometry import ParticleGeometry

pg = ParticleGeometry()
electron_mass = pg.mass_from_curvature(generation=1)
print(f"Electron mass scale: {electron_mass:.4e} GeV")

gauge_groups = pg.gauge_groups()
print(f"Emergent gauge groups: {gauge_groups}")    # → ['U(1)', 'SU(2)', 'SU(3)']
```

### Dark Matter as B_μ Geometry (Pillar 8)

```python
from src.core.dark_matter_geometry import DarkMatterGeometry

dm = DarkMatterGeometry(rho_0=0.3, r_s=8.5)      # rho_0 in GeV/cm³, r_s in kpc
v_flat = dm.flat_rotation_velocity(r_kpc=10.0)
print(f"Flat rotation velocity: {v_flat:.1f} km/s")
```



```
┌──────────────────────────────────────────────────────────────────────┐
│                    Numerical Evolution Pipeline                      │
│                                                                      │
│  1. Initialise  g_μν, B_μ, φ  (flat Minkowski + small perturbation) │
│                                                                      │
│  2. Curvature via 4D→5D→4D pipeline  (see §2a)                      │
│       a. Lift: assemble G_AB (5×5) from g, B, φ                     │
│       b. Curve: 5D Christoffel symbols → Riemann → Ricci5           │
│       c. Project: Ricci = Ricci5[:,:4,:4],  R = g⁻¹·Ricci           │
│                                                                      │
│  3. Update fields  via Walker–Pearson equations                      │
│       g:  semi-implicit Nyquist  g_new = (g + dt·dg + dt·c·η)       │
│                                         ────────────────────────     │
│                                              1 + dt·c,  c = 4/dx²   │
│       B:  explicit  B_new = B + dt·∂_ν(λ² H^νμ)                     │
│       φ:  semi-implicit  φ_new = (φ + dt·(αRφ + S_H + lap_φ))      │
│                                  ─────────────────────────────      │
│                                         1 + dt·2/dx²                │
│                                                                      │
│  4. Enforce constraints  (monitor ‖Ricci‖, ‖∇·J‖)                   │
│  5. Project onto boundary  (holographic screen)                      │
│  6. Apply U = I + H + T  (multiverse update)                        │
│  7. Check FTUM convergence  ‖A_i/4G − S_i‖ < ε   (defect norm)     │
└──────────────────────────────────────────────────────────────────────┘
```

Recommended numerical settings:
- `dt ≤ 0.01 * dx²` for the bulk fields (CFL-like condition)
- Staggered grids for $B_\mu$ (gauge field)
- Semi-implicit schemes for both $g_{\mu\nu}$ and $\phi$ (already built-in)
- Constraint damping coefficient ≥ 0.1 for long runs

---

## 6 · Monograph Structure

The full monograph (*74 chapters, XXIII parts*) is included as
`THEBOOKV9a (1).pdf`.  Key chapters:

| Chapters | Topic |
|----------|-------|
| 1–2 | Motivation & Mathematical Preliminaries |
| 3–6 | 5D Metric Construction & Dimensional Reduction |
| 7–9 | Walker–Pearson Field Equations |
| 49–55 | Irreversible Friedmann Equations & Holographic Fate |
| 56–62 | Multiverse Topology & Inter-Manifold Information Flow |
| 63–74 | Observers, Mind & Co-emergence of Classical Reality |

---

## 7 · Semantic Bridge: Theory ↔ Implementation

The file [`.github/CONTEXT_SSCE.md`](.github/CONTEXT_SSCE.md) serves as the **Global Context
Manifest** for AI-assisted development.  It maps every abstract claim in the monograph to a
concrete engineering requirement so that GitHub Copilot and other LLM agents remain
*physics-aware* during code generation.

For the full function-level predicate map (IMPLEMENTATION / IMPLICATION / LOGIC annotations
that sit *alongside* the source without modifying it), see
[`docs/semantic-bridge.md`](docs/semantic-bridge.md).

### Functional Logic Map

| Monograph Claim (Abstract)  | Implementation (Concrete)          | AI/Copilot Instruction                              |
|-----------------------------|------------------------------------|-----------------------------------------------------|
| **Energy Conservation**     | Unitary Logic Gates                | Ensure all matrix ops are Unitary/Orthogonal.       |
| **Frequency-Mass Coupling** | High-THz Clocking                  | Optimize signal paths for phase-coherence.          |
| **Topological Invariance**  | HDI Differential Routing           | Maintain 50-ohm impedance with zero stubs.          |
| **Walker–Pearson equations**| `src/core/evolution.py`            | Field updates must conserve `‖∇·J_inf‖ ≈ 0`.       |
| **KK Metric Ansatz**        | `src/core/metric.py`               | 5D metric assembly; preserve block structure G_AB.  |
| **FTUM Fixed Point**        | `src/multiverse/fixed_point.py`    | Operator U = I + H + T must converge: `U Ψ* = Ψ*`. |
| **Holographic Boundary**    | `src/holography/boundary.py`       | Entropy-area law `S = A/4G`; no boundary leakage.   |

### Isolation Policy

| Path                  | Edit Policy   | Rationale                                      |
|-----------------------|---------------|------------------------------------------------|
| `THEBOOKV9a*.pdf`     | **READ-ONLY** | Canonical theoretical reference                |
| `manuscript/`         | **READ-ONLY** | Monograph source chapters                      |
| `src/`                | Editable      | Numerical implementation of field equations    |
| `.github/CONTEXT_SSCE.md` | Maintain  | AI context manifest                            |

---

## 8 · Minimal Falsification Conditions

The framework makes the following **specific, testable predictions** beyond
standard GR + the Standard Model.  Any confirmed observation inconsistent with
these predictions would falsify or materially constrain the theory.

### F-1 · Scalar breathing mode in gravitational waves

The dynamic radion $\phi$ is not frozen.  In the strong-gravity regime
(binary mergers, neutron-star collisions), $\phi$ evolves and sources a
**scalar breathing mode** in gravitational radiation — a transverse-scalar
polarisation absent in GR.

**Falsified if:** Next-generation detectors (Einstein Telescope, LISA) confirm
no scalar polarisation to the sensitivity floor set by the Walker–Pearson
coupling $\alpha$.

**Relevant code:** `src/core/evolution.py` — `step()` evolves $\phi$; its
time-derivative directly sets the scalar radiation amplitude.

---

### F-2 · Frequency-dependent gravitational-wave dispersion

The irreversibility field $B_\mu$ contributes $\lambda^2(H_{\mu\rho}H_\nu{}^\rho - \tfrac{1}{4}g_{\mu\nu}H^2)$
to the stress-energy.  For $\lambda > 0$, this produces a small but
**frequency-dependent phase velocity** for gravitational waves — group velocity
$v_g(\omega) \neq c$ at high frequency.

**Falsified if:** Multi-band GW observations (10 mHz – 10 kHz) confirm
dispersion-free propagation at the level $|\Delta v/c| < 10^{-16}$, which
constrains $\lambda^2 \lesssim 10^{-16} / \omega_{\rm peak}^2$.

---

### F-3 · CMB non-Gaussianity from entropic scalar dynamics

If $\phi$ was dynamically active during inflation, its quantum fluctuations
would generate **non-Gaussian correlations** in the CMB (non-zero
$f_{\rm NL}^{\rm local}$ at a level set by $\alpha$).  ΛCDM predicts
$f_{\rm NL} \approx 0$.

**Falsified if:** Simons Observatory / CMB-S4 measure $f_{\rm NL}^{\rm local}$
consistent with zero to $\sigma(f_{\rm NL}) < 1$, while the Walker–Pearson
value for the best-fit $\alpha$ exceeds that bound.

---

### F-4 · Holographic entropy saturation at the fixed point

The FTUM guarantees a fixed point $\Psi^*$ at which the defect
$\|A/4G - S\| \to 0$.  The framework therefore predicts that **no isolated
gravitational system maintains $S \ll A/4G$ indefinitely** — entropy must
converge to the holographic bound.

**Falsified if:** A thermodynamically isolated system (e.g., a black hole
remnant) is confirmed to persist with $S/( A/4G) < \epsilon$ for all
time, where $\epsilon \ll 1$.

**Relevant code:** `src/multiverse/fixed_point.py` — `fixed_point_iteration()`
tracks the defect norm; `src/holography/boundary.py` — `entropy_area()`
computes $A/4G$.

---

### F-5 · GR recovery in the zero-coupling limit

Setting $\lambda \to 0$ and $\phi \to \phi_0$ (constant) must **exactly**
recover the Einstein field equations with a cosmological constant.  This is
not a prediction to be confirmed experimentally — it is a hard internal
consistency requirement that is continuously verified by the test suite.

**Falsified if:** `test_metric.py` or `test_evolution.py` show non-zero
residuals in the GR limit.  Run `python -m pytest tests/ -v` to verify
(**3294 tests: 3282 passed, 1 skipped (guard), 11 slow-deselected, 0 failures**).

---

### Summary table

| ID | Observable | Instrument | Falsification threshold |
|----|-----------|-----------|------------------------|
| F-1 | Scalar GW polarisation | ET / LISA | Non-detection at $\alpha$-predicted amplitude |
| F-2 | GW dispersion | Multi-band GW | $\|\Delta v/c\| < 10^{-16}$ |
| F-3 | CMB non-Gaussianity | Simons Obs / CMB-S4 | $\sigma(f_{\rm NL}) < 1$ with $f_{\rm NL}^{WP} > 1$ |
| F-4 | Holographic entropy saturation | BH thermodynamics | Persistent $S \ll A/4G$ |
| F-5 | GR limit (internal) | `pytest` (3294 tests: 3282 pass · 1 skip · 11 slow-deselected) | Any non-zero GR-limit residual |

---

## 9 · Safety Architecture — SAFETY/

> *"With great power comes great responsibility."* — Stan Lee  
> *"Knowledge belongs to all — but it carries a responsibility that belongs to each of us."* — ThomasCory Walker-Pearson

The `SAFETY/` folder contains the **Manual for the Brakes** — the mathematical kill-switches and ethical framework that any responsible engagement with this theory demands. It is the logical conclusion of building a public-domain framework that includes a formal model for enhanced nuclear tunneling (Pillar 15).

**Core principle: Stability is Topological.** In a 5D framework, safety is not about adding shielding — it is about staying within the (5,7) braid. If you exit the resonance, you lose the protection of the sound-speed floor.

| File | Purpose |
|------|---------|
| [`SAFETY/README.md`](SAFETY/README.md) | Ethical framework, dual-use landscape, Handover of Agency, full safety dimensions table |
| [`SAFETY/unitarity_sentinel.py`](SAFETY/unitarity_sentinel.py) | Real-time monitor: aborts field evolution if kinetic mixing ρ → 1 (manifold tear) |
| [`SAFETY/admissibility_checker.py`](SAFETY/admissibility_checker.py) | Z-admissibility bound: five-edge Pentagonal Collapse detector |
| [`SAFETY/thermal_runaway_mitigation.py`](SAFETY/thermal_runaway_mitigation.py) | 4-layer Pillar 15 guard: temperature · 5D coupling · loading ratio · neutron flux |
| [`SAFETY/PROOF_OF_UNIQUENESS.md`](SAFETY/PROOF_OF_UNIQUENESS.md) | Mathematical proof that (5,7) has no safe nearby alternative — the brittleness argument |
| [`SAFETY/RADIOLOGICAL_SAFETY.md`](SAFETY/RADIOLOGICAL_SAFETY.md) | Neutron flux (D+D → ³He+n), tritium, Pd/D₂ handling, scientific integrity protocol |

### Quick start — safe field evolution

```python
from SAFETY.unitarity_sentinel import UnitaritySentinel, monitor_evolution
from SAFETY.admissibility_checker import AdmissibilityChecker
from src.core.evolution import FieldState

state = FieldState.flat(N=64)
history = monitor_evolution(state, dt=1e-3, steps=500)  # aborts if ρ → 1
```

### Quick start — safe cold fusion modelling

```python
from SAFETY.thermal_runaway_mitigation import ThermalRunawayGuard
from src.core.cold_fusion import ColdFusionConfig

guard = ThermalRunawayGuard(T_max_K=400.0, neutron_flux_limit=1.0)
result = guard.run_safe(ColdFusionConfig(T_K=293.0, loading_ratio=0.9))
```

---

## 10 · License — Dual-Layer Protection

This repository uses two complementary licenses to protect the work for the
global public in perpetuity.

| Layer | Scope | License |
|-------|-------|---------|
| **Theory & content** | Manuscripts, equations, datasets, PDF monograph | [Defensive Public Commons License v1.0 (2026)](LICENSE) |
| **Software** | `src/` · `scripts/` · `tests/` · `submission/` | [GNU AGPL-3.0-or-later](LICENSE-AGPL) |

**DPC v1.0** — Irrevocable public domain dedication.  No patents, no exclusive
IP claims, no paywalls, no proprietary relicensing of the core equations or theory.

**AGPL-3.0** — Strong copyleft for the software implementation.  Any company or
individual who distributes or deploys a modified version — including as a network
service or SaaS product — **must** release their modified source code under the
same open terms.  This closes the "SaaS loophole" and makes commercial lock-in
on the implementation legally impossible.

Attribution is requested but not legally required.  See [NOTICE](NOTICE) for the
full dual-license explanation.

---

## 10 · Credits

This repository is the product of genuine synthesis — theory and science from a human mind, code and document engineering from AI, verification from both.

| Role | Name / System |
|------|--------------|
| Principal Architect — theory, framework, scientific direction | ThomasCory Walker-Pearson |
| Code Architecture, Test Suites, Document Engineering & Synthesis | GitHub Copilot (AI) |
| Safety Architecture (SAFETY/ folder) | GitHub Copilot (AI), commissioned by ThomasCory Walker-Pearson |
| Synthesis & Verification Support | ThomasCory Walker-Pearson · GitHub Copilot · Google Gemini · OpenAI · Microsoft Copilot |
| Version | 9.11 — Academic Edition |

---

## 11 · Citation

If you use this work, please cite it as:

```
Walker-Pearson, T. (2026). The Unitary Manifold: A 5D Gauge Geometry of
Emergent Irreversibility (v9.11). Zenodo.
https://doi.org/10.5281/zenodo.19584531
```

BibTeX:

```bibtex
@misc{walkerPearson2026unitary,
  author    = {Walker-Pearson, ThomasCory},
  title     = {The Unitary Manifold: A 5D Gauge Geometry of Emergent Irreversibility},
  year      = {2026},
  version   = {9.11},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.19584531},
  url       = {https://doi.org/10.5281/zenodo.19584531}
}
```

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19584531.svg)](https://doi.org/10.5281/zenodo.19584531)

For technical inquiries or peer-review submissions, use the LaTeX source files
and BibLaTeX citations provided in the accompanying documentation.
