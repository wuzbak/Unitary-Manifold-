# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 264 — two-loop Higgs naturalness UV completion in RS1/KK geometry.

Tests cover:
- One-loop correction sign and magnitude
- Two-loop perturbativity (d2 < d1)
- RS1 brane counterterm sign and scaling
- Barbieri-Giudice fine-tuning measure across M_KK range
- UV fixed-point existence, positivity, and stability
- Scan monotonicity and coverage
- Report key completeness
- Verdict logic thresholds
"""
from __future__ import annotations

import math

import pytest

from src.core.pillar264_higgs_naturalness_two_loop_uv import (
    C_A,
    C_F,
    DELTA_NATURAL_THRESHOLD,
    DELTA_PARTIAL_THRESHOLD,
    M_H_GEV,
    M_KK_DEFAULT_GEV,
    M_PL_GEV,
    Y_T,
    __all__ as MODULE_ALL,
    fine_tuning_delta,
    higgs_naturalness_two_loop_report,
    higgs_naturalness_two_loop_scan,
    one_loop_kk_higgs_correction,
    rs1_brane_counterterm,
    two_loop_qcd_yukawa_correction,
    uv_fixed_point_stability,
)

# ── Convenience constants ─────────────────────────────────────────────────────
_ALPHA_S = 0.113
_MKK_1TEV = 1.0e3   # 1 TeV in GeV
_MKK_500 = 500.0    # 500 GeV (Δ < 10 → DERIVED_NATURAL)
_MKK_5TEV = 5.0e3   # 5 TeV (Δ < 1000 but > 100 → ARCHITECTURE_LIMIT)
_MKK_LARGE = 1.0e8  # 100 PeV (deep ARCHITECTURE_LIMIT)

# ── Module structure ──────────────────────────────────────────────────────────

def test_all_exports_present():
    """__all__ must expose every required public function."""
    required = {
        "one_loop_kk_higgs_correction",
        "two_loop_qcd_yukawa_correction",
        "rs1_brane_counterterm",
        "fine_tuning_delta",
        "uv_fixed_point_stability",
        "higgs_naturalness_two_loop_report",
        "higgs_naturalness_two_loop_scan",
    }
    assert required.issubset(set(MODULE_ALL))


# ── One-loop KK correction ────────────────────────────────────────────────────

def test_one_loop_correction_positive():
    """One-loop KK correction must be positive (UV sensitivity)."""
    assert one_loop_kk_higgs_correction(_MKK_1TEV) > 0.0


def test_one_loop_correction_magnitude_order():
    """One-loop correction at 1 TeV must be O(10⁵) GeV²."""
    d1 = one_loop_kk_higgs_correction(_MKK_1TEV)
    assert 1.0e4 < d1 < 1.0e7


def test_one_loop_scales_quadratically_with_MKK():
    """Doubling M_KK quadruples the one-loop correction."""
    d1_low = one_loop_kk_higgs_correction(1.0e3)
    d1_high = one_loop_kk_higgs_correction(2.0e3)
    ratio = d1_high / d1_low
    assert abs(ratio - 4.0) < 1e-10


def test_one_loop_scales_linearly_with_N_KK():
    """One-loop correction is linear in N_KK."""
    d1_10 = one_loop_kk_higgs_correction(_MKK_1TEV, N_KK=10)
    d1_20 = one_loop_kk_higgs_correction(_MKK_1TEV, N_KK=20)
    assert abs(d1_20 / d1_10 - 2.0) < 1e-10


def test_one_loop_scales_with_yukawa():
    """One-loop correction scales as y_t²."""
    d1_ref = one_loop_kk_higgs_correction(_MKK_1TEV, y_t=Y_T)
    d1_half = one_loop_kk_higgs_correction(_MKK_1TEV, y_t=Y_T / 2.0)
    assert abs(d1_half / d1_ref - 0.25) < 1e-10


# ── Two-loop QCD-Yukawa correction ────────────────────────────────────────────

def test_two_loop_correction_positive():
    """Two-loop QCD-Yukawa correction must be positive."""
    d2 = two_loop_qcd_yukawa_correction(_MKK_1TEV)
    assert d2 > 0.0


def test_two_loop_smaller_than_one_loop():
    """Two-loop term must be smaller than one-loop (perturbativity check)."""
    d1 = one_loop_kk_higgs_correction(_MKK_1TEV)
    d2 = two_loop_qcd_yukawa_correction(_MKK_1TEV)
    assert d2 < d1


def test_two_loop_perturbativity_ratio():
    """Two-loop / one-loop ratio must be ≪ 1 (< 5 %)."""
    d1 = one_loop_kk_higgs_correction(_MKK_1TEV)
    d2 = two_loop_qcd_yukawa_correction(_MKK_1TEV)
    assert d2 / d1 < 0.05


def test_two_loop_scales_quadratically_with_MKK():
    """Two-loop correction is also proportional to M_KK²."""
    d2_low = two_loop_qcd_yukawa_correction(1.0e3)
    d2_high = two_loop_qcd_yukawa_correction(2.0e3)
    ratio = d2_high / d2_low
    assert abs(ratio - 4.0) < 1e-10


def test_two_loop_increases_with_alpha_s():
    """Larger α_s gives a larger two-loop correction."""
    d2_small = two_loop_qcd_yukawa_correction(_MKK_1TEV, alpha_s=0.05)
    d2_large = two_loop_qcd_yukawa_correction(_MKK_1TEV, alpha_s=0.20)
    assert d2_large > d2_small


def test_two_loop_uses_correct_color_factors():
    """Verify C_F = 4/3 and C_A = 3 are encoded correctly in the module."""
    assert abs(C_F - 4.0 / 3.0) < 1e-12
    assert abs(C_A - 3.0) < 1e-12


# ── RS1 brane counterterm ─────────────────────────────────────────────────────

def test_brane_counterterm_negative():
    """RS1 brane counterterm must be negative (partial cancellation)."""
    db = rs1_brane_counterterm(_MKK_1TEV)
    assert db < 0.0


def test_brane_counterterm_partial_cancellation():
    """Brane counterterm magnitude must exceed the one-loop term at 1 TeV."""
    d1 = one_loop_kk_higgs_correction(_MKK_1TEV)
    db = rs1_brane_counterterm(_MKK_1TEV)
    assert abs(db) > abs(d1)


def test_brane_counterterm_scales_quadratically_with_MKK():
    """Brane counterterm (via warp geometry) also scales as M_KK²."""
    db_low = rs1_brane_counterterm(1.0e3)
    db_high = rs1_brane_counterterm(2.0e3)
    ratio = db_high / db_low
    assert abs(ratio - 4.0) < 1e-6


def test_brane_counterterm_smaller_for_larger_kR():
    """Larger kR → larger warp suppression → smaller |brane counterterm|."""
    db_small_kR = rs1_brane_counterterm(_MKK_1TEV, kR=5.0)
    db_large_kR = rs1_brane_counterterm(_MKK_1TEV, kR=15.0)
    assert abs(db_large_kR) < abs(db_small_kR)


def test_brane_counterterm_explicit_kR():
    """Explicit kR parameter overrides the derived value."""
    kR_val = 10.0
    db = rs1_brane_counterterm(_MKK_1TEV, kR=kR_val)
    expected = -(3.0 * Y_T ** 2 / (8.0 * math.pi ** 2)) * M_PL_GEV ** 2 * math.exp(
        -2.0 * math.pi * kR_val
    )
    assert abs(db / expected - 1.0) < 1e-12


# ── Fine-tuning measure ───────────────────────────────────────────────────────

def test_fine_tuning_positive():
    """Fine-tuning measure Δ must be positive."""
    delta = fine_tuning_delta(_MKK_1TEV)
    assert delta > 0.0


def test_fine_tuning_less_100_at_1TeV():
    """Δ < 100 at M_KK = 1 TeV: KK tower + RS1 brane achieves naturalness bound."""
    delta = fine_tuning_delta(_MKK_1TEV)
    assert delta < DELTA_PARTIAL_THRESHOLD


def test_fine_tuning_less_10_at_500GeV():
    """Δ < 10 at M_KK = 500 GeV: genuine naturalness regime."""
    delta = fine_tuning_delta(_MKK_500)
    assert delta < DELTA_NATURAL_THRESHOLD


def test_fine_tuning_less_1000_at_5TeV():
    """Δ < 1000 at M_KK = 5 TeV (within an order of magnitude of threshold)."""
    delta = fine_tuning_delta(_MKK_5TEV)
    assert delta < 1000.0


def test_fine_tuning_increases_with_MKK():
    """Fine-tuning is monotone increasing with M_KK."""
    d_low = fine_tuning_delta(1.0e3)
    d_mid = fine_tuning_delta(1.0e4)
    d_high = fine_tuning_delta(1.0e5)
    assert d_low < d_mid < d_high


# ── UV fixed-point analysis ───────────────────────────────────────────────────

def test_uv_fixed_point_alpha_positive():
    """The UV fixed-point coupling α_* must be positive."""
    fp = uv_fixed_point_stability()
    assert fp["alpha_fixed_point"] > 0.0


def test_uv_fixed_point_perturbative():
    """The UV fixed point must be in the perturbative regime (α_* < 1)."""
    fp = uv_fixed_point_stability()
    assert fp["alpha_fixed_point"] < 1.0


def test_uv_fixed_point_stable():
    """The UV fixed point must be declared stable for canonical parameters."""
    fp = uv_fixed_point_stability()
    assert fp["fixed_point_stable"] is True


def test_uv_fixed_point_dict_keys():
    """Fixed-point dict must contain all required keys."""
    required = {
        "b0", "b1", "alpha_fixed_point", "fixed_point_stable",
        "alpha_s_at_MZ", "alpha_ratio", "N_KK", "N_c",
    }
    fp = uv_fixed_point_stability()
    assert required.issubset(fp.keys())


def test_uv_fixed_point_alpha_ratio_subunit():
    """α_s(M_Z) / α_* < 1 confirms the theory is below the fixed point."""
    fp = uv_fixed_point_stability()
    assert fp["alpha_ratio"] < 1.0


def test_uv_fixed_point_b1_negative_for_N_KK_10():
    """b₁ < 0 with N_KK=10 signals asymptotic-safety UV fixed point."""
    fp = uv_fixed_point_stability(N_KK=10)
    assert fp["b1"] < 0.0


def test_uv_fixed_point_b0_positive_for_N_KK_10():
    """b₀ > 0 with N_KK=10 confirms the theory is (perturbatively) asymptotically free."""
    fp = uv_fixed_point_stability(N_KK=10)
    assert fp["b0"] > 0.0


# ── Full report ───────────────────────────────────────────────────────────────

_REQUIRED_REPORT_KEYS = {
    "M_KK_gev",
    "kR",
    "delta_fine_tuning",
    "one_loop_correction_gev2",
    "two_loop_correction_gev2",
    "brane_counterterm_gev2",
    "total_correction_gev2",
    "verdict",
    "closure_note",
    "fixed_point_info",
    "pillar",
    "adjacency_label",
}


def test_report_keys_present():
    """Full report must contain all required keys."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert _REQUIRED_REPORT_KEYS.issubset(r.keys())


