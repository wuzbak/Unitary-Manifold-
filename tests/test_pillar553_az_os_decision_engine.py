# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 553 — AZ-OS φ-Debt Decision Engine."""
from __future__ import annotations

import math
import pytest
from az_os.phi_decision_engine import (
    PHI_DECISION_CONSTANTS,
    DecisionLevel,
    PhiDebtSignal,
    PhiDecisionEngine,
    SchedulingDecision,
    equilibrium_check,
    kk_level_to_decision_level,
    phi_debt_to_priority,
)
from src.core.pillar553_az_os_decision_engine import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    VERSION,
    pillar_report,
)


# ─── Identity ────────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 553


def test_pillar_status():
    assert "DECISION_ENGINE" in PILLAR_STATUS


def test_version():
    assert VERSION == "v19.1"


# ─── Constants ───────────────────────────────────────────────────────────────

def test_xi_c():
    assert PHI_DECISION_CONSTANTS["xi_c"] == pytest.approx(35 / 74)


def test_phi0():
    assert PHI_DECISION_CONSTANTS["phi0"] == pytest.approx(5 * 2 * math.pi)


def test_kk_levels():
    assert PHI_DECISION_CONSTANTS["kk_levels"] == 5


def test_hils_alert_sigma():
    assert PHI_DECISION_CONSTANTS["hils_alert_sigma"] == pytest.approx(2.0)


# ─── DecisionLevel ───────────────────────────────────────────────────────────

def test_decision_level_values():
    assert DecisionLevel.KERNEL == 0
    assert DecisionLevel.SYSTEM == 1
    assert DecisionLevel.SERVICE == 2
    assert DecisionLevel.USER == 3
    assert DecisionLevel.GUEST == 4


def test_decision_level_names():
    assert DecisionLevel.name(0) == "KERNEL"
    assert DecisionLevel.name(4) == "GUEST"


# ─── PhiDebtSignal ───────────────────────────────────────────────────────────

def test_phi_debt_signal_normal():
    sig = PhiDebtSignal(
        agent_id="test-agent",
        phi_debt=0.01,
        radion_tension=0.5,
        kk_level=2,
    )
    assert sig.debt_category() == "NORMAL"
    assert sig.hils_alert_required() is False


def test_phi_debt_signal_elevated():
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = PhiDebtSignal(
        agent_id="test-agent",
        phi_debt=0.2 * xi_c,
        radion_tension=1.0,
        kk_level=3,
    )
    assert sig.debt_category() == "ELEVATED"


def test_phi_debt_signal_high():
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = PhiDebtSignal(
        agent_id="test-agent",
        phi_debt=0.7 * xi_c,
        radion_tension=1.5,
        kk_level=3,
    )
    assert sig.debt_category() == "HIGH"


def test_phi_debt_signal_critical():
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = PhiDebtSignal(
        agent_id="test-agent",
        phi_debt=1.5 * xi_c,
        radion_tension=2.5,
        kk_level=3,
    )
    assert sig.debt_category() == "CRITICAL"
    assert sig.hils_alert_required() is True


def test_phi_debt_signal_hils_alert_at_2sigma():
    sig = PhiDebtSignal(
        agent_id="test-agent",
        phi_debt=0.01,
        radion_tension=2.0,
        kk_level=2,
    )
    assert sig.hils_alert_required() is True


def test_phi_debt_signal_no_hils_below_2sigma():
    sig = PhiDebtSignal(
        agent_id="test-agent",
        phi_debt=0.01,
        radion_tension=1.9,
        kk_level=2,
    )
    assert sig.hils_alert_required() is False


def test_debt_fraction():
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = PhiDebtSignal("a", phi_debt=xi_c / 2, radion_tension=0.5, kk_level=2)
    assert sig.debt_fraction() == pytest.approx(0.5)


# ─── kk_level_to_decision_level ──────────────────────────────────────────────

def test_kk_level_clamped_high():
    assert kk_level_to_decision_level(10) == 4


def test_kk_level_clamped_low():
    assert kk_level_to_decision_level(-1) == 0


def test_kk_level_identity():
    for lv in range(5):
        assert kk_level_to_decision_level(lv) == lv


# ─── phi_debt_to_priority ────────────────────────────────────────────────────

def test_phi_debt_to_priority_normal():
    priority, cat = phi_debt_to_priority(0.001)
    assert cat == "NORMAL"
    assert priority == 10


def test_phi_debt_to_priority_critical():
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    priority, cat = phi_debt_to_priority(2.0 * xi_c)
    assert cat == "CRITICAL"
    assert priority > 50


def test_phi_debt_priority_order():
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    p_normal, _ = phi_debt_to_priority(0.001)
    p_elevated, _ = phi_debt_to_priority(0.2 * xi_c)
    p_high, _ = phi_debt_to_priority(0.7 * xi_c)
    p_critical, _ = phi_debt_to_priority(2.0 * xi_c)
    # Higher debt → lower priority (higher priority number)
    assert p_normal <= p_elevated <= p_high <= p_critical


# ─── equilibrium_check ───────────────────────────────────────────────────────

def test_equilibrium_at_phi0():
    phi0 = PHI_DECISION_CONSTANTS["phi0"]
    result = equilibrium_check(phi0, sigma_phi=0.1)
    assert result["status"] == "EQUILIBRIUM"
    assert result["tension_sigma"] == pytest.approx(0.0)
    assert result["requires_hils"] is False


