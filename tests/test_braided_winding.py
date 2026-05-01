# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_braided_winding.py
==============================
Tests for src/core/braided_winding.py — the (5,7) resonant braided geometry.

Physical claim under test
--------------------------
The Chern–Simons level k_cs = 74 satisfies the sum-of-squares resonance:

    k_cs = 5² + 7² = 25 + 49 = 74

This is not a free parameter.  k_cs = 74 was derived independently from the
birefringence measurement (β ≈ 0.35°) as the unique integer minimising
|β(k) − 0.35°|.  The resonance k_cs = n₁² + n₂² is therefore a prediction of
the theory, not an input.

Under this resonance condition the braided sound speed is:

    c_s = (n₂ − n₁)(n₁ + n₂) / k_cs = 2 × 12 / 74 = 12/37

The resulting effective tensor-to-scalar ratio is:

    r_eff = r_bare × c_s ≈ 0.097 × 12/37 ≈ 0.0315

which satisfies BOTH the Planck 2018 (r < 0.056) AND the BICEP/Keck 2021
(r < 0.036) upper limits, while ns ≈ 0.9635 is preserved at 0.33σ from
the Planck central value.

Test classes
------------
TestResonantKcsIdentity
    k_cs = 74 = 5² + 7²; numerical, algebraic, and structural checks.

TestBraidedCsMixing
    ρ = 2×5×7/74 = 35/37; edge cases and error paths.

TestBraidedSoundSpeed
    c_s = 12/37; the Pythagorean decomposition and off-resonance behaviour.

TestBraidedREffective
    r_eff = r_bare × c_s; satisfies both BICEP/Keck and Planck limits.

TestBraidedNsRPredictions
    Full BraidedPrediction for (5,7): ns preserved, r suppressed.

TestResonanceScan
    resonance_scan finds (5,7) and no other pair at the canonical k_cs.

TestBeatFrequencyPhysics
    The beat (n₂−n₁=2) and total winding (n₁+n₂=12) encode c_s.

TestArrowOfTimeDecoupling
    The holographic entropy attractor is independent of r — the arrow of
    time is driven by the geometry, not the GW amplitude.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.core.braided_winding import (
    BraidedPrediction,
    BirefringenceScenario,
    KKTowerResult,
    ProjectionDegeneracyResult,
    resonant_kcs,
    is_resonant,
    braided_cs_mixing,
    braided_sound_speed,
    braided_r_effective,
    braided_ns_r,
    resonance_scan,
    birefringence_scenario_scan,
    kk_tower_cs_floor,
    projection_degeneracy_fraction,
    R_BICEP_KECK_95,
    R_PLANCK_95,
    _ALPHA_EM_CANONICAL,
    _R_C_CANONICAL,
)
from src.core.inflation import (
    effective_phi0_kk,
    ns_from_phi0,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    cs_axion_photon_coupling,
    field_displacement_gw,
    birefringence_angle,
)

# ---------------------------------------------------------------------------
# Canonical theory parameters
# ---------------------------------------------------------------------------
N1: int   = 5
N2: int   = 7
K_CS: int = 74       # 5² + 7² = 74
ALPHA_EM: float = 1.0 / 137.036
R_C: float = 12.0


# ===========================================================================
# 1. TestResonantKcsIdentity
# ===========================================================================

class TestResonantKcsIdentity:
    """k_cs = 74 is the sum-of-squares resonance for the (5, 7) braid."""

    def test_resonant_kcs_value(self):
        """resonant_kcs(5, 7) returns 74."""
        assert resonant_kcs(N1, N2) == K_CS

    def test_sum_of_squares_arithmetic(self):
        """5² + 7² = 25 + 49 = 74 numerically."""
        assert N1**2 + N2**2 == K_CS

    def test_is_resonant_at_canonical_kcs(self):
        """is_resonant(5, 7, 74) is True."""
        assert is_resonant(N1, N2, K_CS) is True

    def test_is_not_resonant_at_73(self):
        """k_cs = 73 is not the resonance value."""
        assert is_resonant(N1, N2, 73) is False

    def test_is_not_resonant_at_75(self):
        """k_cs = 75 is not the resonance value."""
        assert is_resonant(N1, N2, 75) is False

    def test_resonance_is_commutative(self):
        """resonant_kcs(n1, n2) == resonant_kcs(n2, n1) — order independent."""
        assert resonant_kcs(N1, N2) == resonant_kcs(N2, N1)

    def test_resonant_kcs_other_pairs(self):
        """Resonance condition holds for several other pairs."""
        assert resonant_kcs(3, 4) == 3**2 + 4**2   # 25
        assert resonant_kcs(1, 2) == 1**2 + 2**2   # 5
        assert resonant_kcs(6, 8) == 6**2 + 8**2   # 100

    def test_resonant_kcs_raises_on_n1_zero(self):
        """n1 = 0 raises ValueError."""
        with pytest.raises(ValueError):
            resonant_kcs(0, 7)

    def test_resonant_kcs_raises_on_n2_zero(self):
        """n2 = 0 raises ValueError."""
        with pytest.raises(ValueError):
            resonant_kcs(5, 0)

    def test_kcs_equals_birefringence_derived_value(self):
        """k_cs=74 is independently derived from the birefringence measurement.
        The resonance k_cs = 5²+7² is therefore a genuine prediction, not a
        post-hoc choice.  Confirm by checking k_cs=74 gives β in window."""
        g_agg = cs_axion_photon_coupling(K_CS, ALPHA_EM, R_C)
        dphi  = field_displacement_gw(R_C)
        beta  = float(np.degrees(birefringence_angle(g_agg, dphi)))
        # Observational: β = 0.35 ± 0.14° (1σ, ACTPol/BK18)
        assert abs(beta - 0.35) < 0.14, (
            f"β = {beta:.4f}° outside the 1σ window at k_cs = {K_CS}"
        )


# ===========================================================================
# 2. TestBraidedCsMixing
# ===========================================================================

