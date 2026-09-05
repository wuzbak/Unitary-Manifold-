# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Regression bookkeeping must not promote an unsupported solver to closure."""
import json

import pytest

from src.core import pillar819_sprint_ax_regression_certificate as certificate
from src.core import pillar818_full_backreacted_boltzmann as boltzmann


def test_historical_inventory_is_preserved_not_promoted_to_proof():
    result = certificate.validate_sprint()
    assert certificate.PILLAR_NUMBER == 819
    assert [pillar["number"] for pillar in certificate.PILLARS] == [818]
    assert result["lean4_start"] == 1386
    assert result["lean4_end"] == 1411
    assert result["lean4_delta"] == 25
    assert result["next_pillar_slot"] == 820
    assert result["lean4_evidence"] == "historical inventory, not solver verification"


def test_valid_bookkeeping_explicitly_reports_unsupported_physics():
    result = certificate.validate_sprint()
    assert certificate.SPRINT_VALID is True
    assert result["valid"]
    assert result["errors"] == []
    assert result["status"] == "UNSUPPORTED"
    assert result["validation_scope"] == "bookkeeping and unsupported-boundary consistency only"
    assert not result["full_5d_boltzmann_closed"]
    assert not result["closure_earned"]
    assert result["boltzmann_gate"] == boltzmann.PILLAR_GATE
    assert result["a_br_median"] is None
    assert result["a_br_max"] is None
    assert result["delta_cl_median"] is None
    assert set(boltzmann.OPEN_ITEMS).issubset(result["open_items"])
    json.dumps(result, allow_nan=False)


@pytest.mark.parametrize("changes", [
    {"gate": "FULL_5D_BOLTZMANN_CLOSED"}, {"converged": True},
    {"a_br_median": 0.0}, {"a_br_max": 0.0}, {"delta_cl_median": 0.0},
    {"n_modes": 1}, {"n_iter_max": 1}, {"mode_results": [0]}, {"open_items": []},
])
def test_certificate_rejects_fabricated_execution_or_zero_predictions(monkeypatch, changes):
    result = boltzmann.run_full_backreacted_boltzmann()._replace(**changes)
    monkeypatch.setattr(certificate, "run_full_backreacted_boltzmann", lambda **kwargs: result)
    report = certificate.validate_sprint()
    assert not report["valid"]
    assert report["status"] == "FAIL"
    assert report["errors"]
    assert not report["closure_earned"]


def test_certificate_rejects_stale_closure_constant(monkeypatch):
    monkeypatch.setattr(certificate, "FULL_5D_BOLTZMANN_CLOSED", True)
    report = certificate.validate_sprint()
    assert not report["valid"]
    assert report["errors"]
    assert not report["closure_earned"]


def test_report_does_not_expose_mutable_open_item_registry():
    certificate.validate_sprint()["open_items"].clear()
    assert certificate.validate_sprint()["open_items"]
