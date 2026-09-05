# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import src.core.pillar1079_gemini_critique_proof_matrix as p1079

from src.core.pillar1079_gemini_critique_proof_matrix import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    gemini_critique_proof_matrix,
    pillar1079_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1079
    assert PILLAR_GATE == "GEMINI_CRITIQUE_PROOF_MATRIX"
    assert PILLAR_STATUS == "GEMINI_CRITIQUE_PROOF_MATRIX_COMPLETE"
    assert isinstance(PILLAR_VALID, bool)


def test_matrix_structure() -> None:
    report = gemini_critique_proof_matrix()
    assert report["immutable_baseline_lock"]["status"] == "PASS"
    assert len(report["rows"]) == 5
    assert report["counts"]["pass"] >= 1
    assert report["counts"]["tension"] >= 1
    assert report["valid"] is True


def test_confabulation_register_nonempty() -> None:
    report = gemini_critique_proof_matrix()
    assert len(report["confabulation_register"]) >= 1
    assert all(row["status"] == "CORRECTED" for row in report["confabulation_register"])


def test_baseline_lock_fails_closed_when_artifact_missing(monkeypatch, tmp_path) -> None:
    missing = tmp_path / "missing.md"
    monkeypatch.setattr(p1079, "_BASELINE_FORMAL_REVIEW", missing)
    lock = p1079._baseline_lock()
    assert lock["formal_review_exists"] is False
    assert lock["status"] == "FAIL"


def test_unknown_evidence_status_routes_to_falsified() -> None:
    assert p1079._route_from_evidence_status("UNKNOWN") == "FALSIFIED"


def test_summary() -> None:
    summary = pillar1079_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["confabulation_entries"] >= 1