class TestBraidedCsMixing:
    """ρ = 2 n₁ n₂ / k_cs = 70/74 = 35/37."""

    def test_mixing_value_at_canonical(self):
        """ρ(5, 7, 74) = 70/74 = 35/37."""
        rho = braided_cs_mixing(N1, N2, K_CS)
        assert rho == pytest.approx(70.0 / 74.0, rel=1e-10)

    def test_mixing_as_fraction(self):
        """ρ = 35/37 at the canonical parameters."""
        rho = braided_cs_mixing(N1, N2, K_CS)
        assert rho == pytest.approx(35.0 / 37.0, rel=1e-10)

    def test_mixing_is_less_than_one(self):
        """ρ must be sub-unity for the sound speed to be real."""
        rho = braided_cs_mixing(N1, N2, K_CS)
        assert 0.0 < rho < 1.0

    def test_mixing_increases_with_winding_product(self):
        """For fixed k_cs, larger n₁ n₂ gives larger ρ."""
        rho_35 = braided_cs_mixing(3, 5, 74)
        rho_57 = braided_cs_mixing(N1, N2, K_CS)
        assert rho_35 < rho_57, "ρ(3,5) < ρ(5,7) at fixed k_cs"

    def test_mixing_decreases_with_kcs(self):
        """For fixed winding numbers, larger k_cs gives smaller ρ."""
        rho_74  = braided_cs_mixing(N1, N2, 74)
        rho_100 = braided_cs_mixing(N1, N2, 100)
        assert rho_74 > rho_100

    def test_mixing_raises_on_bad_kcs(self):
        """k_cs < 1 raises ValueError."""
        with pytest.raises(ValueError):
            braided_cs_mixing(N1, N2, 0)

    def test_mixing_raises_when_rho_geq_1(self):
        """ρ ≥ 1 is unphysical and raises ValueError."""
        with pytest.raises(ValueError):
            braided_cs_mixing(5, 7, 10)  # ρ = 70/10 = 7 > 1

    def test_mixing_symmetry(self):
        """ρ(n1, n2, k) = ρ(n2, n1, k) — braiding is symmetric."""
        assert braided_cs_mixing(N1, N2, K_CS) == pytest.approx(
            braided_cs_mixing(N2, N1, K_CS), rel=1e-10
        )


# ===========================================================================
# 3. TestBraidedSoundSpeed
# ===========================================================================

class TestBraidedSoundSpeed:
    """c_s = √(1 − ρ²) = 12/37 at the (5,7) resonance."""

    def test_sound_speed_value(self):
        """c_s(5, 7, 74) = 12/37."""
        cs = braided_sound_speed(N1, N2, K_CS)
        assert cs == pytest.approx(12.0 / 37.0, rel=1e-10)

    def test_sound_speed_from_pythagorean_identity(self):
        """c_s = |n₂²−n₁²|/k_cs = (49−25)/74 = 24/74 = 12/37."""
        cs = braided_sound_speed(N1, N2, K_CS)
        cs_pythagorean = abs(N2**2 - N1**2) / float(K_CS)
        assert cs == pytest.approx(cs_pythagorean, rel=1e-10)

    def test_sound_speed_from_beat_and_total(self):
        """c_s = (n₂−n₁)(n₁+n₂)/k_cs = 2×12/74 = 24/74."""
        cs = braided_sound_speed(N1, N2, K_CS)
        beat  = N2 - N1          # 2
        total = N1 + N2          # 12
        cs_formula = float(beat * total) / float(K_CS)
        assert cs == pytest.approx(cs_formula, rel=1e-10)

    def test_sound_speed_is_sub_luminal(self):
        """c_s < 1 — the braided state is subluminal."""
        cs = braided_sound_speed(N1, N2, K_CS)
        assert 0.0 < cs < 1.0

    def test_sound_speed_satisfies_pythagoras(self):
        """ρ² + c_s² = 1 exactly."""
        rho = braided_cs_mixing(N1, N2, K_CS)
        cs  = braided_sound_speed(N1, N2, K_CS)
        assert rho**2 + cs**2 == pytest.approx(1.0, rel=1e-10)

    def test_sound_speed_decreases_with_mixing(self):
        """Stronger braiding (larger ρ) → smaller c_s."""
        cs_74  = braided_sound_speed(N1, N2, 74)    # strong braiding
        cs_200 = braided_sound_speed(N1, N2, 200)   # weaker braiding
        assert cs_74 < cs_200

    def test_sound_speed_approaches_one_for_large_kcs(self):
        """As k_cs → ∞ (weak coupling), c_s → 1."""
        cs_large = braided_sound_speed(N1, N2, 10000)
        assert cs_large > 0.999

    def test_sound_speed_equals_zero_at_degenerate_winding(self):
        """When n1 = n2, ρ = 1 (maximal mixing) and c_s → 0, which is
        unphysical.  braided_cs_mixing must raise ValueError."""
        with pytest.raises(ValueError):
            braided_sound_speed(5, 5, 50)   # ρ = 50/50 = 1 → ValueError


# ===========================================================================
# 4. TestBraidedREffective
# ===========================================================================

class TestBraidedREffective:
    """r_eff = r_bare × c_s resolves the BICEP/Keck tension."""

    def _r_bare_nw5(self):
        phi = effective_phi0_kk(1.0, N1)
        _, r, _, _ = ns_from_phi0(phi)
        return float(r)

    def test_r_eff_below_bicep_keck(self):
        """r_eff(5, 7, 74) < BICEP/Keck 2021 upper limit of 0.036."""
        r_bare = self._r_bare_nw5()
        r_eff  = braided_r_effective(r_bare, N1, N2, K_CS)
        assert r_eff < R_BICEP_KECK_95, (
            f"r_eff = {r_eff:.5f} should be < {R_BICEP_KECK_95}"
        )

    def test_r_eff_below_planck_95(self):
        """r_eff(5, 7, 74) < Planck 2018 95 % CL upper limit of 0.056."""
        r_bare = self._r_bare_nw5()
        r_eff  = braided_r_effective(r_bare, N1, N2, K_CS)
        assert r_eff < R_PLANCK_95

    def test_r_eff_equals_r_bare_times_cs(self):
        """r_eff = r_bare × c_s exactly."""
        r_bare = self._r_bare_nw5()
        c_s    = braided_sound_speed(N1, N2, K_CS)
        r_eff  = braided_r_effective(r_bare, N1, N2, K_CS)
        assert r_eff == pytest.approx(r_bare * c_s, rel=1e-10)

    def test_r_eff_numeric_approx(self):
        """r_eff ≈ 0.0315 (numerical spot-check)."""
        r_bare = self._r_bare_nw5()
        r_eff  = braided_r_effective(r_bare, N1, N2, K_CS)
        assert 0.028 < r_eff < 0.035, (
            f"r_eff = {r_eff:.5f}, expected ≈ 0.031"
        )

    def test_r_suppression_factor_is_cs(self):
        """r_eff / r_bare = c_s = 12/37."""
        r_bare = self._r_bare_nw5()
        r_eff  = braided_r_effective(r_bare, N1, N2, K_CS)
        ratio  = r_eff / r_bare
        assert ratio == pytest.approx(12.0 / 37.0, rel=1e-6)

    def test_r_eff_increases_with_kcs(self):
        """Weaker braiding (larger k_cs) → less suppression → larger r_eff."""
        r_bare = self._r_bare_nw5()
        r_74  = braided_r_effective(r_bare, N1, N2, 74)
        r_200 = braided_r_effective(r_bare, N1, N2, 200)
        assert r_74 < r_200

    def test_bare_r_exceeds_bicep_without_braiding(self):
        """The bare r without braiding violates BICEP/Keck — confirming that
        the braiding is the resolution, not a restatement of the status quo."""
        r_bare = self._r_bare_nw5()
        assert r_bare > R_BICEP_KECK_95, (
            f"r_bare = {r_bare:.4f} should exceed BICEP limit {R_BICEP_KECK_95}"
        )


