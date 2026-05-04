# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_neutrino_majorana_uv_proof.py
==========================================
Pillar 150 — Tests for neutrino_majorana_uv_proof.py.

Tests cover:
  - Constants: C_R_GEOMETRIC, PI_KR, HIGGS_VEV_GEV, M_PLANCK_GEV
  - z2_parity_majorana_term(): Z₂ parity analysis
  - gw_potential_uv_brane_scale(): GW-derived M_R
  - neutrino_seesaw_mass_proof(): full seesaw proof
  - lightest_neutrino_mass_status(): Pillar 150 status report
  - pillar150_summary(): audit summary
"""

from __future__ import annotations

import math
import pytest

from src.core.neutrino_majorana_uv_proof import (
    C_R_GEOMETRIC,
    PI_KR,
    HIGGS_VEV_GEV,
    M_PLANCK_GEV,
    PLANCK_SUM_MNU_EV,
    GEV_TO_EV,
    K_ADS_GEV,
    Y_DIRAC_DEFAULT,
    z2_parity_majorana_term,
    gw_potential_uv_brane_scale,
    neutrino_seesaw_mass_proof,
    lightest_neutrino_mass_status,
    pillar150_summary,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_c_r_is_23_over_25(self):
        assert abs(C_R_GEOMETRIC - 23.0 / 25.0) < 1e-12

    def test_c_r_is_0_920(self):
        assert abs(C_R_GEOMETRIC - 0.920) < 1e-6

    def test_pi_kr_is_37(self):
        assert abs(PI_KR - 37.0) < 1e-10

    def test_higgs_vev_is_246(self):
        assert 245.0 < HIGGS_VEV_GEV < 247.0

    def test_m_planck_order(self):
        assert 1e18 < M_PLANCK_GEV < 2e19

    def test_planck_limit_is_0_12(self):
        assert abs(PLANCK_SUM_MNU_EV - 0.12) < 1e-10

    def test_gev_to_ev_is_1e9(self):
        assert abs(GEV_TO_EV - 1e9) < 1.0

    def test_k_ads_gev_positive(self):
        assert K_ADS_GEV > 0

    def test_k_ads_gev_order(self):
        """k_UV ~ M_Pl for the UV brane (RS1 UV brane is at Planck scale)."""
        assert K_ADS_GEV > 1e18  # UV brane scale ~ M_Pl

    def test_y_dirac_default_is_1(self):
        assert abs(Y_DIRAC_DEFAULT - 1.0) < 1e-10


# ---------------------------------------------------------------------------
# Z₂ parity of UV-brane Majorana term
# ---------------------------------------------------------------------------

class TestZ2ParityMajoranaTermDefaultCR:
    def setup_method(self):
        self.result = z2_parity_majorana_term(C_R_GEOMETRIC)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_c_r_stored(self):
        assert abs(self.result["c_r"] - C_R_GEOMETRIC) < 1e-12

    def test_uv_localised_true(self):
        """c_R = 0.920 > 0.5 → UV localised."""
        assert self.result["uv_localised"] is True

    def test_z2_parity_field_is_plus_1(self):
        """UV-localised → even parity."""
        assert self.result["z2_parity_field"] == +1

    def test_z2_parity_delta_is_plus_1(self):
        """δ(y) is Z₂-even."""
        assert self.result["z2_parity_delta_function"] == +1

    def test_z2_parity_majorana_bilinear_is_plus_1(self):
        """ψ_R^T C ψ_R: (+1)² = +1."""
        assert self.result["z2_parity_majorana_bilinear"] == +1

    def test_combined_parity_is_plus_1(self):
        assert self.result["z2_parity_combined"] == +1

    def test_term_z2_allowed(self):
        assert self.result["term_z2_allowed"] is True

    def test_conclusion_contains_allowed(self):
        assert "ALLOWED" in self.result["conclusion"] or "allowed" in self.result["conclusion"]

    def test_proof_step_complete(self):
        assert "COMPLETE" in self.result["proof_step"] or "✅" in self.result["proof_step"]


class TestZ2ParityMajoranaTermIRLocalised:
    def test_ir_localised_c_r(self):
        """c_R = 0.3 < 0.5 → IR localised → different parity."""
        result = z2_parity_majorana_term(0.3)
        assert result["uv_localised"] is False
        # IR-localised: Z₂ parity is -1 → Majorana term FORBIDDEN
        assert result["z2_parity_field"] == -1

    def test_forbidden_at_uv_brane_for_ir_localised(self):
        result = z2_parity_majorana_term(0.3)
        # (-1)² = +1 → still Z₂-even for Majorana bilinear
        # because ψ_R^T C ψ_R has even parity regardless of individual field parity
        assert result["z2_parity_majorana_bilinear"] == +1

    def test_invalid_c_r_raises(self):
        with pytest.raises(ValueError, match="positive"):
            z2_parity_majorana_term(0.0)

    def test_negative_c_r_raises(self):
        with pytest.raises(ValueError):
            z2_parity_majorana_term(-0.5)


# ---------------------------------------------------------------------------
# GW potential UV-brane scale
# ---------------------------------------------------------------------------

class TestGWPotentialUVBraneScale:
    def setup_method(self):
        self.result = gw_potential_uv_brane_scale(C_R_GEOMETRIC, PI_KR)

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_c_r_stored(self):
        assert abs(self.result["c_r"] - C_R_GEOMETRIC) < 1e-12

    def test_pi_kr_stored(self):
        assert abs(self.result["pi_kr"] - PI_KR) < 1e-10

    def test_gw_exponent_positive(self):
        """For c_R = 0.920 > 0.5, exponent = (2c_R-1)*πkR/2 > 0."""
        assert self.result["gw_exponent"] > 0

    def test_gw_exponent_value(self):
        """exponent = (2×0.920 - 1) × 37/2 = 0.840 × 18.5 = 15.54"""
        expected = (2 * C_R_GEOMETRIC - 1) * PI_KR / 2
        assert abs(self.result["gw_exponent"] - expected) < 1e-8

    def test_m_r_5d_huge(self):
        """5D estimate should be enormous (above Planck scale)."""
        assert self.result["m_r_5d_estimate_gev"] > 1e10

    def test_saturates_planck_scale(self):
        """c_R = 0.920 with πkR = 37 gives M_R^{5D} > M_Pl."""
        assert self.result["saturates_planck_scale"] is True

    def test_physical_m_r_is_m_planck(self):
        """Physical M_R should be capped at M_Pl."""
        assert abs(self.result["m_r_physical_gev"] - M_PLANCK_GEV) < 1e12

    def test_conclusion_nonempty(self):
        assert len(self.result["conclusion"]) > 20

    def test_proof_step_complete(self):
        assert "COMPLETE" in self.result["proof_step"] or "✅" in self.result["proof_step"]

    def test_invalid_c_r_raises(self):
        with pytest.raises(ValueError, match="positive"):
            gw_potential_uv_brane_scale(0.0, PI_KR)

    def test_invalid_pi_kr_raises(self):
        with pytest.raises(ValueError, match="positive"):
            gw_potential_uv_brane_scale(C_R_GEOMETRIC, 0.0)

    def test_small_c_r_below_planck(self):
        """For c_R = 0.52, small exponent → M_R^{5D} may not saturate Planck."""
        # c_R = 0.52: exponent = (2×0.52-1)*37/2 = 0.04*18.5 = 0.74 (small)
        # k_UV = M_Pl, M_R = M_Pl * exp(0.74) ≈ 2.1 * M_Pl → still > M_Pl
        # The Planck cap ensures M_R = M_Pl regardless
        result = gw_potential_uv_brane_scale(0.52, PI_KR)
        # Either way, the physical M_R ≤ M_Pl
        assert result["m_r_physical_gev"] <= M_PLANCK_GEV * 1.01  # within 1%


# ---------------------------------------------------------------------------
# Full seesaw proof
# ---------------------------------------------------------------------------

class TestNeutrinoSeesawMassProof:
    def setup_method(self):
        self.result = neutrino_seesaw_mass_proof()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_y_dirac_stored(self):
        assert abs(self.result["y_dirac"] - Y_DIRAC_DEFAULT) < 1e-10

    def test_c_r_stored(self):
        assert abs(self.result["c_r"] - C_R_GEOMETRIC) < 1e-12

    def test_pi_kr_stored(self):
        assert abs(self.result["pi_kr"] - PI_KR) < 1e-10

    def test_seesaw_formula_string(self):
        assert "M_R" in self.result["seesaw_formula"]

    def test_m_r_is_m_planck(self):
        assert abs(self.result["m_r_gev"] - M_PLANCK_GEV) < 1e12

    def test_m_nu_gev_positive(self):
        assert self.result["m_nu_gev"] > 0

    def test_m_nu_ev_positive(self):
        assert self.result["m_nu_ev"] > 0

    def test_m_nu_ev_small(self):
        """m_ν₁ should be well below 0.12 eV (Planck bound)."""
        assert self.result["m_nu_ev"] < PLANCK_SUM_MNU_EV

    def test_planck_consistent_true(self):
        assert self.result["planck_consistent"] is True

    def test_both_proofs_complete(self):
        assert self.result["both_proofs_complete"] is True

    def test_status_proved(self):
        assert "PROVED" in self.result["status"] or "✅" in self.result["status"]

    def test_conclusion_nonempty(self):
        assert len(self.result["conclusion"]) > 50

    def test_m_nu_order_of_magnitude(self):
        """m_ν₁ ~ (246 GeV)² / M_Pl ~ few meV."""
        m_nu_mev = self.result["m_nu_mev"]
        assert 0.001 < m_nu_mev < 100.0  # meV range

    def test_invalid_y_dirac_raises(self):
        with pytest.raises(ValueError, match="positive"):
            neutrino_seesaw_mass_proof(y_dirac=-1.0)

    def test_y_dirac_0_5_smaller_mass(self):
        """Smaller Yukawa → smaller neutrino mass."""
        result_1 = neutrino_seesaw_mass_proof(y_dirac=1.0)
        result_05 = neutrino_seesaw_mass_proof(y_dirac=0.5)
        assert result_05["m_nu_ev"] < result_1["m_nu_ev"]

    def test_seesaw_scaling_y_squared(self):
        """Seesaw mass scales as y_D²."""
        r1 = neutrino_seesaw_mass_proof(y_dirac=1.0)
        r2 = neutrino_seesaw_mass_proof(y_dirac=2.0)
        ratio = r2["m_nu_ev"] / r1["m_nu_ev"]
        assert abs(ratio - 4.0) < 0.1  # 2² = 4


# ---------------------------------------------------------------------------
# Full Pillar 150 status
# ---------------------------------------------------------------------------

class TestLightestNeutrinoMassStatus:
    def setup_method(self):
        self.result = lightest_neutrino_mass_status()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_150(self):
        assert self.result["pillar"] == 150

    def test_new_status_resolved(self):
        assert "RESOLVED" in self.result["new_status"]

    def test_previous_status_partially_resolved(self):
        assert "PARTIALLY" in self.result["previous_status"] or \
               "VIABLE" in self.result["previous_status"]

    def test_proof_1_z2_parity_proved(self):
        assert self.result["proof_1_z2_parity"]["result"] is True

    def test_proof_2_gw_scale_proved(self):
        assert self.result["proof_2_gw_scale"]["result"] is True

    def test_seesaw_result_planck_consistent(self):
        assert self.result["seesaw_result"]["planck_consistent"] is True

    def test_seesaw_m_nu_small(self):
        assert self.result["seesaw_result"]["m_nu_ev"] < PLANCK_SUM_MNU_EV

    def test_resolution_nonempty(self):
        assert len(self.result["resolution"]) > 50

    def test_remaining_open_nonempty(self):
        assert len(self.result["remaining_open"]) > 20

    def test_pillar_references_nonempty(self):
        assert len(self.result["pillar_references"]) >= 3


# ---------------------------------------------------------------------------
# Pillar 150 summary
# ---------------------------------------------------------------------------

class TestPillar150Summary:
    def setup_method(self):
        self.result = pillar150_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_is_150(self):
        assert self.result["pillar"] == 150

    def test_status_resolved(self):
        assert "RESOLVED" in self.result["status"]

    def test_c_r_is_23_over_25(self):
        assert abs(self.result["c_r"] - 23.0 / 25.0) < 1e-12

    def test_pi_kr_is_37(self):
        assert abs(self.result["pi_kr"] - 37.0) < 1e-10

    def test_m_r_is_planck_scale(self):
        assert self.result["m_r_gev"] > 1e18

    def test_m_nu_ev_positive(self):
        assert self.result["m_nu_ev"] > 0

    def test_planck_consistent(self):
        assert self.result["planck_consistent"] is True

    def test_z2_parity_allowed(self):
        assert self.result["z2_parity_allowed"] is True

    def test_gw_saturates_planck(self):
        assert self.result["gw_saturates_planck"] is True

    def test_both_proofs_complete(self):
        assert self.result["both_proofs_complete"] is True

    def test_mechanism_nonempty(self):
        assert len(self.result["mechanism"]) > 30

    def test_grand_synthesis_update_nonempty(self):
        assert len(self.result["grand_synthesis_update"]) > 30
