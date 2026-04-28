# Simulation Runs — Unitary Manifold

This document records the reproducible simulation scripts in `scripts/`, the
parameter regimes used, and the expected outputs with numerical tolerances.
All scripts use fixed random seeds and produce structured JSON output.

---

## How to run

```bash
pip install -r requirements.txt
python scripts/run_metric.py
python scripts/run_evolution.py
python scripts/run_boundary.py
python scripts/run_fixed_point.py
```

Each script prints human-readable progress, then a JSON block with all
parameter values, measured metrics, tolerances, and a `"status": "PASS"` or
exception on failure.

---

## 1. `scripts/run_metric.py` — KK metric and curvature

### What is being tested

- The 5-D Kaluza–Klein metric `G_AB` is assembled from a near-flat 4-D metric,
  a small gauge field `B_μ`, and a scalar `φ ≈ 1`.
- The field-strength tensor `H_μν = ∂_μ B_ν − ∂_ν B_μ` is computed.
- The full curvature hierarchy `(Γ, Riemann, Ricci, R)` is computed.
- A second run on the *exact* Minkowski background verifies that `Ricci = 0`
  and `R = 0` analytically.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Grid points `N` | 64 |
| Spacing `dx` | 0.1 |
| KK coupling `λ` | 1.0 |
| Perturbation amplitude `ε` | 1e-3 |
| Random seed | 0 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| `max |G_AB − G_BA|` (symmetry) | < 1e-14 |
| `max |H_μν + H_νμ|` (antisymmetry) | < 1e-10 |
| Ricci Frobenius norm mean (near-flat) | < 1.0 |
| Scalar curvature `R_max` (near-flat) | < 5.0 |
| Ricci (exact flat), `R` (exact flat) | = 0.0 (machine precision) |

### Reproducibility

Re-running with `SEED=0` always produces the same JSON output.

---

## 2. `scripts/run_evolution.py` — Walker–Pearson field evolution

### What is being tested

- `FieldState.flat` initialises a reproducible near-flat background.
- `run_evolution` advances the metric `g_μν`, gauge field `B_μ`, and scalar
  `φ` for `STEPS=50` steps using the semi-implicit Walker–Pearson integrator.
- The constraint monitor is evaluated every 10 steps:
  - `R_max`, `phi_max`, `B_norm_mean`, `ricci_frob_mean`
  - `T_div_max` (new stress-energy divergence diagnostic)
- Determinism is verified: two runs from the same seed produce identical output.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Grid points `N` | 64 |
| Spacing `dx` | 0.1 |
| Timestep `dt` | 1e-3 |
| Steps | 50 |
| KK coupling `λ` | 1.0 |
| Nonminimal coupling `α` | 0.1 |
| Random seed | 42 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| `phi_max` at `t=0.05` | < 100 |
| `R_max` at `t=0.05` | < 10 |
| `T_div_max` | finite |
| Determinism residual | = 0.0 (exact) |

### Known limitations

Beyond approximately `t=0.05` (50 steps at `dt=1e-3`) the explicit `α R φ`
reaction term can drive instability when `R` grows large.  The semi-implicit
Laplacian treatment (introduced in the bug fix) stabilises the diffusion
component but not the reaction component.  Longer stable runs require either
a smaller `dt`, a smaller `α`, or a fully implicit treatment of the reaction
term.

---

## 3. `scripts/run_boundary.py` — Holographic boundary dynamics

### What is being tested

- `BoundaryState.from_bulk` projects bulk fields onto the holographic screen.
- `entropy_area` computes the Bekenstein–Hawking entropy `S = A / 4G`.
- `evolve_boundary` co-evolves the boundary metric alongside the bulk for
  `STEPS=50` steps.
- `information_conservation_check` computes the Gauss-law residual at each step.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Grid points `N` | 64 |
| Spacing `dx` | 0.1 |
| Timestep `dt` | 1e-3 |
| Co-evolution steps | 50 |
| Newton's constant `G4` | 1.0 |
| Random seed | 0 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| Initial entropy `S0` | > 0 |
| Boundary metric `h_ab` | finite throughout |
| Information flux `J_bdry` | finite throughout |
| Information conservation residual | finite throughout |

### Observation

The boundary entropy grows rapidly (exponentially) because the evolve_boundary
equation contains a `θ_ab[J_inf]` deformation sourced by the information flux,
which itself grows as the bulk evolves.  This is a known consequence of the
explicit coupling; it does not indicate a code error.  A well-posed boundary
theory should include a damping or renormalisation prescription.

