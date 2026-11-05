# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""Content-addressed raw feed archives and source-bound, network-free replay."""

from __future__ import annotations

import base64
import hashlib
import json
import os
from pathlib import Path
import re
import stat

from src.infrastructure.artifact_io import publish_immutable

from .temporal_adapter import EarthquakeCapture, _capture_validated_feed
from .usgs_adapter import (
    LiveDataError, MAX_FEED_BYTES, USGS_FEED_URL, _decode_validated_feed, _parse_utc,
)

ARCHIVE_SCHEMA = "usgs_raw_capture_v1"
MAX_ARCHIVE_BYTES = 4 * ((MAX_FEED_BYTES + 2) // 3) + 65536
_DIGEST = re.compile(r"[0-9a-f]{64}")


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate archive key: {key}")
        result[key] = value
    return result


def _restore(document: object, *, owner_scope: str) -> EarthquakeCapture:
    expected = {
        "schema_version", "source_url", "owner_scope", "origin", "observed_at",
        "raw_payload_base64", "raw_payload_sha256", "snapshot_sha256", "code_bundle_sha256",
    }
    if not isinstance(document, dict) or set(document) != expected:
        raise ValueError("Malformed raw capture archive schema")
    if document["schema_version"] != ARCHIVE_SCHEMA or document["source_url"] != USGS_FEED_URL:
        raise ValueError("Unsupported raw capture archive source or schema")
    if not isinstance(owner_scope, str) or not owner_scope.strip():
        raise ValueError("owner_scope must be nonempty text")
    if document["owner_scope"] != owner_scope:
        raise ValueError("Requested owner_scope does not match the archive")
    if document["origin"] not in ("real", "synthetic", "fallback"):
        raise ValueError("Invalid archive origin")
    for key in ("raw_payload_sha256", "snapshot_sha256"):
        if not isinstance(document[key], str) or not _DIGEST.fullmatch(document[key]):
            raise ValueError(f"Invalid archive {key}")
    encoded = document["raw_payload_base64"]
    if not isinstance(encoded, str) or len(encoded) > 4 * ((MAX_FEED_BYTES + 2) // 3):
        raise ValueError("Invalid or oversized archived response")
    raw = base64.b64decode(encoded, validate=True)
    if len(raw) > MAX_FEED_BYTES or hashlib.sha256(raw).hexdigest() != document["raw_payload_sha256"]:
        raise ValueError("Archived response hash or size verification failed")
    observed_at = _parse_utc(document["observed_at"])
    payload, summary = _decode_validated_feed(raw, observed_at)
    capture = _capture_validated_feed(
        payload, summary, raw, owner_scope=owner_scope, origin=document["origin"],
    )
    if dict(capture.code_bundle_sha256) != document["code_bundle_sha256"]:
        raise ValueError("Replay transform source has changed; use the archived source version")
    if capture.snapshot.content_hash != document["snapshot_sha256"]:
        raise ValueError("Replayed snapshot hash verification failed")
    return capture


def save_capture_archive(capture: EarthquakeCapture, directory: str | Path) -> Path:
    """Atomically retain exact response bytes with their observation and source bindings.

    The existing directory and its ancestors must already be durably established.
    Scope/origin labels and local hashes do not authenticate the upstream source.
    """
    if not isinstance(capture, EarthquakeCapture):
        raise ValueError("capture must be an EarthquakeCapture")
    if not isinstance(capture.raw_payload, bytes) or len(capture.raw_payload) > MAX_FEED_BYTES:
        raise ValueError("Capture response must be bounded bytes")
    document = {
        "schema_version": ARCHIVE_SCHEMA,
        "source_url": USGS_FEED_URL,
        "owner_scope": capture.snapshot.owner_scope,
        "origin": capture.origin,
        "observed_at": capture.snapshot.captured_at.isoformat(),
        "raw_payload_base64": base64.b64encode(capture.raw_payload).decode("ascii"),
        "raw_payload_sha256": capture.raw_payload_sha256,
        "snapshot_sha256": capture.snapshot.content_hash,
        "code_bundle_sha256": dict(capture.code_bundle_sha256),
    }
    _restore(document, owner_scope=capture.snapshot.owner_scope)
    raw = (json.dumps(document, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()
    if len(raw) > MAX_ARCHIVE_BYTES:
        raise ValueError("Raw capture archive exceeds its byte bound")
    archive_id = hashlib.sha256(raw).hexdigest()
    root_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        return publish_immutable(directory, archive_id, raw, directory_fd=root_fd)
    finally:
        os.close(root_fd)


def load_capture_archive(
    directory: str | Path, archive_id: str, *, owner_scope: str,
) -> EarthquakeCapture:
    """Replay verified bytes at their original observation time without any transport."""
    if not isinstance(archive_id, str) or not _DIGEST.fullmatch(archive_id):
        raise ValueError("archive_id must be a lowercase SHA-256 identifier")
    root_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        fd = os.open(
            archive_id + ".json", os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
            dir_fd=root_fd,
        )
        with os.fdopen(fd, "rb") as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_ARCHIVE_BYTES:
                raise ValueError("Archive must be a bounded regular file")
            raw = stream.read(MAX_ARCHIVE_BYTES + 1)
    finally:
        os.close(root_fd)
    if len(raw) > MAX_ARCHIVE_BYTES or hashlib.sha256(raw).hexdigest() != archive_id:
        raise ValueError("Raw capture archive hash or size verification failed")
    try:
        document = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_keys)
        return _restore(document, owner_scope=owner_scope)
    except (ValueError, TypeError, OverflowError, RecursionError, LiveDataError) as exc:
        raise ValueError(f"Raw capture replay invalid: {exc}") from exc
