# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1092_psicat_formal_training_integration import (
    NEXT_PILLAR_SLOT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    psicat_formal_training_integration,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1092
    assert PILLAR_GATE == 'PSICAT_FORMAL_TRAINING_INTEGRATION'
    assert PILLAR_STATUS == 'PSICAT_FORMAL_TRAINING_INTEGRATION_COMPLETE'
    assert NEXT_PILLAR_SLOT == 1093


def test_training_integration_contract() -> None:
    report = psicat_formal_training_integration()
    assert report['outcome'] in {'PSICAT_FORMAL_TRAINING_INTEGRATION_READY', 'PSICAT_FORMAL_TRAINING_INTEGRATION_BLOCKED'}
    assert report['dependencies']['formal_proof_foundry_family_present'] is True
    assert report['dependencies']['proof_foundry_queue_items_present'] is True
    assert report['artifact_bundle']['formal_proof_foundry_bundle']['program'] == 'FORMAL_PROOF_FOUNDRY'
