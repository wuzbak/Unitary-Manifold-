# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Atomic, no-overwrite publication for local immutable reference artifacts."""

from __future__ import annotations

import os
from pathlib import Path
import re
import stat
import uuid

_DIGEST = re.compile(r"^[0-9a-f]{64}$")


def publish_immutable(
    directory: str | Path,
    artifact_id: str,
    content: bytes,
    suffix: str = ".json",
) -> Path:
    """Publish bytes durably in an existing, caller-established POSIX directory.

    The caller defines and verifies the artifact identity; it need not be the
    digest of the complete file (for example, an embedded checksum may cover its
    semantic payload). Existing different bytes are never overwritten.
    """
    if not isinstance(artifact_id, str) or not _DIGEST.fullmatch(artifact_id):
        raise ValueError("artifact_id must be a lowercase SHA-256 identifier")
    if not isinstance(content, bytes):
        raise ValueError("content must be immutable bytes")
    if suffix not in (".json", ".bin", ".azlq", ".azmq", ".npz"):
        raise ValueError("Unsupported artifact suffix")
    directory = Path(directory)
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    temporary = f".{artifact_id}.{uuid.uuid4().hex}.tmp"
    target = artifact_id + suffix
    try:
        fd = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=directory_fd,
        )
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(
                    temporary, target,
                    src_dir_fd=directory_fd, dst_dir_fd=directory_fd,
                    follow_symlinks=False,
                )
            except FileExistsError:
                existing_fd = os.open(
                    target, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                    dir_fd=directory_fd,
                )
                with os.fdopen(existing_fd, "rb") as stream:
                    if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                        raise ValueError("Existing artifact must be a regular file")
                    if stream.read() != content:
                        raise ValueError("Existing immutable artifact does not match its identity")
                    os.fsync(stream.fileno())
        finally:
            try:
                os.unlink(temporary, dir_fd=directory_fd)
            finally:
                os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return directory / target
