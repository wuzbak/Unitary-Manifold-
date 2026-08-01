# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 573: Anchor C — Matter Curves → c_L Lower Bound.

src/twelved/ftheory_matter_curves.py — 🔵 ADJACENT TRACK
"""

from __future__ import annotations

import math

import pytest

from src.twelved.ftheory_matter_curves import (
    C_L_FTHEORY_MIN,
    C_L_MANUAL_CUTOFF,
    EPISTEMIC_STATUS,
    K_CS,
    M_KK_GEV,
    N_W,
    PI_KR,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SUM_MNU_BOUND_GEV,
    axiomzero_seed_purity_check,
    cl_bound_comparison,
    gap_b_assessment,
    kill_switch_check,
    matter_curve_yukawa_constraint,
    matter_curves_summary,
    strong_ftheory_cl_bound,
    weak_normalizability_bound,
)


# ---------------------------------------------------------------------------
# Metadata constants
# ---------------------------------------------------------------------------

class TestMetadataConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 573

    def test_pillar_status_nonempty(self):
        assert len(PILLAR_STATUS) > 10

    def test_adjacent_in_status(self):
        assert "ADJACENT" in PILLAR_STATUS

    def test_epistemic_status(self):
        assert EPISTEMIC_STATUS == "ADJACENT_TRACK"

    def test_title_nonempty(self):
        assert len(PILLAR_TITLE) > 10


# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

class TestPhysicalConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_pi_kr(self):
        assert PI_KR == 37.0

    def test_m_kk_gev(self):
        assert M_KK_GEV == 1000.0

    def test_sum_mnu_bound_gev(self):
        # 0.12 eV in GeV = 0.12e-9 GeV
        assert abs(SUM_MNU_BOUND_GEV - 0.12e-9) < 1e-15

    def test_c_l_manual_cutoff(self):
        assert C_L_MANUAL_CUTOFF == 0.88

    def test_c_l_ftheory_min_above_half(self):
        assert C_L_FTHEORY_MIN > 0.5

    def test_c_l_ftheory_min_above_manual(self):
        # F-theory bound should be slightly above manual cutoff
        assert C_L_FTHEORY_MIN > C_L_MANUAL_CUTOFF

    def test_c_l_ftheory_min_value(self):
        # Recalculate independently
        m_nu1_max = SUM_MNU_BOUND_GEV / 3.0
        expected = 0.5 + math.log(M_KK_GEV / m_nu1_max) / (2.0 * PI_KR)
        assert abs(C_L_FTHEORY_MIN - expected) < 1e-10

    def test_c_l_ftheory_min_range(self):
        # Should be in reasonable range [0.88, 1.1]
        assert 0.88 < C_L_FTHEORY_MIN < 1.1


# ---------------------------------------------------------------------------
# weak_normalizability_bound
# ---------------------------------------------------------------------------

class TestWeakNormalizabilityBound:
    def test_passes(self):
        r = weak_normalizability_bound()
        assert r["pass"] is True

    def test_c_l_weak_is_half(self):
        r = weak_normalizability_bound()
        assert r["c_l_weak_bound"] == 0.5

    def test_manual_cutoff_present(self):
        r = weak_normalizability_bound()
        assert r["c_l_manual_cutoff"] == C_L_MANUAL_CUTOFF

    def test_weak_below_manual(self):
        r = weak_normalizability_bound()
        assert r["weak_bound_below_manual"] is True

    def test_evidence_nonempty(self):
        r = weak_normalizability_bound()
        assert len(r["evidence"]) > 0


# ---------------------------------------------------------------------------
# strong_ftheory_cl_bound
# ---------------------------------------------------------------------------

class TestStrongFTheoryClBound:
    def test_default_passes(self):
        r = strong_ftheory_cl_bound()
        assert r["pass"] is True

    def test_c_l_ftheory_min_correct(self):
        r = strong_ftheory_cl_bound()
        assert abs(r["c_l_ftheory_min"] - C_L_FTHEORY_MIN) < 1e-10

    def test_ftheory_above_manual(self):
        r = strong_ftheory_cl_bound()
        assert r["ftheory_bound_above_manual"] is True

    def test_ftheory_consistent_with_manual(self):
        r = strong_ftheory_cl_bound()
        assert r["ftheory_bound_consistent_with_manual"] is True

    def test_m_kk_stored(self):
        r = strong_ftheory_cl_bound()
        assert r["m_kk_gev"] == M_KK_GEV

    def test_pi_kr_stored(self):
        r = strong_ftheory_cl_bound()
        assert r["pi_kr"] == PI_KR

    def test_m_nu1_max_computed(self):
        r = strong_ftheory_cl_bound()
        expected = SUM_MNU_BOUND_GEV / 3.0
        assert abs(r["m_nu1_max_gev"] - expected) < 1e-20

    def test_log_ratio_positive(self):
        r = strong_ftheory_cl_bound()
        assert r["log_ratio"] > 0

    def test_evidence_nonempty(self):
        r = strong_ftheory_cl_bound()
        assert len(r["evidence"]) > 0

    def test_custom_pi_kr_larger_gives_smaller_cl(self):
        r1 = strong_ftheory_cl_bound(pi_kr=37.0)
        r2 = strong_ftheory_cl_bound(pi_kr=74.0)
        # larger πkR → smaller c_l_min (less warp suppression needed)
        assert r2["c_l_ftheory_min"] < r1["c_l_ftheory_min"]

    def test_invalid_m_kk_raises(self):
        with pytest.raises(ValueError):
            strong_ftheory_cl_bound(m_kk_gev=0.0)

    def test_invalid_sum_mnu_raises(self):
        with pytest.raises(ValueError):
            strong_ftheory_cl_bound(sum_mnu_bound_gev=0.0)


# ---------------------------------------------------------------------------
# cl_bound_comparison
# ---------------------------------------------------------------------------

class TestClBoundComparison:
    def test_passes(self):
        r = cl_bound_comparison()
        assert r["pass"] is True

    def test_three_bounds(self):
        r = cl_bound_comparison()
        bounds = r["bounds"]
        assert "5D_RS_weak" in bounds
        assert "manual_code_cutoff" in bounds
        assert "ftheory_normalizability" in bounds

    def test_ftheory_provides_mechanism(self):
        r = cl_bound_comparison()
        assert r["ftheory_provides_mechanism"] is True

    def test_gap_b_status_nonempty(self):
        r = cl_bound_comparison()
        assert "PARTIALLY_ADDRESSED" in r["gap_b_status"]

    def test_ordering_5d_lt_manual(self):
        r = cl_bound_comparison()
        assert r["bounds"]["5D_RS_weak"] < r["bounds"]["manual_code_cutoff"]

    def test_evidence_nonempty(self):
        r = cl_bound_comparison()
        assert len(r["evidence"]) > 0


# ---------------------------------------------------------------------------
# matter_curve_yukawa_constraint
# ---------------------------------------------------------------------------

class TestMatterCurveYukawaConstraint:
    def test_default_passes(self):
        r = matter_curve_yukawa_constraint()
        assert r["pass"] is True

    def test_n_gen_3(self):
        r = matter_curve_yukawa_constraint()
        assert r["n_gen"] == 3

    def test_matter_curve_count_equals_n_gen(self):
        r = matter_curve_yukawa_constraint()
        assert r["matter_curve_count"] == 3

    def test_k_cs_74(self):
        r = matter_curve_yukawa_constraint()
        assert r["k_cs"] == K_CS

    def test_n_w_5(self):
        r = matter_curve_yukawa_constraint()
        assert r["n_w"] == N_W

    def test_evidence_nonempty(self):
        r = matter_curve_yukawa_constraint()
        assert len(r["evidence"]) > 0


# ---------------------------------------------------------------------------
# gap_b_assessment
# ---------------------------------------------------------------------------

class TestGapBAssessment:
    def test_gap_label(self):
        r = gap_b_assessment()
        assert r["gap"] == "B"

    def test_partially_closed(self):
        r = gap_b_assessment()
        assert r["partially_closed"] is True

    def test_mechanism_identified(self):
        r = gap_b_assessment()
        assert "MECHANISM_IDENTIFIED" in r["after_status"]

    def test_before_was_open(self):
        r = gap_b_assessment()
        assert "OPEN" in r["before_status"]

    def test_toe_score_no_change(self):
        r = gap_b_assessment()
        assert r["toe_score_change"] == 0.0

    def test_has_blocking_residuals(self):
        r = gap_b_assessment()
        assert len(r["blocking_residuals"]) >= 3

    def test_ftheory_mechanism_nonempty(self):
        r = gap_b_assessment()
        assert len(r["ftheory_mechanism"]) > 30

    def test_c_l_ftheory_min_correct(self):
        r = gap_b_assessment()
        assert abs(r["c_l_ftheory_min"] - C_L_FTHEORY_MIN) < 1e-10

    def test_consistent_with_manual(self):
        r = gap_b_assessment()
        assert r["ftheory_consistent_with_manual"] is True


# ---------------------------------------------------------------------------
# axiomzero_seed_purity_check
# ---------------------------------------------------------------------------

class TestAxiomzeroSeedPurityCheck:
    def test_passes(self):
        r = axiomzero_seed_purity_check()
        assert r["pass"] is True

    def test_geometric_inputs_present(self):
        r = axiomzero_seed_purity_check()
        assert len(r["geometric_inputs"]) >= 4

    def test_note_nonempty(self):
        r = axiomzero_seed_purity_check()
        assert len(r["note"]) > 0

    def test_evidence_nonempty(self):
        r = axiomzero_seed_purity_check()
        assert len(r["evidence"]) > 0


# ---------------------------------------------------------------------------
# kill_switch_check
# ---------------------------------------------------------------------------

class TestKillSwitchCheck:
    def test_returns_true(self):
        assert kill_switch_check() is True

    def test_is_bool(self):
        result = kill_switch_check()
        assert isinstance(result, bool)


# ---------------------------------------------------------------------------
# matter_curves_summary
# ---------------------------------------------------------------------------

class TestMatterCurvesSummary:
    def test_pillar_number(self):
        r = matter_curves_summary()
        assert r["pillar"] == 573

    def test_anchor_c(self):
        r = matter_curves_summary()
        assert r["anchor"] == "C"

    def test_kill_switch_pass(self):
        r = matter_curves_summary()
        assert r["kill_switch_pass"] is True

    def test_gap_b_addressed(self):
        r = matter_curves_summary()
        assert r["gap_b_addressed"] is True

    def test_mechanism_identified(self):
        r = matter_curves_summary()
        assert "MECHANISM_IDENTIFIED" in r["gap_b_after_status"]

    def test_c_l_manual_cutoff(self):
        r = matter_curves_summary()
        assert r["c_l_manual_cutoff"] == C_L_MANUAL_CUTOFF

    def test_c_l_ftheory_min_present(self):
        r = matter_curves_summary()
        assert abs(r["c_l_ftheory_min"] - C_L_FTHEORY_MIN) < 1e-10

    def test_ftheory_stronger_than_manual(self):
        r = matter_curves_summary()
        assert r["ftheory_stronger_than_manual"] is True

    def test_bounds_consistent(self):
        r = matter_curves_summary()
        assert r["bounds_consistent"] is True

    def test_toe_score_zero(self):
        r = matter_curves_summary()
        assert r["toe_score_change"] == 0.0

    def test_blocking_residuals(self):
        r = matter_curves_summary()
        assert len(r["blocking_residuals"]) >= 3

    def test_honest_summary_nonempty(self):
        r = matter_curves_summary()
        assert len(r["honest_summary"]) > 50

    def test_honest_summary_mentions_mechanism(self):
        r = matter_curves_summary()
        assert "mechanism" in r["honest_summary"].lower() or "F-theory" in r["honest_summary"]

    def test_epistemic_status(self):
        r = matter_curves_summary()
        assert r["epistemic_status"] == "ADJACENT_TRACK"
