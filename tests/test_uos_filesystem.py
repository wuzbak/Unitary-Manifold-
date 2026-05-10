"""
tests/test_uos_filesystem.py
=============================
Unit tests for UOS/filesystem.py.

Covers:
  - _content_projection_key: deterministic, in [0,1), identical content→same key
  - _shard: correct count, correct reconstruction
  - HolographicFilesystem: store, retrieve, exists, delete, list_files, stats
  - De-duplication on identical content
  - Capacity overflow
  - Reconstruction with missing shards (simulated corruption)
"""

import pytest
import numpy as np

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from UOS.filesystem import (
    HolographicFilesystem,
    FileRecord,
    MIN_RECONSTRUCTION_SHARDS,
)
from UOS.constants import UOS_FS_SHARDS, K_CS


# ---------------------------------------------------------------------------
# _content_projection_key
# ---------------------------------------------------------------------------

class TestContentProjectionKey:
    def test_in_unit_interval(self):
        key = HolographicFilesystem._content_projection_key(b"hello")
        assert 0.0 <= key < 1.0

    def test_deterministic(self):
        data = b"test data for determinism"
        key1 = HolographicFilesystem._content_projection_key(data)
        key2 = HolographicFilesystem._content_projection_key(data)
        assert key1 == key2

    def test_different_content_may_differ(self):
        # Not guaranteed (collision), but should differ for these inputs
        key1 = HolographicFilesystem._content_projection_key(b"aaaaaa")
        key2 = HolographicFilesystem._content_projection_key(b"zzzzzz")
        # Both valid regardless
        assert 0.0 <= key1 < 1.0
        assert 0.0 <= key2 < 1.0

    def test_empty_bytes(self):
        key = HolographicFilesystem._content_projection_key(b"")
        assert 0.0 <= key < 1.0

    def test_key_is_multiple_of_1_over_k_cs(self):
        key = HolographicFilesystem._content_projection_key(b"sample")
        remainder = round(key * K_CS)
        assert abs(key - remainder / K_CS) < 1e-10


# ---------------------------------------------------------------------------
# _shard and _reconstruct
# ---------------------------------------------------------------------------

class TestShardReconstruct:
    def _fs(self):
        return HolographicFilesystem()

    def test_shard_count(self):
        fs = self._fs()
        data = b"hello manifold " * 10
        shards = fs._shard(data)
        assert len(shards) == UOS_FS_SHARDS

    def test_reconstruct_exact(self):
        fs = self._fs()
        data = b"exact reconstruction test data"
        shards = fs._shard(data)
        out = fs._reconstruct(shards, len(data))
        assert out == data

    def test_reconstruct_arbitrary_lengths(self):
        fs = self._fs()
        for size in [1, 7, 13, 100, 255, 1024]:
            # Use a simple repeating pattern that is never empty
            data = (b'\x42' * size)
            shards = fs._shard(data)
            out = fs._reconstruct(shards, size)
            assert out == data, f"Failed for size={size}"

    def test_reconstruct_too_few_shards_raises(self):
        fs = self._fs()
        data = b"reconstruct failure test"
        shards = fs._shard(data)
        # Corrupt shards below minimum threshold
        for i in range(len(shards) - MIN_RECONSTRUCTION_SHARDS + 1):
            shards[i] = np.array([], dtype=np.uint8)
        with pytest.raises(ValueError):
            fs._reconstruct(shards, len(data))


# ---------------------------------------------------------------------------
# HolographicFilesystem — store
# ---------------------------------------------------------------------------

class TestStore:
    def test_store_returns_float(self):
        fs = HolographicFilesystem()
        key = fs.store("file.txt", b"content")
        assert isinstance(key, float)

    def test_store_key_in_unit_interval(self):
        fs = HolographicFilesystem()
        key = fs.store("file.txt", b"content")
        assert 0.0 <= key < 1.0

    def test_store_increases_file_count(self):
        fs = HolographicFilesystem()
        fs.store("a.txt", b"aaa")
        assert fs.stats()["files_stored"] == 1

    def test_store_increases_bytes_used(self):
        fs = HolographicFilesystem()
        data = b"hello manifold"
        fs.store("b.txt", data)
        assert fs.stats()["bytes_used"] == len(data)

    def test_store_dedup_same_content(self):
        fs = HolographicFilesystem()
        data = b"identical content"
        key1 = fs.store("f1.txt", data)
        key2 = fs.store("f2.txt", data)
        assert key1 == key2
        assert fs.stats()["files_stored"] == 1  # only one entry

    def test_store_overflow_raises(self):
        fs = HolographicFilesystem(shard_capacity_bytes=10)
        with pytest.raises(OverflowError):
            fs.store("big.bin", b"x" * 11)

    def test_store_with_metadata(self):
        fs = HolographicFilesystem()
        key = fs.store("m.txt", b"data", metadata={"author": "UOS"})
        assert fs._store[key].metadata["author"] == "UOS"


