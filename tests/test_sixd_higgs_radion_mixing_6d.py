# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/higgs_radion_mixing_6d.py — Track 1 (Higgs θ_HR, 6D+ Workstream)."""
from __future__ import annotations

import math
import pytest

from src.sixd.higgs_radion_mixing_6d import (
    HIGGS_MASS_GEV,
    HIGGS_VEV_GEV,
    M_H_GEV,
    M_RADION_GEV,
    PI_KR,
    RADION_DECAY_CONST_GEV,
    XI_BRANE,
    coleman_weinberg_coefficient,
    higgs_mass_cw_correction,
    higgs_radion_mixing_angle,
    higgs_radion_mixing_summary,
    p5_closure_gate,
    radion_mass_gw,
)


class TestConstants:
    def test_xi_brane_conformal(self):
        assert XI_BRANE == pytest.approx(1.0 / 6.0, rel=1e-9)

    def test_higgs_mass_gev(self):
        assert HIGGS_MASS_GEV == pytest.approx(125.25, abs=0.01)

    def test_higgs_vev_gev(self):
        assert HIGGS_VEV_GEV == pytest.approx(246.22, abs=0.01)

    def test_radion_decay_const_tev_scale(self):
        assert RADION_DECAY_CONST_GEV == pytest.approx(1000.0, rel=1e-9)

    def test_m_radion_gev(self):
        assert M_RADION_GEV == pytest.approx(300.0, rel=1e-9)

    def test_m_h_equals_higgs_mass(self):
        assert M_H_GEV == pytest.approx(HIGGS_MASS_GEV, rel=1e-9)

    def test_pi_kr_value(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)


class TestRadionMassGW:
    def test_positive_mass(self):
        m = radion_mass_gw(0.05, 37.0)
        assert m > 0

    def test_warp_suppression(self):
        # Larger pi_kr → more warping → lighter radion
        m1 = radion_mass_gw(0.05, 30.0)
        m2 = radion_mass_gw(0.05, 40.0)
        assert m1 > m2

    def test_linear_in_k_over_mpl(self):
        m1 = radion_mass_gw(0.05, 37.0)
        m2 = radion_mass_gw(0.10, 37.0)
        assert m2 == pytest.approx(2 * m1, rel=1e-9)

    def test_returns_float(self):
        assert isinstance(radion_mass_gw(0.05, 37.0), float)


class TestHiggsRadionMixingAngle:
    def test_canonical_is_nonzero(self):
        theta = higgs_radion_mixing_angle(XI_BRANE, HIGGS_VEV_GEV, RADION_DECAY_CONST_GEV,
                                          M_H_GEV, M_RADION_GEV)
        assert abs(theta) > 1e-6

    def test_perturbative(self):
        theta = higgs_radion_mixing_angle(XI_BRANE, HIGGS_VEV_GEV, RADION_DECAY_CONST_GEV,
                                          M_H_GEV, M_RADION_GEV)
        assert abs(theta) < math.pi / 4

    def test_larger_xi_larger_theta(self):
        t1 = higgs_radion_mixing_angle(0.1, 246.22, 1000.0, 125.25, 300.0)
        t2 = higgs_radion_mixing_angle(0.2, 246.22, 1000.0, 125.25, 300.0)
        assert abs(t2) > abs(t1)

    def test_degenerate_mass_no_crash(self):
        # m_h == m_radion → should not raise
        theta = higgs_radion_mixing_angle(1.0 / 6.0, 246.22, 1000.0, 300.0, 300.0)
        assert math.isfinite(theta)

    def test_small_xi_small_theta(self):
        theta = higgs_radion_mixing_angle(1e-6, 246.22, 1000.0, 125.25, 300.0)
        assert abs(theta) < 1e-4


