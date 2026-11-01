# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Dense/LayerNorm/FeedForward building blocks built on the local autograd ``Tensor``."""

from __future__ import annotations

import numpy as np

from .tensor import Tensor, gelu, layer_norm

__all__ = ["Linear", "LayerNorm", "FeedForward", "Embedding"]


def _xavier(rng: np.random.Generator, fan_in: int, fan_out: int) -> np.ndarray:
    limit = np.sqrt(6.0 / (fan_in + fan_out))
    return rng.uniform(-limit, limit, size=(fan_in, fan_out))


class Linear:
    def __init__(self, in_features: int, out_features: int, rng: np.random.Generator, bias: bool = True):
        self.weight = Tensor(_xavier(rng, in_features, out_features), requires_grad=True)
        self.bias = Tensor(np.zeros(out_features), requires_grad=True) if bias else None

    def __call__(self, x: Tensor) -> Tensor:
        out = x @ self.weight
        if self.bias is not None:
            out = out + self.bias
        return out

    def parameters(self) -> list[Tensor]:
        return [self.weight] + ([self.bias] if self.bias is not None else [])


class LayerNorm:
    def __init__(self, dim: int):
        self.gamma = Tensor(np.ones(dim), requires_grad=True)
        self.beta = Tensor(np.zeros(dim), requires_grad=True)

    def __call__(self, x: Tensor) -> Tensor:
        return layer_norm(x, self.gamma, self.beta)

    def parameters(self) -> list[Tensor]:
        return [self.gamma, self.beta]


class FeedForward:
    def __init__(self, dim: int, hidden_dim: int, rng: np.random.Generator):
        self.fc1 = Linear(dim, hidden_dim, rng)
        self.fc2 = Linear(hidden_dim, dim, rng)

    def __call__(self, x: Tensor) -> Tensor:
        return self.fc2(gelu(self.fc1(x)))

    def parameters(self) -> list[Tensor]:
        return self.fc1.parameters() + self.fc2.parameters()


class Embedding:
    def __init__(self, n_vocab: int, dim: int, rng: np.random.Generator):
        self.weight = Tensor(rng.normal(scale=0.02, size=(n_vocab, dim)), requires_grad=True)

    def __call__(self, indices: np.ndarray) -> Tensor:
        return self.weight[np.asarray(indices)]

    def parameters(self) -> list[Tensor]:
        return [self.weight]
