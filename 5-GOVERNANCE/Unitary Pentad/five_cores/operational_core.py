# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
five_cores/operational_core.py
===============================
Operational Core — task routing, workflow execution, cross-domain coordination.

The Operational Core is the execution layer of the Five-Cores architecture.
It receives structured tasks from any of the five cores, classifies them by
domain and criticality, routes them to the correct handling path, and tracks
their completion state.

Mathematical Framework
-----------------------
Each task has a *complexity score* κ ∈ [0, 1]:

    κ = criticality × (1 − domain_familiarity)

where ``criticality`` ∈ [0, 1] is the caller-declared urgency and
``domain_familiarity`` ∈ [0, 1] is the operational core's current proficiency
in that domain (exponentially updated via experience).

Routing Decision
-----------------
Given κ and the current trust radion φ_trust:

    effective_complexity = κ / max(φ_trust, 1e-6)

    • effective_complexity < AUTO_THRESHOLD  → AUTO (autonomous execution)
    • AUTO_THRESHOLD ≤ eff < HOLD_THRESHOLD  → SUPERVISED (HIL monitoring)
    • HOLD_THRESHOLD ≤ eff < 1.0            → HOLD (await HIL approval)
    • eff ≥ 1.0 OR safety_interlock=True    → HALT (full stop)

Workflow Tracking
-----------------
Tasks are tracked as state machines with states:
    QUEUED → IN_PROGRESS → COMPLETED | FAILED | CANCELLED

The operational throughput metric T ∈ [0, 1] is the fraction of completed
tasks over all resolved tasks in the last WINDOW steps.

Public API
----------
TaskDomain
    Domain constants: NAVIGATION, PROPULSION, LIFE_SUPPORT, SCIENCE,
    COMMUNICATIONS, MAINTENANCE, MEDICAL, COMMAND.

ExecutionMode
    HALT, HOLD, SUPERVISED, AUTO.

TaskStatus
    QUEUED, IN_PROGRESS, COMPLETED, FAILED, CANCELLED.

Task
    Dataclass: id, domain, criticality, description, status, mode, step_created.

OperationalState
    Current state snapshot.

OperationalCore
    The operational routing and tracking engine.
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
import uuid

import numpy as np

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

C_S: float = 12 / 37  # braided sound speed — stability floor

AUTO_THRESHOLD: float = 0.35   # below → autonomous execution
HOLD_THRESHOLD: float = 0.70   # above → hold for HIL approval

#: Experience smoothing factor (0 < α < 1).
EXPERIENCE_ALPHA: float = 0.10

#: Window (in steps) for throughput computation.
THROUGHPUT_WINDOW: int = 74  # k_cs resonance level

#: Trust floor below which ALL tasks become HOLD or HALT.
TRUST_FLOOR: float = C_S


# ---------------------------------------------------------------------------
# Domain and Mode constants
# ---------------------------------------------------------------------------

class TaskDomain:
    NAVIGATION = "NAVIGATION"
    PROPULSION = "PROPULSION"
    LIFE_SUPPORT = "LIFE_SUPPORT"
    SCIENCE = "SCIENCE"
    COMMUNICATIONS = "COMMUNICATIONS"
    MAINTENANCE = "MAINTENANCE"
    MEDICAL = "MEDICAL"
    COMMAND = "COMMAND"


class ExecutionMode:
    AUTO = "AUTO"
    SUPERVISED = "SUPERVISED"
    HOLD = "HOLD"
    HALT = "HALT"


class TaskStatus:
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class Task:
    """A single operational task."""

    id: str
    domain: str
    criticality: float         # ∈ [0, 1]
    description: str
    status: str = TaskStatus.QUEUED
    mode: str = ExecutionMode.AUTO
    step_created: int = 0
    step_resolved: Optional[int] = None
    safety_interlock: bool = False

    def is_resolved(self) -> bool:
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)


@dataclass
class OperationalState:
    """Snapshot of the Operational Core at a given tick."""

    queued: int
    in_progress: int
    completed: int
    failed: int
    throughput: float         # ∈ [0, 1]
    phi_trust: float
    step_count: int
    domain_familiarity: Dict[str, float]
    active_tasks: List[Task]


# ---------------------------------------------------------------------------
# Core Implementation
# ---------------------------------------------------------------------------

