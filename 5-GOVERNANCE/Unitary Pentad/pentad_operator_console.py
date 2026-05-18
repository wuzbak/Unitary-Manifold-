# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Unitary Pentad/pentad_operator_console.py
==========================================
Sprint B — Operator UI Console for the Unitary Pentad multi-agent system.

A pure-Python terminal operator console that renders a live status dashboard
for the Five-Cores System, Unitary Pentad, autopilot state, pending HIL gates,
audit event log, and agent task queue.  Uses plain ANSI escape codes only —
no curses, rich, or other external UI dependencies — so it works in any
terminal and in CI pipelines.

Public API
----------
ANSI constants : RST, BOLD, DIM, RED, GRN, YLW, CYN, WHT, MAG
phi_color(phi)            → ANSI color string for a radion value
bar(val, maxval, ...)     → progress-bar string
ConsoleState              → dataclass holding one render frame's data
render_console(state)     → multi-line string, one complete frame
print_console(state)      → clear terminal + print frame
PentadOperatorConsole     → stateful wrapper with snapshot/replay support
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

import datetime
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from five_cores.five_cores_system import (
    FiveCoresSystem,
    CoreLabel,
    CORE_LABELS,
    SystemStatus,
    SystemHealthReport,
)
from unitary_pentad import (
    PentadSystem,
    PentadLabel,
    PENTAD_LABELS,
    trust_modulation,
    pentad_defect,
)
from consciousness_autopilot import AutopilotUniverse, AutopilotMode

# ---------------------------------------------------------------------------
# ANSI color constants
# ---------------------------------------------------------------------------

RST: str = "\033[0m"
BOLD: str = "\033[1m"
DIM: str = "\033[2m"
RED: str = "\033[31m"
GRN: str = "\033[32m"
YLW: str = "\033[33m"
CYN: str = "\033[36m"
WHT: str = "\033[37m"
MAG: str = "\033[35m"

_WIDTH: int = 68  # console line width

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def phi_color(phi: float) -> str:
    """Return ANSI color code for a radion value.

    Parameters
    ----------
    phi : float — radion value ∈ [0, 1]

    Returns
    -------
    str — GRN if phi ≥ 0.7, YLW if phi ≥ 0.3, RED otherwise.
    """
    if phi >= 0.7:
        return GRN
    if phi >= 0.3:
        return YLW
    return RED


def bar(
    val: float,
    maxval: float = 1.0,
    width: int = 24,
    fill: str = "█",
    empty: str = "░",
) -> str:
    """Render a progress bar as a fixed-width string.

    Parameters
    ----------
    val    : float — current value.
    maxval : float — maximum value (default 1.0).
    width  : int   — total bar width in characters (default 24).
    fill   : str   — filled character (default "█").
    empty  : str   — empty character (default "░").

    Returns
    -------
    str — bar of exactly *width* characters.
    """
    if maxval <= 0:
        fraction = 0.0
    else:
        fraction = max(0.0, min(1.0, val / maxval))
    filled = round(fraction * width)
    return fill * filled + empty * (width - filled)


# ---------------------------------------------------------------------------
# Pentad body display metadata
# ---------------------------------------------------------------------------

_BODY_META: Dict[str, tuple] = {
    PentadLabel.UNIV:  ("◉", "UNIV ", "(Universe)  "),
    PentadLabel.BRAIN: ("◎", "BRAIN", "(Biology)   "),
    PentadLabel.HUMAN: ("★", "HUMAN", "(You)       "),
    PentadLabel.AI:    ("◆", "AI   ", "(Precision) "),
    PentadLabel.TRUST: ("♥", "TRUST", "(Coupling)  "),
}

_BODY_LABELS: Dict[str, str] = {
    PentadLabel.UNIV:  "STABLE",
    PentadLabel.BRAIN: "STABLE",
    PentadLabel.HUMAN: "← YOU ",
    PentadLabel.AI:    "STABLE",
    PentadLabel.TRUST: "OK    ",
}

# ---------------------------------------------------------------------------
# ConsoleState
# ---------------------------------------------------------------------------