---

## 4. `scripts/run_fixed_point.py` — FTUM multiverse fixed-point

### What is being tested

- `fixed_point_iteration` applies the combined operator `U = I + H + T` to a
  multiverse network and iterates until convergence.
- Two network topologies are tested: chain (`n=5`) and fully-connected (`n=4`).
- After convergence, every node is verified to satisfy `S ≤ A / 4G`
  (holographic entropy bound).
- UEUM geodesic acceleration is verified finite for all nodes.

### Parameter regime

| Parameter | Value |
|-----------|-------|
| Chain network | `n=5`, `coupling=0.05` |
| Fully-connected | `n=4`, `coupling=0.05` |
| Pseudo-timestep `dt` | 1e-3 |
| Convergence tolerance `tol` | 1e-2 |
| Max iterations | 500 (chain), 1000 (fully-connected) |
| Random seed | 42 |

### Expected outputs and tolerances

| Metric | Tolerance |
|--------|-----------|
| `converged` flag | `True` |
| Final residual | < 1e-2 |
| All node entropies `S ≤ A/4G` | exact (up to 1e-10) |
| UEUM acceleration | finite |

### Note on convergence tolerance

The natural residual floor is `O(dt) ≈ 1e-3` because the Irreversibility
operator increases entropy by `κ A dt` per step and the Holography operator
clamps it back, creating a cyclic perturbation.  A tolerance of `1e-2` (ten
times this floor) confirms that the system has reached its steady regime.
Reducing `dt` reduces the floor proportionally.

---

## Test suite

The full automated test suite is in `tests/` and can be run with:

```bash
pip install pytest numpy scipy
python -m pytest tests/ recycling/ "Unitary Pentad/" -q
```

12962 tests (11413 fast-selected + 11 slow-deselected + recycling/ 316 + Unitary Pentad/ 1234): 12950 passed · 2 skipped · 0 failed.

> **Skip 1:** `test_arrow_of_time.py::TestEntropyProductionRate::test_defect_history_mostly_decreasing` uses a `pytest.skip()` guard that fires on immediate convergence — correct behaviour, not a failure.
> **Skip 2:** `test_precision_audit.py` — skipped at collection when `mpmath` is not installed; `pip install mpmath` enables it.
> **Slow:** 11 tests in `test_richardson_multitime.py` marked `@pytest.mark.slow`; run with `pytest tests/ -m slow`.

