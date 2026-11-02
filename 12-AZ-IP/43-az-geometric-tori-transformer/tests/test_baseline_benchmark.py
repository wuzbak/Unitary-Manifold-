# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Empirical comparison of toroidal attention and a standard RoPE control arm.

Checks two things without attributing the result to an untested mechanism:

1. The toroidal mechanism is not merely a theoretical model structure — it
   actually trains and converges on a concrete task (shared with the
   standard-RoPE control arm defined in ``baseline_attention.py``), using
   the project's own from-scratch autograd engine end to end.
2. Reports the empirical loss comparison on a synthetic cyclic-copy task.
   The task period is not matched to the Z_74 rotary orbit, and the toroidal
   model has additional learned relative-bias parameters, so the result does
   not isolate periodicity as its cause.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.train_demo import run_toroidal_copy_demo


def test_both_positional_modes_train_and_converge() -> None:
    """Both arms must actually learn the task, not just execute without error."""
    for mode in ("toroidal", "rope"):
        report = run_toroidal_copy_demo(seq_len=12, vocab_size=8, shift=4, steps=150, seed=0, positional_mode=mode)
        assert report["final_loss"] < report["initial_loss"] * 0.5, mode
        assert report["eval_accuracy"] > 0.5, mode


def test_toroidal_arm_has_lower_empirical_loss_on_cyclic_copy_task() -> None:
    """Compare observed losses only; this task does not isolate periodicity.
    """
    seq_len, vocab_size, shift, steps = 12, 8, 7, 120  # shift=7 > seq_len/2: genuinely wraps
    toroidal_finals = []
    rope_finals = []
    parameter_deltas = []
    for seed in range(4):
        toroidal = run_toroidal_copy_demo(
            seq_len=seq_len, vocab_size=vocab_size, shift=shift, steps=steps, seed=seed,
            positional_mode="toroidal",
        )
        rope = run_toroidal_copy_demo(
            seq_len=seq_len, vocab_size=vocab_size, shift=shift, steps=steps, seed=seed,
            positional_mode="rope",
        )
        toroidal_finals.append(toroidal["final_loss"])
        rope_finals.append(rope["final_loss"])
        parameter_deltas.append(toroidal["num_parameters"] - rope["num_parameters"])

    assert parameter_deltas == [304] * 4
    toroidal_mean = sum(toroidal_finals) / len(toroidal_finals)
    rope_mean = sum(rope_finals) / len(rope_finals)
    assert toroidal_mean < rope_mean, (
        f"toroidal mean final loss {toroidal_mean!r} was not below RoPE control-arm "
        f"mean final loss {rope_mean!r} over seeds {list(range(4))}"
    )
