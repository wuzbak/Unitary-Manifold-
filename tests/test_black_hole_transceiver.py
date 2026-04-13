"""
tests/test_black_hole_transceiver.py
=====================================
Tests for src/core/black_hole_transceiver.py

Covers all public API functions and the HorizonTransceiver class:

    horizon_saturation           — κ_H ∈ [0, 1), peaks at horizon
    geometric_encoding_density   — ρ_enc ≥ 0, vanishes for flat B
    winding_redistribution       — channels sum exactly to encoded_info
    HorizonTransceiver.encode    — delegates to geometric_encoding_density
    HorizonTransceiver.decode    — channels + total consistency
    HorizonTransceiver.transceiver_gain  — ≈ 1 (information conservation)
    HorizonTransceiver.horizon_location  — returns valid grid index
    HorizonTransceiver.horizon_entropy   — ≥ 0, scales with B amplitude

    alpha_drift                  — Δα = 1/φ_today² − 1/φ_early² (Hubble tension)
    hubble_tension_ratio         — H_local / H_CMB = φ_CMB / φ_today
    gw_echo_delay                — τ_echo = 2π⟨φ⟩
    gw_echo_spectrum             — times, amplitudes; energy conservation
"""

import numpy as np
import pytest

from src.core.black_hole_transceiver import (
    HorizonTransceiver,
    alpha_drift,
    geometric_encoding_density,
    gw_echo_delay,
    gw_echo_spectrum,
    horizon_saturation,
    hubble_tension_ratio,
    winding_redistribution,
)
from src.core.evolution import FieldState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_state(N=32, dx=0.1, rng_seed=0):
    """Flat Minkowski FieldState with small random perturbations."""
    return FieldState.flat(N=N, dx=dx, rng=np.random.default_rng(rng_seed))


def _state_with_horizon(N=64, dx=0.1, x_h=3.2):
    """FieldState with a Gaussian B-field spike at x_h (simulated horizon)."""
    x = np.arange(N) * dx
    g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
    phi = np.ones(N)
    B = np.zeros((N, 4))
    # Strong B-field localised near x_h
    amplitude = 2.0 * np.exp(-((x - x_h) ** 2) / 0.2)
    B[:, 1] = amplitude
    return FieldState(g=g, B=B, phi=phi, t=0.0, dx=dx)


# ---------------------------------------------------------------------------
# horizon_saturation
# ---------------------------------------------------------------------------

class TestHorizonSaturation:
    """κ_H = λ²φ²|B|² / (1 + λ²φ²|B|²) — saturation parameter tests."""

    def test_shape(self):
        """Output shape matches the number of grid points."""
        state = _flat_state(N=16)
        kappa = horizon_saturation(state.B, state.phi)
        assert kappa.shape == (16,)

    def test_range(self):
        """κ_H is in [0, 1) everywhere."""
        state = _flat_state(N=32)
        kappa = horizon_saturation(state.B, state.phi)
        assert np.all(kappa >= 0.0)
        assert np.all(kappa < 1.0)

    def test_zero_B_gives_zero_saturation(self):
        """No field → no saturation: κ_H = 0."""
        N = 16
        phi = np.ones(N)
        B = np.zeros((N, 4))
        kappa = horizon_saturation(B, phi)
        np.testing.assert_allclose(kappa, 0.0, atol=1e-30)

    def test_larger_B_gives_higher_saturation(self):
        """Stronger B-field → higher saturation."""
        N = 16
        phi = np.ones(N)
        B_weak  = 0.1 * np.ones((N, 4))
        B_strong = 5.0 * np.ones((N, 4))
        kappa_weak   = horizon_saturation(B_weak,  phi)
        kappa_strong = horizon_saturation(B_strong, phi)
        assert np.all(kappa_strong > kappa_weak)

    def test_larger_phi_gives_higher_saturation(self):
        """Larger radion φ → higher saturation (coupling α = 1/φ² ↓ but λφ|B| ↑)."""
        N = 16
        B = 0.5 * np.ones((N, 4))
        phi_small = np.full(N, 0.5)
        phi_large = np.full(N, 2.0)
        kappa_small = horizon_saturation(B, phi_small)
        kappa_large = horizon_saturation(B, phi_large)
        assert np.all(kappa_large > kappa_small)

    def test_saturation_monotone_in_lam(self):
        """Larger λ → larger saturation."""
        N = 16
        B = np.ones((N, 4))
        phi = np.ones(N)
        k1 = horizon_saturation(B, phi, lam=0.5)
        k2 = horizon_saturation(B, phi, lam=2.0)
        assert np.all(k2 > k1)

    def test_horizon_localised_at_B_spike(self):
        """argmax κ_H is close to the grid point with the largest |B|."""
        state = _state_with_horizon(N=64, dx=0.1, x_h=3.2)
        kappa = horizon_saturation(state.B, state.phi)
        idx_kappa = np.argmax(kappa)
        idx_B = np.argmax(np.sum(state.B ** 2, axis=1))
        assert abs(idx_kappa - idx_B) <= 1

    def test_finite_everywhere(self):
        """κ_H is finite for bounded, non-degenerate fields."""
        state = _flat_state(N=32)
        kappa = horizon_saturation(state.B, state.phi)
        assert np.all(np.isfinite(kappa))