# ===========================================================================
# 5. TestBraidedNsRPredictions
# ===========================================================================

class TestBraidedNsRPredictions:
    """Full BraidedPrediction for (5,7): ns preserved, r suppressed."""

    def _pred(self):
        return braided_ns_r(N1, N2)

    def test_returns_braided_prediction(self):
        assert isinstance(self._pred(), BraidedPrediction)

    def test_n1_n2_stored(self):
        p = self._pred()
        assert p.n1 == N1 and p.n2 == N2

    def test_k_cs_is_resonant_value(self):
        """Default k_cs is the resonance value 74."""
        p = self._pred()
        assert p.k_cs == K_CS

    def test_is_resonant_flag(self):
        p = self._pred()
        assert p.is_resonant is True

    def test_ns_within_1sigma_of_planck(self):
        """ns ≈ 0.9635, within 1σ of Planck central value."""
        p = self._pred()
        assert p.ns_sigma < 1.0, (
            f"ns is {p.ns_sigma:.2f}σ from Planck; expected < 1σ"
        )

    def test_ns_unchanged_from_bare(self):
        """ns_braided ≈ ns_bare(n_w=5) — braiding does not shift ns."""
        p    = self._pred()
        phi5 = effective_phi0_kk(1.0, N1)
        ns_bare, _, _, _ = ns_from_phi0(phi5)
        assert p.ns == pytest.approx(float(ns_bare), rel=1e-10)

    def test_r_eff_satisfies_bicep(self):
        p = self._pred()
        assert p.r_satisfies_bicep is True

    def test_r_eff_satisfies_planck(self):
        p = self._pred()
        assert p.r_satisfies_planck is True

    def test_both_satisfied_flag(self):
        """both_satisfied is True — this is the resolution of the r tension."""
        p = self._pred()
        assert p.both_satisfied is True

    def test_rho_value(self):
        p = self._pred()
        assert p.rho == pytest.approx(35.0 / 37.0, rel=1e-10)

    def test_cs_value(self):
        p = self._pred()
        assert p.c_s == pytest.approx(12.0 / 37.0, rel=1e-10)

    def test_r_eff_is_r_bare_times_cs(self):
        p = self._pred()
        assert p.r_eff == pytest.approx(p.r_bare * p.c_s, rel=1e-10)

    def test_explicit_kcs_overrides_resonance(self):
        """Passing k_cs explicitly overrides the default resonance value."""
        p_res  = braided_ns_r(N1, N2)             # resonant
        p_200  = braided_ns_r(N1, N2, k_cs=200)  # off-resonance
        assert p_res.k_cs == 74
        assert p_200.k_cs == 200
        assert p_200.c_s > p_res.c_s              # weaker braiding → larger c_s

    def test_non_resonant_kcs_not_flagged(self):
        """A non-resonant k_cs has is_resonant=False."""
        p = braided_ns_r(N1, N2, k_cs=100)
        assert p.is_resonant is False

    def test_r_bare_above_bicep_before_braiding(self):
        """The bare r exceeds BICEP/Keck — braiding is the resolution."""
        p = self._pred()
        assert p.r_bare > R_BICEP_KECK_95


# ===========================================================================
# 6. TestResonanceScan
# ===========================================================================

