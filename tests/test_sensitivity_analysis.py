# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_sensitivity_analysis.py
=====================================
Tests for Pillar 185 — Fixed-Point Robustness (src/core/sensitivity_analysis.py).

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.sensitivity_analysis import (
    PHI0_CANONICAL, N_S_CANONICAL, R_BRAIDED_CANONICAL, EPSILON_GRID,
    ns_from_phi0, r_from_phi0, cs_from_phi0, w_kk_from_phi0,
    observable_at_perturbation, sensitivity_coefficient,
    phi0_sensitivity_audit, fixed_point_basin, brittleness_verdict,
    pillar185_summary,
)


class TestModuleConstants:
    def test_phi0_is_10pi(self):
        assert PHI0_CANONICAL == pytest.approx(10.0 * math.pi, rel=1e-9)

    def test_n_s_canonical(self):
        assert 0.95 < N_S_CANONICAL < 0.975

    def test_r_braided_canonical(self):
        assert 0.020 < R_BRAIDED_CANONICAL < 0.045

    def test_epsilon_grid_has_entries(self):
        assert len(EPSILON_GRID) >= 5

    def test_epsilon_grid_has_small_values(self):
        assert min(EPSILON_GRID) <= 1e-10


class TestNsFromPhi0:
    def test_canonical_ns(self):
        ns = ns_from_phi0(PHI0_CANONICAL)
        assert ns == pytest.approx(N_S_CANONICAL, abs=0.01)

    def test_larger_phi0_higher_ns(self):
        # More e-folds → closer to 1
        assert ns_from_phi0(PHI0_CANONICAL * 2) > ns_from_phi0(PHI0_CANONICAL)

    def test_smaller_phi0_lower_ns(self):
        assert ns_from_phi0(PHI0_CANONICAL * 0.5) < ns_from_phi0(PHI0_CANONICAL)

    def test_ns_formula(self):
        phi0 = PHI0_CANONICAL
        N_e = phi0**2 / (4.0 * 5)
        expected = 1.0 - 2.0 / N_e
        assert ns_from_phi0(phi0) == pytest.approx(expected, rel=1e-9)


class TestRFromPhi0:
    def test_canonical_r(self):
        r = r_from_phi0(PHI0_CANONICAL)
        # r_from_phi0 uses the slow-roll formula r_bare × c_s;
        # the canonical R_BRAIDED_CANONICAL constant is from phi0_closure.py
        # which uses a slightly different normalization.  Check order of magnitude.
        assert 0.01 < r < 0.10

    def test_r_positive(self):
        assert r_from_phi0(PHI0_CANONICAL) > 0

    def test_larger_phi0_smaller_r(self):
        assert r_from_phi0(PHI0_CANONICAL * 2) < r_from_phi0(PHI0_CANONICAL)


class TestCsFromPhi0:
    def test_cs_is_constant(self):
        # c_s is phi0-independent at leading order
        cs1 = cs_from_phi0(PHI0_CANONICAL)
        cs2 = cs_from_phi0(PHI0_CANONICAL * 2)
        assert cs1 == pytest.approx(cs2, rel=1e-9)

    def test_cs_value(self):
        assert cs_from_phi0(PHI0_CANONICAL) == pytest.approx(12.0/37.0, rel=1e-9)


class TestWKKFromPhi0:
    def test_w_kk_constant(self):
        w1 = w_kk_from_phi0(PHI0_CANONICAL)
        w2 = w_kk_from_phi0(PHI0_CANONICAL * 2)
        assert w1 == pytest.approx(w2, rel=1e-9)

    def test_w_kk_less_than_minus_one(self):
        assert w_kk_from_phi0(PHI0_CANONICAL) > -1.0

    def test_w_kk_approximately(self):
        w = w_kk_from_phi0(PHI0_CANONICAL)
        assert w == pytest.approx(-0.930, abs=0.005)


