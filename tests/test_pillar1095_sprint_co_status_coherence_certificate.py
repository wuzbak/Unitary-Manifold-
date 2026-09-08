# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1095_sprint_co_status_coherence_certificate import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    sprint_co_status_coherence_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1095
    assert PILLAR_GATE == 'SPRINT_CO_STATUS_COHERENCE_CERTIFICATE'
    assert PILLAR_STATUS == 'SPRINT_CO_STATUS_COHERENCE_CERTIFICATE_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1096


def test_status_coherence_contract() -> None:
    report = sprint_co_status_coherence_certificate()
    assert report['outcome'] in {'SPRINT_CO_STATUS_COHERENCE_CERTIFICATE_READY', 'SPRINT_CO_STATUS_COHERENCE_CERTIFICATE_BLOCKED'}
    assert 'pillar1094_valid' in report['dependencies']
    assert 'truth_surface_sync' in report