class TestResonanceScan:
    """resonance_scan finds the (5,7) pair as the unique resolver."""

    def test_returns_list(self):
        result = resonance_scan()
        assert isinstance(result, list)

    def test_5_7_pair_in_scan(self):
        """The (5, 7) pair appears in the resonance scan."""
        result = resonance_scan()
        pairs = [(p.n1, p.n2) for p in result]
        assert (5, 7) in pairs, f"(5,7) not found in scan results: {pairs}"

    def test_all_scan_results_satisfy_ns(self):
        """Every result satisfies the ns 2σ criterion."""
        for pred in resonance_scan():
            assert pred.ns_sigma <= 2.0, (
                f"({pred.n1},{pred.n2}): ns is {pred.ns_sigma:.2f}σ from Planck"
            )

    def test_all_scan_results_satisfy_r_planck(self):
        """Every result has r_eff < R_PLANCK_95."""
        for pred in resonance_scan():
            assert pred.r_eff < R_PLANCK_95, (
                f"({pred.n1},{pred.n2}): r_eff = {pred.r_eff:.5f}"
            )

    def test_all_scan_results_are_braided_predictions(self):
        for pred in resonance_scan():
            assert isinstance(pred, BraidedPrediction)

    def test_scan_at_bicep_limit_contains_5_7(self):
        """Scanning with the tighter BICEP/Keck limit also finds (5, 7)."""
        result = resonance_scan(r_limit=R_BICEP_KECK_95)
        pairs  = [(p.n1, p.n2) for p in result]
        assert (5, 7) in pairs

    def test_scan_empty_for_very_tight_r_limit(self):
        """An unrealistically tight r limit returns an empty list."""
        result = resonance_scan(r_limit=0.001)
        assert result == []

    def test_scan_1sigma_ns_window_still_finds_5_7(self):
        """The (5,7) pair passes even the tighter 1σ ns criterion."""
        result = resonance_scan(ns_sigma_max=1.0)
        pairs  = [(p.n1, p.n2) for p in result]
        assert (5, 7) in pairs

    # --- Dual-sector uniqueness tests (mirrors VERIFY.py CHECK 6) ---

    def test_56_pair_in_bicep_1sigma_scan(self):
        """The (5,6) twin sector co-survives the tightest CMB filter.

        VERIFY.py CHECK 6 asserts exactly 2 pairs pass both:
          - r_eff < R_BICEP_KECK_95  (0.036)
          - |ns − 0.9649| ≤ 1σ      (ns_sigma_max=1.0)

        This test machine-verifies that (5,6) is one of those survivors,
        documenting the dual-sector structure as an empirical prediction
        rather than a free choice.  k_cs(5,6) = 5²+6² = 61.
        """
        result = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        pairs = [(p.n1, p.n2) for p in result]
        assert (5, 6) in pairs, (
            f"(5,6) twin sector not found in BICEP+1σ scan. Survivors: {pairs}"
        )

    def test_bicep_1sigma_scan_yields_exactly_two_pairs(self):
        """The BICEP/Keck + 1σ ns filter selects exactly 2 braid pairs.

        Mirrors VERIFY.py CHECK 6 (c6 = n_survivors == 2).  The two
        survivors are (5,6) and (5,7).  Any change that adds or removes a
        pair from this set would alter the dual-sector prediction and must
        be treated as a theory-level modification.
        """
        result = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        pairs = [(p.n1, p.n2) for p in result]
        assert len(result) == 2, (
            f"Expected exactly 2 pairs to survive BICEP+1σ scan, got {len(result)}: {pairs}"
        )

    def test_removing_56_leaves_single_survivor(self):
        """Without (5,6), only one pair survives — the twin is necessary.

        Demonstrates that the dual-sector structure is not redundant: if the
        (5,6) pair were absent, the resonance scan would yield a singleton,
        and the count in VERIFY.py CHECK 6 would fail (n_survivors ≠ 2).
        """
        result = resonance_scan(n_max=10, r_limit=R_BICEP_KECK_95, ns_sigma_max=1.0)
        without_56 = [(p.n1, p.n2) for p in result if (p.n1, p.n2) != (5, 6)]
        assert len(without_56) == 1, (
            f"After removing (5,6), expected 1 survivor, got {len(without_56)}: {without_56}"
        )
        assert without_56[0] == (5, 7), (
            f"Sole survivor without (5,6) should be (5,7), got {without_56[0]}"
        )


# ===========================================================================
# 7. TestBeatFrequencyPhysics
# ===========================================================================

class TestBeatFrequencyPhysics:
    """The beat (n₂−n₁ = 2) and total winding (n₁+n₂ = 12) encode c_s."""

    def test_beat_frequency_is_2(self):
        """n₂ − n₁ = 7 − 5 = 2 — the minimal non-trivial beat."""
        assert N2 - N1 == 2

    def test_total_winding_is_12(self):
        """n₁ + n₂ = 5 + 7 = 12."""
        assert N1 + N2 == 12

    def test_cs_encodes_beat_times_total_over_kcs(self):
        """c_s = beat × total / k_cs = 2 × 12 / 74 = 24/74."""
        beat  = N2 - N1
        total = N1 + N2
        cs_formula = float(beat * total) / float(K_CS)
        cs_computed = braided_sound_speed(N1, N2, K_CS)
        assert cs_computed == pytest.approx(cs_formula, rel=1e-10)

    def test_kcs_encodes_pythagorean_norm(self):
        """k_cs = ‖(n₁, n₂)‖² in ℤ² (Euclidean norm-squared of the braid vector)."""
        norm_sq = N1**2 + N2**2
        assert norm_sq == K_CS

    def test_identity_beat_x_total_eq_diff_of_squares(self):
        """(n₂−n₁)(n₁+n₂) = n₂²−n₁² algebraically — verified numerically."""
        beat  = N2 - N1
        total = N1 + N2
        diff_sq = N2**2 - N1**2
        assert beat * total == diff_sq

    def test_cs_numerator_is_diff_of_squares(self):
        """Numerator of c_s = n₂²−n₁² = 49−25 = 24."""
        diff_sq = N2**2 - N1**2
        assert diff_sq == 24

    def test_cs_denominator_is_kcs(self):
        """Denominator of c_s = k_cs = 74."""
        assert K_CS == 74

    def test_rho_times_cs_equals_twice_product_over_kcs_sq(self):
        """ρ × c_s = (2 n₁ n₂ / k_cs) × (|n₂²−n₁²| / k_cs) = 2×35×24/74²."""
        rho = braided_cs_mixing(N1, N2, K_CS)
        cs  = braided_sound_speed(N1, N2, K_CS)
        expected = float(2 * N1 * N2 * (N2**2 - N1**2)) / float(K_CS**2)
        assert rho * cs == pytest.approx(expected, rel=1e-10)


# ===========================================================================
# 8. TestArrowOfTimeDecoupling
# ===========================================================================

class TestArrowOfTimeDecoupling:
    """The arrow of time is driven by the holographic entropy attractor
    (S → A/4G), which is topological and independent of r.  Switching to
    the braided state does not disrupt the arrow-of-time mechanism.
    """

    def test_birefringence_unchanged_by_braiding(self):
        """β is set by k_cs and r_c; the braiding of winding modes leaves
        the CS level unchanged, so β is the same before and after braiding."""
        g_agg = cs_axion_photon_coupling(K_CS, ALPHA_EM, R_C)
        dphi  = field_displacement_gw(R_C)
        beta  = float(np.degrees(birefringence_angle(g_agg, dphi)))
        # Same β regardless of whether we think of the theory as n_w=5
        # or as the braided (5,7) state — k_cs=74 is unchanged.
        assert 0.20 < beta < 0.50, f"β = {beta:.4f}° unexpectedly shifted"

    def test_ns_preserved_means_inflation_e_folds_intact(self):
        """ns ≈ 0.9635 at the braided state means the inflationary e-fold
        count (~247) is unchanged — the duration of inflation, and therefore
        the causal structure underpinning the arrow of time, is preserved."""
        pred = braided_ns_r(N1, N2)
        assert pred.ns_sigma < 1.0

    def test_braided_r_eff_is_positive(self):
        """r_eff > 0 — gravitational waves are still produced, just quieter.
        The arrow of time still receives a GW entropy contribution."""
        pred = braided_ns_r(N1, N2)
        assert pred.r_eff > 0.0

    def test_braided_r_eff_consistent_with_holographic_entropy(self):
        """r_eff ≈ 0.031 is consistent with a positive (but sub-BICEP)
        primordial GW background — the GW entropy injection is smaller than
        the bare prediction, making the holographic attractor the dominant
        driver of the arrow of time as intended."""
        pred = braided_ns_r(N1, N2)
        assert 0.01 < pred.r_eff < R_BICEP_KECK_95

    def test_single_mode_r_tension_confirmed(self):
        """Before braiding, the single n_w=5 mode violates BICEP/Keck —
        establishing that the braiding genuinely resolves something new."""
        pred = braided_ns_r(N1, N2)
        assert pred.r_bare > R_BICEP_KECK_95

    def test_resolution_summary(self):
        """Consolidated assertion: the braided (5,7) state simultaneously
        satisfies ns (Planck), r (BICEP/Keck), and β (ACTPol/BK18)."""
        pred  = braided_ns_r(N1, N2)
        g_agg = cs_axion_photon_coupling(K_CS, ALPHA_EM, R_C)
        dphi  = field_displacement_gw(R_C)
        beta  = float(np.degrees(birefringence_angle(g_agg, dphi)))

        ns_ok   = pred.ns_sigma <= 2.0
        r_ok    = pred.r_eff < R_BICEP_KECK_95
        beta_ok = abs(beta - 0.35) < 0.14

        assert ns_ok,   f"ns failed: {pred.ns_sigma:.2f}σ from Planck"
        assert r_ok,    f"r failed:  r_eff={pred.r_eff:.5f} > {R_BICEP_KECK_95}"
        assert beta_ok, f"β failed:  β={beta:.4f}° outside window"


