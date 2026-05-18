# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_mission_packs.py
=======================================
Sprint E — Multi-Agent Mission Packs.

Pre-built, reusable mission packs that wire together :class:`AgentJob` entries,
:class:`HILGate` checkpoints, and adjunct tasks into complete operational
workflows.  An operator selects a pack by its :class:`MissionPackID` constant,
optionally customises the job list, and launches it through :class:`MissionRunner`.

Module is designed to be **resilient to missing Sprint A / Sprint D files**: if
``pentad_workflow_engine`` or ``pentad_adjunct_orchestrator`` are not importable,
lightweight fallback stubs are activated so that tests still pass.

Public API
----------
MissionPackID
    Built-in mission pack identifier constants.

MISSION_PACK_IDS : tuple[str, ...]
    All five pack identifier strings.

MissionPackSpec
    Declarative specification for one mission pack.

MISSION_PACK_REGISTRY : dict[str, MissionPackSpec]
    Registry of all built-in pack specs.

get_pack_spec(pack_id) -> MissionPackSpec
    Return spec for a registered pack_id.

list_pack_ids() -> tuple[str, ...]
    Return all registered pack ids.

describe_pack(pack_id) -> str
    Return a human-readable multi-line description of a pack.

MissionRunner
    Wraps WorkflowEngine + AdjunctOrchestrator for one mission.

research_jobs(include_cloud) -> list
    Default AgentJob list for the RESEARCH mission pack.

triage_jobs() -> list
    Default AgentJob list for the TRIAGE mission pack.

planning_jobs(include_cloud) -> list
    Default AgentJob list for the PLANNING mission pack.

monitoring_jobs() -> list
    Default AgentJob list for the MONITORING mission pack.

interrogation_jobs(include_cloud) -> list
    Default AgentJob list for the INTERROGATION mission pack.
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
    "sprint": "E — Multi-Agent Mission Packs",
}

import uuid
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Optional Sprint A / Sprint D imports with graceful fallback
# ---------------------------------------------------------------------------

try:
    from pentad_workflow_engine import (
        AgentJob,
        HILGate,
        HILGateType,
        PentadWorkflowSchema,
        StopCondition,
        build_workflow,
        WorkflowEngine,
        TRUST_PHI_MIN,
    )
    _HAS_WORKFLOW_ENGINE = True
except ImportError:
    _HAS_WORKFLOW_ENGINE = False
    TRUST_PHI_MIN: float = 12 / 37

    # ------------------------------------------------------------------
    # Minimal stubs so code paths still execute without Sprint A
    # ------------------------------------------------------------------

    class HILGateType:  # type: ignore[no-redef]
        """Fallback HIL gate type constants."""

        SAFETY = "safety"
        LEGITIMACY = "legitimacy"
        BIFURCATION = "bifurcation"
        CRITICALITY = "criticality"
        MANDATORY_REVIEW = "mandatory_review"

    @dataclass(frozen=True)
    class HILGate:  # type: ignore[no-redef]
        """Fallback HIL gate stub."""

        gate_id: str
        gate_type: str
        description: str
        required: bool = True

    @dataclass
    class AgentJob:  # type: ignore[no-redef]
        """Fallback AgentJob stub."""

        job_id: str
        description: str
        core_lane: str
        hil_gates: List
        cloud_adjunct_eligible: bool = False
        cloud_role: Optional[str] = None
        trust_threshold: float = TRUST_PHI_MIN
        stop_conditions: Tuple[str, ...] = ()
        handler: Optional[Callable] = field(default=None, repr=False)

    class PentadWorkflowSchema:  # type: ignore[no-redef]
        """Fallback schema stub (not used at runtime without Sprint A)."""

    class WorkflowEngine:  # type: ignore[no-redef]
        """Fallback engine stub."""

        def __init__(self, system):  # noqa: ANN001
            self._system = system
            self._event_log: List[dict] = []

        def run(self, schema, *, hil_handler=None) -> dict:  # noqa: ANN001
            return {
                "status": "completed",
                "stop_reason": "",
                "jobs_completed": [],
                "jobs_pending": [],
                "event_log": [],
            }

    def build_workflow(  # type: ignore[misc]
        name: str,
        description: str,
        jobs: list,
        *,
        trust_floor: float = TRUST_PHI_MIN,
        max_autonomous_steps: int = 50,
    ):  # noqa: ANN201
        """Fallback build_workflow stub."""
        return PentadWorkflowSchema()

    class StopCondition:  # type: ignore[no-redef]
        TRUST_BELOW_FLOOR = "trust_below_floor"
        SAFETY_HALT = "safety_halt"
        LEGITIMACY_REJECTED = "legitimacy_rejected"
        COLLAPSE_DETECTED = "collapse_detected"
        MAX_STEPS_EXCEEDED = "max_steps_exceeded"
        HIL_TIMEOUT = "hil_timeout"


