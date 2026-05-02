# Full Test Results — Unitary Manifold

Run date: 2026-05-01 | Python 3.12 | pytest | numpy ≥ 1.24 | scipy ≥ 1.11

**Fast suite (default `pytest tests/ -v`): PASSED · 76 SKIPPED ⚑ · 11 DESELECTED · 0 FAILED**
**Slow suite (`pytest tests/ -m slow`): 11 PASSED · 0 FAILED**
**Grand total (all suites): 15,296 passed · 330 skipped · 11 deselected · 0 failures** (tests/ + recycling/ + 5-GOVERNANCE/Unitary Pentad/ + omega/)

**14,641 = 11⁴** — prior structural milestone at v9.25. Not a physical claim.

⚑ **Skip explanation (330 skips):**
- **76 dual-use stubs** (`test_lattice_dynamics.py` + `test_cold_fusion.py`): implementation functions raise `NotImplementedError` to prevent dual-use misuse. See `DUAL_USE_NOTICE.md`.
- **254 Pentad product stubs** (`5-GOVERNANCE/Unitary Pentad/`): deployment functions reserved for AxiomZero product. See `PENTAD_PRODUCT_NOTICE.md`.

**Deselected explanation:** 11 tests in `test_richardson_multitime.py` carry `@pytest.mark.slow`
and are excluded by `addopts = -m "not slow"` in `pytest.ini`. Run with `pytest tests/ -m slow`.

---

## test_boundary.py — 21/21 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestBoundaryArea::test_flat_identity_area` | ✅ PASSED |
| 2 | `TestBoundaryArea::test_non_negative` | ✅ PASSED |
| 3 | `TestBoundaryArea::test_scales_with_metric` | ✅ PASSED |
| 4 | `TestBoundaryArea::test_zero_for_degenerate_metric` | ✅ PASSED |
| 5 | `TestEntropyArea::test_formula` | ✅ PASSED |
| 6 | `TestEntropyArea::test_default_G4_is_one` | ✅ PASSED |
| 7 | `TestEntropyArea::test_non_negative` | ✅ PASSED |
| 8 | `TestBoundaryStateFromBulk::test_h_shape` | ✅ PASSED |
| 9 | `TestBoundaryStateFromBulk::test_J_bdry_shape` | ✅ PASSED |
| 10 | `TestBoundaryStateFromBulk::test_kappa_shape` | ✅ PASSED |
| 11 | `TestBoundaryStateFromBulk::test_h_symmetric` | ✅ PASSED |
| 12 | `TestBoundaryStateFromBulk::test_kappa_non_negative` | ✅ PASSED |
| 13 | `TestBoundaryStateFromBulk::test_all_finite` | ✅ PASSED |
| 14 | `TestBoundaryStateFromBulk::test_h_matches_spatial_block_of_g` | ✅ PASSED |
| 15 | `TestEvolveBoundary::test_h_finite` | ✅ PASSED |
| 16 | `TestEvolveBoundary::test_time_advances` | ✅ PASSED |
| 17 | `TestEvolveBoundary::test_h_stays_symmetric` | ✅ PASSED |
| 18 | `TestEvolveBoundary::test_h_changes_from_initial` | ✅ PASSED |
| 19 | `TestInformationConservationCheck::test_returns_float` | ✅ PASSED |
| 20 | `TestInformationConservationCheck::test_non_negative` | ✅ PASSED |
| 21 | `TestInformationConservationCheck::test_finite` | ✅ PASSED |

---

## test_convergence.py — 10/10 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestFullPipeline::test_bulk_to_boundary_to_multiverse` | ✅ PASSED |
| 2 | `TestFullPipeline::test_boundary_evolve_after_bulk_step` | ✅ PASSED |
| 3 | `TestFTUMConvergence::test_defect_decreases_overall` | ✅ PASSED |
| 4 | `TestFTUMConvergence::test_residual_history_non_empty` | ✅ PASSED |
| 5 | `TestFTUMConvergence::test_fully_connected_also_converges` | ✅ PASSED |
| 6 | `TestEvolutionDiagnostics::test_phi_energy_bounded` | ✅ PASSED |
| 7 | `TestEvolutionDiagnostics::test_ricci_symmetry_preserved_through_step` | ✅ PASSED |
| 8 | `TestEvolutionDiagnostics::test_information_conservation_stays_finite` | ✅ PASSED |
| 9 | `TestBoundaryDiagnostics::test_boundary_entropy_non_negative_after_evolution` | ✅ PASSED |
| 10 | `TestBoundaryDiagnostics::test_kappa_non_negative_after_bulk_step` | ✅ PASSED |

---

## test_derivation.py — 59/59 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestCSLevelDerivation::test_cs_level_planck_match_constant_is_74` | ✅ PASSED |
| 2 | `TestCSLevelDerivation::test_cs_level_planck_match_is_int` | ✅ PASSED |
| 3 | `TestCSLevelDerivation::test_cs_level_for_birefringence_returns_float_near_73p7` | ✅ PASSED |
| 4 | `TestCSLevelDerivation::test_rounding_cs_float_gives_74` | ✅ PASSED |
| 5 | `TestCSLevelDerivation::test_cs_level_float_between_73_and_74` | ✅ PASSED |
| 6 | `TestCSLevelDerivation::test_k74_gives_beta_within_1sigma_planck` | ✅ PASSED |
| 7 | `TestCSLevelDerivation::test_k73_deviation_exceeds_k74_deviation` | ✅ PASSED |
| 8 | `TestCSLevelDerivation::test_k75_deviation_exceeds_k74_deviation` | ✅ PASSED |
| 9 | `TestCSLevelDerivation::test_k74_uniquely_minimises_beta_deviation_over_1_to_100` | ✅ PASSED |
| 10 | `TestCSLevelDerivation::test_cs_coupling_formula_is_k_alpha_over_2pi2_rc` | ✅ PASSED |
| 11 | `TestCSLevelDerivation::test_k74_beta_approximately_0p35_degrees` | ✅ PASSED |
| 12 | `TestCSLevelDerivation::test_k_cs_derivation_inverts_birefringence_formula` | ✅ PASSED |
| 13 | `TestCSLevelDerivation::test_k_cs_is_positive_integer_greater_than_zero` | ✅ PASSED |
| 14 | `TestCSLevelDerivation::test_g_agg_from_k74_is_positive_and_finite` | ✅ PASSED |
| 15 | `TestCSLevelDerivation::test_beta_from_k74_is_positive_radians` | ✅ PASSED |
| 16 | `TestKKWindingNumber::test_n_winding_5_is_default_for_effective_phi0_kk` | ✅ PASSED |
| 17 | `TestKKWindingNumber::test_n_winding_5_gives_phi0_eff_equal_to_10pi` | ✅ PASSED |
| 18 | `TestKKWindingNumber::test_n_winding_5_gives_ns_in_planck_1sigma` | ✅ PASSED |
| 19 | `TestKKWindingNumber::test_n_winding_4_fails_planck_1sigma` | ✅ PASSED |
| 20 | `TestKKWindingNumber::test_n_winding_6_fails_planck_1sigma` | ✅ PASSED |
| 21 | `TestKKWindingNumber::test_only_n_winding_5_passes_planck_1sigma_among_1_to_10` | ✅ PASSED |
| 22 | `TestKKWindingNumber::test_jacobian_kk_for_phi0_1_nw_5_equals_10pi` | ✅ PASSED |
| 23 | `TestKKWindingNumber::test_jacobian_kk_scales_linearly_with_n_winding` | ✅ PASSED |
| 24 | `TestKKWindingNumber::test_n_winding_5_gives_phi0_eff_approximately_31` | ✅ PASSED |
| 25 | `TestKKWindingNumber::test_n_winding_kk_is_positive_integer` | ✅ PASSED |
| 26 | `TestRSWindingNumber::test_n_winding_7_is_default_for_effective_phi0_rs` | ✅ PASSED |
| 27 | `TestRSWindingNumber::test_n_winding_7_gives_phi0_eff_near_31p1` | ✅ PASSED |
| 28 | `TestRSWindingNumber::test_n_winding_7_gives_ns_in_planck_1sigma` | ✅ PASSED |
| 29 | `TestRSWindingNumber::test_n_winding_6_rs_fails_planck_1sigma` | ✅ PASSED |
| 30 | `TestRSWindingNumber::test_n_winding_8_rs_fails_planck_1sigma` | ✅ PASSED |
| 31 | `TestRSWindingNumber::test_only_n_winding_7_passes_planck_1sigma_rs_among_1_to_12` | ✅ PASSED |
| 32 | `TestRSWindingNumber::test_rs_and_kk_winding_numbers_differ` | ✅ PASSED |
| 33 | `TestRSWindingNumber::test_rs_phi0_eff_approximates_7_times_2pi_over_sqrt2` | ✅ PASSED |
| 34 | `TestRSWindingNumber::test_both_branches_give_ns_within_1sigma` | ✅ PASSED |
| 35 | `TestRSWindingNumber::test_both_branches_phi0_eff_within_1_percent_of_each_other` | ✅ PASSED |
| 36 | `TestRSHierarchyProduct::test_k_rc_product_equals_12` | ✅ PASSED |
| 37 | `TestRSHierarchyProduct::test_j_rs_for_k1_rc12_is_near_1_over_sqrt2` | ✅ PASSED |
| 38 | `TestRSHierarchyProduct::test_j_rs_squared_is_near_half` | ✅ PASSED |
| 39 | `TestRSHierarchyProduct::test_j_rs_saturation_exponential_negligible_at_krc12` | ✅ PASSED |
| 40 | `TestRSHierarchyProduct::test_hierarchy_suppression_factor_represents_33_orders_of_magnitude` | ✅ PASSED |
| 41 | `TestRSHierarchyProduct::test_j_rs_stable_for_krc_11_to_15` | ✅ PASSED |
| 42 | `TestRSHierarchyProduct::test_rc_12_with_k_1_gives_integer_krc` | ✅ PASSED |
| 43 | `TestRSHierarchyProduct::test_j_rs_formula_matches_direct_computation` | ✅ PASSED |
| 44 | `TestRSHierarchyProduct::test_phi_min_phys_from_krc12_and_phi_min_bare_18` | ✅ PASSED |
| 45 | `TestRSHierarchyProduct::test_krc_12_is_minimum_integer_achieving_saturation` | ✅ PASSED |
| 46 | `TestGWMinimumInteger::test_phi_min_bare_18_is_positive` | ✅ PASSED |
| 47 | `TestGWMinimumInteger::test_phi_min_phys_is_j_rs_times_18` | ✅ PASSED |
| 48 | `TestGWMinimumInteger::test_delta_phi_from_phi_min_phys_is_positive` | ✅ PASSED |
| 49 | `TestGWMinimumInteger::test_delta_phi_formula_is_phi_min_times_one_minus_one_over_sqrt3` | ✅ PASSED |
| 50 | `TestGWMinimumInteger::test_phi_min_bare_18_closes_to_k_cs_74` | ✅ PASSED |
| 51 | `TestGWMinimumInteger::test_phi_min_bare_exceeds_phi0_bare` | ✅ PASSED |
| 52 | `TestGWMinimumInteger::test_phi_min_phys_approximately_12p7` | ✅ PASSED |
| 53 | `TestDimensionalIntegers::test_total_dimensions_is_5` | ✅ PASSED |
| 54 | `TestDimensionalIntegers::test_kk_jacobian_involves_sqrt_phi0_reflecting_single_extra_dim` | ✅ PASSED |
| 55 | `TestDimensionalIntegers::test_5d_theory_has_exactly_one_extra_dimension` | ✅ PASSED |
| 56 | `TestDimensionalIntegers::test_five_pillars_map_to_five_mathematical_integers` | ✅ PASSED |
| 57 | `TestDimensionalIntegers::test_kk_reduction_factor_is_2pi_per_winding` | ✅ PASSED |
| 58 | `TestDimensionalIntegers::test_4d_observables_determined_by_single_5d_parameter_phi0` | ✅ PASSED |
| 59 | `TestDimensionalIntegers::test_five_dimensional_coupling_reduces_to_4d_fine_structure` | ✅ PASSED |

