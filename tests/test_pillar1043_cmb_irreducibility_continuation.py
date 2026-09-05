# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

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


def test_no_transfer_calculation_means_no_tightening() -> None:
    report = cmb_irreducibility_continuation()
    assert report["demonstrable_reduction"] is False
    assert report["scientific_progress"] is False
    assert report["deficit_after"] == report["deficit_before"]
    assert report["residual_budget_after"] == report["dependency"]["residual_budget_delta"]["after"]
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


@pytest.mark.parametrize("interval", [
    {"lower": float("nan"), "upper": 5.15},
    {"lower": 4.0, "upper": 3.0},
    {"lower": 0.0, "upper": 5.15},
])
def test_invalid_inherited_intervals_do_not_validate_packet(monkeypatch, interval) -> None:
    import src.core.pillar1043_cmb_irreducibility_continuation as module

    prior = module.parallel_cmb_closure_campaign()
    prior["deficit_after"] = interval
    monkeypatch.setattr(module, "parallel_cmb_closure_campaign", lambda: prior)
    report = module.cmb_irreducibility_continuation()
    assert report["packet_valid"] is False
    assert report["closure_earned"] is False
    assert report["scientific_progress"] is False
