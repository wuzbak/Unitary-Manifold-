# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Pillar 787 — Falsification Boundary Map."""

from __future__ import annotations

import pytest

from src.core.pillar787_falsification_boundary_map import (
    PILLAR,
    VERSION,
    STATUS,
    BETA_PREDICTED_CANONICAL,
    BETA_PREDICTED_DERIVED,
    BETA_ADMISSIBLE_LO,
    BETA_ADMISSIBLE_HI,
    BETA_GAP_LO,
    BETA_GAP_HI,
    N_S_PREDICTED,
    R_PREDICTED,
    EXPERIMENT_REGISTRY,
    get_experiment,
    compute_boundary_map,
    verdict_for_value,
    falsification_boundary_summary,
    TEST_EXPECTATIONS,
)


# ── Metadata ───────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR == 787

def test_version():
    assert VERSION == "v23.0"

def test_status():
    assert STATUS == "FALSIFICATION_MAP_REGISTERED"

# ── Boundary constants ────────────────────────────────────────────────────

def test_beta_canonical_pair():
    assert BETA_PREDICTED_CANONICAL == (0.273, 0.331)

def test_beta_derived_pair():
    assert BETA_PREDICTED_DERIVED == (0.290, 0.351)

def test_beta_admissible_lo():
    assert BETA_ADMISSIBLE_LO == 0.22

def test_beta_admissible_hi():
    assert BETA_ADMISSIBLE_HI == 0.38

def test_beta_gap_lo():
    assert BETA_GAP_LO == 0.29

def test_beta_gap_hi():
    assert BETA_GAP_HI == 0.31

def test_n_s_predicted():
    assert abs(N_S_PREDICTED - 0.9635) < 1e-6

def test_r_predicted():
    assert abs(R_PREDICTED - 0.0315) < 1e-6

# ── Experiment registry ───────────────────────────────────────────────────

def test_registry_has_seven_experiments():
    assert len(EXPERIMENT_REGISTRY) == 7

def test_registry_required_ids():
    ids = {e["id"] for e in EXPERIMENT_REGISTRY}
    for req in ["litebird", "desi", "juno", "act", "hl_lhc", "nedm", "xenon_nt"]:
        assert req in ids

def test_each_experiment_has_required_fields():
    required = ["id", "name", "observable", "um_prediction", "falsifies_if",
                "confirms_if", "launch_year", "status"]
    for exp in EXPERIMENT_REGISTRY:
        for field in required:
            assert field in exp, f"Missing {field!r} in {exp['id']!r}"

def test_litebird_primary_falsifier():
    exp = get_experiment("litebird")
    assert exp["launch_year"] == 2032

def test_desi_has_current_tension():
    exp = get_experiment("desi")
    assert exp["current_tension_sigma"] is not None

def test_get_experiment_unknown_raises():
    with pytest.raises(KeyError):
        get_experiment("nonexistent_exp")

def test_experiment_launch_years_positive():
    for exp in EXPERIMENT_REGISTRY:
        assert exp["launch_year"] > 2020

# ── verdict_for_value — LiteBIRD ─────────────────────────────────────────

def test_litebird_inside_canonical_confirmed():
    # β = 0.273 is the low end of canonical pair
    assert verdict_for_value("litebird", 0.273) == "CONFIRMED"

def test_litebird_inside_high_canonical_confirmed():
    assert verdict_for_value("litebird", 0.331) == "CONFIRMED"

def test_litebird_below_window_falsified():
    assert verdict_for_value("litebird", 0.10) == "FALSIFIED"

def test_litebird_above_window_falsified():
    assert verdict_for_value("litebird", 0.50) == "FALSIFIED"

def test_litebird_in_gap_falsified():
    # β = 0.30 is inside predicted gap [0.29, 0.31]
    assert verdict_for_value("litebird", 0.30) == "FALSIFIED"

def test_litebird_gap_lo_boundary():
    assert verdict_for_value("litebird", 0.29) == "FALSIFIED"

def test_litebird_gap_hi_boundary():
    assert verdict_for_value("litebird", 0.31) == "FALSIFIED"

def test_litebird_admissible_but_outside_canonical_inconclusive():
    # β = 0.25 is in admissible window but below canonical pair
    assert verdict_for_value("litebird", 0.25) == "INCONCLUSIVE"

# ── verdict_for_value — DESI ──────────────────────────────────────────────

def test_desi_zero_wa_confirmed():
    assert verdict_for_value("desi", 0.0) == "CONFIRMED"

def test_desi_small_wa_confirmed():
    assert verdict_for_value("desi", 0.04) == "CONFIRMED"

def test_desi_large_wa_falsified():
    assert verdict_for_value("desi", 0.5) == "FALSIFIED"

def test_desi_moderate_wa_inconclusive():
    assert verdict_for_value("desi", -0.15) == "INCONCLUSIVE"

# ── verdict_for_value — ACT ───────────────────────────────────────────────

def test_act_ns_in_range_confirmed():
    assert verdict_for_value("act", 0.9635) == "CONFIRMED"

def test_act_ns_too_low_falsified():
    assert verdict_for_value("act", 0.940) == "FALSIFIED"

def test_act_ns_too_high_falsified():
    assert verdict_for_value("act", 0.980) == "FALSIFIED"

# ── compute_boundary_map ──────────────────────────────────────────────────

def test_compute_boundary_map_keys():
    m = compute_boundary_map()
    for key in ["pillar", "version", "status", "n_experiments",
                "primary_falsifier", "beta_boundary", "experiments"]:
        assert key in m

def test_compute_boundary_map_n_experiments():
    m = compute_boundary_map()
    assert m["n_experiments"] == 7

def test_compute_boundary_map_primary_falsifier():
    m = compute_boundary_map()
    assert m["primary_falsifier"] == "litebird"

def test_compute_boundary_map_beta_boundary_keys():
    m = compute_boundary_map()
    bb = m["beta_boundary"]
    for key in ["admissible_lo", "admissible_hi", "predicted_gap_lo",
                "predicted_gap_hi", "canonical_pair", "derived_pair"]:
        assert key in bb

def test_compute_boundary_map_experiments_list():
    m = compute_boundary_map()
    assert len(m["experiments"]) == 7

# ── falsification_boundary_summary ───────────────────────────────────────

def test_summary_has_interpretation():
    s = falsification_boundary_summary()
    assert "interpretation" in s
    assert len(s["interpretation"]) > 50

def test_summary_pillar():
    s = falsification_boundary_summary()
    assert s["pillar"] == 787

# ── TEST_EXPECTATIONS ─────────────────────────────────────────────────────

def test_expectations_pillar():
    assert TEST_EXPECTATIONS["pillar"] == 787

def test_expectations_n_experiments():
    assert TEST_EXPECTATIONS["n_experiments"] == 7

def test_expectations_primary_falsifier():
    assert TEST_EXPECTATIONS["primary_falsifier"] == "litebird"

def test_expectations_verdict_inside():
    assert TEST_EXPECTATIONS["verdict_inside_canonical"] == "CONFIRMED"

def test_expectations_verdict_outside():
    assert TEST_EXPECTATIONS["verdict_outside_window"] == "FALSIFIED"

def test_expectations_verdict_in_gap():
    assert TEST_EXPECTATIONS["verdict_in_gap"] == "FALSIFIED"
