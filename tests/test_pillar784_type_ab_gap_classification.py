# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 784 — Type A / Type B Gap Classification.

Covers:
- Module constants and Lean4 accounting
- Gap descriptor structure (G1–G4)
- All four discriminant criteria for each gap
- Constraint-surface Jacobian structure
- Geometric ratio prediction (G2/G3 correlation)
- Residual correlation matrix
- Falsification conditions completeness and structure
- Full gap classification (TYPE_B_STRUCTURAL_FLOOR / TYPE_B_CANDIDATE)
- Full report and certificate structure
- Upstream pillar references
- Honest-note enforcement (no hand-waving)
- Physics consistency: bounds strictly positive, consistent with observation
- DESI exclusion confirmed
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar784_type_ab_gap_classification import (
    # Constants
    N_W,
    K_CS,
    EPSILON,
    EPSILON_SQ,
    EPSILON_4,
    PILLAR,
    PILLAR_NUMBER,
    VERSION,
    STATUS,
    PILLAR_STATUS,
    LEAN4_PREV_TOTAL,
    LEAN4_NEW_THEOREMS,
    LEAN4_NEW_TOTAL,
    LEAN4_MODULE,
    # Physical constants
    ALPHA_S_PDG,
    ALPHA_S_ADS_BOUND,
    G1_IRREDUCIBLE_FRAC,
    G2_RESIDUAL_FRAC,
    G3_RESIDUAL_FRAC,
    M_H_OBS_GEV,
    M_H_5D_CEILING_GEV,
    TENSION_NNLO,
    NLO_FLOOR,
    NNLO_CORRECTION,
    # Gap descriptors
    GAP_G1,
    GAP_G2,
    GAP_G3,
    GAP_G4,
    # Functions
    criterion_1_irreducibility,
    criterion_2_cross_sector_correlation,
    criterion_3_symmetry_character,
    criterion_4_geometric_bound,
    constraint_surface_jacobian,
    geometric_ratio_prediction,
    residual_correlation_matrix,
    type_b_falsification_conditions,
    classify_gap,
    full_gap_classification_report,
    pillar784_certificate,
)

PI = math.pi
ALL_GAPS = ("G1", "G2", "G3", "G4")


# ── Constants ──────────────────────────────────────────────────────────────

class TestConstants:
    def test_pillar_number(self):
        assert PILLAR == 784
        assert PILLAR_NUMBER == 784

    def test_version_format(self):
        parts = VERSION.split(".")
        assert len(parts) == 2
        assert all(p.isdigit() for p in parts)

    def test_status_token(self):
        assert STATUS == "TYPE_AB_CLASSIFICATION_COMPLETE"
        assert PILLAR_STATUS == STATUS

    def test_lean4_accounting(self):
        assert LEAN4_PREV_TOTAL == 958
        assert LEAN4_NEW_THEOREMS == 18
        assert LEAN4_NEW_TOTAL == LEAN4_PREV_TOTAL + LEAN4_NEW_THEOREMS
        assert LEAN4_NEW_TOTAL == 976

    def test_lean4_module_name(self):
        assert LEAN4_MODULE == "TypeABGapClassification.lean"

    def test_n_w_k_cs(self):
        assert N_W == 5
        assert K_CS == 74
        assert K_CS == N_W ** 2 + 7 ** 2   # sum-of-squares resonance

    def test_epsilon(self):
        assert abs(EPSILON - N_W / K_CS) < 1e-12
        assert abs(EPSILON_SQ - EPSILON ** 2) < 1e-14
        assert abs(EPSILON_4 - EPSILON ** 4) < 1e-16

    def test_epsilon_hierarchy(self):
        assert EPSILON_4 < EPSILON_SQ < EPSILON < 1.0

    def test_physical_constants(self):
        assert ALPHA_S_PDG == pytest.approx(0.1180, rel=1e-4)
        assert ALPHA_S_ADS_BOUND == pytest.approx(PI ** 2 / (2 * K_CS), rel=1e-10)
        assert M_H_OBS_GEV == pytest.approx(125.25, rel=1e-4)
        assert M_H_5D_CEILING_GEV == pytest.approx(72.305, rel=1e-3)
        assert TENSION_NNLO == pytest.approx(1.07, abs=0.02)

    def test_nlo_floor_positive(self):
        assert NLO_FLOOR > 0.0
        expected = EPSILON_SQ * (0.5 + 1.0 / (4.0 * PI ** 2))
        assert NLO_FLOOR == pytest.approx(expected, rel=1e-9)

    def test_nnlo_much_smaller_than_nlo(self):
        assert NNLO_CORRECTION < NLO_FLOOR / 10.0

    def test_residual_fracs_in_range(self):
        assert 0.0 < G1_IRREDUCIBLE_FRAC < 1.0
        assert 0.0 < G2_RESIDUAL_FRAC < 1.0
        assert 0.0 < G3_RESIDUAL_FRAC < 1.0
        assert TENSION_NNLO > 0.0

    def test_g2_residual_frac(self):
        expected = 1.0 - ALPHA_S_ADS_BOUND / ALPHA_S_PDG
        assert G2_RESIDUAL_FRAC == pytest.approx(expected, rel=1e-9)

    def test_g3_residual_frac(self):
        expected = (M_H_OBS_GEV - M_H_5D_CEILING_GEV) / M_H_OBS_GEV
        assert G3_RESIDUAL_FRAC == pytest.approx(expected, rel=1e-9)