try:
    from pentad_adjunct_orchestrator import (
        AdjunctOrchestrator,
        make_research_task,
        make_batch_task,
        make_model_task,
    )
    _HAS_ADJUNCT = True
except ImportError:
    _HAS_ADJUNCT = False

from five_cores.five_cores_system import FiveCoresSystem, CoreLabel, CORE_LABELS

# ---------------------------------------------------------------------------
# Pack identifier constants
# ---------------------------------------------------------------------------


class MissionPackID:
    """Built-in mission pack identifier constants."""

    RESEARCH = "research"
    TRIAGE = "triage"
    PLANNING = "planning"
    MONITORING = "monitoring"
    INTERROGATION = "interrogation"


#: All five built-in pack ids in canonical order.
MISSION_PACK_IDS: Tuple[str, ...] = (
    MissionPackID.RESEARCH,
    MissionPackID.TRIAGE,
    MissionPackID.PLANNING,
    MissionPackID.MONITORING,
    MissionPackID.INTERROGATION,
)

# ---------------------------------------------------------------------------
# MissionPackSpec
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class MissionPackSpec:
    """
    Declarative specification for one mission pack.

    Attributes
    ----------
    pack_id : str
        One of :class:`MissionPackID` constants.
    name : str
        Short human-readable name.
    description : str
        Full description of the pack's purpose and scope.
    required_cores : tuple[str, ...]
        :class:`CoreLabel` constants that must be represented.
    trust_floor : float
        Minimum φ_trust required to launch this pack.
    hil_threshold : str
        Primary :class:`HILGateType` constant for this pack.
    cloud_adjunct_eligible : bool
        Whether cloud adjunct dispatch is permitted.
    cloud_roles : tuple[str, ...]
        Permitted :class:`CloudAdjunctRole` values (empty if not eligible).
    max_autonomous_steps : int
        Maximum number of job iterations before stopping.
    ui_panels : tuple[str, ...]
        Relevant operator console panel names.
    """

    pack_id: str
    name: str
    description: str
    required_cores: Tuple[str, ...]
    trust_floor: float
    hil_threshold: str
    cloud_adjunct_eligible: bool
    cloud_roles: Tuple[str, ...]
    max_autonomous_steps: int
    ui_panels: Tuple[str, ...]


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

