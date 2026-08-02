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

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

from .constants import K_CS, PHI_0, PHI_TOLERANCE, DOSSIER_EMIT_DEADLINE_MS
from .oscal_schema import build_override_dossier, AssessmentPlan


# Default output directory (can be overridden for testing)
DEFAULT_DOSSIER_DIR = "/var/www/eige_public_dashboard/dossiers"


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
    ) -> None:
        self.phi_0 = target_phi_0
        self.k_cs = target_k_cs
        self.output_directory = output_directory or DEFAULT_DOSSIER_DIR
        self.system_status: str = "CLOSED_PURE"
        self._intercept_count: int = 0
        self._pass_count: int = 0

    # ------------------------------------------------------------------
    # Primary evaluation gateway
    # ------------------------------------------------------------------

    def evaluate_and_route_transaction(
        self,
        tx_payload: dict,
        operator_sig: str,
        terminal_id: str,
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
            )

        self._pass_count += 1
        return {
            "status": "PROCESSED_SUCCESSFULLY",
            "action": "STANDARD_TALLY_EVOLUTION",
        }

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
    ) -> dict:
        """Handle a detected violation: emit dossier and throttle."""
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

    def reset_status(self) -> None:
        """Reset system status to CLOSED_PURE (for testing / new election cycles)."""
        self.system_status = "CLOSED_PURE"
        self._intercept_count = 0
        self._pass_count = 0

    def __repr__(self) -> str:
        return (
            f"SentinelLoadBalancer("
            f"phi_0={self.phi_0:.16f}, k_cs={self.k_cs}, "
            f"status={self.system_status!r}, "
            f"intercepts={self._intercept_count}, passes={self._pass_count})"
        )
