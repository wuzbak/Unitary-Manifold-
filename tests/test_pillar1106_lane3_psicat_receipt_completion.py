# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1106_lane3_psicat_receipt_completion import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    lane3_psicat_receipt_completion,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1106
    assert PILLAR_GATE == 'LANE3_PSICAT_RECEIPT_COMPLETION'
    assert PILLAR_STATUS == 'LANE3_PSICAT_RECEIPT_COMPLETION_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1107


def test_lane3_contract() -> None:
    report = lane3_psicat_receipt_completion()
    assert report['outcome'] in {'LANE3_PSICAT_RECEIPT_COMPLETION_READY', 'LANE3_PSICAT_RECEIPT_COMPLETION_BLOCKED'}
    assert report['dependencies']['formal_proof_foundry_queue_items_present'] is True
    assert report['dependencies']['stage_receipt_visibility_present'] is True
    assert report['dependencies']['new_reviewer_packets_present'] is True
    assert report['co_runner_mode']['openrouter_compatibility_only'] is True