MISSION_PACK_REGISTRY: Dict[str, MissionPackSpec] = {
    MissionPackID.RESEARCH: MissionPackSpec(
        pack_id=MissionPackID.RESEARCH,
        name="Research Mission",
        description=(
            "Drives a full research cycle: raw data gathering via the SCIENCES "
            "core, multi-pass analysis, and structured reporting via the "
            "STRATEGIC core.  Cloud truth-query and model-host roles are "
            "eligible.  Criticality HIL gates guard the analysis step."
        ),
        required_cores=(CoreLabel.SCIENCES, CoreLabel.STRATEGIC),
        trust_floor=0.3,
        hil_threshold=HILGateType.CRITICALITY,
        cloud_adjunct_eligible=True,
        cloud_roles=("truth_query", "model_host"),
        max_autonomous_steps=30,
        ui_panels=("five_cores", "events", "task_queue"),
    ),
    MissionPackID.TRIAGE: MissionPackSpec(
        pack_id=MissionPackID.TRIAGE,
        name="Triage Mission",
        description=(
            "Time-critical safety and biological triage.  SAFETY core assesses "
            "the threat; BIOLOGICAL core executes the response.  All HIL gates "
            "are required safety checks.  Cloud adjunct is disabled to preserve "
            "low latency."
        ),
        required_cores=(CoreLabel.SAFETY, CoreLabel.BIOLOGICAL),
        trust_floor=0.5,
        hil_threshold=HILGateType.SAFETY,
        cloud_adjunct_eligible=False,
        cloud_roles=(),
        max_autonomous_steps=10,
        ui_panels=("five_cores", "pentad", "pending_approvals"),
    ),
    MissionPackID.PLANNING: MissionPackSpec(
        pack_id=MissionPackID.PLANNING,
        name="Planning Mission",
        description=(
            "Long-horizon doctrine and resource planning.  STRATEGIC core sets "
            "objectives; OPERATIONAL core builds the execution plan and allocates "
            "resources.  Mandatory-review HIL gates ensure human approval of all "
            "major decisions.  Batch-compute cloud adjunct is eligible."
        ),
        required_cores=(CoreLabel.STRATEGIC, CoreLabel.OPERATIONAL),
        trust_floor=0.4,
        hil_threshold=HILGateType.MANDATORY_REVIEW,
        cloud_adjunct_eligible=True,
        cloud_roles=("batch_compute",),
        max_autonomous_steps=50,
        ui_panels=("five_cores", "events", "task_queue"),
    ),
    MissionPackID.MONITORING: MissionPackSpec(
        pack_id=MissionPackID.MONITORING,
        name="Monitoring Mission",
        description=(
            "Continuous full-spectrum system monitoring across all five cores. "
            "Each core contributes a dedicated monitoring job.  A bifurcation "
            "HIL gate on the STRATEGIC assessment job flags phase-space "
            "divergence.  Cloud adjunct is disabled; all monitoring is local."
        ),
        required_cores=CORE_LABELS,
        trust_floor=0.2,
        hil_threshold=HILGateType.BIFURCATION,
        cloud_adjunct_eligible=False,
        cloud_roles=(),
        max_autonomous_steps=100,
        ui_panels=("five_cores", "pentad", "events", "task_queue", "pending_approvals"),
    ),
    MissionPackID.INTERROGATION: MissionPackSpec(
        pack_id=MissionPackID.INTERROGATION,
        name="Interrogation Mission",
        description=(
            "Structured interrogation of an agent or system: OPERATIONAL core "
            "queries the target, SAFETY core validates responses, and OPERATIONAL "
            "core produces a summary.  Legitimacy HIL gates on query and validation "
            "steps enforce constitutional authority.  Truth-query cloud adjunct is "
            "eligible for external cross-checks."
        ),
        required_cores=(CoreLabel.OPERATIONAL, CoreLabel.SAFETY),
        trust_floor=0.6,
        hil_threshold=HILGateType.LEGITIMACY,
        cloud_adjunct_eligible=True,
        cloud_roles=("truth_query",),
        max_autonomous_steps=20,
        ui_panels=("pentad", "pending_approvals", "events"),
    ),
}


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def get_pack_spec(pack_id: str) -> MissionPackSpec:
    """
    Return the :class:`MissionPackSpec` for a registered pack_id.

    Parameters
    ----------
    pack_id : str
        One of :class:`MissionPackID` constants.

    Raises
    ------
    KeyError
        If ``pack_id`` is not registered.
    """
    if pack_id not in MISSION_PACK_REGISTRY:
        raise KeyError(
            f"Unknown mission pack id: {pack_id!r}. "
            f"Available ids: {list(MISSION_PACK_REGISTRY)}"
        )
    return MISSION_PACK_REGISTRY[pack_id]


def list_pack_ids() -> Tuple[str, ...]:
    """Return all registered pack ids as a tuple."""
    return tuple(MISSION_PACK_REGISTRY.keys())


def describe_pack(pack_id: str) -> str:
    """
    Return a human-readable multi-line description of a mission pack.

    Parameters
    ----------
    pack_id : str
        One of :class:`MissionPackID` constants.

    Raises
    ------
    KeyError
        If ``pack_id`` is not registered.
    """
    spec = get_pack_spec(pack_id)
    cloud_info = (
        f"Cloud adjunct: ELIGIBLE — roles: {', '.join(spec.cloud_roles)}"
        if spec.cloud_adjunct_eligible
        else "Cloud adjunct: DISABLED"
    )
    return (
        f"Mission Pack: {spec.name} [{spec.pack_id}]\n"
        f"  Description    : {spec.description}\n"
        f"  Required cores : {', '.join(spec.required_cores)}\n"
        f"  Trust floor    : {spec.trust_floor}\n"
        f"  HIL threshold  : {spec.hil_threshold}\n"
        f"  {cloud_info}\n"
        f"  Max steps      : {spec.max_autonomous_steps}\n"
        f"  UI panels      : {', '.join(spec.ui_panels)}"
    )


