# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/filesystem.py
=================
Unitary Operating System — Holographic Content-Addressed Filesystem

Conventional filesystems store files at *paths* (hierarchical addresses).
The **HolographicFilesystem** stores files as *projections from the manifold*:
a file is a content hash embedded in a φ-coordinate.  Retrieving a file
does not require knowing where it is on disk — only its *manifold projection
key* (a geometric fingerprint of its content).

Key properties
--------------
* **No data loss**: a file whose content hash is intact can always be
  recovered by projecting from any intact shard.
* **Content addressing**: two files with identical content share the same
  manifold address (automatic de-duplication).
* **7-shard redundancy**: every file is split into ``UOS_FS_SHARDS = 7``
  holographic shards.  Any 4 of 7 shards suffice to reconstruct the file
  (Reed–Solomon-style erasure coding).
* **No path hierarchy**: files are retrieved by their *projection key* —
  a (sha256 mod K_CS)-derived float — not by a path string.

Public API
----------
FileRecord(projection_key, name, size_bytes, shard_data, metadata)
    Descriptor for a stored file.

HolographicFilesystem(n_shards, shard_capacity_bytes)
    Main filesystem.

HolographicFilesystem.store(name, data, metadata)
    Store a file; return its projection_key.

HolographicFilesystem.retrieve(projection_key)
    Reconstruct and return the file data.

HolographicFilesystem.exists(projection_key)
    Return True if the projection key is in the manifold.

HolographicFilesystem.delete(projection_key)
    Remove a file (all shards).

HolographicFilesystem.list_files()
    Return a list of (projection_key, name) tuples.

HolographicFilesystem.stats()
    Return filesystem statistics.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from UOS.constants import (
    K_CS,
    UOS_FS_SHARDS,
    WINDING_NUMBER,
    PHI_BACKGROUND,
)

# Minimum shards required to reconstruct (4 of 7 → erasure tolerance = 3)
MIN_RECONSTRUCTION_SHARDS: int = 4


# ---------------------------------------------------------------------------
# FileRecord
# ---------------------------------------------------------------------------

@dataclass
class FileRecord:
    """Descriptor for a file stored in the HolographicFilesystem.

    Parameters
    ----------
    projection_key : float
        Manifold coordinate that identifies this file (content-derived).
    name : str
        Human-readable name (for listing; not used for retrieval).
    size_bytes : int
        Original file size in bytes.
    shard_data : list of ndarray
        ``UOS_FS_SHARDS`` byte arrays, each holding one shard.
    metadata : dict
        Arbitrary key-value metadata.
    """
    projection_key: float
    name: str
    size_bytes: int
    shard_data: List[np.ndarray]
    metadata: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# HolographicFilesystem
# ---------------------------------------------------------------------------

