# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1055_sprint_cb_verification_release_discipline import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    TARGETED_SUITES,
    sprint_cb_verification_release_discipline,
    pillar1055_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1055
    assert PILLAR_GATE == "SPRINT_CB_VERIFICATION_RELEASE_DISCIPLINE"
    assert PILLAR_STATUS == "SPRINT_CB_VERIFICATION_RELEASE_DISCIPLINE_COMPLETE"
    assert PILLAR_VALID is True


def test_verification_contract() -> None:
    report = sprint_cb_verification_release_discipline()
    assert len(TARGETED_SUITES) >= 5
    assert report["workflow_checks"]["schedule_present"] is True
    assert report["workflow_checks"]["upload_artifact_present"] is True
    assert report["status_gate"]["zero_failures_in_header"] is True
    assert report["status_gate"]["evidence_scope"] == (
        "historical regression metadata; not current execution verification"
    )
    assert report["valid"] is True


def test_summary() -> None:
    summary = pillar1055_summary()
    assert summary["status"] == PILLAR_STATUS
    assert summary["valid"] is True


def test_named_regression_record_survives_a_long_honesty_preamble(tmp_path, monkeypatch) -> None:
    import src.core.pillar1055_sprint_cb_verification_release_discipline as module

    status = tmp_path / "STATUS.md"
    status.write_text(
        "# Status\n" + "> Scientific obligations remain open.\n" * 30
        + "Latest verified full regression in current branch history: "
        "64,150 passed · 22 skipped · 18 deselected · 0 failed.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "_STATUS", status)
    assert module._status_has_zero_failures() is True


def test_latest_named_record_does_not_borrow_older_zero_failure_counts(tmp_path, monkeypatch) -> None:
    import src.core.pillar1055_sprint_cb_verification_release_discipline as module

    status = tmp_path / "STATUS.md"
    monkeypatch.setattr(module, "_STATUS", status)
    for latest in (
        "1 failed",
        "10 failed",
        "REGRESSION_PENDING",
        "1 failed (previous baseline: 0 failed)",
        "0 failed (conflicting result: 1 failed)",
    ):
        status.write_text(
            "# Status\n> Earlier baseline: 0 failed.\n"
            f"Latest verified full regression in current branch history: {latest}.\n"
            "Latest verified full regression in current branch history: 0 failed.\n",
            encoding="utf-8",
        )
        assert module._status_has_zero_failures() is False


def test_missing_regression_metadata_stays_closed(tmp_path, monkeypatch) -> None:
    import src.core.pillar1055_sprint_cb_verification_release_discipline as module

    status = tmp_path / "STATUS.md"
    status.write_text("# Status\n> Execution still pending.\n", encoding="utf-8")
    monkeypatch.setattr(module, "_STATUS", status)
    assert module._status_has_zero_failures() is False
