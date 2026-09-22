# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1127_sprint_cv_status_coherence_certificate as p1127

from src.core.pillar1127_sprint_cv_status_coherence_certificate import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    pillar1127_summary,
    sprint_cv_status_coherence_certificate,
)


@pytest.fixture(scope="module")
def report():
    return sprint_cv_status_coherence_certificate()


def test_identity() -> None:
    assert PILLAR_NUMBER == 1127
    assert PILLAR_GATE == 'SPRINT_CV_STATUS_COHERENCE_CERTIFICATE'
    assert PILLAR_STATUS == 'SPRINT_CV_STATUS_COHERENCE_CERTIFICATE_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1128
    assert isinstance(bool(PILLAR_VALID), bool)


def test_all_lane_dependencies_present(report) -> None:
    deps = report['dependencies']
    for key in (
        'pillar1122_valid',
        'pillar1123_valid',
        'pillar1124_valid',
        'pillar1125_valid',
        'pillar1126_valid',
        'truth_surfaces_synchronized_to_v38_0',
    ):
        assert deps[key] is True


def test_truth_surface_sync_covers_all_canonical_surfaces(report) -> None:
    sync = report['truth_surface_sync']
    assert sync['all_pass'] is True
    paths = {f['path'] for f in sync['files']}
    assert any(p.endswith('STATUS.md') for p in paths)
    assert any(p.endswith('mas_tracker.yml') for p in paths)
    assert any(p.endswith('FALLIBILITY.md') for p in paths)
    assert any(p.endswith('CLAIM_MASTER_BOARD.md') for p in paths)
    assert any(p.endswith('GATEKEEPER_SUMMARY.md') for p in paths)
    assert any(p.endswith('TRUTH_LAYER.md') for p in paths)
    assert any(p.endswith('WAVE_CHANGELOG.md') for p in paths)
    assert any(p.endswith('SPRINT_PLAN.md') for p in paths)
    assert any(p.endswith('um_live_status.json') for p in paths)


def test_valid(report) -> None:
    assert report['valid'] is True


def test_invalid_if_pillar1126_breaks(monkeypatch) -> None:
    monkeypatch.setattr(p1127, 'P1126_VALID', False)
    p1127.sprint_cv_status_coherence_certificate.cache_clear()
    try:
        report = p1127.sprint_cv_status_coherence_certificate()
        assert report['valid'] is False
    finally:
        p1127.sprint_cv_status_coherence_certificate.cache_clear()


def test_summary_contract(report) -> None:
    summary = pillar1127_summary()
    assert summary['pillar'] == 1127
    assert summary['status'] == PILLAR_STATUS
    assert summary['outcome'] == report['outcome']
