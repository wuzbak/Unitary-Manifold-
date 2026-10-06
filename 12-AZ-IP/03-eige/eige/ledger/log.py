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


def encode_record(record: Dict[str, Any]) -> bytes:
    """Validate a log record and return its canonical leaf bytes."""
    if not isinstance(record, dict) or not isinstance(record.get("type"), str):
        raise LogError("records must be dicts with a string 'type' field")
    return canonical_bytes(record)


def sign_tree_head(signer: Signer, log_id: str, tree_size: int, root: bytes, timestamp: int) -> SignedTreeHead:
    unsigned = SignedTreeHead(log_id, int(tree_size), root.hex(), int(timestamp), signer.key_id, "")
    return SignedTreeHead(**{**unsigned.__dict__, "signature": signer.sign(STH_CONTEXT, unsigned.signed_payload())})


class MerkleLog:
    """In-memory append-only log (tests, demos, small jurisdictions).

    Roots and proofs at any historical size cost O(log n) / O(log^2 n) hash
    lookups.  For county- or state-scale logs use
    :class:`eige.ledger.store.DurableMerkleLog`, which has the same API and
    keeps leaves and tree nodes in SQLite.
    """

    def __init__(self, log_id: str) -> None:
        if not log_id:
            raise LogError("log_id required")
        self.log_id = log_id
        self._leaves: List[bytes] = []
        self._tree = merkle.LevelledTree()

    def append(self, record: Dict[str, Any]) -> int:
        """Append a record (dict with a ``type`` field); returns its leaf index."""
        data = encode_record(record)
        self._leaves.append(data)
        return self._tree.append(merkle.leaf_hash(data))

    @property
    def size(self) -> int:
        return self._tree.size

    def entries(self) -> List[bytes]:
        return list(self._leaves)

    def leaf_hashes(self) -> List[bytes]:
        return [self._tree.leaf(i) for i in range(self.size)]

    def _wrap(self, fn, *args):
        try:
            return fn(*args)
        except merkle.ProofError as exc:
            raise LogError(str(exc)) from exc

    def root(self, size: Optional[int] = None) -> bytes:
        return self._wrap(self._tree.root, size)

    def inclusion_proof(self, index: int, size: Optional[int] = None) -> List[bytes]:
        return self._wrap(self._tree.inclusion_proof, index, size)

    def consistency_proof(self, old_size: int, new_size: Optional[int] = None) -> List[bytes]:
        return self._wrap(self._tree.consistency_proof, old_size, new_size)

    def sign_head(self, signer: Signer, timestamp: int) -> SignedTreeHead:
        return sign_tree_head(signer, self.log_id, self.size, self.root(), timestamp)
