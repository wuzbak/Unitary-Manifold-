# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 290 — Dark Matter Direct Detection Constraints."""
import math
import pytest
from src.core.pillar290_dark_matter_direct_detection import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    M_KK_GEV,
    M_N_GEV,
    N_W,
    K_CS,
    G_N_CGS,
    GEV_TO_G,
    LEGACY_PROXY_UNITS,
    LZ_YEAR2_SIGMA_LIMIT_CM2,
    LZ_YEAR3_PROJECTED_LIMIT_CM2,
    separation_guard,
    kk_graviton_si_cross_section,
    legacy_kk_graviton_dimensional_proxy,
    lz_year2_exclusion_limit,
    consistency_verdict,
    lz_year3_projection,
    dm_detection_preregistration_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 290


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard_keys():
    g = separation_guard()
    assert g["pillar"] == 290
    assert g["is_hardgate"] is False
    assert g["modifies_hardgate_module"] is False
    assert g["alters_falsifier_window"] is False
    assert "experiments" in g


def test_separation_guard_experiments():
    g = separation_guard()
    assert "LZ" in g["experiments"]


def test_constants_physical():
    assert M_KK_GEV == 1.0e3
    assert M_N_GEV > 0.0
    assert N_W == 5
    assert K_CS == 74


def test_lz_year2_limit_value():
    assert abs(LZ_YEAR2_SIGMA_LIMIT_CM2 - 6.6e-48) < 1e-50


def test_kk_graviton_si_positive():
    with pytest.warns(DeprecationWarning):
        sigma = kk_graviton_si_cross_section(1.0)
    assert sigma > 0.0


def test_kk_graviton_si_finite():
    with pytest.warns(DeprecationWarning):
        sigma = kk_graviton_si_cross_section(1.0)
    assert math.isfinite(sigma)


def test_legacy_proxy_value_preserved_without_area_comparison():
    expected = (
        G_N_CGS ** 2 * (M_N_GEV * GEV_TO_G) ** 2
        * (M_N_GEV / 1000.0) ** 4 * (N_W / K_CS) ** 2 / math.pi
    )
    with pytest.warns(DeprecationWarning, match="not a cross-section"):
        proxy = kk_graviton_si_cross_section(1.0)
    assert proxy == pytest.approx(expected, rel=1e-12, abs=0)
    assert proxy == pytest.approx(1.4096711831004588e-77, rel=1e-12, abs=0)
    assert legacy_kk_graviton_dimensional_proxy() == proxy


def test_kk_graviton_si_very_small():
    # Legacy numeric magnitude only; units are cm^6/s^4, not cm².
    with pytest.warns(DeprecationWarning):
        sigma = kk_graviton_si_cross_section(1.0)
    assert sigma < 1.0e-48


def test_kk_graviton_si_raises_non_positive():
    with pytest.warns(DeprecationWarning), pytest.raises(ValueError):
        kk_graviton_si_cross_section(0.0)


def test_kk_graviton_si_scales_with_mass():
    # Higher mediator mass → smaller dimensional proxy.
    with pytest.warns(DeprecationWarning):
        sigma_1 = kk_graviton_si_cross_section(1.0)
        sigma_2 = kk_graviton_si_cross_section(2.0)
    assert sigma_2 < sigma_1
    assert sigma_2 == pytest.approx(sigma_1 / 16, rel=1e-12, abs=0)


def test_lz_year2_exclusion_limit_keys():
    r = lz_year2_exclusion_limit()
    for key in ("sigma_limit_cm2", "m_chi_gev", "confidence_level", "reference"):
        assert key in r


def test_lz_year2_exclusion_confidence():
    r = lz_year2_exclusion_limit()
    assert "90%" in r["confidence_level"]


def test_consistency_verdict_unsupported():
    v = consistency_verdict()
    assert v["verdict"] == "UNSUPPORTED"
    assert v["um_sigma_cm2"] is None