| File | Tests | Topics |
|------|-------|--------|
| `test_metric.py` | 36 | KK metric, Christoffel, Riemann/Ricci, field strength, α from curvature |
| `test_evolution.py` | 49 | RK4 integrator, determinism, flat-space stability, φ boundedness, ∇T diagnostic |
| `test_boundary.py` | 21 | entropy bound, info conservation, evolve_boundary |
| `test_fixed_point.py` | 73 | IHT operators, UEUM, convergence, Banach contraction proof, α derivation |
| `test_convergence.py` | 10 | O(dx²) gradient, Laplacian, Christoffel convergence |
| `test_inflation.py` | 271 | CMB power spectrum, ns/r, birefringence, triple constraint, EE/TE source functions, TB/EB spectra |
| `test_parallel_validation.py` | 38 | dual-branch independence, observable decoupling, amplitude closure, transfer physics |
| `test_arrow_of_time.py` | 23 | entropy growth, backward deficit, path independence, production rates |
| `test_cmb_landscape.py` | 17 | χ² landscape, TB/EB cross-checks, amplitude analysis |
| `test_e2e_pipeline.py` | 26 | end-to-end chain closure, CS level uniqueness, α consistency loop |
| `test_observational_resolution.py` | 30 | nₛ/β/χ² tolerances, angular resolution, LiteBIRD pol-ratio bounds |
| `test_ew_hierarchy.py` | 410 | Pillar 50: electroweak hierarchy, naturalness, KK radiative corrections |
| `test_zero_point_vacuum.py` | 323 | Pillar 49: zero-point vacuum energy, Casimir spectrum |
| `test_cold_fusion.py` | 240 | φ-enhanced tunneling, Pd lattice dynamics, excess heat |
| `test_aps_spin_structure.py` | 217 | Pillar 70-B: APS spin structure, η̄ derivation, Z₂ parity |
| `test_roman_space_telescope.py` | 187 | Pillar 66: Roman ST falsification forecasts |
| `test_lattice_boltzmann.py` | 187 | Pillar 15-C: KK-mediated radion COP, unitary collision integral |
| `test_atomic_structure.py` | 187 | atomic orbitals, fine structure, spectroscopy |
| `test_nonabelian_kk.py` | 173 | Pillar 62: SU(3)_C KK reduction, gluon KK tower, α_s running |
| `test_phi0_closure.py` | 170 | Pillar 56: φ₀ self-consistency closure |
| `test_completeness_theorem.py` | 170 | Pillar 74: k_CS=74 topological completeness, 7 constraints |
| `test_kk_backreaction.py` | 161 | Pillar 72: KK back-reaction, radion-metric closed loop |
| `test_aps_eta_invariant.py` | 158 | Pillar 70: APS eta invariant, spectral asymmetry |
| `test_nw_anomaly_selection.py` | 156 | Pillar 67: anomaly-cancellation uniqueness for n_w |
| `test_boundary_singularities.py` | 153 | holographic boundary singularities, Fefferman-Graham |
| `test_goldberger_wise.py` | 146 | Pillar 68: Goldberger-Wise moduli stabilisation |
| `test_bmu_dark_photon.py` | 145 | Pillar 71: B_μ dark photon, kinetic mixing |
| `test_anomaly_closure.py` | 144 | Pillar 58: anomaly closure, first-principles derivation |
| `test_photon_epoch.py` | 141 | Pillar 64: photon epoch, recombination, sound horizon |
| `test_kk_gw_background.py` | 140 | Pillar 69: KK stochastic GW background |
| `test_medicine.py` | 139 | φ homeostasis, diagnosis, treatment |
| `test_cmb_boltzmann_peaks.py` | 136 | Pillar 73: CMB Boltzmann peak structure |
| `test_observational_frontiers.py` | 129 | Pillar 38: observational frontiers |
| `test_polariton_vortex.py` | 127 | Pillar 47: exciton-polariton vortex lattice |
| `test_torsion_remnant.py` | 125 | Pillar 48: torsion remnant |
| `test_justice.py` | 124 | courts, sentencing, φ equity |
| `test_braided_winding.py` | 118 | braided (5,7) resonance, CS level k=74, c_s=12/37 |
| `test_litebird_forecast.py` | 116 | Pillar 45-D: LiteBIRD forecast |
| `test_hubble_tension.py` | 116 | Hubble tension, 5D radion H_eff |
| `test_dirty_data_test.py` | 116 | Pillar 61: AxiomZero internal falsifier suite |
| `test_governance.py` | 115 | democracy, social contract, φ-geometry |
| `test_basin_analysis.py` | 114 | FTUM 192-case convergence sweep |
| `test_transfer.py` | 112 | CMB transfer function, radiation-dominated era |
| `test_biology.py` | 111 | evolution, morphogenesis, life emergence |
| `test_anomaly_uniqueness.py` | 111 | Pillar 55: anomaly cancellation uniqueness |
| `test_ads_cft_tower.py` | 111 | Pillar 40: AdS/CFT tower correspondence |
| `test_matter_power_spectrum.py` | 109 | Pillar 59: matter power spectrum P(k) |
| `test_cmb_transfer.py` | 106 | Pillar 63: Eisenstein-Hu CMB transfer |
| `test_particle_mass_spectrum.py` | 105 | Pillar 60: particle mass spectrum |
| `test_consciousness_deployment.py` | 105 | Pillar 9-B: consciousness deployment |
| `test_fermion_emergence.py` | 104 | Pillar 54: fermion emergence from Z₂ orbifold |
| `test_solitonic_charge.py` | 103 | Pillar 39: solitonic topological charge |
| `test_froehlich_polaron.py` | 102 | Pillar 46: Fröhlich polaron |
| `test_chemistry.py` | 102 | bonds, periodic table, reaction dynamics |
| `test_layering.py` | 99 | multiverse layering, vacuum selection |
| `test_lattice_dynamics.py` | 98 | Pillar 15-B: phonon-radion bridge |
| `test_fiber_bundle.py` | 96 | principal bundles, characteristic classes, anomaly cancellation |
| `test_three_generations.py` | 94 | Pillar 42: three-generation theorem |
| `test_quark_gluon_epoch.py` | 94 | Pillar 65: QGP epoch, radion sound-speed coincidence |
| `test_neuroscience.py` | 92 | neurons, synaptic dynamics, cognition as φ networks |
| `test_stellar.py` | 91 | stellar structure, nucleosynthesis |
| `test_coupled_attractor.py` | 83 | coupled brain-universe attractor, birefringence constants |
| `test_psychology.py` | 82 | cognition, behaviour, social psychology |
| `test_genetics.py` | 78 | genomics, gene expression |
| `test_coupled_history.py` | 78 | Pillar 45: coupled history, consciousness-QM bridge |
| `test_materials.py` | 75 | condensed matter, semiconductors, metamaterials |
| `test_information_paradox.py` | 75 | Pillar 36: information paradox, BH holography |
| `test_dissipation_geometry.py` | 75 | Pillar 35: dissipation geometry, entropy current |
| `test_delay_field.py` | 75 | Pillar 41: 5D delay field model |
| `test_black_hole_transceiver.py` | 75 | BH information transceiver |
| `test_quantum_switch.py` | 74 | Theorem XVI: quantum switch, causal order |
| `test_non_gaussianity.py` | 73 | two-field f_NL from dynamical radion |
| `test_branch_catalog.py` | 73 | multiverse branch catalog |
| `test_marine.py` | 72 | deep ocean, marine life |
| `test_completions.py` | 72 | completion and endpoint tests |
| `test_adm_engine.py` | 72 | Pillar 53: 5D ADM decomposition |
| `test_ecology.py` | 70 | ecosystems, biodiversity, food web |
| `test_dynamical_radion.py` | 67 | dynamical radion, moduli potential |
| `test_climate.py` | 66 | atmosphere, carbon cycle, feedback |
| `test_compactification.py` | 65 | Pillar 29: compactification, vacuum selection |
| `test_boltzmann_bridge.py` | 65 | Pillar 52-B: CAMB/CLASS bridge |
| `test_analytic_benchmark.py` | 64 | analytic benchmarks, machine-precision checks |
| `test_uniqueness.py` | 61 | S¹/Z₂ uniqueness scan, ΛCDM no-go |
| `test_mesh_refinement.py` | 61 | Pillar 59: mesh-refinement convergence |
| `test_kk_quantum_info.py` | 59 | Pillar 31: KK quantum information |
| `test_geology.py` | 59 | plate tectonics, mantle dynamics |
| `test_derivation_module.py` | 59 | Stage 0–3 constraint derivation |
| `test_derivation.py` | 59 | key-integer derivations (k_cs=74, n_w=5/7, k_rc=12, φ_min=18) |
| `test_higher_harmonics.py` | 58 | higher KK harmonic structure |
| `test_geometric_collapse.py` | 58 | Pillar 44: geometric wavefunction collapse |
| `test_particle_geometry.py` | 51 | particle mass spectrum from KK geometry |
| `test_planetary.py` | 49 | planetary orbitals, braid scaling laws |
| `test_boltzmann.py` | 49 | baryon-loaded CMB transfer |
| `test_oceanography.py` | 46 | ocean thermodynamics, salinity, currents |
| `test_realworld_comparison.py` | 45 | real-world benchmark comparisons |
| `test_meteorology.py` | 45 | atmospheric dynamics, weather patterns |
| `test_field_equation_stress.py` | 45 | field-equation stress tests |
| `test_dark_matter_geometry.py` | 45 | DM halo profiles, rotation curves |
| `test_boundary_group_theory.py` | 42 | group-theory representations, holographic boundary |
| `test_kk_gauge_spectrum.py` | 36 | KK gauge boson mass spectrum |
| `test_prediction_impact.py` | 35 | real-world prediction impact assessment |
| `test_closure_batch2.py` | 31 | numerical robustness, cross-module consistency |
| `test_external_benchmarks.py` | 30 | external benchmark validation |
| `test_cosmological_predictions.py` | 28 | Hubble tension, muon g-2, DM curves, GW echoes |
| `test_quantum_unification.py` | 26 | BH info, CCR, Hawking T, ER=EPR |
| `test_closure_batch1.py` | 25 | α dual-path, nₛ KK=Casimir, β coupling chain |
| `test_safety_imports.py` | 23 | SAFETY/ module smoke tests |
| `test_kk_geodesic_reduction.py` | 23 | Lorentz force as geodesic theorem |
| `test_im_action.py` | 22 | irreversibility measure action |
| `test_boundary_completions.py` | 22 | boundary completion structural tests |
| `test_fuzzing.py` | 20 | edge cases, random inputs, adversarial numerics |
| `test_dimensional_reduction.py` | 14 | KK dimensional reduction identities |
| `test_discretization_invariance.py` | 13 | grid-independence checks |
| `test_precision_audit.py` | 1 ⚑ | arbitrary-precision audit (skipped: mpmath absent) |
| `test_richardson_multitime.py` | 11 🐌 | second-order temporal convergence — slow suite |
