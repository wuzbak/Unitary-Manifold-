# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar398_jarlskog_lattice_scan.py
=============================================
Tests for Pillar 398 — Jarlskog Lattice Scan.

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar398_jarlskog_lattice_scan import (
    PILLAR_NUMBER,
    PILLAR_TITLE,
    PILLAR_STATUS,
    N_W,
    K_CS,
    PI_KR,
    LATTICE_STEP,
    LATTICE_SUPPRESSION,
    J_PDG,
    J_GEO_LEADING_ORDER,
    J_GEO_RESIDUAL_PCT,
    SIN_DELTA_PDG,
    c_l_lattice_point,
    lattice_mixing_angle,
    jarlskog_from_lattice,
    jarlskog_lattice_scan,
    admission_7_closure_verdict,
    pillar398_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 398

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0, rel=1e-9)

    def test_lattice_step_formula(self):
        assert LATTICE_STEP == pytest.approx(5.0 / 74.0, rel=1e-10)

    def test_lattice_suppression_formula(self):
        expected = math.exp(-LATTICE_STEP * PI_KR)
        assert LATTICE_SUPPRESSION == pytest.approx(expected, rel=1e-10)

    def test_lattice_suppression_approx_value(self):
        assert LATTICE_SUPPRESSION == pytest.approx(math.exp(-2.5), rel=1e-6)

    def test_j_pdg_order(self):
        assert 2e-5 < J_PDG < 5e-5

    def test_j_geo_leading_order_excess(self):
        assert J_GEO_LEADING_ORDER > J_PDG

    def test_leading_order_residual_pct(self):
        expected = abs(J_GEO_LEADING_ORDER - J_PDG) / J_PDG * 100.0
        assert J_GEO_RESIDUAL_PCT == pytest.approx(expected, rel=1e-6)

    def test_leading_order_residual_around_37pct(self):
        assert 30.0 < J_GEO_RESIDUAL_PCT < 50.0

    def test_sin_delta_pdg_range(self):
        assert 0.8 < SIN_DELTA_PDG < 1.0

    def test_pillar_status(self):
        assert PILLAR_STATUS == "ARCHITECTURE_LIMIT"


# ─────────────────────────────────────────────────────────────────────────────
# c_l_lattice_point
# ─────────────────────────────────────────────────────────────────────────────

class TestCLLatticePoint:
    def test_at_zero(self):
        assert c_l_lattice_point(0) == pytest.approx(0.0, abs=1e-15)

    def test_formula(self):
        for ell in [1, 5, 10, 74]:
            assert c_l_lattice_point(ell) == pytest.approx(LATTICE_STEP * ell, rel=1e-10)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            c_l_lattice_point(-1)

    def test_at_ell_74(self):
        assert c_l_lattice_point(74) == pytest.approx(5.0, rel=1e-9)

    def test_uv_threshold(self):
        assert c_l_lattice_point(8) > 0.5
        assert c_l_lattice_point(7) < 0.5


# ─────────────────────────────────────────────────────────────────────────────
# lattice_mixing_angle
# ─────────────────────────────────────────────────────────────────────────────

class TestLatticeMixingAngle:
    def test_at_zero(self):
        assert lattice_mixing_angle(0) == pytest.approx(1.0, rel=1e-10)

    def test_at_one(self):
        assert lattice_mixing_angle(1) == pytest.approx(math.exp(-2.5), rel=1e-8)

    def test_at_two(self):
        assert lattice_mixing_angle(2) == pytest.approx(math.exp(-5.0), rel=1e-8)

    def test_decreases_with_delta_ell(self):
        assert lattice_mixing_angle(1) < lattice_mixing_angle(0)
        assert lattice_mixing_angle(2) < lattice_mixing_angle(1)

    def test_positive(self):
        for dl in range(6):
            assert lattice_mixing_angle(dl) > 0.0

    def test_below_cabibbo_at_delta_1(self):
        assert lattice_mixing_angle(1) < 0.225

    def test_above_cabibbo_at_delta_0(self):
        assert lattice_mixing_angle(0) > 0.225

    def test_symmetric(self):
        assert lattice_mixing_angle(-2) == pytest.approx(lattice_mixing_angle(2), rel=1e-10)


# ─────────────────────────────────────────────────────────────────────────────
# jarlskog_from_lattice
# ─────────────────────────────────────────────────────────────────────────────

