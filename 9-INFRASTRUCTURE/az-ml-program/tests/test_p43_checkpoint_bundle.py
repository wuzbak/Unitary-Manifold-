# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Actual P43 optimizer/RNG continuation and bounded shard rejection contracts."""

from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
from uuid import uuid4
import zipfile

import numpy as np
import pytest

from src.infrastructure import checkpoint_bundle as bundle
from src.infrastructure import p43_checkpoint_bundle as adapter

api = adapter._api()
from az_tori_transformer.optim import Adam
from az_tori_transformer.tensor import cross_entropy


@pytest.fixture
def workspace():
    path = Path(__file__).parent / f".p43-bundle-{uuid4().hex}"
    path.mkdir()
    try:
        yield path
    finally:
        shutil.rmtree(path)


def _model(mode="toroidal", layers=1, causal=True):
    return api.GeometricToriTransformer(api.GeometricToriTransformerConfig(
        vocab_size=7, dim=8, num_heads=2, num_layers=layers,
        ff_hidden_dim=12, causal=causal, positional_mode=mode, seed=19,
    ))


def _step(model, optimizer, rng):
    tokens = rng.integers(0, model.cfg.vocab_size, size=(1, 5))
    targets = np.roll(tokens, -1, axis=1)
    logits, _ = model(tokens)
    before = logits.data.copy()
    loss = cross_entropy(logits, targets)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return tokens, before, loss.data.copy()


def _save(path, *, mode="toroidal", layers=1, steps=3, causal=True):
    model = _model(mode, layers, causal)
    optimizer = Adam(model.parameters(), lr=0.003, betas=(0.8, 0.95), eps=1e-7)
    rng = np.random.default_rng(37)
    for _ in range(steps):
        _step(model, optimizer, rng)
    metadata = {"fixture": "constructed numeric minibatches", "nested": {"labels": ["α", "b"], "count": 3}}
    api.save_checkpoint(path, model, optimizer=optimizer, rng=rng, metadata=metadata)
    return model, optimizer, rng, metadata


@pytest.fixture
def content(workspace):
    path = workspace / "source.npz"
    _save(path)
    return path.read_bytes()


def _split(content):
    return adapter.split_checkpoint(content, checkpoint_id="step-3", owner_scope="tenant:test")


def _bundle(shards, *, checkpoint_id="step-3", owner_scope="tenant:test"):
    shards = tuple(shards)
    identity = bundle.checkpoint_manifest_id(
        checkpoint_id=checkpoint_id, owner_scope=owner_scope, shards=shards,
    )
    return bundle.CheckpointBundle(checkpoint_id, owner_scope, shards, identity)


