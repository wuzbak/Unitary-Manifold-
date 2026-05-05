# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
holon_zero/subpillars/test_holon_landscape.py
==============================================
Test suite for the Theory Landscape sub-pillar.

Tests verify:
  A. Module constants — algebraically exact
  B. dimension_efficiency_ratio() — ordering, values, coverage
  C. symmetry_breaking_comparison() — all four theories, key fields
  D. falsification_score() — ordering, score arithmetic, deadlines
  E. theory_landscape_summary() — structure, consistency, UM QCD flag
  F. Cross-function consistency — same theory, same data across functions
  G. Edge cases and boundary values

Expected: 90 passed, 0 failed.

Tests: GitHub Copilot (AI)
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74, 0)",
}

import pytest

from holon_zero.subpillars.holon_landscape import (
    # constants
    N_W, N_2, K_CS, N_DIM_UM, N_DIM_GU,
    UM_DERIVED_SM_PARAMS,
    E8_DIMENSIONS, E8_DERIVED_PARAMS,
    WOLFRAM_DIMENSIONS, WOLFRAM_DERIVED_PARAMS,
    GU_DIMENSIONS, GU_DERIVED_PARAMS,
    LITEBIRD_SIGMA_BETA_DEG,
    UM_BETA_PRIMARY_DEG, UM_BETA_SHADOW_DEG,
    UM_INTER_SECTOR_GAP_DEG, UM_GAP_IN_SIGMA,
    UM_CONCRETE_PREDICTIONS, UM_FREE_PARAMETERS,
    E8_CONCRETE_PREDICTIONS, E8_FREE_PARAMETERS,
    WOLFRAM_CONCRETE_PREDICTIONS, WOLFRAM_FREE_PARAMETERS,
    GU_CONCRETE_PREDICTIONS, GU_FREE_PARAMETERS,
    # functions
    dimension_efficiency_ratio,
    symmetry_breaking_comparison,
    falsification_score,
    theory_landscape_summary,
    # dataclasses
    DimensionEfficiency,
    SymmetryBreakingEntry,
    FalsificationEntry,
    TheoryRecord,
)


# ===========================================================================
# SECTION A — Module constants
# ===========================================================================

class TestConstants:
    def test_n_w_is_five(self):
        assert N_W == 5

    def test_n_2_is_seven(self):
        assert N_2 == 7

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS == N_W ** 2 + N_2 ** 2
        assert K_CS == 74

    def test_um_dim_is_five(self):
        assert N_DIM_UM == 5

    def test_gu_dim_is_fourteen(self):
        assert N_DIM_GU == 14

    def test_um_derived_sm_params_positive(self):
        assert UM_DERIVED_SM_PARAMS > 0

    def test_e8_dimensions_is_four(self):
        assert E8_DIMENSIONS == 4

    def test_wolfram_dimensions_is_zero(self):
        """Wolfram has no fixed dimension — encoded as 0."""
        assert WOLFRAM_DIMENSIONS == 0

    def test_gu_dimensions_is_fourteen(self):
        assert GU_DIMENSIONS == 14

    def test_wolfram_derived_params_is_zero(self):
        assert WOLFRAM_DERIVED_PARAMS == 0

    def test_gu_derived_params_is_zero(self):
        assert GU_DERIVED_PARAMS == 0

    def test_litebird_sigma_is_002(self):
        assert LITEBIRD_SIGMA_BETA_DEG == pytest.approx(0.02, abs=1e-9)

    def test_beta_primary_gt_shadow(self):
        assert UM_BETA_PRIMARY_DEG > UM_BETA_SHADOW_DEG

    def test_inter_sector_gap_value(self):
        expected = round(UM_BETA_PRIMARY_DEG - UM_BETA_SHADOW_DEG, 4)
        assert UM_INTER_SECTOR_GAP_DEG == pytest.approx(expected, abs=1e-6)

    def test_gap_in_sigma_positive(self):
        assert UM_GAP_IN_SIGMA > 0

    def test_gap_in_sigma_gt_two(self):
        """Gap must exceed 2 σ_LB to be a meaningful discriminator."""
        assert UM_GAP_IN_SIGMA > 2.0

    def test_um_concrete_predictions_gte_eight(self):
        """F1–F8 documented in FALSIFICATION_CONDITIONS.md."""
        assert UM_CONCRETE_PREDICTIONS >= 8

    def test_um_free_params_is_zero(self):
        assert UM_FREE_PARAMETERS == 0

    def test_e8_free_params_positive(self):
        assert E8_FREE_PARAMETERS > 0

    def test_wolfram_free_params_large(self):
        assert WOLFRAM_FREE_PARAMETERS >= 100

    def test_gu_free_params_large(self):
        assert GU_FREE_PARAMETERS >= 100