# ── Gap descriptors ────────────────────────────────────────────────────────

class TestGapDescriptors:
    def test_all_gaps_have_required_keys(self):
        for gap in (GAP_G1, GAP_G2, GAP_G3, GAP_G4):
            assert "label" in gap
            assert "current_type" in gap
            assert "upstream_pillar" in gap
            assert "upstream_status" in gap
            assert "geometric_bound" in gap

    def test_g1_label_and_type(self):
        assert GAP_G1["label"] == "G1"
        assert GAP_G1["current_type"] == "TYPE_B_STRUCTURAL_FLOOR"
        assert GAP_G1["upstream_pillar"] == 780

    def test_g2_label_and_type(self):
        assert GAP_G2["label"] == "G2"
        assert GAP_G2["current_type"] == "TYPE_B_STRUCTURAL_FLOOR"
        assert GAP_G2["upstream_pillar"] == 782

    def test_g3_label_and_type(self):
        assert GAP_G3["label"] == "G3"
        assert GAP_G3["current_type"] == "TYPE_B_STRUCTURAL_FLOOR"
        assert GAP_G3["upstream_pillar"] == 681

    def test_g4_label_and_type(self):
        assert GAP_G4["label"] == "G4"
        assert GAP_G4["current_type"] == "TYPE_B_CANDIDATE"
        assert GAP_G4["upstream_pillar"] == 779

    def test_g4_candidate_note_present(self):
        assert "candidate_note" in GAP_G4
        assert len(GAP_G4["candidate_note"]) > 10

    def test_upstream_status_tokens(self):
        assert GAP_G1["upstream_status"] == "CMB_PEAK_RESIDUAL_DECOMPOSED_V2"
        assert GAP_G2["upstream_status"] == "ALPHA_S_ALL_ROUTES_ARCHITECTURE_LIMIT"
        assert GAP_G3["upstream_status"] == "MH_ARCHITECTURE_LIMIT_CERTIFIED"
        assert GAP_G4["upstream_status"] == "DM21_NNLO_ARCHITECTURE_LIMIT_CERTIFIED"


# ── Criterion 1 ────────────────────────────────────────────────────────────

class TestCriterion1:
    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_returns_dict(self, gap):
        result = criterion_1_irreducibility(gap)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_required_keys(self, gap):
        result = criterion_1_irreducibility(gap)
        assert "gap_label" in result
        assert "irreducible" in result
        assert "proof_summary" in result
        assert "status" in result

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_all_pass(self, gap):
        result = criterion_1_irreducibility(gap)
        assert result["irreducible"] is True
        assert result["status"] == "CRITERION_1_PASSED"

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_proof_summary_non_empty(self, gap):
        result = criterion_1_irreducibility(gap)
        assert len(result["proof_summary"]) > 20

    def test_g2_jacobian_sign_in_proof(self):
        result = criterion_1_irreducibility("G2")
        assert "< 0" in result["proof_summary"] or "negative" in result["proof_summary"].lower()

    def test_g4_references_nnlo(self):
        result = criterion_1_irreducibility("G4")
        assert "779" in result["proof_summary"] or "NNLO" in result["proof_summary"]

    def test_invalid_gap_raises(self):
        with pytest.raises(ValueError):
            criterion_1_irreducibility("G99")


# ── Criterion 2 ────────────────────────────────────────────────────────────

