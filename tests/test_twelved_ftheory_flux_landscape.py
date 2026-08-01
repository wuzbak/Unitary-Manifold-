# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 571: Anchor A — CY4 D3-Tadpole and G4 Flux Quantization.

src/twelved/ftheory_flux_landscape.py — 🔵 ADJACENT TRACK
"""

from __future__ import annotations

import math

import pytest

from src.twelved.ftheory_flux_landscape import (
    B4_DOMINANT,
    B4_FULL,
    CY4_CHI,
    CY4_H11,
    CY4_H31,
    EPISTEMIC_STATUS,
    K_CS,
    LOG10_NVAC_10D,
    LOG10_NVAC_CY4,
    N_D3_MAX,
    N_FLUX_10D,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    axiomzero_seed_purity_check,
    cc_architecture_status,
    flux_landscape_summary,
    g4_quantization_check,
    kill_switch_check,
    landscape_density_comparison,
    landscape_vacuum_spacing,
    tadpole_condition,
)


# ---------------------------------------------------------------------------
# Metadata constants
# ---------------------------------------------------------------------------

class TestMetadataConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 571

    def test_pillar_status(self):
        assert "ADJACENT_TRACK" in PILLAR_STATUS

    def test_epistemic_status(self):
        assert EPISTEMIC_STATUS == "ADJACENT_TRACK"

    def test_title_nonempty(self):
        assert len(PILLAR_TITLE) > 10


# ---------------------------------------------------------------------------
# CY4 constants
# ---------------------------------------------------------------------------

class TestCY4Constants:
    def test_chi_cy4(self):
        assert CY4_CHI == 1_820_160

    def test_chi_divisible_24(self):
        assert CY4_CHI % 24 == 0

    def test_n_d3_max(self):
        assert N_D3_MAX == 75_840

    def test_n_d3_equals_chi_over_24(self):
        assert N_D3_MAX == CY4_CHI // 24

    def test_h11(self):
        assert CY4_H11 == 1

    def test_h31(self):
        assert CY4_H31 == 3878

    def test_b4_dominant(self):
        assert B4_DOMINANT == 2 * (2 + CY4_H11 + CY4_H31)

    def test_b4_dominant_value(self):
        assert B4_DOMINANT == 7762

    def test_b4_full_equals_dominant(self):
        assert B4_FULL == B4_DOMINANT

    def test_n_flux_10d(self):
        assert N_FLUX_10D == K_CS // 2

    def test_n_flux_10d_value(self):
        assert N_FLUX_10D == 37

    def test_log10_nvac_10d(self):
        assert LOG10_NVAC_10D == 74

    def test_log10_nvac_cy4_larger_than_10d(self):
        assert LOG10_NVAC_CY4 > LOG10_NVAC_10D

    def test_log10_nvac_cy4_approx(self):
        # 3881 * log10(75840) ≈ 18939
        expected = (B4_DOMINANT / 2) * math.log10(N_D3_MAX)
        assert abs(LOG10_NVAC_CY4 - expected) < 1.0


# ---------------------------------------------------------------------------
# tadpole_condition
# ---------------------------------------------------------------------------

class TestTadpoleCondition:
    def test_exact_satisfaction(self):
        r = tadpole_condition(n_d3=0, n_flux_quanta=N_D3_MAX)
        assert r["pass"] is True
        assert r["deficit"] == 0.0

    def test_split_between_d3_and_flux(self):
        # N_D3 = 1000, N_flux = N_D3_MAX - 1000
        r = tadpole_condition(n_d3=1000, n_flux_quanta=N_D3_MAX - 1000)
        assert r["pass"] is True

    def test_deficit_nonzero_fails(self):
        r = tadpole_condition(n_d3=100, n_flux_quanta=100)
        assert r["pass"] is False
        assert r["deficit"] != 0.0

    def test_negative_n_d3_fails(self):
        r = tadpole_condition(n_d3=-1, n_flux_quanta=N_D3_MAX + 1)
        assert r["pass"] is False

    def test_negative_flux_fails(self):
        r = tadpole_condition(n_d3=N_D3_MAX + 1, n_flux_quanta=-1)
        assert r["pass"] is False

    def test_rhs_value(self):
        r = tadpole_condition(n_d3=0, n_flux_quanta=N_D3_MAX)
        assert r["rhs_chi_over_24"] == 75_840.0

    def test_evidence_string_present(self):
        r = tadpole_condition(n_d3=0, n_flux_quanta=N_D3_MAX)
        assert isinstance(r["evidence"], str) and len(r["evidence"]) > 0

    def test_chi_not_divisible_fails(self):
        r = tadpole_condition(n_d3=0, n_flux_quanta=5, chi_cy4=101)
        assert r["pass"] is False
        assert r["chi_divisible_by_24"] is False


# ---------------------------------------------------------------------------
# g4_quantization_check
# ---------------------------------------------------------------------------

class TestG4QuantizationCheck:
    def test_default_passes(self):
        r = g4_quantization_check()
        assert r["pass"] is True

    def test_flux_max_derived(self):
        r = g4_quantization_check()
        assert r["flux_max_derived"] == N_D3_MAX

    def test_blocking_residual_documented(self):
        r = g4_quantization_check()
        assert len(r["blocking_residual"]) > 20

    def test_wrong_n_d3_max_fails(self):
        r = g4_quantization_check(n_d3_max=99999)
        assert r["pass"] is False

    def test_chi_divisibility(self):
        r = g4_quantization_check()
        assert r["flux_max_derived"] == CY4_CHI // 24


# ---------------------------------------------------------------------------
# landscape_density_comparison
# ---------------------------------------------------------------------------

class TestLandscapeDensityComparison:
    def test_cy4_denser_than_10d(self):
        r = landscape_density_comparison()
        assert r["cy4_denser_than_10d"] is True

    def test_log10_nvac_10d(self):
        r = landscape_density_comparison()
        assert r["log10_nvac_10d"] == 74.0

    def test_log10_nvac_cy4_large(self):
        r = landscape_density_comparison()
        # Should be ~18939
        assert r["log10_nvac_cy4"] > 10000

    def test_improvement_positive(self):
        r = landscape_density_comparison()
        assert r["log10_improvement"] > 0

    def test_status_improvement(self):
        r = landscape_density_comparison()
        assert r["status"] == "ARCHITECTURE_TRACK_IMPROVEMENT"

    def test_honest_caveat_present(self):
        r = landscape_density_comparison()
        assert "NOT" in r["honest_caveat"] or "not" in r["honest_caveat"]


# ---------------------------------------------------------------------------
# landscape_vacuum_spacing
# ---------------------------------------------------------------------------

class TestLandscapeVacuumSpacing:
    def test_contains_observed_lambda(self):
        r = landscape_vacuum_spacing()
        assert r["landscape_contains_observed_lambda"] is True

    def test_spacing_much_smaller_than_obs(self):
        r = landscape_vacuum_spacing()
        assert r["log10_delta_lambda_spacing"] < r["log10_lambda_obs"]

    def test_status_string(self):
        r = landscape_vacuum_spacing()
        assert r["status"] == "LANDSCAPE_CONTAINS_OBSERVED_VALUE"

    def test_caveat_mentions_selection(self):
        r = landscape_vacuum_spacing()
        assert "selection" in r["caveat"].lower() or "vacuum" in r["caveat"].lower()

    def test_log10_lambda_obs_value(self):
        r = landscape_vacuum_spacing()
        # Λ_obs ~ 10^{-122}
        assert r["log10_lambda_obs"] < -100


# ---------------------------------------------------------------------------
# cc_architecture_status
# ---------------------------------------------------------------------------

class TestCCArchitectureStatus:
    def test_not_closed_by_ftheory(self):
        r = cc_architecture_status()
        assert r["closed_by_ftheory"] is False

    def test_status_architecture_limit(self):
        r = cc_architecture_status()
        assert "ARCHITECTURE_LIMIT" in r["status"]

    def test_improvement_over_10d(self):
        r = cc_architecture_status()
        assert r["improvement_over_10d"] is True

    def test_blocking_residuals_listed(self):
        r = cc_architecture_status()
        assert len(r["blocking_residuals"]) >= 3

    def test_honest_summary_present(self):
        r = cc_architecture_status()
        assert "F-theory" in r["honest_summary"] or "CY4" in r["honest_summary"]

    def test_landscape_contains_obs(self):
        r = cc_architecture_status()
        assert r["landscape_contains_observed_lambda"] is True


# ---------------------------------------------------------------------------
# axiomzero_seed_purity_check
# ---------------------------------------------------------------------------

class TestAxiomZeroSeedPurityCheck:
    def test_passes(self):
        r = axiomzero_seed_purity_check()
        assert r["pass"] is True

    def test_no_pdg(self):
        r = axiomzero_seed_purity_check()
        assert len(r["pdg_inputs"]) == 0

    def test_geometric_inputs(self):
        r = axiomzero_seed_purity_check()
        assert len(r["geometric_inputs"]) >= 4


# ---------------------------------------------------------------------------
# kill_switch_check
# ---------------------------------------------------------------------------

class TestKillSwitchCheck:
    def test_returns_true(self):
        assert kill_switch_check() is True


# ---------------------------------------------------------------------------
# flux_landscape_summary
# ---------------------------------------------------------------------------

class TestFluxLandscapeSummary:
    def test_pillar_number(self):
        r = flux_landscape_summary()
        assert r["pillar"] == 571

    def test_anchor_a(self):
        r = flux_landscape_summary()
        assert r["anchor"] == "A"

    def test_kill_switch_pass(self):
        r = flux_landscape_summary()
        assert r["kill_switch_pass"] is True

    def test_tadpole_satisfied(self):
        r = flux_landscape_summary()
        assert r["tadpole_max_satisfied"] is True

    def test_g4_consistent(self):
        r = flux_landscape_summary()
        assert r["g4_quantization_consistent"] is True

    def test_cy4_denser(self):
        r = flux_landscape_summary()
        assert r["landscape_cy4_denser"] is True

    def test_cc_not_closed(self):
        r = flux_landscape_summary()
        assert r["cc_architecture_closed"] is False

    def test_n_d3_max(self):
        r = flux_landscape_summary()
        assert r["n_d3_max"] == 75_840

    def test_improvement_note_present(self):
        r = flux_landscape_summary()
        assert len(r["improvement_note"]) > 20

    def test_blocking_residuals_present(self):
        r = flux_landscape_summary()
        assert len(r["blocking_residuals"]) >= 3
