# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 979 — Sprint BJ Master Regression Certificate."""
import pytest
from src.core.pillar979_sprint_bj_regression_certificate import (
    PILLAR_STATUS, PILLAR_VALID,
    SPRINT_NAME, VERSION, SPRINT_PILLARS, NEXT_PILLAR_SLOT,
    LEAN4_START, LEAN4_END, LEAN4_DELTA,
    STATUS_964, VALID_964, STATUS_965, VALID_965,
    STATUS_966, VALID_966, STATUS_967, VALID_967,
    STATUS_968, VALID_968, STATUS_969, VALID_969,
    STATUS_970, VALID_970, STATUS_971, VALID_971,
    STATUS_972, VALID_972, STATUS_973, VALID_973,
    STATUS_974, VALID_974, STATUS_975, VALID_975,
    STATUS_976, VALID_976, STATUS_977, VALID_977,
    STATUS_978, VALID_978,
    sprint_bj_outcome_table, sprint_bj_regression_report, pillar979_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "SPRINT_BJ_REGRESSION_CERTIFICATE_COMPLETE"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_sprint_name():
    assert SPRINT_NAME == "BJ"


def test_version():
    assert VERSION == "v33.0"


def test_next_pillar_slot():
    assert NEXT_PILLAR_SLOT == 980


def test_sprint_pillars():
    assert 964 in SPRINT_PILLARS
    assert 979 in SPRINT_PILLARS
    assert len(SPRINT_PILLARS) == 16  # 964..979 inclusive


def test_lean4_start():
    assert LEAN4_START == 3812


def test_lean4_end():
    assert LEAN4_END == 3912


def test_lean4_delta():
    assert LEAN4_DELTA == 100


def test_all_pillars_valid():
    valids = [
        VALID_964, VALID_965, VALID_966, VALID_967, VALID_968,
        VALID_969, VALID_970, VALID_971, VALID_972, VALID_973,
        VALID_974, VALID_975, VALID_976, VALID_977, VALID_978,
    ]
    assert all(valids)


def test_p964_status():
    assert STATUS_964 == "CL_PHYS_ANALYTICALLY_DERIVED"


def test_p965_status():
    assert STATUS_965 == "QUARK_LEPTON_CL_SPLITTING_DERIVED"


def test_p967_status():
    assert STATUS_967 == "EFOLDS_DERIVED_WINDOW"


def test_p969_status():
    assert STATUS_969 == "A4_SYMMETRY_MECHANISM_IDENTIFIED"


def test_p970_status():
    assert STATUS_970 == "JARLSKOG_LAYER2_MECHANISM_PARTIAL"


def test_p972_status():
    assert STATUS_972 == "ISW_NLO_BOLTZMANN_BOUNDED"


def test_p973_status():
    assert STATUS_973 == "MNU1_GEOMETRIC_ESTIMATE"


def test_p974_status():
    assert STATUS_974 == "ETA_BAR_SPINSTRUCTURE_UNIQUENESS_PROVED"


def test_p975_status():
    assert STATUS_975 == "CMB_AS_LOWER_BOUND_SHARPENED"


def test_p976_status():
    assert STATUS_976 == "ALPHA_S_ROUTE_C_NONEXISTENT_CERTIFIED"


def test_p977_status():
    assert STATUS_977 == "HIGGS_MASS_CEILING_SHARPENED"


def test_outcome_table_length():
    outcomes = sprint_bj_outcome_table()
    assert len(outcomes) == 15  # P964..P978


def test_outcome_table_all_valid():
    outcomes = sprint_bj_outcome_table()
    assert all(o["valid"] for o in outcomes)


def test_regression_report_all_valid():
    report = sprint_bj_regression_report()
    assert report["all_valid"] is True


def test_regression_report_closures():
    report = sprint_bj_regression_report()
    assert len(report["closures_this_sprint"]) == 5


def test_regression_report_advances():
    report = sprint_bj_regression_report()
    assert len(report["advances_this_sprint"]) == 5


def test_regression_report_remaining_open():
    report = sprint_bj_regression_report()
    # Still have honest open items
    assert len(report["remaining_open"]) >= 8


def test_lean4_chain():
    report = sprint_bj_regression_report()
    assert report["lean4_end"] == report["lean4_start"] + report["lean4_delta"]


def test_pillar979_summary():
    s = pillar979_summary()
    assert s["pillar"] == 979
    assert s["next_pillar_slot"] == 980
    assert s["all_valid"] is True
    assert s["valid"] is True


def test_admission11_closed_in_closures():
    report = sprint_bj_regression_report()
    closures_str = " ".join(report["closures_this_sprint"])
    assert "Admission 11" in closures_str or "EFOLDS" in closures_str


def test_type_b_floors_in_remaining():
    report = sprint_bj_regression_report()
    remaining_str = " ".join(report["remaining_open"])
    assert "TYPE_B" in remaining_str or "IRREDUCIBLE" in remaining_str
