# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1122_sprint_cv_master_charter as p1122

from src.core.pillar1122_sprint_cv_master_charter import (
    FINAL_SPRINT_NEXT_SLOT,
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    SPRINT,
    VERSION,
    pillar1122_summary,
    sprint_cv_master_charter,
)


@pytest.fixture(scope="module")
def report():
    return sprint_cv_master_charter()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1122
    assert PILLAR_GATE == 'SPRINT_CV_MASTER_CHARTER'
    assert PILLAR_STATUS == 'SPRINT_CV_MASTER_CHARTER_COMPLETE'
    assert VERSION == 'v38.0'
    assert SPRINT == 'CV'
    assert NEXT_PILLAR_SLOT == 1123
    assert FINAL_SPRINT_NEXT_SLOT == 1129
    assert isinstance(bool(PILLAR_VALID), bool)


def test_report_contract(report) -> None:
    assert report['outcome'] == 'SPRINT_CV_MASTER_CHARTER_READY'
    assert report['valid'] is True
    assert report['truth_surface_sync']['all_pass'] is True
    assert report['scope']['lane1_physics']
    assert report['scope']['lane2_psicat']
    assert report['scope']['lane3_health']
    assert len(report['definition_of_done']) == 4


def test_dependencies(report) -> None:
    deps = report['dependencies']
    assert deps['pillar1121_valid'] is True
    assert deps['truth_surfaces_synchronized_to_v38_0'] is True


def test_invalid_if_pillar1121_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1122, 'P1121_VALID', False)
    p1122.sprint_cv_master_charter.cache_clear()
    try:
        report = p1122.sprint_cv_master_charter()
        assert report['valid'] is False
        assert report['dependencies']['pillar1121_valid'] is False
    finally:
        p1122.sprint_cv_master_charter.cache_clear()


def test_invalid_if_truth_sync_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1122, '_truth_surface_sync_status', lambda: {'all_pass': False, 'files': []})
    p1122.sprint_cv_master_charter.cache_clear()
    try:
        report = p1122.sprint_cv_master_charter()
        assert report['valid'] is False
    finally:
        p1122.sprint_cv_master_charter.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1122_summary()
    assert summary['pillar'] == 1122
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
    assert summary['valid'] is True
