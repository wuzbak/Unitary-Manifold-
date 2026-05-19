# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/pillar255_open_gap_residual_dashboard.py (~50 tests)."""
from __future__ import annotations

import math

import pytest

from src.core.pillar255_open_gap_residual_dashboard import (
    ADJACENCY_TRACK_LABEL,
    C_S,
    K_CS,
    N_W,
    closure_priority_ranking,
    dashboard_report,
    full_dashboard,
    monitoring_g3_desi_status,
    monitoring_juno_status,
    residual_a3_status,
    residual_sc2_status,
    residual_sc4_status,
    residual_t3_status,
    separation_guard,
)


# ===========================================================================
# 1. Module-level constants
# ===========================================================================

class TestConstants:
    def test_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert C_S == pytest.approx(12.0 / 37.0)


# ===========================================================================
# 2. separation_guard
# ===========================================================================

def test_separation_guard_returns_true():
    assert separation_guard() is True


# ===========================================================================
# 3. residual_sc2_status
# ===========================================================================

class TestResidualSC2Status:
    def setup_method(self):
        self.status = residual_sc2_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_residual_id(self):
        assert self.status["residual_id"] == "SC2"

    def test_alpha_gw_interval_present(self):
        assert "alpha_gw_interval" in self.status

    def test_alpha_gw_interval_low(self):
        lo, hi = self.status["alpha_gw_interval"]
        assert lo == pytest.approx(4.2e-10)

    def test_alpha_gw_interval_high(self):
        lo, hi = self.status["alpha_gw_interval"]
        assert hi == pytest.approx(4.8e-10)

    def test_rs1_estimate(self):
        assert self.status["rs1_estimate"] == pytest.approx(4.33e-65, rel=1e-3)

    def test_10d_bridge_value_in_band(self):
        val = self.status["value_10d_bridge"]
        lo = self.status["alpha_gw_interval_low"]
        hi = self.status["alpha_gw_interval_high"]
        assert lo <= val <= hi

    def test_in_band_true(self):
        assert self.status["in_band"] is True

    def test_status_field(self):
        assert self.status["status"] in {
            "CLOSED_WITH_10D_HARDGATE",
            "CLOSED_FULL_POINT_DERIVATION",
        }
        assert self.status["full_chain_verdict"] in {"PASS", "TENSION", "FALSIFIED"}

    def test_closure_blocker_present(self):
        assert "closure_blocker" in self.status
        assert len(self.status["closure_blocker"]) > 0

    def test_adjacency_label(self):
        assert self.status["adjacency_label"] == ADJACENCY_TRACK_LABEL


# ===========================================================================
# 4. residual_sc4_status
# ===========================================================================

class TestResidualSC4Status:
    def setup_method(self):
        self.status = residual_sc4_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_residual_id(self):
        assert self.status["residual_id"] == "SC4"

    def test_n_flux_current(self):
        assert self.status["n_flux_current"] == 37

    def test_n_flux_required(self):
        assert self.status["n_flux_required"] == 61

    def test_gap_fraction(self):
        # (61 - 37) / 37 ≈ 0.6486
        expected = (61 - 37) / 37
        assert self.status["gap_fraction"] == pytest.approx(expected, rel=1e-9)

    def test_gap_percent_approximately_65(self):
        assert 60.0 < self.status["gap_percent"] < 70.0

    def test_status_field(self):
        assert self.status["status"] in {"ARCHITECTURE_LIMIT", "CLOSED_WITH_EFFECTIVE_FLUX_CHANNELS"}
        assert "effective_flux_scan_status" in self.status

    def test_adjacency_label(self):
        assert self.status["adjacency_label"] == ADJACENCY_TRACK_LABEL


# ===========================================================================
# 5. residual_a3_status
# ===========================================================================