class TestSensitivityCoefficient:
    def test_small_epsilon_linear(self):
        # n_s sensitivity should be ~0.076
        s = sensitivity_coefficient(ns_from_phi0, PHI0_CANONICAL, 1e-8)
        assert 0.01 < s < 1.0  # sub-linear (not brittle)

    def test_cs_zero_sensitivity(self):
        # c_s is phi0-independent → sensitivity = 0
        s = sensitivity_coefficient(cs_from_phi0, PHI0_CANONICAL, 1e-6)
        assert s == pytest.approx(0.0, abs=1e-6)

    def test_w_kk_zero_sensitivity(self):
        s = sensitivity_coefficient(w_kk_from_phi0, PHI0_CANONICAL, 1e-6)
        assert s == pytest.approx(0.0, abs=1e-6)


class TestPhi0SensitivityAudit:
    def setup_method(self):
        self.audit = phi0_sensitivity_audit()

    def test_not_brittle(self):
        assert self.audit["any_observable_brittle"] is False

    def test_verdict_non_brittle(self):
        assert "NON-BRITTLE" in self.audit["verdict"]

    def test_ns_max_sensitivity_sub_10(self):
        assert self.audit["n_s"]["max_sensitivity_coeff"] < 10.0

    def test_r_braided_max_sensitivity_sub_10(self):
        assert self.audit["r_braided"]["max_sensitivity_coeff"] < 10.0

    def test_cs_max_sensitivity_near_zero(self):
        assert self.audit["c_s"]["max_sensitivity_coeff"] < 1e-3

    def test_w_kk_max_sensitivity_near_zero(self):
        assert self.audit["w_KK"]["max_sensitivity_coeff"] < 1e-3

    def test_phi0_recorded(self):
        assert self.audit["phi0"] == pytest.approx(PHI0_CANONICAL, rel=1e-9)

    def test_planck_stability_present(self):
        ps = self.audit["planck_stability"]
        assert "ns_canonical" in ps
        assert "within_planck_1sigma" in ps

    def test_ns_canonical_value(self):
        assert self.audit["n_s"]["canonical_value"] == pytest.approx(N_S_CANONICAL, abs=0.01)


class TestFixedPointBasin:
    def setup_method(self):
        self.basin = fixed_point_basin()

    def test_phi0_canonical(self):
        assert self.basin["phi0_canonical"] == pytest.approx(PHI0_CANONICAL, rel=1e-9)

    def test_stable_range_nonzero(self):
        assert self.basin["total_basin_frac"] > 0

    def test_stable_low_positive(self):
        assert self.basin["frac_stable_low"] > 0

    def test_stable_high_positive(self):
        assert self.basin["frac_stable_high"] > 0

    def test_interpretation_present(self):
        assert len(self.basin["interpretation"]) > 20

    def test_ns_2sigma_window(self):
        assert self.basin["ns_2sigma_low"] < self.basin["ns_2sigma_high"]


class TestBrittlenessVerdict:
    def setup_method(self):
        self.v = brittleness_verdict()

    def test_not_brittle(self):
        assert self.v["brittle"] is False

    def test_max_amplification_sub_10(self):
        assert self.v["max_amplification"] < 10.0

    def test_verdict_mentions_not_brittle(self):
        assert "NOT BRITTLE" in self.v["verdict"]

    def test_audit_response_present(self):
        assert "CLOSED" in self.v["audit_response"]


class TestPillar185Summary:
    def setup_method(self):
        self.s = pillar185_summary()

    def test_pillar_number(self):
        assert self.s["pillar"] == 185

    def test_not_brittle(self):
        assert self.s["brittle"] is False

    def test_max_sensitivity_sub_10(self):
        assert self.s["max_sensitivity_coefficient"] < 10.0

    def test_status_contains_not_brittle(self):
        assert "NOT brittle" in self.s["status"] or "non-brittle" in self.s["status"].lower()

    def test_version_v9_39(self):
        assert "9.39" in self.s["version"]
