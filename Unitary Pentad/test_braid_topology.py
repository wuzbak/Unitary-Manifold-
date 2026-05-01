# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_braid_topology.py
=======================================
Unit tests for the braid topology verification module
(``Unitary Pentad/braid_topology.py``).

Covers:
  - Module constants: PHI_GOLDEN, CS_BRAIDED_EXACT, N_CORE/N_LAYER/K_CS/N_TOTAL,
                      BRAID_ANGLE_DEG, PHI_STAR_MIN/MAX_DEFAULT, SPREAD_PCT_DEFAULT
  - PentagramBoundsResult: structure, inner/outer vertex arithmetic, tolerances,
                            both_match consistency, interpretation string
  - VarianceWindingResult: structure, spread→sin→degree mapping, error range,
                            matches flag consistency, interpretation string
  - GearRatiosResult: exact arithmetic identities (no tolerance), self-similar
                      flag, cs_gear_check, shared numerator = 35
  - BraidTopologyReport: n_checks_total=4, n_checks_passing range, all_checks_pass,
                          summary string, sub-result delegation
  - pentagram_bounds_check: default call passes both checks, custom values
  - variance_winding_check: default call, tight tolerance should fail, loose passes
  - gear_ratios_check: exact identities, always self_similar=True
  - braid_topology_report: default all-pass, custom values, check count consistency

Gemini topological landmark programme (second round, April 2026):
  ThomasCory Walker-Pearson (scientific direction) ·
  Gemini (adversarial interrogation) ·
  GitHub Copilot (code and tests)
