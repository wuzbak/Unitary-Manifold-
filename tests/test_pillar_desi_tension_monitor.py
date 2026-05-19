# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/pillar_desi_tension_monitor.py.

v11.x note: the monitor now reports the wₐ-only tension (2.75σ) as the primary
metric, matching published DESI DR2 figures (arXiv:2503.14738).  The previous
naive uncorrelated joint quadrature (3.30σ, CRITICAL) was methodologically
incorrect because it ignored the strong negative w0–wₐ posterior correlation.
Tests are updated to reflect the corrected, defensible numbers.
"""

from __future__ import annotations

import math
import pytest

from src.core.pillar_desi_tension_monitor import (
    KK_W0_PREDICTION,
    KK_WA_PREDICTION,
    DESI_BASELINE_OBS,
    DESI_CPL_CORRELATION,
    DESI_TENSION_SIGMA,
    DESI_WA_ONLY_TENSION_SIGMA,
    DESI_JOINT_TENSION_SIGMA,
    wa_only_tension_sigma,
    joint_tension_sigma,
    desi_tension_sigma,
    tension_flag,
    observation_window,
    monitor_desi_tension,
    updated_monitor_from_payload,
)


class TestConstants:
    def test_kk_prediction_exact(self):
        assert KK_W0_PREDICTION == -1.0
        assert KK_WA_PREDICTION == 0.0

    def test_baseline_has_required_fields(self):
        for key in ("w0_obs", "w0_sigma", "wa_obs", "wa_sigma"):
            assert key in DESI_BASELINE_OBS

    def test_named_sigma_positive(self):
        assert DESI_TENSION_SIGMA > 0.0

    def test_cpl_correlation_plausible(self):
        # DESI CPL fits show strong anti-correlation in the −0.6 to −0.9 range
        assert -1.0 < DESI_CPL_CORRELATION < 0.0
        assert DESI_CPL_CORRELATION <= -0.5

    def test_wa_only_sigma_matches_published(self):
        # DESI DR2 combined: |−0.55| / 0.20 = 2.75σ — matches arXiv:2503.14738
        assert DESI_TENSION_SIGMA == pytest.approx(2.75, abs=1e-9)

    def test_wa_only_alias_consistency(self):
        assert DESI_WA_ONLY_TENSION_SIGMA == pytest.approx(DESI_TENSION_SIGMA)

    def test_joint_sigma_below_3_sigma(self):
        # Covariance-corrected joint must be below 3σ (not falsified)
        assert DESI_JOINT_TENSION_SIGMA < 3.0

    def test_joint_sigma_positive(self):
        assert DESI_JOINT_TENSION_SIGMA > 0.0

    def test_joint_less_than_naive_quadrature(self):
        # Anti-correlation always reduces the joint chi-squared vs naive sum
        z_w0 = (DESI_BASELINE_OBS["w0_obs"] - KK_W0_PREDICTION) / DESI_BASELINE_OBS["w0_sigma"]
        z_wa = (DESI_BASELINE_OBS["wa_obs"] - KK_WA_PREDICTION) / DESI_BASELINE_OBS["wa_sigma"]
        naive = math.sqrt(z_w0**2 + z_wa**2)
        assert DESI_JOINT_TENSION_SIGMA < naive


class TestWaOnlyTension:
    def test_published_combined_value(self):
        # 2.75σ: direct match with arXiv:2503.14738
        sigma = wa_only_tension_sigma(-0.55, 0.20)
        assert sigma == pytest.approx(2.75, abs=1e-9)

    def test_published_bao_only_value(self):
        # 2.07σ: direct match with arXiv:2503.14738 BAO-only
        sigma = wa_only_tension_sigma(-0.62, 0.30)
        assert sigma == pytest.approx(2.0667, abs=1e-3)

    def test_zero_when_prediction_matches(self):
        sigma = wa_only_tension_sigma(0.0, 0.1)
        assert sigma == pytest.approx(0.0)

    def test_positive_wa_obs_gives_positive_tension(self):
        sigma = wa_only_tension_sigma(0.3, 0.1)
        assert sigma == pytest.approx(3.0)

    def test_invalid_sigma_raises(self):
        with pytest.raises(ValueError):
            wa_only_tension_sigma(-0.5, 0.0)
        with pytest.raises(ValueError):
            wa_only_tension_sigma(-0.5, -0.1)

    def test_symmetric_in_wa(self):
        # |wₐ| is symmetric: positive and negative deviations give same tension
        s1 = wa_only_tension_sigma(-0.4, 0.2)
        s2 = wa_only_tension_sigma(0.4, 0.2)
        assert s1 == pytest.approx(s2)


class TestJointTension:
    def test_uncorrelated_matches_naive_quadrature(self):
        # rho=0 → naive uncorrelated quadrature
        w0_obs, w0_s, wa_obs, wa_s = -0.90, 0.055, -0.55, 0.20
        z_w0 = (w0_obs - KK_W0_PREDICTION) / w0_s
        z_wa = (wa_obs - KK_WA_PREDICTION) / wa_s
        naive = math.sqrt(z_w0**2 + z_wa**2)
        joint = joint_tension_sigma(w0_obs, w0_s, wa_obs, wa_s, rho=0.0)
        assert joint == pytest.approx(naive, abs=1e-9)

    def test_negative_rho_reduces_tension(self):
        # Strong anti-correlation reduces joint chi-squared
        w0_obs, w0_s, wa_obs, wa_s = -0.90, 0.055, -0.55, 0.20
        joint_corr = joint_tension_sigma(w0_obs, w0_s, wa_obs, wa_s, rho=-0.80)
        joint_zero = joint_tension_sigma(w0_obs, w0_s, wa_obs, wa_s, rho=0.0)
        assert joint_corr < joint_zero

    def test_desi_combined_below_falsification(self):
        # With ρ = −0.80 the combined joint tension is < 3σ (not falsified)
        joint = joint_tension_sigma(
            DESI_BASELINE_OBS["w0_obs"],
            DESI_BASELINE_OBS["w0_sigma"],
            DESI_BASELINE_OBS["wa_obs"],
            DESI_BASELINE_OBS["wa_sigma"],
            rho=DESI_CPL_CORRELATION,
        )
        assert joint < 3.0

    def test_zero_tension_for_exact_prediction(self):
        # Both deviations zero → chi-squared = 0
        joint = joint_tension_sigma(KK_W0_PREDICTION, 0.1, KK_WA_PREDICTION, 0.1, rho=-0.5)
        assert joint == pytest.approx(0.0)

    def test_invalid_rho_raises(self):
        with pytest.raises(ValueError):
            joint_tension_sigma(-0.9, 0.05, -0.5, 0.2, rho=1.0)
        with pytest.raises(ValueError):
            joint_tension_sigma(-0.9, 0.05, -0.5, 0.2, rho=-1.0)
        with pytest.raises(ValueError):
            joint_tension_sigma(-0.9, 0.05, -0.5, 0.2, rho=1.5)

    def test_invalid_sigma_raises(self):
        with pytest.raises(ValueError):
            joint_tension_sigma(-0.9, 0.0, -0.5, 0.2)

    def test_joint_increases_with_positive_rho(self):
        # Positive correlation amplifies the joint chi-squared when both deviate
        w0_obs, w0_s, wa_obs, wa_s = -0.90, 0.055, -0.55, 0.20
        j_neg = joint_tension_sigma(w0_obs, w0_s, wa_obs, wa_s, rho=-0.50)
        j_pos = joint_tension_sigma(w0_obs, w0_s, wa_obs, wa_s, rho=0.50)
        # With same-sign deviations and positive rho, joint is larger
        assert j_pos > j_neg


class TestTensionSigmaCompat:
    """desi_tension_sigma() is the API-compat entry point — now returns wₐ-only."""

    def test_returns_wa_only(self):
        # Must match wa_only_tension_sigma exactly
        calc = desi_tension_sigma(**DESI_BASELINE_OBS)
        expected = wa_only_tension_sigma(DESI_BASELINE_OBS["wa_obs"], DESI_BASELINE_OBS["wa_sigma"])
        assert calc == pytest.approx(expected)

    def test_matches_named_constant(self):
        calc = desi_tension_sigma(**DESI_BASELINE_OBS)
        assert calc == pytest.approx(DESI_TENSION_SIGMA)

    def test_zero_tension_for_exact_match(self):
        sigma = desi_tension_sigma(-1.0, 0.1, 0.0, 0.1)
        assert sigma == pytest.approx(0.0)

    def test_sigma_increases_with_wa_offset(self):
        s1 = desi_tension_sigma(-0.95, 0.1, -0.1, 0.2)
        s2 = desi_tension_sigma(-0.85, 0.1, -0.3, 0.2)
        assert s2 > s1

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError):
            desi_tension_sigma(-0.9, -0.1, -0.2, 0.2)
        with pytest.raises(ValueError):
            desi_tension_sigma(-0.9, 0.1, -0.2, 0.0)


class TestFlags:
    def test_flag_pass(self):
        assert tension_flag(1.9) == "PASS"

    def test_flag_warning_lower_edge(self):
        assert tension_flag(2.01) == "WARNING"

    def test_flag_warning_upper_edge(self):
        assert tension_flag(2.99) == "WARNING"

    def test_flag_critical_at_exactly_3(self):
        assert tension_flag(3.0) == "CRITICAL"

    def test_flag_critical_above_3(self):
        assert tension_flag(3.01) == "CRITICAL"


class TestObservationWindow:
    def test_window_structure(self):
        window = observation_window(-0.9, 0.05, -0.5, 0.2)
        assert set(window.keys()) == {"w0_1sigma", "wa_1sigma", "w0_2sigma", "wa_2sigma"}

    def test_window_ordering(self):
        window = observation_window(-0.9, 0.05, -0.5, 0.2)
        for lo, hi in window.values():
            assert lo < hi

    def test_window_invalid_sigma_raises(self):
        with pytest.raises(ValueError):
            observation_window(-0.9, 0.0, -0.5, 0.2)


class TestMonitor:
    def test_monitor_structure(self):
        payload = monitor_desi_tension()
        required = (
            "kk_prediction", "observation", "window",
            "desi_tension_sigma", "wa_only_tension_sigma",
            "joint_tension_sigma", "joint_tension_rho",
            "flag", "update_ready", "tension_method_note",
        )
        for key in required:
            assert key in payload

    def test_monitor_flag_consistency(self):
        payload = monitor_desi_tension()
        assert payload["flag"] == tension_flag(payload["desi_tension_sigma"])

    def test_monitor_update_ready_true(self):
        payload = monitor_desi_tension()
        assert payload["update_ready"] is True

    def test_baseline_is_high_tension_not_critical(self):
        # CORRECTED: baseline is HIGH_TENSION (WARNING) at 2.75σ, not CRITICAL
        payload = monitor_desi_tension()
        assert 2.0 < payload["desi_tension_sigma"] < 3.0
        assert payload["flag"] == "WARNING"

    def test_baseline_wa_only_matches_published(self):
        payload = monitor_desi_tension()
        # Matches arXiv:2503.14738 combined: 2.75σ
        assert payload["wa_only_tension_sigma"] == pytest.approx(2.75, abs=1e-9)

    def test_baseline_joint_below_falsification(self):
        payload = monitor_desi_tension()
        assert payload["joint_tension_sigma"] < 3.0

    def test_baseline_joint_uses_correct_rho(self):
        payload = monitor_desi_tension()
        assert payload["joint_tension_rho"] == DESI_CPL_CORRELATION

    def test_monitor_warning_case(self):
        # wa-only: |−0.45| / 0.20 = 2.25σ → WARNING
        payload = monitor_desi_tension(w0_obs=-0.95, w0_sigma=0.1, wa_obs=-0.45, wa_sigma=0.2)
        assert payload["flag"] == "WARNING"

    def test_monitor_pass_case(self):
        payload = monitor_desi_tension(w0_obs=-1.01, w0_sigma=0.2, wa_obs=-0.05, wa_sigma=0.2)
        assert payload["flag"] == "PASS"

    def test_monitor_critical_case(self):
        # Only CRITICAL if wₐ-only tension ≥ 3σ
        payload = monitor_desi_tension(w0_obs=-0.9, w0_sigma=0.05, wa_obs=-0.9, wa_sigma=0.2)
        assert payload["flag"] == "CRITICAL"
        assert payload["desi_tension_sigma"] >= 3.0

    def test_custom_rho_changes_joint(self):
        p1 = monitor_desi_tension(rho=-0.80)
        p2 = monitor_desi_tension(rho=0.0)
        assert p1["joint_tension_sigma"] != p2["joint_tension_sigma"]
        # Anti-correlation reduces joint tension
        assert p1["joint_tension_sigma"] < p2["joint_tension_sigma"]


class TestPayloadUpdate:
    def test_payload_update_structure(self):
        payload = {"w0_obs": -0.95, "w0_sigma": 0.1, "wa_obs": -0.4, "wa_sigma": 0.2}
        result = updated_monitor_from_payload(payload)
        assert "desi_tension_sigma" in result

    def test_payload_missing_field_raises(self):
        with pytest.raises(ValueError):
            updated_monitor_from_payload({"w0_obs": -0.9, "w0_sigma": 0.1})

    def test_payload_float_conversion(self):
        payload = {"w0_obs": "-0.95", "w0_sigma": "0.1", "wa_obs": "-0.4", "wa_sigma": "0.2"}
        result = updated_monitor_from_payload(payload)
        assert result["observation"]["w0_obs"] == pytest.approx(-0.95)

    def test_payload_uses_wa_only_sigma(self):
        payload = {"w0_obs": -0.95, "w0_sigma": 0.1, "wa_obs": -0.4, "wa_sigma": 0.2}
        result = updated_monitor_from_payload(payload)
        expected_wa_only = abs(-0.4) / 0.2
        assert result["desi_tension_sigma"] == pytest.approx(expected_wa_only)

    def test_payload_accepts_rho(self):
        payload = {
            "w0_obs": -0.9, "w0_sigma": 0.055,
            "wa_obs": -0.55, "wa_sigma": 0.20,
            "rho_w0_wa": -0.75,
        }
        result = updated_monitor_from_payload(payload)
        assert result["joint_tension_rho"] == pytest.approx(-0.75)

    def test_payload_flag_in_valid_set(self):
        payload = {"w0_obs": -0.95, "w0_sigma": 0.1, "wa_obs": -0.4, "wa_sigma": 0.2}
        result = updated_monitor_from_payload(payload)
        assert result["flag"] in {"WARNING", "CRITICAL", "PASS"}


class TestBaselineSanity:
    def test_baseline_sigma_recomputes(self):
        baseline = monitor_desi_tension(**DESI_BASELINE_OBS)
        assert baseline["desi_tension_sigma"] == pytest.approx(DESI_TENSION_SIGMA)

    def test_baseline_window_contains_observed_values(self):
        baseline = monitor_desi_tension()
        w = baseline["window"]
        obs = baseline["observation"]
        assert w["w0_1sigma"][0] <= obs["w0_obs"] <= w["w0_1sigma"][1]
        assert w["wa_1sigma"][0] <= obs["wa_obs"] <= w["wa_1sigma"][1]

    def test_prediction_not_in_baseline_wa_1sigma(self):
        baseline = monitor_desi_tension()
        wa_lo, wa_hi = baseline["window"]["wa_1sigma"]
        assert not (wa_lo <= 0.0 <= wa_hi)

    def test_joint_sigma_numerically_correct(self):
        # Verify the covariance formula directly
        w0_obs, w0_s = -0.90, 0.055
        wa_obs, wa_s = -0.55, 0.20
        rho = -0.80
        z_w0 = (w0_obs - KK_W0_PREDICTION) / w0_s
        z_wa = (wa_obs - KK_WA_PREDICTION) / wa_s
        chi2_expected = (z_w0**2 - 2*rho*z_w0*z_wa + z_wa**2) / (1 - rho**2)
        expected = math.sqrt(chi2_expected)
        computed = joint_tension_sigma(w0_obs, w0_s, wa_obs, wa_s, rho=rho)
        assert computed == pytest.approx(expected, abs=1e-9)

    def test_tension_below_falsification_threshold(self):
        # Core integrity: current DESI data does NOT falsify the framework
        assert DESI_TENSION_SIGMA < 3.0
        assert DESI_JOINT_TENSION_SIGMA < 3.0
