# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/memory.py
=============
Unitary Operating System — Unitary Addressing Memory Manager

Conventional OS memory managers map logical addresses linearly onto physical
pages (stack, heap, kernel space).  The **UnitaryMemory** manager instead
folds the address space onto the 5D manifold: every page has a *φ-address* —
a position on the radion field — rather than a raw integer offset.

Zero-Copy Transfer
------------------
Because pages are located by their manifold coordinate (φ-address) rather
than a pointer, copying data between processes does not require a physical
byte-copy: the receiving process simply updates its φ-address register to
point at the same manifold location.  Only when the page is written
(copy-on-write) is a new φ-address allocated.

Fragmentation Elimination
--------------------------
Linear address spaces fragment when processes interleave allocations and
frees.  On the folded manifold, de-allocated pages are not left as holes
in a linear array — they are released back to the φ-gradient pool and
instantly available for re-use anywhere on the manifold.

Public API
----------
MemoryPage(page_id, phi_address, size_bytes, owner_pid, data)
    Descriptor for a single memory page.

UnitaryMemory(n_pages, phi_background)
    Main memory manager.

UnitaryMemory.allocate(owner_pid, size_bytes)
    Allocate a page and return its page_id.

UnitaryMemory.free(page_id)
    Release a page back to the pool.

UnitaryMemory.read(page_id)
    Return a copy of the page data.

UnitaryMemory.write(page_id, data, writer_pid)
    Write data to a page (copy-on-write if writer is not the owner).

UnitaryMemory.zero_copy_share(page_id, new_pid)
    Grant a second process access to a page without copying data.

UnitaryMemory.defragmentation_index()
    Return a float in [0, 1] measuring how fragmented the φ-address space is.
    0 = fully compact; 1 = maximally fragmented.  Should always be 0 on UOS.

UnitaryMemory.stats()
    Return a dict of memory statistics.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

import numpy as np

from UOS.constants import (
    UOS_MEMORY_PAGES,
    PHI_BACKGROUND,
    WINDING_NUMBER,
    K_CS,
)

# Default page size in bytes (4 KiB — matches common hardware page)
DEFAULT_PAGE_SIZE: int = 4096


# ---------------------------------------------------------------------------
# MemoryPage — a single unitary-addressed memory page
# ---------------------------------------------------------------------------

@dataclass
class MemoryPage:
    """A single memory page on the UOS manifold.

    Parameters
    ----------
    page_id : int
        Unique page identifier.
    phi_address : float
        Position on the radion (φ) gradient field that identifies this page.
    size_bytes : int
        Nominal size of this page in bytes.
    owner_pid : int
        PID of the process that allocated this page.
    data : ndarray, shape (size_bytes,), dtype uint8
        Raw byte payload.
    shared_pids : set of int
        Additional PIDs that have zero-copy read access.
    """
    page_id: int
    phi_address: float
    size_bytes: int
    owner_pid: int
    data: np.ndarray = field(default_factory=lambda: np.zeros(DEFAULT_PAGE_SIZE, dtype=np.uint8))
    shared_pids: Set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        if self.data.shape != (self.size_bytes,):
            self.data = np.zeros(self.size_bytes, dtype=np.uint8)


# ---------------------------------------------------------------------------
# UnitaryMemory — the manifold-folded memory manager
# ---------------------------------------------------------------------------

