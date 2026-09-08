# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1093_validation_resilience_scoped_security import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    validation_resilience_scoped_security,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1093
    assert PILLAR_GATE == 'VALIDATION_RESILIENCE_SCOPED_SECURITY'
    assert PILLAR_STATUS == 'VALIDATION_RESILIENCE_SCOPED_SECURITY_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1094


def test_validation_packet_contract() -> None:
    report = validation_resilience_scoped_security()
    assert report['outcome'] in {'VALIDATION_RESILIENCE_SCOPED_SECURITY_READY', 'VALIDATION_RESILIENCE_SCOPED_SECURITY_BLOCKED'}
    assert report['dependencies']['workflow_surfaces_present'] is True
    assert len(report['changed_surface_first_targets']) >= 4
    assert 'codeql_oversize' in report['missing_signal_policy']
