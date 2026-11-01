# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Toroidal multi-head self-attention: the Geometric Tori Transformer's attention block.

Combines two geometric mechanisms from ``positional.py`` with standard
scaled-dot-product attention:

* query/key vectors are rotated by the exact Z_74 toroidal rotary encoding
  before the dot product (``apply_rotation``);
* a learned per-head bias is added to the attention logits, indexed by the
  circular distance between each pair of positions' braid-bank addresses
  (``gather_relative_bias``), so geometrically nearby positions (which need
  not be adjacent in raw sequence index — the torus wraps) receive a
  learnable attention preference independent of the rotary term.
"""

from __future__ import annotations

import numpy as np

from .layers import Linear
from .positional import toroidal_relative_bias_indices, toroidal_rotation_table
from .tensor import Tensor, softmax
from .toroidal_geometry import HALF_TURN

__all__ = ["ToroidalMultiHeadAttention"]


def apply_rotation(x: Tensor, cos: np.ndarray, sin: np.ndarray) -> Tensor:
    """Differentiable pairwise rotation of ``x``'s last axis by exact (cos, sin) tables."""
    data = x.data
    x_even = data[..., 0::2]
    x_odd = data[..., 1::2]
    rotated_even = x_even * cos - x_odd * sin
    rotated_odd = x_even * sin + x_odd * cos
    out_data = np.empty_like(data)
    out_data[..., 0::2] = rotated_even
    out_data[..., 1::2] = rotated_odd
    out = Tensor(out_data, x.requires_grad, (x,), "toroidal_rotation")

    def _backward() -> None:
        if x.requires_grad:
            g = out.grad
            g_even = g[..., 0::2]
            g_odd = g[..., 1::2]
            grad_even = g_even * cos + g_odd * sin
            grad_odd = -g_even * sin + g_odd * cos
            grad_x = np.empty_like(data)
            grad_x[..., 0::2] = grad_even
            grad_x[..., 1::2] = grad_odd
            x._accumulate(grad_x)

    out._backward = _backward
    return out


def gather_relative_bias(table: Tensor, idx: np.ndarray) -> Tensor:
    """Differentiable gather: ``table`` is ``(num_heads, HALF_TURN + 1)``, ``idx`` is ``(T, T)``."""
    out_data = table.data[:, idx]
    out = Tensor(out_data, table.requires_grad, (table,), "gather_relative_bias")

    def _backward() -> None:
        if table.requires_grad:
            grad_table = np.zeros_like(table.data)
            for h in range(table.data.shape[0]):
                np.add.at(grad_table[h], idx, out.grad[h])
            table._accumulate(grad_table)

    out._backward = _backward
    return out


class ToroidalMultiHeadAttention:
    def __init__(self, dim: int, num_heads: int, rng: np.random.Generator, causal: bool = True):
        if dim % num_heads != 0:
            raise ValueError("dim must be divisible by num_heads")
        self.dim = dim
        self.num_heads = num_heads
        self.head_dim = dim // num_heads
        self.causal = causal
        self.wq = Linear(dim, dim, rng, bias=False)
        self.wk = Linear(dim, dim, rng, bias=False)
        self.wv = Linear(dim, dim, rng, bias=False)
        self.wo = Linear(dim, dim, rng)
        self.relative_bias = Tensor(np.zeros((num_heads, HALF_TURN + 1)), requires_grad=True)

    def parameters(self) -> list[Tensor]:
        return (
            self.wq.parameters()
            + self.wk.parameters()
            + self.wv.parameters()
            + self.wo.parameters()
            + [self.relative_bias]
        )

    def _split_heads(self, x: Tensor, batch: int, seq_len: int) -> Tensor:
        return x.reshape(batch, seq_len, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)

    def __call__(self, x: Tensor) -> tuple[Tensor, np.ndarray]:
        batch, seq_len, _ = x.shape
        q = self._split_heads(self.wq(x), batch, seq_len)
        k = self._split_heads(self.wk(x), batch, seq_len)
        v = self._split_heads(self.wv(x), batch, seq_len)

        cos, sin = toroidal_rotation_table(seq_len, self.head_dim)
        q = apply_rotation(q, cos, sin)
        k = apply_rotation(k, cos, sin)

        scale = 1.0 / np.sqrt(self.head_dim)
        logits = (q @ k.transpose(0, 1, 3, 2)) * scale

        bias_idx = toroidal_relative_bias_indices(seq_len)
        bias = gather_relative_bias(self.relative_bias, bias_idx)
        logits = logits + bias.reshape(1, self.num_heads, seq_len, seq_len)

        if self.causal:
            mask = np.triu(np.full((seq_len, seq_len), -1e9), k=1)
            logits = logits + Tensor(mask)

        attn = softmax(logits, axis=-1)
        out = attn @ v
        out = out.transpose(0, 2, 1, 3).reshape(batch, seq_len, self.dim)
        return self.wo(out), attn.data