# ---------------------------------------------------------------------------
# geometric_encoding_density
# ---------------------------------------------------------------------------

class TestGeometricEncodingDensity:
    """ρ_enc = φ² λ² H_μν H^μν — 5D topological encoding tests."""

    def test_shape(self):
        """Output shape matches the number of grid points."""
        state = _flat_state(N=16)
        rho = geometric_encoding_density(state.B, state.phi, state.dx)
        assert rho.shape == (16,)

    def test_nonnegative(self):
        """Encoding density is non-negative (H_μν H^μν ≥ 0 for antisymmetric H)."""
        state = _flat_state(N=32)
        rho = geometric_encoding_density(state.B, state.phi, state.dx)
        assert np.all(rho >= 0.0)

    def test_uniform_B_gives_zero_encoding(self):
        """Perfectly uniform B has no gradients → H = 0 → ρ_enc = 0."""
        N = 32
        phi = np.ones(N)
        B = np.ones((N, 4))   # constant → ∂B = 0 → H = 0
        rho = geometric_encoding_density(B, phi, dx=0.1)
        np.testing.assert_allclose(rho, 0.0, atol=1e-10)

    def test_larger_B_gradient_gives_larger_encoding(self):
        """Steeper B gradient → stronger H → more encoding."""
        N = 32
        dx = 0.1
        x = np.arange(N) * dx
        phi = np.ones(N)
        B_gentle = np.zeros((N, 4))
        B_steep  = np.zeros((N, 4))
        B_gentle[:, 1] = 0.1 * x
        B_steep[:, 1]  = 1.0 * x
        rho_gentle = geometric_encoding_density(B_gentle, phi, dx)
        rho_steep  = geometric_encoding_density(B_steep,  phi, dx)
        assert np.mean(rho_steep) > np.mean(rho_gentle)

    def test_larger_phi_amplifies_encoding(self):
        """Larger φ multiplies ρ_enc by φ² (radion weight)."""
        N = 32
        dx = 0.1
        x = np.arange(N) * dx
        B = np.zeros((N, 4))
        B[:, 1] = 0.5 * x
        phi1 = np.ones(N)
        phi2 = 2.0 * np.ones(N)
        rho1 = geometric_encoding_density(B, phi1, dx)
        rho2 = geometric_encoding_density(B, phi2, dx)
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-10)

    def test_lam_scales_quadratically(self):
        """ρ_enc ∝ λ² — doubling λ quadruples encoding density."""
        N = 32
        dx = 0.1
        x = np.arange(N) * dx
        phi = np.ones(N)
        B = np.zeros((N, 4))
        B[:, 1] = 0.3 * x
        rho1 = geometric_encoding_density(B, phi, dx, lam=1.0)
        rho2 = geometric_encoding_density(B, phi, dx, lam=2.0)
        np.testing.assert_allclose(rho2, 4.0 * rho1, rtol=1e-10)

    def test_finite_everywhere(self):
        """ρ_enc is finite for a well-posed field state."""
        state = _flat_state(N=32)
        rho = geometric_encoding_density(state.B, state.phi, state.dx)
        assert np.all(np.isfinite(rho))