def test_equilibrium_high_tension():
    phi0 = PHI_DECISION_CONSTANTS["phi0"]
    result = equilibrium_check(phi0 + 0.25, sigma_phi=0.1)  # 2.5σ
    assert result["status"] == "HIGH_TENSION"
    assert result["requires_hils"] is True


def test_equilibrium_critical():
    phi0 = PHI_DECISION_CONSTANTS["phi0"]
    result = equilibrium_check(phi0 + 0.35, sigma_phi=0.1)  # 3.5σ
    assert result["status"] == "CRITICAL"
    assert result["requires_hils"] is True


def test_equilibrium_keys():
    phi0 = PHI_DECISION_CONSTANTS["phi0"]
    result = equilibrium_check(phi0)
    for key in ["phi_value", "phi0", "deviation", "tension_sigma", "status", "requires_hils"]:
        assert key in result


# ─── PhiDecisionEngine ───────────────────────────────────────────────────────

def _make_signal(agent_id: str, phi_debt: float, radion_tension: float, kk_level: int):
    return PhiDebtSignal(
        agent_id=agent_id,
        phi_debt=phi_debt,
        radion_tension=radion_tension,
        kk_level=kk_level,
    )


def test_engine_kernel_always_scheduled():
    engine = PhiDecisionEngine()
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = _make_signal("kernel", phi_debt=2.0 * xi_c, radion_tension=0.5, kk_level=0)
    decision = engine.decide(sig)
    assert decision.decision == "SCHEDULE"
    assert decision.kk_level_recommended == 0


def test_engine_normal_debt_schedules():
    engine = PhiDecisionEngine()
    sig = _make_signal("agent-1", phi_debt=0.001, radion_tension=0.5, kk_level=2)
    decision = engine.decide(sig)
    assert decision.decision == "SCHEDULE"


def test_engine_critical_debt_suspends_user():
    engine = PhiDecisionEngine()
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = _make_signal("user-agent", phi_debt=1.5 * xi_c, radion_tension=0.5, kk_level=3)
    decision = engine.decide(sig)
    assert decision.decision == "SUSPEND"


def test_engine_high_debt_throttles_user():
    engine = PhiDecisionEngine()
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    sig = _make_signal("user-agent", phi_debt=0.7 * xi_c, radion_tension=0.5, kk_level=3)
    decision = engine.decide(sig)
    assert decision.decision in ("THROTTLE", "DEPRIORITIZE")


def test_engine_hils_alert_propagated():
    engine = PhiDecisionEngine()
    sig = _make_signal("agent", phi_debt=0.001, radion_tension=2.5, kk_level=2)
    decision = engine.decide(sig)
    assert decision.hils_alert is True


def test_engine_decide_all():
    engine = PhiDecisionEngine()
    for i in range(3):
        engine.ingest_signal(_make_signal(f"a{i}", phi_debt=0.001, radion_tension=0.5, kk_level=2))
    decisions = engine.decide_all()
    assert len(decisions) == 3


def test_engine_hils_alerts():
    engine = PhiDecisionEngine()
    engine.ingest_signal(_make_signal("ok", phi_debt=0.001, radion_tension=0.5, kk_level=2))
    engine.ingest_signal(_make_signal("alert", phi_debt=0.001, radion_tension=2.5, kk_level=2))
    alerts = engine.hils_alerts()
    assert len(alerts) == 1
    assert alerts[0].agent_id == "alert"


def test_engine_priority_queue():
    engine = PhiDecisionEngine()
    xi_c = PHI_DECISION_CONSTANTS["xi_c"]
    engine.ingest_signal(_make_signal("high-debt", phi_debt=1.5 * xi_c, radion_tension=0.5, kk_level=3))
    engine.ingest_signal(_make_signal("low-debt", phi_debt=0.001, radion_tension=0.5, kk_level=3))
    queue = engine.priority_queue()
    assert len(queue) == 2
    # low-debt should come first (lower priority number = higher priority)
    assert queue[0][1] == "low-debt"


def test_engine_equilibrium_summary():
    engine = PhiDecisionEngine()
    engine.ingest_signal(_make_signal("a1", phi_debt=0.001, radion_tension=0.5, kk_level=2))
    engine.ingest_signal(_make_signal("a2", phi_debt=0.001, radion_tension=2.5, kk_level=2))
    summary = engine.equilibrium_summary()
    assert summary["agents"] == 2
    assert summary["hils_alerts_pending"] == 1
    assert summary["global_status"] == "HIGH_TENSION"


def test_engine_report_keys():
    engine = PhiDecisionEngine()
    engine.ingest_signal(_make_signal("a1", phi_debt=0.001, radion_tension=0.5, kk_level=2))
    engine.decide(engine._signals[0])
    report = engine.report()
    for key in ["signals_ingested", "decisions_issued", "hils_alerts",
                "priority_queue", "equilibrium_summary"]:
        assert key in report


# ─── Full report ─────────────────────────────────────────────────────────────

def test_pillar_report_structure():
    report = pillar_report()
    assert report["pillar"] == 553
    assert report["adjacent_track"] is True
    assert report["parent_pillar"] == 547
    assert report["toe_score_delta"] == pytest.approx(0.0)
