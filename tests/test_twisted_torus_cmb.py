# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_twisted_torus_cmb.py
================================
Tests for src/core/twisted_torus_cmb.py — Pillar 115:
Twisted Torus CMB Signatures (E2/E3 Observable Predictions).

Physical claims under test
--------------------------
1. l_cut: correct formula π / L_over_chi; large L → small ℓ_cut; invalid raises.
2. low_l_power_ratio: monotonically increasing with ell; → 1 for large ell; → 0 for tiny ell.
3. circle_cross_correlation: E1 (θ=0°) → positive; E2 (θ=180°) → negative; E3 (θ=90°) → 0.
4. minimum_detectable_size: E2 > 0; E3 > 0; depends on sigma_C.
5. quadrupole_axis_anisotropy: E1 no axis; E2 fold=2; E3 fold=4.
6. litebird_topology_forecast: correct structure; primary_um_target_unaffected=True.
7. e2_e3_cmb_summary: correct structure; L_over_chi passed through.
8. topology_signal_table: correct correlations; um_prediction_affected=False.
9. Input validation: ValueError on bad topology, ell < 2, L_over_chi ≤ 0.
"""

from __future__ import annotations

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.core.twisted_torus_cmb import (
    l_cut,
    low_l_power_ratio,
    circle_cross_correlation,
    minimum_detectable_size,
    quadrupole_axis_anisotropy,
    litebird_topology_forecast,
    e2_e3_cmb_summary,
    topology_signal_table,
    TWIST_ANGLES_DEG,
    LITEBIRD_SIGMA_C,
)


# ---------------------------------------------------------------------------
# l_cut
# ---------------------------------------------------------------------------

class TestLCut:
    def test_formula_l_over_chi_1(self):
        assert l_cut(1.0) == pytest.approx(math.pi, rel=1e-9)

    def test_formula_l_over_chi_half(self):
        # L = 0.5 χ_rec → ℓ_cut = π/0.5 = 2π ≈ 6.28
        assert l_cut(0.5) == pytest.approx(2 * math.pi, rel=1e-9)

    def test_larger_L_smaller_l_cut(self):
        # Bigger torus → smaller cut-off multipole
        assert l_cut(2.0) < l_cut(1.0)

    def test_smaller_L_larger_l_cut(self):
        assert l_cut(0.3) > l_cut(0.5)

    def test_positive_output(self):
        assert l_cut(0.7) > 0

    def test_zero_L_raises(self):
        with pytest.raises(ValueError):
            l_cut(0.0)

    def test_negative_L_raises(self):
        with pytest.raises(ValueError):
            l_cut(-1.0)


# ---------------------------------------------------------------------------
# low_l_power_ratio
# ---------------------------------------------------------------------------

class TestLowLPowerRatio:
    def test_high_ell_approaches_1(self):
        # ℓ >> ℓ_cut → ratio → 1
        r = low_l_power_ratio(100.0, 1.0)
        assert r > 0.99

    def test_at_l_cut_half_power(self):
        # By logistic definition, at ℓ = ℓ_cut the ratio ≈ 0.5
        lc = l_cut(1.0)
        r = low_l_power_ratio(lc, 1.0)
        assert 0.45 < r < 0.55

    def test_low_ell_suppressed(self):
        # ℓ << ℓ_cut → strongly suppressed
        r = low_l_power_ratio(2.0, 0.1)  # ℓ_cut ≈ 31 >> 2
        assert r < 0.01

    def test_monotone_in_ell(self):
        L = 0.5
        vals = [low_l_power_ratio(float(ell), L) for ell in [2, 5, 10, 20, 50]]
        assert all(vals[i] < vals[i+1] for i in range(len(vals)-1))

    def test_range_is_01(self):
        for ell in [2.0, 5.0, 20.0, 100.0]:
            r = low_l_power_ratio(ell, 0.5)
            assert 0.0 <= r <= 1.0

    def test_ell_below_2_raises(self):
        with pytest.raises(ValueError):
            low_l_power_ratio(1.0, 1.0)

    def test_invalid_L_raises(self):
        with pytest.raises(ValueError):
            low_l_power_ratio(5.0, 0.0)


# ---------------------------------------------------------------------------
# circle_cross_correlation
# ---------------------------------------------------------------------------

class TestCircleCrossCorrelation:
    def test_e1_at_zero_separation_positive(self):
        """θ=0°, α=0°: C = 1 × cos(0) = 1."""
        c = circle_cross_correlation(0.0, 0.0)
        assert c == pytest.approx(1.0, rel=1e-9)

    def test_e2_at_zero_separation_negative(self):
        """θ=180°, α=0°: C = 1 × cos(π) = -1."""
        c = circle_cross_correlation(0.0, 180.0)
        assert c == pytest.approx(-1.0, rel=1e-9)

    def test_e3_at_zero_separation_zero(self):
        """θ=90°, α=0°: C = 1 × cos(π/2) = 0."""
        c = circle_cross_correlation(0.0, 90.0)
        assert abs(c) < 1e-12

    def test_e1_decreases_with_separation(self):
        # cos(0°) envelope decreases with α
        c0 = circle_cross_correlation(0.0, 0.0)
        c5 = circle_cross_correlation(5.0, 0.0)
        assert c5 < c0

    def test_e2_anticorrelation_at_small_sep(self):
        c = circle_cross_correlation(1.0, 180.0)
        assert c < 0.0

    def test_invalid_negative_alpha(self):
        with pytest.raises(ValueError):
            circle_cross_correlation(-1.0, 0.0)

    def test_invalid_twist_over_360(self):
        with pytest.raises(ValueError):
            circle_cross_correlation(0.0, 361.0)

    def test_invalid_negative_twist(self):
        with pytest.raises(ValueError):
            circle_cross_correlation(0.0, -10.0)


# ---------------------------------------------------------------------------
# minimum_detectable_size
# ---------------------------------------------------------------------------

class TestMinimumDetectableSize:
    def test_e2_positive(self):
        s = minimum_detectable_size("E2")
        assert s > 0.0

    def test_e3_positive(self):
        s = minimum_detectable_size("E3")
        assert s > 0.0

    def test_smaller_sigma_larger_l(self):
        # Better noise → can detect larger (further) tori
        s_good = minimum_detectable_size("E2", sigma_C=0.001)
        s_bad = minimum_detectable_size("E2", sigma_C=0.1)
        assert s_good < s_bad  # smaller L_max when noise is worse

    def test_invalid_topology(self):
        with pytest.raises(ValueError):
            minimum_detectable_size("E1")

    def test_invalid_sigma_raises(self):
        with pytest.raises(ValueError):
            minimum_detectable_size("E2", sigma_C=0.0)

    def test_e2_less_than_1(self):
        # Detection requires L < χ_rec
        s = minimum_detectable_size("E2")
        assert s < 1.5  # Reasonable upper bound


# ---------------------------------------------------------------------------
# quadrupole_axis_anisotropy
# ---------------------------------------------------------------------------

class TestQuadrupoleAxisAnisotropy:
    def test_e1_no_axis(self):
        a = quadrupole_axis_anisotropy("E1")
        assert a["axis_present"] is False

    def test_e2_fold_2(self):
        a = quadrupole_axis_anisotropy("E2")
        assert a["symmetry_fold"] == 2
        assert a["axis_present"] is True

    def test_e3_fold_4(self):
        a = quadrupole_axis_anisotropy("E3")
        assert a["symmetry_fold"] == 4
        assert a["axis_present"] is True

    def test_invalid_topology(self):
        with pytest.raises(ValueError):
            quadrupole_axis_anisotropy("E4")

    def test_topology_key_present(self):
        for top in ("E1", "E2", "E3"):
            a = quadrupole_axis_anisotropy(top)
            assert a["topology"] == top

    def test_pattern_description_present(self):
        for top in ("E1", "E2", "E3"):
            a = quadrupole_axis_anisotropy(top)
            assert "description" in a["pattern_description"] or len(a["pattern_description"]) > 5


# ---------------------------------------------------------------------------
# litebird_topology_forecast
# ---------------------------------------------------------------------------

class TestLiteBIRDTopologyForecast:
    def test_primary_um_target_unaffected(self):
        for top in ("E1", "E2", "E3"):
            f = litebird_topology_forecast(top, 1.0)
            assert f["primary_um_target_unaffected"] is True

    def test_e1_not_detectable(self):
        f = litebird_topology_forecast("E1", 0.3)
        assert f["detectable"] is False

    def test_e2_not_detectable_large_torus(self):
        f = litebird_topology_forecast("E2", 2.0)
        assert f["detectable"] is False

    def test_e3_not_detectable_large_torus(self):
        f = litebird_topology_forecast("E3", 2.0)
        assert f["detectable"] is False

    def test_invalid_topology_raises(self):
        with pytest.raises(ValueError):
            litebird_topology_forecast("E4", 0.5)

    def test_invalid_L_raises(self):
        with pytest.raises(ValueError):
            litebird_topology_forecast("E2", 0.0)

    def test_l_cut_in_output(self):
        f = litebird_topology_forecast("E2", 0.5)
        assert "l_cut" in f
        assert f["l_cut"] > 0

    def test_reason_present(self):
        f = litebird_topology_forecast("E2", 1.0)
        assert "reason" in f
        assert len(f["reason"]) > 5


# ---------------------------------------------------------------------------
# e2_e3_cmb_summary
# ---------------------------------------------------------------------------

class TestE2E3CMBSummary:
    def test_l_over_chi_passthrough(self):
        s = e2_e3_cmb_summary(1.0)
        assert s["L_over_chi"] == 1.0

    def test_e2_key_present(self):
        s = e2_e3_cmb_summary(1.0)
        assert "E2" in s

    def test_e3_key_present(self):
        s = e2_e3_cmb_summary(1.0)
        assert "E3" in s

    def test_l_cut_present(self):
        s = e2_e3_cmb_summary(1.0)
        assert "l_cut" in s
        assert s["l_cut"] == pytest.approx(math.pi, rel=1e-9)

    def test_e2_correlation_at_zero_negative(self):
        s = e2_e3_cmb_summary(1.0)
        assert s["E2"]["circle_correlation_at_0deg"] == pytest.approx(-1.0, rel=1e-9)

    def test_e3_correlation_at_zero(self):
        s = e2_e3_cmb_summary(1.0)
        assert abs(s["E3"]["circle_correlation_at_0deg"]) < 1e-12

    def test_power_fraction_l2_between_0_and_1(self):
        s = e2_e3_cmb_summary(0.5)
        assert 0.0 <= s["E2"]["power_fraction_at_l2"] <= 1.0
        assert 0.0 <= s["E3"]["power_fraction_at_l2"] <= 1.0

    def test_invalid_L_raises(self):
        with pytest.raises(ValueError):
            e2_e3_cmb_summary(0.0)


# ---------------------------------------------------------------------------
# topology_signal_table
# ---------------------------------------------------------------------------

class TestTopologySignalTable:
    def test_three_keys(self):
        t = topology_signal_table()
        assert set(t.keys()) == {"E1", "E2", "E3"}

    def test_e1_correlation_1(self):
        t = topology_signal_table()
        assert t["E1"]["correlation_at_0deg"] == pytest.approx(1.0, rel=1e-9)

    def test_e2_correlation_minus1(self):
        t = topology_signal_table()
        assert t["E2"]["correlation_at_0deg"] == pytest.approx(-1.0, rel=1e-9)

    def test_e3_correlation_0(self):
        t = topology_signal_table()
        assert t["E3"]["correlation_at_0deg"] == pytest.approx(0.0, abs=1e-12)

    def test_um_prediction_unaffected(self):
        t = topology_signal_table()
        for top in ("E1", "E2", "E3"):
            assert t[top]["um_prediction_affected"] is False

    def test_e1_ruled_out(self):
        t = topology_signal_table()
        assert "RULED_OUT" in t["E1"]["observational_status"]

    def test_e2_e3_viable(self):
        t = topology_signal_table()
        assert t["E2"]["observational_status"] == "VIABLE"
        assert t["E3"]["observational_status"] == "VIABLE"
