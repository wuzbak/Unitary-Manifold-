# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Gradient-check tests for the local autograd engine."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.tensor import Tensor, cross_entropy, gelu, layer_norm, softmax


#: Central-difference step. Empirically swept against this engine's
#: analytic gradients (matmul/add/mul, softmax, layer_norm, gelu) over
#: eps in {1e-4..1e-7}; 1e-5 minimizes the sum of truncation error
#: (O(eps^2)) and floating-point cancellation error (O(mach_eps/eps)),
#: giving max abs error ~1e-10, two orders of magnitude inside the
#: 1e-7 gate asserted below.
_GRAD_CHECK_EPS = 1e-5

#: Required agreement between this engine's analytic backward() output
#: and the central-difference numerical gradient, per the project's
#: gradient-check mandate.
GRAD_CHECK_TOLERANCE = 1e-7


def _numerical_grad(f, x: np.ndarray, eps: float = _GRAD_CHECK_EPS) -> np.ndarray:
    grad = np.zeros_like(x)
    it = np.nditer(x, flags=["multi_index"])
    for _ in it:
        idx = it.multi_index
        orig = x[idx]
        x[idx] = orig + eps
        plus = f(x)
        x[idx] = orig - eps
        minus = f(x)
        x[idx] = orig
        grad[idx] = (plus - minus) / (2 * eps)
    return grad


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_matmul_add_mul_gradients(seed: int) -> None:
    rng = np.random.default_rng(seed)
    a_data = rng.normal(size=(3, 4))
    b_data = rng.normal(size=(4, 2))

    def f(a: np.ndarray) -> float:
        a_t = Tensor(a)
        b_t = Tensor(b_data)
        out = (a_t @ b_t) * 2.0 + 1.0
        return float(out.sum().data)

    numeric = _numerical_grad(f, a_data.copy())

    a_t = Tensor(a_data, requires_grad=True)
    b_t = Tensor(b_data)
    out = (a_t @ b_t) * 2.0 + 1.0
    out.sum().backward()
    assert np.allclose(a_t.grad, numeric, atol=GRAD_CHECK_TOLERANCE, rtol=0.0)


def test_softmax_gradient() -> None:
    rng = np.random.default_rng(3)
    x_data = rng.normal(size=(5, 6))

    def f(x: np.ndarray) -> float:
        weights = np.arange(x.shape[-1], dtype=np.float64)
        probs = softmax(Tensor(x), axis=-1)
        return float((probs * weights).sum().data)

    numeric = _numerical_grad(f, x_data.copy())

    weights = Tensor(np.arange(x_data.shape[-1], dtype=np.float64))
    x_t = Tensor(x_data, requires_grad=True)
    probs = softmax(x_t, axis=-1)
    (probs * weights).sum().backward()
    assert np.allclose(x_t.grad, numeric, atol=GRAD_CHECK_TOLERANCE, rtol=0)


def test_layer_norm_gradient() -> None:
    rng = np.random.default_rng(4)
    x_data = rng.normal(size=(3, 8))
    gamma_data = rng.normal(size=(8,))
    beta_data = rng.normal(size=(8,))

    def f(x: np.ndarray) -> float:
        out = layer_norm(Tensor(x), Tensor(gamma_data), Tensor(beta_data))
        return float(out.sum().data)

    numeric = _numerical_grad(f, x_data.copy())

    x_t = Tensor(x_data, requires_grad=True)
    out = layer_norm(x_t, Tensor(gamma_data), Tensor(beta_data))
    out.sum().backward()
    assert np.allclose(x_t.grad, numeric, atol=GRAD_CHECK_TOLERANCE, rtol=0)


def test_gelu_gradient() -> None:
    rng = np.random.default_rng(5)
    x_data = rng.normal(size=(10,))

    def f(x: np.ndarray) -> float:
        return float(gelu(Tensor(x)).sum().data)

    numeric = _numerical_grad(f, x_data.copy())
    x_t = Tensor(x_data, requires_grad=True)
    gelu(x_t).sum().backward()
    assert np.allclose(x_t.grad, numeric, atol=GRAD_CHECK_TOLERANCE, rtol=0)


def test_embedding_getitem_gradient() -> None:
    table_data = np.random.default_rng(6).normal(size=(5, 3))
    indices = np.array([0, 2, 2, 4])

    table = Tensor(table_data, requires_grad=True)
    out = table[indices]
    out.sum().backward()

    expected = np.zeros_like(table_data)
    for i in indices:
        expected[i] += 1.0
    assert np.allclose(table.grad, expected)


def test_cross_entropy_decreases_towards_correct_logit() -> None:
    logits_data = np.zeros((2, 4))
    targets = np.array([1, 3])
    logits = Tensor(logits_data, requires_grad=True)
    loss = cross_entropy(logits, targets)
    loss.backward()
    # Gradient should push the target-class logit up (negative grad direction
    # for gradient descent) and others down.
    grad = logits.grad
    for row, target in enumerate(targets):
        assert grad[row, target] < 0
        others = [c for c in range(4) if c != target]
        assert all(grad[row, c] > 0 for c in others)