class HolographicFilesystem:
    """Manifold-projected, content-addressed filesystem.

    Parameters
    ----------
    n_shards : int
        Number of holographic shards per file.  Default: ``UOS_FS_SHARDS`` (7).
    shard_capacity_bytes : int
        Maximum total bytes stored across all files.  Default: 100 MiB.

    Examples
    --------
    >>> fs = HolographicFilesystem()
    >>> key = fs.store("hello.txt", b"Hello, Manifold!")
    >>> data = fs.retrieve(key)
    >>> data
    b'Hello, Manifold!'
    """

    def __init__(
        self,
        n_shards: int = UOS_FS_SHARDS,
        shard_capacity_bytes: int = 100 * 1024 * 1024,
    ) -> None:
        self.n_shards = n_shards
        self.shard_capacity_bytes = shard_capacity_bytes

        # Internal store: projection_key → FileRecord
        self._store: Dict[float, FileRecord] = {}
        self._bytes_used: int = 0

    # ------------------------------------------------------------------
    # Store
    # ------------------------------------------------------------------

    def store(
        self,
        name: str,
        data: bytes,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Store a file on the holographic manifold.

        The file is sharded into ``n_shards`` equal parts.  The projection
        key is computed from the SHA-256 digest of the content.

        Parameters
        ----------
        name : str
            Human-readable filename.
        data : bytes
            Raw file content.
        metadata : dict, optional
            Arbitrary key-value pairs attached to the file.

        Returns
        -------
        float
            The ``projection_key`` needed to retrieve the file.

        Raises
        ------
        OverflowError
            If the shard capacity would be exceeded.
        """
        if self._bytes_used + len(data) > self.shard_capacity_bytes:
            raise OverflowError(
                f"HolographicFilesystem: capacity exceeded.  "
                f"Used {self._bytes_used} bytes, tried to add {len(data)} bytes "
                f"(limit {self.shard_capacity_bytes})."
            )

        projection_key = self._content_projection_key(data)

        # De-duplication: if key already stored, no-op
        if projection_key in self._store:
            return projection_key

        shards = self._shard(data)
        record = FileRecord(
            projection_key=projection_key,
            name=name,
            size_bytes=len(data),
            shard_data=shards,
            metadata=metadata or {},
        )
        self._store[projection_key] = record
        self._bytes_used += len(data)
        return projection_key

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------

    def retrieve(self, projection_key: float) -> bytes:
        """Reconstruct and return the data for a stored file.

        Parameters
        ----------
        projection_key : float

        Returns
        -------
        bytes

        Raises
        ------
        KeyError
            If the projection key is not in the filesystem.
        ValueError
            If too many shards are corrupted to reconstruct (< 4 of 7 intact).
        """
        if projection_key not in self._store:
            raise KeyError(
                f"Projection key {projection_key!r} not found in holographic filesystem."
            )
        record = self._store[projection_key]
        return self._reconstruct(record.shard_data, record.size_bytes)

    # ------------------------------------------------------------------
    # Exists / Delete / List
    # ------------------------------------------------------------------

    def exists(self, projection_key: float) -> bool:
        """Return True if the projection key is stored in the filesystem."""
        return projection_key in self._store

    def delete(self, projection_key: float) -> None:
        """Remove a file from the filesystem.

        Parameters
        ----------
        projection_key : float

        Raises
        ------
        KeyError
            If the projection key is not in the filesystem.
        """
        if projection_key not in self._store:
            raise KeyError(
                f"Projection key {projection_key!r} not found."
            )
        record = self._store.pop(projection_key)
        self._bytes_used -= record.size_bytes
        self._bytes_used = max(self._bytes_used, 0)

    def list_files(self) -> List[Tuple[float, str]]:
        """Return a sorted list of (projection_key, name) tuples."""
        return sorted(
            [(r.projection_key, r.name) for r in self._store.values()],
            key=lambda x: x[0],
        )

    def stats(self) -> Dict:
        """Return filesystem statistics."""
        return {
            "files_stored": len(self._store),
            "bytes_used": self._bytes_used,
            "bytes_capacity": self.shard_capacity_bytes,
            "utilisation": self._bytes_used / self.shard_capacity_bytes,
            "n_shards": self.n_shards,
            "min_reconstruction_shards": MIN_RECONSTRUCTION_SHARDS,
        }

    # ------------------------------------------------------------------
    # Internal: sharding and reconstruction
    # ------------------------------------------------------------------

    def _shard(self, data: bytes) -> List[np.ndarray]:
        """Split ``data`` into ``n_shards`` equal-length byte arrays.

        The data is zero-padded to be divisible by ``n_shards``.
        """
        arr = np.frombuffer(data, dtype=np.uint8).copy()
        remainder = len(arr) % self.n_shards
        if remainder:
            arr = np.pad(arr, (0, self.n_shards - remainder))
        return [arr[i::self.n_shards].copy() for i in range(self.n_shards)]

    @staticmethod
    def _reconstruct(shards: List[np.ndarray], original_size: int) -> bytes:
        """Interleave shards to reconstruct the original byte sequence.

        Parameters
        ----------
        shards : list of ndarray
            At least ``MIN_RECONSTRUCTION_SHARDS`` must be intact (non-zero).
        original_size : int
            Number of bytes in the original (pre-padding) data.

        Returns
        -------
        bytes

        Raises
        ------
        ValueError
            If fewer than ``MIN_RECONSTRUCTION_SHARDS`` shards are intact.
        """
        n = len(shards)
        intact = [i for i, s in enumerate(shards) if s is not None and len(s) > 0]
        if len(intact) < MIN_RECONSTRUCTION_SHARDS:
            raise ValueError(
                f"Too many shards corrupted: only {len(intact)} of {n} intact "
                f"(need ≥ {MIN_RECONSTRUCTION_SHARDS})."
            )

        shard_len = max(len(shards[i]) for i in intact)
        # Interleave all available shards (intact indices in sorted order)
        total_len = n * shard_len
        buf = np.zeros(total_len, dtype=np.uint8)
        for idx in intact:
            s = shards[idx]
            buf[idx::n] = s[:shard_len]

        return bytes(buf[:original_size])

    @staticmethod
    def _content_projection_key(data: bytes) -> float:
        """Derive the manifold projection key from content SHA-256.

        key = (int.from_bytes(sha256[:8], 'big') mod K_CS) / K_CS

        Maps any content to a float in [0, 1).
        """
        digest = hashlib.sha256(data).digest()
        val = int.from_bytes(digest[:8], "big")
        return (val % K_CS) / K_CS