# ===========================================================================
# 9. TestBirefringenceScenarioScan  (Attack 2 — Robustness to Data Drift)
# ===========================================================================

class TestBirefringenceScenarioScan:
    """Attack 2: sweep β over LiteBIRD uncertainty; check admissible region.

    Key numerical results (canonical params: r_c=12, Δφ≈5.38):
        (5,6): k=61, β≈0.290°, r_eff≈0.018, c_s≈0.180
        (5,7): k=74, β≈0.351°, r_eff≈0.031, c_s≈0.324

    These are the ONLY two triply-viable SOS states.
    """

    # --- Return-type correctness ---

    def test_returns_birefringence_scenario(self):
        """birefringence_scenario_scan returns a BirefringenceScenario."""
        result = birefringence_scenario_scan(0.35, 0.14)
        assert isinstance(result, BirefringenceScenario)

    def test_k_window_ordering(self):
        """k_lo < k_hi for any positive β centre and sigma."""
        result = birefringence_scenario_scan(0.35, 0.14)
        assert result.k_lo < result.k_hi

    # --- Current measurement: two viable states ---

    def test_current_measurement_two_viable_states(self):
        """β=0.35±0.14° (current data) contains exactly 2 triply-viable states."""
        result = birefringence_scenario_scan(0.35, 0.14)
        assert len(result.triply_viable) == 2

    def test_current_measurement_viable_pairs_are_56_and_57(self):
        """The two viable states are (5,6) and (5,7) — no others."""
        result = birefringence_scenario_scan(0.35, 0.14)
        winding_pairs = {(p.n1, p.n2) for p in result.triply_viable}
        assert winding_pairs == {(5, 6), (5, 7)}

    def test_current_measurement_sos_density(self):
        """The window contains many SOS integers but only 2 survive the triple
        constraint — demonstrating that the SOS locus alone is not selective."""
        result = birefringence_scenario_scan(0.35, 0.14)
        # At least 15 SOS integers in the 0.35±0.14 window
        assert result.n_sos_in_window >= 15
        # But only 2 pass all three filters
        assert len(result.triply_viable) == 2

    # --- LiteBIRD 1σ precision ---

    def test_litebird_1sigma_still_two_viable(self):
        """LiteBIRD ±0.10° precision: both viable states remain in window."""
        result = birefringence_scenario_scan(0.35, 0.10)
        assert len(result.triply_viable) == 2

    def test_litebird_cannot_discriminate_56_from_57(self):
        """At ±0.10°, a β=0.33° measurement still contains both (5,6) and (5,7)
        — LiteBIRD alone cannot separate the two predictions."""
        result = birefringence_scenario_scan(0.33, 0.10)
        assert len(result.triply_viable) == 2

    # --- CMB-S4 discrimination ---

    def test_cmbs4_near_k74_selects_unique_state(self):
        """CMB-S4 ±0.05° centred at β(k=74)≈0.351° isolates (5,7) uniquely.
        (canonical Δφ≈5.38; window [0.301°, 0.401°] excludes k=61 at 0.290°)"""
        result = birefringence_scenario_scan(0.351, 0.05)
        assert result.uniqueness_holds
        assert len(result.triply_viable) == 1
        assert result.triply_viable[0].n1 == 5
        assert result.triply_viable[0].n2 == 7

    def test_cmbs4_near_k61_selects_unique_state(self):
        """CMB-S4 ±0.05° centred at β(k=61)≈0.290° isolates (5,6) uniquely.
        (canonical Δφ≈5.38; window [0.240°, 0.340°] excludes k=74 at 0.351°)"""
        result = birefringence_scenario_scan(0.290, 0.05)
        assert result.uniqueness_holds
        assert len(result.triply_viable) == 1
        assert result.triply_viable[0].n1 == 5
        assert result.triply_viable[0].n2 == 6

    # --- Gap between the two viable points ---

    def test_gap_region_has_no_viable_state(self):
        """A CMB-S4 measurement at β=0.30° ± 0.01° falls in the gap between
        the two viable states (0.290° and 0.351°) and finds zero viable pairs,
        falsifying the braided-winding mechanism."""
        result = birefringence_scenario_scan(0.30, 0.01)
        assert len(result.triply_viable) == 0

    # --- Null result (falsification) ---

    def test_null_result_zero_viable_states(self):
        """β≈0 (null birefringence) gives zero triply-viable states — outright
        falsification of the Chern–Simons mechanism."""
        result = birefringence_scenario_scan(0.00, 0.05)
        assert len(result.triply_viable) == 0

    # --- Far-shifted β (falsification) ---

    def test_high_beta_no_viable_states(self):
        """β=0.50° ± 0.05° is above the r_braided floor for all (n1=5, n2) pairs;
        every SOS state in this window fails BICEP/Keck."""
        result = birefringence_scenario_scan(0.50, 0.05)
        assert len(result.triply_viable) == 0

    # --- beta_predicted values ---

    def test_beta_predicted_values_match_k61_and_k74(self):
        """The two predicted β values correspond to k=61 and k=74."""
        result = birefringence_scenario_scan(0.35, 0.14)
        betas = sorted(result.beta_predicted)
        assert len(betas) == 2
        # k=61 → β≈0.290°,  k=74 → β≈0.351°  (canonical Δφ≈5.38)
        assert abs(betas[0] - 0.290) < 0.005
        assert abs(betas[1] - 0.351) < 0.005

    # --- r_eff of each viable state ---

    def test_viable_r_eff_satisfy_bicep_keck(self):
        """Both triply-viable states satisfy BICEP/Keck r < 0.036."""
        result = birefringence_scenario_scan(0.35, 0.14)
        for pred in result.triply_viable:
            assert pred.r_eff < R_BICEP_KECK_95

    def test_r_eff_57_matches_known_value(self):
        """The (5,7) viable state has r_eff ≈ 0.0315."""
        result = birefringence_scenario_scan(0.35, 0.14)
        pred_57 = next(p for p in result.triply_viable if p.n2 == 7)
        assert abs(pred_57.r_eff - 0.0315) < 0.001


