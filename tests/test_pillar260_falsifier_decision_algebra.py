# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

from src.core.pillar260_falsifier_decision_algebra import (
    ADJACENCY_TRACK_LABEL,
    cmbs4_secondary_decision,
    desi_falsifier_decision,
    juno_falsifier_decision,
    litebird_boundary_margins,
    litebird_decision,
    pillar260_falsifier_decision_report,
)


def test_litebird_boundary_margins_shape():
    margins = litebird_boundary_margins(0.331)
    assert "to_mode_1_sigma" in margins
    assert margins["to_mode_1_sigma"] == 0.0


def test_litebird_decision_primary_and_gap():
    assert litebird_decision(0.331)["verdict"] == "PRIMARY_SECTOR_CONFIRMED"
    assert litebird_decision(0.300, sigma_beta=0.002)["verdict"] == "FALSIFIED_GAP"


def test_desi_decision_warning_or_worse():
    row = desi_falsifier_decision()
    assert row["verdict"] in {"PASS", "WARNING", "FALSIFIED"}
    assert "margin_to_falsification_sigma" in row


def test_juno_decision_flags_high_precision_risk():
    row = juno_falsifier_decision(2.453e-3)
    assert row["verdict"] in {"WARNING", "FALSIFIED"}
    assert row["tension_sigma"] > 0.0


def test_cmbs4_secondary_decision_shape():
    row = cmbs4_secondary_decision(r_obs=0.0315, r_sigma=0.005, ns_obs=0.9635, ns_sigma=0.001)
    assert row["r"]["verdict"] in {"PASS", "FALSIFIED"}
    assert row["n_s"]["verdict"] in {"PASS", "FALSIFIED_LOW", "FALSIFIED_HIGH"}


def test_pillar260_report_shape():
    report = pillar260_falsifier_decision_report()
    assert report["pillar"] == 260
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["status"] == "DECISION_BOUNDARIES_LOCKED"
    assert report["litebird_examples"]["primary_mode"]["verdict"] == "PRIMARY_SECTOR_CONFIRMED"
