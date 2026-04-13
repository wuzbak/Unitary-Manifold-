"""
tests/test_dark_matter_geometry.py
====================================
Tests for src/core/dark_matter_geometry.py

Covers:

    b_field_energy_density      — ρ_B = λ²φ²|B|²/2 on field grid
    b_field_dark_density        — isothermal ρ_dark(r) ∝ 1/r² from B_μ ∝ 1/r
    b_field_dark_mass_enclosed  — M_dark(<r) ∝ r (flat curve signature)
    flat_curve_velocity         — v_flat² = 2π G λ²φ²B₀²r_s²
    b_field_rotation_velocity   — v_total = v_baryon + v_dark combined
    dark_field_profile          — full galaxy profile dataclass
"""

import numpy as np
import pytest

from src.core.dark_matter_geometry import (
    DarkFieldProfile,
    b_field_dark_density,
    b_field_dark_mass_enclosed,
    b_field_energy_density,
    b_field_rotation_velocity,
    dark_field_profile,
    flat_curve_velocity,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _radial_grid(r_min=0.1, r_max=10.0, N=100):
    return np.linspace(r_min, r_max, N)


def _exponential_sphere_mass(r, M_total=1.0, R_d=1.0):
    """Cumulative baryonic mass from 3-D exponential sphere."""
    x = r / R_d
    return M_total * (1.0 - (1.0 + x + 0.5 * x**2) * np.exp(-x))


# ---------------------------------------------------------------------------
# b_field_energy_density
# ---------------------------------------------------------------------------

class TestBFieldEnergyDensity:
    """ρ_B = λ²φ²|B|²/2 on the field grid."""

    def test_shape(self):
        """Output shape matches number of grid points."""
        N = 16
        B = np.ones((N, 4))
        phi = np.ones(N)
        rho = b_field_energy_density(B, phi)
        assert rho.shape == (N,)

    def test_nonnegative(self):
        """Energy density is non-negative."""
        N = 32
        rng = np.random.default_rng(1)
        B = rng.standard_normal((N, 4))
        phi = np.abs(rng.standard_normal(N)) + 0.1
        rho = b_field_energy_density(B, phi)
        assert np.all(rho >= 0.0)

    def test_zero_B_gives_zero_density(self):
        """No B field → no energy density."""
        N = 16
        B = np.zeros((N, 4))
        phi = np.ones(N)
        np.testing.assert_allclose(b_field_energy_density(B, phi), 0.0, atol=1e-30)

    def test_scales_with_B_squared(self):
        """Doubling |B| quadruples ρ_B."""
        N = 16
        phi = np.ones(N)
        B1 = np.ones((N, 4))
        B2 = 2.0 * np.ones((N, 4))
        rho1 = b_field_energy_density(B1, phi)
        rho2 = b_field_energy_density(B2, phi)
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-12)

    def test_scales_with_phi_squared(self):
        """Doubling φ quadruples ρ_B."""
        N = 16
        B = np.ones((N, 4))
        rho1 = b_field_energy_density(B, np.ones(N))
        rho2 = b_field_energy_density(B, 2.0 * np.ones(N))
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-12)

    def test_scales_with_lambda_squared(self):
        """Doubling λ quadruples ρ_B."""
        N = 16
        B = np.ones((N, 4))
        phi = np.ones(N)
        rho1 = b_field_energy_density(B, phi, lam=1.0)
        rho2 = b_field_energy_density(B, phi, lam=2.0)
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-12)

    def test_finite_everywhere(self):
        """ρ_B is finite for bounded fields."""
        N = 32
        B = np.random.default_rng(2).standard_normal((N, 4))
        phi = np.ones(N)
        assert np.all(np.isfinite(b_field_energy_density(B, phi)))


# ---------------------------------------------------------------------------
# b_field_dark_density
# ---------------------------------------------------------------------------

