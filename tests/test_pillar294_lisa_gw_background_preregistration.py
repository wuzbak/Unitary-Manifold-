# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 294 — LISA GW Background Preregistration."""
import math
import pytest
from src.core.pillar294_lisa_gw_background_preregistration import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    UM_OMEGA_GW_PREDICTION,
    UM_OMEGA_GW_LOG10,
    LISA_PEAK_FREQ_HZ,
    LISA_OMEGA_SENSITIVITY,
    LISA_LAUNCH_YEAR,
    DOCS_TO_UPDATE,
    separation_guard,
    um_omega_gw_prediction,
    lisa_sensitivity_comparison,
    omega_gw_spectral_shape,
    lisa_routing_thresholds,
    lisa_dr1_routing,
    lisa_preregistration_checklist,
    euclid_desi_dr3_readiness,
    lisa_preregistration_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 294


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_separation_guard():
    g = separation_guard()
    assert g["pillar"] == 294
    assert g["is_hardgate"] is False
    assert g["preregistration"] is True
    assert g["target_experiment"] == "LISA"
    assert g["expected_launch_year"] == LISA_LAUNCH_YEAR


def test_um_omega_prediction():
    assert abs(UM_OMEGA_GW_PREDICTION - 1.0e-15) < 1e-20
    assert abs(UM_OMEGA_GW_LOG10 - (-15.0)) < 1e-6


def test_lisa_peak_freq():
    assert abs(LISA_PEAK_FREQ_HZ - 3.0e-3) < 1e-8


def test_um_omega_gw_prediction_keys():
    p = um_omega_gw_prediction()
    for key in ("omega_gw_p25_derivation", "f_peak_kk_hz", "f_peak_kk_undetectable_by_lisa"):
        assert key in p


def test_um_omega_undetectable():
    p = um_omega_gw_prediction()
    assert p["f_peak_kk_undetectable_by_lisa"] is True


def test_lisa_sensitivity_comparison_keys():
    s = lisa_sensitivity_comparison()
    for key in ("um_omega_gw", "lisa_sensitivity", "snr_estimate", "verdict"):
        assert key in s


def test_lisa_sensitivity_below():
    s = lisa_sensitivity_comparison()
    assert s["direct_detection_possible"] is False
    assert s["verdict"] == "UM_BELOW_LISA_SENSITIVITY"


def test_lisa_snr_below_one():
    s = lisa_sensitivity_comparison()
    assert s["snr_estimate"] < 1.0


def test_omega_gw_spectral_shape_peak():
    # At f = f_ref, shape = omega_ref × 1² × e^(-1)
    shape = omega_gw_spectral_shape(LISA_PEAK_FREQ_HZ, LISA_PEAK_FREQ_HZ)
    expected = UM_OMEGA_GW_PREDICTION * math.exp(-1.0)
    assert abs(shape - expected) < 1e-25


def test_omega_gw_spectral_shape_zero():
    # At very low frequency relative to f_ref, shape → 0 (smaller than at peak)
    shape_low = omega_gw_spectral_shape(LISA_PEAK_FREQ_HZ * 1e-7, LISA_PEAK_FREQ_HZ)
    shape_peak = omega_gw_spectral_shape(LISA_PEAK_FREQ_HZ, LISA_PEAK_FREQ_HZ)
    # The low-frequency shape should be much smaller than at the peak
    assert shape_low < shape_peak * 1e-10


def test_omega_gw_spectral_shape_invalid():
    with pytest.raises(ValueError):
        omega_gw_spectral_shape(0.0)


def test_lisa_routing_thresholds_keys():
    t = lisa_routing_thresholds()
    for key in ("CONSISTENT", "TENSION", "FALSIFIED", "decisive_experiment"):
        assert key in t


def test_lisa_routing_thresholds_version():
    t = lisa_routing_thresholds()
    assert t["preregistration_version"] == "v11.9"


def test_lisa_dr1_routing_nondetect():
    r = lisa_dr1_routing(LISA_OMEGA_SENSITIVITY * 0.1, LISA_OMEGA_SENSITIVITY * 0.05)
    assert r["verdict"] == "CONSISTENT"
    assert not r["is_detection"]


def test_lisa_dr1_routing_detect_consistent():
    r = lisa_dr1_routing(LISA_OMEGA_SENSITIVITY * 5.0, LISA_OMEGA_SENSITIVITY * 0.5,
                         spectral_shape_consistent=True)
    assert r["verdict"] in ("TENSION", "INCONCLUSIVE")


def test_lisa_dr1_routing_falsified():
    r = lisa_dr1_routing(
        LISA_OMEGA_SENSITIVITY * 100.0, LISA_OMEGA_SENSITIVITY * 5.0,
        spectral_shape_consistent=False
    )
    assert r["verdict"] == "FALSIFIED"


def test_lisa_dr1_routing_invalid_sigma():
    with pytest.raises(ValueError):
        lisa_dr1_routing(1e-14, 0.0)


def test_lisa_dr1_routing_preregistration_version():
    r = lisa_dr1_routing(LISA_OMEGA_SENSITIVITY * 0.1, LISA_OMEGA_SENSITIVITY * 0.05)
    assert r["preregistration_version"] == "v11.9"


def test_lisa_preregistration_checklist_length():
    c = lisa_preregistration_checklist()
    assert len(c) >= 4


def test_lisa_preregistration_checklist_items():
    c = lisa_preregistration_checklist()
    for item in c:
        assert "item" in item
        assert "status" in item


def test_euclid_desi_dr3_readiness_keys():
    e = euclid_desi_dr3_readiness()
    for key in ("current_status", "euclid_projection", "euclid_desi_combined", "routing_instruction"):
        assert key in e


def test_euclid_desi_dr3_current_not_falsified():
    e = euclid_desi_dr3_readiness()
    assert e["current_status"]["falsified"] is False


def test_euclid_desi_dr3_version():
    e = euclid_desi_dr3_readiness()
    assert e["preregistration_version"] == "v11.9"


def test_lisa_preregistration_report_keys():
    rep = lisa_preregistration_report()
    for key in ("pillar", "title", "prediction", "routing_thresholds", "status"):
        assert key in rep


def test_lisa_preregistration_report_pillar():
    rep = lisa_preregistration_report()
    assert rep["pillar"] == 294


def test_lisa_preregistration_status_locked():
    rep = lisa_preregistration_report()
    assert rep["status"] == "PREREGISTRATION_LOCKED"


def test_docs_to_update_non_empty():
    assert len(DOCS_TO_UPDATE) >= 4
