# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Parameter-matched, synthetic positional-mechanism comparison."""

from __future__ import annotations

from typing import Any

import numpy as np

from .model import GeometricToriTransformer, GeometricToriTransformerConfig
from .optim import Adam
from .tensor import cross_entropy
from .train_demo import _accuracy, toroidal_copy_batch

__all__ = ["run_positional_ablation"]


def _make_model(mode: str, *, seed: int, dim: int, num_heads: int, num_layers: int,
                vocab_size: int) -> GeometricToriTransformer:
    return GeometricToriTransformer(
        GeometricToriTransformerConfig(
            vocab_size=vocab_size,
            dim=dim,
            num_heads=num_heads,
            num_layers=num_layers,
            causal=False,
            seed=seed,
            positional_mode=mode,
        )
    )


def run_positional_ablation(
    *,
    seq_len: int = 12,
    vocab_size: int = 8,
    shift: int = 7,
    steps: int = 120,
    seed: int = 0,
    dim: int = 16,
    num_heads: int = 4,
    num_layers: int = 1,
    batch_size: int = 8,
    lr: float = 0.02,
) -> dict[str, Any]:
    """Compare Z_74 rotary to continuous RoPE with matched learned bank bias.

    Both arms use the same initialization, training batches, optimizer, budget,
    architecture, and active learned bias table. Thus this ablation isolates
    the rotary phase schedule on this synthetic cyclic-copy task; it is not a
    general model-quality or real-corpus benchmark.
    """
    if steps < 1:
        raise ValueError("steps must be positive")
    if seq_len < 1 or vocab_size < 2 or batch_size < 1:
        raise ValueError("seq_len and batch_size must be positive; vocab_size must be at least 2")
    if not 0 <= shift:
        raise ValueError("shift must be nonnegative")

    modes = ("toroidal", "rope_matched")
    models = {mode: _make_model(
        mode, seed=seed, dim=dim, num_heads=num_heads, num_layers=num_layers, vocab_size=vocab_size
    ) for mode in modes}
    named = {mode: model.named_parameters() for mode, model in models.items()}
    names = list(named[modes[0]])
    if names != list(named[modes[1]]) or any(
        named[modes[0]][name].data.shape != named[modes[1]][name].data.shape for name in names
    ):
        raise RuntimeError("positional ablation arms do not have matching parameter schemas")
    if any(not np.array_equal(named[modes[0]][name].data, named[modes[1]][name].data) for name in names):
        raise RuntimeError("positional ablation arms did not receive identical initial parameters")
    counts = {mode: models[mode].num_parameters() for mode in modes}
    if counts[modes[0]] != counts[modes[1]]:
        raise RuntimeError("positional ablation arms do not have matched parameter counts")

    rngs = {mode: np.random.default_rng(seed + 1) for mode in modes}
    optimizers = {mode: Adam(models[mode].parameters(), lr=lr) for mode in modes}
    metrics: dict[str, dict[str, float | int]] = {}
    for mode in modes:
        model = models[mode]
        optimizer = optimizers[mode]
        rng = rngs[mode]
        initial_loss = None
        final_loss = None
        for _ in range(steps):
            tokens, targets = toroidal_copy_batch(rng, batch_size, seq_len, vocab_size, shift)
            logits, _ = model(tokens)
            loss = cross_entropy(logits, targets)
            if initial_loss is None:
                initial_loss = float(loss.data)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            final_loss = float(loss.data)

        eval_tokens, eval_targets = toroidal_copy_batch(
            np.random.default_rng(seed + 2), 64, seq_len, vocab_size, shift
        )
        eval_logits, _ = model(eval_tokens)
        metrics[mode] = {
            "parameter_count": counts[mode],
            "active_parameter_count": counts[mode],
            "initial_loss": initial_loss,
            "final_loss": final_loss,
            "eval_accuracy": _accuracy(eval_logits.data, eval_targets),
        }

    return {
        "task": "synthetic_cyclic_copy",
        "evidence_scope": "descriptive synthetic ablation; not a real-corpus benchmark",
        "comparison": "Z_74 rotary vs continuous RoPE; both retain the same learned circular-bank bias",
        "matched_parameter_count": counts[modes[0]],
        "matched_parameter_schema": names,
        "shared_settings": {
            "seq_len": seq_len,
            "vocab_size": vocab_size,
            "shift": shift,
            "steps": steps,
            "seed": seed,
            "dim": dim,
            "num_heads": num_heads,
            "num_layers": num_layers,
            "batch_size": batch_size,
            "learning_rate": lr,
        },
        "arms": metrics,
    }
