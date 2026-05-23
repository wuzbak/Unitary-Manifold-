# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 385 — Kac-Moody Level-K c₁ Exact Computation."""

import math
import pytest
from src.core.pillar385_kac_moody_c1_computation import (
    K_CS, K_EFF, GAMMA_THEORY, GAMMA_FIT, GAMMA_GAP_FRAC,
    CASIMIR_FUNDAMENTAL,
    kac_moody_central_charge,
    one_loop_km_correction,
    two_loop_km_correction,
    empirical_c1,
    non_perturbative_residual,
    kac_moody_c1_full_report,
    l2_status_certificate,
)


class TestKacMoodyConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_k_eff(self):
        # SU(2) dual Coxeter number = 2
        assert K_EFF == 76

    def test_gamma_theory(self):
        assert 0.23 < GAMMA_THEORY < 0.26

    def test_gamma_fit(self):
        assert 0.26 < GAMMA_FIT < 0.29

    def test_gamma_gap(self):
        assert 0.10 < GAMMA_GAP_FRAC < 0.16  # ~13% gap

    def test_casimir_fundamental(self):
        # C₂(j=½) = j(j+1) = ½ × 3/2 = 3/4
        assert abs(CASIMIR_FUNDAMENTAL - 0.75) < 1e-10


class TestCentralCharge:
    def test_central_charge_formula(self):
        # c_KM = 3K / (K + 2) for SU(2)_K WZW
        c = kac_moody_central_charge()
        expected = 3.0 * 74 / 76
        assert abs(c - expected) < 1e-10

    def test_central_charge_positive(self):
        c = kac_moody_central_charge()
        assert c > 0.0

    def test_central_charge_below_3(self):
        # c_KM < 3 for all finite K (approaches 3 as K → ∞)
        c = kac_moody_central_charge()
        assert c < 3.0

    def test_central_charge_approaches_3(self):
        # For large K, c_KM → 3
        c = kac_moody_central_charge()
        assert abs(c - 3.0) < 0.1  # K=74 is large enough


class TestOneLoopKMCorrection:
    def test_delta_gamma_1_formula(self):
        result = one_loop_km_correction()
        expected = 0.75 / 76
        assert abs(result["delta_gamma_1"] - expected) < 1e-10

    def test_c1_km_positive(self):
        result = one_loop_km_correction()
        assert result["c1_km"] > 0

    def test_c1_km_below_k_cs(self):
        # c₁ must be below K_CS (Borel-Padé upper bound from P380)
        result = one_loop_km_correction()
        assert result["c1_km"] < K_CS

    def test_gamma_km_above_theory(self):
        # γ_KM > γ_theory (correction is positive)
        result = one_loop_km_correction()
        assert result["gamma_km_1loop"] > GAMMA_THEORY

    def test_gamma_km_below_fit(self):
        # γ_KM < γ_fit (one-loop doesn't fully explain the gap)
        result = one_loop_km_correction()
        assert result["gamma_km_1loop"] < GAMMA_FIT

    def test_residual_positive(self):
        result = one_loop_km_correction()
        assert result["residual_abs"] > 0

    def test_c1_km_approximately_3(self):
        # Expected c₁^{KM} ≈ 3.02
        result = one_loop_km_correction()
        assert 2.5 < result["c1_km"] < 3.5


class TestTwoLoopKMCorrection:
    def test_delta_gamma_2_formula(self):
        result = two_loop_km_correction()
        expected = 0.75 ** 2 / 76 ** 2
        assert abs(result["delta_gamma_2"] - expected) < 1e-10

    def test_two_loop_smaller_than_one_loop(self):
        one = one_loop_km_correction()
        two = two_loop_km_correction()
        assert two["delta_gamma_2"] < one["delta_gamma_1"]

    def test_c2_km_positive(self):
        result = two_loop_km_correction()
        assert result["c2_km"] > 0


class TestEmpiricalC1:
    def test_empirical_c1_formula(self):
        c1 = empirical_c1()
        expected = K_CS * (GAMMA_FIT / GAMMA_THEORY - 1.0)
        assert abs(c1 - expected) < 1e-10

    def test_empirical_c1_positive(self):
        assert empirical_c1() > 0

    def test_empirical_c1_below_k_cs(self):
        # P380 Borel-Padé bound: c₁ < K_CS
        assert empirical_c1() < K_CS

    def test_empirical_c1_approximately_9_4(self):
        # Expected ≈ 9.40 from P380
        c1 = empirical_c1()
        assert 8.0 < c1 < 11.0


