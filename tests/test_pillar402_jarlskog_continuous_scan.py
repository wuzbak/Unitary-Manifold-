# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar402_jarlskog_continuous_scan.py
================================================
Tests for Pillar 402 -- Jarlskog Continuous Scan and Sub-leading Correction Ansatz.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar402_jarlskog_continuous_scan import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    N_W,
    K_CS,
    PI_KR,
    LATTICE_STEP,
    LATTICE_SUPPRESSION,
    J_PDG,
    SIN_DELTA_PDG,
    DELTA_PDG_DEGREES,
    LAMBDA_CABIBBO,
    SIN_THETA23_PDG,
    DELTA_ELL_12_TARGET,
    DELTA_ELL_23_TARGET,
    DELTA_ELL_13_TARGET,
    DELTA_KT_REQUIRED,
    N_FN_REQUIRED,
    continuous_mixing_angle,
    jarlskog_continuous,
    continuous_jarlskog_scan,
    find_exact_continuous_target,
    nlo_lkt_correction_ansatz,
    fn_charge_mapping,
    admission_7_mapped_verdict,
    pillar402_summary,
)


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 402

    def test_pillar_status(self):
        assert PILLAR_STATUS == "ARCHITECTURE_LIMIT_MAPPED"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_lattice_step(self):
        assert LATTICE_STEP == pytest.approx(5.0 / 74.0, rel=1e-10)

    def test_lattice_suppression(self):
        assert LATTICE_SUPPRESSION == pytest.approx(math.exp(-2.5), rel=1e-9)

    def test_j_pdg_order(self):
        assert 2e-5 < J_PDG < 4e-5

    def test_lambda_cabibbo(self):
        assert LAMBDA_CABIBBO == pytest.approx(0.225, rel=1e-3)

    def test_sin_theta23_pdg(self):
        assert 0.03 < SIN_THETA23_PDG < 0.06

    def test_sin_delta_pdg_range(self):
        assert 0.85 < SIN_DELTA_PDG < 1.0

    def test_delta_ell_12_target_positive(self):
        assert DELTA_ELL_12_TARGET > 0.0

    def test_delta_ell_23_target_positive(self):
        assert DELTA_ELL_23_TARGET > 0.0

    def test_delta_ell_13_target_sum(self):
        assert DELTA_ELL_13_TARGET == pytest.approx(
            DELTA_ELL_12_TARGET + DELTA_ELL_23_TARGET, rel=1e-9
        )

    def test_delta_kt_required_natural(self):
        # Should be < 10% for sub-leading naturalness
        assert DELTA_KT_REQUIRED < 0.10

    def test_delta_kt_required_nonzero(self):
        assert DELTA_KT_REQUIRED > 0.0

    def test_n_fn_required_positive(self):
        assert N_FN_REQUIRED > 0.0

    def test_n_fn_equals_target(self):
        assert N_FN_REQUIRED == pytest.approx(DELTA_ELL_12_TARGET, rel=1e-9)


class TestContinuousMixingAngle:
    def test_zero_step(self):
        assert continuous_mixing_angle(0.0) == pytest.approx(1.0, rel=1e-10)

    def test_positive_step_suppression(self):
        result = continuous_mixing_angle(1.0)
        assert 0.0 < result < 1.0

    def test_lattice_integer_step(self):
        result = continuous_mixing_angle(1.0)
        expected = math.exp(-LATTICE_STEP * PI_KR)
        assert result == pytest.approx(expected, rel=1e-9)

    def test_negative_step_abs(self):
        assert continuous_mixing_angle(-1.0) == pytest.approx(continuous_mixing_angle(1.0), rel=1e-9)

    def test_monotone_decreasing(self):
        assert continuous_mixing_angle(1.0) > continuous_mixing_angle(2.0)
        assert continuous_mixing_angle(2.0) > continuous_mixing_angle(3.0)

    def test_large_step_near_zero(self):
        result = continuous_mixing_angle(10.0)
        assert result < 1e-10


