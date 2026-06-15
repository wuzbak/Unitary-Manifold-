# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 520 — 11D E8 gauge threshold → p_R derivation.

Status: CONDITIONAL_DERIVATION_11D (🔵 ADJACENT TRACK)
"""

from __future__ import annotations

import math
import pytest

from src.eleventd.e8_gauge_pr_derivation import (
    G11_SQUARED,
    K_CS,
    N_W,
    P_R_FITTED_P383,
    P_R_GEOMETRIC_MAX,
    P_R_GEOMETRIC_MIN,
    P_R_TWO_LOOP_MAX,
    P_R_TWO_LOOP_MIN,
    PI_KR,
    VOL_CY3_FIDUCIAL,
    e8_gauge_coupling_squared,
    e8_gauge_pr_report,
    e8_participation_weight,
    e8_threshold_correction,
    kk_gauge_coupling,
    p_r_11d_conditional,
    p_r_conditional_certificate,
    p_r_interval_from_vol,
    vol_cy3_admissible_range,
)


# ── Module constants ───────────────────────────────────────────────────────────


class TestModuleConstants:
    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5

    def test_pi_kr(self):
        assert PI_KR == pytest.approx(37.0)

    def test_p_r_fitted(self):
        assert P_R_FITTED_P383 == pytest.approx(0.364)

    def test_p_r_geometric_bounds(self):
        assert P_R_GEOMETRIC_MIN == pytest.approx(1e-5)
        assert P_R_GEOMETRIC_MAX == pytest.approx(0.535)

    def test_p_r_two_loop_bounds(self):
        assert P_R_TWO_LOOP_MIN == pytest.approx(0.30)
        assert P_R_TWO_LOOP_MAX == pytest.approx(0.43)

    def test_vol_cy3_fiducial_positive(self):
        assert VOL_CY3_FIDUCIAL > 0

    def test_vol_cy3_fiducial_value(self):
        expected = (37.0 / 74) ** 3
        assert VOL_CY3_FIDUCIAL == pytest.approx(expected, rel=1e-10)


# ── e8_gauge_coupling_squared ─────────────────────────────────────────────────


class TestE8GaugeCouplingSquared:
    def test_positive(self):
        assert e8_gauge_coupling_squared() > 0

    def test_formula(self):
        vol = VOL_CY3_FIDUCIAL
        expected = G11_SQUARED / math.sqrt(vol)
        assert e8_gauge_coupling_squared(vol) == pytest.approx(expected, rel=1e-10)

    def test_decreases_with_volume(self):
        g1 = e8_gauge_coupling_squared(0.1)
        g2 = e8_gauge_coupling_squared(1.0)
        assert g1 > g2

    def test_raises_for_non_positive_volume(self):
        with pytest.raises(ValueError):
            e8_gauge_coupling_squared(0.0)
        with pytest.raises(ValueError):
            e8_gauge_coupling_squared(-1.0)


# ── kk_gauge_coupling ─────────────────────────────────────────────────────────


class TestKKGaugeCoupling:
    def test_formula(self):
        expected = 2.0 * math.pi * 5 / math.sqrt(74)
        assert kk_gauge_coupling() == pytest.approx(expected, rel=1e-10)

    def test_positive(self):
        assert kk_gauge_coupling() > 0

    def test_scales_with_n_w(self):
        g1 = kk_gauge_coupling(1, 74)
        g5 = kk_gauge_coupling(5, 74)
        assert g5 == pytest.approx(5 * g1, rel=1e-10)


# ── e8_participation_weight ───────────────────────────────────────────────────


class TestE8ParticipationWeight:
    def test_formula(self):
        assert e8_participation_weight() == pytest.approx(5.0 / 74.0, rel=1e-10)

    def test_between_zero_and_one(self):
        lam = e8_participation_weight()
        assert 0 < lam < 1

    def test_canonical_value(self):
        assert e8_participation_weight(5, 74) == pytest.approx(5.0 / 74.0)


# ── e8_threshold_correction ───────────────────────────────────────────────────


class TestE8ThresholdCorrection:
    def test_positive(self):
        assert e8_threshold_correction() > 0

    def test_small_correction(self):
        # Threshold correction should be small (perturbative regime)
        delta = e8_threshold_correction()
        assert delta < 1.0, "Threshold correction should be perturbatively small"

    def test_increases_with_decreasing_volume(self):
        d1 = e8_threshold_correction(0.01)
        d2 = e8_threshold_correction(0.1)
        assert d1 > d2

    def test_formula(self):
        vol = VOL_CY3_FIDUCIAL
        g_e8_sq = e8_gauge_coupling_squared(vol)
        g_kk = kk_gauge_coupling()
        lam = e8_participation_weight()
        expected = (g_e8_sq / g_kk**2) * lam
        assert e8_threshold_correction(vol) == pytest.approx(expected, rel=1e-10)


# ── p_r_11d_conditional ───────────────────────────────────────────────────────


class TestPR11DConditional:
    def test_greater_than_geometric(self):
        p_r = p_r_11d_conditional()
        # Should be at least as large as baseline (positive correction)
        assert p_r >= P_R_FITTED_P383

    def test_formula(self):
        vol = VOL_CY3_FIDUCIAL
        delta = e8_threshold_correction(vol)
        expected = P_R_FITTED_P383 * (1.0 + delta)
        assert p_r_11d_conditional(vol) == pytest.approx(expected, rel=1e-10)

    def test_within_geometric_bounds(self):
        p_r = p_r_11d_conditional()
        assert P_R_GEOMETRIC_MIN <= p_r <= P_R_GEOMETRIC_MAX

    def test_positive(self):
        assert p_r_11d_conditional() > 0


# ── vol_cy3_admissible_range ──────────────────────────────────────────────────


class TestVolCY3AdmissibleRange:
    def test_returns_tuple(self):
        result = vol_cy3_admissible_range()
        assert len(result) == 2

    def test_min_less_than_max(self):
        vol_min, vol_max = vol_cy3_admissible_range()
        assert vol_min < vol_max

    def test_both_positive(self):
        vol_min, vol_max = vol_cy3_admissible_range()
        assert vol_min > 0
        assert vol_max > 0

    def test_fiducial_in_range(self):
        vol_min, vol_max = vol_cy3_admissible_range()
        assert vol_min <= VOL_CY3_FIDUCIAL <= vol_max


# ── p_r_interval_from_vol ─────────────────────────────────────────────────────


class TestPRIntervalFromVol:
    @pytest.fixture(scope="class")
    def interval(self):
        return p_r_interval_from_vol()

    def test_required_keys(self, interval):
        for key in (
            "vol_min", "vol_max", "p_r_11d_min", "p_r_11d_max",
            "p_r_geometric", "contains_two_loop_interval",
            "contains_fitted_value",
        ):
            assert key in interval

    def test_min_less_than_max(self, interval):
        assert interval["p_r_11d_min"] < interval["p_r_11d_max"]

    def test_both_positive(self, interval):
        assert interval["p_r_11d_min"] > 0
        assert interval["p_r_11d_max"] > 0

    def test_geometric_baseline_present(self, interval):
        assert interval["p_r_geometric"] == pytest.approx(P_R_FITTED_P383)


# ── p_r_conditional_certificate ──────────────────────────────────────────────


class TestPRConditionalCertificate:
    @pytest.fixture(scope="class")
    def cert(self):
        return p_r_conditional_certificate()

    def test_pillar_number(self, cert):
        assert cert["pillar"] == 520

    def test_status(self, cert):
        assert cert["status"] == "CONDITIONAL_DERIVATION_11D"

    def test_p_r_conditional_positive(self, cert):
        assert cert["p_r_conditional"] > 0

    def test_within_geometric_bounds(self, cert):
        assert cert["consistency_checks"]["within_geometric_bounds"] is True

    def test_open_condition_named(self, cert):
        assert "521" in cert["open_condition"]

    def test_upgrade_from_named(self, cert):
        assert "517" in cert["upgrade_from"]

    def test_no_hardgate_score_change(self, cert):
        assert cert["no_hardgate_score_change"] is True


# ── e8_gauge_pr_report ────────────────────────────────────────────────────────


class TestE8GaugePRReport:
    @pytest.fixture(scope="class")
    def report(self):
        return e8_gauge_pr_report()

    def test_pillar_number(self, report):
        assert report["pillar"] == 520

    def test_status(self, report):
        assert report["status"] == "CONDITIONAL_DERIVATION_11D"

    def test_track_label(self, report):
        assert "ADJACENT TRACK" in report["track"]

    def test_e8_coupling_present(self, report):
        ec = report["e8_coupling"]
        assert ec["g_e8_squared"] > 0
        assert ec["g_kk"] > 0
        assert 0 < ec["lambda_e8"] < 1

    def test_p_r_derivation_present(self, report):
        pr = report["p_r_derivation"]
        assert pr["p_r_11d_conditional"] > 0
        assert pr["within_geometric_bounds"] is True

    def test_upstream_pillars(self, report):
        assert 517 in report["upstream_pillars"]
        assert 521 in report["upstream_pillars"]

    def test_downstream_pillars(self, report):
        assert 523 in report["downstream_pillars"]
        assert 522 in report["downstream_pillars"]

    def test_no_hardgate_score_change(self, report):
        assert report["no_hardgate_score_change"] is True

    def test_deterministic(self):
        r1 = e8_gauge_pr_report()
        r2 = e8_gauge_pr_report()
        assert r1["p_r_derivation"]["p_r_11d_conditional"] == r2["p_r_derivation"]["p_r_11d_conditional"]
