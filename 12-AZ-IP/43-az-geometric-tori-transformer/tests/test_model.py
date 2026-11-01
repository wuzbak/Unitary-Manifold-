# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Forward-pass and determinism tests for the assembled model."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer.model import GeometricToriTransformer, GeometricToriTransformerConfig


def test_odd_num_heads_ratio_rejected() -> None:
    with pytest.raises(ValueError):
        GeometricToriTransformerConfig(vocab_size=10, dim=10, num_heads=4)


def test_odd_head_dim_rejected() -> None:
    with pytest.raises(ValueError):
        GeometricToriTransformerConfig(vocab_size=10, dim=12, num_heads=4)  # head_dim=3, odd


def test_forward_pass_shape() -> None:
    cfg = GeometricToriTransformerConfig(vocab_size=20, dim=16, num_heads=4, num_layers=2, seed=0)
    model = GeometricToriTransformer(cfg)
    tokens = np.random.default_rng(0).integers(0, 20, size=(3, 7))
    logits, attn_maps = model(tokens)
    assert logits.shape == (3, 7, 20)
    assert len(attn_maps) == 2
    assert attn_maps[0].shape == (3, 4, 7, 7)


def test_forward_pass_is_deterministic_given_seed() -> None:
    cfg = GeometricToriTransformerConfig(vocab_size=10, dim=8, num_heads=2, num_layers=1, seed=42)
    tokens = np.array([[1, 2, 3, 4]])
    logits_a, _ = GeometricToriTransformer(cfg)(tokens)
    logits_b, _ = GeometricToriTransformer(cfg)(tokens)
    assert np.allclose(logits_a.data, logits_b.data)


def test_num_parameters_is_positive_and_matches_sum() -> None:
    cfg = GeometricToriTransformerConfig(vocab_size=10, dim=8, num_heads=2, num_layers=1, seed=0)
    model = GeometricToriTransformer(cfg)
    assert model.num_parameters() == sum(p.data.size for p in model.parameters())
    assert model.num_parameters() > 0
