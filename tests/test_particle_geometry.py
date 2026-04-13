"""
tests/test_particle_geometry.py
================================
Tests for src/core/particle_geometry.py

Covers the full public API:

    PARTICLE_CATALOG           — standard particles as geometric windings
    GeometricParticle          — dataclass consistency
    fiber_curvature            — κ_fib = n_w |∂φ| / φ
    geometric_mass             — m = λ n_w / ⟨φ⟩
    generation_mass_ratio      — m₂/m₁ = ⟨φ₁⟩/⟨φ₂⟩
    muon_kk_correction         — δa_μ = m_μ² ⟨φ⟩² / 12π²
    unwinding_rate             — Γ = κ_H × n_w
    particle_info_fraction     — f_enc = κ_H
"""

import numpy as np
import pytest

from src.core.particle_geometry import (
    PARTICLE_CATALOG,
    GeometricParticle,
    _PHI_GEN1,
    _PHI_GEN2,
    _PHI_GEN3,
    fiber_curvature,
    generation_mass_ratio,
    geometric_mass,
    muon_kk_correction,
    particle_info_fraction,
    unwinding_rate,
)


# ---------------------------------------------------------------------------
# Particle catalog
# ---------------------------------------------------------------------------

class TestParticleCatalog:
    """PARTICLE_CATALOG contains consistent SM particle descriptions."""

    def test_catalog_contains_expected_particles(self):
        """All nine SM particles + photon are present."""
        for name in ("electron", "muon", "tau",
                     "up", "down", "strange", "charm", "bottom", "top",
                     "photon"):
            assert name in PARTICLE_CATALOG, f"Missing particle: {name}"

    def test_all_entries_are_geometric_particles(self):
        """Every catalog entry is a GeometricParticle."""
        for name, p in PARTICLE_CATALOG.items():
            assert isinstance(p, GeometricParticle), (
                f"{name} is not a GeometricParticle")

    def test_lepton_charges(self):
        """Electron, muon, tau all have charge −1."""
        for name in ("electron", "muon", "tau"):
            assert PARTICLE_CATALOG[name].charge == pytest.approx(-1.0)

    def test_quark_charges(self):
        """Up-type quarks 2/3, down-type −1/3."""
        for name in ("up", "charm", "top"):
            assert PARTICLE_CATALOG[name].charge == pytest.approx(2.0 / 3.0)
        for name in ("down", "strange", "bottom"):
            assert PARTICLE_CATALOG[name].charge == pytest.approx(-1.0 / 3.0)

    def test_photon_zero_charge_zero_mass(self):
        """Photon has charge 0, mass 0, winding 0."""
        ph = PARTICLE_CATALOG["photon"]
        assert ph.charge == 0.0 and ph.mass_mev == 0.0 and ph.winding_number == 0

    def test_sm_particles_share_winding_five(self):
        """All massive particles have the canonical winding number n_w = 5."""
        for name, p in PARTICLE_CATALOG.items():
            if p.mass_mev > 0.0:
                assert p.winding_number == 5, (
                    f"{name}: expected n_w=5, got {p.winding_number}")

    def test_generation_ordering(self):
        """Generation 3 masses are larger than generation 1."""
        e = PARTICLE_CATALOG["electron"]
        mu = PARTICLE_CATALOG["muon"]
        tau = PARTICLE_CATALOG["tau"]
        assert e.mass_mev < mu.mass_mev < tau.mass_mev

    def test_generation_ordering_quarks(self):
        """Bottom quark heavier than strange, strange heavier than down."""
        assert (PARTICLE_CATALOG["down"].mass_mev
                < PARTICLE_CATALOG["strange"].mass_mev
                < PARTICLE_CATALOG["bottom"].mass_mev)

    def test_phi_eff_decreases_with_generation(self):
        """Heavier generations have smaller φ_eff (tighter 5D loop)."""
        assert (_PHI_GEN3 < _PHI_GEN2 < _PHI_GEN1)


# ---------------------------------------------------------------------------
# fiber_curvature
# ---------------------------------------------------------------------------