---

## test_evolution.py — 49/49 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestFieldStateFlat::test_shapes` | ✅ PASSED |
| 2 | `TestFieldStateFlat::test_initial_time_zero` | ✅ PASSED |
| 3 | `TestFieldStateFlat::test_metric_near_minkowski` | ✅ PASSED |
| 4 | `TestFieldStateFlat::test_phi_near_unity` | ✅ PASSED |
| 5 | `TestFieldStateFlat::test_reproducibility` | ✅ PASSED |
| 6 | `TestStep::test_time_advances` | ✅ PASSED |
| 7 | `TestStep::test_output_shapes_unchanged` | ✅ PASSED |
| 8 | `TestStep::test_metric_remains_symmetric` | ✅ PASSED |
| 9 | `TestStep::test_fields_change` | ✅ PASSED |
| 10 | `TestStep::test_phi_finite` | ✅ PASSED |
| 11 | `TestStep::test_g_finite` | ✅ PASSED |
| 12 | `TestRunEvolution::test_history_length` | ✅ PASSED |
| 13 | `TestRunEvolution::test_first_state_is_initial` | ✅ PASSED |
| 14 | `TestRunEvolution::test_times_monotone` | ✅ PASSED |
| 15 | `TestRunEvolution::test_callback_called` | ✅ PASSED |
| 16 | `TestInformationCurrent::test_shape` | ✅ PASSED |
| 17 | `TestInformationCurrent::test_time_component_positive` | ✅ PASSED |
| 18 | `TestInformationCurrent::test_finite` | ✅ PASSED |
| 19 | `TestInformationCurrent::test_zero_phi_gives_zero_current` | ✅ PASSED |
| 20 | `TestConstraintMonitor::test_returns_dict_with_expected_keys` | ✅ PASSED |
| 21 | `TestConstraintMonitor::test_values_are_finite` | ✅ PASSED |
| 22 | `TestConstraintMonitor::test_phi_max_near_one_for_flat` | ✅ PASSED |
| 23 | `TestRK4VsEuler::test_euler_and_rk4_agree_first_order` | ✅ PASSED |
| 24 | `TestRK4VsEuler::test_rk4_metric_symmetric` | ✅ PASSED |
| 25 | `TestRK4VsEuler::test_rk4_all_fields_finite` | ✅ PASSED |
| 26 | `TestRK4VsEuler::test_euler_all_fields_finite` | ✅ PASSED |
| 27 | `TestRK4VsEuler::test_rk4_time_advances` | ✅ PASSED |
| 28 | `TestRK4VsEuler::test_euler_time_advances` | ✅ PASSED |
| 29 | `TestCFLTimestep::test_cfl_positive` | ✅ PASSED |
| 30 | `TestCFLTimestep::test_cfl_finite` | ✅ PASSED |
| 31 | `TestCFLTimestep::test_cfl_scales_with_dx_squared` | ✅ PASSED |
| 32 | `TestCFLTimestep::test_default_test_dt_within_cfl` | ✅ PASSED |
| 33 | `TestEvolutionPhysics::test_r_max_bounded_over_20_steps` | ✅ PASSED |
| 34 | `TestEvolutionPhysics::test_phi_norm_bounded_over_20_steps` | ✅ PASSED |
| 35 | `TestEvolutionPhysics::test_metric_invertible_over_20_steps` | ✅ PASSED |
| 36 | `TestRadionStabilization::test_zero_m_phi_recovers_original_behavior` | ✅ PASSED |
| 37 | `TestRadionStabilization::test_stabilization_restores_phi_toward_background` | ✅ PASSED |
| 38 | `TestRadionStabilization::test_phi0_and_m_phi_carried_through_evolution` | ✅ PASSED |
| 39 | `TestRadionStabilization::test_flat_factory_accepts_phi0_and_m_phi` | ✅ PASSED |
| 40 | `TestMetricVolumePreservation::test_project_enforces_target_det` | ✅ PASSED |
| 41 | `TestMetricVolumePreservation::test_project_preserves_symmetry` | ✅ PASSED |
| 42 | `TestMetricVolumePreservation::test_project_identity_on_exact_minkowski` | ✅ PASSED |
| 43 | `TestMetricVolumePreservation::test_step_det_pinned_after_rk4` | ✅ PASSED |
| 44 | `TestMetricVolumePreservation::test_euler_det_pinned_after_step` | ✅ PASSED |
| 45 | `TestMetricVolumePreservation::test_det_remains_pinned_over_20_steps` | ✅ PASSED |
| 46 | `TestConstraintMonitorDetG::test_no_det_key_without_g` | ✅ PASSED |
| 47 | `TestConstraintMonitorDetG::test_det_key_present_with_g` | ✅ PASSED |
| 48 | `TestConstraintMonitorDetG::test_det_violation_near_zero_for_projected_metric` | ✅ PASSED |
| 49 | `TestConstraintMonitorDetG::test_det_violation_finite` | ✅ PASSED |

---

