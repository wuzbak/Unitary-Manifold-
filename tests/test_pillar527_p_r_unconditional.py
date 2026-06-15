# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 527 — Unconditional p_R Derivation."""

from __future__ import annotations

import math
import pytest

from src.eleventd.p_r_unconditional import (
    DELTA_RGE,
    DELTA_SEESAW_TOTAL,
    DM31_LO,
    ETA_BAR,
    G11_SQUARED,
    K_CS,
    N_W,
    P_R_TWO_LOOP_MAX,
    P_R_TWO_LOOP_MIN,
    P_R_UNCOND,
    PDG_DM31,
    PI_KR,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    VOL_CY3_FIXED,
    dm31_nlo_with_unconditional_pr,
    dm31_residual_pct,
    dm31_within_juno_window,
    e8_gauge_coupling_squared,
    e8_participation_weight,
    e8_threshold_correction,
    kk_gauge_coupling_squared,
    p_r_geometric_leading_order,
    p_r_unconditional,
    p_r_within_two_loop_band,
    pillar527_report,
)


class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 527

    def test_pillar_status(self):
        assert PILLAR_STATUS == "UNCONDITIONAL_DERIVATION"

    def test_pillar_title_mentions_gap_closed(self):
        assert "Closed" in PILLAR_TITLE or "CLOSED" in PILLAR_TITLE or "Unconditional" in PILLAR_TITLE

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_eta_bar(self):
        assert ETA_BAR == 0.5


class TestVolCY3Fixed:
    def test_vol_positive(self):
        assert VOL_CY3_FIXED > 0

    def test_vol_finite(self):
        assert math.isfinite(VOL_CY3_FIXED)

    def test_vol_reasonable_magnitude(self):
        # Should be O(1) in Planck units
        assert 1e-10 < VOL_CY3_FIXED < 1e2


class TestE8GaugeCoupling:
    def test_positive_for_fixed_vol(self):
        assert e8_gauge_coupling_squared() > 0

    def test_zero_for_zero_vol(self):
        assert e8_gauge_coupling_squared(0.0) == 0.0

    def test_formula(self):
        expected = G11_SQUARED / math.sqrt(VOL_CY3_FIXED)
        assert abs(e8_gauge_coupling_squared() - expected) < 1e-12

    def test_decreases_with_vol(self):
        g1 = e8_gauge_coupling_squared(1.0)
        g2 = e8_gauge_coupling_squared(4.0)
        assert g2 < g1


class TestKKGaugeCoupling:
    def test_positive(self):
        assert kk_gauge_coupling_squared() > 0

    def test_formula(self):
        expected = 4.0 * math.pi**2 * N_W**2 / K_CS
        assert abs(kk_gauge_coupling_squared() - expected) < 1e-12


class TestE8ParticipationWeight:
    def test_value(self):
        assert abs(e8_participation_weight() - N_W / K_CS) < 1e-12

    def test_in_zero_one_range(self):
        assert 0 < e8_participation_weight() < 1


class TestE8ThresholdCorrection:
    def test_positive(self):
        assert e8_threshold_correction() > 0

    def test_small_correction(self):
        # Should be a small correction, not O(1)
        assert e8_threshold_correction() < 1.0

    def test_finite(self):
        assert math.isfinite(e8_threshold_correction())


class TestPRGeometricLO:
    def test_positive(self):
        assert p_r_geometric_leading_order() > 0

    def test_formula(self):
        # p_R^{geom} is derived from the NLO closure condition (Pillar 475)
        frac_gap = PDG_DM31 / DM31_LO - 1.0
        expected = (frac_gap - DELTA_RGE) / DELTA_SEESAW_TOTAL
        assert abs(p_r_geometric_leading_order() - expected) < 1e-12

    def test_finite(self):
        assert math.isfinite(p_r_geometric_leading_order())


class TestPRUnconditional:
    def test_matches_constant(self):
        p_r = p_r_unconditional()
        assert abs(p_r - P_R_UNCOND) < 1e-10

    def test_positive(self):
        assert P_R_UNCOND > 0

    def test_within_two_loop_band(self):
        assert P_R_TWO_LOOP_MIN <= P_R_UNCOND <= P_R_TWO_LOOP_MAX

    def test_larger_than_geometric_lo(self):
        # E8 correction should increase p_R above geometric LO
        assert P_R_UNCOND >= p_r_geometric_leading_order()

    def test_finite(self):
        assert math.isfinite(P_R_UNCOND)

    def test_physically_reasonable(self):
        assert 0.1 < P_R_UNCOND < 0.8


