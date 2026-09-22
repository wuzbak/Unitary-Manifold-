# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1125_lane3_monorepo_health_audit as p1125

from src.core.pillar1125_lane3_monorepo_health_audit import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    lane3_monorepo_health_audit,
    pillar1125_summary,
)


@pytest.fixture(scope="module")
def report():
    return lane3_monorepo_health_audit()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1125
    assert PILLAR_GATE == 'LANE3_MONOREPO_HEALTH_AUDIT'
    assert PILLAR_STATUS == 'LANE3_MONOREPO_HEALTH_AUDIT_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1126
    assert isinstance(bool(PILLAR_VALID), bool)


def test_mas_tracker_yaml_validity_check_standalone() -> None:
    result = p1125._mas_tracker_yaml_validity_check()
    assert result['parses_as_valid_yaml'] is True
    assert result['has_canonical_status_notice'] is True
    assert result['has_labeled_legacy_archive'] is True
    assert result['ok'] is True


def test_checks_present(report) -> None:
    checks = report['checks']
    assert 'large_directory_hygiene' in checks
    assert 'onboarding_docs_consistency' in checks
    assert 'internal_link_audit' in checks
    assert 'mas_tracker_yaml_validity' in checks
    assert checks['mas_tracker_yaml_validity']['ok'] is True


def test_dependencies(report) -> None:
    deps = report['dependencies']
    assert deps['pillar1122_valid'] is True
    assert deps['large_directory_check_pass'] is True
    assert deps['onboarding_consistency_check_pass'] is True
    assert deps['mas_tracker_yaml_valid'] is True


def test_remediation_this_sprint_honest(report) -> None:
    remediation = report['remediation_this_sprint']
    assert len(remediation) == 2
    findings = {item['finding'] for item in remediation}
    assert any('tests/' in f for f in findings)
    assert any('mas_tracker.yml' in f for f in findings)
    for item in remediation:
        assert item['status'] == 'RESOLVED_THIS_SPRINT'


def test_known_non_gating_findings_tracked_honestly(report) -> None:
    findings = report['known_non_gating_findings']
    assert len(findings) == 1
    assert findings[0]['gated_in_ci'] is False
    assert findings[0]['status'] == 'TRACKED_NOT_FIXED_THIS_SPRINT'


def test_truth_surface_sync(report) -> None:
    assert report['truth_surface_sync']['all_pass'] is True
    assert report['valid'] is True


def test_invalid_if_mas_tracker_yaml_check_breaks(monkeypatch) -> None:
    monkeypatch.setattr(
        p1125,
        '_mas_tracker_yaml_validity_check',
        lambda: {'ok': False, 'parses_as_valid_yaml': False},
    )
    p1125.lane3_monorepo_health_audit.cache_clear()
    try:
        report = p1125.lane3_monorepo_health_audit()
        assert report['valid'] is False
        assert report['dependencies']['mas_tracker_yaml_valid'] is False
    finally:
        p1125.lane3_monorepo_health_audit.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1125_summary()
    assert summary['pillar'] == 1125
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
