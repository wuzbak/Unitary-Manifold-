# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar222_nanotechnology_control_systems.py — Pillar 222 test suite."""
import pytest

from src.core.pillar222_nanotechnology_control_systems import (
    N_W,
    K_CS,
    PHI0,
    BOLTZMANN_SI,
    BODY_TEMPERATURE_K,
    WATER_VISCOSITY_BODY_PA_S,
    stokes_einstein_diffusion,
    nanoparticle_diffusion_time,
    first_order_nano_release,
    pid_nano_positioning,
    nanosensor_snr_db,
    nanotech_control_readiness,
    pillar222_summary,
)


class TestConstants:
    def test_core_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert abs(PHI0 - 0.739085) < 1e-6

    def test_physical_constants(self):
        assert BOLTZMANN_SI > 0
        assert BODY_TEMPERATURE_K > 300
        assert WATER_VISCOSITY_BODY_PA_S > 0


class TestDiffusion:
    def test_diffusion_positive(self):
        r = stokes_einstein_diffusion(50.0)
        assert r["diffusion_m2_s"] > 0

    def test_smaller_radius_faster_diffusion(self):
        d1 = stokes_einstein_diffusion(20.0)["diffusion_m2_s"]
        d2 = stokes_einstein_diffusion(80.0)["diffusion_m2_s"]
        assert d1 > d2

    def test_diffusion_time_positive(self):
        r = nanoparticle_diffusion_time(100.0, 50.0)
        assert r["diffusion_time_s"] > 0

    def test_longer_distance_longer_time(self):
        t1 = nanoparticle_diffusion_time(50.0, 50.0)["diffusion_time_s"]
        t2 = nanoparticle_diffusion_time(100.0, 50.0)["diffusion_time_s"]
        assert t2 > t1

    def test_invalid_radius_raises(self):
        with pytest.raises(ValueError):
            stokes_einstein_diffusion(0.0)


class TestRelease:
    def test_release_conservation(self):
        r = first_order_nano_release(10.0, 8.0, 8.0)
        assert abs((r["remaining_mg"] + r["released_mg"]) - 10.0) < 1e-10

    def test_half_life_point(self):
        r = first_order_nano_release(10.0, 6.0, 6.0)
        assert abs(r["remaining_mg"] - 5.0) < 1e-6

    def test_zero_time_no_release(self):
        r = first_order_nano_release(10.0, 6.0, 0.0)
        assert abs(r["released_fraction"]) < 1e-12


class TestPidPositioning:
    def test_pid_returns_keys(self):
        r = pid_nano_positioning(setpoint_nm=20.0, kp=0.3, ki=8.0, kd=0.0003)
        for k in ("final_error_nm", "rmse_nm", "overshoot_nm", "settling_time_ms"):
            assert k in r

    def test_pid_tracks_setpoint(self):
        r = pid_nano_positioning(setpoint_nm=20.0, kp=0.5, ki=12.0, kd=0.0005)
        assert abs(r["final_error_nm"]) < 2.0

    def test_invalid_gain_raises(self):
        with pytest.raises(ValueError):
            pid_nano_positioning(setpoint_nm=10.0, kp=-1.0, ki=0.0, kd=0.0)


class TestSNRAndReadiness:
    def test_snr_db_monotonic(self):
        s1 = nanosensor_snr_db(1.0, 0.1)
        s2 = nanosensor_snr_db(2.0, 0.1)
        assert s2 > s1

    def test_zero_signal_negative_infinity(self):
        assert nanosensor_snr_db(0.0, 0.1) == float("-inf")

    def test_readiness_range(self):
        r = nanotech_control_readiness(precision_nm=2.0, settling_time_ms=8.0, snr_db=35.0, cytotoxicity_index=0.1)
        assert 0.0 <= r["readiness_score"] <= 1.0

    def test_worse_safety_reduces_readiness(self):
        good = nanotech_control_readiness(2.0, 8.0, 35.0, 0.05)["readiness_score"]
        bad = nanotech_control_readiness(2.0, 8.0, 35.0, 0.8)["readiness_score"]
        assert bad < good


class TestSummary:
    def test_summary_shape(self):
        s = pillar222_summary()
        assert s["pillar"] == 222
        assert s["diffusion_m2_s_at_50nm"] > 0
        assert s["readiness_score_example"] >= 0
        assert isinstance(s["epistemic_note"], str)
