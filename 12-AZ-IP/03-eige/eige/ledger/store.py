# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Durable, county/state-scale Merkle log backed by SQLite.

:class:`DurableMerkleLog` has the same API as the in-memory
:class:`eige.ledger.log.MerkleLog`, but leaves, perfect-subtree hashes and
published signed tree heads live in a single SQLite file:

* appends are batched in transactions (``append_many``), so ingesting tens of
  millions of records costs a few hundred bytes of disk per record and
  constant memory;
* roots and inclusion/consistency proofs at any historical size are computed
  from stored subtree hashes in O(log n) / O(log^2 n) lookups;
* the database can be closed and reopened (for example after a crash or a
  reboot) and appending resumes at the last committed record — a partially
  written batch is rolled back by SQLite, never half-applied;
* :meth:`check_integrity` recomputes every leaf hash and the root from the
  stored leaf bytes, so a database edited outside EIGE is detected before it is
  published.

The file is an operational store, not a publication format; publish with
:meth:`export_bundle`.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Tuple

from ..crypto import merkle
from ..crypto.signing import Signer
from .log import LogError, SignedTreeHead, encode_record, sign_tree_head

SCHEMA_VERSION = "eige.durable_log.v1"


class _SQLiteNodeStore(merkle.NodeStore):
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get(self, level: int, index: int) -> bytes:
        row = self._conn.execute("SELECT hash FROM nodes WHERE level=? AND idx=?", (level, index)).fetchone()
        if row is None:
            raise LogError(f"missing tree node ({level}, {index}); the store is corrupt")
        return bytes(row[0])

    def put(self, level: int, index: int, digest: bytes) -> None:
        self._conn.execute("INSERT INTO nodes(level, idx, hash) VALUES (?,?,?)", (level, index, digest))


class _CachedNodeStore(merkle.NodeStore):
    """Write-through cache of the right edge so appends don't re-read nodes."""

    def __init__(self, inner: _SQLiteNodeStore) -> None:
        self._inner = inner
        self._edge: Dict[int, tuple] = {}

    def get(self, level: int, index: int) -> bytes:
        hit = self._edge.get(level)
        if hit is not None and hit[0] == index:
            return hit[1]
        return self._inner.get(level, index)

    def put(self, level: int, index: int, digest: bytes) -> None:
        self._inner.put(level, index, digest)
        self._edge[level] = (index, digest)

    def reset(self) -> None:
        self._edge.clear()


