# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_geometric_chirality_uniqueness.py
=============================================
Tests for Pillar 70-C — Geometric Chirality Uniqueness Theorem.
(src/core/geometric_chirality_uniqueness.py)

Tests: GitHub Copilot (AI).
"""
from __future__ import annotations
import math
import pytest

from src.core.geometric_chirality_uniqueness import (
    # Constants
    N_W_CANDIDATES,
    TWO_SPIN_STRUCTURES,
    ZERO_MODE_CHIRALITY,
    APS_AHAT_FLAT,
    ETA_BAR,
    # Functions
    spin_structure_zero_mode_chirality,
    index_dirac_orbifold,
    is_chiral_spectrum,
    gw_requires_chiral_spectrum,
    ewsb_selects_left_handed,
    geometric_chirality_uniqueness,
    nw_geometric_selection_audit,
    pillar70c_summary,
)


# ===========================================================================
# Module constants
# ===========================================================================

class TestConstants:
    def test_candidates(self):
        assert set(N_W_CANDIDATES) == {5, 7}

    def test_two_spin_structures(self):
        assert len(TWO_SPIN_STRUCTURES) == 2
        assert "Omega_plus" in TWO_SPIN_STRUCTURES
        assert "Omega_minus" in TWO_SPIN_STRUCTURES

    def test_zero_mode_chirality_keys(self):
        assert set(ZERO_MODE_CHIRALITY.keys()) == {"Omega_plus", "Omega_minus"}

    def test_zero_mode_chirality_plus_right(self):
        assert ZERO_MODE_CHIRALITY["Omega_plus"] == "right-handed"

    def test_zero_mode_chirality_minus_left(self):
        assert ZERO_MODE_CHIRALITY["Omega_minus"] == "left-handed"

    def test_ahat_flat_zero(self):
        assert APS_AHAT_FLAT == 0.0

    def test_eta_bar_5(self):
        assert ETA_BAR[5] == 0.5

    def test_eta_bar_7(self):
        assert ETA_BAR[7] == 0.0

    def test_eta_bar_only_two_candidates(self):
        assert set(ETA_BAR.keys()) == {5, 7}


# ===========================================================================
# Step A: spin structure and zero-mode chirality
# ===========================================================================

class TestSpinStructureZeroModeChirality:
    def test_plus_one_is_right_handed(self):
        assert spin_structure_zero_mode_chirality(+1) == "right-handed"

    def test_minus_one_is_left_handed(self):
        assert spin_structure_zero_mode_chirality(-1) == "left-handed"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            spin_structure_zero_mode_chirality(0)

    def test_invalid_large_raises(self):
        with pytest.raises(ValueError):
            spin_structure_zero_mode_chirality(2)


# ===========================================================================
# Step B: APS index theorem
# ===========================================================================

class TestIndexDiracOrbifold:
    def test_n5_index_quarter(self):
        idx = index_dirac_orbifold(5)
        assert abs(idx - 0.25) < 1e-10

    def test_n7_index_zero(self):
        idx = index_dirac_orbifold(7)
        assert abs(idx) < 1e-10

    def test_explicit_eta_bar(self):
        idx = index_dirac_orbifold(5, eta_bar=0.5)
        assert abs(idx - 0.25) < 1e-10

    def test_explicit_eta_bar_zero(self):
        idx = index_dirac_orbifold(7, eta_bar=0.0)
        assert abs(idx) < 1e-10

    def test_unknown_nw_raises(self):
        with pytest.raises(ValueError):
            index_dirac_orbifold(3)

    def test_index_proportional_to_eta(self):
        for eta in [0.0, 0.25, 0.5, 1.0]:
            idx = index_dirac_orbifold(5, eta_bar=eta)
            assert abs(idx - 0.5 * eta) < 1e-10

    def test_flat_background_ahat_zero(self):
        # A-hat contribution is exactly 0 for flat background
        idx = index_dirac_orbifold(5, eta_bar=0.0)
        assert idx == 0.0


class TestIsChiralSpectrum:
    def test_nonzero_index_is_chiral(self):
        assert is_chiral_spectrum(0.25) is True

    def test_zero_index_is_not_chiral(self):
        assert is_chiral_spectrum(0.0) is False

    def test_small_nonzero_is_chiral(self):
        assert is_chiral_spectrum(1e-8) is True

    def test_exact_zero_is_not_chiral(self):
        assert is_chiral_spectrum(0.0, tol=1e-10) is False

    def test_n5_chiral(self):
        idx = index_dirac_orbifold(5)
        assert is_chiral_spectrum(idx) is True

    def test_n7_vector_like(self):
        idx = index_dirac_orbifold(7)
        assert is_chiral_spectrum(idx) is False


# ===========================================================================
# Step C: GW potential requires chiral spectrum
# ===========================================================================

class TestGwRequiresChiralSpectrum:
    def test_returns_dict(self):
        result = gw_requires_chiral_spectrum()
        assert isinstance(result, dict)

    def test_required_is_true(self):
        result = gw_requires_chiral_spectrum()
        assert result["required"] is True

    def test_has_reason(self):
        result = gw_requires_chiral_spectrum()
        assert "reason" in result
        assert len(result["reason"]) > 20

    def test_has_reference(self):
        result = gw_requires_chiral_spectrum()
        assert "reference" in result
        assert "Goldberger" in result["reference"]

    def test_status_says_derived(self):
        result = gw_requires_chiral_spectrum()
        assert "DERIVED" in result["status"]

    def test_no_sm_input_in_status(self):
        result = gw_requires_chiral_spectrum()
        assert "no SM" in result["status"]

    def test_gw_potential_form(self):
        result = gw_requires_chiral_spectrum()
        assert "phi0" in result["gw_potential"]
        assert "lambda_GW" in result["gw_potential"]


# ===========================================================================
# Step D: EWSB selects left-handed spin structure
# ===========================================================================

class TestEwsbSelectsLeftHanded:
    def test_minus_one_compatible(self):
        assert ewsb_selects_left_handed(-1) is True

    def test_plus_one_incompatible(self):
        assert ewsb_selects_left_handed(+1) is False

    def test_right_handed_is_su2_singlet(self):
        # The motivation: only left-handed is EWSB-compatible
        assert not ewsb_selects_left_handed(+1)

    def test_left_handed_is_su2_doublet(self):
        assert ewsb_selects_left_handed(-1)


# ===========================================================================
# Master theorem: geometric_chirality_uniqueness
# ===========================================================================

class TestGeometricChiralityUniqueness:
    """Test the master four-step function for n_w = 5 and n_w = 7."""

    # --- n_w = 5 ---

    def test_n5_eta_bar(self):
        r = geometric_chirality_uniqueness(5)
        assert abs(r["eta_bar"] - 0.5) < 1e-10

    def test_n5_index(self):
        r = geometric_chirality_uniqueness(5)
        assert abs(r["index"] - 0.25) < 1e-10

    def test_n5_is_chiral(self):
        r = geometric_chirality_uniqueness(5)
        assert r["is_chiral"] is True

    def test_n5_gw_requires_chiral(self):
        r = geometric_chirality_uniqueness(5)
        assert r["gw_requires_chiral"] is True

    def test_n5_index_consistent(self):
        r = geometric_chirality_uniqueness(5)
        assert r["index_consistent"] is True

    def test_n5_spin_structure_omega_minus(self):
        r = geometric_chirality_uniqueness(5)
        assert r["spin_structure"] == "Omega_minus"

    def test_n5_zero_mode_chirality_left(self):
        r = geometric_chirality_uniqueness(5)
        assert r["zero_mode_chirality"] == "left-handed"

    def test_n5_ewsb_compatible(self):
        r = geometric_chirality_uniqueness(5)
        assert r["ewsb_compatible"] is True

    def test_n5_selected(self):
        r = geometric_chirality_uniqueness(5)
        assert r["n_w_selected"] is True

    def test_n5_status_derived(self):
        r = geometric_chirality_uniqueness(5)
        assert r["overall_status"] == "DERIVED"

    def test_n5_all_steps_passed(self):
        r = geometric_chirality_uniqueness(5)
        for step, status in r["step_status"].items():
            assert status == "PASSED", f"{step} expected PASSED, got {status}"

    # --- n_w = 7 ---

    def test_n7_eta_bar(self):
        r = geometric_chirality_uniqueness(7)
        assert abs(r["eta_bar"]) < 1e-10

    def test_n7_index_zero(self):
        r = geometric_chirality_uniqueness(7)
        assert abs(r["index"]) < 1e-10

    def test_n7_not_chiral(self):
        r = geometric_chirality_uniqueness(7)
        assert r["is_chiral"] is False

    def test_n7_index_inconsistent_with_gw(self):
        r = geometric_chirality_uniqueness(7)
        # GW always requires chiral; n_w=7 gives vector-like: inconsistent
        assert r["index_consistent"] is False

    def test_n7_spin_structure_na(self):
        r = geometric_chirality_uniqueness(7)
        assert "vector-like" in r["spin_structure"]

    def test_n7_not_selected(self):
        r = geometric_chirality_uniqueness(7)
        assert r["n_w_selected"] is False

    def test_n7_status_not_selected(self):
        r = geometric_chirality_uniqueness(7)
        assert r["overall_status"] == "NOT-SELECTED"

    def test_n7_ewsb_not_compatible(self):
        r = geometric_chirality_uniqueness(7)
        assert r["ewsb_compatible"] is False

    def test_n7_step_b_failed(self):
        r = geometric_chirality_uniqueness(7)
        assert r["step_status"]["Step_B_index_nonzero"] == "FAILED"

    # --- Custom eta_bar_fn ---

    def test_custom_eta_bar_fn(self):
        r = geometric_chirality_uniqueness(5, eta_bar_fn=lambda n: 0.5)
        assert r["n_w_selected"] is True

    def test_custom_eta_bar_fn_zero(self):
        # Force eta_bar = 0 even for n_w=5 → vector-like → not selected
        r = geometric_chirality_uniqueness(5, eta_bar_fn=lambda n: 0.0)
        assert r["n_w_selected"] is False

    def test_unknown_n_w_raises(self):
        with pytest.raises(ValueError):
            geometric_chirality_uniqueness(3)


# ===========================================================================
# Audit: nw_geometric_selection_audit
# ===========================================================================

class TestNwGeometricSelectionAudit:
    def _audit(self):
        return nw_geometric_selection_audit()

    def test_returns_dict(self):
        assert isinstance(self._audit(), dict)

    def test_has_n5_result(self):
        audit = self._audit()
        assert "n_w_5" in audit

    def test_has_n7_result(self):
        audit = self._audit()
        assert "n_w_7" in audit

    def test_unique_selection_true(self):
        audit = self._audit()
        assert audit["unique_selection"] is True

    def test_selected_n_w_is_five(self):
        audit = self._audit()
        assert audit["selected_n_w"] == 5

    def test_audit_passed(self):
        audit = self._audit()
        assert audit["audit_passed"] is True

    def test_summary_contains_n5_derived(self):
        audit = self._audit()
        assert "n_w = 5" in audit["summary"]
        assert "DERIVED" in audit["summary"]

    def test_summary_contains_n7_not_selected(self):
        audit = self._audit()
        assert "n_w = 7" in audit["summary"]
        assert "NOT-SELECTED" in audit["summary"]

    def test_n5_subresult_selected(self):
        audit = self._audit()
        assert audit["n_w_5"]["n_w_selected"] is True

    def test_n7_subresult_not_selected(self):
        audit = self._audit()
        assert audit["n_w_7"]["n_w_selected"] is False


# ===========================================================================
# Summary: pillar70c_summary
# ===========================================================================

class TestPillar70cSummary:
    def _summary(self):
        return pillar70c_summary()

    def test_returns_dict(self):
        assert isinstance(self._summary(), dict)

    def test_pillar_label(self):
        s = self._summary()
        assert s["pillar"] == "70-C"

    def test_has_four_steps(self):
        s = self._summary()
        assert len(s["steps"]) == 4

    def test_step_a_proved(self):
        s = self._summary()
        assert "PROVED" in s["steps"][0]["status"]

    def test_step_b_proved(self):
        s = self._summary()
        assert "PROVED" in s["steps"][1]["status"]

    def test_step_c_derived(self):
        s = self._summary()
        assert "DERIVED" in s["steps"][2]["status"]

    def test_step_d_derived(self):
        s = self._summary()
        assert "DERIVED" in s["steps"][3]["status"]

    def test_overall_status_derived(self):
        s = self._summary()
        assert s["overall_status"] == "DERIVED"

    def test_residual_gap_mentions_lambda(self):
        s = self._summary()
        assert "lambda_GW" in s["residual_gap"] or "λ_GW" in s["residual_gap"]

    def test_planck_role_mentions_confirmation(self):
        s = self._summary()
        assert "confirmation" in s["planck_role"]

    def test_planck_role_no_longer_primary(self):
        s = self._summary()
        assert "no longer" in s["planck_role"]

    def test_audit_present(self):
        s = self._summary()
        assert "audit" in s
        assert s["audit"]["audit_passed"] is True

    def test_title_contains_chirality(self):
        s = self._summary()
        assert "Chirality" in s["title"]


# ===========================================================================
# Cross-consistency: Pillar 70-B values are honoured
# ===========================================================================

class TestPillar70BCrossConsistency:
    """Verify that Pillar 70-C respects Pillar 70-B derived η̄ values."""

    def test_eta_bar_5_matches_70b(self):
        # Pillar 70-B DERIVED: η̄(5) = ½
        r = geometric_chirality_uniqueness(5)
        assert abs(r["eta_bar"] - 0.5) < 1e-10

    def test_eta_bar_7_matches_70b(self):
        # Pillar 70-B DERIVED: η̄(7) = 0
        r = geometric_chirality_uniqueness(7)
        assert abs(r["eta_bar"] - 0.0) < 1e-10

    def test_index_follows_from_eta(self):
        for n_w, expected_eta in [(5, 0.5), (7, 0.0)]:
            r = geometric_chirality_uniqueness(n_w)
            assert abs(r["index"] - 0.5 * r["eta_bar"]) < 1e-10

    def test_n5_chirality_follows_from_eta_nonzero(self):
        r5 = geometric_chirality_uniqueness(5)
        r7 = geometric_chirality_uniqueness(7)
        assert r5["is_chiral"] and not r7["is_chiral"]

    def test_only_n5_satisfies_all_four_steps(self):
        selected = [n for n in [5, 7]
                    if geometric_chirality_uniqueness(n)["n_w_selected"]]
        assert selected == [5]


# ===========================================================================
# Pillar 70-C-bis: Z₂-parity of G_{μ5} forces chirality from metric geometry
# ===========================================================================

from src.core.geometric_chirality_uniqueness import (
    bmu_z2_parity_forces_chirality,
    metric_parity_chirality_audit,
)


class TestBmuZ2ParityChirality:
    """Tests for bmu_z2_parity_forces_chirality and metric_parity_chirality_audit."""

    # --- G_{μ5} Z₂-odd ---
    def test_g_mu5_z2_parity_is_odd(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert r["G_mu5_z2_parity"] == "odd"

    def test_g_mu5_z2_parity_is_odd_nw7(self):
        r = bmu_z2_parity_forces_chirality(7)
        assert r["G_mu5_z2_parity"] == "odd"

    # --- A_5^eff Z₂-odd ---
    def test_a5_eff_z2_parity_is_odd(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert r["A5_eff_z2_parity"] == "odd"

    # --- T(n_w) values ---
    def test_T5_equals_15(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert r["T_nw"] == 15

    def test_T7_equals_28(self):
        r = bmu_z2_parity_forces_chirality(7)
        assert r["T_nw"] == 28

    # --- T parity ---
    def test_T5_parity_odd(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert r["T_nw_parity"] == "odd"

    def test_T7_parity_even(self):
        r = bmu_z2_parity_forces_chirality(7)
        assert r["T_nw_parity"] == "even"

    # --- Holonomy ---
    def test_holonomy_nontrivial_for_nw5(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert r["holonomy_trivial"] is False

    def test_holonomy_trivial_for_nw7(self):
        r = bmu_z2_parity_forces_chirality(7)
        assert r["holonomy_trivial"] is True

    # --- η̄ forced ---
    def test_eta_bar_forced_half_for_nw5(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert abs(r["eta_bar_forced"] - 0.5) < 1e-12

    def test_eta_bar_forced_zero_for_nw7(self):
        r = bmu_z2_parity_forces_chirality(7)
        assert abs(r["eta_bar_forced"] - 0.0) < 1e-12

    # --- Spin structure ---
    def test_spin_structure_omega_minus_for_nw5(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert "Omega_minus" in r["spin_structure_from_metric"]

    def test_spin_structure_not_omega_minus_for_nw7(self):
        r = bmu_z2_parity_forces_chirality(7)
        assert "Omega_minus" not in r["spin_structure_from_metric"]

    # --- derivation_status ---
    def test_derivation_status_contains_DERIVED(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert "DERIVED" in r["derivation_status"]

    def test_derivation_status_no_SM_input(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert "no SM input" in r["derivation_status"]

    # --- argument string ---
    def test_argument_mentions_z2_or_parity(self):
        r = bmu_z2_parity_forces_chirality(5)
        assert "Z₂" in r["argument"] or "parity" in r["argument"]

    # --- Uniqueness: n_w=5 is the only one forced left-handed ---
    def test_nw5_unique_left_handed_in_candidates(self):
        left_handed = [
            nw for nw in [5, 7]
            if "Omega_minus" in bmu_z2_parity_forces_chirality(nw)["spin_structure_from_metric"]
        ]
        assert left_handed == [5]

    # --- metric_parity_chirality_audit ---
    def test_audit_unique_left_handed(self):
        audit = metric_parity_chirality_audit()
        assert audit["unique_left_handed"] is True

    def test_audit_selected_nw_is_5(self):
        audit = metric_parity_chirality_audit()
        assert audit["selected_n_w"] == 5

    def test_audit_candidates_are_5_and_7(self):
        audit = metric_parity_chirality_audit()
        assert set(audit["candidates"]) == {5, 7}

    def test_audit_compares_exactly_2_candidates(self):
        audit = metric_parity_chirality_audit()
        assert len(audit["candidates"]) == 2

    def test_audit_nw5_eta_bar_half(self):
        audit = metric_parity_chirality_audit()
        assert abs(audit["n_w_5"]["eta_bar_forced"] - 0.5) < 1e-12

    def test_audit_nw7_eta_bar_zero(self):
        audit = metric_parity_chirality_audit()
        assert abs(audit["n_w_7"]["eta_bar_forced"] - 0.0) < 1e-12

    # --- pillar70c_summary contains step_d_metric_derivation ---
    def test_pillar70c_summary_has_step_d_metric_derivation(self):
        from src.core.geometric_chirality_uniqueness import pillar70c_summary
        s = pillar70c_summary()
        assert "step_d_metric_derivation" in s

    def test_pillar70c_summary_step_d_status_mentions_metric(self):
        from src.core.geometric_chirality_uniqueness import pillar70c_summary
        s = pillar70c_summary()
        assert "metric" in s["step_d_status"].lower() or "Z₂" in s["step_d_status"]
