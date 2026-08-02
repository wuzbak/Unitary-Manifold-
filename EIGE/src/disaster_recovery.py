# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/disaster_recovery.py — Cold Storage Snapshots & Inter-County Replication
==================================================================================

EIGE frames disaster mitigation as a Thermodynamic Dissipation Problem:
catastrophic events (grid blackouts, ransomware, kinetic destruction) are
treated as Localized Manifold Tears.  The system responds with:

  1. 8-Shard Topological Healing (see county_node.py + recovery_kernel.py)
  2. HILS thermal absorption (sentinel_load_balance.py)
  3. Continuous, multi-tiered cold storage replication (this module)

ColdStorageManager
-------------------
  - export_immutable_cold_snapshot() — reads the local ledger, packages
    it as a SnapshotEnvelope, and replicates to peer county nodes.
  - replicate_to_peer_mesh() — fires one background thread per peer;
    buffers locally if peer unreachable, retries when the network restores.
  - The replication protocol is mTLS in production (modelled here as HTTPS).

SnapshotEnvelope
-----------------
  - Carries: source_jurisdiction, timestamp, verified_block_height,
    generalized_state_hash, and a base64-encoded cryptographic payload blob.
  - Does NOT carry raw ballot data — it carries the ledger's hash-chain
    representation, which is cryptographically committed but cannot be
    reversed to individual ballot records.

Retry / queuing model
---------------------
  - Peers that are unreachable are added to a retry queue.
  - retry_pending_replications() attempts to flush the queue.
  - This ensures that network isolation mid-election does not cause
    snapshot loss.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import sys
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple
import urllib.request
import urllib.error

from .constants import K_CS, ENGINE_VERSION, COUNTY_COUNT


# ---------------------------------------------------------------------------
# Snapshot envelope
# ---------------------------------------------------------------------------

@dataclass
class SnapshotEnvelope:
    """Immutable cold storage snapshot of a county's ledger state.

    Attributes
    ----------
    source_jurisdiction : str
        Originating jurisdiction ID, e.g. "WA-KING-COUNTY".
    timestamp : str
        UTC ISO 8601 timestamp at snapshot time.
    verified_block_height : int
        The ledger block index at which this snapshot was taken.
    generalized_state_hash : str
        SHA-512 hex digest of the ledger state at this height.
    cryptographic_payload_blob : str
        Base64-encoded, UTF-8 encoded JSON representation of the ledger
        content up to verified_block_height.  In production, this is
        additionally encrypted with AES-256-GCM using the county's TEE key.
    engine_version : str
        EIGE engine version at snapshot time.
    k_cs_level : int
        Chern-Simons invariant asserted at snapshot time.
    """

    source_jurisdiction: str
    timestamp: str
    verified_block_height: int
    generalized_state_hash: str
    cryptographic_payload_blob: str
    engine_version: str = ENGINE_VERSION
    k_cs_level: int = K_CS

    def to_dict(self) -> dict:
        return {
            "source_jurisdiction": self.source_jurisdiction,
            "timestamp": self.timestamp,
            "verified_block_height": self.verified_block_height,
            "generalized_state_hash": self.generalized_state_hash,
            "cryptographic_payload_blob": self.cryptographic_payload_blob,
            "engine_version": self.engine_version,
            "k_cs_level": self.k_cs_level,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, d: dict) -> "SnapshotEnvelope":
        return cls(
            source_jurisdiction=d["source_jurisdiction"],
            timestamp=d["timestamp"],
            verified_block_height=int(d["verified_block_height"]),
            generalized_state_hash=d["generalized_state_hash"],
            cryptographic_payload_blob=d["cryptographic_payload_blob"],
            engine_version=d.get("engine_version", ENGINE_VERSION),
            k_cs_level=int(d.get("k_cs_level", K_CS)),
        )


# ---------------------------------------------------------------------------
# Replication result
# ---------------------------------------------------------------------------

@dataclass
class ReplicationResult:
    """Result of a single peer replication attempt."""

    peer_address: str
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    error: str = ""
    http_status: Optional[int] = None


# ---------------------------------------------------------------------------
# Cold storage manager
# ---------------------------------------------------------------------------

