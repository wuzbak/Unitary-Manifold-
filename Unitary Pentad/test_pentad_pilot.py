# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/test_pentad_pilot.py
=====================================
Unit tests for the pure-logic components of
``Unitary Pentad/pentad_pilot.py`` (PPN-1).

Scope
-----
Only stateless / lock-safe functions and dataclass construction are tested here.
Interactive I/O, curses display, threading, and Arduino serial are excluded —
those require a live terminal and hardware respectively.

Braid fingerprint
-----------------
This file contains exactly **25 = 5²** tests.
Its companion tests/test_planetary.py contains **49 = 7²** tests.
Together: 5² + 7² = 74 = k_cs = SUM_OF_SQUARES_RESONANCE.
The two new files bring the total test-file count to **74** — the same (5, 7)
resonance that governs KK winding, birefringence, and the Pentad architecture.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).
"""

import sys
import os
import pytest

_PENTAD_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT       = os.path.dirname(_PENTAD_DIR)
for _p in (_ROOT, _PENTAD_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from pentad_pilot import (
    STEP_DT,
    TICK_SLEEP,
    TRUST_STEP,
    HUMAN_STEP,
    PHI_MIN,
    PHI_MAX,
    BODY_NAMES,
    BODY_SYMBOLS,
    BODY_LED_IDX,
    PilotState,
    _clamp,
    _bar,
    inject_trust,
    inject_human,
    reset_system,
)
from unitary_pentad import PentadSystem, PentadLabel, PENTAD_LABELS


# ---------------------------------------------------------------------------
# TestPilotConstants  (5 tests)
# ---------------------------------------------------------------------------

class TestPilotConstants:
    def test_step_dt_positive(self):
        assert STEP_DT > 0.0

    def test_phi_min_less_than_phi_max(self):
        assert PHI_MIN < PHI_MAX

    def test_body_names_covers_all_labels(self):
        assert set(BODY_NAMES.keys()) == set(PENTAD_LABELS)

    def test_body_symbols_covers_all_labels(self):
        assert set(BODY_SYMBOLS.keys()) == set(PENTAD_LABELS)

    def test_body_led_idx_unique_and_complete(self):
        # Exactly one LED index per body, values 0–4 with no gaps.
        assert sorted(BODY_LED_IDX.values()) == [0, 1, 2, 3, 4]


# ---------------------------------------------------------------------------
# TestClamp  (5 tests)
# ---------------------------------------------------------------------------

class TestClamp:
    def test_interior_value_unchanged(self):
        mid = (PHI_MIN + PHI_MAX) / 2.0
        assert pytest.approx(_clamp(mid)) == mid

    def test_below_min_returns_min(self):
        assert pytest.approx(_clamp(PHI_MIN - 100.0)) == PHI_MIN

    def test_above_max_returns_max(self):
        assert pytest.approx(_clamp(PHI_MAX + 100.0)) == PHI_MAX

    def test_at_min_returns_min(self):
        assert pytest.approx(_clamp(PHI_MIN)) == PHI_MIN

    def test_at_max_returns_max(self):
        assert pytest.approx(_clamp(PHI_MAX)) == PHI_MAX


# ---------------------------------------------------------------------------
# TestBar  (5 tests)
# ---------------------------------------------------------------------------

class TestBar:
    def test_zero_value_all_empty(self):
        assert _bar(0.0, 1.0, 10) == "░" * 10

    def test_full_value_all_filled(self):
        assert _bar(1.0, 1.0, 10) == "█" * 10

    def test_half_value_half_fill(self):
        result = _bar(0.5, 1.0, 20)
        assert result == "█" * 10 + "░" * 10

    def test_below_zero_clamped_to_empty(self):
        assert _bar(-5.0, 1.0, 8) == "░" * 8

    def test_above_max_clamped_to_full(self):
        assert _bar(999.0, 1.0, 8) == "█" * 8


# ---------------------------------------------------------------------------
# TestPilotState  (5 tests)
# ---------------------------------------------------------------------------

class TestPilotState:
    def _make(self) -> PilotState:
        return PilotState(system=PentadSystem.default())

    def test_running_is_true_at_creation(self):
        assert self._make().running is True

    def test_hardware_not_connected_at_creation(self):
        assert self._make().hardware_connected is False

    def test_step_is_zero_at_creation(self):
        assert self._make().step == 0

    def test_last_error_empty_at_creation(self):
        assert self._make().last_error == ""

    def test_system_has_all_five_bodies(self):
        state = self._make()
        assert set(state.system.bodies.keys()) == set(PENTAD_LABELS)


# ---------------------------------------------------------------------------
# TestInjectAndReset  (5 tests)
# ---------------------------------------------------------------------------

class TestInjectAndReset:
    def _make(self) -> PilotState:
        return PilotState(system=PentadSystem.default())

    def test_inject_trust_increases_trust_val(self):
        state = self._make()
        before = state.trust_val
        inject_trust(state, TRUST_STEP)
        assert state.trust_val > before

    def test_inject_trust_clamps_at_phi_max(self):
        state = self._make()
        inject_trust(state, 10_000.0)
        assert pytest.approx(state.trust_val) == PHI_MAX

    def test_inject_trust_clamps_at_phi_min(self):
        state = self._make()
        inject_trust(state, -10_000.0)
        assert pytest.approx(state.trust_val) == PHI_MIN

    def test_inject_human_increases_human_val(self):
        state = self._make()
        before = state.human_val
        inject_human(state, HUMAN_STEP)
        assert state.human_val > before

    def test_reset_system_resets_step_to_zero(self):
        state = self._make()
        state.step = 999
        reset_system(state)
        assert state.step == 0
