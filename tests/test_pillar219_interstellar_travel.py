# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar219_interstellar_travel.py — Pillar 219 test suite."""
import math
import pytest
from src.core.pillar219_interstellar_travel import (
    # Constants
    N_W,
    K_CS,
    PHI0,
    BRAIDED_SOUND_SPEED,
    C_LIGHT,
    AU_METERS,
    LY_METERS,
    PARSEC_METERS,
    ALPHA_CENTAURI_LY,
    SOLAR_MASS_KG,
    KJ_PER_KG_TNT,
    WORLD_ENERGY_ANNUAL_J,
    PLANCK_MASS_KG,
    # Functions
    kinetic_energy_fraction_c,
    time_dilation,
    radiation_dose_interstellar,
    alcubierre_energy_estimate,
    generation_ship_analysis,
    kk_warp_geometry_bound,
    propulsion_comparison,
    pillar219_summary,
)


# ---------------------------------------------------------------------------
# TestConstants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi0_value(self):
        assert abs(PHI0 - 0.739085) < 1e-6

    def test_braided_sound_speed(self):
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-12

    def test_c_light(self):
        assert abs(C_LIGHT - 2.998e8) < 1e3

    def test_alpha_centauri_ly(self):
        assert abs(ALPHA_CENTAURI_LY - 4.37) < 0.01

    def test_ly_meters_order(self):
        assert 9.0e15 < LY_METERS < 1.0e16

    def test_au_meters_order(self):
        assert 1.4e11 < AU_METERS < 1.6e11

    def test_parsec_meters_order(self):
        assert 3.0e16 < PARSEC_METERS < 3.2e16

    def test_solar_mass_kg(self):
        assert 1.9e30 < SOLAR_MASS_KG < 2.1e30

    def test_world_energy_annual_positive(self):
        assert WORLD_ENERGY_ANNUAL_J > 0

    def test_planck_mass_kg_order(self):
        # Planck mass ≈ 2.176e-8 kg
        assert 2.0e-8 < PLANCK_MASS_KG < 2.5e-8


