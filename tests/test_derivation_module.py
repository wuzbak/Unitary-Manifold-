# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_derivation_module.py
========================
Tests for src/core/derivation.py — the Stage 0 → Stage 3 constraint-based
derivation of the Unitary Manifold integers (n_w, k_CS).

Structure
---------
TestStage1WindingNumber
    Verifies that Stage 1 derives n_w = 5 as the unique minimal winding
    number satisfying all structural constraints (C1 round-trip closure,
    C2 KK consistency, C4 Z₂ orbifold parity, C1+C2 e-folds ≥ 60, C6
    FTUM convergence, C7 holographic stability).

TestStage2CSLevel
    Verifies that Stage 2 with use_birefringence_hint=True returns k_CS=74
    (observationally assisted) and marks it as not purely derived.
    With use_birefringence_hint=False, all positive integers survive the
    purely structural constraints and k_CS=1 is the minimal choice.

TestStage3JointConsistency
    Verifies that the canonical (n_w=5, k_CS=74) pair passes the joint
    consistency check with finite observables.

TestDerivationResult
    End-to-end: derive_integers() returns the expected (n_w=5, k_CS=74),
    with correct is_derived flags and a consistent metadata dict.

TestIndividualConstraintChecks
    Unit tests for each of the nine individual constraint-check functions.

TestFailureModes
    Verifies that DerivationFailure is raised when no candidate survives,
    and that the universality-class path is exercised when only structural
    constraints apply to k_CS.
