# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded immutable checkpoint bundle, integrity, and retry contracts."""

import hashlib
import json
from pathlib import Path
import select
import subprocess
import sys

import pytest

from src.infrastructure import checkpoint_bundle as bundle
from src.infrastructure.checkpoint_bundle import (
    MAX_SHARDS,
    CheckpointShard,
    commit_checkpoint,
    load_checkpoint,
)


def shards():
    return (
        CheckpointShard("model-0", "model", b"opaque model bytes"),
        CheckpointShard("optimizer-0", "optimizer", b"opaque optimizer bytes"),
        CheckpointShard("rng-0", "rng", b"opaque rng bytes"),
    )


def commit(path):
    return commit_checkpoint(
        path, checkpoint_id="step-17", owner_scope="tenant:research",
        shards=shards(),
    )


def test_opaque_role_shards_round_trip_and_manifest_are_deterministic(tmp_path):
    manifest_id = commit(tmp_path)
    loaded = load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")

    assert loaded.checkpoint_id == "step-17"
    assert loaded.manifest_id == manifest_id
    assert [(item.name, item.role, item.payload) for item in loaded.shards] == [
        ("model-0", "model", b"opaque model bytes"),
        ("optimizer-0", "optimizer", b"opaque optimizer bytes"),
        ("rng-0", "rng", b"opaque rng bytes"),
    ]
    assert commit(tmp_path) == manifest_id
    assert len(list(tmp_path.glob("*.bin"))) == 3
    assert len(list(tmp_path.glob("*.json"))) == 1
    manifest = json.loads((tmp_path / f"{manifest_id}.json").read_bytes())
    assert set(manifest) == {"schema_version", "checkpoint_id", "owner_scope", "shards"}
    assert all(set(shard) == {"name", "role", "sha256", "byte_length"}
               for shard in manifest["shards"])


def test_concurrent_local_processes_publish_identical_and_distinct_bundles(tmp_path):
    """Qualify one local POSIX store, not network or multi-host durability."""
    worker = """
import json
import sys
from src.infrastructure.checkpoint_bundle import (
    CheckpointShard, commit_checkpoint, load_checkpoint,
)

mode, directory, encoded = sys.argv[1:]
if mode == "write":
    shards = tuple(CheckpointShard(name, role, bytes.fromhex(payload))
                   for name, role, payload in json.loads(encoded))
    print("ready", flush=True)
    if sys.stdin.readline() != "publish\\n":
        raise RuntimeError("publication barrier was not released")
    manifest_id = commit_checkpoint(directory, checkpoint_id="step-17",
                                    owner_scope="tenant:research", shards=shards)
    repeated_id = commit_checkpoint(directory, checkpoint_id="step-17",
                                    owner_scope="tenant:research", shards=shards)
    print(json.dumps([manifest_id, repeated_id]), flush=True)
else:
    result = {}
    for manifest_id in json.loads(encoded):
        loaded = load_checkpoint(directory, manifest_id, owner_scope="tenant:research")
        assert loaded.manifest_id == manifest_id
        assert loaded.checkpoint_id == "step-17"
        assert loaded.owner_scope == "tenant:research"
        result[manifest_id] = [[s.name, s.role, s.payload.hex()] for s in loaded.shards]
    print(json.dumps(result), flush=True)
"""
    variants = [shards()] + [
        tuple(CheckpointShard(s.name, s.role, s.payload + bytes([index]))
              for s in shards())
        for index in (1, 2)
    ]
    manifest_ids = [
        bundle.checkpoint_manifest_id(
            checkpoint_id="step-17", owner_scope="tenant:research", shards=items)
        for items in variants
    ]
    assert len(set(manifest_ids)) == 3
    encoded_shards = [
        [[s.name, s.role, s.payload.hex()] for s in items] for items in variants
    ]
    repo_root = Path(bundle.__file__).resolve().parents[2]

    def snapshot():
        return {
            path.name: (path.read_bytes(), path.stat().st_ino, path.stat().st_mtime_ns)
            for path in tmp_path.iterdir()
        }

    def publish_together(indices):
        before = snapshot()
        processes = []
        try:
            for index in indices:
                processes.append(subprocess.Popen(
                    [sys.executable, "-c", worker, "write", str(tmp_path),
                     json.dumps(encoded_shards[index])],
                    cwd=repo_root, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, text=True,
                ))
            assert len({process.pid for process in processes}) == len(indices)
            for process in processes:
                ready, _, _ = select.select([process.stdout], [], [], 30)
                assert ready, f"writer {process.pid} did not reach publication barrier"
                assert process.stdout.readline() == "ready\n"
                assert process.poll() is None
            # Every independent interpreter is waiting before any is allowed to write.
            assert snapshot() == before
            for process in processes:
                process.stdin.write("publish\n")
                process.stdin.flush()
            for index, process in zip(indices, processes):
                stdout, stderr = process.communicate(timeout=30)
                assert process.returncode == 0, (stdout, stderr)
                assert json.loads(stdout) == [manifest_ids[index]] * 2
        finally:
            for process in processes:
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=10)

    def validate_with_fresh_reader(indices):
        expected = {manifest_ids[index]: encoded_shards[index] for index in indices}
        reader = subprocess.run(
            [sys.executable, "-c", worker, "read", str(tmp_path), json.dumps(list(expected))],
            cwd=repo_root, capture_output=True, text=True, timeout=30,
        )
        assert reader.returncode == 0, (reader.stdout, reader.stderr)
        assert json.loads(reader.stdout) == expected
        expected_names = {
            f"{hashlib.sha256(s.payload).hexdigest()}.bin"
            for index in indices for s in variants[index]
        } | {f"{manifest_id}.json" for manifest_id in expected}
        assert {path.name for path in tmp_path.iterdir()} == expected_names
        for path in tmp_path.iterdir():
            assert hashlib.sha256(path.read_bytes()).hexdigest() == path.stem

    publish_together([0, 0, 0])
    validate_with_fresh_reader([0])
    identical = snapshot()
    publish_together([0, 1, 2])
    validate_with_fresh_reader([0, 1, 2])
    distinct = snapshot()
    assert {name: distinct[name] for name in identical} == identical
    publish_together([0, 1, 2])
    validate_with_fresh_reader([0, 1, 2])
    assert snapshot() == distinct


