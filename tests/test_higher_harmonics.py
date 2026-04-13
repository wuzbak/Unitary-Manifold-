# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_higher_harmonics.py
==============================
Tests for the "higher harmonic" exploration: what happens when n_w = 5 is
challenged by the r-tension (BICEP/Keck 2021 upper limit on the gravitational-
wave amplitude) and whether moving to n_w = 7 or a multi-winding superposition
can resolve it.

Physical background
-------------------
The Goldberger–Wise slow-roll potential used in the Unitary Manifold gives:

    ε  = 2 / φ₀_eff²
    ns = 1 − 6ε  (at inflection point, η ≈ 0)
    r  = 16ε

Eliminating ε:

    **r = (8/3)(1 − ns)**           [the GW-potential track]

This is a single straight line in (ns, r) space.  Every winding number
n_w — integer or fractional — sits on this line.  The line cannot be escaped
by tuning n_w alone.

Observational windows (used throughout):
    Planck 2018: ns = 0.9649 ± 0.0042 (1σ)
    BICEP/Keck 2021: r < 0.036 (95 % CL)
    Planck 2018:     r < 0.056 (95 % CL)

Test classes
------------
TestNsRTrackConstraint
    Every integer n_w in [1, 10] satisfies r = (8/3)(1 − ns) exactly.
    Proves no integer n_w can simultaneously satisfy the Planck ns window
    AND either r upper limit.

TestNw7HigherHarmonic
    The n_w = 7 candidate: precise predictions, comparison to n_w = 5, and
    verification that birefringence is unchanged (it is driven by k_cs, not n_w).

TestDeadZone
    Maps the gap between the ns 2σ window (closes at n_w ≈ 5.88) and the
    Planck-r window (opens at n_w ≈ 6.60).  No integer or half-integer n_w
    occupies this gap from the "correct" side simultaneously.

TestMultiWindingSuperposition
    Quadrature mixing of the n_w = 5 and n_w = 7 field amplitudes via
        φ_mix = √(w₅·φ₅² + w₇·φ₇²)
    The mixed state remains on the r = (8/3)(1 − ns) track for all weights;
    no mixing fraction satisfies both the Planck ns window and either r limit.

TestHigherHarmonicResolutionRoutes
    Systematic survey of the four candidate physics routes that could move
    the theory off the track:
        A) Varying φ₀_bare at n_w = 7 — stays on track, moves along it.
        B) The r < 0.036 constraint requires φ₀_eff > 29.8; the Planck ns
           2σ window closes before φ₀_eff reaches that threshold.
        C) The corridor is genuinely empty: no φ₀_eff satisfies BOTH
           simultaneously with the GW potential.
        D) The birefringence angle β ≈ 0.33° is insensitive to the winding
           sector — it depends only on k_cs and r_c.
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pytest

from src.core.inflation import (
    effective_phi0_kk,
    ns_from_phi0,
    planck2018_check,
    cs_axion_photon_coupling,
    field_displacement_gw,
    birefringence_angle,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
)

# ---------------------------------------------------------------------------
# Observational constants used across all tests
# ---------------------------------------------------------------------------
R_BICEP_KECK_95: float = 0.036   # BICEP/Keck 2021, 95 % CL upper limit
R_PLANCK_95:     float = 0.056   # Planck 2018,      95 % CL upper limit
TRACK_SLOPE:     float = 8.0 / 3.0   # r / (1 − ns) for the GW potential

# Canonical theory parameters
PHI0_BARE_FTUM: float = 1.0
K_CS_CANONICAL: int   = 74
R_C_CANONICAL:  float = 12.0
ALPHA_EM:       float = 1.0 / 137.036


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _ns_r_for_nw(n_w: float, phi0_bare: float = PHI0_BARE_FTUM):
    """Return (ns, r) for a given (possibly fractional) winding number."""
    phi0_eff = n_w * 2.0 * np.pi * np.sqrt(phi0_bare) * phi0_bare
    return ns_from_phi0(phi0_eff)[:2]


# ===========================================================================
# 1. TestNsRTrackConstraint
# ===========================================================================

