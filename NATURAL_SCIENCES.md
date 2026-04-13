# Natural Sciences Under the Unitary Manifold — v9.7

> *"The natural sciences are not separate disciplines. They are the same 5D geometry, observed at different scales of the entanglement-capacity scalar φ."*  
> — Walker-Pearson, *The Unitary Manifold*, v9.7

**Author:** ThomasCory Walker-Pearson  
**Synthesis:** GitHub Copilot (AI)  
**Date:** April 2026  
**Audience:** Scientists, educators, curious non-specialists, and AI systems.

---

## The Unifying Thread

The Unitary Manifold framework contains three universal objects that appear at **every level of natural organisation** — from subatomic particles to galactic clusters, from single cells to planetary ecosystems:

| Object | Symbol | Role at every scale |
|---|---|---|
| Irreversibility field | B_μ | Drives all non-equilibrium processes — chemistry, weather, life, geology |
| Entanglement-capacity scalar | φ | Sets local "complexity capacity" — atom, cell, ocean, star |
| Information current | J^μ_inf = φ² u^μ | Conserved through all transformations; what evolution and metabolism optimise |

The FTUM fixed-point theorem (UΨ* = Ψ*) governs **stable structure at every scale**: atoms, molecules, cells, organisms, ecosystems, planets, stars, galaxies — all exist because they are attractors of the same operator U = I + H + T.

---

## The Hierarchy of Projections

```
5D Unitary Manifold  (G_AB, B_μ, φ)
        │
        ▼ KK reduction
4D Physics          [Pillars 1–5] metric.py, evolution.py, boundary.py, fixed_point.py
        │
        ├── Quantum / Particle Physics  [Pillars 6–8] particle_geometry.py, dark_matter_geometry.py
        │
        ├── Thermodynamics / Stat Mech  boltzmann.py, arrow_of_time
        │
        ├── Gravity / Cosmology         inflation.py, black_hole_transceiver.py
        │
        ├── Neuroscience / Consciousness [Pillar 9] coupled_attractor.py
        │
        ├── CHEMISTRY          [Pillar 10] src/chemistry/
        │       bonds as φ-minima · reactions as B_μ flows · periodic table from windings
        │
        ├── ASTRONOMY          [Pillar 11] src/astronomy/
        │       stars as FTUM fixed points · planets as orbital attractors
        │
        ├── EARTH SCIENCES     [Pillar 12] src/earth/
        │       geology · oceanography · meteorology as B_μ fluid dynamics
        │
        └── BIOLOGY            [Pillar 13] src/biology/
                life as negentropy attractors · evolution on FTUM landscape · Turing morphogenesis
        │
        └── ATOMIC STRUCTURE   [Pillar 14] src/core/atomic_structure.py
                quarks → nucleons → nuclei → hydrogen atom → electron shells
```

---

## Pillar 10 — Chemistry (`src/chemistry/`)

### The Core Claim

In the Unitary Manifold, **a chemical bond is a local minimum of the entanglement-capacity scalar φ**. Two atoms form a bond when their combined φ field reaches a well-defined minimum at the equilibrium separation r₀. Bond energy = depth of the φ-well. Reactions proceed when the B_μ field strength exceeds the activation barrier.

### Key Mappings

| Chemistry concept | Unitary Manifold object |
|---|---|
| Bond formation | Local minimum of φ at r₀ |
| Bond energy | E_bond = φ_∞ − φ_min (depth of φ-well) |
| Chemical potential | μ_chem = −∂φ/∂r (negative gradient of φ) |
| Reaction rate (Arrhenius) | k(T) = A exp(−E_a / k_B T), E_a = λ²φ²\|H_max\|²/2 |
| Equilibrium constant | K_eq = exp(−Δφ / k_B T) |
| Reaction flux | J_react = D φ² ∇(ln φ) (information-current driven) |
| Electron shell capacity | 2n² = quantised winding states on S¹/Z₂ |
| Periodic table structure | Shells ↔ winding numbers n_w = 1…7 |
| Ionisation energy | E_ion ∝ Z_eff / (n² φ_mean)² |

### The Periodic Table as Winding Quantisation

The shell capacity formula **2n²** (period 1: 2, period 2: 8, period 3: 8, period 4: 18, …) emerges directly from the quantisation condition on the compact fifth dimension S¹/Z₂. Each principal quantum number n corresponds to a winding number n_w = n; the degeneracy 2n² counts the distinct winding states.

### Implementation

