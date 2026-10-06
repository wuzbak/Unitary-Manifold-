# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Exact duplicate detection over arbitrarily many identifiers in bounded memory.

Identifiers are kept in an in-memory set until ``memory_limit`` distinct values
have been seen.  After that every identifier is spilled to one of 256 bucket
files on disk, chosen by the first byte of its SHA-256.  At the end each bucket
is counted on its own, so peak memory is about ``memory_limit`` identifiers or
1/256 of the total, whichever is larger.  The result is exact: there are no
probabilistic structures and no hash-collision false positives, because the
identifiers themselves (not digests) are compared.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import tempfile
from collections import Counter
from contextlib import ExitStack
from pathlib import Path
from typing import Dict, List, Optional

_BUCKETS = 256


class DuplicateDetector:
    def __init__(self, memory_limit: int = 2_000_000, tmpdir: Optional[str] = None) -> None:
        if memory_limit < 1:
            raise ValueError("memory_limit must be positive")
        self.memory_limit = memory_limit
        self._tmp_parent = tmpdir
        self._seen: set = set()
        self._dups: Counter = Counter()
        self._dir: Optional[Path] = None
        self._files: List = []
        self.count = 0

    @property
    def spilled(self) -> bool:
        return self._dir is not None

    def _bucket(self, key: str) -> int:
        return hashlib.sha256(key.encode("utf-8")).digest()[0]

    def _spill(self) -> None:
        self._dir = Path(tempfile.mkdtemp(prefix="eige-dedup-", dir=self._tmp_parent))
        files: List = []
        with ExitStack() as stack:  # if any bucket fails to open, the ones already open are closed
            for i in range(_BUCKETS):
                files.append(stack.enter_context(
                    open(self._dir / f"{i:02x}.jsonl", "a", encoding="utf-8", buffering=1 << 16)))
            stack.pop_all()  # all open: ownership passes to this detector, released by close()
        self._files = files
        for key in self._seen:
            self._write(key)
        for key, extra in self._dups.items():
            for _ in range(extra):
                self._write(key)
        self._seen = set()
        self._dups = Counter()

    def _write(self, key: str) -> None:
        self._files[self._bucket(key)].write(json.dumps(key, ensure_ascii=False) + "\n")

    def add(self, key: str) -> None:
        self.count += 1
        if self._dir is not None:
            self._write(key)
            return
        if key in self._seen:
            self._dups[key] += 1
            return
        self._seen.add(key)
        if len(self._seen) > self.memory_limit:
            self._spill()

    def duplicates(self) -> Dict[str, int]:
        """Return ``{identifier: occurrences}`` for every identifier seen more than once."""
        if self._dir is None:
            return {k: n + 1 for k, n in self._dups.items()}
        out: Dict[str, int] = {}
        for i, fh in enumerate(self._files):
            fh.flush()
            with open(self._dir / f"{i:02x}.jsonl", encoding="utf-8") as rd:
                c = Counter(json.loads(line) for line in rd)
            out.update({k: n for k, n in c.items() if n > 1})
        return out

    def close(self) -> None:
        for fh in self._files:
            fh.close()
        self._files = []
        if self._dir is not None:
            shutil.rmtree(self._dir, ignore_errors=True)

    def __enter__(self) -> "DuplicateDetector":
        return self

    def __exit__(self, *exc) -> None:
        self.close()
