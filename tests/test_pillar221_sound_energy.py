# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar221_sound_energy.py — Pillar 221 test suite."""
import math
import pytest

from src.core.pillar221_sound_energy import (
    N_W,
    K_CS,
    PHI0,
    BRAIDED_SOUND_SPEED,
    SOUND_SPEED_AIR_20C,
    SOUND_SPEED_WATER_20C,
    SOUND_SPEED_SOFT_TISSUE,
    AIR_DENSITY_20C,
    WATER_DENSITY_20C,
    REFERENCE_PRESSURE_PA,
    FDA_MECHANICAL_INDEX_LIMIT,
    spl_from_pressure_rms,
    pressure_rms_from_spl,
    acoustic_intensity_from_spl,
    acoustic_radiation_force,
    piezoelectric_harvested_power,
    ultrasound_attenuation,
    cavitation_mechanical_index,
    ultrasound_safety_window,
    sound_energy_use_matrix,
    pillar221_summary,
)


class TestConstants:
    def test_core_constants(self):
        assert N_W == 5
        assert K_CS == 74
        assert abs(PHI0 - 0.739085) < 1e-6
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-12

    def test_sound_speeds_order(self):
        assert SOUND_SPEED_AIR_20C < SOUND_SPEED_WATER_20C < SOUND_SPEED_SOFT_TISSUE + 200

    def test_reference_pressure(self):
        assert REFERENCE_PRESSURE_PA == 20e-6
        assert FDA_MECHANICAL_INDEX_LIMIT == 1.9


class TestSplConversions:
    def test_reference_pressure_is_zero_db(self):
        assert abs(spl_from_pressure_rms(REFERENCE_PRESSURE_PA)) < 1e-12

    def test_round_trip_conversion(self):
        p = 0.2
        spl = spl_from_pressure_rms(p)
        p2 = pressure_rms_from_spl(spl)
        assert abs(p - p2) / p < 1e-12

    def test_raises_on_nonpositive_pressure(self):
        with pytest.raises(ValueError):
            spl_from_pressure_rms(0.0)


class TestIntensityAndForce:
    def test_intensity_positive(self):
        r = acoustic_intensity_from_spl(94.0)
        assert r["intensity_w_m2"] > 0

    def test_higher_spl_higher_intensity(self):
        i1 = acoustic_intensity_from_spl(80.0)["intensity_w_m2"]
        i2 = acoustic_intensity_from_spl(100.0)["intensity_w_m2"]
        assert i2 > i1

    def test_force_scales_with_area(self):
        f1 = acoustic_radiation_force(10.0, 1e-4)["force_newton"]
        f2 = acoustic_radiation_force(10.0, 2e-4)["force_newton"]
        assert abs(f2 - 2 * f1) < 1e-12

    def test_force_nonnegative(self):
        assert acoustic_radiation_force(0.0, 1e-4)["force_newton"] == 0.0

    def test_invalid_reflectivity_raises(self):
        with pytest.raises(ValueError):
            acoustic_radiation_force(1.0, 1e-4, reflectivity=1.2)


class TestHarvesting:
    def test_harvested_power_nonnegative(self):
        r = piezoelectric_harvested_power(90.0, 0.01, 0.2)
        assert r["harvested_power_w"] >= 0

    def test_zero_efficiency_gives_zero_harvest(self):
        r = piezoelectric_harvested_power(100.0, 0.1, 0.0)
        assert r["harvested_power_w"] == 0.0

    def test_harvested_power_below_incident(self):
        r = piezoelectric_harvested_power(100.0, 0.01, 0.5)
        assert r["harvested_power_w"] <= r["incident_power_w"]


class TestUltrasoundSafety:
    def test_attenuation_nonnegative(self):
        r = ultrasound_attenuation(3.0, 5.0)
        assert r["total_loss_db"] >= 0
        assert 0 < r["transmitted_fraction"] <= 1.0

    def test_deeper_depth_more_loss(self):
        l1 = ultrasound_attenuation(3.0, 2.0)["total_loss_db"]
        l2 = ultrasound_attenuation(3.0, 6.0)["total_loss_db"]
        assert l2 > l1

    def test_mi_limit_flag(self):
        r = cavitation_mechanical_index(1.0, 2.0)
        assert r["within_diagnostic_limit"] is True
        r2 = cavitation_mechanical_index(4.0, 1.0)
        assert r2["within_diagnostic_limit"] is False

    def test_safety_window_reduces_mi_with_depth(self):
        r = ultrasound_safety_window(3.0, 1.2, 5.0)
        assert r["effective_mi_at_depth"] <= r["input_mi"]


class TestSummaryAndUses:
    def test_use_matrix_has_domains(self):
        domains = {d["domain"] for d in sound_energy_use_matrix()}
        assert {"medical_imaging", "energy_harvesting", "materials_and_nanocontrol"} <= domains

    def test_summary_shape(self):
        s = pillar221_summary()
        assert s["pillar"] == 221
        assert "speech_intensity_w_m2_at_60db" in s
        assert "diagnostic_within_limit_example" in s
        assert isinstance(s["epistemic_note"], str)