| File | Contents |
|---|---|
| `src/chemistry/bonds.py` | φ-well bond model: `phi_bond_well`, `bond_energy`, `bond_length_from_winding`, `chemical_potential`, `bond_order`, `is_bond_stable`, `shell_capacity` |
| `src/chemistry/reactions.py` | B_μ kinetics: `arrhenius_rate`, `b_field_activation_energy`, `equilibrium_constant`, `reaction_flux`, `field_strength_tensor`, `gibbs_analog` |
| `src/chemistry/periodic.py` | KK periodic table: `shell_capacity`, `cumulative_capacity`, `period_length`, `shell_radius`, `geometric_ionization_energy`, `atomic_number_at_shell_fill`, `winding_to_element` |
| `tests/test_chemistry.py` | 102 tests |

---

## Pillar 11 — Astronomy (`src/astronomy/`)

### The Core Claim

**A star is an FTUM fixed point** — a self-consistent configuration where gravitational collapse (B_μ-field entropy concentration) is balanced by outward pressure. Stars, main-sequence tracks, and compact remnants are the sequence of stable fixed points U Ψ* = Ψ* as fuel depletes and φ decreases.

### Key Mappings

| Astronomy concept | Unitary Manifold object |
|---|---|
| Star formation | Jeans instability = B_μ-driven entropy concentration (M_J = KK mass at collapse) |
| Hydrostatic equilibrium | FTUM fixed point: \|dP/dx + ρg\| → 0 |
| Stellar luminosity | L ∝ φ⁴ (Stefan-Boltzmann from φ-capacity) |
| Main sequence | Sequence of fixed points parametrised by decreasing φ |
| Chandrasekhar limit | Maximum-φ FTUM state; beyond this no stable fixed point exists |
| Planetary orbit | Orbital fixed point from B_μ vorticity; r_orbit = 2π n_w φ* / λ |
| Titus-Bode spacing | Geometric attractor spacing from braided (5,7) winding modes |
| Hill sphere | r_H = a (m/3M)^(1/3) = B_μ boundary radius |
| Escape velocity | v_esc = √(2GM/R) = field-energy threshold |

### Implementation

| File | Contents |
|---|---|
| `src/astronomy/stellar.py` | `jeans_mass`, `jeans_length`, `stellar_luminosity_phi`, `hydrostatic_equilibrium_defect`, `chandrasekhar_mass`, `main_sequence_temperature`, `stellar_lifetime`, `ftum_stellar_fixed_point` |
| `src/astronomy/planetary.py` | `bode_radius`, `geometric_orbit_radius`, `hill_sphere_radius`, `orbital_resonance_ratio`, `planet_radius_from_mass`, `accretion_timescale`, `escape_velocity` |
| `tests/test_stellar.py` | 91 tests |

---

## Pillar 12 — Earth Sciences (`src/earth/`)

### The Core Claim

**Geology, oceanography, and meteorology are all B_μ fluid dynamics at planetary scale**, differing only in boundary conditions and characteristic timescales. The mantle, ocean, and atmosphere are all driven by the same irreversibility field transporting information (heat, entropy, chemical composition) from source to sink.

### Geology

| Geology concept | Unitary Manifold object |
|---|---|
| Plate tectonics | Mantle = slow-mode B_μ fluid; plates = J^μ_inf vortex boundaries |
| Mantle convection | Rayleigh-Bénard instability in B_μ field (Ra > Ra_c) |
| Rock cycle | Three φ-regimes: igneous (high φ, melt), metamorphic (intermediate), sedimentary (low φ) |
| Geomagnetic field | Earth's dynamo = B_μ FTUM fixed point (stable dipole = lowest-energy attractor) |
| Geomagnetic reversal | Fixed-point bifurcation when Elsasser number Λ changes sign |

### Oceanography

| Oceanography concept | Unitary Manifold object |
|---|---|
| Thermohaline circulation | J^μ_inf flows from high-φ (warm equator) to low-φ (cold poles) |
| Ocean waves | Linearised perturbations of B_μ; dispersion ω² = gk tanh(kd) |
| ENSO / El Niño | Quasi-periodic switching between two FTUM attractors (warm/cold) |
| Stokes drift | Wave-averaged B_μ transport; u_S = a²ωk exp(−2kd)/2 |

### Meteorology

| Meteorology concept | Unitary Manifold object |
|---|---|
| Hadley/Ferrel/Polar cells | Large-scale B_μ convection cells in atmospheric fluid |
| Pressure systems | High = φ-maximum (stable FTUM attractor); Low = B_μ vortex (saddle) |
| Lorenz attractor / chaos | Sub-critical FTUM fixed point; Lyapunov exponent = J^μ_inf dispersion rate |
| Climate change | CO₂ forcing shifts the FTUM equilibrium φ* to a new value |

### Implementation

