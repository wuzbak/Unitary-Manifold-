# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 287 — Short-Cycle Assignment Derivation."""
import math
import pytest
from src.core.pillar287_short_cycle_assignment_derivation import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    K_CS,
    N1,
    N2,
    PI_KR,
    GW_EPSILON,
    separation_guard,
    gw_two_radius_potential,
    gw_minimum_radius_ordering,
    kk_mass_ordering_argument,
    convention_279_3_derivation_status,
    short_cycle_derivation_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 287


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 287
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert g["partially_derives_convention_279_3"] is True


def test_constants_braid_pair():
    assert N1 == 5
    assert N2 == 7
    assert K_CS == 74
    assert PI_KR == 37


def test_gw_potential_returns_float():
    v = gw_two_radius_potential(7.4, 5.286)
    assert isinstance(v, float)
    assert math.isfinite(v)


def test_gw_potential_positive_when_kR1_large():
    # (7.4)^4 >> epsilon*(5.286)^4 for epsilon=0.1
    v = gw_two_radius_potential(7.4, 5.286)
    assert v > 0.0


def test_gw_potential_raises_zero_kR1():
    with pytest.raises(ValueError):
        gw_two_radius_potential(0.0, 5.0)


def test_gw_potential_raises_zero_kR2():
    with pytest.raises(ValueError):
        gw_two_radius_potential(7.4, 0.0)


def test_gw_potential_raises_negative():
    with pytest.raises(ValueError):
        gw_two_radius_potential(-1.0, 5.0)


def test_gw_minimum_ordering_keys():
    r = gw_minimum_radius_ordering()
    for key in ("kR_n1", "kR_n2", "V_n1_primary", "V_n2_primary",
                "ordering_favors_n1_primary", "nw_assignment"):
        assert key in r


def test_gw_minimum_kR_values():
    r = gw_minimum_radius_ordering()
    assert abs(r["kR_n1"] - PI_KR / N1) < 1e-10
    assert abs(r["kR_n2"] - PI_KR / N2) < 1e-10


def test_gw_minimum_potentials_finite():
    r = gw_minimum_radius_ordering()
    assert math.isfinite(r["V_n1_primary"])
    assert math.isfinite(r["V_n2_primary"])


def test_kk_mass_ordering_keys():
    r = kk_mass_ordering_argument()
    for key in ("kR_n1", "kR_n2", "larger_kR", "argument"):
        assert key in r


def test_kk_mass_values_positive():
    r = kk_mass_ordering_argument()
    assert r["kR_n1"] > 0.0
    assert r["kR_n2"] > 0.0


def test_convention_279_3_status_keys():
    r = convention_279_3_derivation_status()
    for key in ("status", "gap_name", "gap_description", "convention_279_3_fully_derived"):
        assert key in r


def test_convention_279_3_gap_name():
    r = convention_279_3_derivation_status()
    assert r["gap_name"] == "CYCLE_RADION_COUPLING_UNIQUENESS"


def test_convention_279_3_not_fully_derived():
    r = convention_279_3_derivation_status()
    assert r["convention_279_3_fully_derived"] is False


def test_convention_279_3_status_value():
    r = convention_279_3_derivation_status()
    assert r["status"] in ("PARTIALLY_DERIVED_GW_ORDERING", "AMBIGUOUS_GW_ORDERING")


def test_short_cycle_report_pillar():
    r = short_cycle_derivation_report()
    assert r["pillar"] == 287


def test_short_cycle_report_has_all_sections():
    r = short_cycle_derivation_report()
    for key in ("separation_guard", "gw_potential_ordering", "kk_mass_argument", "derivation_status"):
        assert key in r
