# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent full reverse-equation and optimizer contract checks."""

from dataclasses import asdict
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from src.infrastructure import p43_training_reference as ref


@pytest.mark.parametrize("kwargs", [
    {}, {"dim": 16, "layers": 2, "length": 7}, {"steps": 2, "dim": 8, "length": 75},
    {"layers": 0, "decay": 0}, {"length": 1, "decay": 1},
])
def test_all_gradients_and_successive_updates(kwargs):
    result = ref.compare_training(**kwargs)
    assert result["passed"], result
    assert len(result["steps"]) == kwargs.get("steps", 5)
    assert result["parameter_count"] > 0


def fixture():
    _, Model, Config, _ = ref.p43._p43_api()
    cfg = Config(vocab_size=5, dim=8, num_heads=2, num_layers=1, ff_hidden_dim=16)
    model = Model(cfg)
    weights = {name: p.data.copy() for name, p in model.named_parameters().items()}
    return weights, asdict(cfg), np.array([[1, 2, 1], [1, 1, 1]]), np.array([2, 3])


def test_reference_does_not_call_p43_forward_or_backward(monkeypatch):
    weights, cfg, tokens, targets = fixture()
    _, Model, _, _ = ref.p43._p43_api()
    from az_tori_transformer.tensor import Tensor

    def forbidden(*args, **kwargs):
        raise AssertionError("independent reference invoked P43 execution")

    monkeypatch.setattr(Model, "__call__", forbidden)
    monkeypatch.setattr(Tensor, "backward", forbidden)
    before = {name: w.copy() for name, w in weights.items()}
    logits, loss, grads = ref.loss_and_gradients(weights, cfg, tokens, targets)
    assert logits.shape == (2, 3, 5)
    assert np.isfinite(loss)
    assert set(grads) == set(weights)
    for name in weights:
        np.testing.assert_array_equal(weights[name], before[name])


def test_manual_gradient_central_difference_and_label_independence():
    weights, cfg, tokens, targets = fixture()
    logits, _, grads = ref.loss_and_gradients(weights, cfg, tokens, targets)
    other_logits, _, _ = ref.loss_and_gradients(weights, cfg, tokens, (targets + 1) % 5)
    np.testing.assert_array_equal(logits, other_logits)
    for name, gradient in grads.items():
        index = np.unravel_index(np.argmax(np.abs(gradient)), gradient.shape)
        original = weights[name][index]
        weights[name][index] = original + 1e-6
        upper = ref.loss_and_gradients(weights, cfg, tokens, targets)[1]
        weights[name][index] = original - 1e-6
        lower = ref.loss_and_gradients(weights, cfg, tokens, targets)[1]
        weights[name][index] = original
        assert gradient[index] == pytest.approx((upper - lower) / 2e-6, abs=1e-7, rel=1e-4)


def test_native_optimizer_error_is_not_reported_as_parity(monkeypatch):
    Adam, _, _, _ = ref.p43._p43_api()
    original = Adam.step

    def broken_step(self):
        original(self)
        self.parameters[0].data += 1e-4

    monkeypatch.setattr(Adam, "step", broken_step)
    result = ref.compare_training(steps=1)
    assert not result["passed"]
    assert result["steps"][0]["max_updated_weight_absolute_error"] > 9e-5


def test_nonfinite_native_state_cannot_disappear_in_maximum(monkeypatch):
    Adam, _, _, _ = ref.p43._p43_api()
    original = Adam.step

    def broken_step(self):
        original(self)
        self.v[-1][0] = np.nan

    monkeypatch.setattr(Adam, "step", broken_step)
    with pytest.raises(FloatingPointError, match="nonfinite implementation"):
        ref.compare_training(steps=1)


def test_reference_workspace_bound_precedes_model_allocation(monkeypatch):
    _, Model, Config, _ = ref.p43._p43_api()
    cfg = Config(vocab_size=5, dim=128, num_heads=64, num_layers=1, ff_hidden_dim=256)
    weights = {name: p.data.copy() for name, p in Model(cfg).named_parameters().items()}

    def forbidden(*args, **kwargs):
        raise AssertionError("model allocated before workspace bound")

    monkeypatch.setattr(Model, "__init__", forbidden)
    with pytest.raises(ValueError, match="workspace"):
        ref.loss_and_gradients(weights, asdict(cfg), np.zeros((128, 128), dtype=int),
                               np.zeros(128, dtype=int))


@pytest.mark.parametrize("change", ["target_shape", "target_float", "target_range", "tokens_float",
                                    "token_range", "empty", "large_batch", "mode", "causal",
                                    "weight_names", "weight_dtype", "weight_nan", "weight_shape", "huge_config"])
def test_invalid_reference_inputs_rejected(change):
    weights, cfg, tokens, targets = fixture()
    if change == "target_shape":
        targets = targets[:1]
    elif change == "target_float":
        targets = targets.astype(float)
    elif change == "target_range":
        targets[0] = 5
    elif change == "tokens_float":
        tokens = tokens.astype(float)
    elif change == "token_range":
        tokens[0, 0] = -1
    elif change == "empty":
        tokens = tokens[:, :0]
    elif change == "large_batch":
        tokens = np.ones((129, 2), dtype=int)
    elif change == "mode":
        cfg["positional_mode"] = "rope"
    elif change == "causal":
        cfg["causal"] = False
    elif change == "weight_names":
        weights["bogus"] = weights.pop("head.weight")
    elif change == "weight_dtype":
        weights["head.weight"] = weights["head.weight"].astype(np.float32)
    elif change == "weight_nan":
        weights["head.weight"][0, 0] = np.nan
    elif change == "weight_shape":
        weights["head.weight"] = weights["head.weight"].T.copy()
    elif change == "huge_config":
        cfg["dim"] = 10**12
    with pytest.raises(ValueError):
        ref.loss_and_gradients(weights, cfg, tokens, targets)


@pytest.mark.parametrize("kwargs", [
    {"steps": True}, {"steps": 0}, {"steps": 21}, {"decay": np.nan}, {"decay": -1},
    {"decay": True}, {"seed": -1}, {"dim": 3}, {"layers": 3}, {"length": 129},
])
def test_invalid_comparison_bounds(kwargs):
    with pytest.raises(ValueError):
        ref.compare_training(**kwargs)


def test_measurement_cli_and_byte_hashes(tmp_path):
    assert ref.main(["--output-dir", str(tmp_path)]) == 0
    path, = tmp_path.glob("*.json")
    assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem
    report = json.loads(path.read_bytes())
    assert report["passed"]
    assert report["execution_spine"]["promotion"]["eligible"] is False
    assert all(row["passed"] for row in report["measurements"])
    assert ref.benchmark(tmp_path)[0] == path


def test_actual_failed_checkpoint_training_gradients():
    root = Path(__file__).resolve().parents[1] / "evidence"
    checkpoint = root / "a01eda39d6c3edb942c619ea9f709fc46b46f5664b9c1c64abdffa0884ac5cdc.npz"
    result = ref.compare_checkpoint(checkpoint.read_bytes())
    assert result["passed"], result
    assert result["training_rows"] == 81
    assert len(result["parameter_gradient_absolute_errors"]) == 19
