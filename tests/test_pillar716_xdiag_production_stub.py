# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 716 — XDiag production install stub."""
from __future__ import annotations

import math

import pytest

from src.quantum.pillar716_xdiag_production_stub import (
    C_S,
    K_CS,
    N_W,
    PILLAR_NUMBER,
    STATUS,
    T_KK,
    U_KK,
    U_OVER_T_KK,
    XDIAG_PRODUCTION_STUB_VALIDATED,
    double_occupancy_mott,
    mock_xdiag_solve,
    mott_energy_analytic,
    xdiag_stub_health_check,
)


ANALYTIC = mott_energy_analytic()
DOUBLE_OCC = double_occupancy_mott()
PERIODIC = mock_xdiag_solve(10, U_OVER_T_KK, "periodic")
OPEN = mock_xdiag_solve(10, U_OVER_T_KK, "open")
HEALTH = xdiag_stub_health_check()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 716

    def test_core_constants(self) -> None:
        assert N_W == 5
        assert K_CS == 74
        assert math.isclose(T_KK, 12.0 / 37.0, rel_tol=0.0, abs_tol=1e-15)
        assert math.isclose(U_KK, 74.0 / 5.0, rel_tol=0.0, abs_tol=1e-15)

    def test_ratio_and_speed(self) -> None:
        assert math.isclose(U_OVER_T_KK, 74.0 * 37.0 / (5.0 * 12.0), rel_tol=0.0, abs_tol=1e-15)
        assert C_S == T_KK

    def test_validated_flag(self) -> None:
        assert XDIAG_PRODUCTION_STUB_VALIDATED is True


class TestAnalyticFunctions:
    def test_mott_energy_formula(self) -> None:
        expected = -4.0 * (12.0 / 37.0) ** 2 / (74.0 / 5.0)
        assert ANALYTIC["ground_state_energy_per_site"] == pytest.approx(expected, rel=1e-12)

    def test_total_energy_scales_with_sites(self) -> None:
        assert ANALYTIC["ground_state_energy_total"] == pytest.approx(
            ANALYTIC["l_sites"] * ANALYTIC["ground_state_energy_per_site"],
            rel=1e-12,
        )

    def test_analytic_status(self) -> None:
        assert ANALYTIC["epistemic_status"] == "ANALYTICAL_ESTIMATE"

    def test_double_occupancy_formula(self) -> None:
        expected = ((12.0 / 37.0) / (74.0 / 5.0)) ** 2
        assert DOUBLE_OCC["double_occupancy"] == pytest.approx(expected, rel=1e-12)

    def test_double_occupancy_small(self) -> None:
        assert 0.0 < DOUBLE_OCC["double_occupancy"] < 1e-3


class TestMockSolver:
    def test_mock_returns_dict(self) -> None:
        assert isinstance(PERIODIC, dict)

    def test_mock_marks_scaffold(self) -> None:
        assert PERIODIC["status"] == STATUS == "SCAFFOLD"
        assert PERIODIC["epistemic_status"] == "SCAFFOLD"

    def test_mock_matches_analytic_within_5pct(self) -> None:
        assert PERIODIC["energy_matches_strong_coupling_within_5pct"] is True
        assert PERIODIC["relative_error_vs_analytic"] < 0.05

    def test_periodic_is_closer_than_open(self) -> None:
        assert PERIODIC["relative_error_vs_analytic"] < OPEN["relative_error_vs_analytic"]

    def test_spectrum_is_sorted(self) -> None:
        assert PERIODIC["spectrum"] == sorted(PERIODIC["spectrum"])

    def test_charge_gap_positive(self) -> None:
        assert PERIODIC["charge_gap_estimate"] > 0.0

    def test_first_gap_positive(self) -> None:
        assert PERIODIC["first_gap"] > 0.0

    def test_double_occupancy_matches_analytic(self) -> None:
        assert PERIODIC["double_occupancy"] == pytest.approx(DOUBLE_OCC["double_occupancy"], rel=1e-12)

    def test_invalid_l_raises(self) -> None:
        with pytest.raises(ValueError, match="L must be >= 2"):
            mock_xdiag_solve(1, U_OVER_T_KK, "periodic")

    def test_invalid_ratio_raises(self) -> None:
        with pytest.raises(ValueError, match="U_over_t must be positive"):
            mock_xdiag_solve(10, 0.0, "periodic")

    def test_invalid_bc_raises(self) -> None:
        with pytest.raises(ValueError, match="bc must be"):
            mock_xdiag_solve(10, U_OVER_T_KK, "twisted")


class TestHealthCheck:
    def test_health_is_healthy(self) -> None:
        assert HEALTH["status"] == "HEALTHY"

    def test_health_validated(self) -> None:
        assert HEALTH["validated"] is True
        assert HEALTH["xdiag_production_stub_validated"] is True

    def test_health_relative_error_pct(self) -> None:
        assert 0.0 <= HEALTH["relative_error_pct"] < 5.0

    def test_health_honesty(self) -> None:
        assert HEALTH["production_readiness"] == "REQUIRES_REAL_XDIAG_INSTALL"
