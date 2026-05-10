# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""tests/test_jax_backend.py
=============================
Tests for src/core/jax_backend.py — real JAX, no skipping.
"""
import numpy as np
import jax.numpy as jnp
import pytest

from src.core.jax_backend import (
    JAX_VERSION,
    field_strength_jax,
    assemble_metric_jax,
    grad_spectral_index,
    vmap_field_strength,
    numerical_agreement_check,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_state():
    rng = np.random.default_rng(0)
    N = 16
    g = rng.standard_normal((N, 4, 4))
    g = 0.5 * (g + g.transpose(0, 2, 1))
    B = rng.standard_normal((N, 4))
    phi = 1.0 + 0.01 * rng.standard_normal(N)
    return g, B, phi


# ---------------------------------------------------------------------------
# JAX availability
# ---------------------------------------------------------------------------

def test_jax_available():
    import jax
    assert isinstance(jax.__version__, str)
    assert len(jax.__version__) > 0


def test_jax_version_exported():
    assert isinstance(JAX_VERSION, str)
    assert len(JAX_VERSION) > 0


# ---------------------------------------------------------------------------
# field_strength_jax
# ---------------------------------------------------------------------------

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
    N = 20
    B = np.ones((N, 4))
    H = np.array(field_strength_jax(jnp.array(B), 0.1))
    np.testing.assert_allclose(H, 0.0, atol=1e-6)


def test_field_strength_dx_scaling(small_state):
    g, B, phi = small_state
    H1 = np.array(field_strength_jax(jnp.array(B), 0.1))
    H2 = np.array(field_strength_jax(jnp.array(B), 0.2))
    # halving dx doubles the gradient
    np.testing.assert_allclose(H1, 2.0 * H2, atol=1e-5)


def test_field_strength_diagonal_zero(small_state):
    g, B, phi = small_state
    H = np.array(field_strength_jax(jnp.array(B), 0.1))
    # H[x, mu, mu] = 0 for all mu
    for mu in range(4):
        np.testing.assert_allclose(H[:, mu, mu], 0.0, atol=1e-12)


# ---------------------------------------------------------------------------
# assemble_metric_jax
# ---------------------------------------------------------------------------

def test_assemble_metric_shape(small_state):
    g, B, phi = small_state
    G = assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi))
    assert G.shape == (g.shape[0], 5, 5)


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
    lam = 1.0
    G = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi), lam))
    # G_mu5 = lam * phi * B_mu
    expected = lam * phi[:, None] * B
    np.testing.assert_allclose(G[:, :4, 4], expected, rtol=1e-5)


def test_assemble_metric_4x4_block(small_state):
    g, B, phi = small_state
    lam = 1.0
    G = np.array(assemble_metric_jax(jnp.array(g), jnp.array(B), jnp.array(phi), lam))
    expected_44 = g + ((lam * phi) ** 2)[:, None, None] * np.einsum('ni,nj->nij', B, B)
    np.testing.assert_allclose(G[:, :4, :4], expected_44, rtol=1e-5)


# ---------------------------------------------------------------------------
# grad_spectral_index
# ---------------------------------------------------------------------------

def test_grad_spectral_index_values():
    phi0 = 10.0
    n_w = 5.0
    n_s, _, _ = grad_spectral_index(phi0, n_w)
    expected = 1.0 - 8.0 * n_w / phi0 ** 2
    assert abs(n_s - expected) < 1e-6


def test_grad_spectral_index_gradient_phi0():
    phi0 = 10.0
    n_w = 5.0
    _, dn_dphi0, _ = grad_spectral_index(phi0, n_w)
    # n_s = 1 - 8 n_w / phi0^2, so dn/dphi0 = 16 n_w / phi0^3 > 0
    assert dn_dphi0 > 0, f"Expected dn_s/dphi0 > 0, got {dn_dphi0}"


def test_grad_spectral_index_gradient_nw():
    phi0 = 10.0
    n_w = 5.0
    _, _, dn_dnw = grad_spectral_index(phi0, n_w)
    # dn/dn_w = -8/phi0^2 < 0
    assert dn_dnw < 0, f"Expected dn_s/dn_w < 0, got {dn_dnw}"


def test_grad_spectral_index_formula_phi0():
    phi0 = 10.0
    n_w = 5.0
    _, dn_dphi0, _ = grad_spectral_index(phi0, n_w)
    expected_deriv = 16.0 * n_w / phi0 ** 3
    assert abs(dn_dphi0 - expected_deriv) < 1e-5


def test_grad_spectral_index_formula_nw():
    phi0 = 10.0
    n_w = 5.0
    _, _, dn_dnw = grad_spectral_index(phi0, n_w)
    expected_deriv = -8.0 / phi0 ** 2
    assert abs(dn_dnw - expected_deriv) < 1e-5


def test_grad_spectral_index_planck_value():
    # phi0 ≈ 33.1 gives n_s = 1 - 8*5/phi0^2 ≈ 0.9635 (UM prediction)
    phi0 = 33.1
    n_w = 5.0
    n_s, _, _ = grad_spectral_index(phi0, n_w)
    assert 0.93 < n_s < 0.98, f"n_s={n_s} out of reasonable range"


# ---------------------------------------------------------------------------
# numerical_agreement_check
# ---------------------------------------------------------------------------

def test_numerical_agreement_passes():
    result = numerical_agreement_check(N=16, steps=2, dt=0.001)
    assert result["passed"] is True or result["passed"] == True


def test_numerical_agreement_keys():
    result = numerical_agreement_check(N=16, steps=2, dt=0.001)
    assert "max_metric_err" in result
    assert "passed" in result
    assert "jax_version" in result
    assert "backend" in result


def test_numerical_agreement_backend_label():
    result = numerical_agreement_check(N=16, steps=2, dt=0.001)
    assert result["backend"] == "jax"


def test_numerical_agreement_error_small():
    result = numerical_agreement_check(N=16, steps=2, dt=0.001, rtol=1e-3)
    assert result["max_metric_err"] < 1e-3


# ---------------------------------------------------------------------------
# vmap_field_strength
# ---------------------------------------------------------------------------

def test_vmap_field_strength():
    rng = np.random.default_rng(1)
    batch = 4
    N = 12
    B_batch = rng.standard_normal((batch, N, 4))

    H_batch = np.array(vmap_field_strength(jnp.array(B_batch), 0.1))

    for i in range(batch):
        H_single = np.array(field_strength_jax(jnp.array(B_batch[i]), 0.1))
        np.testing.assert_allclose(H_batch[i], H_single, atol=1e-6)


def test_vmap_field_strength_shape():
    rng = np.random.default_rng(2)
    batch, N = 3, 8
    B_batch = rng.standard_normal((batch, N, 4))
    H_batch = vmap_field_strength(jnp.array(B_batch), 0.1)
    assert H_batch.shape == (batch, N, 4, 4)


# ---------------------------------------------------------------------------
# JIT determinism
# ---------------------------------------------------------------------------

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
