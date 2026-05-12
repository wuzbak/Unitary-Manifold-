# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/realtime_safety_core.py
====================================
Real-Time Safety Core — continuous guardrails, trust thresholds, hard-stop/hold logic.

The Real-Time Safety Core monitors all five functional cores and the ambient
environment for safety violations.  It enforces the (5,7)-braid stability
bounds as hard operational limits: no core may operate at a coupling strength
below the braided sound speed c_s = 12/37.

Safety Architecture
--------------------
Safety is modelled as a **layered guardrail stack**, from softest to hardest:

    Layer 0 — NOMINAL     : All metrics within bounds.  Full autonomy.
    Layer 1 — ADVISORY    : A metric is approaching a threshold (≥ 75% of limit).
                            Issue advisory alert; continue operation.
    Layer 2 — CAUTION     : A metric has crossed the caution band.
                            Reduce autonomy; notify HIL.
    Layer 3 — WARNING     : A metric is close to the hard limit.
                            Force SUPERVISED mode on all tasks.
    Layer 4 — HOLD        : A hard limit has been reached.
                            Freeze all non-essential operations; mandatory HIL.
    Layer 5 — HALT        : Critical safety interlock tripped.
                            Full hard-stop; only life-support exempt.

Trust-Threshold Logic
----------------------
The Pentad trust radion φ_trust directly sets the permitted autonomy tier:

    φ_trust ≥ 0.80  → Layer 0 (NOMINAL) unlocked
    φ_trust ≥ 0.60  → Layer 1 (ADVISORY) threshold
    φ_trust ≥ C_S   → Layer 2 (CAUTION) minimum  [≈ 0.324]
    φ_trust ≥ 0.20  → Layer 3 (WARNING) threshold
    φ_trust < 0.20  → Layer 4 (HOLD) forced

Hard Interlocks
----------------
These conditions trigger Layer 5 HALT regardless of φ_trust:
    • Any single metric m_i > HARD_INTERLOCK_THRESHOLD (default = 0.95)
    • Safety constraint violation count ≥ MAX_VIOLATIONS_BEFORE_HALT
    • Explicit external halt signal

Public API
----------
SafetyLayer : str constants
    NOMINAL, ADVISORY, CAUTION, WARNING, HOLD, HALT.

SafetyMetric
    Dataclass: label, value ∈ [0, 1], threshold, hard_interlock.

SafetyAlert
    Dataclass: layer, metric_label, value, threshold, step.

SafetyState
    Full state snapshot.

RealTimeSafetyCore
    The safety monitoring engine.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "license_software": "AGPL-3.0-or-later",
    "fingerprint": "(5, 7, 74)",
}

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

C_S: float = 12 / 37           # braided sound speed ≈ 0.3243

TRUST_NOMINAL: float = 0.80
TRUST_ADVISORY: float = 0.60
TRUST_CAUTION: float = C_S
TRUST_WARNING: float = 0.20

METRIC_ADVISORY_FRACTION: float = 0.75   # 75% of threshold → advisory
HARD_INTERLOCK_THRESHOLD: float = 0.95   # metric value → instant HALT
MAX_VIOLATIONS_BEFORE_HALT: int = 5      # cumulative violations → HALT

LIFE_SUPPORT_DOMAINS = frozenset({"LIFE_SUPPORT", "MEDICAL"})


# ---------------------------------------------------------------------------
# Layer / alert constants
# ---------------------------------------------------------------------------

class SafetyLayer:
    NOMINAL = "NOMINAL"
    ADVISORY = "ADVISORY"
    CAUTION = "CAUTION"
    WARNING = "WARNING"
    HOLD = "HOLD"
    HALT = "HALT"

    _ORDER = ["NOMINAL", "ADVISORY", "CAUTION", "WARNING", "HOLD", "HALT"]

    @classmethod
    def severity(cls, layer: str) -> int:
        try:
            return cls._ORDER.index(layer)
        except ValueError:
            return -1

    @classmethod
    def more_severe(cls, a: str, b: str) -> str:
        return a if cls.severity(a) >= cls.severity(b) else b


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class SafetyMetric:
    """A continuously monitored safety metric."""

    label: str
    value: float = 0.0          # current normalised value ∈ [0, 1]; higher = worse
    threshold: float = 0.70     # caution threshold
    hard_interlock: bool = False

    def __post_init__(self) -> None:
        self.value = float(np.clip(self.value, 0.0, 1.0))

    @property
    def advisory_threshold(self) -> float:
        return self.threshold * METRIC_ADVISORY_FRACTION

    @property
    def layer(self) -> str:
        if self.value >= HARD_INTERLOCK_THRESHOLD:
            return SafetyLayer.HALT
        if self.value >= self.threshold:
            return SafetyLayer.WARNING
        if self.value >= self.advisory_threshold:
            return SafetyLayer.ADVISORY
        return SafetyLayer.NOMINAL


@dataclass
class SafetyAlert:
    """A generated safety alert."""

    layer: str
    metric_label: str
    value: float
    threshold: float
    step: int
    message: str = ""


@dataclass
class SafetyState:
    """Snapshot of the Real-Time Safety Core."""

    layer: str                   # overall safety layer (worst active)
    phi_trust: float
    metrics: Dict[str, SafetyMetric]
    alerts: List[SafetyAlert]
    violation_count: int
    halt_active: bool
    step_count: int


# ---------------------------------------------------------------------------
# Core Implementation
# ---------------------------------------------------------------------------