class TestResidualA3Status:
    def setup_method(self):
        self.status = residual_a3_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_residual_id(self):
        assert self.status["residual_id"] == "A3"

    def test_tuning_delta_positive(self):
        assert self.status["tuning_Delta"] > 0.0

    def test_naturalness_threshold(self):
        assert self.status["naturalness_threshold"] == pytest.approx(100.0)

    def test_partial_closure_is_bool(self):
        assert isinstance(self.status["partial_closure"], bool)

    def test_status_derived_partial_or_architecture_limit(self):
        assert self.status["status"] in (
            "DERIVED_PARTIAL",
            "ARCHITECTURE_LIMIT_CERTIFIED",
            "DERIVED_COMPLETE",
            "DERIVED_WITH_RESIDUAL",
        )
        assert self.status["extended_overall_status"] in {"DERIVED_COMPLETE", "DERIVED_WITH_RESIDUAL"}

    def test_convergence_ratio_present(self):
        assert "convergence_ratio" in self.status
        assert math.isfinite(self.status["convergence_ratio"])

    def test_m_kk_gev_positive(self):
        assert self.status["M_KK_GeV"] > 0.0

    def test_adjacency_label(self):
        assert self.status["adjacency_label"] == ADJACENCY_TRACK_LABEL

    def test_custom_params(self):
        result = residual_a3_status(k=0.05, R=20.0, N_modes=5)
        assert result["k"] == pytest.approx(0.05)
        assert result["N_modes"] == 5


# ===========================================================================
# 6. residual_t3_status
# ===========================================================================

class TestResidualT3Status:
    def setup_method(self):
        self.status = residual_t3_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_residual_id(self):
        assert self.status["residual_id"] == "T3"

    def test_lapse_identification_present(self):
        assert "lapse_identification" in self.status
        assert "phi" in self.status["lapse_identification"].lower()

    def test_lapse_deviation_percent(self):
        assert self.status["lapse_deviation_percent"] == pytest.approx(0.6, rel=1e-9)

    def test_kinematic_closure_true(self):
        assert self.status["kinematic_closure"] is True

    def test_bssn_full_evolution_is_bool(self):
        assert isinstance(self.status["bssn_full_evolution"], bool)

    def test_status_reflects_live_closure(self):
        assert self.status["status"] in {"PARTIALLY_CLOSED", "CLOSED_REDUCED_SECTOR"}
        assert self.status["dynamical_verdict"] in {"PASS", "TENSION", "FALSIFIED"}

    def test_closure_blocker_present(self):
        assert "closure_blocker" in self.status

    def test_adjacency_label(self):
        assert self.status["adjacency_label"] == ADJACENCY_TRACK_LABEL


# ===========================================================================
# 7. monitoring_g3_desi_status
# ===========================================================================

class TestMonitoringG3DesiStatus:
    def setup_method(self):
        self.status = monitoring_g3_desi_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_monitor_id(self):
        assert self.status["monitor_id"] == "G3"

    def test_desi_tension_sigma(self):
        assert self.status["desi_tension_sigma"] == pytest.approx(2.75)

    def test_um_prediction_wa_zero(self):
        assert self.status["um_prediction_wa"] == pytest.approx(0.0)

    def test_not_yet_falsified(self):
        # 2.75σ < 3.0σ
        assert self.status["is_falsified"] is False

    def test_status_high_tension(self):
        assert self.status["status"] == "HIGH_TENSION"

    def test_falsification_threshold(self):
        assert self.status["falsification_threshold_sigma"] == pytest.approx(3.0)

    def test_adjacency_label(self):
        assert self.status["adjacency_label"] == ADJACENCY_TRACK_LABEL


# ===========================================================================
# 8. monitoring_juno_status
# ===========================================================================

class TestMonitoringJunoStatus:
    def setup_method(self):
        self.status = monitoring_juno_status()

    def test_returns_dict(self):
        assert isinstance(self.status, dict)

    def test_monitor_id(self):
        assert self.status["monitor_id"] == "JUNO"

    def test_um_prediction_dm31(self):
        assert self.status["um_prediction_dm31_eV2"] == pytest.approx(2.400e-3, rel=1e-6)

    def test_pdg_central_dm31(self):
        assert self.status["pdg_central_dm31_eV2"] == pytest.approx(2.453e-3, rel=1e-6)

    def test_fractional_deviation_approx_2_percent(self):
        # (2.453 - 2.400) / 2.453 ≈ 2.16%
        assert 1.5 < self.status["fractional_deviation_percent"] < 3.0

    def test_tension_sigma_approx_4_4(self):
        # If JUNO confirms at 0.5% → ~4.4σ
        assert self.status["tension_sigma_if_confirmed"] == pytest.approx(4.4, abs=0.15)

    def test_is_falsified_if_confirmed(self):
        assert self.status["is_falsified_if_confirmed"] is True

    def test_status_field(self):
        assert "RISK" in self.status["status"] or "FALSIF" in self.status["status"]

    def test_juno_precision_target(self):
        assert self.status["juno_precision_target"] == pytest.approx(0.005)

    def test_adjacency_label(self):
        assert self.status["adjacency_label"] == ADJACENCY_TRACK_LABEL