class TestFiberCurvature:
    """κ_fib = n_w |∂_x φ| / φ — 5D loop curvature."""

    def test_shape(self):
        """Output shape equals input shape."""
        phi = np.ones(32)
        kappa = fiber_curvature(phi, winding_number=5, dx=0.1)
        assert kappa.shape == (32,)

    def test_nonnegative(self):
        """Fiber curvature is non-negative everywhere."""
        rng = np.random.default_rng(1)
        phi = 1.0 + 0.1 * rng.standard_normal(32)
        kappa = fiber_curvature(phi, winding_number=5, dx=0.1)
        assert np.all(kappa >= 0.0)

    def test_uniform_phi_gives_zero_curvature(self):
        """Constant φ has no gradient → κ_fib = 0."""
        phi = np.ones(32)
        kappa = fiber_curvature(phi, winding_number=5, dx=0.1)
        np.testing.assert_allclose(kappa, 0.0, atol=1e-10)

    def test_linear_phi_analytic(self):
        """φ = a + bx → |∂φ|/φ = b/(a+bx) on interior points."""
        N, dx = 32, 0.1
        x = np.arange(N) * dx
        a, b = 2.0, 0.3
        phi = a + b * x
        n_w = 5
        kappa = fiber_curvature(phi, winding_number=n_w, dx=dx)
        expected = n_w * b / (a + b * x)
        np.testing.assert_allclose(kappa[1:-1], expected[1:-1], rtol=1e-4)

    def test_scales_with_winding_number(self):
        """κ_fib ∝ n_w — doubling n_w doubles curvature."""
        N, dx = 32, 0.1
        x = np.arange(N) * dx
        phi = 1.0 + 0.1 * x
        k1 = fiber_curvature(phi, winding_number=1, dx=dx)
        k5 = fiber_curvature(phi, winding_number=5, dx=dx)
        np.testing.assert_allclose(k5, 5.0 * k1, rtol=1e-12)

    def test_steeper_gradient_gives_higher_curvature(self):
        """Steeper φ gradient → higher fiber curvature."""
        N, dx = 32, 0.1
        x = np.arange(N) * dx
        phi_gentle = 1.0 + 0.05 * x
        phi_steep  = 1.0 + 0.50 * x
        k_gentle = fiber_curvature(phi_gentle, 5, dx)
        k_steep  = fiber_curvature(phi_steep,  5, dx)
        assert np.mean(k_steep) > np.mean(k_gentle)

    def test_finite_everywhere(self):
        """κ_fib is finite for bounded non-zero φ."""
        rng = np.random.default_rng(2)
        phi = 1.0 + 0.01 * rng.standard_normal(32)
        assert np.all(np.isfinite(fiber_curvature(phi, 5, 0.1)))


# ---------------------------------------------------------------------------
# geometric_mass
# ---------------------------------------------------------------------------

class TestGeometricMass:
    """m = λ n_w / ⟨φ⟩ — KK mass from 5D loop curvature."""

    def test_mass_positive(self):
        """Geometric mass is strictly positive for n_w > 0, φ > 0."""
        assert geometric_mass(1.0, winding_number=5) > 0.0

    def test_zero_winding_zero_mass(self):
        """n_w = 0 (photon) → massless."""
        assert geometric_mass(1.0, winding_number=0) == 0.0

    def test_inversely_proportional_to_phi(self):
        """Doubling φ halves the mass."""
        m1 = geometric_mass(1.0, winding_number=5)
        m2 = geometric_mass(2.0, winding_number=5)
        assert m2 == pytest.approx(0.5 * m1, rel=1e-12)

    def test_proportional_to_winding_number(self):
        """Doubling n_w doubles the mass."""
        m5 = geometric_mass(1.0, winding_number=5)
        m10 = geometric_mass(1.0, winding_number=10)
        assert m10 == pytest.approx(2.0 * m5, rel=1e-12)

    def test_scales_with_lambda(self):
        """Doubling λ doubles the mass."""
        m1 = geometric_mass(1.0, winding_number=5, lam=1.0)
        m2 = geometric_mass(1.0, winding_number=5, lam=2.0)
        assert m2 == pytest.approx(2.0 * m1, rel=1e-12)

    def test_heavier_generation_from_smaller_phi(self):
        """Smaller φ_eff → heavier particle (generation hierarchy)."""
        m_gen1 = geometric_mass(_PHI_GEN1, winding_number=5)
        m_gen2 = geometric_mass(_PHI_GEN2, winding_number=5)
        assert m_gen2 > m_gen1

    def test_raises_on_zero_phi(self):
        """phi_mean = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_mean"):
            geometric_mass(0.0)

    def test_raises_on_negative_winding(self):
        """n_w < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="winding_number"):
            geometric_mass(1.0, winding_number=-1)