# ---------------------------------------------------------------------------
# winding_redistribution
# ---------------------------------------------------------------------------

class TestWindingRedistribution:
    """Channels sum exactly to encoded_info — global unitarity."""

    def test_default_n_w_is_five(self):
        """Default winding number is n_w = 5 (Atiyah–Singer)."""
        rho = np.ones(16)
        channels, _ = winding_redistribution(rho)
        assert channels.shape[0] == 5

    def test_channels_shape(self):
        """channels has shape (n_w, N)."""
        N, n_w = 32, 5
        rho = np.random.default_rng(1).random(N)
        channels, _ = winding_redistribution(rho, n_w)
        assert channels.shape == (n_w, N)

    def test_total_equals_encoded(self):
        """Sum of all channels exactly recovers encoded_info (unitarity)."""
        rng = np.random.default_rng(2)
        rho = rng.random(64)
        _, total = winding_redistribution(rho, n_w=5)
        np.testing.assert_allclose(total, rho, rtol=1e-14)

    def test_each_channel_equal_fraction(self):
        """Each winding channel carries exactly 1/n_w of the encoded density."""
        N, n_w = 32, 5
        rho = np.full(N, 10.0)
        channels, _ = winding_redistribution(rho, n_w)
        for k in range(n_w):
            np.testing.assert_allclose(channels[k], rho / n_w, rtol=1e-14)

    def test_n_w_one_returns_identity(self):
        """n_w = 1: single channel = encoded_info."""
        rho = np.arange(1.0, 9.0)
        channels, total = winding_redistribution(rho, n_w=1)
        np.testing.assert_allclose(channels[0], rho, rtol=1e-14)
        np.testing.assert_allclose(total, rho, rtol=1e-14)

    def test_total_scales_with_amplitude(self):
        """Doubling ρ_enc doubles the total redistributed output."""
        rho = np.ones(16)
        _, total1 = winding_redistribution(rho,       n_w=5)
        _, total2 = winding_redistribution(2.0 * rho, n_w=5)
        np.testing.assert_allclose(total2, 2.0 * total1, rtol=1e-14)

    def test_n_w_zero_raises(self):
        """n_w = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="n_w must be"):
            winding_redistribution(np.ones(8), n_w=0)

    def test_n_w_negative_raises(self):
        """n_w < 0 must raise ValueError."""
        with pytest.raises(ValueError, match="n_w must be"):
            winding_redistribution(np.ones(8), n_w=-3)


# ---------------------------------------------------------------------------
# HorizonTransceiver
# ---------------------------------------------------------------------------

class TestHorizonTransceiver:
    """Full encode → decode pipeline and derived quantities."""

    def test_encode_shape(self):
        """encode returns shape (N,)."""
        state = _flat_state(N=32)
        ht = HorizonTransceiver()
        rho = ht.encode(state)
        assert rho.shape == (32,)

    def test_encode_nonnegative(self):
        """encode output is non-negative."""
        state = _flat_state(N=32)
        rho = HorizonTransceiver().encode(state)
        assert np.all(rho >= 0.0)

    def test_decode_channels_shape(self):
        """decode channels have shape (n_w, N)."""
        state = _flat_state(N=32)
        ht = HorizonTransceiver(n_w=5)
        channels, _ = ht.decode(state)
        assert channels.shape == (5, 32)

    def test_decode_total_equals_encode(self):
        """Total decoded output exactly equals encoded density (unitarity)."""
        state = _flat_state(N=32)
        ht = HorizonTransceiver()
        rho_enc = ht.encode(state)
        _, total = ht.decode(state)
        np.testing.assert_allclose(total, rho_enc, rtol=1e-14)

    def test_transceiver_gain_is_one(self):
        """Gain = ∫ decoded / ∫ encoded = 1 exactly."""
        state = _flat_state(N=32)
        gain = HorizonTransceiver().transceiver_gain(state)
        assert gain == pytest.approx(1.0, rel=1e-12)

    def test_transceiver_gain_flat_B_is_one(self):
        """Even with zero encoding (flat B), gain returns 1.0 gracefully."""
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi = np.ones(N)
        B = np.zeros((N, 4))   # flat → H = 0 → ρ_enc = 0
        state = FieldState(g=g, B=B, phi=phi, t=0.0, dx=0.1)
        gain = HorizonTransceiver().transceiver_gain(state)
        assert gain == pytest.approx(1.0)

    def test_horizon_location_returns_valid_index(self):
        """horizon_location returns an integer in [0, N)."""
        state = _flat_state(N=32)
        ht = HorizonTransceiver()
        idx = ht.horizon_location(state)
        assert isinstance(idx, int)
        assert 0 <= idx < 32

    def test_horizon_location_tracks_B_spike(self):
        """horizon_location is near the simulated B-field spike."""
        state = _state_with_horizon(N=64, dx=0.1, x_h=3.2)
        ht = HorizonTransceiver()
        idx = ht.horizon_location(state)
        x_h_idx = int(3.2 / 0.1)
        assert abs(idx - x_h_idx) <= 3

    def test_horizon_entropy_nonneg(self):
        """Horizon entropy is non-negative."""
        state = _flat_state(N=32)
        S_H = HorizonTransceiver().horizon_entropy(state)
        assert S_H >= 0.0

    def test_horizon_entropy_scales_with_B(self):
        """Larger B amplitude → larger horizon entropy."""
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi = np.ones(N)
        B_weak   = 0.1 * np.ones((N, 4))
        B_strong = 5.0 * np.ones((N, 4))
        ht = HorizonTransceiver()
        S_weak   = ht.horizon_entropy(
            FieldState(g=g, B=B_weak,   phi=phi, t=0.0, dx=0.1))
        S_strong = ht.horizon_entropy(
            FieldState(g=g, B=B_strong, phi=phi, t=0.0, dx=0.1))
        assert S_strong > S_weak

    def test_horizon_entropy_zero_B_gives_zero(self):
        """No B field → κ_H = 0 everywhere → S_H = 0."""
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi = np.ones(N)
        B = np.zeros((N, 4))
        ht = HorizonTransceiver()
        S_H = ht.horizon_entropy(
            FieldState(g=g, B=B, phi=phi, t=0.0, dx=0.1))
        assert S_H == pytest.approx(0.0, abs=1e-30)

    def test_custom_n_w_propagates(self):
        """HorizonTransceiver with n_w=3 produces 3 channels."""
        state = _flat_state(N=16)
        ht = HorizonTransceiver(n_w=3)
        channels, _ = ht.decode(state)
        assert channels.shape[0] == 3

    def test_lam_coupling_propagates(self):
        """Custom λ affects encode output consistently with standalone function."""
        state = _flat_state(N=16)
        lam = 3.0
        ht = HorizonTransceiver(lam=lam)
        rho_ht = ht.encode(state)
        rho_fn = geometric_encoding_density(state.B, state.phi, state.dx, lam=lam)
        np.testing.assert_allclose(rho_ht, rho_fn, rtol=1e-14)


# ---------------------------------------------------------------------------
# Physical consistency
# ---------------------------------------------------------------------------

class TestPhysicalConsistency:
    """Cross-module consistency checks linking transceiver to other pillars."""

    def test_horizon_entropy_increases_with_stronger_phi_coupling(self):
        """Higher φ boosts κ_H → more horizon area → higher S_H."""
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        B = 0.5 * np.ones((N, 4))
        phi_lo = np.full(N, 0.5)
        phi_hi = np.full(N, 2.0)
        ht = HorizonTransceiver()
        S_lo = ht.horizon_entropy(
            FieldState(g=g, B=B, phi=phi_lo, t=0.0, dx=0.1))
        S_hi = ht.horizon_entropy(
            FieldState(g=g, B=B, phi=phi_hi, t=0.0, dx=0.1))
        assert S_hi > S_lo

    def test_encoding_density_localised_at_horizon(self):
        """ρ_enc is largest near the B-spike (event horizon location)."""
        state = _state_with_horizon(N=64, dx=0.1, x_h=3.2)
        rho = geometric_encoding_density(state.B, state.phi, state.dx)
        x_h_idx = int(3.2 / 0.1)
        # Maximum encoding should be within a few grid points of the horizon
        assert abs(np.argmax(rho) - x_h_idx) <= 5

    def test_transceiver_gain_preserved_after_evolution(self):
        """Gain remains ≈ 1 after several evolution steps (dynamical state)."""
        from src.core.evolution import run_evolution
        state0 = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(99))
        history = run_evolution(state0, dt=1e-3, steps=5)
        ht = HorizonTransceiver()
        for s in history:
            gain = ht.transceiver_gain(s)
            assert gain == pytest.approx(1.0, rel=1e-12), (
                f"Gain deviated from 1 at t={s.t:.4f}: {gain}")

    def test_five_winding_modes_match_index_theorem(self):
        """Default n_w=5 matches derive_nw_index_theorem output."""
        from src.core.metric import derive_nw_index_theorem
        n_w, _ = derive_nw_index_theorem()
        ht = HorizonTransceiver()
        assert ht.n_w == n_w

    def test_saturation_bounded_by_bekenstein_entropy(self):
        """κ_H < 1 everywhere implies finite horizon entropy (no naked singularity)."""
        state = _state_with_horizon(N=64, dx=0.1, x_h=3.2)
        kappa = horizon_saturation(state.B, state.phi)
        assert np.all(kappa < 1.0)
        S_H = HorizonTransceiver().horizon_entropy(state)
        assert np.isfinite(S_H)


# ---------------------------------------------------------------------------
# Hubble Tension — α-drift tests
# ---------------------------------------------------------------------------

class TestAlphaDrift:
    """Δα = 1/φ_today² − 1/φ_early² — coupling drift resolves Hubble tension."""

    def test_drift_positive_when_phi_shrinks(self):
        """φ_today < φ_early → α_today > α_CMB → Δα > 0."""
        da = alpha_drift(phi_early=1.0831, phi_today=1.0)
        assert da > 0.0

    def test_drift_zero_when_phi_unchanged(self):
        """φ_today = φ_early → Δα = 0 (no tension)."""
        da = alpha_drift(phi_early=1.5, phi_today=1.5)
        assert da == pytest.approx(0.0, abs=1e-15)

    def test_drift_negative_when_phi_grows(self):
        """φ_today > φ_early → α decreases → Δα < 0."""
        da = alpha_drift(phi_early=0.8, phi_today=1.2)
        assert da < 0.0

    def test_drift_analytic_value(self):
        """Δα = 1/φ_today² − 1/φ_early² matches explicit formula."""
        phi_e, phi_t = 1.0831, 1.0
        expected = 1.0 / phi_t**2 - 1.0 / phi_e**2
        np.testing.assert_allclose(alpha_drift(phi_e, phi_t), expected, rtol=1e-12)

    def test_drift_finite_for_finite_phi(self):
        """Δα is finite for bounded non-zero φ."""
        da = alpha_drift(phi_early=2.0, phi_today=0.5)
        assert np.isfinite(da)

    def test_raises_on_zero_phi_early(self):
        """phi_early = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_early"):
            alpha_drift(0.0, 1.0)

    def test_raises_on_zero_phi_today(self):
        """phi_today = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_today"):
            alpha_drift(1.0, 0.0)

    def test_raises_on_negative_phi(self):
        """Negative φ must raise ValueError."""
        with pytest.raises(ValueError):
            alpha_drift(-1.0, 1.0)


class TestHubbleTensionRatio:
    """H_local / H_CMB = φ_CMB / φ_today — geometric prediction."""

    #: Observed Hubble constant values in km/s/Mpc
    H_CMB: float = 67.4    # Planck 2018 CMB measurement
    H_SNe: float = 73.0    # SH0ES supernova distance-ladder measurement

    def test_ratio_greater_than_one_for_larger_phi_cmb(self):
        """φ_CMB > φ_today → H_local > H_CMB → ratio > 1."""
        ratio = hubble_tension_ratio(phi_cmb=1.0831, phi_today=1.0)
        assert ratio > 1.0

    def test_ratio_equals_one_when_phi_equal(self):
        """Same φ → no tension → ratio = 1."""
        ratio = hubble_tension_ratio(phi_cmb=1.5, phi_today=1.5)
        assert ratio == pytest.approx(1.0, rel=1e-12)

    def test_predicted_ratio_bridges_hubble_tension(self):
        """φ_CMB = H_SNe/H_CMB → ratio = H_SNe/H_CMB (exact identity)."""
        phi_cmb = self.H_SNe / self.H_CMB     # ≈ 1.0831
        ratio = hubble_tension_ratio(phi_cmb=phi_cmb, phi_today=1.0)
        expected = self.H_SNe / self.H_CMB
        np.testing.assert_allclose(ratio, expected, rtol=1e-12)

    def test_predicted_H_local_in_tension_window(self):
        """H_local = H_CMB × ratio falls in [H_CMB, H_SNe + 1] km/s/Mpc."""
        phi_cmb = self.H_SNe / self.H_CMB
        ratio = hubble_tension_ratio(phi_cmb=phi_cmb)
        H_local = self.H_CMB * ratio
        assert self.H_CMB <= H_local <= self.H_SNe + 1.0

    def test_ratio_analytic(self):
        """ratio = phi_cmb / phi_today matches explicit formula."""
        phi_c, phi_t = 2.3, 0.7
        np.testing.assert_allclose(
            hubble_tension_ratio(phi_c, phi_t), phi_c / phi_t, rtol=1e-14)

    def test_raises_on_zero_phi_cmb(self):
        """phi_cmb = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_cmb"):
            hubble_tension_ratio(0.0)

    def test_raises_on_negative_phi_today(self):
        """phi_today ≤ 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_today"):
            hubble_tension_ratio(1.0, phi_today=-1.0)


# ---------------------------------------------------------------------------
# GW Echoes
# ---------------------------------------------------------------------------

class TestGWEchoDelay:
    """τ_echo = 2π⟨φ⟩ — echo delay from compact dimension."""

    def test_value_is_two_pi_phi(self):
        """τ_echo = 2π φ exactly."""
        for phi in [0.5, 1.0, 2.0, 5.0]:
            assert gw_echo_delay(phi) == pytest.approx(2.0 * np.pi * phi, rel=1e-12)

    def test_larger_phi_gives_longer_delay(self):
        """Larger compact dimension → longer round-trip → longer echo delay."""
        assert gw_echo_delay(2.0) > gw_echo_delay(1.0)

    def test_delay_positive(self):
        """Echo delay is always positive."""
        assert gw_echo_delay(0.001) > 0.0

    def test_delay_finite(self):
        """Echo delay is finite for finite φ."""
        assert np.isfinite(gw_echo_delay(1.0))

    def test_raises_on_zero_phi(self):
        """phi_mean = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="phi_mean"):
            gw_echo_delay(0.0)

    def test_raises_on_negative_phi(self):
        """phi_mean < 0 must raise ValueError."""
        with pytest.raises(ValueError):
            gw_echo_delay(-1.0)