class TestJarlskogContinuous:
    def test_returns_dict(self):
        r = jarlskog_continuous(1.0, 0.5)
        assert isinstance(r, dict)

    def test_at_target_within_1pct(self):
        r = jarlskog_continuous(DELTA_ELL_12_TARGET, DELTA_ELL_23_TARGET)
        assert r["within_1pct"], f"Residual: {r['residual_pct']:.3f}%"

    def test_at_target_j_approx_pdg(self):
        r = jarlskog_continuous(DELTA_ELL_12_TARGET, DELTA_ELL_23_TARGET)
        assert r["j"] == pytest.approx(J_PDG, rel=0.01)

    def test_integer_assignment_not_within_1pct(self):
        # Integer assignment (1, 1) is the NEAREST point -- should have significant residual
        r = jarlskog_continuous(1.0, 1.0)
        assert not r["within_1pct"]

    def test_j_positive(self):
        r = jarlskog_continuous(0.5, 1.0)
        assert r["j"] > 0.0

    def test_negative_step_raises(self):
        with pytest.raises(ValueError):
            jarlskog_continuous(-0.1, 1.0)

    def test_negative_dl23_raises(self):
        with pytest.raises(ValueError):
            jarlskog_continuous(1.0, -0.1)

    def test_residual_computation(self):
        r = jarlskog_continuous(0.5, 1.0)
        expected_residual = abs(r["j"] - J_PDG) / J_PDG * 100.0
        assert r["residual_pct"] == pytest.approx(expected_residual, rel=1e-6)

    def test_within_flags_consistent(self):
        r = jarlskog_continuous(0.5, 1.0)
        if r["within_1pct"]:
            assert r["within_5pct"]
            assert r["within_15pct"]
        if r["within_5pct"]:
            assert r["within_15pct"]

    def test_j_pdg_in_result(self):
        r = jarlskog_continuous(0.5, 1.0)
        assert r["j_pdg"] == pytest.approx(J_PDG, rel=1e-9)

    def test_triangle_relation(self):
        r = jarlskog_continuous(1.0, 0.5)
        assert r["delta_ell_13"] == pytest.approx(1.5, rel=1e-9)

    def test_s13_from_triangle(self):
        r = jarlskog_continuous(1.0, 0.5)
        expected_s13 = continuous_mixing_angle(1.5)
        assert r["s13"] == pytest.approx(expected_s13, rel=1e-9)


class TestContinuousJarlskogScan:
    def test_returns_dict(self):
        r = continuous_jarlskog_scan(scan_max=1.0, step=0.1)
        assert isinstance(r, dict)

    def test_solution_exists_at_fine_scan(self):
        r = continuous_jarlskog_scan(scan_max=3.0, step=0.05)
        assert r["solution_exists"], f"Best residual: {r['best_residual_pct']:.3f}%"

    def test_best_residual_under_5pct(self):
        r = continuous_jarlskog_scan(scan_max=3.0, step=0.05)
        assert r["best_residual_pct"] < 5.0

    def test_n_scanned_positive(self):
        r = continuous_jarlskog_scan(scan_max=0.5, step=0.1)
        assert r["n_scanned"] > 0

    def test_invalid_scan_max(self):
        with pytest.raises(ValueError):
            continuous_jarlskog_scan(scan_max=-1.0, step=0.1)

    def test_invalid_step(self):
        with pytest.raises(ValueError):
            continuous_jarlskog_scan(scan_max=1.0, step=0.0)

    def test_best_delta_ells_non_negative(self):
        r = continuous_jarlskog_scan(scan_max=2.0, step=0.1)
        assert r["best_delta_ell_12"] >= 0.0
        assert r["best_delta_ell_23"] >= 0.0

    def test_verdict_string_present(self):
        r = continuous_jarlskog_scan(scan_max=1.0, step=0.1)
        assert "Best residual" in r["verdict"]


class TestFindExactContinuousTarget:
    def test_returns_dict(self):
        r = find_exact_continuous_target()
        assert isinstance(r, dict)

    def test_within_1pct(self):
        r = find_exact_continuous_target()
        assert r["within_1pct"], f"Residual: {r['residual_pct']:.4f}%"

    def test_lambda_cabibbo_reproduced_near_cabibbo(self):
        r = find_exact_continuous_target()
        # The reconstructed lambda from n_fn_cabibbo should equal lambda_Cabibbo
        assert r["lambda_cabibbo_reproduced"] == pytest.approx(LAMBDA_CABIBBO, rel=0.01)

    def test_delta_ell_12_target_correct(self):
        r = find_exact_continuous_target()
        assert r["delta_ell_12_target"] == pytest.approx(DELTA_ELL_12_TARGET, rel=1e-6)

    def test_delta_ell_23_target_correct(self):
        r = find_exact_continuous_target()
        assert r["delta_ell_23_target"] == pytest.approx(DELTA_ELL_23_TARGET, rel=1e-6)

    def test_delta_dl12_nonzero(self):
        r = find_exact_continuous_target()
        # Target is not exactly an integer
        assert abs(r["delta_dl12_from_integer"]) > 0.05

    def test_delta_kt_required_natural(self):
        r = find_exact_continuous_target()
        assert r["delta_kt_required"] > 0.0
        assert r["delta_kt_required"] < 0.10

    def test_n_fn_required_in_result(self):
        r = find_exact_continuous_target()
        assert r["n_fn_12"] == pytest.approx(DELTA_ELL_12_TARGET, rel=1e-9)

    def test_j_at_target_close_to_pdg(self):
        r = find_exact_continuous_target()
        assert r["j_at_target"] == pytest.approx(J_PDG, rel=0.01)