## test_fiber_bundle.py — 96/96 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestConstants::test_n_w_canonical` | ✅ PASSED |
| 2 | `TestConstants::test_k_cs_canonical` | ✅ PASSED |
| 3 | `TestBuildBundleCatalog::test_catalog_length` | ✅ PASSED |
| 4 | `TestBuildBundleCatalog::test_catalog_names` | ✅ PASSED |
| 5 | `TestBuildBundleCatalog::test_no_duplicate_names` | ✅ PASSED |
| 6 | `TestBuildBundleCatalog::test_all_are_principal_bundle` | ✅ PASSED |
| 7 | `TestBuildBundleCatalog::test_kk_bundle_flag` | ✅ PASSED |
| 8 | `TestBuildBundleCatalog::test_kk_bundle_characteristic_integer_equals_k_cs` | ✅ PASSED |
| 9 | `TestBuildBundleCatalog::test_su2_characteristic_integer_equals_n_w` | ✅ PASSED |
| 10 | `TestBuildBundleCatalog::test_su3_vacuum_sector` | ✅ PASSED |
| 11 | `TestBuildBundleCatalog::test_u1y_unit_charge` | ✅ PASSED |
| 12 | `TestBuildBundleCatalog::test_trivial_zero_integer` | ✅ PASSED |
| 13 | `TestBuildBundleCatalog::test_kk_bundle_structure_group` | ✅ PASSED |
| 14 | `TestBuildBundleCatalog::test_su2_structure_group` | ✅ PASSED |
| 15 | `TestBuildBundleCatalog::test_su3_structure_group` | ✅ PASSED |
| 16 | `TestBuildBundleCatalog::test_trivial_structure_group` | ✅ PASSED |
| 17 | `TestBuildBundleCatalog::test_custom_n_w` | ✅ PASSED |
| 18 | `TestBuildBundleCatalog::test_custom_k_cs` | ✅ PASSED |
| 19 | `TestBuildBundleCatalog::test_rank_values` | ✅ PASSED |
| 20 | `TestBuildBundleCatalog::test_description_nonempty_for_physical_bundles` | ✅ PASSED |
| 21 | `TestComputeCharacteristicClasses::test_trivial_all_zero` | ✅ PASSED |
| 22 | `TestComputeCharacteristicClasses::test_u1_c1_equals_n` | ✅ PASSED |
| 23 | `TestComputeCharacteristicClasses::test_u1_c2_is_none` | ✅ PASSED |
| 24 | `TestComputeCharacteristicClasses::test_u1_p1_is_c1_squared` | ✅ PASSED |
| 25 | `TestComputeCharacteristicClasses::test_su2_c1_is_none` | ✅ PASSED |
| 26 | `TestComputeCharacteristicClasses::test_su2_c2_equals_n` | ✅ PASSED |
| 27 | `TestComputeCharacteristicClasses::test_su2_p1_is_minus_2_c2` | ✅ PASSED |
| 28 | `TestComputeCharacteristicClasses::test_su3_c2_equals_n` | ✅ PASSED |
| 29 | `TestComputeCharacteristicClasses::test_su3_p1_vacuum` | ✅ PASSED |
| 30 | `TestComputeCharacteristicClasses::test_su3_nonzero_instanton` | ✅ PASSED |
| 31 | `TestComputeCharacteristicClasses::test_u1_unit_charge` | ✅ PASSED |
| 32 | `TestComputeCharacteristicClasses::test_returns_characteristic_classes_instance` | ✅ PASSED |
| 33 | `TestComputeCharacteristicClasses::test_kk_bundle_p1` | ✅ PASSED |
| 34 | `TestComputeCharacteristicClasses::test_euler_class_none_for_all` | ✅ PASSED |
| 35 | `TestClassifyBundle::test_kk_bundle_passes_all` | ✅ PASSED |
| 36 | `TestClassifyBundle::test_su2_bundle_passes_all` | ✅ PASSED |
| 37 | `TestClassifyBundle::test_su3_passes_all` | ✅ PASSED |
| 38 | `TestClassifyBundle::test_u1y_passes_all` | ✅ PASSED |
| 39 | `TestClassifyBundle::test_trivial_fails` | ✅ PASSED |
| 40 | `TestClassifyBundle::test_trivial_fail_reasons_nonempty` | ✅ PASSED |
| 41 | `TestClassifyBundle::test_kk_topological_type` | ✅ PASSED |
| 42 | `TestClassifyBundle::test_su2_topological_type` | ✅ PASSED |
| 43 | `TestClassifyBundle::test_trivial_topological_type` | ✅ PASSED |
| 44 | `TestClassifyBundle::test_u1y_topological_type` | ✅ PASSED |
| 45 | `TestClassifyBundle::test_unit_instanton_type` | ✅ PASSED |
| 46 | `TestClassifyBundle::test_anti_instanton_type` | ✅ PASSED |
| 47 | `TestClassifyBundle::test_kk_consistency_fail_wrong_c1` | ✅ PASSED |
| 48 | `TestClassifyBundle::test_kk_consistency_pass` | ✅ PASSED |
| 49 | `TestClassifyBundle::test_su2_index_fail_wrong_c2` | ✅ PASSED |
| 50 | `TestClassifyBundle::test_su2_index_pass` | ✅ PASSED |
| 51 | `TestClassifyBundle::test_returns_bundle_classification_instance` | ✅ PASSED |
| 52 | `TestClassifyBundle::test_characteristic_classes_embedded` | ✅ PASSED |
| 53 | `TestClassifyBundle::test_non_kk_u1_kk_consistency_not_applicable` | ✅ PASSED |
| 54 | `TestClassifyBundle::test_su3_index_not_applicable` | ✅ PASSED |
| 55 | `TestGlobalAnomalyCancellation::test_canonical_values_cancel` | ✅ PASSED |
| 56 | `TestGlobalAnomalyCancellation::test_gs_condition_74_plus_1_divisible_by_5` | ✅ PASSED |
| 57 | `TestGlobalAnomalyCancellation::test_wrong_k_cs_fails` | ✅ PASSED |
| 58 | `TestGlobalAnomalyCancellation::test_wrong_k_cs_correct_mod` | ✅ PASSED |
| 59 | `TestGlobalAnomalyCancellation::test_explanation_is_string` | ✅ PASSED |
| 60 | `TestGlobalAnomalyCancellation::test_missing_bundle_returns_false` | ✅ PASSED |
| 61 | `TestBundleTopologyScan::test_returns_bundle_scan_result` | ✅ PASSED |
| 62 | `TestBundleTopologyScan::test_canonical_scan_globally_consistent` | ✅ PASSED |
| 63 | `TestBundleTopologyScan::test_n_w_recorded` | ✅ PASSED |
| 64 | `TestBundleTopologyScan::test_k_cs_recorded` | ✅ PASSED |
| 65 | `TestBundleTopologyScan::test_all_integer_quantized` | ✅ PASSED |
| 66 | `TestBundleTopologyScan::test_kk_bundle_consistent` | ✅ PASSED |
| 67 | `TestBundleTopologyScan::test_su2_bundle_consistent` | ✅ PASSED |
| 68 | `TestBundleTopologyScan::test_global_anomaly_cancelled` | ✅ PASSED |
| 69 | `TestBundleTopologyScan::test_classifications_dict_has_five_entries` | ✅ PASSED |
| 70 | `TestBundleTopologyScan::test_classifications_contains_all_names` | ✅ PASSED |
| 71 | `TestBundleTopologyScan::test_summary_is_nonempty_string` | ✅ PASSED |
| 72 | `TestBundleTopologyScan::test_wrong_k_cs_fails_global` | ✅ PASSED |
| 73 | `TestBundleTopologyScan::test_wrong_n_w_fails_global` | ✅ PASSED |
| 74 | `TestBundleTopologyScan::test_trivial_bundle_fails_in_scan` | ✅ PASSED |
| 75 | `TestBundleTopologyScan::test_kk_bundle_passes_in_scan` | ✅ PASSED |
| 76 | `TestBundleTopologyScan::test_su2_passes_in_scan` | ✅ PASSED |
| 77 | `TestBundleTopologyScan::test_u1y_passes_in_scan` | ✅ PASSED |
| 78 | `TestCompareBundleTopologies::test_same_bundle_equivalent` | ✅ PASSED |
| 79 | `TestCompareBundleTopologies::test_kk_and_u1y_inequivalent` | ✅ PASSED |
| 80 | `TestCompareBundleTopologies::test_kk_and_u1y_same_group` | ✅ PASSED |
| 81 | `TestCompareBundleTopologies::test_kk_and_u1y_different_c1` | ✅ PASSED |
| 82 | `TestCompareBundleTopologies::test_kk_and_su2_different_group` | ✅ PASSED |
| 83 | `TestCompareBundleTopologies::test_distinguishing_invariant_is_c1_for_u1_bundles` | ✅ PASSED |
| 84 | `TestCompareBundleTopologies::test_distinguishing_invariant_is_c2_for_su_bundles` | ✅ PASSED |
| 85 | `TestCompareBundleTopologies::test_trivial_vs_nontrivial` | ✅ PASSED |
| 86 | `TestCompareBundleTopologies::test_returns_dict` | ✅ PASSED |
| 87 | `TestCompareBundleTopologies::test_all_five_bundles_pairwise_distinct_except_trivial_su3` | ✅ PASSED |
| 88 | `TestIntegration::test_canonical_kk_c1` | ✅ PASSED |
| 89 | `TestIntegration::test_canonical_su2_c2` | ✅ PASSED |
| 90 | `TestIntegration::test_canonical_kk_p1` | ✅ PASSED |
| 91 | `TestIntegration::test_canonical_su2_p1` | ✅ PASSED |
| 92 | `TestIntegration::test_exactly_four_physical_bundles_pass_all` | ✅ PASSED |
| 93 | `TestIntegration::test_summary_contains_table_header` | ✅ PASSED |
| 94 | `TestIntegration::test_summary_contains_pass_indicator` | ✅ PASSED |
| 95 | `TestIntegration::test_gs_condition_uniquely_selects_k_cs_74_among_1_to_100` | ✅ PASSED |
| 96 | `TestIntegration::test_anomaly_condition_encodes_k_cs` | ✅ PASSED |

---

## test_fixed_point.py — 35/35 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestMultiverseNode::test_state_vector_shape` | ✅ PASSED |
| 2 | `TestMultiverseNode::test_state_vector_values` | ✅ PASSED |
| 3 | `TestMultiverseNode::test_norm_positive` | ✅ PASSED |
| 4 | `TestMultiverseNetwork::test_chain_adjacency` | ✅ PASSED |
| 5 | `TestMultiverseNetwork::test_fully_connected_adjacency` | ✅ PASSED |
| 6 | `TestMultiverseNetwork::test_global_state_shape` | ✅ PASSED |
| 7 | `TestApplyIrreversibility::test_exact_dS_formula` | ✅ PASSED |
| 8 | `TestApplyIrreversibility::test_no_drift_at_fixed_point` | ✅ PASSED |
| 9 | `TestApplyIrreversibility::test_S_increases_when_below_bound` | ✅ PASSED |
| 10 | `TestApplyIrreversibility::test_S_decreases_when_above_bound` | ✅ PASSED |
| 11 | `TestApplyIrreversibility::test_other_fields_unchanged` | ✅ PASSED |
| 12 | `TestApplyHolography::test_clamps_S_above_bound` | ✅ PASSED |
| 13 | `TestApplyHolography::test_does_not_raise_S_below_bound` | ✅ PASSED |
| 14 | `TestApplyHolography::test_at_exactly_bound` | ✅ PASSED |
| 15 | `TestApplyHolography::test_G4_scaling` | ✅ PASSED |
| 16 | `TestApplyTopology::test_gradient_flow_formula` | ✅ PASSED |
| 17 | `TestApplyTopology::test_isolated_node_no_change` | ✅ PASSED |
| 18 | `TestUeumAcceleration::test_shape` | ✅ PASSED |
| 19 | `TestUeumAcceleration::test_finite` | ✅ PASSED |
| 20 | `TestUeumAcceleration::test_zero_X_no_divergence` | ✅ PASSED |
| 21 | `TestFixedPointIteration::test_return_types` | ✅ PASSED |
| 22 | `TestFixedPointIteration::test_converges_on_chain` | ✅ PASSED |
| 23 | `TestFixedPointIteration::test_final_defect_below_tol` | ✅ PASSED |
| 24 | `TestFixedPointIteration::test_residuals_non_negative` | ✅ PASSED |
| 25 | `TestFixedPointIteration::test_per_node_entropy_at_bound` | ✅ PASSED |
| 26 | `TestDeriveAlphaFromFixedPoint::test_unit_phi_gives_alpha_one` | ✅ PASSED |
| 27 | `TestDeriveAlphaFromFixedPoint::test_phi_two_gives_alpha_quarter` | ✅ PASSED |
| 28 | `TestDeriveAlphaFromFixedPoint::test_phi_half_gives_alpha_four` | ✅ PASSED |
| 29 | `TestDeriveAlphaFromFixedPoint::test_array_phi_uses_spatial_mean` | ✅ PASSED |
| 30 | `TestDeriveAlphaFromFixedPoint::test_alpha_positive_for_any_phi` | ✅ PASSED |
| 31 | `TestDeriveAlphaFromFixedPoint::test_alpha_decreases_with_larger_phi` | ✅ PASSED |
| 32 | `TestDeriveAlphaFromFixedPoint::test_with_network_runs_fixed_point_iteration` | ✅ PASSED |
| 33 | `TestDeriveAlphaFromFixedPoint::test_with_network_result_is_converged` | ✅ PASSED |
| 34 | `TestDeriveAlphaFromFixedPoint::test_none_network_returns_none` | ✅ PASSED |
| 35 | `TestDeriveAlphaFromFixedPoint::test_return_types` | ✅ PASSED |

