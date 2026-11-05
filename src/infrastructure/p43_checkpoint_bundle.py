# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Bounded actual P43 training checkpoints over the opaque checkpoint bundle.

Exactly one model, Adam, and PCG64 shard is required. Checkpoints are taken at
completed optimizer-step boundaries; gradients/graphs are not persisted. This
is a local serialization/resume contract, not a training-quality claim.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, fields
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys
from uuid import uuid4
import zipfile
import zlib

import numpy as np

from . import checkpoint_bundle as bundle

SCHEMA_VERSION = "az_p43_training_checkpoint_shards_v1"
MAX_ARCHIVE_BYTES = 32 * 1024 * 1024
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
MAX_ARRAY_BYTES = 8 * 1024 * 1024
MAX_MANIFEST_BYTES = 256 * 1024
MAX_HEADER_BYTES = 4096
MAX_MEMBERS = 1024
MAX_PARAMETERS = 1_000_000
MAX_LAYERS = 16
_ROOT = Path(__file__).resolve().parents[2]
_P43 = "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer"
_ROLES = ("model", "optimizer", "rng")
_ENVELOPE = {
    "schema_version", "role", "checkpoint_id", "owner_scope", "binding", "state",
}
_CHECKPOINT_FIELDS = {"format", "schema_version", "config", "optimizer", "rng", "metadata"}

__all__ = [
    "split_checkpoint", "join_checkpoint", "commit_checkpoint",
    "load_checkpoint", "load_p43_checkpoint",
]


def _api():
    root = str(_ROOT / Path(_P43).parent)
    if root not in sys.path:
        sys.path.insert(0, root)
    from az_tori_transformer import checkpoint
    return checkpoint


def _canonical(value: object) -> bytes:
    try:
        return json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False).encode("ascii")
    except (TypeError, ValueError, RecursionError) as exc:
        raise ValueError("checkpoint requires bounded finite JSON") from exc


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


def _document(raw: bytes) -> dict:
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError("checkpoint manifest exceeds byte bound")
    try:
        result = json.loads(raw, object_pairs_hook=_pairs, parse_constant=_reject_constant)
        if not isinstance(result, dict):
            raise ValueError("checkpoint manifest must be an object")
        if len(_canonical(result)) > MAX_MANIFEST_BYTES:
            raise ValueError("checkpoint manifest exceeds canonical byte bound")
        return result
    except (UnicodeError, RecursionError) as exc:
        raise ValueError("invalid bounded checkpoint JSON") from exc


@dataclass(frozen=True)
class _Archive:
    content: bytes
    manifest: dict
    shapes: dict[str, tuple[int, ...]]

    def members(self) -> dict[str, bytes]:
        try:
            with zipfile.ZipFile(io.BytesIO(self.content)) as archive:
                return {name: archive.read(name + ".npy") for name in self.shapes}
        except (zipfile.BadZipFile, zlib.error, EOFError, OSError) as exc:
            raise ValueError("invalid bounded NPZ member content") from exc