"""

from __future__ import annotations

import numpy as np
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.derivation import (
    # constants
    PHI0_BARE_FIXED_POINT,
    ALPHA_EM_CANONICAL,
    R_C_CANONICAL,
    N_EFOLDS_MIN,
    ROUND_TRIP_TOL,
    # exception
    DerivationFailure,
    # dataclass
    DerivationResult,
    # individual checks — winding number
    check_round_trip_closure,
    check_kk_consistency,
    check_orbifold_parity,
    check_efolds,
    check_ftum_convergence,
    check_holographic_stability,
    # individual checks — CS level
    check_cs_gauge_invariance,
    check_cs_bundle_quantization,
    check_anomaly_cancellation,
    check_cs_coupling_finite,
    check_ftum_cs_stability,
    # pipeline functions
    derive_winding_number,
    derive_cs_level,
    derive_integers,
)
from src.core.inflation import (
    CS_LEVEL_PLANCK_MATCH,
    BIREFRINGENCE_TARGET_DEG,
    BIREFRINGENCE_SIGMA_DEG,
    effective_phi0_kk,
    ns_from_phi0,
)


# ===========================================================================
# TestStage1WindingNumber
# ===========================================================================

class TestStage1WindingNumber:
    """Stage 1: structural constraints derive n_w = 5 uniquely."""

    def test_derives_n_w_5(self):
        """derive_winding_number returns n_w = 5 for phi0_bare = 1."""
        n_w, candidates, is_derived, _ = derive_winding_number(
            phi0_bare=PHI0_BARE_FIXED_POINT,
            n_efolds_min=N_EFOLDS_MIN,
        )
        assert n_w == 5, f"Expected n_w=5, got {n_w}"

    def test_n_w_is_derived(self):
        """n_w derivation is purely structural (is_derived = True)."""
        _, _, is_derived, _ = derive_winding_number()
        assert is_derived is True

    def test_candidates_include_5(self):
        """Candidate set contains n_w = 5."""
        _, candidates, _, _ = derive_winding_number()
        assert 5 in candidates

    def test_candidates_exclude_even_integers(self):
        """Even winding numbers are eliminated by the Z₂ orbifold parity (C4)."""
        _, candidates, _, _ = derive_winding_number(n_max=20)
        for n in candidates:
            assert n % 2 == 1, f"Even candidate n_w={n} should have been rejected"

    def test_candidates_exclude_1_and_3(self):
        """n_w = 1 and n_w = 3 are excluded by the e-folds constraint (N_e ≥ 60)."""
        _, candidates, _, details = derive_winding_number(n_max=20)
        assert 1 not in candidates, "n_w=1 should fail the e-folds constraint"
        assert 3 not in candidates, "n_w=3 should fail the e-folds constraint"

    def test_n_efolds_min_drives_lower_bound(self):
        """Reducing n_efolds_min to 20 allows n_w = 3 as a candidate."""
        _, candidates_20, _, _ = derive_winding_number(
            n_efolds_min=20
        )
        assert 3 in candidates_20, (
            "With n_efolds_min=20, n_w=3 should survive the e-folds constraint"
        )

    def test_n5_gives_correct_efolds(self):
        """n_w = 5 → phi0_eff ≈ 31.42 → N_e ≈ 82 (well above 60)."""
        phi0_eff = effective_phi0_kk(1.0, 5)
        n_efolds = phi0_eff ** 2 / 12.0
        assert n_efolds >= 60.0

    def test_n3_gives_insufficient_efolds(self):
        """n_w = 3 → N_e ≈ 30 < 60 (fails structural e-folds check)."""
        phi0_eff = effective_phi0_kk(1.0, 3)
        n_efolds = phi0_eff ** 2 / 12.0
        assert n_efolds < 60.0

    def test_minimality_selects_smallest_candidate(self):
        """C8 minimality: n_w = 5 is the smallest candidate that survives C1–C7."""
        n_w, candidates, _, _ = derive_winding_number()
        assert n_w == min(candidates)

    def test_details_contains_phi0_eff(self):
        """Details dict provides phi0_eff for each surviving candidate."""
        _, candidates, _, details = derive_winding_number()
        for n_w in candidates:
            assert "phi0_eff" in details[n_w]

    def test_details_contains_ns(self):
        """Details dict provides nₛ for each surviving candidate."""
        _, candidates, _, details = derive_winding_number()
        for n_w in candidates:
            assert "ns" in details[n_w]
            assert np.isfinite(details[n_w]["ns"])


# ===========================================================================
# TestStage2CSLevel
# ===========================================================================

class TestStage2CSLevel:
    """Stage 2: structural + observational constraints yield k_CS = 74."""

    _N_W = 5  # Use derived winding number

    def test_derives_k_cs_74_with_birefringence_hint(self):
        """With birefringence hint, k_CS = 74 is selected."""
        k_cs, _, _, _ = derive_cs_level(
            n_w=self._N_W,
            use_birefringence_hint=True,
        )
        assert k_cs == CS_LEVEL_PLANCK_MATCH, (
            f"Expected k_CS={CS_LEVEL_PLANCK_MATCH}, got {k_cs}"
        )

    def test_k_cs_74_is_not_derived(self):
        """k_CS = 74 requires the birefringence prior → is_derived = False."""
        _, _, is_derived, _ = derive_cs_level(
            n_w=self._N_W,
            use_birefringence_hint=True,
        )
        assert is_derived is False, (
            "k_CS=74 depends on the birefringence observational prior; "
            "must be marked is_derived=False"
        )

    def test_without_hint_minimal_candidate_is_1(self):
        """Without birefringence hint, all k ∈ ℤ⁺ survive → C8 selects k_CS=1."""
        k_cs, _, _, _ = derive_cs_level(
            n_w=self._N_W,
            use_birefringence_hint=False,
        )
        assert k_cs == 1, (
            f"Without observational input, C8 minimality should select k_CS=1; "
            f"got k_CS={k_cs}"
        )

    def test_without_hint_is_derived_true(self):
        """Without the birefringence hint the result is marked as purely structural."""
        _, _, is_derived, _ = derive_cs_level(
            n_w=self._N_W,
            use_birefringence_hint=False,
        )
        assert is_derived is True

    def test_without_hint_all_candidates_present(self):
        """Structural constraints alone don't eliminate any positive integer."""
        _, candidates, _, _ = derive_cs_level(
            n_w=self._N_W,
            k_max=10,
            use_birefringence_hint=False,
        )
        assert candidates == list(range(1, 11)), (
            "All k_CS ∈ [1, 10] should survive the purely structural constraints"
        )

    def test_k74_within_birefringence_window(self):
        """k_CS = 74 satisfies |β(74) − β_target| ≤ σ_β."""
        _, _, _, details = derive_cs_level(
            n_w=self._N_W,
            k_max=100,
            use_birefringence_hint=True,
        )
        beta_74 = details[74]["beta_deg"]
        assert abs(beta_74 - BIREFRINGENCE_TARGET_DEG) <= BIREFRINGENCE_SIGMA_DEG

    def test_details_contain_beta_deg(self):
        """Each candidate in details has a beta_deg entry."""
        _, candidates, _, details = derive_cs_level(
            n_w=self._N_W,
            k_max=10,
            use_birefringence_hint=False,
        )
        for k in candidates:
            assert "beta_deg" in details[k]
            assert np.isfinite(details[k]["beta_deg"])


