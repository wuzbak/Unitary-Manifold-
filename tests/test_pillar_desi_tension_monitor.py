# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/pillar_desi_tension_monitor.py."""

from __future__ import annotations

import pytest

from src.core.pillar_desi_tension_monitor import (
    KK_W0_PREDICTION,
    KK_WA_PREDICTION,
    DESI_BASELINE_OBS,
    DESI_TENSION_SIGMA,
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


class TestTensionComputation:
    def test_zero_tension_for_exact_match(self):
        sigma = desi_tension_sigma(-1.0, 0.1, 0.0, 0.1)
        assert sigma == pytest.approx(0.0)

    def test_sigma_increases_with_offset(self):
        s1 = desi_tension_sigma(-0.95, 0.1, -0.1, 0.2)
        s2 = desi_tension_sigma(-0.85, 0.1, -0.3, 0.2)
        assert s2 > s1

    def test_negative_sigma_raises(self):
        with pytest.raises(ValueError):
            desi_tension_sigma(-0.9, -0.1, -0.2, 0.2)
        with pytest.raises(ValueError):
            desi_tension_sigma(-0.9, 0.1, -0.2, 0.0)

    def test_baseline_sigma_matches_named_constant(self):
        calc = desi_tension_sigma(**DESI_BASELINE_OBS)
        assert calc == pytest.approx(DESI_TENSION_SIGMA)


class TestFlags:
    def test_flag_pass(self):
        assert tension_flag(1.9) == "PASS"

    def test_flag_warning_lower_edge(self):
        assert tension_flag(2.01) == "WARNING"

    def test_flag_warning_upper_edge(self):
        assert tension_flag(3.0) == "WARNING"

    def test_flag_critical(self):
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
        for key in ("kk_prediction", "observation", "window", "desi_tension_sigma", "flag", "update_ready"):
            assert key in payload

    def test_monitor_flag_consistency(self):
        payload = monitor_desi_tension()
        assert payload["flag"] == tension_flag(payload["desi_tension_sigma"])

    def test_monitor_update_ready_true(self):
        payload = monitor_desi_tension()
        assert payload["update_ready"] is True

    def test_monitor_baseline_currently_critical(self):
        payload = monitor_desi_tension()
        assert payload["desi_tension_sigma"] > 3.0
        assert payload["flag"] == "CRITICAL"

    def test_monitor_warning_case(self):
        payload = monitor_desi_tension(w0_obs=-0.95, w0_sigma=0.1, wa_obs=-0.4, wa_sigma=0.2)
        assert payload["flag"] == "WARNING"

    def test_monitor_pass_case(self):
        payload = monitor_desi_tension(w0_obs=-1.01, w0_sigma=0.2, wa_obs=-0.05, wa_sigma=0.2)
        assert payload["flag"] == "PASS"


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

    def test_payload_warning_threshold(self):
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
