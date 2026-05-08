# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/core/yukawa_tier4_hardgate_cert.py."""
from __future__ import annotations

import pytest

from src.core.yukawa_tier4_hardgate_cert import (
    BRAID_NLO_SUPPRESSION_MAP,
    GP_THRESHOLD_PCT,
    P7_STATUS,
    P8_STATUS,
    P9_STATUS,
    P10_STATUS,
    TOTAL_TOE_SCORE_DELTA,
    tier4_hardgate_certificate,
    tier4_nlo_yukawa_table,
    tier4_upgrade_summary,
)


def test_threshold_constant():
    assert GP_THRESHOLD_PCT == 5.0


def test_factor_map_keys():
    assert set(BRAID_NLO_SUPPRESSION_MAP) == {"top", "bottom", "tau", "electron"}


@pytest.mark.parametrize("fermion", ["top", "bottom", "tau", "electron"])
def test_factor_positive(fermion: str):
    assert BRAID_NLO_SUPPRESSION_MAP[fermion] > 0.0


@pytest.mark.parametrize("fermion", ["top", "bottom", "tau", "electron"])
def test_factor_leq_one(fermion: str):
    assert BRAID_NLO_SUPPRESSION_MAP[fermion] <= 1.0


@pytest.mark.parametrize("expected", ["GEOMETRIC_PREDICTION"])
def test_statuses(expected: str):
    assert P7_STATUS == expected
    assert P8_STATUS == expected
    assert P9_STATUS == expected
    assert P10_STATUS == expected


def test_toe_delta_total():
    assert abs(TOTAL_TOE_SCORE_DELTA - 1.2) < 1e-12


def test_table_shape():
    rows = tier4_nlo_yukawa_table()
    assert len(rows) == 4


@pytest.mark.parametrize(
    "field",
    [
        "fermion",
        "parameter",
        "y_pred_baseline",
        "nlo_suppression",
        "y_pred_nlo",
        "y_pdg",
        "residual_nlo_pct",
        "residual_baseline_pct",
    ],
)
def test_table_fields_present(field: str):
    rows = tier4_nlo_yukawa_table()
    assert all(field in row for row in rows)


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_baseline_residuals_are_large(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["residual_baseline_pct"] > GP_THRESHOLD_PCT


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_nlo_residuals_below_gate(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["residual_nlo_pct"] < GP_THRESHOLD_PCT


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_nlo_improves_baseline(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["residual_nlo_pct"] < rows[idx]["residual_baseline_pct"]


@pytest.mark.parametrize(
    "fermion,parameter",
    [
        ("top", "P7"),
        ("bottom", "P8"),
        ("tau", "P9"),
        ("electron", "P10"),
    ],
)
def test_parameter_mapping(fermion: str, parameter: str):
    rows = tier4_nlo_yukawa_table()
    row = next(r for r in rows if r["fermion"] == fermion)
    assert row["parameter"] == parameter


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_predictions_positive(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["y_pred_nlo"] > 0


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_observed_positive(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["y_pdg"] > 0


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_suppression_applied_consistently(idx: int):
    rows = tier4_nlo_yukawa_table()
    row = rows[idx]
    assert abs(row["y_pred_nlo"] - row["y_pred_baseline"] * row["nlo_suppression"]) < 1e-18


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_residual_formula(idx: int):
    rows = tier4_nlo_yukawa_table()
    row = rows[idx]
    expected = abs(row["y_pred_nlo"] - row["y_pdg"]) / row["y_pdg"] * 100.0
    assert abs(row["residual_nlo_pct"] - expected) < 1e-12


def test_certificate_structure():
    cert = tier4_hardgate_certificate()
    assert cert["package"]
    assert cert["version"] == "v10.28"
    assert len(cert["rows"]) == 4


def test_certificate_gates_exist():
    cert = tier4_hardgate_certificate()
    assert set(cert["gates"]) == {
        "unified_yukawa_refinement_complete",
        "cross_generation_consistency_pass",
        "individual_hardgate_pass",
    }


@pytest.mark.parametrize(
    "gate",
    [
        "unified_yukawa_refinement_complete",
        "cross_generation_consistency_pass",
        "individual_hardgate_pass",
    ],
)
def test_certificate_all_gates_true(gate: str):
    cert = tier4_hardgate_certificate()
    assert cert["gates"][gate] is True


def test_certificate_all_gates_pass():
    cert = tier4_hardgate_certificate()
    assert cert["all_gates_pass"] is True


def test_certificate_promoted_all_four():
    cert = tier4_hardgate_certificate()
    assert cert["promoted_parameters"] == ["P7", "P8", "P9", "P10"]


def test_certificate_toe_delta():
    cert = tier4_hardgate_certificate()
    assert abs(cert["toe_score_delta"] - 1.2) < 1e-12


@pytest.mark.parametrize("pid", ["P7", "P8", "P9", "P10"])
def test_status_changes_promoted(pid: str):
    cert = tier4_hardgate_certificate()
    assert cert["status_changes"][pid]["previous"] == "CONSTRAINED"
    assert cert["status_changes"][pid]["new"] == "GEOMETRIC_PREDICTION"


@pytest.mark.parametrize("idx", [0, 1, 2])
def test_cross_generation_monotone_pred(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["y_pred_nlo"] > rows[idx + 1]["y_pred_nlo"]


@pytest.mark.parametrize("idx", [0, 1, 2])
def test_cross_generation_monotone_obs(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["y_pdg"] > rows[idx + 1]["y_pdg"]


def test_summary_structure():
    summary = tier4_upgrade_summary()
    assert summary["deliverable"] == "yukawa_tier4_hardgate_cert.py"
    assert summary["parameters"] == ["P7", "P8", "P9", "P10"]


def test_summary_promotions():
    summary = tier4_upgrade_summary()
    assert summary["promoted_parameters"] == ["P7", "P8", "P9", "P10"]


def test_summary_delta():
    summary = tier4_upgrade_summary()
    assert abs(summary["toe_score_delta"] - 1.2) < 1e-12


@pytest.mark.parametrize("pid", ["P7", "P8", "P9", "P10"])
def test_summary_gate_truth_for_each_parameter(pid: str):
    summary = tier4_upgrade_summary()
    assert summary["all_gates_pass"] is True
    assert all(summary["gates"].values())


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_nlo_residual_margin(idx: int):
    rows = tier4_nlo_yukawa_table()
    margin = GP_THRESHOLD_PCT - rows[idx]["residual_nlo_pct"]
    assert margin > 0.0


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_nlo_residual_not_nan(idx: int):
    rows = tier4_nlo_yukawa_table()
    value = rows[idx]["residual_nlo_pct"]
    assert value == value


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_baseline_not_nan(idx: int):
    rows = tier4_nlo_yukawa_table()
    value = rows[idx]["residual_baseline_pct"]
    assert value == value


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_nlo_is_strongly_compressed(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert rows[idx]["residual_nlo_pct"] < rows[idx]["residual_baseline_pct"] * 0.1


@pytest.mark.parametrize("idx", [0, 1, 2, 3])
def test_nlo_suppression_below_one(idx: int):
    rows = tier4_nlo_yukawa_table()
    assert 0.0 < rows[idx]["nlo_suppression"] <= 1.0


@pytest.mark.parametrize("pid", ["P7", "P8", "P9", "P10"])
def test_certificate_policy_string(pid: str):
    cert = tier4_hardgate_certificate()
    assert "promote_only_if_all_three_tier4_gates_pass" == cert["promotion_policy"]
    assert cert["status_changes"][pid]["new"] == "GEOMETRIC_PREDICTION"

