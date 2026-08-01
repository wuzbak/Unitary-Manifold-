# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 646 — LISA Ω_GW template hardening."""
from __future__ import annotations

import math

from src.core.pillar646_lisa_ogw_template import (
    F_PEAK_HZ,
    K_CS,
    LISA_DATE,
    LISA_SENSITIVITY,
    LISA_SNR,
    N_T,
    N_W,
    OGW_AT_LISA,
    OGW_PEAK,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    R_BRAIDED,
    VERSION,
    falsification_condition,
    kk_cascade_spectrum,
    lisa_detection,
    pillar_report,
    spectral_template,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
SPECTRUM = kk_cascade_spectrum()
DETECTION = lisa_detection()
TEMPLATE = spectral_template()
FALSIF = falsification_condition()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 646

    def test_status(self):
        assert "HARDENED" in PILLAR_STATUS

    def test_ogw_peak_positive(self):
        assert OGW_PEAK > 0.0

    def test_n_t_formula(self):
        expected = -R_BRAIDED / 8.0
        assert abs(N_T - expected) < 1e-12

    def test_n_t_negative(self):
        assert N_T < 0.0

    def test_lisa_snr_large(self):
        assert LISA_SNR > 1.0e3

    def test_ogw_above_sensitivity(self):
        assert OGW_PEAK > LISA_SENSITIVITY


class TestKKCascadeSpectrum:
    def test_n_w(self):
        assert SPECTRUM["n_w"] == N_W

    def test_k_cs(self):
        assert SPECTRUM["k_cs"] == K_CS

    def test_formula(self):
        assert "n_w" in SPECTRUM["amplitude_formula"]


class TestLISADetection:
    def test_detectable(self):
        assert DETECTION["detectable_3sigma"] is True

    def test_date(self):
        assert DETECTION["lisa_date"] == LISA_DATE

    def test_log10_snr_positive(self):
        assert DETECTION["log10_snr"] > 0.0


class TestSpectralTemplate:
    def test_five_frequencies(self):
        assert len(TEMPLATE["spectrum"]) == 5

    def test_peak_freq(self):
        assert abs(TEMPLATE["peak_freq"] - F_PEAK_HZ) < 1e-12


class TestFalsificationCondition:
    def test_claim_ref(self):
        assert "P25" in FALSIF["claim_reference"]


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
