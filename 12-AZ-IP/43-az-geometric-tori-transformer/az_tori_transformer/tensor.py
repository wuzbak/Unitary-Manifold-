# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""A minimal reverse-mode autograd engine over NumPy arrays.

No PyTorch/JAX dependency is available in every deployment target for this
product, and the rest of the monorepo's non-hardgate "Phase 0/1" products
(28-42) are plain NumPy/SciPy. This module is a small, from-scratch
``Tensor`` type — the same "array micrograd" pattern used by minimal
educational autodiff engines — supporting exactly the operations the
Geometric Tori Transformer needs (matmul, elementwise arithmetic, softmax,
layer norm, GELU, embedding gather, reshape/transpose, and a cross-entropy
loss) with correct gradients, verified against finite differences in
``tests/test_tensor.py``.

This is deliberately *not* a general-purpose autodiff library: it implements
only the closed set of ops this transformer uses, each with a hand-derived
analytic backward pass.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

import numpy as np

__all__ = ["Tensor", "matmul", "softmax", "layer_norm", "gelu", "embedding_lookup", "cross_entropy"]


class Tensor:
    """A NumPy array with a recorded backward closure for reverse-mode autodiff."""

    __slots__ = ("data", "grad", "requires_grad", "_backward", "_prev", "_op")

    def __init__(
        self,
        data: np.ndarray | float | int,
        requires_grad: bool = False,
        _children: Iterable["Tensor"] = (),
        _op: str = "",
    ) -> None:
        self.data = np.asarray(data, dtype=np.float64)
        self.grad: np.ndarray | None = None
        self.requires_grad = requires_grad
        self._backward: Callable[[], None] = lambda: None
        self._prev = tuple(_children)
        self._op = _op

    # -- bookkeeping ---------------------------------------------------
    @property
    def shape(self) -> tuple[int, ...]:
        return self.data.shape

    def zero_grad(self) -> None:
        self.grad = None

    def _ensure_grad(self) -> None:
        if self.grad is None:
            self.grad = np.zeros_like(self.data)

    def _accumulate(self, grad: np.ndarray) -> None:
        self._ensure_grad()
        grad = np.asarray(grad, dtype=np.float64)
        # Broadcast-safe accumulation: sum out any axes NumPy broadcast over.
        while grad.ndim > self.data.ndim:
            grad = grad.sum(axis=0)
        for axis, (g_dim, s_dim) in enumerate(zip(grad.shape, self.data.shape)):
            if s_dim == 1 and g_dim != 1:
                grad = grad.sum(axis=axis, keepdims=True)
        self.grad = self.grad + grad

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Tensor(shape={self.data.shape}, requires_grad={self.requires_grad})"

    # -- elementwise ops -------------------------------------------------
    def __add__(self, other: "Tensor | float") -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data + other.data, self.requires_grad or other.requires_grad, (self, other), "add")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad)
            if other.requires_grad:
                other._accumulate(out.grad)

        out._backward = _backward
        return out

    def __radd__(self, other: float) -> "Tensor":
        return self.__add__(other)

    def __neg__(self) -> "Tensor":
        return self * -1.0

    def __sub__(self, other: "Tensor | float") -> "Tensor":
        return self + (-other if isinstance(other, Tensor) else -other)

    def __rsub__(self, other: float) -> "Tensor":
        return (-self) + other

    def __mul__(self, other: "Tensor | float") -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        out = Tensor(self.data * other.data, self.requires_grad or other.requires_grad, (self, other), "mul")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad * other.data)
            if other.requires_grad:
                other._accumulate(out.grad * self.data)

        out._backward = _backward
        return out

    def __rmul__(self, other: float) -> "Tensor":
        return self.__mul__(other)

    def __truediv__(self, other: "Tensor | float") -> "Tensor":
        other = other if isinstance(other, Tensor) else Tensor(other)
        return self * (other ** -1.0)

    def __pow__(self, power: float) -> "Tensor":
        out = Tensor(self.data ** power, self.requires_grad, (self,), "pow")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad * power * (self.data ** (power - 1)))

        out._backward = _backward
        return out

    # -- reductions / shape ops ------------------------------------------
    def sum(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False) -> "Tensor":
        out = Tensor(self.data.sum(axis=axis, keepdims=keepdims), self.requires_grad, (self,), "sum")

        def _backward() -> None:
            if self.requires_grad:
                grad = out.grad
                if not keepdims and axis is not None:
                    grad = np.expand_dims(grad, axis=axis)
                self._accumulate(np.broadcast_to(grad, self.data.shape))

        out._backward = _backward
        return out

    def mean(self, axis: int | tuple[int, ...] | None = None, keepdims: bool = False) -> "Tensor":
        if axis is None:
            n = self.data.size
        else:
            axes = (axis,) if isinstance(axis, int) else axis
            n = 1
            for a in axes:
                n *= self.data.shape[a]
        return self.sum(axis=axis, keepdims=keepdims) * (1.0 / n)

    def reshape(self, *shape: int) -> "Tensor":
        out = Tensor(self.data.reshape(*shape), self.requires_grad, (self,), "reshape")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad.reshape(self.data.shape))

        out._backward = _backward
        return out

    def transpose(self, *axes: int) -> "Tensor":
        axes = axes if axes else tuple(reversed(range(self.data.ndim)))
        out = Tensor(self.data.transpose(*axes), self.requires_grad, (self,), "transpose")
        inverse = np.argsort(axes)

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad.transpose(*inverse))

        out._backward = _backward
        return out

    def __matmul__(self, other: "Tensor") -> "Tensor":
        out = Tensor(self.data @ other.data, self.requires_grad or other.requires_grad, (self, other), "matmul")

        def _backward() -> None:
            if self.requires_grad:
                other_t = np.swapaxes(other.data, -1, -2)
                self._accumulate(out.grad @ other_t)
            if other.requires_grad:
                self_t = np.swapaxes(self.data, -1, -2)
                other._accumulate(self_t @ out.grad)

        out._backward = _backward
        return out

    def __getitem__(self, index: Any) -> "Tensor":
        out = Tensor(self.data[index], self.requires_grad, (self,), "getitem")

        def _backward() -> None:
            if self.requires_grad:
                self._ensure_grad()
                np.add.at(self.grad, index, out.grad)

        out._backward = _backward
        return out

    def exp(self) -> "Tensor":
        data = np.exp(self.data)
        out = Tensor(data, self.requires_grad, (self,), "exp")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad * data)

        out._backward = _backward
        return out

    def log(self) -> "Tensor":
        out = Tensor(np.log(self.data), self.requires_grad, (self,), "log")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad / self.data)

        out._backward = _backward
        return out

    def tanh(self) -> "Tensor":
        data = np.tanh(self.data)
        out = Tensor(data, self.requires_grad, (self,), "tanh")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad * (1.0 - data * data))

        out._backward = _backward
        return out

    def relu(self) -> "Tensor":
        mask = (self.data > 0).astype(np.float64)
        out = Tensor(self.data * mask, self.requires_grad, (self,), "relu")

        def _backward() -> None:
            if self.requires_grad:
                self._accumulate(out.grad * mask)

        out._backward = _backward
        return out

    # -- backward traversal ----------------------------------------------
    def backward(self) -> None:
        topo: list[Tensor] = []
        visited: set[int] = set()

        def build(node: "Tensor") -> None:
            if id(node) in visited:
                return
            visited.add(id(node))
            for child in node._prev:
                build(child)
            topo.append(node)

        build(self)
        self.grad = np.ones_like(self.data)
        for node in reversed(topo):
            node._backward()