@dataclass
class ConsoleState:
    """All data needed to render one frame of the Pentad Operator Console.

    Parameters
    ----------
    system        : FiveCoresSystem — the live five-cores system.
    pentad        : PentadSystem | None — optional Pentad for the bodies panel.
    autopilot     : AutopilotUniverse | None — optional autopilot state.
    pending_gates : list — HILGate-like objects (duck-typed on .gate_id,
                    .gate_type, .description).
    event_log     : list — WorkflowEvent-like objects (duck-typed on
                    .event_type, .job_id, .core_lane, .timestamp).
    task_queue    : list — AgentJob-like objects (duck-typed on .job_id,
                    .description, .core_lane, and optionally .status).
    max_events    : int — maximum recent events to display (default 10).
    """

    system: FiveCoresSystem
    pentad: Optional[PentadSystem]
    autopilot: Optional[AutopilotUniverse]
    pending_gates: list
    event_log: list
    task_queue: list
    max_events: int = 10


# ---------------------------------------------------------------------------
# Internal render helpers
# ---------------------------------------------------------------------------

def _divider(char: str = "═") -> str:
    return char * _WIDTH


def _heading(text: str) -> str:
    return f"{BOLD}{CYN}▶ {text}{RST}"


def _status_color(status: str) -> str:
    if status == SystemStatus.NOMINAL:
        return GRN
    if status == SystemStatus.DEGRADED:
        return YLW
    if status == SystemStatus.AWAITING_HIL:
        return MAG
    return RED  # HALTED


def _mode_color(mode: str) -> str:
    if mode == AutopilotMode.AUTOPILOT:
        return GRN
    if mode == AutopilotMode.SETTLING:
        return YLW
    return MAG  # AWAITING_SHIFT


def _latest_report(system: FiveCoresSystem) -> Optional[SystemHealthReport]:
    """Return the last SystemHealthReport in the system history, or None."""
    if system._history:
        return system._history[-1]
    return None


def _core_score(system: FiveCoresSystem, label: str) -> float:
    """Get current per-core score, falling back to 0.0 when no history."""
    report = _latest_report(system)
    if report is not None and label in report.per_core_scores:
        return report.per_core_scores[label]
    return 0.0


def _system_health(system: FiveCoresSystem) -> float:
    report = _latest_report(system)
    return report.health_score if report is not None else 0.0


def _system_status(system: FiveCoresSystem) -> str:
    return system._status


def _step_count(system: FiveCoresSystem) -> int:
    return system._step_count


# ---------------------------------------------------------------------------
# Panel renderers
# ---------------------------------------------------------------------------

_CORE_LABEL_WIDTH = 12  # max label display width with padding

_CORE_DISPLAY: List[tuple] = [
    (CoreLabel.STRATEGIC,   "STRATEGIC  "),
    (CoreLabel.OPERATIONAL, "OPERATIONAL"),
    (CoreLabel.SAFETY,      "SAFETY     "),
    (CoreLabel.SCIENCES,    "SCIENCES   "),
    (CoreLabel.BIOLOGICAL,  "BIOLOGICAL "),
]


def _render_five_cores(system: FiveCoresSystem) -> str:
    status = _system_status(system)
    h_sys = _system_health(system)
    phi_t = system.phi_trust
    sc = _status_color(status)

    lines = [
        _heading(
            f"FIVE-CORES SYSTEM   [{sc}{status}{RST}{BOLD}{CYN}]"
            f"   H_sys = {h_sys:.3f}   φ_trust = {phi_t:.3f}"
        ),
    ]
    for label, display in _CORE_DISPLAY:
        score = _core_score(system, label)
        col = phi_color(score)
        ok = "OK" if score >= 0.7 else ("WARN" if score >= 0.3 else "LOW ")
        lines.append(
            f"  {display}  {col}{bar(score)}{RST}  {score:.3f}   {ok}"
        )
    return "\n".join(lines)


def _render_pentad_panel(
    pentad: Optional[PentadSystem],
    autopilot: Optional[AutopilotUniverse],
) -> str:
    mode_str = "—"
    defect_str = "—"
    mode_col = DIM

    if autopilot is not None:
        mode_str = autopilot.mode.upper()
        mode_col = _mode_color(autopilot.mode)
        p = autopilot.core
    elif pentad is not None:
        p = pentad
    else:
        p = None

    if p is not None:
        try:
            defect_val = pentad_defect(p)
            defect_str = f"{defect_val:.6f}"
        except Exception:
            defect_str = "err"

    header = _heading(
        f"PENTAD BODIES   [{mode_col}{mode_str}{RST}{BOLD}{CYN}]"
        f"   defect = {defect_str}"
    )

    lines = [header]

    if p is None:
        lines.append(f"  {DIM}(no Pentad system attached){RST}")
        return "\n".join(lines)

    for lbl in PENTAD_LABELS:
        body = p.bodies.get(lbl)
        phi_val = body.phi if body is not None else 0.0
        icon, short, long_ = _BODY_META[lbl]
        col = phi_color(phi_val)
        tag = _BODY_LABELS[lbl]
        lines.append(
            f"  {icon} {short} {long_}  {phi_val:.3f}  "
            f"{col}{bar(phi_val)}{RST}  {tag}"
        )
    return "\n".join(lines)


