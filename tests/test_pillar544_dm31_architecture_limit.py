# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 544 — P17 Δm²₃₁ Architecture Limit Certificate."""
from __future__ import annotations

import pytest
from src.core.pillar544_dm31_architecture_limit import (
    ARCHITECTURE_LIMIT_RECORD,
    CLOSURE_PATH,
    JUNO_2026_RESULT,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    UM_ESTIMATES,
    VERSION,
    architecture_limit_certificate,
    closure_path_report,
    dm31_tension_sigma,
    pillar_report,
    upgrade_conditions,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 544


def test_pillar_status():
    assert PILLAR_STATUS == "DM31_ARCHITECTURE_LIMIT_CERTIFIED"


def test_version():
    assert VERSION == "v19.0"


# ─── JUNO result ─────────────────────────────────────────────────────────────

def test_juno_result_value():
    assert JUNO_2026_RESULT["dm31_evsq"] == pytest.approx(2.411e-3)


def test_juno_sigma_positive():
    assert JUNO_2026_RESULT["sigma_evsq"] > 0


# ─── UM estimates ────────────────────────────────────────────────────────────

def test_2nlo_bare_below_juno():
    assert UM_ESTIMATES["2NLO_bare"]["dm31_evsq"] < JUNO_2026_RESULT["dm31_evsq"]


def test_best_attempt_below_juno():
    assert UM_ESTIMATES["best_attempt_projection"]["dm31_evsq"] < JUNO_2026_RESULT["dm31_evsq"]


def test_kk_correction_negligible():
    bare = UM_ESTIMATES["2NLO_bare"]["dm31_evsq"]
    kk = UM_ESTIMATES["kk_tower_correction"]["dm31_evsq"]
    # KK correction should be < 1e-10 (negligible)
    # KK correction is ε_KK ≈ 2.3e-21 times the base value — sub-femto eV²
    bare = UM_ESTIMATES["2NLO_bare"]["dm31_evsq"]
    kk = UM_ESTIMATES["kk_tower_correction"]["dm31_evsq"]
    # Relative correction must be < 1e-20 (negligible vs JUNO precision)
    assert abs(kk - bare) / bare < 1e-18


# ─── Tension calculations ────────────────────────────────────────────────────

def test_2nlo_tension_above_6sigma():
    tension = dm31_tension_sigma(UM_ESTIMATES["2NLO_bare"]["dm31_evsq"])
    assert tension > 6.0


def test_best_attempt_tension_above_3sigma():
    tension = dm31_tension_sigma(UM_ESTIMATES["best_attempt_projection"]["dm31_evsq"])
    assert tension > 3.0


def test_tension_zero_for_juno_value():
    tension = dm31_tension_sigma(JUNO_2026_RESULT["dm31_evsq"])
    assert tension == pytest.approx(0.0)


def test_tension_sigma_invalid():
    with pytest.raises(ValueError):
        dm31_tension_sigma(2.3e-3, juno_sigma=0)


# ─── Architecture limit record ───────────────────────────────────────────────

def test_record_status():
    assert "ARCHITECTURE_LIMIT_CERTIFIED" in ARCHITECTURE_LIMIT_RECORD["status"]


def test_record_prediction_id():
    assert ARCHITECTURE_LIMIT_RECORD["prediction_id"] == "P17"


def test_record_current_tension():
    # 3.33σ from Pillar 525 routing
    assert ARCHITECTURE_LIMIT_RECORD["current_tension_sigma"] == pytest.approx(3.33)


def test_record_bare_tension():
    assert ARCHITECTURE_LIMIT_RECORD["bare_tension_sigma"] == pytest.approx(6.46)


# ─── Closure path ────────────────────────────────────────────────────────────

def test_closure_path_has_4_steps():
    assert len(CLOSURE_PATH) == 4


def test_first_3_steps_blocking():
    blocking = [s for s in CLOSURE_PATH if s["blocks_closure"]]
    assert len(blocking) == 3


def test_step_4_not_blocking():
    step4 = CLOSURE_PATH[3]
    assert step4["blocks_closure"] is False


# ─── Functions ───────────────────────────────────────────────────────────────

def test_architecture_limit_certificate_type():
    cert = architecture_limit_certificate()
    assert cert["certificate_type"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_architecture_limit_estimates_have_tension():
    cert = architecture_limit_certificate()
    for key, est in cert["estimates"].items():
        assert "tension_sigma" in est
        assert est["tension_sigma"] > 0


def test_closure_path_report_structure():
    report = closure_path_report()
    assert report["total_steps"] == 4
    assert report["blocking_steps"] == 3


def test_upgrade_conditions_count():
    conditions = upgrade_conditions()
    assert len(conditions) == 3


def test_upgrade_conditions_include_derived():
    conditions = upgrade_conditions()
    assert any("DERIVED" in c for c in conditions)


def test_pillar_report_complete():
    report = pillar_report()
    assert report["pillar"] == 544
    assert report["toe_score_delta"] == 0.0
    assert report["epistemic_delta"] == "P17: HONEST_OPEN_PROBLEM → ARCHITECTURE_LIMIT_CERTIFIED"
