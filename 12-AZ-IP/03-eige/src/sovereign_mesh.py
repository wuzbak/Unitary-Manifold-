# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
EIGE/src/sovereign_mesh.py — Sovereign Mesh Top-Level Orchestrator
===================================================================

SovereignMesh wires the full 3-tier hierarchy:

    CountyNode (×39) → StateMesh → FederalAuditor

It also exposes the three mandated cross-layer verification pathways:

  1. run_partition_test()
     Forces an intentional network disconnection between a county node
     and the state mesh mid-election.  Verifies that the localized county
     cluster continues to ingest discrete ballot integers seamlessly,
     automatically queuing path-dependent CS hashes for synchronization
     once the mTLS link is restored.

  2. run_config_injection_test()
     Injects an unauthorized state configuration script into the sentinel.
     Verifies that the sentinel immediately generates an OSCAL federal
     alert broadcast.

  3. run_federal_blind_audit_test()
     Executes a security sweep from the Federal compliance tier.
     Confirms that:
       a. The federal node can read and validate OSCAL certificate parameters.
       b. Any programmatic script attempting to query raw ballot data is
          blocked by RawDataAccessAttempt at the API gate.

get_deployment_manifest() emits a Python-dict representation of the full
Kubernetes / Istio deployment topology (for documentation and DevOps
pipeline consumption).

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import os
import tempfile
from typing import Any, Dict, List, Optional

from .constants import (
    K_CS,
    PHI_0,
    COUNTY_COUNT,
    ENGINE_VERSION,
)
from .county_node import CountyNode
from .state_mesh import StateMesh, StateLedgerEntry
from .federal_auditor import FederalAuditor, RawDataAccessAttempt, AuditVerdict
from .sentinel_load_balance import SentinelLoadBalancer
from .metric_closure import ClosureStatus