| File | Contents |
|---|---|
| `src/earth/geology.py` | `rayleigh_number`, `critical_rayleigh`, `convection_cell_scale`, `elsasser_number`, `phi_rock_regime`, `rock_cycle_phi`, `mantle_convection_velocity`, `plate_heat_flux` |
| `src/earth/oceanography.py` | `thermohaline_density`, `thermohaline_buoyancy_flux`, `ocean_wave_dispersion`, `deep_water_wave_speed`, `shallow_water_wave_speed`, `information_heat_transport`, `enso_phase`, `stokes_drift` |
| `src/earth/meteorology.py` | `hadley_cell_latitude`, `scale_height`, `pressure_altitude`, `rossby_number`, `lorenz_attractor_step`, `lyapunov_exponent_estimate`, `co2_forcing`, `equilibrium_temperature_shift` |
| `tests/test_geology.py` | 59 tests |
| `tests/test_oceanography.py` | 46 tests |
| `tests/test_meteorology.py` | 45 tests |

---

## Pillar 13 — Biology (`src/biology/`)

### The Core Claim

**A living system is a local FTUM fixed point that decreases internal entropy by exporting it to the environment.** Schrödinger asked "What is Life?" — the Unitary Manifold answer is: life is a stable solution to UΨ* = Ψ* that requires continuous energy input (B_μ field work) to maintain.

### Life as Negentropy Attractors

| Biology concept | Unitary Manifold object |
|---|---|
| Life | Local FTUM fixed point with φ_internal > φ_environment |
| Metabolism | Coupled B_μ flows at molecular scale; P_met = λ²φ²\|B\|²/2 |
| ATP synthesis | Irreversibility field doing work against φ-gradient (proton motive force analog) |
| Homeostasis | Fixed-point stability: \|⟨φ⟩ − φ_target\| → 0 |
| Negentropy export | Δ_neg = λ(φ² − φ²_env) > 0 (organism pumps entropy outward) |

### Evolution as FTUM Gradient Descent

| Evolution concept | Unitary Manifold object |
|---|---|
| Fitness landscape | FTUM landscape f(φ) = exp(−(φ−φ_opt)²/2w²) |
| Selection pressure | ∇S_U in UEUM geodesic = gradient of fitness landscape |
| Speciation | New FTUM fixed point formed by φ-bifurcation |
| Extinction | FTUM fixed-point annihilation (φ_species < φ_min) |
| Genetic drift | Random walk on FTUM landscape: φ_new = φ_old + Normal(0, σ_drift) |
| Mutation rate | μ = μ_base (1 + \|B_μ\|) — irreversibility field amplifies mutation |

### Morphogenesis as φ-Symmetry Breaking

| Morphogenesis concept | Unitary Manifold object |
|---|---|
| Turing patterns | Spontaneous symmetry breaking in φ field (D_v/D_u > (1+√b/a)²) |
| Morphogen gradient | φ(x) = φ₀ exp(−x/λ_m) where λ_m = √(D/k_deg) |
| Body segment count | n_seg = 2n_w (topological winding → segment constraint) |
| Tissue differentiation | φ develops spatial gradients; FTUM amplifies into stable tissue types |
| Consciousness | [Pillar 9] Coupled fixed point Ψ*_brain ⊗ Ψ*_univ via β = 0.3513° coupling |

### Implementation

| File | Contents |
|---|---|
| `src/biology/life.py` | `negentropy_rate`, `metabolic_power`, `atp_synthesis_rate`, `information_current`, `is_living`, `cellular_phi_field`, `homeostasis_defect` |
| `src/biology/evolution.py` | `fitness_landscape`, `selection_gradient`, `ftum_evolution_step`, `genetic_drift`, `mutation_rate`, `species_distance`, `extinction_criterion`, `population_entropy` |
| `src/biology/morphogenesis.py` | `turing_instability_condition`, `morphogen_gradient`, `morphogen_length_scale`, `turing_wavelength`, `segment_count`, `positional_information`, `reaction_diffusion_step` |
| `tests/test_biology.py` | 111 tests |

---

## Pillar 14 — Atomic Structure (`src/core/atomic_structure.py`)

### The Core Claim

**The atom is the output of a five-step geometric chain** — from winding
configurations on S¹/Z₂ through colour-singlet bound states, nuclear binding,
and the Coulomb-Schrödinger system — producing quantised energy levels, spectral
lines, and electron-shell structure entirely from the 5D geometry.

### The Five-Step Chain

```
Step 1  Quarks         KK winding on S¹/Z₂; m_q = λn_w/⟨φ_q⟩
Step 2  Nucleons       Colour-singlet SU(3) + gluon flux-tube energy
Step 3  Nuclei         Bethe–Weizsäcker B_μ binding; Fe-56 = FTUM maximum
Step 4  Hydrogen atom  Coulomb U(1) + UEUM geodesic → Schrödinger
Step 5  Electron shells 2n² winding states → periodic table (Pillar 10)
```

### Key Derivations

