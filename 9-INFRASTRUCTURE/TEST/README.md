# Test Suite — Unitary Manifold

**15,096 tests: 15,096 passed · 330 skipped · 11 slow-deselected · 0 failures** — verified 2026-05-01, Python 3.12, pytest

**14,641 = 11⁴** — prior structural milestone at v9.25: 11 M-theory dimensions to the power of 4 world dimensions.

*(tests/ suite: 13,586 passed 76 skipped + recycling/: 316 + 5-GOVERNANCE/Unitary Pentad/: 1,026 passed 254 skipped + omega/: 168)*

### The 330 skipped tests

- **76 dual-use stubs** (38 in `test_lattice_dynamics.py` + 38 in `test_cold_fusion.py`): test classes guarded by `@pytest.mark.skip` because the corresponding implementation functions raise `NotImplementedError` to prevent dual-use misuse. See `DUAL_USE_NOTICE.md`.

- **254 Pentad product stubs** (`5-GOVERNANCE/Unitary Pentad/`): scenario, interrogation, and pilot test classes guarded by `@pytest.mark.skip` because the corresponding deployment functions are reserved for the AxiomZero product. See `PENTAD_PRODUCT_NOTICE.md`.

### The 11 deselected tests

All in `test_richardson_multitime.py`, decorated `@pytest.mark.slow`. Excluded from the default run by `addopts = -m "not slow"` in `pytest.ini`. They verify O(dt²) temporal convergence via Richardson extrapolation and are computationally expensive by design.

---

## Adversarial attacks — where to find the source

The three adversarial attack functions live in **`src/core/braided_winding.py`**:

| Attack | Function | Location |
|--------|----------|---------|
| Attack 1 — Projection Degeneracy (with LEE) | `projection_degeneracy_fraction()` | `src/core/braided_winding.py` |
| Attack 2 — Robustness to Data Drift | `birefringence_scenario_scan()` | `src/core/braided_winding.py` |
| Attack 3 — Full-tower KK Consistency | `kk_tower_cs_floor()` | `src/core/braided_winding.py` |

Their tests are in `tests/test_braided_winding.py` (118 tests, classes `TestProjectionDegeneracy`, `TestBirefringenceScenarioScan`, `TestKKTowerCsFloor`).

**Look-Elsewhere Effect (LEE) in Attack 1**

`projection_degeneracy_fraction()` now includes a full LEE correction. With default parameters (n_max = 15, 105 candidate pairs):

| Quantity | Value | Meaning |
|---------|-------|---------|
| `tuning_fraction` | 4.17 × 10⁻⁴ | Local p-value: prob. a random 4D EFT accidentally satisfies the 5D lock |
| `n_candidates` | 105 | Maximum LEE trials factor (all (n1,n2) pairs with n1 < n2 ≤ 15) |
| `lee_corrected_tuning` | 0.043 | Global p-value after full LEE correction |
| `lee_sigma_equivalent` | 1.72 σ | Gaussian equivalent — the LEE weakens but does not eliminate the signal |
| `isolation_confirmed` | **True** | Both viable k_cs values (61 and 74) have **unique** SOS decompositions |

The key counter-argument: k_cs = 74 was derived *independently* from the birefringence measurement β ≈ 0.35° **before** any search over (n1, n2) pairs. Given k = 74, there is exactly **one** way to write 74 = n₁² + n₂²: (5, 7). The conditional LEE trials factor is therefore **1**, not 105 — there was never a multiple-hypothesis search, and the coincidence argument is mathematically untenable.

---

## How to Run

```bash
pip install numpy scipy pytest
python -m pytest tests/ -v          # ~13,586 fast pass, 76 skipped, 11 deselected (slow)
python -m pytest tests/ -m slow     # 11 slow tests (Richardson convergence)
python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" omega/ -q  # full suite — 15,096 pass
```

Expected result (default):

```
~13586 passed, 76 skipped, 11 deselected in ~115s
```

---

## Test File Summary

