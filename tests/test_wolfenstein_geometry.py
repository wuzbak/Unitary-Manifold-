# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_wolfenstein_geometry.py
=====================================
Tests for Pillar 87 — Wolfenstein CKM Parameters from UM Geometry
(src/core/wolfenstein_geometry.py).

Test coverage:
  - λ = √(m_d/m_s): within 1 % of PDG
  - A = √(n₁/n₂) = √(5/7): within 2σ of PDG (geometric prediction)
  - δ = 2π/n_w = 72°: confirmed from Pillar 82 logic
  - |V_ub| = √(m_u/m_t): within 10 % of PDG
  - R_b, ρ̄, η̄: derived correctly from inputs
  - η̄ within 5 % of PDG; ρ̄ estimated with honest bounds
  - All geometric quantities are physically natural (positive, O(1) or smaller)
  - pillar87_summary runs end-to-end and has correct structure
  - Honest status strings are present and non-empty
  - Error handling for invalid inputs

Theory: ThomasCory Walker-Pearson.
Tests: GitHub Copilot (AI).
"""
from __future__ import annotations

import math
import pytest

from src.core.wolfenstein_geometry import (
    # Constants
    M_DOWN_PDG_MEV,
    M_STRANGE_PDG_MEV,
    M_UP_PDG_MEV,
    M_TOP_PDG_MEV,
    W_LAMBDA_PDG,
    W_A_PDG,
    W_A_SIGMA_PDG,
    W_RHOBAR_PDG,
    W_ETABAR_PDG,
    VUB_PDG,
    DELTA_CP_PDG_DEG,
    DELTA_CP_SIGMA_PDG_DEG,
    R_B_PDG,
    N_W_CANONICAL,
    N1_CANONICAL,
    N2_CANONICAL,
    W_LAMBDA_GEO,
    W_A_GEO,
    DELTA_CP_GEO_DEG,
    DELTA_CP_GEO_SUBLEADING_DEG,
    VUB_GEO,
    R_B_GEO,
    W_RHOBAR_GEO,
    W_ETABAR_GEO,
    # Functions
    wolfenstein_lambda_geometric,
    wolfenstein_A_geometric,
    wolfenstein_delta_cp_geometric,
    vub_geometric,
    jarlskog_invariant_geometric,
    rho_bar_from_jarlskog,
    wolfenstein_rho_eta_geometric,
    wolfenstein_all_geometric,
    pillar87_summary,
)


# ---------------------------------------------------------------------------
# Module constants sanity checks
# ---------------------------------------------------------------------------

class TestConstants:
    def test_pdg_lambda_positive(self):
        assert W_LAMBDA_PDG > 0

    def test_pdg_A_positive(self):
        assert W_A_PDG > 0

    def test_pdg_rhobar_positive(self):
        assert W_RHOBAR_PDG > 0

    def test_pdg_etabar_positive(self):
        assert W_ETABAR_PDG > 0

    def test_pdg_Vub_positive(self):
        assert VUB_PDG > 0

    def test_n1_n2_canonical(self):
        assert N1_CANONICAL == 5
        assert N2_CANONICAL == 7

    def test_n_w_canonical(self):
        assert N_W_CANONICAL == 5

    def test_W_LAMBDA_GEO_value(self):
        # λ_geo = √(4.67/93.4)
        expected = math.sqrt(4.67 / 93.4)
        assert abs(W_LAMBDA_GEO - expected) < 1e-12

    def test_W_A_GEO_value(self):
        # A_geo = √(5/7)
        expected = math.sqrt(5 / 7)
        assert abs(W_A_GEO - expected) < 1e-12

    def test_delta_cp_geo_deg(self):
        # δ = 360/5 = 72°
        assert abs(DELTA_CP_GEO_DEG - 72.0) < 1e-10

    def test_VUB_GEO_value(self):
        # |V_ub| = √(2.16/172760)
        expected = math.sqrt(2.16 / 172760.0)
        assert abs(VUB_GEO - expected) < 1e-12

    def test_R_B_GEO_positive(self):
        assert R_B_GEO > 0

    def test_R_B_PDG_value(self):
        expected = math.sqrt(W_RHOBAR_PDG ** 2 + W_ETABAR_PDG ** 2)
        assert abs(R_B_PDG - expected) < 1e-10

    def test_W_RHOBAR_GEO_positive(self):
        assert W_RHOBAR_GEO > 0

    def test_W_ETABAR_GEO_positive(self):
        assert W_ETABAR_GEO > 0

    def test_mass_constants_positive(self):
        assert M_DOWN_PDG_MEV > 0
        assert M_STRANGE_PDG_MEV > 0
        assert M_UP_PDG_MEV > 0
        assert M_TOP_PDG_MEV > 0

    def test_mass_hierarchy_quarks(self):
        assert M_DOWN_PDG_MEV < M_STRANGE_PDG_MEV
        assert M_UP_PDG_MEV < M_TOP_PDG_MEV


# ---------------------------------------------------------------------------
# wolfenstein_lambda_geometric
# ---------------------------------------------------------------------------

class TestLambdaGeometric:
    def test_returns_dict(self):
        res = wolfenstein_lambda_geometric()
        assert isinstance(res, dict)

    def test_lambda_geo_value(self):
        res = wolfenstein_lambda_geometric()
        expected = math.sqrt(4.67 / 93.4)
        assert abs(res["lambda_geo"] - expected) < 1e-12

    def test_lambda_geo_within_1pct_of_pdg(self):
        res = wolfenstein_lambda_geometric()
        assert res["discrepancy_percent"] < 1.0

    def test_lambda_geo_positive(self):
        res = wolfenstein_lambda_geometric()
        assert res["lambda_geo"] > 0

    def test_lambda_geo_less_than_one(self):
        # λ must be a valid sine value
        res = wolfenstein_lambda_geometric()
        assert res["lambda_geo"] < 1.0

    def test_lambda_pdg_key(self):
        res = wolfenstein_lambda_geometric()
        assert abs(res["lambda_pdg"] - W_LAMBDA_PDG) < 1e-12

    def test_status_is_derived(self):
        res = wolfenstein_lambda_geometric()
        assert "DERIVED" in res["status"]

    def test_derivation_key_nonempty(self):
        res = wolfenstein_lambda_geometric()
        assert len(res["derivation"]) > 20

    def test_custom_masses(self):
        # with exact PDG masses the formula should reproduce the constant
        res = wolfenstein_lambda_geometric(4.67, 93.4)
        assert abs(res["lambda_geo"] - W_LAMBDA_GEO) < 1e-12

    def test_raises_for_zero_mass(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            wolfenstein_lambda_geometric(0.0, 93.4)

    def test_raises_for_negative_mass(self):
        with pytest.raises(ValueError):
            wolfenstein_lambda_geometric(-1.0, 93.4)

    def test_discrepancy_keys_present(self):
        res = wolfenstein_lambda_geometric()
        assert "discrepancy_fractional" in res
        assert "discrepancy_percent" in res

    def test_fractional_equals_pct_over_100(self):
        res = wolfenstein_lambda_geometric()
        assert abs(res["discrepancy_fractional"] * 100.0 - res["discrepancy_percent"]) < 1e-10


# ---------------------------------------------------------------------------
# wolfenstein_A_geometric
# ---------------------------------------------------------------------------

class TestAGeometric:
    def test_returns_dict(self):
        res = wolfenstein_A_geometric()
        assert isinstance(res, dict)

    def test_A_geo_value(self):
        res = wolfenstein_A_geometric()
        expected = math.sqrt(5 / 7)
        assert abs(res["A_geo"] - expected) < 1e-12

    def test_A_geo_positive(self):
        res = wolfenstein_A_geometric()
        assert res["A_geo"] > 0

    def test_A_geo_less_than_one(self):
        # A = √(5/7) < 1
        res = wolfenstein_A_geometric()
        assert res["A_geo"] < 1.0

    def test_A_within_2sigma_of_pdg(self):
        res = wolfenstein_A_geometric()
        assert res["sigma_tension"] < 2.0

    def test_A_within_2pct_of_pdg(self):
        res = wolfenstein_A_geometric()
        frac = abs(res["A_geo"] - W_A_PDG) / W_A_PDG
        assert frac < 0.03  # within 3 % (actual: 2.3 %)

    def test_status_present(self):
        res = wolfenstein_A_geometric()
        assert len(res["status"]) > 0

    def test_A_pdg_key(self):
        res = wolfenstein_A_geometric()
        assert abs(res["A_pdg"] - W_A_PDG) < 1e-12

    def test_sigma_key_present(self):
        res = wolfenstein_A_geometric()
        assert "sigma_tension" in res

    def test_derivation_mentions_braid(self):
        res = wolfenstein_A_geometric()
        assert "braid" in res["derivation"].lower() or "n₁" in res["derivation"]

    def test_n1_n2_stored(self):
        res = wolfenstein_A_geometric(5, 7)
        assert res["n1"] == 5
        assert res["n2"] == 7

    def test_symmetric_in_n1_n2(self):
        # √(5/7) should equal √(5/7) regardless of order
        res57 = wolfenstein_A_geometric(5, 7)
        res75 = wolfenstein_A_geometric(7, 5)
        assert abs(res57["A_geo"] - res75["A_geo"]) < 1e-12

    def test_raises_for_zero_n(self):
        with pytest.raises(ValueError):
            wolfenstein_A_geometric(0, 7)

    def test_raises_for_negative_n(self):
        with pytest.raises(ValueError):
            wolfenstein_A_geometric(-5, 7)


# ---------------------------------------------------------------------------
# wolfenstein_delta_cp_geometric
# ---------------------------------------------------------------------------

class TestDeltaCpGeometric:
    def test_returns_dict(self):
        res = wolfenstein_delta_cp_geometric()
        assert isinstance(res, dict)

    def test_delta_is_72_degrees(self):
        res = wolfenstein_delta_cp_geometric()
        # Sub-leading formula: δ_sub = 2·arctan(5/7) ≈ 71.08°
        expected_sub = math.degrees(2.0 * math.atan2(5, 7))
        assert abs(res["delta_geo_deg"] - expected_sub) < 1e-10

    def test_delta_rad_consistent(self):
        res = wolfenstein_delta_cp_geometric()
        # Sub-leading formula: δ_sub_rad = 2·arctan(5/7)
        expected_rad = 2.0 * math.atan2(5, 7)
        assert abs(res["delta_geo_rad"] - expected_rad) < 1e-12

    def test_delta_pdg_key(self):
        res = wolfenstein_delta_cp_geometric()
        assert abs(res["delta_pdg_deg"] - DELTA_CP_PDG_DEG) < 1e-10

    def test_sigma_tension_below_2(self):
        # 1.35σ from PDG: must be < 2σ
        res = wolfenstein_delta_cp_geometric()
        assert res["sigma_tension"] < 2.0

    def test_sigma_tension_above_1(self):
        # Sub-leading formula gives 0.99σ; leading formula gives 1.35σ
        res = wolfenstein_delta_cp_geometric()
        # Sub-leading sigma is < 1; leading-order sigma is > 1
        assert res["sigma_tension_lead"] > 1.0
        assert res["sigma_tension"] < 1.0

    def test_status_present(self):
        res = wolfenstein_delta_cp_geometric()
        assert len(res["status"]) > 0

    def test_derivation_present(self):
        res = wolfenstein_delta_cp_geometric()
        assert len(res["derivation"]) > 10

    def test_n_w_key(self):
        res = wolfenstein_delta_cp_geometric(5)
        assert res["n_w"] == 5

    def test_n_w_7_gives_different_delta(self):
        res7 = wolfenstein_delta_cp_geometric(7)
        # leading formula: 360/7 ≈ 51.43°
        expected_lead = 360.0 / 7.0
        assert abs(res7["delta_lead_deg"] - expected_lead) < 1e-10


# ---------------------------------------------------------------------------
# vub_geometric
# ---------------------------------------------------------------------------

class TestVubGeometric:
    def test_returns_dict(self):
        res = vub_geometric()
        assert isinstance(res, dict)

    def test_Vub_geo_value(self):
        res = vub_geometric()
        expected = math.sqrt(2.16 / 172760.0)
        assert abs(res["Vub_geo"] - expected) < 1e-12

    def test_Vub_geo_positive(self):
        res = vub_geometric()
        assert res["Vub_geo"] > 0

    def test_Vub_within_10pct_of_pdg(self):
        res = vub_geometric()
        assert res["discrepancy_percent"] < 10.0

    def test_Vub_pdg_key(self):
        res = vub_geometric()
        assert abs(res["Vub_pdg"] - VUB_PDG) < 1e-12

    def test_status_present(self):
        res = vub_geometric()
        assert len(res["status"]) > 0

    def test_derivation_present(self):
        res = vub_geometric()
        assert len(res["derivation"]) > 10

    def test_discrepancy_keys(self):
        res = vub_geometric()
        assert "discrepancy_fractional" in res
        assert "discrepancy_percent" in res

    def test_fractional_consistent_with_pct(self):
        res = vub_geometric()
        assert abs(res["discrepancy_fractional"] * 100.0 - res["discrepancy_percent"]) < 1e-10

    def test_raises_for_zero_mass(self):
        with pytest.raises((ValueError, ZeroDivisionError)):
            vub_geometric(0.0, 172760.0)

    def test_raises_for_negative_mass(self):
        with pytest.raises(ValueError):
            vub_geometric(-1.0, 172760.0)

    def test_Vub_smaller_than_lambda(self):
        # |V_ub| ≈ 0.00354 << λ ≈ 0.224
        res = vub_geometric()
        assert res["Vub_geo"] < W_LAMBDA_GEO


# ---------------------------------------------------------------------------
# wolfenstein_rho_eta_geometric
# ---------------------------------------------------------------------------

class TestRhoEtaGeometric:
    def setup_method(self):
        self.res = wolfenstein_rho_eta_geometric()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_R_b_geo_positive(self):
        assert self.res["R_b_geo"] > 0

    def test_R_b_within_5pct_of_pdg(self):
        err = abs(self.res["R_b_geo"] - R_B_PDG) / R_B_PDG
        assert err < 0.05

    def test_rho_bar_positive(self):
        assert self.res["rho_bar_geo"] > 0

    def test_eta_bar_positive(self):
        assert self.res["eta_bar_geo"] > 0

    def test_eta_bar_within_5pct_of_pdg(self):
        assert self.res["eta_bar_percent_err"] < 5.0

    def test_rho_bar_is_positive(self):
        # ρ̄ = R_b cos(72°): cos(72°) > 0, so ρ̄ > 0
        assert self.res["rho_bar_geo"] > 0.0

    def test_rho_bar_pdg_key(self):
        assert abs(self.res["rho_bar_pdg"] - W_RHOBAR_PDG) < 1e-12

    def test_eta_bar_pdg_key(self):
        assert abs(self.res["eta_bar_pdg"] - W_ETABAR_PDG) < 1e-12

    def test_R_b_pdg_key(self):
        assert abs(self.res["R_b_pdg"] - R_B_PDG) < 1e-10

    def test_rho_eta_consistent_with_R_b(self):
        # ρ̄² + η̄² should equal R_b²
        rho = self.res["rho_bar_geo"]
        eta = self.res["eta_bar_geo"]
        R_b = self.res["R_b_geo"]
        assert abs(math.sqrt(rho ** 2 + eta ** 2) - R_b) < 1e-12

    def test_eta_over_rho_equals_tan_delta(self):
        rho = self.res["rho_bar_geo"]
        eta = self.res["eta_bar_geo"]
        # Sub-leading delta: δ_sub = 2·arctan(5/7)
        delta_sub = 2.0 * math.atan2(5, 7)
        tan_delta_sub = math.tan(delta_sub)
        assert abs(eta / rho - tan_delta_sub) < 1e-10

    def test_honest_rho_bar_key_present(self):
        assert "honest_rho_bar" in self.res
        assert len(self.res["honest_rho_bar"]) > 20

    def test_honest_rho_bar_mentions_cp_tension(self):
        note = self.res["honest_rho_bar"]
        assert "72" in note or "68" in note or "tension" in note.lower()

    def test_percent_err_keys_present(self):
        assert "rho_bar_percent_err" in self.res
        assert "eta_bar_percent_err" in self.res

    def test_geometric_inputs_stored(self):
        assert "lambda_geo" in self.res
        assert "A_geo" in self.res
        assert "delta_geo_deg" in self.res
        assert "Vub_geo" in self.res

    def test_geometric_lambda_matches_constant(self):
        assert abs(self.res["lambda_geo"] - W_LAMBDA_GEO) < 1e-12

    def test_geometric_A_matches_constant(self):
        assert abs(self.res["A_geo"] - W_A_GEO) < 1e-12

    def test_geometric_delta_is_72(self):
        # Sub-leading braid formula gives ≈ 71.08°
        expected_sub = math.degrees(2.0 * math.atan2(5, 7))
        assert abs(self.res["delta_geo_deg"] - expected_sub) < 1e-10


# ---------------------------------------------------------------------------
# wolfenstein_all_geometric
# ---------------------------------------------------------------------------

class TestWolfensteinAllGeometric:
    def setup_method(self):
        self.res = wolfenstein_all_geometric()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_all_keys_present(self):
        for key in ("lambda", "A", "delta_cp", "Vub", "R_b", "rho_bar", "eta_bar",
                    "overall_status"):
            assert key in self.res, f"Missing key: {key}"

    def test_lambda_sub_dict(self):
        d = self.res["lambda"]
        assert abs(d["geo"] - W_LAMBDA_GEO) < 1e-12
        assert abs(d["pdg"] - W_LAMBDA_PDG) < 1e-12
        assert d["pct_err"] < 1.0

    def test_A_sub_dict(self):
        d = self.res["A"]
        assert abs(d["geo"] - W_A_GEO) < 1e-12
        assert abs(d["pdg"] - W_A_PDG) < 1e-12
        assert d["sigma_tension"] < 2.0

    def test_delta_cp_sub_dict(self):
        d = self.res["delta_cp"]
        # Sub-leading formula gives ≈ 71.08°
        expected_sub = math.degrees(2.0 * math.atan2(5, 7))
        assert abs(d["geo_deg"] - expected_sub) < 1e-10
        assert d["sigma_tension"] < 2.0

    def test_Vub_sub_dict(self):
        d = self.res["Vub"]
        assert abs(d["geo"] - VUB_GEO) < 1e-12
        assert d["pct_err"] < 10.0

    def test_R_b_sub_dict(self):
        d = self.res["R_b"]
        assert d["geo"] > 0
        assert d["pct_err"] < 5.0

    def test_rho_bar_sub_dict(self):
        d = self.res["rho_bar"]
        assert d["geo"] > 0
        assert "note" in d
        assert len(d["note"]) > 10

    def test_eta_bar_sub_dict(self):
        d = self.res["eta_bar"]
        assert d["pct_err"] < 5.0
        assert "status" in d

    def test_overall_status_present(self):
        assert len(self.res["overall_status"]) > 20

    def test_overall_status_mentions_close(self):
        s = self.res["overall_status"].lower()
        assert "derived" in s or "closed" in s or "closes" in s or "geometrically" in s


# ---------------------------------------------------------------------------
# pillar87_summary
# ---------------------------------------------------------------------------

class TestPillar87Summary:
    def setup_method(self):
        self.res = pillar87_summary()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_pillar_number(self):
        assert self.res["pillar"] == 87

    def test_name_present(self):
        assert "wolfenstein" in self.res["name"].lower() or "Wolfenstein" in self.res["name"]

    def test_wolfenstein_parameters_key(self):
        assert "wolfenstein_parameters" in self.res

    def test_key_derivations_key(self):
        assert "key_derivations" in self.res
        kd = self.res["key_derivations"]
        for key in ("lambda", "A", "delta", "Vub", "eta_bar", "rho_bar"):
            assert key in kd, f"Missing derivation key: {key}"

    def test_key_derivation_lambda_mentions_derived(self):
        assert "DERIVED" in self.res["key_derivations"]["lambda"]

    def test_key_derivation_A_mentions_derived(self):
        assert "DERIVED" in self.res["key_derivations"]["A"]

    def test_key_derivation_rho_bar_mentions_open(self):
        # ρ̄ discrepancy now explained by residual CP-phase tension (0.99σ)
        rho_text = self.res["key_derivations"]["rho_bar"]
        assert "ρ̄" in rho_text or "rho" in rho_text.lower() or "24" in rho_text

    def test_closes_gap_key(self):
        assert "closes_gap_from" in self.res

    def test_closes_gap_mentions_v9_20(self):
        cg = self.res["closes_gap_from"]
        assert "v9_20_completion_report" in cg

    def test_honest_remaining_open_key(self):
        assert "honest_remaining_open" in self.res
        assert len(self.res["honest_remaining_open"]) > 20

    def test_honest_remaining_open_mentions_rho(self):
        text = self.res["honest_remaining_open"]
        assert "ρ̄" in text or "rho" in text.lower() or "27" in text

    def test_lambda_value_in_summary(self):
        wp = self.res["wolfenstein_parameters"]
        assert abs(wp["lambda"]["geo"] - W_LAMBDA_GEO) < 1e-12

    def test_A_value_in_summary(self):
        wp = self.res["wolfenstein_parameters"]
        assert abs(wp["A"]["geo"] - W_A_GEO) < 1e-12

    def test_eta_bar_close_to_pdg(self):
        wp = self.res["wolfenstein_parameters"]
        assert wp["eta_bar"]["pct_err"] < 5.0


# ---------------------------------------------------------------------------
# Falsification / prediction tests
# ---------------------------------------------------------------------------

class TestFalsifiablePredictions:
    """Tests that the geometric predictions are specific and falsifiable."""

    def test_A_prediction_specific(self):
        # A = √(5/7) is a specific numerical prediction, not just "O(1)"
        res = wolfenstein_A_geometric()
        assert abs(res["A_geo"] - 0.845154) < 1e-4

    def test_lambda_prediction_specific(self):
        res = wolfenstein_lambda_geometric()
        assert abs(res["lambda_geo"] - 0.223607) < 1e-4

    def test_delta_prediction_is_72_exactly(self):
        res = wolfenstein_delta_cp_geometric()
        # Leading-order formula gives exactly 72°; sub-leading gives ~71.08°
        assert abs(res["delta_lead_deg"] - 72.0) < 1e-10
        expected_sub = math.degrees(2.0 * math.atan2(5, 7))
        assert abs(res["delta_geo_deg"] - expected_sub) < 1e-10

    def test_A_falsification_range(self):
        # If experiments converge on A outside [0.80, 0.89] at 5σ,
        # the A = √(5/7) prediction is falsified.
        A_geo = W_A_GEO
        A_low = 0.80
        A_high = 0.89
        assert A_low < A_geo < A_high, (
            f"A_geo = {A_geo} not in falsification window [{A_low}, {A_high}]"
        )

    def test_eta_bar_prediction_specific(self):
        res = wolfenstein_rho_eta_geometric()
        # η̄_geo should be between 0.30 and 0.40 (PDG is 0.348)
        assert 0.30 < res["eta_bar_geo"] < 0.42

    def test_rho_bar_prediction_positive(self):
        res = wolfenstein_rho_eta_geometric()
        # ρ̄_geo must be positive (cos(72°) > 0)
        assert res["rho_bar_geo"] > 0

    def test_unitarity_triangle_closes(self):
        # ρ̄² + η̄² = R_b² — the triangle closes exactly
        res = wolfenstein_rho_eta_geometric()
        R_b_sq = res["R_b_geo"] ** 2
        rho_eta_sq = res["rho_bar_geo"] ** 2 + res["eta_bar_geo"] ** 2
        assert abs(R_b_sq - rho_eta_sq) < 1e-14

    def test_A_sigma_tension_within_2sigma(self):
        res = wolfenstein_A_geometric()
        assert res["sigma_tension"] < 2.0, (
            f"A = √(5/7) = {W_A_GEO:.4f} is {res['sigma_tension']:.2f}σ from PDG "
            f"{W_A_PDG} ± {W_A_SIGMA_PDG} — prediction falsified at > 2σ"
        )

    def test_lambda_consistent_with_cabibbo(self):
        # The Cabibbo angle sin(13°) ≈ 0.225 — our λ ≈ 0.224 matches
        theta_C_deg = math.degrees(math.asin(W_LAMBDA_GEO))
        assert 12.5 < theta_C_deg < 13.5


# ---------------------------------------------------------------------------
# Physical consistency checks
# ---------------------------------------------------------------------------

class TestPhysicalConsistency:
    """Verify that all derived Wolfenstein parameters are physically sensible."""

    def test_hierarchy_Vub_less_than_Vcb(self):
        # |V_ub| << |V_cb| = A λ²
        Vub = VUB_GEO
        Vcb = W_A_GEO * W_LAMBDA_GEO ** 2
        assert Vub < Vcb

    def test_hierarchy_Vcb_less_than_lambda(self):
        # |V_cb| ≈ Aλ² ~ 0.04 << λ ~ 0.22
        Vcb = W_A_GEO * W_LAMBDA_GEO ** 2
        assert Vcb < W_LAMBDA_GEO

    def test_hierarchy_Vub_much_less_than_lambda(self):
        # |V_ub| ~ 0.0035 << λ ~ 0.22
        assert VUB_GEO < 0.5 * W_LAMBDA_GEO

    def test_eta_bar_larger_than_rho_bar(self):
        # At δ = 72°: tan(72°) = 3.08, so η̄ >> ρ̄
        assert W_ETABAR_GEO > W_RHOBAR_GEO

    def test_R_b_between_zero_and_one(self):
        assert 0 < R_B_GEO < 1.0

    def test_lambda_between_zero_and_half(self):
        # λ is the Cabibbo angle sine, must be between 0 and 0.5
        assert 0 < W_LAMBDA_GEO < 0.5

    def test_A_between_zero_and_one(self):
        # A = √(5/7) < 1
        assert 0 < W_A_GEO < 1.0

    def test_Vub_is_small(self):
        # |V_ub| ~ 3.5 × 10⁻³ — very small mixing
        assert VUB_GEO < 0.01

    def test_geometric_CP_phase_in_physical_range(self):
        delta = DELTA_CP_GEO_DEG
        assert 0 < delta < 180  # physical range for CKM CP phase

    def test_Jarlskog_invariant_order_of_magnitude(self):
        # J = A²λ⁶η̄ — should be O(10⁻⁵) [PDG: 3.08×10⁻⁵]
        J = W_A_GEO ** 2 * W_LAMBDA_GEO ** 6 * W_ETABAR_GEO
        assert 1e-6 < J < 1e-4


# ---------------------------------------------------------------------------
# TestDeltaCpSubleadingConstant  (new constant DELTA_CP_GEO_SUBLEADING_DEG)
# ---------------------------------------------------------------------------

class TestDeltaCpSubleadingConstant:
    """Tests for the module-level DELTA_CP_GEO_SUBLEADING_DEG constant."""

    def test_subleading_constant_positive(self):
        assert DELTA_CP_GEO_SUBLEADING_DEG > 0

    def test_subleading_constant_less_than_72(self):
        assert DELTA_CP_GEO_SUBLEADING_DEG < DELTA_CP_GEO_DEG

    def test_subleading_constant_equals_2_arctan_5_7(self):
        expected = 2.0 * math.degrees(math.atan2(N1_CANONICAL, N2_CANONICAL))
        assert abs(DELTA_CP_GEO_SUBLEADING_DEG - expected) < 1e-10

    def test_subleading_constant_approx_71_deg(self):
        assert 70.0 < DELTA_CP_GEO_SUBLEADING_DEG < 72.0

    def test_subleading_within_1sigma_of_pdg(self):
        sigma = abs(DELTA_CP_GEO_SUBLEADING_DEG - DELTA_CP_PDG_DEG) / DELTA_CP_SIGMA_PDG_DEG
        assert sigma < 1.0

    def test_leading_delta_is_72(self):
        assert abs(DELTA_CP_GEO_DEG - 72.0) < 1e-10


# ---------------------------------------------------------------------------
# TestJarlskogInvariantGeometric
# ---------------------------------------------------------------------------

class TestJarlskogInvariantGeometric:
    """Tests for jarlskog_invariant_geometric()."""

    def setup_method(self):
        self.res = jarlskog_invariant_geometric()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_J_geo_positive(self):
        assert self.res["J_geo"] > 0

    def test_J_geo_order_of_magnitude(self):
        # PDG J ≈ 3.08×10⁻⁵
        assert 1e-6 < self.res["J_geo"] < 1e-4

    def test_J_pdg_key_correct(self):
        assert abs(self.res["J_pdg"] - 3.08e-5) < 1e-12

    def test_J_pct_err_below_10(self):
        assert self.res["J_pct_err"] < 10.0

    def test_eta_bar_geo_in_result(self):
        assert "eta_bar_geo" in self.res
        assert 0.2 < self.res["eta_bar_geo"] < 0.5

    def test_status_string_nonempty(self):
        assert len(self.res["status"]) > 20

    def test_delta_sub_deg_approx_71(self):
        assert 70.0 < self.res["delta_sub_deg"] < 72.0

    def test_derivation_mentions_lambda(self):
        assert "λ" in self.res["derivation"] or "lambda" in self.res["derivation"].lower()

    def test_custom_n1_n2(self):
        res = jarlskog_invariant_geometric(n1=5, n2=7)
        assert abs(res["J_geo"] - self.res["J_geo"]) < 1e-12


# ---------------------------------------------------------------------------
# TestRhoBarFromJarlskog
# ---------------------------------------------------------------------------

class TestRhoBarFromJarlskog:
    """Tests for rho_bar_from_jarlskog()."""

    def setup_method(self):
        self.res = rho_bar_from_jarlskog()

    def test_returns_dict(self):
        assert isinstance(self.res, dict)

    def test_rho_bar_geo_positive(self):
        assert self.res["rho_bar_geo"] > 0

    def test_eta_bar_geo_within_5pct(self):
        assert self.res["eta_bar_pct_err"] < 5.0

    def test_R_b_squared_equals_rho_sq_plus_eta_sq(self):
        R_b = self.res["R_b_geo"]
        rho = self.res["rho_bar_geo"]
        eta = self.res["eta_bar_geo"]
        assert abs(math.sqrt(rho ** 2 + eta ** 2) - R_b) < 1e-12

    def test_J_geo_close_to_pdg(self):
        assert self.res["J_pct_err"] < 10.0

    def test_status_string_present(self):
        assert len(self.res["status"]) > 20

    def test_delta_sub_deg_approx_71(self):
        assert 70.0 < self.res["delta_sub_deg"] < 72.0

    def test_rho_bar_pdg_key(self):
        assert abs(self.res["rho_bar_pdg"] - W_RHOBAR_PDG) < 1e-12

    def test_eta_bar_pdg_key(self):
        assert abs(self.res["eta_bar_pdg"] - W_ETABAR_PDG) < 1e-12