class TestCriterion2:
    @pytest.mark.parametrize("pair", [
        ("G2", "G3"), ("G2", "G4"), ("G1", "G2"), ("G1", "G3"),
        ("G1", "G4"), ("G3", "G4"),
    ])
    def test_returns_dict(self, pair):
        result = criterion_2_cross_sector_correlation(pair)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("pair", [
        ("G2", "G3"), ("G1", "G2"), ("G1", "G3"),
    ])
    def test_correlated_pairs_pass(self, pair):
        result = criterion_2_cross_sector_correlation(pair)
        assert result["correlation_or_independence_confirmed"] is True
        assert result["status"] == "CRITERION_2_PASSED"

    @pytest.mark.parametrize("pair", [
        ("G2", "G4"), ("G1", "G4"), ("G3", "G4"),
    ])
    def test_g4_pairs_fail_correlation(self, pair):
        # G4 (ε²-dominated) does not correlate with K_CS/kR gaps — criterion 2 partial
        result = criterion_2_cross_sector_correlation(pair)
        assert result["correlation_or_independence_confirmed"] is False
        assert result["status"] == "CRITERION_2_FAILED"

    def test_g2_g3_frac_diff_below_15pct(self):
        gr = geometric_ratio_prediction()
        assert gr["R_G2_G3_frac_diff"] < 0.15

    def test_g2_g4_structurally_different(self):
        gr = geometric_ratio_prediction()
        assert gr["G2_G4_structurally_different"] is True

    def test_invalid_pair_raises(self):
        with pytest.raises(ValueError):
            criterion_2_cross_sector_correlation(("G1", "G99"))


# ── Criterion 3 ────────────────────────────────────────────────────────────

class TestCriterion3:
    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_returns_dict(self, gap):
        result = criterion_3_symmetry_character(gap)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_required_keys(self, gap):
        result = criterion_3_symmetry_character(gap)
        for key in ("gap_label", "scaling_parameter", "scaling_exponent",
                    "z2_parity", "scales_correctly", "status"):
            assert key in result

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_all_pass(self, gap):
        result = criterion_3_symmetry_character(gap)
        assert result["scales_correctly"] is True
        assert result["status"] == "CRITERION_3_PASSED"

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_z2_parity_is_even(self, gap):
        result = criterion_3_symmetry_character(gap)
        assert result["z2_parity"] == "even"

    def test_g4_scaling_exponent_is_2(self):
        result = criterion_3_symmetry_character("G4")
        assert result["scaling_exponent"] == 2

    def test_g1_scaling_is_kR_dependent(self):
        result = criterion_3_symmetry_character("G1")
        assert "kR" in result["scaling_parameter"]

    def test_invalid_gap_raises(self):
        with pytest.raises(ValueError):
            criterion_3_symmetry_character("G99")


# ── Criterion 4 ────────────────────────────────────────────────────────────

class TestCriterion4:
    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_returns_dict(self, gap):
        result = criterion_4_geometric_bound(gap)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_required_keys(self, gap):
        result = criterion_4_geometric_bound(gap)
        for key in ("gap_label", "geometric_bound", "observed_value",
                    "formula", "strictly_positive", "consistent_with_observation", "status"):
            assert key in result

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_all_pass(self, gap):
        result = criterion_4_geometric_bound(gap)
        assert result["strictly_positive"] is True
        assert result["consistent_with_observation"] is True
        assert result["status"] == "CRITERION_4_PASSED"

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_bound_positive(self, gap):
        result = criterion_4_geometric_bound(gap)
        assert result["geometric_bound"] > 0.0

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_bound_le_observed(self, gap):
        result = criterion_4_geometric_bound(gap)
        assert result["geometric_bound"] <= result["observed_value"] + 1e-6

    def test_g1_bound_value(self):
        result = criterion_4_geometric_bound("G1")
        assert result["geometric_bound"] == pytest.approx(4.0, rel=1e-6)

    def test_g2_bound_matches_ads(self):
        result = criterion_4_geometric_bound("G2")
        assert result["geometric_bound"] == pytest.approx(ALPHA_S_ADS_BOUND, rel=1e-9)

    def test_g3_bound_matches_ceiling(self):
        result = criterion_4_geometric_bound("G3")
        assert result["geometric_bound"] == pytest.approx(M_H_5D_CEILING_GEV, rel=1e-4)

    def test_g4_bound_matches_nlo_floor(self):
        result = criterion_4_geometric_bound("G4")
        assert result["geometric_bound"] == pytest.approx(NLO_FLOOR, rel=1e-9)

    def test_invalid_gap_raises(self):
        with pytest.raises(ValueError):
            criterion_4_geometric_bound("G99")


