"""
tests/test_metric.py
====================
Unit tests for src/core/metric.py.

Covers:
  - field_strength: antisymmetry, zero on constant B
  - assemble_5d_metric: G_55=φ², off-diagonals, 4×4 block, symmetry
  - christoffel: shape, vanishes on flat metric (D=4 and D=5)
  - compute_curvature: shapes, R≈0 on flat Minkowski,
                       5D pipeline differs from naive 4D-only result
  - extract_alpha_from_curvature: no tree-level EH R H² operator,
    cross-block shape and analytic warped-product curvature
"""

import numpy as np
import pytest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.metric import (
    field_strength,
    assemble_5d_metric,
    christoffel,
    compute_curvature,
    _riemann_from_christoffel,
    extract_alpha_from_curvature,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def flat_fields():
    """Flat Minkowski background with zero gauge field and unit scalar."""
    N, dx = 32, 0.1
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1))
    B = np.zeros((N, 4))
    phi = np.ones(N)
    return g, B, phi, N, dx


@pytest.fixture
def perturbed_fields():
    """Near-flat background with small random perturbations."""
    rng = np.random.default_rng(42)
    N, dx = 20, 0.1
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1)) + 5e-3 * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = 5e-3 * rng.standard_normal((N, 4))
    phi = 1.0 + 5e-3 * rng.standard_normal(N)
    return g, B, phi, N, dx


# ---------------------------------------------------------------------------
# field_strength
# ---------------------------------------------------------------------------

