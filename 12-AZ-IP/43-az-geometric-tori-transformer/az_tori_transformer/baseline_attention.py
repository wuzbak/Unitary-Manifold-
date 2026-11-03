# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Standard continuous-frequency RoPE attention: the control arm for benchmarking.

This module is deliberately *not* geometric-tori architecture: it implements
textbook Rotary Position Embedding (Su et al., 2021, "RoFormer") — the same
family the product README cites as the standard this architecture is
compared against. Query/key channel pairs are rotated by a continuous
geometric frequency schedule (``theta ** (-2k/head_dim)``) with **no** finite
modulus and **no** learned relative-distance bias, instead of the Z_74
toroidal rotary encoding + relative bias used in ``attention.py``.

Its only purpose is to exist as a same-engine, same-training-loop control
arm so ``tests/test_baseline_benchmark.py`` can honestly measure whether the
toroidal mechanism in this repository converges, and how its convergence
compares to a standard RoPE baseline, on an identical task/optimizer/budget
— rather than asserting the toroidal mechanism "wins" against a strawman.
"""

from __future__ import annotations

import numpy as np

from .attention import apply_rotation, gather_relative_bias
from .layers import Linear
from .positional import toroidal_relative_bias_indices
from .tensor import Tensor, softmax
from .toroidal_geometry import HALF_TURN

__all__ = ["rope_table", "RopeMultiHeadAttention", "MatchedRopeMultiHeadAttention"]


def rope_table(seq_len: int, head_dim: int, theta: float = 10000.0) -> tuple[np.ndarray, np.ndarray]:
    """Standard RoPE ``(cos, sin)`` tables of shape ``(seq_len, head_dim // 2)``.

    Frequencies follow the canonical RoFormer schedule
    ``freq_k = theta ** (-2k / head_dim)``; angle at position ``i`` is
    ``i * freq_k`` (continuous, unbounded) — the direct counterpart of
    ``positional.toroidal_rotation_table``'s *exact, finite* Z_74 angle.
    """
    if head_dim % 2 != 0:
        raise ValueError("head_dim must be even (rotation acts on channel pairs)")
    n_pairs = head_dim // 2
    freqs = theta ** (-(2.0 * np.arange(n_pairs)) / head_dim)
    positions = np.arange(seq_len, dtype=np.float64).reshape(-1, 1)
    angle = positions * freqs.reshape(1, -1)
    return np.cos(angle), np.sin(angle)


class RopeMultiHeadAttention:
    """Vanilla scaled-dot-product multi-head attention with standard RoPE.

    Structurally identical to ``ToroidalMultiHeadAttention`` (same
    projections, same ``parameters()``/``__call__`` contract, so it is a
    drop-in swap inside ``TransformerBlock``) except it carries *no*
    relative-distance bias term and uses the continuous RoPE table above
    instead of the finite Z_74 rotation table.
    """

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

    def parameters(self) -> list[Tensor]:
        return self.wq.parameters() + self.wk.parameters() + self.wv.parameters() + self.wo.parameters()

    def _split_heads(self, x: Tensor, batch: int, seq_len: int) -> Tensor:
        return x.reshape(batch, seq_len, self.num_heads, self.head_dim).transpose(0, 2, 1, 3)

    def __call__(self, x: Tensor) -> tuple[Tensor, np.ndarray]:
        batch, seq_len, _ = x.shape
        q = self._split_heads(self.wq(x), batch, seq_len)
        k = self._split_heads(self.wk(x), batch, seq_len)
        v = self._split_heads(self.wv(x), batch, seq_len)

        cos, sin = rope_table(seq_len, self.head_dim)
        q = apply_rotation(q, cos, sin)
        k = apply_rotation(k, cos, sin)

        scale = 1.0 / np.sqrt(self.head_dim)
        logits = (q @ k.transpose(0, 1, 3, 2)) * scale

        if self.causal:
            mask = np.triu(np.full((seq_len, seq_len), -1e9), k=1)
            logits = logits + Tensor(mask)

        attn = softmax(logits, axis=-1)
        out = attn @ v
        out = out.transpose(0, 2, 1, 3).reshape(batch, seq_len, self.dim)
        return self.wo(out), attn.data


class MatchedRopeMultiHeadAttention(RopeMultiHeadAttention):
    """RoPE control with the same learned bank-bias parameters as the tori arm.

    This control is intended for positional ablations, not as the product's
    legacy RoPE mode. Keeping the bank bias active makes the parameter count
    and learned-bias mechanism identical, isolating the rotary phase choice.
    """

    def __init__(self, dim: int, num_heads: int, rng: np.random.Generator, causal: bool = True):
        super().__init__(dim, num_heads, rng, causal=causal)
        self.relative_bias = Tensor(np.zeros((num_heads, HALF_TURN + 1)), requires_grad=True)

    def parameters(self) -> list[Tensor]:
        return super().parameters() + [self.relative_bias]

    def __call__(self, x: Tensor) -> tuple[Tensor, np.ndarray]:
        batch, seq_len, _ = x.shape
        q = self._split_heads(self.wq(x), batch, seq_len)
        k = self._split_heads(self.wk(x), batch, seq_len)
        v = self._split_heads(self.wv(x), batch, seq_len)

        cos, sin = rope_table(seq_len, self.head_dim)
        q = apply_rotation(q, cos, sin)
        k = apply_rotation(k, cos, sin)
        logits = (q @ k.transpose(0, 1, 3, 2)) * (1.0 / np.sqrt(self.head_dim))

        bias = gather_relative_bias(self.relative_bias, toroidal_relative_bias_indices(seq_len))
        logits = logits + bias.reshape(1, self.num_heads, seq_len, seq_len)
        if self.causal:
            mask = np.triu(np.full((seq_len, seq_len), -1e9), k=1)
            logits = logits + Tensor(mask)

        attn = softmax(logits, axis=-1)
        out = attn @ v
        out = out.transpose(0, 2, 1, 3).reshape(batch, seq_len, self.dim)
        return self.wo(out), attn.data