def _render_pending_gates(pending_gates: list) -> str:
    header = _heading(f"PENDING APPROVALS ({len(pending_gates)})")
    if not pending_gates:
        return header + f"\n  {DIM}(none){RST}"
    lines = [header]
    for gate in pending_gates:
        gid = getattr(gate, "gate_id", str(gate))
        gtype = getattr(gate, "gate_type", "")
        desc = getattr(gate, "description", "")
        lines.append(f"  {MAG}[GATE]{RST} {gid}  {YLW}{gtype}{RST}  {desc}")
    return "\n".join(lines)


def _fmt_timestamp(ts: Any) -> str:
    """Format a timestamp (float monotonic or datetime) as HH:MM:SS."""
    try:
        # Try interpreting as wall-clock epoch float
        return datetime.datetime.fromtimestamp(float(ts)).strftime("%H:%M:%S")
    except Exception:
        return str(ts)[:8]


def _render_event_log(event_log: list, max_events: int) -> str:
    recent = event_log[-max_events:] if len(event_log) > max_events else event_log
    header = _heading(f"RECENT EVENTS ({len(recent)})")
    if not recent:
        return header + f"\n  {DIM}(none){RST}"
    lines = [header]
    for evt in recent:
        ts = _fmt_timestamp(getattr(evt, "timestamp", ""))
        etype = getattr(evt, "event_type", str(evt))
        jid = getattr(evt, "job_id", "")
        lane = getattr(evt, "core_lane", "")
        col = CYN if "started" in etype else (YLW if "gate" in etype else WHT)
        right = f"{lane:<10}" if lane else f"{jid:<22}"
        lines.append(
            f"  [{ts}] {col}{etype:<25}{RST}  {right}  {jid if lane else ''}"
        )
    return "\n".join(lines)


def _render_task_queue(task_queue: list) -> str:
    header = _heading(f"TASK QUEUE ({len(task_queue)})")
    if not task_queue:
        return header + f"\n  {DIM}(none){RST}"
    lines = [header]
    for i, job in enumerate(task_queue, 1):
        jid = getattr(job, "job_id", str(job))
        lane = getattr(job, "core_lane", "")
        status = getattr(job, "status", "queued")
        col = GRN if status == "completed" else (RED if status == "failed" else YLW)
        lines.append(
            f"  [{i}] {jid:<22}  {lane:<12}  {col}{status}{RST}"
        )
    return "\n".join(lines)


def _footer() -> str:
    return (
        f"{DIM}[Q] Quit   [A] Approve gate   [R] Reject gate   [S] Snapshot{RST}"
    )


# ---------------------------------------------------------------------------
# render_console / print_console
# ---------------------------------------------------------------------------

