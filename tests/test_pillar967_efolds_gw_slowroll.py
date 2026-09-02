# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 967 — N_e Derivation from GW Slow-Roll."""

import math
import pytest
from src.core.pillar967_efolds_gw_slowroll import (
    K_CS,
    N_W,
    PHI0,
    N_S_UM,
    R_BRAIDED,
    N_E_DERIVED,
    N_E_WINDOW_LOW,
    N_E_WINDOW_HIGH,
    PILLAR_STATUS,
    PILLAR_VALID,
    ns_and_r_values,
    efolds_from_ns_r,
    efolds_window,
    efolds_gw_geometry,
    fallibility_update,
    pillar967_summary,
)


def test_pillar_status():
    assert PILLAR_STATUS == "EFOLDS_DERIVED_WINDOW"


def test_pillar_valid():
    assert PILLAR_VALID is True


def test_constants():
    assert K_CS == 74
    assert N_W == 5
    assert PHI0 == pytest.approx(1.0)


def test_observable_constants():
    assert N_S_UM == pytest.approx(0.9635)
    assert R_BRAIDED == pytest.approx(0.0315)


def test_derived_efolds_constant():
    expected = (R_BRAIDED / 8.0 + 2.0) / (1.0 - N_S_UM)
    assert N_E_DERIVED == pytest.approx(expected)


def test_window_constants():
    assert N_E_WINDOW_LOW == pytest.approx(0.9 * N_E_DERIVED)
    assert N_E_WINDOW_HIGH == pytest.approx(1.1 * N_E_DERIVED)


def test_ns_and_r_values_function():
    result = ns_and_r_values()
    assert result["n_s"] == pytest.approx(N_S_UM)
    assert result["r"] == pytest.approx(R_BRAIDED)
    assert result["source"] == "UM_geometry"


def test_efolds_from_ns_r_formula():
    result = efolds_from_ns_r()
    assert result["formula"] == "(r/8 + 2)/(1 - n_s)"
    assert result["derived_not_assumed"] is True


def test_efolds_from_ns_r_value():
    result = efolds_from_ns_r()
    assert result["N_e"] == pytest.approx(N_E_DERIVED)


def test_window_in_standard_range():
    result = efolds_window()
    assert result["in_standard_range"] is True
    assert result["window_overlaps_standard_range"] is True


def test_window_bounds_are_order_55_pm_5():
    result = efolds_window()
    assert 49.0 < result["N_e_low"] < 50.0
    assert 60.0 < result["N_e_high"] < 61.0


def test_geometry_returns_dict():
    result = efolds_gw_geometry()
    assert isinstance(result, dict)


def test_geometry_field_range_within_phi0():
    result = efolds_gw_geometry()
    assert result["field_range_within_phi0"] is True
    assert result["field_range_required"] < PHI0


def test_geometry_warp_factor_small():
    result = efolds_gw_geometry()
    assert result["warp_factor"] < 1.0e-40
    assert result["geometric_consistency"] is True


def test_fallibility_update_upgrade():
    result = fallibility_update()
    assert result["pillar"] == 967
    assert result["previous_status"] == "STANDARD_ASSUMPTION"
    assert result["new_status"] == "DERIVED_WINDOW"


def test_summary_identity():
    result = pillar967_summary()
    assert result["pillar"] == 967
    assert result["status"] == PILLAR_STATUS
    assert result["valid"] is True


def test_summary_contains_sections():
    result = pillar967_summary()
    for key in ("observables", "derived_efolds", "window", "gw_geometry", "fallibility_update"):
        assert key in result


def test_summary_derivation_chain_length():
    result = pillar967_summary()
    assert len(result["derivation_chain"]) >= 5
