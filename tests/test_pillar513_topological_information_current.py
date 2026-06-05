"""
tests/test_pillar513_topological_information_current.py
=======================================================
Tests for Pillar 513 — Topological Information Current.

Verifies that the winding_number parameter in information_current() applies the
Chern-Simons correction correctly, that information_current_topological() works
as a convenience wrapper, and that backward compatibility is fully preserved.
"""

import numpy as np
import pytest

from src.core.evolution import (
    FieldState,
    information_current,
    information_current_topological,
)
from src.core.pillar513_topological_information_current import (
    pillar_report,
    PILLAR_STATUS,
    K_CS,
    cs_correction_factor,
)


# ---------------------------------------------------------------------------
# Pillar report
# ---------------------------------------------------------------------------

class TestPillar513Report:
    def test_pillar_number(self):
        assert pillar_report()["pillar"] == 513

    def test_status(self):
        assert PILLAR_STATUS == "TOPOLOGICAL_INFORMATION_CURRENT_CERTIFIED"

    def test_k_cs_value(self):
        assert K_CS == 74

    def test_correction_factors_by_n_w_range(self):
        r = pillar_report()
        factors = r["correction_factors_by_n_w"]
        assert "n_w=0" in factors
        assert "n_w=5" in factors
        assert "n_w=7" in factors

    def test_n_w_0_correction_is_1(self):
        assert cs_correction_factor(0) == 1.0

    def test_n_w_5_correction(self):
        assert abs(cs_correction_factor(5) - (1.0 + 5.0 / 74.0)) < 1e-15

    def test_n_w_7_correction(self):
        assert abs(cs_correction_factor(7) - (1.0 + 7.0 / 74.0)) < 1e-15


# ---------------------------------------------------------------------------
# Backward compatibility: 3-argument call
# ---------------------------------------------------------------------------

class TestInformationCurrentBackwardCompat:
    def test_shape_unchanged(self):
        N = 16
        s = FieldState.flat(N=N, dx=0.1, rng=np.random.default_rng(1))
        J = information_current(s.g, s.phi, s.dx)
        assert J.shape == (N, 4)

    def test_time_component_positive_no_correction(self):
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(2))
        J = information_current(s.g, s.phi, s.dx)
        assert np.all(J[:, 0] >= 0.0)

    def test_zero_phi_gives_zero_current(self):
        N = 16
        g = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1))
        phi = np.zeros(N)
        J = information_current(g, phi, dx=0.1)
        np.testing.assert_allclose(J, 0.0, atol=1e-14)

    def test_finite(self):
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(3))
        J = information_current(s.g, s.phi, s.dx)
        assert np.all(np.isfinite(J))

    def test_winding_number_none_equals_no_argument(self):
        """Explicit winding_number=None gives same result as omitting it."""
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(4))
        J1 = information_current(s.g, s.phi, s.dx)
        J2 = information_current(s.g, s.phi, s.dx, winding_number=None)
        np.testing.assert_array_equal(J1, J2)


# ---------------------------------------------------------------------------
# Topological correction
# ---------------------------------------------------------------------------

class TestInformationCurrentTopologicalCorrection:
    def test_n_w_0_same_as_classical(self):
        """winding_number=0 gives correction factor 1; identical to classical."""
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(5))
        J_classical = information_current(s.g, s.phi, s.dx)
        J_topo = information_current(s.g, s.phi, s.dx, winding_number=0)
        np.testing.assert_allclose(J_topo, J_classical, atol=1e-15)

    def test_n_w_nonzero_differs_from_classical(self):
        """Non-zero winding number changes the current magnitude."""
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(6))
        J_classical = information_current(s.g, s.phi, s.dx)
        J_topo = information_current(s.g, s.phi, s.dx, winding_number=5)
        assert not np.allclose(J_classical, J_topo)

    def test_correction_factor_applied_uniformly(self):
        """Topological correction is a uniform scalar multiplication."""
        N = 16
        s = FieldState.flat(N=N, dx=0.1, rng=np.random.default_rng(7))
        n_w = 5
        J_classical = information_current(s.g, s.phi, s.dx)
        J_topo = information_current(s.g, s.phi, s.dx, winding_number=n_w)
        expected_factor = 1.0 + n_w / 74.0
        np.testing.assert_allclose(J_topo, J_classical * expected_factor, atol=1e-14)

    def test_correction_positive_definite_for_physical_n_w(self):
        """Correction factor > 0 for all n_w in {0,...,7}."""
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(8))
        for n_w in range(8):
            J = information_current(s.g, s.phi, s.dx, winding_number=n_w)
            assert np.all(J[:, 0] >= 0.0), f"J^0 < 0 for n_w={n_w}"

    def test_higher_n_w_gives_larger_current(self):
        """More winding → larger topological current density."""
        s = FieldState.flat(N=16, dx=0.1, rng=np.random.default_rng(9))
        J3 = information_current(s.g, s.phi, s.dx, winding_number=3)
        J5 = information_current(s.g, s.phi, s.dx, winding_number=5)
        assert np.mean(J5[:, 0]) > np.mean(J3[:, 0])


# ---------------------------------------------------------------------------
# information_current_topological convenience wrapper
# ---------------------------------------------------------------------------

class TestInformationCurrentTopologicalWrapper:
    def test_shape(self):
        s = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        J = information_current_topological(s)
        assert J.shape == (64, 4)

    def test_finite(self):
        s = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        J = information_current_topological(s)
        assert np.all(np.isfinite(J))

    def test_matches_manual_call(self):
        """information_current_topological(s) == information_current(g, phi, dx, n_w)."""
        s = FieldState.initialize_dynamic_braid(N=64, n_w_initial=1, dx=0.05)
        n_w = s.get_winding_number()
        J_manual = information_current(s.g, s.phi, s.dx, winding_number=n_w)
        J_auto = information_current_topological(s)
        np.testing.assert_allclose(J_auto, J_manual, atol=1e-15)

    def test_braided_differs_from_flat(self):
        """Topological current of a braided state differs from flat state."""
        s_flat = FieldState.flat(N=64, dx=0.05, rng=np.random.default_rng(50))
        # Use same amplitude phi for fair comparison
        N = 64
        dx = 0.05
        L = N * dx
        x = np.arange(N) * dx
        phi_cos = np.cos(2.0 * np.pi * 1 * x / L)
        g_flat = np.tile(np.diag([-1.0, 1.0, 1.0, 1.0]), (N, 1, 1)).astype(float)
        B_zero = np.zeros((N, 4))
        s_braided = FieldState(g=g_flat, B=B_zero, phi=phi_cos, t=0.0, dx=dx)
        # Only compare when their n_w values differ
        n_flat = s_flat.get_winding_number()
        n_braid = s_braided.get_winding_number()
        if n_flat != n_braid:
            J_flat = information_current_topological(s_flat)
            J_braid = information_current_topological(s_braided)
            assert not np.allclose(J_flat, J_braid)
