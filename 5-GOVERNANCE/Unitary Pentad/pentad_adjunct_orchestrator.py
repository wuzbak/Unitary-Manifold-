# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_adjunct_orchestrator.py
=============================================
Sprint D — Adjunct Orchestration layer for multi-agent cloud dispatch.

Purpose
-------
This module builds an orchestration layer **on top of** the cloud adjunct
policy defined in ``pentad_cloud_adjunct.py``.  It provides:

- A task queue for cloud adjunct requests submitted by workflow agents.
- Routing logic that evaluates each task through the ``evaluate_cloud_adjunct``
  policy without calling any real network API.
- A local verification step that inspects raw cloud results before they are
  allowed to influence the five-body orbit.
- Status tracking across the full task lifecycle.

Design invariant
----------------
Cloud results **never** directly actuate the five-body orbit.  Every result
must pass local verification and re-enter through the existing Pentad
governance path (Ψ_AI under Ψ_human + β·C supervision) before use.

Public API
----------
TaskStatus
    String constants for task lifecycle stages.

TASK_STATUSES : tuple[str, ...]
    All status constants in canonical order.

AdjunctTask
    One task submitted to the orchestrator.

VerificationResult
    Result of the local verification step.

AdjunctOrchestrator
    Task queue, router, and verifier.

default_local_verifier(task) -> VerificationResult
    Lenient verifier: passes any non-None result.

strict_local_verifier(task) -> VerificationResult
    Strict verifier: requires non-empty dict with no error key.

make_research_task(description, ...) -> AdjunctTask
    Convenience constructor for TRUTH_QUERY tasks.

make_batch_task(description, payload, ...) -> AdjunctTask
    Convenience constructor for BATCH_COMPUTE tasks.

make_model_task(description, ...) -> AdjunctTask
    Convenience constructor for MODEL_HOST tasks.
