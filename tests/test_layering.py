# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_layering.py
=======================
Tests for src/multiverse/layering.py.

Physical claims under test
---------------------------
1. big_bang_braiding_event(5,7): energy partition is exact (E_pre = E_adiab + E_iso).
2. Adiabatic fraction = c_s = 12/37; iso fraction = 25/37.
3. k_cs = 74 at the SOS resonance for (5, 7).
4. Before-state: k_cs=0, is_braided=False, c_s=0, rho=0.
5. After-state:  k_cs=74, is_braided=True, c_s=12/37, rho=35/37.
6. branch_lossiness(canonical_branch) = 0 exactly.
7. branch_lossiness(non-canonical branch) > 0.
8. branch_lossiness raises ValueError for phi_star ≤ 0.
9. layer_pair_resonance_check passes all 5 structural checks for (5,7).
10. Energy conservation holds for arbitrary (n₁, n₂) pairs.

Test classes
-------------
TestBraidingEventCanonical
    Detailed checks for the (5,7) Big Bang braiding event.

TestBraidingEventOtherPairs
    Energy conservation and structural properties for other pairs.

TestWalkingLayerState
    Before/after state fields for the canonical event.

TestBranchLossiness
    Lossiness is 0 for canonical branch; > 0 for others; raises on bad phi_star.

TestLayerPairResonanceCheck
    All structural checks for the resonance identity.

Theory and scientific direction: ThomasCory Walker-Pearson.
Code and tests: GitHub Copilot (AI).
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import numpy as np

from src.multiverse.layering import (
    BraidingEventResult,
    WalkingLayerState,
    big_bang_braiding_event,
    branch_lossiness,
    layer_pair_resonance_check,
    _PHI_STAR_CANONICAL,
    PHI0_BARE_DEFAULT,
)
from src.multiverse.branch_catalog import classify_branch
from src.core.inflation import effective_phi0_kk


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------

N1 = 5
N2 = 7
K_CS = 74
C_S_CANONICAL = 12.0 / 37.0
RHO_CANONICAL  = 35.0 / 37.0


# ===========================================================================
# 1. TestBraidingEventCanonical
# ===========================================================================

class TestBraidingEventCanonical:
    """Big Bang braiding event for the canonical (5, 7) pair."""

    @pytest.fixture(scope="class")
    def evt(self) -> BraidingEventResult:
        return big_bang_braiding_event(N1, N2)

    def test_returns_braiding_event_result(self, evt):
        assert isinstance(evt, BraidingEventResult)

    def test_n1_n2(self, evt):
        assert evt.n1 == N1
        assert evt.n2 == N2

    def test_k_cs_is_74(self, evt):
        assert evt.k_cs == K_CS

    def test_is_sos_resonance(self, evt):
        assert evt.is_sos_resonance is True

    def test_rho_is_35_over_37(self, evt):
        assert evt.rho == pytest.approx(RHO_CANONICAL, rel=1e-10)

    def test_c_s_is_12_over_37(self, evt):
        assert evt.c_s == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_energy_pre_is_74(self, evt):
        """E_pre = k_cs = 74 (in units 1/R² with R=1)."""
        assert evt.energy_pre == pytest.approx(74.0, rel=1e-12)

    def test_energy_adiabatic_is_24(self, evt):
        """E_adiabatic = 74 × 12/37 = 24."""
        assert evt.energy_adiabatic == pytest.approx(24.0, rel=1e-10)

    def test_energy_isocurvature_is_50(self, evt):
        """E_iso = 74 × 25/37 = 50."""
        assert evt.energy_isocurvature == pytest.approx(50.0, rel=1e-10)

    def test_energy_conservation(self, evt):
        """E_adiabatic + E_iso must equal E_pre exactly."""
        total = evt.energy_adiabatic + evt.energy_isocurvature
        assert total == pytest.approx(evt.energy_pre, rel=1e-12)

    def test_adiabatic_fraction_equals_cs(self, evt):
        assert evt.adiabatic_fraction == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_iso_fraction_equals_1_minus_cs(self, evt):
        assert evt.iso_fraction == pytest.approx(1.0 - C_S_CANONICAL, rel=1e-10)

    def test_adiabatic_plus_iso_fractions_is_1(self, evt):
        assert evt.adiabatic_fraction + evt.iso_fraction == pytest.approx(1.0, rel=1e-12)

    def test_ns_prediction_within_planck(self, evt):
        """Adiabatic mode ns should be inside Planck 1σ window."""
        from src.core.inflation import PLANCK_NS_CENTRAL, PLANCK_NS_SIGMA
        assert abs(evt.ns_prediction - PLANCK_NS_CENTRAL) < PLANCK_NS_SIGMA

    def test_r_prediction_below_bicep(self, evt):
        from src.core.braided_winding import R_BICEP_KECK_95
        assert evt.r_prediction < R_BICEP_KECK_95

    def test_adiabatic_fraction_is_less_than_half(self, evt):
        """For (5,7): only 32.4% of energy drives inflation; 67.6% thermalised."""
        assert evt.adiabatic_fraction < 0.5

    def test_iso_fraction_is_dominant(self, evt):
        assert evt.iso_fraction > evt.adiabatic_fraction


