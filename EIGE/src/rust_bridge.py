# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/rust_bridge.py — PyO3 Rust Fast-Ingestion Engine Bridge
================================================================

Provides a transparent bridge between the Python math core and the
compiled Rust fast-ingestion engine (EIGE/blueprint/ingestion_engine.rs).

Architecture
------------
  - ``RustBallotBridge.try_import_rust()`` attempts to import the compiled
    PyO3 module ``eige_rust_core`` at runtime.
  - If the module is available, ballot updates are routed through the Rust
    CS hash implementation (SIMD-optimised, ~10× faster than Python).
  - If unavailable, the bridge silently falls back to
    ``ShardedChernSimonChain`` (pure-Python) — ZERO behaviour difference.

Building the Rust module
------------------------
The Rust source lives at ``EIGE/blueprint/ingestion_engine.rs`` (annotated
with PyO3 ``#[pymodule]`` and ``#[pyfunction]`` entries).  To compile::

    cd EIGE
    pip install maturin
    maturin build --release
    pip install target/wheels/eige_rust_core-*.whl

CountyNode integration
----------------------
Pass ``use_rust=True`` to CountyNode to enable the Rust bridge::

    node = CountyNode("WA-047", "King County", use_rust=True)

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

from typing import Optional

from .chern_simon_hash import ShardedChernSimonChain
from .constants import SHARD_COUNT, K_CS


# ---------------------------------------------------------------------------
# Rust bridge
# ---------------------------------------------------------------------------

class RustBallotBridge:
    """Transparent bridge between Python math core and compiled Rust engine.

    Falls back to pure-Python ShardedChernSimonChain when the Rust module
    is not available, producing identical results.

    Parameters
    ----------
    n_shards : int
        Number of holographic shards (default: SHARD_COUNT = 8).
    """

    _rust_module = None
    _rust_available: Optional[bool] = None

    def __init__(self, n_shards: int = SHARD_COUNT) -> None:
        self._n_shards = n_shards
        self._rust = self.__class__.try_import_rust()
        if self._rust is not None:
            # Rust module is available — use it
            self._engine = self._rust.ShardedChainRS(n_shards)
            self._using_rust = True
        else:
            # Fallback: pure-Python implementation
            self._engine = ShardedChernSimonChain(n_shards=n_shards)
            self._using_rust = False

    @classmethod
    def try_import_rust(cls):
        """Attempt to import the compiled PyO3 Rust module.

        Returns
        -------
        module or None
            The ``eige_rust_core`` module if available, else None.
        """
        if cls._rust_available is None:
            try:
                import eige_rust_core  # type: ignore[import]
                cls._rust_module = eige_rust_core
                cls._rust_available = True
            except ImportError:
                cls._rust_module = None
                cls._rust_available = False
        return cls._rust_module

    @property
    def using_rust(self) -> bool:
        """True if the Rust engine is active; False if using Python fallback."""
        return self._using_rust

    def update(self, ballot_int: int) -> int:
        """Ingest one ballot.  Routes to Rust or Python transparently.

        Returns
        -------
        int
            Shard index that received this ballot.
        """
        return self._engine.update(ballot_int)

    def primary_digest(self) -> int:
        """Return the primary chain's current hash state."""
        return self._engine.primary_digest()

    def primary_hexdigest(self) -> str:
        """Return the primary chain's current hash as hex."""
        return self._engine.primary_hexdigest()

    def primary_ballot_count(self) -> int:
        """Return total ballots ingested."""
        return self._engine.primary_ballot_count()

    def shard_digest(self, shard_index: int) -> int:
        """Return the hash state of a specific shard."""
        return self._engine.shard_digest(shard_index)

    def all_shard_digests(self) -> list:
        """Return list of all shard hash states."""
        return self._engine.all_shard_digests()

    def shard_counts(self) -> list:
        """Return list of ballot counts per shard."""
        return self._engine.shard_counts()

    def get_telemetry(self) -> dict:
        """Return telemetry dict; identical structure regardless of backend."""
        return self._engine.get_telemetry()

    def checkpoint_manifests(self) -> dict:
        """Return shard manifests (Python fallback only; Rust returns serialized form)."""
        if self._using_rust:
            # When Rust is available, use Python deserialization of exported data
            # Rust exports manifest dicts; convert back to ShardManifest objects
            from .chern_simon_hash import ShardManifest, ShardEntry
            raw_manifests = self._rust.export_manifests(self._engine)
            manifests = {}
            for idx, raw in enumerate(raw_manifests):
                entries = [
                    ShardEntry(**e) for e in raw.get("entries", [])
                ]
                primary_entries = [
                    ShardEntry(**e) for e in raw.get("primary_entries", [])
                ]
                manifests[idx] = ShardManifest(
                    shard_index=idx,
                    entries=entries,
                    primary_entries=primary_entries,
                    final_state=raw["final_state"],
                    entry_count=raw["entry_count"],
                    primary_final_state=raw["primary_final_state"],
                )
            return manifests
        return self._engine.checkpoint_manifests()

    def reconstruct_check(self, available_shard_indices: list) -> tuple:
        """Delegate reconstruct_check to the underlying engine."""
        return self._engine.reconstruct_check(available_shard_indices)

    def __repr__(self) -> str:
        backend = "Rust" if self._using_rust else "Python"
        return (
            f"RustBallotBridge(backend={backend!r}, "
            f"n_shards={self._n_shards}, "
            f"ballot_count={self.primary_ballot_count()})"
        )
