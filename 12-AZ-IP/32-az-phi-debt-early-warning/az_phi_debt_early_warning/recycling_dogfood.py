# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Internal dogfooding demonstration — Phase 1 (partial), per article-354
direction #5. Feeds `recycling/entropy_ledger.material_entropy_debt`
readings into the domain-agnostic `DebtMonitor` as a sanity check that the
extracted library reproduces the same qualitative saturation behavior as
the framework-specific recycling accounting it was extracted from.

This demonstrates exactly one of the five internal reuse targets the
article names (recycling); EIGE, the Falsification Observatory, the
Geophysical Monitor, and the staleness-honesty CI gate are not wired up in
this version.
"""

from __future__ import annotations

from typing import List, Sequence

from ._repo import ensure_repo_on_path

ensure_repo_on_path()

from recycling.entropy_ledger import material_entropy_debt  # noqa: E402

from .debt_monitor import DebtMonitor, DebtReading


def run_recycling_dogfood(
    phi_steps: Sequence[tuple[float, float]],
    capacity: float,
    discharge_rate: float,
) -> List[DebtReading]:
    """Replay a sequence of ``(phi_in, phi_out)`` recycling steps through a
    ``DebtMonitor``, using `material_entropy_debt` for each step's debt
    contribution (floored at zero — quality-improving steps discharge
    naturally via the monitor's own discharge rate rather than ever
    reducing accumulated debt below zero)."""
    monitor = DebtMonitor(capacity=capacity, discharge_rate=discharge_rate)
    readings = []
    for phi_in, phi_out in phi_steps:
        debt = material_entropy_debt(phi_in, phi_out)
        readings.append(monitor.accumulate(amount=max(0.0, debt), dt=1.0))
    return readings