"""

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",  # The braid triad; unique to this framework
}


import math
import numpy as np
import pytest

import sys
import os

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_PENTAD_DIR)
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from braid_topology import (
    # Constants
    PHI_GOLDEN,
    CS_BRAIDED_EXACT,
    N_CORE,
    N_LAYER,
    K_CS,
    N_TOTAL,
    BRAID_ANGLE_DEG,
    PHI_STAR_MIN_DEFAULT,
    PHI_STAR_MAX_DEFAULT,
    SPREAD_PCT_DEFAULT,
    DEFAULT_REL_TOL,
    VARIANCE_REL_TOL,
    # Dataclasses
    PentagramBoundsResult,
    VarianceWindingResult,
    GearRatiosResult,
    BraidTopologyReport,
    # Functions
    pentagram_bounds_check,
    variance_winding_check,
    gear_ratios_check,
    braid_topology_report,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def default_pentagram():
    return pentagram_bounds_check()


@pytest.fixture(scope="module")
def default_variance():
    return variance_winding_check()


@pytest.fixture(scope="module")
def default_gear():
    return gear_ratios_check()


@pytest.fixture(scope="module")
def default_report():
    return braid_topology_report()


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_phi_golden_value(self):
        assert abs(PHI_GOLDEN - (1 + math.sqrt(5)) / 2) < 1e-12

    def test_phi_golden_satisfies_phi_squared_eq_phi_plus_one(self):
        # φ² = φ + 1 (defining property of the golden ratio)
        assert abs(PHI_GOLDEN ** 2 - (PHI_GOLDEN + 1)) < 1e-12

    def test_cs_braided_exact_value(self):
        assert abs(CS_BRAIDED_EXACT - 12 / 37) < 1e-15

    def test_cs_braided_in_unit_interval(self):
        assert 0.0 < CS_BRAIDED_EXACT < 1.0

    def test_n_core_is_five(self):
        assert N_CORE == 5

    def test_n_layer_is_seven(self):
        assert N_LAYER == 7

    def test_k_cs_equals_sum_of_squares(self):
        assert K_CS == N_CORE ** 2 + N_LAYER ** 2

    def test_n_total_equals_sum(self):
        assert N_TOTAL == N_CORE + N_LAYER

    def test_braid_angle_deg_range(self):
        assert 0.0 < BRAID_ANGLE_DEG < 90.0

    def test_braid_angle_deg_value(self):
        expected = math.degrees(math.atan2(N_CORE, N_LAYER))
        assert abs(BRAID_ANGLE_DEG - expected) < 1e-10

    def test_phi_star_min_default_positive(self):
        assert PHI_STAR_MIN_DEFAULT > 0.0

    def test_phi_star_max_default_gt_min(self):
        assert PHI_STAR_MAX_DEFAULT > PHI_STAR_MIN_DEFAULT

    def test_spread_pct_default_range(self):
        assert 0.0 < SPREAD_PCT_DEFAULT < 100.0

    def test_default_rel_tol_in_range(self):
        assert 0.0 < DEFAULT_REL_TOL < 1.0

    def test_variance_rel_tol_geq_default(self):
        assert VARIANCE_REL_TOL >= DEFAULT_REL_TOL


# ---------------------------------------------------------------------------
# pentagram_bounds_check
# ---------------------------------------------------------------------------

class TestPentagramBoundsCheck:
    def test_returns_correct_type(self, default_pentagram):
        assert isinstance(default_pentagram, PentagramBoundsResult)

    def test_phi_golden_stored(self, default_pentagram):
        assert abs(default_pentagram.phi_golden - PHI_GOLDEN) < 1e-12

    def test_cs_braided_stored(self, default_pentagram):
        assert abs(default_pentagram.cs_braided - CS_BRAIDED_EXACT) < 1e-12

    def test_two_over_phi_stored(self, default_pentagram):
        expected = 2.0 / PHI_GOLDEN
        assert abs(default_pentagram.two_over_phi - expected) < 1e-12

    def test_inner_vertex_arithmetic(self, default_pentagram):
        expected = PHI_STAR_MIN_DEFAULT * PHI_GOLDEN ** 2
        assert abs(default_pentagram.inner_vertex - expected) < 1e-12

    def test_inner_rel_error_non_negative(self, default_pentagram):
        assert default_pentagram.inner_rel_error >= 0.0

    def test_outer_rel_error_non_negative(self, default_pentagram):
        assert default_pentagram.outer_rel_error >= 0.0

    def test_inner_rel_error_below_five_pct(self, default_pentagram):
        # 0.122 × φ² ≈ c_s within 5%
        assert default_pentagram.inner_rel_error < 0.05

    def test_outer_rel_error_below_five_pct(self, default_pentagram):
        # 1.253 ≈ 2/φ within 5%
        assert default_pentagram.outer_rel_error < 0.05

    def test_inner_matches_default(self, default_pentagram):
        assert default_pentagram.inner_matches is True

    def test_outer_matches_default(self, default_pentagram):
        assert default_pentagram.outer_matches is True

    def test_both_match_default(self, default_pentagram):
        assert default_pentagram.both_match is True

    def test_both_match_consistent(self, default_pentagram):
        expected = default_pentagram.inner_matches and default_pentagram.outer_matches
        assert default_pentagram.both_match == expected

    def test_rel_tol_stored(self, default_pentagram):
        assert default_pentagram.rel_tol == DEFAULT_REL_TOL

    def test_phi_star_min_stored(self, default_pentagram):
        assert default_pentagram.phi_star_min == PHI_STAR_MIN_DEFAULT

    def test_phi_star_max_stored(self, default_pentagram):
        assert default_pentagram.phi_star_max == PHI_STAR_MAX_DEFAULT

    def test_interpretation_string(self, default_pentagram):
        assert isinstance(default_pentagram.interpretation, str)
        assert len(default_pentagram.interpretation) > 0

    def test_tight_tolerance_inner_fails(self):
        # With 0.1% tolerance the inner vertex (1.5% error) should fail
        r = pentagram_bounds_check(rel_tol=0.001)
        assert r.inner_matches is False

    def test_large_tolerance_both_pass(self):
        r = pentagram_bounds_check(rel_tol=0.50)
        assert r.both_match is True

    def test_exact_cs_input_inner_passes(self):
        # If phi_star_min is set so that phi_star_min × φ² = c_s exactly,
        # inner_rel_error should be ~0.
        perfect_min = CS_BRAIDED_EXACT / (PHI_GOLDEN ** 2)
        r = pentagram_bounds_check(phi_star_min=perfect_min, rel_tol=1e-9)
        assert r.inner_rel_error < 1e-9

    def test_exact_2_over_phi_input_outer_passes(self):
        perfect_max = 2.0 / PHI_GOLDEN
        r = pentagram_bounds_check(phi_star_max=perfect_max, rel_tol=1e-9)
        assert r.outer_rel_error < 1e-9

    def test_inner_vertex_approximates_cs(self):
        # Core physical claim: 0.122 × 2.618 ≈ 0.324
        r = pentagram_bounds_check()
        assert abs(r.inner_vertex - CS_BRAIDED_EXACT) < 0.02

    @pytest.fixture
    def default_pentagram(self):
        return pentagram_bounds_check()


# ---------------------------------------------------------------------------
# variance_winding_check
# ---------------------------------------------------------------------------

class TestVarianceWindingCheck:
    def test_returns_correct_type(self, default_variance):
        assert isinstance(default_variance, VarianceWindingResult)

    def test_spread_pct_stored(self, default_variance):
        assert default_variance.spread_pct == SPREAD_PCT_DEFAULT

    def test_spread_fraction_correct(self, default_variance):
        assert abs(default_variance.spread_fraction - SPREAD_PCT_DEFAULT / 100) < 1e-12

    def test_braid_angle_deg_value(self, default_variance):
        expected = math.degrees(math.atan2(N_CORE, N_LAYER))
        assert abs(default_variance.braid_angle_deg - expected) < 1e-10

    def test_sin_braid_angle_value(self, default_variance):
        expected = math.sin(math.atan2(N_CORE, N_LAYER))
        assert abs(default_variance.sin_braid_angle - expected) < 1e-12

    def test_sin_braid_angle_in_unit_interval(self, default_variance):
        assert 0.0 < default_variance.sin_braid_angle < 1.0

    def test_spread_as_sin_deg_in_range(self, default_variance):
        assert 0.0 < default_variance.spread_as_sin_deg < 90.0

    def test_spread_as_sin_deg_approx_33(self, default_variance):
        # arcsin(0.546) ≈ 33.1°
        assert abs(default_variance.spread_as_sin_deg - 33.0) < 2.0

    def test_rel_error_non_negative(self, default_variance):
        assert default_variance.rel_error >= 0.0

    def test_rel_error_below_variance_tol(self, default_variance):
        # Default uses VARIANCE_REL_TOL = 10%
        assert default_variance.rel_error < VARIANCE_REL_TOL

    def test_matches_default(self, default_variance):
        assert default_variance.matches is True

    def test_matches_consistent(self, default_variance):
        expected = default_variance.rel_error < VARIANCE_REL_TOL
        assert default_variance.matches == expected

    def test_rel_tol_stored(self, default_variance):
        assert default_variance.rel_tol == VARIANCE_REL_TOL

    def test_interpretation_string(self, default_variance):
        assert isinstance(default_variance.interpretation, str)

    def test_tight_tolerance_fails(self):
        # At 1% tolerance the ~6% error should fail
        r = variance_winding_check(rel_tol=0.01)
        assert r.matches is False

    def test_perfect_spread_passes(self):
        # Feed exactly sin(braid_angle) as the spread
        sin_ba = math.sin(math.atan2(N_CORE, N_LAYER))
        r = variance_winding_check(spread_pct=sin_ba * 100, rel_tol=1e-9)
        assert r.rel_error < 1e-9
        assert r.matches is True

    def test_zero_spread_rel_error_is_sin(self):
        # spread=0 → spread_fraction=0 → rel_error = sin_braid / sin_braid = 1
        r = variance_winding_check(spread_pct=0.0, rel_tol=2.0)
        assert abs(r.rel_error - 1.0) < 1e-10

    def test_spread_fraction_in_unit_interval_for_default(self, default_variance):
        assert 0.0 < default_variance.spread_fraction < 1.0


# ---------------------------------------------------------------------------
# gear_ratios_check
# ---------------------------------------------------------------------------

class TestGearRatiosCheck:
    def test_returns_correct_type(self, default_gear):
        assert isinstance(default_gear, GearRatiosResult)

    def test_n_core(self, default_gear):
        assert default_gear.n_core == N_CORE

    def test_n_layer(self, default_gear):
        assert default_gear.n_layer == N_LAYER

    def test_k_cs(self, default_gear):
        assert default_gear.k_cs == K_CS

    def test_n_total(self, default_gear):
        assert default_gear.n_total == N_TOTAL

    def test_shared_numerator_is_35(self, default_gear):
        assert default_gear.shared_numerator == 35

    def test_shared_numerator_equals_n_core_times_n_layer(self, default_gear):
        assert default_gear.shared_numerator == N_CORE * N_LAYER

    def test_xi_c_value(self, default_gear):
        assert abs(default_gear.xi_c - 35 / 74) < 1e-15

    def test_xi_c_denominator_is_74(self, default_gear):
        assert default_gear.xi_c_denominator == 74

    def test_xi_human_value(self, default_gear):
        assert abs(default_gear.xi_human - 35 / 888) < 1e-15

    def test_xi_human_denominator_is_888(self, default_gear):
        assert default_gear.xi_human_denominator == 888

    def test_xi_human_denominator_equals_kcs_times_ntotal(self, default_gear):
        assert default_gear.xi_human_denominator == K_CS * N_TOTAL

    def test_ratio_xi_c_to_human_equals_ntotal(self, default_gear):
        assert abs(default_gear.ratio_xi_c_to_human - N_TOTAL) < 1e-10

    def test_self_similar_is_true(self, default_gear):
        assert default_gear.self_similar is True

    def test_cs_times_k_cs_equals_24(self, default_gear):
        # c_s × k_cs = (12/37) × 74 = 888/37 = 24
        assert abs(default_gear.cs_times_k_cs - 24.0) < 1e-10

    def test_cs_times_k_cs_equals_2_times_ntotal(self, default_gear):
        assert abs(default_gear.cs_times_k_cs - 2 * N_TOTAL) < 1e-10

    def test_cs_gear_check_is_true(self, default_gear):
        assert default_gear.cs_gear_check is True

    def test_interpretation_string(self, default_gear):
        assert isinstance(default_gear.interpretation, str)
        assert len(default_gear.interpretation) > 0

    def test_xi_c_lt_half(self, default_gear):
        # Ξ_c = 35/74 < 0.5 (not perfectly entangled)
        assert default_gear.xi_c < 0.5

    def test_xi_human_lt_xi_c(self, default_gear):
        assert default_gear.xi_human < default_gear.xi_c

    def test_888_factorisation(self, default_gear):
        # 888 = 8 × 111 = 8 × 3 × 37 = 24 × 37 = 2 × N_total × (k_cs/beat)
        # i.e. 888 = k_cs × N_total
        assert default_gear.xi_human_denominator == K_CS * N_TOTAL

    def test_gear_ratios_pure_arithmetic(self):
        """gear_ratios_check is deterministic — calling twice gives same result."""
        r1 = gear_ratios_check()
        r2 = gear_ratios_check()
        assert r1.self_similar == r2.self_similar
        assert abs(r1.xi_c - r2.xi_c) < 1e-15


# ---------------------------------------------------------------------------
# braid_topology_report
# ---------------------------------------------------------------------------

class TestBraidTopologyReport:
    def test_returns_correct_type(self, default_report):
        assert isinstance(default_report, BraidTopologyReport)

    def test_n_checks_total_is_four(self, default_report):
        assert default_report.n_checks_total == 4

    def test_n_checks_passing_range(self, default_report):
        assert 0 <= default_report.n_checks_passing <= 4

    def test_all_checks_pass_default(self, default_report):
        assert default_report.all_checks_pass is True

    def test_n_checks_passing_default(self, default_report):
        assert default_report.n_checks_passing == 4

    def test_all_checks_pass_consistent(self, default_report):
        expected = default_report.n_checks_passing == default_report.n_checks_total
        assert default_report.all_checks_pass == expected

    def test_summary_string(self, default_report):
        assert isinstance(default_report.summary, str)
        assert len(default_report.summary) > 0

    def test_pentagram_bounds_is_correct_type(self, default_report):
        assert isinstance(default_report.pentagram_bounds, PentagramBoundsResult)

    def test_variance_winding_is_correct_type(self, default_report):
        assert isinstance(default_report.variance_winding, VarianceWindingResult)

    def test_gear_ratios_is_correct_type(self, default_report):
        assert isinstance(default_report.gear_ratios, GearRatiosResult)

    def test_check_count_matches_sub_results(self, default_report):
        pb = default_report.pentagram_bounds
        vw = default_report.variance_winding
        gr = default_report.gear_ratios
        expected = int(pb.inner_matches) + int(pb.outer_matches) + int(vw.matches) + int(gr.self_similar)
        assert default_report.n_checks_passing == expected

    def test_custom_values_run(self):
        r = braid_topology_report(phi_star_min=0.10, phi_star_max=1.20, spread_pct=50.0)
        assert isinstance(r, BraidTopologyReport)

    def test_tighter_rel_tol_may_reduce_checks(self):
        # Very tight tolerance: inner/outer vertex checks might fail
        r = braid_topology_report(rel_tol=0.001)
        assert r.n_checks_passing <= 4

    def test_gear_always_passes_regardless_of_tol(self):
        # gear_ratios_check uses exact arithmetic, not rel_tol
        r = braid_topology_report(rel_tol=1e-10)
        assert r.gear_ratios.self_similar is True

    def test_partial_pass_summary_lists_failures(self):
        r = braid_topology_report(rel_tol=0.001)
        if not r.all_checks_pass:
            # Summary should mention what failed
            assert any(word in r.summary for word in ["Failing", "fail", "pass"])


# ---------------------------------------------------------------------------
# Integration: cross-module arithmetic consistency
# ---------------------------------------------------------------------------

class TestCrossModuleConsistency:
    def test_phi_golden_times_cs_braided(self):
        # φ × c_s = (1.618...) × (0.324...) ≈ 0.524 (not a canonical constant,
        # but verifying no numerical drift between the two definitions)
        product = PHI_GOLDEN * CS_BRAIDED_EXACT
        assert 0.4 < product < 0.6

    def test_inner_vertex_times_phi_squared_recovers_cs(self):
        r = pentagram_bounds_check()
        # r.inner_vertex = PHI_STAR_MIN_DEFAULT × φ²; that should ≈ c_s
        assert abs(r.inner_vertex - CS_BRAIDED_EXACT) / CS_BRAIDED_EXACT < 0.05

    def test_braid_angle_sin_relationship(self):
        # sin²(θ) + cos²(θ) = 1 for the braid angle
        r   = variance_winding_check()
        sin_val = r.sin_braid_angle
        cos_val = math.cos(math.radians(r.braid_angle_deg))
        assert abs(sin_val ** 2 + cos_val ** 2 - 1.0) < 1e-12

    def test_gear_ratio_matches_consciousness_coupling(self):
        from consciousness_constant import CONSCIOUSNESS_COUPLING, HUMAN_COUPLING_FRACTION
        r = gear_ratios_check()
        assert abs(r.xi_c    - CONSCIOUSNESS_COUPLING)    < 1e-12
        assert abs(r.xi_human - HUMAN_COUPLING_FRACTION)  < 1e-12

    def test_report_gear_ratios_match_module_constants(self, default_report):
        r = default_report.gear_ratios
        assert r.n_core == N_CORE
        assert r.k_cs   == K_CS
        assert r.n_total == N_TOTAL

    def test_braid_topology_report_phi_star_defaults(self, default_report):
        assert default_report.pentagram_bounds.phi_star_min == PHI_STAR_MIN_DEFAULT
        assert default_report.pentagram_bounds.phi_star_max == PHI_STAR_MAX_DEFAULT

    def test_report_spread_pct_default(self, default_report):
        assert default_report.variance_winding.spread_pct == SPREAD_PCT_DEFAULT

    @pytest.fixture
    def default_report(self):
        return braid_topology_report()