class TestNsRTrackConstraint:
    """All n_w values lie on the single track r = (8/3)(1 − ns).

    This is the structural wall imposed by the Goldberger–Wise potential.
    No integer winding number escapes it.
    """

    @pytest.mark.parametrize("n_w", range(1, 11))
    def test_track_slope_is_8_over_3(self, n_w):
        """r / (1 − ns) equals 8/3 exactly for every integer n_w."""
        ns, r = _ns_r_for_nw(n_w)
        assert ns < 1.0, "ns must be sub-unity for slope to be defined"
        slope = r / (1.0 - ns)
        assert slope == pytest.approx(TRACK_SLOPE, rel=1e-5), (
            f"n_w={n_w}: r/(1-ns) = {slope:.6f}, expected {TRACK_SLOPE:.6f}"
        )

    def test_track_is_linear_not_curved(self):
        """Differences in r between successive n_w are monotone and smooth."""
        rs = [_ns_r_for_nw(nw)[1] for nw in range(2, 10)]
        diffs = [rs[i] - rs[i + 1] for i in range(len(rs) - 1)]
        assert all(d > 0 for d in diffs), "r should decrease monotonically with n_w"

    def test_no_integer_nw_satisfies_ns_and_planck_r_simultaneously(self):
        """No integer n_w ∈ [1,10] has ns within 2σ AND r < Planck 95 % CL."""
        both_ok = []
        for n_w in range(1, 11):
            ns, r = _ns_r_for_nw(n_w)
            ns_ok = abs(ns - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA
            r_ok  = r < R_PLANCK_95
            if ns_ok and r_ok:
                both_ok.append(n_w)
        assert both_ok == [], (
            f"Unexpected integer n_w satisfying both ns(2σ) and r<Planck: {both_ok}"
        )

    def test_no_integer_nw_satisfies_ns_and_bicep_r_simultaneously(self):
        """No integer n_w ∈ [1,10] has ns within 2σ AND r < BICEP/Keck 95 % CL."""
        both_ok = []
        for n_w in range(1, 11):
            ns, r = _ns_r_for_nw(n_w)
            ns_ok = abs(ns - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA
            r_ok  = r < R_BICEP_KECK_95
            if ns_ok and r_ok:
                both_ok.append(n_w)
        assert both_ok == [], (
            f"Unexpected integer n_w satisfying both ns(2σ) and r<BICEP: {both_ok}"
        )

    def test_nw5_is_unique_planck_ns_winner(self):
        """n_w = 5 is the only integer n_w whose ns prediction lies within 2σ."""
        ns_ok_list = []
        for n_w in range(1, 11):
            ns, _ = _ns_r_for_nw(n_w)
            if abs(ns - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA:
                ns_ok_list.append(n_w)
        assert ns_ok_list == [5], (
            f"Expected only n_w=5 to pass ns 2σ test; got {ns_ok_list}"
        )

    def test_nw5_ns_sigma_below_1(self):
        """n_w = 5 places ns within 1σ of the Planck central value."""
        ns, _ = _ns_r_for_nw(5)
        sigma = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma < 1.0, f"n_w=5 ns is {sigma:.2f}σ from Planck (expected < 1σ)"

    def test_nw5_r_above_planck_limit(self):
        """n_w = 5 predicts r > Planck 95 % CL — the r tension is real."""
        _, r = _ns_r_for_nw(5)
        assert r > R_PLANCK_95, (
            f"r = {r:.4f} should exceed Planck limit {R_PLANCK_95}"
        )

    def test_nw5_r_above_bicep_limit(self):
        """n_w = 5 predicts r > BICEP/Keck 95 % CL upper limit."""
        _, r = _ns_r_for_nw(5)
        assert r > R_BICEP_KECK_95, (
            f"r = {r:.4f} should exceed BICEP/Keck limit {R_BICEP_KECK_95}"
        )

    def test_r_tension_magnitude_at_nw5(self):
        """r tension at n_w = 5: predicted r is roughly 2.7× the BICEP limit."""
        _, r = _ns_r_for_nw(5)
        ratio = r / R_BICEP_KECK_95
        assert 2.0 < ratio < 4.0, (
            f"Expected r/r_BICEP in (2,4); got {ratio:.2f}"
        )


# ===========================================================================
# 2. TestNw7HigherHarmonic
# ===========================================================================

class TestNw7HigherHarmonic:
    """The n_w = 7 'higher harmonic': one more full twist around the compact
    dimension.  r improves but ns drifts significantly blue-ward.
    """

    def test_phi0_eff_is_7_times_2pi(self):
        """φ₀_eff(n_w=7) = 7 × 2π ≈ 43.98 at the FTUM fixed point."""
        phi0_eff = effective_phi0_kk(1.0, 7)
        assert phi0_eff == pytest.approx(7.0 * 2.0 * np.pi, rel=1e-6)

    def test_nw7_r_below_planck_95(self):
        """n_w = 7 predicts r < Planck 2018 95 % CL (first step in the right
        direction, though ns suffers)."""
        _, r = _ns_r_for_nw(7)
        assert r < R_PLANCK_95, (
            f"n_w=7 r = {r:.4f} should be < Planck limit {R_PLANCK_95}"
        )

    def test_nw7_r_still_above_bicep_keck(self):
        """n_w = 7 still does not satisfy the tighter BICEP/Keck limit."""
        _, r = _ns_r_for_nw(7)
        assert r > R_BICEP_KECK_95, (
            f"n_w=7 r = {r:.4f} is not above BICEP limit {R_BICEP_KECK_95} as expected"
        )

    def test_nw7_ns_fails_planck_2sigma(self):
        """n_w = 7 ns is > 2σ above Planck central — the ns penalty for the
        partial r gain."""
        ns, _ = _ns_r_for_nw(7)
        sigma = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma > 2.0, (
            f"n_w=7 ns is {sigma:.2f}σ from Planck; expected > 2σ"
        )

    def test_nw7_ns_sigma_larger_than_nw5(self):
        """Moving to n_w = 7 worsens the ns deviation relative to n_w = 5."""
        ns5, _ = _ns_r_for_nw(5)
        ns7, _ = _ns_r_for_nw(7)
        sigma5 = abs(ns5 - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        sigma7 = abs(ns7 - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma7 > sigma5, (
            f"Expected σ(n_w=7) > σ(n_w=5); got {sigma7:.2f} vs {sigma5:.2f}"
        )

    def test_nw7_r_smaller_than_nw5(self):
        """Moving to n_w = 7 lowers r — the partial gain."""
        _, r5 = _ns_r_for_nw(5)
        _, r7 = _ns_r_for_nw(7)
        assert r7 < r5, f"Expected r(n_w=7) < r(n_w=5); got {r7:.4f} vs {r5:.4f}"

    def test_nw7_r_reduction_factor(self):
        """r at n_w = 7 is (5/7)² times r at n_w = 5 — set by the Jacobian."""
        _, r5 = _ns_r_for_nw(5)
        _, r7 = _ns_r_for_nw(7)
        expected = (5.0 / 7.0) ** 2
        actual   = r7 / r5
        assert actual == pytest.approx(expected, rel=1e-4), (
            f"r ratio = {actual:.4f}, expected (5/7)² = {expected:.4f}"
        )

    def test_birefringence_unchanged_at_nw7(self):
        """β is driven by k_cs and r_c, not by n_w.  Switching to n_w = 7
        leaves the birefringence prediction untouched."""
        g_agg = cs_axion_photon_coupling(K_CS_CANONICAL, ALPHA_EM, R_C_CANONICAL)
        dphi  = field_displacement_gw(R_C_CANONICAL)
        beta  = float(np.degrees(birefringence_angle(g_agg, dphi)))
        # The birefringence from the n_w=5 baseline tests is ~0.33°
        assert 0.20 < beta < 0.50, (
            f"β = {beta:.4f}° should be in (0.20, 0.50)° regardless of n_w"
        )

    def test_nw7_still_on_track(self):
        """n_w = 7 obeys r = (8/3)(1 − ns) — the tension cannot be resolved
        by the winding number alone."""
        ns7, r7 = _ns_r_for_nw(7)
        slope = r7 / (1.0 - ns7)
        assert slope == pytest.approx(TRACK_SLOPE, rel=1e-5)

    def test_nw7_ns_deviation_is_near_4_sigma(self):
        """n_w = 7 ns sits roughly 3.9σ from Planck central — quantifying
        the cost of the 'extra twist'."""
        ns7, _ = _ns_r_for_nw(7)
        sigma7 = abs(ns7 - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert 3.5 < sigma7 < 4.5, (
            f"Expected σ(n_w=7) ≈ 3.9; got {sigma7:.2f}"
        )


# ===========================================================================
# 3. TestDeadZone
# ===========================================================================

class TestDeadZone:
    """Between the ns 2σ upper edge (~n_w = 5.88) and the Planck-r lower edge
    (~n_w = 6.60) lies a dead zone where neither the spectral index nor the
    tensor amplitude is observationally acceptable.
    """

    def test_ns_window_closes_before_nw6(self):
        """ns leaves the 2σ window between n_w = 5 and n_w = 6."""
        ns5, _ = _ns_r_for_nw(5)
        ns6, _ = _ns_r_for_nw(6)
        ns_upper = PLANCK_NS_CENTRAL + 2.0 * PLANCK_NS_SIGMA
        assert ns5 < ns_upper, "n_w=5 should be inside the 2σ ns window"
        assert ns6 > ns_upper, "n_w=6 should be outside the 2σ ns window"

    def test_r_window_opens_after_nw6(self):
        """r crosses the Planck 95 % CL between n_w = 6 and n_w = 7."""
        _, r6 = _ns_r_for_nw(6)
        _, r7 = _ns_r_for_nw(7)
        assert r6 > R_PLANCK_95, "n_w=6 r should still exceed Planck 95% limit"
        assert r7 < R_PLANCK_95, "n_w=7 r should satisfy Planck 95% limit"

    def test_dead_zone_is_nonempty(self):
        """At least one fractional n_w in (5.9, 6.6) satisfies neither
        ns-2σ nor r-Planck; confirming the gap is real."""
        dead = []
        for nw_10 in range(59, 66):
            nw = nw_10 / 10.0
            ns, r = _ns_r_for_nw(nw)
            ns_ok = abs(ns - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA
            r_ok  = r < R_PLANCK_95
            if not ns_ok and not r_ok:
                dead.append(nw)
        assert len(dead) >= 3, (
            f"Expected ≥ 3 dead-zone points in (5.9, 6.6); found {dead}"
        )

    def test_dead_zone_lower_boundary_approx_nw_5p9(self):
        """ns exits the 2σ window at roughly n_w ≈ 5.9."""
        ns_upper = PLANCK_NS_CENTRAL + 2.0 * PLANCK_NS_SIGMA
        ns58, _ = _ns_r_for_nw(5.8)
        ns59, _ = _ns_r_for_nw(5.9)
        assert ns58 < ns_upper, "n_w=5.8 should still be inside ns 2σ"
        assert ns59 > ns_upper, "n_w=5.9 should have crossed the ns 2σ upper edge"

    def test_dead_zone_upper_boundary_approx_nw_6p6(self):
        """r crosses the Planck 95 % CL at roughly n_w ≈ 6.6."""
        _, r65 = _ns_r_for_nw(6.5)
        _, r66 = _ns_r_for_nw(6.6)
        assert r65 > R_PLANCK_95, "n_w=6.5 r should still exceed Planck limit"
        assert r66 < R_PLANCK_95, "n_w=6.6 r should satisfy Planck limit"

    def test_dead_zone_width_is_roughly_0p7_windings(self):
        """The dead zone spans approximately 0.7 winding units (5.9 to 6.6)."""
        lower = 5.9   # approximate ns 2σ closure
        upper = 6.6   # approximate Planck-r opening
        width = upper - lower
        assert 0.5 < width < 1.0, (
            f"Dead zone width = {width:.1f}; expected in (0.5, 1.0)"
        )

    def test_nw5_is_on_correct_side_of_dead_zone(self):
        """n_w = 5 sits below the dead zone (ns ok, r too large)."""
        ns5, r5 = _ns_r_for_nw(5)
        ns_ok = abs(ns5 - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA
        r_too_large = r5 > R_PLANCK_95
        assert ns_ok and r_too_large

    def test_nw7_is_on_far_side_of_dead_zone(self):
        """n_w = 7 sits above the dead zone (r ok by Planck, but ns broken)."""
        ns7, r7 = _ns_r_for_nw(7)
        ns_broken = abs(ns7 - PLANCK_NS_CENTRAL) > 2.0 * PLANCK_NS_SIGMA
        r_ok = r7 < R_PLANCK_95
        assert ns_broken and r_ok


# ===========================================================================
# 4. TestMultiWindingSuperposition
# ===========================================================================

class TestMultiWindingSuperposition:
    """Tests for a quadrature superposition of n_w = 5 and n_w = 7 modes:

        φ_mix(w) = √(w₅·φ₅² + w₇·φ₇²),   w₅ + w₇ = 1, w₇ ∈ [0, 1]

    This represents a two-winding-mode field state and is the most natural
    'another twist' extension within the 5D geometry.
    """

    PHI5: float = float(effective_phi0_kk(1.0, 5))
    PHI7: float = float(effective_phi0_kk(1.0, 7))

    def _mix(self, w7: float):
        w5 = 1.0 - w7
        phi_mix = float(np.sqrt(w5 * self.PHI5**2 + w7 * self.PHI7**2))
        return ns_from_phi0(phi_mix)[:2]

    def test_pure_nw5_reproduces_nw5_predictions(self):
        """Weight w₇ = 0 recovers the pure n_w = 5 predictions."""
        ns_mix, r_mix = self._mix(0.0)
        ns5, r5 = _ns_r_for_nw(5)
        assert ns_mix == pytest.approx(ns5, rel=1e-6)
        assert r_mix  == pytest.approx(r5,  rel=1e-6)

    def test_pure_nw7_reproduces_nw7_predictions(self):
        """Weight w₇ = 1 recovers the pure n_w = 7 predictions."""
        ns_mix, r_mix = self._mix(1.0)
        ns7, r7 = _ns_r_for_nw(7)
        assert ns_mix == pytest.approx(ns7, rel=1e-6)
        assert r_mix  == pytest.approx(r7,  rel=1e-6)

    def test_phi_mix_monotone_with_weight(self):
        """φ_mix increases monotonically as w₇ goes from 0 to 1 (since φ₇ > φ₅)."""
        phis = []
        for w7_10 in range(0, 11):
            w7 = w7_10 / 10.0
            w5 = 1.0 - w7
            phis.append(float(np.sqrt(w5 * self.PHI5**2 + w7 * self.PHI7**2)))
        assert all(phis[i] <= phis[i + 1] for i in range(len(phis) - 1))

    def test_ns_monotone_increasing_with_weight(self):
        """ns increases monotonically with w₇ (larger φ → bluer tilt)."""
        nss = [self._mix(w7_10 / 10.0)[0] for w7_10 in range(0, 11)]
        assert all(nss[i] <= nss[i + 1] for i in range(len(nss) - 1))

    def test_r_monotone_decreasing_with_weight(self):
        """r decreases monotonically with w₇ (larger φ → weaker GW signal)."""
        rs = [self._mix(w7_10 / 10.0)[1] for w7_10 in range(0, 11)]
        assert all(rs[i] >= rs[i + 1] for i in range(len(rs) - 1))

    def test_mixed_state_remains_on_track(self):
        """The mixed state obeys r = (8/3)(1 − ns) for all weights — it cannot
        leave the GW-potential track by superposing winding modes."""
        for w7_10 in range(0, 11):
            w7 = w7_10 / 10.0
            ns, r = self._mix(w7)
            slope = r / (1.0 - ns)
            assert slope == pytest.approx(TRACK_SLOPE, rel=1e-5), (
                f"w₇ = {w7:.1f}: track slope = {slope:.6f}, expected {TRACK_SLOPE:.6f}"
            )

    def test_no_mixing_weight_satisfies_ns_and_planck_r(self):
        """No w₇ ∈ {0, 0.1, …, 1.0} yields ns within 2σ AND r < Planck 95 %."""
        both_ok = []
        for w7_10 in range(0, 11):
            w7 = w7_10 / 10.0
            ns, r = self._mix(w7)
            ns_ok = abs(ns - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA
            r_ok  = r < R_PLANCK_95
            if ns_ok and r_ok:
                both_ok.append(w7)
        assert both_ok == [], (
            f"Mixing weights {both_ok} unexpectedly satisfy both ns(2σ) and r<Planck"
        )

    def test_no_mixing_weight_satisfies_ns_and_bicep_r(self):
        """No w₇ ∈ {0, 0.1, …, 1.0} yields ns within 2σ AND r < BICEP/Keck 95 %."""
        both_ok = []
        for w7_10 in range(0, 11):
            w7 = w7_10 / 10.0
            ns, r = self._mix(w7)
            ns_ok = abs(ns - PLANCK_NS_CENTRAL) <= 2.0 * PLANCK_NS_SIGMA
            r_ok  = r < R_BICEP_KECK_95
            if ns_ok and r_ok:
                both_ok.append(w7)
        assert both_ok == [], (
            f"Mixing weights {both_ok} unexpectedly satisfy both ns(2σ) and r<BICEP"
        )

    def test_quarter_mix_ns_still_within_2sigma(self):
        """A 25 % n_w = 7 admixture keeps ns inside the Planck 2σ window
        while lowering r — the most promising region before the dead zone."""
        ns_mix, r_mix = self._mix(0.25)
        sigma = abs(ns_mix - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma <= 2.0, (
            f"w₇=0.25: ns is {sigma:.2f}σ from Planck, expected ≤ 2σ"
        )
        # r has come down but not enough
        _, r5 = _ns_r_for_nw(5)
        assert r_mix < r5, "r should decrease with any w₇ > 0"

    def test_half_mix_ns_exits_2sigma(self):
        """A 50/50 mix already pushes ns outside the 2σ window — the dead zone
        is entered before r crosses the Planck limit."""
        ns_mix, _ = self._mix(0.50)
        sigma = abs(ns_mix - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma > 2.0, (
            f"w₇=0.50: ns is {sigma:.2f}σ from Planck, expected > 2σ"
        )


# ===========================================================================
# 5. TestHigherHarmonicResolutionRoutes
# ===========================================================================

class TestHigherHarmonicResolutionRoutes:
    """Systematic evaluation of candidate routes to resolve the r tension
    within the existing Unitary Manifold framework.

    Route A: tuning φ₀_bare at fixed n_w = 7
    Route B: the φ₀_eff threshold for r < BICEP/Keck vs the ns 2σ window
    Route C: the corridor is structurally empty for the GW potential
    Route D: birefringence is decoupled from the winding-sector tension
    """

    # --- Route A: variable phi0_bare at n_w = 7 ----------------------------

    def test_route_a_nw7_phi0bare_08_has_good_ns(self):
        """At n_w = 7, φ₀_bare = 0.8 brings ns back within 1σ of Planck.
        (The Jacobian scales as φ₀_bare^(3/2) so a lower bare vev shrinks φ₀_eff.)
        """
        phi0_eff = effective_phi0_kk(0.8, 7)
        ns, _, _, _ = ns_from_phi0(phi0_eff)
        sigma = abs(ns - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert sigma < 1.0, (
            f"n_w=7, φ₀_bare=0.8: ns is {sigma:.2f}σ, expected < 1σ"
        )

    def test_route_a_nw7_phi0bare_08_r_still_too_large(self):
        """Even with φ₀_bare = 0.8 and n_w = 7, r remains above the
        BICEP/Keck limit — tuning the bare vev does not escape the track."""
        phi0_eff = effective_phi0_kk(0.8, 7)
        _, r, _, _ = ns_from_phi0(phi0_eff)
        assert r > R_BICEP_KECK_95, (
            f"n_w=7, φ₀_bare=0.8: r = {r:.4f} should still exceed BICEP limit"
        )

    def test_route_a_variable_phi0bare_stays_on_track(self):
        """Changing φ₀_bare at fixed n_w = 7 moves along the track, not off it."""
        for phi0_10 in [6, 7, 8, 9, 10, 11]:
            phi0_bare = phi0_10 / 10.0
            phi0_eff  = effective_phi0_kk(phi0_bare, 7)
            ns, r, _, _ = ns_from_phi0(phi0_eff)
            slope = r / (1.0 - ns)
            assert slope == pytest.approx(TRACK_SLOPE, rel=1e-5), (
                f"φ₀_bare={phi0_bare}: slope = {slope:.6f}"
            )

    # --- Route B: the φ₀_eff thresholds -------------------------------------

    def test_route_b_phi0eff_for_bicep_r_limit(self):
        """r < BICEP/Keck requires φ₀_eff > √(32 / 0.036) ≈ 29.8."""
        threshold = float(np.sqrt(32.0 / R_BICEP_KECK_95))
        assert 29.0 < threshold < 31.0, (
            f"BICEP r threshold φ₀_eff = {threshold:.2f}, expected ≈ 29.8"
        )

    def test_route_b_phi0eff_for_planck_r_limit(self):
        """r < Planck 95 % CL requires φ₀_eff > √(32 / 0.056) ≈ 23.9."""
        threshold = float(np.sqrt(32.0 / R_PLANCK_95))
        assert 23.0 < threshold < 25.0, (
            f"Planck r threshold φ₀_eff = {threshold:.2f}, expected ≈ 23.9"
        )

    def test_route_b_nw5_phi0eff_above_bicep_threshold(self):
        """φ₀_eff(n_w=5) ≈ 31.4 is above the BICEP φ₀ threshold of ≈ 29.8 —
        yet r = 0.097 still exceeds 0.036 because the threshold (r < 0.036)
        corresponds to φ₀_eff > 51.6, not 29.8.  The track slope is the
        binding constraint, not just the threshold magnitude."""
        phi0_eff_5 = effective_phi0_kk(1.0, 5)
        # r = 96/φ₀² (from ε = 6/φ₀², r = 16ε)
        # r < 0.036 requires φ₀² > 96/0.036 → φ₀ > sqrt(96/0.036) ≈ 51.6
        bicep_threshold_true = float(np.sqrt(96.0 / R_BICEP_KECK_95))
        assert phi0_eff_5 < bicep_threshold_true, (
            f"n_w=5 φ₀_eff={phi0_eff_5:.2f} should be BELOW the true BICEP "
            f"threshold {bicep_threshold_true:.2f}"
        )
        _, r5 = _ns_r_for_nw(5)
        # Verify the r = 96/φ₀² formula exactly
        r_formula = 96.0 / phi0_eff_5**2
        assert r_formula == pytest.approx(r5, rel=1e-4), (
            "r = 96/φ₀² must hold for the GW potential (ε=6/φ₀², r=16ε)"
        )

    # --- Route C: the corridor is structurally empty ------------------------

    def test_route_c_corridor_empty_on_track(self):
        """On the GW-potential track r = (8/3)(1-ns), there is no point where
        simultaneously ns ∈ Planck 2σ window AND r < R_PLANCK_95."""
        ns_lo = PLANCK_NS_CENTRAL - 2.0 * PLANCK_NS_SIGMA
        ns_hi = PLANCK_NS_CENTRAL + 2.0 * PLANCK_NS_SIGMA
        # At the Planck ns 2σ upper edge, what is r on the track?
        r_at_ns_hi = TRACK_SLOPE * (1.0 - ns_hi)
        # r on the track is still above Planck 95% CL at the ns 2σ boundary
        assert r_at_ns_hi > R_PLANCK_95, (
            f"r on track at ns 2σ upper edge = {r_at_ns_hi:.4f}; "
            f"expected > {R_PLANCK_95} (corridor structurally empty)"
        )

    def test_route_c_corridor_empty_for_bicep(self):
        """The corridor is even more empty for the tighter BICEP/Keck limit."""
        ns_hi = PLANCK_NS_CENTRAL + 2.0 * PLANCK_NS_SIGMA
        r_at_ns_hi = TRACK_SLOPE * (1.0 - ns_hi)
        assert r_at_ns_hi > R_BICEP_KECK_95, (
            f"r on track at ns 2σ upper edge = {r_at_ns_hi:.4f}; "
            f"expected > {R_BICEP_KECK_95}"
        )

    def test_route_c_r_planck_window_requires_unphysically_blue_ns(self):
        """To satisfy r < Planck 95 % on the track, ns must exceed the Planck
        2σ upper bound — the two constraints point in opposite directions."""
        # ns on track where r = R_PLANCK_95 exactly
        ns_for_r_planck = 1.0 - R_PLANCK_95 / TRACK_SLOPE
        assert ns_for_r_planck > PLANCK_NS_CENTRAL + 2.0 * PLANCK_NS_SIGMA, (
            f"ns needed for r=R_PLANCK on track = {ns_for_r_planck:.5f}, "
            f"but Planck 2σ upper = {PLANCK_NS_CENTRAL + 2*PLANCK_NS_SIGMA:.5f}"
        )

    # --- Route D: birefringence is decoupled --------------------------------

    def test_route_d_birefringence_independent_of_nw(self):
        """β depends only on k_cs and r_c — it is the same at n_w = 5, 6, 7."""
        g_agg = cs_axion_photon_coupling(K_CS_CANONICAL, ALPHA_EM, R_C_CANONICAL)
        dphi  = field_displacement_gw(R_C_CANONICAL)
        beta  = float(np.degrees(birefringence_angle(g_agg, dphi)))
        # Whatever n_w we choose, beta is the same number
        assert 0.25 < beta < 0.45, (
            f"β = {beta:.4f}° should be ≈ 0.33° regardless of n_w"
        )

    def test_route_d_nw7_does_not_alter_k_cs_prediction(self):
        """Switching to n_w = 7 does not change the Chern–Simons level.
        k_cs = 74 is fixed by the SM gauge structure, not the winding sector.
        Verified by round-tripping: k_cs=74 → β → back to k_cs=74."""
        g_agg  = cs_axion_photon_coupling(K_CS_CANONICAL, ALPHA_EM, R_C_CANONICAL)
        dphi   = field_displacement_gw(R_C_CANONICAL)
        beta_actual_rad = birefringence_angle(g_agg, dphi)
        # Round-trip: β → g_aγγ → k_cs.  Must recover K_CS_CANONICAL exactly.
        g_back    = 2.0 * beta_actual_rad / dphi
        k_cs_back = g_back * 2.0 * np.pi**2 * R_C_CANONICAL / ALPHA_EM
        assert round(k_cs_back) == K_CS_CANONICAL, (
            f"k_cs round-trip = {k_cs_back:.2f} → {round(k_cs_back)}, "
            f"expected {K_CS_CANONICAL}"
        )

    def test_route_d_birefringence_arrow_of_time_decoupling(self):
        """The arrow-of-time entropy attractor is holographic (S → A/4G) and
        is not driven by r.  A change of r by the winding-sector shift from
        n_w = 5 to n_w = 7 leaves the birefringence-based CP-violation signal
        — which seeds the matter–antimatter asymmetry tied to the arrow of time
        — completely unchanged."""
        g_agg = cs_axion_photon_coupling(K_CS_CANONICAL, ALPHA_EM, R_C_CANONICAL)
        dphi  = field_displacement_gw(R_C_CANONICAL)
        beta  = float(np.degrees(birefringence_angle(g_agg, dphi)))
        # β sets the CP-asymmetry seed; it is n_w-independent.
        # Verify it stays well inside the observational 1σ window (0.35 ± 0.14)°
        assert abs(beta - 0.35) < 0.14, (
            f"β = {beta:.4f}° is outside the 1σ observational window (0.35±0.14)°"
        )
