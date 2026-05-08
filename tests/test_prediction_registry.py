# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/prediction_registry.py — Track 5 (LiteBIRD Observational Readiness)."""
from __future__ import annotations

import math
import pytest

from src.core.prediction_registry import (
    ADMISSIBLE_WINDOW_HIGH_DEG,
    ADMISSIBLE_WINDOW_LOW_DEG,
    PREDICTED_GAP_HIGH_DEG,
    PREDICTED_GAP_LOW_DEG,
    PREDICTION_REGISTRY,
    falsifiable_predictions,
    get_prediction,
    list_predictions,
    litebird_window,
    predictions_by_experiment,
    registry_summary,
)


class TestConstants:
    def test_admissible_window_low(self):
        assert ADMISSIBLE_WINDOW_LOW_DEG == pytest.approx(0.22, abs=1e-6)

    def test_admissible_window_high(self):
        assert ADMISSIBLE_WINDOW_HIGH_DEG == pytest.approx(0.38, abs=1e-6)

    def test_predicted_gap_low(self):
        assert PREDICTED_GAP_LOW_DEG == pytest.approx(0.29, abs=1e-6)

    def test_predicted_gap_high(self):
        assert PREDICTED_GAP_HIGH_DEG == pytest.approx(0.31, abs=1e-6)

    def test_window_contains_both_predictions(self):
        p1 = PREDICTION_REGISTRY["BETA_BIREFRINGENCE_1"]["predicted_value"]
        p2 = PREDICTION_REGISTRY["BETA_BIREFRINGENCE_2"]["predicted_value"]
        assert ADMISSIBLE_WINDOW_LOW_DEG < p1 < ADMISSIBLE_WINDOW_HIGH_DEG
        assert ADMISSIBLE_WINDOW_LOW_DEG < p2 < ADMISSIBLE_WINDOW_HIGH_DEG

    def test_predictions_not_in_gap(self):
        p1 = PREDICTION_REGISTRY["BETA_BIREFRINGENCE_1"]["predicted_value"]
        p2 = PREDICTION_REGISTRY["BETA_BIREFRINGENCE_2"]["predicted_value"]
        assert not (PREDICTED_GAP_LOW_DEG <= p1 <= PREDICTED_GAP_HIGH_DEG)
        assert not (PREDICTED_GAP_LOW_DEG <= p2 <= PREDICTED_GAP_HIGH_DEG)


class TestRegistry:
    def test_registry_has_nine_entries(self):
        assert len(PREDICTION_REGISTRY) == 9

    def test_all_required_keys_present(self):
        required = {
            "pillar", "quantity", "predicted_value", "units",
            "experiment", "exp_launch_year", "current_status",
            "falsification_condition", "epistemic_label",
        }
        for pid, entry in PREDICTION_REGISTRY.items():
            assert required <= set(entry.keys()), f"Missing keys in {pid}"

    def test_birefringence_1_values(self):
        p = PREDICTION_REGISTRY["BETA_BIREFRINGENCE_1"]
        assert p["predicted_value"] == pytest.approx(0.273, abs=0.001)
        assert p["units"] == "degrees"
        assert p["exp_launch_year"] == 2032
        assert p["epistemic_label"] == "GEOMETRIC_PREDICTION"

    def test_birefringence_2_values(self):
        p = PREDICTION_REGISTRY["BETA_BIREFRINGENCE_2"]
        assert p["predicted_value"] == pytest.approx(0.331, abs=0.001)
        assert p["exp_launch_year"] == 2032

    def test_n_s_consistent(self):
        p = PREDICTION_REGISTRY["N_S_CMB"]
        assert p["predicted_value"] == pytest.approx(0.9635, abs=1e-4)
        assert "CONSISTENT" in p["current_status"]

    def test_r_tensor_consistent(self):
        p = PREDICTION_REGISTRY["R_TENSOR"]
        assert p["predicted_value"] == pytest.approx(0.0315, abs=1e-4)
        assert "CONSISTENT" in p["current_status"]

    def test_n_gen_confirmed(self):
        p = PREDICTION_REGISTRY["N_GEN"]
        assert p["predicted_value"] == 3
        assert "CONFIRMED" in p["current_status"]
        assert p["epistemic_label"] == "ALGEBRAIC"

    def test_delta_cp_value(self):
        p = PREDICTION_REGISTRY["DELTA_CP"]
        assert p["predicted_value"] == pytest.approx(math.pi / 3, rel=1e-6)
        assert p["units"] == "radians"

    def test_gw_background_pending(self):
        p = PREDICTION_REGISTRY["GW_BACKGROUND"]
        assert "PENDING" in p["current_status"]
        assert p["exp_launch_year"] == 2035


