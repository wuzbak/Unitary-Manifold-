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

    def __init__(
        self,
        n_shards: int = SHARD_COUNT,
        county_id: Optional[int] = None,
        num_shards: Optional[int] = None,
        use_rust: bool = False,
    ) -> None:
        effective_shards = num_shards if num_shards is not None else n_shards
        self._n_shards = effective_shards
        self.county_id = county_id
        # Respect caller's explicit choice; also try Rust if requested
        rust_available = self.__class__.try_import_rust()
        self._use_rust: bool = use_rust and rust_available
        if self._use_rust and self.__class__._rust_module is not None:
            self._engine = self.__class__._rust_module.ShardedChainRS(effective_shards)
        else:
            self._engine = ShardedChernSimonChain(n_shards=effective_shards)

    @classmethod
    def try_import_rust(cls) -> bool:
        """Attempt to import the compiled PyO3 Rust module.

        Returns
        -------
        bool
            True if ``eige_rust_core`` is importable; False otherwise.
        """
        if cls._rust_available is None:
            try:
                import eige_rust_core  # type: ignore[import]
                cls._rust_module = eige_rust_core
                cls._rust_available = True
            except ImportError:
                cls._rust_module = None
                cls._rust_available = False
        return cls._rust_available  # type: ignore[return-value]

    @property
    def _using_rust(self) -> bool:
        """Backward-compatible alias for ``_use_rust``."""
        return self._use_rust

    @property
    def using_rust(self) -> bool:
        """True if the Rust engine is active; False if using Python fallback."""
        return self._use_rust

    @property
    def state(self) -> int:
        """Current primary hash state integer."""
        return self._engine.primary_digest()

    def update(self, ballot_int: int) -> int:
        """Ingest one ballot.  Routes to Rust or Python transparently.

        Returns
        -------
        int
            Primary hash state after ingesting this ballot.
        """
        self._engine.update(ballot_int)
        return self.state

    def reset(self) -> int:
        """Reset the engine to its initial state.

        Returns
        -------
        int
            Hash state after reset (equals initial state).
        """
        self._engine._primary.reset()
        for shard in self._engine._shards:
            shard.reset()
        return self.state

    def checkpoint_all(self) -> list:
        """Return a list of (shard_index, digest) tuples."""
        return self._engine.checkpoint_all()

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

    def checkpoint_manifests(self) -> list:
        """Return shard manifests as a list (one entry per shard)."""
        if self._use_rust and self.__class__._rust_module is not None:
            from .chern_simon_hash import ShardManifest, ShardEntry
            raw_manifests = self.__class__._rust_module.export_manifests(self._engine)
            manifests = []
            for idx, raw in enumerate(raw_manifests):
                entries = [ShardEntry(**e) for e in raw.get("entries", [])]
                primary_entries = [ShardEntry(**e) for e in raw.get("primary_entries", [])]
                manifests.append(ShardManifest(
                    shard_index=idx,
                    entries=entries,
                    primary_entries=primary_entries,
                    final_state=raw["final_state"],
                    entry_count=raw["entry_count"],
                    primary_final_state=raw["primary_final_state"],
                ))
            return manifests
        return list(self._engine.checkpoint_manifests().values())

    def reconstruct_check(self, available_shard_indices: Optional[list] = None) -> tuple:
        """Delegate reconstruct_check to the underlying engine.

        If ``available_shard_indices`` is omitted, defaults to all shard indices
        (full reconstruction pass).
        """
        if available_shard_indices is None:
            available_shard_indices = list(range(self._n_shards))
        return self._engine.reconstruct_check(available_shard_indices)

    def sha512_hexdigest(self) -> str:
        """Return the SHA-512 hexdigest of the primary chain's current state."""
        return self._engine._primary.sha512_hexdigest()

    def __repr__(self) -> str:
        backend = "Rust" if self._using_rust else "Python"
        return (
            f"RustBallotBridge(backend={backend!r}, "
            f"n_shards={self._n_shards}, "
            f"ballot_count={self.primary_ballot_count()})"
        )