| File | Tests | What It Covers |
|------|------:|----------------|
| `tests/test_ew_hierarchy.py` | 410 | Pillar 50: electroweak hierarchy, naturalness, KK radiative corrections |
| `tests/test_zero_point_vacuum.py` | 323 | Pillar 49: zero-point vacuum energy, Casimir spectrum, cosmological constant |
| `tests/test_inflation.py` | 271 | GW potential, slow-roll, CMB (nₛ, r), Planck check, KK Jacobian, Casimir, birefringence, CS coupling, triple constraint, EE/TE source, TB/EB spectra, COBE normalisation, attractor classification, amplitude gap, FTUM attractor domain, RS1 phase scan, birefringence transfer, B_μ rotation angle |
| `tests/test_cold_fusion.py` | 240 | φ-enhanced tunneling, Pd lattice dynamics, excess heat signatures, Coulomb barrier suppression, lattice loading factor |
| `tests/test_aps_spin_structure.py` | 217 | Pillar 70-B: APS full spin-structure derivation chain, η̄ derivation via Hurwitz ζ, Z₂ parity assignment |
| `tests/test_roman_space_telescope.py` | 187 | Pillar 66: Nancy Grace Roman ST UM falsification forecasts — dark energy EOS, weak lensing, BAO, SNe Ia |
| `tests/test_lattice_boltzmann.py` | 187 | Pillar 15-C: KK-mediated radion COP pipeline, lattice heat transport, unitary collision integral |
| `tests/test_atomic_structure.py` | 187 | Atomic orbitals, fine structure, spectroscopy, Rydberg levels, selection rules |
| `tests/test_nonabelian_kk.py` | 173 | Pillar 62: non-Abelian SU(3)_C KK reduction, gluon KK tower, α_s running, CMS open-data anchors |
| `tests/test_phi0_closure.py` | 170 | Pillar 56: φ₀ self-consistency closure, braided nₛ identity, ns_braided(φ₀_FTUM) = ns_canonical |
| `tests/test_completeness_theorem.py` | 170 | Pillar 74: k_CS=74 topological completeness theorem, 7 independent constraints, repository_closure_statement() |
| `tests/test_kk_backreaction.py` | 161 | Pillar 72: KK tower back-reaction, radion-metric closed loop, back-reaction eigenvalue = 1 |
| `tests/test_aps_eta_invariant.py` | 158 | Pillar 70: APS eta invariant, spectral asymmetry, η̄=½ boundary condition |
| `tests/test_nw_anomaly_selection.py` | 156 | Pillar 67: anomaly-cancellation uniqueness argument for n_w selection, k_eff(5)=74 vs k_eff(7)=130 |
| `tests/test_boundary_singularities.py` | 153 | Holographic boundary singularity structure, Fefferman–Graham expansions, structural-connection tests |
| `tests/test_goldberger_wise.py` | 146 | Pillar 68: Goldberger–Wise moduli stabilisation, bulk mass scan, radion mass formula |
| `tests/test_bmu_dark_photon.py` | 145 | Pillar 71: B_μ dark photon, kinetic mixing, CMB polarisation rotation |
| `tests/test_anomaly_closure.py` | 144 | Pillar 58: anomaly closure, first-principles derivation of gauge anomaly cancellation |
| `tests/test_photon_epoch.py` | 141 | Pillar 64: photon epoch cosmology, recombination, sound horizon, Silk diffusion scale, Saha equation |
| `tests/test_kk_gw_background.py` | 140 | Pillar 69: KK stochastic gravitational-wave background, LISA/ET forecasts |
| `tests/test_medicine.py` | 139 | Diagnosis, treatment, systemic φ homeostasis, organ system couplings |
| `tests/test_cmb_boltzmann_peaks.py` | 136 | Pillar 73: CMB Boltzmann peak structure, closing the spectral loop, peak-position vs Planck |
| `tests/test_observational_frontiers.py` | 129 | Pillar 38: observational frontiers, multiverse falsifiers, telescope timeline |
| `tests/test_polariton_vortex.py` | 127 | Pillar 47: exciton-polariton vortex lattice, φ-pinning, condensate topology |
| `tests/test_torsion_remnant.py` | 125 | Pillar 48: torsion remnant, 5D torsion tensor, 4D trace contribution |
| `tests/test_justice.py` | 124 | Courts, sentencing, reform as φ equity, institutional stability |
| `tests/test_braided_winding.py` | 118 | Braided (5,7) resonance, CS level k=74, sound speed c_s=12/37, adversarial attacks 1–3, **LEE-corrected projection degeneracy**, birefringence scenario scan, KK tower floor |
| `tests/test_litebird_forecast.py` | 116 | Pillar 45-D: LiteBIRD forecast, β sensitivity, birefringence signal-to-noise, power-law fit |
| `tests/test_hubble_tension.py` | 116 | Hubble tension, 5D radion H_eff resolution, H₀ posterior shift |
| `tests/test_dirty_data_test.py` | 116 | Pillar 61: AxiomZero internal falsifier suite, stress-testing against adversarial inputs |
| `tests/test_governance.py` | 115 | Democracy, social contract, stability as φ-geometry |
| `tests/test_basin_analysis.py` | 114 | FTUM 192-case convergence sweep, sensitivity analysis, bifurcation scan, topological invariants, Jacobian eigenvalues |
| `tests/test_transfer.py` | 112 | CMB transfer function, radiation-dominated era, transfer physics |
| `tests/test_biology.py` | 111 | Evolution, morphogenesis, life emergence |
| `tests/test_anomaly_uniqueness.py` | 111 | Pillar 55: anomaly cancellation uniqueness proof, gauge-group emergence |
| `tests/test_ads_cft_tower.py` | 111 | Pillar 40: AdS/CFT tower correspondence, bulk-boundary dictionary |
| `tests/test_matter_power_spectrum.py` | 109 | Pillar 59: large-scale structure, KK-modified matter power spectrum P(k) |
| `tests/test_cmb_transfer.py` | 106 | Pillar 63: Eisenstein–Hu CMB transfer function, baryon loading, acoustic source |
| `tests/test_particle_mass_spectrum.py` | 105 | Pillar 60: particle mass spectrum, KK-geometric lepton masses |
| `tests/test_consciousness_deployment.py` | 105 | Pillar 9-B: consciousness deployment, observer-boundary coupling |
| `tests/test_fermion_emergence.py` | 104 | Pillar 54: fermion emergence from Z₂ orbifold, chiral zero modes |
| `tests/test_solitonic_charge.py` | 103 | Pillar 39: solitonic topological charge quantization, winding-number flux |
| `tests/test_froehlich_polaron.py` | 102 | Pillar 46: Fröhlich polaron, electron-phonon coupling, φ-lattice bridge |
| `tests/test_chemistry.py` | 102 | Bonds, periodic table, reaction dynamics |
| `tests/test_layering.py` | 99 | Multiverse layering, vacuum selection, landscape enumeration |
| `tests/test_lattice_dynamics.py` | 98 | Pillar 15-B: collective Gamow factor, phonon-radion bridge |
| `tests/test_fiber_bundle.py` | 96 | Principal bundles over M₄ (KK U(1), SU(2)_L, SU(3), U(1)_Y, trivial), characteristic classes, c₁[KK U(1)]=k_cs=74, c₂[SU(2)_L]=n_w=5, global anomaly cancellation |
| `tests/test_three_generations.py` | 94 | Pillar 42: three-generation theorem, N_gen=3 derivation from Z₂+CS gap |
| `tests/test_quark_gluon_epoch.py` | 94 | Pillar 65: quark-gluon plasma epoch, radion-QGP sound-speed coincidence (ATLAS Pb-Pb 2024) |
| `tests/test_neuroscience.py` | 92 | Neurons, synaptic dynamics, cognition as φ networks |
| `tests/test_stellar.py` | 91 | Stellar structure, nucleosynthesis, compact objects |
| `tests/test_coupled_attractor.py` | 83 | Coupled brain-universe attractor, synchronisation, phase locking, birefringence constants |
| `tests/test_psychology.py` | 82 | Cognition, behaviour, social psychology |
| `tests/test_genetics.py` | 78 | Genomics, gene expression, molecular evolution |
| `tests/test_coupled_history.py` | 78 | Pillar 45: coupled history, consciousness–quantum measurement entanglement |
| `tests/test_materials.py` | 75 | Condensed matter, semiconductors, metamaterials |
| `tests/test_information_paradox.py` | 75 | Pillar 36: information paradox, BH interior holography |
| `tests/test_dissipation_geometry.py` | 75 | Pillar 35: dissipation geometry, entropy current, viscosity bound |
| `tests/test_delay_field.py` | 75 | Pillar 41: 5D delay field model (DFM), retarded Green's function |
| `tests/test_black_hole_transceiver.py` | 75 | BH information transceiver, qubit encoding, echo timing, retrieval fidelity |
| `tests/test_quantum_switch.py` | 74 | Theorem XVI: quantum switch, indefinite causal order, 5D lifting |
| `tests/test_non_gaussianity.py` | 73 | Two-field f_NL from dynamical radion, equilateral/squeezed shape |
| `tests/test_fixed_point.py` | 73 | Multiverse network, operators I/H/T, FTUM iteration, α derivation from fixed point, Banach contraction proof |
| `tests/test_branch_catalog.py` | 73 | Multiverse branch catalog, vacuum enumeration, branch-weight distribution |
| `tests/test_marine.py` | 72 | Deep ocean dynamics, marine life, ocean circulation |
| `tests/test_completions.py` | 72 | Completion and endpoint tests |
| `tests/test_adm_engine.py` | 72 | Pillar 53: 5D ADM decomposition engine, Hamiltonian and momentum constraints |
| `tests/test_ecology.py` | 70 | Ecosystems, biodiversity, food web stability |
| `tests/test_dynamical_radion.py` | 67 | Dynamical radion, breathing manifold extension, moduli potential |
| `tests/test_climate.py` | 66 | Atmosphere, carbon cycle, climate feedback |
| `tests/test_compactification.py` | 65 | Pillar 29: compactification, vacuum selection, Theorem XVIII |
| `tests/test_boltzmann_bridge.py` | 65 | Pillar 52-B: CAMB/CLASS Boltzmann bridge, transfer-function cross-validation |
| `tests/test_analytic_benchmark.py` | 64 | Pillar 60: analytic benchmarks, trajectory and rate errors at machine precision |
| `tests/test_uniqueness.py` | 61 | S¹/Z₂ uniqueness scan (8 candidate topologies), ΛCDM no-go comparison, integer quantization discriminant, joint prediction overlap |
| `tests/test_mesh_refinement.py` | 61 | Pillar 59: mesh-refinement convergence study, O(dx²) spatial convergence |
| `tests/test_kk_quantum_info.py` | 59 | Pillar 31: KK quantum information, entanglement entropy, KK-mode decoherence |
| `tests/test_geology.py` | 59 | Plate tectonics, mantle dynamics, mineral formation |
| `tests/test_derivation_module.py` | 59 | Stage 0–3 constraint derivation module |
| `tests/test_derivation.py` | 59 | Key-integer derivations: k_cs=74, n_w_kk=5, n_w_rs=7, k_rc=12, φ_min=18 — all geometry-forced, no free parameters |
| `tests/test_higher_harmonics.py` | 58 | Higher KK harmonic structure, mode coupling, spectral gap |
| `tests/test_geometric_collapse.py` | 58 | Pillar 44: geometric wavefunction collapse, decoherence from 5D curvature |
| `tests/test_particle_geometry.py` | 51 | Particle mass spectrum from KK geometry, fermion hierarchy |
| `tests/test_planetary.py` | 49 | Planetary orbitals, braid scaling laws, (5,7) resonance checks |
| `tests/test_evolution.py` | 49 | RK4 integrator, FieldState, CFL timestep, information current, constraint monitor, radion stabilisation, metric volume preservation |
| `tests/test_boltzmann.py` | 49 | Baryon-loaded CMB transfer (cs²=1/(3(1+R))), baryon-corrected sound horizon r_s★, odd/even peak ratio, D_ℓ accuracy ~10–15% |
| `tests/test_oceanography.py` | 46 | Ocean thermodynamics, salinity stratification, current dynamics |
| `tests/test_realworld_comparison.py` | 45 | Real-world benchmark comparisons, data feeds, external-data adapters |
| `tests/test_meteorology.py` | 45 | Atmospheric dynamics, weather patterns, turbulence |
| `tests/test_field_equation_stress.py` | 45 | Stress tests for Walker-Pearson field equations, extreme-parameter robustness |
| `tests/test_dark_matter_geometry.py` | 45 | DM halo profiles, rotation curve fits, KK graviton contribution |
| `tests/test_boundary_group_theory.py` | 42 | Group-theory representations, manifold-embedding, holographic boundary group structure |
| `tests/test_parallel_validation.py` | 38 | Dual-branch independence, observable decoupling, amplitude closure (COBE), transfer function physics, extreme limits |
| `tests/test_metric.py` | 36 | KK metric assembly, Christoffel symbols, Riemann/Ricci tensors, field strength, α derivation from curvature |
| `tests/test_kk_gauge_spectrum.py` | 36 | KK gauge boson mass spectrum, mode coupling, gauge group emergence |
| `tests/test_prediction_impact.py` | 35 | Real-world prediction impact assessment, falsifiability scoring |
| `tests/test_closure_batch2.py` | 31 | Numerical robustness, cross-module consistency, edge-case coverage |
| `tests/test_observational_resolution.py` | 30 | Angular resolution sufficiency, nₛ/β tolerance, χ² sensitivity, LiteBIRD pol-ratio bounds |
| `tests/test_external_benchmarks.py` | 30 | External / published benchmark validation |
| `tests/test_cosmological_predictions.py` | 28 | Hubble tension (5D radion H_eff), muon g-2 (KK graviton loops), dark matter rotation curves (KK δΦ), GW echoes (compact 5th dimension cavity) |
| `tests/test_quantum_unification.py` | 26 | BH information conservation, canonical commutation relation, Hawking temperature, ER=EPR via shared fixed point |
| `tests/test_e2e_pipeline.py` | 26 | End-to-end chain closure, CS level uniqueness (k=74), α consistency loop, no-free-parameters verification |
| `tests/test_closure_batch1.py` | 25 | α dual-path closure, nₛ KK=Casimir, β coupling chain, holographic entropy emergence |
| `tests/test_safety_imports.py` | 23 | SAFETY/ module smoke tests, import integrity |
| `tests/test_kk_geodesic_reduction.py` | 23 | Lorentz force as geodesic theorem, Γ^μ_{ν5} identity, A_μ = λB_μ derivation |
| `tests/test_arrow_of_time.py` | 23 | Forward entropy growth, backward deficit growth, path independence, entropy production rates |
| `tests/test_im_action.py` | 22 | Irreversibility measure action, boundary terms, entropy current |
| `tests/test_boundary_completions.py` | 22 | Boundary completion structural tests |
| `tests/test_boundary.py` | 21 | Entropy-area law, Bekenstein–Hawking formula, holographic boundary construction and evolution |
| `tests/test_fuzzing.py` | 20 | Edge cases, random inputs, adversarial numerics |
| `tests/test_cmb_landscape.py` | 17 | χ² landscape over (φ₀, n_w), TB/EB ratio cross-checks, amplitude analysis |
| `tests/test_dimensional_reduction.py` | 14 | KK dimensional reduction identities |
| `tests/test_discretization_invariance.py` | 13 | Grid-independence and discretization-invariance checks |
| `tests/test_convergence.py` | 10 | Full-pipeline integration (bulk → boundary → multiverse), FTUM defect decrease |
| `tests/test_precision_audit.py` | 49 | Arbitrary-precision arithmetic audit (mpmath 128/256-bit) |
| `tests/test_richardson_multitime.py` | 11 🐌 | Second-order temporal convergence (Richardson extrapolation) — **slow, run with `pytest -m slow`** |
| **Total (tests/ suite)** | **~13,673** | **~13,586 fast passed · 76 skipped · 11 slow deselected · 0 failures** |

