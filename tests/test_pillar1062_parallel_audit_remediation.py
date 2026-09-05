# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import copy
import json
from pathlib import Path

import src.core.pillar1062_parallel_audit_remediation as audit_module

from src.core.pillar1062_parallel_audit_remediation import (
    ADJACENCY_LABEL,
    NEXT_PILLAR_SLOT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    SPRINT,
    VERSION,
    evolution_doc_honesty_check,
    lean_proxy_disclosure_check,
    live_status_alignment_check,
    observation_tracker_status_check,
    pillar1062_parallel_audit_report,
    pillar1062_summary,
    publication_packet_check,
    public_status_sync_check,
    radion_proxy_honesty_check,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1062
    assert PILLAR_STATUS == "PARALLEL_AUDIT_REMEDIATION_COMPLETE"
    assert "Audit" in PILLAR_TITLE
    assert VERSION == "v36.2"
    assert SPRINT == "CF"
    assert NEXT_PILLAR_SLOT == 1063
    assert ADJACENCY_LABEL == "NON_HARDGATE_AUDIT_REMEDIATION"


def test_observation_tracker_status_check() -> None:
    row = observation_tracker_status_check()
    assert row["historical_banner_present"] is True
    assert row["canonical_source_notice_present"] is True
    assert row["current_architecture_note_present"] is True
    assert row["desi_wait_language_current"] is True
    assert row["status"] == "PASS"


def test_evolution_doc_honesty_check() -> None:
    row = evolution_doc_honesty_check()
    assert row["markers"]["optional_stabilization"] is True
    assert row["markers"]["adm_closure"] is True
    assert row["markers"]["kk_lower_bound"] is True
    assert row["status"] == "PASS"


def test_radion_proxy_honesty_check() -> None:
    row = radion_proxy_honesty_check()
    assert row["doc_markers"]["threshold_honesty"] is True
    assert row["doc_markers"]["gradient_proxy_note"] is True
    assert row["doc_markers"]["curvature_proxy_exported"] is True
    assert row["positive_local_curvature"] is True
    assert row["gradient_proxy_flag"] is True
    assert row["status"] == "PASS"


def test_lean_proxy_disclosure_check() -> None:
    row = lean_proxy_disclosure_check()
    assert all(row["checks"].values())
    assert row["status"] == "PASS"


def test_live_status_alignment_check() -> None:
    row = live_status_alignment_check()
    assert row["json_matches_generator"] is True
    assert row["repo_exp2_status"] == "HIGH_TENSION"
    assert row["repo_exp4_status"] == "HIGH_TENSION"
    assert row["built_exp2_status"] == "HIGH_TENSION"
    assert row["built_exp4_status"] == "HIGH_TENSION"
    assert row["required_open_gates_present"] is True
    assert row["generator_required_open_gates_present"] is True
    assert row["status"] == "PASS"


def test_live_status_alignment_check_detects_generator_drift(monkeypatch) -> None:
    repo_json = json.loads(
        Path("9-INFRASTRUCTURE/um_live_status.json").read_text(encoding="utf-8")
    )

    class FakeModule:
        @staticmethod
        def build_live_status():
            payload = copy.deepcopy(repo_json)
            payload["tests"]["passed"] += 1
            return payload

    monkeypatch.setattr(audit_module, "_load_module", lambda *_args, **_kwargs: FakeModule)
    row = audit_module.live_status_alignment_check()
    assert row["json_matches_generator"] is False
    assert row["status"] == "FAIL"


def test_live_status_alignment_check_detects_missing_required_gate(monkeypatch) -> None:
    repo_json = json.loads(
        Path("9-INFRASTRUCTURE/um_live_status.json").read_text(encoding="utf-8")
    )

    class FakeModule:
        @staticmethod
        def build_live_status():
            payload = copy.deepcopy(repo_json)
            payload["open_gates"] = [
                row for row in payload["open_gates"]
                if row["gate"] != "LITEBIRD_BIREFRINGENCE"
            ]
            return payload

    monkeypatch.setattr(audit_module, "_load_module", lambda *_args, **_kwargs: FakeModule)
    row = audit_module.live_status_alignment_check()
    assert row["required_open_gates_present"] is True
    assert row["generator_required_open_gates_present"] is False
    assert row["status"] == "FAIL"


def test_public_status_sync_check() -> None:
    row = public_status_sync_check()
    assert row["aligned"] is True
    assert row["status"] == "PASS"


def test_publication_packet_exists() -> None:
    row = publication_packet_check()
    assert row["self_run_report_exists"] is True
    assert row["substack_post_exists"] is True
    assert row["status"] == "PASS"


def test_publication_packet_check_detects_missing_artifact(monkeypatch) -> None:
    missing = Path("/tmp/nonexistent-pillar1062-report.md")
    monkeypatch.setattr(audit_module, "_SELF_RUN_REPORT", missing)
    row = audit_module.publication_packet_check()
    assert row["self_run_report_exists"] is False
    assert row["status"] == "FAIL"


def test_integrated_report() -> None:
    report = pillar1062_parallel_audit_report()
    assert report["pillar"] == 1062
    assert report["status"] == PILLAR_STATUS
    assert report["overall_status"] == "PASS_WITH_FIXES"
    assert report["failing_checks"] == []
    assert "non_hardgate_statement" in report


def test_summary() -> None:
    row = pillar1062_summary()
    assert row["pillar"] == 1062
    assert row["status"] == PILLAR_STATUS
    assert row["overall_status"] == "PASS_WITH_FIXES"