def _rewrite(content, mutate):
    with np.load(io.BytesIO(content), allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
    manifest = json.loads(arrays["manifest"].item())
    mutate(manifest, arrays)
    arrays["manifest"] = np.array(json.dumps(manifest, allow_nan=False))
    out = io.BytesIO()
    np.savez_compressed(out, **arrays)
    return out.getvalue()


def _rewrite_role(shards, role, mutate):
    return tuple(
        replace(shard, payload=_rewrite(shard.payload, mutate)) if shard.role == role else shard
        for shard in shards
    )


@pytest.mark.parametrize("mode", ["toroidal", "rope", "rope_matched"])
@pytest.mark.parametrize("causal", [True, False])
def test_actual_exact_resume_logits_loss_params_moments_rng(workspace, mode, causal):
    source = workspace / "source.npz"
    model, optimizer, rng, metadata = _save(source, mode=mode, layers=2, causal=causal)
    content = source.read_bytes()
    assert optimizer.t == 3 and rng.bit_generator.state["has_uint32"] == 1
    shards = _split(content)
    assert tuple(shard.role for shard in shards) == ("model", "optimizer", "rng")
    assert len({hashlib.sha256(shard.payload).hexdigest() for shard in shards}) == 3
    checkpoint_id = bundle.commit_checkpoint(
        workspace, checkpoint_id="step-3", owner_scope="tenant:test", shards=shards,
    )
    assert checkpoint_id == adapter.commit_checkpoint(
        workspace, content=content, checkpoint_id="step-3", owner_scope="tenant:test",
    )
    actual_bundle = bundle.load_checkpoint(workspace, checkpoint_id, owner_scope="tenant:test")
    joined = adapter.join_checkpoint(actual_bundle)
    # Reconstruction is the existing non-pickle P43 format, not a surrogate model.
    restored_direct = api.load_checkpoint(io.BytesIO(joined))
    restored = adapter.load_checkpoint(workspace, checkpoint_id, owner_scope="tenant:test")
    assert isinstance(restored, api.LoadedCheckpoint)
    assert restored.model.cfg == model.cfg == restored_direct.model.cfg
    assert restored.metadata == metadata == restored_direct.metadata
    assert restored.rng.bit_generator.state == rng.bit_generator.state
    assert (restored.optimizer.lr, restored.optimizer.beta1, restored.optimizer.beta2,
            restored.optimizer.eps, restored.optimizer.t) == (0.003, 0.8, 0.95, 1e-7, 3)
    assert all(p.grad is None for p in restored.model.parameters())
    for _ in range(3):
        expected = _step(model, optimizer, rng)
        actual = _step(restored.model, restored.optimizer, restored.rng)
        for left, right in zip(expected, actual, strict=True):
            np.testing.assert_array_equal(left, right, strict=True)
        for (name, left), (restored_name, right) in zip(
            model.named_parameters().items(), restored.model.named_parameters().items(), strict=True,
        ):
            assert name == restored_name
            np.testing.assert_array_equal(left.data, right.data, strict=True)
        for moment in ("m", "v"):
            for left, right in zip(getattr(optimizer, moment), getattr(restored.optimizer, moment), strict=True):
                np.testing.assert_array_equal(left, right, strict=True)
        assert optimizer.t == restored.optimizer.t
        np.testing.assert_array_equal(
            rng.integers(0, 2**32, 7, dtype=np.uint32),
            restored.rng.integers(0, 2**32, 7, dtype=np.uint32), strict=True,
        )
        assert rng.bit_generator.state == restored.rng.bit_generator.state
    with np.load(io.BytesIO(joined), allow_pickle=False) as archive:
        assert all(not archive[name].dtype.hasobject for name in archive.files)


def test_zero_step_and_zero_layers_keep_all_three_roles(workspace):
    path = workspace / "zero.npz"
    _, optimizer, _, _ = _save(path, layers=0, steps=0)
    checkpoint = _bundle(_split(path.read_bytes()))
    loaded = adapter.load_p43_checkpoint(adapter.join_checkpoint(checkpoint))
    assert loaded.optimizer.t == optimizer.t == 0
    assert loaded.model.cfg.num_layers == 0
    _step(loaded.model, loaded.optimizer, loaded.rng)


def test_safe_loader_accepts_bounded_inference_checkpoint_without_training_state(workspace):
    source = workspace / "inference.npz"
    model = _model()
    api.save_checkpoint(source, model, metadata={"purpose": "inference"})

    loaded = adapter.load_p43_checkpoint(source.read_bytes())

    assert loaded.model.cfg == model.cfg
    assert loaded.metadata == {"purpose": "inference"}
    assert loaded.optimizer is None
    assert loaded.rng is None


def test_committed_checkpoint_survives_writer_process_loss_and_fresh_process_restore(workspace):
    source = workspace / "source.npz"
    model, optimizer, rng, metadata = _save(source)
    content = source.read_bytes()

    def digest(arrays):
        state = hashlib.sha256()
        for array in arrays:
            state.update(array.tobytes(order="C"))
        return state.hexdigest()

    expected = {
        "config": {
            "causal": model.cfg.causal,
            "dim": model.cfg.dim,
            "ff_hidden_dim": model.cfg.ff_hidden_dim,
            "num_heads": model.cfg.num_heads,
            "num_layers": model.cfg.num_layers,
            "positional_mode": model.cfg.positional_mode,
            "seed": model.cfg.seed,
            "vocab_size": model.cfg.vocab_size,
        },
        "metadata": metadata,
        "model_sha256": digest(parameter.data for parameter in model.parameters()),
        "optimizer": {
            "beta1": optimizer.beta1,
            "beta2": optimizer.beta2,
            "eps": optimizer.eps,
            "lr": optimizer.lr,
            "t": optimizer.t,
        },
        "adam_m_sha256": digest(optimizer.m),
        "adam_v_sha256": digest(optimizer.v),
        "rng_state": rng.bit_generator.state,
    }
    writer = (
        "import os,sys\n"
        "from pathlib import Path\n"
        "from src.infrastructure.p43_checkpoint_bundle import commit_checkpoint\n"
        "commit_checkpoint(sys.argv[1], "
        "content=Path(sys.argv[2]).read_bytes(), "
        "checkpoint_id='restart-step', owner_scope='tenant:test')\n"
        "os._exit(23)\n"
    )
    lost_writer = subprocess.run(
        [sys.executable, "-c", writer, str(workspace), str(source)],
        cwd=adapter._ROOT, capture_output=True, text=True, timeout=90,
    )
    assert lost_writer.returncode == 23
    manifests = list(workspace.glob("*.json"))
    assert len(manifests) == 1
    manifest_id = manifests[0].stem
    assert len(list(workspace.glob("*.bin"))) == 3

    reader = (
        "import hashlib,json,sys\n"
        "from src.infrastructure.p43_checkpoint_bundle import load_checkpoint\n"
        "def digest(arrays):\n"
        " state=hashlib.sha256()\n"
        " for array in arrays: state.update(array.tobytes(order='C'))\n"
        " return state.hexdigest()\n"
        "loaded=load_checkpoint(sys.argv[1],sys.argv[2],owner_scope='tenant:test')\n"
        "print(json.dumps({\n"
        " 'config':loaded.model.cfg.__dict__,\n"
        " 'metadata':loaded.metadata,\n"
        " 'model_sha256':digest(p.data for p in loaded.model.parameters()),\n"
        " 'optimizer':{'beta1':loaded.optimizer.beta1,'beta2':loaded.optimizer.beta2,"
        "'eps':loaded.optimizer.eps,'lr':loaded.optimizer.lr,'t':loaded.optimizer.t},\n"
        " 'adam_m_sha256':digest(loaded.optimizer.m),\n"
        " 'adam_v_sha256':digest(loaded.optimizer.v),\n"
        " 'rng_state':loaded.rng.bit_generator.state},sort_keys=True))\n"
    )
    restored = subprocess.run(
        [sys.executable, "-c", reader, str(workspace), manifest_id],
        cwd=adapter._ROOT, capture_output=True, text=True, timeout=90,
    )
    assert restored.returncode == 0, restored.stderr
    assert json.loads(restored.stdout) == expected


def test_deterministic_split_reassembly_and_commit(content, workspace):
    shards = _split(content)
    assert shards == _split(content)
    joined = adapter.join_checkpoint(_bundle(shards))
    assert joined == adapter.join_checkpoint(_bundle(tuple(reversed(shards))))
    assert _split(joined) == shards
    first = adapter.commit_checkpoint(workspace, content=content, checkpoint_id="step-3", owner_scope="tenant:test")
    assert first == adapter.commit_checkpoint(workspace, content=content, checkpoint_id="step-3", owner_scope="tenant:test")
    assert len(list(workspace.glob("*.bin"))) == 3
    assert len(list(workspace.glob("*.json"))) == 1


@pytest.mark.parametrize("roles", [
    ("model", "optimizer"), ("model", "rng"), ("optimizer", "rng"),
    ("model", "model", "rng"), ("optimizer", "optimizer", "rng"),
    ("model", "optimizer", "optimizer"), ("model", "optimizer", "rng", "rng"),
])
def test_generic_bundle_permissiveness_does_not_weaken_adapter(content, workspace, roles):
    by_role = {shard.role: shard for shard in _split(content)}
    # Give repeats distinct names/content so the generic bundle really accepts them.
    shards = [
        bundle.CheckpointShard(f"entry-{i}", role, by_role[role].payload + b" " * i)
        for i, role in enumerate(roles)
    ]
    identity = bundle.commit_checkpoint(
        workspace, checkpoint_id="step-3", owner_scope="tenant:test", shards=shards,
    )
    with pytest.raises(ValueError, match="exactly one"):
        adapter.load_checkpoint(workspace, identity, owner_scope="tenant:test")


def test_bundle_hash_disk_tampering_and_owner_binding(content, workspace):
    identity = adapter.commit_checkpoint(
        workspace, content=content, checkpoint_id="step-3", owner_scope="tenant:test",
    )
    with pytest.raises(ValueError, match="owner_scope mismatch"):
        adapter.load_checkpoint(workspace, identity, owner_scope="other")
    checkpoint = bundle.load_checkpoint(workspace, identity, owner_scope="tenant:test")
    with pytest.raises(ValueError, match="manifest hash"):
        adapter.join_checkpoint(replace(checkpoint, manifest_id="0" * 64))
    first = checkpoint.shards[0]
    target = workspace / (hashlib.sha256(first.payload).hexdigest() + ".bin")
    target.write_bytes(first.payload[:-1] + bytes([first.payload[-1] ^ 1]))
    with pytest.raises(ValueError, match="SHA-256 mismatch"):
        adapter.load_checkpoint(workspace, identity, owner_scope="tenant:test")
    target.unlink()
    with pytest.raises(ValueError, match="missing or unsafe"):
        adapter.load_checkpoint(workspace, identity, owner_scope="tenant:test")


@pytest.mark.parametrize("role", ["model", "optimizer", "rng"])
@pytest.mark.parametrize("field,value", [
    ("schema_version", "unknown"), ("role", "other"), ("checkpoint_id", "step-4"),
    ("owner_scope", "other"), ("binding", "0" * 64), ("binding", "bad"),
    ("extra", True),
])
def test_shard_envelope_schema_and_binding_fail_closed(content, role, field, value):
    shards = _rewrite_role(_split(content), role, lambda manifest, arrays: manifest.update({field: value}))
    with pytest.raises(ValueError):
        adapter.join_checkpoint(_bundle(shards))


@pytest.mark.parametrize("role", ["model", "optimizer", "rng"])
def test_shards_from_different_real_training_steps_cannot_mix(workspace, role):
    left = workspace / "left.npz"
    right = workspace / "right.npz"
    _save(left, steps=2)
    _save(right, steps=3)
    a, b = _split(left.read_bytes()), _split(right.read_bytes())
    mixed = tuple(next(s for s in b if s.role == role) if s.role == role else s for s in a)
    with pytest.raises(ValueError, match="hash binding"):
        adapter.join_checkpoint(_bundle(mixed))


@pytest.mark.parametrize("mutation", ["weight", "moment", "adam", "rng", "metadata", "config"])
def test_rehashed_bundle_cannot_hide_cross_shard_content_changes(content, mutation):
    role = {"weight": "model", "moment": "optimizer", "adam": "optimizer",
            "rng": "rng", "metadata": "model", "config": "model"}[mutation]

    def mutate(manifest, arrays):
        state = manifest["state"]
        if mutation == "weight":
            arrays["model/token_embedding.weight"][0, 0] += 1
        elif mutation == "moment":
            arrays["adam/m/token_embedding.weight"][0, 0] += 1
        elif mutation == "adam":
            state["lr"] *= 2
        elif mutation == "rng":
            state["state"]["state"] ^= 1
        elif mutation == "metadata":
            state["metadata"]["fixture"] = "changed"
        else:
            state["config"]["seed"] += 1

    shards = _rewrite_role(_split(content), role, mutate)
    with pytest.raises(ValueError, match="hash binding"):
        adapter.join_checkpoint(_bundle(shards))


@pytest.mark.parametrize("mutation", [
    "format", "version", "bool_version", "extra", "metadata", "optimizer_none", "rng_none",
    "optimizer_extra", "adam_step", "adam_bool", "adam_beta", "adam_lr", "adam_huge",
    "rng_kind", "rng_extra", "rng_inner_extra", "rng_uint", "rng_cached", "rng_inc",
    "config_extra", "config_huge", "config_layers", "config_seed", "config_bool",
    "missing", "extra_array", "shape", "dtype", "object", "nan", "negative_v",
])
def test_unsupported_or_malformed_full_checkpoint_is_rejected(content, mutation):
    def mutate(manifest, arrays):
        if mutation == "format":
            manifest["format"] = "unknown"
        elif mutation in ("version", "bool_version"):
            manifest["schema_version"] = True if mutation == "bool_version" else 99
        elif mutation == "extra":
            manifest["unexpected"] = True
        elif mutation == "metadata":
            manifest["metadata"] = []
        elif mutation.endswith("_none"):
            manifest[mutation[:-5]] = None
        elif mutation == "optimizer_extra":
            manifest["optimizer"]["unexpected"] = 1
        elif mutation.startswith("adam_"):
            name, value = {
                "adam_step": ("t", -1), "adam_bool": ("t", True),
                "adam_beta": ("beta1", 1), "adam_lr": ("lr", 0),
                "adam_huge": ("lr", 10**1000),
            }[mutation]
            manifest["optimizer"][name] = value
        elif mutation.startswith("rng_"):
            state = manifest["rng"]
            if mutation == "rng_kind":
                state["bit_generator"] = "MT19937"
            elif mutation == "rng_extra":
                state["extra"] = 0
            elif mutation == "rng_inner_extra":
                state["state"]["extra"] = 0
            elif mutation == "rng_uint":
                state["uinteger"] = 2**32
            elif mutation == "rng_cached":
                state["has_uint32"] = True
            else:
                state["state"]["inc"] = 2
        elif mutation.startswith("config_"):
            name, value = {
                "config_extra": ("extra", 1), "config_huge": ("dim", 10**12),
                "config_layers": ("num_layers", adapter.MAX_LAYERS + 1),
                "config_seed": ("seed", 2**128), "config_bool": ("causal", 1),
            }[mutation]
            manifest["config"][name] = value
        else:
            key = "model/token_embedding.weight"
            if mutation == "missing":
                del arrays[key]
            elif mutation == "extra_array":
                arrays["model/foreign"] = np.zeros(1)
            elif mutation == "shape":
                arrays[key] = np.zeros((1, 1))
            elif mutation == "dtype":
                arrays[key] = arrays[key].astype(np.float32)
            elif mutation == "object":
                arrays[key] = np.array(["never unpickle"], dtype=object)
            elif mutation == "nan":
                arrays[key][0, 0] = np.nan
            elif mutation == "negative_v":
                arrays["adam/v/token_embedding.weight"][0, 0] = -1

    poisoned = _rewrite(content, mutate)
    with pytest.raises(ValueError):
        _split(poisoned)
    if mutation == "rng_none":
        assert adapter.load_p43_checkpoint(poisoned).rng is None
    else:
        with pytest.raises(ValueError):
            adapter.load_p43_checkpoint(poisoned)


def _zip(members, *, compression=zipfile.ZIP_DEFLATED):
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=compression) as archive:
        for name, value in members:
            archive.writestr(name, value)
    return out.getvalue()