class DurableMerkleLog:
    """Append-only RFC 6962 log persisted in SQLite (see module docstring)."""

    def __init__(self, path: str | Path, log_id: Optional[str] = None) -> None:
        self.path = Path(path)
        self._conn = sqlite3.connect(str(self.path), isolation_level=None)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA synchronous=FULL")
        self._conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS leaves (idx INTEGER PRIMARY KEY, data BLOB NOT NULL);
            CREATE TABLE IF NOT EXISTS nodes (level INTEGER NOT NULL, idx INTEGER NOT NULL, hash BLOB NOT NULL,
                                              PRIMARY KEY (level, idx)) WITHOUT ROWID;
            CREATE TABLE IF NOT EXISTS heads (seq INTEGER PRIMARY KEY, tree_size INTEGER NOT NULL, head TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS unique_keys (key TEXT PRIMARY KEY, idx INTEGER NOT NULL) WITHOUT ROWID;
            """
        )
        meta = dict(self._conn.execute("SELECT key, value FROM meta").fetchall())
        if not meta:
            if not log_id:
                raise LogError("log_id required to create a new durable log")
            self._conn.execute("BEGIN")
            self._conn.executemany("INSERT INTO meta(key, value) VALUES (?,?)",
                                   [("schema", SCHEMA_VERSION), ("log_id", log_id)])
            self._conn.execute("COMMIT")
            meta = {"schema": SCHEMA_VERSION, "log_id": log_id}
        if meta.get("schema") != SCHEMA_VERSION:
            raise LogError(f"unsupported store schema {meta.get('schema')!r}")
        if log_id is not None and log_id != meta["log_id"]:
            raise LogError(f"store belongs to log {meta['log_id']!r}, not {log_id!r}")
        self.log_id = meta["log_id"]
        size = self._conn.execute("SELECT COALESCE(MAX(idx) + 1, 0) FROM leaves").fetchone()[0]
        nodes0 = self._conn.execute("SELECT COUNT(*) FROM nodes WHERE level=0").fetchone()[0]
        if nodes0 != size:
            raise LogError("leaf and node tables disagree; the store is corrupt")
        self._store = _CachedNodeStore(_SQLiteNodeStore(self._conn))
        self._tree = merkle.LevelledTree(self._store, size)

    # ----------------------------------------------------------------- lifecycle
    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "DurableMerkleLog":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ------------------------------------------------------------------- append
    def append(self, record: Dict[str, Any]) -> int:
        return self.append_many([record])[0]

    def append_many(self, records: Iterable[Dict[str, Any]], batch_size: int = 10_000,
                    unique_key: Optional[Callable[[Dict[str, Any]], Optional[str]]] = None,
                    atomic: bool = False, before_commit: Optional[Callable[[], None]] = None) -> List[int]:
        """Append records; returns their leaf indices.

        By default each batch of ``batch_size`` records is one transaction:
        after a crash the log contains every committed batch and nothing of a
        partial one.  With ``atomic=True`` the whole input is one transaction
        (still written in batches of ``batch_size``), and ``before_commit`` is
        called just before it commits; if anything raises, nothing is logged.
        If ``unique_key`` returns a key for a record, the key must never have
        been logged before (for example a CVR id); a repeat raises
        :class:`LogError` and rolls back the transaction.
        """
        encoded = ((encode_record(r), unique_key(r) if unique_key else None) for r in records)
        if atomic:
            return self._write(encoded, batch_size, before_commit)
        out: List[int] = []
        batch: List[Tuple[bytes, Optional[str]]] = []
        for item in encoded:
            batch.append(item)
            if len(batch) >= batch_size:
                out.extend(self._write(batch, batch_size))
                batch = []
        if batch:
            out.extend(self._write(batch, batch_size))
        return out

    def has_key(self, key: str) -> bool:
        return self._conn.execute("SELECT 1 FROM unique_keys WHERE key=?", (key,)).fetchone() is not None

    def append_encoded(self, entries: Iterable[bytes], batch_size: int = 10_000) -> int:
        """Append already-canonical leaf bytes (e.g. from another log); returns new size."""
        batch: List[Tuple[bytes, Optional[str]]] = []
        for e in entries:
            batch.append((bytes(e), None))
            if len(batch) >= batch_size:
                self._write(batch, batch_size)
                batch = []
        if batch:
            self._write(batch, batch_size)
        return self.size

    def _write(self, items: Iterable[Tuple[bytes, Optional[str]]], batch_size: int,
               before_commit: Optional[Callable[[], None]] = None) -> List[int]:
        """Write ``items`` in one transaction; the in-memory tree is restored on any failure."""
        start = self._tree.size
        self._conn.execute("BEGIN IMMEDIATE")
        try:
            chunk: List[Tuple[bytes, Optional[str]]] = []
            for item in items:
                chunk.append(item)
                if len(chunk) >= batch_size:
                    self._insert(chunk)
                    chunk = []
            if chunk:
                self._insert(chunk)
            if before_commit is not None:
                before_commit()
            self._conn.execute("COMMIT")
        except BaseException:
            # Restore the in-memory view first: SQLite may already have rolled
            # back on its own (e.g. SQLITE_FULL), making ROLLBACK itself fail.
            self._tree.size = start
            self._store.reset()
            if self._conn.in_transaction:
                try:
                    self._conn.execute("ROLLBACK")
                except sqlite3.Error:
                    pass
            raise
        return list(range(start, self._tree.size))

    def _insert(self, chunk: List[Tuple[bytes, Optional[str]]]) -> None:
        base = self._tree.size
        self._conn.executemany("INSERT INTO leaves(idx, data) VALUES (?,?)",
                               ((base + i, d) for i, (d, _) in enumerate(chunk)))
        keys = [(k, base + i) for i, (_, k) in enumerate(chunk) if k is not None]
        if keys:
            try:
                self._conn.executemany("INSERT INTO unique_keys(key, idx) VALUES (?,?)", keys)
            except sqlite3.IntegrityError as exc:
                raise LogError("a record with the same unique key is already in the log "
                               "(for example a CVR id ingested twice); the transaction was rolled back") from exc
        for d, _ in chunk:
            self._tree.append(merkle.leaf_hash(d))

    # -------------------------------------------------------------------- reads
    @property
    def size(self) -> int:
        return self._tree.size

    def entry(self, index: int) -> bytes:
        row = self._conn.execute("SELECT data FROM leaves WHERE idx=?", (index,)).fetchone()
        if row is None:
            raise LogError(f"no entry {index}")
        return bytes(row[0])

    def iter_entries(self, start: int = 0, stop: Optional[int] = None, chunk: int = 50_000) -> Iterator[bytes]:
        """Stream entries in order using bounded memory."""
        stop = self.size if stop is None else stop
        i = start
        while i < stop:
            rows = self._conn.execute("SELECT data FROM leaves WHERE idx>=? AND idx<? ORDER BY idx",
                                      (i, min(stop, i + chunk))).fetchall()
            for (data,) in rows:
                yield bytes(data)
            i += chunk

    def entries(self) -> List[bytes]:
        return list(self.iter_entries())

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

    # -------------------------------------------------------------------- heads
    def sign_head(self, signer: Signer, timestamp: int) -> SignedTreeHead:
        prev = self.heads()
        if prev and (timestamp < prev[-1].timestamp):
            raise LogError("tree head timestamps must not go backwards")
        head = sign_tree_head(signer, self.log_id, self.size, self.root(), timestamp)
        self._conn.execute("BEGIN IMMEDIATE")
        self._conn.execute("INSERT INTO heads(tree_size, head) VALUES (?,?)",
                           (head.tree_size, json.dumps(head.as_dict(), sort_keys=True)))
        self._conn.execute("COMMIT")
        return head

    def heads(self) -> List[SignedTreeHead]:
        return [SignedTreeHead.from_dict(json.loads(h))
                for (h,) in self._conn.execute("SELECT head FROM heads ORDER BY seq").fetchall()]

    # ---------------------------------------------------------------- integrity
    def check_integrity(self) -> List[str]:
        """Recompute every leaf hash and the current root from stored leaf bytes."""
        problems: List[str] = []
        acc = merkle.CompactRange()
        for i, data in enumerate(self.iter_entries()):
            h = merkle.leaf_hash(data)
            if h != self._tree.leaf(i):
                problems.append(f"leaf {i}: stored hash does not match stored bytes")
                if len(problems) >= 20:
                    break
            acc.append(h)
        if not problems and acc.root() != self.root():
            problems.append("stored tree nodes do not reproduce the root of the stored leaves")
        for head in self.heads():
            if head.tree_size > self.size or self.root(head.tree_size).hex() != head.root_hash:
                problems.append(f"published head of size {head.tree_size} no longer matches the log")
        return problems

    # ------------------------------------------------------------------ publish
    def export_bundle(self, directory: str | Path, files: Dict[str, Any]) -> Path:
        """Write a publication bundle; ``heads.json`` comes from the stored heads."""
        from ..bundle import write_bundle

        files = dict(files)
        files["heads.json"] = [h.as_dict() for h in self.heads()]
        return write_bundle(directory, files, self.iter_entries())
