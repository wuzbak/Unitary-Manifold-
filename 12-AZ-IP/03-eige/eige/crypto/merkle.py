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
from typing import Iterable, List, Optional, Sequence

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
    return 1 << ((n - 1).bit_length() - 1)


# --------------------------------------------------------------------------
# Streaming accumulator: O(log n) memory, any number of leaves
# --------------------------------------------------------------------------

class CompactRange:
    """Streaming Merkle accumulator over leaf hashes.

    Keeps only the roots of the perfect subtrees that make up the tree so far
    (one per set bit of the size), so memory is O(log n) regardless of how many
    leaves are appended.  ``root()`` equals the RFC 6962 Merkle Tree Hash of
    every leaf appended so far.
    """

    __slots__ = ("size", "_stack")

    def __init__(self) -> None:
        self.size = 0
        self._stack: List[bytes] = []

    def append(self, digest: bytes) -> None:
        n = self.size
        h = digest
        while n & 1:
            h = node_hash(self._stack.pop(), h)
            n >>= 1
        self._stack.append(h)
        self.size += 1

    def root(self) -> bytes:
        if not self._stack:
            return empty_root()
        r = self._stack[-1]
        for h in reversed(self._stack[:-1]):
            r = node_hash(h, r)
        return r


# --------------------------------------------------------------------------
# Levelled tree: stores every complete perfect-subtree hash; O(log n) roots
# and O(log^2 n) proofs at any historical size.
# --------------------------------------------------------------------------

class NodeStore:
    """Storage for perfect-subtree hashes, keyed by (level, index)."""

    def get(self, level: int, index: int) -> bytes:  # pragma: no cover - interface
        raise NotImplementedError

    def put(self, level: int, index: int, digest: bytes) -> None:  # pragma: no cover - interface
        raise NotImplementedError


class MemoryNodeStore(NodeStore):
    """Packed in-memory store: 32 bytes per node, about 64 bytes per leaf in total."""

    def __init__(self) -> None:
        self._levels: List[bytearray] = []

    def get(self, level: int, index: int) -> bytes:
        return bytes(self._levels[level][index * HASH_SIZE:(index + 1) * HASH_SIZE])

    def put(self, level: int, index: int, digest: bytes) -> None:
        while len(self._levels) <= level:
            self._levels.append(bytearray())
        buf = self._levels[level]
        if len(buf) != index * HASH_SIZE:
            raise ProofError("nodes must be stored in append order")
        buf += digest


class LevelledTree:
    """Append-only RFC 6962 tree over a :class:`NodeStore`."""

    def __init__(self, store: Optional[NodeStore] = None, size: int = 0) -> None:
        self.store = store if store is not None else MemoryNodeStore()
        self.size = size

    def append(self, digest: bytes) -> int:
        index = self.size
        self.store.put(0, index, digest)
        level, i, h = 0, index, digest
        while i & 1:
            h = node_hash(self.store.get(level, i - 1), h)
            level += 1
            i >>= 1
            self.store.put(level, i, h)
        self.size += 1
        return index

    def _check_size(self, n: int) -> None:
        if not 0 <= n <= self.size:
            raise ProofError(f"size {n} out of range for tree of {self.size} leaves")

    def subtree_hash(self, start: int, size: int) -> bytes:
        """MTH of leaves ``[start, start+size)``; ranges come from RFC 6962 recursion."""
        if size & (size - 1) == 0 and start % size == 0:
            return self.store.get(size.bit_length() - 1, start // size)
        k = _split(size)
        return node_hash(self.subtree_hash(start, k), self.subtree_hash(start + k, size - k))

    def leaf(self, index: int) -> bytes:
        if not 0 <= index < self.size:
            raise ProofError(f"leaf index {index} out of range for tree size {self.size}")
        return self.store.get(0, index)

    def root(self, size: Optional[int] = None) -> bytes:
        n = self.size if size is None else size
        self._check_size(n)
        return empty_root() if n == 0 else self.subtree_hash(0, n)

    def inclusion_proof(self, index: int, size: Optional[int] = None) -> List[bytes]:
        n = self.size if size is None else size
        self._check_size(n)
        if not 0 <= index < n:
            raise ProofError(f"leaf index {index} out of range for tree size {n}")
        out: List[bytes] = []
        start, m = 0, index
        while n > 1:
            k = _split(n)
            if m < k:
                out.append(self.subtree_hash(start + k, n - k))
                n = k
            else:
                out.append(self.subtree_hash(start, k))
                start, m, n = start + k, m - k, n - k
        out.reverse()
        return out

    def consistency_proof(self, old_size: int, new_size: Optional[int] = None) -> List[bytes]:
        n = self.size if new_size is None else new_size
        self._check_size(n)
        if not 0 <= old_size <= n:
            raise ProofError(f"old size {old_size} out of range for tree size {n}")
        if old_size == 0 or old_size == n:
            return []
        out: List[bytes] = []
        start, m, complete = 0, old_size, True
        while m != n:
            k = _split(n)
            if m <= k:
                out.append(self.subtree_hash(start + k, n - k))
                n = k
            else:
                out.append(self.subtree_hash(start, k))
                start, m, n, complete = start + k, m - k, n - k, False
        if not complete:
            out.append(self.subtree_hash(start, n))
        out.reverse()
        return out


def _tree(hashes: Sequence[bytes]) -> LevelledTree:
    tree = LevelledTree()
    for h in hashes:
        tree.append(h)
    return tree


def root_from_leaf_hashes(hashes: Iterable[bytes]) -> bytes:
    """Merkle Tree Hash (MTH) over already-hashed leaves, in O(log n) memory."""
    acc = CompactRange()
    for h in hashes:
        acc.append(h)
    return acc.root()


def merkle_root(leaves: Iterable[bytes]) -> bytes:
    """Merkle Tree Hash over raw leaf data."""
    return root_from_leaf_hashes(leaf_hash(d) for d in leaves)


def inclusion_proof(hashes: Sequence[bytes], index: int) -> List[bytes]:
    """Audit path (RFC 6962 PATH) for leaf ``index`` in the tree of ``hashes``."""
    n = len(hashes)
    if not 0 <= index < n:
        raise ProofError(f"leaf index {index} out of range for tree size {n}")
    return _tree(hashes).inclusion_proof(index)


def consistency_proof(hashes: Sequence[bytes], old_size: int) -> List[bytes]:
    """Consistency proof (RFC 6962 PROOF) from ``old_size`` to ``len(hashes)``."""
    n = len(hashes)
    if not 0 <= old_size <= n:
        raise ProofError(f"old size {old_size} out of range for tree size {n}")
    return _tree(hashes).consistency_proof(old_size)


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
