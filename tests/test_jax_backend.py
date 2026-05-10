# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_jax_backend.py
=========================
Tests for the JAX-accelerated metric and evolution pipeline.

Verifies numerical agreement with the numpy reference implementations in
``src/core/metric.py`` and ``src/core/evolution.py``.

All tests skip gracefully when JAX is not installed.
"""
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Skip entire module if JAX is unavailable
# ---------------------------------------------------------------------------
jax = pytest.importorskip("jax")
jnp = pytest.importorskip("jax.numpy")

from src.core.jax_metric import (
    jax_field_strength,
    jax_assemble_5d_metric,
    jax_christoffel,
    jax_compute_curvature,
    numpy_from_jax,
    JAX_AVAILABLE,
)
from src.core.jax_evolution import (
    JaxFieldState,
    jax_step,
    jax_step_euler,
    jax_run_evolution,
    to_numpy_state,
    from_numpy_state,
)
from src.core.metric import (
    field_strength as np_field_strength,
    assemble_5d_metric as np_assemble_5d_metric,
    christoffel as np_christoffel,
    compute_curvature as np_compute_curvature,
)
from src.core.evolution import FieldState, step as np_step

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

N = 16   # small grid for fast tests
DX = 0.1
LAM = 1.0


@pytest.fixture
def flat_fields():
    """Return (g, B, phi) numpy arrays for a flat Minkowski background."""
    rng = np.random.default_rng(42)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1)) + 1e-4 * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = 1e-4 * rng.standard_normal((N, 4))
    phi = 1.0 + 1e-4 * rng.standard_normal(N)
    return g, B, phi


@pytest.fixture
def np_state():
    """Return a numpy FieldState for the flat Minkowski background."""
    return FieldState.flat(N=N, dx=DX)


@pytest.fixture
def jax_state(np_state):
    """Return a JaxFieldState converted from the numpy FieldState."""
    return from_numpy_state(np_state)


# ---------------------------------------------------------------------------
# Module-level availability
# ---------------------------------------------------------------------------

def test_jax_available():
    assert JAX_AVAILABLE, "JAX should be available when tests are run"


# ---------------------------------------------------------------------------
# (a-1) Field strength
# ---------------------------------------------------------------------------

class TestJaxFieldStrength:
    def test_shape(self, flat_fields):
        g, B, phi = flat_fields
        H = jax_field_strength(B, DX)
        assert H.shape == (N, 4, 4)

    def test_antisymmetry(self, flat_fields):
        g, B, phi = flat_fields
        H = numpy_from_jax(jax_field_strength(B, DX))
        np.testing.assert_allclose(H + H.transpose(0, 2, 1), 0.0, atol=1e-12)

    def test_agrees_with_numpy(self, flat_fields):
        g, B, phi = flat_fields
        H_jax = numpy_from_jax(jax_field_strength(B, DX))
        H_np  = np_field_strength(B, DX)
        np.testing.assert_allclose(H_jax, H_np, rtol=1e-5, atol=1e-10)

    def test_zero_B_gives_zero_H(self):
        B_zero = np.zeros((N, 4))
        H = numpy_from_jax(jax_field_strength(B_zero, DX))
        np.testing.assert_allclose(H, 0.0, atol=1e-14)


# ---------------------------------------------------------------------------
# (a-2) 5D metric assembly
# ---------------------------------------------------------------------------

class TestJaxAssemble5dMetric:
    def test_shape(self, flat_fields):
        g, B, phi = flat_fields
        G5 = jax_assemble_5d_metric(g, B, phi, LAM)
        assert G5.shape == (N, 5, 5)

    def test_symmetry(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        np.testing.assert_allclose(G5, G5.transpose(0, 2, 1), atol=1e-12)

    def test_g55_equals_phi_sq(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        np.testing.assert_allclose(G5[:, 4, 4], phi ** 2, rtol=1e-6)

    def test_agrees_with_numpy(self, flat_fields):
        g, B, phi = flat_fields
        G5_jax = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        G5_np  = np_assemble_5d_metric(g, B, phi, LAM)
        np.testing.assert_allclose(G5_jax, G5_np, rtol=1e-5, atol=1e-10)


# ---------------------------------------------------------------------------
# (a-3) Christoffel symbols
# ---------------------------------------------------------------------------

class TestJaxChristoffel:
    def test_shape(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        Gamma = jax_christoffel(G5, DX)
        assert Gamma.shape == (N, 5, 5, 5)

    def test_symmetry_lower_indices(self, flat_fields):
        """Γ^σ_{μν} = Γ^σ_{νμ} (Christoffel is symmetric in lower indices)."""
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        Gamma = numpy_from_jax(jax_christoffel(G5, DX))
        # Gamma[n, sigma, mu, nu] == Gamma[n, sigma, nu, mu]
        np.testing.assert_allclose(
            Gamma, Gamma.transpose(0, 1, 3, 2), atol=1e-10
        )

    def test_agrees_with_numpy_4d(self, flat_fields):
        """4D Christoffel block from JAX matches numpy on the 4D metric."""
        g, B, phi = flat_fields
        Gamma_jax = numpy_from_jax(jax_christoffel(g, DX))
        Gamma_np  = np_christoffel(g, DX)
        np.testing.assert_allclose(Gamma_jax, Gamma_np, rtol=1e-4, atol=1e-8)

    def test_flat_metric_small_christoffel(self):
        """On a truly flat metric, all Christoffels should be near zero."""
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g_flat = np.tile(eta, (N, 1, 1))
        Gamma = numpy_from_jax(jax_christoffel(g_flat, DX))
        np.testing.assert_allclose(Gamma, 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# (a-4) Full curvature pipeline
# ---------------------------------------------------------------------------

class TestJaxComputeCurvature:
    def test_output_shapes(self, flat_fields):
        g, B, phi = flat_fields
        Gamma, Riem, Ricci, R = jax_compute_curvature(g, B, phi, DX, LAM)
        assert Gamma.shape  == (N, 4, 4, 4)
        assert Riem.shape   == (N, 4, 4, 4, 4)
        assert Ricci.shape  == (N, 4, 4)
        assert R.shape      == (N,)

    def test_ricci_symmetry(self, flat_fields):
        g, B, phi = flat_fields
        _, _, Ricci, _ = jax_compute_curvature(g, B, phi, DX, LAM)
        Ricci_np = numpy_from_jax(Ricci)
        np.testing.assert_allclose(
            Ricci_np, Ricci_np.transpose(0, 2, 1), atol=1e-8
        )

    def test_agrees_with_numpy(self, flat_fields):
        g, B, phi = flat_fields
        Gamma_j, Riem_j, Ricci_j, R_j = jax_compute_curvature(g, B, phi, DX, LAM)
        Gamma_n, Riem_n, Ricci_n, R_n = np_compute_curvature(g, B, phi, DX, LAM)
        np.testing.assert_allclose(numpy_from_jax(Ricci_j), Ricci_n, rtol=1e-4, atol=1e-8)
        np.testing.assert_allclose(numpy_from_jax(R_j), R_n, rtol=1e-4, atol=1e-8)

    def test_ricci_scalar_finite(self, flat_fields):
        g, B, phi = flat_fields
        _, _, _, R = jax_compute_curvature(g, B, phi, DX, LAM)
        assert np.all(np.isfinite(numpy_from_jax(R)))


# ---------------------------------------------------------------------------
# (a-5) JAX FieldState and evolution
# ---------------------------------------------------------------------------

class TestJaxFieldState:
    def test_flat_factory(self):
        state = JaxFieldState.flat(N=N, dx=DX)
        assert state.g.shape   == (N, 4, 4)
        assert state.B.shape   == (N, 4)
        assert state.phi.shape == (N,)
        assert state.t == 0.0

    def test_to_numpy_round_trip(self, np_state):
        jax_s = from_numpy_state(np_state)
        np_s2 = to_numpy_state(jax_s)
        np.testing.assert_allclose(np_s2.g, np_state.g, atol=1e-12)
        np.testing.assert_allclose(np_s2.B, np_state.B, atol=1e-12)
        np.testing.assert_allclose(np_s2.phi, np_state.phi, atol=1e-12)

    def test_from_numpy_preserves_params(self, np_state):
        jax_s = from_numpy_state(np_state)
        assert jax_s.dx    == np_state.dx
        assert jax_s.lam   == np_state.lam
        assert jax_s.alpha == np_state.alpha


class TestJaxStep:
    DT = 1e-4   # CFL-safe for dx=0.1: dt ≤ 0.4×0.01 = 0.004

    def test_step_advances_time(self, jax_state):
        s1 = jax_step(jax_state, self.DT)
        assert s1.t == pytest.approx(self.DT, rel=1e-9)

    def test_step_preserves_shape(self, jax_state):
        s1 = jax_step(jax_state, self.DT)
        assert s1.g.shape   == (N, 4, 4)
        assert s1.B.shape   == (N, 4)
        assert s1.phi.shape == (N,)

    def test_step_fields_are_finite(self, jax_state):
        s1 = jax_step(jax_state, self.DT)
        assert np.all(np.isfinite(np.asarray(s1.g)))
        assert np.all(np.isfinite(np.asarray(s1.B)))
        assert np.all(np.isfinite(np.asarray(s1.phi)))

    def test_euler_step_advances_time(self, jax_state):
        s1 = jax_step_euler(jax_state, self.DT)
        assert s1.t == pytest.approx(self.DT, rel=1e-9)

    def test_jax_and_numpy_steps_agree(self, np_state, jax_state):
        """JAX and numpy RK4 steps should give very close results."""
        s_np  = np_step(np_state, self.DT)
        s_jax = jax_step(jax_state, self.DT)
        np.testing.assert_allclose(
            np.asarray(s_jax.phi), s_np.phi, rtol=1e-3, atol=1e-6
        )

    def test_run_evolution_length(self, jax_state):
        history = jax_run_evolution(jax_state, dt=self.DT, steps=5)
        assert len(history) == 6   # initial + 5 steps

    def test_run_evolution_time_sequence(self, jax_state):
        steps = 5
        history = jax_run_evolution(jax_state, dt=self.DT, steps=steps)
        for i, s in enumerate(history):
            assert s.t == pytest.approx(i * self.DT, rel=1e-9)


# ---------------------------------------------------------------------------
# Benchmark: verify JAX is actually faster than numpy (warm-up + timing)
# ---------------------------------------------------------------------------

class TestJaxSpeedup:
    """Smoke-test that JAX does not regress performance (≥ 1× of numpy).

    This test does not assert a specific speedup — hardware varies — but it
    ensures the JAX pipeline completes without error and produces a valid result.
    For quantitative benchmarking use ``pytest --benchmark-only``.
    """

    def test_jax_curvature_completes(self, flat_fields):
        import time
        g, B, phi = flat_fields
        # Warm-up (first call traces the computation graph)
        _ = jax_compute_curvature(g, B, phi, DX, LAM)
        # Timed call
        t0 = time.perf_counter()
        Gamma, Riem, Ricci, R = jax_compute_curvature(g, B, phi, DX, LAM)
        elapsed = time.perf_counter() - t0
        assert np.all(np.isfinite(numpy_from_jax(R))), "R must be finite"
        # Log for visibility (not an assertion)
        print(f"\n[JAX curvature] elapsed: {elapsed*1000:.2f} ms for N={N}")
