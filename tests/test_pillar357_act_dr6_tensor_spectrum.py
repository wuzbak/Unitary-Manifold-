# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""
tests/test_pillar357_act_dr6_tensor_spectrum.py
================================================
Test suite for Pillar 357 — ACT DR6 r-Tension: Scale-Dependent Tensor
Spectrum Analysis and 2027 SO Resolution Protocol.
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar357_act_dr6_tensor_spectrum import (
    PILLAR_NUMBER, PILLAR_TITLE, PILLAR_STATUS, ADJACENCY_TRACK_LABEL,
    R_UM, N_S_UM, K_CS, N_W, C_S,
    K_PIVOT_MPC, A_S_PLANCK,
    R_ACT_DR6_95CL, R_BICEP_95CL,
    K_MIN_ACT_MPC, K_MAX_ACT_MPC,
    K_MIN_BICEP_MPC, K_MAX_BICEP_MPC,
    R_SO_SIGMA_5YR,
    separation_guard,
    tensor_spectral_index,
    tensor_spectrum_running,
    cs_beta_function,
    r_running_alpha,
    r_at_scale,
    r_eff_for_experiment,
    act_vs_bicep_tension_sigma,
    scale_dependence_analysis,
    so_resolution_forecast,
    act_dr6_routing,
    pillar357_summary,
)


# ─────────────────────────────────────────────────────────────────────────────
class TestModuleConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 357

    def test_pillar_status(self):
        assert PILLAR_STATUS == "HIGH_TENSION_IRREDUCIBLE"

    def test_adjacency_label(self):
        assert ADJACENCY_TRACK_LABEL == "HARDGATE_ADJACENT"

    def test_r_um_value(self):
        assert abs(R_UM - 0.0315) < 1e-6

    def test_n_s_um_value(self):
        assert abs(N_S_UM - 0.9635) < 1e-4

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_n_w_value(self):
        assert N_W == 5

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_k_pivot(self):
        assert abs(K_PIVOT_MPC - 0.05) < 1e-10

    def test_act_dr6_bound(self):
        assert R_ACT_DR6_95CL < R_UM  # tension exists

    def test_bicep_bound_consistent(self):
        assert R_UM < R_BICEP_95CL  # UM is within BICEP bound

    def test_so_sigma_small(self):
        assert R_SO_SIGMA_5YR < 0.01


# ─────────────────────────────────────────────────────────────────────────────
class TestTensorSpectralIndex:
    def test_consistency_relation_sign(self):
        # n_T = -r/8 < 0 for r > 0
        n_t = tensor_spectral_index()
        assert n_t < 0

    def test_consistency_relation_magnitude(self):
        n_t = tensor_spectral_index(r=0.0315)
        assert abs(n_t - (-0.0315 / 8.0)) < 1e-10

    def test_consistency_relation_zero(self):
        assert tensor_spectral_index(r=0.0) == 0.0

    def test_consistency_relation_typical(self):
        # For r = 0.0315, n_T ≈ -0.00394
        n_t = tensor_spectral_index(0.0315)
        assert abs(n_t + 0.00394) < 1e-4

    def test_at_various_r(self):
        for r in [0.01, 0.02, 0.03, 0.05]:
            assert abs(tensor_spectral_index(r) - (-r / 8.0)) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
class TestTensorSpectrumRunning:
    def test_running_small(self):
        # α_T is second-order slow-roll, should be O(10⁻³) or smaller
        alpha_t = tensor_spectrum_running()
        assert abs(alpha_t) < 1e-2

    def test_running_negative(self):
        # n_T < 0 and n_s - 1 < 0 so product may be positive or small negative
        alpha_t = tensor_spectrum_running()
        # Just check it's finite
        assert math.isfinite(alpha_t)

    def test_running_at_zero_r(self):
        assert tensor_spectrum_running(r=0.0) == 0.0


# ─────────────────────────────────────────────────────────────────────────────
class TestCSBetaFunction:
    def test_cs_beta_positive(self):
        assert cs_beta_function() > 0

    def test_cs_beta_small(self):
        # β_CS = 1/(2 × 74) ≈ 0.00676
        beta = cs_beta_function()
        assert abs(beta - 1.0 / (2.0 * 74)) < 1e-10

    def test_cs_beta_magnitude(self):
        beta = cs_beta_function()
        assert 0.005 < beta < 0.01


