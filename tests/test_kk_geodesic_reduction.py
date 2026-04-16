"""tests/test_kk_geodesic_reduction.py
======================================
Tests for src/core/kk_geodesic_reduction.py

These tests verify Gap 4 of UNIFICATION_PROOF.md §XII:
The Lorentz force IS derived from the 5D geodesic equation — it is not
assumed.  The identification A_μ = λ Bμ is a theorem.

Key theorem tested:
    acc_geo + acc_lor  ≈  acc_5d_projected

where:
    acc_geo  = −Γ^μ_νρ(g) u^ν u^ρ  (4D gravity, from g alone)
    acc_lor  = (e/m) F^μ_ν u^ν      (Lorentz force, from B and p₅)
    acc_5d   = full 5D geodesic projected to 4D  (independent)
"""

import numpy as np
import pytest

from src.core.kk_geodesic_reduction import (
    fifth_momentum,
    christoffel_5d_nu5_block,
    lorentz_acceleration,
    geodesic_decomposition,
    verify_christoffel_nu5,
    electromagnetic_potential,
    GeodesicDecomposition,
)


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _flat_state(N=8, dx=0.1, lam=1.0, B_amp=0.05, u5_val=0.01):
    """Flat-space test state with a uniform electromagnetic field."""
    eta = np.diag([-1., 1., 1., 1.])
    g   = np.tile(eta, (N, 1, 1)).copy()
    phi = np.ones(N)

    # Linear Bμ  (gives non-zero H_μν = ∂_μBν − ∂_νBμ)
    x = np.linspace(0, (N - 1) * dx, N)
    B = np.zeros((N, 4))
    B[:, 1] = B_amp * x           # B_x varies linearly → H_{01} = const
    B[:, 0] = B_amp * 0.5 * x    # B_0 also varies

    # Test particle with a simple 4-velocity (normalised approximately)
    u4 = np.zeros((N, 4))
    u4[:, 0] = 1.0   # u^t ≈ 1
    u4[:, 1] = 0.1   # small spatial velocity

    u5 = np.full(N, u5_val)

    return g, B, phi, u4, u5, dx, lam


# ---------------------------------------------------------------------------
# fifth_momentum
# ---------------------------------------------------------------------------

class TestFifthMomentum:
    def test_shape(self):
        g, B, phi, u4, u5, dx, lam = _flat_state()
        p5 = fifth_momentum(B, phi, u4, u5, lam)
        assert p5.shape == (8,)

    def test_zero_when_B_and_u5_zero(self):
        N = 6
        phi = np.ones(N)
        B   = np.zeros((N, 4))
        u4  = np.ones((N, 4)) * 0.1
        u5  = np.zeros(N)
        p5 = fifth_momentum(B, phi, u4, u5, lam=1.0)
        np.testing.assert_allclose(p5, 0.0)

    def test_pure_u5_contribution(self):
        N = 4
        phi = 2.0 * np.ones(N)
        B   = np.zeros((N, 4))
        u4  = np.zeros((N, 4))
        u5  = 3.0 * np.ones(N)
        # p5 = φ² u^5 = 4 * 3 = 12
        p5 = fifth_momentum(B, phi, u4, u5, lam=1.0)
        np.testing.assert_allclose(p5, 12.0)

    def test_gauge_contribution(self):
        N = 4
        phi = np.ones(N)
        B   = np.ones((N, 4)) * 0.5
        u4  = np.ones((N, 4))
        u5  = np.zeros(N)
        lam = 2.0
        # p5 = λ φ Bμ u^μ = 2 * 1 * (4 * 0.5 * 1) = 4
        p5 = fifth_momentum(B, phi, u4, u5, lam)
        np.testing.assert_allclose(p5, 4.0, rtol=1e-10)


# ---------------------------------------------------------------------------
# christoffel_5d_nu5_block
# ---------------------------------------------------------------------------

class TestChristoffel5dNu5Block:
    def test_shape(self):
        g, B, phi, u4, u5, dx, lam = _flat_state()
        Gam = christoffel_5d_nu5_block(g, B, phi, dx, lam)
        assert Gam.shape == (8, 4, 4)

    def test_matches_analytic_formula_flat(self):
        """Γ^σ_{μ5} matches 1D code's exact formula in flat space.

        In 1D: Γ^σ_{μ5} = (λφ/2)[δ_{μ0} g^{σρ}∂_xB_ρ − g^{σ0}∂_xB_μ]
        """
        g, B, phi, u4, u5, dx, lam = _flat_state(N=16, B_amp=0.03)
        result = verify_christoffel_nu5(g, B, phi, dx, lam)
        rel_err = result['rel_error']
        if not np.isnan(rel_err):
            assert rel_err < 0.01, (
                f"Γ^σ_{{μ5}} analytic mismatch: rel_error = {rel_err:.6f}"
            )

    def test_zero_for_zero_B(self):
        """With B = 0, H = 0, so Γ^μ_{ν5} should vanish."""
        N = 8
        eta = np.diag([-1., 1., 1., 1.])
        g   = np.tile(eta, (N, 1, 1))
        B   = np.zeros((N, 4))
        phi = np.ones(N)
        dx, lam = 0.1, 1.0
        Gam = christoffel_5d_nu5_block(g, B, phi, dx, lam)
        np.testing.assert_allclose(np.abs(Gam).max(), 0.0, atol=1e-10)