# ---------------------------------------------------------------------------
# TestKineticEnergy
# ---------------------------------------------------------------------------
class TestKineticEnergy:
    def test_near_zero_speed(self):
        result = kinetic_energy_fraction_c(1000.0, 1e-6)
        assert result["KE_joules"] >= 0

    def test_tenth_c_positive_energy(self):
        result = kinetic_energy_fraction_c(1000.0, 0.1)
        assert result["KE_joules"] > 0

    def test_returns_dict(self):
        result = kinetic_energy_fraction_c(1e6, 0.1)
        assert isinstance(result, dict)

    def test_has_all_keys(self):
        result = kinetic_energy_fraction_c(1e6, 0.1)
        for key in ("KE_joules", "KE_megatons_tnt", "KE_annual_world_energy_ratio",
                    "lorentz_factor", "rest_energy_joules", "notes"):
            assert key in result

    def test_lorentz_factor_tenth_c(self):
        result = kinetic_energy_fraction_c(1.0, 0.1)
        assert abs(result["lorentz_factor"] - 1.0 / math.sqrt(1 - 0.01)) < 1e-8

    def test_energy_increases_with_speed(self):
        r1 = kinetic_energy_fraction_c(1.0, 0.1)
        r2 = kinetic_energy_fraction_c(1.0, 0.5)
        assert r2["KE_joules"] > r1["KE_joules"]

    def test_megatons_tnt_positive(self):
        result = kinetic_energy_fraction_c(1e6, 0.1)
        assert result["KE_megatons_tnt"] > 0

    def test_world_energy_ratio_large_ship(self):
        # 1e6 kg at 0.1c ≈ 75% of annual world energy — a large fraction
        result = kinetic_energy_fraction_c(1e6, 0.1)
        assert result["KE_annual_world_energy_ratio"] > 0.5

    def test_notes_is_string(self):
        result = kinetic_energy_fraction_c(1e3, 0.2)
        assert isinstance(result["notes"], str)

    def test_invalid_speed_raises(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            kinetic_energy_fraction_c(1000.0, 1.0)

    def test_rest_energy_consistency(self):
        m = 10.0
        result = kinetic_energy_fraction_c(m, 0.1)
        assert abs(result["rest_energy_joules"] - m * C_LIGHT ** 2) < 1e10


# ---------------------------------------------------------------------------
# TestTimeDilation
# ---------------------------------------------------------------------------
class TestTimeDilation:
    def test_returns_dict(self):
        result = time_dilation(0.1, 4.37)
        assert isinstance(result, dict)

    def test_has_all_keys(self):
        result = time_dilation(0.5, 10.0)
        for key in ("lorentz_factor", "coordinate_time_years", "proper_time_years",
                    "fraction_of_light_speed", "time_savings_years", "notes"):
            assert key in result

    def test_low_speed_lorentz_near_one(self):
        result = time_dilation(0.01, 4.37)
        assert abs(result["lorentz_factor"] - 1.0) < 0.001

    def test_high_speed_lorentz_large(self):
        result = time_dilation(0.99, 4.37)
        assert result["lorentz_factor"] > 5.0

    def test_proper_time_less_than_coordinate(self):
        result = time_dilation(0.5, 4.37)
        assert result["proper_time_years"] < result["coordinate_time_years"]

    def test_fraction_matches_input(self):
        result = time_dilation(0.3, 10.0)
        assert abs(result["fraction_of_light_speed"] - 0.3) < 1e-10

    def test_coordinate_time_alpha_centauri_at_point1c(self):
        result = time_dilation(0.1, ALPHA_CENTAURI_LY)
        # At 0.1c, 4.37 ly → 43.7 years Earth time
        assert abs(result["coordinate_time_years"] - 43.7) < 0.1

    def test_time_savings_positive_at_relativistic_speed(self):
        result = time_dilation(0.99, 4.37)
        assert result["time_savings_years"] > 0

    def test_notes_is_string(self):
        result = time_dilation(0.2, 4.37)
        assert isinstance(result["notes"], str)


# ---------------------------------------------------------------------------
# TestRadiation
# ---------------------------------------------------------------------------
class TestRadiation:
    def test_returns_dict(self):
        result = radiation_dose_interstellar(0.1)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = radiation_dose_interstellar(0.1)
        for key in ("dose_mSv_per_year", "lethal_threshold_mSv",
                    "shielding_required_bool", "lorentz_factor", "notes"):
            assert key in result

    def test_dose_positive(self):
        result = radiation_dose_interstellar(0.1)
        assert result["dose_mSv_per_year"] > 0

    def test_dose_increases_with_speed(self):
        r1 = radiation_dose_interstellar(0.1)
        r2 = radiation_dose_interstellar(0.5)
        assert r2["dose_mSv_per_year"] > r1["dose_mSv_per_year"]

    def test_lethal_threshold_present(self):
        result = radiation_dose_interstellar(0.1)
        assert result["lethal_threshold_mSv"] > 0

    def test_shielding_required_at_high_speed(self):
        result = radiation_dose_interstellar(0.99)
        assert result["shielding_required_bool"] is True

    def test_shielding_bool_type(self):
        result = radiation_dose_interstellar(0.01)
        assert isinstance(result["shielding_required_bool"], bool)

    def test_zero_speed_no_shielding(self):
        result = radiation_dose_interstellar(0.0)
        assert result["shielding_required_bool"] is False


# ---------------------------------------------------------------------------
# TestAlcubierre
# ---------------------------------------------------------------------------
class TestAlcubierre:
    def test_returns_dict(self):
        result = alcubierre_energy_estimate()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = alcubierre_energy_estimate()
        for key in ("energy_joules", "energy_solar_masses", "feasibility_note",
                    "R_bubble_m", "v_fraction_c", "notes"):
            assert key in result

    def test_energy_joules_negative(self):
        result = alcubierre_energy_estimate()
        assert result["energy_joules"] < 0

    def test_energy_solar_masses_large(self):
        result = alcubierre_energy_estimate(R_bubble_m=100.0, v_fraction_c=1.0)
        # Should be at least 1 solar mass
        assert result["energy_solar_masses"] > 1.0

    def test_feasibility_note_is_string(self):
        result = alcubierre_energy_estimate()
        assert isinstance(result["feasibility_note"], str)

    def test_feasibility_note_mentions_exotic(self):
        result = alcubierre_energy_estimate()
        assert "exotic" in result["feasibility_note"].lower()

    def test_larger_bubble_more_energy(self):
        r1 = alcubierre_energy_estimate(R_bubble_m=10.0)
        r2 = alcubierre_energy_estimate(R_bubble_m=100.0)
        assert abs(r2["energy_joules"]) > abs(r1["energy_joules"])

    def test_bubble_radius_stored(self):
        result = alcubierre_energy_estimate(R_bubble_m=50.0)
        assert abs(result["R_bubble_m"] - 50.0) < 1e-10


# ---------------------------------------------------------------------------
# TestGenerationShip
# ---------------------------------------------------------------------------
class TestGenerationShip:
    def test_returns_dict(self):
        result = generation_ship_analysis(4.37)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = generation_ship_analysis(4.37)
        for key in ("travel_time_years_ship", "travel_time_years_earth",
                    "peak_v_fraction_c", "energy_joules_per_kg", "notes"):
            assert key in result

    def test_travel_time_positive(self):
        result = generation_ship_analysis(4.37)
        assert result["travel_time_years_ship"] > 0

    def test_earth_time_positive(self):
        result = generation_ship_analysis(4.37)
        assert result["travel_time_years_earth"] > 0

    def test_peak_v_less_than_c(self):
        result = generation_ship_analysis(4.37, accel_g=0.01)
        assert 0.0 < result["peak_v_fraction_c"] < 1.0

    def test_higher_accel_faster(self):
        r1 = generation_ship_analysis(4.37, accel_g=0.01)
        r2 = generation_ship_analysis(4.37, accel_g=0.1)
        assert r2["travel_time_years_ship"] < r1["travel_time_years_ship"]

    def test_energy_per_kg_positive(self):
        result = generation_ship_analysis(4.37)
        assert result["energy_joules_per_kg"] > 0

    def test_farther_distance_longer_trip(self):
        r1 = generation_ship_analysis(4.37)
        r2 = generation_ship_analysis(100.0)
        assert r2["travel_time_years_ship"] > r1["travel_time_years_ship"]


# ---------------------------------------------------------------------------
# TestKKWarpBound
# ---------------------------------------------------------------------------
class TestKKWarpBound:
    def test_returns_dict(self):
        result = kk_warp_geometry_bound()
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = kk_warp_geometry_bound()
        for key in ("kk_warp_bound", "K_cs", "phi0", "interpretation", "is_speculative"):
            assert key in result

    def test_bound_positive(self):
        result = kk_warp_geometry_bound()
        assert result["kk_warp_bound"] > 0

    def test_bound_within_range(self):
        result = kk_warp_geometry_bound()
        assert 1.0 < result["kk_warp_bound"] < 100.0

    def test_bound_numerical_value(self):
        # phi0 * 74 / (4 * pi) ≈ 4.35
        expected = PHI0 * K_CS / (4.0 * math.pi)
        result = kk_warp_geometry_bound()
        assert abs(result["kk_warp_bound"] - expected) < 1e-8

    def test_is_speculative_true(self):
        result = kk_warp_geometry_bound()
        assert result["is_speculative"] is True

    def test_interpretation_is_string(self):
        result = kk_warp_geometry_bound()
        assert isinstance(result["interpretation"], str)

    def test_custom_inputs(self):
        result = kk_warp_geometry_bound(K_cs=74, phi0=0.739085)
        assert abs(result["kk_warp_bound"] - 0.739085 * 74 / (4 * math.pi)) < 1e-8


# ---------------------------------------------------------------------------
# TestPropulsionComparison
# ---------------------------------------------------------------------------
class TestPropulsionComparison:
    def setup_method(self):
        self.props = propulsion_comparison()

    def test_returns_list(self):
        assert isinstance(self.props, list)

    def test_has_multiple_entries(self):
        assert len(self.props) >= 4

    def test_each_entry_has_name(self):
        for p in self.props:
            assert "name" in p

    def test_each_entry_has_trl(self):
        for p in self.props:
            assert "TRL" in p

    def test_each_entry_has_max_v(self):
        for p in self.props:
            assert "max_v_fraction_c" in p

    def test_trl_in_valid_range(self):
        for p in self.props:
            assert 1 <= p["TRL"] <= 9

    def test_chemical_has_highest_trl(self):
        chemical = next(p for p in self.props if "Chemical" in p["name"])
        assert chemical["TRL"] == 9

    def test_laser_sail_present(self):
        names = [p["name"] for p in self.props]
        assert any("laser" in n.lower() or "starshot" in n.lower() for n in names)

    def test_laser_sail_v_approx_0p2(self):
        laser = next(p for p in self.props if "Laser" in p["name"] or "laser" in p["name"])
        assert abs(laser["max_v_fraction_c"] - 0.20) < 0.05

    def test_each_entry_has_notes(self):
        for p in self.props:
            assert "notes" in p
            assert isinstance(p["notes"], str)

    def test_each_entry_has_energy_per_kg(self):
        for p in self.props:
            assert "energy_per_kg_J" in p


# ---------------------------------------------------------------------------
# TestSummary
# ---------------------------------------------------------------------------
class TestSummary:
    def setup_method(self):
        self.summary = pillar219_summary()

    def test_returns_dict(self):
        assert isinstance(self.summary, dict)

    def test_has_honest_assessment(self):
        assert "honest_assessment" in self.summary

    def test_honest_assessment_is_string(self):
        assert isinstance(self.summary["honest_assessment"], str)

    def test_has_pillar_number(self):
        assert self.summary["pillar"] == 219

    def test_has_kk_warp_bound(self):
        assert "kk_warp_bound" in self.summary
        assert self.summary["kk_warp_bound"] > 0

    def test_has_status(self):
        assert "status" in self.summary

    def test_has_references(self):
        assert "references" in self.summary
        assert len(self.summary["references"]) > 0

    def test_alpha_centauri_energy_ratio_positive(self):
        assert self.summary["alpha_centauri_energy_0p1c_ratio"] > 0
