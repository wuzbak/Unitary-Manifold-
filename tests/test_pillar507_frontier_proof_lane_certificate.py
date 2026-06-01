# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 507 frontier proof-lane completion certificate."""

from src.core import pillar507_frontier_proof_lane_certificate as p507


def test_constants():
    assert p507.PILLAR_NUMBER == 507
    assert p507.PILLAR_STATUS == "FRONTIER_PROOF_LANES_CERTIFIED"
    assert p507.VERSION == "v15.4"
    assert len(p507.LANE_NAMES) == 7


def test_registry_has_exact_expected_lanes():
    registry = p507.frontier_lane_registry()
    assert sorted(registry) == sorted(p507.LANE_NAMES)
    assert all(lane["lane"] == name for name, lane in registry.items())


def test_five_d_kk_lane_keeps_structural_gap_honest():
    lane = p507.five_d_kk_quantization_lane()
    assert lane["status"] == "ARCHITECTURE_LIMIT_CERTIFIED"
    assert lane["structural_gap_certified"] is True
    assert lane["nonperturbative_full_solution_claimed"] is False
    assert lane["hardgate_score_delta"] == 0.0


def test_p8_lane_proves_lattice_not_full_function_space():
    lane = p507.p8_full_functional_space_lane()
    assert lane["integer_lattice_proved"] is True
    assert lane["canonical_pair"] == {"n_w": 5, "n2": 7}
    assert lane["full_function_space_proved"] is False
    assert lane["status"] == "NAMED_RESIDUAL"


def test_pmns_lane_retains_solar_angle_residual():
    lane = p507.pmns_solar_angle_residual_lane()
    assert lane["status"] == "PMNS_PR_FULL_CHAIN_SYNCHRONIZED"
    assert lane["residual_retained"] is True
    assert lane["target_in_window"] is False
    assert lane["center_residual_deg"] > 0


def test_l2_gamma_external_lane_does_not_claim_missing_receipt():
    lane = p507.l2_gamma_external_confirmation_lane()
    assert lane["status"] == "EXTERNAL_CONFIRMATION_PACKET_READY__HMC_RECEIPT_PENDING"
    assert lane["finite_volume_bound_status"] == "LATTICE_BRAID_PHASE4_NP_CONDENSATE_BOUNDED"
    assert lane["external_hmc_receipt"] is False
    assert lane["hardgate_score_delta"] == 0.0


def test_lean4_manifest_has_local_files_and_build_receipt_gate():
    manifest = p507.lean4_certification_manifest()
    assert manifest["toolchain_present"] is True
    assert manifest["lakefile_present"] is True
    assert manifest["all_expected_files_present"] is True
    assert "lake build" in manifest["completion_criterion"]


def test_quantum_theorem_lanes_are_conjectural_with_criteria():
    lanes = p507.quantum_theorem_lanes()
    assert set(lanes) == {"CCR_OPERATOR_LIMIT", "ER_EPR_KK_HOLOGRAPHY"}
    for lane in lanes.values():
        assert lane["status"] == "CONJECTURAL"
        assert lane["obstruction"]
        assert lane["closure_criterion"]
        assert lane["hardgate_score_delta"] == 0.0


def test_completion_certificate_shape_and_guards():
    cert = p507.completion_certificate()
    assert cert["pillar"] == 507
    assert cert["status"] == p507.PILLAR_STATUS
    assert cert["lane_count"] == 7
    assert cert["all_expected_lanes_present"] is True
    assert cert["all_lanes_have_closure_criteria"] is True
    assert cert["hardgate_score_delta"] == 0.0
    assert "LEAN4_CERTIFICATION" in cert["external_receipt_pending"]
    assert "L2_GAMMA_NP_BRAID_EXTERNAL_CONFIRMATION" in cert["external_receipt_pending"]
    assert "CCR_OPERATOR_LIMIT" in cert["unproved_but_named"]
    assert "ER_EPR_KK_HOLOGRAPHY" in cert["unproved_but_named"]
    assert "not promoted" in cert["claim_guard"]


def test_pillar_report_contains_lanes_and_certificate():
    report = p507.pillar_report()
    assert report["pillar"] == 507
    assert report["status"] == p507.PILLAR_STATUS
    assert sorted(report["lanes"]) == sorted(p507.LANE_NAMES)
    assert report["certificate"]["all_expected_lanes_present"] is True
