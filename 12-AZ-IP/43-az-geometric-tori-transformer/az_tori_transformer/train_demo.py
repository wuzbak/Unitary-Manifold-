# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""A toy training demonstration: a cyclic ("toroidal") copy task.

The task is deliberately chosen to exercise the architecture's namesake
property. For a sequence of length ``T`` and a fixed cyclic shift ``K``,
the target at position ``i`` is the input token at position
``(i + K) mod T`` — a copy relation that *wraps around the end of the
sequence*. Solving it requires a position-encoding scheme where the
relative offset ``K`` is recognisable the same way whether it falls inside
the sequence or wraps past the end; that is exactly the invariant the
toroidal rotary encoding and toroidal relative bias provide (see the module
docstring in ``positional.py``). The model is non-causal (bidirectional)
here because the task is a fixed-offset lookup, not autoregressive
generation.

This is a synthetic architecture smoke-test, not a claim about language
modelling performance; see the product README's epistemic status section.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from .model import GeometricToriTransformer, GeometricToriTransformerConfig
from .optim import Adam
from .tensor import cross_entropy

__all__ = ["toroidal_copy_batch", "run_toroidal_copy_demo"]


def toroidal_copy_batch(
    rng: np.random.Generator, batch_size: int, seq_len: int, vocab_size: int, shift: int
) -> tuple[np.ndarray, np.ndarray]:
    tokens = rng.integers(0, vocab_size, size=(batch_size, seq_len))
    targets = np.roll(tokens, shift=-shift, axis=1)
    return tokens, targets


def _accuracy(logits: np.ndarray, targets: np.ndarray) -> float:
    predictions = np.argmax(logits, axis=-1)
    return float(np.mean(predictions == targets))


def run_toroidal_copy_demo(
    *,
    seq_len: int = 16,
    vocab_size: int = 12,
    shift: int = 5,
    dim: int = 16,
    num_heads: int = 4,
    num_layers: int = 2,
    steps: int = 200,
    batch_size: int = 8,
    lr: float = 0.02,
    seed: int = 0,
    positional_mode: str = "toroidal",
) -> dict[str, Any]:
    cfg = GeometricToriTransformerConfig(
        vocab_size=vocab_size, dim=dim, num_heads=num_heads, num_layers=num_layers, causal=False, seed=seed,
        positional_mode=positional_mode,
    )
    model = GeometricToriTransformer(cfg)
    optimizer = Adam(model.parameters(), lr=lr)
    rng = np.random.default_rng(seed + 1)

    losses: list[float] = []
    for _ in range(steps):
        tokens, targets = toroidal_copy_batch(rng, batch_size, seq_len, vocab_size, shift)
        logits, _ = model(tokens)
        loss = cross_entropy(logits, targets)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        losses.append(float(loss.data))

    eval_tokens, eval_targets = toroidal_copy_batch(np.random.default_rng(seed + 2), 64, seq_len, vocab_size, shift)
    eval_logits, attn_maps = model(eval_tokens)

    return {
        "task": "toroidal_copy",
        "config": {
            "seq_len": seq_len, "vocab_size": vocab_size, "shift": shift, "dim": dim,
            "num_heads": num_heads, "num_layers": num_layers, "steps": steps, "batch_size": batch_size, "lr": lr,
            "positional_mode": positional_mode,
        },
        "num_parameters": model.num_parameters(),
        "initial_loss": losses[0],
        "final_loss": losses[-1],
        "loss_trace": losses,
        "eval_accuracy": _accuracy(eval_logits.data, eval_targets),
        "attention_map_shape": list(attn_maps[0].shape) if attn_maps else [],
    }