def _npy_header(shape, descr="<f8"):
    stream = io.BytesIO()
    np.lib.format.write_array_header_1_0(
        stream, {"descr": descr, "fortran_order": False, "shape": shape},
    )
    return stream.getvalue()


@pytest.mark.parametrize("attack", [
    "huge_shape", "huge_manifest_dtype", "object", "structured", "trailing",
    "truncated", "header_version", "manifest_shape", "npy", "not_zip",
    "duplicate", "members", "expanded", "input", "compression", "json_duplicate",
    "json_nonfinite", "json_exponent", "huge_config", "header_bound", "role_array",
])
def test_bounds_and_headers_rejected_before_numpy_or_model_allocations(content, monkeypatch, attack):
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        members = {member.filename: archive.read(member) for member in archive.infolist()}
    name = "model/token_embedding.weight.npy"
    if attack == "huge_shape":
        members[name] = _npy_header((2**62, 2**62))
    elif attack == "huge_manifest_dtype":
        members["manifest.npy"] = _npy_header((), "<U1000000000")
    elif attack == "object":
        members[name] = _npy_header((1,), "|O")
    elif attack == "structured":
        members[name] = _npy_header((1,), [("x", "<f8")]) + b"\0" * 8
    elif attack == "trailing":
        members[name] += b"extra"
    elif attack == "truncated":
        members[name] = members[name][:-1]
    elif attack == "header_version":
        members[name] = b"\x93NUMPY\x03\x00" + members[name][8:]
    elif attack == "manifest_shape":
        members["manifest.npy"] = _npy_header((1,), "<U1") + b" \0\0\0"
    elif attack == "members":
        monkeypatch.setattr(adapter, "MAX_MEMBERS", len(members) - 1)
    elif attack == "expanded":
        monkeypatch.setattr(adapter, "MAX_EXPANDED_BYTES", 1)
    elif attack == "input":
        monkeypatch.setattr(adapter, "MAX_ARCHIVE_BYTES", 1)
    elif attack == "header_bound":
        monkeypatch.setattr(adapter, "MAX_HEADER_BYTES", 8)
    elif attack in ("json_duplicate", "json_nonfinite", "json_exponent"):
        text = {
            "json_duplicate": '{"duplicate":1,"duplicate":2}',
            "json_nonfinite": '{"value":NaN}',
            "json_exponent": '{"value":1e999}',
        }[attack]
        raw = io.BytesIO()
        np.save(raw, np.array(text), allow_pickle=False)
        members["manifest.npy"] = raw.getvalue()
    elif attack == "role_array":
        members["adam/m/wrong.npy"] = members.pop(name)
    elif attack == "huge_config":
        poisoned = _rewrite(content, lambda manifest, arrays: manifest["config"].update({"num_layers": 10**12}))
    if attack == "npy":
        poisoned = members[name]
    elif attack == "not_zip":
        poisoned = b"not an archive"
    elif attack == "duplicate":
        with pytest.warns(UserWarning, match="Duplicate name"):
            poisoned = _zip([*members.items(), (name, members[name])])
    elif attack == "compression":
        poisoned = _zip(members.items(), compression=zipfile.ZIP_BZIP2)
    elif attack != "huge_config":
        poisoned = _zip(members.items())

    def forbidden(*args, **kwargs):
        raise AssertionError("NumPy/model allocation before structural validation")

    monkeypatch.setattr(np, "load", forbidden)
    monkeypatch.setattr(api, "GeometricToriTransformer", forbidden)
    with pytest.raises(ValueError):
        adapter.load_p43_checkpoint(poisoned)


