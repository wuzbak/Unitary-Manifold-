# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Portable checkpoint round trips, exact training continuation, and rejection."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from uuid import uuid4

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from az_tori_transformer import (
    Adam, GeometricToriTransformer, GeometricToriTransformerConfig,
    load_checkpoint, save_checkpoint,
)
from az_tori_transformer.tensor import cross_entropy
from az_tori_transformer.train_demo import toroidal_copy_batch


@pytest.fixture
def checkpoint_path():
    path = Path(__file__).parent / f".checkpoint-{uuid4().hex}.npz"
    yield path
    path.unlink(missing_ok=True)
    for pending in path.parent.glob(f".{path.name}.*.pending"):
        pending.unlink()


def _model(mode="toroidal", causal=False, layers=1):
    return GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=7, dim=8, num_heads=2, num_layers=layers,
        ff_hidden_dim=12, causal=causal, positional_mode=mode, seed=19,
    ))


def _step(model, optimizer, rng):
    tokens, targets = toroidal_copy_batch(rng, 1, 5, 7, 2)
    logits, _ = model(tokens)
    loss = cross_entropy(logits, targets)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return float(loss.data), tokens


@pytest.mark.parametrize("mode", ["toroidal", "rope", "rope_matched"])
@pytest.mark.parametrize("causal", [True, False])
def test_weights_only_roundtrip(checkpoint_path, mode, causal):
    model = _model(mode, causal)
    params = model.named_parameters()
    assert list(params.values()) == model.parameters()
    tokens = np.array([[1, 3, 5]])
    before, maps = model(tokens)
    save_checkpoint(checkpoint_path, model, metadata={"tokenizer": {"vocab": ["a", "b"]}})
    loaded = load_checkpoint(checkpoint_path)
    assert loaded.model.cfg == model.cfg
    assert loaded.optimizer is None and loaded.rng is None
    assert loaded.metadata == {"tokenizer": {"vocab": ["a", "b"]}}
    after, restored_maps = loaded.model(tokens)
    np.testing.assert_array_equal(before.data, after.data)
    for a, b in zip(maps, restored_maps):
        np.testing.assert_array_equal(a, b)
    assert all(p.grad is None and p.requires_grad for p in loaded.model.parameters())
    with np.load(checkpoint_path, allow_pickle=False) as archive:
        assert all(archive[key].dtype.kind != "O" for key in archive.files)


@pytest.mark.parametrize("mode", ["toroidal", "rope", "rope_matched"])
def test_exact_training_continuation(checkpoint_path, mode):
    model = _model(mode, layers=2)
    optimizer = Adam(model.parameters(), lr=0.003, betas=(0.8, 0.95), eps=1e-7)
    rng = np.random.default_rng(37)
    for _ in range(3):
        _step(model, optimizer, rng)
    assert rng.bit_generator.state["has_uint32"] == 1
    save_checkpoint(checkpoint_path, model, optimizer=optimizer, rng=rng, metadata={"task": "cyclic_copy"})
    loaded = load_checkpoint(checkpoint_path)
    assert loaded.optimizer.t == 3
    assert (loaded.optimizer.lr, loaded.optimizer.beta1, loaded.optimizer.beta2, loaded.optimizer.eps) == (0.003, 0.8, 0.95, 1e-7)
    for _ in range(4):
        expected_loss, expected_tokens = _step(model, optimizer, rng)
        actual_loss, actual_tokens = _step(loaded.model, loaded.optimizer, loaded.rng)
        assert expected_loss == actual_loss
        np.testing.assert_array_equal(expected_tokens, actual_tokens)
    assert loaded.optimizer.t == optimizer.t == 7
    for a, b in zip(model.parameters(), loaded.model.parameters()):
        np.testing.assert_array_equal(a.data, b.data)
    for moment in ("m", "v"):
        for a, b in zip(getattr(optimizer, moment), getattr(loaded.optimizer, moment)):
            np.testing.assert_array_equal(a, b)


def test_zero_step_optimizer_and_empty_stack(checkpoint_path):
    model = _model(layers=0)
    save_checkpoint(checkpoint_path, model, optimizer=Adam(model.parameters()))
    loaded = load_checkpoint(checkpoint_path)
    assert loaded.optimizer.t == 0 and loaded.rng is None
    _step(loaded.model, loaded.optimizer, np.random.default_rng(1))