class TestColemanWeinbergCoefficient:
    def test_positive(self):
        a = coleman_weinberg_coefficient(1, 1.0)
        assert a > 0

    def test_scales_with_n_fields(self):
        a1 = coleman_weinberg_coefficient(1, 0.5)
        a3 = coleman_weinberg_coefficient(3, 0.5)
        assert a3 == pytest.approx(3 * a1, rel=1e-9)

    def test_quartic_in_mass_ratio(self):
        a1 = coleman_weinberg_coefficient(1, 1.0)
        a2 = coleman_weinberg_coefficient(1, 2.0)
        assert a2 == pytest.approx(16 * a1, rel=1e-9)

    def test_known_value(self):
        # n=1, m/v=1: A = 1/(64π²)
        a = coleman_weinberg_coefficient(1, 1.0)
        assert a == pytest.approx(1.0 / (64 * math.pi**2), rel=1e-9)


class TestHiggsMassCWCorrection:
    def test_returns_float(self):
        corr = higgs_mass_cw_correction(0.1, M_RADION_GEV)
        assert isinstance(corr, float)

    def test_zero_angle_zero_correction(self):
        corr = higgs_mass_cw_correction(0.0, M_RADION_GEV)
        assert corr == pytest.approx(0.0, abs=1e-10)

    def test_sign_radion_heavier_than_higgs(self):
        # m_radion > m_H → correction is positive
        corr = higgs_mass_cw_correction(0.1, 300.0)
        assert corr > 0

    def test_pi_quarter_angle_maximal(self):
        corr_quarter = higgs_mass_cw_correction(math.pi / 4, 300.0)
        corr_small = higgs_mass_cw_correction(0.1, 300.0)
        assert abs(corr_quarter) > abs(corr_small)


class TestP5ClosureGate:
    def test_canonical_theta_passes(self):
        theta = higgs_radion_mixing_angle(XI_BRANE, HIGGS_VEV_GEV, RADION_DECAY_CONST_GEV,
                                          M_H_GEV, M_RADION_GEV)
        gate = p5_closure_gate(theta)
        assert gate["gate_pass"] is True

    def test_zero_theta_fails(self):
        gate = p5_closure_gate(0.0)
        assert gate["gate_pass"] is False

    def test_large_theta_fails(self):
        gate = p5_closure_gate(math.pi)
        assert gate["gate_pass"] is False

    def test_status_string_present(self):
        theta = higgs_radion_mixing_angle(XI_BRANE, HIGGS_VEV_GEV, RADION_DECAY_CONST_GEV,
                                          M_H_GEV, M_RADION_GEV)
        gate = p5_closure_gate(theta)
        assert "ARCHITECTURE_LIMIT_CERTIFIED" in gate["status"]

    def test_returns_required_keys(self):
        gate = p5_closure_gate(0.05)
        for key in ["theta_hr_rad", "theta_hr_deg", "nonzero", "perturbative_regime",
                    "gate_pass", "status"]:
            assert key in gate

    def test_theta_deg_conversion(self):
        theta_rad = 0.1
        gate = p5_closure_gate(theta_rad)
        assert gate["theta_hr_deg"] == pytest.approx(math.degrees(0.1), rel=1e-9)


class TestHiggsRadionMixingSummary:
    def test_returns_dict(self):
        s = higgs_radion_mixing_summary()
        assert isinstance(s, dict)

    def test_required_keys(self):
        s = higgs_radion_mixing_summary()
        for key in ["theta_hr_rad", "theta_hr_deg", "cw_coefficient",
                    "higgs_mass_cw_correction_gev2", "radion_mass_gw_gev",
                    "gate", "overall_status", "note"]:
            assert key in s

    def test_overall_status(self):
        s = higgs_radion_mixing_summary()
        assert "ARCHITECTURE_LIMIT_CERTIFIED" in s["overall_status"]

    def test_gate_passes(self):
        s = higgs_radion_mixing_summary()
        assert s["gate"]["gate_pass"] is True

    def test_theta_consistent(self):
        s = higgs_radion_mixing_summary()
        assert s["theta_hr_deg"] == pytest.approx(
            math.degrees(s["theta_hr_rad"]), rel=1e-9
        )
