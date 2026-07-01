# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 538 — Enteric Neural Core: ENS as Second Brain and KK Biophysical Coupling.

Covers all exported constants and functions.  75 tests.
"""

from __future__ import annotations

import math
import pytest

from src.core.pillar538_enteric_neural_core import (
    # KK constants
    N_W,
    K_CS,
    C_S,
    PHI0,
    N_BEFORE,
    # ENS constants
    ENS_NEURON_COUNT_LOW,
    ENS_NEURON_COUNT_HIGH,
    ENS_NEURON_COUNT_MID,
    SEROTONIN_GUT_FRACTION,
    DOPAMINE_GUT_FRACTION,
    NEUROTRANSMITTER_TYPES,
    SPINAL_CORD_NEURON_COUNT,
    VAGUS_NERVE_MAX_SPEED_MS,
    # Geometric constants
    SUB_UMBILICAL_DISTANCE_CM,
    SUB_UMBILICAL_DISTANCE_IN,
    TORSO_MAJOR_RADIUS_CM,
    TORSO_MINOR_RADIUS_CM,
    # Functions
    torus_surface_point,
    torus_vector_field_integral,
    toroidal_null_condition,
    ens_autonomy_score,
    gut_brain_reaction_lag,
    ens_serotonin_production,
    ens_phi_coherence,
    kk_bio_coupling_strength,
    neural_crest_migration_ratio,
    embryological_kk_link,
    enteric_vs_cranial_comparison,
    pillar538_summary,
    __provenance__,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestKKConstants:
    def test_n_w_is_5(self):
        assert N_W == 5

    def test_k_cs_is_74(self):
        assert K_CS == 74

    def test_k_cs_identity(self):
        """K_CS = N_W^2 + 7^2."""
        assert K_CS == N_W**2 + 7**2

    def test_c_s_value(self):
        assert abs(C_S - 12 / 37) < 1e-12

    def test_phi0_approx(self):
        assert abs(PHI0 - 0.7390851332151607) < 1e-12

    def test_n_before_is_6(self):
        assert N_BEFORE == 6

    def test_n_before_equals_2_times_n_gen(self):
        N_gen = 3
        assert N_BEFORE == 2 * N_gen


class TestENSConstants:
    def test_neuron_count_low(self):
        assert ENS_NEURON_COUNT_LOW == 100_000_000

    def test_neuron_count_high(self):
        assert ENS_NEURON_COUNT_HIGH == 500_000_000

    def test_neuron_count_mid(self):
        assert ENS_NEURON_COUNT_MID == (ENS_NEURON_COUNT_LOW + ENS_NEURON_COUNT_HIGH) // 2

    def test_ens_exceeds_spinal_cord(self):
        assert ENS_NEURON_COUNT_LOW > SPINAL_CORD_NEURON_COUNT

    def test_serotonin_fraction_range(self):
        assert 0.8 < SEROTONIN_GUT_FRACTION < 1.0

    def test_dopamine_fraction_range(self):
        assert 0.0 < DOPAMINE_GUT_FRACTION <= 0.5

    def test_neurotransmitter_types(self):
        assert NEUROTRANSMITTER_TYPES >= 30

    def test_vagus_speed_positive(self):
        assert VAGUS_NERVE_MAX_SPEED_MS > 0


class TestGeometricConstants:
    def test_sub_umbilical_cm(self):
        assert abs(SUB_UMBILICAL_DISTANCE_CM - 4.4) < 0.1

    def test_sub_umbilical_in(self):
        assert abs(SUB_UMBILICAL_DISTANCE_IN - 1.74) < 0.01

    def test_cm_in_conversion(self):
        """1 inch ≈ 2.54 cm — check rough agreement."""
        assert abs(SUB_UMBILICAL_DISTANCE_CM / SUB_UMBILICAL_DISTANCE_IN - 2.54) < 0.05

    def test_torso_radii_positive(self):
        assert TORSO_MAJOR_RADIUS_CM > 0
        assert TORSO_MINOR_RADIUS_CM > 0


# ---------------------------------------------------------------------------
# Toroidal geometry
# ---------------------------------------------------------------------------

class TestTorusSurfacePoint:
    def test_returns_three_floats(self):
        x, y, z = torus_surface_point(0.0, 0.0)
        assert isinstance(x, float)
        assert isinstance(y, float)
        assert isinstance(z, float)

    def test_equatorial_point_sigma0_phi0(self):
        """At sigma=0, phi=0: point is at (R+r, 0, 0)."""
        R, r = 15.0, 10.0
        x, y, z = torus_surface_point(0.0, 0.0, R=R, r=r)
        assert abs(x - (R + r)) < 1e-9
        assert abs(y) < 1e-9
        assert abs(z) < 1e-9

    def test_inner_equatorial_point(self):
        """At sigma=π, phi=0: point is at (R-r, 0, 0)."""
        R, r = 15.0, 10.0
        x, y, z = torus_surface_point(math.pi, 0.0, R=R, r=r)
        assert abs(x - (R - r)) < 1e-9
        assert abs(y) < 1e-9
        assert abs(z) < 1e-9

    def test_top_of_tube(self):
        """At sigma=π/2, phi=0: point is at (R, 0, r)."""
        R, r = 15.0, 10.0
        x, y, z = torus_surface_point(math.pi / 2, 0.0, R=R, r=r)
        assert abs(x - R) < 1e-9
        assert abs(y) < 1e-9
        assert abs(z - r) < 1e-9

    def test_invalid_radii(self):
        with pytest.raises(ValueError):
            torus_surface_point(0.0, 0.0, R=-1.0, r=5.0)
        with pytest.raises(ValueError):
            torus_surface_point(0.0, 0.0, R=5.0, r=0.0)


class TestToroidalNullCondition:
    def test_null_satisfied(self):
        result = toroidal_null_condition(tolerance=1e-4)
        assert result["null_satisfied"] is True

    def test_magnitude_near_zero(self):
        result = toroidal_null_condition(tolerance=1e-4)
        assert result["magnitude"] < 1e-4

    def test_contains_geometry(self):
        result = toroidal_null_condition()
        assert abs(result["sub_umbilical_cm"] - SUB_UMBILICAL_DISTANCE_CM) < 1e-9
        assert abs(result["sub_umbilical_in"] - SUB_UMBILICAL_DISTANCE_IN) < 1e-9

    def test_vector_integral_low_resolution(self):
        """Even at coarse resolution, integral should be near zero."""
        Fx, Fy, Fz = torus_vector_field_integral(n_sigma=36, n_phi=36)
        mag = math.sqrt(Fx**2 + Fy**2 + Fz**2)
        assert mag < 1e-3

    def test_invalid_resolution(self):
        with pytest.raises(ValueError):
            torus_vector_field_integral(n_sigma=1, n_phi=36)


# ---------------------------------------------------------------------------
# ENS functional metrics
# ---------------------------------------------------------------------------

class TestENSAutonomyScore:
    def test_fully_autonomous(self):
        result = ens_autonomy_score(0.0)
        assert result["autonomous_fraction"] == pytest.approx(1.0)
        assert result["phi_autonomy"] == pytest.approx(1.0 / PHI0)
        assert "FULLY_AUTONOMOUS" in result["status"]

    def test_partial_vagal(self):
        result = ens_autonomy_score(0.3)
        assert result["autonomous_fraction"] == pytest.approx(0.7)
        assert result["vagal_fraction"] == pytest.approx(0.3)

    def test_invalid_fraction(self):
        with pytest.raises(ValueError):
            ens_autonomy_score(-0.1)
        with pytest.raises(ValueError):
            ens_autonomy_score(1.1)

    def test_fully_cranial(self):
        result = ens_autonomy_score(1.0)
        assert result["autonomous_fraction"] == pytest.approx(0.0)


class TestGutBrainReactionLag:
    def test_gut_is_faster_default(self):
        result = gut_brain_reaction_lag()
        assert result["gut_is_faster"] is True

    def test_lag_positive_default(self):
        result = gut_brain_reaction_lag()
        assert result["lag_ms"] > 0

    def test_cranial_arrival_formula(self):
        result = gut_brain_reaction_lag(
            stimulus_distance_m=1.0,
            ens_local_reaction_ms=1.0,
            vagal_conduction_speed_ms=100.0,
        )
        expected_cranial = (1.0 / 100.0) * 1000.0
        assert result["cranial_arrival_ms"] == pytest.approx(expected_cranial)

    def test_invalid_inputs(self):
        with pytest.raises(ValueError):
            gut_brain_reaction_lag(stimulus_distance_m=0.0)
        with pytest.raises(ValueError):
            gut_brain_reaction_lag(ens_local_reaction_ms=0.0)


class TestENSSerotoninProduction:
    def test_fractions_sum_to_one(self):
        result = ens_serotonin_production(10.0)
        assert result["gut_serotonin_mg"] + result["cranial_serotonin_mg"] == pytest.approx(10.0)

    def test_gut_fraction_correct(self):
        result = ens_serotonin_production(100.0)
        assert result["gut_fraction"] == pytest.approx(SEROTONIN_GUT_FRACTION)
        assert result["gut_serotonin_mg"] == pytest.approx(100.0 * SEROTONIN_GUT_FRACTION)

    def test_neurotransmitter_types(self):
        result = ens_serotonin_production()
        assert result["neurotransmitter_types"] == NEUROTRANSMITTER_TYPES

    def test_invalid_input(self):
        with pytest.raises(ValueError):
            ens_serotonin_production(0.0)


class TestENSPhiCoherence:
    def test_returns_dict(self):
        result = ens_phi_coherence()
        assert isinstance(result, dict)

    def test_phi_debt_non_negative(self):
        result = ens_phi_coherence()
        assert result["phi_debt"] >= 0.0

    def test_high_synchrony_low_phi_debt(self):
        result_high = ens_phi_coherence(
            neuron_count=float(ENS_NEURON_COUNT_HIGH),
            firing_synchrony=0.99,
        )
        result_low = ens_phi_coherence(
            neuron_count=float(ENS_NEURON_COUNT_LOW),
            firing_synchrony=0.1,
        )
        assert result_high["phi_coherence"] > result_low["phi_coherence"]

    def test_invalid_synchrony(self):
        with pytest.raises(ValueError):
            ens_phi_coherence(firing_synchrony=1.5)

    def test_invalid_neuron_count(self):
        with pytest.raises(ValueError):
            ens_phi_coherence(neuron_count=0.0)


# ---------------------------------------------------------------------------
# KK biophysical coupling
# ---------------------------------------------------------------------------

class TestKKBioCouplingStrength:
    def test_returns_dict(self):
        result = kk_bio_coupling_strength()
        assert isinstance(result, dict)

    def test_coupling_positive(self):
        result = kk_bio_coupling_strength()
        assert result["coupling_strength"] > 0.0

    def test_kk_scale_factor(self):
        result = kk_bio_coupling_strength()
        assert result["kk_scale_factor"] == pytest.approx(1.0 / K_CS)

    def test_adjacent_track_status(self):
        result = kk_bio_coupling_strength()
        assert "ADJACENT TRACK" in result["status"]

    def test_invalid_inputs(self):
        with pytest.raises(ValueError):
            kk_bio_coupling_strength(neural_density_per_cm3=0.0)
        with pytest.raises(ValueError):
            kk_bio_coupling_strength(field_frequency_hz=0.0)


# ---------------------------------------------------------------------------
# Embryological link
# ---------------------------------------------------------------------------

class TestNeuralCrestMigrationRatio:
    def test_sacral_fraction_equals_1_over_n_w(self):
        result = neural_crest_migration_ratio()
        assert result["sacral_fraction"] == pytest.approx(1.0 / N_W)

    def test_ratio_sacral_vagal(self):
        result = neural_crest_migration_ratio()
        assert result["ratio_sacral_vagal"] == pytest.approx(1.0 / N_W)

    def test_n_w_consistent(self):
        result = neural_crest_migration_ratio()
        assert result["n_w"] == N_W

    def test_n_before_consistent(self):
        result = neural_crest_migration_ratio()
        assert result["n_before"] == N_BEFORE


class TestEmbryologicalKKLink:
    def test_n_generations_is_3(self):
        result = embryological_kk_link()
        assert result["n_generations"] == 3

    def test_n_before_is_6(self):
        result = embryological_kk_link()
        assert result["n_before"] == N_BEFORE

    def test_three_ncc_subpopulations(self):
        result = embryological_kk_link()
        assert result["n_ncc_subpopulations"] == 3
        assert len(result["ncc_subpopulations"]) == 3

    def test_epistemic_status_is_curiosity(self):
        result = embryological_kk_link()
        assert "GEOMETRIC_CURIOSITY" in result["epistemic_status"]


# ---------------------------------------------------------------------------
# Comparison table
# ---------------------------------------------------------------------------

class TestEntericVsCranialComparison:
    def test_returns_list(self):
        table = enteric_vs_cranial_comparison()
        assert isinstance(table, list)
        assert len(table) > 0

    def test_has_neuron_count_row(self):
        table = enteric_vs_cranial_comparison()
        attrs = [row["attribute"] for row in table]
        assert "neuron_count" in attrs

    def test_cranial_neuron_count_larger(self):
        table = enteric_vs_cranial_comparison()
        nc_row = next(r for r in table if r["attribute"] == "neuron_count")
        assert nc_row["cranial_brain"] > nc_row["enteric_brain"]

    def test_enteric_serotonin_dominant(self):
        table = enteric_vs_cranial_comparison()
        ser_row = next(r for r in table if r["attribute"] == "serotonin_production_fraction")
        assert ser_row["enteric_brain"] > ser_row["cranial_brain"]

    def test_enteric_autonomous(self):
        table = enteric_vs_cranial_comparison()
        auto_row = next(r for r in table if r["attribute"] == "autonomous_without_vagus")
        assert auto_row["enteric_brain"] is True
        assert auto_row["cranial_brain"] is False


# ---------------------------------------------------------------------------
# Provenance and summary
# ---------------------------------------------------------------------------

class TestProvenance:
    def test_pillar_number(self):
        assert __provenance__["pillar"] == 538

    def test_adjacent_track_status(self):
        assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]

    def test_author(self):
        assert "Walker-Pearson" in __provenance__["author"]

    def test_fingerprint(self):
        assert __provenance__["fingerprint"] == "(5, 7, 74)"


class TestPillar538Summary:
    def test_returns_dict(self):
        result = pillar538_summary()
        assert isinstance(result, dict)

    def test_pillar_number(self):
        assert pillar538_summary()["pillar"] == 538

    def test_adjacent_track_status(self):
        assert "ADJACENT" in pillar538_summary()["status"]

    def test_kk_constants_present(self):
        kk = pillar538_summary()["kk_constants"]
        assert kk["N_W"] == N_W
        assert kk["K_CS"] == K_CS

    def test_ens_constants_present(self):
        ens = pillar538_summary()["ens_constants"]
        assert ens["neuron_count_low"] == ENS_NEURON_COUNT_LOW

    def test_toroidal_null_present(self):
        null = pillar538_summary()["toroidal_null"]
        assert "null_satisfied" in null

    def test_comparison_table_present(self):
        table = pillar538_summary()["comparison_table"]
        assert isinstance(table, list)
        assert len(table) == len(enteric_vs_cranial_comparison())
