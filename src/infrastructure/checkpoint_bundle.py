# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Bounded local immutable checkpoint bundles; no distributed transport implied."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from .artifact_io import publish_immutable

CHECKPOINT_SCHEMA_VERSION = "um_distributed_checkpoint_v1"
MAX_SHARDS = 64
MAX_SHARD_BYTES = 256 * 1024 * 1024
MAX_TOTAL_BYTES = 1024 * 1024 * 1024
MAX_MANIFEST_BYTES = 64 * 1024
MAX_TEXT_LENGTH = 256
_ROLES = frozenset({"model", "optimizer", "rng"})
_DIGEST = re.compile(r"^[0-9a-f]{64}$")
_MANIFEST_FIELDS = {
    "schema_version", "checkpoint_id", "owner_scope", "shards",
}
_SHARD_FIELDS = {"name", "role", "sha256", "byte_length"}


def _text(value: object, field: str) -> str:
    if (not isinstance(value, str) or not value.strip()
            or len(value) > MAX_TEXT_LENGTH
            or any(ord(char) < 32 or ord(char) == 127 for char in value)):
        raise ValueError(f"{field} must be bounded nonempty text without control characters")
    return value


def _digest(value: object) -> str:
    if not isinstance(value, str) or not _DIGEST.fullmatch(value):
        raise ValueError("Expected lowercase SHA-256")
    return value


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"Nonfinite JSON value: {value}")


@dataclass(frozen=True, slots=True)
class CheckpointShard:
    """Opaque shard bytes and their caller-assigned unique name and role."""

    name: str
    role: str
    payload: bytes

    def __post_init__(self) -> None:
        _text(self.name, "name")
        if not isinstance(self.role, str) or self.role not in _ROLES:
            raise ValueError("role must be model, optimizer, or rng")
        if not isinstance(self.payload, bytes):
            raise ValueError("payload must be immutable bytes")
        if len(self.payload) > MAX_SHARD_BYTES:
            raise ValueError("Shard exceeds MAX_SHARD_BYTES")


@dataclass(frozen=True, slots=True)
class CheckpointShardRecord:
    name: str
    role: str
    sha256: str
    byte_length: int

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name, "role": self.role,
            "sha256": self.sha256, "byte_length": self.byte_length,
        }


@dataclass(frozen=True, slots=True)
class CheckpointBundle:
    """One validated immutable manifest and the exact opaque bytes it names."""

    checkpoint_id: str
    owner_scope: str
    shards: tuple[CheckpointShard, ...]
    manifest_id: str


def _validated_shards(shards: object) -> tuple[CheckpointShard, ...]:
    if not isinstance(shards, (tuple, list)):
        raise ValueError("shards must be a tuple or list")
    if not 2 <= len(shards) <= MAX_SHARDS:
        raise ValueError("A bundle requires 2..MAX_SHARDS shards")
    if any(not isinstance(shard, CheckpointShard) for shard in shards):
        raise ValueError("Expected CheckpointShard entries")
    ordered = tuple(sorted(shards, key=lambda shard: (shard.name, shard.role)))
    if len({shard.name for shard in ordered}) != len(ordered):
        raise ValueError("Duplicate shard name")
    digests = [hashlib.sha256(shard.payload).hexdigest() for shard in ordered]
    if len(set(digests)) != len(digests):
        raise ValueError("Duplicate shard content")
    if sum(map(len, (shard.payload for shard in ordered))) > MAX_TOTAL_BYTES:
        raise ValueError("Bundle exceeds MAX_TOTAL_BYTES")
    return ordered


def _manifest(checkpoint_id: str, owner_scope: str,
              shards: tuple[CheckpointShard, ...]) -> tuple[dict[str, object], tuple[CheckpointShardRecord, ...]]:
    records = tuple(
        CheckpointShardRecord(
            shard.name, shard.role, hashlib.sha256(shard.payload).hexdigest(),
            len(shard.payload),
        )
        for shard in shards
    )
    data: dict[str, object] = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "checkpoint_id": checkpoint_id,
        "owner_scope": owner_scope,
        "shards": [record.to_dict() for record in records],
    }
    return data, records


