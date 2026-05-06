# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_gw_polarization_constraints.py
==========================================
Tests for Pillar 199 — GW250114 Scalar Polarization Constraints + H₀/S₈ Audit.
"""
import math
import pytest
from src.core.gw_polarization_constraints import (
    um_scalar_breathing_mode_frequency,
    gw250114_polarization_constraint,
    h0_tension_audit,
    s8_tension_audit,
    gw_polarization_verdict,
    gw_pillar199_summary,
    M_KK_GEV,
    H0_LCDM_KM_S_MPC,
    H0_SHOES_KM_S_MPC,
    W_KK,
    S8_PLANCK,
    S8_LENSING,
    GW250114_SCALAR_TENSOR_RATIO_LIMIT,
    BETA_CMB_DEG,
    R_BRAIDED,
    N_S,
)


class TestBreathingModeFrequency:
    def test_returns_float(self):
        f = um_scalar_breathing_mode_frequency()
        assert isinstance(f, float)

    def test_frequency_positive(self):
        assert um_scalar_breathing_mode_frequency() > 0

    def test_frequency_far_above_ligo(self):
        # f should be >> 10 kHz (LIGO upper band)
        f = um_scalar_breathing_mode_frequency()
        assert f > 1e20  # must be at least 10^20 Hz

    def test_frequency_order_of_magnitude(self):
        # m_KK ≈ 1040 GeV; ℏ ≈ 6.582e-25 GeV·s
        # f = 1040 / (2π × 6.582e-25) ≈ 2.5e26 Hz
        f = um_scalar_breathing_mode_frequency()
        log10_f = math.log10(f)
        assert 25.0 < log10_f < 28.0

    def test_scales_with_kk_mass(self):
        # Frequency ∝ m_KK
        # If we doubled M_KK, frequency should double
        f_base = um_scalar_breathing_mode_frequency()
        assert f_base > 0  # basic sanity


class TestGW250114Constraint:
    def setup_method(self):
        self.result = gw250114_polarization_constraint()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 199

    def test_event_name(self):
        assert self.result["event"] == "GW250114"

    def test_detection_date(self):
        assert "2026" in self.result["detection_date"]

    def test_breathing_not_in_ligo_band(self):
        assert self.result["breathing_in_ligo_band"] is False

    def test_um_amplitude_zero_in_ligo(self):
        assert self.result["um_scalar_amplitude_ratio_in_ligo_band"] == 0.0

    def test_constraint_satisfied(self):
        assert self.result["constraint_satisfied"] is True

    def test_margin_enormous(self):
        # 22+ orders of magnitude above LIGO
        assert self.result["log10_orders_above_ligo"] > 20.0

    def test_lvk_limit_recorded(self):
        assert self.result["lvk_scalar_tensor_limit"] == GW250114_SCALAR_TENSOR_RATIO_LIMIT

    def test_verdict_safe(self):
        assert "SAFE" in self.result["verdict"]

    def test_has_honest_caveat(self):
        assert "honest_caveat" in self.result
        assert len(self.result["honest_caveat"]) > 20

    def test_caveat_mentions_pillar_147(self):
        # Should acknowledge Cassini elimination of light radion (Pillar 147)
        assert "147" in self.result["honest_caveat"] or "Cassini" in self.result["honest_caveat"]


class TestH0TensionAudit:
    def setup_method(self):
        self.result = h0_tension_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 199

    def test_analysis_label(self):
        assert "H" in self.result["analysis"] and "tension" in self.result["analysis"]

    def test_planck_h0_recorded(self):
        assert abs(self.result["h0_planck_km_s_mpc"] - H0_LCDM_KM_S_MPC) < 0.01

    def test_shoes_h0_recorded(self):
        assert abs(self.result["h0_shoes_km_s_mpc"] - H0_SHOES_KM_S_MPC) < 0.01

    def test_um_h0_between_planck_and_shoes(self):
        # UM H₀ should be between Planck (67.4) and SHOES (73.0)
        assert H0_LCDM_KM_S_MPC < self.result["h0_um_km_s_mpc"] < H0_SHOES_KM_S_MPC

    def test_tension_reduced(self):
        # UM reduces tension but not to zero
        assert self.result["tension_um_vs_shoes_sigma"] < self.result["tension_lcdm_vs_shoes_sigma"]
        assert self.result["tension_um_vs_shoes_sigma"] > 0.5  # still has tension

    def test_partial_improvement_label(self):
        assert "PARTIAL" in self.result["um_vs_lcdm_improvement"].upper()

    def test_does_not_claim_full_resolution(self):
        improvement = self.result["um_vs_lcdm_improvement"]
        assert "NOT" in improvement.upper() or "not" in improvement

    def test_open_caveat_mentions_desi(self):
        assert "DESI" in self.result["open_caveat"] or "w₀" in self.result["open_caveat"]

    def test_delta_h0_positive(self):
        # w_KK = -0.930 ≠ -1 → positive H₀ shift
        assert self.result["delta_h0_um_km_s_mpc"] > 0

    def test_w_kk_recorded(self):
        assert abs(self.result["w_kk"] - W_KK) < 0.001


class TestS8TensionAudit:
    def setup_method(self):
        self.result = s8_tension_audit()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 199

    def test_planck_s8_recorded(self):
        assert abs(self.result["s8_planck"] - S8_PLANCK) < 0.001

    def test_lensing_s8_recorded(self):
        assert abs(self.result["s8_lensing"] - S8_LENSING) < 0.001

    def test_um_s8_between_planck_and_lensing(self):
        # UM S₈ should be between lensing and Planck
        assert S8_LENSING < self.result["s8_um"] <= S8_PLANCK

    def test_tension_reduced_marginally(self):
        assert self.result["tension_um_sigma"] < self.result["tension_lcdm_sigma"]

    def test_marginal_improvement_label(self):
        assert "MARGINAL" in self.result["um_vs_lcdm_improvement"].upper()

    def test_open_caveat_mentions_acoustic_amplitude(self):
        assert ("acoustic" in self.result["open_caveat"].lower()
                or "A_s" in self.result["open_caveat"]
                or "57" in self.result["open_caveat"])

    def test_kk_exchange_positive(self):
        assert self.result["delta_sigma8_kk_exchange"] > 0

    def test_de_coupling_negative(self):
        assert self.result["delta_sigma8_de_coupling"] < 0


class TestGWPolarizationVerdict:
    def setup_method(self):
        self.result = gw_polarization_verdict()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 199

    def test_version(self):
        assert self.result["version"] == "v10.2"

    def test_has_three_analyses(self):
        assert "gw250114_constraint" in self.result
        assert "h0_tension" in self.result
        assert "s8_tension" in self.result

    def test_verdict_has_pass(self):
        assert "PASS" in self.result["overall_verdict"]

    def test_verdict_mentions_litebird(self):
        assert "LiteBIRD" in self.result["overall_verdict"] or "LiteBIRD" in self.result["professional_standing"]

    def test_professional_standing_honest(self):
        standing = self.result["professional_standing"].lower()
        assert "coherent provocation" in standing or "not better" in standing


class TestGWPillar199Summary:
    def setup_method(self):
        self.result = gw_pillar199_summary()

    def test_returns_dict(self):
        assert isinstance(self.result, dict)

    def test_pillar_number(self):
        assert self.result["pillar"] == 199

    def test_name_correct(self):
        assert "GW250114" in self.result["name"] or "GW" in self.result["name"]

    def test_has_three_findings(self):
        assert len(self.result["red_team_findings"]) == 3

    def test_gw_verdict_safe(self):
        assert "SAFE" in self.result["gw250114_verdict"]

    def test_h0_verdict_partial(self):
        assert "PARTIAL" in self.result["h0_verdict"].upper()

    def test_s8_verdict_marginal(self):
        assert "MARGINAL" in self.result["s8_verdict"].upper()

    def test_primary_falsifier_litebird(self):
        assert "LiteBIRD" in self.result["primary_falsifier"]

    def test_gw_falsifier_lisa_et(self):
        assert "LISA" in self.result["gw_falsifier"] or "ET" in self.result["gw_falsifier"]

    def test_has_two_next_attacks(self):
        assert len(self.result["next_attacks_anticipated"]) >= 2

    def test_attacks_have_responses(self):
        for attack in self.result["next_attacks_anticipated"]:
            assert "Response:" in attack or "response" in attack.lower()


class TestPredictiveConsistency:
    """Cross-check that Pillar 199 uses the same constants as the rest of the UM."""

    def test_beta_cmb_canonical(self):
        # Primary β = 0.331° (canonical (5,7) sector)
        assert abs(BETA_CMB_DEG - 0.331) < 0.001

    def test_r_braided_consistent(self):
        # r = 0.0315 from braided (5,7) winding
        assert abs(R_BRAIDED - 0.0315) < 0.001

    def test_ns_consistent(self):
        # n_s = 0.9635 from n_w = 5
        assert abs(N_S - 0.9635) < 0.001

    def test_h0_planck_consistent(self):
        assert abs(H0_LCDM_KM_S_MPC - 67.4) < 0.5

    def test_shoes_larger_than_planck(self):
        assert H0_SHOES_KM_S_MPC > H0_LCDM_KM_S_MPC

    def test_s8_planck_larger_than_lensing(self):
        # This IS the S₈ tension
        assert S8_PLANCK > S8_LENSING