def test_consistency_verdict_no_dimensionally_invalid_margin():
    v = consistency_verdict()
    assert v["margin_factors"] is None
    assert v["ratio_limit_to_um"] is None
    assert v["legacy_kk_graviton_proxy_cm6_s4"] == legacy_kk_graviton_dimensional_proxy()
    assert v["legacy_proxy_units"] == "cm^6/s^4"
    assert v["mediator_mass_gev"] == 1000.0
    assert v["dm_mass_gev"] is None
    assert v["limit_dm_mass_gev"] == 30.0


def test_consistency_verdict_keys():
    v = consistency_verdict()
    for key in ("um_sigma_cm2", "lz_limit_cm2", "verdict", "margin_factors"):
        assert key in v


def test_lz_year3_projection_unsupported():
    r = lz_year3_projection()
    assert r["verdict"] == "UNSUPPORTED"
    assert r["um_sigma_cm2"] is None
    assert r["ratio_limit_to_um"] is None


def test_lz_year3_projection_keys():
    r = lz_year3_projection()
    for key in ("projected_limit_cm2", "um_sigma_cm2", "verdict", "note"):
        assert key in r


def test_dm_report_pillar():
    r = dm_detection_preregistration_report()
    assert r["pillar"] == 290


def test_dm_report_has_sections():
    r = dm_detection_preregistration_report()
    for key in ("kk_graviton_sigma_cm2", "lz_year2_limit", "consistency", "lz_year3"):
        assert key in r


def test_report_physical_quantity_absent_legacy_proxy_explicit():
    report = dm_detection_preregistration_report()
    assert report["kk_graviton_sigma_cm2"] is None
    assert report["verdict"] == "UNSUPPORTED"
    assert report["legacy_proxy_units"] == LEGACY_PROXY_UNITS == "cm^6/s^4"
    assert report["legacy_kk_graviton_proxy_cm6_s4"] == legacy_kk_graviton_dimensional_proxy()
    for section in (report["consistency"], report["lz_year3"]):
        assert section["um_sigma_cm2"] is None
        assert section["verdict"] == "UNSUPPORTED"
        assert section["ratio_limit_to_um"] is None
        assert section["legacy_proxy_units"] == LEGACY_PROXY_UNITS
        assert section["legacy_kk_graviton_proxy_cm6_s4"] == legacy_kk_graviton_dimensional_proxy()


def test_missing_prediction_cannot_route_confirmation_or_refutation():
    for message in lz_year3_projection()["routing"].values():
        assert "cannot confirm or refute" in message
        assert "missing" in message


def test_legacy_proxy_dimensions():
    # G has [L³ M⁻¹ T⁻²]; squaring and multiplying by m_n² leaves L⁶ T⁻⁴.
    newton_dimensions = (3, -1, -2)
    nucleon_mass_dimensions = (0, 1, 0)
    dimensions = tuple(
        2 * gravity + 2 * mass
        for gravity, mass in zip(newton_dimensions, nucleon_mass_dimensions)
    )
    assert dimensions == (6, 0, -4)
    assert dimensions != (2, 0, 0)


@pytest.mark.parametrize("proxy", [0.0, 1.0e10])
def test_proxy_magnitude_cannot_create_physical_prediction(monkeypatch, proxy):
    from src.core import pillar290_dark_matter_direct_detection as dm

    monkeypatch.setattr(dm, "legacy_kk_graviton_dimensional_proxy", lambda: proxy)
    report = dm.dm_detection_preregistration_report()
    assert report["kk_graviton_sigma_cm2"] is None
    assert report["verdict"] == "UNSUPPORTED"
    for section in (report["consistency"], report["lz_year3"]):
        assert section["legacy_kk_graviton_proxy_cm6_s4"] == proxy
        assert section["um_sigma_cm2"] is None
        assert section["ratio_limit_to_um"] is None
        assert section["verdict"] == "UNSUPPORTED"