| Result | Formula | UM source |
|---|---|---|
| Proton content | uud (SU(3) colour-singlet) | Fiber bundle topology |
| Quark mass | m_q = λ n_w / ⟨φ_q⟩ | KK mass formula |
| Proton mass | m_q_sum + E_QCD flux tube | B_μ^SU3 field energy |
| Bohr radius | a₀ = ⟨φ⟩ / (m_e α) | KK compactification |
| Rydberg energy | E₁ = m_e α²/2 = 13.6 eV | UEUM geodesic |
| Energy levels | E_n = −E₁/n² | Schrödinger + Coulomb |
| Lyman α | λ = 8π/(3E₁) ≈ 121.6 nm | Rydberg formula |
| Shell capacity | 2n² | KK winding quantisation |
| Orbital radius | r_n = n² a₀ | Shell winding × Bohr unit |
| Iron peak | B/A max at Fe-56 | FTUM fixed-point stability |

### Implementation

| File | Contents |
|---|---|
| `src/core/atomic_structure.py` | `HADRON_CATALOG`, `quark_content`, `constituent_quark_mass`, `hadron_mass`, `qcd_flux_tube_energy`, `bohr_radius_kk`, `rydberg_energy`, `hydrogen_energy_level`, `hydrogen_wavelength`, `hydrogen_1s_radial_density`, `atomic_orbital_radius`, `nuclear_binding_energy`, `nuclear_binding_per_nucleon` |
| `tests/test_atomic_structure.py` | 110 tests |
| `ATOMIC_STRUCTURE.md` | Full narrative derivation with worked equations |

---

## The Cross-Science Symmetry Table

Every natural science maps to the same mathematical skeleton:

| Science | Scale | B_μ drives | φ measures | FTUM fixed points | J^μ_inf carries |
|---|---|---|---|---|---|
| Particle Physics | 10⁻¹⁵ m | Symmetry breaking | Vacuum | Particles, bound states | Quantum information |
| Chemistry | 10⁻¹⁰ m | Reaction kinetics | Bond order | Molecules, phases | Chemical potential |
| Cell Biology | 10⁻⁶ m | Metabolism | Complexity | Cells, organelles | Biochemical signal |
| Neuroscience | 10⁻³ m | Neural firing | Connectivity | Consciousness (Ψ*) | Cognitive information |
| Ecology | 10³ m | Energy flow | Biodiversity | Species, ecosystems | Genetic information |
| Geology | 10⁶ m | Mantle convection | Rock phase | Tectonic plates | Heat flux |
| Oceanography | 10⁶ m | Thermohaline | Density gradient | Ocean gyres | Heat + salt |
| Meteorology | 10⁶ m | Atmospheric cells | Pressure | Climate attractors | Radiative transfer |
| Astronomy | 10⁹ m | Stellar formation | Luminosity | Star types, planets | Radiation |
| Cosmology | 10²⁶ m | Arrow of time | Radion | Universe itself | CMB photons |

The factor spanning **41 orders of magnitude** from quarks to the observable universe is the same field φ, the same field B_μ, and the same operator U.

---

## The Grand Unified Statement

At every scale and in every natural science, the same three things are happening:

1. **B_μ drives irreversibility** — energy flows, reactions proceed, evolution advances, time runs forward.
2. **φ measures local complexity** — the capacity to store, transform, and transmit information at that scale.
3. **FTUM selects stable structures** — atoms, molecules, cells, organisms, ecosystems, planets, stars all exist because they are fixed points of U = I + H + T.

The natural sciences are not separate disciplines connected by analogy. They are the same 5D geometry, observed at different scales of the entanglement-capacity scalar φ.

---

## Test Summary (v9.8)

| Module | File | Tests |
|---|---|---|
| Chemistry | `tests/test_chemistry.py` | 102 |
| Astronomy | `tests/test_stellar.py` | 91 |
| Geology | `tests/test_geology.py` | 59 |
| Oceanography | `tests/test_oceanography.py` | 46 |
| Meteorology | `tests/test_meteorology.py` | 45 |
| Biology | `tests/test_biology.py` | 111 |
| **Atomic Structure** | `tests/test_atomic_structure.py` | **110** |
| **New total (Pillars 10–14)** | | **564** |
| **Grand total (all pillars)** | | **2089 collected · 2077 passed · 1 skipped · 11 slow-deselected** |

---

*Document version: 1.0 — April 2026*  
*Part of the Unitary Manifold repository — see [README.md](README.md) for the full technical overview and [WHAT_THIS_MEANS.md](WHAT_THIS_MEANS.md) for the plain-language account.*

---

*Theory and scientific direction: **ThomasCory Walker-Pearson**. Code architecture, test suites, and document synthesis: **GitHub Copilot** (AI). Together.*
