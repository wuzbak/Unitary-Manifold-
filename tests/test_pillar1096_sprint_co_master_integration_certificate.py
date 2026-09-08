# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1096_sprint_co_master_integration_certificate import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    sprint_co_master_integration_certificate,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1096
    assert PILLAR_GATE == 'SPRINT_CO_MASTER_INTEGRATION_CERTIFICATE'
    assert PILLAR_STATUS == 'SPRINT_CO_MASTER_INTEGRATION_CERTIFICATE_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1097


def test_master_integration_contract() -> None:
    report = sprint_co_master_integration_certificate()
    assert report['outcome'] in {'SPRINT_CO_MASTER_INTEGRATION_CERTIFICATE_READY', 'SPRINT_CO_MASTER_INTEGRATION_CERTIFICATE_BLOCKED'}
    assert 'lean_burden_ledger' in report['lane_packets']
    assert 'status_coherence' in report['lane_packets']
    assert len(report['definition_of_done']) == 5