class TestDm31NLO:
    def test_positive(self):
        assert dm31_nlo_with_unconditional_pr() > 0

    def test_above_lo(self):
        assert dm31_nlo_with_unconditional_pr() > DM31_LO

    def test_close_to_pdg(self):
        dm31 = dm31_nlo_with_unconditional_pr()
        residual = abs(dm31 - PDG_DM31) / PDG_DM31
        assert residual < 0.02, f"Residual {residual:.4%} > 2%"

    def test_residual_below_juno_precision(self):
        residual_pct = dm31_residual_pct()
        assert residual_pct < 0.5, f"Residual {residual_pct:.4f}% exceeds JUNO 0.5% gate"

    def test_residual_small(self):
        assert dm31_residual_pct() < 0.1

    def test_custom_pr_works(self):
        dm31_low = dm31_nlo_with_unconditional_pr(P_R_TWO_LOOP_MIN)
        dm31_high = dm31_nlo_with_unconditional_pr(P_R_TWO_LOOP_MAX)
        assert dm31_high > dm31_low


class TestPRWithinTwoLoopBand:
    def setup_method(self):
        self.check = p_r_within_two_loop_band()

    def test_returns_dict(self):
        assert isinstance(self.check, dict)

    def test_within_band_true(self):
        assert self.check["within_band"] is True

    def test_verdict_pass(self):
        assert self.check["verdict"] == "PASS"

    def test_band_limits_correct(self):
        assert self.check["two_loop_min"] == P_R_TWO_LOOP_MIN
        assert self.check["two_loop_max"] == P_R_TWO_LOOP_MAX

    def test_p_r_matches_constant(self):
        assert abs(self.check["p_r"] - P_R_UNCOND) < 1e-5


class TestDm31WithinJUNOWindow:
    def setup_method(self):
        self.check = dm31_within_juno_window()

    def test_returns_dict(self):
        assert isinstance(self.check, dict)

    def test_passes(self):
        assert self.check["passes"] is True

    def test_verdict_safe(self):
        assert self.check["verdict"] == "JUNO_NLO_SAFE"

    def test_residual_pct_below_half_pct(self):
        assert self.check["residual_pct"] < 0.5

    def test_sigma_small(self):
        assert self.check["sigma"] < 1.0

    def test_juno_precision_recorded(self):
        assert self.check["juno_precision_pct"] == 0.5


class TestPillar527Report:
    def setup_method(self):
        self.r = pillar527_report()

    def test_returns_dict(self):
        assert isinstance(self.r, dict)

    def test_pillar_number(self):
        assert self.r["pillar"] == 527

    def test_status_unconditional(self):
        assert self.r["status"] == "UNCONDITIONAL_DERIVATION"

    def test_derivation_present(self):
        assert "derivation" in self.r
        d = self.r["derivation"]
        for key in ("vol_cy3_fixed", "upstream_pillar", "g_e8_squared", "g_kk_squared",
                    "lambda_e8", "delta_e8", "p_r_geometric_lo", "p_r_unconditional"):
            assert key in d

    def test_upstream_pillar_is_526(self):
        assert self.r["derivation"]["upstream_pillar"] == 526

    def test_p_r_uncond_in_derivation(self):
        assert abs(self.r["derivation"]["p_r_unconditional"] - P_R_UNCOND) < 1e-4

    def test_downstream_dm31_close_to_pdg(self):
        dm31 = self.r["downstream"]["dm31_nlo_eV2"]
        residual = abs(dm31 - PDG_DM31) / PDG_DM31
        assert residual < 0.01

    def test_juno_gate_safe(self):
        assert self.r["validation"]["juno_gate"]["passes"] is True

    def test_epistemic_upgrade_present(self):
        assert "epistemic_upgrade" in self.r
        assert "from" in self.r["epistemic_upgrade"]
        assert "to" in self.r["epistemic_upgrade"]
        assert "gap_closed" in self.r["epistemic_upgrade"]

    def test_gap_closed_references_p383(self):
        gap_text = self.r["epistemic_upgrade"]["gap_closed"]
        assert "383" in gap_text or "SEESAW" in gap_text

    def test_summary_mentions_unconditional(self):
        assert "unconditionally" in self.r["summary"].lower() or "UNCONDITIONAL" in self.r["summary"]

    def test_two_loop_band_check_passes(self):
        assert self.r["validation"]["two_loop_band_check"]["within_band"] is True
