# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 645 — SPHEREx f_NL DBI+KK bounds sharpening."""
from __future__ import annotations

import math

from src.core.pillar645_spherex_fnl_sharpened import (
    C_S_CANONICAL,
    C_S_KK,
    DELTA_C_S,
    F_NL_DBI_EXACT,
    F_NL_KK_CORRECTED,
    F_NL_SHARPENED_BAND,
    F_NL_THEORY_BAND,
    K_CS,
    N_W,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SPHEREX_SIGMA_FNL,
    VERSION,
    dbi_fnl_exact,
    kk_sound_speed_correction,
    pillar_report,
    sharpened_prediction,
    spherex_snr,
    theory_band_update,
    what_is_NOT_claimed,
    what_is_claimed,
)

REPORT = pillar_report()
DBI = dbi_fnl_exact()
KK_CS = kk_sound_speed_correction()
SHARP = sharpened_prediction()
SNR = spherex_snr()
BAND = theory_band_update()


class TestConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 645

    def test_status(self):
        assert "SHARPENED" in PILLAR_STATUS

    def test_c_s_canonical(self):
        assert abs(C_S_CANONICAL - 12.0 / 37.0) < 1e-12

    def test_delta_c_s(self):
        expected = C_S_CANONICAL * (N_W ** 2) / (2.0 * K_CS)
        assert abs(DELTA_C_S - expected) < 1e-12

    def test_c_s_kk_larger(self):
        assert C_S_KK > C_S_CANONICAL

    def test_f_nl_dbi_negative(self):
        assert F_NL_DBI_EXACT < 0.0

    def test_f_nl_kk_negative(self):
        assert F_NL_KK_CORRECTED < 0.0

    def test_f_nl_kk_larger_than_dbi(self):
        # KK correction raises c_s → less negative f_NL
        assert F_NL_KK_CORRECTED > F_NL_DBI_EXACT

    def test_f_nl_in_original_band(self):
        assert F_NL_THEORY_BAND[0] <= F_NL_KK_CORRECTED <= F_NL_THEORY_BAND[1]


class TestDBIFormula:
    def test_formula_string(self):
        assert "c_s²" in DBI["formula"] or "c_s" in DBI["formula"]

    def test_dbi_value(self):
        expected = -35.0 / 108.0 * (1.0 / C_S_CANONICAL ** 2 - 1.0)
        assert abs(F_NL_DBI_EXACT - expected) < 1e-10


class TestKKCorrection:
    def test_correction_percent_positive(self):
        assert KK_CS["correction_percent"] > 0.0

    def test_c_s_kk_correct(self):
        assert abs(KK_CS["c_s_kk"] - C_S_KK) < 1e-12


class TestSharpenedPrediction:
    def test_band_tighter(self):
        assert SHARP["band_tighter"] is True


class TestSPHERExSNR:
    def test_snr_positive(self):
        assert SNR["snr_kk_corrected"] > 0.0

    def test_falsification_condition(self):
        assert "+10" in SNR["falsification_condition"]


class TestReport:
    def test_toe_delta(self):
        assert REPORT["toe_score_delta"] == 0.0

    def test_claims(self):
        assert len(what_is_claimed()) >= 4
        assert len(what_is_NOT_claimed()) >= 3