def _inspect(content: bytes) -> _Archive:
    """Inspect every ZIP size and NPY header without allocating NumPy arrays."""
    if not isinstance(content, bytes) or not content or len(content) > MAX_ARCHIVE_BYTES:
        raise ValueError("checkpoint archive exceeds input byte bound or is not bytes")
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = archive.infolist()
            if (not members or len(members) > MAX_MEMBERS
                    or len({m.filename for m in members}) != len(members)
                    or sum(m.file_size for m in members) > MAX_EXPANDED_BYTES):
                raise ValueError("NPZ exceeds member or expanded byte bounds")
            shapes = {}
            manifest = None
            for member in members:
                if (not member.filename.endswith(".npy") or member.is_dir()
                        or member.flag_bits & 1
                        or member.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED)):
                    raise ValueError("unsupported NPZ member")
                is_manifest = member.filename == "manifest.npy"
                limit = MAX_MANIFEST_BYTES if is_manifest else MAX_ARRAY_BYTES
                if member.file_size > limit + MAX_HEADER_BYTES + 16:
                    raise ValueError("NPY member exceeds byte bound")
                with archive.open(member) as stream:
                    version = np.lib.format.read_magic(stream)
                    if version == (1, 0):
                        reader = np.lib.format.read_array_header_1_0
                    elif version == (2, 0):
                        reader = np.lib.format.read_array_header_2_0
                    else:
                        raise ValueError("unsupported NPY header version")
                    shape, _, dtype = reader(stream, max_header_size=MAX_HEADER_BYTES)
                    if (len(shape) > 8 or any(type(n) is not int or n < 0 for n in shape)
                            or dtype.hasobject or dtype.fields is not None
                            or dtype.subdtype is not None or dtype.itemsize <= 0):
                        raise ValueError("unsupported NPY shape or dtype")
                    size = math.prod(shape) * dtype.itemsize
                    if size > limit or stream.tell() + size != member.file_size:
                        raise ValueError("NPY shape/dtype disagrees with bounded member bytes")
                    if is_manifest:
                        if shape != () or dtype.kind != "U":
                            raise ValueError("NPZ manifest must be scalar Unicode JSON")
                        endian = dtype.byteorder
                        if endian == "=":
                            endian = "<" if sys.byteorder == "little" else ">"
                        text = stream.read(size).decode("utf-32-le" if endian == "<" else "utf-32-be")
                        manifest = _document(text.rstrip("\0").encode("utf-8"))
                    else:
                        if dtype != np.dtype("float64"):
                            raise ValueError("checkpoint numerical arrays must be float64")
                        shapes[member.filename[:-4]] = shape
            if manifest is None:
                raise ValueError("NPZ requires exactly one manifest")
            return _Archive(content, manifest, shapes)
    except (zipfile.BadZipFile, EOFError, KeyError, TypeError, UnicodeError,
            NotImplementedError, OverflowError, OSError, zlib.error) as exc:
        raise ValueError("invalid bounded P43 NPZ archive") from exc


def _int(value, lower: int, upper: int, name: str) -> None:
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError(f"{name} must be an integer within bounds")


def _parameter_shapes(config) -> dict[str, tuple[int, ...]]:
    api = _api()
    Config = api.GeometricToriTransformerConfig
    if not isinstance(config, dict) or set(config) != {f.name for f in fields(Config)}:
        raise ValueError("config must contain exactly the P43 model fields")
    for name in ("vocab_size", "dim", "num_heads", "ff_hidden_dim"):
        _int(config[name], 1, MAX_PARAMETERS, f"config {name}")
    _int(config["num_layers"], 0, MAX_LAYERS, "config num_layers")
    _int(config["seed"], 0, 2**64 - 1, "config seed")
    if type(config["causal"]) is not bool or not isinstance(config["positional_mode"], str):
        raise ValueError("invalid config causal/positional_mode")
    cfg = Config(**config)
    d, h, v = cfg.dim, cfg.ff_hidden_dim, cfg.vocab_size
    from az_tori_transformer.toroidal_geometry import HALF_TURN
    bias = cfg.num_heads * (HALF_TURN + 1) if cfg.positional_mode != "rope" else 0
    count = 2 * v * d + cfg.num_layers * (4 * d * d + 2 * d * h + 6 * d + h + bias) + 2 * d + v
    if count > MAX_PARAMETERS:
        raise ValueError("model exceeds parameter allocation bound")
    shapes = {"token_embedding.weight": (v, d)}
    for i in range(cfg.num_layers):
        prefix = f"blocks.{i}"
        for name in ("wq", "wk", "wv", "wo"):
            shapes[f"{prefix}.attn.{name}.weight"] = (d, d)
        shapes[f"{prefix}.attn.wo.bias"] = (d,)
        if cfg.positional_mode != "rope":
            shapes[f"{prefix}.attn.relative_bias"] = (cfg.num_heads, HALF_TURN + 1)
        for name, shape in (
            ("ff.fc1.weight", (d, h)), ("ff.fc1.bias", (h,)),
            ("ff.fc2.weight", (h, d)), ("ff.fc2.bias", (d,)),
            ("ln1.gamma", (d,)), ("ln1.beta", (d,)),
            ("ln2.gamma", (d,)), ("ln2.beta", (d,)),
        ):
            shapes[f"{prefix}.{name}"] = shape
    shapes.update({
        "ln_final.gamma": (d,), "ln_final.beta": (d,),
        "head.weight": (d, v), "head.bias": (v,),
    })
    return shapes


