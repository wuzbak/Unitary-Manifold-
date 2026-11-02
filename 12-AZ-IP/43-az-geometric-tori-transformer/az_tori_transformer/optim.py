# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""A small Adam optimizer over the local ``Tensor`` type."""

from __future__ import annotations

import numpy as np

from .tensor import Tensor

__all__ = ["Adam"]


class Adam:
    def __init__(self, parameters: list[Tensor], lr: float = 1e-2, betas: tuple[float, float] = (0.9, 0.999), eps: float = 1e-8):
        self.parameters = parameters
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        self.m = [np.zeros_like(p.data) for p in parameters]
        self.v = [np.zeros_like(p.data) for p in parameters]
        self.t = 0

    def zero_grad(self) -> None:
        for p in self.parameters:
            p.zero_grad()

    def step(self) -> None:
        self.t += 1
        for i, p in enumerate(self.parameters):
            if p.grad is None:
                continue
            g = p.grad
            self.m[i] = self.beta1 * self.m[i] + (1 - self.beta1) * g
            self.v[i] = self.beta2 * self.v[i] + (1 - self.beta2) * (g * g)
            m_hat = self.m[i] / (1 - self.beta1 ** self.t)
            v_hat = self.v[i] / (1 - self.beta2 ** self.t)
            p.data = p.data - self.lr * m_hat / (np.sqrt(v_hat) + self.eps)