def test_report_pillar_number():
    """Report must identify itself as Pillar 264."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert r["pillar"] == 264


def test_report_adjacency_label():
    """Report must carry the NON_HARDGATE_ADJACENT label."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert r["adjacency_label"] == "NON_HARDGATE_ADJACENT"


def test_report_total_is_sum_of_parts():
    """total_correction_gev2 must equal d1 + d2 + brane."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    expected = (
        r["one_loop_correction_gev2"]
        + r["two_loop_correction_gev2"]
        + r["brane_counterterm_gev2"]
    )
    assert abs(r["total_correction_gev2"] - expected) < 1e-6


def test_report_delta_consistent():
    """delta_fine_tuning must equal |total_correction| / m_H²."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    expected_delta = abs(r["total_correction_gev2"]) / M_H_GEV ** 2
    assert abs(r["delta_fine_tuning"] - expected_delta) < 1e-10


def test_report_verdict_natural_at_500GeV():
    """DERIVED_NATURAL verdict at M_KK = 500 GeV (Δ < 10)."""
    r = higgs_naturalness_two_loop_report(_MKK_500)
    assert r["verdict"] == "DERIVED_NATURAL"


def test_report_verdict_partial_at_1TeV():
    """DERIVED_PARTIAL verdict at M_KK = 1 TeV (10 ≤ Δ < 100)."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert r["verdict"] == "DERIVED_PARTIAL"


def test_report_verdict_arch_limit_at_5TeV():
    """ARCHITECTURE_LIMIT verdict at M_KK = 5 TeV (Δ ≥ 100)."""
    r = higgs_naturalness_two_loop_report(_MKK_5TEV)
    assert r["verdict"] == "ARCHITECTURE_LIMIT"


def test_report_closure_note_mentions_6D_gap():
    """Every closure note must honestly mention the 6D open gap."""
    for mkk in [_MKK_500, _MKK_1TEV, _MKK_5TEV]:
        r = higgs_naturalness_two_loop_report(mkk)
        assert "6D" in r["closure_note"] or "6d" in r["closure_note"].lower()


def test_report_brane_counterterm_negative():
    """brane_counterterm_gev2 in the report must be negative."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert r["brane_counterterm_gev2"] < 0.0


