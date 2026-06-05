"""
tests/test_pillar511_braid_winding_observable.py
=================================================
Tests for Pillar 511 — Braid Winding Number as a Dynamic Observable.

Verifies that braid_winding_number(), FieldState.initialize_dynamic_braid(),
and FieldState.get_winding_number() are correctly implemented and that the
winding number behaves as an integer topological invariant.
"""

import numpy as np
import pytest

from src.core.evolution import (
    FieldState,
    braid_winding_number,
)
from src.core.pillar511_braid_winding_observable import pillar_report, PILLAR_STATUS


# ---------------------------------------------------------------------------
# Pillar report
# ---------------------------------------------------------------------------

class TestPillar511Report:
    def test_pillar_number(self):
        r = pillar_report()
        assert r["pillar"] == 511

    def test_pillar_status_string(self):
        assert PILLAR_STATUS == "BRAID_WINDING_OBSERVABLE_CERTIFIED"

    def test_report_contains_braid_triad(self):
        r = pillar_report()
        assert r["braid_triad"] == (5, 7, 74)

    def test_report_cs_level(self):
        r = pillar_report()
        assert r["cs_level_k"] == 74


# ---------------------------------------------------------------------------
# braid_winding_number: basic properties
# ---------------------------------------------------------------------------

class TestBraidWindingNumberBasic:
    def test_returns_integer(self):
        N = 32
        phi = np.cos(2.0 * np.pi * 1 * np.arange(N) / N)
        result = braid_winding_number(phi, dx=1.0)
        assert isinstance(result, int)

    def test_zero_winding_for_constant_field(self):
        """A constant positive field has no phase winding."""
        phi = np.ones(32) * 2.0
        assert braid_winding_number(phi, dx=0.1) == 0

    def test_zero_winding_for_constant_negative_field(self):
        """A constant negative field also has no phase winding."""
        phi = -np.ones(32)
        assert braid_winding_number(phi, dx=0.1) == 0

    def test_cosine_mode_n1(self):
        """phi = cos(2pi*1*x/L) should yield winding number 1 (absolute value)."""
        N = 64
        dx = 0.05
        L = N * dx
        x = np.arange(N) * dx
        phi = np.cos(2.0 * np.pi * 1 * x / L)
        n_w = braid_winding_number(phi, dx)
        assert abs(n_w) == 1

    def test_cosine_mode_n3(self):
        """phi = cos(2pi*3*x/L) should yield |n_w| = 3."""
        N = 128
        dx = 0.05
        L = N * dx
        x = np.arange(N) * dx
        phi = np.cos(2.0 * np.pi * 3 * x / L)
        n_w = braid_winding_number(phi, dx)
        assert abs(n_w) == 3

    def test_cosine_mode_n5(self):
        """phi = cos(2pi*5*x/L) should yield |n_w| = 5 (canonical UM sector)."""
        N = 256
        dx = 0.05
        L = N * dx
        x = np.arange(N) * dx
        phi = np.cos(2.0 * np.pi * 5 * x / L)
        n_w = braid_winding_number(phi, dx)
        assert abs(n_w) == 5

    def test_scaling_invariance(self):
        """Winding number is invariant under amplitude scaling."""
        N = 64
        dx = 0.05
        L = N * dx
        x = np.arange(N) * dx
        phi_base = np.cos(2.0 * np.pi * 2 * x / L)
        n1 = braid_winding_number(phi_base, dx)
        n2 = braid_winding_number(3.7 * phi_base, dx)
        assert abs(n1) == abs(n2)

    def test_dx_does_not_change_winding(self):
        """Changing dx by a factor of 2 should not change the winding number."""
        N = 64
        for n_w in [1, 2]:
            L1, L2 = N * 0.05, N * 0.1
            x1 = np.arange(N) * 0.05
            x2 = np.arange(N) * 0.1
            phi1 = np.cos(2.0 * np.pi * n_w * x1 / L1)
            phi2 = np.cos(2.0 * np.pi * n_w * x2 / L2)
            assert abs(braid_winding_number(phi1, 0.05)) == n_w
            assert abs(braid_winding_number(phi2, 0.1)) == n_w


# ---------------------------------------------------------------------------
# FieldState.initialize_dynamic_braid
# ---------------------------------------------------------------------------

class TestInitializeDynamicBraid:
    def test_shape_g(self):
        s = FieldState.initialize_dynamic_braid(N=32, n_w_initial=1, dx=0.1)
        assert s.g.shape == (32, 4, 4)

    def test_shape_phi(self):
        s = FieldState.initialize_dynamic_braid(N=32, n_w_initial=1, dx=0.1)
        assert s.phi.shape == (32,)

    def test_metric_is_exact_minkowski(self):
        """initialize_dynamic_braid uses exact Minkowski (no noise)."""
        s = FieldState.initialize_dynamic_braid(N=32, n_w_initial=1, dx=0.1)
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        np.testing.assert_allclose(s.g, eta[None, :, :], atol=1e-15)

    def test_winding_number_matches_request(self):
        """Winding number of the factory output must equal |n_w_initial|."""
        for n_w in [1, 2, 3]:
            s = FieldState.initialize_dynamic_braid(N=128, n_w_initial=n_w, dx=0.05)
            assert abs(s.get_winding_number()) == n_w

    def test_amplitude_parameter(self):
        """amplitude parameter sets the max of phi."""
        amp = 2.5
        s = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05, amplitude=amp)
        assert abs(float(np.max(np.abs(s.phi))) - amp) < 1e-12

    def test_rejects_zero_amplitude(self):
        with pytest.raises(ValueError, match="amplitude must be positive"):
            FieldState.initialize_dynamic_braid(N=32, n_w_initial=1, dx=0.1, amplitude=0.0)

    def test_rejects_insufficient_grid(self):
        """Must have N >= 4 * n_w grid points."""
        with pytest.raises(ValueError, match="insufficient for n_w_initial"):
            FieldState.initialize_dynamic_braid(N=8, n_w_initial=5, dx=0.1)

    def test_b_field_is_zero(self):
        s = FieldState.initialize_dynamic_braid(N=32, n_w_initial=1, dx=0.1)
        np.testing.assert_allclose(s.B, 0.0, atol=1e-15)

    def test_time_zero(self):
        s = FieldState.initialize_dynamic_braid(N=32, n_w_initial=1, dx=0.1)
        assert s.t == 0.0


# ---------------------------------------------------------------------------
# FieldState.get_winding_number
# ---------------------------------------------------------------------------

class TestGetWindingNumber:
    def test_flat_state_has_winding_zero(self):
        """A flat state near phi=1 should have winding number 0."""
        s = FieldState.flat(N=32, dx=0.1, rng=np.random.default_rng(42))
        assert s.get_winding_number() == 0

    def test_braided_state_returns_correct_winding(self):
        for n_w in [1, 2]:
            s = FieldState.initialize_dynamic_braid(N=128, n_w_initial=n_w, dx=0.05)
            assert abs(s.get_winding_number()) == n_w
