# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Domain-agnostic bounded-capacity debt accounting.

A ``DebtMonitor`` tracks accumulated debt against a fixed capacity, given an
accumulation rate and a discharge rate, and reports a running
time-to-saturation estimate. No field of this API mentions physics,
recycling, or governance by name — it is the nounless formalism underneath
`recycling/entropy_ledger.py` and `src/governance/resonance_audit.py`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class DebtStatus(str, Enum):
    NOMINAL = "NOMINAL"
    WARNING = "WARNING"
    SATURATED = "SATURATED"


@dataclass(frozen=True)
class DebtReading:
    """One accounting step."""

    time: float
    debt: float
    status: DebtStatus


@dataclass
class DebtMonitor:
    """Tracks accumulated debt against a fixed capacity.

    capacity : the maximum sustainable accumulated debt before saturation.
    discharge_rate : the steady-state rate at which debt is paid down
        per unit time, independent of any accumulation event.
    warning_fraction : fraction of capacity at which the monitor reports
        WARNING instead of NOMINAL (default 0.8, i.e. 80% of capacity).
    """

    capacity: float
    discharge_rate: float
    warning_fraction: float = 0.8
    _debt: float = field(default=0.0, init=False, repr=False)
    _time: float = field(default=0.0, init=False, repr=False)
    _history: List[DebtReading] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")
        if self.discharge_rate < 0:
            raise ValueError("discharge_rate must be non-negative")
        if not 0.0 < self.warning_fraction <= 1.0:
            raise ValueError("warning_fraction must be in (0, 1]")
        self._history.append(DebtReading(time=0.0, debt=0.0, status=DebtStatus.NOMINAL))

    @property
    def debt(self) -> float:
        return self._debt

    @property
    def history(self) -> List[DebtReading]:
        return list(self._history)

    def status(self) -> DebtStatus:
        if self._debt >= self.capacity:
            return DebtStatus.SATURATED
        if self._debt >= self.warning_fraction * self.capacity:
            return DebtStatus.WARNING
        return DebtStatus.NOMINAL

    def accumulate(self, amount: float, dt: float = 1.0) -> DebtReading:
        """Advance the monitor by ``dt``, adding ``amount`` of new debt and
        discharging ``discharge_rate * dt`` of existing debt."""
        if dt <= 0:
            raise ValueError("dt must be positive")
        if amount < 0:
            raise ValueError("amount must be non-negative")
        self._debt = max(0.0, self._debt + amount - self.discharge_rate * dt)
        self._time += dt
        reading = DebtReading(time=self._time, debt=self._debt, status=self.status())
        self._history.append(reading)
        return reading

    def time_to_saturation(self, projected_rate: float | None = None) -> float | None:
        """Project forward at a constant net rate and estimate how long
        until the monitor reaches ``capacity``.

        ``projected_rate`` defaults to the net rate observed over the most
        recent accumulation step (last reading's debt minus the one
        before it, divided by the elapsed time). Returns ``None`` if the
        monitor is already saturated, or if the net rate is non-positive
        (debt is flat or discharging — no saturation is projected)."""
        if self.status() == DebtStatus.SATURATED:
            return None
        if projected_rate is None:
            if len(self._history) < 2:
                return None
            prev, last = self._history[-2], self._history[-1]
            dt = last.time - prev.time
            if dt <= 0:
                return None
            projected_rate = (last.debt - prev.debt) / dt
        if projected_rate <= 0:
            return None
        remaining = self.capacity - self._debt
        return remaining / projected_rate

    def to_report(self) -> dict:
        return {
            "capacity": self.capacity,
            "discharge_rate": self.discharge_rate,
            "debt": self._debt,
            "status": self.status().value,
            "time_to_saturation": self.time_to_saturation(),
        }