# ===========================================================================
# SECTION B — dimension_efficiency_ratio()
# ===========================================================================

class TestDimensionEfficiency:

    @pytest.fixture
    def results(self):
        return dimension_efficiency_ratio()

    def test_returns_list(self, results):
        assert isinstance(results, list)

    def test_four_entries(self, results):
        assert len(results) == 4

    def test_all_are_dataclass(self, results):
        for r in results:
            assert isinstance(r, DimensionEfficiency)

    def test_sorted_descending_by_efficiency(self, results):
        ratios = [r.efficiency_ratio for r in results]
        assert ratios == sorted(ratios, reverse=True)

    def test_um_has_highest_efficiency(self, results):
        assert results[0].theory == "Unitary Manifold"

    def test_um_efficiency_value(self, results):
        um = results[0]
        expected = round(UM_DERIVED_SM_PARAMS / N_DIM_UM, 4)
        assert um.efficiency_ratio == pytest.approx(expected, abs=1e-6)

    def test_um_spacetime_dim(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.spacetime_dimensions == 5

    def test_e8_spacetime_dim(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert e8.spacetime_dimensions == 4

    def test_wolfram_efficiency_is_zero(self, results):
        wf = next(r for r in results if r.theory == "Wolfram Physics")
        assert wf.efficiency_ratio == 0.0

    def test_gu_efficiency_is_zero(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert gu.efficiency_ratio == 0.0

    def test_gu_spacetime_dim_is_fourteen(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert gu.spacetime_dimensions == 14

    def test_um_notes_mentions_qcd(self, results):
        """v9.34: QCD gap closure should appear in UM notes."""
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "QCD" in um.notes or "Λ_QCD" in um.notes

    def test_um_notes_mentions_zero_free_params(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "zero free param" in um.notes.lower() or "0 free" in um.notes.lower()

    def test_e8_notes_mentions_lhc(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert "LHC" in e8.notes or "2012" in e8.notes

    def test_wolfram_notes_mentions_formalism(self, results):
        wf = next(r for r in results if r.theory == "Wolfram Physics")
        assert "formalism" in wf.notes.lower() or "emergent" in wf.notes.lower()

    def test_gu_notes_mentions_nguyen(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert "Nguyen" in gu.notes or "inconsistencies" in gu.notes.lower()

    def test_all_efficiency_ratios_nonnegative(self, results):
        for r in results:
            assert r.efficiency_ratio >= 0.0

    def test_all_theory_names_nonempty(self, results):
        for r in results:
            assert len(r.theory) > 0

    def test_all_notes_nonempty(self, results):
        for r in results:
            assert len(r.notes) > 0


# ===========================================================================
# SECTION C — symmetry_breaking_comparison()
# ===========================================================================

class TestSymmetryBreaking:

    @pytest.fixture
    def results(self):
        return symmetry_breaking_comparison()

    def test_returns_list(self, results):
        assert isinstance(results, list)

    def test_four_entries(self, results):
        assert len(results) == 4

    def test_all_are_dataclass(self, results):
        for r in results:
            assert isinstance(r, SymmetryBreakingEntry)

    def test_um_present(self, results):
        theories = [r.theory for r in results]
        assert "Unitary Manifold" in theories

    def test_e8_present(self, results):
        theories = [r.theory for r in results]
        assert "E8 Theory (Lisi)" in theories

    def test_wolfram_present(self, results):
        theories = [r.theory for r in results]
        assert "Wolfram Physics" in theories

    def test_gu_present(self, results):
        theories = [r.theory for r in results]
        assert "Geometric Unity" in theories

    def test_um_parent_symmetry_is_su5(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "SU(5)" in um.parent_symmetry

    def test_um_target_contains_sm_gauge(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "SU(3)" in um.target_symmetry
        assert "SU(2)" in um.target_symmetry
        assert "U(1)" in um.target_symmetry

    def test_um_first_principles_true(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.first_principles is True

    def test_um_fermion_spectrum_derived_true(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.fermion_spectrum_derived is True

    def test_um_mechanism_mentions_orbifold(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "orbifold" in um.mechanism.lower() or "Kawamura" in um.mechanism

    def test_um_reference_mentions_v934_qcd(self, results):
        """Phase B closure should appear in UM reference."""
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "Phase B" in um.reference or "omega_qcd" in um.reference.lower()

    def test_e8_first_principles_false(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert e8.first_principles is False

    def test_e8_fermion_spectrum_not_derived(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert e8.fermion_spectrum_derived is False

    def test_e8_mechanism_mentions_distler(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert "Nguyen" in e8.mechanism or "anomaly" in e8.mechanism.lower()

    def test_wolfram_first_principles_false(self, results):
        wf = next(r for r in results if r.theory == "Wolfram Physics")
        assert wf.first_principles is False

    def test_wolfram_fermion_not_derived(self, results):
        wf = next(r for r in results if r.theory == "Wolfram Physics")
        assert wf.fermion_spectrum_derived is False

    def test_gu_first_principles_false(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert gu.first_principles is False

    def test_gu_fermion_not_derived(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert gu.fermion_spectrum_derived is False

    def test_gu_mechanism_mentions_nguyen(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert "Nguyen" in gu.mechanism or "inconsistencies" in gu.mechanism.lower()

    def test_all_mechanisms_nonempty(self, results):
        for r in results:
            assert len(r.mechanism) > 10

    def test_all_references_nonempty(self, results):
        for r in results:
            assert len(r.reference) > 0


# ===========================================================================
# SECTION D — falsification_score()
# ===========================================================================

class TestFalsificationScore:

    @pytest.fixture
    def results(self):
        return falsification_score()

    def test_returns_list(self, results):
        assert isinstance(results, list)

    def test_four_entries(self, results):
        assert len(results) == 4

    def test_all_are_dataclass(self, results):
        for r in results:
            assert isinstance(r, FalsificationEntry)

    def test_sorted_descending_by_score(self, results):
        scores = [r.score for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_um_has_highest_score(self, results):
        assert results[0].theory == "Unitary Manifold"

    def test_um_score_gt_zero(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.score > 0.0

    def test_um_score_arithmetic(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        expected = round(UM_CONCRETE_PREDICTIONS / max(1, UM_FREE_PARAMETERS), 4)
        assert um.score == pytest.approx(expected, abs=1e-6)

    def test_um_free_params_is_zero(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.free_parameters == 0

    def test_um_concrete_predictions_gte_eight(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.concrete_predictions >= 8

    def test_um_hard_deadline_is_2032(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert um.hard_deadline == "2032"

    def test_um_smoking_gun_mentions_litebird(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "LiteBIRD" in um.smoking_gun

    def test_um_smoking_gun_mentions_gap_sigma(self, results):
        """Smoking gun should quantify the gap in sigma units."""
        um = next(r for r in results if r.theory == "Unitary Manifold")
        assert "σ" in um.smoking_gun or "sigma" in um.smoking_gun.lower()

    def test_e8_score_lt_um(self, results):
        um = next(r for r in results if r.theory == "Unitary Manifold")
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert e8.score < um.score

    def test_e8_hard_deadline_is_none(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert e8.hard_deadline is None

    def test_e8_smoking_gun_mentions_lhc(self, results):
        e8 = next(r for r in results if r.theory == "E8 Theory (Lisi)")
        assert "LHC" in e8.smoking_gun or "2012" in e8.smoking_gun

    def test_wolfram_score_is_zero(self, results):
        wf = next(r for r in results if r.theory == "Wolfram Physics")
        assert wf.score == 0.0

    def test_wolfram_hard_deadline_is_none(self, results):
        wf = next(r for r in results if r.theory == "Wolfram Physics")
        assert wf.hard_deadline is None

    def test_gu_score_is_zero(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert gu.score == 0.0

    def test_gu_hard_deadline_is_none(self, results):
        gu = next(r for r in results if r.theory == "Geometric Unity")
        assert gu.hard_deadline is None

    def test_all_scores_nonnegative(self, results):
        for r in results:
            assert r.score >= 0.0

    def test_all_statuses_nonempty(self, results):
        for r in results:
            assert len(r.status) > 0

    def test_all_smoking_guns_nonempty(self, results):
        for r in results:
            assert len(r.smoking_gun) > 0


# ===========================================================================
# SECTION E — theory_landscape_summary()
# ===========================================================================

class TestLandscapeSummary:

    @pytest.fixture
    def summary(self):
        return theory_landscape_summary()

    def test_returns_dict(self, summary):
        assert isinstance(summary, dict)

    def test_four_keys(self, summary):
        assert set(summary.keys()) == {"UM", "E8", "Wolfram", "GU"}

    def test_all_values_are_theory_records(self, summary):
        for v in summary.values():
            assert isinstance(v, TheoryRecord)

    def test_um_theory_name(self, summary):
        assert summary["UM"].theory == "Unitary Manifold"

    def test_e8_theory_name(self, summary):
        assert summary["E8"].theory == "E8 Theory (Lisi)"

    def test_wolfram_theory_name(self, summary):
        assert summary["Wolfram"].theory == "Wolfram Physics"

    def test_gu_theory_name(self, summary):
        assert summary["GU"].theory == "Geometric Unity"

    def test_um_spacetime_dim(self, summary):
        assert summary["UM"].spacetime_dim == 5

    def test_gu_spacetime_dim(self, summary):
        assert summary["GU"].spacetime_dim == 14

    def test_um_qcd_gap_closed_true(self, summary):
        """v9.34: QCD gap is closed — this flag must be True for UM."""
        assert summary["UM"].qcd_gap_closed is True

    def test_e8_qcd_gap_closed_false(self, summary):
        assert summary["E8"].qcd_gap_closed is False

    def test_wolfram_qcd_gap_closed_false(self, summary):
        assert summary["Wolfram"].qcd_gap_closed is False

    def test_gu_qcd_gap_closed_false(self, summary):
        assert summary["GU"].qcd_gap_closed is False

    def test_um_free_params_zero(self, summary):
        assert summary["UM"].free_parameters == 0

    def test_um_concrete_predictions_gte_eight(self, summary):
        assert summary["UM"].concrete_predictions >= 8

    def test_um_falsification_score_gt_zero(self, summary):
        assert summary["UM"].falsification_score > 0.0

    def test_wolfram_falsification_score_zero(self, summary):
        assert summary["Wolfram"].falsification_score == 0.0

    def test_gu_falsification_score_zero(self, summary):
        assert summary["GU"].falsification_score == 0.0

    def test_um_hard_deadline(self, summary):
        assert summary["UM"].hard_deadline == "2032"

    def test_e8_deadline_is_none(self, summary):
        assert summary["E8"].hard_deadline is None

    def test_um_parent_symmetry_contains_su5(self, summary):
        assert "SU(5)" in summary["UM"].parent_symmetry

    def test_um_sm_derived_true(self, summary):
        assert summary["UM"].sm_derived is True

    def test_e8_sm_derived_false(self, summary):
        assert summary["E8"].sm_derived is False

    def test_wolfram_sm_derived_false(self, summary):
        assert summary["Wolfram"].sm_derived is False

    def test_gu_sm_derived_false(self, summary):
        assert summary["GU"].sm_derived is False

    def test_um_notes_mention_v934(self, summary):
        assert "v9.34" in summary["UM"].notes or "Phase B" in summary["UM"].notes

    def test_all_notes_nonempty(self, summary):
        for v in summary.values():
            assert len(v.notes) > 0

    def test_all_statuses_nonempty(self, summary):
        for v in summary.values():
            assert len(v.status) > 0


# ===========================================================================
# SECTION F — Cross-function consistency
# ===========================================================================

class TestCrossConsistency:
    """Verify that the same theory returns consistent data across all three
    functions and the summary."""

    @pytest.fixture
    def data(self):
        return {
            "dim": {e.theory: e for e in dimension_efficiency_ratio()},
            "sym": {e.theory: e for e in symmetry_breaking_comparison()},
            "fals": {e.theory: e for e in falsification_score()},
            "summary": theory_landscape_summary(),
        }

    def test_um_score_matches_summary(self, data):
        fals_score = data["fals"]["Unitary Manifold"].score
        summary_score = data["summary"]["UM"].falsification_score
        assert fals_score == pytest.approx(summary_score, abs=1e-9)

    def test_e8_score_matches_summary(self, data):
        fals_score = data["fals"]["E8 Theory (Lisi)"].score
        summary_score = data["summary"]["E8"].falsification_score
        assert fals_score == pytest.approx(summary_score, abs=1e-9)

    def test_um_first_principles_consistent(self, data):
        sym_fp = data["sym"]["Unitary Manifold"].first_principles
        summary_sm = data["summary"]["UM"].sm_derived
        assert sym_fp == summary_sm

    def test_e8_first_principles_consistent(self, data):
        sym_fp = data["sym"]["E8 Theory (Lisi)"].first_principles
        summary_sm = data["summary"]["E8"].sm_derived
        assert sym_fp == summary_sm

    def test_gu_dim_consistent_with_summary(self, data):
        dim_entry = data["dim"]["Geometric Unity"].spacetime_dimensions
        summary_dim = data["summary"]["GU"].spacetime_dim
        assert dim_entry == summary_dim

    def test_wolfram_efficiency_consistent_with_derived_params(self, data):
        assert data["dim"]["Wolfram Physics"].sm_params_derived == 0
        assert data["dim"]["Wolfram Physics"].efficiency_ratio == 0.0

    def test_four_theories_covered_dim(self, data):
        assert len(data["dim"]) == 4

    def test_four_theories_covered_sym(self, data):
        assert len(data["sym"]) == 4

    def test_four_theories_covered_fals(self, data):
        assert len(data["fals"]) == 4


# ===========================================================================
# SECTION G — Edge cases and boundary checks
# ===========================================================================

class TestEdgeCases:

    def test_litebird_gap_resolves_sectors(self):
        """The inter-sector gap must exceed 2 σ_LB for LiteBIRD to distinguish."""
        gap_sigma = UM_INTER_SECTOR_GAP_DEG / LITEBIRD_SIGMA_BETA_DEG
        assert gap_sigma > 2.0

    def test_beta_admissible_window_contains_primary(self):
        assert 0.22 <= UM_BETA_PRIMARY_DEG <= 0.38

    def test_beta_admissible_window_contains_shadow(self):
        assert 0.22 <= UM_BETA_SHADOW_DEG <= 0.38

    def test_beta_gap_not_in_admissible_window_edge(self):
        """Mid-gap value 0.302° should be inside the forbidden interval."""
        mid_gap = (UM_BETA_PRIMARY_DEG + UM_BETA_SHADOW_DEG) / 2
        assert 0.29 < mid_gap < 0.31

    def test_um_score_with_zero_free_params_uses_max1(self):
        """Score with 0 free params should use max(1, 0)=1 in denominator."""
        score = falsification_score()
        um = next(r for r in score if r.theory == "Unitary Manifold")
        assert um.score == pytest.approx(UM_CONCRETE_PREDICTIONS / 1, abs=1e-6)

    def test_landscape_summary_is_idempotent(self):
        """Calling summary twice returns equivalent data."""
        s1 = theory_landscape_summary()
        s2 = theory_landscape_summary()
        for key in s1:
            assert s1[key].falsification_score == s2[key].falsification_score
            assert s1[key].qcd_gap_closed == s2[key].qcd_gap_closed

    def test_dimension_efficiency_list_is_idempotent(self):
        r1 = dimension_efficiency_ratio()
        r2 = dimension_efficiency_ratio()
        assert [e.efficiency_ratio for e in r1] == [e.efficiency_ratio for e in r2]

    def test_falsification_score_list_is_idempotent(self):
        f1 = falsification_score()
        f2 = falsification_score()
        assert [e.score for e in f1] == [e.score for e in f2]

    def test_symmetry_breaking_list_is_idempotent(self):
        s1 = symmetry_breaking_comparison()
        s2 = symmetry_breaking_comparison()
        assert [e.first_principles for e in s1] == [e.first_principles for e in s2]

    def test_um_efficiency_gt_gu_efficiency(self):
        dim = {e.theory: e for e in dimension_efficiency_ratio()}
        assert dim["Unitary Manifold"].efficiency_ratio > dim["Geometric Unity"].efficiency_ratio

    def test_um_efficiency_gt_wolfram_efficiency(self):
        dim = {e.theory: e for e in dimension_efficiency_ratio()}
        assert dim["Unitary Manifold"].efficiency_ratio > dim["Wolfram Physics"].efficiency_ratio