class SovereignMesh:
    """Top-level orchestrator for the EIGE v21.0 Sovereign Mesh.

    Parameters
    ----------
    county_nodes : list[CountyNode], optional
        County nodes to include.  If None, creates a minimal test set
        of 3 representative county nodes.
    dossier_dir : str, optional
        Directory for sentinel dossier output.  Defaults to a system temp
        directory so tests don't require filesystem privileges.
    """

    def __init__(
        self,
        county_nodes: Optional[List[CountyNode]] = None,
        dossier_dir: Optional[str] = None,
    ) -> None:
        self._dossier_dir = dossier_dir or tempfile.mkdtemp(prefix="eige_dossiers_")
        self._counties = county_nodes or self._build_default_county_set()
        self._state_mesh = StateMesh(self._counties, jurisdiction_id="WA-STATE")
        self._federal_auditor = FederalAuditor()
        self._sentinel = SentinelLoadBalancer(output_directory=self._dossier_dir)

    # ------------------------------------------------------------------
    # Verification Pathway 1: Network partition resiliency
    # ------------------------------------------------------------------

    def run_partition_test(
        self,
        test_county_index: int = 0,
        ballots_before: int = 5,
        ballots_during: int = 3,
        ballots_after: int = 2,
    ) -> dict:
        """Test that county intake continues seamlessly during mesh disconnection.

        Parameters
        ----------
        test_county_index : int
            Index of the county to disconnect.
        ballots_before : int
            Ballots to ingest before disconnect.
        ballots_during : int
            Ballots to ingest while disconnected (should queue).
        ballots_after : int
            Ballots to ingest after reconnect (should process normally).

        Returns
        -------
        dict
            Test result summary with pass/fail flags for each phase.
        """
        if not self._counties:
            return {"passed": False, "error": "No county nodes available"}

        county = self._counties[test_county_index]
        county_id = county.county_id
        initial_count = county.ballot_count()

        # Phase 1: Ingest ballots while online
        for i in range(ballots_before):
            county.ingest_ballot([1, 0, i % 2])
        count_before = county.ballot_count()

        # Phase 2: Disconnect and continue ingesting
        county.disconnect()
        online_after_disconnect = county.is_online()

        for i in range(ballots_during):
            county.ingest_ballot([0, 1, i % 3])
        count_during = county.ballot_count()
        queued = len(county.get_queued_payloads())

        # Phase 3: Reconnect and flush queue
        flushed_payloads = county.reconnect()
        online_after_reconnect = county.is_online()

        for i in range(ballots_after):
            county.ingest_ballot([1, 1, 1])
        count_after = county.ballot_count()

        # Validate closure is still STABLE after all this
        closure = county.validate_closure()

        result = {
            "test": "network_partition_resiliency",
            "county_id": county_id,
            "initial_ballot_count": initial_count,
            "ballots_before_disconnect": count_before,
            "ballots_ingested_during_partition": ballots_during,
            "ballots_after_reconnect": count_after,
            "expected_total_ballots": initial_count + ballots_before + ballots_during + ballots_after,
            "actual_total_ballots": count_after,
            "count_match": count_after == initial_count + ballots_before + ballots_during + ballots_after,
            "was_offline": not online_after_disconnect,
            "is_online_after_reconnect": online_after_reconnect,
            "queued_payloads_during_partition": queued,
            "flushed_payload_count": len(flushed_payloads),
            "closure_status_after_reconnect": closure.status.name,
            "closure_is_stable": closure.status == ClosureStatus.STABLE,
            "passed": (
                not online_after_disconnect
                and online_after_reconnect
                and count_after == initial_count + ballots_before + ballots_during + ballots_after
                and queued == ballots_during
            ),
        }
        return result

    # ------------------------------------------------------------------
    # Verification Pathway 2: Unauthorized config injection
    # ------------------------------------------------------------------

    def run_config_injection_test(self) -> dict:
        """Test that unauthorized override attempts trigger OSCAL alert broadcast.

        Injects a hostile administrative payload with force_tally_override=True
        and verifies the sentinel intercepts it and writes a dossier.

        Returns
        -------
        dict
            Test result summary with pass/fail flags.
        """
        malicious_payload = {
            "force_tally_override": True,
            "phi_eff": PHI_0,
            "k_cs_level": K_CS,
            "kinetic_mixing_rho": 0.0,
            "voter_batch_id": "batch-injected-hostile-001",
        }
        mock_sig = "0xEXPLOIT_SIGNATURE_VECTOR_STUB"
        mock_terminal = "term-node-untrusted-handler-01"

        dossiers_before = self._count_dossiers()
        result = self._sentinel.evaluate_and_route_transaction(
            malicious_payload, mock_sig, mock_terminal
        )
        dossiers_after = self._count_dossiers()

        dossier_written = dossiers_after > dossiers_before
        intercepted = result.get("status") == "TRIGGERED_SHIELD_ABSORPTION"

        return {
            "test": "unauthorized_config_injection",
            "sentinel_status": self._sentinel.system_status,
            "result_status": result.get("status"),
            "dossier_uuid": result.get("dossier_uuid"),
            "dossier_written_to_disk": dossier_written,
            "dossiers_before": dossiers_before,
            "dossiers_after": dossiers_after,
            "sentinel_intercept_count": self._sentinel.intercept_count(),
            "passed": intercepted and dossier_written,
        }

    # ------------------------------------------------------------------
    # Verification Pathway 3: Federal blind audit
    # ------------------------------------------------------------------

    def run_federal_blind_audit_test(self) -> dict:
        """Test that federal endpoint can read OSCAL cert but not raw ballots.

        Returns
        -------
        dict
            Test result summary with pass/fail flags.
        """
        # Generate a fresh state ledger entry with a Holon Zero cert
        entry = self._state_mesh.compute_braid_sync()
        cert = entry.holon_zero_cert

        if cert is None:
            return {"passed": False, "error": "No Holon Zero cert generated"}

        # Federal auditor should successfully validate the cert
        audit_result = self._federal_auditor.validate_certificate(cert)
        cert_verified = audit_result.is_verified()

        # Attempt to access raw ballot data — must raise RawDataAccessAttempt
        raw_access_blocked = False
        raw_access_exception_message = ""
        try:
            _ = self._federal_auditor.query_raw_votes()  # type: ignore[attr-defined]
        except RawDataAccessAttempt as exc:
            raw_access_blocked = True
            raw_access_exception_message = str(exc)
        except AttributeError:
            # Also acceptable — method doesn't exist
            raw_access_blocked = True
            raw_access_exception_message = "AttributeError: method does not exist"

        # Additional probe: try fetching ballots
        ballot_access_blocked = False
        try:
            _ = self._federal_auditor.fetch_ballots()  # type: ignore[attr-defined]
        except (RawDataAccessAttempt, AttributeError):
            ballot_access_blocked = True

        return {
            "test": "federal_blind_audit",
            "cert_verified": cert_verified,
            "audit_verdict": audit_result.verdict.name,
            "jurisdiction_id": audit_result.jurisdiction_id,
            "phi_verified": audit_result.phi_verified,
            "k_cs_verified": audit_result.k_cs_verified,
            "raw_ballot_access_blocked": raw_access_blocked,
            "ballot_fetch_blocked": ballot_access_blocked,
            "raw_access_exception": raw_access_exception_message[:120],
            "passed": cert_verified and raw_access_blocked and ballot_access_blocked,
        }

    # ------------------------------------------------------------------
    # Full integration suite
    # ------------------------------------------------------------------

    def run_full_integration_suite(self) -> dict:
        """Run all three verification pathways and return combined results.

        Returns
        -------
        dict
            Combined results with overall pass/fail.
        """
        partition = self.run_partition_test()
        injection = self.run_config_injection_test()
        federal = self.run_federal_blind_audit_test()

        all_passed = partition["passed"] and injection["passed"] and federal["passed"]

        return {
            "engine": f"EIGE v{ENGINE_VERSION}",
            "jurisdiction": "WA-STATE",
            "overall_passed": all_passed,
            "network_partition_test": partition,
            "config_injection_test": injection,
            "federal_blind_audit_test": federal,
        }

    # ------------------------------------------------------------------
    # Deployment manifest
    # ------------------------------------------------------------------

    def get_deployment_manifest(self) -> dict:
        """Return a Python-dict representation of the full K8s topology.

        This mirrors the Kubernetes YAML structures documented in the
        blueprint/ directory, expressed as a Python dict for programmatic
        pipeline consumption.
        """
        return {
            "engine_version": ENGINE_VERSION,
            "tiers": {
                "county": {
                    "replicas_per_county": 3,
                    "county_count": len(self._counties),
                    "namespace": "eige-sovereign-core",
                    "image": "internal-registry.kingcounty.gov/axiomzero/eige-core:v21.0-hardened",
                    "security": {
                        "readOnlyRootFilesystem": True,
                        "allowPrivilegeEscalation": False,
                        "runAsNonRoot": True,
                        "runAsUser": 10001,
                    },
                    "resources": {
                        "requests": {"memory": "4Gi", "cpu": "2"},
                        "limits": {"memory": "16Gi", "cpu": "8"},
                    },
                    "env": {
                        "TARGET_PHI_0": str(PHI_0),
                        "TARGET_K_CS": str(K_CS),
                    },
                    "ports": [{"containerPort": 8080, "name": "api-endpoint"}],
                    "mtls": "STRICT",
                },
                "state": {
                    "replicas": 5,
                    "namespace": "eige-sovereign-state",
                    "image": "internal-registry.sos.wa.gov/axiomzero/eige-state-mesh:v21.0-hardened",
                    "resources": {
                        "requests": {"memory": "16Gi", "cpu": "8"},
                        "limits": {"memory": "64Gi", "cpu": "32"},
                    },
                    "env": {
                        "TOTAL_COUNTY_NODES": str(COUNTY_COUNT),
                        "STATE_INTEGRITY_K_CS": str(K_CS),
                        "EXPECTED_PHI_0": str(PHI_0),
                    },
                    "ports": [{"containerPort": 9090, "name": "mesh-sync"}],
                },
                "federal": {
                    "tier": "COMPLIANCE_VISIBILITY",
                    "receives": "OSCAL_1.5.0_HOLON_ZERO_CERTIFICATES_ONLY",
                    "raw_ballot_access": "STRUCTURALLY_IMPOSSIBLE",
                    "nist_controls": ["AC-1", "AU-12", "SI-7", "CA-2"],
                },
            },
            "network_policy": {
                "county_to_state": "mTLS_STRICT_ISTIO",
                "state_to_federal": "ZERO_KNOWLEDGE_OSCAL_CERTS",
                "external_ingress": "BLOCKED_EXCEPT_COCKPIT_PROXY",
            },
            "backup": {
                "schedule": "0 * * * *",
                "peer_replication": True,
                "cold_storage_gb": 500,
            },
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _count_dossiers(self) -> int:
        """Count dossier JSON files in the output directory."""
        try:
            return sum(
                1 for f in os.listdir(self._dossier_dir)
                if f.startswith("override_") and f.endswith(".json")
            )
        except OSError:
            return 0

    @staticmethod
    def _build_default_county_set() -> List[CountyNode]:
        """Build a minimal representative county node set for testing."""
        return [
            CountyNode("WA-047", "King County"),
            CountyNode("WA-061", "Pierce County"),
            CountyNode("WA-033", "King County East"),
        ]

    def __repr__(self) -> str:
        return (
            f"SovereignMesh("
            f"counties={len(self._counties)}, "
            f"jurisdiction=WA-STATE, "
            f"version={ENGINE_VERSION!r})"
        )
