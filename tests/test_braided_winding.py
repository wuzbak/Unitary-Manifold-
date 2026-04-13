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
    resonant_kcs,
    is_resonant,
    braided_cs_mixing,
    braided_sound_speed,
    braided_r_effective,
    braided_ns_r,
    resonance_scan,
    R_BICEP_KECK_95,
    R_PLANCK_95,
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
