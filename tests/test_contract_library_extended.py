# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for src/core/contract_library_extended.py — ~80 pytest tests."""

from __future__ import annotations

import sympy as sp
import pytest

from src.core.contract_library_extended import (
    ASSUMPTION_LEDGER,
    TheoremArtifact,
    extended_theorem_set,
    verify_extended_theorem_set,
    extended_contract_library_artifact,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def theorems():
    return extended_theorem_set()


@pytest.fixture(scope="module")
def theorem_map(theorems):
    return {t.theorem_id: t for t in theorems}


@pytest.fixture(scope="module")
def results():
    return verify_extended_theorem_set()


@pytest.fixture(scope="module")
def artifact():
    return extended_contract_library_artifact()


# ---------------------------------------------------------------------------
# ASSUMPTION_LEDGER tests
# ---------------------------------------------------------------------------

class TestAssumptionLedger:
    def test_ledger_is_list(self):
        assert isinstance(ASSUMPTION_LEDGER, list)

    def test_ledger_length(self):
        assert len(ASSUMPTION_LEDGER) == 9

    def test_ledger_ids(self):
        ids = [a["id"] for a in ASSUMPTION_LEDGER]
        assert ids == ["A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9"]

    def test_a4_content(self):
        a4 = next(a for a in ASSUMPTION_LEDGER if a["id"] == "A4")
        assert "74" in a4["assumption"]
        assert "K_CS" in a4["assumption"]

    def test_a5_content(self):
        a5 = next(a for a in ASSUMPTION_LEDGER if a["id"] == "A5")
        assert "N_C" in a5["assumption"]
        assert "3" in a5["assumption"]

    def test_a6_content(self):
        a6 = next(a for a in ASSUMPTION_LEDGER if a["id"] == "A6")
        assert "alpha_GUT" in a6["assumption"]

    def test_a7_content(self):
        a7 = next(a for a in ASSUMPTION_LEDGER if a["id"] == "A7")
        assert "M_KK" in a7["assumption"]

    def test_a8_content(self):
        a8 = next(a for a in ASSUMPTION_LEDGER if a["id"] == "A8")
        assert "246" in a8["assumption"]

    def test_a9_content(self):
        a9 = next(a for a in ASSUMPTION_LEDGER if a["id"] == "A9")
        assert "b_3" in a9["assumption"] or "beta" in a9["assumption"] or "-7" in a9["assumption"]

    def test_each_entry_has_required_keys(self):
        for entry in ASSUMPTION_LEDGER:
            assert "id" in entry
            assert "assumption" in entry
            assert "scope" in entry


# ---------------------------------------------------------------------------
# extended_theorem_set structure
# ---------------------------------------------------------------------------

class TestTheoremSetStructure:
    EXPECTED_IDS = [
        "T2-ALPHA-GUT",
        "T3-SIN2W-GUT",
        "T4-N_E-FORMULA",
        "T5-SLOW-ROLL-EPSILON",
        "T6-SLOW-ROLL-ETA",
        "T7-R-FROM-EPSILON",
        "T8-NS-FROM-EPSILON-ETA",
        "T9-KK-MASS-ZERO-MODE",
        "T10-KK-MASS-N-TH-MODE",
        "T11-GUT-COUPLING-BOUND",
        "T12-SEESAW-FORMULA",
        "T13-ALPHA-S-AT-MZ",
        "T14-BRAID-SUM-OF-SQUARES",
        "T15-SOUND-SPEED-FORMULA",
        "T16-INFLATION-OBSERVABLE-CHAIN",
        "T17-ALPHA-GUT-CASIMIR",
        "T18-N_C-FROM-WINDING",
        "T19-K_CS-UNIQUENESS",
        "T20-PHI0-SELF-CONSISTENCY",
    ]

    def test_theorem_set_returns_list(self, theorems):
        assert isinstance(theorems, list)

    def test_theorem_count(self, theorems):
        assert len(theorems) == 19

    def test_all_expected_ids_present(self, theorem_map):
        for tid in self.EXPECTED_IDS:
            assert tid in theorem_map, f"Missing theorem: {tid}"

    def test_no_duplicate_ids(self, theorems):
        ids = [t.theorem_id for t in theorems]
        assert len(ids) == len(set(ids))

    def test_all_are_theorem_artifacts(self, theorems):
        for t in theorems:
            assert isinstance(t, TheoremArtifact)

    def test_each_theorem_has_statement(self, theorems):
        for t in theorems:
            assert isinstance(t.statement, str)
            assert len(t.statement) > 0

    def test_each_theorem_has_assumptions_list(self, theorems):
        for t in theorems:
            assert isinstance(t.assumptions, list)
            assert len(t.assumptions) >= 1

    def test_each_theorem_has_sympy_lhs(self, theorems):
        for t in theorems:
            assert isinstance(t.lhs, sp.Basic)

    def test_each_theorem_has_sympy_rhs(self, theorems):
        for t in theorems:
            assert isinstance(t.rhs, sp.Basic)


# ---------------------------------------------------------------------------
# Individual theorem verification
# ---------------------------------------------------------------------------

class TestTheoremVerification:
    def test_t2_alpha_gut_verifies(self, theorem_map):
        t = theorem_map["T2-ALPHA-GUT"]
        assert t.theorem_id == "T2-ALPHA-GUT"
        assert "alpha_GUT" in t.statement or "N_C" in t.statement
        assert t.verify() is True

    def test_t3_sin2w_verifies(self, theorem_map):
        assert theorem_map["T3-SIN2W-GUT"].verify() is True

    def test_t4_ne_formula_verifies(self, theorem_map):
        assert theorem_map["T4-N_E-FORMULA"].verify() is True

    def test_t5_slow_roll_epsilon_verifies(self, theorem_map):
        assert theorem_map["T5-SLOW-ROLL-EPSILON"].verify() is True

    def test_t6_slow_roll_eta_verifies(self, theorem_map):
        assert theorem_map["T6-SLOW-ROLL-ETA"].verify() is True

    def test_t7_r_from_epsilon_verifies(self, theorem_map):
        assert theorem_map["T7-R-FROM-EPSILON"].verify() is True

    def test_t8_ns_from_epsilon_eta_verifies(self, theorem_map):
        assert theorem_map["T8-NS-FROM-EPSILON-ETA"].verify() is True

    def test_t9_kk_zero_mode_verifies(self, theorem_map):
        assert theorem_map["T9-KK-MASS-ZERO-MODE"].verify() is True

    def test_t10_kk_nth_mode_verifies(self, theorem_map):
        assert theorem_map["T10-KK-MASS-N-TH-MODE"].verify() is True

    def test_t11_gut_bound_verifies(self, theorem_map):
        assert theorem_map["T11-GUT-COUPLING-BOUND"].verify() is True

    def test_t12_seesaw_verifies(self, theorem_map):
        assert theorem_map["T12-SEESAW-FORMULA"].verify() is True

    def test_t13_alpha_s_verifies(self, theorem_map):
        assert theorem_map["T13-ALPHA-S-AT-MZ"].verify() is True

    def test_t14_braid_sum_of_squares_verifies(self, theorem_map):
        assert theorem_map["T14-BRAID-SUM-OF-SQUARES"].verify() is True

    def test_t15_sound_speed_verifies(self, theorem_map):
        assert theorem_map["T15-SOUND-SPEED-FORMULA"].verify() is True

    def test_t16_inflation_chain_verifies(self, theorem_map):
        assert theorem_map["T16-INFLATION-OBSERVABLE-CHAIN"].verify() is True

    def test_t17_alpha_gut_casimir_verifies(self, theorem_map):
        assert theorem_map["T17-ALPHA-GUT-CASIMIR"].verify() is True

    def test_t18_nc_from_winding_verifies(self, theorem_map):
        assert theorem_map["T18-N_C-FROM-WINDING"].verify() is True

    def test_t19_k_cs_uniqueness_verifies(self, theorem_map):
        assert theorem_map["T19-K_CS-UNIQUENESS"].verify() is True

    def test_t20_phi0_self_consistency_verifies(self, theorem_map):
        assert theorem_map["T20-PHI0-SELF-CONSISTENCY"].verify() is True


# ---------------------------------------------------------------------------
# Specific numerical / algebraic spot-checks
# ---------------------------------------------------------------------------

class TestNumericalSpotChecks:
    def test_t14_lhs_equals_74(self, theorem_map):
        t = theorem_map["T14-BRAID-SUM-OF-SQUARES"]
        assert int(t.lhs) == 74

    def test_t14_rhs_equals_74(self, theorem_map):
        t = theorem_map["T14-BRAID-SUM-OF-SQUARES"]
        assert int(t.rhs) == 74

    def test_t14_five_squared_plus_seven_squared(self):
        assert 5**2 + 7**2 == 74

    def test_t15_sound_speed_lhs_numerical(self, theorem_map):
        t = theorem_map["T15-SOUND-SPEED-FORMULA"]
        val = float(t.lhs)
        assert abs(val - (12 / 37)**2) < 1e-12

    def test_t15_sound_speed_rhs_numerical(self, theorem_map):
        t = theorem_map["T15-SOUND-SPEED-FORMULA"]
        val = float(t.rhs)
        assert abs(val - 144 / 1369) < 1e-12

    def test_t11_alpha_gut_positive(self):
        alpha = sp.Rational(3, 74)
        assert alpha > 0

    def test_t11_alpha_gut_below_quarter(self):
        alpha = sp.Rational(3, 74)
        assert alpha < sp.Rational(1, 4)

    def test_t18_nc_equals_three(self, theorem_map):
        t = theorem_map["T18-N_C-FROM-WINDING"]
        assert int(t.rhs) == 3

    def test_t18_lhs_five_minus_two(self, theorem_map):
        t = theorem_map["T18-N_C-FROM-WINDING"]
        assert int(t.lhs) == 3

    def test_t20_phi0_self_consistency_symbolic(self):
        n_w = sp.Symbol("N_w", positive=True, integer=True)
        n_s = sp.Symbol("n_s", real=True)
        phi0_sq = 8 * n_w / (1 - n_s)
        n_s_back = 1 - 8 * n_w / phi0_sq
        diff = sp.simplify(n_s_back - n_s)
        assert diff == 0

    def test_t5_epsilon_equals_half_ne_inverse(self):
        phi0 = sp.Symbol("phi0", positive=True)
        n_w = sp.Symbol("N_w", positive=True, integer=True)
        n_e = phi0**2 / (4 * n_w)
        epsilon = 2 * n_w / phi0**2  # epsilon = 1/(2*N_e)
        assert sp.simplify(epsilon - 1 / (2 * n_e)) == 0

    def test_t3_sin2w_value(self, theorem_map):
        t = theorem_map["T3-SIN2W-GUT"]
        assert t.lhs == sp.Rational(3, 8)
        assert t.rhs == sp.Rational(3, 8)

    def test_t9_zero_mode_is_integer_zero(self, theorem_map):
        t = theorem_map["T9-KK-MASS-ZERO-MODE"]
        assert t.lhs == sp.Integer(0)
        assert t.rhs == sp.Integer(0)

    def test_t17_lhs_rhs_equal_numerically(self, theorem_map):
        t = theorem_map["T17-ALPHA-GUT-CASIMIR"]
        assert abs(float(t.lhs) - float(t.rhs)) < 1e-12

    def test_t19_lhs_plus_49_eq_74(self, theorem_map):
        t = theorem_map["T19-K_CS-UNIQUENESS"]
        assert int(t.lhs) == 74

    def test_t7_commutativity(self, theorem_map):
        t = theorem_map["T7-R-FROM-EPSILON"]
        assert sp.simplify(t.lhs - t.rhs) == 0


# ---------------------------------------------------------------------------
# verify_extended_theorem_set
# ---------------------------------------------------------------------------

class TestVerifyExtendedTheoremSet:
    def test_returns_list(self, results):
        assert isinstance(results, list)

    def test_length_matches_theorem_count(self, results):
        assert len(results) == 19

    def test_each_result_has_theorem_id(self, results):
        for r in results:
            assert "theorem_id" in r

    def test_each_result_has_statement(self, results):
        for r in results:
            assert "statement" in r

    def test_each_result_has_verified_key(self, results):
        for r in results:
            assert "verified" in r

    def test_each_result_has_assumptions(self, results):
        for r in results:
            assert "assumptions" in r

    def test_theorems_that_must_pass(self, results):
        must_pass = {
            "T3-SIN2W-GUT", "T4-N_E-FORMULA", "T5-SLOW-ROLL-EPSILON",
            "T6-SLOW-ROLL-ETA", "T7-R-FROM-EPSILON", "T8-NS-FROM-EPSILON-ETA",
            "T9-KK-MASS-ZERO-MODE", "T10-KK-MASS-N-TH-MODE",
            "T11-GUT-COUPLING-BOUND", "T12-SEESAW-FORMULA",
            "T13-ALPHA-S-AT-MZ", "T14-BRAID-SUM-OF-SQUARES",
            "T15-SOUND-SPEED-FORMULA", "T16-INFLATION-OBSERVABLE-CHAIN",
            "T17-ALPHA-GUT-CASIMIR", "T18-N_C-FROM-WINDING",
            "T19-K_CS-UNIQUENESS", "T20-PHI0-SELF-CONSISTENCY",
        }
        result_map = {r["theorem_id"]: r for r in results}
        for tid in must_pass:
            assert result_map[tid]["verified"] is True, f"{tid} failed to verify"


# ---------------------------------------------------------------------------
# extended_contract_library_artifact
# ---------------------------------------------------------------------------

class TestArtifact:
    def test_artifact_is_dict(self, artifact):
        assert isinstance(artifact, dict)

    def test_artifact_status_pass(self, artifact):
        assert artifact["status"] == "PASS"

    def test_artifact_all_verified_true(self, artifact):
        assert artifact["all_verified"] is True

    def test_artifact_has_track(self, artifact):
        assert "track" in artifact

    def test_artifact_has_title(self, artifact):
        assert "title" in artifact

    def test_artifact_has_workflow(self, artifact):
        assert "workflow" in artifact

    def test_artifact_theorems_key(self, artifact):
        assert "theorems" in artifact
        assert isinstance(artifact["theorems"], list)

    def test_artifact_assumption_ledger(self, artifact):
        assert "assumption_ledger" in artifact
        assert len(artifact["assumption_ledger"]) == 9

    def test_artifact_theorem_count(self, artifact):
        assert len(artifact["theorems"]) == 19

    def test_artifact_all_theorems_verified_in_dict(self, artifact):
        for t in artifact["theorems"]:
            assert t["verified"] is True, f"Artifact says {t['theorem_id']} failed"