class TestNonPerturbativeResidual:
    def test_c1_np_positive(self):
        result = non_perturbative_residual()
        assert result["c1_np"] > 0

    def test_c1_km_plus_np_equals_empirical(self):
        result = non_perturbative_residual()
        assert abs(result["c1_km"] + result["c1_np"] - result["c1_empirical"]) < 1e-8

    def test_km_fraction_positive(self):
        result = non_perturbative_residual()
        assert result["km_frac_explained"] > 0

    def test_km_fraction_below_one(self):
        # KM one-loop explains less than all the gap
        result = non_perturbative_residual()
        assert result["km_frac_explained"] < 1.0

    def test_original_gap_positive(self):
        result = non_perturbative_residual()
        assert result["gamma_gap_original"] > 0

    def test_gap_after_km_less_than_original(self):
        result = non_perturbative_residual()
        assert result["gamma_gap_after_km"] < result["gamma_gap_original"]


class TestFullReport:
    @pytest.fixture
    def report(self):
        return kac_moody_c1_full_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 385

    def test_status(self, report):
        assert report["status"] == "L2_KACMOODY_CONSTRAINED"

    def test_epistemic_upgrade(self, report):
        assert "L2_BOUNDED_NON_PERTURBATIVE" in report["epistemic_upgrade"]
        assert "L2_KACMOODY_CONSTRAINED" in report["epistemic_upgrade"]

    def test_km_explanation_pct_positive(self, report):
        assert report["km_explanation_pct"] > 0

    def test_remaining_gap_pct_positive(self, report):
        assert report["remaining_gap_pct"] > 0

    def test_remaining_gap_less_than_original(self, report):
        # Gap is partially closed
        original = GAMMA_GAP_FRAC * 100
        remaining = report["remaining_gap_pct"]
        assert remaining < original

    def test_verdict_is_string(self, report):
        assert isinstance(report["verdict"], str)
        assert len(report["verdict"]) > 20

    def test_borel_pade_still_holds(self, report):
        assert report["borel_pade_bound_still_holds"] is True


class TestL2StatusCertificate:
    @pytest.fixture
    def cert(self):
        return l2_status_certificate()

    def test_pillar(self, cert):
        assert cert["pillar"] == 385

    def test_status(self, cert):
        assert cert["l2_status"] == "L2_KACMOODY_CONSTRAINED"

    def test_prior_status(self, cert):
        assert cert["prior_status"] == "L2_BOUNDED_NON_PERTURBATIVE"

    def test_gap_reduced(self, cert):
        assert cert["gap_after_km_pct"] < cert["gap_original_pct"]

    def test_c1_km_in_bounds(self, cert):
        c1_km = cert["c1_km"]
        assert cert["borel_pade_bounds"]["lower"] <= c1_km <= cert["borel_pade_bounds"]["upper"]

    def test_certifies_non_zero(self, cert):
        assert cert["certifies_not_zero"] is True

    def test_certifies_not_k_cs(self, cert):
        assert cert["certifies_not_k_cs"] is True

    def test_requires_full_km(self, cert):
        assert cert["requires_full_km"] is True

    def test_c1_np_positive(self, cert):
        assert cert["c1_np_residual"] > 0


class TestGapHierarchy:
    """Tests that validate the hierarchy of γ values."""

    def test_gamma_ordering(self):
        # γ_theory < γ_KM_1loop < γ_fit
        one_loop = one_loop_km_correction()
        assert GAMMA_THEORY < one_loop["gamma_km_1loop"] < GAMMA_FIT

    def test_c1_ordering(self):
        # 0 < c1_km < c1_empirical < K_CS
        result = non_perturbative_residual()
        assert 0 < result["c1_km"] < result["c1_empirical"] < K_CS

    def test_gap_partially_closed(self):
        # KM one-loop closes part (not all) of the 13% gap
        one_loop = one_loop_km_correction()
        fraction_closed = 1.0 - one_loop["residual_abs"] / (GAMMA_FIT - GAMMA_THEORY)
        assert 0 < fraction_closed < 1.0

    def test_gap_reduction_non_trivial(self):
        # At least 1% of the gap should be explained by KM
        report = kac_moody_c1_full_report()
        assert report["km_explanation_pct"] > 1.0