---

## test_inflation.py — 271/271 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestGWPotential::test_zero_at_minimum` | ✅ PASSED |
| 2 | `TestGWPotential::test_non_negative` | ✅ PASSED |
| 3 | `TestGWPotential::test_lambda_scaling` | ✅ PASSED |
| 4 | `TestGWPotential::test_array_input` | ✅ PASSED |
| 5 | `TestGWPotentialDerivs::test_at_minimum_V_zero` | ✅ PASSED |
| 6 | `TestGWPotentialDerivs::test_inflection_point_d2V_zero` | ✅ PASSED |
| 7 | `TestGWPotentialDerivs::test_finite_at_phi_zero` | ✅ PASSED |
| 8 | `TestGWPotentialDerivs::test_consistency_with_gw_potential` | ✅ PASSED |
| 9 | `TestSlowRollParams::test_inflection_point_eta_zero` | ✅ PASSED |
| 10 | `TestSlowRollParams::test_epsilon_non_negative` | ✅ PASSED |
| 11 | `TestSlowRollParams::test_raises_on_non_positive_V` | ✅ PASSED |
| 12 | `TestSlowRollParams::test_scale_invariant_limit` | ✅ PASSED |
| 13 | `TestCMBObservables::test_spectral_index_formula` | ✅ PASSED |
| 14 | `TestCMBObservables::test_tensor_ratio` | ✅ PASSED |
| 15 | `TestCMBObservables::test_tensor_tilt` | ✅ PASSED |
| 16 | `TestCMBObservables::test_consistency_relation` | ✅ PASSED |
| 17 | `TestNsFromPhi0::test_returns_finite_tuple` | ✅ PASSED |
| 18 | `TestNsFromPhi0::test_ns_lambda_independent` | ✅ PASSED |
| 19 | `TestNsFromPhi0::test_ns_phi0_dependence` | ✅ PASSED |
| 20 | `TestNsFromPhi0::test_custom_phi_star` | ✅ PASSED |
| 21 | `TestPlanck2018Check::test_central_value_passes_1sigma` | ✅ PASSED |
| 22 | `TestPlanck2018Check::test_value_at_1sigma_boundary` | ✅ PASSED |
| 23 | `TestPlanck2018Check::test_outside_1sigma_fails` | ✅ PASSED |
| 24 | `TestPlanck2018Check::test_outside_1sigma_passes_2sigma` | ✅ PASSED |
| 25 | `TestPlanck2018Check::test_far_value_fails_both` | ✅ PASSED |
| 26 | `TestPrimordialPowerSpectrum::test_scale_invariant` | ✅ PASSED |
| 27 | `TestPrimordialPowerSpectrum::test_tilt_direction_red` | ✅ PASSED |
| 28 | `TestPrimordialPowerSpectrum::test_tilt_direction_blue` | ✅ PASSED |
| 29 | `TestPrimordialPowerSpectrum::test_at_pivot` | ✅ PASSED |
| 30 | `TestCMBSourceFunction::test_small_k_limit` | ✅ PASSED |
| 31 | `TestCMBSourceFunction::test_silk_damping_large_k` | ✅ PASSED |
| 32 | `TestCMBSourceFunction::test_acoustic_oscillations` | ✅ PASSED |
| 33 | `TestCMBSourceFunction::test_output_shape` | ✅ PASSED |
| 34 | `TestAngularPowerSpectrum::test_returns_positive_values` | ✅ PASSED |
| 35 | `TestAngularPowerSpectrum::test_returns_finite_values` | ✅ PASSED |
| 36 | `TestAngularPowerSpectrum::test_output_shape` | ✅ PASSED |
| 37 | `TestAngularPowerSpectrum::test_red_tilt_suppresses_high_ell` | ✅ PASSED |
| 38 | `TestDlFromCl::test_zero_ell_zero` | ✅ PASSED |
| 39 | `TestDlFromCl::test_positive_for_positive_Cl` | ✅ PASSED |
| 40 | `TestDlFromCl::test_T_cmb_scaling` | ✅ PASSED |
| 41 | `TestDlFromCl::test_order_of_magnitude` | ✅ PASSED |
| 42 | `TestChi2Planck::test_perfect_match_zero_chi2` | ✅ PASSED |
| 43 | `TestChi2Planck::test_one_sigma_deviation_contributes_one` | ✅ PASSED |
| 44 | `TestChi2Planck::test_no_overlap_raises` | ✅ PASSED |
| 45 | `TestChi2Planck::test_partial_overlap` | ✅ PASSED |
| 46 | `TestChi2Planck::test_n_dof_counts_matched` | ✅ PASSED |
| 47 | `TestJacobian5d4d::test_formula_n1` | ✅ PASSED |
| 48 | `TestJacobian5d4d::test_formula_n5_phi1` | ✅ PASSED |
| 49 | `TestJacobian5d4d::test_scales_with_sqrt_phi0` | ✅ PASSED |
| 50 | `TestJacobian5d4d::test_scales_linearly_with_n_winding` | ✅ PASSED |
| 51 | `TestJacobian5d4d::test_raises_on_non_positive_phi0` | ✅ PASSED |
| 52 | `TestJacobian5d4d::test_raises_on_zero_winding` | ✅ PASSED |
| 53 | `TestEffectivePhi0KK::test_n5_recovers_planck_ns` | ✅ PASSED |
| 54 | `TestEffectivePhi0KK::test_n5_phi_eff_approx_31` | ✅ PASSED |
| 55 | `TestEffectivePhi0KK::test_bare_phi0_fails_planck` | ✅ PASSED |
| 56 | `TestEffectivePhi0KK::test_larger_n_increases_phi_eff` | ✅ PASSED |
| 57 | `TestEffectivePhi0KK::test_phi_eff_scales_with_phi0_bare` | ✅ PASSED |
| 58 | `TestCasimirPotential::test_positive_for_positive_A_c` | ✅ PASSED |
| 59 | `TestCasimirPotential::test_phi4_scaling` | ✅ PASSED |
| 60 | `TestCasimirPotential::test_A_c_scaling` | ✅ PASSED |
| 61 | `TestCasimirPotential::test_array_input` | ✅ PASSED |
| 62 | `TestCasimirEffectivePotentialDerivs::test_reduces_to_gw_at_zero_A_c` | ✅ PASSED |
| 63 | `TestCasimirEffectivePotentialDerivs::test_casimir_increases_V` | ✅ PASSED |
| 64 | `TestCasimirEffectivePotentialDerivs::test_casimir_makes_dV_more_negative_at_small_phi` | ✅ PASSED |
| 65 | `TestCasimirEffectivePotentialDerivs::test_d2V_casimir_positive_correction` | ✅ PASSED |
| 66 | `TestCasimirAcFromPhiMin::test_round_trip_minimum` | ✅ PASSED |
| 67 | `TestCasimirAcFromPhiMin::test_positive_A_c` | ✅ PASSED |
| 68 | `TestCasimirAcFromPhiMin::test_raises_when_phi_min_le_phi0` | ✅ PASSED |
| 69 | `TestCasimirAcFromPhiMin::test_scales_as_phi_min_8_for_large_phi_min` | ✅ PASSED |
| 70 | `TestNsWithCasimir::test_casimir_at_kk_minimum_is_near_scale_invariant` | ✅ PASSED |
| 71 | `TestNsWithCasimir::test_jacobian_minimum_gives_planck_ns` | ✅ PASSED |
| 72 | `TestNsWithCasimir::test_returns_four_finite_values` | ✅ PASSED |
| 73 | `TestNsWithCasimir::test_larger_phi_min_increases_ns` | ✅ PASSED |
| 74 | `TestNsWithCasimir::test_casimir_dramatically_improves_over_bare_ftum` | ✅ PASSED |
| 75 | `TestJacobianRSOrbifold::test_formula` | ✅ PASSED |
| 76 | `TestJacobianRSOrbifold::test_saturates_at_large_krc` | ✅ PASSED |
| 77 | `TestJacobianRSOrbifold::test_saturation_independent_of_krc_above_10` | ✅ PASSED |
| 78 | `TestJacobianRSOrbifold::test_smaller_krc_gives_smaller_J` | ✅ PASSED |
| 79 | `TestJacobianRSOrbifold::test_larger_k_gives_smaller_J` | ✅ PASSED |
| 80 | `TestJacobianRSOrbifold::test_raises_on_non_positive_k` | ✅ PASSED |
| 81 | `TestJacobianRSOrbifold::test_raises_on_non_positive_rc` | ✅ PASSED |
| 82 | `TestEffectivePhi0RS::test_n7_k1_recovers_planck_ns` | ✅ PASSED |
| 83 | `TestEffectivePhi0RS::test_phi_eff_approx_31` | ✅ PASSED |
| 84 | `TestEffectivePhi0RS::test_bare_phi0_fails_planck` | ✅ PASSED |
| 85 | `TestNsStabilityRS::test_ns_stability_across_krc` | ✅ PASSED |
| 86 | `TestNsStabilityRS::test_tensor_to_scalar_stable_across_krc` | ✅ PASSED |
| 87 | `TestNsStabilityRS::test_ns_stable_means_planck_across_krc` | ✅ PASSED |
| 88 | `TestCsAxionPhotonCoupling::test_formula` | ✅ PASSED |
| 89 | `TestCsAxionPhotonCoupling::test_linear_in_k_cs` | ✅ PASSED |
| 90 | `TestCsAxionPhotonCoupling::test_positive` | ✅ PASSED |
| 91 | `TestCsAxionPhotonCoupling::test_raises_on_bad_k_cs` | ✅ PASSED |
| 92 | `TestCsAxionPhotonCoupling::test_raises_on_bad_alpha` | ✅ PASSED |
| 93 | `TestCsAxionPhotonCoupling::test_raises_on_bad_rc` | ✅ PASSED |
| 94 | `TestFieldDisplacementGW::test_formula` | ✅ PASSED |
| 95 | `TestFieldDisplacementGW::test_positive` | ✅ PASSED |
| 96 | `TestFieldDisplacementGW::test_raises_on_non_positive` | ✅ PASSED |
| 97 | `TestFieldDisplacementGW::test_reference_value` | ✅ PASSED |
| 98 | `TestBirefringenceAngle::test_formula` | ✅ PASSED |
| 99 | `TestBirefringenceAngle::test_takes_absolute_value` | ✅ PASSED |
| 100 | `TestBirefringenceAngle::test_zero_for_zero_delta_phi` | ✅ PASSED |
| 101 | `TestCsLevelForBirefringence::test_matches_planck_constant` | ✅ PASSED |
| 102 | `TestCsLevelForBirefringence::test_round_trip` | ✅ PASSED |
| 103 | `TestCsLevelForBirefringence::test_scales_linearly_with_beta` | ✅ PASSED |
| 104 | `TestCosmicBirefringenceK74::test_k_cs_74_gives_target_birefringence` | ✅ PASSED |
| 105 | `TestCosmicBirefringenceK74::test_birefringence_within_1sigma` | ✅ PASSED |
| 106 | `TestCosmicBirefringenceK74::test_birefringence_stable_across_krc` | ✅ PASSED |
| 107 | `TestCosmicBirefringenceK74::test_topological_consistency` | ✅ PASSED |
| 108 | `TestTripleConstraint::test_returns_all_keys` | ✅ PASSED |
| 109 | `TestTripleConstraint::test_ns_passes_planck` | ✅ PASSED |
| 110 | `TestTripleConstraint::test_beta_matches_target` | ✅ PASSED |
| 111 | `TestTripleConstraint::test_r_positive_and_finite` | ✅ PASSED |
| 112 | `TestEESourceFunction::test_small_k_limit` | ✅ PASSED |
| 113 | `TestEESourceFunction::test_silk_damping_large_k` | ✅ PASSED |
| 114 | `TestEESourceFunction::test_amplitude_factor` | ✅ PASSED |
| 115 | `TestEESourceFunction::test_output_shape` | ✅ PASSED |
| 116 | `TestEESourceFunction::test_phase_orthogonal_to_temperature` | ✅ PASSED |
| 117 | `TestTESourceFunction::test_equals_product_of_t_and_e` | ✅ PASSED |
| 118 | `TestTESourceFunction::test_small_k_limit` | ✅ PASSED |
| 119 | `TestTESourceFunction::test_silk_damping_large_k` | ✅ PASSED |
| 120 | `TestTESourceFunction::test_can_be_negative` | ✅ PASSED |
| 121 | `TestTESourceFunction::test_output_shape` | ✅ PASSED |
| 122 | `TestBirefringenceAngleFreq::test_achromatic_returns_beta0_at_any_nu` | ✅ PASSED |
| 123 | `TestBirefringenceAngleFreq::test_achromatic_ratio_is_one` | ✅ PASSED |
| 124 | `TestBirefringenceAngleFreq::test_dispersive_at_ref_freq_equals_beta0` | ✅ PASSED |
| 125 | `TestBirefringenceAngleFreq::test_dispersive_scales_as_nu_minus2` | ✅ PASSED |
| 126 | `TestBirefringenceAngleFreq::test_dispersive_ratio_not_one` | ✅ PASSED |
| 127 | `TestTBEBSpectrum::test_output_shape_tb` | ✅ PASSED |
| 128 | `TestTBEBSpectrum::test_output_shape_eb` | ✅ PASSED |
| 129 | `TestTBEBSpectrum::test_c_te_shape` | ✅ PASSED |
| 130 | `TestTBEBSpectrum::test_c_ee_positive` | ✅ PASSED |
| 131 | `TestTBEBSpectrum::test_finite_values` | ✅ PASSED |
| 132 | `TestTBEBSpectrum::test_lcdm_limit_tb_zero` | ✅ PASSED |
| 133 | `TestTBEBSpectrum::test_lcdm_limit_eb_zero` | ✅ PASSED |
| 134 | `TestTBEBSpectrum::test_model_tb_nonzero` | ✅ PASSED |
| 135 | `TestTBEBSpectrum::test_model_eb_nonzero` | ✅ PASSED |
| 136 | `TestTBEBSpectrum::test_tb_proportional_to_c_te` | ✅ PASSED |
| 137 | `TestTBEBSpectrum::test_eb_proportional_to_c_ee` | ✅ PASSED |
| 138 | `TestTBEBSpectrum::test_achromaticity_ratio_is_one` | ✅ PASSED |
| 139 | `TestTBEBSpectrum::test_achromaticity_ratio_eb_is_one` | ✅ PASSED |
| 140 | `TestTBEBSpectrum::test_faraday_ratio_not_one` | ✅ PASSED |
| 141 | `TestTBEBSpectrum::test_achromaticity_invariant_across_all_nu_pairs` | ✅ PASSED |
| 142 | `TestSlowRollAmplitude::test_returns_required_keys` | ✅ PASSED |
| 143 | `TestSlowRollAmplitude::test_As_positive` | ✅ PASSED |
| 144 | `TestSlowRollAmplitude::test_H_inf_positive` | ✅ PASSED |
| 145 | `TestSlowRollAmplitude::test_As_equals_standard_slow_roll_formula` | ✅ PASSED |
| 146 | `TestSlowRollAmplitude::test_As_scales_linearly_with_lambda` | ✅ PASSED |
| 147 | `TestSlowRollAmplitude::test_phi_star_default_is_phi0_over_sqrt3` | ✅ PASSED |
| 148 | `TestSlowRollAmplitude::test_explicit_phi_star_respected` | ✅ PASSED |
| 149 | `TestSlowRollAmplitude::test_lam1_As_is_large_compared_to_planck_value` | ✅ PASSED |
| 150 | `TestSlowRollAmplitude::test_epsilon_small_for_valid_slow_roll` | ✅ PASSED |
| 151 | `TestSlowRollAmplitude::test_eta_near_zero_at_inflection_point` | ✅ PASSED |
| 152 | `TestCOBENormalization::test_returns_required_keys` | ✅ PASSED |
| 153 | `TestCOBENormalization::test_As_predicted_matches_target` | ✅ PASSED |
| 154 | `TestCOBENormalization::test_lam_cobe_positive_and_small` | ✅ PASSED |
| 155 | `TestCOBENormalization::test_ns_within_planck_1sigma` | ✅ PASSED |
| 156 | `TestCOBENormalization::test_r_within_planck_bound` | ✅ PASSED |
| 157 | `TestCOBENormalization::test_E_inf_in_GUT_range` | ✅ PASSED |
| 158 | `TestCOBENormalization::test_lam_independent_observables_listed` | ✅ PASSED |
| 159 | `TestCOBENormalization::test_custom_As_target` | ✅ PASSED |
| 160 | `TestCOBENormalization::test_h_inf_positive` | ✅ PASSED |
| 161 | `TestCOBENormalization::test_phi0_eff_matches_effective_phi0_kk` | ✅ PASSED |
| 162 | `TestClassifyAttractorRegime::test_flat_s1_ftum_at_reference` | ✅ PASSED |
| 163 | `TestClassifyAttractorRegime::test_flat_s1_ftum_within_band` | ✅ PASSED |
| 164 | `TestClassifyAttractorRegime::test_flat_s1_outside_band_is_off_attractor` | ✅ PASSED |
| 165 | `TestClassifyAttractorRegime::test_rs1_saturated_at_kr_c_12` | ✅ PASSED |
| 166 | `TestClassifyAttractorRegime::test_rs1_saturated_at_kr_c_15` | ✅ PASSED |
| 167 | `TestClassifyAttractorRegime::test_rs1_with_n_winding_5_is_off_attractor` | ✅ PASSED |
| 168 | `TestClassifyAttractorRegime::test_wrong_n_winding_is_off_attractor` | ✅ PASSED |
| 169 | `TestClassifyAttractorRegime::test_rs1_unsaturated_is_off_attractor` | ✅ PASSED |
| 170 | `TestClassifyAttractorRegime::test_returns_string` | ✅ PASSED |
| 171 | `TestAmplitudeAttractor::test_returns_required_keys` | ✅ PASSED |
| 172 | `TestAmplitudeAttractor::test_lam_independent_ns` | ✅ PASSED |
| 173 | `TestAmplitudeAttractor::test_As_scales_linearly_with_lam` | ✅ PASSED |
| 174 | `TestAmplitudeAttractor::test_unified_ns_attractor` | ✅ PASSED |
| 175 | `TestAmplitudeAttractor::test_attractor_set_contains_both_branches` | ✅ PASSED |
| 176 | `TestAmplitudeAttractor::test_all_attractor_set_in_2sigma` | ✅ PASSED |
| 177 | `TestAmplitudeAttractor::test_ns_attractor_spread_tight` | ✅ PASSED |
| 178 | `TestAmplitudeAttractor::test_phi0eff_spread_within_two_percent` | ✅ PASSED |
| 179 | `TestAmplitudeAttractor::test_majority_attractor_set_within_1sigma` | ✅ PASSED |
| 180 | `TestAmplitudeAttractor::test_all_attractor_set_within_2sigma` | ✅ PASSED |
| 181 | `TestAmplitudeAttractor::test_ns_ref_within_planck_1sigma` | ✅ PASSED |
| 182 | `TestAmplitudeAttractor::test_As_increases_with_lam` | ✅ PASSED |
| 183 | `TestAmplitudeAttractor::test_attractor_set_records_have_required_keys` | ✅ PASSED |
| 184 | `TestScaleDependence::test_returns_required_keys` | ✅ PASSED |
| 185 | `TestScaleDependence::test_ns_within_1sigma_planck` | ✅ PASSED |
| 186 | `TestScaleDependence::test_r_within_planck_bound` | ✅ PASSED |
| 187 | `TestScaleDependence::test_r_consistency_relation` | ✅ PASSED |
| 188 | `TestScaleDependence::test_alpha_s_within_planck_bound` | ✅ PASSED |
| 189 | `TestScaleDependence::test_gap_is_normalization` | ✅ PASSED |
| 190 | `TestScaleDependence::test_nt_negative` | ✅ PASSED |
| 191 | `TestScaleDependence::test_ns_planck_echo` | ✅ PASSED |
| 192 | `TestFoliationClock::test_returns_required_keys` | ✅ PASSED |
| 193 | `TestFoliationClock::test_N_efolds_in_canonical_window` | ✅ PASSED |
| 194 | `TestFoliationClock::test_slow_roll_valid_at_phi_star` | ✅ PASSED |
| 195 | `TestFoliationClock::test_foliations_consistent` | ✅ PASSED |
| 196 | `TestFoliationClock::test_entropy_clock_correction_small` | ✅ PASSED |
| 197 | `TestFoliationClock::test_phi_star_default_is_phi0_over_sqrt3` | ✅ PASSED |
| 198 | `TestFoliationClock::test_N_efolds_positive` | ✅ PASSED |
| 199 | `TestAmplitudeGapReport::test_returns_required_keys` | ✅ PASSED |
| 200 | `TestAmplitudeGapReport::test_gap_factor_equals_lambda_cobe` | ✅ PASSED |
| 201 | `TestAmplitudeGapReport::test_gap_factor_positive` | ✅ PASSED |
| 202 | `TestAmplitudeGapReport::test_gap_summary_is_string` | ✅ PASSED |
| 203 | `TestAmplitudeGapReport::test_fully_determined` | ✅ PASSED |
| 204 | `TestAmplitudeGapReport::test_slow_roll_sub_dict_correct` | ✅ PASSED |
| 205 | `TestAmplitudeGapReport::test_sub_dicts_internally_consistent` | ✅ PASSED |
| 206 | `TestAmplitudeGapReport::test_gap_summary_contains_key_numbers` | ✅ PASSED |
| 207 | `TestFTUMAttractorDomain::test_returns_required_keys` | ✅ PASSED |
| 208 | `TestFTUMAttractorDomain::test_flat_branch_keys` | ✅ PASSED |
| 209 | `TestFTUMAttractorDomain::test_rs1_branch_keys` | ✅ PASSED |
| 210 | `TestFTUMAttractorDomain::test_excluded_phase_keys` | ✅ PASSED |
| 211 | `TestFTUMAttractorDomain::test_flat_branch_ns_within_planck_1sigma` | ✅ PASSED |
| 212 | `TestFTUMAttractorDomain::test_rs1_branch_ns_within_planck_1sigma` | ✅ PASSED |
| 213 | `TestFTUMAttractorDomain::test_excluded_phase_outside_planck_1sigma` | ✅ PASSED |
| 214 | `TestFTUMAttractorDomain::test_both_branches_consistent` | ✅ PASSED |
| 215 | `TestFTUMAttractorDomain::test_branches_agree_in_phi0eff_within_2pct` | ✅ PASSED |
| 216 | `TestFTUMAttractorDomain::test_phi0_band_symmetric_around_ref` | ✅ PASSED |
| 217 | `TestFTUMAttractorDomain::test_flat_branch_phi0_eff_near_pi5` | ✅ PASSED |
| 218 | `TestFTUMAttractorDomain::test_rs1_branch_jacobian_near_saturation` | ✅ PASSED |
| 219 | `TestFTUMAttractorDomain::test_excluded_phase_phi0eff_below_25` | ✅ PASSED |
| 220 | `TestFTUMAttractorDomain::test_ftum_condition_is_string` | ✅ PASSED |
| 221 | `TestFTUMAttractorDomain::test_degeneracy_is_close` | ✅ PASSED |
| 222 | `TestRS1PhaseScan::test_returns_required_keys` | ✅ PASSED |
| 223 | `TestRS1PhaseScan::test_j_rs_saturates_by_kr_c_5` | ✅ PASSED |
| 224 | `TestRS1PhaseScan::test_j_rs_saturated_value_correct` | ✅ PASSED |
| 225 | `TestRS1PhaseScan::test_j_rs_monotone_increasing` | ✅ PASSED |
| 226 | `TestRS1PhaseScan::test_natural_branch_all_within_planck_2sigma` | ✅ PASSED |
| 227 | `TestRS1PhaseScan::test_mixed_phase_all_outside_planck_1sigma` | ✅ PASSED |
| 228 | `TestRS1PhaseScan::test_natural_branch_ns_spread_tiny_post_saturation` | ✅ PASSED |
| 229 | `TestRS1PhaseScan::test_mixed_phase_ns_lower_than_natural` | ✅ PASSED |
| 230 | `TestRS1PhaseScan::test_phase_labels_are_strings` | ✅ PASSED |
| 231 | `TestRS1PhaseScan::test_custom_r_c_values` | ✅ PASSED |
| 232 | `TestRS1PhaseScan::test_natural_ns_in_planck_window_at_saturation` | ✅ PASSED |
| 233 | `TestBirefringenceTransferFunction::test_coherent_model_all_ones` | ✅ PASSED |
| 234 | `TestBirefringenceTransferFunction::test_coherent_shape` | ✅ PASSED |
| 235 | `TestBirefringenceTransferFunction::test_gaussian_ul_axion_limit` | ✅ PASSED |
| 236 | `TestBirefringenceTransferFunction::test_gaussian_qcd_axion_limit` | ✅ PASSED |
| 237 | `TestBirefringenceTransferFunction::test_gaussian_monotonically_decreasing_in_ell` | ✅ PASSED |
| 238 | `TestBirefringenceTransferFunction::test_gaussian_values_in_unit_interval` | ✅ PASSED |
| 239 | `TestBirefringenceTransferFunction::test_invalid_model_raises` | ✅ PASSED |
| 240 | `TestPropagatePrimordialAmplitude::test_coherent_t_eff_is_one` | ✅ PASSED |
| 241 | `TestPropagatePrimordialAmplitude::test_coherent_required_equals_observed` | ✅ PASSED |
| 242 | `TestPropagatePrimordialAmplitude::test_coherent_no_extra_amplitude_needed` | ✅ PASSED |
| 243 | `TestPropagatePrimordialAmplitude::test_suppressed_requires_more_primordial_amplitude` | ✅ PASSED |
| 244 | `TestPropagatePrimordialAmplitude::test_c_ee_weighted_mean_correct` | ✅ PASSED |
| 245 | `TestTBEBWithTransfer::test_none_matches_explicit_ones` | ✅ PASSED |
| 246 | `TestTBEBWithTransfer::test_default_transfer_ell_is_ones_in_output` | ✅ PASSED |
| 247 | `TestTBEBWithTransfer::test_half_transfer_halves_signal` | ✅ PASSED |
| 248 | `TestTBEBWithTransfer::test_wrong_shape_raises` | ✅ PASSED |
| 249 | `TestBMuRotationAngle::test_consistent_with_birefringence_angle` | ✅ PASSED |
| 250 | `TestBMuRotationAngle::test_is_linear_flag_always_true` | ✅ PASSED |
| 251 | `TestBMuRotationAngle::test_linearity_double_b_mu_doubles_alpha` | ✅ PASSED |
| 252 | `TestBMuRotationAngle::test_coupling_factor_formula` | ✅ PASSED |
| 253 | `TestBMuRotationAngle::test_quadratic_subdominant_for_model_beta` | ✅ PASSED |
| 254 | `TestBMuRotationAngle::test_alpha_zero_for_zero_b_mu` | ✅ PASSED |
| 255 | `TestQuadraticCorrectionBound::test_zero_alpha_exact_prefactor_is_one` | ✅ PASSED |
| 256 | `TestQuadraticCorrectionBound::test_model_beta_is_subdominant` | ✅ PASSED |
| 257 | `TestQuadraticCorrectionBound::test_analytic_approximation_accuracy` | ✅ PASSED |
| 258 | `TestQuadraticCorrectionBound::test_exact_prefactor_less_than_one_for_nonzero_alpha` | ✅ PASSED |
| 259 | `TestBMuKineticRunning::test_default_gamma_zero_returns_one` | ✅ PASSED |
| 260 | `TestBMuKineticRunning::test_power_law_scaling` | ✅ PASSED |
| 261 | `TestBMuKineticRunning::test_perturbative_estimate_is_small` | ✅ PASSED |
| 262 | `TestVerifyDualJacobianPaths::test_both_branches_pass_attractor` | ✅ PASSED |
| 263 | `TestVerifyDualJacobianPaths::test_jacobians_differ` | ✅ PASSED |
| 264 | `TestVerifyDualJacobianPaths::test_dual_path_confirmed` | ✅ PASSED |
| 265 | `TestVerifyDualJacobianPaths::test_regime_labels_correct` | ✅ PASSED |
| 266 | `TestVerifyDualJacobianPaths::test_ns_delta_within_one_sigma` | ✅ PASSED |
| 267 | `TestRS1JacobianTrace::test_warp_factor_is_negligible_at_krc12` | ✅ PASSED |
| 268 | `TestRS1JacobianTrace::test_jacobian_fully_saturated` | ✅ PASSED |
| 269 | `TestRS1JacobianTrace::test_delta_is_geometric` | ✅ PASSED |
| 270 | `TestRS1JacobianTrace::test_delta_value_is_minus_one_percent` | ✅ PASSED |
| 271 | `TestRS1JacobianTrace::test_phi0_eff_values_match_existing_functions` | ✅ PASSED |

