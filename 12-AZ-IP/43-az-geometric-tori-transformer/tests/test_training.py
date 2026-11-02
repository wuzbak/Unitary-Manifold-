# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""End-to-end training: the toroidal copy task loss must measurably decrease."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.train_demo import run_toroidal_copy_demo


def test_training_loss_decreases() -> None:
    report = run_toroidal_copy_demo(seq_len=12, vocab_size=8, shift=4, steps=150, seed=0)
    assert report["final_loss"] < report["initial_loss"] * 0.5


def test_training_reaches_nontrivial_accuracy() -> None:
    report = run_toroidal_copy_demo(seq_len=12, vocab_size=8, shift=4, steps=150, seed=0)
    # Random-guess accuracy would be ~1/vocab_size (0.125); a trained model on
    # this small deterministic task should comfortably clear that floor.
    assert report["eval_accuracy"] > 0.5


def test_training_report_is_deterministic_given_seed() -> None:
    report_a = run_toroidal_copy_demo(seq_len=10, vocab_size=6, shift=2, steps=20, seed=7)
    report_b = run_toroidal_copy_demo(seq_len=10, vocab_size=6, shift=2, steps=20, seed=7)
    assert report_a["loss_trace"] == report_b["loss_trace"]