def test_report_two_loop_less_than_one_loop():
    """two_loop_correction_gev2 < one_loop_correction_gev2 in the report."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert r["two_loop_correction_gev2"] < r["one_loop_correction_gev2"]


def test_report_kR_positive():
    """Derived kR must be positive."""
    r = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert r["kR"] > 0.0


# ── Scan ─────────────────────────────────────────────────────────────────────

def test_scan_default_returns_7_points():
    """Default scan (1e3 – 1e9 GeV decade spacing) returns exactly 7 points."""
    results = higgs_naturalness_two_loop_scan()
    assert len(results) == 7


def test_scan_covers_all_requested_MKK():
    """Custom scan returns one entry per requested M_KK value."""
    mkk_vals = [1.0e3, 2.0e3, 5.0e3]
    results = higgs_naturalness_two_loop_scan(mkk_vals)
    assert len(results) == len(mkk_vals)
    returned_mkk = [r["M_KK_gev"] for r in results]
    for mkk in mkk_vals:
        assert mkk in returned_mkk


def test_scan_all_have_required_keys():
    """Every scan entry must contain all required report keys."""
    results = higgs_naturalness_two_loop_scan([1.0e3, 1.0e4])
    for r in results:
        assert _REQUIRED_REPORT_KEYS.issubset(r.keys())


def test_scan_monotone_fine_tuning():
    """Fine-tuning Δ is strictly monotone increasing with M_KK in the default scan."""
    results = higgs_naturalness_two_loop_scan()
    deltas = [r["delta_fine_tuning"] for r in results]
    assert all(deltas[i] < deltas[i + 1] for i in range(len(deltas) - 1))


def test_scan_contains_natural_and_unnatural_points():
    """Scan must include both DERIVED_NATURAL and ARCHITECTURE_LIMIT verdicts."""
    results = higgs_naturalness_two_loop_scan([500.0, 1.0e3, 1.0e5])
    verdicts = {r["verdict"] for r in results}
    assert "DERIVED_NATURAL" in verdicts
    assert "ARCHITECTURE_LIMIT" in verdicts


def test_scan_delta_at_1TeV_consistent():
    """Scan entry at 1 TeV must agree with standalone report."""
    scan_1tev = higgs_naturalness_two_loop_scan([_MKK_1TEV])[0]
    report_1tev = higgs_naturalness_two_loop_report(_MKK_1TEV)
    assert abs(scan_1tev["delta_fine_tuning"] - report_1tev["delta_fine_tuning"]) < 1e-10


# ── Threshold constants ───────────────────────────────────────────────────────

def test_naturalness_threshold_value():
    """DELTA_NATURAL_THRESHOLD must be 10.0."""
    assert DELTA_NATURAL_THRESHOLD == 10.0


def test_partial_threshold_value():
    """DELTA_PARTIAL_THRESHOLD must be 100.0."""
    assert DELTA_PARTIAL_THRESHOLD == 100.0