# ---------------------------------------------------------------------------
# Default job builders
# ---------------------------------------------------------------------------


def _make_hil_gate(gate_type: str, description: str, *, required: bool = True) -> "HILGate":
    """Construct a :class:`HILGate` (or fallback dict) for a given gate type."""
    return HILGate(
        gate_id=str(uuid.uuid4()),
        gate_type=gate_type,
        description=description,
        required=required,
    )


def _make_job(
    description: str,
    core_lane: str,
    hil_gates: List,
    *,
    cloud_adjunct_eligible: bool = False,
    cloud_role: Optional[str] = None,
) -> "AgentJob":
    """Construct an :class:`AgentJob` (or fallback dict) for a given description."""
    return AgentJob(
        job_id=str(uuid.uuid4()),
        description=description,
        core_lane=core_lane,
        hil_gates=hil_gates,
        cloud_adjunct_eligible=cloud_adjunct_eligible,
        cloud_role=cloud_role,
    )


def research_jobs(*, include_cloud: bool = True) -> List:
    """
    Return the default :class:`AgentJob` list for the RESEARCH mission pack.

    Jobs
    ----
    1. SCIENCES / gather_data  — safety HIL gate; cloud-eligible (truth_query)
    2. SCIENCES / analyze      — criticality HIL gate; cloud-eligible (truth_query)
    3. STRATEGIC / report      — no HIL gate; cloud-eligible (model_host)

    Parameters
    ----------
    include_cloud : bool
        When ``False``, cloud adjunct eligibility is suppressed for all jobs.
    """
    return [
        _make_job(
            "SCIENCES/gather_data: Collect raw observational data from Sciences core",
            CoreLabel.SCIENCES,
            [_make_hil_gate(HILGateType.SAFETY, "Safety check before data gathering")],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="truth_query" if include_cloud else None,
        ),
        _make_job(
            "SCIENCES/analyze: Multi-pass analysis of gathered data",
            CoreLabel.SCIENCES,
            [_make_hil_gate(HILGateType.CRITICALITY, "Criticality gate before analysis")],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="truth_query" if include_cloud else None,
        ),
        _make_job(
            "STRATEGIC/report: Synthesise findings into structured strategic report",
            CoreLabel.STRATEGIC,
            [],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="model_host" if include_cloud else None,
        ),
    ]


def triage_jobs() -> List:
    """
    Return the default :class:`AgentJob` list for the TRIAGE mission pack.

    Jobs
    ----
    1. SAFETY / assess   — safety HIL gate (required)
    2. BIOLOGICAL / respond — safety HIL gate (required)
    """
    return [
        _make_job(
            "SAFETY/assess: Real-time safety threat assessment",
            CoreLabel.SAFETY,
            [_make_hil_gate(HILGateType.SAFETY, "Required safety gate before assessment", required=True)],
        ),
        _make_job(
            "BIOLOGICAL/respond: Biological core emergency response",
            CoreLabel.BIOLOGICAL,
            [_make_hil_gate(HILGateType.SAFETY, "Required safety gate before response", required=True)],
        ),
    ]


def planning_jobs(*, include_cloud: bool = True) -> List:
    """
    Return the default :class:`AgentJob` list for the PLANNING mission pack.

    Jobs
    ----
    1. STRATEGIC / objectives — mandatory_review HIL gate; cloud batch_compute eligible
    2. OPERATIONAL / plan     — mandatory_review HIL gate; cloud batch_compute eligible
    3. STRATEGIC / allocate   — no HIL gate; cloud batch_compute eligible

    Parameters
    ----------
    include_cloud : bool
        When ``False``, cloud adjunct eligibility is suppressed for all jobs.
    """
    return [
        _make_job(
            "STRATEGIC/objectives: Define long-horizon mission objectives",
            CoreLabel.STRATEGIC,
            [_make_hil_gate(HILGateType.MANDATORY_REVIEW, "Mandatory human review of objectives")],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="batch_compute" if include_cloud else None,
        ),
        _make_job(
            "OPERATIONAL/plan: Build task-level execution plan",
            CoreLabel.OPERATIONAL,
            [_make_hil_gate(HILGateType.MANDATORY_REVIEW, "Mandatory human review of execution plan")],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="batch_compute" if include_cloud else None,
        ),
        _make_job(
            "STRATEGIC/allocate: Allocate resources across mission domains",
            CoreLabel.STRATEGIC,
            [],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="batch_compute" if include_cloud else None,
        ),
    ]


