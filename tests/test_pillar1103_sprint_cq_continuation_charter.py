# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1103_sprint_cq_continuation_charter import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    sprint_cq_continuation_charter,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1103
    assert PILLAR_GATE == 'SPRINT_CQ_CONTINUATION_CHARTER'
    assert PILLAR_STATUS == 'SPRINT_CQ_CONTINUATION_CHARTER_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1104


def test_charter_contract() -> None:
    report = sprint_cq_continuation_charter()
    assert report['outcome'] in {'SPRINT_CQ_CONTINUATION_CHARTER_READY', 'SPRINT_CQ_CONTINUATION_CHARTER_BLOCKED'}
    assert len(report['lane_charter']) == 3
    assert report['definition_of_done']['lane_2'].startswith('audit only Lane 1 touched units')
