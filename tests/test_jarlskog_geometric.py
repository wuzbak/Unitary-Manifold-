# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 145: Jarlskog Invariant from Braid Curvature
(src/core/jarlskog_geometric.py).

Verifies the geometric proof that J≠0 iff n₁≠n₂, the braid strand phase
asymmetry, and the geometric Jarlskog estimate.
"""

import math
import pytest

from src.core.jarlskog_geometric import (
    braid_strand_phases,
    cp_violation_condition,
    jarlskog_geometric,
    jarlskog_nw_survey,
    pillar145_summary,
    N1_CANONICAL,
    N2_CANONICAL,
    J_PDG,
    J_GEO_CANONICAL,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

class TestModuleConstants:
    def test_n1_canonical(self):
        assert N1_CANONICAL == 5

    def test_n2_canonical(self):
        assert N2_CANONICAL == 7

    def test_j_pdg_order_of_magnitude(self):
        assert 1e-5 < J_PDG < 1e-4

    def test_j_geo_canonical_positive(self):
        assert J_GEO_CANONICAL > 0

    def test_j_geo_canonical_less_than_one(self):
        assert J_GEO_CANONICAL < 1.0


# ---------------------------------------------------------------------------
# braid_strand_phases
# ---------------------------------------------------------------------------

class TestBraidStrandPhases:
    @pytest.fixture(scope="class")
    def phases(self):
        return braid_strand_phases()

    def test_phi_up_positive(self, phases):
        assert phases["phi_up_deg"] > 0

    def test_phi_down_positive(self, phases):
        assert phases["phi_down_deg"] > 0

    def test_phi_up_equals_arctan_5_7(self, phases):
        expected = math.degrees(math.atan2(5, 7))
        assert abs(phases["phi_up_deg"] - expected) < 1e-10

    def test_phi_down_equals_arctan_7_5(self, phases):
        expected = math.degrees(math.atan2(7, 5))
        assert abs(phases["phi_down_deg"] - expected) < 1e-10

    def test_delta_asymm_positive(self, phases):
        assert phases["delta_asymm_deg"] > 0

    def test_delta_asymm_about_19_degrees(self, phases):
        # |arctan(5/7) - arctan(7/5)| ≈ 18.93°
        assert 15 < phases["delta_asymm_deg"] < 25

    def test_phases_do_not_cancel(self, phases):
        assert phases["phases_cancel"] is False

    def test_symmetric_braid_cancels(self):
        p = braid_strand_phases(5, 5)
        assert p["phases_cancel"] is True
        assert abs(p["delta_asymm_deg"]) < 1e-10

    def test_invalid_n1_raises(self):
        with pytest.raises(ValueError):
            braid_strand_phases(0, 7)

    def test_invalid_n2_raises(self):
        with pytest.raises(ValueError):
            braid_strand_phases(5, -1)

    def test_cp_origin_mentions_cancel(self, phases):
        assert "cancel" in phases["cp_violation_origin"].lower() or \
               "not cancel" in phases["cp_violation_origin"].lower()


# ---------------------------------------------------------------------------
# cp_violation_condition
# ---------------------------------------------------------------------------

class TestCPViolationCondition:
    @pytest.fixture(scope="class")
    def result(self):
        return cp_violation_condition()

    def test_canonical_cp_violated(self, result):
        assert result["cp_violated"] is True

    def test_symmetric_no_cp(self):
        r = cp_violation_condition(5, 5)
        assert r["cp_violated"] is False

    def test_theorem_status_proved(self, result):
        assert "PROVEN" in result["theorem_status"] or \
               "PROOF" in result["theorem_status"]

    def test_proof_steps_at_least_4(self, result):
        assert len(result["proof_steps"]) >= 4

    def test_asymmetry_in_result(self, result):
        assert result["delta_asymm_deg"] > 0

    def test_n1_n2_stored(self, result):
        assert result["n1"] == N1_CANONICAL
        assert result["n2"] == N2_CANONICAL

    def test_other_asymmetric_pair(self):
        r = cp_violation_condition(3, 7)
        assert r["cp_violated"] is True


# ---------------------------------------------------------------------------
# jarlskog_geometric
# ---------------------------------------------------------------------------

class TestJarlskogGeometric:
    @pytest.fixture(scope="class")
    def j_result(self):
        return jarlskog_geometric()

    def test_j_geo_positive(self, j_result):
        assert j_result["j_geo"] > 0

    def test_j_geo_not_zero(self, j_result):
        assert j_result["j_geo"] > 1e-6

    def test_cp_violated(self, j_result):
        assert j_result["cp_violated_geometric"] is True

    def test_sin_2theta_exact(self, j_result):
        # sin(2θ_braid) = 2×5×7/(5²+7²) = 70/74 = 35/37
        expected = 70.0 / 74.0
        assert abs(j_result["sin_2theta"] - expected) < 1e-12

    def test_j_geo_matches_module_constant(self, j_result):
        assert abs(j_result["j_geo"] - J_GEO_CANONICAL) < 1e-14

    def test_j_geo_less_than_one(self, j_result):
        assert j_result["j_geo"] < 1.0

    def test_honest_caveat_present(self, j_result):
        assert "mass hierarchy" in j_result["honest_caveat"].lower() or \
               "quark" in j_result["honest_caveat"].lower()

    def test_symmetric_braid_j_zero(self):
        j = jarlskog_geometric(5, 5)
        assert abs(j["j_geo"]) < 1e-14

    def test_theorem_mentions_n1_neq_n2(self, j_result):
        assert "≠" in j_result["theorem"] or "neq" in j_result["theorem"].lower() or \
               "n1" in j_result["theorem"].lower()

    def test_ratio_geo_pdg_large(self, j_result):
        # J_geo >> J_PDG (because mass hierarchy factor not included)
        assert j_result["ratio_geo_over_pdg"] > 100


# ---------------------------------------------------------------------------
# jarlskog_nw_survey
# ---------------------------------------------------------------------------

class TestJarlskogNwSurvey:
    @pytest.fixture(scope="class")
    def survey(self):
        return jarlskog_nw_survey()

    def test_returns_list(self, survey):
        assert isinstance(survey, list)

    def test_default_length(self, survey):
        assert len(survey) == 5

    def test_canonical_entry(self, survey):
        canonical = next(e for e in survey if e["n_w"] == 5)
        assert abs(canonical["j_geo"] - J_GEO_CANONICAL) < 1e-14

    def test_all_asymmetric_cp_violated(self, survey):
        for entry in survey:
            # All canonical pairs are (n_w, n_w+2) → n1 ≠ n2 → cp_violated = True
            assert entry["cp_violated"] is True


# ---------------------------------------------------------------------------
# pillar145_summary
# ---------------------------------------------------------------------------

class TestPillar145Summary:
    @pytest.fixture(scope="class")
    def summary(self):
        return pillar145_summary()

    def test_pillar_number(self, summary):
        assert summary["pillar"] == 145

    def test_title_present(self, summary):
        assert "jarlskog" in summary["title"].lower() or "braid" in summary["title"].lower()

    def test_cp_proved(self, summary):
        assert summary["cp_violated_proved"] is True

    def test_j_geo_positive(self, summary):
        assert summary["j_geo"] > 0

    def test_toe_status_present(self, summary):
        assert len(summary["toe_status"]) > 10

    def test_previous_gap_mentioned(self, summary):
        assert "gap" in summary["previous_gap"].lower() or \
               "known" in summary["previous_gap"].lower()

    def test_resolution_mentions_asymmetry(self, summary):
        assert "asymm" in summary["resolution"].lower() or \
               "n₁ ≠ n₂" in summary["resolution"] or \
               "n1" in summary["resolution"].lower()

    def test_improvement_mentions_proven(self, summary):
        assert "proven" in summary["improvement"].lower() or \
               "proved" in summary["improvement"].lower() or \
               "PROVED" in summary["improvement"]