def test_shard_role_arrays_cannot_be_smuggled_or_dropped(content):
    shards = _split(content)
    for role, key in (("rng", "model/smuggled"), ("optimizer", "model/smuggled")):
        altered = _rewrite_role(shards, role, lambda manifest, arrays: arrays.update({key: np.zeros(1)}))
        with pytest.raises(ValueError, match="outside its named role"):
            adapter.join_checkpoint(_bundle(altered))
    altered = _rewrite_role(
        shards, "optimizer", lambda manifest, arrays: arrays.pop("adam/m/token_embedding.weight"),
    )
    with pytest.raises(ValueError, match="names/shapes"):
        adapter.join_checkpoint(_bundle(altered))


def test_invalid_input_does_not_publish_manifest_or_shards(content, workspace):
    poisoned = _rewrite(content, lambda manifest, arrays: manifest.update({"optimizer": None}))
    with pytest.raises(ValueError):
        adapter.commit_checkpoint(
            workspace, content=poisoned, checkpoint_id="step-3", owner_scope="tenant:test",
        )
    assert not list(workspace.glob("*.json"))
    assert not list(workspace.glob("*.bin"))


def test_actual_cli_receipt_is_deterministic_complete_and_nonpromoting(workspace, capsys):
    args = ["--output-dir", str(workspace), "--owner-scope", "tenant:receipt"]
    assert adapter.main(args) == 0
    result = json.loads(capsys.readouterr().out)
    receipt_path = workspace / (result["receipt_id"] + ".json")
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes)
    assert hashlib.sha256(receipt_bytes).hexdigest() == result["receipt_id"]
    assert receipt["schema_version"] == "az_p43_actual_checkpoint_resume_receipt_v1"
    assert receipt["promotion"] is False
    assert receipt["training_quality_claim"] is False
    assert receipt["execution_spine"]["promotion"]["eligible"] is False
    assert receipt["execution_spine"]["governance"]["fail_closed"] is True
    assert all(receipt["exact_resume"].values())
    assert receipt["fixture"]["identical_next_minibatches"] == 1
    assert receipt["fixture"]["optimizer_steps_before_checkpoint"] == 3
    assert receipt["source_sha256"]
    assert "src/infrastructure/p43_checkpoint_bundle.py" in receipt["source_sha256"]
    assert "9-INFRASTRUCTURE/az-ml-program/tests/test_p43_checkpoint_bundle.py" in receipt["source_sha256"]
    for path in adapter.SOURCE_FILES:
        assert receipt["source_sha256"][path] == hashlib.sha256((adapter._ROOT / path).read_bytes()).hexdigest()
    for artifact in receipt["artifacts"].values():
        content = (workspace / artifact["filename"]).read_bytes()
        assert artifact["byte_length"] == len(content)
        assert artifact["sha256"] == hashlib.sha256(content).hexdigest()
    total = sum(path.stat().st_size for path in workspace.iterdir())
    assert receipt["bytes"]["receipt"] == len(receipt_bytes)
    assert receipt["bytes"]["complete_published_bytes"] == total == result["complete_published_bytes"]
    assert receipt["bytes"]["artifacts_excluding_receipt"] + len(receipt_bytes) == total
    checkpoint = bundle.load_checkpoint(workspace, result["checkpoint_manifest_id"], owner_scope="tenant:receipt")
    manifest_size = (workspace / (checkpoint.manifest_id + ".json")).stat().st_size
    assert receipt["bytes"]["bundle_complete_bytes"] == manifest_size + sum(len(s.payload) for s in checkpoint.shards)
    assert adapter.main(args) == 0
    assert json.loads(capsys.readouterr().out) == result
    assert sum(path.stat().st_size for path in workspace.iterdir()) == total


