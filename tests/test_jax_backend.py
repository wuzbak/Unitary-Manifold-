# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_jax_backend.py
==============================
Tests for both JAX-accelerated backends:
  - src/core/jax_backend.py  (Triple-Point bridge API: constants, vmap, autodiff)
  - src/core/jax_metric.py   (curvature pipeline)
  - src/core/jax_evolution.py (RK4 evolution)
"""
import numpy as np
import pytest
jax = pytest.importorskip("jax")
jnp = jax.numpy

from src.core.jax_backend import (
    JAX_VERSION,
    field_strength_jax,
    assemble_metric_jax,
    grad_spectral_index,
    vmap_field_strength,
    numerical_agreement_check,
)
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

N = 16
DX = 0.1
LAM = 1.0


@pytest.fixture
def small_state():
    rng = np.random.default_rng(0)
    g = rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = rng.standard_normal((N, 4))
    phi = 1.0 + 0.01 * rng.standard_normal(N)
    return g, B, phi


@pytest.fixture
def flat_fields():
    rng = np.random.default_rng(42)
    eta = np.diag([-1.0, 1.0, 1.0, 1.0])
    g = np.tile(eta, (N, 1, 1)) + 1e-4 * rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = 1e-4 * rng.standard_normal((N, 4))
    phi = 1.0 + 1e-4 * rng.standard_normal(N)
    return g, B, phi


@pytest.fixture
def np_state():
    return FieldState.flat(N=N, dx=DX)


@pytest.fixture
def jax_state(np_state):
    return from_numpy_state(np_state)


# ===========================================================================
# Part A: src/core/jax_backend.py (Triple-Point API)
# ===========================================================================

def test_jax_available():
    import jax
    assert isinstance(jax.__version__, str)
    assert len(jax.__version__) > 0


def test_jax_version_exported():
    assert isinstance(JAX_VERSION, str)
    assert len(JAX_VERSION) > 0


# field_strength_jax ----------------------------------------------------------

def test_field_strength_shape(small_state):
    g, B, phi = small_state
    H = field_strength_jax(jnp.array(B), 0.1)
    assert H.shape == (B.shape[0], 4, 4)


def test_field_strength_antisymmetric(small_state):
    g, B, phi = small_state
    H = np.array(field_strength_jax(jnp.array(B), 0.1))
    np.testing.assert_allclose(H, -H.transpose(0, 2, 1), atol=1e-12)


def test_field_strength_dtype(small_state):
    g, B, phi = small_state
    H = field_strength_jax(jnp.array(B), 0.1)
    assert H.dtype in (jnp.float32, jnp.float64)


def test_field_strength_zero_for_uniform_B():
    B = np.ones((20, 4))
    H = np.array(field_strength_jax(jnp.array(B), 0.1))
    np.testing.assert_allclose(H, 0.0, atol=1e-6)


def test_field_strength_dx_scaling(small_state):
    g, B, phi = small_state
    H1 = np.array(field_strength_jax(jnp.array(B), 0.1))
    H2 = np.array(field_strength_jax(jnp.array(B), 0.2))
    np.testing.assert_allclose(H1, 2.0 * H2, atol=1e-5)


def test_field_strength_diagonal_zero(small_state):
    g, B, phi = small_state
    H = np.array(field_strength_jax(jnp.array(B), 0.1))
    for mu in range(4):
        np.testing.assert_allclose(H[:, mu, mu], 0.0, atol=1e-12)


# assemble_metric_jax ---------------------------------------------------------

def test_assemble_metric_shape(small_state):
    g, B, phi = small_state
    G = assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi))
    assert G.shape == (N, 5, 5)


def test_assemble_metric_g55_equals_phi_sq(small_state):
    g, B, phi = small_state
    G = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi)))
    np.testing.assert_allclose(G[:, 4, 4], phi ** 2, rtol=1e-5)


def test_assemble_metric_symmetry(small_state):
    g, B, phi = small_state
    G = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi)))
    np.testing.assert_allclose(G, G.transpose(0, 2, 1), atol=1e-10)


def test_assemble_metric_off_diagonal(small_state):
    g, B, phi = small_state
    G = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi), 1.0))
    np.testing.assert_allclose(G[:, :4, 4], 1.0 * phi[:, None] * B, rtol=1e-5)


def test_assemble_metric_4x4_block(small_state):
    g, B, phi = small_state
    G = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi), 1.0))
    expected = g + ((1.0 * phi) ** 2)[:, None, None] * np.einsum('ni,nj->nij', B, B)
    np.testing.assert_allclose(G[:, :4, :4], expected, rtol=1e-5)


# grad_spectral_index ---------------------------------------------------------

def test_grad_spectral_index_values():
    n_s, _, _ = grad_spectral_index(10.0, 5.0)
    assert abs(n_s - (1.0 - 8.0 * 5.0 / 10.0 ** 2)) < 1e-6


def test_grad_spectral_index_gradient_phi0():
    _, dn_dphi0, _ = grad_spectral_index(10.0, 5.0)
    assert dn_dphi0 > 0


def test_grad_spectral_index_gradient_nw():
    _, _, dn_dnw = grad_spectral_index(10.0, 5.0)
    assert dn_dnw < 0


def test_grad_spectral_index_formula_phi0():
    _, dn_dphi0, _ = grad_spectral_index(10.0, 5.0)
    assert abs(dn_dphi0 - 16.0 * 5.0 / 10.0 ** 3) < 1e-5


def test_grad_spectral_index_formula_nw():
    _, _, dn_dnw = grad_spectral_index(10.0, 5.0)
    assert abs(dn_dnw - (-8.0 / 10.0 ** 2)) < 1e-5


def test_grad_spectral_index_planck_value():
    n_s, _, _ = grad_spectral_index(33.1, 5.0)
    assert 0.93 < n_s < 0.98


# numerical_agreement_check ---------------------------------------------------

def test_numerical_agreement_passes():
    assert numerical_agreement_check(N=16, steps=2, dt=0.001)["passed"]


def test_numerical_agreement_keys():
    r = numerical_agreement_check(N=16, steps=2, dt=0.001)
    for k in ("max_metric_err", "passed", "jax_version", "backend"):
        assert k in r


def test_numerical_agreement_backend_label():
    assert numerical_agreement_check(N=16, steps=2, dt=0.001)["backend"] == "jax"


def test_numerical_agreement_error_small():
    assert numerical_agreement_check(N=16, steps=2, dt=0.001, rtol=1e-3)["max_metric_err"] < 1e-3


# vmap_field_strength ---------------------------------------------------------

def test_vmap_field_strength():
    rng = np.random.default_rng(1)
    B_batch = rng.standard_normal((4, 12, 4))
    H_batch = np.array(vmap_field_strength(jnp.array(B_batch), 0.1))
    for i in range(4):
        H_single = np.array(field_strength_jax(jnp.array(B_batch[i]), 0.1))
        np.testing.assert_allclose(H_batch[i], H_single, atol=1e-6)


def test_vmap_field_strength_shape():
    B_batch = np.random.default_rng(2).standard_normal((3, 8, 4))
    assert vmap_field_strength(jnp.array(B_batch), 0.1).shape == (3, 8, 4, 4)


def test_jit_determinism(small_state):
    g, B, phi = small_state
    H1 = np.array(field_strength_jax(jnp.array(B), 0.1))
    H2 = np.array(field_strength_jax(jnp.array(B), 0.1))
    np.testing.assert_array_equal(H1, H2)


def test_jit_metric_determinism(small_state):
    g, B, phi = small_state
    G1 = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi)))
    G2 = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi)))
    np.testing.assert_array_equal(G1, G2)


# ===========================================================================
# Part B: src/core/jax_metric.py + src/core/jax_evolution.py
# ===========================================================================

def test_jax_available_from_metric():
    assert JAX_AVAILABLE


# jax_metric: field strength --------------------------------------------------

class TestJaxMetricFieldStrength:
    def test_shape(self, flat_fields):
        g, B, phi = flat_fields
        assert jax_field_strength(B, DX).shape == (N, 4, 4)

    def test_antisymmetry(self, flat_fields):
        g, B, phi = flat_fields
        H = numpy_from_jax(jax_field_strength(B, DX))
        np.testing.assert_allclose(H + H.transpose(0, 2, 1), 0.0, atol=1e-12)

    def test_agrees_with_numpy(self, flat_fields):
        g, B, phi = flat_fields
        np.testing.assert_allclose(
            numpy_from_jax(jax_field_strength(B, DX)),
            np_field_strength(B, DX), rtol=1e-5, atol=1e-10)

    def test_zero_B(self):
        H = numpy_from_jax(jax_field_strength(np.zeros((N, 4)), DX))
        np.testing.assert_allclose(H, 0.0, atol=1e-14)


# jax_metric: 5D metric assembly ----------------------------------------------

class TestJaxMetric5d:
    def test_shape(self, flat_fields):
        g, B, phi = flat_fields
        assert jax_assemble_5d_metric(g, B, phi, LAM).shape == (N, 5, 5)

    def test_symmetry(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        np.testing.assert_allclose(G5, G5.transpose(0, 2, 1), atol=1e-12)

    def test_g55_phi_sq(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        np.testing.assert_allclose(G5[:, 4, 4], phi ** 2, rtol=1e-6)

    def test_agrees_with_numpy(self, flat_fields):
        g, B, phi = flat_fields
        np.testing.assert_allclose(
            numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM)),
            np_assemble_5d_metric(g, B, phi, LAM), rtol=1e-5, atol=1e-10)


# jax_metric: Christoffel -----------------------------------------------------

class TestJaxChristoffel:
    def test_shape(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        assert jax_christoffel(G5, DX).shape == (N, 5, 5, 5)

    def test_lower_symmetry(self, flat_fields):
        g, B, phi = flat_fields
        G5 = numpy_from_jax(jax_assemble_5d_metric(g, B, phi, LAM))
        Gamma = numpy_from_jax(jax_christoffel(G5, DX))
        np.testing.assert_allclose(Gamma, Gamma.transpose(0, 1, 3, 2), atol=1e-10)

    def test_flat_near_zero(self):
        eta = np.diag([-1.0, 1.0, 1.0, 1.0])
        g_flat = np.tile(eta, (N, 1, 1))
        np.testing.assert_allclose(
            numpy_from_jax(jax_christoffel(g_flat, DX)), 0.0, atol=1e-12)


# jax_metric: curvature pipeline ----------------------------------------------

class TestJaxCurvature:
    def test_output_shapes(self, flat_fields):
        g, B, phi = flat_fields
        Gamma, Riem, Ricci, R = jax_compute_curvature(g, B, phi, DX, LAM)
        assert Gamma.shape == (N, 4, 4, 4)
        assert Riem.shape  == (N, 4, 4, 4, 4)
        assert Ricci.shape == (N, 4, 4)
        assert R.shape     == (N,)

    def test_ricci_symmetry(self, flat_fields):
        g, B, phi = flat_fields
        _, _, Ricci, _ = jax_compute_curvature(g, B, phi, DX, LAM)
        Ricci_np = numpy_from_jax(Ricci)
        np.testing.assert_allclose(Ricci_np, Ricci_np.transpose(0, 2, 1), atol=1e-8)

    def test_agrees_with_numpy(self, flat_fields):
        g, B, phi = flat_fields
        _, _, Ricci_j, R_j = jax_compute_curvature(g, B, phi, DX, LAM)
        _, _, Ricci_n, R_n = np_compute_curvature(g, B, phi, DX, LAM)
        np.testing.assert_allclose(numpy_from_jax(Ricci_j), Ricci_n, rtol=1e-4, atol=1e-8)
        np.testing.assert_allclose(numpy_from_jax(R_j), R_n, rtol=1e-4, atol=1e-8)

    def test_ricci_scalar_finite(self, flat_fields):
        g, B, phi = flat_fields
        _, _, _, R = jax_compute_curvature(g, B, phi, DX, LAM)
        assert np.all(np.isfinite(numpy_from_jax(R)))


# jax_evolution ---------------------------------------------------------------

class TestJaxFieldState:
    def test_flat_factory(self):
        s = JaxFieldState.flat(N=N, dx=DX)
        assert s.g.shape == (N, 4, 4)
        assert s.B.shape == (N, 4)
        assert s.phi.shape == (N,)
        assert s.t == 0.0

    def test_to_numpy_round_trip(self, np_state):
        jax_s = from_numpy_state(np_state)
        np_s2 = to_numpy_state(jax_s)
        np.testing.assert_allclose(np_s2.g, np_state.g, atol=1e-12)
        np.testing.assert_allclose(np_s2.phi, np_state.phi, atol=1e-12)

    def test_from_numpy_preserves_params(self, np_state):
        jax_s = from_numpy_state(np_state)
        assert jax_s.dx == np_state.dx
        assert jax_s.lam == np_state.lam


DT = 1e-4


class TestJaxStepEvol:
    def test_step_advances_time(self, jax_state):
        assert jax_step(jax_state, DT).t == pytest.approx(DT, rel=1e-9)

    def test_step_preserves_shape(self, jax_state):
        s1 = jax_step(jax_state, DT)
        assert s1.g.shape == (N, 4, 4)

    def test_step_fields_finite(self, jax_state):
        s1 = jax_step(jax_state, DT)
        assert np.all(np.isfinite(np.asarray(s1.g)))
        assert np.all(np.isfinite(np.asarray(s1.phi)))

    def test_euler_step_advances_time(self, jax_state):
        assert jax_step_euler(jax_state, DT).t == pytest.approx(DT, rel=1e-9)

    def test_run_evolution_length(self, jax_state):
        history = jax_run_evolution(jax_state, dt=DT, steps=5)
        assert len(history) == 6

    def test_run_evolution_time_sequence(self, jax_state):
        history = jax_run_evolution(jax_state, dt=DT, steps=5)
        for i, s in enumerate(history):
            assert s.t == pytest.approx(i * DT, rel=1e-9)
