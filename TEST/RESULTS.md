# Full Test Results — Unitary Manifold

Run date: 2026-04-11 | Python 3.12.3 | pytest 9.0.3 | numpy ≥ 1.24 | scipy ≥ 1.11

**Result: 256 PASSED / 0 FAILED / 0 ERRORS**

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

## test_inflation.py — 111/111 PASSED

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

## Summary

| File | Passed | Failed | Total |
|------|-------:|-------:|------:|
| `test_boundary.py` | 21 | 0 | 21 |
| `test_convergence.py` | 10 | 0 | 10 |
| `test_evolution.py` | 49 | 0 | 49 |
| `test_fixed_point.py` | 35 | 0 | 35 |
| `test_inflation.py` | 111 | 0 | 111 |
| `test_metric.py` | 30 | 0 | 30 |
| **Total** | **256** | **0** | **256** |