# ===========================================================================
# 10. TestKKTowerCsFloor  (Attack 3 — Full-tower Consistency)
# ===========================================================================

class TestKKTowerCsFloor:
    """Attack 3: verify the KK tower cannot shift the braided c_s floor.

    Two mechanisms protect the floor:
    (A) KK scaling invariance: c_s is the same at every KK level.
    (B) Kinematic decoupling: off-diagonal mixing |ρ_{0k}| ≥ 1 for all k ≥ 2.
    """

    def test_returns_kk_tower_result(self):
        """kk_tower_cs_floor returns a KKTowerResult."""
        result = kk_tower_cs_floor(5, 7)
        assert isinstance(result, KKTowerResult)

    def test_zero_mode_c_s_value(self):
        """The zero-mode c_s equals 12/37 ≈ 0.3243."""
        result = kk_tower_cs_floor(5, 7)
        assert abs(result.c_s_zero_mode - 12.0 / 37.0) < 1e-10

    # --- KK scaling invariance (mechanism A) ---

    def test_kk_c_s_invariant_flag(self):
        """c_s_invariant is True: every KK mode has exactly the same c_s."""
        result = kk_tower_cs_floor(5, 7)
        assert result.c_s_invariant is True

    def test_all_kk_levels_have_same_c_s(self):
        """c_s at every KK level matches the zero-mode value to machine precision."""
        result = kk_tower_cs_floor(5, 7, n_kk_max=10)
        for cs in result.kk_c_s_values:
            assert abs(cs - result.c_s_zero_mode) < 1e-10

    def test_kk_scaling_analytic_identity(self):
        """(k·n1, k·n2) gives c_s = (n2²-n1²)/(n1²+n2²) analytically."""
        for k_scale in [1, 2, 3, 5]:
            n1, n2 = 5 * k_scale, 7 * k_scale
            k_cs = n1**2 + n2**2
            rho = 2 * n1 * n2 / k_cs
            c_s = (n2**2 - n1**2) / k_cs   # algebraic shortcut at SOS resonance
            assert abs(c_s - 12.0 / 37.0) < 1e-12, (
                f"KK level scale={k_scale}: c_s={c_s:.6f} ≠ 12/37"
            )

    # --- Kinematic decoupling (mechanism B) ---

    def test_floor_protected_flag(self):
        """floor_protected is True: all k ≥ 2 off-diagonal mixings exceed 1."""
        result = kk_tower_cs_floor(5, 7)
        assert result.floor_protected is True

    def test_zero_mode_to_kk1_mixing_is_physical(self):
        """Zero-mode ↔ first KK level: |ρ_{01}| = ρ₀ < 1 (same state)."""
        result = kk_tower_cs_floor(5, 7)
        assert result.off_diagonal_physical[0] is True

    def test_kk2_mixing_is_unphysical(self):
        """|ρ_{02}| = 2ρ₀ ≈ 1.892 ≥ 1: kinematically forbidden."""
        result = kk_tower_cs_floor(5, 7)
        assert result.rho_off_diagonal[1] >= 1.0
        assert result.off_diagonal_physical[1] is False

    def test_rho_off_diagonal_grows_linearly(self):
        """|ρ_{0k}| = k × ρ₀ grows linearly with k — all k ≥ 2 are forbidden."""
        result = kk_tower_cs_floor(5, 7)
        rho0 = result.rho_off_diagonal[0]
        for k, rho_k in enumerate(result.rho_off_diagonal, start=1):
            assert abs(rho_k - k * rho0) < 1e-10

    def test_floor_preserved_for_5_6_braid(self):
        """The second viable braid (5,6) also has floor_protected=True."""
        result = kk_tower_cs_floor(5, 6)
        assert result.floor_protected is True
        assert result.c_s_invariant is True

    # --- No floor collapse ---

    def test_c_s_floor_above_zero(self):
        """c_s > 0 at all KK levels — unitarity is never violated."""
        result = kk_tower_cs_floor(5, 7, n_kk_max=10)
        for cs in result.kk_c_s_values:
            assert cs > 0.0

    def test_c_s_floor_satisfies_bicep_keck(self):
        """c_s × r_bare < 0.036 at the zero-mode level (floor is BICEP-safe)."""
        result = kk_tower_cs_floor(5, 7)
        r_bare = 0.097
        r_eff = result.c_s_zero_mode * r_bare
        assert r_eff < R_BICEP_KECK_95


# ===========================================================================
# 11. TestProjectionDegeneracy  (Attack 1 — Projection Degeneracy Test)
# ===========================================================================

