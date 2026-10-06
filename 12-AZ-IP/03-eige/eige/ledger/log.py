# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Append-only Merkle event log with Ed25519-signed tree heads (STH).

Every ballot-ingestion record, custody event and administrative action is a
leaf (canonical JSON bytes).  A county periodically publishes a signed tree
head; anyone can then check

* that a given record is in the log (inclusion proof), and
* that a later head extends an earlier one without rewriting history
  (consistency proof).

Stuffing, deletion or reordering of already-published records changes the
root and breaks the consistency proof.  Records that were never logged (for
example, ballots altered before scanning) cannot be detected by this log.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..canonical import canonical_bytes
from ..crypto import merkle
from ..crypto.signing import SIGNATURE_ALG, KeyRegistry, Signer, VerificationResult

STH_FORMAT = "eige.sth.v1"
STH_CONTEXT = "sth"


class LogError(ValueError):
    """Raised for invalid log operations."""


@dataclass(frozen=True)
class SignedTreeHead:
    log_id: str
    tree_size: int
    root_hash: str
    timestamp: int
    key_id: str
    signature: str

    def signed_payload(self) -> dict:
        return {
            "format": STH_FORMAT,
            "log_id": self.log_id,
            "tree_size": self.tree_size,
            "root_hash": self.root_hash,
            "timestamp": self.timestamp,
            "key_id": self.key_id,
            "alg": SIGNATURE_ALG,
        }

    def as_dict(self) -> dict:
        d = self.signed_payload()
        d["signature"] = self.signature
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "SignedTreeHead":
        if d.get("format") != STH_FORMAT or d.get("alg") != SIGNATURE_ALG:
            raise LogError("unsupported signed tree head format")
        size = d["tree_size"]
        ts = d["timestamp"]
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            raise LogError("tree_size must be a non-negative integer")
        if not isinstance(ts, int) or isinstance(ts, bool):
            raise LogError("timestamp must be an integer")
        root = str(d["root_hash"])
        if len(bytes.fromhex(root)) != merkle.HASH_SIZE:
            raise LogError("root_hash must be 32 bytes of hex")
        return cls(str(d["log_id"]), size, root, ts, str(d["key_id"]), str(d["signature"]))

    def verify(self, registry: KeyRegistry, expected_owner: Optional[str] = None, allow_development: bool = True) -> VerificationResult:
        return registry.verify(
            self.key_id,
            STH_CONTEXT,
            self.signed_payload(),
            self.signature,
            self.timestamp,
            expected_owner=expected_owner,
            allow_development=allow_development,
        )


def sign_tree_head(signer: Signer, log_id: str, tree_size: int, root: bytes, timestamp: int) -> SignedTreeHead:
    unsigned = SignedTreeHead(log_id, int(tree_size), root.hex(), int(timestamp), signer.key_id, "")
    return SignedTreeHead(**{**unsigned.__dict__, "signature": signer.sign(STH_CONTEXT, unsigned.signed_payload())})


class MerkleLog:
    """In-memory append-only log.  Persist ``entries()`` to durable storage."""

    def __init__(self, log_id: str) -> None:
        if not log_id:
            raise LogError("log_id required")
        self.log_id = log_id
        self._leaves: List[bytes] = []
        self._hashes: List[bytes] = []

    def append(self, record: Dict[str, Any]) -> int:
        """Append a record (dict with a ``type`` field); returns its leaf index."""
        if not isinstance(record, dict) or not isinstance(record.get("type"), str):
            raise LogError("records must be dicts with a string 'type' field")
        data = canonical_bytes(record)
        self._leaves.append(data)
        self._hashes.append(merkle.leaf_hash(data))
        return len(self._leaves) - 1

    @property
    def size(self) -> int:
        return len(self._leaves)

    def entries(self) -> List[bytes]:
        return list(self._leaves)

    def leaf_hashes(self) -> List[bytes]:
        return list(self._hashes)

    def root(self, size: Optional[int] = None) -> bytes:
        n = self.size if size is None else size
        if not 0 <= n <= self.size:
            raise LogError(f"size {n} out of range")
        return merkle.root_from_leaf_hashes(self._hashes[:n])

    def inclusion_proof(self, index: int, size: Optional[int] = None) -> List[bytes]:
        n = self.size if size is None else size
        if not 0 <= n <= self.size:
            raise LogError(f"size {n} out of range")
        return merkle.inclusion_proof(self._hashes[:n], index)

    def consistency_proof(self, old_size: int, new_size: Optional[int] = None) -> List[bytes]:
        n = self.size if new_size is None else new_size
        if not 0 <= n <= self.size:
            raise LogError(f"size {n} out of range")
        return merkle.consistency_proof(self._hashes[:n], old_size)

    def sign_head(self, signer: Signer, timestamp: int) -> SignedTreeHead:
        return sign_tree_head(signer, self.log_id, self.size, self.root(), timestamp)