---

## test_metric.py — 30/30 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestFieldStrength::test_shape` | ✅ PASSED |
| 2 | `TestFieldStrength::test_zero_on_constant_B` | ✅ PASSED |
| 3 | `TestFieldStrength::test_antisymmetry` | ✅ PASSED |
| 4 | `TestFieldStrength::test_diagonal_zero` | ✅ PASSED |
| 5 | `TestAssemble5dMetric::test_shape` | ✅ PASSED |
| 6 | `TestAssemble5dMetric::test_radion_G55_equals_phi_squared` | ✅ PASSED |
| 7 | `TestAssemble5dMetric::test_off_diagonal_G_mu5` | ✅ PASSED |
| 8 | `TestAssemble5dMetric::test_4x4_block` | ✅ PASSED |
| 9 | `TestAssemble5dMetric::test_symmetry` | ✅ PASSED |
| 10 | `TestAssemble5dMetric::test_lam_coupling` | ✅ PASSED |
| 11 | `TestChristoffel::test_shape_4d` | ✅ PASSED |
| 12 | `TestChristoffel::test_shape_5d` | ✅ PASSED |
| 13 | `TestChristoffel::test_vanishes_on_flat_4d` | ✅ PASSED |
| 14 | `TestChristoffel::test_symmetry_lower_indices` | ✅ PASSED |
| 15 | `TestComputeCurvature::test_output_shapes` | ✅ PASSED |
| 16 | `TestComputeCurvature::test_ricci_scalar_near_zero_on_flat` | ✅ PASSED |
| 17 | `TestComputeCurvature::test_ricci_symmetry` | ✅ PASSED |
| 18 | `TestComputeCurvature::test_all_finite` | ✅ PASSED |
| 19 | `TestComputeCurvature::test_5d_pipeline_differs_from_naive_4d` | ✅ PASSED |
| 20 | `TestExtractAlphaFromCurvature::test_output_types` | ✅ PASSED |
| 21 | `TestExtractAlphaFromCurvature::test_alpha_equals_one_for_unit_phi` | ✅ PASSED |
| 22 | `TestExtractAlphaFromCurvature::test_alpha_quarters_when_phi_doubles` | ✅ PASSED |
| 23 | `TestExtractAlphaFromCurvature::test_alpha_general_uniform_phi` | ✅ PASSED |
| 24 | `TestExtractAlphaFromCurvature::test_alpha_spatial_mean_for_varying_phi` | ✅ PASSED |
| 25 | `TestExtractAlphaFromCurvature::test_cross_block_shape` | ✅ PASSED |
| 26 | `TestExtractAlphaFromCurvature::test_cross_block_finite` | ✅ PASSED |
| 27 | `TestExtractAlphaFromCurvature::test_cross_block_zero_on_flat_background` | ✅ PASSED |
| 28 | `TestExtractAlphaFromCurvature::test_cross_block_nonzero_with_B` | ✅ PASSED |
| 29 | `TestExtractAlphaFromCurvature::test_alpha_positive` | ✅ PASSED |
| 30 | `TestExtractAlphaFromCurvature::test_lam_does_not_affect_alpha` | ✅ PASSED |

