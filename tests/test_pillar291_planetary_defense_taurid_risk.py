# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 291 — Planetary Defense / Taurid Risk UM Intersection."""
import math
import pytest
from src.core.pillar291_planetary_defense_taurid_risk import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PHI_0,
    XI_C,
    TAURID_ANNUAL_RISK_PER_100M,
    DART_SUCCESS_YEAR,
    NEO_SURVEYOR_LAUNCH,
    separation_guard,
    taurid_encounter_risk_score,
    planetary_defense_readiness_index,
    um_phi_entropy_warning_capacity,
    cros_integration_with_taurid,
    taurid_risk_preregistration_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 291


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 291
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert g["integrates_cros_pillar237"] is True
    assert g["real_world_application"] is True


def test_phi_0_golden_ratio():
    assert abs(PHI_0 - (1 + math.sqrt(5)) / 2) < 1e-10


def test_xi_c_value():
    assert abs(XI_C - 35/74) < 1e-10


def test_dart_success_year():
    assert DART_SUCCESS_YEAR == 2022


def test_neo_surveyor_launch():
    assert NEO_SURVEYOR_LAUNCH == 2028


def test_taurid_risk_score_150m_2032_keys():
    r = taurid_encounter_risk_score(150.0, 2032)
    for key in ("object_diameter_m", "base_annual_risk", "years_warning",
                "detection_factor", "residual_risk", "verdict"):
        assert key in r


def test_taurid_risk_score_150m_2032_manageable():
    r = taurid_encounter_risk_score(150.0, 2032)
    assert r["verdict"] == "MANAGEABLE"


def test_taurid_risk_score_base_annual_risk_positive():
    r = taurid_encounter_risk_score(150.0, 2032)
    assert r["base_annual_risk"] > 0.0


def test_taurid_risk_score_scales_with_diameter():
    r100 = taurid_encounter_risk_score(100.0, 2032)
    r200 = taurid_encounter_risk_score(200.0, 2032)
    assert r200["base_annual_risk"] > r100["base_annual_risk"]


def test_taurid_risk_score_raises_non_positive_diameter():
    with pytest.raises(ValueError):
        taurid_encounter_risk_score(0.0, 2032)


def test_taurid_risk_score_years_warning_2026():
    # encounter_year == 2026 → years_warning == 0
    r = taurid_encounter_risk_score(150.0, 2026)
    assert r["years_warning"] == 0


def test_taurid_risk_score_detection_factor_bounded():
    r = taurid_encounter_risk_score(150.0, 2050)
    # detection_factor capped at 1.0
    assert r["detection_factor"] <= 1.0


def test_planetary_defense_readiness_keys():
    r = planetary_defense_readiness_index()
    for key in ("detection_score", "deflection_score", "warning_score",
                "readiness_index", "dart_validated", "assessment"):
        assert key in r


def test_planetary_defense_readiness_between_0_and_1():
    r = planetary_defense_readiness_index()
    assert 0.0 <= r["readiness_index"] <= 1.0


def test_planetary_defense_dart_validated():
    r = planetary_defense_readiness_index()
    assert r["dart_validated"] is True


def test_planetary_defense_assessment_operational():
    r = planetary_defense_readiness_index()
    assert r["assessment"] == "OPERATIONAL_WITH_GAPS"


def test_um_phi_entropy_capacity_ratio():
    r = um_phi_entropy_warning_capacity()
    assert abs(r["capacity_ratio"] - PHI_0 / XI_C) < 1e-8


def test_um_phi_entropy_keys():
    r = um_phi_entropy_warning_capacity()
    for key in ("phi_0", "xi_c", "capacity_ratio", "interpretation", "caveat"):
        assert key in r


def test_um_phi_entropy_capacity_positive():
    r = um_phi_entropy_warning_capacity()
    assert r["capacity_ratio"] > 1.0


def test_cros_integration_keys():
    r = cros_integration_with_taurid()
    for key in ("sector_weight", "um_capacity_ratio", "effective_taurid_warning_enhancement"):
        assert key in r


def test_cros_integration_enhancement_positive():
    r = cros_integration_with_taurid()
    assert r["effective_taurid_warning_enhancement"] > 0.0


def test_cros_integration_raises_zero_weight():
    with pytest.raises(ValueError):
        cros_integration_with_taurid(0.0)


def test_cros_integration_raises_weight_above_1():
    with pytest.raises(ValueError):
        cros_integration_with_taurid(1.5)


def test_taurid_report_pillar():
    r = taurid_risk_preregistration_report()
    assert r["pillar"] == 291


def test_taurid_report_has_sections():
    r = taurid_risk_preregistration_report()
    for key in ("separation_guard", "encounter_risk_150m_2032",
                "readiness_index", "um_capacity", "cros_integration"):
        assert key in r
