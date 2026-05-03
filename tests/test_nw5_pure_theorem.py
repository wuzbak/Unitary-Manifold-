# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_nw5_pure_theorem.py
================================
Tests for Pillar 70-D — The Pure n_w = 5 Uniqueness Theorem.
(src/core/nw5_pure_theorem.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import cmath
import math
import pytest

from src.core.nw5_pure_theorem import (
    # Constants
    CANDIDATES,
    N_W_CANONICAL,
    BRAID_STEP,
    Z2_ODD_PHASE,
    # Arithmetic helpers
    triangular_number,
    aps_eta_bar,
    kcs_minimum_step_braid,
    z2_odd_consistency_product,
    is_z2_odd_consistent,
    # Main theorem
    z2_odd_phase_constraint,
    nw5_pure_theorem,
    # SU(5) derivation
    su5_from_kk_species,
    sm_gauge_group_from_5d,
    full_nw5_proof_summary,
    # §XIV.2 honest-gap function
    su3_emergence_status,
)


# ===========================================================================
# Constants
# ===========================================================================

class TestConstants:
    def test_candidates(self):
        assert set(CANDIDATES) == {5, 7}

    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_braid_step(self):
        assert BRAID_STEP == 2

    def test_z2_odd_phase(self):
        assert abs(Z2_ODD_PHASE.real + 1.0) < 1e-12
        assert abs(Z2_ODD_PHASE.imag) < 1e-12


# ===========================================================================
# Arithmetic helpers
# ===========================================================================

class TestTriangularNumber:
    def test_t1(self):
        assert triangular_number(1) == 1

    def test_t2(self):
        assert triangular_number(2) == 3

    def test_t3(self):
        assert triangular_number(3) == 6

    def test_t4(self):
        assert triangular_number(4) == 10

    def test_t5(self):
        assert triangular_number(5) == 15

    def test_t6(self):
        assert triangular_number(6) == 21

    def test_t7(self):
        assert triangular_number(7) == 28

    def test_t10(self):
        assert triangular_number(10) == 55

    def test_formula(self):
        for n in range(1, 20):
            assert triangular_number(n) == n * (n + 1) // 2

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            triangular_number(0)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            triangular_number(-1)


class TestApsEtaBar:
    """η̄(n_w) = T(n_w)/2 mod 1."""

    def test_eta_bar_5_is_half(self):
        """n_w=5: T=15 (odd) → η̄=½."""
        assert aps_eta_bar(5) == pytest.approx(0.5, abs=1e-12)

    def test_eta_bar_7_is_zero(self):
        """n_w=7: T=28 (even) → η̄=0."""
        assert aps_eta_bar(7) == pytest.approx(0.0, abs=1e-12)

    def test_eta_bar_1_is_half(self):
        """n_w=1: T=1 (odd) → η̄=½."""
        assert aps_eta_bar(1) == pytest.approx(0.5, abs=1e-12)

    def test_eta_bar_3_is_zero(self):
        """n_w=3: T=6 (even) → η̄=0."""
        assert aps_eta_bar(3) == pytest.approx(0.0, abs=1e-12)

    def test_eta_bar_9_is_half(self):
        """n_w=9: 9 mod 4=1 → T=45 (odd) → η̄=½."""
        assert aps_eta_bar(9) == pytest.approx(0.5, abs=1e-12)

    def test_eta_bar_11_is_zero(self):
        """n_w=11: 11 mod 4=3 → T=66 (even) → η̄=0."""
        assert aps_eta_bar(11) == pytest.approx(0.0, abs=1e-12)

    def test_eta_bar_in_range(self):
        for nw in [1, 3, 5, 7, 9, 11, 13]:
            eta = aps_eta_bar(nw)
            assert eta in (0.0, 0.5), f"η̄({nw}) = {eta} not in {{0,½}}"

    def test_eta_bar_pattern_mod4(self):
        """n_w ≡ 1 mod 4 → η̄=½; n_w ≡ 3 mod 4 → η̄=0."""
        for nw in range(1, 30, 2):  # odd numbers only
            eta = aps_eta_bar(nw)
            expected = 0.5 if (nw % 4 == 1) else 0.0
            assert eta == pytest.approx(expected, abs=1e-12), (
                f"n_w={nw}: expected {expected}, got {eta}"
            )

    def test_raises_for_even(self):
        with pytest.raises(ValueError):
            aps_eta_bar(6)

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            aps_eta_bar(0)


class TestKcsBraid:
    """k_CS(n_w) = n_w² + (n_w+2)²."""

    def test_kcs_5(self):
        """k_CS(5) = 5²+7² = 74."""
        assert kcs_minimum_step_braid(5) == 74

    def test_kcs_7(self):
        """k_CS(7) = 7²+9² = 130."""
        assert kcs_minimum_step_braid(7) == 130

    def test_kcs_1(self):
        assert kcs_minimum_step_braid(1) == 1 ** 2 + 3 ** 2  # 10

    def test_kcs_3(self):
        assert kcs_minimum_step_braid(3) == 3 ** 2 + 5 ** 2  # 34

    def test_kcs_formula(self):
        for nw in [1, 3, 5, 7, 9, 11]:
            expected = nw ** 2 + (nw + 2) ** 2
            assert kcs_minimum_step_braid(nw) == expected

    def test_kcs_strictly_increasing(self):
        vals = [kcs_minimum_step_braid(nw) for nw in [1, 3, 5, 7, 9]]
        for a, b in zip(vals, vals[1:]):
            assert b > a

    def test_kcs_raises_even(self):
        with pytest.raises(ValueError):
            kcs_minimum_step_braid(4)

    def test_kcs_raises_zero(self):
        with pytest.raises(ValueError):
            kcs_minimum_step_braid(0)


class TestZ2OddConsistencyProduct:
    """k_CS(n_w) × η̄(n_w) rounded to nearest integer."""

    def test_product_nw5(self):
        """74 × 0.5 = 37."""
        assert z2_odd_consistency_product(5) == 37

    def test_product_nw7(self):
        """130 × 0 = 0."""
        assert z2_odd_consistency_product(7) == 0

    def test_product_nw1(self):
        """10 × 0.5 = 5."""
        assert z2_odd_consistency_product(1) == 5

    def test_product_nw3(self):
        """34 × 0 = 0."""
        assert z2_odd_consistency_product(3) == 0

    def test_product_nw9(self):
        """9²+11²=202; η̄(9)=½; product=101."""
        assert z2_odd_consistency_product(9) == 101

    def test_product_nw11(self):
        """11²+13²=290; η̄(11)=0; product=0."""
        assert z2_odd_consistency_product(11) == 0


class TestIsZ2OddConsistent:
    """is_z2_odd_consistent: product must be odd."""

    def test_nw5_consistent(self):
        """n_w=5 satisfies condition (*): product=37 (odd)."""
        assert is_z2_odd_consistent(5) is True

    def test_nw7_inconsistent(self):
        """n_w=7 violates condition (*): product=0 (even)."""
        assert is_z2_odd_consistent(7) is False

    def test_nw1_consistent(self):
        """n_w=1: product=5 (odd)."""
        assert is_z2_odd_consistent(1) is True

    def test_nw3_inconsistent(self):
        """n_w=3: product=0 (even)."""
        assert is_z2_odd_consistent(3) is False

    def test_nw9_consistent(self):
        """n_w=9: product=101 (odd)."""
        assert is_z2_odd_consistent(9) is True

    def test_nw11_inconsistent(self):
        """n_w=11: product=0 (even)."""
        assert is_z2_odd_consistent(11) is False


# ===========================================================================
# Z₂-odd phase constraint
# ===========================================================================

class TestZ2OddPhaseConstraint:
    def test_nw5_structure(self):
        r = z2_odd_phase_constraint(5)
        assert r["n_w"] == 5
        assert r["k_cs"] == 74
        assert r["eta_bar"] == pytest.approx(0.5, abs=1e-12)
        assert r["kcs_times_eta"] == 37
        assert r["product_is_odd"] is True
        assert r["z2_consistent"] is True

    def test_nw7_structure(self):
        r = z2_odd_phase_constraint(7)
        assert r["n_w"] == 7
        assert r["k_cs"] == 130
        assert r["eta_bar"] == pytest.approx(0.0, abs=1e-12)
        assert r["kcs_times_eta"] == 0
        assert r["product_is_odd"] is False
        assert r["z2_consistent"] is False

    def test_nw5_boundary_phase_is_minus_one(self):
        """exp(iπ × 74 × ½) = exp(37iπ) = -1."""
        r = z2_odd_phase_constraint(5)
        assert r["boundary_phase_is_minus_one"] is True

    def test_nw7_boundary_phase_is_plus_one(self):
        """exp(iπ × 130 × 0) = exp(0) = +1 ≠ -1."""
        r = z2_odd_phase_constraint(7)
        assert r["boundary_phase_is_minus_one"] is False

    def test_nw5_braid_pair(self):
        r = z2_odd_phase_constraint(5)
        assert r["braid_pair"] == (5, 7)

    def test_nw7_braid_pair(self):
        r = z2_odd_phase_constraint(7)
        assert r["braid_pair"] == (7, 9)

    def test_nw5_verdict_contains_consistent(self):
        r = z2_odd_phase_constraint(5)
        assert "CONSISTENT" in r["verdict"]

    def test_nw7_verdict_contains_excluded(self):
        r = z2_odd_phase_constraint(7)
        assert "EXCLUDED" in r["verdict"]


# ===========================================================================
# Main theorem
# ===========================================================================

class TestNw5PureTheorem:
    def setup_method(self):
        self.result = nw5_pure_theorem()

    def test_status_is_proved(self):
        assert self.result["status"] == "PROVED"

    def test_unique_solution_is_true(self):
        assert self.result["unique_solution"] is True

    def test_n_w_proved_is_5(self):
        assert self.result["n_w_proved"] == 5

    def test_consistent_candidates(self):
        assert self.result["consistent_candidates"] == [5]

    def test_h1_status(self):
        assert self.result["hypotheses"]["H1"]["status"] == "PROVED"

    def test_h2_status(self):
        assert self.result["hypotheses"]["H2"]["status"] == "DERIVED"

    def test_h3_status(self):
        assert "DERIVED" in self.result["hypotheses"]["H3"]["status"]

    def test_h4_status(self):
        assert self.result["hypotheses"]["H4"]["status"] == "PROVED"

    def test_axiom_a_status(self):
        assert self.result["hypotheses"]["A"]["status"] == "DERIVED"

    def test_nw5_arithmetic(self):
        ka = self.result["key_arithmetic"]["n_w=5"]
        assert ka["k_cs"] == 74
        assert ka["eta_bar"] == pytest.approx(0.5, abs=1e-12)
        assert ka["product"] == 37
        assert ka["is_odd"] is True
        assert ka["verdict"] == "CONSISTENT"

    def test_nw7_arithmetic(self):
        ka = self.result["key_arithmetic"]["n_w=7"]
        assert ka["k_cs"] == 130
        assert ka["eta_bar"] == pytest.approx(0.0, abs=1e-12)
        assert ka["product"] == 0
        assert ka["is_odd"] is False
        assert ka["verdict"] == "EXCLUDED"

    def test_closure_status_mentions_proved(self):
        assert "PROVED" in self.result["closure_status"]

    def test_observational_independence(self):
        assert "No observational data used" in self.result["observational_independence"]

    def test_candidate_checks_keys(self):
        assert set(self.result["candidate_checks"].keys()) == {5, 7}

    def test_nw5_candidate_consistent(self):
        assert self.result["candidate_checks"][5]["z2_consistent"] is True

    def test_nw7_candidate_excluded(self):
        assert self.result["candidate_checks"][7]["z2_consistent"] is False

    def test_proof_narrative_not_empty(self):
        assert len(self.result["proof_narrative"]) > 100

    def test_proof_narrative_mentions_qed(self):
        assert "Q.E.D" in self.result["proof_narrative"]


# ===========================================================================
# SU(5) from KK species
# ===========================================================================

class TestSu5FromKkSpecies:
    def test_default_is_su5(self):
        r = su5_from_kk_species(5)
        assert r["gauge_group"] == "SU(5)"

    def test_kk_species_count(self):
        r = su5_from_kk_species(5)
        assert r["kk_charged_species"] == 5

    def test_kk_modes_list(self):
        r = su5_from_kk_species(5)
        assert r["kk_modes"] == [1, 2, 3, 4, 5]

    def test_rank_is_4(self):
        r = su5_from_kk_species(5)
        assert r["rank"] == 4

    def test_n_generators_su5(self):
        r = su5_from_kk_species(5)
        assert r["n_generators"] == 24  # 5²-1

    def test_dim_fundamental_equals_nw(self):
        for nw in [3, 5, 7, 10]:
            r = su5_from_kk_species(nw)
            assert r["dim_fundamental"] == nw

    def test_rank_formula_correct(self):
        r = su5_from_kk_species(5)
        assert r["rank"] + 1 == r["n_w"]

    def test_status_is_derived(self):
        r = su5_from_kk_species(5)
        assert "DERIVED" in r["status"]

    def test_contains_sm_subgroup_for_nw5(self):
        r = su5_from_kk_species(5)
        assert r["contains_sm_subgroup"] is True

    def test_kawamura_breaks_to_sm_for_nw5(self):
        r = su5_from_kk_species(5)
        assert r["kawamura_breaks_to_sm"] is True

    def test_su7_from_nw7(self):
        r = su5_from_kk_species(7)
        assert r["gauge_group"] == "SU(7)"
        assert r["rank"] == 6

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            su5_from_kk_species(0)


# ===========================================================================
# SM gauge group from 5D
# ===========================================================================

class TestSmGaugeGroupFrom5D:
    def setup_method(self):
        self.result = sm_gauge_group_from_5d()

    def test_status_is_derived(self):
        assert self.result["status"] == "DERIVED"

    def test_claim(self):
        assert "SU(3)" in self.result["claim"]
        assert "SU(2)" in self.result["claim"]

    def test_step1_status(self):
        assert self.result["derivation_chain"]["step_1"]["status"] == "PROVED"

    def test_step2_status(self):
        assert self.result["derivation_chain"]["step_2"]["status"] == "PROVED"

    def test_step3_status(self):
        assert "DERIVED" in self.result["derivation_chain"]["step_3"]["status"]

    def test_step4_kawamura_status(self):
        assert "PROVED" in self.result["derivation_chain"]["step_4"]["status"]

    def test_step4_generators(self):
        s4 = self.result["derivation_chain"]["step_4"]
        assert s4["z2_even_generators"] == 12
        assert s4["z2_odd_generators"] == 12

    def test_step5_sin2_exact(self):
        s5 = self.result["derivation_chain"]["step_5"]
        assert s5["value"] == pytest.approx(3.0 / 8.0, abs=1e-12)

    def test_step6_sin2_accuracy(self):
        s6 = self.result["derivation_chain"]["step_6"]
        assert s6["pct_err_sin2"] < 1.0  # < 1% error

    def test_step6_alpha_s_accuracy(self):
        s6 = self.result["derivation_chain"]["step_6"]
        assert s6["pct_err_alpha_s"] < 2.0  # < 2% error

    def test_final_result_no_free_parameters(self):
        assert self.result["final_result"]["no_free_parameters"] is True

    def test_final_result_no_conjectures(self):
        assert self.result["final_result"]["no_conjectures"] is True

    def test_final_result_observational_independence(self):
        val = self.result["final_result"]["observational_independence"].lower()
        assert "pdg" in val or "observ" in val

    def test_qed_string(self):
        assert "Q.E.D" in self.result["qed"]

    def test_gauge_group_in_final_result(self):
        assert "SU(3)" in self.result["final_result"]["gauge_group"]


# ===========================================================================
# Full proof summary
# ===========================================================================

class TestFullNw5ProofSummary:
    def setup_method(self):
        self.result = full_nw5_proof_summary()

    def test_status_fully_proved(self):
        assert "FULLY PROVED" in self.result["status_after_pillar_70D"]

    def test_seven_levels(self):
        assert len(self.result["levels"]) == 7

    def test_level1_proved(self):
        assert self.result["levels"][1]["status"] == "PROVED"

    def test_level2_proved(self):
        assert self.result["levels"][2]["status"] == "PROVED"

    def test_level3_derived(self):
        assert self.result["levels"][3]["status"] == "DERIVED"

    def test_level4_derived(self):
        assert self.result["levels"][4]["status"] == "DERIVED"

    def test_level5_derived(self):
        assert self.result["levels"][5]["status"] == "DERIVED"

    def test_level6_now_proved(self):
        """The previously PHYSICALLY-MOTIVATED level is now PROVED."""
        assert self.result["levels"][6]["status"] == "PROVED"

    def test_level6_was_previously_motivated(self):
        assert self.result["levels"][6]["was_previously"] == "PHYSICALLY-MOTIVATED"

    def test_level7_empirical(self):
        assert "EMPIRICAL" in self.result["levels"][7]["status"]

    def test_conclusion_no_observation_needed(self):
        assert "no observational input" in self.result["conclusion"].lower() or \
               "observation" in self.result["conclusion"].lower()

    def test_theorem_core_proved(self):
        assert self.result["theorem_core"]["status"] == "PROVED"


# ===========================================================================
# End-to-end consistency checks
# ===========================================================================

class TestEndToEndConsistency:
    """Cross-module consistency: nw5_pure_theorem ↔ aps_spin_structure."""

    def test_eta_bar_agrees_with_aps_spin_structure(self):
        """η̄(n_w) from nw5_pure_theorem must match aps_spin_structure."""
        from src.core.aps_spin_structure import eta_bar_from_cs_inflow
        for nw in [1, 3, 5, 7, 9, 11]:
            assert aps_eta_bar(nw) == pytest.approx(
                eta_bar_from_cs_inflow(nw), abs=1e-12
            ), f"Mismatch at n_w={nw}"

    def test_triangular_number_agrees(self):
        """T(n_w) from nw5_pure_theorem must match aps_spin_structure."""
        from src.core.aps_spin_structure import triangular_number as t_aps
        for n in range(1, 15):
            assert triangular_number(n) == t_aps(n)

    def test_nw5_consistent_nw7_not(self):
        """Pure theorem selects n_w=5 and excludes n_w=7."""
        assert is_z2_odd_consistent(5) is True
        assert is_z2_odd_consistent(7) is False

    def test_kcs_5_is_canonical(self):
        """k_CS(5) = 74 is the UM canonical CS level."""
        assert kcs_minimum_step_braid(5) == 74

    def test_product_37_is_odd(self):
        """37 is the crucial odd number: k_CS(5) × η̄(5) = 74×½ = 37."""
        assert z2_odd_consistency_product(5) == 37
        assert 37 % 2 == 1

    def test_product_0_is_even(self):
        """0 is even: k_CS(7) × η̄(7) = 130×0 = 0."""
        assert z2_odd_consistency_product(7) == 0
        assert 0 % 2 == 0

    def test_boundary_phase_nw5_is_minus_one(self):
        """exp(iπ × 37) = exp(iπ) = -1 (since 37 is odd)."""
        kcs = 74
        eta = 0.5
        phase = complex(math.cos(math.pi * kcs * eta), math.sin(math.pi * kcs * eta))
        assert abs(phase.real + 1.0) < 1e-9
        assert abs(phase.imag) < 1e-9

    def test_boundary_phase_nw7_is_plus_one(self):
        """exp(iπ × 0) = +1 ≠ -1."""
        kcs = 130
        eta = 0.0
        phase = complex(math.cos(math.pi * kcs * eta), math.sin(math.pi * kcs * eta))
        assert abs(phase.real - 1.0) < 1e-9
        assert abs(phase.imag) < 1e-9

    def test_su5_from_nw5_agrees_with_su5_orbifold_proof(self):
        """SU(5) rank=4 consistent with su5_orbifold_proof constants."""
        from src.core.su5_orbifold_proof import SU5_RANK
        r = su5_from_kk_species(5)
        assert r["rank"] == SU5_RANK

    def test_n_generators_su5(self):
        """SU(5) has 24 generators (5²-1)."""
        r = su5_from_kk_species(5)
        assert r["n_generators"] == 24


# ---------------------------------------------------------------------------
# §XIV.2 — SU(3) emergence status (su3_emergence_status)
# ---------------------------------------------------------------------------

class TestSU3EmergenceStatus:
    """Verify the derivation-chain classification of the SU(3) emergence chain (§XIV.2)."""

    @pytest.fixture(autouse=True)
    def result(self):
        self.result = su3_emergence_status()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_step4_is_now_derived(self):
        """Step 4 (Kawamura parity matrix) is now DERIVED_FROM_5D_GEOMETRY."""
        assert self.result["steps"]["step_4"]["classification"] == "DERIVED_FROM_5D_GEOMETRY"

    def test_step4_external_flag_false(self):
        """Step 4 external_flag must be False after closure."""
        assert self.result["steps"]["step_4"]["external_flag"] is False

    def test_step3_is_derived(self):
        """Step 3 (SU(5) from KK species) must be DERIVED_FROM_5D_GEOMETRY."""
        assert self.result["steps"]["step_3"]["classification"] == "DERIVED_FROM_5D_GEOMETRY"

    def test_external_steps_list_empty(self):
        """No external steps remain after Kawamura closure."""
        assert self.result["external_steps"] == []

    def test_n_steps_derived(self):
        assert self.result["n_steps_derived_from_5d"] == 6

    def test_n_steps_external(self):
        assert self.result["n_steps_external"] == 0

    def test_kawamura_closure_key_present(self):
        assert "kawamura_closure" in self.result

    def test_step4_derivation_function_reference(self):
        """step_4 must point to the new derivation function."""
        src = self.result["steps"]["step_4"]["derivation_function"]
        assert "kawamura_from_winding" in src

    def test_verdict_mentions_derived(self):
        verdict = self.result["status_verdict"]
        assert "DERIVED_FROM_5D_GEOMETRY" in verdict or "derived" in verdict.lower()

    def test_step7_closure_summary(self):
        """step_7 summarizes that all steps are internal."""
        s7 = self.result["steps"]["step_7"]
        assert s7["classification"] == "DERIVED_FROM_5D_GEOMETRY"
        assert "no external imports" in s7["note"].lower() or "no external" in s7["note"]


# ===========================================================================
# kawamura_from_winding — new derivation function
# ===========================================================================

class TestKawamuraFromWinding:
    """Tests for kawamura_from_winding() in su5_orbifold_proof.py."""

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.core.su5_orbifold_proof import kawamura_from_winding
        self.fn = kawamura_from_winding
        self.r5 = kawamura_from_winding(5)
        self.r7 = kawamura_from_winding(7)

    # --- n_w = 5 basic structure ---

    def test_returns_dict_nw5(self):
        assert isinstance(self.r5, dict)

    def test_n_w_stored(self):
        assert self.r5["n_w"] == 5

    def test_n_even_nw5(self):
        """ceil(5/2) = 3."""
        assert self.r5["n_even"] == 3

    def test_n_odd_nw5(self):
        """floor(5/2) = 2."""
        assert self.r5["n_odd"] == 2

    def test_P_matrix_nw5(self):
        """P = [+1, +1, +1, -1, -1]."""
        assert self.r5["P_matrix"] == [1, 1, 1, -1, -1]

    def test_P_squared_is_I(self):
        assert self.r5["P_squared_is_I"] is True

    def test_P_squared_values(self):
        assert self.r5["P_squared"] == [1, 1, 1, 1, 1]

    def test_det_P_plus1(self):
        """det(P) = (+1)³(−1)² = +1 → P ∈ SU(5)."""
        assert self.r5["det_P"] == 1

    def test_det_P_equals_plus1_flag(self):
        assert self.r5["det_P_equals_plus1"] is True

    def test_P_in_SU_n_w(self):
        assert self.r5["P_in_SU_n_w"] is True

    def test_status_derived(self):
        assert self.r5["status"] == "DERIVED_FROM_UM_ORBIFOLD"

    def test_breaking_pattern_nw5(self):
        pattern = self.r5["breaking_pattern"]
        assert "SU(3)" in pattern and "SU(2)" in pattern and "U(1)" in pattern

    def test_derivation_text_present(self):
        assert len(self.r5["derivation"]) > 50

    def test_cross_check_n7_present(self):
        assert "cross_check_n7" in self.r5

    # --- n_w = 7 cross-check ---

    def test_n_even_nw7(self):
        """ceil(7/2) = 4."""
        assert self.r5["cross_check_n7"]["n_even"] == 4

    def test_n_odd_nw7(self):
        """floor(7/2) = 3."""
        assert self.r5["cross_check_n7"]["n_odd"] == 3

    def test_P_matrix_nw7_wrong_group(self):
        """n_w=7 gives P=[+1,+1,+1,+1,-1,-1,-1] — not the SM."""
        assert self.r5["cross_check_n7"]["P_matrix"] == [1, 1, 1, 1, -1, -1, -1]

    def test_nw7_breaking_pattern_not_SM(self):
        pattern = self.r5["cross_check_n7"]["breaking_pattern"]
        assert "NOT" in pattern or "not" in pattern.lower()

    def test_direct_nw7_call_n_even(self):
        """Direct call with n_w=7 also gives n_even=4."""
        assert self.r7["n_even"] == 4

    def test_direct_nw7_call_n_odd(self):
        assert self.r7["n_odd"] == 3

    def test_direct_nw7_P_matrix(self):
        assert self.r7["P_matrix"] == [1, 1, 1, 1, -1, -1, -1]

    def test_direct_nw7_status_still_derived(self):
        assert self.r7["status"] == "DERIVED_FROM_UM_ORBIFOLD"

    def test_replaces_external_import(self):
        assert "EXTERNAL_IMPORT" in self.r5["replaces"] or "external" in self.r5["replaces"].lower()

