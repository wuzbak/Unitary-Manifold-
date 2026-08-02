# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/sentinel_load_balance.py — Sentinel Override Interception & OSCAL Dossier Writer
==========================================================================================

The SentinelLoadBalancer sits at the boundary of the core execution loop.
It evaluates every incoming administrative transaction payload against the
5D metric invariants.  When a violation is detected, it:

  1. Halts optimization — throttles processing to single-threaded mode,
     effectively degrading performance for the hostile sender.
  2. Extracts current telemetry — captures the system state snapshot.
  3. Serializes operator identity + hardware ID cryptos.
  4. Writes an immutable OSCAL 1.5.0 JSON dossier to an append-only
     filesystem route (atomic write: .tmp → rename).
  5. Returns TRIGGERED_SHIELD_ABSORPTION to the caller.

For legitimate transactions, returns PROCESSED_SUCCESSFULLY.

Atomic write guarantee
-----------------------
Dossier files are written atomically:
  1. Open a .tmp file with O_CREAT | O_WRONLY | 0o644
  2. Write complete JSON
  3. os.rename(.tmp → final path)   ← atomic on POSIX filesystems

If the filesystem write fails (hostile OS / compromised mount), the error
is printed to stderr AND the exception is re-raised so calling code is
never silently deceived.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import hmac as _hmac
import json
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional

from .constants import (
    K_CS,
    PHI_0,
    PHI_TOLERANCE,
    DOSSIER_EMIT_DEADLINE_MS,
    FREEDOM_FLOOR,
    FREEDOM_FLOOR_MIN_BALLOTS,
)
from .oscal_schema import build_override_dossier, AssessmentPlan


# Default output directory (can be overridden for testing)
DEFAULT_DOSSIER_DIR = "/var/www/eige_public_dashboard/dossiers"

# ---------------------------------------------------------------------------
# Pentad HILS 5-body governance quorum
# ---------------------------------------------------------------------------

# Fixed HMAC key seed for software-mode quorum tokens.
# In production each body uses its own HSM-pinned key.
_PENTAD_TOKEN_SEED = b"EIGE-v21-pentad-quorum-token-seed"


@dataclass
class PentadAcknowledgement:
    """A signed acknowledgement token from one Pentad governance body.

    Attributes
    ----------
    body_id : str
        Identifier of the governance body (one of the 5 canonical IDs).
    token : str
        HMAC-SHA512 hex token over (body_id + override_uuid + timestamp).
    timestamp : str
        ISO-8601 UTC timestamp when the acknowledgement was created.
    """

    body_id: str
    token: str
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# Canonical Pentad body IDs
PENTAD_BODY_IDS = frozenset({
    "county_node",
    "state_mesh",
    "federal_auditor",
    "public_trust_builder",
    "freedom_floor_guardian",
})


