# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests — Lane 1: Measurement confrontation instrument registry.

Validates that:
- docs/falsification/instrument_registry.yml is structurally complete
- Every named falsifier prediction has explicit pass AND fail conditions
- All current_status values are from the canonical vocabulary
- DESI HIGH_TENSION and LiteBIRD PENDING are correctly recorded
- The integrity checker itself raises on malformed input
"""
from __future__ import annotations

import pytest

pytest.importorskip("yaml", reason="pyyaml required for instrument registry tests")

from src.core.instrument_registry import (  # noqa: E402
    check_all_statuses,
    has_high_tension_or_falsified,
    load_instrument_registry,
    validate_registry_integrity,
)

REQUIRED_PREDICTION_IDS = {"P1", "P2", "P3", "P3b", "P4", "P25", "LAB-CP"}
VALID_STATUSES = {"PENDING", "CONSISTENT", "HIGH_TENSION", "FALSIFIED"}

@pytest.fixture(scope="module")
def registry():
    return load_instrument_registry()


class TestRegistryLoads:
    def test_loads_without_error(self, registry):
        assert isinstance(registry, dict)

    def test_has_predictions(self, registry):
        assert len(registry.get("predictions", [])) > 0

    def test_has_version(self, registry):
        assert "version" in registry

    def test_has_governance(self, registry):
        assert "governance" in registry


class TestRegistryIntegrity:
    def test_no_violations(self, registry):
        violations = validate_registry_integrity(registry)
        assert violations == [], f"Registry integrity violations:\n" + "\n".join(violations)

    def test_required_prediction_ids_present(self, registry):
        ids = {p["id"] for p in registry["predictions"]}
        missing = REQUIRED_PREDICTION_IDS - ids
        assert not missing, f"Missing required prediction IDs: {missing}"

    def test_all_statuses_valid(self, registry):
        for pred in registry["predictions"]:
            status = pred.get("current_status", "")
            assert status in VALID_STATUSES, (
                f"[{pred.get('id')}] Invalid status: {status}"
            )

    def test_every_prediction_has_fail_condition(self, registry):
        for pred in registry["predictions"]:
            fc = pred.get("fail_condition", "")
            assert fc and fc.strip(), (
                f"[{pred.get('id')}] fail_condition is empty or missing"
            )

    def test_every_prediction_has_pass_condition(self, registry):
        for pred in registry["predictions"]:
            pc = pred.get("pass_condition", "")
            assert pc and pc.strip(), (
                f"[{pred.get('id')}] pass_condition is empty or missing"
            )

    def test_every_prediction_has_at_least_one_instrument(self, registry):
        for pred in registry["predictions"]:
            instruments = pred.get("instruments", [])
            assert isinstance(instruments, list) and len(instruments) >= 1, (
                f"[{pred.get('id')}] Must have at least one instrument"
            )


class TestKnownStatuses:
    def test_p4_desi_is_high_tension(self, registry):
        statuses = check_all_statuses(registry)
        assert statuses["P4"] == "HIGH_TENSION", (
            "DESI wₐ tension must remain HIGH_TENSION until DR3 resolves or falsifies"
        )

    def test_p3_litebird_is_pending(self, registry):
        statuses = check_all_statuses(registry)
        assert statuses["P3"] == "PENDING"

    def test_p1_ns_is_consistent(self, registry):
        statuses = check_all_statuses(registry)
        assert statuses["P1"] == "CONSISTENT"

    def test_p2_r_is_consistent(self, registry):
        statuses = check_all_statuses(registry)
        assert statuses["P2"] == "CONSISTENT"

    def test_p25_gw_is_pending(self, registry):
        statuses = check_all_statuses(registry)
        assert statuses["P25"] == "PENDING"


class TestSentinel:
    def test_sentinel_true_because_desi_tension(self, registry):
        assert has_high_tension_or_falsified(registry), (
            "Sentinel should be True — DESI P4 is HIGH_TENSION"
        )


class TestIntegrityCheckerRaisesOnBadInput:
    def test_raises_on_empty_registry(self):
        violations = validate_registry_integrity({"predictions": []})
        assert any("no predictions" in v.lower() for v in violations)

    def test_raises_on_invalid_status(self):
        fake = {
            "predictions": [{
                "id": "TEST",
                "description": "x",
                "pass_condition": "x",
                "fail_condition": "x",
                "current_status": "INVENTED_STATUS",
                "instruments": [{"name": "x", "status": "PENDING"}],
                "last_updated": "2026-01-01",
            }],
            "governance": {
                "update_obligation": "x",
                "escalation": "x",
                "machine_ingest": "x",
            }
        }
        violations = validate_registry_integrity(fake)
        assert any("INVENTED_STATUS" in v for v in violations)

    def test_raises_on_missing_fail_condition(self):
        fake = {
            "predictions": [{
                "id": "TEST",
                "description": "x",
                "pass_condition": "x",
                "fail_condition": "",
                "current_status": "PENDING",
                "instruments": [{"name": "x", "status": "PENDING"}],
                "last_updated": "2026-01-01",
            }],
            "governance": {
                "update_obligation": "x",
                "escalation": "x",
                "machine_ingest": "x",
            }
        }
        violations = validate_registry_integrity(fake)
        assert any("fail_condition" in v for v in violations)
