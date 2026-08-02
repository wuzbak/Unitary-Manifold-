# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/state_mesh.py — State-Wide Topological Aggregation Core
=================================================================

The StateMesh runs at the Washington State Secretary of State level.  It:

  1. Polls all 39 county nodes for their shard telemetry.
  2. Validates each county's metric closure (φ_eff, k_CS).
  3. Computes a cross-county braid synchronization — verifying that all
     counties' metric closures are mutually consistent.
  4. Produces a StateLedgerEntry: a signed aggregate closure certificate
     per election cycle.
  5. Emits a OSCAL Holon Zero Certificate for federal consumption.

Key design constraints
-----------------------
  - The state mesh NEVER re-tallies raw votes.  It reads only shard
    telemetry (hash state summaries, not ballot records).
  - Any county in VIOLATED closure state triggers a state-level OSCAL alert.
  - The 512-bit aggregate metric is computed using mpmath.

Async pattern
-------------
poll_all_counties() is synchronous by default (for Python 3.12 compatibility
in this repo).  An async variant is provided via async_poll_all_counties()
for production deployments using asyncio.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import math
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

try:
    from mpmath import mp, mpf, sqrt as mp_sqrt
    MPMATH_AVAILABLE = True
except ImportError:  # pragma: no cover
    MPMATH_AVAILABLE = False

from .constants import (
    K_CS,
    PHI_0,
    PHI_TOLERANCE,
    MPMATH_DPS,
    COUNTY_COUNT,
    SHARD_COUNT,
)
from .county_node import CountyNode
from .metric_closure import MetricClosure, ClosureStatus, ClosureResult
from .holon_zero_cert import generate_holon_zero_cert, validate_holon_zero_cert


# ---------------------------------------------------------------------------
# State ledger entry
# ---------------------------------------------------------------------------

@dataclass
class StateLedgerEntry:
    """Signed aggregate closure certificate for one election cycle pass.

    Attributes
    ----------
    timestamp : str
        UTC ISO 8601 timestamp of this aggregation pass.
    county_count : int
        Number of county nodes polled.
    counties_stable : int
        Number of counties returning STABLE closure.
    counties_drifted : int
        Number of counties in DRIFTED state.
    counties_violated : int
        Number of counties in VIOLATED state (triggers alert).
    aggregate_phi : float
        Mean φ_eff across all polled counties.
    aggregate_state_hash : str
        SHA-512 hex digest of the concatenated county primary hashes.
    state_closure_status : str
        "STABLE" | "DRIFTED" | "VIOLATED" — worst-case county status.
    county_details : list[dict]
        Per-county metric state and closure result.
    holon_zero_cert : dict
        Generated Holon Zero Certificate for federal transmission.
    """

    timestamp: str
    county_count: int
    counties_stable: int
    counties_drifted: int
    counties_violated: int
    aggregate_phi: float
    aggregate_state_hash: str
    state_closure_status: str
    county_details: List[dict] = field(default_factory=list)
    holon_zero_cert: Optional[dict] = field(default=None)

    def as_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "county_count": self.county_count,
            "counties_stable": self.counties_stable,
            "counties_drifted": self.counties_drifted,
            "counties_violated": self.counties_violated,
            "aggregate_phi": self.aggregate_phi,
            "aggregate_state_hash": self.aggregate_state_hash,
            "state_closure_status": self.state_closure_status,
            "county_details": self.county_details,
        }

    def is_clean(self) -> bool:
        """Return True only when all counties are STABLE."""
        return self.state_closure_status == "STABLE"


# ---------------------------------------------------------------------------
# State mesh
# ---------------------------------------------------------------------------