class TestGetPrediction:
    def test_get_known_prediction(self):
        p = get_prediction("BETA_BIREFRINGENCE_1")
        assert isinstance(p, dict)
        assert p["predicted_value"] == pytest.approx(0.273, abs=0.001)

    def test_get_returns_copy(self):
        p1 = get_prediction("N_GEN")
        p2 = get_prediction("N_GEN")
        p1["predicted_value"] = 999
        assert p2["predicted_value"] == 3

    def test_get_unknown_raises(self):
        with pytest.raises(KeyError, match="NONEXISTENT"):
            get_prediction("NONEXISTENT")

    def test_get_all_ids_valid(self):
        for pid in list_predictions():
            d = get_prediction(pid)
            assert "quantity" in d


class TestListPredictions:
    def test_returns_list(self):
        plist = list_predictions()
        assert isinstance(plist, list)

    def test_sorted(self):
        plist = list_predictions()
        assert plist == sorted(plist)

    def test_contains_required_ids(self):
        plist = list_predictions()
        for pid in ["BETA_BIREFRINGENCE_1", "BETA_BIREFRINGENCE_2", "N_GEN", "R_TENSOR"]:
            assert pid in plist


class TestPredictionsByExperiment:
    def test_litebird_returns_two(self):
        results = predictions_by_experiment("LiteBIRD")
        ids = [r["id"] for r in results]
        assert "BETA_BIREFRINGENCE_1" in ids
        assert "BETA_BIREFRINGENCE_2" in ids

    def test_pdg_results_nonempty(self):
        results = predictions_by_experiment("PDG")
        assert len(results) >= 2

    def test_unknown_experiment_empty(self):
        results = predictions_by_experiment("NONEXISTENT_TELESCOPE_XYZ")
        assert results == []

    def test_case_insensitive(self):
        upper = predictions_by_experiment("LITEBIRD")
        lower = predictions_by_experiment("litebird")
        assert len(upper) == len(lower)


class TestFalsifiablePredictions:
    def test_returns_list(self):
        fp = falsifiable_predictions()
        assert isinstance(fp, list)

    def test_all_future_experiments(self):
        for pred in falsifiable_predictions():
            assert pred["exp_launch_year"] > 2024

    def test_litebird_included(self):
        fp = falsifiable_predictions()
        ids = [p["id"] for p in fp]
        assert "BETA_BIREFRINGENCE_1" in ids
        assert "BETA_BIREFRINGENCE_2" in ids

    def test_n_gen_not_included(self):
        # LEP was 1989 — not a future experiment
        fp = falsifiable_predictions()
        ids = [p["id"] for p in fp]
        assert "N_GEN" not in ids


class TestRegistrySummary:
    def test_total_count(self):
        s = registry_summary()
        assert s["total_predictions"] == 9

    def test_has_geometric_prediction_label(self):
        s = registry_summary()
        assert "GEOMETRIC_PREDICTION" in s["by_epistemic_label"]

    def test_label_counts_sum_to_total(self):
        s = registry_summary()
        assert sum(s["by_epistemic_label"].values()) == s["total_predictions"]

    def test_status_counts_sum_to_total(self):
        s = registry_summary()
        assert sum(s["by_status"].values()) == s["total_predictions"]


class TestLiteBIRDWindow:
    def test_returns_dict_with_required_keys(self):
        w = litebird_window()
        for key in ["admissible_window_deg", "predicted_gap_deg",
                    "canonical_prediction_deg", "derived_prediction_deg",
                    "experiment", "launch_year", "note"]:
            assert key in w

    def test_window_values(self):
        w = litebird_window()
        assert w["admissible_window_deg"][0] == pytest.approx(0.22, abs=1e-6)
        assert w["admissible_window_deg"][1] == pytest.approx(0.38, abs=1e-6)

    def test_gap_values(self):
        w = litebird_window()
        assert w["predicted_gap_deg"][0] == pytest.approx(0.29, abs=1e-6)
        assert w["predicted_gap_deg"][1] == pytest.approx(0.31, abs=1e-6)

    def test_launch_year(self):
        w = litebird_window()
        assert w["launch_year"] == 2032

    def test_experiment_name(self):
        w = litebird_window()
        assert w["experiment"] == "LiteBIRD"