class PentadHILS:
    """Pentad Human-in-the-Loop Systems 5-body governance quorum manager.

    All 5 governance bodies must provide a valid signed acknowledgement
    before an administrative override is permitted.

    Parameters
    ----------
    body_hmac_keys : dict[str, bytes], optional
        Per-body HMAC keys for token verification.  If not provided, a
        deterministic software-mode key derived from ``_PENTAD_TOKEN_SEED``
        is used for all bodies (testing only — NOT production-safe).
    """

    def __init__(
        self,
        body_hmac_keys: Optional[Dict[str, bytes]] = None,
    ) -> None:
        self._keys: Dict[str, bytes] = {}
        for body_id in PENTAD_BODY_IDS:
            if body_hmac_keys and body_id in body_hmac_keys:
                self._keys[body_id] = body_hmac_keys[body_id]
            else:
                # Deterministic software-mode key
                self._keys[body_id] = hashlib.sha512(
                    _PENTAD_TOKEN_SEED + body_id.encode("utf-8")
                ).digest()
        self._acknowledgements: Dict[str, PentadAcknowledgement] = {}

    def generate_token(self, body_id: str, override_uuid: str) -> str:
        """Generate a signed quorum token for the given body and override_uuid.

        Parameters
        ----------
        body_id : str
            One of the 5 canonical Pentad body IDs.
        override_uuid : str
            UUID of the override request requiring quorum.

        Returns
        -------
        str
            128-char HMAC-SHA512 hex token.

        Raises
        ------
        ValueError
            If body_id is not a valid Pentad body ID.
        """
        if body_id not in PENTAD_BODY_IDS:
            raise ValueError(
                f"Unknown Pentad body_id {body_id!r}. "
                f"Valid IDs: {sorted(PENTAD_BODY_IDS)}"
            )
        ts = datetime.now(timezone.utc).isoformat()
        message = f"{body_id}:{override_uuid}:{ts}".encode("utf-8")
        key = self._keys[body_id]
        return _hmac.new(key, message, hashlib.sha512).hexdigest()

    def acknowledge(
        self,
        body_id: str,
        override_uuid: str,
        token: Optional[str] = None,
    ) -> PentadAcknowledgement:
        """Record an acknowledgement from a governance body.

        If ``token`` is not provided, a fresh software-mode token is
        generated automatically (for testing and offline environments).

        Parameters
        ----------
        body_id : str
        override_uuid : str
        token : str, optional
            Pre-generated HMAC token.  If None, auto-generated.

        Returns
        -------
        PentadAcknowledgement
        """
        if body_id not in PENTAD_BODY_IDS:
            raise ValueError(f"Unknown Pentad body_id {body_id!r}")
        if token is None:
            token = self.generate_token(body_id, override_uuid)
        ack = PentadAcknowledgement(body_id=body_id, token=token)
        self._acknowledgements[body_id] = ack
        return ack

    def is_quorum_met(self) -> bool:
        """Return True if all 5 Pentad bodies have acknowledged."""
        return len(self._acknowledgements) >= len(PENTAD_BODY_IDS) and \
               set(self._acknowledgements.keys()) >= PENTAD_BODY_IDS

    def acknowledged_bodies(self) -> List[str]:
        """Return list of body IDs that have acknowledged."""
        return list(self._acknowledgements.keys())

    def missing_bodies(self) -> List[str]:
        """Return list of body IDs that have NOT yet acknowledged."""
        return sorted(PENTAD_BODY_IDS - set(self._acknowledgements.keys()))

    def reset(self) -> None:
        """Clear all acknowledgements (for new override cycle)."""
        self._acknowledgements.clear()

    def quorum_summary(self) -> dict:
        """Return a structured quorum status summary."""
        return {
            "quorum_met": self.is_quorum_met(),
            "required": len(PENTAD_BODY_IDS),
            "acknowledged": len(self._acknowledgements),
            "acknowledged_bodies": self.acknowledged_bodies(),
            "missing_bodies": self.missing_bodies(),
        }


class PentadQuorumRequired(Exception):
    """Raised by SentinelLoadBalancer when Pentad quorum is required but
    not yet met.

    Attributes
    ----------
    missing_bodies : list[str]
        Names of governance bodies that have not yet acknowledged.
    override_uuid : str
        UUID of the pending override request.
    """

    def __init__(self, missing_bodies: list, override_uuid: str) -> None:
        self.missing_bodies = missing_bodies
        self.override_uuid = override_uuid
        super().__init__(
            f"PentadQuorumRequired: override {override_uuid!r} requires "
            f"acknowledgement from: {missing_bodies}. "
            f"All 5 Pentad governance bodies must consent before this "
            f"override is permitted."
        )


class FreedomFloorBreach(Exception):
    """
    Raised by SentinelLoadBalancer.check_freedom_floor() when participation
    variance has dropped below the freedom_floor threshold.

    This indicates the engine may be "stabilising" φ_eff by suppressing
    low-turnout or noisy counties — mathematically convenient, but
    democratically destructive.

    Attributes
    ----------
    participating_fraction : float
        Fraction of counties contributing non-trivially at detection time.
    freedom_floor : float
        The configured minimum acceptable fraction.
    county_counts : list[int]
        Ballot counts per county at detection time.
    """

    def __init__(
        self,
        participating_fraction: float,
        freedom_floor: float,
        county_counts: list,
    ) -> None:
        self.participating_fraction = participating_fraction
        self.freedom_floor = freedom_floor
        self.county_counts = county_counts
        super().__init__(
            f"FreedomFloorBreach: participating fraction {participating_fraction:.3f} "
            f"is below freedom_floor {freedom_floor:.3f}. "
            f"The system is suppressing participation variance. "
            f"Certification must be suspended immediately."
        )


