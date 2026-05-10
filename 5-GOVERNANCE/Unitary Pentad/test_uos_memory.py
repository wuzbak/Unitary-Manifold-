"""
tests/test_uos_memory.py
========================
Unit tests for UOS/memory.py.

Covers:
  - MemoryPage: construction, data shape
  - UnitaryMemory: allocate, free, read, write (CoW), zero_copy_share
  - Capacity limits, error paths
  - defragmentation_index always 0
  - stats dict
"""

import numpy as np
import pytest

import sys, os
_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.abspath(os.path.join(_PENTAD_DIR, "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
if _PENTAD_DIR not in sys.path:
    sys.path.insert(0, _PENTAD_DIR)

from UOS.memory import MemoryPage, UnitaryMemory, DEFAULT_PAGE_SIZE
from UOS.constants import UOS_MEMORY_PAGES, PHI_BACKGROUND


# ---------------------------------------------------------------------------
# MemoryPage
# ---------------------------------------------------------------------------

class TestMemoryPage:
    def test_default_data_shape(self):
        page = MemoryPage(page_id=0, phi_address=0.1,
                          size_bytes=128, owner_pid=1)
        assert page.data.shape == (128,)

    def test_data_zero_initialised(self):
        page = MemoryPage(page_id=1, phi_address=0.2,
                          size_bytes=64, owner_pid=2)
        assert np.all(page.data == 0)

    def test_shared_pids_empty(self):
        page = MemoryPage(page_id=2, phi_address=0.3,
                          size_bytes=32, owner_pid=3)
        assert len(page.shared_pids) == 0


# ---------------------------------------------------------------------------
# UnitaryMemory — construction
# ---------------------------------------------------------------------------

class TestUnitaryMemoryConstruction:
    def test_pages_free_equals_n_pages(self):
        mem = UnitaryMemory(n_pages=100)
        assert mem.pages_free == 100
        assert mem.pages_allocated == 0

    def test_phi_addresses_length(self):
        mem = UnitaryMemory(n_pages=50)
        assert len(mem._free_phi_addresses) == 50

    def test_phi_addresses_in_range(self):
        import math
        mem = UnitaryMemory(n_pages=32)
        max_addr = 2.0 * math.pi * 5  # 2π × WINDING_NUMBER
        for addr in mem._free_phi_addresses:
            assert 0.0 <= addr < max_addr + 1e-9


# ---------------------------------------------------------------------------
# UnitaryMemory — allocate
# ---------------------------------------------------------------------------

class TestAllocate:
    def test_allocate_returns_int(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1)
        assert isinstance(pid, int)

    def test_allocate_reduces_free(self):
        mem = UnitaryMemory(n_pages=8)
        mem.allocate(owner_pid=1)
        assert mem.pages_free == 7

    def test_allocate_increases_allocated(self):
        mem = UnitaryMemory(n_pages=8)
        mem.allocate(owner_pid=1)
        assert mem.pages_allocated == 1

    def test_allocate_custom_size(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=256)
        assert mem._pages[pid].size_bytes == 256

    def test_allocate_zero_size_raises(self):
        mem = UnitaryMemory(n_pages=8)
        with pytest.raises(ValueError):
            mem.allocate(owner_pid=1, size_bytes=0)

    def test_allocate_beyond_capacity_raises(self):
        mem = UnitaryMemory(n_pages=2)
        mem.allocate(owner_pid=1)
        mem.allocate(owner_pid=1)
        with pytest.raises(MemoryError):
            mem.allocate(owner_pid=1)

    def test_allocate_multiple_unique_ids(self):
        mem = UnitaryMemory(n_pages=8)
        ids = [mem.allocate(owner_pid=1) for _ in range(5)]
        assert len(set(ids)) == 5


# ---------------------------------------------------------------------------
# UnitaryMemory — free
# ---------------------------------------------------------------------------

class TestFree:
    def test_free_restores_page_count(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1)
        mem.free(pid)
        assert mem.pages_free == 8
        assert mem.pages_allocated == 0

    def test_free_invalid_raises(self):
        mem = UnitaryMemory(n_pages=8)
        with pytest.raises(KeyError):
            mem.free(999)

    def test_free_then_reallocate(self):
        mem = UnitaryMemory(n_pages=2)
        pid = mem.allocate(owner_pid=1)
        mem.free(pid)
        new_pid = mem.allocate(owner_pid=2)
        assert isinstance(new_pid, int)


# ---------------------------------------------------------------------------
# UnitaryMemory — read
# ---------------------------------------------------------------------------

class TestRead:
    def test_read_returns_zeros_on_fresh_page(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=64)
        data = mem.read(pid)
        assert np.all(data == 0)

    def test_read_correct_shape(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=128)
        data = mem.read(pid)
        assert data.shape == (128,)

    def test_read_is_copy(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=64)
        d1 = mem.read(pid)
        d1[0] = 99
        d2 = mem.read(pid)
        assert d2[0] == 0  # original unmodified

    def test_read_invalid_raises(self):
        mem = UnitaryMemory(n_pages=8)
        with pytest.raises(KeyError):
            mem.read(9999)


# ---------------------------------------------------------------------------
# UnitaryMemory — write
# ---------------------------------------------------------------------------

class TestWrite:
    def test_owner_write_in_place(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=4)
        data = np.array([10, 20, 30, 40], dtype=np.uint8)
        out_pid = mem.write(pid, data, writer_pid=1)
        assert out_pid == pid
        np.testing.assert_array_equal(mem.read(pid), data)

    def test_non_owner_write_raises_permission(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=4)
        with pytest.raises(PermissionError):
            mem.write(pid, np.zeros(4, dtype=np.uint8), writer_pid=99)

    def test_shared_pid_cow(self):
        """A shared (non-owner) writer triggers copy-on-write."""
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=4)
        mem.zero_copy_share(pid, new_pid=2)
        data = np.array([1, 2, 3, 4], dtype=np.uint8)
        new_pid = mem.write(pid, data, writer_pid=2)
        # A NEW page was created for the writer
        assert new_pid != pid
        # Original page is unchanged
        assert np.all(mem.read(pid) == 0)
        # New page has the written data
        np.testing.assert_array_equal(mem.read(new_pid), data)

    def test_write_invalid_page_raises(self):
        mem = UnitaryMemory(n_pages=8)
        with pytest.raises(KeyError):
            mem.write(9999, b"\x00", writer_pid=1)

    def test_write_truncates_to_page_size(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=4)
        mem.write(pid, np.ones(10, dtype=np.uint8), writer_pid=1)
        assert mem.read(pid).shape == (4,)


# ---------------------------------------------------------------------------
# UnitaryMemory — zero_copy_share
# ---------------------------------------------------------------------------

class TestZeroCopyShare:
    def test_share_adds_pid_to_shared(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=16)
        mem.zero_copy_share(pid, new_pid=5)
        assert 5 in mem._pages[pid].shared_pids

    def test_share_invalid_page_raises(self):
        mem = UnitaryMemory(n_pages=8)
        with pytest.raises(KeyError):
            mem.zero_copy_share(9999, new_pid=5)

    def test_share_multiple_pids(self):
        mem = UnitaryMemory(n_pages=8)
        pid = mem.allocate(owner_pid=1, size_bytes=16)
        for new_pid in [2, 3, 4]:
            mem.zero_copy_share(pid, new_pid=new_pid)
        assert {2, 3, 4}.issubset(mem._pages[pid].shared_pids)


# ---------------------------------------------------------------------------
# UnitaryMemory — defragmentation_index
# ---------------------------------------------------------------------------

class TestDefragmentationIndex:
    def test_always_zero_on_fresh(self):
        mem = UnitaryMemory(n_pages=32)
        assert mem.defragmentation_index() == 0.0

    def test_zero_after_alloc_and_free(self):
        mem = UnitaryMemory(n_pages=32)
        ids = [mem.allocate(owner_pid=1) for _ in range(16)]
        for pid in ids[::2]:  # free every other
            mem.free(pid)
        # Pool stays sorted → index should be 0.0
        assert mem.defragmentation_index() == 0.0


# ---------------------------------------------------------------------------
# UnitaryMemory — stats
# ---------------------------------------------------------------------------

class TestStats:
    def test_stats_keys(self):
        mem = UnitaryMemory(n_pages=16)
        s = mem.stats()
        assert "total_pages" in s
        assert "allocated_pages" in s
        assert "free_pages" in s
        assert "utilisation" in s
        assert "defragmentation_index" in s

    def test_utilisation_zero_on_empty(self):
        mem = UnitaryMemory(n_pages=16)
        assert mem.stats()["utilisation"] == 0.0

    def test_utilisation_one_after_full(self):
        mem = UnitaryMemory(n_pages=4)
        for _ in range(4):
            mem.allocate(owner_pid=1)
        assert abs(mem.stats()["utilisation"] - 1.0) < 1e-9