def _rng(state) -> None:
    if not isinstance(state, dict) or set(state) != {"bit_generator", "state", "has_uint32", "uinteger"}:
        raise ValueError("requires exact PCG64 RNG state")
    if state["bit_generator"] != "PCG64":
        raise ValueError("requires PCG64 RNG")
    inner = state["state"]
    if not isinstance(inner, dict) or set(inner) != {"state", "inc"}:
        raise ValueError("invalid PCG64 inner state")
    for name in ("state", "inc"):
        _int(inner[name], 0, 2**128 - 1, f"PCG64 {name}")
    if inner["inc"] % 2 != 1:
        raise ValueError("PCG64 increment must be odd")
    _int(state["has_uint32"], 0, 1, "PCG64 has_uint32")
    _int(state["uinteger"], 0, 2**32 - 1, "PCG64 uinteger")


def _validate(
    manifest: dict,
    shapes: dict[str, tuple[int, ...]],
    *,
    require_training_state: bool = True,
) -> None:
    if set(manifest) != _CHECKPOINT_FIELDS:
        raise ValueError("invalid checkpoint manifest fields")
    api = _api()
    if (manifest["format"] != api.FORMAT or type(manifest["schema_version"]) is not int
            or manifest["schema_version"] != api.SCHEMA_VERSION):
        raise ValueError("unsupported P43 checkpoint format or schema")
    params = _parameter_shapes(manifest["config"])
    adam = manifest["optimizer"]
    if adam is None:
        if require_training_state:
            raise ValueError("training checkpoints require exact Adam state")
    else:
        if not isinstance(adam, dict) or set(adam) != {"lr", "beta1", "beta2", "eps", "t"}:
            raise ValueError("requires exact Adam hyperparameters and step")
        for name in ("lr", "beta1", "beta2", "eps"):
            value = adam[name]
            if (type(value) not in (int, float)
                    or (type(value) is int and abs(value) > 2**63 - 1)
                    or not math.isfinite(value)):
                raise ValueError("Adam hyperparameters must be finite supported numbers")
        if adam["lr"] <= 0 or adam["eps"] <= 0 or not (0 <= adam["beta1"] < 1 and 0 <= adam["beta2"] < 1):
            raise ValueError("invalid Adam hyperparameters")
        _int(adam["t"], 0, 2**63 - 1, "Adam step")
    rng = manifest["rng"]
    if rng is None:
        if require_training_state:
            raise ValueError("training checkpoints require exact PCG64 RNG state")
    else:
        _rng(rng)
    if not isinstance(manifest["metadata"], dict):
        raise ValueError("metadata must be a JSON object")
    expected = {f"model/{name}": shape for name, shape in params.items()}
    if adam is not None:
        expected.update({f"adam/{moment}/{name}": shape
                         for moment in ("m", "v") for name, shape in params.items()})
    if shapes != expected:
        raise ValueError("checkpoint parameter names/shapes do not match model and Adam")


def _check_values(archive: _Archive) -> None:
    # Header/config/member bounds have all passed before NumPy reads any array.
    try:
        with np.load(io.BytesIO(archive.content), allow_pickle=False) as arrays:
            for name in archive.shapes:
                value = arrays[name]
                if not np.all(np.isfinite(value)) or (name.startswith("adam/v/") and np.any(value < 0)):
                    raise ValueError("checkpoint has invalid numerical state")
    except (zipfile.BadZipFile, zlib.error, EOFError, OSError) as exc:
        raise ValueError("invalid bounded NPZ numerical content") from exc


def load_p43_checkpoint(content: bytes):
    """Safely restore a P43 inference or training checkpoint from NPZ bytes."""
    archive = _inspect(content)
    _validate(archive.manifest, archive.shapes, require_training_state=False)
    _check_values(archive)
    return _api().load_checkpoint(io.BytesIO(content))


def _binding(manifest: dict, members: dict[str, bytes]) -> str:
    return hashlib.sha256(_canonical({
        "checkpoint": manifest,
        "arrays": {name: hashlib.sha256(raw).hexdigest() for name, raw in sorted(members.items())},
    })).hexdigest()