class TestGWEchoSpectrum:
    """Echo amplitude series — times, decay, energy conservation."""

    def test_shape(self):
        """Returns arrays of length n_echoes."""
        times, amps = gw_echo_spectrum(1.0, n_echoes=5, echo_quality=10.0,
                                       phi_mean=1.0)
        assert times.shape == (5,) and amps.shape == (5,)

    def test_times_are_multiples_of_tau(self):
        """t_k = k × τ_echo."""
        phi = 1.5
        tau = gw_echo_delay(phi)
        times, _ = gw_echo_spectrum(1.0, n_echoes=4, echo_quality=10.0,
                                    phi_mean=phi)
        expected = np.arange(1, 5) * tau
        np.testing.assert_allclose(times, expected, rtol=1e-12)

    def test_amplitudes_decrease_monotonically(self):
        """Echoes decay: A_1 > A_2 > … (damped cavity)."""
        _, amps = gw_echo_spectrum(1.0, n_echoes=6, echo_quality=3.0,
                                   phi_mean=1.0)
        assert np.all(np.diff(amps) < 0.0)

    def test_amplitudes_nonnegative(self):
        """All echo amplitudes are ≥ 0."""
        _, amps = gw_echo_spectrum(2.5, n_echoes=8, echo_quality=5.0,
                                   phi_mean=1.0)
        assert np.all(amps >= 0.0)

    def test_amplitudes_finite(self):
        """All amplitudes are finite."""
        _, amps = gw_echo_spectrum(1.0, n_echoes=10, echo_quality=2.0,
                                   phi_mean=0.5)
        assert np.all(np.isfinite(amps))

    def test_energy_bounded_by_total(self):
        """Sum of echo energies ≤ total_energy."""
        E = 3.7
        _, amps = gw_echo_spectrum(E, n_echoes=100, echo_quality=5.0,
                                   phi_mean=1.0)
        assert np.sum(amps) <= E + 1e-10

    def test_high_quality_factor_slower_decay(self):
        """Higher echo_quality → slower amplitude decay (smaller ratio A_k/A_1)."""
        _, amps_low  = gw_echo_spectrum(1.0, 5, echo_quality=1.0,  phi_mean=1.0)
        _, amps_high = gw_echo_spectrum(1.0, 5, echo_quality=20.0, phi_mean=1.0)
        # Higher quality = less damping → last/first ratio closer to 1
        ratio_low  = amps_low[-1]  / (amps_low[0]  + 1e-30)
        ratio_high = amps_high[-1] / (amps_high[0] + 1e-30)
        assert ratio_high > ratio_low

    def test_larger_phi_shifts_echo_times(self):
        """Larger ⟨φ⟩ → later echo arrival times."""
        t1, _ = gw_echo_spectrum(1.0, 3, echo_quality=5.0, phi_mean=1.0)
        t2, _ = gw_echo_spectrum(1.0, 3, echo_quality=5.0, phi_mean=2.0)
        assert np.all(t2 > t1)

    def test_zero_energy_gives_zero_amplitudes(self):
        """No merger energy → no echoes."""
        _, amps = gw_echo_spectrum(0.0, n_echoes=5, echo_quality=5.0,
                                   phi_mean=1.0)
        np.testing.assert_allclose(amps, 0.0, atol=1e-30)

    def test_raises_on_n_echoes_zero(self):
        """n_echoes = 0 must raise ValueError."""
        with pytest.raises(ValueError, match="n_echoes"):
            gw_echo_spectrum(1.0, 0, 5.0, 1.0)

    def test_raises_on_negative_quality(self):
        """echo_quality ≤ 0 must raise ValueError."""
        with pytest.raises(ValueError, match="echo_quality"):
            gw_echo_spectrum(1.0, 5, 0.0, 1.0)

    def test_raises_on_negative_energy(self):
        """Negative total_energy must raise ValueError."""
        with pytest.raises(ValueError, match="total_energy"):
            gw_echo_spectrum(-1.0, 5, 5.0, 1.0)

    def test_echo_delay_consistent_with_standalone(self):
        """First echo time equals gw_echo_delay(phi_mean)."""
        phi = 0.8
        times, _ = gw_echo_spectrum(1.0, 3, echo_quality=5.0, phi_mean=phi)
        assert times[0] == pytest.approx(gw_echo_delay(phi), rel=1e-12)