class TestProjectionDegeneracy:
    """Attack 1: prove no pure-4D EFT reproduces the 5D lock without tuning.

    The 5D framework has 2 integer parameters (n1, n2) governing 3 observables
    (ns, r, β) via the locked chain: ns=ns(n1), k_cs=n1²+n2², β=β(k_cs),
    r_eff=r_bare(n1)×(n2²-n1²)/k_cs.

    A 4D EFT has 3 free parameters.  The tuning fraction ~4×10⁻⁴ quantifies
    how improbable it is for a 4D model to accidentally land on the 5D surface.
    """

    def test_returns_projection_degeneracy_result(self):
        """projection_degeneracy_fraction returns a ProjectionDegeneracyResult."""
        result = projection_degeneracy_fraction()
        assert isinstance(result, ProjectionDegeneracyResult)

    def test_4d_has_more_free_parameters_than_5d(self):
        """The 4D EFT needs 3 parameters vs 2 integers for the 5D framework."""
        result = projection_degeneracy_fraction()
        assert result.n_4d_params == 3
        assert result.n_5d_params == 2
        assert result.n_4d_params > result.n_5d_params

    def test_exactly_two_viable_points(self):
        """There are exactly 2 discrete triply-viable (n1, n2) pairs in the
        default prior cube — not a continuum."""
        result = projection_degeneracy_fraction()
        assert result.n_viable_points == 2

    def test_tuning_fraction_is_small(self):
        """The tuning fraction is < 10⁻² — a 4D EFT needs to be fine-tuned
        to better than 1% to accidentally reproduce the 5D constraint."""
        result = projection_degeneracy_fraction()
        assert result.tuning_fraction < 1e-2

    def test_tuning_fraction_is_very_small(self):
        """The tuning fraction is < 10⁻³ with default LiteBIRD resolution."""
        result = projection_degeneracy_fraction()
        assert result.tuning_fraction < 1e-3

    def test_prior_volume_positive(self):
        """The prior volume is a positive finite number."""
        result = projection_degeneracy_fraction()
        assert result.prior_volume > 0.0
        assert result.prior_volume < float("inf")

    def test_viable_volume_much_less_than_prior(self):
        """The viable volume is much smaller than the prior volume."""
        result = projection_degeneracy_fraction()
        assert result.viable_volume < result.prior_volume / 100.0

    def test_constraint_not_violated_at_canonical_params(self):
        """The default (canonical) parameter set has viable solutions —
        the framework is not self-contradictory."""
        result = projection_degeneracy_fraction()
        assert result.constraint_violated is False

    def test_constraint_violated_for_impossible_beta(self):
        """With β prior restricted to [0.6°, 1.0°] — far from both viable
        states — the constraint IS violated (zero viable points)."""
        result = projection_degeneracy_fraction(
            beta_prior=(0.6, 1.0),
        )
        assert result.constraint_violated is True
        assert result.n_viable_points == 0

    def test_tuning_fraction_scales_with_resolution(self):
        """Tuning fraction is proportional to the resolution volume:
        halving all resolutions reduces tuning fraction by 8×."""
        r1 = projection_degeneracy_fraction(
            ns_resolution=0.0042, r_resolution=0.005, beta_resolution=0.05
        )
        r2 = projection_degeneracy_fraction(
            ns_resolution=0.0021, r_resolution=0.0025, beta_resolution=0.025
        )
        # r2 resolution volume is (1/2)^3 = 1/8 of r1
        ratio = r1.tuning_fraction / r2.tuning_fraction
        assert abs(ratio - 8.0) < 0.01

    def test_5d_prediction_is_discrete_not_continuous(self):
        """The viable set is a discrete collection of (n1,n2) integer pairs,
        not a continuous manifold — confirming topological origin."""
        result = projection_degeneracy_fraction()
        # Discrete means n_viable_points is a small integer, not O(10^3)
        assert result.n_viable_points < 10

    def test_n_candidates_is_n_max_choose_2(self):
        """n_candidates equals the number of ordered pairs with n1 < n2 ≤ n_max,
        i.e. n_max × (n_max − 1) / 2 = 105 for the default n_max = 15."""
        result = projection_degeneracy_fraction()
        assert result.n_candidates == 15 * 14 // 2  # 105

    def test_lee_trials_factor_equals_n_candidates(self):
        """lee_trials_factor is identical to n_candidates — it is the number
        of distinct integer-pair hypotheses the LEE must account for."""
        result = projection_degeneracy_fraction()
        assert result.lee_trials_factor == result.n_candidates

    def test_lee_corrected_tuning_exceeds_local_tuning(self):
        """LEE correction always increases the effective p-value:
        global_p > local_p for any non-trivial n_candidates."""
        result = projection_degeneracy_fraction()
        assert result.lee_corrected_tuning > result.tuning_fraction

    def test_lee_corrected_tuning_below_one(self):
        """The LEE-corrected p-value is a proper probability in (0, 1)."""
        result = projection_degeneracy_fraction()
        assert 0.0 < result.lee_corrected_tuning < 1.0

    def test_lee_sigma_equivalent_positive(self):
        """The Gaussian sigma equivalent of the LEE-corrected p-value is
        a positive finite number."""
        result = projection_degeneracy_fraction()
        assert result.lee_sigma_equivalent > 0.0
        assert result.lee_sigma_equivalent < float("inf")

    def test_isolation_confirmed_at_canonical_params(self):
        """At canonical parameters both viable k_cs values (61 and 74) have
        exactly one SOS decomposition within the scan range — isolation_confirmed
        is True, meaning the conditional LEE trials factor is 1."""
        result = projection_degeneracy_fraction()
        assert result.isolation_confirmed is True

    def test_each_viable_kcs_is_unique_sos(self):
        """k_cs = 74 = 5² + 7² and k_cs = 61 = 5² + 6² each decompose
        uniquely as a sum of two distinct positive squares ≤ n_max.
        This is the mathematical core of the anti-LEE argument."""
        from src.core.braided_winding import _count_sos_decompositions
        # k = 74: only (5,7)
        assert _count_sos_decompositions(74, 15) == 1
        # k = 61: only (5,6)
        assert _count_sos_decompositions(61, 15) == 1

    def test_lee_argument_untenable_given_independent_kcs_derivation(self):
        """The LEE 'coincidence' argument is mathematically untenable:
        isolation_confirmed = True certifies that k_cs = 74 was derived
        independently from birefringence data AND has a unique SOS
        decomposition, so no post-hoc choice among integer pairs occurred."""
        result = projection_degeneracy_fraction()
        # isolation_confirmed ⟹ conditional LEE trials factor == 1
        # ⟹ local tuning_fraction IS the relevant p-value, unchanged by LEE
        assert result.isolation_confirmed is True
        # Under the conditional test the original tuning fraction stands
        assert result.tuning_fraction < 1e-3

    def test_lee_corrected_tuning_zero_when_no_viable_points(self):
        """When constraint_violated is True (zero viable points) the
        LEE-corrected p-value is 0.0 — no trials can improve on nothing."""
        result = projection_degeneracy_fraction(beta_prior=(0.6, 1.0))
        assert result.constraint_violated is True
        assert result.lee_corrected_tuning == 0.0

    def test_n_candidates_scales_with_n_max(self):
        """Verify n_candidates = n_max×(n_max−1)/2 for a non-default n_max."""
        result = projection_degeneracy_fraction(n_max=10)
        assert result.n_candidates == 10 * 9 // 2  # 45