class TestJarlskogFromLattice:
    def test_returns_dict(self):
        assert isinstance(jarlskog_from_lattice(1, 1), dict)

    def test_j_positive(self):
        r = jarlskog_from_lattice(1, 1)
        assert r["j_lattice"] > 0.0

    def test_residual_computed(self):
        r = jarlskog_from_lattice(1, 1)
        expected = abs(r["j_lattice"] - J_PDG) / J_PDG * 100.0
        assert r["residual_pct"] == pytest.approx(expected, rel=1e-6)

    def test_delta_ell_13_is_sum(self):
        r = jarlskog_from_lattice(2, 3)
        assert r["delta_ell_13"] == 5

    def test_s12_formula(self):
        r = jarlskog_from_lattice(2, 1)
        assert r["s12"] == pytest.approx(lattice_mixing_angle(2), rel=1e-10)

    def test_s23_formula(self):
        r = jarlskog_from_lattice(2, 1)
        assert r["s23"] == pytest.approx(lattice_mixing_angle(1), rel=1e-10)

    def test_s13_formula(self):
        r = jarlskog_from_lattice(2, 1)
        assert r["s13"] == pytest.approx(lattice_mixing_angle(3), rel=1e-10)

    def test_degenerate_case_zero_j(self):
        r = jarlskog_from_lattice(0, 0)
        assert r["j_lattice"] == pytest.approx(0.0, abs=1e-20)

    def test_within_15pct_flag(self):
        r = jarlskog_from_lattice(1, 1)
        assert r["within_15pct"] == (r["residual_pct"] < 15.0)

    def test_within_37pct_flag(self):
        r = jarlskog_from_lattice(1, 1)
        assert r["within_37pct"] == (r["residual_pct"] < 37.0)

    def test_raises_negative(self):
        with pytest.raises(ValueError):
            jarlskog_from_lattice(-1, 1)


# ─────────────────────────────────────────────────────────────────────────────
# jarlskog_lattice_scan
# ─────────────────────────────────────────────────────────────────────────────

class TestJarlskogLatticeScan:
    @pytest.fixture(scope="class")
    def result(self):
        return jarlskog_lattice_scan(delta_ell_max=5)

    def test_returns_dict(self, result):
        assert isinstance(result, dict)

    def test_n_scanned(self, result):
        assert result["n_assignments_scanned"] == 36

    def test_best_residual_positive(self, result):
        assert result["best_residual_pct"] > 0.0

    def test_best_config_exists(self, result):
        assert result["best_config"] is not None

    def test_architecture_limit_confirmed(self, result):
        assert result["architecture_limit_confirmed"] is True

    def test_none_within_15pct(self, result):
        assert result["n_within_15pct"] == 0
        assert result["any_within_15pct"] is False

    def test_lattice_step_correct(self, result):
        assert result["lattice_step"] == pytest.approx(LATTICE_STEP, rel=1e-10)

    def test_j_pdg_correct(self, result):
        assert result["j_pdg"] == pytest.approx(J_PDG, rel=1e-6)

    def test_leading_order_residual(self, result):
        assert result["leading_order_residual_pct"] == pytest.approx(J_GEO_RESIDUAL_PCT, rel=1e-4)

    def test_verdict_string(self, result):
        assert isinstance(result["verdict"], str)
        assert "ARCHITECTURE_LIMIT" in result["verdict"]

    def test_key_physics_string(self, result):
        assert isinstance(result["key_physics"], str)
        assert "Cabibbo" in result["key_physics"]

    def test_small_scan_consistent(self):
        r = jarlskog_lattice_scan(delta_ell_max=2)
        assert r["n_assignments_scanned"] == 9
        assert r["architecture_limit_confirmed"] is True

    def test_raises_negative_max(self):
        with pytest.raises(ValueError):
            jarlskog_lattice_scan(delta_ell_max=-1)


# ─────────────────────────────────────────────────────────────────────────────
# Admission 7 verdict
# ─────────────────────────────────────────────────────────────────────────────

class TestAdmission7Verdict:
    @pytest.fixture(scope="class")
    def verdict(self):
        return admission_7_closure_verdict()

    def test_returns_dict(self, verdict):
        assert isinstance(verdict, dict)

    def test_admission_number(self, verdict):
        assert verdict["admission"] == 7

    def test_previous_status(self, verdict):
        assert verdict["previous_status"] == "OPEN"

    def test_new_status(self, verdict):
        assert verdict["new_status"] == "ARCHITECTURE_LIMIT"

    def test_architecture_limit_confirmed(self, verdict):
        assert verdict["architecture_limit_confirmed"] is True

    def test_physical_reason(self, verdict):
        assert isinstance(verdict["physical_reason"], str)
        assert len(verdict["physical_reason"]) > 30

    def test_path_forward(self, verdict):
        assert isinstance(verdict["path_forward"], str)
        assert len(verdict["path_forward"]) > 30

    def test_j_geo_leading_order(self, verdict):
        assert verdict["j_geo_leading_order"] == pytest.approx(J_GEO_LEADING_ORDER, rel=1e-4)

    def test_citation(self, verdict):
        assert "398" in verdict["citation"]


# ─────────────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar398Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar398_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_pillar_number(self, summary):
        assert summary["pillar_number"] == 398

    def test_status(self, summary):
        assert summary["status"] == "ARCHITECTURE_LIMIT"

    def test_admission(self, summary):
        assert summary["admission"] == 7

    def test_architecture_limit_confirmed(self, summary):
        assert summary["architecture_limit_confirmed"] is True

    def test_none_within_15pct(self, summary):
        assert summary["any_within_15pct"] is False

    def test_key_result(self, summary):
        assert isinstance(summary["key_result"], str)
        assert "ARCHITECTURE_LIMIT" in summary["key_result"]

    def test_honest_residual(self, summary):
        assert isinstance(summary["honest_residual"], str)

    def test_lattice_step(self, summary):
        assert summary["lattice_step"] == pytest.approx(LATTICE_STEP, rel=1e-10)

    def test_n_scanned_positive(self, summary):
        assert summary["n_scanned"] > 0