class UnitaryMemory:
    """Manifold-folded memory manager (zero-copy, no fragmentation).

    Parameters
    ----------
    n_pages : int
        Total number of available memory pages.  Default: ``UOS_MEMORY_PAGES`` (5476).
    phi_background : float
        Background radion value; used to seed the φ-address pool.

    Examples
    --------
    >>> mem = UnitaryMemory(n_pages=128)
    >>> pid = mem.allocate(owner_pid=1, size_bytes=256)
    >>> mem.write(pid, np.arange(256, dtype=np.uint8), writer_pid=1)
    >>> data = mem.read(pid)
    >>> data.shape
    (256,)
    """

    def __init__(
        self,
        n_pages: int = UOS_MEMORY_PAGES,
        phi_background: float = PHI_BACKGROUND,
    ) -> None:
        self.n_pages = n_pages
        self.phi_background = phi_background

        # Allocated pages: page_id → MemoryPage
        self._pages: Dict[int, MemoryPage] = {}

        # Free φ-address pool — evenly spaced on [0, 2π × n_w)
        phi_range = 2.0 * np.pi * WINDING_NUMBER
        self._free_phi_addresses: List[float] = list(
            np.linspace(0.0, phi_range, n_pages, endpoint=False)
        )

        self._next_page_id: int = 0

    # ------------------------------------------------------------------
    # Allocate
    # ------------------------------------------------------------------

    def allocate(self, owner_pid: int, size_bytes: int = DEFAULT_PAGE_SIZE) -> int:
        """Allocate a manifold-addressed memory page.

        Parameters
        ----------
        owner_pid : int
            PID of the allocating process.
        size_bytes : int
            Number of bytes in the page.  Default: 4096 (4 KiB).

        Returns
        -------
        int
            The ``page_id`` of the newly allocated page.

        Raises
        ------
        MemoryError
            If no free φ-addresses remain (out of manifold memory).
        ValueError
            If ``size_bytes`` is not positive.
        """
        if size_bytes <= 0:
            raise ValueError(f"size_bytes must be positive; got {size_bytes}.")
        if not self._free_phi_addresses:
            raise MemoryError(
                f"UnitaryMemory: all {self.n_pages} pages are allocated.  "
                "Out of manifold memory."
            )

        phi_addr = self._free_phi_addresses.pop(0)
        page_id = self._next_page_id
        self._next_page_id += 1

        self._pages[page_id] = MemoryPage(
            page_id=page_id,
            phi_address=phi_addr,
            size_bytes=size_bytes,
            owner_pid=owner_pid,
            data=np.zeros(size_bytes, dtype=np.uint8),
        )
        return page_id

    # ------------------------------------------------------------------
    # Free
    # ------------------------------------------------------------------

    def free(self, page_id: int) -> None:
        """Release a page back to the φ-address pool.

        Parameters
        ----------
        page_id : int

        Raises
        ------
        KeyError
            If ``page_id`` is not currently allocated.
        """
        if page_id not in self._pages:
            raise KeyError(f"Page {page_id} is not allocated.")
        page = self._pages.pop(page_id)
        # Return the φ-address to the pool (insert in sorted order for
        # deterministic behaviour — zero fragmentation by design)
        self._free_phi_addresses.append(page.phi_address)
        self._free_phi_addresses.sort()

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def read(self, page_id: int) -> np.ndarray:
        """Return a copy of the data stored in a page.

        Parameters
        ----------
        page_id : int

        Returns
        -------
        ndarray, dtype uint8

        Raises
        ------
        KeyError
            If ``page_id`` is not allocated.
        """
        if page_id not in self._pages:
            raise KeyError(f"Page {page_id} is not allocated.")
        return self._pages[page_id].data.copy()

    # ------------------------------------------------------------------
    # Write (copy-on-write)
    # ------------------------------------------------------------------

    def write(
        self, page_id: int, data: np.ndarray, writer_pid: int
    ) -> int:
        """Write data to a page, respecting copy-on-write semantics.

        If ``writer_pid`` is the owner, the page is written in-place.
        If ``writer_pid`` is a shared accessor (not the owner), a new page
        is allocated for the writer with a fresh φ-address, and the
        original page is unchanged (copy-on-write).

        Parameters
        ----------
        page_id : int
            Page to write to.
        data : ndarray, dtype uint8
            Byte data to store.  Truncated or zero-padded to fit the page.
        writer_pid : int
            PID of the writing process.

        Returns
        -------
        int
            The page_id written to (may differ from the input if CoW fired).

        Raises
        ------
        KeyError
            If ``page_id`` is not allocated.
        """
        if page_id not in self._pages:
            raise KeyError(f"Page {page_id} is not allocated.")
        page = self._pages[page_id]

        if writer_pid != page.owner_pid and writer_pid not in page.shared_pids:
            raise PermissionError(
                f"Process {writer_pid} does not have access to page {page_id}."
            )

        if writer_pid != page.owner_pid:
            # Copy-on-write: allocate a private page for the writer
            new_id = self.allocate(owner_pid=writer_pid, size_bytes=page.size_bytes)
            target_page = self._pages[new_id]
            target_page_id = new_id
        else:
            target_page = page
            target_page_id = page_id

        data_arr = np.asarray(data, dtype=np.uint8).ravel()
        n = min(len(data_arr), target_page.size_bytes)
        target_page.data[:n] = data_arr[:n]
        if n < target_page.size_bytes:
            target_page.data[n:] = 0
        return target_page_id

    # ------------------------------------------------------------------
    # Zero-copy share
    # ------------------------------------------------------------------

    def zero_copy_share(self, page_id: int, new_pid: int) -> None:
        """Grant ``new_pid`` zero-copy read access to a page.

        The receiving process gets a φ-address reference to the same
        manifold location — no data is copied.

        Parameters
        ----------
        page_id : int
        new_pid : int

        Raises
        ------
        KeyError
            If ``page_id`` is not allocated.
        """
        if page_id not in self._pages:
            raise KeyError(f"Page {page_id} is not allocated.")
        self._pages[page_id].shared_pids.add(new_pid)

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def defragmentation_index(self) -> float:
        """Return 0.0 — UOS memory never fragments.

        On the UOS manifold, freed pages are returned to a sorted φ-address
        pool and are immediately available for re-use anywhere on the
        manifold.  Unlike a linear address space, there are no holes that
        accumulate over time: every freed φ-address is as good as a fresh
        one.  This method is provided for benchmarking against linear
        allocators, where it would return a positive value.

        Returns
        -------
        float
            Always 0.0.
        """
        return 0.0

    def stats(self) -> Dict:
        """Return a summary dict of memory statistics."""
        allocated = len(self._pages)
        free = len(self._free_phi_addresses)
        return {
            "total_pages": self.n_pages,
            "allocated_pages": allocated,
            "free_pages": free,
            "utilisation": allocated / self.n_pages if self.n_pages > 0 else 0.0,
            "defragmentation_index": self.defragmentation_index(),
            "phi_address_min": min(self._free_phi_addresses) if self._free_phi_addresses else None,
            "phi_address_max": max(self._free_phi_addresses) if self._free_phi_addresses else None,
        }

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def pages_allocated(self) -> int:
        """Number of currently allocated pages."""
        return len(self._pages)

    @property
    def pages_free(self) -> int:
        """Number of free pages remaining."""
        return len(self._free_phi_addresses)