class RealTimeSafetyCore:
    """
    Real-Time Safety Core — continuous guardrails and hard-stop/hold logic.

    Parameters
    ----------
    phi_trust : float
        Initial trust radion.
    metrics : list[SafetyMetric] | None
        Initial safety metrics.  Defaults to canonical mission-critical set.
    """

    def __init__(
        self,
        phi_trust: float = 1.0,
        metrics: Optional[List[SafetyMetric]] = None,
    ) -> None:
        self._phi_trust = float(np.clip(phi_trust, 0.0, 1.0))
        self._step_count = 0
        self._violation_count = 0
        self._halt_active = False
        self._alert_log: List[SafetyAlert] = []

        if metrics is None:
            metrics = [
                SafetyMetric("RADIATION_EXPOSURE", value=0.10, threshold=0.70),
                SafetyMetric("HULL_STRESS", value=0.15, threshold=0.65),
                SafetyMetric("ATMOSPHERE_CO2", value=0.12, threshold=0.60),
                SafetyMetric("POWER_DRAIN", value=0.20, threshold=0.75),
                SafetyMetric("NAVIGATION_UNCERTAINTY", value=0.25, threshold=0.80),
            ]
        self._metrics: Dict[str, SafetyMetric] = {m.label: m for m in metrics}

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _trust_layer(self) -> str:
        if self._phi_trust >= TRUST_NOMINAL:
            return SafetyLayer.NOMINAL
        elif self._phi_trust >= TRUST_ADVISORY:
            return SafetyLayer.ADVISORY
        elif self._phi_trust >= TRUST_CAUTION:
            return SafetyLayer.CAUTION
        elif self._phi_trust >= TRUST_WARNING:
            return SafetyLayer.WARNING
        else:
            return SafetyLayer.HOLD

    def _overall_layer(self) -> str:
        worst = self._trust_layer()
        for m in self._metrics.values():
            worst = SafetyLayer.more_severe(worst, m.layer)
        if self._violation_count >= MAX_VIOLATIONS_BEFORE_HALT:
            worst = SafetyLayer.HALT
        return worst

    def _generate_alerts(self) -> List[SafetyAlert]:
        alerts = []
        for m in self._metrics.values():
            if m.layer in (SafetyLayer.ADVISORY, SafetyLayer.WARNING, SafetyLayer.HALT):
                alerts.append(SafetyAlert(
                    layer=m.layer,
                    metric_label=m.label,
                    value=m.value,
                    threshold=m.threshold,
                    step=self._step_count,
                    message=f"{m.label} at {m.value:.3f} (threshold {m.threshold:.3f})",
                ))
        return alerts

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def register_metric(self, metric: SafetyMetric) -> None:
        """Add or replace a monitored safety metric."""
        self._metrics[metric.label] = metric

    def update_metric(self, label: str, value: float) -> None:
        """Update the current value of a safety metric."""
        if label in self._metrics:
            self._metrics[label].value = float(np.clip(value, 0.0, 1.0))
        else:
            self._metrics[label] = SafetyMetric(label=label, value=value)

    def hard_halt(self, reason: str = "external") -> None:
        """Trigger an immediate HALT (e.g. from external interlock)."""
        self._halt_active = True
        self._alert_log.append(SafetyAlert(
            layer=SafetyLayer.HALT,
            metric_label="HARD_INTERLOCK",
            value=1.0,
            threshold=0.0,
            step=self._step_count,
            message=f"Hard HALT triggered: {reason}",
        ))

    def release_halt(self, phi_trust_required: float = TRUST_CAUTION) -> bool:
        """
        Release a soft HALT if trust is above the required floor.

        Returns True if halt was released, False if conditions not met.
        """
        if self._phi_trust >= phi_trust_required and self._violation_count < MAX_VIOLATIONS_BEFORE_HALT:
            self._halt_active = False
            return True
        return False

    def is_operation_permitted(self, domain: str) -> bool:
        """
        True if an operation in the given domain is currently permitted.

        Life-support domains are always permitted.
        """
        if domain in LIFE_SUPPORT_DOMAINS:
            return True
        overall = self._overall_layer()
        if self._halt_active or overall == SafetyLayer.HALT:
            return False
        if overall == SafetyLayer.HOLD:
            return False
        return True

    def tick(
        self,
        metric_updates: Optional[Dict[str, float]] = None,
        trust_delta: float = 0.0,
    ) -> SafetyState:
        """
        Advance the Safety Core by one step.

        Parameters
        ----------
        metric_updates : dict[label → new_value] | None
            External sensor readings for this step.
        trust_delta : float
            Change in trust radion this step.
        """
        self._step_count += 1
        self._phi_trust = float(np.clip(self._phi_trust + trust_delta, 0.0, 1.0))

        if metric_updates:
            for label, val in metric_updates.items():
                self.update_metric(label, val)

        # Count violations this step
        step_violations = sum(
            1 for m in self._metrics.values()
            if m.value >= m.threshold
        )
        if step_violations > 0:
            self._violation_count += step_violations

        # Check hard interlocks
        for m in self._metrics.values():
            if m.value >= HARD_INTERLOCK_THRESHOLD:
                self._halt_active = True

        alerts = self._generate_alerts()
        self._alert_log.extend(alerts)

        return SafetyState(
            layer=SafetyLayer.HALT if self._halt_active else self._overall_layer(),
            phi_trust=self._phi_trust,
            metrics=dict(self._metrics),
            alerts=alerts,
            violation_count=self._violation_count,
            halt_active=self._halt_active,
            step_count=self._step_count,
        )

    def recent_alerts(self, n: int = 10) -> List[SafetyAlert]:
        """Return the n most recent safety alerts."""
        return self._alert_log[-n:]

    def reset_violation_count(self) -> None:
        """HIL-initiated violation count reset after review."""
        self._violation_count = 0

    @classmethod
    def default(cls) -> "RealTimeSafetyCore":
        """Factory: canonical mission safety core at full trust."""
        return cls(phi_trust=1.0)