def _encoded_manifest(checkpoint_id: str, owner_scope: str,
                      shards: object) -> tuple[bytes, tuple[CheckpointShard, ...]]:
    checkpoint_id = _text(checkpoint_id, "checkpoint_id")
    owner_scope = _text(owner_scope, "owner_scope")
    ordered = _validated_shards(shards)
    payload = _canonical(_manifest(checkpoint_id, owner_scope, ordered)[0])
    if len(payload) > MAX_MANIFEST_BYTES:
        raise ValueError("Manifest exceeds MAX_MANIFEST_BYTES")
    return payload, ordered


def checkpoint_manifest_id(
    *,
    checkpoint_id: str,
    owner_scope: str,
    shards: tuple[CheckpointShard, ...] | list[CheckpointShard],
) -> str:
    """Return the deterministic manifest identity without writing anything."""
    return hashlib.sha256(_encoded_manifest(checkpoint_id, owner_scope, shards)[0]).hexdigest()


def _stage_at(root_fd: int, directory: Path, shard: CheckpointShard) -> CheckpointShardRecord:
    digest = hashlib.sha256(shard.payload).hexdigest()
    publish_immutable(directory, digest, shard.payload, suffix=".bin", directory_fd=root_fd)
    return CheckpointShardRecord(shard.name, shard.role, digest, len(shard.payload))


def stage_shard(directory: str | Path, shard: CheckpointShard) -> CheckpointShardRecord:
    """Publish one worker's opaque shard immutably; this alone commits nothing.

    One validated directory descriptor anchors the whole publication.
    """
    if not isinstance(shard, CheckpointShard):
        raise ValueError("Expected CheckpointShard")
    root_fd = _open_root(directory)
    try:
        return _stage_at(root_fd, Path(directory), shard)
    finally:
        os.close(root_fd)


def commit_checkpoint(
    directory: str | Path,
    *,
    checkpoint_id: str,
    owner_scope: str,
    shards: tuple[CheckpointShard, ...] | list[CheckpointShard],
) -> str:
    """Publish shard bytes first and the content-addressed manifest last.

    The manifest publication is the sole commit point. If publication stops
    before then, already-published shards are uncommitted immutable objects;
    retrying the same inputs safely reuses them. No mutable ledger is written.
    """
    payload, ordered = _encoded_manifest(checkpoint_id, owner_scope, shards)
    manifest_id = hashlib.sha256(payload).hexdigest()
    directory = Path(directory)
    # Every shard and the manifest are published relative to this one descriptor,
    # so a concurrent rename or symlink swap of the pathname cannot split them.
    root_fd = _open_root(directory)
    try:
        for shard in ordered:
            _stage_at(root_fd, directory, shard)
        publish_immutable(directory, manifest_id, payload, suffix=".json",
                          directory_fd=root_fd)
    finally:
        os.close(root_fd)
    return manifest_id


