# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 236 — Critique Hardening Engine."""

from __future__ import annotations

import math

import pytest

from src.core.pillar236_critique_hardening_engine import (
    N_W,
    K_CS,
    C_S,
    NS_UM,
    R_UM_BRAIDED,
    BETA_UM_PRIMARY_DEG,
    BETA_UM_SHADOW_DEG,
    WA_UM,
    ExternalConstraint,
    __provenance__,
    source_quality_ladder,
    default_external_constraints,
    default_predictions,
    evaluate_against_constraint,
    preregistered_falsification_table,
    critique_hardening_ledger,
    ledger_summary,
    monte_carlo_critique_stability,
    pillar236_critique_hardening_report,
)


def test_provenance_and_constants():
    assert __provenance__["pillar"] == 236
    assert "ADJACENT RESEARCH TRACK" in __provenance__["status"]
    assert N_W == 5
    assert K_CS == 74
    assert math.isclose(C_S, 12.0 / 37.0, rel_tol=0, abs_tol=1e-15)


def test_predictions_basics():
    p = default_predictions()
    assert p["n_s"] == NS_UM
    assert p["r"] == R_UM_BRAIDED
    assert p["beta_primary"] == BETA_UM_PRIMARY_DEG
    assert p["beta_shadow"] == BETA_UM_SHADOW_DEG
    assert p["wa"] == WA_UM


def test_source_quality_ladder_structure_and_order():
    ladder = source_quality_ladder()
    assert set(ladder) == {"T1", "T2", "T3", "T4", "T5"}
    ranks = [ladder[k]["rank"] for k in ("T1", "T2", "T3", "T4", "T5")]
    assert ranks == [1, 2, 3, 4, 5]


def test_default_external_constraints_keys_and_urls():
    c = default_external_constraints()
    for key in ("n_s", "r", "beta", "w0", "wa", "litebird_beta_sigma"):
        assert key in c
    assert c["n_s"].source_url.startswith("https://")


def test_symmetric_constraint_evaluation_consistent():
    c = ExternalConstraint(observable="x", observed=1.0, sigma=0.1)
    row = evaluate_against_constraint(1.02, c)
    assert row["verdict"] == "CONSISTENT"
    assert row["sigma_distance"] < 1.0


def test_symmetric_constraint_high_tension_and_falsified():
    c = ExternalConstraint(observable="x", observed=0.0, sigma=1.0)
    high = evaluate_against_constraint(2.2, c)
    bad = evaluate_against_constraint(3.4, c)
    assert high["verdict"] == "HIGH_TENSION"
    assert bad["verdict"] == "FALSIFIED"


def test_upper_bound_evaluation():
    c = ExternalConstraint(observable="r", observed=0.0, upper_bound=0.05)
    ok = evaluate_against_constraint(0.03, c)
    bad = evaluate_against_constraint(0.07, c)
    assert ok["verdict"] == "CONSISTENT"
    assert bad["verdict"] == "FALSIFIED"
    assert ok["margin"] > 0


def test_invalid_constraint_rejected():
    with pytest.raises(ValueError):
        evaluate_against_constraint(1.0, ExternalConstraint(observable="x", observed=0.0, sigma=0.0))
    with pytest.raises(ValueError):
        evaluate_against_constraint(1.0, ExternalConstraint(observable="x", observed=0.0, upper_bound=-1.0))


def test_preregistered_falsification_table_shape():
    rows = preregistered_falsification_table()
    assert len(rows) >= 4
    ids = {r["id"] for r in rows}
    assert len(ids) == len(rows)
    for row in rows:
        assert "kill_condition" in row
        assert "decision_rule" in row


def test_critique_hardening_ledger_contains_expected_claims():
    rows = critique_hardening_ledger()
    claim_ids = {r["claim_id"] for r in rows}
    assert {"P2", "P3", "P1-primary", "P1-shadow", "P4-w0", "P4-wa"} <= claim_ids


def test_ledger_expected_current_severity_profile():
    rows = critique_hardening_ledger()
    by_id = {r["claim_id"]: r for r in rows}
    assert by_id["P2"]["check"]["verdict"] in {"CONSISTENT", "TENSION"}
    assert by_id["P3"]["check"]["verdict"] == "CONSISTENT"
    assert by_id["P4-wa"]["check"]["verdict"] in {"HIGH_TENSION", "TENSION", "FALSIFIED"}


def test_ledger_summary_shape_and_counts():
    summary = ledger_summary()
    assert summary["n_checks"] == 6
    assert "counts" in summary
    assert sum(summary["counts"].values()) == 6
    assert summary["max_severity"] in {"CONSISTENT", "TENSION", "HIGH_TENSION", "FALSIFIED", "INFORMATIONAL"}


def test_monte_carlo_stability_reproducible_with_seed():
    a = monte_carlo_critique_stability(samples=50, seed=99)
    b = monte_carlo_critique_stability(samples=50, seed=99)
    assert a == b


def test_monte_carlo_invalid_samples_raises():
    with pytest.raises(ValueError):
        monte_carlo_critique_stability(samples=0)


def test_monte_carlo_contains_claims_and_bounded_fractions():
    out = monte_carlo_critique_stability(samples=25, seed=7)
    assert out["samples"] == 25
    assert set(out["per_claim"]) == {"P2", "P1-primary", "P1-shadow", "P4-w0", "P4-wa"}
    for row in out["per_claim"].values():
        assert 0.0 <= row["dominant_fraction"] <= 1.0
        assert row["entropy"] >= 0.0


def test_integrated_report_sections():
    report = pillar236_critique_hardening_report(samples=20, seed=4)
    for key in (
        "pillar",
        "status",
        "source_quality_ladder",
        "external_validation_ledger",
        "ledger_summary",
        "preregistered_falsifiers",
        "stability_simulation",
        "falsification_condition",
    ):
        assert key in report
    assert report["pillar"] == 236
    assert len(report["external_validation_ledger"]) == 6