# ── Jacobian ───────────────────────────────────────────────────────────────

class TestJacobian:
    def test_returns_dict(self):
        result = constraint_surface_jacobian()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = constraint_surface_jacobian()
        for key in ("jacobian_4x2", "observable_labels", "parameter_labels",
                    "row_has_nonzero", "no_single_param_closes_all", "interpretation"):
            assert key in result

    def test_jacobian_shape(self):
        result = constraint_surface_jacobian()
        J = result["jacobian_4x2"]
        assert len(J) == 4
        assert all(len(row) == 2 for row in J)

    def test_g1_g2_g4_rows_are_zero(self):
        result = constraint_surface_jacobian()
        J = result["jacobian_4x2"]
        # Rows 0 (G1), 1 (G2), 3 (G4) should be zero
        for i in [0, 1, 3]:
            assert all(abs(x) < 1e-12 for x in J[i]), f"Row {i} unexpectedly non-zero"

    def test_g3_kR_nonzero(self):
        result = constraint_surface_jacobian()
        J = result["jacobian_4x2"]
        # Row 2 (G3), column 0 (kR) should be non-zero
        assert abs(J[2][0]) > 1e-6

    def test_no_single_param_closes_all(self):
        result = constraint_surface_jacobian()
        assert result["no_single_param_closes_all"] is True

    def test_parameter_labels(self):
        result = constraint_surface_jacobian()
        assert result["parameter_labels"] == ["kR", "ε_UV"]

    def test_observable_labels(self):
        result = constraint_surface_jacobian()
        labels = result["observable_labels"]
        assert len(labels) == 4
        assert "G1_Swarp" in labels


# ── Geometric ratio ────────────────────────────────────────────────────────

class TestGeometricRatio:
    def test_returns_dict(self):
        result = geometric_ratio_prediction()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = geometric_ratio_prediction()
        for key in ("G2_residual_frac", "G3_residual_frac",
                    "R_G2_G3_observed", "R_G2_G3_geometric_prediction",
                    "R_G2_G3_frac_diff", "G2_G3_correlation_confirmed",
                    "G2_G4_structurally_different"):
            assert key in result

    def test_fracs_match_module_constants(self):
        result = geometric_ratio_prediction()
        assert result["G2_residual_frac"] == pytest.approx(G2_RESIDUAL_FRAC, rel=1e-9)
        assert result["G3_residual_frac"] == pytest.approx(G3_RESIDUAL_FRAC, rel=1e-9)

    def test_g2_g3_ratio_observed_positive(self):
        result = geometric_ratio_prediction()
        assert result["R_G2_G3_observed"] > 0.0

    def test_g2_g3_correlation_confirmed(self):
        result = geometric_ratio_prediction()
        assert result["G2_G3_correlation_confirmed"] is True

    def test_g2_g4_structurally_different(self):
        result = geometric_ratio_prediction()
        assert result["G2_G4_structurally_different"] is True

    def test_frac_diff_below_threshold(self):
        result = geometric_ratio_prediction()
        assert result["R_G2_G3_frac_diff"] < 0.15


# ── Correlation matrix ─────────────────────────────────────────────────────

class TestCorrelationMatrix:
    def test_returns_dict(self):
        result = residual_correlation_matrix()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = residual_correlation_matrix()
        assert "labels" in result
        assert "correlation_matrix" in result
        assert "interpretation" in result

    def test_matrix_shape(self):
        result = residual_correlation_matrix()
        C = result["correlation_matrix"]
        assert len(C) == 4
        assert all(len(row) == 4 for row in C)

    def test_labels(self):
        result = residual_correlation_matrix()
        assert result["labels"] == ["G1", "G2", "G3", "G4"]

    def test_matrix_values_in_range(self):
        result = residual_correlation_matrix()
        for row in result["correlation_matrix"]:
            for val in row:
                assert 0.0 <= val <= 1.0


# ── Falsification conditions ───────────────────────────────────────────────