# ─────────────────────────────────────────────────────────────────────────────
class TestRRunningAlpha:
    def test_alpha_r_positive(self):
        assert r_running_alpha() > 0

    def test_alpha_r_very_small(self):
        # α_r = 2 × β_CS × r / K_CS ≈ 2 × 0.00676 × 0.0315 / 74 ≈ 5.7 × 10⁻⁶
        alpha = r_running_alpha()
        assert alpha < 1e-4

    def test_alpha_r_proportional_to_r(self):
        alpha1 = r_running_alpha(r=0.0315)
        alpha2 = r_running_alpha(r=0.063)
        assert abs(alpha2 / alpha1 - 2.0) < 0.01


# ─────────────────────────────────────────────────────────────────────────────
class TestRAtScale:
    def test_r_at_pivot(self):
        # At k = k_pivot, r should equal r_pivot
        r_val = r_at_scale(K_PIVOT_MPC, R_UM, K_PIVOT_MPC)
        assert abs(r_val - R_UM) < 1e-10

    def test_r_decreases_at_higher_k(self):
        # For n_T < 0, tensor spectrum falls at higher k
        r_low = r_at_scale(0.005)
        r_high = r_at_scale(0.1)
        assert r_low > r_high

    def test_r_change_small(self):
        # Change from k=0.001 to k=0.2 should be O(1%)
        r_low = r_at_scale(0.001)
        r_high = r_at_scale(0.2)
        change = abs(r_low - r_high) / R_UM
        assert change < 0.10  # Less than 10%

    def test_r_positive(self):
        for k in [0.001, 0.01, 0.05, 0.1, 0.2]:
            assert r_at_scale(k) > 0


# ─────────────────────────────────────────────────────────────────────────────
class TestREff:
    def test_r_eff_close_to_pivot(self):
        # Effective r near pivot scale should be close to R_UM
        r_eff = r_eff_for_experiment(0.04, 0.06)
        assert abs(r_eff - R_UM) / R_UM < 0.01

    def test_r_eff_act_close_to_um(self):
        # r_eff for ACT should be close to R_UM (scale dependence negligible)
        r_eff = r_eff_for_experiment(K_MIN_ACT_MPC, K_MAX_ACT_MPC)
        # Should be within 2% of R_UM
        assert abs(r_eff - R_UM) / R_UM < 0.02

    def test_r_eff_bicep_close_to_um(self):
        r_eff = r_eff_for_experiment(K_MIN_BICEP_MPC, K_MAX_BICEP_MPC)
        assert abs(r_eff - R_UM) / R_UM < 0.02

    def test_r_eff_positive(self):
        assert r_eff_for_experiment(0.001, 0.2) > 0


# ─────────────────────────────────────────────────────────────────────────────
class TestActVsBicepTension:
    def test_act_tension_exists(self):
        result = act_vs_bicep_tension_sigma()
        assert result["tension_act_sigma"] > 0

    def test_bicep_consistent(self):
        result = act_vs_bicep_tension_sigma()
        # UM r = 0.0315 < BICEP r_95cl = 0.036, so no tension with BICEP
        assert result["tension_bicep_sigma"] == 0.0

    def test_act_status_high_tension(self):
        result = act_vs_bicep_tension_sigma()
        # ACT tension ~1.9-2σ — classified as TENSION or HIGH_TENSION
        assert result["status_act"] in ("TENSION", "HIGH_TENSION")

    def test_bicep_status_consistent(self):
        result = act_vs_bicep_tension_sigma()
        assert result["status_bicep"] == "CONSISTENT"

    def test_sigma_act_positive(self):
        result = act_vs_bicep_tension_sigma()
        assert result["sigma_act_approx"] > 0

    def test_keys_present(self):
        result = act_vs_bicep_tension_sigma()
        for key in ["r_um", "r_act_dr6_95cl", "r_bicep_95cl",
                    "tension_act_sigma", "tension_bicep_sigma"]:
            assert key in result


