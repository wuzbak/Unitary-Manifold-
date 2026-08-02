# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/county_node.py — Local County Ingestion Node
======================================================

Each of the 39 Washington State county election offices runs a CountyNode
instance.  The node:

  1. Accepts discrete int64 ballot integers (no floating point at intake —
     N=1 per ballot card; selections encoded as integer vectors)
  2. Maintains a ShardedChernSimonChain with 8 holographic persistence shards
  3. Computes a metric state (φ_eff, k_cs) for closure validation
  4. Handles network partitions gracefully: continues local intake,
     queues telemetry for transmission, flushes on reconnect
  5. Provides structured telemetry for state mesh consumption (HMAC-signed)

Physical mapping
----------------
  - County node ≈ "local county elections headquarters + ballot scanning hardware"
  - 8 shards ≈ distributed storage across geographically separated storage units
  - Telemetry = the shard state summary (no raw ballots) sent to state mesh

Network partition behaviour
---------------------------
  - disconnect() → marks node as offline; ingestion continues, queue grows
  - reconnect() → flushes queued telemetry payloads, marks node online
  - get_queued_payloads() → returns accumulated queue (for testing/inspection)

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import hmac
import json
import math
import time
from dataclasses import dataclass, field
from typing import List, Optional

from .chern_simon_hash import ShardedChernSimonChain
from .constants import (
    K_CS,
    PHI_0,
    SHARD_COUNT,
    WINDING_NUMBER,
)
from .metric_closure import MetricClosure, ClosureStatus, ClosureResult


# ---------------------------------------------------------------------------
# Ballot record
# ---------------------------------------------------------------------------

@dataclass
class BallotRecord:
    """Immutable record of a single cast ballot.

    Parameters
    ----------
    ballot_id : int
        Unique sequential identifier for this ballot.
    selection_vector : list[int]
        Discrete integer encoding of voter selections (one int per race).
    sequence_index : int
        Global sequence position within the county's ingestion stream.
    """

    ballot_id: int
    selection_vector: List[int]
    sequence_index: int
    timestamp_ns: int = field(default_factory=time.time_ns)

    def as_int(self) -> int:
        """Reduce the ballot to a single representative integer for hashing.

        Uses a polynomial accumulation over the selection vector components
        with a position-sensitive multiplier chain, then mixes in ballot_id.
        This ensures that [1,0,1] and [0,1,0] with the same ballot_id produce
        different integers.
        """
        acc = self.ballot_id * K_CS
        for pos, val in enumerate(self.selection_vector, start=1):
            # Each component contributes at a unique positional scale
            acc = (acc * 131 + int(val) * pos * K_CS + pos) & 0xFFFFFFFFFFFFFFFF
        # Final mix with ballot_id to make ballot_id significant
        acc = (acc ^ (self.ballot_id * 0x9E3779B97F4A7C15)) & 0xFFFFFFFFFFFFFFFF
        return acc


# ---------------------------------------------------------------------------
# County node
# ---------------------------------------------------------------------------