# ===========================================================================
# 9. full_dashboard
# ===========================================================================

class TestFullDashboard:
    def setup_method(self):
        self.dashboard = full_dashboard()

    def test_returns_dict(self):
        assert isinstance(self.dashboard, dict)

    def test_has_residuals(self):
        assert "residuals" in self.dashboard
        for key in ("SC2", "SC4", "A3", "T3"):
            assert key in self.dashboard["residuals"]

    def test_has_monitoring(self):
        assert "monitoring" in self.dashboard
        for key in ("G3", "JUNO"):
            assert key in self.dashboard["monitoring"]

    def test_framework_constants(self):
        fc = self.dashboard["framework_constants"]
        assert fc["N_W"] == N_W
        assert fc["K_CS"] == K_CS
        assert fc["C_S"] == pytest.approx(C_S)

    def test_separation_guard_passed(self):
        assert self.dashboard["separation_guard_passed"] is True

    def test_adjacency_label(self):
        assert self.dashboard["adjacency_label"] == ADJACENCY_TRACK_LABEL


# ===========================================================================
# 10. closure_priority_ranking
# ===========================================================================

class TestClosurePriorityRanking:
    def setup_method(self):
        self.ranking = closure_priority_ranking()

    def test_returns_list(self):
        assert isinstance(self.ranking, list)

    def test_contains_all_residuals(self):
        for rid in ("T3", "A3", "SC2", "SC4"):
            assert rid in self.ranking

    def test_length(self):
        assert len(self.ranking) == 4

    def test_t3_most_tractable(self):
        # T3 (partially closed) should be first
        assert self.ranking[0] == "T3"

    def test_sc4_least_tractable(self):
        # SC4 (architecture limit) should be last
        assert self.ranking[-1] == "SC4"


# ===========================================================================
# 11. dashboard_report
# ===========================================================================

class TestDashboardReport:
    def setup_method(self):
        self.report = dashboard_report()

    def test_returns_string(self):
        assert isinstance(self.report, str)

    def test_contains_sc2(self):
        assert "SC2" in self.report

    def test_contains_sc4(self):
        assert "SC4" in self.report

    def test_contains_a3(self):
        assert "A3" in self.report

    def test_contains_t3(self):
        assert "T3" in self.report

    def test_contains_g3(self):
        assert "G3" in self.report

    def test_contains_juno(self):
        assert "JUNO" in self.report

    def test_contains_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL in self.report


def test_v11_5_residual_tightening_overlay_aggregates_all_pillars():
    """Pillar 255 surfaces the v11.5 wave overlay without disturbing fields."""
    from src.core.pillar255_open_gap_residual_dashboard import (
        full_dashboard,
        v11_5_residual_tightening_overlay,
    )

    overlay = v11_5_residual_tightening_overlay()
    assert overlay["wave_id"] == "v11.5_RESIDUAL_TIGHTENING_WAVE"
    assert overlay["adjacency_label"] == "NON_HARDGATE_ADJACENT"
    expected_keys = {
        "JUNO", "A3", "T3", "CMB_PEAK", "SC4",
        "NW_OBSTRUCTION", "SC2", "DESI_DR3_DRILL",
    }
    assert set(overlay["tightening_modules"].keys()) == expected_keys

    # Each overlay module reports its own pillar number under 'pillar'
    pillars = {
        mod.get("pillar") for mod in overlay["tightening_modules"].values()
    }
    assert pillars == {274, 275, 276, 277, 278, 279, 280, 281}

    # Original residual / monitoring fields are untouched
    fd = full_dashboard()
    assert set(fd["residuals"].keys()) == {"SC2", "SC4", "A3", "T3"}
    assert set(fd["monitoring"].keys()) == {"G3", "JUNO"}


def test_v11_5_overlay_no_hardgate_drift():
    """v11.5 overlay must not promote any hardgate label."""
    from src.core.pillar255_open_gap_residual_dashboard import (
        v11_5_residual_tightening_overlay,
    )

    overlay = v11_5_residual_tightening_overlay()
    for mod in overlay["tightening_modules"].values():
        sg = mod.get("separation_guard")
        assert sg is not None
        assert sg["is_hardgate"] is False
        assert sg["alters_falsifier_window"] is False