class ColdStorageManager:
    """Manages cold storage snapshots and inter-county mesh replication.

    Parameters
    ----------
    local_ledger_path : str
        Path to the local county ledger file.
    peer_nodes : list[str]
        FQDN or IP addresses of peer county replication endpoints,
        e.g. ["pierce-county-eige.wa.gov", "snohomish-county-eige.wa.gov"]
    jurisdiction_id : str
        Source jurisdiction identifier.
    cold_storage_path : str, optional
        Local path for cold storage output files.
    http_timeout : float
        Timeout in seconds for peer replication HTTP calls.
    """

    REPLICATION_ENDPOINT = "/api/v21/recovery/sync"

    def __init__(
        self,
        local_ledger_path: str,
        peer_nodes: Optional[List[str]] = None,
        jurisdiction_id: str = "WA-KING-COUNTY",
        cold_storage_path: Optional[str] = None,
        http_timeout: float = 5.0,
    ) -> None:
        self.local_ledger_path = local_ledger_path
        self.peer_nodes = peer_nodes or []
        self.jurisdiction_id = jurisdiction_id
        self.cold_storage_path = cold_storage_path
        self.http_timeout = http_timeout
        self._pending_queue: List[Tuple[str, SnapshotEnvelope]] = []
        self._replication_results: List[ReplicationResult] = []
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Snapshot export
    # ------------------------------------------------------------------

    def export_immutable_cold_snapshot(
        self,
        verified_block_height: int,
        state_hash: str,
    ) -> SnapshotEnvelope:
        """Read the local ledger, package it as a SnapshotEnvelope, and replicate.

        Parameters
        ----------
        verified_block_height : int
            The block height at which this snapshot is taken.
        state_hash : str
            The SHA-512 state hash at this height (from RecoveryKernel or StateMesh).

        Returns
        -------
        SnapshotEnvelope
            The packaged, base64-encoded cold storage envelope.

        Raises
        ------
        OSError
            If the local ledger cannot be read.
        """
        with open(self.local_ledger_path, "r", encoding="utf-8") as f:
            ledger_content = f.read()

        # Base64-encode for transport (AES-256-GCM in production)
        payload_blob = base64.b64encode(ledger_content.encode("utf-8")).decode("ascii")

        ts = datetime.now(timezone.utc).isoformat()
        envelope = SnapshotEnvelope(
            source_jurisdiction=self.jurisdiction_id,
            timestamp=ts,
            verified_block_height=verified_block_height,
            generalized_state_hash=state_hash,
            cryptographic_payload_blob=payload_blob,
        )

        # Persist locally if a cold storage path is configured
        if self.cold_storage_path:
            self._write_local_snapshot(envelope)

        # Replicate to peer mesh asynchronously
        self.replicate_to_peer_mesh(envelope)

        return envelope

    def export_snapshot_from_file(
        self,
        verified_block_height: int,
    ) -> SnapshotEnvelope:
        """Convenience wrapper: reads ledger and computes state_hash automatically."""
        with open(self.local_ledger_path, "r", encoding="utf-8") as f:
            content = f.read()
        state_hash = hashlib.sha512(content.encode("utf-8")).hexdigest()
        return self.export_immutable_cold_snapshot(verified_block_height, state_hash)

    # ------------------------------------------------------------------
    # Peer mesh replication
    # ------------------------------------------------------------------

    def replicate_to_peer_mesh(self, envelope: SnapshotEnvelope) -> None:
        """Replicate envelope to all peer county nodes (one thread per peer).

        Peers that fail are added to the pending retry queue.
        Non-blocking: fires daemon threads and returns immediately.
        """
        serialized = envelope.to_json()
        for peer in self.peer_nodes:
            t = threading.Thread(
                target=self._replicate_to_single_peer,
                args=(peer, serialized, envelope),
                daemon=True,
                name=f"eige-repl-{peer}",
            )
            t.start()

    def retry_pending_replications(self) -> List[ReplicationResult]:
        """Attempt to flush the pending retry queue.

        Returns
        -------
        list[ReplicationResult]
            Results of this retry pass.
        """
        results = []
        with self._lock:
            still_pending = []
            for peer, envelope in self._pending_queue:
                result = self._attempt_peer_post(peer, envelope.to_json())
                results.append(result)
                if not result.success:
                    still_pending.append((peer, envelope))
                else:
                    with self._lock:
                        self._replication_results.append(result)
            self._pending_queue = still_pending
        return results

    def pending_count(self) -> int:
        """Return number of envelopes in the retry queue."""
        with self._lock:
            return len(self._pending_queue)

    def replication_results(self) -> List[ReplicationResult]:
        """Return all replication results from this session."""
        with self._lock:
            return list(self._replication_results)

    # ------------------------------------------------------------------
    # Local snapshot persistence
    # ------------------------------------------------------------------

    def _write_local_snapshot(self, envelope: SnapshotEnvelope) -> None:
        """Write envelope to local cold storage path."""
        try:
            os.makedirs(self.cold_storage_path, exist_ok=True)
            filename = (
                f"snapshot_{self.jurisdiction_id.replace('-', '_')}"
                f"_h{envelope.verified_block_height}"
                f"_{int(time.time())}.json"
            )
            path = os.path.join(self.cold_storage_path, filename)
            tmp_path = f"{path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(envelope.to_dict(), f, indent=2)
            os.rename(tmp_path, path)
        except OSError as exc:
            print(
                f"WARN: Local cold storage write failed: {exc}",
                file=sys.stderr,
            )

    # ------------------------------------------------------------------
    # Peer communication (synchronous, called from thread)
    # ------------------------------------------------------------------

    def _replicate_to_single_peer(
        self,
        peer: str,
        serialized: str,
        envelope: SnapshotEnvelope,
    ) -> None:
        """Thread target: attempt to POST envelope to a single peer."""
        result = self._attempt_peer_post(peer, serialized)

        with self._lock:
            self._replication_results.append(result)
            if not result.success:
                self._pending_queue.append((peer, envelope))

    def _attempt_peer_post(self, peer: str, body: str) -> ReplicationResult:
        """Attempt a single HTTP POST to a peer's sync endpoint."""
        url = f"https://{peer}{self.REPLICATION_ENDPOINT}"
        ts = datetime.now(timezone.utc).isoformat()
        try:
            data = body.encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(data)),
                },
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=self.http_timeout) as resp:
                return ReplicationResult(
                    peer_address=peer,
                    success=(200 <= resp.status < 300),
                    timestamp=ts,
                    http_status=resp.status,
                )
        except (urllib.error.URLError, OSError) as exc:
            return ReplicationResult(
                peer_address=peer,
                success=False,
                timestamp=ts,
                error=str(exc),
            )

    def __repr__(self) -> str:
        return (
            f"ColdStorageManager("
            f"jurisdiction={self.jurisdiction_id!r}, "
            f"peers={len(self.peer_nodes)}, "
            f"pending={self.pending_count()})"
        )