class TestNloLktCorrectionAnsatz:
    def test_returns_dict(self):
        r = nlo_lkt_correction_ansatz()
        assert isinstance(r, dict)

    def test_delta_kt_12_natural(self):
        r = nlo_lkt_correction_ansatz()
        assert r["is_natural_12"], f"delta_KT_12 = {r['delta_kt_12']:.4f}"

    def test_delta_kt_23_natural(self):
        r = nlo_lkt_correction_ansatz()
        assert r["is_natural_23"], f"delta_KT_23 = {r['delta_kt_23']:.4f}"

    def test_delta_kt_12_positive(self):
        r = nlo_lkt_correction_ansatz()
        assert r["delta_kt_12"] > 0.0

    def test_delta_kt_23_positive(self):
        r = nlo_lkt_correction_ansatz()
        assert r["delta_kt_23"] > 0.0

    def test_delta_kt_12_approx_value(self):
        r = nlo_lkt_correction_ansatz()
        assert 0.01 < r["delta_kt_12"] < 0.15

    def test_interpretation_in_result(self):
        r = nlo_lkt_correction_ansatz()
        assert len(r["interpretation"]) > 20

    def test_verdict_in_result(self):
        r = nlo_lkt_correction_ansatz()
        assert "NATURAL" in r["verdict"]

    def test_delta_dl12_nonzero(self):
        r = nlo_lkt_correction_ansatz()
        assert abs(r["delta_dl12"]) > 0.05


class TestFnChargeMapping:
    def test_returns_dict(self):
        r = fn_charge_mapping()
        assert isinstance(r, dict)

    def test_epsilon_braid(self):
        r = fn_charge_mapping()
        assert r["epsilon_braid"] == pytest.approx(LATTICE_SUPPRESSION, rel=1e-9)

    def test_n_fn_12_equals_target(self):
        r = fn_charge_mapping()
        assert r["n_fn_12"] == pytest.approx(DELTA_ELL_12_TARGET, rel=1e-9)

    def test_n_fn_23_positive(self):
        r = fn_charge_mapping()
        assert r["n_fn_23"] > 0.0

    def test_lambda_reconstructed_approx_cabibbo(self):
        r = fn_charge_mapping()
        # epsilon_braid^{n_fn_cabibbo} should reproduce lambda_Cabibbo exactly by construction
        assert r["lambda_reconstructed_from_fn"] == pytest.approx(LAMBDA_CABIBBO, rel=0.01)

    def test_reconstruction_error_small(self):
        r = fn_charge_mapping()
        assert r["reconstruction_error_pct"] < 5.0

    def test_n_fn_13_equals_sum(self):
        r = fn_charge_mapping()
        assert r["n_fn_13"] == pytest.approx(r["n_fn_12"] + r["n_fn_23"], rel=1e-9)

    def test_interpretation_in_result(self):
        r = fn_charge_mapping()
        assert len(r["interpretation"]) > 20


class TestAdmission7MappedVerdict:
    def test_returns_dict(self):
        r = admission_7_mapped_verdict()
        assert isinstance(r, dict)

    def test_admission_number(self):
        r = admission_7_mapped_verdict()
        assert r["admission"] == 7

    def test_previous_status(self):
        r = admission_7_mapped_verdict()
        assert r["previous_status"] == "ARCHITECTURE_LIMIT"

    def test_new_status(self):
        r = admission_7_mapped_verdict()
        assert r["new_status"] == "ARCHITECTURE_LIMIT_MAPPED"

    def test_j_pdg_reproducible(self):
        r = admission_7_mapped_verdict()
        assert r["j_pdg_reproducible"]

    def test_closure_path_a_mentions_lkt(self):
        r = admission_7_mapped_verdict()
        assert "LKT" in r["closure_path_a"] or "kinetic" in r["closure_path_a"].lower()

    def test_closure_path_b_mentions_fn(self):
        r = admission_7_mapped_verdict()
        assert "FN" in r["closure_path_b"] or "Froggatt" in r["closure_path_b"]

    def test_lkt_is_natural(self):
        r = admission_7_mapped_verdict()
        assert r["lkt_is_natural"]

    def test_citation_present(self):
        r = admission_7_mapped_verdict()
        assert "pillar402" in r["citation"].lower() or "Pillar 402" in r["citation"]


class TestPillar402Summary:
    def test_returns_dict(self):
        r = pillar402_summary()
        assert isinstance(r, dict)

    def test_pillar_number(self):
        r = pillar402_summary()
        assert r["pillar_number"] == 402

    def test_status(self):
        r = pillar402_summary()
        assert r["status"] == "ARCHITECTURE_LIMIT_MAPPED"

    def test_j_pdg_reproducible(self):
        r = pillar402_summary()
        assert r["j_pdg_reproducible_within_1pct"]

    def test_delta_ell_12_target(self):
        r = pillar402_summary()
        assert r["delta_ell_12_target"] == pytest.approx(DELTA_ELL_12_TARGET, rel=1e-6)

    def test_honest_residual_present(self):
        r = pillar402_summary()
        assert len(r["honest_residual"]) > 50

    def test_delta_kt_lkt_required(self):
        r = pillar402_summary()
        assert r["delta_kt_lkt_required"] > 0.0
        assert r["delta_kt_lkt_required"] < 0.1

    def test_n_fn_required(self):
        r = pillar402_summary()
        assert r["n_fn_required"] == pytest.approx(DELTA_ELL_12_TARGET, rel=1e-6)

    def test_verdict_dict_present(self):
        r = pillar402_summary()
        assert "verdict_dict" in r
        assert r["verdict_dict"]["new_status"] == "ARCHITECTURE_LIMIT_MAPPED"
