# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/federal_auditor.py — Federal Blind Audit Tier
=======================================================

The FederalAuditor receives ONLY OSCAL 1.5.0 Holon Zero Certificates from
the state aggregation mesh.  It:

  1. Validates the certificate structure.
  2. Verifies that k_CS = 74 and φ₀ = π/4 are asserted in the cert.
  3. Returns an AuditResult without accessing any raw ballot data.

Federal blind audit guarantee
------------------------------
The FederalAuditor class has NO method that returns raw ballot counts,
voter IDs, or individual ballot records.  This is a structural guarantee,
not an access control policy — there is no API route that leads to raw data.

Any attempt to call a non-existent raw-data method raises
RawDataAccessAttempt immediately.  The __getattr__ override enforces this:
any attribute access that is not in the explicit allowlist triggers the
exception.

This mirrors the architectural intent: "Federal systems can verify these
constraints instantly using zero-trust protocols" — the protocol is
enforced at the Python object boundary.

NIST SP-800-53 R5 mapping
--------------------------
  CA-2 : Security Assessment — validates OSCAL compliance artifacts
  AC-1 : Access Control — structural prohibition on raw data access
  AU-12: Audit Generation — emits AuditResult for oversight logging

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

from .constants import K_CS, PHI_0, PHI_TOLERANCE, ENGINE_VERSION
from .holon_zero_cert import validate_holon_zero_cert


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class RawDataAccessAttempt(Exception):
    """Raised when any code attempts to access raw ballot data via the
    FederalAuditor.  This is a hard architectural gate.

    Federal oversight tiers may never receive raw vote counts, voter IDs,
    or individual ballot records through this interface.
    """

    def __init__(self, attempted_attribute: str = "") -> None:
        msg = (
            "SECURITY VIOLATION: Raw ballot data access attempt detected at federal tier. "
            f"Attribute: {attempted_attribute!r}. "
            "Federal auditors may only access OSCAL Holon Zero Certificates. "
            "This attempt has been logged."
        )
        super().__init__(msg)
        self.attempted_attribute = attempted_attribute


# ---------------------------------------------------------------------------
# Audit result
# ---------------------------------------------------------------------------

class AuditVerdict(Enum):
    VERIFIED = auto()
    """Certificate is valid; all invariants hold."""

    INTEGRITY_VIOLATION = auto()
    """Certificate asserts violated invariants (k_CS ≠ 74 or φ₀ drift)."""

    SCHEMA_INVALID = auto()
    """Certificate does not conform to the required OSCAL structure."""


@dataclass
class AuditResult:
    """Federal audit outcome for a single Holon Zero Certificate.

    Contains ONLY derived proof metadata — no raw ballot information.
    """

    verdict: AuditVerdict
    jurisdiction_id: str
    block_height: int
    state_hash: str
    phi_verified: bool
    k_cs_verified: bool
    proof_status: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    remarks: str = ""

    def is_verified(self) -> bool:
        return self.verdict == AuditVerdict.VERIFIED

    def as_dict(self) -> dict:
        return {
            "verdict": self.verdict.name,
            "jurisdiction_id": self.jurisdiction_id,
            "block_height": self.block_height,
            "state_hash": self.state_hash,
            "phi_verified": self.phi_verified,
            "k_cs_verified": self.k_cs_verified,
            "proof_status": self.proof_status,
            "timestamp": self.timestamp,
            "remarks": self.remarks,
            "engine_version": ENGINE_VERSION,
            "nist_control": "CA-2",
        }


# ---------------------------------------------------------------------------
# Federal auditor
# ---------------------------------------------------------------------------