class OperationalCore:
    """
    Operational Core — task routing, workflow execution, cross-domain coordination.

    Parameters
    ----------
    phi_trust : float
        Initial trust radion (from Pentad).
    """

    def __init__(self, phi_trust: float = 1.0) -> None:
        self._phi_trust = float(np.clip(phi_trust, 0.0, 1.0))
        self._step_count = 0
        self._tasks: Dict[str, Task] = {}

        # Domain familiarity ∈ [0, 1] — updated via experience
        self._familiarity: Dict[str, float] = {
            TaskDomain.NAVIGATION: 0.80,
            TaskDomain.PROPULSION: 0.70,
            TaskDomain.LIFE_SUPPORT: 0.85,
            TaskDomain.SCIENCE: 0.75,
            TaskDomain.COMMUNICATIONS: 0.90,
            TaskDomain.MAINTENANCE: 0.80,
            TaskDomain.MEDICAL: 0.65,
            TaskDomain.COMMAND: 0.60,
        }

        # Sliding window of resolved (step, outcome) for throughput
        self._resolution_log: List[tuple] = []  # (step, success: bool)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _complexity(self, task: Task) -> float:
        fam = self._familiarity.get(task.domain, 0.5)
        return float(np.clip(task.criticality * (1.0 - fam), 0.0, 1.0))

    def _route(self, task: Task) -> str:
        if task.safety_interlock:
            return ExecutionMode.HALT
        eff = self._complexity(task) / max(self._phi_trust, 1e-6)
        if eff >= 1.0:
            return ExecutionMode.HALT
        elif eff >= HOLD_THRESHOLD:
            return ExecutionMode.HOLD
        elif eff >= AUTO_THRESHOLD:
            return ExecutionMode.SUPERVISED
        else:
            return ExecutionMode.AUTO

    def _update_familiarity(self, domain: str, success: bool) -> None:
        current = self._familiarity.get(domain, 0.5)
        target = 1.0 if success else 0.0
        self._familiarity[domain] = (
            (1 - EXPERIENCE_ALPHA) * current + EXPERIENCE_ALPHA * target
        )

    def _throughput(self) -> float:
        cutoff = self._step_count - THROUGHPUT_WINDOW
        recent = [(s, ok) for s, ok in self._resolution_log if s >= cutoff]
        if not recent:
            return 1.0
        successes = sum(1 for _, ok in recent if ok)
        return float(successes / len(recent))

    def _active_tasks(self) -> List[Task]:
        return [t for t in self._tasks.values() if not t.is_resolved()]

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit_task(
        self,
        domain: str,
        criticality: float,
        description: str = "",
        safety_interlock: bool = False,
    ) -> Task:
        """
        Submit a new task to the operational queue.

        Returns the Task with its routing mode assigned.
        """
        task = Task(
            id=str(uuid.uuid4())[:8],
            domain=domain,
            criticality=float(np.clip(criticality, 0.0, 1.0)),
            description=description,
            step_created=self._step_count,
            safety_interlock=safety_interlock,
        )
        task.mode = self._route(task)
        task.status = TaskStatus.QUEUED
        self._tasks[task.id] = task
        return task

    def start_task(self, task_id: str) -> Optional[Task]:
        """Move a QUEUED task to IN_PROGRESS."""
        t = self._tasks.get(task_id)
        if t and t.status == TaskStatus.QUEUED:
            if t.mode in (ExecutionMode.AUTO, ExecutionMode.SUPERVISED):
                t.status = TaskStatus.IN_PROGRESS
        return t

    def resolve_task(self, task_id: str, success: bool = True) -> Optional[Task]:
        """Mark an IN_PROGRESS task as COMPLETED or FAILED."""
        t = self._tasks.get(task_id)
        if t and t.status == TaskStatus.IN_PROGRESS:
            t.status = TaskStatus.COMPLETED if success else TaskStatus.FAILED
            t.step_resolved = self._step_count
            self._update_familiarity(t.domain, success)
            self._resolution_log.append((self._step_count, success))
        return t

    def cancel_task(self, task_id: str) -> Optional[Task]:
        """Cancel a QUEUED or IN_PROGRESS task."""
        t = self._tasks.get(task_id)
        if t and not t.is_resolved():
            t.status = TaskStatus.CANCELLED
            t.step_resolved = self._step_count
            self._resolution_log.append((self._step_count, False))
        return t

    def hil_approve(self, task_id: str) -> Optional[Task]:
        """HIL approval transitions a HOLD task to IN_PROGRESS."""
        t = self._tasks.get(task_id)
        if t and t.mode == ExecutionMode.HOLD and t.status == TaskStatus.QUEUED:
            t.mode = ExecutionMode.SUPERVISED
            t.status = TaskStatus.IN_PROGRESS
        return t

    def tick(self, trust_delta: float = 0.0) -> OperationalState:
        """
        Advance the Operational Core by one step.

        Auto-progresses AUTO-mode QUEUED tasks to IN_PROGRESS.
        """
        self._step_count += 1
        self._phi_trust = float(np.clip(self._phi_trust + trust_delta, 0.0, 1.0))

        # Auto-progress queued AUTO tasks
        for t in list(self._tasks.values()):
            if t.status == TaskStatus.QUEUED and t.mode == ExecutionMode.AUTO:
                t.status = TaskStatus.IN_PROGRESS

        # Re-route all non-resolved tasks when trust changes
        for t in list(self._tasks.values()):
            if not t.is_resolved():
                t.mode = self._route(t)

        counts = {s: 0 for s in (TaskStatus.QUEUED, TaskStatus.IN_PROGRESS,
                                   TaskStatus.COMPLETED, TaskStatus.FAILED)}
        for t in self._tasks.values():
            if t.status in counts:
                counts[t.status] += 1

        return OperationalState(
            queued=counts[TaskStatus.QUEUED],
            in_progress=counts[TaskStatus.IN_PROGRESS],
            completed=counts[TaskStatus.COMPLETED],
            failed=counts[TaskStatus.FAILED],
            throughput=self._throughput(),
            phi_trust=self._phi_trust,
            step_count=self._step_count,
            domain_familiarity=dict(self._familiarity),
            active_tasks=self._active_tasks(),
        )

    def cross_domain_load(self) -> Dict[str, int]:
        """Count active tasks per domain."""
        load: Dict[str, int] = {}
        for t in self._tasks.values():
            if not t.is_resolved():
                load[t.domain] = load.get(t.domain, 0) + 1
        return load

    @classmethod
    def default(cls) -> "OperationalCore":
        """Factory: canonical operational core at full trust."""
        return cls(phi_trust=1.0)