---

## Key Physical Results Verified by Tests

| Observable | Value | Planck 2018 bound | Test class |
|-----------|-------|-------------------|------------|
| Spectral index nₛ | 0.9635 | 0.965 ± 0.004 (1σ) | `TestEffectivePhi0KK`, `TestNsWithCasimir`, `TestTripleConstraint` |
| Tensor-to-scalar r | < 0.036 | < 0.036 (BICEP/Keck 95% CL) | `TestTripleConstraint`, `TestBraidedREffective` |
| Cosmic birefringence β | 0.3513° | 0.35° ± 0.14° (1σ) | `TestCosmicBirefringenceK74` |
| CS level k_cs | 74 = 5² + 7² | — | `TestResonantKcsIdentity`, `TestCsLevelForBirefringence` |
| Braided sound speed c_s | 12/37 ≈ 0.3243 | — | `TestBraidedSoundSpeed` |
| α (derived) | φ₀⁻² | — | `TestExtractAlphaFromCurvature`, `TestDeriveAlphaFromFixedPoint` |
| Holographic bound | S = A/4G | Bekenstein–Hawking | `TestFixedPointIteration`, `TestApplyHolography` |
| LEE isolation | `isolation_confirmed = True` | — | `TestProjectionDegeneracy` |

---

See [RESULTS.md](RESULTS.md) for the complete per-test pass/fail listing.
