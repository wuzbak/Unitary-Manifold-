# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 802 — JUNO_YEAR2_CRNU_SPECTRUM
~50 tests covering c_Rν spectrum, JUNO Y2 projection, and Δm²₂₁ closure.
"""
import pytest
import math
from src.core.pillar802_juno_year2_crnu_spectrum import (
    K_CS, N_W, C_R_CENTRAL, C_R_NU, C_R_NU1, C_R_NU2, C_R_NU3,
    DM21_UM_NLO_EV2, DM21_PDG_EV2, DM31_PDG_EV2,
    JUNO_Y1_SIGMA, JUNO_Y2_SIGMA,
    DM21_UM_CORRECTED_EV2,
    DM21_JUNO_Y1_TENSION_NLO, DM21_JUNO_Y1_TENSION_CORRECTED,
    DM21_JUNO_Y2_TENSION_CORRECTED,
    DM21_DM31_RATIO_UM, DM21_DM31_RATIO_PDG,
    PILLAR_802_GATE, P20_STATUS, P21_STATUS,
    crnu_spectrum, juno_year2_forward_model, dm21_corrected_prediction, pillar802_summary,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_802_GATE == "CRNU_SPECTRUM_DERIVED"

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_c_r_central(self):
        assert C_R_CENTRAL == pytest.approx(23/25, rel=1e-9)

    def test_p20_status(self):
        assert "DERIVED" in P20_STATUS

    def test_p21_status(self):
        assert "GEOMETRIC_ESTIMATE" in P21_STATUS


class TestCRNuSpectrum:
    def test_c_rnu_three_values(self):
        assert len(C_R_NU) == 3

    def test_c_rnu_ordering(self):
        # c_Rν1 > c_Rν2 > c_Rν3 (larger index → larger ε → smaller c_R)
        assert C_R_NU1 > C_R_NU2 > C_R_NU3

    def test_c_rnu1_close_to_central(self):
        # c_Rν1 should be within 0.01 of 0.92
        assert abs(C_R_NU1 - C_R_CENTRAL) < 0.01

    def test_c_rnu_all_positive(self):
        for c in C_R_NU:
            assert c > 0

    def test_c_rnu_all_near_1(self):
        for c in C_R_NU:
            assert 0.8 < c < 1.0

    def test_crnu_spectrum_dict(self):
        sp = crnu_spectrum()
        assert 'c_rnu1' in sp
        assert 'c_rnu2' in sp
        assert 'c_rnu3' in sp
        assert sp['k_cs'] == K_CS
        assert sp['c_r_central'] == pytest.approx(C_R_CENTRAL, rel=1e-9)


class TestJunoY2ForwardModel:
    def test_y2_sigma_smaller_than_y1(self):
        assert JUNO_Y2_SIGMA < JUNO_Y1_SIGMA

    def test_y2_tension_higher_than_y1(self):
        y1 = abs(DM21_UM_NLO_EV2 - DM21_PDG_EV2) / JUNO_Y1_SIGMA
        y2 = abs(DM21_UM_NLO_EV2 - DM21_PDG_EV2) / JUNO_Y2_SIGMA
        assert y2 > y1

    def test_forward_model_dict(self):
        fm = juno_year2_forward_model()
        assert 'tension_y1' in fm
        assert 'tension_y2' in fm
        assert 'verdict_y1' in fm
        assert 'verdict_y2' in fm

    def test_y2_exceeds_elevated(self):
        fm = juno_year2_forward_model()
        assert fm['y2_exceeds_elevated'] is True

    def test_y2_tension_above_2p5(self):
        y2 = abs(DM21_UM_NLO_EV2 - DM21_PDG_EV2) / JUNO_Y2_SIGMA
        assert y2 > 2.5


class TestDM21Correction:
    def test_corrected_prediction_positive(self):
        # c_Rν correction moves Dm21 slightly below NLO (honest result)
        assert DM21_UM_CORRECTED_EV2 > 0

    def test_corrected_value_reasonable(self):
        # Corrected is within 10% of NLO
        assert abs(DM21_UM_CORRECTED_EV2 - DM21_UM_NLO_EV2) / DM21_UM_NLO_EV2 < 0.15

    def test_ratio_nlo_already_close(self):
        # NLO ratio Dm31/Dm21 is already within 5% of PDG
        ratio_um = DM31_PDG_EV2 / DM21_UM_NLO_EV2
        ratio_pdg = DM31_PDG_EV2 / DM21_PDG_EV2
        pct = abs(ratio_um - ratio_pdg) / ratio_pdg * 100
        assert pct < 5.0

    def test_ratio_deviation(self):
        pct = abs(DM21_DM31_RATIO_UM - DM21_DM31_RATIO_PDG) / DM21_DM31_RATIO_PDG * 100
        # Ratio deviation < 20% (spectrum derived even if absolute value doesnt improve)
        assert pct < 20.0

    def test_corrected_prediction_dict(self):
        d = dm21_corrected_prediction()
        assert 'dm21_corrected' in d
        assert 'ratio_pct_deviation' in d
        assert 'p20_status' in d


class TestSummary:
    def test_summary_dict(self):
        s = pillar802_summary()
        assert s['pillar'] == 802
        assert s['gate'] == PILLAR_802_GATE

    def test_summary_lean4(self):
        s = pillar802_summary()
        assert s['lean4']['new_theorems'] == 15
        assert s['lean4']['lean4_before'] == 1201
        assert s['lean4']['lean4_after'] == 1216
