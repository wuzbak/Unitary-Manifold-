# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Versioned NPZ/JSON checkpoints for this adjacent-track NumPy architecture."""

from __future__ import annotations

from dataclasses import asdict, dataclass, fields
import json
import os
from pathlib import Path
from typing import Any
from uuid import uuid4

import numpy as np

from .model import GeometricToriTransformer, GeometricToriTransformerConfig
from .optim import Adam

__all__ = ["LoadedCheckpoint", "save_checkpoint", "load_checkpoint"]

FORMAT = "az-tori-transformer-npz"
SCHEMA_VERSION = 1


@dataclass
class LoadedCheckpoint:
    model: GeometricToriTransformer
    optimizer: Adam | None
    rng: np.random.Generator | None
    metadata: dict[str, Any]


def _config(value: dict[str, Any]) -> GeometricToriTransformerConfig:
    if not isinstance(value, dict) or set(value) != {f.name for f in fields(GeometricToriTransformerConfig)}:
        raise ValueError("checkpoint config must contain exactly the model config fields")
    for name in ("vocab_size", "dim", "num_heads", "ff_hidden_dim"):
        if type(value[name]) is not int or value[name] <= 0:
            raise ValueError(f"config {name} must be a positive integer")
    for name in ("num_layers", "seed"):
        if type(value[name]) is not int or value[name] < 0:
            raise ValueError(f"config {name} must be a nonnegative integer")
    if type(value["causal"]) is not bool:
        raise ValueError("config causal must be a boolean")
    return GeometricToriTransformerConfig(**value)


def _adam(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"lr", "beta1", "beta2", "eps", "t"}:
        raise ValueError("invalid Adam metadata")
    for name in ("lr", "beta1", "beta2", "eps"):
        number = value[name]
        if type(number) not in (int, float) or not np.isfinite(number):
            raise ValueError(f"Adam {name} must be finite")
    if value["lr"] <= 0 or value["eps"] <= 0:
        raise ValueError("Adam lr and eps must be positive")
    if not (0 <= value["beta1"] < 1 and 0 <= value["beta2"] < 1):
        raise ValueError("Adam betas must be in [0, 1)")
    if type(value["t"]) is not int or value["t"] < 0:
        raise ValueError("Adam step must be a nonnegative integer")
    return value


def _rng(value: Any) -> np.random.Generator | None:
    if value is None:
        return None
    if not isinstance(value, dict) or value.get("bit_generator") != "PCG64":
        raise ValueError("checkpoint RNG must use PCG64 (numpy.default_rng)")
    rng = np.random.default_rng()
    try:
        rng.bit_generator.state = value
    except (TypeError, ValueError, KeyError, OverflowError) as exc:
        raise ValueError("invalid PCG64 RNG state") from exc
    return rng


def _array(value: np.ndarray, shape: tuple[int, ...], name: str, *, nonnegative: bool = False) -> np.ndarray:
    if value.shape != shape or value.dtype != np.dtype("float64"):
        raise ValueError(f"{name}: expected shape {shape} and float64 dtype")
    if not np.all(np.isfinite(value)) or (nonnegative and np.any(value < 0)):
        raise ValueError(f"{name}: invalid numerical values")
    return value.copy()