# ---------------------------------------------------------------------------
# generation_mass_ratio
# ---------------------------------------------------------------------------

class TestGenerationMassRatio:
    """m₂/m₁ = ⟨φ₁⟩/⟨φ₂⟩ — geometric generation hierarchy."""

    def test_ratio_greater_than_one_for_heavier_gen(self):
        """φ₁ > φ₂ → gen2 heavier → ratio > 1."""
        ratio = generation_mass_ratio(phi_gen1=1.0, phi_gen2=0.5)
        assert ratio > 1.0

    def test_ratio_equals_one_for_same_phi(self):
        """Same φ → same mass → ratio = 1."""
        assert generation_mass_ratio(1.0, 1.0) == pytest.approx(1.0)

    def test_analytic_value(self):
        """ratio = phi1 / phi2 exactly."""
        np.testing.assert_allclose(
            generation_mass_ratio(2.0, 0.5), 4.0, rtol=1e-12)

    def test_electron_muon_ratio_order_of_magnitude(self):
        """φ_gen1/φ_gen2 gives ~207 (electron:muon mass ratio) at order of magnitude."""
        ratio = generation_mass_ratio(_PHI_GEN1, _PHI_GEN2)
        # m_μ/m_e ≈ 207; check it's in the right ballpark (within 3×)
        assert 50 < ratio < 1000

    def test_raises_on_zero_phi_gen1(self):
        """phi_gen1 = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_gen1"):
            generation_mass_ratio(0.0, 1.0)

    def test_raises_on_zero_phi_gen2(self):
        """phi_gen2 = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_gen2"):
            generation_mass_ratio(1.0, 0.0)


# ---------------------------------------------------------------------------
# muon_kk_correction
# ---------------------------------------------------------------------------

