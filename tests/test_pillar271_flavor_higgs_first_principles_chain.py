# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 271 — unified flavor + Higgs first-principles chain."""
from __future__ import annotations

from src.core.pillar271_flavor_higgs_first_principles_chain import (
    ADJACENCY_TRACK_LABEL,
    derived_top_yukawa_prediction,
    flavor_higgs_first_principles_report,
    higgs_mass_from_derived_top_yukawa,
)


def test_top_yukawa_prediction_is_near_unity():
    top = derived_top_yukawa_prediction()
    assert 0.8 < top["y_t_pred"] < 1.1
    assert top["residual_pct"] < 5.0


def test_higgs_from_derived_top_yukawa_is_within_gate():
    higgs = higgs_mass_from_derived_top_yukawa()
    assert higgs["status"] == "PASS"
    assert higgs["residual_pct"] < 5.0


def test_unified_report_passes():
    report = flavor_higgs_first_principles_report()
    assert report["adjacency_label"] == ADJACENCY_TRACK_LABEL
    assert report["all_pass"] is True
    assert report["status"] == "UNIFIED_FLAVOR_HIGGS_CHAIN_EXECUTABLE"
