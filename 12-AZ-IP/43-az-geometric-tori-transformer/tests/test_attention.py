# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Shape, masking, and gradient-flow tests for toroidal multi-head attention."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.attention import ToroidalMultiHeadAttention
from az_tori_transformer.tensor import Tensor


def test_attention_output_shape() -> None:
    rng = np.random.default_rng(0)
    attn = ToroidalMultiHeadAttention(dim=16, num_heads=4, rng=rng, causal=True)
    x = Tensor(rng.normal(size=(2, 10, 16)), requires_grad=True)
    out, weights = attn(x)
    assert out.shape == (2, 10, 16)
    assert weights.shape == (2, 4, 10, 10)


def test_causal_mask_zeroes_future_attention() -> None:
    rng = np.random.default_rng(1)
    attn = ToroidalMultiHeadAttention(dim=8, num_heads=2, rng=rng, causal=True)
    x = Tensor(rng.normal(size=(1, 6, 8)))
    _, weights = attn(x)
    upper = np.triu(np.ones((6, 6)), k=1).astype(bool)
    assert np.allclose(weights[:, :, upper], 0.0, atol=1e-10)


def test_attention_rows_sum_to_one() -> None:
    rng = np.random.default_rng(2)
    attn = ToroidalMultiHeadAttention(dim=8, num_heads=2, rng=rng, causal=False)
    x = Tensor(rng.normal(size=(1, 5, 8)))
    _, weights = attn(x)
    assert np.allclose(weights.sum(axis=-1), 1.0, atol=1e-8)


def test_gradients_flow_to_all_parameters() -> None:
    rng = np.random.default_rng(3)
    attn = ToroidalMultiHeadAttention(dim=8, num_heads=2, rng=rng, causal=False)
    x = Tensor(rng.normal(size=(1, 5, 8)), requires_grad=True)
    out, _ = attn(x)
    out.sum().backward()
    for p in attn.parameters():
        assert p.grad is not None
        assert np.any(p.grad != 0.0)
    assert x.grad is not None and np.any(x.grad != 0.0)
