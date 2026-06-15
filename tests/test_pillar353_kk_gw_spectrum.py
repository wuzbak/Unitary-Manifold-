# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 353 — Full KK Mode GW Background Spectrum for LISA."""
import math
import pytest
from src.core.pillar353_kk_gw_spectrum import (
    ADJACENCY_TRACK_LABEL, PILLAR_NUMBER, PILLAR_TITLE,
    M_KK_EV, F_KK_HZ, OMEGA_GW_TOTAL, OMEGA_GW_AT_LISA_MHZ,
    LISA_SENSITIVITY, LISA_FREQ_MIN, LISA_FREQ_MAX,
    kk_mode_spectrum, omega_gw_at_frequency, lisa_transfer_function,
    kk_gw_full_spectrum, lisa_detectability, frequency_resolved_prediction,
    honest_observability_report, separation_guard,
)


# ── Identity ─────────────────────────────────────────────────────────────────────

def test_module_identity():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert PILLAR_NUMBER == 353


def test_constants():
    assert M_KK_EV == pytest.approx(110e-3)
    assert F_KK_HZ > 1e12   # THz range
    assert OMEGA_GW_TOTAL == pytest.approx(1e-15)
    assert OMEGA_GW_AT_LISA_MHZ < LISA_SENSITIVITY  # undetectable


# ── KK Mode Spectrum ─────────────────────────────────────────────────────────────

def test_kk_mode_spectrum_n10():
    modes = kk_mode_spectrum(n_max=10)
    assert len(modes) == 10


def test_kk_mode_spectrum_frequency_scaling():
    modes = kk_mode_spectrum(n_max=5)
    for n, mode in enumerate(modes, 1):
        assert mode["n"] == n
        assert mode["f_n_hz"] == pytest.approx(n * F_KK_HZ, rel=1e-10)


def test_kk_mode_spectrum_omega_scaling():
    modes = kk_mode_spectrum(n_max=5)
    # Ω_GW^{(n)} = Ω_GW_total / n³
    for mode in modes:
        expected = OMEGA_GW_TOTAL / mode["n"]**3
        assert mode["Omega_GW_n"] == pytest.approx(expected, rel=1e-10)


def test_kk_mode_spectrum_above_thz():
    modes = kk_mode_spectrum(n_max=3)
    for mode in modes:
        assert mode["f_n_thz"] > 1   # all modes in THz range


# ── Ω_GW at Frequency ───────────────────────────────────────────────────────────

def test_omega_gw_at_lisa_sub_kk():
    result = omega_gw_at_frequency(f_hz=1e-3)
    assert result["regime"] == "SUB_KK_POWER_LAW"
    assert not result["is_detectable_by_LISA"]


def test_omega_gw_power_law():
    # At f << f_KK: Ω ∝ f^(2/3)
    f1 = 1e-4
    f2 = 1e-3
    r1 = omega_gw_at_frequency(f1)
    r2 = omega_gw_at_frequency(f2)
    ratio_expected = (f2 / f1)**(2 / 3)
    ratio_actual = r2["Omega_GW"] / r1["Omega_GW"]
    assert ratio_actual == pytest.approx(ratio_expected, rel=1e-6)


def test_omega_gw_at_kk_near_resonance():
    result = omega_gw_at_frequency(f_hz=F_KK_HZ * 1.01)
    assert result["regime"] == "NEAR_KK_RESONANCE"


def test_omega_gw_extremely_small_at_lisa():
    for f in [1e-4, 1e-3, 1e-2, 0.1]:
        result = omega_gw_at_frequency(f)
        assert result["Omega_GW"] < 1e-20


# ── LISA Transfer Function ────────────────────────────────────────────────────────

def test_lisa_transfer_function_at_kk():
    T = lisa_transfer_function(F_KK_HZ)
    assert T == pytest.approx(1.0, rel=1e-10)


def test_lisa_transfer_function_below_kk():
    T = lisa_transfer_function(1e-3)
    assert T < 1e-10  # vastly suppressed at LISA frequencies


def test_lisa_transfer_function_power_law():
    f1, f2 = 1e-4, 1e-3
    T1 = lisa_transfer_function(f1)
    T2 = lisa_transfer_function(f2)
    ratio_expected = (f2 / f1)**(2 / 3)
    assert T2 / T1 == pytest.approx(ratio_expected, rel=1e-10)


# ── Full Spectrum ────────────────────────────────────────────────────────────────

def test_kk_gw_full_spectrum():
    spectrum = kk_gw_full_spectrum()
    assert len(spectrum) > 0
    # Should include LISA band points
    f_vals = [s["f_hz"] for s in spectrum]
    assert any(LISA_FREQ_MIN <= f <= LISA_FREQ_MAX for f in f_vals)


def test_kk_gw_spectrum_custom_freqs():
    spectrum = kk_gw_full_spectrum(f_values=[1e-3, 1.0, 1e6])
    assert len(spectrum) == 3


# ── LISA Detectability ───────────────────────────────────────────────────────────

def test_lisa_detectability_undetectable():
    result = lisa_detectability()
    assert not result["detectable"]


def test_lisa_detectability_frequency_gap():
    result = lisa_detectability()
    # Gap should be > 10^12 (f_KK ≈ 10^13 Hz vs f_LISA ≈ 10^-3 Hz)
    assert result["log10_frequency_gap"] > 12


def test_lisa_detectability_omega_below_sensitivity():
    result = lisa_detectability()
    assert result["Omega_GW_at_LISA"] < result["LISA_sensitivity"]


def test_lisa_detectability_honest_verdict():
    result = lisa_detectability()
    assert "UNDETECTABLE_BY_LISA" in result["honest_verdict"]


# ── Frequency-Resolved Prediction ────────────────────────────────────────────────

def test_frequency_resolved_prediction():
    result = frequency_resolved_prediction(n_modes=3)
    assert result["n_modes"] == 3
    assert len(result["kk_mode_catalog"]) == 3
    assert not result["LISA_detectability"]["detectable"]
    # Summary should mention being below LISA sensitivity
    assert "LISA" in result["honest_summary"].upper()


def test_frequency_resolved_clarification():
    result = frequency_resolved_prediction()
    assert "PILLAR 231" in result["clarification"]
    assert "phase transition" in result["clarification"].lower()


# ── Honest Observability ──────────────────────────────────────────────────────────

def test_honest_observability_channels():
    result = honest_observability_report()
    assert "inflationary_tensor" in result["channels"]
    assert "kk_phase_transition" in result["channels"]
    assert "kk_tower_annihilation" in result["channels"]


def test_honest_observability_kk_tower_undetectable():
    result = honest_observability_report()
    kk_tower = result["channels"]["kk_tower_annihilation"]
    assert not kk_tower["detectable"]


def test_honest_observability_tensor_detectable():
    result = honest_observability_report()
    tensor = result["channels"]["inflationary_tensor"]
    assert tensor["detectable"]


def test_honest_observability_priority():
    result = honest_observability_report()
    assert "LiteBIRD" in result["priority_observable"]


# ── Separation Guard ─────────────────────────────────────────────────────────────

def test_separation_guard():
    guard = separation_guard()
    assert "SEPARATION_INTACT" in guard
    assert "353" in guard
