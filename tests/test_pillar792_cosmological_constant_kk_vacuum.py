# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 792 — COSMOLOGICAL_CONSTANT_KK_VACUUM_ENERGY
~50 tests covering the KK vacuum energy hierarchy computation.
"""
import math
import pytest
from src.core.pillar792_cosmological_constant_kk_vacuum import (
    kk_vacuum_energy_density_gev4,
    hierarchy_ratio,
    rs1_warp_suppression,
    net_residual_hierarchy,
    log10_hierarchy,
    log10_net_residual,
    cancellation_orders_of_magnitude,
    brane_tension_cancellation_fraction,
    cc_gate_summary,
    CC_STATUS,
    PILLAR_792_GATE,
    CC_KK_SUMMARY,
    K_CS,
    N_KK,
    LAMBDA_OBS_GEV4,
    M_KK_GEV,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_k_cs_value(self):
        assert K_CS == 74

    def test_n_kk_equals_k_cs(self):
        assert N_KK == K_CS

    def test_lambda_obs_positive(self):
        assert LAMBDA_OBS_GEV4 > 0

    def test_m_kk_gev(self):
        assert M_KK_GEV == 1000.0

    def test_gate_label(self):
        assert CC_STATUS == "CC_KK_HIERARCHY_ARCHITECTURE_LIMIT"

    def test_pillar_alias(self):
        assert PILLAR_792_GATE == CC_STATUS


# ---------------------------------------------------------------------------
# kk_vacuum_energy_density_gev4
# ---------------------------------------------------------------------------

class TestKKVacuumEnergyDensity:
    def test_returns_float(self):
        rho = kk_vacuum_energy_density_gev4()
        assert isinstance(rho, float)

    def test_positive(self):
        assert kk_vacuum_energy_density_gev4() > 0

    def test_scales_with_mkk4(self):
        rho1 = kk_vacuum_energy_density_gev4(m_kk_gev=1000.0)
        rho2 = kk_vacuum_energy_density_gev4(m_kk_gev=2000.0)
        # Scales as M_KK^4
        assert pytest.approx(rho2 / rho1, rel=1e-6) == 16.0

    def test_scales_with_n_kk(self):
        # Σ n^4 for N=1 vs N=2: 1 vs 1+16=17
        rho1 = kk_vacuum_energy_density_gev4(n_kk=1, m_kk_gev=100.0)
        rho2 = kk_vacuum_energy_density_gev4(n_kk=2, m_kk_gev=100.0)
        assert rho2 / rho1 == pytest.approx(17.0, rel=1e-6)

    def test_n_kk_1_formula(self):
        m = 1000.0
        expected = (m**4 / (16.0 * math.pi**2)) * 1.0  # Σ 1^4 = 1
        result = kk_vacuum_energy_density_gev4(n_kk=1, m_kk_gev=m)
        assert result == pytest.approx(expected, rel=1e-8)

    def test_default_enormously_larger_than_lambda_obs(self):
        rho = kk_vacuum_energy_density_gev4()
        assert rho > LAMBDA_OBS_GEV4 * 1e40

    def test_n_kk_74_finite(self):
        rho = kk_vacuum_energy_density_gev4(n_kk=74)
        assert math.isfinite(rho)


# ---------------------------------------------------------------------------
# hierarchy_ratio
# ---------------------------------------------------------------------------

class TestHierarchyRatio:
    def test_returns_float(self):
        assert isinstance(hierarchy_ratio(), float)

    def test_enormous(self):
        # Must be >> 1e50
        assert hierarchy_ratio() > 1e50

    def test_consistent_with_rho(self):
        rho = kk_vacuum_energy_density_gev4()
        assert hierarchy_ratio(rho) == pytest.approx(rho / LAMBDA_OBS_GEV4, rel=1e-9)

    def test_log10_positive(self):
        assert log10_hierarchy() > 0

    def test_cancellation_orders_same_as_log10(self):
        assert cancellation_orders_of_magnitude() == pytest.approx(log10_hierarchy(), rel=1e-9)


# ---------------------------------------------------------------------------
# rs1_warp_suppression
# ---------------------------------------------------------------------------

class TestRS1WarpSuppression:
    def test_returns_float(self):
        assert isinstance(rs1_warp_suppression(), float)

    def test_small_suppression(self):
        # e^{-74} is extremely small
        assert rs1_warp_suppression() < 1e-30

    def test_formula(self):
        k_r_pi = 37.0
        expected = math.exp(-2.0 * k_r_pi)
        assert rs1_warp_suppression(k_r_pi) == pytest.approx(expected, rel=1e-10)

    def test_increases_with_smaller_k_r_pi(self):
        assert rs1_warp_suppression(10.0) > rs1_warp_suppression(37.0)

    def test_always_positive(self):
        assert rs1_warp_suppression() > 0


# ---------------------------------------------------------------------------
# net_residual_hierarchy
# ---------------------------------------------------------------------------

class TestNetResidual:
    def test_returns_float(self):
        assert isinstance(net_residual_hierarchy(), float)

    def test_still_large(self):
        # Even after warp suppression residual >> 1e10
        assert net_residual_hierarchy() > 1e10

    def test_smaller_than_raw(self):
        assert net_residual_hierarchy() < hierarchy_ratio()

    def test_log10_positive(self):
        assert log10_net_residual() > 0

    def test_consistent(self):
        rho = kk_vacuum_energy_density_gev4()
        w = rs1_warp_suppression()
        expected = (rho * w) / LAMBDA_OBS_GEV4
        assert net_residual_hierarchy(rho) == pytest.approx(expected, rel=1e-9)


# ---------------------------------------------------------------------------
# brane_tension_cancellation_fraction
# ---------------------------------------------------------------------------

class TestBraneTension:
    def test_returns_float(self):
        assert isinstance(brane_tension_cancellation_fraction(), float)

    def test_extremely_small(self):
        assert brane_tension_cancellation_fraction() < 1e-60

    def test_positive(self):
        assert brane_tension_cancellation_fraction() > 0

    def test_formula(self):
        expected = math.exp(-4.0 * 37.0)
        assert brane_tension_cancellation_fraction() == pytest.approx(expected, rel=1e-10)


# ---------------------------------------------------------------------------
# cc_gate_summary
# ---------------------------------------------------------------------------

class TestCCGateSummary:
    def setup_method(self):
        self.summary = cc_gate_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_pillar_number(self):
        assert self.summary["pillar"] == 792

    def test_gate_label(self):
        assert self.summary["gate"] == "CC_KK_HIERARCHY_ARCHITECTURE_LIMIT"

    def test_hierarchy_log10_present(self):
        assert "hierarchy_log10" in self.summary

    def test_hierarchy_log10_large(self):
        assert self.summary["hierarchy_log10"] > 50

    def test_residual_after_rs1_present(self):
        assert "residual_after_rs1_log10" in self.summary

    def test_cancellation_orders_present(self):
        assert "cancellation_orders" in self.summary

    def test_cancellation_orders_positive(self):
        assert self.summary["cancellation_orders"] > 0

    def test_lean4_entry(self):
        assert "lean4" in self.summary
        assert "1036" in self.summary["lean4"]
        assert "1051" in self.summary["lean4"]

    def test_falsification_condition_present(self):
        assert "falsification_condition" in self.summary

    def test_status_architecture_limit(self):
        assert "ARCHITECTURE_LIMIT" in self.summary["status"]

    def test_alias_callable(self):
        s = CC_KK_SUMMARY()
        assert s["pillar"] == 792