class TestBFieldDarkDensity:
    """ρ_dark(r) = ρ₀ r_s² / r² — isothermal profile."""

    def test_shape(self):
        """Output shape matches radial grid."""
        r = _radial_grid(N=50)
        rho = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert rho.shape == (50,)

    def test_nonnegative(self):
        """Dark density is non-negative."""
        r = _radial_grid()
        rho = b_field_dark_density(r, B0=0.5, r_scale=2.0, phi_mean=1.0)
        assert np.all(rho >= 0.0)

    def test_decreases_with_radius(self):
        """ρ_dark ∝ 1/r² strictly decreases outward."""
        r = _radial_grid(r_min=0.5)
        rho = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert np.all(np.diff(rho) < 0.0)

    def test_isothermal_profile_exponent(self):
        """ρ_dark ∝ r⁻² — verify by log-log slope ≈ −2."""
        r = np.logspace(0, 2, 200)    # 1 to 100 Planck lengths
        rho = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        slope = np.polyfit(np.log(r[10:-10]), np.log(rho[10:-10]), 1)[0]
        assert slope == pytest.approx(-2.0, abs=0.02)

    def test_scales_with_B0_squared(self):
        """Doubling B₀ quadruples ρ_dark (ρ ∝ B₀²)."""
        r = _radial_grid()
        rho1 = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        rho2 = b_field_dark_density(r, B0=2.0, r_scale=1.0, phi_mean=1.0)
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-12)

    def test_scales_with_phi_squared(self):
        """Doubling φ_mean quadruples ρ_dark (ρ ∝ φ²)."""
        r = _radial_grid()
        rho1 = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        rho2 = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=2.0)
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-12)

    def test_larger_r_scale_gives_higher_density(self):
        """Larger scale radius r_s → denser dark field at same physical r."""
        r = _radial_grid()
        rho1 = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        rho2 = b_field_dark_density(r, B0=1.0, r_scale=2.0, phi_mean=1.0)
        assert np.all(rho2 > rho1)

    def test_finite_everywhere(self):
        """ρ_dark is finite for r > 0."""
        r = _radial_grid()
        rho = b_field_dark_density(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert np.all(np.isfinite(rho))


# ---------------------------------------------------------------------------
# b_field_dark_mass_enclosed
# ---------------------------------------------------------------------------

class TestBFieldDarkMassEnclosed:
    """M_dark(<r) ∝ r — linear growth gives flat curve."""

    def test_shape(self):
        r = _radial_grid(N=50)
        M = b_field_dark_mass_enclosed(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert M.shape == (50,)

    def test_nonnegative(self):
        r = _radial_grid()
        M = b_field_dark_mass_enclosed(r, B0=0.5, r_scale=1.0, phi_mean=1.0)
        assert np.all(M >= 0.0)

    def test_increases_with_radius(self):
        """More volume enclosed → more dark mass."""
        r = _radial_grid()
        M = b_field_dark_mass_enclosed(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert np.all(np.diff(M) > 0.0)

    def test_linear_in_r(self):
        """M_dark(<r) ∝ r — verified by log-log slope ≈ 1."""
        r = np.linspace(0.5, 20.0, 200)
        M = b_field_dark_mass_enclosed(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        slope = np.polyfit(np.log(r), np.log(M + 1e-30), 1)[0]
        assert slope == pytest.approx(1.0, abs=0.01)

    def test_flat_curve_condition(self):
        """v²_dark = G M_dark / r = 4π G ρ₀ r_s² = const (independent of r)."""
        r = np.linspace(1.0, 20.0, 100)
        B0, r_scale, phi_mean = 1.0, 1.0, 1.0
        M_dark = b_field_dark_mass_enclosed(r, B0, r_scale, phi_mean)
        v_sq_dark = M_dark / r           # G = 1
        # v²_dark should be roughly constant (std/mean < 1e-10)
        np.testing.assert_allclose(v_sq_dark, v_sq_dark[0], rtol=1e-12)

    def test_scales_with_B0_squared(self):
        """M_dark ∝ B₀² — doubling B₀ quadruples enclosed dark mass."""
        r = _radial_grid()
        M1 = b_field_dark_mass_enclosed(r, B0=1.0, r_scale=1.0, phi_mean=1.0)
        M2 = b_field_dark_mass_enclosed(r, B0=2.0, r_scale=1.0, phi_mean=1.0)
        np.testing.assert_allclose(M2, 4.0 * M1, rtol=1e-12)


# ---------------------------------------------------------------------------
# flat_curve_velocity
# ---------------------------------------------------------------------------

class TestFlatCurveVelocity:
    """v_flat² = 2π G λ²φ²B₀²r_s² — asymptotic rotation speed."""

    def test_positive(self):
        """Flat curve velocity is strictly positive."""
        assert flat_curve_velocity(B0=1.0, r_scale=1.0, phi_mean=1.0) > 0.0

    def test_analytic_formula(self):
        """v_flat = sqrt(2π G λ²φ²B₀²r_s²) matches explicit calculation."""
        B0, r_s, phi, lam, G4 = 2.0, 1.5, 0.8, 1.0, 1.0
        expected = np.sqrt(2.0 * np.pi * G4 * lam**2 * phi**2 * B0**2 * r_s**2)
        np.testing.assert_allclose(
            flat_curve_velocity(B0, r_s, phi, lam, G4), expected, rtol=1e-12)

    def test_scales_with_B0(self):
        """Doubling B₀ doubles v_flat (v_flat ∝ B₀)."""
        v1 = flat_curve_velocity(1.0, 1.0, 1.0)
        v2 = flat_curve_velocity(2.0, 1.0, 1.0)
        assert v2 == pytest.approx(2.0 * v1, rel=1e-12)

    def test_scales_with_phi(self):
        """Doubling φ doubles v_flat (v_flat ∝ φ)."""
        v1 = flat_curve_velocity(1.0, 1.0, 1.0)
        v2 = flat_curve_velocity(1.0, 1.0, 2.0)
        assert v2 == pytest.approx(2.0 * v1, rel=1e-12)

    def test_scales_with_r_scale(self):
        """Doubling r_scale doubles v_flat."""
        v1 = flat_curve_velocity(1.0, 1.0, 1.0)
        v2 = flat_curve_velocity(1.0, 2.0, 1.0)
        assert v2 == pytest.approx(2.0 * v1, rel=1e-12)

    def test_finite(self):
        """v_flat is finite for bounded parameters."""
        assert np.isfinite(flat_curve_velocity(1.0, 1.0, 1.0))

    def test_raises_on_zero_B0(self):
        """B0 = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="B0"):
            flat_curve_velocity(0.0, 1.0, 1.0)

    def test_raises_on_zero_r_scale(self):
        """r_scale = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="r_scale"):
            flat_curve_velocity(1.0, 0.0, 1.0)

    def test_raises_on_zero_phi_mean(self):
        """phi_mean = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_mean"):
            flat_curve_velocity(1.0, 1.0, 0.0)


# ---------------------------------------------------------------------------
# b_field_rotation_velocity
# ---------------------------------------------------------------------------

class TestBFieldRotationVelocity:
    """v_total = sqrt(G [M_baryon + M_dark] / r) — total rotation curve."""

    def test_shape(self):
        """Output shape matches radial grid."""
        r = _radial_grid(N=50)
        M_b = _exponential_sphere_mass(r)
        v = b_field_rotation_velocity(r, M_b, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert v.shape == (50,)

    def test_nonnegative(self):
        """Total rotation speed is non-negative."""
        r = _radial_grid()
        M_b = _exponential_sphere_mass(r)
        v = b_field_rotation_velocity(r, M_b, B0=1.0, r_scale=1.0, phi_mean=1.0)
        assert np.all(v >= 0.0)

    def test_finite(self):
        """Rotation speed is finite for well-posed inputs."""
        r = _radial_grid()
        M_b = _exponential_sphere_mass(r)
        v = b_field_rotation_velocity(r, M_b, B0=0.5, r_scale=1.0, phi_mean=1.0)
        assert np.all(np.isfinite(v))

    def test_5d_curve_exceeds_newtonian_at_large_r(self):
        """v_total > v_Newtonian at large r (dark field boosts velocity)."""
        r = _radial_grid(r_min=0.5, r_max=15.0, N=200)
        M_b = _exponential_sphere_mass(r, M_total=1.0, R_d=1.0)
        v_Newton = np.sqrt(np.clip(M_b / (r + 1e-10), 0.0, None))
        v_total  = b_field_rotation_velocity(r, M_b, B0=1.5, r_scale=2.0,
                                              phi_mean=1.0)
        outer = r > 5.0
        assert np.mean(v_total[outer]) > np.mean(v_Newton[outer])

    def test_outer_curve_approaches_flat(self):
        """v_total(r) flattens at large r (std/mean < Newtonian std/mean)."""
        r = np.linspace(5.0, 20.0, 300)
        M_b = _exponential_sphere_mass(r, M_total=0.1, R_d=1.0)
        v_N = np.sqrt(np.clip(M_b / (r + 1e-10), 0.0, None))
        v_5D = b_field_rotation_velocity(r, M_b, B0=1.0, r_scale=2.0,
                                          phi_mean=1.0)
        cv_N  = float(np.std(v_N)  / (np.mean(v_N)  + 1e-30))
        cv_5D = float(np.std(v_5D) / (np.mean(v_5D) + 1e-30))
        assert cv_5D < cv_N, (
            f"5D curve must be flatter; cv_N={cv_N:.4f}, cv_5D={cv_5D:.4f}")

    def test_larger_B0_gives_higher_outer_velocity(self):
        """Stronger B_μ field → more dark mass → faster outer rotation."""
        r = _radial_grid(r_min=5.0, r_max=15.0)
        M_b = _exponential_sphere_mass(r)
        v_weak  = b_field_rotation_velocity(r, M_b, B0=0.5, r_scale=1.0,
                                             phi_mean=1.0)
        v_strong = b_field_rotation_velocity(r, M_b, B0=3.0, r_scale=1.0,
                                              phi_mean=1.0)
        assert np.mean(v_strong) > np.mean(v_weak)


# ---------------------------------------------------------------------------
# dark_field_profile
# ---------------------------------------------------------------------------

class TestDarkFieldProfile:
    """DarkFieldProfile builder — full galaxy prediction."""

    def _make_profile(self, **kwargs):
        defaults = dict(B0=1.0, r_scale=1.0, phi_mean=1.0,
                        r_max=10.0, N=100, M_total=1.0, R_disk=1.0)
        defaults.update(kwargs)
        return dark_field_profile(**defaults)

    def test_returns_dark_field_profile(self):
        """Return type is DarkFieldProfile."""
        assert isinstance(self._make_profile(), DarkFieldProfile)

    def test_arrays_correct_length(self):
        """All arrays have length N."""
        p = self._make_profile(N=80)
        for arr_name in ("r", "rho_dark", "M_dark", "v_baryonic", "v_total"):
            arr = getattr(p, arr_name)
            assert arr.shape == (80,), f"{arr_name} shape {arr.shape} ≠ (80,)"

    def test_v_flat_matches_standalone(self):
        """DarkFieldProfile.v_flat equals flat_curve_velocity()."""
        B0, r_s, phi = 2.0, 1.5, 0.8
        p = self._make_profile(B0=B0, r_scale=r_s, phi_mean=phi)
        expected = flat_curve_velocity(B0, r_s, phi)
        assert p.v_flat == pytest.approx(expected, rel=1e-10)

    def test_v_total_exceeds_v_baryonic_at_large_r(self):
        """Dark field boosts v_total above v_baryonic at large radii."""
        p = self._make_profile(B0=2.0, r_scale=1.0, phi_mean=1.0,
                               r_max=15.0, N=200, M_total=0.3)
        outer = p.r > 5.0
        assert np.mean(p.v_total[outer]) > np.mean(p.v_baryonic[outer])

    def test_rho_dark_decreases_outward(self):
        """Dark density ρ_dark(r) decreases monotonically."""
        p = self._make_profile(r_max=10.0, N=100)
        assert np.all(np.diff(p.rho_dark) < 0.0)

    def test_M_dark_increases_outward(self):
        """Enclosed dark mass grows with radius."""
        p = self._make_profile()
        assert np.all(np.diff(p.M_dark) > 0.0)

    def test_stored_parameters(self):
        """DarkFieldProfile stores the input parameters."""
        p = self._make_profile(B0=3.0, r_scale=2.5, phi_mean=0.7, lam=1.5)
        assert p.B0 == 3.0
        assert p.r_scale == 2.5
        assert p.phi_mean == 0.7
        assert p.lam == 1.5

    def test_all_velocities_finite(self):
        """All velocity arrays are finite."""
        p = self._make_profile()
        assert np.all(np.isfinite(p.v_baryonic))
        assert np.all(np.isfinite(p.v_total))

    def test_v_flat_positive(self):
        """Asymptotic flat speed is positive."""
        p = self._make_profile()
        assert p.v_flat > 0.0