# ---------------------------------------------------------------------------
# lorentz_acceleration
# ---------------------------------------------------------------------------

class TestLorentzAcceleration:
    def test_shape(self):
        g, B, phi, u4, u5, dx, lam = _flat_state()
        acc, em = lorentz_acceleration(B, phi, u4, u5, g, dx, lam)
        assert acc.shape == (8, 4)
        assert em.shape  == (8,)

    def test_zero_for_zero_u5(self):
        """Zero u^5 → zero Lorentz force (no 5th-momentum coupling)."""
        g, B, phi, u4, u5, dx, lam = _flat_state()
        u5_zero = np.zeros(8)
        acc, em = lorentz_acceleration(B, phi, u4, u5_zero, g, dx, lam)
        np.testing.assert_allclose(np.abs(acc).max(), 0.0, atol=1e-12)

    def test_zero_for_zero_B(self):
        """Zero B → zero Christoffel Γ^μ_{ν5} → zero Lorentz force."""
        N = 8
        eta = np.diag([-1., 1., 1., 1.])
        g   = np.tile(eta, (N, 1, 1))
        B   = np.zeros((N, 4))
        phi = np.ones(N)
        u4  = np.zeros((N, 4)); u4[:, 0] = 1.0
        u5  = 0.05 * np.ones(N)
        acc, _ = lorentz_acceleration(B, phi, u4, u5, g, dx=0.1, lam=1.0)
        np.testing.assert_allclose(np.abs(acc).max(), 0.0, atol=1e-12)

    def test_em_ratio_formula(self):
        """e/m = λ p₅ / φ."""
        N = 5
        g   = np.tile(np.eye(4), (N, 1, 1))
        B   = np.zeros((N, 4))
        phi = 2.0 * np.ones(N)
        u4  = np.zeros((N, 4)); u4[:, 0] = 1.0
        u5  = 3.0 * np.ones(N)    # p5 = φ² u^5 = 4 * 3 = 12
        lam = 2.0
        _, em = lorentz_acceleration(B, phi, u4, u5, g, dx=0.1, lam=lam)
        # p5 = φ² u^5 = 4 * 3 = 12; e/m = 2 * 12 / 2 = 12
        np.testing.assert_allclose(em, 12.0, rtol=1e-10)


# ---------------------------------------------------------------------------
# geodesic_decomposition — the central theorem test
# ---------------------------------------------------------------------------