def test_partial_worker_failure_is_retryable_and_manifest_is_commit_point(tmp_path, monkeypatch):
    original = bundle.publish_immutable
    published_shards = 0

    def fail_after_one_shard(directory, artifact_id, content, suffix=".json", **kwargs):
        nonlocal published_shards
        if suffix == ".bin":
            published_shards += 1
            if published_shards == 2:
                raise OSError("simulated worker failure")
        return original(directory, artifact_id, content, suffix, **kwargs)

    monkeypatch.setattr(bundle, "publish_immutable", fail_after_one_shard)
    with pytest.raises(OSError, match="simulated worker failure"):
        commit(tmp_path)
    assert len(list(tmp_path.glob("*.bin"))) == 1
    assert list(tmp_path.glob("*.json")) == []

    monkeypatch.setattr(bundle, "publish_immutable", original)
    manifest_id = commit(tmp_path)
    loaded = load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")
    assert len(loaded.shards) == 3
    assert len(list(tmp_path.glob("*.bin"))) == 3
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_owner_scope_and_unsafe_manifest_ids_are_rejected(tmp_path):
    manifest_id = commit(tmp_path)
    with pytest.raises(ValueError, match="owner_scope mismatch"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:other")
    with pytest.raises(ValueError, match="SHA-256"):
        load_checkpoint(tmp_path, "../outside", owner_scope="tenant:research")


def test_missing_or_corrupt_shard_is_rejected(tmp_path):
    manifest_id = commit(tmp_path)
    manifest = json.loads((tmp_path / f"{manifest_id}.json").read_bytes())
    shard_path = tmp_path / f"{manifest['shards'][0]['sha256']}.bin"
    shard_path.unlink()
    with pytest.raises(ValueError, match="missing or unsafe"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")

    commit(tmp_path)
    manifest_id = commit(tmp_path)
    manifest = json.loads((tmp_path / f"{manifest_id}.json").read_bytes())
    shard_path = tmp_path / f"{manifest['shards'][0]['sha256']}.bin"
    shard_path.write_bytes(b"corrupted")
    with pytest.raises(ValueError, match="byte_length mismatch|SHA-256 mismatch"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")


def test_symlink_shard_is_rejected_without_following_it(tmp_path):
    manifest_id = commit(tmp_path)
    manifest = json.loads((tmp_path / f"{manifest_id}.json").read_bytes())
    shard_path = tmp_path / f"{manifest['shards'][0]['sha256']}.bin"
    outside = tmp_path.parent / f"{tmp_path.name}-outside"
    outside.write_bytes(b"outside")
    shard_path.unlink()
    shard_path.symlink_to(outside)
    with pytest.raises(ValueError, match="missing or unsafe"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")
    assert outside.read_bytes() == b"outside"


def test_symlink_manifest_is_rejected_without_following_it(tmp_path):
    manifest_id = commit(tmp_path)
    manifest_path = tmp_path / f"{manifest_id}.json"
    outside = tmp_path.parent / f"{tmp_path.name}-manifest-outside"
    outside.write_bytes(manifest_path.read_bytes())
    manifest_path.unlink()
    manifest_path.symlink_to(outside)
    with pytest.raises(ValueError, match="missing or unsafe"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")
    assert outside.read_bytes()


def test_conflicting_existing_content_address_is_never_overwritten(tmp_path):
    shard = shards()[0]
    digest = hashlib.sha256(shard.payload).hexdigest()
    target = tmp_path / f"{digest}.bin"
    target.write_bytes(b"different bytes")
    with pytest.raises(ValueError, match="does not match its identity"):
        commit(tmp_path)
    assert target.read_bytes() == b"different bytes"
    assert list(tmp_path.glob("*.json")) == []


def test_manifest_with_unknown_fields_or_noncanonical_identity_is_rejected(tmp_path):
    value = {
        "schema_version": bundle.CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_id": "step-1",
        "owner_scope": "tenant:research",
        "shards": [],
        "unexpected": True,
    }
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    manifest_id = hashlib.sha256(payload).hexdigest()
    (tmp_path / f"{manifest_id}.json").write_bytes(payload)
    with pytest.raises(ValueError, match="unknown manifest fields"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")


@pytest.mark.parametrize(
    "items, message",
    [
        ((CheckpointShard("one", "model", b"a"),), "2..MAX_SHARDS"),
        ((CheckpointShard("same", "model", b"a"),
          CheckpointShard("same", "rng", b"b")), "Duplicate shard name"),
        ((CheckpointShard("one", "model", b"a"),
          CheckpointShard("two", "rng", b"a")), "Duplicate shard content"),
    ],
)
def test_invalid_shard_sets_are_rejected_before_publication(tmp_path, items, message):
    with pytest.raises(ValueError, match=message):
        commit_checkpoint(
            tmp_path, checkpoint_id="step-1", owner_scope="tenant",
            shards=items,
        )
    assert list(tmp_path.iterdir()) == []


def test_unknown_shard_role_is_rejected():
    with pytest.raises(ValueError, match="role must be"):
        CheckpointShard("one", "unknown", b"a")


def test_bundle_shard_count_has_an_explicit_upper_bound(tmp_path):
    items = tuple(
        CheckpointShard(f"shard-{index}", "model", f"bytes-{index}".encode())
        for index in range(MAX_SHARDS + 1)
    )
    with pytest.raises(ValueError, match="2..MAX_SHARDS"):
        commit_checkpoint(
            tmp_path, checkpoint_id="step-1", owner_scope="tenant",
            shards=items,
        )


def test_stage_shard_alone_never_commits(tmp_path):
    items = shards()
    expected = bundle.checkpoint_manifest_id(
        checkpoint_id="step-17", owner_scope="tenant:research", shards=items)
    record = bundle.stage_shard(tmp_path, items[0])
    assert record.sha256 == hashlib.sha256(items[0].payload).hexdigest()
    assert [path.name for path in tmp_path.iterdir()] == [f"{record.sha256}.bin"]
    with pytest.raises(ValueError, match="missing or unsafe"):
        load_checkpoint(tmp_path, expected, owner_scope="tenant:research")
    assert commit(tmp_path) == expected


def test_recovery_cli_observes_real_worker_loss_and_publishes_receipt(tmp_path, capsys):
    assert bundle.main(["--output-dir", str(tmp_path)]) == 0
    summary = json.loads(capsys.readouterr().out)
    evidence = tmp_path / summary["evidence"].rsplit("/", 1)[-1]
    raw = evidence.read_bytes()
    assert evidence.name == f"{hashlib.sha256(raw).hexdigest()}.json"
    payload = json.loads(raw)

    assert payload["passed"] is True and all(payload["checks"].values())
    fixture = bundle.fixture_shards()
    worker = payload["worker_loss"]
    assert worker["observed_exit_code"] == bundle.WORKER_LOSS_EXIT_CODE
    assert worker["store_after_loss"] == [
        f"{hashlib.sha256(fixture[0].payload).hexdigest()}.bin"]
    assert worker["load_before_commit"]["rejected"] is True
    recovery = payload["recovery"]
    assert (recovery["precomputed_manifest_id"] == recovery["recovered_manifest_id"]
            == recovery["repeated_manifest_id"])
    assert recovery["store_after_repeat"] == recovery["store_after_recovery"]
    rejections = payload["expected_rejections"]
    assert "SHA-256 mismatch" in rejections["corrupt_optimizer_checksum"]["message"]
    assert "owner_scope mismatch" in rejections["wrong_owner_scope"]["message"]
    assert all(len(value) == 64 for value in payload["source_sha256"].values())
    assert "src/infrastructure/checkpoint_bundle.py" in payload["source_sha256"]
    spine = payload["execution_spine"]
    assert spine["promotion"]["eligible"] is False
    assert spine["promotion"]["training_state_qualification"] is False
    assert spine["promotion"]["distributed_claim"] is False
    assert all(check["passed"] for check in spine["health_checks"])

    assert payload["checks"]["recovered_role_bytes_exact"] is True
    assert list(tmp_path.iterdir()) == [evidence]

    assert bundle.main(["--output-dir", str(tmp_path)]) == 0
    repeated = json.loads(capsys.readouterr().out)
    assert repeated["evidence"] == summary["evidence"]
    assert evidence.read_bytes() == raw
    assert list(tmp_path.iterdir()) == [evidence]


def test_recovery_cli_reports_failure_when_worker_does_not_die(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(bundle, "_WORKER", "raise SystemExit(0)\n")
    assert bundle.main(["--output-dir", str(tmp_path)]) == 1
    summary = json.loads(capsys.readouterr().out)
    assert summary["passed"] is False
    assert summary["checks"]["worker_loss_exit_observed"] is False
    assert summary["checks"]["partial_stage_has_exactly_one_shard_and_no_manifest"] is False


def test_recovery_cli_requires_existing_real_output_directory(tmp_path):
    with pytest.raises(ValueError, match="existing real directory"):
        bundle.main(["--output-dir", str(tmp_path / "missing")])


def _swap_directory_after_first_publish(tmp_path, monkeypatch, replacement):
    """Rename the store after its first publication and put ``replacement`` at its path."""
    store = tmp_path / "store"
    store.mkdir()
    moved = tmp_path / "moved-store"
    decoy = tmp_path / "decoy"
    decoy.mkdir()
    original = bundle.publish_immutable
    calls = []

    def swap_after_first(directory, artifact_id, content, suffix=".json", **kwargs):
        assert isinstance(kwargs.get("directory_fd"), int)
        calls.append((artifact_id, suffix))
        result = original(directory, artifact_id, content, suffix, **kwargs)
        if len(calls) == 1:
            store.rename(moved)
            if replacement == "symlink":
                store.symlink_to(decoy, target_is_directory=True)
            else:
                store.mkdir()
        return result

    monkeypatch.setattr(bundle, "publish_immutable", swap_after_first)
    manifest_id = commit(store)
    monkeypatch.setattr(bundle, "publish_immutable", original)
    return store, moved, decoy, manifest_id, calls


@pytest.mark.parametrize("replacement", ["symlink", "directory"])
def test_mid_commit_rename_or_symlink_swap_cannot_split_the_bundle(
        tmp_path, monkeypatch, replacement):
    store, moved, decoy, manifest_id, calls = _swap_directory_after_first_publish(
        tmp_path, monkeypatch, replacement)
    assert [suffix for _, suffix in calls] == [".bin", ".bin", ".bin", ".json"]
    assert list(decoy.iterdir()) == []
    if replacement == "directory":
        assert list(store.iterdir()) == []
    assert sorted(path.name for path in moved.iterdir()) == sorted(
        [f"{hashlib.sha256(s.payload).hexdigest()}.bin" for s in shards()]
        + [f"{manifest_id}.json"])
    loaded = load_checkpoint(moved, manifest_id, owner_scope="tenant:research")
    assert {s.role: s.payload for s in loaded.shards} == {s.role: s.payload for s in shards()}
    with pytest.raises(ValueError):
        load_checkpoint(store, manifest_id, owner_scope="tenant:research")


def test_commit_into_symlinked_directory_is_rejected(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real, target_is_directory=True)
    with pytest.raises(ValueError, match="existing real directory"):
        commit(link)
    with pytest.raises(ValueError, match="existing real directory"):
        bundle.stage_shard(link, shards()[0])
    assert list(real.iterdir()) == []


def _sparse(path, size):
    with open(path, "wb") as stream:
        stream.truncate(size)


@pytest.mark.parametrize("stage", ["shard", "manifest"])
def test_oversized_existing_conflict_is_rejected_without_commit(tmp_path, stage):
    items = shards()
    manifest_id = bundle.checkpoint_manifest_id(
        checkpoint_id="step-17", owner_scope="tenant:research", shards=items)
    name = (f"{hashlib.sha256(items[1].payload).hexdigest()}.bin" if stage == "shard"
            else f"{manifest_id}.json")
    target = tmp_path / name
    _sparse(target, 1 << 30)
    with pytest.raises(ValueError, match="does not match"):
        commit(tmp_path)
    assert target.stat().st_size == 1 << 30
    if stage == "shard":
        assert list(tmp_path.glob("*.json")) == []
    with pytest.raises(ValueError):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")


def test_oversized_committed_shard_is_rejected_by_size_before_read(tmp_path):
    manifest_id = commit(tmp_path)
    target = tmp_path / f"{hashlib.sha256(shards()[0].payload).hexdigest()}.bin"
    target.unlink()
    _sparse(target, 1 << 30)
    with pytest.raises(ValueError, match="byte_length mismatch"):
        load_checkpoint(tmp_path, manifest_id, owner_scope="tenant:research")
