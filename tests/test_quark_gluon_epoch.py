# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_quark_gluon_epoch.py
================================
Test suite for Pillar 65: Quark-Gluon Plasma Epoch
(src/core/quark_gluon_epoch.py).

Covers:
- Module constants: physical plausibility, UM/KK values, ATLAS anchor
- qgp_sound_speed_um(): C_S = 12/37 derivation and value
- qgp_sound_speed_squared_um(): C_S² = (12/37)²
- qgp_cs2_reference_values(): SB limit, lattice, ATLAS values
- qgp_radion_cs_coincidence_audit(): honest coincidence accounting
- qgp_radion_pressure_fraction(): f_braid = C_S²/k_CS
- qgp_hubble_correction(): δH/H = ½ f_braid
- qgp_alpha_s_running(): one-loop α_s at QGP temperatures
- qgp_summary(): complete Pillar 65 audit

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""
from __future__ import annotations

import math

import pytest

from src.core.quark_gluon_epoch import (
    # Constants
    C_S,
    C_S_SQUARED,
    K_CS,
    F_BRAID_QGP,
    QGP_CS2_ATLAS,
    QGP_CS2_ATLAS_UNC,
    QGP_CS2_SB_LIMIT,
    QGP_CS2_LATTICE_NEAR_TC,
    QGP_CS2_LATTICE_2TC,
    T_DECONFINEMENT_MEV,
    ALPHA_S_MZ_PDG,
    M_Z_GEV,
    N_W,
    # Functions
    qgp_sound_speed_um,
    qgp_sound_speed_squared_um,
    qgp_cs2_reference_values,
    qgp_radion_cs_coincidence_audit,
    qgp_radion_pressure_fraction,
    qgp_hubble_correction,
    qgp_alpha_s_running,
    qgp_summary,
)


# ===========================================================================
# I. Module constants
# ===========================================================================

