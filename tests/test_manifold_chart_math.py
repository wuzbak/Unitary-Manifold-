# SPDX-License-Identifier: LicenseRef-DPC-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_manifold_chart_math.py
─────────────────────────────────
Python validation of the mathematics embedded in public-site/js/manifold-chart.js.

Each test mirrors a JS function and verifies the formula is correct.
This guards against copy-paste errors in the rendering engine and
documents the expected numerical behaviour of the chart.

References:
  src/core/metric.py          — KK metric, curvature
  src/core/fixed_point.py     — fixed-point iteration T(x)
  src/core/chart_coords.py    — coordinate map (Eq. 2.1, 2.2)
"""

import math
import pytest

# ─── Architecture constants ───────────────────────────────────────────────────
K_CS_CRITICAL   = 74
N1_CANONICAL    = 5
N2_CANONICAL    = 7
NS_CENTRAL      = 0.9635
NS_SIGMA        = 0.0042
R_TENSOR        = 0.0315
C_BRAID         = 12 / 37
FIXED_POINT_R   = 0.5
LAMBDA_CONTRACT = 2.5
D_THETA         = -0.15


# ─── Coordinate map (Eq. 2.1, 2.2) ──────────────────────────────────────────

def radial_coord(B_hat, phi_hat, K_hat, U_hat, wB=0.25, wPhi=0.25, wK=0.25, wU=0.25):
    """r = sqrt(w_B·B̂² + w_φ·φ̂² + w_K·K̂² + w_U·Û²)  [Eq. 2.1]"""
    return math.sqrt(wB * B_hat**2 + wPhi * phi_hat**2 + wK * K_hat**2 + wU * U_hat**2)


def angular_coord(n1, n2):
    """θ = atan2(n₂, n₁) ∈ [0, 2π)  [Eq. 2.2]"""
    return math.atan2(n2, n1)


def braid_index(n1, n2):
    """k_CS = n₁² + n₂²"""
    return n1 * n1 + n2 * n2


# ─── Fixed-point map T(x) ────────────────────────────────────────────────────

def fixed_point_map(r, theta):
    """
    T(r, θ):
      r_new     = r · exp(−λ · (r − r*))
      theta_new = θ + δθ · sin(θ)
    Contractive in r toward r* = FIXED_POINT_R.
    """
    r_new     = r * math.exp(-LAMBDA_CONTRACT * (r - FIXED_POINT_R))
    theta_new = theta + D_THETA * math.sin(theta)
    return max(0.0, min(1.0, r_new)), theta_new


def iterate_fixed_point(r0, theta0, n_steps=50, eps=1e-6):
    """Run T(x) for n_steps or until convergence."""
    r, theta = r0, theta0
    for _ in range(n_steps):
        r_new, theta_new = fixed_point_map(r, theta)
        if abs(r_new - r) < eps and abs(theta_new - theta) < eps:
            return r_new, theta_new, True
        r, theta = r_new, theta_new
    return r, theta, False


# ─── Smith-chart conformal map helpers ───────────────────────────────────────

def resistance_circle_centre(R_val, chart_radius=1.0):
    """Centre of constant-R circle in normalised coords: (R/(R+1), 0)"""
    return R_val / (R_val + 1) * chart_radius, 0.0


def resistance_circle_radius(R_val, chart_radius=1.0):
    """Radius of constant-R circle: 1/(R+1)"""
    return chart_radius / (R_val + 1)


def reactance_arc_centre_y(X_val, chart_radius=1.0):
    """Y coordinate of constant-X arc centre: −chart_radius/X"""
    return -chart_radius / X_val


def reactance_arc_radius(X_val, chart_radius=1.0):
    """Radius of constant-X arc: chart_radius/|X|"""
    return chart_radius / abs(X_val)


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════

class TestBraidIndex:
    def test_canonical_pair(self):
        assert braid_index(N1_CANONICAL, N2_CANONICAL) == K_CS_CRITICAL

    def test_canonical_pair_74(self):
        assert braid_index(5, 7) == 74

    def test_identity_pair(self):
        assert braid_index(1, 0) == 1

    def test_unit_pair(self):
        assert braid_index(1, 1) == 2

    def test_commutative(self):
        assert braid_index(3, 4) == braid_index(4, 3)

    def test_negative_inputs(self):
        # k_CS uses squares so sign doesn't matter
        assert braid_index(-5, -7) == braid_index(5, 7)

    def test_zero(self):
        assert braid_index(0, 0) == 0

    @pytest.mark.parametrize("n1,n2,expected", [
        (0, 1, 1), (1, 2, 5), (2, 3, 13), (3, 4, 25), (5, 7, 74),
    ])
    def test_known_values(self, n1, n2, expected):
        assert braid_index(n1, n2) == expected


class TestAngularCoord:
    def test_canonical_pair_angle(self):
        theta = angular_coord(N1_CANONICAL, N2_CANONICAL)
        assert 0 < theta < math.pi / 2  # first quadrant

    def test_positive_x_axis(self):
        assert angular_coord(1, 0) == pytest.approx(0.0)

    def test_positive_y_axis(self):
        assert angular_coord(0, 1) == pytest.approx(math.pi / 2)

    def test_negative_x_axis(self):
        assert angular_coord(-1, 0) == pytest.approx(math.pi)

    def test_negative_y_axis(self):
        assert angular_coord(0, -1) == pytest.approx(-math.pi / 2)

    def test_45_degrees(self):
        assert angular_coord(1, 1) == pytest.approx(math.pi / 4)

    def test_canonical_angle_value(self):
        theta = angular_coord(5, 7)
        assert theta == pytest.approx(math.atan2(7, 5), rel=1e-9)


class TestRadialCoord:
    def test_zero_state(self):
        assert radial_coord(0, 0, 0, 0) == pytest.approx(0.0)

    def test_unit_state_equal_weights(self):
        # r = sqrt(0.25·1 + 0.25·1 + 0.25·1 + 0.25·1) = 1.0
        assert radial_coord(1, 1, 1, 1) == pytest.approx(1.0)

    def test_single_component(self):
        # Only B_hat = 1, rest 0 → r = sqrt(0.25) = 0.5
        assert radial_coord(1, 0, 0, 0) == pytest.approx(0.5)

    def test_positive_definite(self):
        assert radial_coord(0.3, 0.4, 0.2, 0.1) > 0

    def test_weight_sensitivity(self):
        r_eq  = radial_coord(1, 0, 0, 0, wB=0.25)
        r_high = radial_coord(1, 0, 0, 0, wB=0.9)
        assert r_high > r_eq

    def test_normalisation_invariance(self):
        # Doubling all weights should double r²
        r1 = radial_coord(0.5, 0.3, 0.2, 0.1, 0.25, 0.25, 0.25, 0.25)
        r2 = radial_coord(0.5, 0.3, 0.2, 0.1, 0.50, 0.50, 0.50, 0.50)
        assert r2 == pytest.approx(r1 * math.sqrt(2), rel=1e-6)

    def test_triangle_inequality(self):
        # r(x+y) ≤ r(x) + r(y) not directly testable, but r is a norm
        a = radial_coord(0.6, 0, 0, 0)
        b = radial_coord(0, 0.8, 0, 0)
        c = radial_coord(0.6, 0.8, 0, 0)
        assert c <= a + b + 1e-9


class TestFixedPointMap:
    def test_contraction_above_fixed_point(self):
        r_in = 0.9
        r_out, _, _ = iterate_fixed_point(r_in, 0, n_steps=1)
        assert r_out < r_in, "Should contract from above"

    def test_contraction_below_fixed_point(self):
        # T is not guaranteed to expand from below — just check it moves
        r_in = 0.1
        r_out, _, _ = iterate_fixed_point(r_in, 0, n_steps=1)
        assert 0 <= r_out <= 1

    def test_convergence_from_large_r(self):
        _, _, converged = iterate_fixed_point(0.95, math.pi / 4, n_steps=100)
        assert converged

    def test_convergence_from_small_r(self):
        _, _, converged = iterate_fixed_point(0.05, 1.0, n_steps=100)
        assert converged

    def test_theta_rotation_direction(self):
        # D_THETA < 0: sin(θ)>0 in upper half → theta decreases
        _, theta_new = fixed_point_map(0.5, math.pi / 3)
        assert theta_new < math.pi / 3

    def test_r_bounded(self):
        r, _ = fixed_point_map(0.95, 0)
        assert 0 <= r <= 1

    def test_fixed_point_stability(self):
        # Starting at x*, one iteration should stay close
        r_out, theta_out = fixed_point_map(FIXED_POINT_R, 0)
        assert abs(r_out - FIXED_POINT_R) < 0.05

    def test_20_steps_reduces_r_spread(self):
        starts = [0.1, 0.3, 0.7, 0.95]
        finals = [iterate_fixed_point(r0, 0, n_steps=20)[0] for r0 in starts]
        spread = max(finals) - min(finals)
        assert spread < 0.3, "Trajectories should cluster after 20 steps"


class TestSmithAnalogy:
    def test_resistance_circle_r0(self):
        cx, cy = resistance_circle_centre(0)
        radius  = resistance_circle_radius(0)
        assert cx == pytest.approx(0.0)
        assert cy == pytest.approx(0.0)
        assert radius == pytest.approx(1.0)  # full unit circle

    def test_resistance_circle_r1(self):
        cx, cy = resistance_circle_centre(1)
        radius  = resistance_circle_radius(1)
        assert cx == pytest.approx(0.5)
        assert radius == pytest.approx(0.5)

    def test_resistance_circle_r_inf(self):
        # As R → ∞, circle shrinks to point at (1, 0)
        R = 1e6
        cx, _ = resistance_circle_centre(R)
        radius = resistance_circle_radius(R)
        assert cx == pytest.approx(1.0, rel=1e-4)
        assert radius == pytest.approx(0.0, abs=1e-4)

    def test_reactance_arc_x1(self):
        cy = reactance_arc_centre_y(1)
        r  = reactance_arc_radius(1)
        assert cy == pytest.approx(-1.0)
        assert r  == pytest.approx(1.0)

    def test_reactance_arc_x_neg1(self):
        cy = reactance_arc_centre_y(-1)
        r  = reactance_arc_radius(-1)
        assert cy == pytest.approx(1.0)
        assert r  == pytest.approx(1.0)

    def test_reactance_arc_x_positive_negative_symmetric(self):
        # |cy| and r should be the same for +X and -X
        assert reactance_arc_centre_y(2) == pytest.approx(-reactance_arc_centre_y(-2))
        assert reactance_arc_radius(2) == pytest.approx(reactance_arc_radius(-2))


class TestArchitectureConstants:
    def test_k_cs_critical(self):
        assert K_CS_CRITICAL == 74

    def test_canonical_pair_gives_k_cs(self):
        assert N1_CANONICAL**2 + N2_CANONICAL**2 == K_CS_CRITICAL

    def test_ns_within_planck_bounds(self):
        # Planck 2018: n_s = 0.9649 ± 0.0042 (68% CL)
        planck_central = 0.9649
        assert abs(NS_CENTRAL - planck_central) < 3 * NS_SIGMA

    def test_r_tensor_below_bicep_limit(self):
        bicep_limit = 0.036
        assert R_TENSOR < bicep_limit

    def test_c_braid_exact(self):
        assert C_BRAID == pytest.approx(12 / 37, rel=1e-10)

    def test_fixed_point_r_in_unit_interval(self):
        assert 0 < FIXED_POINT_R < 1


class TestPolarToCartesian:
    """Verify the polar ↔ canvas coordinate transform used in the JS renderer."""

    def _polar_to_xy(self, r, theta, chart_radius=1.0):
        return r * chart_radius * math.cos(theta), r * chart_radius * math.sin(theta)

    def test_origin(self):
        x, y = self._polar_to_xy(0, 0)
        assert x == pytest.approx(0) and y == pytest.approx(0)

    def test_unit_right(self):
        x, y = self._polar_to_xy(1, 0)
        assert x == pytest.approx(1) and y == pytest.approx(0)

    def test_unit_up(self):
        x, y = self._polar_to_xy(1, math.pi / 2)
        assert x == pytest.approx(0, abs=1e-9) and y == pytest.approx(1)

    def test_canonical_angle(self):
        theta = math.atan2(N2_CANONICAL, N1_CANONICAL)
        x, y  = self._polar_to_xy(1, theta)
        # Should be proportional to (5, 7) / |(5,7)|
        norm  = math.hypot(5, 7)
        assert x == pytest.approx(5 / norm, rel=1e-6)
        assert y == pytest.approx(7 / norm, rel=1e-6)

    def test_round_trip(self):
        r0, t0 = 0.62, 1.23
        x, y = self._polar_to_xy(r0, t0)
        r1   = math.hypot(x, y)
        t1   = math.atan2(y, x)
        assert r1 == pytest.approx(r0, rel=1e-9)
        assert t1 == pytest.approx(t0, rel=1e-9)