@pytest.mark.parametrize("mutation", [
    "version", "format", "missing", "extra", "shape", "dtype", "nan", "object",
    "negative_v", "adam_step", "adam_beta", "rng", "config_zero", "config_boolean",
    "metadata", "manifest_shape", "json_duplicate", "json_infinity",
])
def test_reject_invalid_checkpoint(checkpoint_path, mutation):
    model = _model()
    save_checkpoint(checkpoint_path, model, optimizer=Adam(model.parameters()), rng=np.random.default_rng(2))
    with np.load(checkpoint_path, allow_pickle=False) as archive:
        arrays = {key: archive[key] for key in archive.files}
    manifest = json.loads(arrays["manifest"].item())
    key = "model/token_embedding.weight"
    if mutation == "version":
        manifest["schema_version"] = 99
    elif mutation == "format":
        manifest["format"] = "other"
    elif mutation == "missing":
        del arrays[key]
    elif mutation == "extra":
        arrays["unexpected"] = np.zeros(1)
    elif mutation == "shape":
        arrays[key] = np.zeros((1, 1))
    elif mutation == "dtype":
        arrays[key] = arrays[key].astype(np.float32)
    elif mutation == "nan":
        arrays[key][0, 0] = np.nan
    elif mutation == "object":
        arrays[key] = np.array(["not a weight"], dtype=object)
    elif mutation == "negative_v":
        arrays["adam/v/token_embedding.weight"][0, 0] = -1
    elif mutation == "adam_step":
        manifest["optimizer"]["t"] = -1
    elif mutation == "adam_beta":
        manifest["optimizer"]["beta1"] = 1
    elif mutation == "rng":
        manifest["rng"] = {"bit_generator": "unknown"}
    elif mutation == "config_zero":
        manifest["config"]["num_heads"] = 0
    elif mutation == "config_boolean":
        manifest["config"]["causal"] = 1
    elif mutation == "metadata":
        manifest["metadata"] = []
    arrays["manifest"] = np.array(json.dumps(manifest))
    if mutation == "manifest_shape":
        arrays["manifest"] = arrays["manifest"].reshape(1)
    elif mutation == "json_duplicate":
        arrays["manifest"] = np.array('{"format":"first",' + arrays["manifest"].item()[1:])
    elif mutation == "json_infinity":
        arrays["manifest"] = np.array(arrays["manifest"].item().replace('"metadata": {}', '"metadata": {"invalid": 1e999}'))
    with checkpoint_path.open("wb") as handle:
        np.savez(handle, **arrays)
    with pytest.raises(ValueError):
        load_checkpoint(checkpoint_path)


def test_reject_plain_npy(checkpoint_path):
    with checkpoint_path.open("wb") as handle:
        np.save(handle, np.ones(3))
    with pytest.raises(ValueError, match="NPZ"):
        load_checkpoint(checkpoint_path)


@pytest.mark.parametrize("invalid", ["foreign_optimizer", "reordered_optimizer", "metadata", "rng", "weights", "moments"])
def test_save_rejection_preserves_existing_file(checkpoint_path, invalid):
    model = _model()
    save_checkpoint(checkpoint_path, model)
    before = checkpoint_path.read_bytes()
    kwargs = {}
    if invalid == "foreign_optimizer":
        kwargs["optimizer"] = Adam(_model().parameters())
    elif invalid == "reordered_optimizer":
        kwargs["optimizer"] = Adam(model.parameters()[::-1])
    elif invalid == "metadata":
        kwargs["metadata"] = {"invalid": float("nan")}
    elif invalid == "rng":
        kwargs["rng"] = np.random.Generator(np.random.MT19937(1))
    elif invalid == "weights":
        model.parameters()[0].data[0, 0] = np.inf
    elif invalid == "moments":
        optimizer = Adam(model.parameters())
        optimizer.v[0][0, 0] = -1
        kwargs["optimizer"] = optimizer
    with pytest.raises(ValueError):
        save_checkpoint(checkpoint_path, model, **kwargs)
    assert checkpoint_path.read_bytes() == before


def test_atomic_write_failure_preserves_old_checkpoint(checkpoint_path, monkeypatch):
    model = _model()
    save_checkpoint(checkpoint_path, model)
    before = checkpoint_path.read_bytes()

    def fail(handle, **arrays):
        handle.write(b"partial")
        raise OSError("simulated disk error")

    monkeypatch.setattr(np, "savez_compressed", fail)
    with pytest.raises(OSError, match="simulated disk error"):
        save_checkpoint(checkpoint_path, model)
    assert checkpoint_path.read_bytes() == before
    assert not list(checkpoint_path.parent.glob(f".{checkpoint_path.name}.*.pending"))
