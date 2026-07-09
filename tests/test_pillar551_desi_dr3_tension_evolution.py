# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 551 — DESI DR3 Tension Evolution Model."""
from __future__ import annotations

import math
import pytest
from src.core.pillar551_desi_dr3_tension_evolution import (
    DR2_TENSION,
    DR3_PROJECTION,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    SURVEY_TIMELINE,
    TRIGGER_CONDITIONS,
    VERSION,
    decision_day_template,
    dr3_central_projection,
    dr3_scatter_band,
    extension_spec_trigger,
    pillar_report,
    route_tension,
    tension_at_dataset_size,
    tension_evolution_table,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 551


def test_pillar_status():
    assert "DESI_DR3" in PILLAR_STATUS
    assert "TENSION_EVOLUTION" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.1"


# ─── DR2 baseline ────────────────────────────────────────────────────────────

def test_dr2_tension_canonical():
    assert DR2_TENSION["tension_sigma_2d_cpl"] == pytest.approx(2.30)


def test_dr2_effective_years():
    assert DR2_TENSION["effective_years"] == pytest.approx(2.0)


def test_dr2_verdict_not_falsified():
    assert "NOT FALSIFIED" in DR2_TENSION["verdict"]


def test_dr2_wa_central_negative():
    assert DR2_TENSION["wa_central"] < 0


# ─── DR3 projection ──────────────────────────────────────────────────────────

def test_dr3_sigma_central_greater_than_dr2():
    assert DR3_PROJECTION["sigma_central"] > DR2_TENSION["tension_sigma_2d_cpl"]


def test_dr3_sigma_central_formula():
    sigma_dr2 = DR2_TENSION["tension_sigma_2d_cpl"]
    years_dr2 = DR2_TENSION["effective_years"]
    years_dr3 = DR3_PROJECTION["effective_years"]
    expected = sigma_dr2 * math.sqrt(years_dr3 / years_dr2)
    assert DR3_PROJECTION["sigma_central"] == pytest.approx(expected)


def test_dr3_sigma_band():
    assert DR3_PROJECTION["sigma_low"] < DR3_PROJECTION["sigma_central"]
    assert DR3_PROJECTION["sigma_high"] > DR3_PROJECTION["sigma_central"]


def test_dr3_verdict_central():
    # At 2.30σ × √(5/2) ≈ 3.64σ, central verdict should be FALSIFIED
    assert DR3_PROJECTION["verdict_central"] in ("FALSIFIED", "HIGH_TENSION")


# ─── Trigger conditions ──────────────────────────────────────────────────────

def test_falsified_threshold():
    assert TRIGGER_CONDITIONS["falsified_threshold"] == pytest.approx(3.0)


def test_high_tension_threshold():
    assert TRIGGER_CONDITIONS["high_tension_threshold"] == pytest.approx(2.0)


def test_trigger_conditions_have_actions():
    for key in ["falsified_action", "high_tension_action", "pass_action"]:
        assert key in TRIGGER_CONDITIONS
        assert len(TRIGGER_CONDITIONS[key]) > 20


# ─── tension_at_dataset_size ─────────────────────────────────────────────────

def test_tension_at_dr2_equals_dr2():
    sigma = tension_at_dataset_size(2.0, sigma_dr2=2.30, years_dr2=2.0)
    assert sigma == pytest.approx(2.30)


def test_tension_scales_up_with_more_data():
    sigma_2yr = tension_at_dataset_size(2.0, sigma_dr2=2.30, years_dr2=2.0)
    sigma_5yr = tension_at_dataset_size(5.0, sigma_dr2=2.30, years_dr2=2.0)
    assert sigma_5yr > sigma_2yr


def test_tension_scaling_formula():
    sigma = tension_at_dataset_size(5.0, sigma_dr2=2.30, years_dr2=2.0)
    expected = 2.30 * math.sqrt(5.0 / 2.0)
    assert sigma == pytest.approx(expected)


def test_tension_invalid_years():
    with pytest.raises(ValueError):
        tension_at_dataset_size(0.0)


def test_tension_invalid_negative():
    with pytest.raises(ValueError):
        tension_at_dataset_size(-1.0)


# ─── dr3_central_projection ──────────────────────────────────────────────────

def test_dr3_central_projection_keys():
    proj = dr3_central_projection()
    for key in ["sigma_dr2", "sigma_dr3_projected", "effective_years_dr3", "scaling_factor"]:
        assert key in proj


def test_dr3_central_scaling_factor():
    proj = dr3_central_projection()
    expected = math.sqrt(5.0 / 2.0)
    assert proj["scaling_factor"] == pytest.approx(expected)


def test_dr3_central_sigma_consistent():
    proj = dr3_central_projection()
    assert proj["sigma_dr3_projected"] == pytest.approx(
        proj["sigma_dr2"] * proj["scaling_factor"]
    )


# ─── dr3_scatter_band ────────────────────────────────────────────────────────

def test_scatter_band_keys():
    band = dr3_scatter_band()
    for key in ["sigma_central", "sigma_low", "sigma_high", "coverage"]:
        assert key in band


def test_scatter_band_ordering():
    band = dr3_scatter_band()
    assert band["sigma_low"] < band["sigma_central"] < band["sigma_high"]


# ─── route_tension ───────────────────────────────────────────────────────────

def test_route_falsified():
    result = route_tension(3.5)
    assert result["verdict"] == "FALSIFIED"


def test_route_high_tension():
    result = route_tension(2.30)
    assert result["verdict"] == "HIGH_TENSION"


def test_route_pass():
    result = route_tension(1.5)
    assert result["verdict"] == "PASS"


def test_route_exactly_at_threshold():
    result_at_3 = route_tension(3.0)
    assert result_at_3["verdict"] == "FALSIFIED"

    result_at_2 = route_tension(2.0)
    assert result_at_2["verdict"] == "HIGH_TENSION"


def test_route_returns_action():
    result = route_tension(3.5)
    assert len(result["action"]) > 20


# ─── tension_evolution_table ─────────────────────────────────────────────────

def test_evolution_table_releases():
    table = tension_evolution_table()
    releases = [e["release"] for e in table]
    assert "DR2" in releases
    assert "DR3" in releases


def test_evolution_table_monotone_sigma():
    table = tension_evolution_table()
    sigmas = [e["sigma_projected"] for e in table]
    # Sigma should increase monotonically with dataset size
    for i in range(1, len(sigmas)):
        assert sigmas[i] >= sigmas[i - 1]


def test_evolution_table_verdicts_present():
    table = tension_evolution_table()
    for entry in table:
        assert entry["verdict"] in ("PASS", "HIGH_TENSION", "FALSIFIED")


def test_evolution_dr2_verdict():
    table = tension_evolution_table()
    dr2 = next(e for e in table if e["release"] == "DR2")
    assert dr2["verdict"] == "HIGH_TENSION"


# ─── decision_day_template ───────────────────────────────────────────────────

def test_decision_day_keys():
    tmpl = decision_day_template()
    for key in ["trigger", "first_action", "compute", "route",
                "publish_to", "if_falsified", "if_high_tension", "if_pass",
                "preregistration_hash"]:
        assert key in tmpl


def test_decision_day_publish_to_nonempty():
    tmpl = decision_day_template()
    assert len(tmpl["publish_to"]) >= 3


def test_decision_day_preregistration():
    tmpl = decision_day_template()
    assert "Pillar 543" in tmpl["preregistration_hash"]


# ─── extension_spec_trigger ──────────────────────────────────────────────────

def test_extension_spec_trigger_keys():
    trigger = extension_spec_trigger()
    for key in ["trigger_condition", "extension_module", "not_triggered_yet"]:
        assert key in trigger


def test_extension_not_triggered():
    trigger = extension_spec_trigger()
    assert trigger["not_triggered_yet"] is True


def test_extension_current_tension():
    trigger = extension_spec_trigger()
    assert trigger["current_tension"] == pytest.approx(2.30)


def test_extension_toe_impact_described():
    trigger = extension_spec_trigger()
    assert "T1" in trigger["toe_impact_if_triggered"] or "wₐ" in trigger["toe_impact_if_triggered"]


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 551
    assert report["adjacent_track"] is True
    assert report["toe_score_delta"] == pytest.approx(0.0)
    assert report["parent_pillar"] == 543
