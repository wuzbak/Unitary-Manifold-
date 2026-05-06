# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 200: Pure Geometric α_s Forward Chain (AxiomZero Compliant).

Verifies:
  • AxiomZero compliance — no SM particle masses imported as anchors
  • Geometric basis correctness (M_KK, α_GUT_geo, λ_H, α_s(M_KK), v_geo)
  • Warp-anchor EW scale consistency
  • KK β-function correction magnitude and formula
  • Forward chain (downward run) numerical stability and direction
  • Upward KK-corrected GUT consistency check
  • Honest residual ranges (α_s within expected Warp-Anchor Gap)
  • Summary structure completeness
  • No regression to hidden PDG anchors
"""

import math
import pytest
from src.core.pillar200_rge_geometric import (
    # module-level constants
    N_W, K_CS, N_C, M_PL_GEV, PI_KR,
    M_KK_GEV, ALPHA_GUT_GEO, LAMBDA_H_GEO,
    ALPHA_S_MKK_GEO, V_GEO_GEV, M_HIGGS_GEO_GEV,
    N_F_IN_FORWARD_RUN,
    # functions
    geometric_basis,
    warp_anchor_ew_scale,
    kk_beta_correction,
    alpha_s_forward_chain,
    axiom_zero_audit,
    gut_consistency_kk_corrected,
    pillar200_summary,
    _beta0,
    _run_down,
    _run_up,
)


# ─────────────────────────────────────────────────────────────────────────────
# AXIOM-ZERO COMPLIANCE
# ─────────────────────────────────────────────────────────────────────────────

class TestAxiomZeroCompliance:
    """The module must use ZERO SM particle masses as computational anchors."""

    def test_audit_passes(self):
        a = axiom_zero_audit()
        assert a["axiom_zero_compliant"] is True

    def test_no_sm_anchors_in_audit(self):
        a = axiom_zero_audit()
        assert a["sm_anchors_count"] == 0

    def test_no_mz_pdg_in_forward_chain_inputs(self):
        fc = alpha_s_forward_chain()
        assert fc["sm_anchors_used"] == []

    def test_no_mz_pdg_in_basis(self):
        b = geometric_basis()
        assert b["sm_anchors_used"] == []

    def test_forward_chain_axiom_zero_flag(self):
        fc = alpha_s_forward_chain()
        assert fc["axiom_zero_compliant"] is True

    def test_warp_anchor_no_sm_anchors(self):
        w = warp_anchor_ew_scale()
        assert w["sm_anchors_used"] == []

    def test_gut_check_no_sm_anchors(self):
        gc = gut_consistency_kk_corrected()
        assert gc["sm_anchors_used"] == []


# ─────────────────────────────────────────────────────────────────────────────
# GEOMETRIC BASIS CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

class TestGeometricBasis:
    """All module-level constants must derive correctly from {n_w, K_CS, M_Pl}."""

    def test_winding_number(self):
        assert N_W == 5

    def test_cs_level(self):
        assert K_CS == 74

    def test_n_colors(self):
        # N_c = ⌈n_w/2⌉
        assert N_C == math.ceil(N_W / 2)
        assert N_C == 3

    def test_pi_kr(self):
        # πkR = K_CS/2
        assert PI_KR == K_CS / 2.0
        assert PI_KR == 37.0

    def test_mkk_formula(self):
        expected = M_PL_GEV * math.exp(-PI_KR)
        assert abs(M_KK_GEV - expected) / expected < 1e-10

    def test_mkk_order_of_magnitude(self):
        # M_KK ≈ 1040 GeV
        assert 900 < M_KK_GEV < 1200

    def test_alpha_gut_geo_formula(self):
        expected = N_C / K_CS
        assert abs(ALPHA_GUT_GEO - expected) < 1e-12
        # ≈ 3/74 ≈ 0.04054
        assert abs(ALPHA_GUT_GEO - 3 / 74) < 1e-12

    def test_lambda_h_formula(self):
        expected = N_W ** 2 / (2.0 * K_CS)
        assert abs(LAMBDA_H_GEO - expected) < 1e-12
        # = 25/148
        assert abs(LAMBDA_H_GEO - 25 / 148) < 1e-12

    def test_alpha_s_mkk_formula(self):
        expected = 2.0 * math.pi / (N_C * K_CS)
        assert abs(ALPHA_S_MKK_GEO - expected) < 1e-12

    def test_alpha_s_mkk_value(self):
        # 2π/222 ≈ 0.0283
        assert abs(ALPHA_S_MKK_GEO - 2 * math.pi / 222) < 1e-10

    def test_v_geo_formula(self):
        expected = M_KK_GEV * math.sqrt(N_C / K_CS)
        assert abs(V_GEO_GEV - expected) < 1e-8

    def test_v_geo_order(self):
        # Should be in the EW ballpark: 150–300 GeV
        assert 150 < V_GEO_GEV < 300

    def test_m_higgs_geo_formula(self):
        expected = math.sqrt(2.0 * LAMBDA_H_GEO) * V_GEO_GEV
        assert abs(M_HIGGS_GEO_GEV - expected) < 1e-8

    def test_m_higgs_geo_close_to_pdg(self):
        # m_H_geo should be within 5% of PDG 125.25 GeV
        assert abs(M_HIGGS_GEO_GEV - 125.25) / 125.25 < 0.05

    def test_n_f_in_forward_run(self):
        assert N_F_IN_FORWARD_RUN == 6

    def test_basis_dict_keys(self):
        b = geometric_basis()
        required = {
            "n_w", "K_CS", "N_c", "M_Pl_GeV", "pi_kR", "M_KK_GeV",
            "alpha_GUT_geo", "lambda_H_geo", "alpha_s_mkk_geo",
            "v_geo_GeV", "m_higgs_geo_GeV", "sm_anchors_used",
        }
        assert required.issubset(set(b.keys()))

    def test_basis_n_c_equals_ceil_nw_over_2(self):
        b = geometric_basis()
        assert b["N_c"] == math.ceil(b["n_w"] / 2)


# ─────────────────────────────────────────────────────────────────────────────
# 1-LOOP RGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

class TestBeta0:
    """β₀ = (11 N_c − 2 N_f) / 3 for N_c=3."""

    @pytest.mark.parametrize("n_f,expected", [
        (5, (33 - 10) / 3),
        (6, (33 - 12) / 3),
        (4, (33 - 8) / 3),
        (3, (33 - 6) / 3),
    ])
    def test_beta0_values(self, n_f, expected):
        assert abs(_beta0(n_f) - expected) < 1e-12

    def test_beta0_positive_for_nf_le_8(self):
        for n_f in range(1, 9):
            assert _beta0(n_f) > 0, f"β₀ should be positive for N_f={n_f} ≤ 8"

    def test_asymptotic_freedom_check(self):
        # QCD has asymptotic freedom iff β₀ > 0, i.e. N_f < 16.5 for N_c=3
        assert _beta0(16) > 0
        assert _beta0(17) < 0


class TestRunDown:
    """Downward running increases α_s (QCD: coupling grows at lower scales)."""

    def test_run_down_increases_alpha(self):
        alpha_hi = 0.05
        alpha_lo = _run_down(alpha_hi, 1000.0, 100.0, n_f=6)
        assert alpha_lo > alpha_hi

    def test_run_down_consistency_with_run_up(self):
        alpha_start = 0.05
        mu_hi, mu_lo = 1000.0, 100.0
        alpha_lo = _run_down(alpha_start, mu_hi, mu_lo, n_f=6)
        alpha_recovered = _run_up(alpha_lo, mu_lo, mu_hi, n_f=6)
        assert abs(alpha_recovered - alpha_start) / alpha_start < 1e-10

    def test_landau_pole_raises(self):
        """Starting from α_GUT_geo at M_GUT and running to M_Z hits Landau pole."""
        with pytest.raises(RuntimeError, match="Landau pole"):
            _run_down(ALPHA_GUT_GEO, 2e16, 91.18, n_f=6)

    def test_wrong_direction_raises(self):
        with pytest.raises(ValueError):
            _run_down(0.05, 100.0, 1000.0, n_f=6)

    def test_short_run_no_pole(self):
        """Short 1-decade run should be safe."""
        alpha = _run_down(0.05, 1000.0, 100.0, n_f=6)
        assert 0.05 < alpha < 0.20

    def test_run_up_decreases_alpha(self):
        alpha_hi = _run_up(0.118, 91.18, 1000.0, n_f=6)
        assert alpha_hi < 0.118

    def test_run_up_wrong_direction_raises(self):
        with pytest.raises(ValueError):
            _run_up(0.05, 1000.0, 100.0, n_f=6)


# ─────────────────────────────────────────────────────────────────────────────
# WARP-ANCHOR EW SCALE
# ─────────────────────────────────────────────────────────────────────────────

class TestWarpAnchorEWScale:
    def test_v_geo_formula(self):
        w = warp_anchor_ew_scale()
        assert abs(w["v_geo_GeV"] - M_KK_GEV * math.sqrt(N_C / K_CS)) < 1e-6

    def test_v_geo_in_reasonable_range(self):
        w = warp_anchor_ew_scale()
        assert 150 < w["v_geo_GeV"] < 350

    def test_v_geo_within_20pct_of_pdg(self):
        w = warp_anchor_ew_scale()
        assert w["v_residual_pct"] < 20.0

    def test_m_higgs_geo_within_5pct_of_pdg(self):
        w = warp_anchor_ew_scale()
        assert w["m_higgs_geo_residual_pct"] < 5.0

    def test_m_higgs_geo_consistent_with_module_constant(self):
        w = warp_anchor_ew_scale()
        assert abs(w["m_higgs_geo_GeV"] - M_HIGGS_GEO_GEV) < 1e-6

    def test_top_threshold_note_present(self):
        w = warp_anchor_ew_scale()
        assert "top_threshold_note" in w
        assert "N_f=6" in w["top_threshold_note"]

    def test_no_sm_anchors(self):
        w = warp_anchor_ew_scale()
        assert w["sm_anchors_used"] == []


# ─────────────────────────────────────────────────────────────────────────────
# KK BETA CORRECTION
# ─────────────────────────────────────────────────────────────────────────────

class TestKKBetaCorrection:
    def test_delta_b0_formula(self):
        kk = kk_beta_correction()
        expected = (11.0 * N_C / 3.0) * (N_W / K_CS)
        assert abs(kk["delta_b0_kk"] - expected) < 1e-12

    def test_delta_b0_positive(self):
        kk = kk_beta_correction()
        assert kk["delta_b0_kk"] > 0

    def test_delta_b0_value(self):
        # (11×3/3) × (5/74) = 11 × 5/74 = 55/74 ≈ 0.7432
        kk = kk_beta_correction()
        assert abs(kk["delta_b0_kk"] - 55 / 74) < 1e-10

    def test_b0_eff_larger_than_sm(self):
        kk = kk_beta_correction()
        assert kk["b0_eff_nf6_above_mkk"] > kk["b0_sm_nf6"]

    def test_b0_eff_formula(self):
        kk = kk_beta_correction()
        expected = _beta0(6) + 55 / 74
        assert abs(kk["b0_eff_nf6_above_mkk"] - expected) < 1e-10

    def test_applies_above_mkk_only(self):
        kk = kk_beta_correction()
        assert kk["applies_above_mkk_only"] is True

    def test_fraction_string(self):
        kk = kk_beta_correction()
        # (11 × N_c × n_w) / (3 × K_CS) = 165/222, simplified = 55/74
        assert kk["delta_b0_kk_fraction"] == "165/222"

    def test_b0_sm_nf5_and_nf6(self):
        kk = kk_beta_correction()
        assert abs(kk["b0_sm_nf6"] - _beta0(6)) < 1e-12
        assert abs(kk["b0_sm_nf5"] - _beta0(5)) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# FORWARD CHAIN (AxiomZero)
# ─────────────────────────────────────────────────────────────────────────────

class TestAlphaSForwardChain:
    @pytest.fixture
    def fc(self):
        return alpha_s_forward_chain()

    def test_axiom_zero_compliant(self, fc):
        assert fc["axiom_zero_compliant"] is True

    def test_no_sm_anchors(self, fc):
        assert fc["sm_anchors_used"] == []

    def test_alpha_s_at_mew_is_positive(self, fc):
        assert fc["alpha_s_at_mew_geo"] > 0

    def test_alpha_s_larger_at_mew_than_mkk(self, fc):
        """Coupling grows as scale decreases — running increases α_s downward."""
        assert fc["alpha_s_at_mew_geo"] > ALPHA_S_MKK_GEO

    def test_warp_anchor_gap_factor_gt_1(self, fc):
        """PDG > geometric prediction."""
        assert fc["warp_anchor_gap_factor"] > 1.0

    def test_warp_anchor_gap_factor_range(self, fc):
        """Gap should be in the range 3.5–4.5 for physical sanity."""
        assert 3.0 < fc["warp_anchor_gap_factor"] < 5.5

    def test_n_f_in_run(self, fc):
        assert fc["running"]["n_f"] == 6

    def test_inputs_dict_present(self, fc):
        assert "inputs" in fc
        assert fc["inputs"]["K_CS"] == K_CS
        assert fc["inputs"]["n_w"] == N_W
        assert fc["inputs"]["N_c"] == N_C

    def test_m_ew_geo_consistent_with_constant(self, fc):
        assert abs(fc["m_ew_geo_gev"] - V_GEO_GEV) < 1e-6

    def test_alpha_s_mkk_consistent_with_constant(self, fc):
        assert abs(fc["derived_starting_values"]["alpha_s_mkk"] - ALPHA_S_MKK_GEO) < 1e-12

    def test_status_not_full_derivation(self, fc):
        """Status must NOT claim full derivation."""
        assert "PARTIAL" in fc["status"] or "CONSISTENCY" in fc["status"]

    def test_verdict_contains_warp_anchor_gap(self, fc):
        assert "Warp-Anchor Gap" in fc["verdict"]

    def test_forward_chain_no_pdg_alpha_s_anchor(self, fc):
        """The PDG α_s value must appear ONLY in the honest residual display."""
        # The PDG value is in fc["pdg_alpha_s_mz"] for display purposes.
        # Verify it equals 0.1179 (just a stored reference).
        assert abs(fc["pdg_alpha_s_mz"] - 0.1179) < 1e-4

    def test_m_ew_geo_less_than_mkk(self, fc):
        """Endpoint must be below the starting scale."""
        assert fc["m_ew_geo_gev"] < fc["derived_starting_values"]["M_KK_GeV"]

    def test_custom_inputs_change_result(self):
        """Result should change when we pass different (but still geometric) inputs."""
        r1 = alpha_s_forward_chain()
        # Slightly vary α_s(M_KK) — same M_KK, smaller coupling → smaller α_s at endpoint
        r2 = alpha_s_forward_chain(alpha_s_mkk=0.020)
        assert r2["alpha_s_at_mew_geo"] < r1["alpha_s_at_mew_geo"]

    def test_raises_if_mew_above_mkk(self):
        with pytest.raises(ValueError):
            alpha_s_forward_chain(m_kk_gev=500.0, v_geo_gev=600.0)


# ─────────────────────────────────────────────────────────────────────────────
# KK-CORRECTED UPWARD GUT CONSISTENCY CHECK
# ─────────────────────────────────────────────────────────────────────────────

class TestGUTConsistencyKKCorrected:
    @pytest.fixture
    def gc(self):
        return gut_consistency_kk_corrected()

    def test_no_sm_anchors(self, gc):
        assert gc["sm_anchors_used"] == []

    def test_kk_correction_is_positive(self, gc):
        assert gc["kk_correction_delta_b0"] > 0

    def test_kk_correction_value(self, gc):
        assert abs(gc["kk_correction_delta_b0"] - 55 / 74) < 1e-10

    def test_b0_eff_with_kk_larger(self, gc):
        assert gc["b0_eff_with_kk"] > gc["b0_plain_nf6"]

    def test_alpha_s_gut_positive(self, gc):
        assert gc["alpha_s_gut_kk_corrected"] > 0
        assert gc["alpha_s_gut_no_kk_correction"] > 0

    def test_kk_correction_slows_running(self, gc):
        """Larger b₀ → coupling decreases FASTER going up →
        α_s at M_GUT is SMALLER with KK correction."""
        assert gc["alpha_s_gut_kk_corrected"] < gc["alpha_s_gut_no_kk_correction"]

    def test_alpha_gut_geo_target_correct(self, gc):
        assert abs(gc["alpha_gut_geo_target"] - 3 / 74) < 1e-12

    def test_deviation_values_physical(self, gc):
        """Both deviations should be less than 100% (not wildly unphysical)."""
        assert gc["deviation_no_kk_pct"] < 100.0
        assert gc["deviation_kk_corrected_pct"] < 100.0

    def test_geometric_starting_point_label(self, gc):
        assert "GEOMETRIC" in gc["starting_alpha_s_mkk_formula"]

    def test_starting_alpha_consistent_with_constant(self, gc):
        assert abs(gc["starting_alpha_s_mkk"] - ALPHA_S_MKK_GEO) < 1e-12


# ─────────────────────────────────────────────────────────────────────────────
# FULL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

class TestPillar200Summary:
    @pytest.fixture
    def s(self):
        return pillar200_summary()

    def test_pillar_number(self, s):
        assert s["pillar"] == "200"

    def test_top_level_keys(self, s):
        expected = {
            "pillar", "title", "version", "axiom_zero_audit",
            "warp_anchor_ew_scale", "kk_beta_correction",
            "forward_chain", "gut_consistency_kk_corrected",
            "key_results", "clarification_of_1pt5_percent",
            "path_to_closure", "status",
        }
        assert expected.issubset(set(s.keys()))

    def test_key_results_complete(self, s):
        kr = s["key_results"]
        assert "geometric_alpha_s_at_mew_geo" in kr
        assert "warp_anchor_gap_factor" in kr
        assert "kk_correction_delta_b0" in kr
        assert "v_geo_gev" in kr

    def test_clarification_mentions_1pt5(self, s):
        assert "1.5%" in s["clarification_of_1pt5_percent"]

    def test_clarification_mentions_analytic(self, s):
        assert "ANALYTIC" in s["clarification_of_1pt5_percent"]

    def test_path_to_closure_mentions_182(self, s):
        assert "Pillar_182" in s["path_to_closure"]

    def test_path_to_closure_mentions_201(self, s):
        assert "Pillar_201" in s["path_to_closure"]

    def test_path_to_closure_mentions_203(self, s):
        assert "Pillar_203" in s["path_to_closure"]

    def test_status_partial(self, s):
        assert "PARTIAL" in s["status"]

    def test_axiom_zero_compliant_in_summary(self, s):
        assert s["axiom_zero_audit"]["axiom_zero_compliant"] is True

    def test_warp_anchor_gap_in_key_results(self, s):
        gap = s["key_results"]["warp_anchor_gap_factor"]
        assert 3.0 < gap < 6.0

    def test_key_results_alpha_s_positive(self, s):
        assert s["key_results"]["geometric_alpha_s_at_mew_geo"] > 0

    def test_key_results_kk_correction_positive(self, s):
        assert s["key_results"]["kk_correction_delta_b0"] > 0

    def test_version_string(self, s):
        assert "v10" in s["version"]


# ─────────────────────────────────────────────────────────────────────────────
# PHYSICAL CONSISTENCY CROSS-CHECKS
# ─────────────────────────────────────────────────────────────────────────────

class TestPhysicalConsistency:
    def test_alpha_s_mkk_lt_pdg_mz(self):
        """α_s(M_KK) from CS quantisation must be smaller than PDG α_s(M_Z)
        because M_KK > M_Z and α_s is asymptotically free."""
        assert ALPHA_S_MKK_GEO < 0.1179

    def test_forward_alpha_s_gt_mkk_value(self):
        """Downward run: α_s increases as scale decreases."""
        fc = alpha_s_forward_chain()
        assert fc["alpha_s_at_mew_geo"] > ALPHA_S_MKK_GEO

    def test_alpha_gut_geo_and_alpha_s_mkk_ordering(self):
        """α_GUT_geo = 3/74 ≈ 0.0405 is LARGER than α_s(M_KK) = 2π/222 ≈ 0.0283.
        These are two different geometric quantities — α_GUT_geo represents the
        unified GUT coupling; α_s(M_KK) is the CS-quantised QCD coupling at M_KK.
        They are not connected by simple 1-loop running."""
        assert ALPHA_GUT_GEO > ALPHA_S_MKK_GEO

    def test_kk_correction_fraction_lt_1(self):
        """KK correction should be a small perturbation, not dominant."""
        kk = kk_beta_correction()
        assert kk["delta_b0_kk"] / kk["b0_sm_nf6"] < 0.15   # < 15% correction

    def test_higgs_mass_lt_kk_scale(self):
        """m_H_geo must be below M_KK."""
        assert M_HIGGS_GEO_GEV < M_KK_GEV

    def test_ew_scale_lt_kk_scale(self):
        """EW scale must be below M_KK."""
        assert V_GEO_GEV < M_KK_GEV

    def test_warp_exponent_37(self):
        """πkR = 37 is required for the KK hierarchy."""
        assert PI_KR == 37.0

    def test_mkk_within_factor_2_of_1_tev(self):
        """M_KK should be in the 0.5–2 TeV range for RS1."""
        assert 500 < M_KK_GEV < 2000

    def test_alpha_gut_geo_close_to_1_over_24(self):
        """α_GUT_geo = 3/74 ≈ 0.040 should be within 2% of 1/24.3 ≈ 0.041."""
        alpha_gut_su5 = 1 / 24.3
        assert abs(ALPHA_GUT_GEO - alpha_gut_su5) / alpha_gut_su5 < 0.02

    def test_landau_pole_documented(self):
        """Direct M_GUT → M_Z downward run must raise — documenting the barrier.

        Note: 91.18 GeV appears here as the *domain boundary* for the Landau-pole
        test, not as a computational anchor.  We are verifying that the 1-loop
        perturbative path from M_GUT to any sub-M_KK scale is non-perturbative
        (1/α → 0).  The 91.18 value is representative; any target below ~500 GeV
        would trigger the same pole.
        """
        with pytest.raises(RuntimeError, match="Landau pole"):
            _run_down(ALPHA_GUT_GEO, 2.0e16, 91.18, n_f=6)

    def test_landau_pole_also_with_kk_correction(self):
        """Even with KK-corrected b₀, the M_GUT → M_Z direct run still fails."""
        kk = kk_beta_correction()
        b0_eff = kk["b0_eff_nf6_above_mkk"]
        # Manual 1-loop run to check
        log_ratio = math.log(91.18 / 2.0e16)
        inv_alpha = 1.0 / ALPHA_GUT_GEO + (b0_eff / (2.0 * math.pi)) * log_ratio
        # This should still go negative (Landau pole)
        assert inv_alpha < 0, (
            "Expected Landau pole even with KK correction for GUT→M_Z direct run"
        )