# ===========================================================================
# 2. TestBraidingEventOtherPairs
# ===========================================================================

class TestBraidingEventOtherPairs:
    """Energy conservation and structure for arbitrary (n₁, n₂) pairs."""

    _EXAMPLE_WINDING_PAIRS = [(1, 2), (2, 3), (3, 5), (4, 7), (6, 8), (1, 10)]

    @pytest.mark.parametrize("n1,n2", _EXAMPLE_WINDING_PAIRS)
    def test_energy_conservation(self, n1, n2):
        evt = big_bang_braiding_event(n1, n2)
        total = evt.energy_adiabatic + evt.energy_isocurvature
        assert total == pytest.approx(evt.energy_pre, rel=1e-12)

    @pytest.mark.parametrize("n1,n2", _EXAMPLE_WINDING_PAIRS)
    def test_k_cs_is_sum_of_squares(self, n1, n2):
        evt = big_bang_braiding_event(n1, n2)
        assert evt.k_cs == n1**2 + n2**2

    @pytest.mark.parametrize("n1,n2", _EXAMPLE_WINDING_PAIRS)
    def test_fractions_sum_to_one(self, n1, n2):
        evt = big_bang_braiding_event(n1, n2)
        assert evt.adiabatic_fraction + evt.iso_fraction == pytest.approx(1.0)

    @pytest.mark.parametrize("n1,n2", _EXAMPLE_WINDING_PAIRS)
    def test_c_s_positive_and_sub_unity(self, n1, n2):
        evt = big_bang_braiding_event(n1, n2)
        assert 0.0 < evt.c_s < 1.0

    @pytest.mark.parametrize("n1,n2", _EXAMPLE_WINDING_PAIRS)
    def test_is_sos_resonance_always_true(self, n1, n2):
        evt = big_bang_braiding_event(n1, n2)
        assert evt.is_sos_resonance is True

    def test_raises_on_n1_zero(self):
        with pytest.raises(ValueError):
            big_bang_braiding_event(0, 5)

    def test_raises_on_n2_equal_n1(self):
        with pytest.raises(ValueError):
            big_bang_braiding_event(4, 4)

    def test_raises_on_n2_less_than_n1(self):
        with pytest.raises(ValueError):
            big_bang_braiding_event(7, 2)

    def test_energy_pre_equals_k_cs(self):
        for n1, n2 in [(2, 5), (3, 4), (1, 7)]:
            evt = big_bang_braiding_event(n1, n2)
            assert evt.energy_pre == pytest.approx(n1**2 + n2**2, rel=1e-12)


# ===========================================================================
# 3. TestWalkingLayerState
# ===========================================================================

class TestWalkingLayerState:
    """Pre- and post-braiding state snapshots for the canonical event."""

    @pytest.fixture(scope="class")
    def evt(self) -> BraidingEventResult:
        return big_bang_braiding_event(N1, N2)

    # --- before_state ---

    def test_before_is_walking_layer_state(self, evt):
        assert isinstance(evt.before_state, WalkingLayerState)

    def test_before_k_cs_is_zero(self, evt):
        """Before CS coupling: k_cs = 0 (no braid yet)."""
        assert evt.before_state.k_cs == 0

    def test_before_is_braided_false(self, evt):
        assert evt.before_state.is_braided is False

    def test_before_c_s_is_zero(self, evt):
        assert evt.before_state.c_s == pytest.approx(0.0, abs=1e-15)

    def test_before_rho_is_zero(self, evt):
        assert evt.before_state.rho == pytest.approx(0.0, abs=1e-15)

    def test_before_n1_n2(self, evt):
        assert evt.before_state.n1 == N1
        assert evt.before_state.n2 == N2

    def test_before_phi_n1_positive(self, evt):
        assert evt.before_state.phi_n1 > 0.0

    def test_before_phi_n2_positive(self, evt):
        assert evt.before_state.phi_n2 > 0.0

    def test_before_phi_n2_greater_than_phi_n1(self, evt):
        """φ(n₂=7) > φ(n₁=5) since KK Jacobian scales with n_w."""
        assert evt.before_state.phi_n2 > evt.before_state.phi_n1

    # --- after_state ---

    def test_after_is_walking_layer_state(self, evt):
        assert isinstance(evt.after_state, WalkingLayerState)

    def test_after_k_cs_is_74(self, evt):
        assert evt.after_state.k_cs == K_CS

    def test_after_is_braided_true(self, evt):
        assert evt.after_state.is_braided is True

    def test_after_c_s_is_12_over_37(self, evt):
        assert evt.after_state.c_s == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_after_rho_is_35_over_37(self, evt):
        assert evt.after_state.rho == pytest.approx(RHO_CANONICAL, rel=1e-10)

    def test_after_phi_n1_same_as_before(self, evt):
        """φ_branch values are set by winding number, unchanged by braiding."""
        assert evt.after_state.phi_n1 == pytest.approx(evt.before_state.phi_n1)

    def test_after_phi_n2_same_as_before(self, evt):
        assert evt.after_state.phi_n2 == pytest.approx(evt.before_state.phi_n2)


