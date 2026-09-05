# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

import pytest

import src.core.pillar1071_extension_free_parameter_audit as module

from src.core.pillar1071_extension_free_parameter_audit import (
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_VALID,
    extension_free_parameter_audit,
    pillar1071_summary,
)


def test_identity() -> None:
    assert PILLAR_NUMBER == 1071
    assert PILLAR_GATE == "SPRINT_CF_TRACK_B_EXTENSION_FREE_PARAMETER_AUDIT"
    assert PILLAR_STATUS == "SPRINT_CF_TRACK_B_EXTENSION_FREE_PARAMETER_AUDIT_COMPLETE"
    assert PILLAR_VALID is True


def test_empty_declarations_do_not_establish_zero_parameters() -> None:
    r = extension_free_parameter_audit()
    assert r["total_new_free_parameters"] is None
    assert r["parameter_free_extension"] is None
    assert r["parameter_inventory_complete"] is False
    assert all(row["free_parameter_count"] is None for row in r["per_pillar"])
    assert r["all_new_free_parameters"] == []


def test_covers_three_track_b_pillars() -> None:
    r = extension_free_parameter_audit()
    assert {row["pillar"] for row in r["per_pillar"]} == {1068, 1069, 1070}


def test_summary() -> None:
    s = pillar1071_summary()
    assert s["pillar"] == 1071
    assert s["parameter_free_extension"] is None


@pytest.mark.parametrize("count,evidence", [(False, ["inventory"]), (0, []), (0, [""]), (1, ["inventory"]), (0, "inventory")])
def test_inventory_flags_alone_or_inconsistent_counts_are_rejected(monkeypatch, count, evidence) -> None:
    report = module.cw_quartic_extension_report()
    report.update(parameter_inventory_complete=True, free_parameter_count=count,
                  parameter_inventory_evidence=evidence, closure_earned=True)
    monkeypatch.setattr(module, "cw_quartic_extension_report", lambda: report)
    audit = module.extension_free_parameter_audit()
    row = audit["per_pillar"][0]
    assert row["free_parameter_count"] is None
    assert row["closure_earned"] is False
    assert audit["parameter_free_extension"] is None


def test_complete_inventory_is_distinct_from_physical_closure(monkeypatch) -> None:
    for name in ("cw_quartic_extension_report", "ftheory_spectral_cover_report", "as_mechanism_report"):
        report = getattr(module, name)()
        report.update(parameter_inventory_complete=True, free_parameter_count=0,
                      parameter_inventory_evidence=["independent inventory result"])
        monkeypatch.setattr(module, name, lambda report=report: report)
    audit = module.extension_free_parameter_audit()
    assert audit["parameter_free_extension"] is True
    assert audit["total_new_free_parameters"] == 0
    assert all(row["closure_earned"] is False for row in audit["per_pillar"])


def test_unverified_parameter_declarations_stay_out_of_established_aggregate(monkeypatch) -> None:
    unknown = module.cw_quartic_extension_report()
    unknown["free_parameters_introduced"] = ["unverified_modulus"]
    known = module.ftheory_spectral_cover_report()
    known.update(free_parameters_introduced=["verified_modulus"], free_parameter_count=1,
                 parameter_inventory_complete=True, parameter_inventory_evidence=["inventory"])
    monkeypatch.setattr(module, "cw_quartic_extension_report", lambda: unknown)
    monkeypatch.setattr(module, "ftheory_spectral_cover_report", lambda: known)
    audit = module.extension_free_parameter_audit()
    assert audit["all_new_free_parameters"] == ["verified_modulus"]
    assert audit["per_pillar"][0]["free_parameters_introduced"] == ["unverified_modulus"]
    assert audit["per_pillar"][0]["free_parameter_count"] is None
    assert audit["total_new_free_parameters"] is None