"""

from __future__ import annotations

__provenance__ = {
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
}

import uuid
from dataclasses import dataclass, field
from typing import Callable, Optional

from unitary_pentad import PentadSystem, trust_modulation, TRUST_PHI_MIN
from pentad_cloud_adjunct import (
    CloudAdjunctRole,
    CloudAdjunctRequest,
    CloudAdjunctDecision,
    CloudAdjunctPolicy,
    evaluate_cloud_adjunct,
    default_cloud_adjunct_policy,
    CLOUD_ADJUNCT_ROLES,
)
from five_cores.five_cores_system import FiveCoresSystem, CoreLabel, SystemStatus


# ---------------------------------------------------------------------------
# Task status constants
# ---------------------------------------------------------------------------

class TaskStatus:
    """Lifecycle stages for an adjunct task."""

    QUEUED = "queued"
    ROUTING = "routing"
    DISPATCHED = "dispatched"
    AWAITING_VERIFICATION = "awaiting_verification"
    VERIFIED = "verified"
    REJECTED_BY_POLICY = "rejected_by_policy"
    VERIFICATION_FAILED = "verification_failed"
    COMPLETED = "completed"
    FAILED = "failed"


TASK_STATUSES: tuple[str, ...] = (
    TaskStatus.QUEUED,
    TaskStatus.ROUTING,
    TaskStatus.DISPATCHED,
    TaskStatus.AWAITING_VERIFICATION,
    TaskStatus.VERIFIED,
    TaskStatus.REJECTED_BY_POLICY,
    TaskStatus.VERIFICATION_FAILED,
    TaskStatus.COMPLETED,
    TaskStatus.FAILED,
)

# Terminal states — tasks in these states do not appear in pending_tasks().
_TERMINAL_STATUSES: frozenset[str] = frozenset(
    {TaskStatus.COMPLETED, TaskStatus.FAILED}
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class AdjunctTask:
    """One task submitted to the orchestrator.

    Parameters
    ----------
    task_id : str
        UUID4 string identifying this task.  Assigned by :func:`submit`.
    role : str
        One of the :class:`CloudAdjunctRole` constants.
    description : str
        Human-readable description of what this task does.
    criticality : float
        Task criticality in [0, 1].  Higher values trigger confirmation
        requirements at the policy layer.
    estimated_roundtrip_ms : float
        Expected round-trip latency in milliseconds.
    requires_human_confirmation : bool
        Caller hint; the policy may also force confirmation independently.
    payload : dict
        Arbitrary task-specific data passed to the cloud (not sent by this
        module — callers are responsible for delivery).
    status : str
        Current lifecycle stage.  Set by the orchestrator.
    decision : CloudAdjunctDecision | None
        Populated after :meth:`AdjunctOrchestrator.route`.
    result : dict | None
        Populated after successful :meth:`AdjunctOrchestrator.verify`.
    error : str
        Non-empty when the task has failed.
    """

    task_id: str
    role: str
    description: str
    criticality: float = 0.5
    estimated_roundtrip_ms: float = 100.0
    requires_human_confirmation: bool = False
    payload: dict = field(default_factory=dict)
    # Set by orchestrator:
    status: str = TaskStatus.QUEUED
    decision: Optional[CloudAdjunctDecision] = None
    result: Optional[dict] = None
    error: str = ""


@dataclass
class VerificationResult:
    """Result of the local verification step.

    Parameters
    ----------
    task_id : str
        Matches the originating :class:`AdjunctTask`.
    passed : bool
        Whether the verification was successful.
    confidence : float
        Verifier confidence in [0, 1].
    issues : list[str]
        Descriptions of any problems found.
    verified_payload : dict
        Cleaned / approved subset of the raw result.
    """

    task_id: str
    passed: bool
    confidence: float
    issues: list[str]
    verified_payload: dict


# ---------------------------------------------------------------------------
# Verifiers
# ---------------------------------------------------------------------------

def default_local_verifier(task: AdjunctTask) -> VerificationResult:
    """Lenient verifier: passes any non-None result with confidence 0.8.

    Flags empty or error results as issues but still passes them (lenient).
    """
    issues: list[str] = []
    raw = task.result  # raw_result stored on the task by verify()

    if raw is None:
        return VerificationResult(
            task_id=task.task_id,
            passed=False,
            confidence=0.0,
            issues=["Result is None; cannot verify."],
            verified_payload={},
        )

    if not raw:
        issues.append("Result dict is empty.")

    if "error" in raw:
        issues.append(f"Result contains error key: {raw['error']!r}")

    return VerificationResult(
        task_id=task.task_id,
        passed=True,
        confidence=0.8,
        issues=issues,
        verified_payload=dict(raw),
    )


def strict_local_verifier(task: AdjunctTask) -> VerificationResult:
    """Strict verifier: requires non-empty result dict with no 'error' key.

    Confidence is weighted by task criticality (higher criticality → lower
    confidence when any issue is present).
    """
    issues: list[str] = []
    raw = task.result

    if raw is None:
        return VerificationResult(
            task_id=task.task_id,
            passed=False,
            confidence=0.0,
            issues=["Result is None."],
            verified_payload={},
        )

    if not raw:
        issues.append("Result dict is empty.")

    if "error" in raw:
        issues.append(f"Result contains error key: {raw['error']!r}")

    if issues:
        confidence = max(0.0, 1.0 - task.criticality)
        return VerificationResult(
            task_id=task.task_id,
            passed=False,
            confidence=confidence,
            issues=issues,
            verified_payload={},
        )

    confidence = 1.0 - 0.5 * task.criticality
    return VerificationResult(
        task_id=task.task_id,
        passed=True,
        confidence=confidence,
        issues=[],
        verified_payload=dict(raw),
    )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class AdjunctOrchestrator:
    """Task queue for cloud adjunct requests.

    Responsibilities
    ----------------
    - Accept task submissions from workflow agents.
    - Route each task through the ``evaluate_cloud_adjunct`` policy.
    - Track task status through the pipeline.
    - Run local verification before marking tasks complete.
    - Enforce that cloud results **never** directly actuate the five-body orbit.
    - Expose a clean API for workflow engines and mission packs to consume.

    Parameters
    ----------
    system : FiveCoresSystem
        Live five-cores system — used as the trust radion source.
    policy : CloudAdjunctPolicy | None
        Cloud adjunct policy.  Uses :func:`default_cloud_adjunct_policy` if
        ``None``.
    local_verifier : Callable[[AdjunctTask], VerificationResult] | None
        Callable invoked to verify cloud results before completion.  Uses
        :func:`default_local_verifier` if ``None``.
    """

    def __init__(
        self,
        system: FiveCoresSystem,
        *,
        policy: Optional[CloudAdjunctPolicy] = None,
        local_verifier: Optional[Callable[[AdjunctTask], VerificationResult]] = None,
    ) -> None:
        self._system = system
        self._policy = policy if policy is not None else default_cloud_adjunct_policy()
        self._local_verifier = local_verifier if local_verifier is not None else default_local_verifier
        self._tasks: dict[str, AdjunctTask] = {}
        # Keep a default PentadSystem for policy evaluation; its TRUST body
        # phi is updated from FiveCoresSystem._phi_trust at each route() call.
        self._pentad = PentadSystem.default()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _sync_pentad_trust(self) -> None:
        """Synchronise the Pentad TRUST body's φ from the FiveCoresSystem."""
        from unitary_pentad import PentadLabel
        trust_body = self._pentad.bodies[PentadLabel.TRUST]
        # ManifoldState is a regular (non-frozen) dataclass — phi is mutable.
        trust_body.phi = float(self._system._phi_trust)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(self, task: AdjunctTask) -> str:
        """Add *task* to the queue.

        Parameters
        ----------
        task : AdjunctTask
            Task to enqueue.  ``task.status`` is reset to QUEUED.

        Returns
        -------
        str
            The task's ``task_id``.
        """
        task.status = TaskStatus.QUEUED
        self._tasks[task.task_id] = task
        return task.task_id

    def route(self, task_id: str) -> CloudAdjunctDecision:
        """Evaluate cloud adjunct policy for one task.

        Updates ``task.status`` to either DISPATCHED or REJECTED_BY_POLICY.
        The resulting :class:`CloudAdjunctDecision` is stored on the task and
        also returned.

        Parameters
        ----------
        task_id : str
            ID of a previously submitted task.

        Returns
        -------
        CloudAdjunctDecision
        """
        task = self.get_task(task_id)
        task.status = TaskStatus.ROUTING

        self._sync_pentad_trust()

        request = CloudAdjunctRequest(
            request_id=task.task_id,
            role=task.role,
            estimated_roundtrip_ms=task.estimated_roundtrip_ms,
            criticality=task.criticality,
            phase_lock_required=task.requires_human_confirmation,
            control_write_requested=False,
            state_mutation="none",
        )

        decision = evaluate_cloud_adjunct(self._pentad, request, self._policy)
        task.decision = decision

        if decision.cloud_enabled:
            task.status = TaskStatus.DISPATCHED
        else:
            task.status = TaskStatus.REJECTED_BY_POLICY

        return decision

    def verify(self, task_id: str, raw_result: dict) -> VerificationResult:
        """Run local verification on a raw cloud result.

        Updates ``task.status`` to VERIFIED or VERIFICATION_FAILED and stores
        the verified payload on the task.

        Parameters
        ----------
        task_id : str
            ID of a dispatched task.
        raw_result : dict
            Raw payload returned by the cloud caller.

        Returns
        -------
        VerificationResult
        """
        task = self.get_task(task_id)
        task.status = TaskStatus.AWAITING_VERIFICATION
        task.result = raw_result

        vr = self._local_verifier(task)

        if vr.passed:
            task.status = TaskStatus.VERIFIED
            task.result = vr.verified_payload
        else:
            task.status = TaskStatus.VERIFICATION_FAILED
            task.error = "; ".join(vr.issues) if vr.issues else "Verification failed."

        return vr

    def complete(self, task_id: str) -> AdjunctTask:
        """Mark a verified task as completed.

        Parameters
        ----------
        task_id : str
            ID of a task in VERIFIED status.

        Returns
        -------
        AdjunctTask
            The completed task.

        Raises
        ------
        ValueError
            If the task is not in VERIFIED status.
        """
        task = self.get_task(task_id)
        if task.status != TaskStatus.VERIFIED:
            raise ValueError(
                f"Task {task_id!r} cannot be completed: "
                f"expected status VERIFIED, got {task.status!r}."
            )
        task.status = TaskStatus.COMPLETED
        return task

    def fail(self, task_id: str, error: str) -> None:
        """Mark *task_id* as failed with the given error message.

        Parameters
        ----------
        task_id : str
        error : str
            Human-readable failure description.
        """
        task = self.get_task(task_id)
        task.status = TaskStatus.FAILED
        task.error = error

    def get_task(self, task_id: str) -> AdjunctTask:
        """Retrieve a task by ID.

        Raises
        ------
        KeyError
            If no task with that ID exists.
        """
        try:
            return self._tasks[task_id]
        except KeyError:
            raise KeyError(f"No task with id={task_id!r}.")

    def pending_tasks(self) -> list[AdjunctTask]:
        """Return all tasks not yet completed or failed."""
        return [t for t in self._tasks.values() if t.status not in _TERMINAL_STATUSES]

    def completed_tasks(self) -> list[AdjunctTask]:
        """Return all tasks with COMPLETED status."""
        return [t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]

    def queue_status(self) -> dict:
        """Return a summary dict of queue state.

        Keys
        ----
        total : int
            Total tasks in the queue.
        by_status : dict[str, int]
            Count of tasks per status string.
        trust_level : float
            Current FiveCoresSystem ``_phi_trust``.
        """
        by_status: dict[str, int] = {s: 0 for s in TASK_STATUSES}
        for t in self._tasks.values():
            by_status[t.status] = by_status.get(t.status, 0) + 1
        return {
            "total": len(self._tasks),
            "by_status": by_status,
            "trust_level": float(self._system._phi_trust),
        }

    def flush_completed(self) -> list[AdjunctTask]:
        """Remove and return all COMPLETED tasks from the queue."""
        done = [t for t in self._tasks.values() if t.status == TaskStatus.COMPLETED]
        for t in done:
            del self._tasks[t.task_id]
        return done


