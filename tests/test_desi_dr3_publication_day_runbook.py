# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_desi_dr3_publication_day_runbook.py
==============================================
Comprehensive test suite for the DESI DR3 publication-day runbook module.
~40 tests covering constants, all 4 mock drills, checklist structure,
tension σ calculation, file coverage verification, and edge cases.
"""
from __future__ import annotations

import math

import pytest

from src.core.desi_dr3_publication_day_runbook import (
    CANONICAL_DOCS_TO_UPDATE,
    DESI_DR2_WA_CENTRAL,
    DESI_DR2_WA_SIGMA,
    DR3_TIMELINE_YEAR,
    PILLAR_285_MODULE,
    THRESHOLD_CONSISTENT,
    THRESHOLD_FALSIFIED,
    THRESHOLD_HIGH_TENSION,
    THRESHOLD_TENSION,
    UM_WA_PREDICTION,
    confirm_pillar285_preregistration,
    dr3_readiness_checklist,
    mock_drill_scenario,
    publication_day_checklist,
    publication_day_runbook_report,
    verify_update_coverage,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_um_wa_prediction_is_zero():
    assert UM_WA_PREDICTION == 0.0


def test_desi_dr2_wa_central():
    assert math.isclose(DESI_DR2_WA_CENTRAL, -0.62)


def test_desi_dr2_wa_sigma():
    assert math.isclose(DESI_DR2_WA_SIGMA, 0.30)


def test_threshold_consistent():
    assert THRESHOLD_CONSISTENT == 2.0


def test_threshold_tension():
    assert THRESHOLD_TENSION == 2.0


def test_threshold_high_tension():
    assert THRESHOLD_HIGH_TENSION == 2.5


def test_threshold_falsified():
    assert THRESHOLD_FALSIFIED == 3.0


def test_canonical_docs_has_seven_entries():
    assert len(CANONICAL_DOCS_TO_UPDATE) == 7


def test_canonical_docs_mandatory_filenames():
    filenames = [d["filename"] for d in CANONICAL_DOCS_TO_UPDATE]
    for required in [
        "docs/CLAIM_MASTER_BOARD.md",
        "TRUTH_LAYER.md",
        "OBSERVATION_TRACKER.md",
        "GATEKEEPER_SUMMARY.md",
        "WAVE_CHANGELOG.md",
        "STATUS.md",
        "FALLIBILITY.md",
    ]:
        assert required in filenames


def test_canonical_docs_all_have_update_actions():
    for doc in CANONICAL_DOCS_TO_UPDATE:
        for verdict in ("CONSISTENT", "TENSION", "HIGH_TENSION", "FALSIFIED"):
            assert verdict in doc["update_actions"]
            assert isinstance(doc["update_actions"][verdict], str)
            assert len(doc["update_actions"][verdict]) > 0


def test_canonical_docs_all_have_priority():
    for doc in CANONICAL_DOCS_TO_UPDATE:
        assert "priority" in doc
        assert isinstance(doc["priority"], int)
        assert doc["priority"] >= 1


# ---------------------------------------------------------------------------
# Tension σ edge cases
# ---------------------------------------------------------------------------


def test_tension_sigma_wa_zero():
    """wₐ = 0 exactly → 0 σ tension → CONSISTENT."""
    result = publication_day_checklist(0.0, 0.25)
    assert result["tension_sigma"] == pytest.approx(0.0)
    assert result["verdict"] == "CONSISTENT"


def test_tension_sigma_dr2_baseline():
    """DR2 baseline wₐ = −0.62 ± 0.30 → ~2.07σ → TENSION."""
    result = publication_day_checklist(-0.62, 0.30)
    assert result["tension_sigma"] == pytest.approx(0.62 / 0.30)
    assert result["verdict"] == "TENSION"


def test_tension_sigma_falsified_exact():
    """wₐ = −0.62 ± 0.18 → 0.62/0.18 ≈ 3.44σ → FALSIFIED."""
    sigma = 0.18
    result = publication_day_checklist(-0.62, sigma)
    expected_sigma = 0.62 / 0.18
    assert result["tension_sigma"] == pytest.approx(expected_sigma)
    assert result["verdict"] == "FALSIFIED"
    assert expected_sigma >= 3.0


def test_tension_sigma_exactly_two():
    """Tension exactly at 2.0 → TENSION (lower bound of tension band)."""
    result = publication_day_checklist(-0.40, 0.20)  # 0.40/0.20 = 2.0
    assert result["tension_sigma"] == pytest.approx(2.0)
    assert result["verdict"] == "TENSION"


def test_tension_sigma_exactly_three():
    """Tension clearly above 3.0 → FALSIFIED (avoid FP boundary at exact 3.0)."""
    result = publication_day_checklist(-0.61, 0.20)  # 3.05σ → cleanly FALSIFIED
    assert result["tension_sigma"] > 3.0
    assert result["verdict"] == "FALSIFIED"


def test_tension_sigma_exactly_2p5():
    """Tension exactly at 2.5 → HIGH_TENSION."""
    result = publication_day_checklist(-0.50, 0.20)  # 0.50/0.20 = 2.5
    assert result["tension_sigma"] == pytest.approx(2.5)
    assert result["verdict"] == "HIGH_TENSION"


# ---------------------------------------------------------------------------
# Checklist structure
# ---------------------------------------------------------------------------


def test_checklist_keys_present():
    result = publication_day_checklist(-0.40, 0.25)
    for key in (
        "verdict",
        "tension_sigma",
        "files_to_update",
        "required_within_hours",
        "same_day_sync_required",
        "retraction_required",
    ):
        assert key in result


def test_checklist_files_to_update_count():
    result = publication_day_checklist(-0.10, 0.25)
    assert len(result["files_to_update"]) == 7


def test_checklist_files_to_update_structure():
    result = publication_day_checklist(-0.10, 0.25)
    for entry in result["files_to_update"]:
        assert "filename" in entry
        assert "update_action" in entry
        assert "priority" in entry


def test_checklist_consistent_deadline():
    result = publication_day_checklist(-0.10, 0.25)  # < 2σ
    assert result["verdict"] == "CONSISTENT"
    assert result["required_within_hours"] == 336
    assert result["same_day_sync_required"] is False
    assert result["retraction_required"] is False


def test_checklist_tension_deadline():
    result = publication_day_checklist(-0.62, 0.30)  # ~2.07σ
    assert result["verdict"] == "TENSION"
    assert result["required_within_hours"] == 168
    assert result["same_day_sync_required"] is False
    assert result["retraction_required"] is False


def test_checklist_high_tension_deadline():
    result = publication_day_checklist(-0.50, 0.20)  # 2.5σ
    assert result["verdict"] == "HIGH_TENSION"
    assert result["required_within_hours"] == 72
    assert result["same_day_sync_required"] is True
    assert result["retraction_required"] is False


def test_checklist_falsified_deadline():
    result = publication_day_checklist(-0.62, 0.18)  # ~3.44σ
    assert result["verdict"] == "FALSIFIED"
    assert result["required_within_hours"] == 24
    assert result["same_day_sync_required"] is True
    assert result["retraction_required"] is True


# ---------------------------------------------------------------------------
# verify_update_coverage
# ---------------------------------------------------------------------------


def test_verify_update_coverage_all_present():
    all_files = [d["filename"] for d in CANONICAL_DOCS_TO_UPDATE]
    result = verify_update_coverage(all_files)
    assert result["audit_pass"] is True
    assert result["missing"] == []
    assert len(result["covered"]) == 7


def test_verify_update_coverage_one_missing():
    all_files = [d["filename"] for d in CANONICAL_DOCS_TO_UPDATE]
    without_first = all_files[1:]
    result = verify_update_coverage(without_first)
    assert result["audit_pass"] is False
    assert len(result["missing"]) == 1
    assert all_files[0] in result["missing"]


def test_verify_update_coverage_empty():
    result = verify_update_coverage([])
    assert result["audit_pass"] is False
    assert len(result["missing"]) == 7
    assert result["covered"] == []


def test_verify_update_coverage_extra_files_ok():
    all_files = [d["filename"] for d in CANONICAL_DOCS_TO_UPDATE]
    extra = all_files + ["README.md", "docs/extra.md"]
    result = verify_update_coverage(extra)
    assert result["audit_pass"] is True


# ---------------------------------------------------------------------------
# Mock drill scenarios
# ---------------------------------------------------------------------------


def test_mock_drill_consistent_structure():
    packet = mock_drill_scenario("dr3_consistent")
    assert packet["scenario"] == "dr3_consistent"
    assert "checklist" in packet
    assert packet["checklist"]["verdict"] == "CONSISTENT"


def test_mock_drill_tension_structure():
    packet = mock_drill_scenario("dr3_tension")
    assert packet["scenario"] == "dr3_tension"
    assert packet["checklist"]["verdict"] == "TENSION"


def test_mock_drill_high_tension_structure():
    packet = mock_drill_scenario("dr3_high_tension")
    assert packet["scenario"] == "dr3_high_tension"
    assert packet["checklist"]["verdict"] == "HIGH_TENSION"


def test_mock_drill_falsified_structure():
    packet = mock_drill_scenario("dr3_falsified")
    assert packet["scenario"] == "dr3_falsified"
    assert packet["checklist"]["verdict"] == "FALSIFIED"
    assert packet["checklist"]["retraction_required"] is True
    assert packet["checklist"]["same_day_sync_required"] is True


def test_mock_drill_all_have_wa_sigma():
    for scenario in ("dr3_consistent", "dr3_tension", "dr3_high_tension", "dr3_falsified"):
        packet = mock_drill_scenario(scenario)
        assert "wa_observed" in packet
        assert "sigma_wa" in packet
        assert isinstance(packet["wa_observed"], float)
        assert isinstance(packet["sigma_wa"], float)


def test_mock_drill_invalid_raises():
    with pytest.raises(ValueError, match="Unknown scenario"):
        mock_drill_scenario("dr3_unknown")


def test_mock_drill_falsified_uses_dr2_central():
    """The falsified drill uses DESI DR2 central value with tighter σ."""
    packet = mock_drill_scenario("dr3_falsified")
    assert packet["wa_observed"] == pytest.approx(-0.62)
    assert packet["sigma_wa"] < DESI_DR2_WA_SIGMA  # tighter than DR2


def test_mock_drill_consistent_tension_lt_2():
    """Consistent drill must actually have tension_sigma < 2."""
    packet = mock_drill_scenario("dr3_consistent")
    assert packet["checklist"]["tension_sigma"] < 2.0


def test_mock_drill_tension_in_range():
    """Tension drill: 2.0 ≤ σ < 2.5."""
    packet = mock_drill_scenario("dr3_tension")
    sigma = packet["checklist"]["tension_sigma"]
    assert 2.0 <= sigma < 2.5


def test_mock_drill_high_tension_in_range():
    """High tension drill: 2.5 ≤ σ < 3.0."""
    packet = mock_drill_scenario("dr3_high_tension")
    sigma = packet["checklist"]["tension_sigma"]
    assert 2.5 <= sigma < 3.0


def test_mock_drill_falsified_sigma_ge_3():
    """Falsified drill: σ ≥ 3.0."""
    packet = mock_drill_scenario("dr3_falsified")
    sigma = packet["checklist"]["tension_sigma"]
    assert sigma >= 3.0


# ---------------------------------------------------------------------------
# publication_day_runbook_report
# ---------------------------------------------------------------------------


def test_runbook_report_has_four_drills():
    report = publication_day_runbook_report()
    assert "drills" in report
    assert len(report["drills"]) == 4


def test_runbook_report_has_mandatory_files():
    report = publication_day_runbook_report()
    assert "mandatory_files" in report
    assert len(report["mandatory_files"]) == 7


def test_runbook_report_has_dr2_baseline():
    report = publication_day_runbook_report()
    assert "desi_dr2_baseline" in report
    baseline = report["desi_dr2_baseline"]
    assert "wa_central" in baseline
    assert "tension_sigma" in baseline


def test_runbook_report_dr2_tension_about_2sigma():
    report = publication_day_runbook_report()
    tension = report["desi_dr2_baseline"]["tension_sigma"]
    assert 2.0 < tension < 2.5


def test_runbook_report_all_four_verdict_types():
    report = publication_day_runbook_report()
    verdicts = {d["checklist"]["verdict"] for d in report["drills"]}
    assert verdicts == {"CONSISTENT", "TENSION", "HIGH_TENSION", "FALSIFIED"}


def test_runbook_report_has_version():
    report = publication_day_runbook_report()
    assert "version" in report


def test_runbook_report_has_verdict_thresholds():
    report = publication_day_runbook_report()
    assert "verdict_thresholds" in report
    assert "CONSISTENT" in report["verdict_thresholds"]
    assert "FALSIFIED" in report["verdict_thresholds"]


# ---------------------------------------------------------------------------
# Pillar 285 pre-registration + DR3 readiness checklist (new)
# ---------------------------------------------------------------------------


def test_pillar_285_module_constant():
    assert "pillar285" in PILLAR_285_MODULE
    assert PILLAR_285_MODULE.endswith(".py")


def test_dr3_timeline_year():
    assert isinstance(DR3_TIMELINE_YEAR, int)
    assert DR3_TIMELINE_YEAR >= 2027


def test_confirm_pillar285_preregistration_structure():
    p285 = confirm_pillar285_preregistration()
    for key in (
        "pillar_285_module",
        "preregistered",
        "current_desi_status",
        "falsification_trigger",
        "four_extensions",
        "recommended_extension_if_falsified",
        "dr3_timeline_year",
        "purpose",
    ):
        assert key in p285


def test_confirm_pillar285_preregistered_is_true():
    p285 = confirm_pillar285_preregistration()
    assert p285["preregistered"] is True


def test_confirm_pillar285_four_extensions():
    p285 = confirm_pillar285_preregistration()
    assert len(p285["four_extensions"]) == 4
    assert "Bulk Scalar" in p285["four_extensions"][0]


def test_confirm_pillar285_current_status_not_falsified():
    p285 = confirm_pillar285_preregistration()
    assert "NOT FALSIFIED" in p285["current_desi_status"]


def test_confirm_pillar285_falsification_trigger_is_3sigma():
    p285 = confirm_pillar285_preregistration()
    assert "3.0" in p285["falsification_trigger"]


def test_confirm_pillar285_recommended_extension():
    p285 = confirm_pillar285_preregistration()
    assert "Bulk Scalar" in p285["recommended_extension_if_falsified"]


def test_dr3_readiness_checklist_all_pass():
    result = dr3_readiness_checklist()
    assert result["all_checks_pass"] is True


def test_dr3_readiness_checklist_structure():
    result = dr3_readiness_checklist()
    assert "checks" in result
    assert "pillar_285_status" in result
    assert isinstance(result["checks"], list)
    assert len(result["checks"]) == 6


def test_dr3_readiness_each_check_has_name_pass_detail():
    result = dr3_readiness_checklist()
    for check in result["checks"]:
        assert "name" in check
        assert "pass" in check
        assert "detail" in check
        assert isinstance(check["pass"], bool)


def test_dr3_readiness_pillar_285_check_passes():
    result = dr3_readiness_checklist()
    p285_check = next(c for c in result["checks"] if c["name"] == "pillar_285_preregistered")
    assert p285_check["pass"] is True


def test_dr3_readiness_all_drill_scenarios_executable():
    result = dr3_readiness_checklist()
    drill_check = next(c for c in result["checks"] if "drill" in c["name"])
    assert drill_check["pass"] is True


def test_dr3_readiness_dr2_tension_below_falsification():
    result = dr3_readiness_checklist()
    tension_check = next(c for c in result["checks"] if "baseline_tension" in c["name"])
    assert tension_check["pass"] is True
    # DR2 tension should be ~2.07σ, well below 3.0
    assert "2." in tension_check["detail"]


def test_dr3_readiness_falsification_threshold_check():
    result = dr3_readiness_checklist()
    threshold_check = next(c for c in result["checks"] if "threshold" in c["name"])
    assert threshold_check["pass"] is True
    assert "3.0" in threshold_check["detail"]


def test_dr3_readiness_timeline_documented():
    result = dr3_readiness_checklist()
    timeline_check = next(c for c in result["checks"] if "timeline" in c["name"])
    assert timeline_check["pass"] is True
    assert "2027" in timeline_check["detail"]