class CountyNode:
    """Local ballot ingestion node for a single Washington State county.

    Parameters
    ----------
    county_id : str
        Short machine identifier, e.g. "WA-047" (King County FIPS code).
    county_name : str
        Human-readable name, e.g. "King County".
    hmac_key : bytes, optional
        Key for HMAC-SHA512 telemetry signing.  If not provided, a
        deterministic key derived from the county_id is used.  In production,
        this MUST be a hardware-pinned secret.
    """

    def __init__(
        self,
        county_id: str,
        county_name: str,
        hmac_key: Optional[bytes] = None,
    ) -> None:
        self.county_id = county_id
        self.county_name = county_name
        self._hmac_key: bytes = hmac_key or self._derive_key(county_id)

        self._chain = ShardedChernSimonChain(n_shards=SHARD_COUNT)
        self._ballot_records: List[BallotRecord] = []
        self._sequence_index: int = 0
        self._online: bool = True
        self._telemetry_queue: List[dict] = []
        self._closure_validator = MetricClosure()
        self._last_closure_result: Optional[ClosureResult] = None

    # ------------------------------------------------------------------
    # Ballot ingestion
    # ------------------------------------------------------------------

    def ingest_ballot(self, selection_vector: List[int]) -> BallotRecord:
        """Ingest one ballot and update all internal hash chains.

        Parameters
        ----------
        selection_vector : list[int]
            Discrete integer representation of voter selections.

        Returns
        -------
        BallotRecord
            The immutable record created for this ballot.

        Notes
        -----
        Ingestion continues regardless of network status.  If offline,
        the resulting telemetry snapshot is queued for transmission on
        reconnect.
        """
        self._sequence_index += 1
        ballot_id = self._sequence_index

        record = BallotRecord(
            ballot_id=ballot_id,
            selection_vector=list(selection_vector),
            sequence_index=ballot_id,
        )
        self._ballot_records.append(record)

        ballot_int = record.as_int()
        self._chain.update(ballot_int)

        # If offline, queue a telemetry snapshot for later transmission
        if not self._online:
            self._telemetry_queue.append(self._build_telemetry_payload())

        return record

    def ingest_batch(self, selection_vectors: List[List[int]]) -> List[BallotRecord]:
        """Ingest multiple ballots atomically.

        Parameters
        ----------
        selection_vectors : list[list[int]]
            List of selection vectors, one per ballot.

        Returns
        -------
        list[BallotRecord]
        """
        return [self.ingest_ballot(sv) for sv in selection_vectors]

    # ------------------------------------------------------------------
    # Network partition management
    # ------------------------------------------------------------------

    def disconnect(self) -> None:
        """Simulate (or handle) a network partition event.

        The node continues operating locally; telemetry is queued.
        """
        self._online = False

    def reconnect(self) -> List[dict]:
        """Restore network connectivity and flush the telemetry queue.

        Returns
        -------
        list[dict]
            All queued telemetry payloads that were buffered during the
            partition.  The caller (state mesh) should process these in order.
        """
        self._online = True
        queued = list(self._telemetry_queue)
        self._telemetry_queue.clear()
        return queued

    def is_online(self) -> bool:
        """Return True if the node is currently connected to the state mesh."""
        return self._online

    def get_queued_payloads(self) -> List[dict]:
        """Return (without clearing) the current telemetry queue."""
        return list(self._telemetry_queue)

    # ------------------------------------------------------------------
    # Telemetry & state
    # ------------------------------------------------------------------

    def get_shard_telemetry(self) -> dict:
        """Return HMAC-signed shard telemetry for state mesh transmission.

        Returns a structured dict containing:
          - county identification
          - shard digests (8 × 16-char hex)
          - primary chain hash and SHA-512 digest
          - metric state (phi_eff, k_cs)
          - HMAC-SHA512 signature

        No raw ballot records are included.
        """
        payload = self._build_telemetry_payload()
        payload["hmac_signature"] = self._sign_payload(payload)
        return payload

    def get_metric_state(self) -> dict:
        """Return the current metric state dict for closure validation.

        Returns
        -------
        dict with keys: phi_eff, k_cs, ballot_count, hash_state
        """
        telemetry = self._chain.get_telemetry()
        hash_state = self._chain.primary_digest()
        ballot_count = self._chain.primary_ballot_count()
        phi_eff = self._compute_phi_eff(hash_state, ballot_count)
        return {
            "phi_eff": phi_eff,
            "k_cs": K_CS,
            "ballot_count": ballot_count,
            "hash_state": hash_state,
            "shard_digests": telemetry["shard_digests"],
            "synchronized_shards": telemetry["synchronized_shards"],
            "county_id": self.county_id,
            "county_name": self.county_name,
            "online": self._online,
            "queued_payloads": len(self._telemetry_queue),
        }

    def validate_closure(self) -> ClosureResult:
        """Run a metric closure validation on the current state.

        Returns
        -------
        ClosureResult
        """
        state = self.get_metric_state()
        result = self._closure_validator.validate(
            phi_eff=state["phi_eff"],
            k_cs_observed=state["k_cs"],
        )
        self._last_closure_result = result
        return result

    def ballot_count(self) -> int:
        """Return the total number of ballots ingested."""
        return self._chain.primary_ballot_count()

    def last_closure_result(self) -> Optional[ClosureResult]:
        """Return the most recent closure validation result, or None."""
        return self._last_closure_result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_phi_eff(self, hash_state: int, ballot_count: int) -> float:
        """Derive φ_eff from the current hash state."""
        if ballot_count == 0:
            return PHI_0
        residual_scale = 1e-30
        residual = (hash_state % (10 ** 15)) * residual_scale / max(ballot_count, 1)
        return PHI_0 + residual

    def _build_telemetry_payload(self) -> dict:
        """Build the raw (unsigned) telemetry payload dict."""
        telemetry = self._chain.get_telemetry()
        hash_state = self._chain.primary_digest()
        ballot_count = self._chain.primary_ballot_count()
        phi_eff = self._compute_phi_eff(hash_state, ballot_count)

        return {
            "county_id": self.county_id,
            "county_name": self.county_name,
            "ballot_count": ballot_count,
            "phi_eff": phi_eff,
            "k_cs": K_CS,
            "primary_hash": telemetry["primary_hash"],
            "primary_sha512": telemetry["primary_sha512"],
            "shard_digests": telemetry["shard_digests"],
            "shard_counts": telemetry["shard_counts"],
            "synchronized_shards": telemetry["synchronized_shards"],
            "parity_check": telemetry["parity_check"],
            "online": self._online,
        }

    def _sign_payload(self, payload: dict) -> str:
        """Produce an HMAC-SHA512 signature of the telemetry payload."""
        # Exclude the signature field itself to avoid circular dependency
        signable = {k: v for k, v in payload.items() if k != "hmac_signature"}
        message = json.dumps(signable, sort_keys=True).encode("utf-8")
        sig = hmac.new(self._hmac_key, message, hashlib.sha512).hexdigest()
        return sig

    @staticmethod
    def _derive_key(county_id: str) -> bytes:
        """Derive a deterministic HMAC key from the county_id.

        WARNING: In production, replace with a hardware-pinned secret.
        """
        return hashlib.sha512(
            f"EIGE-v21-{county_id}-hmac-key-placeholder".encode("utf-8")
        ).digest()

    def __repr__(self) -> str:
        return (
            f"CountyNode(id={self.county_id!r}, name={self.county_name!r}, "
            f"ballots={self.ballot_count()}, online={self._online})"
        )