def save_checkpoint(
    path: str | Path,
    model: GeometricToriTransformer,
    *,
    optimizer: Adam | None = None,
    rng: np.random.Generator | None = None,
    metadata: dict[str, Any] | None = None,
) -> None:
    """Atomically save weights and optional training state; never serialize pickle.

    ``metadata`` is a JSON object for caller-owned task/tokenizer provenance.
    Checkpoints are intended at completed optimizer-step boundaries; gradients
    and autograd graphs are deliberately not persisted.
    """
    cfg = asdict(model.cfg)
    _config(cfg)
    params = model.named_parameters()
    arrays = {f"model/{name}": _array(p.data, p.shape, name) for name, p in params.items()}
    adam = None
    if optimizer is not None:
        if len(optimizer.parameters) != len(params) or any(
            actual is not expected for actual, expected in zip(optimizer.parameters, params.values())
        ):
            raise ValueError("optimizer must own this model's parameters in model order")
        adam = _adam({
            "lr": optimizer.lr, "beta1": optimizer.beta1, "beta2": optimizer.beta2,
            "eps": optimizer.eps, "t": optimizer.t,
        })
        if len(optimizer.m) != len(params) or len(optimizer.v) != len(params):
            raise ValueError("Adam moment count does not match model")
        for i, (name, p) in enumerate(params.items()):
            arrays[f"adam/m/{name}"] = _array(optimizer.m[i], p.shape, f"adam/m/{name}")
            arrays[f"adam/v/{name}"] = _array(optimizer.v[i], p.shape, f"adam/v/{name}", nonnegative=True)
    rng_state = rng.bit_generator.state if rng is not None else None
    _rng(rng_state)
    if metadata is None:
        metadata = {}
    if not isinstance(metadata, dict):
        raise ValueError("metadata must be a JSON object")
    manifest = {
        "format": FORMAT, "schema_version": SCHEMA_VERSION, "config": cfg,
        "optimizer": adam, "rng": rng_state, "metadata": metadata,
    }
    try:
        encoded = json.dumps(manifest, allow_nan=False, sort_keys=True)
    except (TypeError, ValueError) as exc:
        raise ValueError("metadata must contain finite JSON-serializable values") from exc
    arrays["manifest"] = np.array(encoded)
    path = Path(path)
    pending = path.with_name(f".{path.name}.{uuid4().hex}.pending")
    try:
        with pending.open("xb") as handle:
            np.savez_compressed(handle, **arrays)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(pending, path)
    finally:
        pending.unlink(missing_ok=True)


def load_checkpoint(path: str | Path) -> LoadedCheckpoint:
    """Create a fresh model/optimizer/RNG after validating a schema-v1 archive."""
    archive = np.load(path, allow_pickle=False)
    if not isinstance(archive, np.lib.npyio.NpzFile):
        raise ValueError("checkpoint must be an NPZ archive")
    with archive:
        if "manifest" not in archive.files:
            raise ValueError("checkpoint is missing its manifest")
        raw = archive["manifest"]
        if raw.shape != () or raw.dtype.kind != "U":
            raise ValueError("manifest must be a scalar JSON string")
        try:
            manifest = json.loads(raw.item(), parse_constant=_reject_constant, object_pairs_hook=_json_object)
            json.dumps(manifest, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid checkpoint JSON manifest") from exc
        required = {"format", "schema_version", "config", "optimizer", "rng", "metadata"}
        if not isinstance(manifest, dict) or set(manifest) != required:
            raise ValueError("invalid checkpoint manifest fields")
        if manifest["format"] != FORMAT or type(manifest["schema_version"]) is not int or manifest["schema_version"] != SCHEMA_VERSION:
            raise ValueError("unsupported checkpoint format or schema version")
        cfg = _config(manifest["config"])
        adam = _adam(manifest["optimizer"]) if manifest["optimizer"] is not None else None
        rng = _rng(manifest["rng"])
        if not isinstance(manifest["metadata"], dict):
            raise ValueError("metadata must be a JSON object")
        model = GeometricToriTransformer(cfg)
        params = model.named_parameters()
        expected = {"manifest"} | {f"model/{name}" for name in params}
        if adam is not None:
            expected |= {f"adam/{moment}/{name}" for moment in ("m", "v") for name in params}
        if len(archive.files) != len(expected) or set(archive.files) != expected:
            raise ValueError("checkpoint array names do not match its model and optimizer")
        for name, p in params.items():
            p.data = _array(archive[f"model/{name}"], p.shape, name)
        optimizer = None
        if adam is not None:
            optimizer = Adam(model.parameters(), lr=adam["lr"], betas=(adam["beta1"], adam["beta2"]), eps=adam["eps"])
            optimizer.t = adam["t"]
            optimizer.m = [_array(archive[f"adam/m/{name}"], p.shape, f"adam/m/{name}") for name, p in params.items()]
            optimizer.v = [_array(archive[f"adam/v/{name}"], p.shape, f"adam/v/{name}", nonnegative=True) for name, p in params.items()]
    return LoadedCheckpoint(model, optimizer, rng, manifest["metadata"])


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant: {value}")


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result
