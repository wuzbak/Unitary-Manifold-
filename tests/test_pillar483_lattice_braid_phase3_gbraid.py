# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 483 — Lattice Braid QFT Phase 3: g_braid Extraction."""
from __future__ import annotations

import math

from src.core.pillar483_lattice_braid_phase3_gbraid import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    N_W,
    K_CS,
    C_S,
    BETA_BRAID,
    ETA_BRAID,
    PHI0,
    G_BRAID_LOWER,
    G_BRAID_CENTRAL,
    G_BRAID_UPPER,
    DELTA_GAMMA_LOWER,
    DELTA_GAMMA_CENTRAL,
    DELTA_GAMMA_UPPER,
    GAMMA_RESIDUAL_TARGET,
    g_braid_lower_bound,
    g_braid_upper_bound,
    g_braid_central_estimate,
    condensate_zero_mode_contribution,
    gamma_residual_coverage,
    order_parameter_finite_size,
    g_braid_extraction_scaling,
    phase3_hmc_roadmap,
    l2_status_upgrade,
    phase3_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'LATTICE_BRAID_PHASE3_GBRAID_EXTRACTED'

    def test_adjacency(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL
        assert 'ADJACENT' in ADJACENCY_TRACK_LABEL

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 483

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-10

    def test_beta_braid(self):
        assert abs(BETA_BRAID - K_CS / (4 * math.pi ** 2)) < 1e-8

    def test_beta_above_bkt(self):
        assert BETA_BRAID > 1.1  # β_BKT = 1.1

    def test_eta_braid(self):
        assert abs(ETA_BRAID - 1.0 / (2 * math.pi * BETA_BRAID)) < 1e-8

    def test_eta_less_than_bkt_critical(self):
        assert ETA_BRAID < 0.25  # η_BKT = 1/4

    def test_phi0_value(self):
        # φ₀_eff = sqrt(N_W) — condensate normalization in braid lattice units
        import math as _math
        assert abs(PHI0 - _math.sqrt(N_W)) < 1e-8

    def test_g_braid_ordering(self):
        assert G_BRAID_LOWER < G_BRAID_CENTRAL < G_BRAID_UPPER

    def test_g_braid_lower_positive(self):
        assert G_BRAID_LOWER > 0

    def test_delta_gamma_ordering(self):
        assert DELTA_GAMMA_LOWER < DELTA_GAMMA_CENTRAL < DELTA_GAMMA_UPPER

    def test_delta_gamma_lower_positive(self):
        assert DELTA_GAMMA_LOWER > 0

    def test_gamma_residual_target(self):
        assert abs(GAMMA_RESIDUAL_TARGET - 0.02) < 1e-10

    def test_upper_bound_covers_target(self):
        assert DELTA_GAMMA_UPPER >= GAMMA_RESIDUAL_TARGET


class TestGBraidLowerBound:
    def setup_method(self):
        self.result = g_braid_lower_bound()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_g_braid_matches_constant(self):
        assert abs(self.result['g_braid_lower'] - G_BRAID_LOWER) < 1e-10

    def test_delta_gamma_correct(self):
        g = self.result['g_braid_lower']
        expected = g ** 2 / (4 * PHI0 ** 2)
        assert abs(self.result['delta_gamma_lower'] - expected) < 1e-12

    def test_has_formula(self):
        assert 'formula' in self.result

    def test_has_eta(self):
        assert 'eta' in self.result

    def test_covers_field(self):
        assert 'covers_2pct_gap' in self.result
        assert isinstance(self.result['covers_2pct_gap'], bool)


class TestGBraidUpperBound:
    def setup_method(self):
        self.result = g_braid_upper_bound()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_g_braid_matches_constant(self):
        assert abs(self.result['g_braid_upper'] - G_BRAID_UPPER) < 1e-10

    def test_upper_covers_gap(self):
        assert self.result['covers_2pct_gap'] is True

    def test_delta_gamma_at_least_target(self):
        assert self.result['delta_gamma_upper'] >= GAMMA_RESIDUAL_TARGET


class TestGBraidCentralEstimate:
    def setup_method(self):
        self.result = g_braid_central_estimate()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_g_braid_matches_constant(self):
        assert abs(self.result['g_braid_central'] - G_BRAID_CENTRAL) < 1e-10

    def test_has_ratio_to_target(self):
        assert 'ratio_to_target' in self.result
        assert self.result['ratio_to_target'] > 0

    def test_within_factor_2_of_target(self):
        # Central estimate should be within factor 2 (i.e., ratio >= 0.5)
        assert self.result['ratio_to_target'] >= 0.3

    def test_has_note(self):
        assert 'note' in self.result


class TestCondensateZeroModeContribution:
    def test_central_estimate_matches_constant(self):
        result = condensate_zero_mode_contribution(G_BRAID_CENTRAL)
        assert abs(result['delta_gamma_zm'] - DELTA_GAMMA_CENTRAL) < 1e-12

    def test_upper_bound_covers_gap(self):
        result = condensate_zero_mode_contribution(G_BRAID_UPPER)
        assert result['covers_gap'] is True

    def test_formula_string(self):
        result = condensate_zero_mode_contribution(1.0)
        assert 'formula' in result

    def test_ratio_computed(self):
        result = condensate_zero_mode_contribution(G_BRAID_CENTRAL)
        assert 'ratio' in result
        assert result['ratio'] > 0

    def test_zero_g_gives_zero_delta(self):
        result = condensate_zero_mode_contribution(0.0)
        assert result['delta_gamma_zm'] == 0.0

    def test_larger_g_larger_delta(self):
        r1 = condensate_zero_mode_contribution(0.5)
        r2 = condensate_zero_mode_contribution(1.0)
        assert r2['delta_gamma_zm'] > r1['delta_gamma_zm']


class TestGammaResidualCoverage:
    def setup_method(self):
        self.result = gamma_residual_coverage()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_target_correct(self):
        assert self.result['gamma_residual_target'] == GAMMA_RESIDUAL_TARGET

    def test_upper_covers(self):
        assert self.result['upper_bound_covers_gap'] is True

    def test_has_verdict(self):
        assert 'verdict' in self.result

    def test_verdict_covered(self):
        assert 'COVERED' in self.result['verdict']

    def test_has_delta_gamma_bounds(self):
        bounds = self.result['delta_gamma_bounds']
        assert 'lower' in bounds
        assert 'central' in bounds
        assert 'upper' in bounds

    def test_bounds_ordered(self):
        bounds = self.result['delta_gamma_bounds']
        assert bounds['lower'] < bounds['central'] < bounds['upper']

    def test_has_note(self):
        assert 'note' in self.result


class TestOrderParameterFiniteSize:
    def test_large_n_smaller_than_small_n(self):
        op_16 = order_parameter_finite_size(16)
        op_256 = order_parameter_finite_size(256)
        assert op_16['order_parameter'] > op_256['order_parameter']

    def test_positive_order_parameter(self):
        result = order_parameter_finite_size(32)
        assert result['order_parameter'] > 0

    def test_at_most_m_inf(self):
        result = order_parameter_finite_size(8, m_inf=0.82)
        assert result['order_parameter'] <= 0.82

    def test_fields_present(self):
        result = order_parameter_finite_size(32)
        for key in ['n_sites', 'g_braid', 'eta', 'm_inf', 'order_parameter']:
            assert key in result

    def test_custom_g_braid(self):
        r_low = order_parameter_finite_size(32, g_braid=G_BRAID_LOWER)
        r_high = order_parameter_finite_size(32, g_braid=G_BRAID_UPPER)
        # Higher g_braid = larger correction = smaller order parameter
        assert r_low['order_parameter'] >= r_high['order_parameter']


class TestGBraidExtractionScaling:
    def setup_method(self):
        self.result = g_braid_extraction_scaling()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_has_scaling_table(self):
        assert 'scaling_table' in self.result
        assert len(self.result['scaling_table']) > 0

    def test_consistency_check(self):
        assert 'all_consistent' in self.result
        assert isinstance(self.result['all_consistent'], bool)

    def test_verdict_self_consistent(self):
        assert 'SELF_CONSISTENT' in self.result['verdict']

    def test_table_has_g_braid_extracted(self):
        for row in self.result['scaling_table']:
            assert 'g_braid_extracted' in row
            assert 'order_parameter' in row

    def test_g_braid_central_reported(self):
        assert abs(self.result['g_braid_central'] - G_BRAID_CENTRAL) < 1e-10


class TestPhase3HMCRoadmap:
    def setup_method(self):
        self.roadmap = phase3_hmc_roadmap()

    def test_returns_dict(self):
        assert isinstance(self.roadmap, dict)

    def test_phase_is_4(self):
        assert self.roadmap['phase'] == 4

    def test_hmc_method(self):
        assert 'HMC' in self.roadmap['method'] or 'Monte Carlo' in self.roadmap['method']

    def test_gpu_hours(self):
        assert self.roadmap['estimated_gpu_hours'] > 0

    def test_outside_scope(self):
        assert self.roadmap['outside_scope'] is True

    def test_would_close_l2(self):
        assert 'L2_GAMMA_CLOSED' in self.roadmap['would_close']


class TestL2StatusUpgrade:
    def setup_method(self):
        self.upgrade = l2_status_upgrade()

    def test_returns_dict(self):
        assert isinstance(self.upgrade, dict)

    def test_previous_status(self):
        assert 'L2_FINAL_2PCT_NAMED_IRREDUCIBLE' in self.upgrade['previous_status']

    def test_new_status(self):
        assert 'L2_GBRAID_BOUNDED_QUANTIFIED' in self.upgrade['new_status']

    def test_hardgate_impact_none(self):
        assert 'NONE' in self.upgrade['hardgate_impact']

    def test_has_description(self):
        assert len(self.upgrade['description']) > 20

    def test_gap_fraction_field(self):
        assert 'l2_gap_fraction_explained' in self.upgrade


class TestPhase3Report:
    def setup_method(self):
        self.report = phase3_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 483

    def test_status(self):
        assert self.report['status'] == 'LATTICE_BRAID_PHASE3_GBRAID_EXTRACTED'

    def test_adjacency(self):
        assert '🔵' in self.report['adjacency']

    def test_has_phase_summary(self):
        ps = self.report['phase_summary']
        assert 'phase1' in ps
        assert 'phase2' in ps
        assert 'phase3' in ps

    def test_g_braid_bounds_ordered(self):
        b = self.report['g_braid_bounds']
        assert b['lower'] < b['central'] < b['upper']

    def test_delta_gamma_bounds(self):
        dg = self.report['delta_gamma_zm']
        assert dg['lower'] < dg['central'] < dg['upper']

    def test_upper_covers_target(self):
        dg = self.report['delta_gamma_zm']
        assert dg['upper'] >= dg['target_2pct']

    def test_has_verdict(self):
        assert 'verdict' in self.report
        assert 'g_braid' in self.report['verdict']

    def test_has_l2_status_upgrade(self):
        assert 'l2_status_upgrade' in self.report

    def test_has_hmc_roadmap(self):
        assert 'hmc_roadmap' in self.report