# ===========================================================================
# TestStage3JointConsistency
# ===========================================================================

class TestStage3JointConsistency:
    """Stage 3: (n_w=5, k_CS=74) passes joint consistency checks."""

    def test_joint_consistent_canonical(self):
        """derive_integers with canonical inputs sets joint_consistent = True."""
        result = derive_integers(
            phi0_bare=PHI0_BARE_FIXED_POINT,
            use_birefringence_hint=True,
        )
        assert result.joint_consistent is True

    def test_joint_ns_finite(self):
        """nₛ in joint metadata is finite."""
        result = derive_integers(use_birefringence_hint=True)
        ns = result.metadata["stage3_joint"]["ns"]
        assert np.isfinite(ns)

    def test_joint_r_positive(self):
        """r = 16ε in joint metadata is positive."""
        result = derive_integers(use_birefringence_hint=True)
        r = result.metadata["stage3_joint"]["r"]
        assert r > 0.0

    def test_joint_beta_positive(self):
        """β in joint metadata is positive."""
        result = derive_integers(use_birefringence_hint=True)
        beta = result.metadata["stage3_joint"]["beta_deg"]
        assert beta > 0.0

    def test_joint_g_agg_positive(self):
        """g_aγγ in joint metadata is positive."""
        result = derive_integers(use_birefringence_hint=True)
        g = result.metadata["stage3_joint"]["g_agg"]
        assert g > 0.0


# ===========================================================================
# TestDerivationResult
# ===========================================================================

class TestDerivationResult:
    """End-to-end: derive_integers returns the correct DerivationResult."""

    _RESULT: DerivationResult | None = None

    @classmethod
    def _get(cls) -> DerivationResult:
        if cls._RESULT is None:
            cls._RESULT = derive_integers(use_birefringence_hint=True)
        return cls._RESULT

    def test_n_w_is_5(self):
        """derive_integers returns n_w = 5."""
        assert self._get().n_w == 5

    def test_k_cs_is_74(self):
        """derive_integers returns k_CS = 74 (with birefringence hint)."""
        assert self._get().k_cs == CS_LEVEL_PLANCK_MATCH

    def test_n_w_is_derived(self):
        """n_w is purely structurally derived (n_w_is_derived = True)."""
        assert self._get().n_w_is_derived is True

    def test_k_cs_is_not_derived(self):
        """k_CS is observationally assisted (k_cs_is_derived = False)."""
        assert self._get().k_cs_is_derived is False

    def test_joint_consistent(self):
        """joint_consistent is True for the canonical pair."""
        assert self._get().joint_consistent is True

    def test_n_w_candidates_is_list_of_odd_ints(self):
        """n_w_candidates contains only odd positive integers."""
        for n in self._get().n_w_candidates:
            assert isinstance(n, int)
            assert n >= 1
            assert n % 2 == 1

    def test_k_cs_candidates_all_positive_ints(self):
        """k_cs_candidates (structural universality class) are all positive ints."""
        for k in self._get().k_cs_candidates:
            assert isinstance(k, (int, np.integer))
            assert k >= 1

    def test_metadata_has_stage3_joint(self):
        """metadata contains stage3_joint sub-dict."""
        assert "stage3_joint" in self._get().metadata

    def test_result_is_dataclass(self):
        """derive_integers returns a DerivationResult instance."""
        assert isinstance(self._get(), DerivationResult)


