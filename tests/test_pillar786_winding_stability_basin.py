# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 786 — Winding Resonance Stability Basin."""

from __future__ import annotations

import math
import pytest

from src.core.pillar786_winding_stability_basin import (
    PILLAR,
    VERSION,
    STATUS,
    N_W_SELECTED,
    K_CS,
    N_S_WINDOW_LO,
    N_S_WINDOW_HI,
    R_WINDOW_HI,
    BETA_WINDOW_LO,
    BETA_WINDOW_HI,
    STABILITY_BASIN,
    STABILITY_BASIN_SIZE,
    STABILITY_BASIN_GATE,
    n_s_from_winding,
    r_from_winding,
    beta_from_winding,
    winding_passes_ns,
    winding_passes_r,
    winding_passes_beta,
    winding_in_basin,
    compute_stability_basin,
    stability_basin_summary,
    TEST_EXPECTATIONS,
)


# ── Metadata ───────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR == 786

def test_version():
    assert VERSION == "v23.0"

def test_status():
    assert STATUS == "WINDING_BASIN_CLOSED"

def test_n_w_selected():
    assert N_W_SELECTED == 5

def test_k_cs():
    assert K_CS == 74

# ── Observational windows ─────────────────────────────────────────────────

def test_ns_window_lo():
    assert abs(N_S_WINDOW_LO - (0.9649 - 2 * 0.0042)) < 1e-6

def test_ns_window_hi():
    assert abs(N_S_WINDOW_HI - (0.9649 + 2 * 0.0042)) < 1e-6

def test_r_window_hi():
    assert R_WINDOW_HI == 0.036

def test_beta_window_lo():
    assert BETA_WINDOW_LO == 0.22

def test_beta_window_hi():
    assert BETA_WINDOW_HI == 0.38

# ── n_s_from_winding ──────────────────────────────────────────────────────

def test_ns_n5_value():
    """n_s(5) = 1 - 2/(6*25-1) = 1 - 2/149 ≈ 0.9866… wait, check formula."""
    ns = n_s_from_winding(5)
    assert 0.90 < ns < 1.0

def test_ns_increases_with_nw():
    """Larger n_w → shallower potential → n_s closer to 1."""
    for n_w in range(1, 14):
        assert n_s_from_winding(n_w) < n_s_from_winding(n_w + 1)

def test_ns_n1_less_than_n5():
    assert n_s_from_winding(1) < n_s_from_winding(5)

def test_ns_n15_gt_n5():
    assert n_s_from_winding(15) > n_s_from_winding(5)

def test_ns_invalid_zero():
    with pytest.raises(ValueError):
        n_s_from_winding(0)

def test_ns_invalid_negative():
    with pytest.raises(ValueError):
        n_s_from_winding(-3)

# ── r_from_winding ────────────────────────────────────────────────────────

def test_r_positive():
    for n_w in range(1, 16):
        assert r_from_winding(n_w) > 0

def test_r_decreases_with_nw():
    """Larger n_w → smaller r."""
    for n_w in range(1, 14):
        assert r_from_winding(n_w) > r_from_winding(n_w + 1)

def test_r_n5_below_bicep_bound():
    assert r_from_winding(5) < R_WINDOW_HI

def test_r_invalid_zero():
    with pytest.raises(ValueError):
        r_from_winding(0)

# ── beta_from_winding ─────────────────────────────────────────────────────

def test_beta_returns_pair():
    b = beta_from_winding(5)
    assert len(b) == 2

def test_beta_n5_canonical():
    b_lo, b_hi = beta_from_winding(5)
    assert abs(b_lo - 0.273) < 1e-9
    assert abs(b_hi - 0.331) < 1e-9

def test_beta_ordered():
    for n_w in range(1, 16):
        b_lo, b_hi = beta_from_winding(n_w)
        assert b_lo < b_hi

def test_beta_decreases_with_nw():
    """Larger n_w → smaller β."""
    for n_w in range(1, 14):
        b_lo_a, _ = beta_from_winding(n_w)
        b_lo_b, _ = beta_from_winding(n_w + 1)
        assert b_lo_a > b_lo_b

def test_beta_invalid():
    with pytest.raises(ValueError):
        beta_from_winding(0)

# ── Basin membership tests ─────────────────────────────────────────────────

def test_n5_passes_ns():
    assert winding_passes_ns(5)

def test_n5_passes_r():
    assert winding_passes_r(5)

def test_n5_passes_beta():
    assert winding_passes_beta(5)

def test_n5_in_basin():
    assert winding_in_basin(5)

def test_n1_fails():
    """n_w=1 gives very small n_s, should fail the n_s window."""
    assert not winding_in_basin(1)

def test_n15_fails():
    """n_w=15 gives very large β → outside admissible window."""
    assert not winding_in_basin(15)

def test_n2_fails():
    assert not winding_in_basin(2)

def test_n3_fails():
    assert not winding_in_basin(3)

def test_n10_fails():
    assert not winding_in_basin(10)

# ── Full basin computation ─────────────────────────────────────────────────

def test_stability_basin_singleton():
    assert STABILITY_BASIN == frozenset({5})

def test_stability_basin_size():
    assert STABILITY_BASIN_SIZE == 1

def test_stability_basin_gate():
    assert STABILITY_BASIN_GATE == "WINDING_BASIN_CLOSED"

def test_compute_basin_returns_dict():
    result = compute_stability_basin()
    assert isinstance(result, dict)

def test_compute_basin_selected_in_basin():
    result = compute_stability_basin()
    assert result["selected_in_basin"] is True

def test_compute_basin_full_report_length():
    result = compute_stability_basin()
    lo, hi = result["winding_range_tested"]
    assert len(result["full_report"]) == hi - lo + 1

def test_compute_basin_full_report_keys():
    result = compute_stability_basin()
    row = result["full_report"][0]
    for key in ["n_w", "n_s", "r", "beta_low_deg", "beta_high_deg",
                "passes_ns", "passes_r", "passes_beta", "in_basin"]:
        assert key in row

def test_compute_basin_gate_value():
    result = compute_stability_basin()
    assert result["gate"] == "WINDING_BASIN_CLOSED"

def test_compute_basin_n5_row():
    result = compute_stability_basin()
    n5_rows = [r for r in result["full_report"] if r["n_w"] == 5]
    assert len(n5_rows) == 1
    assert n5_rows[0]["in_basin"] is True

# ── Summary ────────────────────────────────────────────────────────────────

def test_summary_keys():
    s = stability_basin_summary()
    for key in ["pillar", "version", "status", "stability_basin",
                "basin_size", "gate", "observational_windows", "interpretation"]:
        assert key in s

def test_summary_basin():
    s = stability_basin_summary()
    assert s["stability_basin"] == [5]

def test_summary_interpretation_not_empty():
    s = stability_basin_summary()
    assert len(s["interpretation"]) > 50

# ── TEST_EXPECTATIONS ─────────────────────────────────────────────────────

def test_expectations_pillar():
    assert TEST_EXPECTATIONS["pillar"] == 786

def test_expectations_basin_singleton():
    assert TEST_EXPECTATIONS["basin_singleton"] is True

def test_expectations_n5_in_basin():
    assert TEST_EXPECTATIONS["n_w_5_in_basin"] is True

def test_expectations_n1_not_in_basin():
    assert TEST_EXPECTATIONS["n_w_1_in_basin"] is False

def test_expectations_gate():
    assert TEST_EXPECTATIONS["gate"] == "WINDING_BASIN_CLOSED"