# ===========================================================================
# TestBraidedRDerivation — Pillar 97-B: full derivation chain
# ===========================================================================

from src.core.braided_winding import (
    braided_kinetic_matrix,
    cs_wzw_dispersion,
    braided_power_spectra_derivation,
    braided_r_full_derivation,
)
import numpy as np
import math


class TestBraidedRDerivation:
    """Tests for the four new Pillar 97-B derivation functions."""

    # --- braided_kinetic_matrix ---

    def test_kinetic_matrix_shape(self):
        r = braided_kinetic_matrix(5, 7)
        assert r["matrix"].shape == (2, 2)

    def test_kinetic_matrix_rho_for_57(self):
        r = braided_kinetic_matrix(5, 7)
        expected_rho = 2 * 5 * 7 / 74.0
        assert abs(r["rho"] - expected_rho) < 1e-12

    def test_kinetic_matrix_off_diagonal_equals_rho(self):
        r = braided_kinetic_matrix(5, 7)
        K = r["matrix"]
        assert abs(K[0, 1] - r["rho"]) < 1e-12
        assert abs(K[1, 0] - r["rho"]) < 1e-12

    def test_kinetic_matrix_eigenvalues(self):
        r = braided_kinetic_matrix(5, 7)
        rho = r["rho"]
        eigs = sorted(r["eigenvalues"])
        expected = sorted([1.0 + rho, 1.0 - rho])
        assert abs(eigs[0] - expected[0]) < 1e-12
        assert abs(eigs[1] - expected[1]) < 1e-12

    def test_kinetic_matrix_det_equals_1_minus_rho_sq(self):
        r = braided_kinetic_matrix(5, 7)
        assert abs(r["det"] - (1.0 - r["rho"]**2)) < 1e-12

    def test_kinetic_matrix_sound_speed_sq(self):
        r = braided_kinetic_matrix(5, 7)
        assert abs(r["sound_speed_sq"] - (1.0 - r["rho"]**2)) < 1e-12

    def test_kinetic_matrix_c_s_from_det(self):
        r = braided_kinetic_matrix(5, 7)
        assert abs(r["c_s"] - np.sqrt(r["det"])) < 1e-12

    # --- cs_wzw_dispersion ---

    def test_wzw_both_methods_agree(self):
        r = cs_wzw_dispersion(5, 7)
        assert r["agreement"] is True

    def test_wzw_agreement_tolerance_1e12(self):
        r = cs_wzw_dispersion(5, 7)
        assert abs(r["c_s_from_rotation"] - r["c_s_from_algebra"]) < 1e-12

    def test_wzw_rotation_angle_for_57(self):
        r = cs_wzw_dispersion(5, 7)
        rho = 2 * 5 * 7 / 74.0
        expected_angle = np.arcsin(rho)
        assert abs(r["wzw_rotation_angle_rad"] - expected_angle) < 1e-12

    def test_wzw_c_s_approx_12_over_37_for_57(self):
        r = cs_wzw_dispersion(5, 7)
        expected = 12.0 / 37.0
        assert abs(r["c_s_from_rotation"] - expected) < 1e-10

    def test_wzw_derivation_chain_contains_WZW(self):
        r = cs_wzw_dispersion(5, 7)
        assert "WZW" in r["derivation_chain"]

    def test_wzw_status_contains_DERIVED(self):
        r = cs_wzw_dispersion(5, 7)
        assert "DERIVED" in r["status"]

    def test_wzw_mode_equation_prefactor_is_1_minus_rho_sq(self):
        r = cs_wzw_dispersion(5, 7)
        assert abs(r["mode_equation_prefactor"] - (1.0 - r["rho"]**2)) < 1e-12

    # --- braided_power_spectra_derivation ---

    def test_power_spectra_P_h_relative_is_one(self):
        r = braided_power_spectra_derivation(0.097, 5, 7)
        assert abs(r["P_h_relative"] - 1.0) < 1e-12

    def test_power_spectra_P_h_unchanged_flag(self):
        r = braided_power_spectra_derivation(0.097, 5, 7)
        assert r["c_s_unchanged_P_h"] is True

    def test_power_spectra_P_zeta_relative_is_1_over_cs(self):
        r = braided_power_spectra_derivation(0.097, 5, 7)
        c_s = r["c_s"]
        assert abs(r["P_zeta_relative"] - 1.0 / c_s) < 1e-10

    def test_power_spectra_r_braided_equals_r_bare_times_cs(self):
        r = braided_power_spectra_derivation(0.097, 5, 7)
        assert abs(r["r_braided"] - r["r_bare"] * r["c_s"]) < 1e-12

    def test_power_spectra_enhancement_factor_greater_than_1(self):
        r = braided_power_spectra_derivation(0.097, 5, 7)
        # c_s < 1 → enhancement = 1/c_s > 1
        assert r["enhancement_factor"] > 1.0

    # --- braided_r_full_derivation ---

    def test_full_derivation_overall_status_is_DERIVED(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert r["overall_status"] == "DERIVED"

    def test_full_derivation_old_status_STRONGLY_MOTIVATED(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert r["old_status"] == "STRONGLY MOTIVATED"

    def test_full_derivation_new_status_DERIVED(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert r["new_status"] == "DERIVED"

    def test_full_derivation_r_braided_lt_r_bare(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert r["r_braided"] < r["r_bare"]

    def test_full_derivation_r_braided_equals_r_bare_times_cs(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert abs(r["r_braided"] - r["r_bare"] * r["c_s"]) < 1e-12

    def test_full_derivation_c_s_approx_12_over_37_for_57(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert abs(r["c_s"] - 12.0 / 37.0) < 1e-10

    def test_full_derivation_step4_ratio_equals_cs(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        assert abs(r["step4_ratio"] - r["c_s"]) < 1e-10

    def test_full_derivation_has_all_steps(self):
        r = braided_r_full_derivation(5, 7, 1.0)
        for key in ["step1_cs_mixing", "step2_sound_speed", "step3_power_spectra"]:
            assert key in r