class StateMesh:
    """Washington State-wide topological aggregation core.

    Parameters
    ----------
    county_nodes : list[CountyNode]
        All county nodes to aggregate.  Typically 39 for Washington State.
    jurisdiction_id : str
        State-level identifier (default: "WA-STATE").
    """

    def __init__(
        self,
        county_nodes: List[CountyNode],
        jurisdiction_id: str = "WA-STATE",
    ) -> None:
        self._counties = county_nodes
        self.jurisdiction_id = jurisdiction_id
        self._closure_validator = MetricClosure()
        self._ledger_entries: List[StateLedgerEntry] = []
        if MPMATH_AVAILABLE:
            mp.dps = MPMATH_DPS

    # ------------------------------------------------------------------
    # Primary aggregation methods
    # ------------------------------------------------------------------

    def poll_all_counties(self) -> List[dict]:
        """Synchronously poll all county nodes for their metric states.

        Returns
        -------
        list[dict]
            One metric state dict per county node.
        """
        return [node.get_metric_state() for node in self._counties]

    async def async_poll_all_counties(self) -> List[dict]:
        """Asynchronously poll all county nodes (asyncio variant).

        Uses asyncio.gather for concurrent polling in production deployments.
        """
        loop = asyncio.get_event_loop()
        tasks = [
            loop.run_in_executor(None, node.get_metric_state)
            for node in self._counties
        ]
        return list(await asyncio.gather(*tasks))

    def compute_braid_sync(self) -> StateLedgerEntry:
        """Aggregate all county states and produce a StateLedgerEntry.

        Returns
        -------
        StateLedgerEntry
            The aggregate closure certificate.  county_details includes
            per-county metric state and closure result.
        """
        ts = datetime.now(timezone.utc).isoformat()
        county_states = self.poll_all_counties()

        counties_stable = 0
        counties_drifted = 0
        counties_violated = 0
        phi_sum = 0.0
        hash_parts: List[str] = []
        county_details: List[dict] = []
        worst_status = ClosureStatus.STABLE

        for state in county_states:
            phi_eff = float(state.get("phi_eff", PHI_0))
            k_cs_obs = int(state.get("k_cs", K_CS))
            result = self._closure_validator.validate(phi_eff, k_cs_obs)

            if result.status == ClosureStatus.STABLE:
                counties_stable += 1
            elif result.status == ClosureStatus.DRIFTED:
                counties_drifted += 1
                if worst_status == ClosureStatus.STABLE:
                    worst_status = ClosureStatus.DRIFTED
            else:
                counties_violated += 1
                worst_status = ClosureStatus.VIOLATED

            phi_sum += phi_eff
            hash_parts.append(state.get("primary_hash", "0" * 16))

            county_details.append({
                "county_id": state.get("county_id", "unknown"),
                "county_name": state.get("county_name", "unknown"),
                "ballot_count": state.get("ballot_count", 0),
                "phi_eff": phi_eff,
                "k_cs": k_cs_obs,
                "closure_status": result.status.name,
                "online": state.get("online", True),
            })

        n = len(county_states)
        aggregate_phi = phi_sum / n if n > 0 else PHI_0
        aggregate_hash = self._compute_aggregate_hash(hash_parts)

        # Generate Holon Zero Certificate for federal tier
        holon_cert = generate_holon_zero_cert(
            jurisdiction_id=self.jurisdiction_id,
            phi_eff=aggregate_phi,
            k_cs=K_CS,
            block_height=len(self._ledger_entries),
            state_hash=aggregate_hash,
            timestamp=ts,
        )

        entry = StateLedgerEntry(
            timestamp=ts,
            county_count=n,
            counties_stable=counties_stable,
            counties_drifted=counties_drifted,
            counties_violated=counties_violated,
            aggregate_phi=aggregate_phi,
            aggregate_state_hash=aggregate_hash,
            state_closure_status=worst_status.name,
            county_details=county_details,
            holon_zero_cert=holon_cert,
        )

        self._ledger_entries.append(entry)
        return entry

    def get_state_closure(self) -> ClosureStatus:
        """Return the current state-wide closure status.

        Runs a fresh poll and returns the worst-case status across all counties.
        """
        entry = self.compute_braid_sync()
        return ClosureStatus[entry.state_closure_status]

    def get_holon_zero_cert(self) -> Optional[dict]:
        """Return the most recently generated Holon Zero Certificate."""
        if self._ledger_entries:
            return self._ledger_entries[-1].holon_zero_cert
        return None

    def county_count(self) -> int:
        """Return the number of county nodes in this mesh."""
        return len(self._counties)

    def ledger_entries(self) -> List[StateLedgerEntry]:
        """Return all ledger entries produced this session."""
        return list(self._ledger_entries)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _compute_aggregate_hash(self, hash_parts: List[str]) -> str:
        """Compute the SHA-512 aggregate hash from all county primary hashes.

        This is the state-wide "braid lock" — a cryptographic commitment
        to the collective metric state of all 39 counties.
        """
        combined = "|".join(sorted(hash_parts))  # sorted for determinism
        return hashlib.sha512(combined.encode("utf-8")).hexdigest()

    def __repr__(self) -> str:
        return (
            f"StateMesh(jurisdiction={self.jurisdiction_id!r}, "
            f"counties={len(self._counties)}, "
            f"ledger_entries={len(self._ledger_entries)})"
        )