class TestFieldStrength:
    def test_shape(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        H = field_strength(B, dx)
        assert H.shape == (N, 4, 4)

    def test_zero_on_constant_B(self, flat_fields):
        """Constant B has zero gradient → H = 0."""
        g, B, phi, N, dx = flat_fields
        B_const = np.tile([1.0, -0.5, 0.2, 0.0], (N, 1))
        H = field_strength(B_const, dx)
        assert np.allclose(H, 0.0, atol=1e-12)

    def test_antisymmetry(self, perturbed_fields):
        """H_μν = −H_νμ."""
        g, B, phi, N, dx = perturbed_fields
        H = field_strength(B, dx)
        assert np.allclose(H, -H.transpose(0, 2, 1), atol=1e-12)

    def test_diagonal_zero(self, perturbed_fields):
        """Diagonal entries H_μμ = 0 by antisymmetry."""
        g, B, phi, N, dx = perturbed_fields
        H = field_strength(B, dx)
        for mu in range(4):
            assert np.allclose(H[:, mu, mu], 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# assemble_5d_metric
# ---------------------------------------------------------------------------

class TestAssemble5dMetric:
    def test_shape(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        G5 = assemble_5d_metric(g, B, phi)
        assert G5.shape == (N, 5, 5)

    def test_radion_G55_equals_phi_squared(self, perturbed_fields):
        """G_55 = φ²  (radion is the scalar, NOT fixed to 1)."""
        g, B, phi, N, dx = perturbed_fields
        G5 = assemble_5d_metric(g, B, phi)
        assert np.allclose(G5[:, 4, 4], phi**2, atol=1e-14)

    def test_off_diagonal_G_mu5(self, perturbed_fields):
        """G_μ5 = λφ² B_μ  (with default λ=1)."""
        g, B, phi, N, dx = perturbed_fields
        G5 = assemble_5d_metric(g, B, phi, lam=1.0)
        expected = phi[:, None]**2 * B       # shape (N, 4)
        assert np.allclose(G5[:, :4, 4], expected, atol=1e-14)
        assert np.allclose(G5[:, 4, :4], expected, atol=1e-14)

    def test_4x4_block(self, perturbed_fields):
        """4×4 block = g_μν + λ²φ² B_μ B_ν."""
        g, B, phi, N, dx = perturbed_fields
        lam = 1.0
        G5 = assemble_5d_metric(g, B, phi, lam=lam)
        lam_phi_sq = ((lam * phi)**2)[:, None, None]   # parenthesise to avoid precedence bug
        expected_block = g + lam_phi_sq * np.einsum('ni,nj->nij', B, B)
        assert np.allclose(G5[:, :4, :4], expected_block, atol=1e-14)

    def test_symmetry(self, perturbed_fields):
        """G_AB = G_BA."""
        g, B, phi, N, dx = perturbed_fields
        G5 = assemble_5d_metric(g, B, phi)
        assert np.allclose(G5, G5.transpose(0, 2, 1), atol=1e-14)

    def test_lam_coupling(self, flat_fields):
        """Off-diagonal scales with λ."""
        g, B, phi, N, dx = flat_fields
        rng = np.random.default_rng(7)
        B2 = rng.standard_normal((N, 4))
        G5_lam1 = assemble_5d_metric(g, B2, phi, lam=1.0)
        G5_lam2 = assemble_5d_metric(g, B2, phi, lam=2.0)
        # Off-diagonal should double
        assert np.allclose(G5_lam2[:, :4, 4], 2.0 * G5_lam1[:, :4, 4], atol=1e-14)


# ---------------------------------------------------------------------------
# christoffel
# ---------------------------------------------------------------------------

class TestChristoffel:
    def test_shape_4d(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        Gamma = christoffel(g, dx)
        assert Gamma.shape == (N, 4, 4, 4)

    def test_shape_5d(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        G5 = assemble_5d_metric(g, B, phi)
        Gamma5 = christoffel(G5, dx)
        assert Gamma5.shape == (N, 5, 5, 5)

    def test_vanishes_on_flat_4d(self, flat_fields):
        """Christoffel symbols vanish on constant flat metric."""
        g, B, phi, N, dx = flat_fields
        Gamma = christoffel(g, dx)
        assert np.allclose(Gamma, 0.0, atol=1e-10)

    def test_symmetry_lower_indices(self, perturbed_fields):
        """Γ^σ_μν = Γ^σ_νμ  (torsion-free)."""
        g, B, phi, N, dx = perturbed_fields
        Gamma = christoffel(g, dx)
        # Gamma[n, sigma, mu, nu] == Gamma[n, sigma, nu, mu]
        assert np.allclose(Gamma, Gamma.transpose(0, 1, 3, 2), atol=1e-10)


# ---------------------------------------------------------------------------
# compute_curvature
# ---------------------------------------------------------------------------

class TestComputeCurvature:
    def test_output_shapes(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        assert Gamma.shape == (N, 4, 4, 4)
        assert Riemann.shape == (N, 4, 4, 4, 4)
        assert Ricci.shape == (N, 4, 4)
        assert R.shape == (N,)

    def test_ricci_scalar_near_zero_on_flat(self, flat_fields):
        """Ricci scalar R ≈ 0 on flat Minkowski background."""
        g, B, phi, N, dx = flat_fields
        _, _, _, R = compute_curvature(g, B, phi, dx)
        assert np.allclose(R, 0.0, atol=1e-8)

    def test_ricci_symmetry(self, perturbed_fields):
        """Ricci tensor is symmetric: R_μν = R_νμ."""
        g, B, phi, N, dx = perturbed_fields
        _, _, Ricci, _ = compute_curvature(g, B, phi, dx)
        assert np.allclose(Ricci, Ricci.transpose(0, 2, 1), atol=1e-10)

    def test_all_finite(self, perturbed_fields):
        """All outputs are finite (no NaN or Inf)."""
        g, B, phi, N, dx = perturbed_fields
        Gamma, Riemann, Ricci, R = compute_curvature(g, B, phi, dx)
        for arr in (Gamma, Riemann, Ricci, R):
            assert np.all(np.isfinite(arr)), f"Non-finite values in {arr.shape} array"

    def test_5d_pipeline_differs_from_naive_4d(self, perturbed_fields):
        """With non-zero B and phi≠1, 5D pipeline gives different Ricci than bare 4D."""
        g, B, phi, N, dx = perturbed_fields
        # 5D pipeline (correct)
        _, _, Ricci_5d, _ = compute_curvature(g, B, phi, dx)
        # Naive 4D: Christoffel directly from g, ignoring B and phi
        Gamma_4d = christoffel(g, dx)
        Riem_4d = _riemann_from_christoffel(Gamma_4d, dx)
        Ricci_4d = np.zeros((N, 4, 4))
        for A in range(4):
            for Bx in range(4):
                for C in range(4):
                    Ricci_4d[:, A, Bx] += Riem_4d[:, C, A, C, Bx]
        # They should NOT be identical when B != 0 and phi != 1
        assert not np.allclose(Ricci_5d, Ricci_4d, atol=1e-12)


# ---------------------------------------------------------------------------
# extract_alpha_from_curvature
# ---------------------------------------------------------------------------

class TestExtractAlphaFromCurvature:
    """Tree-level circle EH reduction contains H², but no R H² operator."""

    def test_output_types(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        alpha_geom, cb = extract_alpha_from_curvature(g, B, phi, dx)
        assert isinstance(alpha_geom, float)
        assert cb.shape == (N, 4, 4)

    def test_alpha_zero_for_unit_phi(self, flat_fields):
        g, B, phi, N, dx = flat_fields  # phi = ones(N)
        alpha_geom, _ = extract_alpha_from_curvature(g, B, phi, dx)
        assert alpha_geom == 0.0

    def test_doubling_radius_does_not_generate_nonminimal_operator(self, flat_fields):
        g, B, phi, N, dx = flat_fields
        phi2 = 2.0 * phi
        alpha2, _ = extract_alpha_from_curvature(g, B, phi2, dx)
        assert alpha2 == 0.0

    def test_alpha_general_uniform_phi(self, flat_fields):
        """No R H² coefficient for any uniform radius."""
        g, B, phi, N, dx = flat_fields
        for phi_val in (0.5, 1.0, 2.0, 3.0):
            phi_uniform = phi_val * np.ones(N)
            alpha_geom, _ = extract_alpha_from_curvature(g, B, phi_uniform, dx)
            assert alpha_geom == 0.0

    def test_varying_radius_is_not_an_action_coefficient(self, perturbed_fields):
        g, B, phi, N, dx = perturbed_fields
        alpha_geom, _ = extract_alpha_from_curvature(g, B, phi, dx)
        assert alpha_geom == 0.0
        assert not np.isclose(alpha_geom, np.mean(1.0 / phi**2))

    def test_cross_block_shape(self, perturbed_fields):
        """Cross-block Riemann array has shape (N, 4, 4)."""
        g, B, phi, N, dx = perturbed_fields
        _, cb = extract_alpha_from_curvature(g, B, phi, dx)
        assert cb.shape == (N, 4, 4)

    def test_cross_block_finite(self, perturbed_fields):
        """Cross-block Riemann contains no NaN or Inf."""
        g, B, phi, N, dx = perturbed_fields
        _, cb = extract_alpha_from_curvature(g, B, phi, dx)
        assert np.all(np.isfinite(cb))

    def test_cross_block_zero_on_flat_background(self, flat_fields):
        """On a flat Minkowski background (B=0, φ=const), all 5D Christoffel
        symbols vanish ⟹ cross-block Riemann R^μ_{5ν5} = 0."""
        g, B, phi, N, dx = flat_fields
        _, cb = extract_alpha_from_curvature(g, B, phi, dx)
        assert np.allclose(cb, 0.0, atol=1e-8)

    def test_cross_block_nonzero_with_B(self, flat_fields):
        """Non-zero B field produces non-zero cross-block curvature."""
        g, B, phi, N, dx = flat_fields
        rng = np.random.default_rng(7)
        B_nz = rng.standard_normal((N, 4)) * 0.1
        _, cb = extract_alpha_from_curvature(g, B_nz, phi, dx)
        assert not np.allclose(cb, 0.0, atol=1e-8)

    def test_alpha_zero_with_nonzero_curvature(self, perturbed_fields):
        g, B, phi, N, dx = perturbed_fields
        alpha_geom, cb = extract_alpha_from_curvature(g, B, phi, dx)
        assert alpha_geom == 0.0
        assert np.linalg.norm(cb) > 0

    def test_lam_does_not_affect_alpha(self, flat_fields):
        """Changing λ does not generate an R H² operator."""
        g, B, phi, N, dx = flat_fields
        alpha1, _ = extract_alpha_from_curvature(g, B, phi, dx, lam=1.0)
        alpha2, _ = extract_alpha_from_curvature(g, B, phi, dx, lam=3.7)
        assert abs(alpha1 - alpha2) < 1e-12


# ---------------------------------------------------------------------------
# Radion cross-block curvature (not a dark-matter density)
# ---------------------------------------------------------------------------

# Numerical-noise tolerance for the monotonicity check: finite-difference
# stencil errors on a 1-D grid are O(dx²) ≈ 10⁻² for dx=0.1, so trace
# fluctuations ≲ 10⁻¹² are purely numerical and must be ignored.
_MONOTONE_NOISE_FLOOR: float = 1e-12

# Maximum fraction of grid points allowed to violate strict decrease (10%).
# Needed because edge points and central-difference stencil boundaries can
# introduce small spurious upward fluctuations.
_MAX_NONMONOTONE_FRACTION: float = 0.10


class TestRadionCrossBlock5D:
    """For flat Cartesian base and B=0, R^x_{5x5} = -φ φ''.

    The old density assertions confused a coordinate Riemann block with a
    positive matter source. The prescribed profile is not a galaxy solution.
    """

    @staticmethod
    def _galaxy_fields(N: int = 64, dx: float = 0.1,
                       phi0: float = 1.0, R_5: float = 2.0):
        """A prescribed smooth profile on a Cartesian x grid, not spherical r."""
        r = np.arange(N) * dx + dx          # avoid r = 0
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        B = np.zeros((N, 4))
        phi = phi0 / np.sqrt(1.0 + r / R_5)
        return g, B, phi, N, dx, r

    # ------------------------------------------------------------------
    def test_cross_block_curvature_negative_for_convex_phi(self):
        """Convex φ gives -φ φ'' < 0, not a positive density."""
        g, B, phi, N, dx, _ = self._galaxy_fields()
        _, cb = extract_alpha_from_curvature(g, B, phi, dx)
        trace = np.array([np.trace(cb[i]) for i in range(N)])
        assert np.all(trace < 0.0)

    def test_cross_block_magnitude_decreases_outward(self):
        """The negative curvature approaches zero from below."""
        g, B, phi, N, dx, _ = self._galaxy_fields(N=64, dx=0.1, R_5=2.0)
        _, cb = extract_alpha_from_curvature(g, B, phi, dx)
        trace = np.array([np.trace(cb[i]) for i in range(N)])
        diffs = np.diff(np.abs(trace))
        n_increasing = int(np.sum(diffs > _MONOTONE_NOISE_FLOOR))
        max_allowed = int(_MAX_NONMONOTONE_FRACTION * (N - 1))
        assert n_increasing <= max_allowed, (
            f"Curvature proxy must decrease outward; {n_increasing}/{N-1} "
            f"points show an increase > {_MONOTONE_NOISE_FLOOR:.0e} "
            f"(allowed ≤ {max_allowed})"
        )

    def test_cross_block_matches_analytic_hessian(self):
        """Check amplitude and sign, not merely correlation with another curve."""
        R_5 = 2.0
        N, dx = 64, 0.1
        g, B, phi, _, dx_out, r = self._galaxy_fields(N=N, dx=dx, R_5=R_5)
        _, cb = extract_alpha_from_curvature(g, B, phi, dx_out)
        trace = np.array([np.trace(cb[i]) for i in range(N)])

        expected = -3.0 / (4 * R_5**2) * (1 + r / R_5)**-3
        np.testing.assert_allclose(trace[2:-2], expected[2:-2], rtol=0.025)

    def test_cross_block_zero_for_uniform_phi(self, flat_fields):
        """A constant product metric has no cross-block curvature."""
        g, B, phi, N, dx = flat_fields    # phi = ones(N), B = 0
        _, cb = extract_alpha_from_curvature(g, B, phi, dx)
        assert np.allclose(cb, 0.0, atol=1e-8), (
            "Cross-block Riemann must vanish for uniform φ"
        )

    def test_cross_block_magnitude_grows_for_shorter_profile_scale(self):
        N, dx = 64, 0.1

        # Compact halo: R₅ = 1.0 → steep gradient
        g1, B1, phi1, _, _, _ = self._galaxy_fields(N=N, dx=dx, R_5=1.0)
        _, cb1 = extract_alpha_from_curvature(g1, B1, phi1, dx)
        trace1_mean = float(np.mean([np.trace(cb1[i]) for i in range(N)]))

        # Diffuse halo: R₅ = 5.0 → gentle gradient
        g2, B2, phi2, _, _, _ = self._galaxy_fields(N=N, dx=dx, R_5=5.0)
        _, cb2 = extract_alpha_from_curvature(g2, B2, phi2, dx)
        trace2_mean = float(np.mean([np.trace(cb2[i]) for i in range(N)]))

        assert abs(trace1_mean) > abs(trace2_mean)

    def test_cross_block_is_not_squared_logarithmic_gradient(self):
        """The two quantities have different sign AND radial power."""
        R_5 = 2.0
        N, dx = 64, 0.1
        g, B, phi, _, dx_out, r = self._galaxy_fields(N=N, dx=dx, R_5=R_5)
        _, cb = extract_alpha_from_curvature(g, B, phi, dx_out)
        trace = np.array([np.trace(cb[i]) for i in range(N)])

        # Analytic formula: (∂_r φ / φ)²
        dphi = np.gradient(phi, dx_out)
        rho_kk = (dphi / phi) ** 2

        ratio = trace[2:-2] / rho_kk[2:-2]
        np.testing.assert_allclose(ratio, -3 * phi[2:-2]**2, rtol=0.025)
        assert np.ptp(ratio) > 0.5


# ===========================================================================
# TestZ2ParityClarification (Pillar A3 peer-review addition)
# ===========================================================================

from src.core.metric import z2_parity_clarification


class TestZ2ParityClarification:
    """Tests for z2_parity_clarification() — referee Z₂ parity resolution."""

    def setup_method(self):
        self.result = z2_parity_clarification()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_B_mu_is_z2_odd(self):
        assert "Z₂-ODD" in self.result["B_mu_parity"]

    def test_phi_is_z2_even(self):
        assert "Z₂-EVEN" in self.result["phi_parity"]

    def test_A_mu_is_not_an_independent_boundary_field(self):
        assert self.result["fields_are_distinct"] is False
        assert self.result["photon_zero_mode"] is False
        assert self.result["fixed_plane_value"] == 0.0

    def test_resolution_non_empty(self):
        assert len(self.result["resolution"]) > 80

    def test_status_open(self):
        assert "OPEN" in self.result["status"]

    def test_g_munu_is_z2_even(self):
        assert "Z₂-EVEN" in self.result["g_munu_parity"]

    def test_G_mu5_is_z2_odd(self):
        assert "Z₂-ODD" in self.result["G_mu5_parity"]

    def test_G_55_is_z2_even(self):
        assert "Z₂-EVEN" in self.result["G_55_parity"]

    def test_referee_question_present(self):
        assert "zero mode" in self.result["referee_question"].lower()

    def test_code_references_non_empty(self):
        refs = self.result["code_references"]
        assert len(refs) >= 3
        assert any("metric.py" in r for r in refs)


# ---------------------------------------------------------------------------
# B1 audit fix: near-singular metric guard in christoffel()
# ---------------------------------------------------------------------------

class TestChristoffelNearSingular:
    """Verify that christoffel() raises ValueError for near-singular metrics."""

    def test_near_singular_metric_raises(self):
        """A metric with a near-zero determinant (condition number > 1e12) must
        raise ValueError rather than silently producing garbage Christoffel symbols."""
        N, D = 8, 4
        # Build a metric whose second row/column is a tiny multiple of the first.
        g_base = np.diag([-1.0, 1.0, 1.0, 1.0])
        g_singular = g_base.copy()
        g_singular[1, :] = 1e-14 * g_base[0, :]
        g_singular[:, 1] = 1e-14 * g_base[:, 0]
        g = np.tile(g_singular, (N, 1, 1))
        with pytest.raises(ValueError, match="Near-singular metric"):
            christoffel(g, dx=0.1)