class TestFalsificationConditions:
    def test_returns_list(self):
        result = type_b_falsification_conditions()
        assert isinstance(result, list)

    def test_exactly_four_conditions(self):
        result = type_b_falsification_conditions()
        assert len(result) == 4

    def test_all_gaps_covered(self):
        result = type_b_falsification_conditions()
        covered = {c["gap"] for c in result}
        assert covered == {"G1", "G2", "G3", "G4"}

    def test_required_keys_per_condition(self):
        for cond in type_b_falsification_conditions():
            for key in ("gap", "current_type", "falsification_observable",
                        "experiment", "threshold", "falsification_implies",
                        "currently_unfalsified"):
                assert key in cond, f"Missing key {key!r} in {cond['gap']}"

    def test_all_currently_unfalsified(self):
        for cond in type_b_falsification_conditions():
            assert cond["currently_unfalsified"] is True

    def test_g1_g2_pre_registered(self):
        conds = {c["gap"]: c for c in type_b_falsification_conditions()}
        assert conds["G1"]["pre_registered"] is True
        assert conds["G2"]["pre_registered"] is True

    def test_g4_is_candidate_in_conditions(self):
        conds = {c["gap"]: c for c in type_b_falsification_conditions()}
        assert "CANDIDATE" in conds["G4"]["current_type"]

    def test_thresholds_non_empty(self):
        for cond in type_b_falsification_conditions():
            assert len(cond["threshold"]) > 20

    def test_experiments_non_empty(self):
        for cond in type_b_falsification_conditions():
            assert len(cond["experiment"]) > 5

    def test_g1_references_cmb_s4(self):
        conds = {c["gap"]: c for c in type_b_falsification_conditions()}
        assert "CMB-S4" in conds["G1"]["experiment"] or "LiteBIRD" in conds["G1"]["experiment"]

    def test_g3_references_f_theory(self):
        conds = {c["gap"]: c for c in type_b_falsification_conditions()}
        assert "F-theory" in conds["G3"]["experiment"] or "M-theory" in conds["G3"]["falsification_observable"]


# ── Classification ─────────────────────────────────────────────────────────

class TestClassifyGap:
    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_returns_dict(self, gap):
        result = classify_gap(gap)
        assert isinstance(result, dict)

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_required_keys(self, gap):
        result = classify_gap(gap)
        for key in ("gap_label", "classification", "rationale", "criteria",
                    "criterion_details"):
            assert key in result

    def test_g1_is_type_b_floor(self):
        result = classify_gap("G1")
        assert result["classification"] == "TYPE_B_STRUCTURAL_FLOOR"

    def test_g2_is_type_b_floor(self):
        result = classify_gap("G2")
        assert result["classification"] == "TYPE_B_STRUCTURAL_FLOOR"

    def test_g3_is_type_b_floor(self):
        result = classify_gap("G3")
        assert result["classification"] == "TYPE_B_STRUCTURAL_FLOOR"

    def test_g4_is_type_b_candidate(self):
        result = classify_gap("G4")
        assert result["classification"] == "TYPE_B_CANDIDATE"

    @pytest.mark.parametrize("gap", ALL_GAPS)
    def test_criteria_dict_has_four_keys(self, gap):
        result = classify_gap(gap)
        assert len(result["criteria"]) == 4

    @pytest.mark.parametrize("gap", ("G1", "G2", "G3"))
    def test_all_four_criteria_pass_for_floors(self, gap):
        result = classify_gap(gap)
        assert all(result["criteria"].values()), f"Not all criteria passed for {gap}"

    def test_g4_criteria_1_3_4_pass_c2_partial(self):
        result = classify_gap("G4")
        c = result["criteria"]
        assert c["c1_irreducibility"] is True
        assert c["c3_symmetry"] is True
        assert c["c4_geometric_bound"] is True
        assert c["c2_correlation"] is False  # G4 doesn't correlate with K_CS gaps

    def test_rationale_non_empty(self):
        for gap in ALL_GAPS:
            result = classify_gap(gap)
            assert len(result["rationale"]) > 20

    def test_invalid_gap_raises(self):
        with pytest.raises((ValueError, KeyError)):
            classify_gap("G99")


# ── Full report ────────────────────────────────────────────────────────────

