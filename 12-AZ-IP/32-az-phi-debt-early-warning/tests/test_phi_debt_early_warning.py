# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_phi_debt_early_warning import DebtMonitor, DebtStatus, run_recycling_dogfood


def test_monitor_starts_nominal():
    monitor = DebtMonitor(capacity=10.0, discharge_rate=1.0)
    assert monitor.status() == DebtStatus.NOMINAL
    assert monitor.debt == 0.0


def test_monitor_rejects_nonpositive_capacity():
    with pytest.raises(ValueError):
        DebtMonitor(capacity=0.0, discharge_rate=1.0)


def test_monitor_rejects_negative_discharge_rate():
    with pytest.raises(ValueError):
        DebtMonitor(capacity=10.0, discharge_rate=-1.0)


def test_monitor_accumulates_and_discharges():
    monitor = DebtMonitor(capacity=10.0, discharge_rate=1.0)
    reading = monitor.accumulate(amount=5.0, dt=1.0)
    assert reading.debt == pytest.approx(4.0)  # 5 - 1*1
    reading = monitor.accumulate(amount=0.0, dt=1.0)
    assert reading.debt == pytest.approx(3.0)


def test_monitor_debt_floored_at_zero():
    monitor = DebtMonitor(capacity=10.0, discharge_rate=5.0)
    monitor.accumulate(amount=1.0, dt=1.0)
    assert monitor.debt == 0.0


def test_monitor_reaches_warning_then_saturated():
    monitor = DebtMonitor(capacity=10.0, discharge_rate=0.0, warning_fraction=0.8)
    monitor.accumulate(amount=8.0, dt=1.0)
    assert monitor.status() == DebtStatus.WARNING
    monitor.accumulate(amount=2.0, dt=1.0)
    assert monitor.status() == DebtStatus.SATURATED


def test_time_to_saturation_projects_forward():
    monitor = DebtMonitor(capacity=10.0, discharge_rate=0.0)
    monitor.accumulate(amount=2.0, dt=1.0)
    monitor.accumulate(amount=2.0, dt=1.0)
    tts = monitor.time_to_saturation()
    assert tts == pytest.approx(3.0)  # (10 - 4) / 2 per unit time


def test_time_to_saturation_none_when_already_saturated():
    monitor = DebtMonitor(capacity=5.0, discharge_rate=0.0)
    monitor.accumulate(amount=10.0, dt=1.0)
    assert monitor.status() == DebtStatus.SATURATED
    assert monitor.time_to_saturation() is None


def test_time_to_saturation_none_when_discharging():
    monitor = DebtMonitor(capacity=10.0, discharge_rate=5.0)
    monitor.accumulate(amount=1.0, dt=1.0)
    monitor.accumulate(amount=1.0, dt=1.0)
    assert monitor.time_to_saturation() is None


def test_run_recycling_dogfood_tracks_real_entropy_ledger_debt():
    steps = [(1.0, 0.9), (1.0, 0.8), (1.0, 0.95)]
    readings = run_recycling_dogfood(steps, capacity=1.0, discharge_rate=0.05)
    assert len(readings) == 3
    assert all(r.debt >= 0.0 for r in readings)


def test_run_recycling_dogfood_can_reach_warning():
    steps = [(1.0, 0.0)] * 5
    readings = run_recycling_dogfood(steps, capacity=2.0, discharge_rate=0.0)
    assert readings[-1].status in (DebtStatus.WARNING, DebtStatus.SATURATED)
