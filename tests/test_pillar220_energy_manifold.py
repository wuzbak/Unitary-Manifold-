# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_pillar220_energy_manifold.py — Pillar 220 test suite."""
import math
import pytest
from src.core.pillar220_energy_manifold import (
    N_W,
    K_CS,
    PHI0,
    BRAIDED_SOUND_SPEED,
    KWH_PER_JOULE,
    WORLD_PRIMARY_ENERGY_EJ_2023,
    US_HOUSEHOLD_KWH_YEAR,
    GLOBAL_POPULATION_2026,
    CO2_KG_PER_KWH_COAL,
    CO2_KG_PER_KWH_GAS,
    CO2_KG_PER_KWH_SOLAR,
    CARNOT_LIMIT,
    RENEWABLE_FRACTION_2023,
    SCALE_NAMES,
    household_phi_efficiency,
    kk_efficiency_scaling,
    energy_phi_debt,
    city_energy_audit,
    global_energy_manifold,
    phi_pathway_to_sustainability,
    appliance_phi_audit,
    pillar220_summary,
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

    def test_phi0_is_fixed_point(self):
        # φ₀ satisfies x = cos(x) to 5 significant figures
        assert abs(math.cos(PHI0) - PHI0) < 1e-4

    def test_braided_sound_speed(self):
        assert abs(BRAIDED_SOUND_SPEED - 12 / 37) < 1e-12

    def test_kwh_per_joule(self):
        assert abs(KWH_PER_JOULE - 1 / 3.6e6) < 1e-14

    def test_world_primary_energy_range(self):
        # IEA 2023 estimate: 580–660 EJ
        assert 580.0 <= WORLD_PRIMARY_ENERGY_EJ_2023 <= 660.0

    def test_us_household_kwh(self):
        assert 8_000 <= US_HOUSEHOLD_KWH_YEAR <= 14_000

    def test_global_population_order(self):
        assert 7e9 < GLOBAL_POPULATION_2026 < 10e9

    def test_co2_coal_intensity(self):
        assert 0.7 <= CO2_KG_PER_KWH_COAL <= 1.0

    def test_co2_gas_intensity(self):
        assert 0.3 <= CO2_KG_PER_KWH_GAS <= 0.7

    def test_co2_solar_low(self):
        assert CO2_KG_PER_KWH_SOLAR < CO2_KG_PER_KWH_GAS

    def test_carnot_limit(self):
        assert CARNOT_LIMIT == 1.0

    def test_renewable_fraction_2023(self):
        assert 0.10 <= RENEWABLE_FRACTION_2023 <= 0.25

    def test_scale_names_complete(self):
        assert set(SCALE_NAMES.keys()) == {0, 1, 2, 3, 4}

    def test_scale_name_level0(self):
        assert SCALE_NAMES[0] == "household"

    def test_scale_name_level4(self):
        assert SCALE_NAMES[4] == "world"


# ---------------------------------------------------------------------------
# TestHouseholdEfficiency
# ---------------------------------------------------------------------------
class TestHouseholdEfficiency:
    def test_returns_dict(self):
        result = household_phi_efficiency(10_500)
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = household_phi_efficiency(10_500)
        for key in ("total_kwh", "useful_fraction_estimate", "phi_debt_kwh",
                    "phi_debt_fraction", "co2_kg", "recommendations"):
            assert key in result, f"Missing key: {key}"

    def test_total_kwh_matches_input(self):
        result = household_phi_efficiency(12_000)
        assert result["total_kwh"] == 12_000

    def test_phi_debt_nonnegative(self):
        result = household_phi_efficiency(10_500)
        assert result["phi_debt_kwh"] >= 0

    def test_phi_debt_fraction_nonnegative(self):
        result = household_phi_efficiency(10_500)
        assert result["phi_debt_fraction"] >= 0

    def test_co2_positive_for_nonzero(self):
        result = household_phi_efficiency(10_500)
        assert result["co2_kg"] > 0

    def test_recommendations_is_list(self):
        result = household_phi_efficiency(10_500)
        assert isinstance(result["recommendations"], list)

    def test_recommendations_nonempty(self):
        result = household_phi_efficiency(10_500)
        assert len(result["recommendations"]) >= 1

    def test_zero_usage(self):
        result = household_phi_efficiency(0)
        assert result["phi_debt_kwh"] == 0.0
        assert result["co2_kg"] == 0.0

    def test_efficient_home_lower_debt(self):
        avg = household_phi_efficiency(10_500, home_type="average_us")
        eff = household_phi_efficiency(10_500, home_type="efficient")
        assert eff["phi_debt_kwh"] <= avg["phi_debt_kwh"]

    def test_inefficient_home_higher_debt(self):
        avg = household_phi_efficiency(10_500, home_type="average_us")
        bad = household_phi_efficiency(10_500, home_type="inefficient")
        assert bad["phi_debt_kwh"] >= avg["phi_debt_kwh"]

    def test_useful_fraction_in_range(self):
        result = household_phi_efficiency(10_500)
        assert 0.0 < result["useful_fraction_estimate"] <= 1.0

    def test_negative_kwh_raises(self):
        with pytest.raises(ValueError):
            household_phi_efficiency(-100)


# ---------------------------------------------------------------------------
# TestKKScaling
# ---------------------------------------------------------------------------
class TestKKScaling:
    def test_level0_efficiency_equals_phi0(self):
        result = kk_efficiency_scaling(0)
        assert abs(result["efficiency_ceiling"] - PHI0) < 1e-9

    def test_levels_return_valid_efficiency(self):
        for level in range(5):
            r = kk_efficiency_scaling(level)
            assert 0.0 < r["efficiency_ceiling"] <= 1.0

    def test_efficiency_decreases_with_scale(self):
        effs = [kk_efficiency_scaling(n)["efficiency_ceiling"] for n in range(5)]
        for i in range(len(effs) - 1):
            assert effs[i] >= effs[i + 1], f"Level {i} eff < level {i+1} eff"

    def test_phi_debt_fraction_complement(self):
        for level in range(5):
            r = kk_efficiency_scaling(level)
            assert abs(r["efficiency_ceiling"] + r["phi_debt_fraction"] - 1.0) < 1e-10

    def test_scale_name_present(self):
        for level in range(5):
            r = kk_efficiency_scaling(level)
            assert "scale_name" in r

    def test_invalid_level_raises(self):
        with pytest.raises(ValueError):
            kk_efficiency_scaling(5)

    def test_world_level_efficiency_below_phi0(self):
        world = kk_efficiency_scaling(4)
        assert world["efficiency_ceiling"] < PHI0


# ---------------------------------------------------------------------------
# TestPhiDebt
# ---------------------------------------------------------------------------
class TestPhiDebt:
    def test_zero_waste_gives_zero_debt(self):
        result = energy_phi_debt(1_000_000, 1_000_000)
        assert result["phi_debt_joules"] == 0.0
        assert result["phi_debt_fraction"] == 0.0

    def test_all_waste_gives_full_debt(self):
        result = energy_phi_debt(1_000_000, 0)
        assert result["phi_debt_joules"] == 1_000_000
        assert abs(result["phi_debt_fraction"] - 1.0) < 1e-10

    def test_partial_waste(self):
        result = energy_phi_debt(1_000_000, 600_000)
        assert abs(result["phi_debt_joules"] - 400_000) < 1e-6
        assert abs(result["phi_debt_fraction"] - 0.4) < 1e-10

    def test_co2_nonnegative(self):
        result = energy_phi_debt(1e9, 5e8)
        assert result["co2_equivalent_kg"] >= 0

    def test_zero_consumed_zero_fraction(self):
        result = energy_phi_debt(0, 0)
        assert result["phi_debt_fraction"] == 0.0

    def test_useful_exceeds_consumed_raises(self):
        with pytest.raises(ValueError):
            energy_phi_debt(100, 200)

    def test_negative_consumed_raises(self):
        with pytest.raises(ValueError):
            energy_phi_debt(-1, 0)

    def test_negative_useful_raises(self):
        with pytest.raises(ValueError):
            energy_phi_debt(100, -1)


# ---------------------------------------------------------------------------
# TestCityAudit
# ---------------------------------------------------------------------------
class TestCityAudit:
    def setup_method(self):
        self.result = city_energy_audit(1_000_000, kwh_per_capita_year=6_000)

    def test_total_kwh_positive(self):
        assert self.result["total_kwh_year"] > 0

    def test_total_kwh_value(self):
        assert abs(self.result["total_kwh_year"] - 6e9) < 1e3

    def test_phi_debt_nonnegative(self):
        assert self.result["phi_debt_ej"] >= 0

    def test_kk_tower_level(self):
        assert self.result["kk_tower_level"] == 2

    def test_renewable_target_in_range(self):
        assert 0.0 <= self.result["renewable_target_fraction"] <= 1.0

    def test_total_ej_positive(self):
        assert self.result["total_ej_year"] > 0

    def test_larger_city_more_energy(self):
        small = city_energy_audit(500_000)
        large = city_energy_audit(2_000_000)
        assert large["total_kwh_year"] > small["total_kwh_year"]


# ---------------------------------------------------------------------------
# TestGlobalEnergy
# ---------------------------------------------------------------------------
class TestGlobalEnergy:
    def setup_method(self):
        self.result = global_energy_manifold(2023)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_world_primary_ej_in_range(self):
        # 2023 baseline should be ~580–660 EJ
        assert 580.0 <= self.result["world_primary_ej"] <= 660.0

    def test_required_keys(self):
        for key in ("world_primary_ej", "renewable_fraction_current",
                    "phi_ceiling_ej", "phi_debt_ej",
                    "gap_to_phi_ceiling_ej", "co2_gt_year", "recommendations"):
            assert key in self.result

    def test_renewable_fraction_in_range(self):
        assert 0.0 <= self.result["renewable_fraction_current"] <= 1.0

    def test_phi_ceiling_positive(self):
        assert self.result["phi_ceiling_ej"] > 0

    def test_phi_debt_positive(self):
        assert self.result["phi_debt_ej"] > 0

    def test_co2_gt_positive(self):
        assert self.result["co2_gt_year"] > 0

    def test_recommendations_nonempty(self):
        assert len(self.result["recommendations"]) > 0

    def test_future_year_higher_energy(self):
        now = global_energy_manifold(2023)
        future = global_energy_manifold(2030)
        assert future["world_primary_ej"] > now["world_primary_ej"]


# ---------------------------------------------------------------------------
# TestPhiPathway
# ---------------------------------------------------------------------------
class TestPhiPathway:
    def setup_method(self):
        self.result = phi_pathway_to_sustainability(2050)

    def test_feasibility_score_in_range(self):
        assert 0.0 <= self.result["feasibility_score"] <= 1.0

    def test_required_keys(self):
        for key in ("start_year", "target_year", "years_available",
                    "yearly_reduction_fraction", "technology_mix",
                    "feasibility_score"):
            assert key in self.result

    def test_years_available_positive(self):
        assert self.result["years_available"] > 0

    def test_target_year_matches(self):
        assert self.result["target_year"] == 2050

    def test_tech_mix_sums_to_one(self):
        total = sum(self.result["technology_mix"].values())
        assert abs(total - 1.0) < 1e-9

    def test_longer_horizon_better_feasibility(self):
        near = phi_pathway_to_sustainability(2040)
        far = phi_pathway_to_sustainability(2060)
        assert far["feasibility_score"] >= near["feasibility_score"]

    def test_yearly_reduction_nonnegative(self):
        assert self.result["yearly_reduction_fraction"] >= 0.0


# ---------------------------------------------------------------------------
# TestApplianceAudit
# ---------------------------------------------------------------------------
class TestApplianceAudit:
    def test_empty_list_returns_zero(self):
        result = appliance_phi_audit([])
        assert result["total_phi_debt_kwh_year"] == 0.0

    def test_empty_list_empty_rankings(self):
        result = appliance_phi_audit([])
        assert result["appliance_rankings"] == []

    def test_single_appliance_positive_debt(self):
        apps = [{"name": "old_fridge", "watts": 150, "hours_per_day": 24, "efficiency_percent": 40}]
        result = appliance_phi_audit(apps)
        assert result["total_phi_debt_kwh_year"] > 0

    def test_100_percent_efficient_no_debt(self):
        apps = [{"name": "perfect", "watts": 100, "hours_per_day": 8, "efficiency_percent": 100}]
        result = appliance_phi_audit(apps)
        assert result["total_phi_debt_kwh_year"] == 0.0

    def test_multiple_appliances_ranked_by_waste(self):
        apps = [
            {"name": "fridge", "watts": 150, "hours_per_day": 24, "efficiency_percent": 40},
            {"name": "led_bulb", "watts": 10, "hours_per_day": 5, "efficiency_percent": 90},
        ]
        result = appliance_phi_audit(apps)
        rankings = result["appliance_rankings"]
        assert rankings[0]["phi_debt_kwh_year"] >= rankings[1]["phi_debt_kwh_year"]

    def test_total_is_sum_of_rankings(self):
        apps = [
            {"name": "a", "watts": 200, "hours_per_day": 10, "efficiency_percent": 60},
            {"name": "b", "watts": 100, "hours_per_day": 5, "efficiency_percent": 50},
        ]
        result = appliance_phi_audit(apps)
        ranked_total = sum(r["phi_debt_kwh_year"] for r in result["appliance_rankings"])
        assert abs(result["total_phi_debt_kwh_year"] - ranked_total) < 1e-9

    def test_summary_string_present(self):
        apps = [{"name": "ac", "watts": 1500, "hours_per_day": 8, "efficiency_percent": 70}]
        result = appliance_phi_audit(apps)
        assert isinstance(result["summary"], str)
        assert len(result["summary"]) > 0


# ---------------------------------------------------------------------------
# TestSummary
# ---------------------------------------------------------------------------
class TestSummary:
    def setup_method(self):
        self.result = pillar220_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_status_key(self):
        assert "status" in self.result

    def test_has_phi_ceiling_key(self):
        assert "phi_ceiling" in self.result

    def test_phi_ceiling_value(self):
        assert abs(self.result["phi_ceiling"] - PHI0) < 1e-9

    def test_pillar_number(self):
        assert self.result["pillar"] == 220

    def test_kk_tower_levels_complete(self):
        assert set(self.result["kk_tower_levels"].keys()) == {0, 1, 2, 3, 4}

    def test_epistemic_note_present(self):
        assert "epistemic_note" in self.result