def test_cli_fails_closed_without_a_real_output_directory(workspace, capsys):
    with pytest.raises(SystemExit) as exc:
        adapter.main(["--output-dir", str(workspace / "missing")])
    assert exc.value.code == 2
    assert "existing real directory" in capsys.readouterr().err


def test_actual_cli_keeps_commit_and_receipt_on_validated_directory_inode(workspace, capsys, monkeypatch):
    moved = workspace.parent / f"{workspace.name}-moved"
    decoy = workspace.parent / f"{workspace.name}-decoy"
    decoy.mkdir()
    original = bundle.commit_checkpoint
    swapped = False

    def replace_path_after_commit(directory, **kwargs):
        nonlocal swapped
        result = original(directory, **kwargs)
        if not swapped:
            swapped = True
            workspace.rename(moved)
            workspace.symlink_to(decoy, target_is_directory=True)
        return result

    try:
        monkeypatch.setattr(bundle, "commit_checkpoint", replace_path_after_commit)
        assert adapter.main(["--output-dir", str(workspace), "--owner-scope", "tenant:race"]) == 0
        result = json.loads(capsys.readouterr().out)
        receipt = moved / f"{result['receipt_id']}.json"
        assert receipt.is_file()
        assert (moved / f"{result['checkpoint_manifest_id']}.json").is_file()
        assert len(list(moved.glob("*.bin"))) == 3
        assert list(decoy.iterdir()) == []
    finally:
        if workspace.is_symlink():
            workspace.unlink()
        if moved.exists():
            shutil.rmtree(moved)
        if decoy.exists():
            shutil.rmtree(decoy)
        workspace.mkdir(exist_ok=True)