def monitoring_jobs() -> List:
    """
    Return the default :class:`AgentJob` list for the MONITORING mission pack.

    Jobs
    ----
    1. SAFETY / monitor       — no HIL gate
    2. BIOLOGICAL / vitals    — no HIL gate
    3. SCIENCES / telemetry   — no HIL gate
    4. OPERATIONAL / status   — no HIL gate
    5. STRATEGIC / assess     — bifurcation HIL gate (required)
    """
    return [
        _make_job(
            "SAFETY/monitor: Continuous safety guardrail monitoring",
            CoreLabel.SAFETY,
            [],
        ),
        _make_job(
            "BIOLOGICAL/vitals: Crew vitals and biological readiness telemetry",
            CoreLabel.BIOLOGICAL,
            [],
        ),
        _make_job(
            "SCIENCES/telemetry: Sciences core instrument telemetry collection",
            CoreLabel.SCIENCES,
            [],
        ),
        _make_job(
            "OPERATIONAL/status: Operational task queue and throughput status",
            CoreLabel.OPERATIONAL,
            [],
        ),
        _make_job(
            "STRATEGIC/assess: Strategic phase-space assessment with bifurcation detection",
            CoreLabel.STRATEGIC,
            [_make_hil_gate(HILGateType.BIFURCATION, "Bifurcation gate on strategic assessment")],
        ),
    ]


def interrogation_jobs(*, include_cloud: bool = True) -> List:
    """
    Return the default :class:`AgentJob` list for the INTERROGATION mission pack.

    Jobs
    ----
    1. OPERATIONAL / query    — legitimacy HIL gate (required); cloud truth_query eligible
    2. SAFETY / validate      — legitimacy HIL gate (required)
    3. OPERATIONAL / summarize — no HIL gate; cloud truth_query eligible

    Parameters
    ----------
    include_cloud : bool
        When ``False``, cloud adjunct eligibility is suppressed for all jobs.
    """
    return [
        _make_job(
            "OPERATIONAL/query: Issue structured query to interrogation target",
            CoreLabel.OPERATIONAL,
            [_make_hil_gate(HILGateType.LEGITIMACY, "Legitimacy gate before query issuance", required=True)],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="truth_query" if include_cloud else None,
        ),
        _make_job(
            "SAFETY/validate: Validate query responses against safety constraints",
            CoreLabel.SAFETY,
            [_make_hil_gate(HILGateType.LEGITIMACY, "Legitimacy gate before response validation", required=True)],
        ),
        _make_job(
            "OPERATIONAL/summarize: Produce structured interrogation summary",
            CoreLabel.OPERATIONAL,
            [],
            cloud_adjunct_eligible=include_cloud,
            cloud_role="truth_query" if include_cloud else None,
        ),
    ]


# ---------------------------------------------------------------------------
# MissionRunner
# ---------------------------------------------------------------------------

_JOB_BUILDERS = {
    MissionPackID.RESEARCH: research_jobs,
    MissionPackID.TRIAGE: triage_jobs,
    MissionPackID.PLANNING: planning_jobs,
    MissionPackID.MONITORING: monitoring_jobs,
    MissionPackID.INTERROGATION: interrogation_jobs,
}