# ---------------------------------------------------------------------------
# Composite ops built from the primitives above
# ---------------------------------------------------------------------------

def matmul(a: Tensor, b: Tensor) -> Tensor:
    return a @ b


def softmax(x: Tensor, axis: int = -1) -> Tensor:
    """Numerically stable softmax; the max-subtraction is a non-differentiable shift."""
    shifted_data = x.data - np.max(x.data, axis=axis, keepdims=True)
    shifted = Tensor(shifted_data, x.requires_grad, (x,), "softmax_shift")

    def _shift_backward() -> None:
        if x.requires_grad:
            x._accumulate(shifted.grad)

    shifted._backward = _shift_backward
    exp = shifted.exp()
    denom = exp.sum(axis=axis, keepdims=True)
    return exp / denom


def layer_norm(x: Tensor, gamma: Tensor, beta: Tensor, axis: int = -1, eps: float = 1e-5) -> Tensor:
    n = x.data.shape[axis]
    mean = x.sum(axis=axis, keepdims=True) * (1.0 / n)
    centered = x - mean
    var = (centered * centered).sum(axis=axis, keepdims=True) * (1.0 / n)
    std = (var + eps) ** 0.5
    normed = centered / std
    return normed * gamma + beta


def gelu(x: Tensor) -> Tensor:
    """Tanh approximation of GELU (Hendrycks & Gimpel, 2016)."""
    c = float(np.sqrt(2.0 / np.pi))
    inner = (x + x * x * x * 0.044715) * c
    return x * 0.5 * (inner.tanh() + 1.0)


def embedding_lookup(table: Tensor, indices: np.ndarray) -> Tensor:
    return table[indices]


def cross_entropy(logits: Tensor, targets: np.ndarray) -> Tensor:
    """Mean cross-entropy over the last axis; ``targets`` holds class indices."""
    probs = softmax(logits, axis=-1)
    flat_probs = probs.reshape(-1, logits.shape[-1])
    flat_targets = np.asarray(targets).reshape(-1)
    rows = np.arange(flat_targets.shape[0])
    picked = flat_probs[(rows, flat_targets)]
    return -(picked.log().mean())