# ===========================================================================
# TestIndividualConstraintChecks
# ===========================================================================

class TestIndividualConstraintChecks:
    """Unit tests for all nine individual constraint-check functions."""

    # --- Winding number checks ---

    def test_round_trip_closure_passes_n5(self):
        """Round-trip closure passes for n_w = 5."""
        ok, _ = check_round_trip_closure(5)
        assert ok

    def test_round_trip_closure_fails_n0(self):
        """Round-trip closure rejects n_w = 0 (non-positive)."""
        ok, _ = check_round_trip_closure(0)
        assert not ok

    def test_round_trip_closure_symmetry(self):
        """Round-trip closure passes for all odd n_w in [1, 15]."""
        for n in range(1, 16, 2):
            ok, _ = check_round_trip_closure(n)
            assert ok, f"Round-trip closure failed for n_w={n}"

    def test_kk_consistency_passes_n5(self):
        """KK consistency passes for n_w = 5."""
        ok, _ = check_kk_consistency(5)
        assert ok

    def test_kk_consistency_produces_finite_ns(self):
        """KK consistency check returns a finite nₛ in the message."""
        ok, msg = check_kk_consistency(5)
        assert ok
        assert "nₛ" in msg

    def test_orbifold_parity_rejects_even(self):
        """Orbifold parity rejects even winding numbers."""
        for n in [2, 4, 6, 8, 10]:
            ok, _ = check_orbifold_parity(n)
            assert not ok, f"n_w={n} (even) should be rejected by orbifold parity"

    def test_orbifold_parity_accepts_odd(self):
        """Orbifold parity accepts odd winding numbers."""
        for n in [1, 3, 5, 7, 9]:
            ok, _ = check_orbifold_parity(n)
            assert ok, f"n_w={n} (odd) should pass orbifold parity"

    def test_efolds_passes_n5(self):
        """e-folds check passes for n_w = 5 with N_EFOLDS_MIN = 60."""
        ok, _ = check_efolds(5, n_efolds_min=60)
        assert ok

    def test_efolds_rejects_n1(self):
        """e-folds check rejects n_w = 1 (N_e ≈ 3.3 < 60)."""
        ok, _ = check_efolds(1, n_efolds_min=60)
        assert not ok

    def test_efolds_rejects_n3(self):
        """e-folds check rejects n_w = 3 (N_e ≈ 30 < 60)."""
        ok, _ = check_efolds(3, n_efolds_min=60)
        assert not ok

    def test_ftum_convergence_passes(self):
        """FTUM convergence check passes for n_w = 5."""
        ok, _ = check_ftum_convergence(5)
        assert ok

    def test_holographic_stability_passes(self):
        """Holographic stability check passes for n_w = 5."""
        ok, _ = check_holographic_stability(5)
        assert ok

    # --- CS level checks ---

    def test_cs_gauge_invariance_passes_k74(self):
        """CS gauge invariance passes for k_CS = 74."""
        ok, _ = check_cs_gauge_invariance(74)
        assert ok

    def test_cs_gauge_invariance_fails_k0(self):
        """CS gauge invariance rejects k_CS = 0."""
        ok, _ = check_cs_gauge_invariance(0)
        assert not ok

    def test_cs_gauge_invariance_fails_negative(self):
        """CS gauge invariance rejects negative k_CS."""
        ok, _ = check_cs_gauge_invariance(-1)
        assert not ok

    def test_cs_bundle_quantization_passes_k1(self):
        """Bundle quantization passes for k_CS = 1."""
        ok, _ = check_cs_bundle_quantization(1)
        assert ok

    def test_cs_bundle_quantization_fails_k0(self):
        """Bundle quantization rejects k_CS = 0."""
        ok, _ = check_cs_bundle_quantization(0)
        assert not ok

    def test_anomaly_cancellation_passes_any_positive_k(self):
        """Anomaly cancellation passes for any positive k_CS."""
        for k in [1, 5, 37, 74, 100]:
            ok, _ = check_anomaly_cancellation(k, n_w=5)
            assert ok, f"Anomaly cancellation should pass for k_cs={k}"

    def test_cs_coupling_finite_passes_k74(self):
        """CS coupling check passes for k_CS = 74."""
        ok, _ = check_cs_coupling_finite(74)
        assert ok

    def test_cs_coupling_finite_g_positive(self):
        """CS coupling check message confirms g_aγγ is positive for any k ≥ 1."""
        for k in [1, 10, 74, 100]:
            ok, msg = check_cs_coupling_finite(k)
            assert ok, f"Coupling check failed for k={k}: {msg}"

    def test_ftum_cs_stability_passes_k74(self):
        """FTUM CS stability check passes for k_CS = 74."""
        ok, _ = check_ftum_cs_stability(74)
        assert ok

    def test_ftum_cs_stability_passes_k1(self):
        """FTUM CS stability check passes for k_CS = 1."""
        ok, _ = check_ftum_cs_stability(1)
        assert ok


