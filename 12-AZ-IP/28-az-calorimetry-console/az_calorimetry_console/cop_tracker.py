# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Live COP tracker — Phase 0 of the cold-fusion falsification roadmap.

Ingests a thermocouple/electrical-power feed (as a sequence of readings) and
plots measured output power against the predicted excess-heat curve from
``src/cold_fusion/excess_heat.py``, using the project's own
``cop()`` and ``is_excess_heat()`` functions. This module performs no new
physics; it is instrumentation software around an already-existing,
already-tested prediction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from src.cold_fusion.excess_heat import cop, is_excess_heat  # noqa: E402

DEFAULT_COP_THRESHOLD = 1.01


@dataclass(frozen=True)
class COPReading:
    """One measured calorimetry sample."""

    timestamp_s: float
    power_in_w: float
    power_out_w: float

    @property
    def cop(self) -> float:
        return cop(self.power_out_w, self.power_in_w)

    @property
    def is_excess(self) -> bool:
        return is_excess_heat(self.power_out_w, self.power_in_w, threshold=DEFAULT_COP_THRESHOLD)


class COPTracker:
    """Accumulates COP readings and reports a running verdict against the
    project's own pre-registered COP > 1.01 falsification threshold."""

    def __init__(self, threshold: float = DEFAULT_COP_THRESHOLD) -> None:
        if threshold <= 0:
            raise ValueError("threshold must be positive")
        self.threshold = threshold
        self._readings: List[COPReading] = []

    def ingest(self, timestamp_s: float, power_in_w: float, power_out_w: float) -> COPReading:
        if power_in_w <= 0:
            raise ValueError("power_in_w must be positive")
        reading = COPReading(timestamp_s=timestamp_s, power_in_w=power_in_w, power_out_w=power_out_w)
        self._readings.append(reading)
        return reading

    @property
    def readings(self) -> List[COPReading]:
        return list(self._readings)

    def latest_cop(self) -> float | None:
        if not self._readings:
            return None
        return self._readings[-1].cop

    def mean_cop(self) -> float | None:
        if not self._readings:
            return None
        return sum(r.cop for r in self._readings) / len(self._readings)

    def verdict(self) -> str:
        """Return one of ``AWAITING_DATA``, ``EXCESS_HEAT_OBSERVED``, or
        ``NO_EXCESS_HEAT`` — never a claim stronger than the data supports."""
        if not self._readings:
            return "AWAITING_DATA"
        mean = self.mean_cop()
        assert mean is not None
        return "EXCESS_HEAT_OBSERVED" if mean > self.threshold else "NO_EXCESS_HEAT"

    def to_report(self) -> dict:
        return {
            "threshold": self.threshold,
            "n_readings": len(self._readings),
            "latest_cop": self.latest_cop(),
            "mean_cop": self.mean_cop(),
            "verdict": self.verdict(),
        }