---

## test_arrow_of_time.py — 22/23 PASSED · 1 SKIPPED ⚑

| # | Test | Result |
|---|------|--------|
| 1 | `TestForwardEntropyGrowth::test_below_bound_entropy_increases` | ✅ PASSED |
| 2 | `TestForwardEntropyGrowth::test_above_bound_entropy_decreases` | ✅ PASSED |
| 3 | `TestForwardEntropyGrowth::test_at_bound_no_change` | ✅ PASSED |
| 4 | `TestForwardEntropyGrowth::test_deficit_decreases_from_below` | ✅ PASSED |
| 5 | `TestForwardEntropyGrowth::test_deficit_decreases_from_above` | ✅ PASSED |
| 6 | `TestForwardEntropyGrowth::test_multiple_steps_converge_to_bound` | ✅ PASSED |
| 7 | `TestForwardEntropyGrowth::test_kappa_scales_convergence_rate` | ✅ PASSED |
| 8 | `TestForwardEntropyGrowth::test_area_unchanged_by_irreversibility` | ✅ PASSED |
| 9 | `TestBackwardDeficitGrowth::test_backward_below_bound_entropy_decreases` | ✅ PASSED |
| 10 | `TestBackwardDeficitGrowth::test_backward_above_bound_entropy_increases` | ✅ PASSED |
| 11 | `TestBackwardDeficitGrowth::test_backward_deficit_grows_from_below` | ✅ PASSED |
| 12 | `TestBackwardDeficitGrowth::test_forward_backward_not_symmetric` | ✅ PASSED |
| 13 | `TestBackwardDeficitGrowth::test_arrow_of_time_sign` | ✅ PASSED |
| 14 | `TestPathIndependence::test_converges_from_below_bound` | ✅ PASSED |
| 15 | `TestPathIndependence::test_converges_from_above_bound` | ✅ PASSED |
| 16 | `TestPathIndependence::test_same_fixed_point_from_below_and_above` | ✅ PASSED |
| 17 | `TestPathIndependence::test_entropy_monotone_increasing_from_below` | ✅ PASSED |
| 18 | `TestPathIndependence::test_different_initial_x_same_convergence` | ✅ PASSED |
| 19 | `TestEntropyProductionRate::test_positive_production_rate_single_step` | ✅ PASSED |
| 20 | `TestEntropyProductionRate::test_production_rate_proportional_to_deficit` | ✅ PASSED |
| 21 | `TestEntropyProductionRate::test_defect_history_mostly_decreasing` | ⚑ SKIPPED |
| 22 | `TestEntropyProductionRate::test_total_entropy_increase_over_run` | ✅ PASSED |
| 23 | `TestEntropyProductionRate::test_entropy_rate_zero_at_fixed_point` | ✅ PASSED |

