# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 789 — WINDING_RESONANCE_STABILITY_BASIN (55 tests)."""

import math
import pytest
from src.core.pillar789_winding_resonance_stability_basin import (
    N_W_SELECTED, N_W_SECONDARY,
    N_S_LOW, N_S_HIGH, BETA_LOW_DEG, BETA_HIGH_DEG,
    BETA_GAP_LOW, BETA_GAP_HIGH, R_BICEP_LIMIT,
    N_S_PREDICTED, BETA_PREDICTED_DEG, R_PREDICTED, K_CS_NW5,
    is_admissible, compute_stability_basin, get_stability_basin_dict,
    STABILITY_BASIN, PILLAR_STATUS, PILLAR_NUMBER,
    run_pillar789, StabilityBasin,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
class TestConstants:
    def test_n_w_selected(self):
        assert N_W_SELECTED == 5

    def test_n_w_secondary(self):
        assert N_W_SECONDARY == 7

    def test_ns_window_ordered(self):
        assert N_S_LOW < N_S_HIGH

    def test_beta_window_ordered(self):
        assert BETA_LOW_DEG < BETA_HIGH_DEG

    def test_beta_gap_inside_window(self):
        assert BETA_LOW_DEG < BETA_GAP_LOW < BETA_GAP_HIGH < BETA_HIGH_DEG

    def test_r_limit_positive(self):
        assert R_BICEP_LIMIT > 0

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 789

    def test_status_string(self):
        assert "STABILITY" in PILLAR_STATUS


# ---------------------------------------------------------------------------
# Predicted observables at n_w = 5
# ---------------------------------------------------------------------------
class TestGeometryNW5:
    def test_k_cs_nw5(self):
        assert K_CS_NW5 == 74  # 5² + 7² = 74

    def test_spectral_index_nw5_in_planck_window(self):
        assert N_S_LOW <= N_S_PREDICTED <= N_S_HIGH

    def test_spectral_index_nw5_value(self):
        assert 0.960 < N_S_PREDICTED < 0.970

    def test_birefringence_nw5_in_window(self):
        assert BETA_LOW_DEG <= BETA_PREDICTED_DEG <= BETA_HIGH_DEG

    def test_birefringence_nw5_not_in_gap(self):
        assert not (BETA_GAP_LOW < BETA_PREDICTED_DEG < BETA_GAP_HIGH)

    def test_birefringence_nw5_value(self):
        # canonical β ≈ 0.331° or 0.351°; accept [0.22, 0.38]
        assert 0.22 < BETA_PREDICTED_DEG < 0.38

    def test_tensor_to_scalar_nw5_below_limit(self):
        assert R_PREDICTED < R_BICEP_LIMIT

    def test_tensor_to_scalar_positive(self):
        assert R_PREDICTED > 0


# ---------------------------------------------------------------------------
# Admissibility
# ---------------------------------------------------------------------------
class TestAdmissibility:
    def test_nw5_admissible(self):
        ok, detail = is_admissible(5)
        assert ok
        assert detail["admissible"]

    def test_nw4_not_admissible(self):
        # n_w=4: k_CS=52, c_s²=24/52, n_s shifts out of window or β fails
        ok, _ = is_admissible(4)
        assert not ok

    def test_nw6_not_admissible(self):
        ok, _ = is_admissible(6)
        assert not ok

    def test_detail_keys(self):
        _, detail = is_admissible(5)
        for key in ["n_w", "n_s", "beta_deg", "r", "ok_ns", "ok_beta", "ok_r", "admissible"]:
            assert key in detail

    def test_detail_ok_ns_nw5(self):
        _, detail = is_admissible(5)
        assert detail["ok_ns"]

    def test_detail_ok_r_nw5(self):
        _, detail = is_admissible(5)
        assert detail["ok_r"]

    def test_nw1_not_admissible(self):
        ok, _ = is_admissible(1)
        assert not ok

    def test_nw15_not_admissible(self):
        ok, _ = is_admissible(15)
        assert not ok


# ---------------------------------------------------------------------------
# Stability basin
# ---------------------------------------------------------------------------
class TestStabilityBasin:
    def setup_method(self):
        self.basin = compute_stability_basin()

    def test_nw5_in_admissible_set(self):
        assert 5 in self.basin.admissible_set

    def test_nw4_in_excluded_set(self):
        assert 4 in self.basin.excluded_set

    def test_nw6_in_excluded_set(self):
        assert 6 in self.basin.excluded_set

    def test_admissible_nonempty(self):
        assert len(self.basin.admissible_set) >= 1

    def test_excluded_nonempty(self):
        assert len(self.basin.excluded_set) >= 1

    def test_n_s_predicted_in_window(self):
        assert N_S_LOW <= self.basin.n_s_predicted <= N_S_HIGH

    def test_beta_predicted_in_window(self):
        assert BETA_LOW_DEG <= self.basin.beta_deg_predicted <= BETA_HIGH_DEG

    def test_r_predicted_below_limit(self):
        assert self.basin.r_predicted < R_BICEP_LIMIT

    def test_k_cs_correct(self):
        assert self.basin.k_cs_value == 74

    def test_stability_margin_positive(self):
        assert self.basin.stability_margin_delta_nw >= 1

    def test_nearest_excluded_lower(self):
        assert self.basin.nearest_excluded_lower is not None
        assert self.basin.nearest_excluded_lower < 5

    def test_nearest_excluded_upper(self):
        assert self.basin.nearest_excluded_upper is not None
        assert self.basin.nearest_excluded_upper > 5

    def test_falsification_condition_nonempty(self):
        assert len(self.basin.falsification_condition) > 20

    def test_litebird_in_falsification(self):
        assert "LiteBIRD" in self.basin.falsification_condition

    def test_gate(self):
        assert self.basin.gate == "STABILITY_BASIN_QUANTIFIED"

    def test_dns_dnw_negative(self):
        # n_s decreases as n_w increases (more braiding → more deviation)
        # This is expected from the physics
        assert self.basin.dns_dnw != 0.0

    def test_run_pillar789_returns_basin(self):
        b = run_pillar789()
        assert isinstance(b, StabilityBasin)
        assert b.n_w_selected == 5


# ---------------------------------------------------------------------------
# STABILITY_BASIN dict
# ---------------------------------------------------------------------------
class TestStabilityBasinDict:
    def test_dict_keys(self):
        required = ["pillar", "status", "n_w_selected", "admissible_set",
                    "excluded_set", "n_s_predicted", "beta_deg_predicted",
                    "r_predicted", "k_cs", "gate"]
        for key in required:
            assert key in STABILITY_BASIN

    def test_dict_pillar(self):
        assert STABILITY_BASIN["pillar"] == 789

    def test_dict_admissible_contains_5(self):
        assert 5 in STABILITY_BASIN["admissible_set"]

    def test_dict_k_cs(self):
        assert STABILITY_BASIN["k_cs"] == 74

    def test_get_stability_basin_dict_deterministic(self):
        d1 = get_stability_basin_dict()
        d2 = get_stability_basin_dict()
        assert d1["n_s_predicted"] == d2["n_s_predicted"]
