# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for EIGE/src/sentinel_load_balance.py"""

import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

import pytest
from EIGE.src.sentinel_load_balance import SentinelLoadBalancer
from EIGE.src.constants import K_CS, PHI_0, PHI_TOLERANCE


class TestSentinelCleanPath:
    def setup_method(self, tmp_path_factory=None):
        import tempfile
        self.dossier_dir = tempfile.mkdtemp(prefix="eige_test_sentinel_")
        self.sentinel = SentinelLoadBalancer(output_directory=self.dossier_dir)

    def _clean_payload(self, **overrides):
        p = {
            "force_tally_override": False,
            "phi_eff": PHI_0,
            "k_cs_level": K_CS,
            "kinetic_mixing_rho": 0.0,
            "voter_batch_id": "batch-001",
        }
        p.update(overrides)
        return p

    def test_clean_payload_returns_processed(self):
        result = self.sentinel.evaluate_and_route_transaction(
            self._clean_payload(), "0xSIG", "term-001"
        )
        assert result["status"] == "PROCESSED_SUCCESSFULLY"

    def test_clean_payload_action(self):
        result = self.sentinel.evaluate_and_route_transaction(
            self._clean_payload(), "0xSIG", "term-001"
        )
        assert result["action"] == "STANDARD_TALLY_EVOLUTION"

    def test_clean_payload_does_not_write_dossier(self):
        self.sentinel.evaluate_and_route_transaction(
            self._clean_payload(), "0xSIG", "term-001"
        )
        files = os.listdir(self.dossier_dir)
        assert len(files) == 0

    def test_pass_count_increments(self):
        for _ in range(3):
            self.sentinel.evaluate_and_route_transaction(
                self._clean_payload(), "0xSIG", "term-001"
            )
        assert self.sentinel.pass_count() == 3

    def test_system_status_unchanged_on_clean(self):
        self.sentinel.evaluate_and_route_transaction(
            self._clean_payload(), "0xSIG", "term-001"
        )
        assert self.sentinel.system_status == "CLOSED_PURE"


class TestSentinelInterception:
    def setup_method(self, tmp_path_factory=None):
        import tempfile
        self.dossier_dir = tempfile.mkdtemp(prefix="eige_test_sentinel_")
        self.sentinel = SentinelLoadBalancer(output_directory=self.dossier_dir)

    def _override_payload(self):
        return {
            "force_tally_override": True,
            "phi_eff": PHI_0,
            "k_cs_level": K_CS,
            "kinetic_mixing_rho": 0.0,
            "voter_batch_id": "batch-hostile-001",
        }

    def test_override_flag_triggers_shield(self):
        result = self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_override_returns_dossier_uuid(self):
        result = self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        assert "dossier_uuid" in result
        assert len(result["dossier_uuid"]) == 36

    def test_override_writes_dossier_to_disk(self):
        self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        files = [f for f in os.listdir(self.dossier_dir) if f.endswith(".json")]
        assert len(files) == 1

    def test_dossier_file_is_valid_json(self):
        result = self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        uuid = result["dossier_uuid"]
        path = os.path.join(self.dossier_dir, f"override_{uuid}.json")
        with open(path) as f:
            data = json.load(f)
        assert "$schema" in data
        assert "assessment-plan" in data

    def test_dossier_status_is_intercepted(self):
        result = self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        uuid = result["dossier_uuid"]
        path = os.path.join(self.dossier_dir, f"override_{uuid}.json")
        with open(path) as f:
            data = json.load(f)
        results = data["assessment-plan"]["assessment-results"]
        assert results["status"] == "INTERCEPTED_BY_SENTINEL"

    def test_system_status_changes_to_intercepted(self):
        self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        assert self.sentinel.system_status == "INTERCEPTED_BY_SENTINEL"

    def test_intercept_count_increments(self):
        for _ in range(3):
            self.sentinel.evaluate_and_route_transaction(
                self._override_payload(), "0xEXPLOIT", "term-bad"
            )
        assert self.sentinel.intercept_count() == 3

    def test_phi_violation_triggers_shield(self):
        payload = {
            "force_tally_override": False,
            "phi_eff": PHI_0 + 1e-10,  # above tolerance
            "k_cs_level": K_CS,
            "kinetic_mixing_rho": 0.0,
        }
        result = self.sentinel.evaluate_and_route_transaction(payload, "0xSIG", "term-001")
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_k_cs_violation_triggers_shield(self):
        payload = {
            "force_tally_override": False,
            "phi_eff": PHI_0,
            "k_cs_level": 73,  # wrong
            "kinetic_mixing_rho": 0.0,
        }
        result = self.sentinel.evaluate_and_route_transaction(payload, "0xSIG", "term-001")
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_rho_violation_triggers_shield(self):
        payload = {
            "force_tally_override": False,
            "phi_eff": PHI_0,
            "k_cs_level": K_CS,
            "kinetic_mixing_rho": 1.0,  # at boundary
        }
        result = self.sentinel.evaluate_and_route_transaction(payload, "0xSIG", "term-001")
        assert result["status"] == "TRIGGERED_SHIELD_ABSORPTION"

    def test_multiple_dossiers_written(self):
        for _ in range(3):
            self.sentinel.evaluate_and_route_transaction(
                self._override_payload(), "0xEXPLOIT", "term-bad"
            )
        files = [f for f in os.listdir(self.dossier_dir) if f.endswith(".json")]
        assert len(files) == 3

    def test_dossier_uuid_unique_per_event(self):
        uuids = set()
        for _ in range(5):
            result = self.sentinel.evaluate_and_route_transaction(
                self._override_payload(), "0xEXPLOIT", "term-bad"
            )
            uuids.add(result["dossier_uuid"])
        assert len(uuids) == 5

    def test_reset_clears_status(self):
        self.sentinel.evaluate_and_route_transaction(
            self._override_payload(), "0xEXPLOIT", "term-bad"
        )
        self.sentinel.reset_status()
        assert self.sentinel.system_status == "CLOSED_PURE"
        assert self.sentinel.intercept_count() == 0