⚑ Guard skip: `pytest.skip("Insufficient residual history to test monotonicity")` fires when `fixed_point_iteration` converges in < 2 steps. Immediate convergence = correct behaviour, not an error.

---

## test_cmb_landscape.py — 17/17 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestChi2LandscapeShape::test_returns_correct_shape` | ✅ PASSED |
| 2 | `TestChi2LandscapeShape::test_all_finite` | ✅ PASSED |
| 3 | `TestChi2LandscapeShape::test_all_positive` | ✅ PASSED |
| 4 | `TestChi2LandscapeShape::test_landscape_varies_with_params` | ✅ PASSED |
| 5 | `TestChi2MinimumAtCanonicalParameters::test_minimum_is_finite` | ✅ PASSED |
| 6 | `TestChi2MinimumAtCanonicalParameters::test_canonical_chi2_is_positive` | ✅ PASSED |
| 7 | `TestChi2MinimumAtCanonicalParameters::test_ns_shift_increases_chi2` | ✅ PASSED |
| 8 | `TestChi2MinimumAtCanonicalParameters::test_landscape_minimum_phi0_in_range` | ✅ PASSED |
| 9 | `TestChi2MinimumAtCanonicalParameters::test_landscape_minimum_nw_in_range` | ✅ PASSED |
| 10 | `TestChi2MinimumAtCanonicalParameters::test_relative_delta_chi2_positive` | ✅ PASSED |
| 11 | `TestChi2ExtractObservables::test_returns_expected_keys` | ✅ PASSED |
| 12 | `TestChi2ExtractObservables::test_ns_finite` | ✅ PASSED |
| 13 | `TestChi2ExtractObservables::test_r_positive` | ✅ PASSED |
| 14 | `TestChi2ExtractObservables::test_chi2_positive` | ✅ PASSED |
| 15 | `TestChi2ExtractObservables::test_dl_array_shape` | ✅ PASSED |
| 16 | `TestChi2ExtractObservables::test_dl_finite` | ✅ PASSED |
| 17 | `TestTBEBRatioCrossCheck::test_lcdm_has_zero_tb_at_any_beta0_input_of_zero` | ✅ PASSED |

---

## test_e2e_pipeline.py — 26/26 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestChainClosure::test_phi0_eff_approximately_31` | ✅ PASSED |
| 2 | `TestChainClosure::test_ns_passes_planck_1sigma` | ✅ PASSED |
| 3 | `TestChainClosure::test_r_is_positive_and_finite` | ✅ PASSED |
| 4 | `TestChainClosure::test_beta_within_1sigma_planck` | ✅ PASSED |
| 5 | `TestChainClosure::test_all_three_observables_simultaneously` | ✅ PASSED |
| 6 | `TestChainClosure::test_chain_deterministic` | ✅ PASSED |
| 7 | `TestChainClosure::test_rs_orbifold_chain_also_passes` | ✅ PASSED |
| 8 | `TestUniquenessOfCSLevel::test_k74_minimises_beta_deviation` | ✅ PASSED |
| 9 | `TestUniquenessOfCSLevel::test_k74_is_unique_minimiser` | ✅ PASSED |
| 10 | `TestUniquenessOfCSLevel::test_k74_within_1sigma` | ✅ PASSED |
| 11 | `TestUniquenessOfCSLevel::test_k73_further_than_k74` | ✅ PASSED |
| 12 | `TestUniquenessOfCSLevel::test_k75_further_than_k74` | ✅ PASSED |
| 13 | `TestUniquenessOfCSLevel::test_beta_monotone_in_k` | ✅ PASSED |
| 14 | `TestUniquenessOfCSLevel::test_k74_beta_matches_target_to_2dp` | ✅ PASSED |
| 15 | `TestAlphaConsistencyLoop::test_alpha_from_phi0_is_unity` | ✅ PASSED |
| 16 | `TestAlphaConsistencyLoop::test_g5_round_trip` | ✅ PASSED |
| 17 | `TestAlphaConsistencyLoop::test_birefringence_via_g5_route` | ✅ PASSED |
| 18 | `TestAlphaConsistencyLoop::test_birefringence_direct_vs_g5_route_agree` | ✅ PASSED |
| 19 | `TestAlphaConsistencyLoop::test_cs_level_inverts_back_to_74` | ✅ PASSED |
| 20 | `TestNoFreeParameters::test_ns_uniquely_determined` | ✅ PASSED |
| 21 | `TestNoFreeParameters::test_r_uniquely_determined` | ✅ PASSED |
| 22 | `TestNoFreeParameters::test_beta_uniquely_determined` | ✅ PASSED |
| 23 | `TestNoFreeParameters::test_alpha_pinned_by_phi0` | ✅ PASSED |
| 24 | `TestNoFreeParameters::test_all_four_observables_finite` | ✅ PASSED |
| 25 | `TestNoFreeParameters::test_changing_n_winding_breaks_planck` | ✅ PASSED |
| 26 | `TestNoFreeParameters::test_changing_n_winding_6_breaks_planck` | ✅ PASSED |

---