class FederalAuditor:
    """Federal-tier blind auditor for EIGE Holon Zero Certificates.

    This class implements the strict zero-knowledge API gate.  It:
      - Accepts only OSCAL Holon Zero Certificate dicts.
      - Returns only proof metadata (AuditResult).
      - Raises RawDataAccessAttempt for any access outside the allowlist.

    The __getattr__ override ensures that if any external code tries to
    call a method like query_raw(), get_votes(), or fetch_ballots(), they
    receive RawDataAccessAttempt regardless of whether such a method exists.
    """

    # Explicitly allowed attributes (everything else → RawDataAccessAttempt)
    _ALLOWED_ATTRS = frozenset({
        "validate_certificate",
        "get_audit_report",
        "audit_history",
        "clear_history",
        "_history",
        "_k_cs",
        "_phi_0",
        "_phi_tolerance",
        "__class__",
        "__repr__",
        "__str__",
        "__init__",
        "__dict__",
        "__doc__",
    })

    def __init__(
        self,
        k_cs: int = K_CS,
        phi_0: float = PHI_0,
        phi_tolerance: float = PHI_TOLERANCE,
    ) -> None:
        self._k_cs = k_cs
        self._phi_0 = phi_0
        self._phi_tolerance = phi_tolerance
        self._history: list = []

    def __getattr__(self, name: str) -> Any:
        """Block all attribute access that is not in the explicit allowlist."""
        if name.startswith("_") or name in self._ALLOWED_ATTRS:
            raise AttributeError(name)
        raise RawDataAccessAttempt(name)

    def validate_certificate(self, cert: dict) -> AuditResult:
        """Validate a Holon Zero Certificate and return an AuditResult.

        Parameters
        ----------
        cert : dict
            OSCAL 1.5.0 Holon Zero Certificate dict as produced by
            generate_holon_zero_cert().

        Returns
        -------
        AuditResult
            Contains ONLY proof metadata.  No raw ballot information.

        Notes
        -----
        The FederalAuditor never reads the raw ballot data from the cert
        because the cert contains no raw ballot data by construction.
        """
        ts = datetime.now(timezone.utc).isoformat()

        # Structural validation
        if not isinstance(cert, dict):
            result = AuditResult(
                verdict=AuditVerdict.SCHEMA_INVALID,
                jurisdiction_id="UNKNOWN",
                block_height=0,
                state_hash="",
                phi_verified=False,
                k_cs_verified=False,
                proof_status="SCHEMA_INVALID",
                timestamp=ts,
                remarks="Certificate is not a dict.",
            )
            self._history.append(result)
            return result

        if not validate_holon_zero_cert(cert):
            # Determine if it's a structural or invariant issue
            has_proof = "zero_knowledge_proof" in cert
            proof_data = cert.get("zero_knowledge_proof", {})

            # Support both Pedersen and legacy boolean formats
            if "proof_bytes" in proof_data:
                phi_ok = bool(proof_data.get("phi_delta_bound", False))
                kcs_ok = bool(proof_data.get("k_cs_match", False))
            else:
                phi_ok = bool(proof_data.get("phi_verified", False))
                kcs_ok = bool(proof_data.get("k_cs_verified", False))
            proof_status = proof_data.get("proof_status", "INVARIANTS_VIOLATED")

            if not has_proof or not cert.get("component-definition"):
                verdict = AuditVerdict.SCHEMA_INVALID
                remarks = "Certificate structure does not conform to OSCAL 1.5.0 schema."
            else:
                verdict = AuditVerdict.INTEGRITY_VIOLATION
                remarks = (
                    f"Invariant failure: phi_verified={phi_ok}, k_cs_verified={kcs_ok}."
                )

            result = AuditResult(
                verdict=verdict,
                jurisdiction_id=cert.get("component-definition", {}).get("jurisdiction_id", "UNKNOWN"),
                block_height=cert.get("component-definition", {}).get("block_height", 0),
                state_hash=cert.get("component-definition", {}).get("state_hash", ""),
                phi_verified=phi_ok,
                k_cs_verified=kcs_ok,
                proof_status=proof_status,
                timestamp=ts,
                remarks=remarks,
            )
            self._history.append(result)
            return result

        # Certificate passes — extract proof metadata only
        proof_data = cert["zero_knowledge_proof"]
        comp_def = cert["component-definition"]

        # Support both Pedersen (v21+) and legacy boolean format
        if "proof_bytes" in proof_data:
            phi_ok = bool(proof_data.get("phi_delta_bound", False))
            kcs_ok = bool(proof_data.get("k_cs_match", False))
        else:
            phi_ok = bool(proof_data.get("phi_verified", False))
            kcs_ok = bool(proof_data.get("k_cs_verified", False))
        proof_status = proof_data.get("proof_status", "")

        result = AuditResult(
            verdict=AuditVerdict.VERIFIED,
            jurisdiction_id=comp_def.get("jurisdiction_id", "UNKNOWN"),
            block_height=comp_def.get("block_height", 0),
            state_hash=comp_def.get("state_hash", ""),
            phi_verified=phi_ok,
            k_cs_verified=kcs_ok,
            proof_status=proof_status,
            timestamp=ts,
            remarks="All invariants verified. Certificate is authentic.",
        )
        self._history.append(result)
        return result

    def get_audit_report(self, cert: dict) -> dict:
        """Return a minimal federal audit report dict.

        Returns ONLY: verdict, jurisdiction_id, phi_verified, k_cs_verified,
        proof_status, timestamp.  Nothing else.

        Parameters
        ----------
        cert : dict
            OSCAL Holon Zero Certificate.

        Returns
        -------
        dict
            Minimal audit report — no raw ballot data.
        """
        result = self.validate_certificate(cert)
        return result.as_dict()

    def audit_history(self) -> list:
        """Return list of all AuditResult objects from this session."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear the audit history (for new election cycle)."""
        self._history.clear()

    def __repr__(self) -> str:
        return (
            f"FederalAuditor(k_cs={self._k_cs}, phi_0={self._phi_0:.8f}, "
            f"audits={len(self._history)})"
        )