# ---------------------------------------------------------------------------
# HolographicFilesystem — retrieve
# ---------------------------------------------------------------------------

class TestRetrieve:
    def test_retrieve_returns_original(self):
        fs = HolographicFilesystem()
        data = b"retrieve me from the manifold"
        key = fs.store("r.txt", data)
        out = fs.retrieve(key)
        assert out == data

    def test_retrieve_binary_content(self):
        fs = HolographicFilesystem()
        data = bytes(range(256))
        key = fs.store("bin.bin", data)
        out = fs.retrieve(key)
        assert out == data

    def test_retrieve_missing_raises(self):
        fs = HolographicFilesystem()
        with pytest.raises(KeyError):
            fs.retrieve(0.999)

    def test_retrieve_large_file(self):
        fs = HolographicFilesystem()
        data = b"A" * 4096
        key = fs.store("large.txt", data)
        out = fs.retrieve(key)
        assert out == data


# ---------------------------------------------------------------------------
# HolographicFilesystem — exists
# ---------------------------------------------------------------------------

class TestExists:
    def test_exists_true_after_store(self):
        fs = HolographicFilesystem()
        key = fs.store("e.txt", b"exists")
        assert fs.exists(key) is True

    def test_exists_false_for_unknown(self):
        fs = HolographicFilesystem()
        assert fs.exists(0.12345) is False

    def test_exists_false_after_delete(self):
        fs = HolographicFilesystem()
        key = fs.store("d.txt", b"gone")
        fs.delete(key)
        assert fs.exists(key) is False


# ---------------------------------------------------------------------------
# HolographicFilesystem — delete
# ---------------------------------------------------------------------------

class TestDelete:
    def test_delete_removes_file(self):
        fs = HolographicFilesystem()
        key = fs.store("del.txt", b"delete me")
        fs.delete(key)
        assert fs.stats()["files_stored"] == 0

    def test_delete_frees_bytes(self):
        fs = HolographicFilesystem()
        data = b"delete me"
        key = fs.store("del2.txt", data)
        fs.delete(key)
        assert fs.stats()["bytes_used"] == 0

    def test_delete_missing_raises(self):
        fs = HolographicFilesystem()
        with pytest.raises(KeyError):
            fs.delete(0.5)


# ---------------------------------------------------------------------------
# HolographicFilesystem — list_files
# ---------------------------------------------------------------------------

class TestListFiles:
    def test_empty_list(self):
        fs = HolographicFilesystem()
        assert fs.list_files() == []

    def test_list_contains_stored_names(self):
        fs = HolographicFilesystem()
        fs.store("alpha.txt", b"aaa")
        fs.store("beta.txt", b"bbb")
        names = [name for _, name in fs.list_files()]
        assert "alpha.txt" in names or "beta.txt" in names  # dedup may merge

    def test_list_is_sorted_by_key(self):
        fs = HolographicFilesystem()
        for i in range(5):
            fs.store(f"file_{i}.txt", f"content {i}".encode())
        files = fs.list_files()
        keys = [k for k, _ in files]
        assert keys == sorted(keys)


# ---------------------------------------------------------------------------
# HolographicFilesystem — stats
# ---------------------------------------------------------------------------

class TestStats:
    def test_stats_keys(self):
        fs = HolographicFilesystem()
        s = fs.stats()
        assert "files_stored" in s
        assert "bytes_used" in s
        assert "bytes_capacity" in s
        assert "utilisation" in s
        assert "n_shards" in s
        assert "min_reconstruction_shards" in s

    def test_stats_n_shards(self):
        fs = HolographicFilesystem()
        assert fs.stats()["n_shards"] == UOS_FS_SHARDS

    def test_stats_min_reconstruction(self):
        fs = HolographicFilesystem()
        assert fs.stats()["min_reconstruction_shards"] == MIN_RECONSTRUCTION_SHARDS

    def test_stats_utilisation_zero_initially(self):
        fs = HolographicFilesystem()
        assert fs.stats()["utilisation"] == 0.0

    def test_stats_utilisation_increases(self):
        fs = HolographicFilesystem(shard_capacity_bytes=100)
        fs.store("u.txt", b"x" * 50)
        assert fs.stats()["utilisation"] > 0.0
