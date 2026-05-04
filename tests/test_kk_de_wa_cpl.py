# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_kk_de_wa_cpl.py
============================
Pillar 155 — Tests for kk_de_wa_cpl.py.

Tests cover:
  - Constants: C_S_BRAIDED, W_KK, W_A_UM, DESI_DR2_W0, DESI_DR2_WA
  - um_cpl_w0(): UM w₀ prediction
  - um_cpl_wa(): UM wₐ = 0 prediction
  - gw_radion_wa_slow_roll(): wₐ from GW radion evolution
  - kk_wa_from_multi_mode(): KK tower wₐ estimate
  - cpl_tension_analysis(): full tension analysis
  - pillar155_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.kk_de_wa_cpl import (
    C_S_BRAIDED,
    W_KK,
    W_A_UM,
    PI_KR,
    M_PLANCK_GEV,
    M_KK_EW_GEV,
    H0_GEV,
    DESI_DR2_W0,
    DESI_DR2_W0_SIGMA,
    DESI_DR2_WA,
    DESI_DR2_WA_SIGMA,
    PLANCK_BAO_W,
    DESI_DR2_REF,
    A_DESI_MIN,
    A_DESI_MAX,
    DELTA_PHI_OVER_MPL_DEFAULT,
    um_cpl_w0,
    um_cpl_wa,
    gw_radion_wa_slow_roll,
    kk_wa_from_multi_mode,
    cpl_tension_analysis,
    pillar155_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_c_s_braided_is_12_over_37(self):
        assert abs(C_S_BRAIDED - 12.0 / 37.0) < 1e-12

    def test_w_kk_formula(self):
        expected = -1.0 + (2.0 / 3.0) * (12.0 / 37.0) ** 2
        assert abs(W_KK - expected) < 1e-12

    def test_w_kk_near_minus_0_93(self):
        assert abs(W_KK - (-0.9302)) < 0.001

    def test_w_kk_greater_than_minus_1(self):
        assert W_KK > -1.0

    def test_wa_um_is_zero(self):
        assert abs(W_A_UM - 0.0) < 1e-15

    def test_pi_kr_is_37(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_m_kk_ew_gev_order(self):
        """EW KK scale should be O(1 TeV)."""
        assert 100.0 < M_KK_EW_GEV < 1e6

    def test_h0_gev_very_small(self):
        """H₀ in GeV is extremely small (~2×10⁻⁴² GeV)."""
        assert H0_GEV < 1e-40

    def test_desi_dr2_w0_near_minus_0_838(self):
        assert abs(DESI_DR2_W0 - (-0.838)) < 0.01

    def test_desi_dr2_wa_negative(self):
        assert DESI_DR2_WA < 0

    def test_desi_dr2_wa_sigma_positive(self):
        assert DESI_DR2_WA_SIGMA > 0

    def test_planck_bao_w_near_minus_1(self):
        assert abs(PLANCK_BAO_W - (-1.03)) < 0.05

    def test_desi_ref_nonempty(self):
        assert len(DESI_DR2_REF) > 10

    def test_a_desi_min_is_1_over_3(self):
        """a(z=2) = 1/3."""
        assert abs(A_DESI_MIN - 1.0 / 3.0) < 1e-6

    def test_a_desi_max_is_1(self):
        """a(z=0) = 1."""
        assert abs(A_DESI_MAX - 1.0) < 1e-10

    def test_m_kk_much_larger_than_h0(self):
        """The EW KK scale is astronomically larger than H₀."""
        assert M_KK_EW_GEV / H0_GEV > 1e40


# ---------------------------------------------------------------------------
# um_cpl_w0
# ---------------------------------------------------------------------------

class TestUMCPLW0:
    def test_returns_float(self):
        w0 = um_cpl_w0()
        assert isinstance(w0, float)

    def test_equals_w_kk(self):
        assert abs(um_cpl_w0() - W_KK) < 1e-15

    def test_greater_than_minus_1(self):
        assert um_cpl_w0() > -1.0

    def test_near_minus_0_93(self):
        assert abs(um_cpl_w0() - (-0.9302)) < 0.001

    def test_on_same_side_as_desi_relative_to_lcdm(self):
        """Both w_KK and DESI DR2 predict w > −1 (same side as ΛCDM)."""
        w0 = um_cpl_w0()
        # Both UM and DESI find w > −1
        assert w0 > -1.0
        assert DESI_DR2_W0 > -1.0


# ---------------------------------------------------------------------------
# um_cpl_wa
# ---------------------------------------------------------------------------

class TestUMCPLWa:
    def test_returns_float(self):
        wa = um_cpl_wa()
        assert isinstance(wa, float)

    def test_equals_zero(self):
        """UM predicts wₐ = 0 exactly (frozen radion)."""
        assert abs(um_cpl_wa() - 0.0) < 1e-15

    def test_not_negative(self):
        assert um_cpl_wa() >= 0.0


# ---------------------------------------------------------------------------
# gw_radion_wa_slow_roll
# ---------------------------------------------------------------------------

class TestGWRadionWaSlowRoll:
    def test_returns_dict(self):
        result = gw_radion_wa_slow_roll(1e60)
        assert isinstance(result, dict)

    def test_frozen_radion_wa_near_zero(self):
        """m_r >> H₀ → field is frozen → wₐ ≈ 0."""
        result = gw_radion_wa_slow_roll(1e60)
        assert abs(result["wa_cpl"]) < 1e-10

    def test_frozen_flag_true_for_large_mass(self):
        result = gw_radion_wa_slow_roll(1e60)
        assert result["frozen"] is True

    def test_rolling_regime_for_small_mass(self):
        """m_r = 0.5 H₀ → rolling quintessence → |wₐ| > 0."""
        result = gw_radion_wa_slow_roll(0.5, delta_phi_over_mpl=0.1)
        # Rolling quintessence should have significant wₐ
        assert abs(result["wa_cpl"]) > 0

    def test_regime_string_nonempty(self):
        result = gw_radion_wa_slow_roll(1e60)
        assert len(result["regime"]) > 10

    def test_conclusion_nonempty(self):
        result = gw_radion_wa_slow_roll(1e60)
        assert len(result["conclusion"]) > 20

    def test_w0_w_at_a_f(self):
        """w₀ from CPL is w evaluated at a_f."""
        result = gw_radion_wa_slow_roll(1e60)
        assert abs(result["w0_cpl"] - result["w_at_a_f"]) < 1e-12

    def test_invalid_m_r_raises(self):
        with pytest.raises(ValueError, match="positive"):
            gw_radion_wa_slow_roll(0.0)

    def test_invalid_delta_phi_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            gw_radion_wa_slow_roll(1.0, delta_phi_over_mpl=-0.1)

    def test_invalid_a_i_raises(self):
        with pytest.raises(ValueError, match="positive"):
            gw_radion_wa_slow_roll(1.0, a_i=0.0)

    def test_invalid_a_f_le_a_i_raises(self):
        with pytest.raises(ValueError, match="greater than"):
            gw_radion_wa_slow_roll(1.0, a_i=0.5, a_f=0.3)

    def test_zero_delta_phi_gives_lcdm(self):
        """Zero displacement → w = −1 everywhere → wₐ = 0."""
        result = gw_radion_wa_slow_roll(1.0, delta_phi_over_mpl=0.0)
        assert abs(result["wa_cpl"]) < 1e-15
        assert abs(result["w0_cpl"] - (-1.0)) < 1e-15

    def test_m_r_over_h0_stored(self):
        result = gw_radion_wa_slow_roll(100.0)
        assert abs(result["m_r_over_h0"] - 100.0) < 1e-10


# ---------------------------------------------------------------------------
# kk_wa_from_multi_mode
# ---------------------------------------------------------------------------

class TestKKWaFromMultiMode:
    def test_returns_dict(self):
        result = kk_wa_from_multi_mode()
        assert isinstance(result, dict)

    def test_wa_total_positive(self):
        result = kk_wa_from_multi_mode()
        assert result["wa_kk_total_schematic"] > 0

    def test_wa_total_negligibly_small(self):
        """KK tower wₐ should be exponentially small (far below DESI)."""
        result = kk_wa_from_multi_mode()
        assert result["wa_kk_total_schematic"] < 1e-50

    def test_not_sufficient_for_desi(self):
        """KK multi-mode wₐ cannot explain DESI |wₐ| ≈ 0.62."""
        result = kk_wa_from_multi_mode()
        assert result["sufficient_for_desi"] is False

    def test_mode_contributions_count(self):
        result = kk_wa_from_multi_mode(n_modes=3)
        assert len(result["mode_contributions"]) == 3

    def test_mode_numbers_sequential(self):
        result = kk_wa_from_multi_mode(n_modes=3)
        for i, mode in enumerate(result["mode_contributions"]):
            assert mode["mode_n"] == i + 1

    def test_higher_modes_smaller_wa(self):
        """Higher KK modes are more massive → smaller wₐ contribution."""
        result = kk_wa_from_multi_mode(n_modes=3)
        wa_1 = result["mode_contributions"][0]["wa_n_schematic"]
        wa_2 = result["mode_contributions"][1]["wa_n_schematic"]
        wa_3 = result["mode_contributions"][2]["wa_n_schematic"]
        assert wa_1 > wa_2 > wa_3

    def test_conclusion_nonempty(self):
        result = kk_wa_from_multi_mode()
        assert len(result["conclusion"]) > 30

    def test_h0_over_m_kk_tiny(self):
        result = kk_wa_from_multi_mode()
        assert result["h0_over_m_kk"] < 1e-40

    def test_invalid_n_modes_raises(self):
        with pytest.raises(ValueError, match="at least 1"):
            kk_wa_from_multi_mode(n_modes=0)

    def test_invalid_m_kk_raises(self):
        with pytest.raises(ValueError, match="positive"):
            kk_wa_from_multi_mode(m_kk_gev=0.0)

    def test_invalid_h0_raises(self):
        with pytest.raises(ValueError, match="positive"):
            kk_wa_from_multi_mode(h0_gev=-1.0)


# ---------------------------------------------------------------------------
# cpl_tension_analysis
# ---------------------------------------------------------------------------

class TestCPLTensionAnalysis:
    def setup_method(self):
        self.result = cpl_tension_analysis()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_um_prediction_present(self):
        um = self.result["um_prediction"]
        assert abs(um["w0"] - W_KK) < 1e-12
        assert abs(um["wa"] - W_A_UM) < 1e-15

    def test_desi_constraint_present(self):
        desi = self.result["desi_dr2_constraint"]
        assert abs(desi["w0_central"] - DESI_DR2_W0) < 1e-10
        assert abs(desi["wa_central"] - DESI_DR2_WA) < 1e-10

    def test_w0_tension_positive(self):
        assert self.result["tension_w0_desi"]["tension_sigma"] > 0

    def test_w0_tension_consistent_with_desi(self):
        """w_KK should be within 2σ of DESI DR2 w₀."""
        assert self.result["tension_w0_desi"]["consistent"] is True

    def test_wa_tension_positive(self):
        assert self.result["tension_wa_desi"]["tension_sigma"] > 0

    def test_wa_tension_with_desi(self):
        """wₐ = 0 vs DESI wₐ = −0.62 → tension ~2σ."""
        tension = self.result["tension_wa_desi"]["tension_sigma"]
        assert 1.0 < tension < 5.0

    def test_wa_tension_note_nonempty(self):
        assert len(self.result["tension_wa_desi"]["note"]) > 20

    def test_tension_w0_planck_bao_large(self):
        """w_KK vs Planck+BAO should be in tension (superseded dataset)."""
        assert self.result["tension_w0_planck_bao"]["tension_sigma"] > 1.0

    def test_combined_tension_positive(self):
        assert self.result["combined_tension_desi"]["combined_sigma"] > 0

    def test_kk_multimode_wa_present(self):
        kk = self.result["kk_multimode_wa"]
        assert kk["wa_kk_total_schematic"] > 0

    def test_gw_radion_ew_sector_present(self):
        gw = self.result["gw_radion_ew_sector"]
        assert "wa_cpl" in gw
        assert gw["frozen"] is True

    def test_summary_nonempty(self):
        assert len(self.result["summary"]) > 80


# ---------------------------------------------------------------------------
# pillar155_summary
# ---------------------------------------------------------------------------

class TestPillar155Summary:
    def setup_method(self):
        self.result = pillar155_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_155(self):
        assert self.result["pillar"] == 155

    def test_title_nonempty(self):
        assert len(self.result["title"]) > 10

    def test_new_status_analysed(self):
        assert "ANALYSED" in self.result["new_status"]

    def test_um_w0_matches_w_kk(self):
        assert abs(self.result["um_w0"] - W_KK) < 1e-12

    def test_um_wa_is_zero(self):
        assert abs(self.result["um_wa"] - 0.0) < 1e-15

    def test_desi_dr2_w0_stored(self):
        assert abs(self.result["desi_dr2_w0"] - DESI_DR2_W0) < 1e-10

    def test_desi_dr2_wa_stored(self):
        assert abs(self.result["desi_dr2_wa"] - DESI_DR2_WA) < 1e-10

    def test_tension_w0_sigma_positive(self):
        assert self.result["tension_w0_sigma"] > 0

    def test_tension_wa_sigma_positive(self):
        assert self.result["tension_wa_sigma"] > 0

    def test_w0_consistent_with_desi_true(self):
        assert self.result["w0_consistent_with_desi"] is True

    def test_wa_tension_genuine(self):
        """wₐ tension is genuine — should NOT be consistent."""
        assert self.result["wa_consistent_with_desi"] is False

    def test_kk_multimode_wa_tiny(self):
        assert abs(self.result["kk_multimode_wa_schematic"]) < 1e-50

    def test_kk_correction_negligible_true(self):
        assert self.result["kk_correction_negligible"] is True

    def test_mechanism_nonempty(self):
        assert len(self.result["mechanism"]) > 30

    def test_open_problem_nonempty(self):
        assert len(self.result["open_problem"]) > 50

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 4