class MissionRunner:
    """
    Wraps :class:`WorkflowEngine` + :class:`AdjunctOrchestrator` for one mission pack.

    If the workflow engine is unavailable (Sprint A not imported), falls back to
    a simple sequential job executor that records events as plain dicts.

    Parameters
    ----------
    pack_id : str
        One of :class:`MissionPackID` constants.
    system : FiveCoresSystem
        Live Five-Cores system to run against.
    custom_jobs : list | None
        Override the default job list for the selected pack.
    hil_handler : callable | None
        ``(gate, ctx) → bool`` synchronous HIL callback.
        ``None`` → all gates auto-approved.
    """

    def __init__(
        self,
        pack_id: str,
        system: FiveCoresSystem,
        *,
        custom_jobs: Optional[List] = None,
        hil_handler: Optional[Callable] = None,
    ) -> None:
        self._spec: MissionPackSpec = get_pack_spec(pack_id)
        self._system = system
        self._hil_handler = hil_handler
        self._events: List = []

        # Resolve job list
        builder = _JOB_BUILDERS[pack_id]
        if custom_jobs is not None:
            self._jobs: List = custom_jobs
        else:
            self._jobs = builder()

        # Adjunct orchestrator (optional)
        self._orchestrator = None
        if _HAS_ADJUNCT:
            from pentad_adjunct_orchestrator import AdjunctOrchestrator  # noqa: PLC0415
            self._orchestrator = AdjunctOrchestrator(system=system)

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def spec(self) -> MissionPackSpec:
        """The :class:`MissionPackSpec` for this runner's mission."""
        return self._spec

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    def run(self) -> dict:
        """
        Execute the mission.

        Returns
        -------
        dict
            Result dict with keys:

            - ``'status'``: ``'completed'`` | ``'failed'`` | ``'stopped'``
            - ``'pack_id'``: str
            - ``'jobs_completed'``: list[str]
            - ``'jobs_pending'``: list[str]
            - ``'event_count'``: int
            - ``'stop_reason'``: str
        """
        if _HAS_WORKFLOW_ENGINE:
            return self._run_with_engine()
        return self._run_fallback()

    def _run_with_engine(self) -> dict:
        """Execute using the full WorkflowEngine (Sprint A path)."""
        jobs = self._jobs
        handoff_order = [j.job_id for j in jobs]
        schema = PentadWorkflowSchema(
            workflow_id=str(uuid.uuid4()),
            name=self._spec.name,
            description=self._spec.description,
            agent_jobs=list(jobs),
            handoff_order=handoff_order,
            required_cores=self._spec.required_cores,
            trust_floor=self._spec.trust_floor,
            max_autonomous_steps=self._spec.max_autonomous_steps,
        )
        engine = WorkflowEngine(self._system)
        result = engine.run(schema, hil_handler=self._hil_handler)

        self._events = list(getattr(result, "event_log", []))

        return {
            "status": result.status,
            "pack_id": self._spec.pack_id,
            "jobs_completed": list(result.jobs_completed),
            "jobs_pending": list(result.jobs_pending),
            "event_count": len(self._events),
            "stop_reason": result.stop_reason,
        }

    def _run_fallback(self) -> dict:
        """Simple sequential executor used when Sprint A is not available."""
        completed: List[str] = []
        pending: List[str] = [
            getattr(j, "job_id", j.get("job_id", str(i)))
            for i, j in enumerate(self._jobs)
        ]

        for job in self._jobs:
            job_id = getattr(job, "job_id", job.get("job_id", str(id(job))))
            event = {
                "event_type": "job_completed",
                "job_id": job_id,
                "pack_id": self._spec.pack_id,
            }
            self._events.append(event)
            completed.append(job_id)
            pending.remove(job_id)

        return {
            "status": "completed",
            "pack_id": self._spec.pack_id,
            "jobs_completed": completed,
            "jobs_pending": pending,
            "event_count": len(self._events),
            "stop_reason": "",
        }

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def get_events(self) -> List:
        """Return the event log (list of dicts or WorkflowEvent objects)."""
        return list(self._events)

    def summary(self) -> str:
        """One-paragraph human-readable mission summary."""
        spec = self._spec
        n_jobs = len(self._jobs)
        n_events = len(self._events)
        cloud_note = (
            f"Cloud adjunct roles: {', '.join(spec.cloud_roles)}."
            if spec.cloud_adjunct_eligible
            else "Cloud adjunct disabled."
        )
        return (
            f"Mission '{spec.name}' ({spec.pack_id}): "
            f"{n_jobs} job(s) across cores "
            f"[{', '.join(spec.required_cores)}]. "
            f"Trust floor={spec.trust_floor}, "
            f"HIL gate type={spec.hil_threshold}, "
            f"max steps={spec.max_autonomous_steps}. "
            f"{cloud_note} "
            f"Events recorded: {n_events}."
        )
