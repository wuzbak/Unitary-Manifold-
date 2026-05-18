# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_pentad_operator_console.py
================================================
Tests for pentad_operator_console.py.

All tests use render_console() / PentadOperatorConsole.render() and inspect
the returned string — no real terminal is required.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
}

import pytest

from five_cores.five_cores_system import FiveCoresSystem, CoreLabel, SystemStatus
from unitary_pentad import PentadSystem, PENTAD_LABELS
from consciousness_autopilot import AutopilotUniverse, AutopilotMode

from pentad_operator_console import (
    RST, GRN, YLW, RED,
    phi_color,
    bar,
    ConsoleState,
    render_console,
    PentadOperatorConsole,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def system() -> FiveCoresSystem:
    """Default FiveCoresSystem (no tick called — empty history)."""
    return FiveCoresSystem(phi_trust=0.9)


@pytest.fixture()
def ticked_system() -> FiveCoresSystem:
    """FiveCoresSystem with one tick so _history is populated."""
    s = FiveCoresSystem(phi_trust=0.9)
    s.tick()
    return s


@pytest.fixture()
def pentad() -> PentadSystem:
    return PentadSystem.default()


@pytest.fixture()
def autopilot() -> AutopilotUniverse:
    return AutopilotUniverse.default()


@pytest.fixture()
def empty_state(system: FiveCoresSystem) -> ConsoleState:
    return ConsoleState(
        system=system,
        pentad=None,
        autopilot=None,
        pending_gates=[],
        event_log=[],
        task_queue=[],
    )


@pytest.fixture()
def full_state(ticked_system: FiveCoresSystem, pentad: PentadSystem, autopilot: AutopilotUniverse) -> ConsoleState:
    class _Gate:
        gate_id = "gate-safety-01"
        gate_type = "SAFETY"
        description = "Review safety constraints before execution."

    class _Event:
        timestamp = 1_000_000.0
        event_type = "workflow_started"
        job_id = "research_mission_01"
        core_lane = ""

    class _Job:
        job_id = "gather_data"
        description = "Collect observations."
        core_lane = CoreLabel.SCIENCES
        status = "queued"

    return ConsoleState(
        system=ticked_system,
        pentad=pentad,
        autopilot=autopilot,
        pending_gates=[_Gate()],
        event_log=[_Event()],
        task_queue=[_Job()],
    )


# ---------------------------------------------------------------------------
# bar() tests
# ---------------------------------------------------------------------------

class TestBar:
    def test_full(self) -> None:
        result = bar(1.0, 1.0, width=10)
        assert result == "█" * 10

    def test_empty(self) -> None:
        result = bar(0.0, 1.0, width=8)
        assert result == "░" * 8

    def test_half(self) -> None:
        result = bar(0.5, 1.0, width=10)
        assert len(result) == 10
        assert result.count("█") == 5
        assert result.count("░") == 5

    def test_length_always_correct(self) -> None:
        for val in [0.0, 0.25, 0.5, 0.75, 1.0]:
            assert len(bar(val, 1.0, width=24)) == 24

    def test_clamped_above_max(self) -> None:
        result = bar(2.0, 1.0, width=8)
        assert result == "█" * 8

    def test_clamped_below_zero(self) -> None:
        result = bar(-1.0, 1.0, width=8)
        assert result == "░" * 8

    def test_custom_chars(self) -> None:
        result = bar(0.5, 1.0, width=4, fill="#", empty="-")
        assert result == "##--"

    def test_zero_maxval(self) -> None:
        result = bar(1.0, maxval=0.0, width=6)
        assert result == "░" * 6


# ---------------------------------------------------------------------------
# phi_color() tests
# ---------------------------------------------------------------------------

class TestPhiColor:
    def test_green_at_unity(self) -> None:
        assert phi_color(1.0) == GRN

    def test_green_at_threshold(self) -> None:
        assert phi_color(0.7) == GRN

    def test_yellow_above_03(self) -> None:
        assert phi_color(0.5) == YLW

    def test_yellow_at_threshold(self) -> None:
        assert phi_color(0.3) == YLW

    def test_red_below_03(self) -> None:
        assert phi_color(0.29) == RED

    def test_red_at_zero(self) -> None:
        assert phi_color(0.0) == RED


# ---------------------------------------------------------------------------
# render_console() — structural tests
# ---------------------------------------------------------------------------

class TestRenderConsole:
    def test_non_empty(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_contains_five_cores_heading(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "FIVE-CORES SYSTEM" in result

    def test_contains_pentad_heading(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "PENTAD BODIES" in result

    def test_contains_pending_approvals(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "PENDING APPROVALS" in result

    def test_contains_recent_events(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "RECENT EVENTS" in result

    def test_contains_task_queue(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "TASK QUEUE" in result

    def test_contains_footer_hint(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "Quit" in result

    def test_none_when_no_gates(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        assert "(none)" in result

    def test_core_labels_present(self, empty_state: ConsoleState) -> None:
        result = render_console(empty_state)
        for label in ("STRATEGIC", "SAFETY", "SCIENCES", "BIOLOGICAL"):
            assert label in result

    def test_full_state_gate_displayed(self, full_state: ConsoleState) -> None:
        result = render_console(full_state)
        assert "gate-safety-01" in result

    def test_full_state_event_displayed(self, full_state: ConsoleState) -> None:
        result = render_console(full_state)
        assert "workflow_started" in result

    def test_full_state_job_displayed(self, full_state: ConsoleState) -> None:
        result = render_console(full_state)
        assert "gather_data" in result

    def test_full_state_pentad_bodies(self, full_state: ConsoleState) -> None:
        result = render_console(full_state)
        # Autopilot mode string should appear
        assert "AUTOPILOT" in result.upper()

    def test_ticked_system_shows_health(self, full_state: ConsoleState) -> None:
        result = render_console(full_state)
        assert "H_sys" in result

    def test_step_count_in_header(self, ticked_system: FiveCoresSystem) -> None:
        state = ConsoleState(
            system=ticked_system,
            pentad=None,
            autopilot=None,
            pending_gates=[],
            event_log=[],
            task_queue=[],
        )
        result = render_console(state)
        assert "step 1" in result


# ---------------------------------------------------------------------------
# PentadOperatorConsole tests
# ---------------------------------------------------------------------------

class TestPentadOperatorConsole:
    def test_render_returns_string(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system)
        result = console.render()
        assert isinstance(result, str)
        assert len(result) > 0

    def test_render_with_pentad(self, system: FiveCoresSystem, pentad: PentadSystem) -> None:
        console = PentadOperatorConsole(system, pentad=pentad)
        result = console.render()
        assert "PENTAD BODIES" in result

    def test_update_event_log(self, system: FiveCoresSystem) -> None:
        class _Evt:
            timestamp = 0.0
            event_type = "job_started"
            job_id = "test_job"
            core_lane = "SCIENCES"

        console = PentadOperatorConsole(system)
        console.update(event_log=[_Evt()])
        result = console.render()
        assert "job_started" in result

    def test_update_pending_gates(self, system: FiveCoresSystem) -> None:
        class _Gate:
            gate_id = "g-001"
            gate_type = "SAFETY"
            description = "Test gate"

        console = PentadOperatorConsole(system)
        console.update(pending_gates=[_Gate()])
        result = console.render()
        assert "g-001" in result

    def test_update_task_queue(self, system: FiveCoresSystem) -> None:
        class _Job:
            job_id = "analyze_xyz"
            description = "Analyze"
            core_lane = "STRATEGIC"
            status = "queued"

        console = PentadOperatorConsole(system)
        console.update(task_queue=[_Job()])
        result = console.render()
        assert "analyze_xyz" in result

    def test_update_autopilot(self, system: FiveCoresSystem, autopilot: AutopilotUniverse) -> None:
        console = PentadOperatorConsole(system)
        console.update(autopilot=autopilot)
        result = console.render()
        assert len(result) > 0

    def test_snapshot_returns_dict(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system)
        snap = console.snapshot()
        assert isinstance(snap, dict)
        assert "system" in snap
        assert "pentad" in snap
        assert "autopilot" in snap
        assert "pending_gates" in snap
        assert "event_log" in snap
        assert "task_queue" in snap

    def test_replay_frame_non_empty(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system)
        snap = console.snapshot()
        result = console.replay_frame(snap)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_replay_contains_sections(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system)
        snap = console.snapshot()
        result = console.replay_frame(snap)
        assert "FIVE-CORES SYSTEM" in result
        assert "PENTAD BODIES" in result
        assert "PENDING APPROVALS" in result
        assert "RECENT EVENTS" in result

    def test_snapshot_stores_in_history(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system, max_history=5)
        for _ in range(3):
            console.snapshot()
        assert len(console._history) == 3

    def test_history_capped_at_max(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system, max_history=3)
        for _ in range(10):
            console.snapshot()
        assert len(console._history) == 3

    def test_replay_with_pentad_data(self, system: FiveCoresSystem, pentad: PentadSystem) -> None:
        console = PentadOperatorConsole(system, pentad=pentad)
        snap = console.snapshot()
        result = console.replay_frame(snap)
        assert "PENTAD BODIES" in result

    def test_pending_none_shown_when_empty(self, system: FiveCoresSystem) -> None:
        console = PentadOperatorConsole(system)
        result = console.render()
        assert "(none)" in result

    def test_max_events_respected(self, system: FiveCoresSystem) -> None:
        class _Evt:
            def __init__(self, n: int) -> None:
                self.timestamp = float(n)
                self.event_type = f"event_{n:03d}"
                self.job_id = f"job_{n}"
                self.core_lane = ""

        console = PentadOperatorConsole(system, max_events=3)
        console.update(event_log=[_Evt(i) for i in range(10)])
        result = console.render()
        # Only last 3 events should be visible
        assert "event_009" in result
        assert "event_008" in result
        assert "event_007" in result
        assert "event_000" not in result
