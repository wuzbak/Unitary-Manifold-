# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for screening leads and public verification reports."""

import pytest

from eige.report import FAILED, NOT_CHECKED, VERIFIED, WARNING, OUT_OF_SCOPE, CheckResult, VerificationReport
from eige.screening import DISCLAIMER, EVIDENTIARY_STATUS, residual_vote_outliers, turnout_outliers


def test_screening_leads_carry_non_evidence_status_and_disclaimer():
    units = [{"id": f"p{i}", "registered": 100, "ballots": 45 + (i % 5)} for i in range(20)] + [{"id": "odd", "registered": 100, "ballots": 95}]
    leads = turnout_outliers(units)
    assert len(leads) == 1
    lead = leads[0].as_dict()
    assert lead["unit_id"] == "odd"
    assert lead["evidentiary_status"] == EVIDENTIARY_STATUS
    assert lead["disclaimer"] == DISCLAIMER
    assert "not evidence" in lead["disclaimer"]


def test_residual_outlier_and_invalid_unit_rejections():
    units = [{"id": f"p{i}", "ballots": 100, "valid_votes": 96 + (i % 4)} for i in range(20)] + [{"id": "resid", "ballots": 100, "valid_votes": 60}]
    assert residual_vote_outliers(units)[0].unit_id == "resid"
    with pytest.raises(ValueError):
        turnout_outliers([{"id": "bad", "registered": 0, "ballots": 1}])
    with pytest.raises(ValueError):
        residual_vote_outliers([{"id": "bad", "ballots": 1, "valid_votes": 2}])


def test_report_renders_all_audiences_with_limits_and_not_checked_items():
    report = VerificationReport("Example election")
    report.add("root", VERIFIED, "matches")
    report.add("audit", WARNING, "development key")
    report.add("paper audit", NOT_CHECKED, "not supplied")
    assert report.passed
    as_dict = report.as_dict()
    assert as_dict["counts"][NOT_CHECKED] == 1
    for audience in ["official", "court", "voter"]:
        rendered = report.render(audience)
        assert ("not checked" in rendered.lower() or "not supplied" in rendered or "could not be run" in rendered.lower())
        assert any(limit in rendered for limit in OUT_OF_SCOPE)
    report.add("signature", FAILED, "bad")
    assert not report.passed
    assert "FAILED" in report.render("official")
    with pytest.raises(ValueError):
        CheckResult("x", "unknown", "bad")
    with pytest.raises(ValueError):
        report.render("alien")