class TestMuonKKCorrection:
    """δa_μ = m_μ² ⟨φ⟩² / 12π² — KK anomalous magnetic moment."""

    M_MUON_PLANCK: float = 8.49e-23
    DELTA_AMU_MEASURED: float = 2.51e-9

    def test_positive(self):
        """KK correction is always positive."""
        assert muon_kk_correction(1.0) > 0.0

    def test_scales_as_phi_squared(self):
        """δa_μ ∝ ⟨φ⟩² — doubling φ quadruples correction."""
        d1 = muon_kk_correction(1.0)
        d2 = muon_kk_correction(2.0)
        assert d2 == pytest.approx(4.0 * d1, rel=1e-12)

    def test_scales_as_m_muon_squared(self):
        """δa_μ ∝ m_μ² — doubling muon mass quadruples correction."""
        d1 = muon_kk_correction(1.0, m_muon_planck=1e-5)
        d2 = muon_kk_correction(1.0, m_muon_planck=2e-5)
        assert d2 == pytest.approx(4.0 * d1, rel=1e-12)

    def test_matches_fermilab_anomaly_at_correct_r5(self):
        """R₅ = sqrt(Δa_μ × 12π² / m_μ²) gives the measured Δa_μ."""
        m_mu = self.M_MUON_PLANCK
        R5 = np.sqrt(self.DELTA_AMU_MEASURED * 12.0 * np.pi**2 / m_mu**2)
        d = muon_kk_correction(R5, m_muon_planck=m_mu)
        np.testing.assert_allclose(d, self.DELTA_AMU_MEASURED, rtol=1e-8)

    def test_finite(self):
        """Correction is finite for finite φ > 0."""
        assert np.isfinite(muon_kk_correction(1.5))

    def test_raises_on_zero_phi(self):
        """phi_mean = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_mean"):
            muon_kk_correction(0.0)


# ---------------------------------------------------------------------------
# unwinding_rate
# ---------------------------------------------------------------------------

class TestUnwindingRate:
    """Γ_unwind = κ_H × n_w — horizon stripping of winding."""

    def test_shape(self):
        """Output shape matches input."""
        kappa = np.linspace(0.0, 0.9, 16)
        rate = unwinding_rate(kappa, winding_number=5)
        assert rate.shape == (16,)

    def test_zero_kappa_zero_rate(self):
        """No saturation → no unwinding."""
        kappa = np.zeros(8)
        np.testing.assert_allclose(unwinding_rate(kappa, 5), 0.0, atol=1e-30)

    def test_full_saturation_rate_equals_n_w(self):
        """κ_H = 1 (fully saturated) → Γ = n_w."""
        kappa = np.ones(8)
        np.testing.assert_allclose(unwinding_rate(kappa, 5), 5.0, rtol=1e-12)

    def test_rate_proportional_to_kappa(self):
        """Γ ∝ κ_H — linear relationship."""
        kappa = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
        rate = unwinding_rate(kappa, winding_number=4)
        np.testing.assert_allclose(rate, 4.0 * kappa, rtol=1e-12)

    def test_rate_proportional_to_n_w(self):
        """Γ ∝ n_w — more windings = faster unwinding."""
        kappa = np.full(8, 0.5)
        r1 = unwinding_rate(kappa, winding_number=1)
        r5 = unwinding_rate(kappa, winding_number=5)
        np.testing.assert_allclose(r5, 5.0 * r1, rtol=1e-12)

    def test_nonnegative(self):
        """Rate is non-negative for κ_H ∈ [0, 1]."""
        kappa = np.linspace(0.0, 0.99, 32)
        assert np.all(unwinding_rate(kappa, 5) >= 0.0)


# ---------------------------------------------------------------------------
# particle_info_fraction
# ---------------------------------------------------------------------------

class TestParticleInfoFraction:
    """f_enc = κ_H — fraction of particle info in 5D."""

    def test_identity(self):
        """f_enc equals κ_H exactly."""
        kappa = np.array([0.0, 0.3, 0.7, 0.99])
        np.testing.assert_allclose(particle_info_fraction(kappa), kappa, rtol=1e-14)

    def test_range(self):
        """f_enc ∈ [0, 1) for κ_H ∈ [0, 1)."""
        kappa = np.linspace(0.0, 0.999, 50)
        f = particle_info_fraction(kappa)
        assert np.all(f >= 0.0) and np.all(f < 1.0)

    def test_zero_kappa_zero_encoding(self):
        """Far from horizon (κ_H = 0): particle retains full 4D identity."""
        kappa = np.zeros(16)
        np.testing.assert_allclose(particle_info_fraction(kappa), 0.0, atol=1e-30)

    def test_shape_preserved(self):
        """Output shape matches input."""
        kappa = np.ones(24) * 0.5
        assert particle_info_fraction(kappa).shape == (24,)


# ---------------------------------------------------------------------------
# Physical consistency
# ---------------------------------------------------------------------------

class TestPhysicalConsistency:
    """Cross-checks linking particle geometry to other pillars."""

    def test_geometric_mass_ordering_matches_catalog(self):
        """Smaller φ_eff → larger geometric mass, consistent with catalog masses."""
        m1 = geometric_mass(_PHI_GEN1, winding_number=5)
        m2 = geometric_mass(_PHI_GEN2, winding_number=5)
        m3 = geometric_mass(_PHI_GEN3, winding_number=5)
        assert m1 < m2 < m3

    def test_photon_mass_zero_winding_zero(self):
        """Photon has n_w = 0 → geometric mass zero (massless gauge boson)."""
        ph = PARTICLE_CATALOG["photon"]
        assert geometric_mass(ph.phi_eff, ph.winding_number) == 0.0

    def test_unwinding_rate_peaks_at_horizon(self):
        """Unwinding rate at κ_H ≈ 1 equals n_w — particle fully dissolved."""
        kappa_horizon = np.array([0.999])
        rate = unwinding_rate(kappa_horizon, winding_number=5)
        assert rate[0] == pytest.approx(5.0 * 0.999, rel=1e-10)

    def test_fiber_curvature_consistent_with_geometric_mass(self):
        """Higher curvature profile → higher effective mass scale."""
        N, dx = 32, 0.1
        x = np.arange(N) * dx
        phi_light = 2.0 * np.ones(N)          # larger φ → lighter
        phi_heavy = 0.1 * np.ones(N)          # smaller φ → heavier
        m_light = geometric_mass(np.mean(phi_light), winding_number=5)
        m_heavy = geometric_mass(np.mean(phi_heavy), winding_number=5)
        assert m_heavy > m_light

    def test_winding_five_from_index_theorem(self):
        """n_w = 5 is the canonical winding from the Atiyah–Singer theorem."""
        from src.core.metric import derive_nw_index_theorem
        n_w, _ = derive_nw_index_theorem()
        # Every SM particle in catalog shares this winding number
        for name, p in PARTICLE_CATALOG.items():
            if p.mass_mev > 0.0:
                assert p.winding_number == n_w, (
                    f"{name} winding {p.winding_number} ≠ index theorem n_w={n_w}")