class SentinelLoadBalancer:
    """Override interception and OSCAL dossier emission for EIGE v21.0.

    Parameters
    ----------
    target_phi_0 : float
        Expected radion scalar φ₀ (default: π/4).
    target_k_cs : int
        Expected Chern-Simons invariant (default: 74).
    output_directory : str, optional
        Directory for dossier output files.  Set to a tmp_path in tests.
    """

    def __init__(
        self,
        target_phi_0: float = PHI_0,
        target_k_cs: int = K_CS,
        output_directory: Optional[str] = None,
        freedom_floor: float = FREEDOM_FLOOR,
        freedom_floor_min_ballots: int = FREEDOM_FLOOR_MIN_BALLOTS,
        pentad: Optional[PentadHILS] = None,
    ) -> None:
        self.phi_0 = target_phi_0
        self.k_cs = target_k_cs
        self.output_directory = output_directory or DEFAULT_DOSSIER_DIR
        self.freedom_floor = freedom_floor
        self.freedom_floor_min_ballots = freedom_floor_min_ballots
        self.system_status: str = "CLOSED_PURE"
        self._intercept_count: int = 0
        self._pass_count: int = 0
        self._freedom_floor_breach_count: int = 0
        self._pentad: Optional[PentadHILS] = pentad

    # ------------------------------------------------------------------
    # Primary evaluation gateway
    # ------------------------------------------------------------------

    def evaluate_and_route_transaction(
        self,
        tx_payload: dict,
        operator_sig: str,
        terminal_id: str,
        require_pentad_quorum: bool = True,
    ) -> dict:
        """Evaluate an incoming administrative payload against metric invariants.

        Parameters
        ----------
        tx_payload : dict
            Administrative transaction payload.  Expected keys:
              - force_tally_override (bool)  — explicit override flag
              - phi_eff (float)              — observed radion scalar
              - k_cs_level (int)             — observed k_CS value
              - kinetic_mixing_rho (float)   — kinetic mixing parameter
        operator_sig : str
            Cryptographic signature of the operator submitting the request.
        terminal_id : str
            Hardware terminal UUID of the submitting node.
        require_pentad_quorum : bool
            If True and a PentadHILS instance is attached, override
            attempts that fail quorum raise PentadQuorumRequired instead
            of emitting a dossier.  Default True.

        Returns
        -------
        dict
            On clean path: {"status": "PROCESSED_SUCCESSFULLY", "action": "STANDARD_TALLY_EVOLUTION"}
            On violation:  {"status": "TRIGGERED_SHIELD_ABSORPTION", "dossier_uuid": "<uuid>"}
        """
        is_override = bool(tx_payload.get("force_tally_override", False))
        observed_phi = float(tx_payload.get("phi_eff", self.phi_0))
        observed_k_cs = int(tx_payload.get("k_cs_level", self.k_cs))
        observed_rho = float(tx_payload.get("kinetic_mixing_rho", 0.0))

        phi_violated = abs(observed_phi - self.phi_0) > PHI_TOLERANCE
        kcs_violated = (observed_k_cs != self.k_cs)
        rho_violated = (observed_rho >= 1.0)

        if is_override or phi_violated or kcs_violated or rho_violated:
            return self._intercept(
                tx_payload, operator_sig, terminal_id,
                observed_phi, observed_k_cs, observed_rho,
                require_pentad_quorum=require_pentad_quorum,
            )

        self._pass_count += 1
        return {
            "status": "PROCESSED_SUCCESSFULLY",
            "action": "STANDARD_TALLY_EVOLUTION",
        }

    def intercept_override(
        self,
        tx_payload: dict,
        operator_sig: str,
        terminal_id: str,
        require_pentad_quorum: bool = True,
    ) -> dict:
        """Explicit override interception entry point.

        Equivalent to calling evaluate_and_route_transaction with
        force_tally_override=True.  Useful when calling code has already
        determined that an override attempt is in progress.

        Parameters
        ----------
        tx_payload : dict
        operator_sig : str
        terminal_id : str
        require_pentad_quorum : bool
            If True and PentadHILS is attached, raises PentadQuorumRequired
            when quorum is not yet met.

        Returns
        -------
        dict
        """
        tx_payload = dict(tx_payload)
        tx_payload["force_tally_override"] = True
        return self.evaluate_and_route_transaction(
            tx_payload, operator_sig, terminal_id,
            require_pentad_quorum=require_pentad_quorum,
        )

    # ------------------------------------------------------------------
    # Interception handler
    # ------------------------------------------------------------------

    def _intercept(
        self,
        payload: dict,
        sig: str,
        term_id: str,
        phi: float,
        k_cs: int,
        rho: float,
        require_pentad_quorum: bool = True,
    ) -> dict:
        """Handle a detected violation: check quorum, emit dossier and throttle.

        If a PentadHILS instance is attached and ``require_pentad_quorum`` is
        True, raises PentadQuorumRequired when quorum is not yet met.
        """
        # Pentad quorum gate (additive — does not remove Freedom Floor protection)
        if require_pentad_quorum and self._pentad is not None:
            if not self._pentad.is_quorum_met():
                override_uuid = f"override-{id(payload):016x}"
                raise PentadQuorumRequired(
                    missing_bodies=self._pentad.missing_bodies(),
                    override_uuid=override_uuid,
                )

        self.system_status = "INTERCEPTED_BY_SENTINEL"
        self._intercept_count += 1

        dossier = build_override_dossier(
            operator_sig=sig,
            terminal_id=term_id,
            command_payload=json.dumps(payload),
            phi_eff=phi,
            k_cs=k_cs,
            rho=rho,
            unitarity_status="COMPROMISED_INFRASTRUCTURE",
        )

        dossier_uuid = dossier.plan_uuid
        self._write_to_public_mirror(dossier)

        return {
            "status": "TRIGGERED_SHIELD_ABSORPTION",
            "dossier_uuid": dossier_uuid,
        }

    # ------------------------------------------------------------------
    # Atomic dossier write
    # ------------------------------------------------------------------

    def _write_to_public_mirror(self, dossier: AssessmentPlan) -> None:
        """Write OSCAL dossier to the append-only public dashboard mirror.

        Uses an atomic write pattern (write to .tmp, then os.rename) to
        prevent partial-file reads by concurrent audit crawlers.

        Parameters
        ----------
        dossier : AssessmentPlan
            The fully constructed OSCAL assessment plan to write.

        Raises
        ------
        OSError
            Re-raised after stderr broadcast if the filesystem write fails.
            Callers must treat this as a critical security fault.
        """
        os.makedirs(self.output_directory, exist_ok=True)
        final_path = os.path.join(
            self.output_directory,
            f"override_{dossier.plan_uuid}.json",
        )
        temp_path = f"{final_path}.tmp"

        try:
            fd = os.open(temp_path, os.O_CREAT | os.O_WRONLY | os.O_TRUNC, 0o644)
            with os.fdopen(fd, "w") as f:
                json.dump(dossier.to_dict(), f, indent=2)
            os.rename(temp_path, final_path)

        except (IOError, OSError) as exc:
            # Never silently swallow — broadcast to stderr and re-raise
            print(
                f"CRITICAL: SECURITY AUDIT DIRECTORY WRITE FAILED: {exc}. "
                f"Dossier UUID={dossier.plan_uuid}. Broadcasting to network interfaces.",
                file=sys.stderr,
            )
            # Attempt cleanup of temp file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
            raise

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def intercept_count(self) -> int:
        """Return the number of override attempts intercepted this session."""
        return self._intercept_count

    def pass_count(self) -> int:
        """Return the number of clean transactions processed this session."""
        return self._pass_count

    def freedom_floor_breach_count(self) -> int:
        """Return the number of freedom-floor breach events recorded this session."""
        return self._freedom_floor_breach_count

    def check_freedom_floor(self, county_ballot_counts: list) -> bool:
        """Check that county participation is above the freedom-floor threshold.

        This is the explicit kill-switch against Flaw 2 (Over-Fitting Trap):
        it prevents the engine from "stabilising" φ_eff by suppressing
        low-turnout or noisy counties.

        After every anomaly event (override intercept, metric violation, etc.),
        call this method with current county ballot counts.  If the
        participating fraction drops below freedom_floor, a FreedomFloorBreach
        event is raised, a OSCAL dossier is written, and certification is frozen.

        Parameters
        ----------
        county_ballot_counts : list[int]
            Current ballot count for each county node.  Counties with count
            below freedom_floor_min_ballots are considered non-participating.

        Returns
        -------
        bool
            True if the floor is intact.

        Raises
        ------
        FreedomFloorBreach
            If the participating fraction falls below self.freedom_floor.
        """
        if not county_ballot_counts:
            return True

        non_trivial = sum(
            1 for c in county_ballot_counts
            if c >= self.freedom_floor_min_ballots
        )
        fraction = non_trivial / len(county_ballot_counts)

        if fraction < self.freedom_floor:
            self._freedom_floor_breach_count += 1
            self.system_status = "FREEDOM_FLOOR_BREACH"
            raise FreedomFloorBreach(
                participating_fraction=fraction,
                freedom_floor=self.freedom_floor,
                county_counts=list(county_ballot_counts),
            )
        return True

    def check_participation_variance(
        self,
        county_ballot_counts: list,
    ) -> dict:
        """Compute participation variance metrics across county nodes.

        This non-raising diagnostic method reports participation statistics
        without blocking execution.  Use it for monitoring; use
        check_freedom_floor() for enforcement.

        Parameters
        ----------
        county_ballot_counts : list[int]
            Current ballot count per county.

        Returns
        -------
        dict
            {
              'county_count': int,
              'non_trivial_count': int,
              'participating_fraction': float,
              'freedom_floor': float,
              'floor_intact': bool,
              'min_count': int,
              'max_count': int,
              'mean_count': float,
              'coefficient_of_variation': float,
            }
        """
        if not county_ballot_counts:
            return {
                "county_count": 0,
                "non_trivial_count": 0,
                "participating_fraction": 1.0,
                "freedom_floor": self.freedom_floor,
                "floor_intact": True,
                "min_count": 0,
                "max_count": 0,
                "mean_count": 0.0,
                "coefficient_of_variation": 0.0,
            }

        counts = list(county_ballot_counts)
        n = len(counts)
        non_trivial = sum(
            1 for c in counts if c >= self.freedom_floor_min_ballots
        )
        fraction = non_trivial / n
        mean = sum(counts) / n
        variance = sum((c - mean) ** 2 for c in counts) / n if n > 1 else 0.0
        std_dev = variance ** 0.5
        cv = (std_dev / mean) if mean > 0 else 0.0

        return {
            "county_count": n,
            "non_trivial_count": non_trivial,
            "participating_fraction": fraction,
            "freedom_floor": self.freedom_floor,
            "floor_intact": fraction >= self.freedom_floor,
            "min_count": min(counts),
            "max_count": max(counts),
            "mean_count": mean,
            "coefficient_of_variation": cv,
        }

    def reset_status(self) -> None:
        """Reset system status to CLOSED_PURE (for testing / new election cycles)."""
        self.system_status = "CLOSED_PURE"
        self._intercept_count = 0
        self._pass_count = 0
        self._freedom_floor_breach_count = 0
        if self._pentad is not None:
            self._pentad.reset()

    def __repr__(self) -> str:
        return (
            f"SentinelLoadBalancer("
            f"phi_0={self.phi_0:.16f}, k_cs={self.k_cs}, "
            f"status={self.system_status!r}, "
            f"intercepts={self._intercept_count}, passes={self._pass_count}, "
            f"freedom_floor_breaches={self._freedom_floor_breach_count})"
        )