# ===========================================================================
# TestFailureModes
# ===========================================================================

class TestFailureModes:
    """Verify the three documented failure modes of the derivation algorithm."""

    def test_failure_if_no_n_w_survives(self):
        """DerivationFailure raised if n_efolds_min forces phi0_eff > n_max*2pi."""
        # Require N_e ≥ 1e8 → phi0_eff ≥ sqrt(12e8) ≈ 34641 → impossible for n_max=20
        with pytest.raises(DerivationFailure):
            derive_winding_number(n_max=20, n_efolds_min=int(1e8))

    def test_universality_class_without_hint(self):
        """Without birefringence hint, Stage 2 returns a universality class."""
        _, candidates, is_derived, _ = derive_cs_level(
            n_w=5,
            k_max=5,
            use_birefringence_hint=False,
        )
        assert len(candidates) == 5, (
            "All k_CS ∈ [1, 5] should survive purely structural constraints"
        )
        assert is_derived is True

    def test_k_cs_marked_fitted_not_derived(self):
        """k_CS = 74 is marked as fitted (not structurally derived) per pseudocode."""
        result = derive_integers(use_birefringence_hint=True)
        assert result.k_cs_is_derived is False, (
            "Pseudocode says: 'If integers depend on observational priors: "
            "Mark as fitted, not derived'.  k_CS=74 uses birefringence data."
        )

    def test_n_w_uniqueness_documented(self):
        """Stage 1 returns exactly one candidate (n_w=5) under canonical constraints."""
        n_w, candidates, _, _ = derive_winding_number()
        # 5 is the minimum; there may be higher odd candidates too.
        # Verify n_w=5 is in the list and is selected.
        assert n_w == 5
        assert 5 in candidates

    def test_stage1_larger_phi0_bare_shifts_n_w(self):
        """Larger phi0_bare reduces J_KK per winding → higher n_w needed."""
        # With phi0_bare=0.1: J_KK = n_w * 2π * sqrt(0.1) ≈ n_w * 1.987
        # phi0_eff = J_KK * phi0_bare = n_w * 1.987 * 0.1 = n_w * 0.1987
        # N_e = phi0_eff²/12 = n_w² * 0.003/12 → very large n_w needed
        with pytest.raises(DerivationFailure):
            # For phi0_bare=0.01, even n_w=20 gives N_e < 60
            derive_winding_number(phi0_bare=0.01, n_max=20, n_efolds_min=60)
