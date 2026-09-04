# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from src.core.pillar1043_cmb_irreducibility_continuation import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    cmb_irreducibility_continuation,
    pillar1043_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1043
    assert PILLAR_GATE == "CMB_IRREDUCIBILITY_CONTINUATION"
    assert PILLAR_STATUS == "CMB_IRREDUCIBILITY_CONTINUATION_COMPLETE"


def test_irreducibility_strengthened() -> None:
    report = cmb_irreducibility_continuation()
    assert report["demonstrable_reduction"] is True
    assert report["closure_earned"] is False
    assert report["valid"] is True


def test_named_missing_objects() -> None:
    report = cmb_irreducibility_continuation()
    assert len(report["named_missing_objects"]) == 2
    assert "global UV completion of transfer normalization" in report["named_missing_objects"]


def test_summary() -> None:
    summary = pillar1043_summary()
    assert PILLAR_VALID is True
    assert summary["status"] == PILLAR_STATUS
