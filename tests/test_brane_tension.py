# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC

from src.core.brane_tension_stabilization import (
    brane_tensions_from_winding,
    kr_c_from_tension_balance,
    phi_min_from_three_sector,
    brane_tension_stabilization_report,
)


def test_tension_squares_and_sum():
    t = brane_tensions_from_winding()
    assert t["T_UV"] == 25.0
    assert t["T_IR"] == 49.0
    assert t["sum_squares"] == 74.0


def test_kr_c_candidate_matches_2n():
    out = kr_c_from_tension_balance()
    assert out["kr_c"] == 12.0
    assert out["status"] == "FITTED"


def test_phi_min_candidate_matches_3n():
    out = phi_min_from_three_sector()
    assert out["phi_min_bare"] == 18.0
    assert out["status"] == "FITTED"


def test_stabilization_report_keys():
    report = brane_tension_stabilization_report()
    assert "tensions" in report
    assert "kr_c_result" in report
    assert "phi_min_result" in report
    assert report["status"] == "FITTED"
