# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Publication integrity and concurrent-reader contract tests."""

from concurrent.futures import ThreadPoolExecutor
import hashlib
import os
import stat

import pytest

from src.infrastructure.artifact_io import publish_immutable

IDENTITY = hashlib.sha256(b"semantic-identity").hexdigest()


def test_identical_concurrent_publishers_observe_one_complete_artifact(tmp_path):
    with ThreadPoolExecutor(max_workers=4) as pool:
        paths = list(pool.map(
            lambda _: publish_immutable(tmp_path, IDENTITY, b"complete-content"), range(12),
        ))
    assert len(set(paths)) == 1
    assert paths[0].read_bytes() == b"complete-content"
    assert list(tmp_path.iterdir()) == [paths[0]]


def test_conflicting_existing_identity_is_not_overwritten(tmp_path):
    path = publish_immutable(tmp_path, IDENTITY, b"first")
    with pytest.raises(ValueError, match="does not match"):
        publish_immutable(tmp_path, IDENTITY, b"different")
    assert path.read_bytes() == b"first"
    assert list(tmp_path.iterdir()) == [path]


def test_symlink_target_is_never_followed(tmp_path):
    outside = tmp_path / "outside"
    outside.write_bytes(b"private")
    (tmp_path / f"{IDENTITY}.json").symlink_to(outside)
    with pytest.raises(OSError):
        publish_immutable(tmp_path, IDENTITY, b"new")
    assert outside.read_bytes() == b"private"


def test_syncs_file_and_directory_and_propagates_directory_sync_error(tmp_path, monkeypatch):
    actual = os.fsync
    synced = []

    def sync(fd):
        kind = "directory" if stat.S_ISDIR(os.fstat(fd).st_mode) else "file"
        synced.append(kind)
        if kind == "directory":
            raise OSError("directory sync failed")
        actual(fd)

    monkeypatch.setattr("src.infrastructure.artifact_io.os.fsync", sync)
    with pytest.raises(OSError, match="directory sync failed"):
        publish_immutable(tmp_path, IDENTITY, b"payload")
    assert synced == ["file", "directory"]
    assert (tmp_path / f"{IDENTITY}.json").read_bytes() == b"payload"
    assert len(list(tmp_path.iterdir())) == 1


def test_interrupted_publication_cleans_temporary_without_success(tmp_path, monkeypatch):
    def interrupted(*_args, **_kwargs):
        raise OSError("publication interrupted")

    monkeypatch.setattr("src.infrastructure.artifact_io.os.link", interrupted)
    with pytest.raises(OSError, match="publication interrupted"):
        publish_immutable(tmp_path, IDENTITY, b"unpublished")
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("identity", ["../outside", "A" * 64, "abc", True])
def test_invalid_identity_is_rejected_before_io(tmp_path, identity):
    with pytest.raises(ValueError, match="artifact_id"):
        publish_immutable(tmp_path, identity, b"payload")


def test_existing_directory_and_bytes_and_supported_suffix_are_required(tmp_path):
    with pytest.raises(FileNotFoundError):
        publish_immutable(tmp_path / "missing", IDENTITY, b"x")
    with pytest.raises(ValueError, match="bytes"):
        publish_immutable(tmp_path, IDENTITY, "x")
    with pytest.raises(ValueError, match="suffix"):
        publish_immutable(tmp_path, IDENTITY, b"x", "/escape")
