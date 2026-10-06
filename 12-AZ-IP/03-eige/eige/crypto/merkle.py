# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""RFC 6962 / RFC 9162 Merkle tree hashing, inclusion and consistency proofs.

This is the Certificate Transparency construction with SHA-256:

* leaf hash      ``SHA-256(0x00 || leaf_bytes)``
* interior hash  ``SHA-256(0x01 || left || right)``
* empty tree     ``SHA-256("")``

Proof generation follows RFC 6962 §2.1.1–2.1.2 and verification follows the
iterative algorithms in RFC 9162 §2.1.3.2 and §2.1.4.2.
"""

from __future__ import annotations

import hashlib
from typing import List, Sequence

HASH_SIZE = 32
_LEAF_PREFIX = b"\x00"
_NODE_PREFIX = b"\x01"


class ProofError(ValueError):
    """Raised for malformed proof requests (bad indices or sizes)."""


def leaf_hash(data: bytes) -> bytes:
    return hashlib.sha256(_LEAF_PREFIX + data).digest()


def node_hash(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(_NODE_PREFIX + left + right).digest()


def empty_root() -> bytes:
    return hashlib.sha256(b"").digest()


def _split(n: int) -> int:
    """Largest power of two strictly less than ``n`` (n >= 2)."""
    k = 1
    while k << 1 < n:
        k <<= 1
    return k


def root_from_leaf_hashes(hashes: Sequence[bytes]) -> bytes:
    """Merkle Tree Hash (MTH) over already-hashed leaves."""
    n = len(hashes)
    if n == 0:
        return empty_root()
    if n == 1:
        return hashes[0]
    k = _split(n)
    return node_hash(root_from_leaf_hashes(hashes[:k]), root_from_leaf_hashes(hashes[k:]))


def merkle_root(leaves: Sequence[bytes]) -> bytes:
    """Merkle Tree Hash over raw leaf data."""
    return root_from_leaf_hashes([leaf_hash(d) for d in leaves])


def inclusion_proof(hashes: Sequence[bytes], index: int) -> List[bytes]:
    """Audit path (RFC 6962 PATH) for leaf ``index`` in the tree of ``hashes``."""
    n = len(hashes)
    if not 0 <= index < n:
        raise ProofError(f"leaf index {index} out of range for tree size {n}")
    if n == 1:
        return []
    k = _split(n)
    if index < k:
        return inclusion_proof(hashes[:k], index) + [root_from_leaf_hashes(hashes[k:])]
    return inclusion_proof(hashes[k:], index - k) + [root_from_leaf_hashes(hashes[:k])]


def _subproof(hashes: Sequence[bytes], m: int, complete: bool) -> List[bytes]:
    n = len(hashes)
    if m == n:
        return [] if complete else [root_from_leaf_hashes(hashes)]
    k = _split(n)
    if m <= k:
        return _subproof(hashes[:k], m, complete) + [root_from_leaf_hashes(hashes[k:])]
    return _subproof(hashes[k:], m - k, False) + [root_from_leaf_hashes(hashes[:k])]


def consistency_proof(hashes: Sequence[bytes], old_size: int) -> List[bytes]:
    """Consistency proof (RFC 6962 PROOF) from ``old_size`` to ``len(hashes)``."""
    n = len(hashes)
    if not 0 <= old_size <= n:
        raise ProofError(f"old size {old_size} out of range for tree size {n}")
    if old_size == 0 or old_size == n:
        return []
    return _subproof(hashes, old_size, True)


def verify_inclusion(
    leaf_digest: bytes, index: int, tree_size: int, proof: Sequence[bytes], root: bytes
) -> bool:
    """RFC 9162 §2.1.3.2 inclusion-proof verification."""
    if not 0 <= index < tree_size:
        return False
    if any(len(p) != HASH_SIZE for p in proof):
        return False
    fn, sn, r = index, tree_size - 1, leaf_digest
    for p in proof:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            r = node_hash(p, r)
            if not fn & 1:
                while not fn & 1 and fn != 0:
                    fn >>= 1
                    sn >>= 1
        else:
            r = node_hash(r, p)
        fn >>= 1
        sn >>= 1
    return sn == 0 and r == root


def verify_consistency(
    old_size: int, new_size: int, old_root: bytes, new_root: bytes, proof: Sequence[bytes]
) -> bool:
    """RFC 9162 §2.1.4.2 consistency-proof verification."""
    if not 0 <= old_size <= new_size:
        return False
    if any(len(p) != HASH_SIZE for p in proof):
        return False
    if old_size == new_size:
        return len(proof) == 0 and old_root == new_root
    if old_size == 0:
        return len(proof) == 0 and old_root == empty_root()
    path = list(proof)
    if old_size & (old_size - 1) == 0:  # exact power of two
        path = [old_root] + path
    if not path:
        return False
    fn, sn = old_size - 1, new_size - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    fr = sr = path[0]
    for c in path[1:]:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr = node_hash(c, fr)
            sr = node_hash(c, sr)
            if not fn & 1:
                while not fn & 1 and fn != 0:
                    fn >>= 1
                    sn >>= 1
        else:
            sr = node_hash(sr, c)
        fn >>= 1
        sn >>= 1
    return fr == old_root and sr == new_root and sn == 0