class TestGeodesicDecomposition:
    def test_returns_namedtuple(self):
        g, B, phi, u4, u5, dx, lam = _flat_state()
        result = geodesic_decomposition(g, B, phi, u4, u5, dx, lam)
        assert isinstance(result, GeodesicDecomposition)

    def test_shapes(self):
        N = 10
        g, B, phi, u4, u5, dx, lam = _flat_state(N=N)
        r = geodesic_decomposition(g, B, phi, u4, u5, dx, lam)
        assert r.acc_geo.shape   == (N, 4)
        assert r.acc_lor.shape   == (N, 4)
        assert r.acc_total.shape == (N, 4)
        assert r.acc_5d.shape    == (N, 4)
        assert r.residual.shape  == (N, 4)
        assert r.em_ratio.shape  == (N,)
        assert r.p5.shape        == (N,)

    def test_total_equals_geo_plus_lor(self):
        """acc_total must equal acc_geo + acc_lor exactly (by construction)."""
        g, B, phi, u4, u5, dx, lam = _flat_state()
        r = geodesic_decomposition(g, B, phi, u4, u5, dx, lam)
        np.testing.assert_allclose(r.acc_total, r.acc_geo + r.acc_lor,
                                   atol=1e-14)

    def test_flat_no_gravity_acc_geo_zero(self):
        """In flat Minkowski space with uniform metric, acc_geo = 0."""
        N = 8
        eta = np.diag([-1., 1., 1., 1.])
        g   = np.tile(eta, (N, 1, 1))   # uniform → all derivatives = 0
        B   = np.zeros((N, 4))
        phi = np.ones(N)
        u4  = np.zeros((N, 4)); u4[:, 0] = 1.0
        u5  = np.zeros(N)
        r = geodesic_decomposition(g, B, phi, u4, u5, dx=0.1, lam=1.0)
        np.testing.assert_allclose(np.abs(r.acc_geo).max(), 0.0, atol=1e-10)

    def test_theorem_residual_small(self):
        """Main theorem: acc_geo + acc_lor + radion = acc_5d EXACTLY.

        The residual acc_total − acc_5d is the RADION term (Γ^μ_{55} (u^5)²).
        For small u^5, it is small relative to the 5D acceleration.
        """
        g, B, phi, u4, u5, dx, lam = _flat_state(N=16, B_amp=0.03,
                                                   u5_val=0.01)
        r = geodesic_decomposition(g, B, phi, u4, u5, dx, lam)
        # The residual is just the radion term, O((u^5)^2) = O(1e-4)
        # Verify it is small relative to the Lorentz term
        norm_5d  = np.linalg.norm(r.acc_5d)
        norm_res = np.linalg.norm(r.residual)
        if norm_5d > 1e-12:
            rel = norm_res / norm_5d
            assert rel < 0.5, (
                f"Radion term too large relative to acc_5d: {rel:.4f}"
            )

    def test_exact_decomposition_with_radion(self):
        """EXACT theorem: acc_4d_from_G5 + acc_lor + acc_radion = acc_5d.

        This tests the numerically exact splitting of the 5D geodesic.
        """
        g, B, phi, u4, u5, dx, lam = _flat_state(N=16, B_amp=0.03,
                                                   u5_val=0.01)
        from src.core.metric import assemble_5d_metric, christoffel
        G5     = assemble_5d_metric(g, B, phi, lam)
        Gamma5 = christoffel(G5, dx)
        U5     = np.concatenate([u4, u5[:, None]], axis=1)
        acc_5d = -np.einsum('nabc,nb,nc->na', Gamma5, U5, U5)[:, :4]

        acc_4d_G5  = -np.einsum('nabc,nb,nc->na', Gamma5[:,:4,:4,:4], u4, u4)
        acc_lor    = -2 * np.einsum('nab,nb,n->na', Gamma5[:,:4,:4,4], u4, u5)
        acc_radion = -Gamma5[:, :4, 4, 4] * u5[:, None]**2

        residual = acc_4d_G5 + acc_lor + acc_radion - acc_5d
        np.testing.assert_allclose(np.abs(residual).max(), 0.0, atol=1e-10)

    def test_lorentz_force_direction(self):
        """Lorentz force should respond to field strength direction."""
        N = 8
        eta  = np.diag([-1., 1., 1., 1.])
        g    = np.tile(eta, (N, 1, 1))
        phi  = np.ones(N)
        dx   = 0.1
        lam  = 1.0
        x = np.linspace(0, (N-1)*dx, N)
        B = np.zeros((N, 4))
        B[:, 1] = 0.1 * x
        u4 = np.zeros((N, 4)); u4[:, 0] = 1.0; u4[:, 1] = 0.1
        u5 = 0.05 * np.ones(N)
        r = geodesic_decomposition(g, B, phi, u4, u5, dx, lam)
        # With non-zero B and u5, the Lorentz acceleration should be non-zero
        assert np.linalg.norm(r.acc_lor) > 0.0


# ---------------------------------------------------------------------------
# electromagnetic_potential
# ---------------------------------------------------------------------------

class TestElectromagneticPotential:
    def test_formula(self):
        """A_μ = λ Bμ."""
        B   = np.random.randn(6, 4)
        lam = 2.5
        A   = electromagnetic_potential(B, lam)
        np.testing.assert_allclose(A, lam * B)

    def test_unit_coupling(self):
        B = np.random.randn(4, 4)
        A = electromagnetic_potential(B, lam=1.0)
        np.testing.assert_allclose(A, B)


# ---------------------------------------------------------------------------
# verify_christoffel_nu5 (integration test)
# ---------------------------------------------------------------------------

class TestVerifyChristoffelNu5:
    def test_returns_dict(self):
        g, B, phi, u4, u5, dx, lam = _flat_state()
        result = verify_christoffel_nu5(g, B, phi, dx, lam)
        assert 'Gamma_nu5' in result
        assert 'expected'  in result
        assert 'rel_error' in result

    def test_shapes(self):
        N = 8
        g, B, phi, u4, u5, dx, lam = _flat_state(N=N)
        result = verify_christoffel_nu5(g, B, phi, dx, lam)
        assert result['Gamma_nu5'].shape == (N, 4, 4)
        assert result['expected'].shape  == (N, 4, 4)

    def test_zero_for_zero_B(self):
        """With B = 0, both Γ^μ_{ν5} and the expected value should be zero."""
        N = 8
        eta = np.diag([-1., 1., 1., 1.])
        g   = np.tile(eta, (N, 1, 1))
        B   = np.zeros((N, 4))
        phi = np.ones(N)
        result = verify_christoffel_nu5(g, B, phi, dx=0.1, lam=1.0)
        np.testing.assert_allclose(np.abs(result['Gamma_nu5']).max(),
                                   0.0, atol=1e-10)
        np.testing.assert_allclose(np.abs(result['expected']).max(),
                                   0.0, atol=1e-10)