# ===========================================================================
# 4. TestBranchLossiness
# ===========================================================================

class TestBranchLossiness:
    """Lossiness function: 0 for canonical, > 0 for others."""

    def test_canonical_branch_lossiness_is_zero(self):
        br = classify_branch(N1, N2)
        L = branch_lossiness(br)
        assert L == pytest.approx(0.0, abs=1e-12)

    def test_canonical_lossiness_with_explicit_phi_star(self):
        br = classify_branch(N1, N2)
        phi_star = float(effective_phi0_kk(PHI0_BARE_DEFAULT, N1))
        L = branch_lossiness(br, phi_star=phi_star)
        assert L == pytest.approx(0.0, abs=1e-12)

    def test_secondary_lossless_branch_56_lossiness(self):
        """(5,6) has n1=5, so φ_branch = φ_star → L = 0."""
        br = classify_branch(5, 6)
        L = branch_lossiness(br)
        assert L == pytest.approx(0.0, abs=1e-12)

    def test_branch_35_lossiness_positive(self):
        br = classify_branch(3, 5)
        L = branch_lossiness(br)
        assert L > 0.0

    def test_branch_37_lossiness_positive(self):
        br = classify_branch(3, 7)
        L = branch_lossiness(br)
        assert L > 0.0

    def test_branch_12_lossiness_positive(self):
        br = classify_branch(1, 2)
        L = branch_lossiness(br)
        assert L > 0.0

    def test_branch_79_lossiness_positive(self):
        """n1=7 > 5 so φ_branch ≠ φ_star → L > 0."""
        br = classify_branch(7, 9)
        L = branch_lossiness(br)
        assert L > 0.0

    @pytest.mark.parametrize("n1,n2", [(1,3),(2,4),(4,6),(6,8),(8,10)])
    def test_non_canonical_branches_all_lossy(self, n1, n2):
        br = classify_branch(n1, n2)
        L = branch_lossiness(br)
        assert L > 0.0

    def test_raises_on_phi_star_zero(self):
        br = classify_branch(N1, N2)
        with pytest.raises(ValueError):
            branch_lossiness(br, phi_star=0.0)

    def test_raises_on_phi_star_negative(self):
        br = classify_branch(N1, N2)
        with pytest.raises(ValueError):
            branch_lossiness(br, phi_star=-1.0)

    def test_lossiness_scales_with_winding_deviation(self):
        """L should be larger for n1 further from 5."""
        br3 = classify_branch(3, 4)   # n1=3: farther from 5
        br4 = classify_branch(4, 6)   # n1=4: closer to 5
        L3 = branch_lossiness(br3)
        L4 = branch_lossiness(br4)
        assert L3 > L4, f"Expected L(n1=3)={L3} > L(n1=4)={L4}"

    def test_phi_star_canonical_constant(self):
        """_PHI_STAR_CANONICAL matches effective_phi0_kk(1.0, 5)."""
        expected = float(effective_phi0_kk(PHI0_BARE_DEFAULT, 5))
        assert _PHI_STAR_CANONICAL == pytest.approx(expected, rel=1e-10)


# ===========================================================================
# 5. TestLayerPairResonanceCheck
# ===========================================================================

class TestLayerPairResonanceCheck:
    """layer_pair_resonance_check passes all structural assertions."""

    @pytest.fixture(scope="class")
    def check57(self) -> dict:
        return layer_pair_resonance_check(N1, N2)

    def test_returns_dict(self, check57):
        assert isinstance(check57, dict)

    def test_n1_n2_in_result(self, check57):
        assert check57["n1"] == N1
        assert check57["n2"] == N2

    def test_k_cs_is_74(self, check57):
        assert check57["k_cs"] == K_CS

    def test_beat_is_2(self, check57):
        assert check57["beat"] == 2

    def test_jacobi_sum_is_12(self, check57):
        assert check57["jacobi_sum"] == 12

    def test_c_s_formula_matches_computed(self, check57):
        assert check57["c_s_match"] is True

    def test_c_s_formula_value(self, check57):
        assert check57["c_s_formula"] == pytest.approx(C_S_CANONICAL, rel=1e-10)

    def test_energy_conserved(self, check57):
        assert check57["energy_conserved"] is True

    def test_sos_identity_holds(self, check57):
        assert check57["sos_identity_holds"] is True

    def test_raises_on_n1_zero(self):
        with pytest.raises(ValueError):
            layer_pair_resonance_check(0, 5)

    def test_raises_on_n2_equal_n1(self):
        with pytest.raises(ValueError):
            layer_pair_resonance_check(3, 3)

    @pytest.mark.parametrize("n1,n2", [(1,2),(2,5),(3,7),(4,9),(6,11)])
    def test_all_checks_pass_for_various_pairs(self, n1, n2):
        result = layer_pair_resonance_check(n1, n2)
        assert result["sos_identity_holds"] is True
        assert result["c_s_match"] is True
        assert result["energy_conserved"] is True
        assert result["k_cs"] == n1**2 + n2**2
        assert result["beat"] == n2 - n1
        assert result["jacobi_sum"] == n1 + n2