class TestFullReport:
    def test_returns_dict(self):
        result = full_gap_classification_report()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = full_gap_classification_report()
        for key in ("classifications", "type_b_structural_floors",
                    "type_b_candidates", "type_a_derivation_gaps",
                    "summary", "falsification_conditions",
                    "honest_note", "desi_excluded"):
            assert key in result

    def test_three_floors(self):
        result = full_gap_classification_report()
        assert len(result["type_b_structural_floors"]) == 3

    def test_one_candidate(self):
        result = full_gap_classification_report()
        assert len(result["type_b_candidates"]) == 1
        assert "G4" in result["type_b_candidates"]

    def test_no_type_a_gaps(self):
        result = full_gap_classification_report()
        assert len(result["type_a_derivation_gaps"]) == 0

    def test_honest_note_content(self):
        result = full_gap_classification_report()
        note = result["honest_note"]
        assert "FALLIBILITY" in note or "honest" in note.lower()
        assert "falsif" in note.lower()

    def test_desi_excluded(self):
        result = full_gap_classification_report()
        assert "DESI" in result["desi_excluded"]
        assert "DR3" in result["desi_excluded"]

    def test_summary_string(self):
        result = full_gap_classification_report()
        assert "3" in result["summary"]
        assert "1" in result["summary"]


# ── Certificate ────────────────────────────────────────────────────────────

class TestCertificate:
    def test_returns_dict(self):
        result = pillar784_certificate()
        assert isinstance(result, dict)

    def test_required_keys(self):
        result = pillar784_certificate()
        for key in ("pillar", "version", "status", "pillar_status",
                    "lean4_module", "lean4_prev_total", "lean4_new_theorems",
                    "lean4_new_total", "upstream_pillars", "gap_classification",
                    "constraint_surface_jacobian", "residual_correlation_matrix",
                    "geometric_ratio", "literature_anchors", "honest_summary"):
            assert key in result

    def test_pillar_number(self):
        result = pillar784_certificate()
        assert result["pillar"] == 784

    def test_lean4_total(self):
        result = pillar784_certificate()
        assert result["lean4_new_total"] == 976

    def test_upstream_pillars(self):
        result = pillar784_certificate()
        up = result["upstream_pillars"]
        assert up["G1_CMB"] == 780
        assert up["G2_alpha_s"] == 782
        assert up["G3_mH"] == 681
        assert up["G4_DM21"] == 779

    def test_literature_anchors_non_empty(self):
        result = pillar784_certificate()
        assert len(result["literature_anchors"]) >= 4

    def test_ooguri_vafa_cited(self):
        result = pillar784_certificate()
        text = " ".join(result["literature_anchors"])
        assert "Ooguri" in text or "Swampland" in text

    def test_csaki_cited(self):
        result = pillar784_certificate()
        text = " ".join(result["literature_anchors"])
        assert "Csaki" in text or "RS1" in text

    def test_honest_summary_content(self):
        result = pillar784_certificate()
        s = result["honest_summary"]
        assert "STRUCTURAL_FLOOR" in s
        assert "CANDIDATE" in s
        assert "DESI" in s
        assert "DR3" in s

    def test_honest_summary_no_overclaim(self):
        result = pillar784_certificate()
        s = result["honest_summary"]
        # Must not claim all four are structural floors
        assert "G4" in s
        assert "CANDIDATE" in s

    def test_status_token(self):
        result = pillar784_certificate()
        assert result["status"] == "TYPE_AB_CLASSIFICATION_COMPLETE"


# ── Physics consistency ────────────────────────────────────────────────────

class TestPhysicsConsistency:
    def test_ads_bound_below_pdg(self):
        assert ALPHA_S_ADS_BOUND < ALPHA_S_PDG

    def test_higgs_ceiling_below_observed(self):
        assert M_H_5D_CEILING_GEV < M_H_OBS_GEV

    def test_tension_is_moderate(self):
        # 1.07σ — not a large tension (pre-falsification threshold)
        assert 0.5 < TENSION_NNLO < 3.0

    def test_nlo_floor_correct_formula(self):
        expected = EPSILON_SQ * (0.5 + 1.0 / (4.0 * PI ** 2))
        assert NLO_FLOOR == pytest.approx(expected, rel=1e-9)

    def test_g1_irreducible_frac_matches_780(self):
        # Pillar 780 R_IRREDUCIBLE = 0.33647
        assert G1_IRREDUCIBLE_FRAC == pytest.approx(0.33647, abs=0.001)

    def test_k_cs_is_sum_of_squares(self):
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_epsilon_lt_1(self):
        assert EPSILON < 1.0

    def test_all_bounds_strictly_positive(self):
        for gap in ALL_GAPS:
            r = criterion_4_geometric_bound(gap)
            assert r["geometric_bound"] > 0, f"Bound not positive for {gap}"