def render_console(state: ConsoleState) -> str:
    """Render a full console frame as a multi-line string.

    The output is suitable for ``print()`` or writing to a file/socket.
    It does **not** clear the terminal — the caller must do that if needed
    (``print_console`` handles clearing).

    Parameters
    ----------
    state : ConsoleState — snapshot of all data needed for one frame.

    Returns
    -------
    str — the complete frame, ready to be printed.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    step = _step_count(state.system)

    title_text = f"  PENTAD OPERATIONS CONSOLE   {now}   step {step}"
    title_pad = max(0, _WIDTH - len(title_text))
    title_line = f"{BOLD}{title_text}{' ' * title_pad}{RST}"

    sections = [
        _divider(),
        title_line,
        _divider(),
        "",
        _render_five_cores(state.system),
        "",
        _render_pentad_panel(state.pentad, state.autopilot),
        "",
        _render_pending_gates(state.pending_gates),
        "",
        _render_event_log(state.event_log, state.max_events),
        "",
        _render_task_queue(state.task_queue),
        "",
        _divider(),
        _footer(),
        _divider(),
    ]
    return "\n".join(sections)


def print_console(state: ConsoleState) -> None:
    """Clear the terminal (ANSI escape) and print one frame.

    Parameters
    ----------
    state : ConsoleState — snapshot of all data needed for one frame.
    """
    # ANSI clear-screen + home cursor
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
    print(render_console(state))


# ---------------------------------------------------------------------------
# PentadOperatorConsole
# ---------------------------------------------------------------------------

class PentadOperatorConsole:
    """Stateful console wrapper that tracks history and supports snapshot/replay.

    Parameters
    ----------
    system     : FiveCoresSystem — the live five-cores system to display.
    pentad     : PentadSystem | None — optional Pentad for the bodies panel.
    max_events : int — maximum recent events to display (default 10).
    max_history: int — maximum snapshot history to keep (default 100).
    """

    def __init__(
        self,
        system: FiveCoresSystem,
        *,
        pentad: Optional[PentadSystem] = None,
        max_events: int = 10,
        max_history: int = 100,
    ) -> None:
        self._system = system
        self._pentad = pentad
        self._max_events = max_events
        self._max_history = max_history

        self._autopilot: Optional[AutopilotUniverse] = None
        self._pending_gates: list = []
        self._event_log: list = []
        self._task_queue: list = []

        self._history: List[dict] = []

    # ------------------------------------------------------------------
    # State update
    # ------------------------------------------------------------------

    def update(
        self,
        *,
        autopilot: Optional[AutopilotUniverse] = None,
        pending_gates: Optional[list] = None,
        event_log: Optional[list] = None,
        task_queue: Optional[list] = None,
    ) -> None:
        """Update internal state from external data.

        Parameters
        ----------
        autopilot     : AutopilotUniverse | None — current autopilot state.
        pending_gates : list | None — HIL gates awaiting approval.
        event_log     : list | None — audit event log.
        task_queue    : list | None — agent job queue.
        """
        if autopilot is not None:
            self._autopilot = autopilot
        if pending_gates is not None:
            self._pending_gates = list(pending_gates)
        if event_log is not None:
            self._event_log = list(event_log)
        if task_queue is not None:
            self._task_queue = list(task_queue)

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _make_state(self) -> ConsoleState:
        return ConsoleState(
            system=self._system,
            pentad=self._pentad,
            autopilot=self._autopilot,
            pending_gates=self._pending_gates,
            event_log=self._event_log,
            task_queue=self._task_queue,
            max_events=self._max_events,
        )

    def render(self) -> str:
        """Return the current frame as a string.

        Returns
        -------
        str — complete rendered frame.
        """
        return render_console(self._make_state())

    def print_frame(self) -> None:
        """Clear the terminal and print the current frame."""
        print_console(self._make_state())

    # ------------------------------------------------------------------
    # Snapshot / replay
    # ------------------------------------------------------------------

    def snapshot(self) -> dict:
        """Capture a plain-dict snapshot of current state for replay.

        The snapshot stores:
        - system: step_count, phi_trust, status, health_score, per_core_scores
        - pentad: per-body phi values (or None)
        - autopilot: mode (or None)
        - pending_gates: list of dicts
        - event_log: list of dicts
        - task_queue: list of dicts

        Returns
        -------
        dict — serialisable snapshot.
        """
        report = _latest_report(self._system)

        sys_snap: dict = {
            "step_count": self._system._step_count,
            "phi_trust": self._system.phi_trust,
            "status": self._system._status,
            "health_score": report.health_score if report else 0.0,
            "per_core_scores": dict(report.per_core_scores) if report else {},
        }

        pentad_snap = None
        p = self._pentad
        if self._autopilot is not None:
            p = self._autopilot.core
        if p is not None:
            try:
                defect = pentad_defect(p)
            except Exception:
                defect = 0.0
            pentad_snap = {
                "bodies": {
                    lbl: p.bodies[lbl].phi for lbl in PENTAD_LABELS if lbl in p.bodies
                },
                "defect": defect,
            }

        ap_snap = None
        if self._autopilot is not None:
            ap_snap = {"mode": self._autopilot.mode}

        def _gate_dict(g: Any) -> dict:
            return {
                "gate_id": getattr(g, "gate_id", str(g)),
                "gate_type": getattr(g, "gate_type", ""),
                "description": getattr(g, "description", ""),
            }

        def _event_dict(e: Any) -> dict:
            return {
                "timestamp": getattr(e, "timestamp", ""),
                "event_type": getattr(e, "event_type", str(e)),
                "job_id": getattr(e, "job_id", ""),
                "core_lane": getattr(e, "core_lane", ""),
            }

        def _job_dict(j: Any) -> dict:
            return {
                "job_id": getattr(j, "job_id", str(j)),
                "description": getattr(j, "description", ""),
                "core_lane": getattr(j, "core_lane", ""),
                "status": getattr(j, "status", "queued"),
            }

        snap = {
            "system": sys_snap,
            "pentad": pentad_snap,
            "autopilot": ap_snap,
            "pending_gates": [_gate_dict(g) for g in self._pending_gates],
            "event_log": [_event_dict(e) for e in self._event_log],
            "task_queue": [_job_dict(j) for j in self._task_queue],
            "max_events": self._max_events,
        }

        # Store in rolling history
        self._history.append(snap)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        return snap

    def replay_frame(self, snapshot: dict) -> str:
        """Render a previously captured snapshot as a string.

        Parameters
        ----------
        snapshot : dict — as returned by :meth:`snapshot`.

        Returns
        -------
        str — rendered frame for the given snapshot.
        """
        sys_data = snapshot.get("system", {})
        pentad_data = snapshot.get("pentad")
        ap_data = snapshot.get("autopilot")
        max_ev = snapshot.get("max_events", self._max_events)

        # Build duck-typed proxy objects for the renderer
        class _SysProxy:
            def __init__(self, d: dict) -> None:
                self._step_count = d.get("step_count", 0)
                self._status = d.get("status", SystemStatus.NOMINAL)
                self._history = [_ReportProxy(d)]
                self.phi_trust = d.get("phi_trust", 1.0)

        class _ReportProxy:
            def __init__(self, d: dict) -> None:
                self.health_score = d.get("health_score", 0.0)
                self.per_core_scores = d.get("per_core_scores", {})

        class _BodyProxy:
            def __init__(self, phi: float) -> None:
                self.phi = phi

        class _PentadProxy:
            def __init__(self, d: dict) -> None:
                self.bodies = {
                    lbl: _BodyProxy(phi)
                    for lbl, phi in d.get("bodies", {}).items()
                }
                self._defect = d.get("defect", 0.0)

        class _ApProxy:
            def __init__(self, d: dict) -> None:
                self.mode = d.get("mode", AutopilotMode.AUTOPILOT)
                self.core = None  # will be overwritten below

        sys_proxy = _SysProxy(sys_data)

        pentad_proxy = None
        if pentad_data is not None:
            pentad_proxy = _PentadProxy(pentad_data)

        ap_proxy = None
        if ap_data is not None:
            ap_proxy = _ApProxy(ap_data)
            if pentad_proxy is not None:
                ap_proxy.core = pentad_proxy

        # Build gate/event/job proxies
        class _GateProxy:
            def __init__(self, d: dict) -> None:
                self.gate_id = d.get("gate_id", "")
                self.gate_type = d.get("gate_type", "")
                self.description = d.get("description", "")

        class _EventProxy:
            def __init__(self, d: dict) -> None:
                self.timestamp = d.get("timestamp", "")
                self.event_type = d.get("event_type", "")
                self.job_id = d.get("job_id", "")
                self.core_lane = d.get("core_lane", "")

        class _JobProxy:
            def __init__(self, d: dict) -> None:
                self.job_id = d.get("job_id", "")
                self.description = d.get("description", "")
                self.core_lane = d.get("core_lane", "")
                self.status = d.get("status", "queued")

        gates = [_GateProxy(g) for g in snapshot.get("pending_gates", [])]
        events = [_EventProxy(e) for e in snapshot.get("event_log", [])]
        jobs = [_JobProxy(j) for j in snapshot.get("task_queue", [])]

        state = ConsoleState(
            system=sys_proxy,  # type: ignore[arg-type]
            pentad=pentad_proxy,  # type: ignore[arg-type]
            autopilot=ap_proxy,   # type: ignore[arg-type]
            pending_gates=gates,
            event_log=events,
            task_queue=jobs,
            max_events=max_ev,
        )
        return render_console(state)