## test_observational_resolution.py — 30/30 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestAngularResolutionSufficiency::test_spectra_finite_for_each_ell_max` | ✅ PASSED |
| 2 | `TestAngularResolutionSufficiency::test_spectra_nonnegative_on_average` | ✅ PASSED |
| 3 | `TestAngularResolutionSufficiency::test_chi2_finite_for_each_ell_max` | ✅ PASSED |
| 4 | `TestAngularResolutionSufficiency::test_ns_prediction_stable_across_ell_max` | ✅ PASSED |
| 5 | `TestAngularResolutionSufficiency::test_chi2_increases_monotonically_with_ell_max` | ✅ PASSED |
| 6 | `TestAngularResolutionSufficiency::test_ell_max_2500_spectra_at_high_ell` | ✅ PASSED |
| 7 | `TestNsTolerance::test_ns_within_planck_sigma_ns` | ✅ PASSED |
| 8 | `TestNsTolerance::test_planck_sigma_ns_is_at_most_twice_planck_ns_sigma` | ✅ PASSED |
| 9 | `TestNsTolerance::test_ns_shift_by_sigma_changes_chi2_by_at_least_chi2_tol` | ✅ PASSED |
| 10 | `TestNsTolerance::test_chi2_sensitive_to_ns_near_central` | ✅ PASSED |
| 11 | `TestNsTolerance::test_ns_model_within_1sigma_of_planck` | ✅ PASSED |
| 12 | `TestNsTolerance::test_ns_2sigma_below_central_outside_1sigma` | ✅ PASSED |
| 13 | `TestBetaTolerance::test_beta_within_planck_sigma_beta` | ✅ PASSED |
| 14 | `TestBetaTolerance::test_planck_sigma_beta_matches_birefringence_sigma_deg` | ✅ PASSED |
| 15 | `TestBetaTolerance::test_beta_shift_changes_ctb_by_detectable_fraction` | ✅ PASSED |
| 16 | `TestBetaTolerance::test_beta_1sigma_above_target_still_nonzero` | ✅ PASSED |
| 17 | `TestBetaTolerance::test_beta_1sigma_below_target_still_nonzero` | ✅ PASSED |
| 18 | `TestBetaTolerance::test_beta_model_matches_k74_geometry` | ✅ PASSED |
| 19 | `TestPolarizationRatioTolerance::test_achromatic_ctb_ratio_within_pol_ratio_tol` | ✅ PASSED |
| 20 | `TestPolarizationRatioTolerance::test_achromatic_ceb_ratio_within_pol_ratio_tol` | ✅ PASSED |
| 21 | `TestPolarizationRatioTolerance::test_dispersive_ratio_far_exceeds_pol_ratio_tol` | ✅ PASSED |
| 22 | `TestPolarizationRatioTolerance::test_achromatic_vs_faraday_ratio_differ_by_more_than_pol_tol` | ✅ PASSED |
| 23 | `TestPolarizationRatioTolerance::test_pol_ratio_tol_is_tight_enough_for_litebird` | ✅ PASSED |
| 24 | `TestChi2Sensitivity::test_1sigma_ns_shift_increases_chi2_dof_by_at_least_chi2_tol` | ✅ PASSED |
| 25 | `TestChi2Sensitivity::test_1sigma_ns_shift_downward_increases_chi2_dof` | ✅ PASSED |
| 26 | `TestChi2Sensitivity::test_2sigma_shift_larger_delta_than_1sigma` | ✅ PASSED |
| 27 | `TestChi2Sensitivity::test_chi2_finite_and_nonnegative_at_model` | ✅ PASSED |
| 28 | `TestChi2Sensitivity::test_model_chi2_dof_is_large_and_amplitude_driven` | ✅ PASSED |
| 29 | `TestChi2Sensitivity::test_chi2_tol_equals_spec_value` | ✅ PASSED |
| 30 | `TestChi2Sensitivity::test_perfect_match_gives_chi2_zero` | ✅ PASSED |

---

## test_parallel_validation.py — 38/38 PASSED

| # | Test | Result |
|---|------|--------|
| 1 | `TestDualBranchIndependence::test_flat_phi0_eff_positive` | ✅ PASSED |
| 2 | `TestDualBranchIndependence::test_rs1_phi0_eff_positive` | ✅ PASSED |
| 3 | `TestDualBranchIndependence::test_flat_branch_passes_attractor` | ✅ PASSED |
| 4 | `TestDualBranchIndependence::test_rs1_branch_passes_attractor` | ✅ PASSED |
| 5 | `TestDualBranchIndependence::test_jacobians_differ_by_large_factor` | ✅ PASSED |
| 6 | `TestDualBranchIndependence::test_paths_differ_flag` | ✅ PASSED |
| 7 | `TestDualBranchIndependence::test_dual_path_confirmed` | ✅ PASSED |
| 8 | `TestDualBranchIndependence::test_phi0eff_spread_matches_analytic_formula` | ✅ PASSED |
| 9 | `TestDualBranchIndependence::test_rs1_jacobian_is_saturated` | ✅ PASSED |
| 10 | `TestDualBranchIndependence::test_excluded_phase_is_excluded` | ✅ PASSED |
| 11 | `TestObservableDecoupling::test_ns_constant_across_lambda_scan` | ✅ PASSED |
| 12 | `TestObservableDecoupling::test_r_constant_across_lambda_scan` | ✅ PASSED |
| 13 | `TestObservableDecoupling::test_As_does_change_with_lambda` | ✅ PASSED |
| 14 | `TestObservableDecoupling::test_ns_within_planck_1sigma` | ✅ PASSED |
| 15 | `TestObservableDecoupling::test_r_within_planck_bound` | ✅ PASSED |
| 16 | `TestObservableDecoupling::test_alpha_s_within_bound` | ✅ PASSED |
| 17 | `TestObservableDecoupling::test_gap_is_normalization_only` | ✅ PASSED |
| 18 | `TestAmplitudeClosure::test_lam_cobe_is_finite_and_positive` | ✅ PASSED |
| 19 | `TestAmplitudeClosure::test_lam_cobe_order_of_magnitude` | ✅ PASSED |
| 20 | `TestAmplitudeClosure::test_as_predicted_matches_planck` | ✅ PASSED |
| 21 | `TestAmplitudeClosure::test_inflation_energy_scale_is_gut_scale` | ✅ PASSED |
| 22 | `TestAmplitudeClosure::test_ns_unchanged_by_normalisation` | ✅ PASSED |
| 23 | `TestAmplitudeClosure::test_lam_independent_observables_listed` | ✅ PASSED |
| 24 | `TestTransferFunctionPhysics::test_b_mu_angle_is_linear_in_b_mu_rms` | ✅ PASSED |
| 25 | `TestTransferFunctionPhysics::test_b_mu_angle_consistent_with_birefringence_angle` | ✅ PASSED |
| 26 | `TestTransferFunctionPhysics::test_quadratic_correction_is_subdominant` | ✅ PASSED |
| 27 | `TestTransferFunctionPhysics::test_transfer_coherent_model_is_unity` | ✅ PASSED |
| 28 | `TestTransferFunctionPhysics::test_transfer_gaussian_ul_axion_limit` | ✅ PASSED |
| 29 | `TestTransferFunctionPhysics::test_transfer_gaussian_suppresses_high_ell` | ✅ PASSED |
| 30 | `TestTransferFunctionPhysics::test_propagate_coherent_needs_no_extra_amplitude` | ✅ PASSED |
| 31 | `TestExtremeLimits::test_transfer_near_infinite_coherence` | ✅ PASSED |
| 32 | `TestExtremeLimits::test_transfer_zero_coherence` | ✅ PASSED |
| 33 | `TestExtremeLimits::test_transfer_values_always_in_unit_interval` | ✅ PASSED |
| 34 | `TestExtremeLimits::test_rotation_angle_zero_for_zero_coupling` | ✅ PASSED |
| 35 | `TestExtremeLimits::test_rotation_angle_zero_for_zero_displacement` | ✅ PASSED |
| 36 | `TestExtremeLimits::test_quadratic_bound_at_zero_alpha` | ✅ PASSED |
| 37 | `TestExtremeLimits::test_jacobian_rs_positive_for_positive_inputs` | ✅ PASSED |
| 38 | `TestExtremeLimits::test_ns_from_phi0_finite_at_low_multipoles` | ✅ PASSED |

---

## Summary

| File | Passed | Skipped | Failed | Total |
|------|-------:|--------:|-------:|------:|
| `test_boundary.py` | 21 | 0 | 0 | 21 |
| `test_convergence.py` | 10 | 0 | 0 | 10 |
| `test_evolution.py` | 49 | 0 | 0 | 49 |
| `test_fiber_bundle.py` | 96 | 0 | 0 | 96 |
| `test_fixed_point.py` | 50 | 0 | 0 | 50 |
| `test_inflation.py` | 271 | 0 | 0 | 271 |
| `test_derivation.py` | 59 | 0 | 0 | 59 |
| `test_metric.py` | 36 | 0 | 0 | 36 |
| `test_closure_batch1.py` | 25 | 0 | 0 | 25 |
| `test_closure_batch2.py` | 31 | 0 | 0 | 31 |
| `test_fuzzing.py` | 20 | 0 | 0 | 20 |
| `test_dimensional_reduction.py` | 14 | 0 | 0 | 14 |
| `test_discretization_invariance.py` | 13 | 0 | 0 | 13 |
| `test_arrow_of_time.py` | 22 | 1 ⚑ | 0 | 23 |
| `test_cmb_landscape.py` | 17 | 0 | 0 | 17 |
| `test_e2e_pipeline.py` | 26 | 0 | 0 | 26 |
| `test_observational_resolution.py` | 30 | 0 | 0 | 30 |
| `test_parallel_validation.py` | 38 | 0 | 0 | 38 |
| `test_quantum_unification.py` | 26 | 0 | 0 | 26 |
| `test_derivation_module.py` | 59 | 0 | 0 | 59 |
| `test_external_benchmarks.py` | 30 | 0 | 0 | 30 |
| `test_completions.py` | 72 | 0 | 0 | 72 |
| `test_uniqueness.py` | 61 | 0 | 0 | 61 |
| `test_boltzmann.py` | 49 | 0 | 0 | 49 |
| `test_cosmological_predictions.py` | 28 | 0 | 0 | 28 |
| `test_richardson_multitime.py` 🐌 | 11 | 0 | 0 | 11 |
| **Total** | **1281** | **1** ⚑ | **0** | **1293** |

⚑ Guard skip: `TestEntropyProductionRate::test_defect_history_mostly_decreasing` — see header note.