def _open_root(directory: str | Path) -> int:
    try:
        return os.open(Path(directory), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise ValueError("Checkpoint directory must be an existing real directory") from exc


def _read_regular(root_fd: int, filename: str, limit: int) -> bytes:
    fd = -1
    try:
        fd = os.open(filename, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=root_fd)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("Checkpoint artifacts must be regular files")
        if info.st_size > limit:
            raise ValueError("Checkpoint artifact exceeds supported size bound")
        with os.fdopen(fd, "rb") as stream:
            fd = -1
            payload = stream.read(limit + 1)
        if len(payload) > limit:
            raise ValueError("Checkpoint artifact exceeds supported size bound")
        return payload
    except OSError as exc:
        raise ValueError("Checkpoint artifact is missing or unsafe") from exc
    finally:
        if fd >= 0:
            os.close(fd)


def load_checkpoint(
    directory: str | Path,
    manifest_id: str,
    *,
    owner_scope: str,
) -> CheckpointBundle:
    """Read only a committed manifest and verify scope, schema, and every shard."""
    manifest_id = _digest(manifest_id)
    owner_scope = _text(owner_scope, "owner_scope")
    root_fd = _open_root(directory)
    try:
        raw = _read_regular(root_fd, manifest_id + ".json", MAX_MANIFEST_BYTES)
        try:
            data = json.loads(raw, object_pairs_hook=_unique_pairs,
                              parse_constant=_reject_constant)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid checkpoint manifest JSON") from exc
        if not isinstance(data, dict) or set(data) != _MANIFEST_FIELDS:
            raise ValueError("Missing or unknown manifest fields")
        if data["schema_version"] != CHECKPOINT_SCHEMA_VERSION:
            raise ValueError("Unsupported checkpoint schema")
        checkpoint_id = _text(data["checkpoint_id"], "checkpoint_id")
        manifest_scope = _text(data["owner_scope"], "owner_scope")
        if manifest_scope != owner_scope:
            raise ValueError("Checkpoint owner_scope mismatch")
        if not isinstance(data["shards"], list) or not 2 <= len(data["shards"]) <= MAX_SHARDS:
            raise ValueError("A bundle requires 2..MAX_SHARDS shards")
        if _canonical(data) != raw or hashlib.sha256(raw).hexdigest() != manifest_id:
            raise ValueError("Manifest canonical encoding or identity mismatch")

        records: list[CheckpointShardRecord] = []
        names: set[str] = set()
        digests: set[str] = set()
        total = 0
        for entry in data["shards"]:
            if not isinstance(entry, dict) or set(entry) != _SHARD_FIELDS:
                raise ValueError("Missing or unknown shard fields")
            name = _text(entry["name"], "name")
            role = entry["role"]
            if not isinstance(role, str) or role not in _ROLES:
                raise ValueError("Unsupported shard role")
            digest = _digest(entry["sha256"])
            length = entry["byte_length"]
            if isinstance(length, bool) or not isinstance(length, int) or not 0 <= length <= MAX_SHARD_BYTES:
                raise ValueError("Invalid shard byte_length")
            if name in names or digest in digests:
                raise ValueError("Duplicate shard name or content")
            names.add(name)
            digests.add(digest)
            total += length
            if total > MAX_TOTAL_BYTES:
                raise ValueError("Bundle exceeds MAX_TOTAL_BYTES")
            records.append(CheckpointShardRecord(name, role, digest, length))
        if records != sorted(records, key=lambda item: (item.name, item.role)):
            raise ValueError("Shard records are not in canonical order")

        loaded: list[CheckpointShard] = []
        for record in records:
            try:
                payload = _read_regular(root_fd, record.sha256 + ".bin", record.byte_length)
            except ValueError as exc:
                if "size bound" in str(exc):
                    raise ValueError("Shard byte_length mismatch") from exc
                raise
            if len(payload) != record.byte_length:
                raise ValueError("Shard byte_length mismatch")
            if hashlib.sha256(payload).hexdigest() != record.sha256:
                raise ValueError("Shard SHA-256 mismatch")
            loaded.append(CheckpointShard(record.name, record.role, payload))
        return CheckpointBundle(
            checkpoint_id, manifest_scope, tuple(loaded), manifest_id,
        )
    finally:
        os.close(root_fd)


EVIDENCE_SCHEMA_VERSION = "um_checkpoint_recovery_evidence_v1"
FIXTURE_CHECKPOINT_ID = "fixture-step-3"
FIXTURE_OWNER_SCOPE = "tenant:checkpoint-fixture"
WORKER_LOSS_EXIT_CODE = 75
_FIXTURE_NOTE = ("Deliberately constructed small opaque fixture bytes; not tensor, "
                 "optimizer, or RNG state from a training run.")
_WORKER = (
    "import os, sys\n"
    "from src.infrastructure.checkpoint_bundle import fixture_shards, stage_shard\n"
    "stage_shard(sys.argv[1], fixture_shards()[0])\n"
    "os._exit(int(sys.argv[2]))\n"
)


def fixture_shards() -> tuple[CheckpointShard, ...]:
    """Return the deterministic three-role recovery fixture (model first)."""
    return (
        CheckpointShard("worker-0/model", "model", b"AZCKPT\x00model\x00" + bytes(range(32))),
        CheckpointShard("worker-1/optimizer", "optimizer",
                        b"AZCKPT\x00optimizer\x00" + bytes(range(31, -1, -1))),
        CheckpointShard("worker-2/rng", "rng", b"AZCKPT\x00rng\x00" + b"\x5a" * 16),
    )


def _expected_rejection(action) -> dict[str, object]:
    try:
        action()
    except ValueError as exc:
        return {"rejected": True, "error_type": "ValueError", "message": str(exc)}
    return {"rejected": False, "error_type": None, "message": None}


def _store_listing(store: Path) -> list[str]:
    return sorted(path.name for path in store.iterdir())


def run_recovery_evidence(output_dir: str | Path) -> tuple[Path, dict[str, object]]:
    """Run local process-loss recovery checks and publish an immutable receipt.

    One real subprocess stages exactly one shard and exits nonzero before any
    manifest exists. This is local filesystem evidence, not distributed I/O.
    """
    import subprocess
    import sys
    import tempfile

    from .execution_spine import (
        ExecutionSpineHealthCheck, ExecutionSpineRecord, build_fail_closed_governance,
        repo_rel,
    )

    output_dir = Path(output_dir)
    os.close(_open_root(output_dir))
    repo_root = Path(__file__).resolve().parents[2]
    shards = fixture_shards()
    by_role = {shard.role: shard.payload for shard in shards}
    expected_id = checkpoint_manifest_id(
        checkpoint_id=FIXTURE_CHECKPOINT_ID, owner_scope=FIXTURE_OWNER_SCOPE, shards=shards,
    )
    # Fixture stores are transient; only the hashed receipt is retained.
    with tempfile.TemporaryDirectory(prefix=".checkpoint-fixture-", dir=output_dir) as scratch:
        store = Path(scratch) / "recovery-store"
        store.mkdir()
        corrupt_store = Path(scratch) / "corruption-store"
        corrupt_store.mkdir()

        worker = subprocess.run(
            [sys.executable, "-c", _WORKER, str(store), str(WORKER_LOSS_EXIT_CODE)],
            cwd=repo_root, capture_output=True, timeout=60, check=False,
        )
        after_loss = _store_listing(store)
        staged_model = store / f"{hashlib.sha256(by_role['model']).hexdigest()}.bin"
        staged_bytes_exact = (
            staged_model.is_file() and staged_model.read_bytes() == by_role["model"]
        )
        partial_load = _expected_rejection(lambda: load_checkpoint(
            store, expected_id, owner_scope=FIXTURE_OWNER_SCOPE))

        recovered_id = commit_checkpoint(store, checkpoint_id=FIXTURE_CHECKPOINT_ID,
                                         owner_scope=FIXTURE_OWNER_SCOPE, shards=shards)
        loaded = load_checkpoint(store, recovered_id, owner_scope=FIXTURE_OWNER_SCOPE)
        loaded_roles = {shard.role: shard.payload for shard in loaded.shards}
        after_recovery = _store_listing(store)
        repeated_id = commit_checkpoint(store, checkpoint_id=FIXTURE_CHECKPOINT_ID,
                                        owner_scope=FIXTURE_OWNER_SCOPE, shards=shards)
        after_repeat = _store_listing(store)
        wrong_scope = _expected_rejection(lambda: load_checkpoint(
            store, recovered_id, owner_scope="tenant:other"))

        corrupt_id = commit_checkpoint(corrupt_store, checkpoint_id=FIXTURE_CHECKPOINT_ID,
                                       owner_scope=FIXTURE_OWNER_SCOPE, shards=shards)
        target = corrupt_store / f"{hashlib.sha256(by_role['optimizer']).hexdigest()}.bin"
        damaged = bytearray(target.read_bytes())
        damaged[-1] ^= 0x01
        target.write_bytes(bytes(damaged))
        checksum = _expected_rejection(lambda: load_checkpoint(
            corrupt_store, corrupt_id, owner_scope=FIXTURE_OWNER_SCOPE))

        manifest_bytes = (store / f"{recovered_id}.json").read_bytes()
    checks = {
        "worker_loss_exit_observed": worker.returncode == WORKER_LOSS_EXIT_CODE,
        "partial_stage_has_exactly_one_shard_and_no_manifest": (
            after_loss == [staged_model.name]
        ),
        "partial_staged_bytes_exact": staged_bytes_exact,
        "absent_commit_rejected": bool(partial_load["rejected"]),
        "recovered_manifest_matches_precomputed_identity": recovered_id == expected_id,
        "recovered_role_bytes_exact": loaded_roles == by_role,
        "recovered_store_has_three_shards_one_manifest": (
            sum(name.endswith(".bin") for name in after_recovery) == 3
            and after_recovery.count(f"{recovered_id}.json") == 1
            and len(after_recovery) == 4
        ),
        "repeat_commit_same_manifest_no_new_files": (
            repeated_id == recovered_id and after_repeat == after_recovery
        ),
        "corrupt_checksum_rejected": (
            bool(checksum["rejected"]) and "SHA-256 mismatch" in str(checksum["message"])
        ),
        "wrong_scope_rejected": (
            bool(wrong_scope["rejected"]) and "owner_scope mismatch" in str(wrong_scope["message"])
        ),
    }
    passed = all(checks.values())
    source = Path(__file__).resolve()
    test_source = repo_root / "9-INFRASTRUCTURE/az-ml-program/tests/test_checkpoint_bundle.py"
    source_hashes = {
        repo_rel(source, repo_root): hashlib.sha256(source.read_bytes()).hexdigest(),
        repo_rel(source.parent / "artifact_io.py", repo_root):
            hashlib.sha256((source.parent / "artifact_io.py").read_bytes()).hexdigest(),
    }
    if test_source.is_file():
        source_hashes[repo_rel(test_source, repo_root)] = hashlib.sha256(
            test_source.read_bytes()).hexdigest()
    spine = ExecutionSpineRecord(
        surface_id="checkpoint_bundle_local_recovery",
        surface_kind="local_failure_injection_evidence",
        lane="az-ml-program/checkpoint-bundle",
        status="passed" if passed else "failed",
        summary=("Local subprocess staged one of three opaque fixture shards and exited "
                 "nonzero; manifest publication remained the sole commit point."),
        generated_at_utc=None,
        canonical_paths=sorted(source_hashes),
        sources=sorted(source_hashes),
        governance=build_fail_closed_governance(
            epistemic_label="local_infrastructure_fixture",
            promotion_rule="manual review only; local fixture evidence is not promotion",
            residual_blockers=[
                "no networked or multi-host distributed storage exercised",
                "fixture bytes are not real tensor, optimizer, or RNG training state",
                "single local POSIX filesystem; no crash-consistency hardware test",
            ],
        ),
        health_checks=[
            ExecutionSpineHealthCheck(name, value, "passed" if value else "failed", name)
            for name, value in checks.items()
        ],
        promotion={"eligible": False, "automatic_promotion": False,
                   "training_state_qualification": False, "distributed_claim": False},
    )
    payload = {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "passed": passed,
        "fixture": {
            "note": _FIXTURE_NOTE,
            "checkpoint_id": FIXTURE_CHECKPOINT_ID,
            "owner_scope": FIXTURE_OWNER_SCOPE,
            "shards": [{"name": shard.name, "role": shard.role,
                        "sha256": hashlib.sha256(shard.payload).hexdigest(),
                        "byte_length": len(shard.payload)} for shard in shards],
        },
        "worker_loss": {
            "mechanism": "real local subprocess: stage_shard(model) then os._exit",
            "expected_exit_code": WORKER_LOSS_EXIT_CODE,
            "observed_exit_code": worker.returncode,
            "store_after_loss": after_loss,
            "load_before_commit": partial_load,
        },
        "recovery": {
            "precomputed_manifest_id": expected_id,
            "recovered_manifest_id": recovered_id,
            "repeated_manifest_id": repeated_id,
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "manifest_byte_length": len(manifest_bytes),
            "store_after_recovery": after_recovery,
            "store_after_repeat": after_repeat,
            "fixture_stores": "temporary under output_dir; removed after measurement",
        },
        "expected_rejections": {"corrupt_optimizer_checksum": checksum,
                                "wrong_owner_scope": wrong_scope},
        "checks": checks,
        "source_sha256": source_hashes,
        "bounds": {"min_shards": 2, "max_shards": MAX_SHARDS,
                   "max_shard_bytes": MAX_SHARD_BYTES, "max_total_bytes": MAX_TOTAL_BYTES,
                   "max_manifest_bytes": MAX_MANIFEST_BYTES, "roles": sorted(_ROLES)},
        "execution_spine": spine.to_dict(),
    }
    encoded = _canonical(payload)
    evidence_id = hashlib.sha256(encoded).hexdigest()
    root_fd = _open_root(output_dir)
    try:
        path = publish_immutable(output_dir, evidence_id, encoded, ".json", directory_fd=root_fd)
    finally:
        os.close(root_fd)
    return path, payload


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Run local checkpoint worker-loss recovery evidence.")
    parser.add_argument("--output-dir", required=True,
                        help="existing directory; fresh fixture stores are created inside")
    args = parser.parse_args(argv)
    path, payload = run_recovery_evidence(args.output_dir)
    print(json.dumps({"evidence": str(path), "passed": payload["passed"],
                      "checks": payload["checks"]}, sort_keys=True))
    return 0 if payload["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