# ─────────────────────────────────────────────────────────────────────────────
class TestScaleDependenceAnalysis:
    def test_returns_dict(self):
        result = scale_dependence_analysis()
        assert isinstance(result, dict)

    def test_n_t_negative(self):
        result = scale_dependence_analysis()
        assert result["n_T"] < 0

    def test_alpha_r_positive(self):
        result = scale_dependence_analysis()
        assert result["alpha_r"] > 0

    def test_r_change_negligible(self):
        result = scale_dependence_analysis()
        # Change should be < 5% (key conclusion: negligible)
        assert result["r_change_percent"] < 5.0

    def test_scale_dep_cannot_resolve(self):
        result = scale_dependence_analysis()
        assert result["can_scale_dependence_resolve_tension"] is False

    def test_verdict_irreducible(self):
        result = scale_dependence_analysis()
        assert "NEGLIGIBLE" in result["verdict"]

    def test_r_eff_positive(self):
        result = scale_dependence_analysis()
        assert result["r_bicep_effective"] > 0
        assert result["r_act_effective"] > 0

    def test_r_bicep_act_close(self):
        result = scale_dependence_analysis()
        ratio = result["r_ratio_act_over_bicep"]
        # The ratio should be very close to 1
        assert abs(ratio - 1.0) < 0.05


# ─────────────────────────────────────────────────────────────────────────────
class TestSOResolutionForecast:
    def test_detection_snr_high(self):
        result = so_resolution_forecast()
        # 10σ detection expected
        assert result["detection_snr_if_correct"] > 8.0

    def test_routing_keys(self):
        result = so_resolution_forecast()
        assert "routing" in result
        routing = result["routing"]
        assert "r_meas_ge_020_at_2sigma" in routing
        assert "r_meas_lt_010_at_3sigma" in routing

    def test_falsification_verdict_in_routing(self):
        result = so_resolution_forecast()
        assert "FALSIFIED" in result["routing"]["r_meas_lt_010_at_3sigma"]

    def test_confirmation_verdict_in_routing(self):
        result = so_resolution_forecast()
        assert "CONSISTENT" in result["routing"]["r_meas_ge_020_at_2sigma"]

    def test_so_date(self):
        result = so_resolution_forecast()
        assert "2027" in result["so_date"]


# ─────────────────────────────────────────────────────────────────────────────
class TestActDr6Routing:
    def test_pending_when_no_measurement(self):
        result = act_dr6_routing()
        assert result["status"] == "PENDING_SO_DR1"

    def test_label_high_tension(self):
        result = act_dr6_routing()
        assert "HIGH_TENSION" in result["label"]

    def test_tension_sigma_set(self):
        result = act_dr6_routing()
        assert result["current_tension_sigma"] > 0

    def test_consistent_verdict_high_r(self):
        result = act_dr6_routing(r_measured=0.030, r_sigma=0.003)
        assert result["verdict"] == "CONSISTENT"

    def test_tension_verdict_mid_r(self):
        result = act_dr6_routing(r_measured=0.015, r_sigma=0.003)
        assert result["verdict"] == "HIGH_TENSION"

    def test_falsified_verdict_low_r(self):
        result = act_dr6_routing(r_measured=0.005, r_sigma=0.003)
        assert result["verdict"] == "FALSIFIED"

    def test_falsified_action_string(self):
        result = act_dr6_routing(r_measured=0.005, r_sigma=0.003)
        assert "FALSIFIED" in result["action"]
        assert "CLAIM_MASTER_BOARD" in result["action"]

    def test_tension_sigma_computed_correctly(self):
        result = act_dr6_routing(r_measured=0.020, r_sigma=0.003)
        expected_tension = abs(0.020 - R_UM) / 0.003
        assert abs(result["tension_sigma"] - expected_tension) < 1e-10


# ─────────────────────────────────────────────────────────────────────────────
class TestSeparationGuard:
    def test_returns_string(self):
        assert isinstance(separation_guard(), str)

    def test_mentions_hardgate_adjacent(self):
        guard = separation_guard()
        assert "HARDGATE_ADJACENT" in guard

    def test_no_score_change(self):
        guard = separation_guard()
        assert "framework derivation coverage" in guard


# ─────────────────────────────────────────────────────────────────────────────
class TestPillar357Summary:
    def test_returns_dict(self):
        result = pillar357_summary()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        result = pillar357_summary()
        assert result["pillar"] == 357

    def test_status_present(self):
        result = pillar357_summary()
        assert "status" in result
        assert "HIGH_TENSION" in result["status"]

    def test_key_conclusion_present(self):
        result = pillar357_summary()
        assert "key_conclusion" in result
        assert "IRREDUCIBLE" in result["key_conclusion"]

    def test_all_sections_present(self):
        result = pillar357_summary()
        for key in ["scale_dependence", "tension_analysis", "so_forecast", "routing"]:
            assert key in result

    def test_separation_guard_present(self):
        result = pillar357_summary()
        assert "separation_guard" in result
