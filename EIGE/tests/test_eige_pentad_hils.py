# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
Tests for Pentad HILS 5-body governance quorum logic in
EIGE/src/sentinel_load_balance.py.
"""

from __future__ import annotations

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from EIGE.src.sentinel_load_balance import (
    SentinelLoadBalancer,
    PentadHILS,
    PentadAcknowledgement,
    PentadQuorumRequired,
    PENTAD_BODY_IDS,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def pentad():
    return PentadHILS()


@pytest.fixture
def sentinel_with_pentad(pentad):
    return SentinelLoadBalancer(output_directory="/tmp/eige_test_dossiers", pentad=pentad)


@pytest.fixture
def sentinel_no_pentad():
    return SentinelLoadBalancer(output_directory="/tmp/eige_test_dossiers")


# ---------------------------------------------------------------------------
# 1. PentadHILS instantiation
# ---------------------------------------------------------------------------

class TestPentadHILSInit:
    def test_creates_with_defaults(self, pentad):
        assert pentad is not None

    def test_creates_with_custom_keys(self):
        keys = {b: os.urandom(64) for b in PENTAD_BODY_IDS}
        p = PentadHILS(body_hmac_keys=keys)
        assert p is not None

    def test_correct_body_count(self):
        assert len(PENTAD_BODY_IDS) == 5

    def test_canonical_body_ids_present(self):
        expected = {
            "county_node",
            "state_mesh",
            "federal_auditor",
            "public_trust_builder",
            "freedom_floor_guardian",
        }
        assert PENTAD_BODY_IDS == expected

    def test_initial_quorum_not_met(self, pentad):
        assert pentad.is_quorum_met() is False

    def test_initial_acknowledged_empty(self, pentad):
        assert pentad.acknowledged_bodies() == []

    def test_initial_missing_bodies_all_five(self, pentad):
        missing = pentad.missing_bodies()
        assert len(missing) == 5
        assert set(missing) == PENTAD_BODY_IDS


# ---------------------------------------------------------------------------
# 2. PentadHILS acknowledge / generate_token
# ---------------------------------------------------------------------------

class TestPentadHILSAcknowledge:
    def test_generate_token_returns_128_char_hex(self, pentad):
        token = pentad.generate_token("county_node", "override-001")
        assert isinstance(token, str)
        assert len(token) == 128

    def test_generate_token_invalid_body_raises(self, pentad):
        with pytest.raises(ValueError, match="Unknown Pentad body_id"):
            pentad.generate_token("invalid_body", "override-001")

    def test_acknowledge_one_body(self, pentad):
        ack = pentad.acknowledge("county_node", "override-001")
        assert isinstance(ack, PentadAcknowledgement)
        assert ack.body_id == "county_node"

    def test_acknowledge_adds_to_acknowledged(self, pentad):
        pentad.acknowledge("county_node", "override-001")
        assert "county_node" in pentad.acknowledged_bodies()

    def test_acknowledge_reduces_missing(self, pentad):
        pentad.acknowledge("county_node", "override-001")
        assert "county_node" not in pentad.missing_bodies()

    def test_acknowledge_invalid_body_raises(self, pentad):
        with pytest.raises(ValueError):
            pentad.acknowledge("invalid_body", "override-001")

    def test_acknowledge_all_five_meets_quorum(self, pentad):
        for body_id in PENTAD_BODY_IDS:
            pentad.acknowledge(body_id, "override-001")
        assert pentad.is_quorum_met() is True

    def test_acknowledge_four_does_not_meet_quorum(self, pentad):
        bodies = list(PENTAD_BODY_IDS)[:4]
        for body_id in bodies:
            pentad.acknowledge(body_id, "override-001")
        assert pentad.is_quorum_met() is False

    def test_acknowledge_with_explicit_token(self, pentad):
        token = pentad.generate_token("state_mesh", "override-002")
        ack = pentad.acknowledge("state_mesh", "override-002", token=token)
        assert ack.token == token

    def test_quorum_summary_structure(self, pentad):
        summary = pentad.quorum_summary()
        assert "quorum_met" in summary
        assert "required" in summary
        assert "acknowledged" in summary
        assert "missing_bodies" in summary
        assert summary["required"] == 5

    def test_quorum_summary_after_full_quorum(self, pentad):
        for body_id in PENTAD_BODY_IDS:
            pentad.acknowledge(body_id, "override-001")
        summary = pentad.quorum_summary()
        assert summary["quorum_met"] is True
        assert summary["acknowledged"] == 5
        assert summary["missing_bodies"] == []


# ---------------------------------------------------------------------------
# 3. PentadHILS reset
# ---------------------------------------------------------------------------

class TestPentadHILSReset:
    def test_reset_clears_acknowledgements(self, pentad):
        for body_id in PENTAD_BODY_IDS:
            pentad.acknowledge(body_id, "override-001")
        pentad.reset()
        assert pentad.acknowledged_bodies() == []

    def test_reset_clears_quorum(self, pentad):
        for body_id in PENTAD_BODY_IDS:
            pentad.acknowledge(body_id, "override-001")
        pentad.reset()
        assert pentad.is_quorum_met() is False


# ---------------------------------------------------------------------------
# 4. SentinelLoadBalancer with Pentad quorum
# ---------------------------------------------------------------------------

class TestSentinelWithPentadQuorum:
    def test_override_without_quorum_raises(self, sentinel_with_pentad):
        with pytest.raises(PentadQuorumRequired):
            sentinel_with_pentad.intercept_override(
                tx_payload={"phi_eff": 0.0, "k_cs_level": 0},
                operator_sig="sig",
                terminal_id="terminal-001",
                require_pentad_quorum=True,
            )

    def test_override_without_quorum_exception_has_missing_bodies(self, sentinel_with_pentad):
        try:
            sentinel_with_pentad.intercept_override(
                tx_payload={"phi_eff": 0.0, "k_cs_level": 0},
                operator_sig="sig",
                terminal_id="terminal-001",
                require_pentad_quorum=True,
            )
        except PentadQuorumRequired as exc:
            assert len(exc.missing_bodies) > 0

    def test_override_with_full_quorum_succeeds(self, sentinel_with_pentad, pentad):
        for body_id in PENTAD_BODY_IDS:
            pentad.acknowledge(body_id, "override-001")
        result = sentinel_with_pentad.intercept_override(
            tx_payload={"phi_eff": 0.0, "k_cs_level": 0},
            operator_sig="sig",
            terminal_id="terminal-001",
            require_pentad_quorum=True,
        )
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_override_with_quorum_bypassed_succeeds(self, sentinel_with_pentad):
        # require_pentad_quorum=False bypasses the check even without quorum
        result = sentinel_with_pentad.intercept_override(
            tx_payload={"phi_eff": 0.0, "k_cs_level": 0},
            operator_sig="sig",
            terminal_id="terminal-001",
            require_pentad_quorum=False,
        )
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"


# ---------------------------------------------------------------------------
# 5. SentinelLoadBalancer without Pentad — backward compatibility
# ---------------------------------------------------------------------------

class TestSentinelWithoutPentad:
    def test_clean_transaction_passes_without_pentad(self, sentinel_no_pentad):
        from EIGE.src.constants import PHI_0, K_CS
        result = sentinel_no_pentad.evaluate_and_route_transaction(
            tx_payload={"phi_eff": PHI_0, "k_cs_level": K_CS, "kinetic_mixing_rho": 0.0},
            operator_sig="sig",
            terminal_id="terminal-001",
        )
        assert result["status"] == "PROCESSED_SUCCESSFULLY"

    def test_override_without_pentad_does_not_raise(self, sentinel_no_pentad):
        result = sentinel_no_pentad.intercept_override(
            tx_payload={"phi_eff": 0.0, "k_cs_level": 0},
            operator_sig="sig",
            terminal_id="terminal-001",
        )
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_reset_clears_pentad_when_attached(self, sentinel_with_pentad, pentad):
        for body_id in PENTAD_BODY_IDS:
            pentad.acknowledge(body_id, "override-001")
        assert pentad.is_quorum_met() is True
        sentinel_with_pentad.reset_status()
        assert pentad.is_quorum_met() is False


# ---------------------------------------------------------------------------
# 6. PentadQuorumRequired exception
# ---------------------------------------------------------------------------

class TestPentadQuorumRequiredException:
    def test_exception_message_contains_override_uuid(self):
        exc = PentadQuorumRequired(
            missing_bodies=["county_node", "state_mesh"],
            override_uuid="override-test-uuid",
        )
        assert "override-test-uuid" in str(exc)

    def test_exception_message_contains_missing_bodies(self):
        exc = PentadQuorumRequired(
            missing_bodies=["county_node"],
            override_uuid="uuid-123",
        )
        assert "county_node" in str(exc)

    def test_exception_is_exception_subclass(self):
        exc = PentadQuorumRequired(missing_bodies=[], override_uuid="uuid")
        assert isinstance(exc, Exception)