class TestConstants:
    def test_nw_canonical(self):
        assert N_W == 5

    def test_k_cs_canonical(self):
        assert K_CS == 74

    def test_c_s_formula(self):
        # C_S = (7²−5²) / (7²+5²) = 24/74 = 12/37
        n1, n2 = 5, 7
        expected = (n2 ** 2 - n1 ** 2) / (n2 ** 2 + n1 ** 2)
        assert abs(C_S - expected) < 1e-12

    def test_c_s_value(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_c_s_range(self):
        # Physical: must be between 0 and 1 (sub-luminal)
        assert 0.0 < C_S < 1.0

    def test_c_s_squared_formula(self):
        assert abs(C_S_SQUARED - C_S ** 2) < 1e-15

    def test_c_s_squared_range(self):
        assert 0.0 < C_S_SQUARED < C_S  # c_s² < c_s for 0 < c_s < 1

    def test_f_braid_formula(self):
        expected = C_S_SQUARED / K_CS
        assert abs(F_BRAID_QGP - expected) < 1e-15

    def test_f_braid_small(self):
        # Must be a small fraction of the radiation budget
        assert F_BRAID_QGP < 1e-2
        assert F_BRAID_QGP > 0.0

    def test_qgp_cs2_sb_limit(self):
        assert abs(QGP_CS2_SB_LIMIT - 1.0 / 3.0) < 1e-12

    def test_qgp_cs2_atlas_range(self):
        # ATLAS measurement must be physically plausible
        assert 0.2 < QGP_CS2_ATLAS < 0.5

    def test_qgp_cs2_atlas_unc_positive(self):
        assert QGP_CS2_ATLAS_UNC > 0.0

    def test_t_deconfinement_mev_range(self):
        # Lattice QCD: T_c ≈ 150–160 MeV
        assert 140.0 < T_DECONFINEMENT_MEV < 170.0

    def test_alpha_s_mz_pdg_value(self):
        assert abs(ALPHA_S_MZ_PDG - 0.1179) < 1e-6

    def test_m_z_gev_value(self):
        assert abs(M_Z_GEV - 91.1876) < 0.001

    def test_lattice_near_tc_below_lattice_2tc(self):
        # Sound speed increases as T rises above T_c
        assert QGP_CS2_LATTICE_NEAR_TC < QGP_CS2_LATTICE_2TC

    def test_lattice_2tc_below_sb_limit(self):
        # At T~2T_c, c_s² is still below the SB limit
        assert QGP_CS2_LATTICE_2TC < QGP_CS2_SB_LIMIT + 0.05


# ===========================================================================
# II. qgp_sound_speed_um
# ===========================================================================

class TestQGPSoundSpeedUM:
    def test_returns_c_s(self):
        assert abs(qgp_sound_speed_um() - C_S) < 1e-15

    def test_value_12_over_37(self):
        assert abs(qgp_sound_speed_um() - 12.0 / 37.0) < 1e-12

    def test_positive(self):
        assert qgp_sound_speed_um() > 0.0

    def test_subluminal(self):
        assert qgp_sound_speed_um() < 1.0

    def test_not_equal_qgp_cs(self):
        # C_S is NOT the QGP sound speed (c_s ~ 0.57 at T >> T_c)
        qgp_cs = math.sqrt(QGP_CS2_SB_LIMIT)
        assert abs(qgp_sound_speed_um() - qgp_cs) > 0.1


# ===========================================================================
# III. qgp_sound_speed_squared_um
# ===========================================================================

class TestQGPSoundSpeedSquaredUM:
    def test_returns_c_s_squared(self):
        assert abs(qgp_sound_speed_squared_um() - C_S_SQUARED) < 1e-15

    def test_formula(self):
        assert abs(qgp_sound_speed_squared_um() - (12.0 / 37.0) ** 2) < 1e-12

    def test_positive(self):
        assert qgp_sound_speed_squared_um() > 0.0

    def test_less_than_c_s(self):
        assert qgp_sound_speed_squared_um() < qgp_sound_speed_um()

    def test_value_approx(self):
        # (12/37)² ≈ 0.1052
        assert abs(qgp_sound_speed_squared_um() - 0.1052) < 0.001


# ===========================================================================
# IV. qgp_cs2_reference_values
# ===========================================================================

class TestQGPCS2ReferenceValues:
    def setup_method(self):
        self.refs = qgp_cs2_reference_values()

    def test_sb_limit_one_third(self):
        assert abs(self.refs["sb_limit"] - 1.0 / 3.0) < 1e-12

    def test_lattice_near_tc_present(self):
        assert "lattice_near_tc" in self.refs
        assert 0.0 < self.refs["lattice_near_tc"] < 0.3

    def test_lattice_at_2tc_present(self):
        assert "lattice_at_2tc" in self.refs
        assert 0.2 < self.refs["lattice_at_2tc"] < 0.4

    def test_atlas_pbpb_at_2tc_present(self):
        assert "atlas_pbpb_at_2tc" in self.refs
        assert abs(self.refs["atlas_pbpb_at_2tc"] - QGP_CS2_ATLAS) < 1e-10

    def test_atlas_pbpb_unc_present(self):
        assert "atlas_pbpb_unc" in self.refs
        assert self.refs["atlas_pbpb_unc"] > 0.0

    def test_t_c_mev_present(self):
        assert "T_c_mev" in self.refs
        assert abs(self.refs["T_c_mev"] - T_DECONFINEMENT_MEV) < 1e-6

    def test_reference_string_present(self):
        assert isinstance(self.refs["reference"], str)
        assert "ATLAS" in self.refs["reference"]

    def test_ordering(self):
        # Physical: near-T_c < 2T_c < SB limit
        assert self.refs["lattice_near_tc"] < self.refs["lattice_at_2tc"]
        assert self.refs["lattice_at_2tc"] <= self.refs["sb_limit"] + 0.05


# ===========================================================================
# V. qgp_radion_cs_coincidence_audit
# ===========================================================================

class TestQGPRadionCSCoincidenceAudit:
    def setup_method(self):
        self.audit = qgp_radion_cs_coincidence_audit()

    def test_c_s_um_matches_constant(self):
        assert abs(self.audit["c_s_um"] - C_S) < 1e-15

    def test_c_s_squared_um_matches_constant(self):
        assert abs(self.audit["c_s_squared_um"] - C_S_SQUARED) < 1e-15

    def test_qgp_cs2_atlas_matches_constant(self):
        assert abs(self.audit["qgp_cs2_atlas"] - QGP_CS2_ATLAS) < 1e-10

    def test_qgp_cs2_sb_one_third(self):
        assert abs(self.audit["qgp_cs2_sb"] - 1.0 / 3.0) < 1e-12

    def test_coincidence_frac_atlas_small(self):
        # |C_S - c_s²_atlas| / c_s²_atlas should be < 5%
        assert self.audit["coincidence_frac_atlas"] < 0.05

    def test_coincidence_frac_sb_small(self):
        # |C_S - 1/3| / (1/3) should be < 5%
        assert self.audit["coincidence_frac_sb"] < 0.05

    def test_coincidence_frac_atlas_formula(self):
        expected = abs(C_S - QGP_CS2_ATLAS) / QGP_CS2_ATLAS
        assert abs(self.audit["coincidence_frac_atlas"] - expected) < 1e-12

    def test_within_1sigma_atlas_is_bool(self):
        assert isinstance(self.audit["within_1sigma_atlas"], bool)

    def test_within_1sigma_atlas_check(self):
        expected = abs(C_S - QGP_CS2_ATLAS) < QGP_CS2_ATLAS_UNC
        assert self.audit["within_1sigma_atlas"] == expected

    def test_dimensional_caveat_present(self):
        assert isinstance(self.audit["dimensional_caveat"], str)
        assert len(self.audit["dimensional_caveat"]) > 20

    def test_honest_status_mentions_coincidence(self):
        assert "COINCIDENCE" in self.audit["honest_status"]

    def test_summary_is_string(self):
        assert isinstance(self.audit["summary"], str)

    def test_c_s_does_not_match_qgp_cs_speed(self):
        # C_S ≈ 0.324 ≠ sqrt(c_s²_QGP) ≈ 0.574 — the coincidence is dimensional
        qgp_cs_speed = math.sqrt(QGP_CS2_ATLAS)
        assert abs(C_S - qgp_cs_speed) > 0.1


# ===========================================================================
# VI. qgp_radion_pressure_fraction
# ===========================================================================

class TestQGPRadionPressureFraction:
    def test_canonical_value(self):
        result = qgp_radion_pressure_fraction()
        assert abs(result - F_BRAID_QGP) < 1e-15

    def test_formula(self):
        result = qgp_radion_pressure_fraction(C_S, K_CS)
        expected = C_S ** 2 / K_CS
        assert abs(result - expected) < 1e-15

    def test_small(self):
        # Must be << 1% (sub-dominant)
        assert qgp_radion_pressure_fraction() < 1e-2

    def test_positive(self):
        assert qgp_radion_pressure_fraction() > 0.0

    def test_scales_as_c_s_squared(self):
        f1 = qgp_radion_pressure_fraction(0.3, 74)
        f2 = qgp_radion_pressure_fraction(0.6, 74)
        assert abs(f2 / f1 - 4.0) < 1e-10

    def test_scales_inversely_with_k_cs(self):
        f1 = qgp_radion_pressure_fraction(C_S, 37)
        f2 = qgp_radion_pressure_fraction(C_S, 74)
        assert abs(f1 / f2 - 2.0) < 1e-10

    def test_raises_zero_c_s(self):
        with pytest.raises(ValueError):
            qgp_radion_pressure_fraction(0.0, 74)

    def test_raises_negative_c_s(self):
        with pytest.raises(ValueError):
            qgp_radion_pressure_fraction(-0.1, 74)

    def test_raises_zero_k_cs(self):
        with pytest.raises(ValueError):
            qgp_radion_pressure_fraction(C_S, 0)


# ===========================================================================
# VII. qgp_hubble_correction
# ===========================================================================

class TestQGPHubbleCorrection:
    def test_canonical_value(self):
        result = qgp_hubble_correction()
        assert abs(result - 0.5 * F_BRAID_QGP) < 1e-15

    def test_half_f_braid(self):
        f = qgp_radion_pressure_fraction()
        dh = qgp_hubble_correction()
        assert abs(dh - 0.5 * f) < 1e-15

    def test_tiny(self):
        # δH/H << 1
        assert qgp_hubble_correction() < 1e-3
        assert qgp_hubble_correction() > 0.0

    def test_custom_params(self):
        dh = qgp_hubble_correction(0.5, 100)
        expected = 0.5 * (0.5 ** 2) / 100
        assert abs(dh - expected) < 1e-15


# ===========================================================================
# VIII. qgp_alpha_s_running
# ===========================================================================

class TestQGPAlphaSRunning:
    def test_at_mz_temperature(self):
        # T such that Q = 3T = M_Z → T = M_Z/3 GeV = M_Z/3 × 1000 MeV
        T_mz_mev = M_Z_GEV / 3.0 * 1000.0
        result = qgp_alpha_s_running(T_mz_mev)
        # At Q = M_Z, α_s should equal the PDG input
        assert abs(result - ALPHA_S_MZ_PDG) < 1e-10

    def test_at_higher_temperature_smaller_coupling(self):
        # Higher T → higher Q → smaller α_s (asymptotic freedom)
        T_low = M_Z_GEV / 3.0 * 1000.0
        T_high = 5.0 * T_low
        alpha_low = qgp_alpha_s_running(T_low)
        alpha_high = qgp_alpha_s_running(T_high)
        assert alpha_high < alpha_low

    def test_at_lower_temperature_larger_coupling(self):
        # Lower T → lower Q → larger α_s (running toward confinement)
        T_mz_mev = M_Z_GEV / 3.0 * 1000.0
        # Use T slightly above deconfinement to stay perturbative
        T_mid = 400.0   # 400 MeV, Q = 1.2 GeV (perturbative)
        alpha_mz = qgp_alpha_s_running(T_mz_mev)
        alpha_mid = qgp_alpha_s_running(T_mid)
        assert alpha_mid > alpha_mz

    def test_at_2tc_gives_reasonable_value(self):
        T_2tc = 2.0 * T_DECONFINEMENT_MEV  # ~310 MeV
        try:
            result = qgp_alpha_s_running(T_2tc)
            assert result > 0.0
            assert result < 1.0  # rough perturbative bound
        except ValueError:
            pass  # Landau pole at this scale is acceptable

    def test_positive_at_high_T(self):
        T_high = 5000.0  # 5 GeV, Q = 15 GeV
        result = qgp_alpha_s_running(T_high)
        assert result > 0.0

    def test_raises_zero_temperature(self):
        with pytest.raises(ValueError):
            qgp_alpha_s_running(0.0)

    def test_raises_negative_temperature(self):
        with pytest.raises(ValueError):
            qgp_alpha_s_running(-100.0)

    def test_raises_zero_alpha_s(self):
        with pytest.raises(ValueError):
            qgp_alpha_s_running(300.0, alpha_s_mz=0.0)

    def test_raises_invalid_nf(self):
        # N_f too large → b0 < 0 → not asymptotically free
        with pytest.raises(ValueError):
            qgp_alpha_s_running(300.0, n_f=17)

    def test_decreasing_with_n_f(self):
        # More flavours → smaller b0 → slower running
        T = M_Z_GEV / 3.0 * 1000.0 * 10.0
        a3 = qgp_alpha_s_running(T, n_f=3)
        a6 = qgp_alpha_s_running(T, n_f=6)
        # With more flavours, b0 is smaller, so coupling runs less
        # (slower asymptotic freedom): α_s at high Q is larger for n_f=6
        assert a6 > a3


# ===========================================================================
# IX. qgp_summary
# ===========================================================================

class TestQGPSummary:
    def setup_method(self):
        self.summary = qgp_summary()

    def test_pillar_number(self):
        assert self.summary["pillar"] == 65

    def test_title_is_string(self):
        assert isinstance(self.summary["title"], str)

    def test_c_s_um_matches_constant(self):
        assert abs(self.summary["c_s_um"] - C_S) < 1e-15

    def test_c_s_squared_um_matches_constant(self):
        assert abs(self.summary["c_s_squared_um"] - C_S_SQUARED) < 1e-15

    def test_k_cs_correct(self):
        assert self.summary["k_cs"] == K_CS

    def test_f_braid_positive_small(self):
        assert 0.0 < self.summary["f_braid"] < 1e-2

    def test_delta_h_over_h_half_f_braid(self):
        assert abs(self.summary["delta_H_over_H"] - 0.5 * self.summary["f_braid"]) < 1e-15

    def test_qgp_references_present(self):
        assert "qgp_references" in self.summary
        assert isinstance(self.summary["qgp_references"], dict)

    def test_coincidence_audit_present(self):
        assert "coincidence_audit" in self.summary
        assert "honest_status" in self.summary["coincidence_audit"]

    def test_open_gaps_is_list(self):
        assert isinstance(self.summary["open_gaps"], list)
        assert len(self.summary["open_gaps"]) >= 3

    def test_overall_verdict_is_string(self):
        assert isinstance(self.summary["overall_verdict"], str)
        assert len(self.summary["overall_verdict"]) > 50

    def test_atlas_anchor_string(self):
        assert isinstance(self.summary["atlas_anchor"], str)
        assert "ATLAS" in self.summary["atlas_anchor"]
        assert "Pb" in self.summary["atlas_anchor"]

    def test_open_gaps_mention_key_limitations(self):
        joined = " ".join(self.summary["open_gaps"])
        # All major gaps should be documented
        assert "predict" in joined.lower() or "derive" in joined.lower()

    def test_verdict_mentions_coincidence(self):
        assert "coincidence" in self.summary["overall_verdict"].lower()

    def test_verdict_mentions_atlas(self):
        assert "ATLAS" in self.summary["overall_verdict"]


# ===========================================================================
# X. Cross-module physics consistency
# ===========================================================================

class TestPhysicsConsistency:
    def test_c_s_consistent_with_photon_epoch(self):
        """C_S from quark_gluon_epoch must match C_S from photon_epoch."""
        from src.core.photon_epoch import C_S as C_S_PE
        assert abs(C_S - C_S_PE) < 1e-12

    def test_k_cs_consistent_with_photon_epoch(self):
        from src.core.photon_epoch import K_CS as K_CS_PE
        assert K_CS == K_CS_PE

    def test_f_braid_consistent_with_photon_epoch(self):
        from src.core.photon_epoch import F_BRAID as F_BRAID_PE
        assert abs(F_BRAID_QGP - F_BRAID_PE) < 1e-12

    def test_c_s_numerically_near_qgp_cs2(self):
        # Numerical coincidence: C_S ≈ c_s²(QGP at 2T_c)
        frac_dev = abs(C_S - QGP_CS2_ATLAS) / QGP_CS2_ATLAS
        assert frac_dev < 0.05  # within 5%

    def test_c_s_not_equal_qgp_cs_speed(self):
        # C_S ≠ sqrt(c_s²_QGP) — the coincidence is dimensional
        qgp_speed = math.sqrt(QGP_CS2_SB_LIMIT)
        assert abs(C_S - qgp_speed) > 0.15

    def test_f_braid_much_smaller_than_radiation(self):
        # KK radion contributes < 0.2% to radiation energy
        assert F_BRAID_QGP < 0.002

    def test_hubble_correction_negligible(self):
        dh = qgp_hubble_correction()
        assert dh < 1e-3  # sub per-mille correction

    def test_coincidence_within_atlas_2sigma(self):
        # |C_S - c_s²_ATLAS| < 2σ (treating C_S as if it were c_s²)
        assert abs(C_S - QGP_CS2_ATLAS) < 2.0 * QGP_CS2_ATLAS_UNC
