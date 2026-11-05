# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Descriptive synthetic training and parameter-matched rotary comparisons.

Checks two separate properties without claiming real-corpus superiority:

1. The toroidal mechanism is not merely a theoretical model structure — it
   actually trains and converges on a concrete task (shared with the
   standard-RoPE control arm defined in ``baseline_attention.py``), using
   the project's own from-scratch autograd engine end to end.
2. The newer matched-bias ablation has matching active parameter counts
   and reports observed results. A 12-position task does not match the
   first rotary pair's 74-position orbit. The historical unmatched RoPE
   comparison cannot establish periodicity as the cause of a loss difference.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.train_demo import run_toroidal_copy_demo
from az_tori_transformer.positional_ablation import run_positional_ablation
from az_tori_transformer.model import GeometricToriTransformer, GeometricToriTransformerConfig


def test_both_positional_modes_train_and_converge() -> None:
    """Both arms must actually learn the task, not just execute without error."""
    for mode in ("toroidal", "rope", "rope_matched"):
        report = run_toroidal_copy_demo(seq_len=12, vocab_size=8, shift=4, steps=150, seed=0, positional_mode=mode)
        assert report["final_loss"] < report["initial_loss"] * 0.5, mode
        assert report["eval_accuracy"] > 0.5, mode


def test_matched_parameter_ablation_is_auditable_and_descriptive() -> None:
    report = run_positional_ablation(seq_len=8, shift=5, steps=12, seed=3, dim=8, num_heads=2)
    toroidal = report["arms"]["toroidal"]
    rope = report["arms"]["rope_matched"]
    assert report["evidence_scope"] == "descriptive synthetic ablation; not a real-corpus benchmark"
    assert report["matched_parameter_count"] == toroidal["parameter_count"] == rope["parameter_count"]
    assert toroidal["active_parameter_count"] == rope["active_parameter_count"]
    assert report["comparison"].endswith("same learned circular-bank bias")
    assert all(np.isfinite(arm[key]) for arm in (toroidal, rope) for key in ("initial_loss", "final_loss", "eval_accuracy"))


def test_legacy_rope_comparison_has_304_fewer_parameters() -> None:
    counts = {
        mode: GeometricToriTransformer(GeometricToriTransformerConfig(
            vocab_size=8, dim=16, num_heads=4, num_layers=2,
            causal=False, seed=0, positional_mode=mode,
        )).num_parameters()
        for mode in ("toroidal", "rope", "rope_matched")
    }
    assert counts["toroidal"] == counts["rope_matched"] == 7064
    assert counts["rope"] == 6760
