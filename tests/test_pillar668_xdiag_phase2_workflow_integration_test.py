# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 668 — XDiag Phase 2 workflow integration spec."""
from __future__ import annotations

from src.core.pillar668_xdiag_phase2_workflow_integration_test_adjacent import (
    ADJACENT_TRACK,
    HEALTH_CHECK_ZONES,
    IDEMPOTENCE_REQUIRED,
    IDEMPOTENCE_TRIALS,
    L_TEST_SITES,
    PILLAR_NUMBER,
    VERSION,
    health_check_spec,
    idempotence_spec,
    integration_certificate,
    pillar_report,
    workflow_stage_spec,
)

STAGES = workflow_stage_spec()
HEALTH = health_check_spec()
IDEMPOTENCE = idempotence_spec()
CERTIFICATE = integration_certificate()
REPORT = pillar_report()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 668

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_test_sites(self) -> None:
        assert L_TEST_SITES == 6

    def test_idempotence_trials(self) -> None:
        assert IDEMPOTENCE_TRIALS == 5
        assert IDEMPOTENCE_REQUIRED is True


class TestWorkflowSpec:
    def test_stage_count(self) -> None:
        assert len(STAGES["stages"]) == 6

    def test_stage_order(self) -> None:
        assert STAGES["stages"][0] == "export_to_xdiag"
        assert STAGES["stages"][-1] == "um_interpretation"

    def test_xdiag_mocked(self) -> None:
        assert STAGES["xdiag_mocked"] is True


class TestHealthAndIdempotence:
    def test_health_zones(self) -> None:
        assert HEALTH["zones"] == HEALTH_CHECK_ZONES
        assert len(HEALTH["zones"]) == 3

    def test_health_status(self) -> None:
        assert HEALTH["expected_status_all"] == "HEALTHY"
        assert HEALTH["schema_version"] == "1.0.0"

    def test_idempotence_spec(self) -> None:
        assert IDEMPOTENCE["n_trials"] == 5
        assert IDEMPOTENCE["determinism_required"] is True


class TestIntegrationCertificate:
    def test_certificate_passes_spec(self) -> None:
        assert CERTIFICATE["all_stages_pass_spec"] is True

    def test_certificate_health_zones(self) -> None:
        assert CERTIFICATE["health_check_zones"] == HEALTH_CHECK_ZONES

    def test_certificate_embeds_idempotence(self) -> None:
        assert CERTIFICATE["idempotence_spec"]["n_trials"] == 5


class TestReport:
    def test_report_core_fields(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0

    def test_report_sections(self) -> None:
        assert set(REPORT).issuperset(
            {
                "workflow_stage_spec",
                "health_check_spec",
                "idempotence_spec",
                "integration_certificate",
            }
        )