# ---------------------------------------------------------------------------
# Convenience constructors
# ---------------------------------------------------------------------------

def _make_task_id() -> str:
    """Return a fresh UUID4 string."""
    return str(uuid.uuid4())


def make_research_task(
    description: str,
    *,
    criticality: float = 0.4,
    estimated_roundtrip_ms: float = 500.0,
) -> AdjunctTask:
    """Return a TRUTH_QUERY :class:`AdjunctTask`.

    Parameters
    ----------
    description : str
    criticality : float
        Default 0.4 — research queries are typically lower criticality.
    estimated_roundtrip_ms : float
        Default 500 ms — typical for knowledge-base lookups.
    """
    return AdjunctTask(
        task_id=_make_task_id(),
        role=CloudAdjunctRole.TRUTH_QUERY,
        description=description,
        criticality=criticality,
        estimated_roundtrip_ms=estimated_roundtrip_ms,
    )


def make_batch_task(
    description: str,
    payload: dict,
    *,
    criticality: float = 0.5,
    estimated_roundtrip_ms: float = 2000.0,
) -> AdjunctTask:
    """Return a BATCH_COMPUTE :class:`AdjunctTask`.

    Parameters
    ----------
    description : str
    payload : dict
        Task-specific data (simulation parameters, dataset refs, etc.).
    criticality : float
        Default 0.5.
    estimated_roundtrip_ms : float
        Default 2000 ms — batch jobs are expected to take longer.
    """
    return AdjunctTask(
        task_id=_make_task_id(),
        role=CloudAdjunctRole.BATCH_COMPUTE,
        description=description,
        criticality=criticality,
        estimated_roundtrip_ms=estimated_roundtrip_ms,
        payload=payload,
    )


def make_model_task(
    description: str,
    *,
    criticality: float = 0.6,
    estimated_roundtrip_ms: float = 300.0,
) -> AdjunctTask:
    """Return a MODEL_HOST :class:`AdjunctTask`.

    Parameters
    ----------
    description : str
    criticality : float
        Default 0.6 — model inference may have significant downstream impact.
    estimated_roundtrip_ms : float
        Default 300 ms — remote inference endpoints.
    """
    return AdjunctTask(
        task_id=_make_task_id(),
        role=CloudAdjunctRole.MODEL_HOST,
        description=description,
        criticality=criticality,
        estimated_roundtrip_ms=estimated_roundtrip_ms,
    )
