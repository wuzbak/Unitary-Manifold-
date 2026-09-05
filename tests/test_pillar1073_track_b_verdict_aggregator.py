# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1073_track_b_verdict_aggregator as module

from src.core.pillar1073_track_b_verdict_aggregator import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    TRACK_B_ATTEMPT_PILLARS,
    TRACK_B_AUDIT_PILLARS,
    pillar1073_summary,
    track_b_verdict_report,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1073
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_VERDICT_AGGREGATOR"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_VERDICT_AGGREGATOR_COMPLETE"
    assert PILLAR_VALID is True


def test_verdict_is_honest_no_false_closure() -> None:
    r = track_b_verdict_report()
    # None of the three attempt pillars actually close their lane in v36.2.
    assert r["all_lanes_closed"] is False
    assert r["verdict"] == "EXTENSION_UNESTABLISHED"
    assert r["closure_earned"] is False
    assert r["runtime_labels_changed"] is False
    assert r["scientific_progress"] is False


def test_parameter_free_and_hardgate_ok() -> None:
    r = track_b_verdict_report()
    assert r["parameter_free_extension"] is None
    assert r["hardgate_non_breakage_verified"] is False


def test_track_b_pillar_lists() -> None:
    assert TRACK_B_ATTEMPT_PILLARS == [1068, 1069, 1070]
    assert TRACK_B_AUDIT_PILLARS == [1071, 1072]


def test_summary() -> None:
    s = pillar1073_summary()
    assert s["pillar"] == 1073
    assert s["closure_earned"] is False


@pytest.mark.parametrize("extra", [
    {}, {"derivation_established": True}, {"derivation_established": True, "derivation_evidence": []},
    {"derivation_established": True, "derivation_evidence": ["claim"], "valid": False},
])
def test_claimed_closure_without_valid_derivation_is_rejected(monkeypatch, extra) -> None:
    for name in ("cw_quartic_extension_report", "ftheory_spectral_cover_report", "as_mechanism_report"):
        report = getattr(module, name)()
        report.update(outcome="EXTENSION_CLOSES_LANE", closure_earned=True, scientific_progress=True)
        report.update(extra)
        monkeypatch.setattr(module, name, lambda report=report: report)
    result = module.track_b_verdict_report()
    assert result["verdict"] == "EXTENSION_UNESTABLISHED"
    assert result["closure_earned"] is False
    assert result["all_lanes_closed"] is False
    assert result["scientific_progress"] is False


def test_valid_packets_do_not_substitute_for_missing_audits(monkeypatch) -> None:
    for name in ("cw_quartic_extension_report", "ftheory_spectral_cover_report", "as_mechanism_report"):
        report = getattr(module, name)()
        report.update(outcome="EXTENSION_CLOSES_LANE", closure_earned=True,
                      derivation_established=True, derivation_evidence=["calculation"])
        monkeypatch.setattr(module, name, lambda report=report: report)
    result = module.track_b_verdict_report()
    assert result["closure_earned"] is False
    assert result["all_lanes_closed"] is False
    assert result["verdict"] == "EXTENSION_UNESTABLISHED"


def test_impact_review_is_not_reported_as_proved_breakage(monkeypatch) -> None:
    audit = module.hardgate_non_breakage_veto()
    audit.update(extension_retracted=False, extension_review_required=True,
                 hardgate_breakage_detected=None)
    monkeypatch.setattr(module, "hardgate_non_breakage_veto", lambda: audit)
    result = module.track_b_verdict_report()
    assert result["verdict"] == "EXTENSION_IMPACT_REVIEW_REQUIRED"
    assert result["closure_earned"] is False


@pytest.mark.parametrize("missing", [
    None, "parameter_inventory_complete", "parameter_inventory_evidence",
    "hardgate_non_breakage_verified", "hardgate_comparison_evidence",
])
def test_progress_requires_complete_evidence_on_the_same_attempt(monkeypatch, missing) -> None:
    report = module.cw_quartic_extension_report()
    report.update(
        scientific_progress=True, derivation_established=True, derivation_evidence=["calculation"],
        parameter_inventory_complete=True, parameter_inventory_evidence=["inventory"],
        free_parameter_count=0, hardgate_non_breakage_verified=True,
        hardgate_breakage_detected=False, hardgate_comparison_evidence=["comparison"],
    )
    if missing is not None:
        report.pop(missing)
    monkeypatch.setattr(module, "cw_quartic_extension_report", lambda: report)
    result = module.track_b_verdict_report()
    assert result["per_lane"][0]["scientific_progress"] is (missing is None)
    assert result["scientific_progress"] is (missing is None)
    assert result["closure_earned"] is False