def _npz(manifest: dict, members: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    raw = io.BytesIO()
    np.save(raw, np.array(_canonical(manifest).decode("ascii")), allow_pickle=False)
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, value in sorted({**members, "manifest": raw.getvalue()}.items()):
            info = zipfile.ZipInfo(name + ".npy", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, value)
    result = stream.getvalue()
    if len(result) > MAX_ARCHIVE_BYTES:
        raise ValueError("encoded NPZ exceeds byte bound")
    return result


def split_checkpoint(
    content: bytes, *, checkpoint_id: str, owner_scope: str,
) -> tuple[bundle.CheckpointShard, ...]:
    """Split an actual safe P43 NPZ into model, optimizer and RNG role shards.

    Each envelope binds scope, checkpoint ID, full config/metadata/training state
    and all named NPY contents. SHA-256 provides integrity, not authentication.
    """
    bundle._text(checkpoint_id, "checkpoint_id")
    bundle._text(owner_scope, "owner_scope")
    archive = _inspect(content)
    _validate(archive.manifest, archive.shapes)
    _check_values(archive)
    manifest, members = archive.manifest, archive.members()
    binding = _binding(manifest, members)
    states = {
        "model": {key: manifest[key] for key in ("format", "schema_version", "config", "metadata")},
        "optimizer": manifest["optimizer"], "rng": manifest["rng"],
    }
    shards = []
    for role, prefix in (("model", "model/"), ("optimizer", "adam/"), ("rng", None)):
        envelope = {
            "schema_version": SCHEMA_VERSION, "role": role, "binding": binding,
            "checkpoint_id": checkpoint_id, "owner_scope": owner_scope, "state": states[role],
        }
        selected = {name: raw for name, raw in members.items()
                    if prefix is not None and name.startswith(prefix)}
        payload = _npz(envelope, selected)
        _inspect(payload)
        shards.append(bundle.CheckpointShard(f"p43-{role}", role, payload))
    return tuple(shards)


def join_checkpoint(checkpoint: bundle.CheckpointBundle) -> bytes:
    """Validate a committed bundle and reconstruct the safe P43 checkpoint."""
    if not isinstance(checkpoint, bundle.CheckpointBundle):
        raise ValueError("expected CheckpointBundle")
    if (len(checkpoint.shards) != 3
            or {shard.role for shard in checkpoint.shards} != set(_ROLES)):
        raise ValueError("requires exactly one model, optimizer and rng role")
    identity = bundle.checkpoint_manifest_id(
        checkpoint_id=checkpoint.checkpoint_id, owner_scope=checkpoint.owner_scope,
        shards=checkpoint.shards,
    )
    if identity != checkpoint.manifest_id:
        raise ValueError("bundle manifest hash binding mismatch")
    archives = {}
    for shard in checkpoint.shards:
        archive = _inspect(shard.payload)
        envelope = archive.manifest
        if (set(envelope) != _ENVELOPE or envelope["schema_version"] != SCHEMA_VERSION
                or envelope["role"] != shard.role
                or envelope["checkpoint_id"] != checkpoint.checkpoint_id
                or envelope["owner_scope"] != checkpoint.owner_scope):
            raise ValueError("unsupported shard schema or role/scope/checkpoint binding mismatch")
        bundle._digest(envelope["binding"])
        prefix = {"model": "model/", "optimizer": "adam/", "rng": None}[shard.role]
        if any(prefix is None or not name.startswith(prefix) for name in archive.shapes):
            raise ValueError("shard contains arrays outside its named role")
        archives[shard.role] = archive
    model_state = archives["model"].manifest["state"]
    if not isinstance(model_state, dict) or set(model_state) != {"format", "schema_version", "config", "metadata"}:
        raise ValueError("invalid model shard state fields")
    manifest = {
        **model_state, "optimizer": archives["optimizer"].manifest["state"],
        "rng": archives["rng"].manifest["state"],
    }
    shapes = {name: shape for archive in archives.values() for name, shape in archive.shapes.items()}
    _validate(manifest, shapes)
    if sum(len(archive.content) for archive in archives.values()) > MAX_EXPANDED_BYTES:
        raise ValueError("combined shard bytes exceed bound")
    members = {name: raw for archive in archives.values() for name, raw in archive.members().items()}
    if sum(map(len, members.values())) > MAX_EXPANDED_BYTES - MAX_MANIFEST_BYTES:
        raise ValueError("combined expanded shard bytes exceed bound")
    binding = _binding(manifest, members)
    if any(archive.manifest["binding"] != binding for archive in archives.values()):
        raise ValueError("cross-shard training state hash binding mismatch")
    for archive in archives.values():
        _check_values(archive)
    content = _npz(manifest, members)
    full = _inspect(content)
    _validate(full.manifest, full.shapes)
    return content


def commit_checkpoint(
    directory: str | Path, *, content: bytes, checkpoint_id: str, owner_scope: str,
    directory_fd: int | None = None,
) -> str:
    """Validate/split a training checkpoint and use the existing manifest commit."""
    shards = split_checkpoint(content, checkpoint_id=checkpoint_id, owner_scope=owner_scope)
    return bundle.commit_checkpoint(
        directory, checkpoint_id=checkpoint_id, owner_scope=owner_scope, shards=shards,
        directory_fd=directory_fd,
    )


def load_checkpoint(
    directory: str | Path, manifest_id: str, *, owner_scope: str,
    directory_fd: int | None = None,
):
    """Restore model, Adam and PCG64 using existing bundle ID/owner-scope checks."""
    checkpoint = bundle.load_checkpoint(
        directory, manifest_id, owner_scope=owner_scope, directory_fd=directory_fd,
    )
    return load_p43_checkpoint(join_checkpoint(checkpoint))


SOURCE_FILES = tuple(sorted({
    "src/infrastructure/__init__.py",
    "src/infrastructure/p43_checkpoint_bundle.py",
    "src/infrastructure/checkpoint_bundle.py",
    "src/infrastructure/artifact_io.py",
    "src/infrastructure/execution_spine.py",
    "9-INFRASTRUCTURE/az-ml-program/tests/test_p43_checkpoint_bundle.py",
    "9-INFRASTRUCTURE/az-ml-program/tests/test_checkpoint_bundle.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/tests/test_checkpoint.py",
    *(path.relative_to(_ROOT).as_posix() for path in (_ROOT / _P43).glob("*.py")),
}))


def main(argv: list[str] | None = None) -> int:
    """Run a deterministic actual numeric resume fixture and publish its receipt."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--owner-scope", default="research:p43-checkpoint-fixture")
    args = parser.parse_args(argv)
    from .artifact_io import publish_immutable
    from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
    root_fd = None
    try:
        root_fd = bundle._open_root(args.output_dir)
        source_hashes = {path: hashlib.sha256((_ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES}
        api = _api()
        from az_tori_transformer.optim import Adam
        from az_tori_transformer.tensor import cross_entropy
        model = api.GeometricToriTransformer(api.GeometricToriTransformerConfig(
            vocab_size=7, dim=8, num_heads=2, num_layers=1,
            ff_hidden_dim=12, seed=19,
        ))
        optimizer = Adam(model.parameters(), lr=0.003, betas=(0.8, 0.95), eps=1e-7)
        rng = np.random.default_rng(37)

        def step(candidate, adam, generator):
            tokens = generator.integers(0, 7, (1, 5))
            logits, _ = candidate(tokens)
            loss = cross_entropy(logits, np.roll(tokens, -1, axis=1))
            result = (tokens, logits.data.copy(), loss.data.copy())
            adam.zero_grad()
            loss.backward()
            adam.step()
            return result

        for _ in range(3):
            step(model, optimizer, rng)
        metadata = {"fixture": "constructed numeric minibatches", "training_quality_claim": False}
        staging = Path.cwd() / f".p43-checkpoint-{uuid4().hex}.npz"
        try:
            api.save_checkpoint(staging, model, optimizer=optimizer, rng=rng, metadata=metadata)
            with staging.open("rb") as stream:
                source = stream.read(MAX_ARCHIVE_BYTES + 1)
        finally:
            staging.unlink(missing_ok=True)
        identity = commit_checkpoint(
            args.output_dir, content=source, checkpoint_id="numeric-fixture-step-3",
            owner_scope=args.owner_scope, directory_fd=root_fd,
        )
        committed = bundle.load_checkpoint(
            args.output_dir, identity, owner_scope=args.owner_scope, directory_fd=root_fd,
        )
        reconstructed = join_checkpoint(committed)
        restored = load_checkpoint(
            args.output_dir, identity, owner_scope=args.owner_scope, directory_fd=root_fd,
        )
        if (restored.metadata != metadata or restored.model.cfg != model.cfg
                or restored.rng.bit_generator.state != rng.bit_generator.state):
            raise ValueError("actual fixture state did not round-trip")
        for original, actual in zip(
            step(model, optimizer, rng), step(restored.model, restored.optimizer, restored.rng), strict=True,
        ):
            np.testing.assert_array_equal(original, actual, strict=True)
        for a, b in zip(model.parameters(), restored.model.parameters(), strict=True):
            np.testing.assert_array_equal(a.data, b.data, strict=True)
        for name in ("m", "v"):
            for a, b in zip(getattr(optimizer, name), getattr(restored.optimizer, name), strict=True):
                np.testing.assert_array_equal(a, b, strict=True)
        for name in ("lr", "beta1", "beta2", "eps", "t"):
            if getattr(optimizer, name) != getattr(restored.optimizer, name):
                raise ValueError("actual fixture optimizer did not resume exactly")
        np.testing.assert_array_equal(
            rng.integers(0, 2**32, 7, dtype=np.uint32),
            restored.rng.integers(0, 2**32, 7, dtype=np.uint32), strict=True,
        )
        if rng.bit_generator.state != restored.rng.bit_generator.state:
            raise ValueError("actual fixture RNG did not resume exactly")
        artifacts = {}

        def record(label, payload, suffix):
            digest = hashlib.sha256(payload).hexdigest()
            publish_immutable(
                args.output_dir, digest, payload, suffix=suffix, directory_fd=root_fd,
            )
            artifacts[label] = {"filename": digest + suffix, "sha256": digest, "byte_length": len(payload)}

        record("source_checkpoint", source, ".npz")
        record("reconstructed_checkpoint", reconstructed, ".npz")
        manifest_bytes = bundle._encoded_manifest(committed.checkpoint_id, committed.owner_scope, committed.shards)[0]
        record("bundle_manifest", manifest_bytes, ".json")
        for shard in committed.shards:
            record(f"shard_{shard.role}", shard.payload, ".bin")
        payload = {
            "schema_version": "az_p43_actual_checkpoint_resume_receipt_v1",
            "checkpoint_manifest_id": identity, "owner_scope": args.owner_scope,
            "source_sha256": source_hashes, "artifacts": artifacts,
            "runtime": {"python": sys.version.split()[0], "numpy": np.__version__},
            "fixture": {"optimizer_steps_before_checkpoint": 3, "identical_next_minibatches": 1,
                        "parameter_count": model.num_parameters(), "model_config": model.cfg.__dict__},
            "exact_resume": {key: True for key in (
                "minibatch", "logits", "loss", "parameters", "adam_hyperparameters",
                "adam_step", "adam_m", "adam_v", "pcg64_outputs", "pcg64_state", "metadata", "config",
            )},
            "promotion": False, "training_quality_claim": False,
            "execution_spine": ExecutionSpineRecord(
                surface_id="az-p43-actual-checkpoint-bundle",
                surface_kind="checkpoint_resume_receipt", lane="az_ml_infrastructure",
                status="actual_numeric_resume_verified", generated_at_utc=None,
                summary="Actual P43 Adam/PCG64 exact continuation on constructed numeric minibatches only.",
                canonical_paths=["src/infrastructure/p43_checkpoint_bundle.py"],
                sources=list(SOURCE_FILES),
                governance=build_fail_closed_governance(
                    epistemic_label="bounded actual checkpoint resume, not model quality",
                    promotion_rule="Serialization fidelity is not promotion evidence.",
                    residual_blockers=[
                        "Only bounded P43 float64 NPZ, Adam and PCG64 at completed optimizer-step boundaries.",
                        "Local manifest commit only; SHA-256 integrity is not authenticated provenance.",
                        "Constructed numeric fixture; no arithmetic quality or distributed-training claim.",
                    ],
                ),
                promotion={"eligible": False, "model_quality_claim": False, "physics_claim": False},
            ).to_dict(),
        }
        unique = {item["filename"]: item["byte_length"] for item in artifacts.values()}
        payload["bytes"] = {
            "bundle_complete_bytes": len(manifest_bytes) + sum(len(s.payload) for s in committed.shards),
            "artifacts_excluding_receipt": sum(unique.values()),
            "receipt": 0, "complete_published_bytes": 0,
        }
        for _ in range(10):
            receipt = _canonical(payload)
            if payload["bytes"]["receipt"] == len(receipt):
                break
            payload["bytes"]["receipt"] = len(receipt)
            payload["bytes"]["complete_published_bytes"] = sum(unique.values()) + len(receipt)
        else:
            raise ValueError("receipt byte accounting did not converge")
        if source_hashes != {path: hashlib.sha256((_ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES}:
            raise ValueError("implementation sources changed during fixture execution")
        digest = hashlib.sha256(receipt).hexdigest()
        publish_immutable(
            args.output_dir, digest, receipt, suffix=".json", directory_fd=root_fd,
        )
        print(json.dumps({"receipt_id": digest, "checkpoint_manifest_id": identity,
                          "complete_published_bytes": payload["bytes"]["complete_published_bytes"]}, sort_keys=True))
    except (ValueError, OSError, AssertionError) as exc:
        parser.exit(2, f"{exc}\n")
    finally:
        if root_fd is not None:
            os.close(root_fd)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
