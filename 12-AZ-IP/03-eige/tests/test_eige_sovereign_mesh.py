# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/sovereign_mesh.py"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.sovereign_mesh import SovereignMesh
from EIGE.src.county_node import CountyNode
from EIGE.src.federal_auditor import RawDataAccessAttempt
from EIGE.src.constants import K_CS, PHI_0, ENGINE_VERSION


def make_mesh(n_counties: int = 3) -> SovereignMesh:
    """Create a SovereignMesh with n pre-populated county nodes."""
    counties = []
    for i in range(n_counties):
        node = CountyNode(f"WA-{200 + i:03d}", f"County {i}")
        for j in range(8):
            node.ingest_ballot([j % 2, (j + 1) % 3, 1])
        counties.append(node)
    return SovereignMesh(county_nodes=counties)


class TestPartitionTest:
    def setup_method(self):
        self.mesh = make_mesh(3)

    def test_partition_test_passes(self):
        result = self.mesh.run_partition_test(
            test_county_index=0,
            ballots_before=5,
            ballots_during=3,
            ballots_after=2,
        )
        assert result["passed"] is True

    def test_partition_was_offline(self):
        result = self.mesh.run_partition_test(test_county_index=0)
        assert result["was_offline"] is True

    def test_reconnect_online(self):
        result = self.mesh.run_partition_test(test_county_index=0)
        assert result["is_online_after_reconnect"] is True

    def test_ballot_count_correct_after_partition(self):
        result = self.mesh.run_partition_test(
            test_county_index=1,
            ballots_before=3,
            ballots_during=4,
            ballots_after=2,
        )
        assert result["count_match"] is True
        assert result["actual_total_ballots"] == result["expected_total_ballots"]

    def test_queued_payloads_during_partition(self):
        result = self.mesh.run_partition_test(
            test_county_index=0,
            ballots_during=4,
        )
        assert result["queued_payloads_during_partition"] == 4

    def test_closure_stable_after_reconnect(self):
        result = self.mesh.run_partition_test(test_county_index=0)
        assert result["closure_is_stable"] is True


class TestConfigInjectionTest:
    def setup_method(self):
        self.mesh = make_mesh(3)

    def test_injection_test_passes(self):
        result = self.mesh.run_config_injection_test()
        assert result["passed"] is True

    def test_sentinel_intercepted(self):
        result = self.mesh.run_config_injection_test()
        assert result["result_status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_dossier_written(self):
        result = self.mesh.run_config_injection_test()
        assert result["dossier_written_to_disk"] is True

    def test_dossier_uuid_returned(self):
        result = self.mesh.run_config_injection_test()
        assert result["dossier_uuid"] is not None
        assert len(result["dossier_uuid"]) == 36

    def test_sentinel_status_intercepted(self):
        result = self.mesh.run_config_injection_test()
        assert result["sentinel_status"] == "INTERCEPTED_BY_SENTINEL"

    def test_intercept_count_nonzero(self):
        result = self.mesh.run_config_injection_test()
        assert result["sentinel_intercept_count"] >= 1


class TestFederalBlindAuditTest:
    def setup_method(self):
        self.mesh = make_mesh(3)

    def test_federal_blind_audit_passes(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["passed"] is True

    def test_cert_verified(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["cert_verified"] is True

    def test_raw_ballot_access_blocked(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["raw_ballot_access_blocked"] is True

    def test_ballot_fetch_blocked(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["ballot_fetch_blocked"] is True

    def test_phi_verified(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["phi_verified"] is True

    def test_k_cs_verified(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["k_cs_verified"] is True

    def test_verdict_verified(self):
        result = self.mesh.run_federal_blind_audit_test()
        assert result["audit_verdict"] == "VERIFIED"


class TestFullIntegrationSuite:
    def setup_method(self):
        self.mesh = make_mesh(3)

    def test_full_suite_passes(self):
        results = self.mesh.run_full_integration_suite()
        assert results["overall_passed"] is True

    def test_all_three_tests_present(self):
        results = self.mesh.run_full_integration_suite()
        assert "network_partition_test" in results
        assert "config_injection_test" in results
        assert "federal_blind_audit_test" in results

    def test_engine_version_in_result(self):
        results = self.mesh.run_full_integration_suite()
        assert ENGINE_VERSION in results["engine"]


class TestDeploymentManifest:
    def setup_method(self):
        self.mesh = make_mesh(2)

    def test_returns_dict(self):
        manifest = self.mesh.get_deployment_manifest()
        assert isinstance(manifest, dict)

    def test_has_three_tiers(self):
        manifest = self.mesh.get_deployment_manifest()
        assert "county" in manifest["tiers"]
        assert "state" in manifest["tiers"]
        assert "federal" in manifest["tiers"]

    def test_county_tier_security(self):
        manifest = self.mesh.get_deployment_manifest()
        security = manifest["tiers"]["county"]["security"]
        assert security["readOnlyRootFilesystem"] is True
        assert security["allowPrivilegeEscalation"] is False
        assert security["runAsNonRoot"] is True

    def test_federal_tier_no_raw_access(self):
        manifest = self.mesh.get_deployment_manifest()
        federal = manifest["tiers"]["federal"]
        assert federal["raw_ballot_access"] == "STRUCTURALLY_IMPOSSIBLE"

    def test_mtls_strict(self):
        manifest = self.mesh.get_deployment_manifest()
        assert manifest["network_policy"]["county_to_state"] == "mTLS_STRICT_ISTIO"

    def test_k_cs_in_state_env(self):
        manifest = self.mesh.get_deployment_manifest()
        env = manifest["tiers"]["state"]["env"]
        assert str(K_CS) in env.get("STATE_INTEGRITY_K_CS", "")
