# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/scheduler.py
================
Unitary Operating System — Geodesic Process Scheduler

Conventional OS schedulers use heuristics (priority queues, CFS) to guess
which process to run next.  The **GeodesicScheduler** instead treats each
process as a *geodesic* on the 5D Kaluza–Klein manifold: processes whose
φ-weighted trajectory aligns with the manifold curvature get CPU quanta;
those whose state deviates from the geodesic flow are deferred until the
manifold curvature supports them.

The scheduler operates entirely in numpy — no heavy dependencies.

Key concepts
------------
ProcessGeodesic
    A lightweight descriptor for a runnable process: a numeric ``pid``,
    a ``priority`` weight (higher = more important), a ``phi_weight``
    encoding the process's φ-field affinity, and a ``state_vector`` that
    records the process's last known position in 5D phase space.

GeodesicScheduler
    Maintains the run queue and selects the next process via the
    **manifold affinity score** — a dot product of the process state
    vector with the current manifold φ-gradient field.  This replaces
    preemptive multitasking with *curvature-aligned scheduling*.

Public API
----------
ProcessGeodesic(pid, priority, phi_weight, state_vector)
    Process descriptor.

GeodesicScheduler(max_slots)
    Scheduler instance.

GeodesicScheduler.enqueue(proc)
    Add a process to the run queue.

GeodesicScheduler.dequeue(pid)
    Remove a process from the run queue.

GeodesicScheduler.next_process(phi_field)
    Select the highest-affinity runnable process given the current φ field.

GeodesicScheduler.update_state(pid, new_state)
    Update the phase-space state vector for a process after a time step.

GeodesicScheduler.queue_depth()
    Return the number of processes currently queued.
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

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from UOS.constants import (
    UOS_PROCESS_SLOTS,
    WINDING_NUMBER,
    K_CS,
    PHI_BACKGROUND,
)

# Phase-space dimension: 5 (one per manifold dimension)
PHASE_DIM: int = WINDING_NUMBER


# ---------------------------------------------------------------------------
# ProcessGeodesic — a runnable process descriptor
# ---------------------------------------------------------------------------

@dataclass
class ProcessGeodesic:
    """Descriptor for a UOS process (geodesic on the manifold).

    Parameters
    ----------
    pid : int
        Unique process identifier.
    priority : float
        Scheduling weight in [0, 1].  Higher = more important.
    phi_weight : float
        The process's affinity for the radion field; governs how strongly
        the manifold curvature attracts this process to the CPU.
    state_vector : ndarray, shape (PHASE_DIM,)
        Current position in 5D phase space.  Initialised to small
        random values if not supplied.
    """
    pid: int
    priority: float = 1.0
    phi_weight: float = PHI_BACKGROUND
    state_vector: np.ndarray = field(default_factory=lambda: np.zeros(PHASE_DIM))

    def __post_init__(self) -> None:
        self.state_vector = np.asarray(self.state_vector, dtype=float)
        if self.state_vector.shape != (PHASE_DIM,):
            raise ValueError(
                f"state_vector must have shape ({PHASE_DIM},); "
                f"got {self.state_vector.shape}."
            )
        self.priority = float(np.clip(self.priority, 0.0, 1.0))
        self.phi_weight = float(self.phi_weight)

    def affinity_score(self, phi_gradient: np.ndarray) -> float:
        """Compute the manifold affinity score for this process.

        Score = priority × phi_weight × ⟨state_vector, phi_gradient⟩

        A higher score means the manifold curvature is aligned with the
        process trajectory → the process should run next.

        Parameters
        ----------
        phi_gradient : ndarray, shape (PHASE_DIM,)
            Spatial gradient of φ evaluated at the process's grid location.

        Returns
        -------
        float
        """
        phi_gradient = np.asarray(phi_gradient, dtype=float)[:PHASE_DIM]
        dot = float(np.dot(self.state_vector, phi_gradient))
        return self.priority * self.phi_weight * (1.0 + dot)


# ---------------------------------------------------------------------------
# GeodesicScheduler — the UOS scheduling engine
# ---------------------------------------------------------------------------

class GeodesicScheduler:
    """Curvature-aligned process scheduler.

    Parameters
    ----------
    max_slots : int
        Maximum number of simultaneously queued processes.
        Default: ``UOS_PROCESS_SLOTS`` (74).

    Examples
    --------
    >>> sched = GeodesicScheduler()
    >>> proc = ProcessGeodesic(pid=1, priority=0.9)
    >>> sched.enqueue(proc)
    >>> phi_field = np.ones(32)
    >>> chosen = sched.next_process(phi_field)
    >>> chosen.pid
    1
    """

    def __init__(self, max_slots: int = UOS_PROCESS_SLOTS) -> None:
        self.max_slots = max_slots
        self._queue: Dict[int, ProcessGeodesic] = {}

    # ------------------------------------------------------------------
    # Queue management
    # ------------------------------------------------------------------

    def enqueue(self, proc: ProcessGeodesic) -> None:
        """Add a process to the run queue.

        Parameters
        ----------
        proc : ProcessGeodesic

        Raises
        ------
        OverflowError
            If the queue is already at ``max_slots`` capacity.
        KeyError
            If a process with the same PID is already queued.
        """
        if len(self._queue) >= self.max_slots:
            raise OverflowError(
                f"Scheduler queue full ({self.max_slots} slots).  "
                "No more geodesic lanes available."
            )
        if proc.pid in self._queue:
            raise KeyError(f"Process {proc.pid} is already in the run queue.")
        self._queue[proc.pid] = proc

    def dequeue(self, pid: int) -> ProcessGeodesic:
        """Remove and return a process from the run queue.

        Parameters
        ----------
        pid : int

        Raises
        ------
        KeyError
            If the process is not in the queue.
        """
        if pid not in self._queue:
            raise KeyError(f"Process {pid} is not in the run queue.")
        return self._queue.pop(pid)

    # ------------------------------------------------------------------
    # Geodesic selection
    # ------------------------------------------------------------------

    def next_process(self, phi_field: np.ndarray) -> Optional[ProcessGeodesic]:
        """Select the highest manifold-affinity runnable process.

        The φ gradient is computed from the supplied ``phi_field`` array
        (spatial derivative via central differences).  The process with the
        maximum affinity score is returned; it remains in the queue (it is
        the caller's responsibility to remove it when it yields the CPU).

        Parameters
        ----------
        phi_field : ndarray, shape (N,)
            Radion field over the spatial grid.

        Returns
        -------
        ProcessGeodesic or None
            The next process to execute, or None if the queue is empty.
        """
        if not self._queue:
            return None

        # Compute φ-gradient and project onto PHASE_DIM
        grad_phi = self._phi_gradient(phi_field)

        best_proc: Optional[ProcessGeodesic] = None
        best_score: float = -np.inf
        for proc in self._queue.values():
            score = proc.affinity_score(grad_phi)
            if score > best_score:
                best_score = score
                best_proc = proc
        return best_proc

    # ------------------------------------------------------------------
    # State update
    # ------------------------------------------------------------------

    def update_state(self, pid: int, new_state: np.ndarray) -> None:
        """Update the phase-space state vector for a process.

        Call this after each time step to keep the process's position on
        the manifold current.

        Parameters
        ----------
        pid : int
        new_state : ndarray, shape (PHASE_DIM,)
        """
        if pid not in self._queue:
            raise KeyError(f"Process {pid} not found in run queue.")
        new_state = np.asarray(new_state, dtype=float)[:PHASE_DIM]
        if new_state.shape != (PHASE_DIM,):
            new_state = np.pad(new_state, (0, PHASE_DIM - len(new_state)))
        self._queue[pid].state_vector = new_state

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def queue_depth(self) -> int:
        """Return the current number of queued processes."""
        return len(self._queue)

    def queue_pids(self) -> List[int]:
        """Return a sorted list of currently queued PIDs."""
        return sorted(self._queue.keys())

    def queue_summary(self) -> List[Dict]:
        """Return a list of dicts describing each queued process."""
        return [
            {
                "pid": p.pid,
                "priority": p.priority,
                "phi_weight": p.phi_weight,
            }
            for p in self._queue.values()
        ]

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _phi_gradient(phi_field: np.ndarray) -> np.ndarray:
        """Compute a PHASE_DIM-length gradient vector from the φ field."""
        phi = np.asarray(phi_field, dtype=float)
        # Central differences; wrap with periodic BC
        grad_full = np.empty_like(phi)
        grad_full[1:-1] = (phi[2:] - phi[:-2]) / 2.0
        grad_full[0] = (phi[1] - phi[-1]) / 2.0
        grad_full[-1] = (phi[0] - phi[-2]) / 2.0
        # Aggregate to PHASE_DIM by block-averaging
        blocks = np.array_split(grad_full, PHASE_DIM)
        return np.array([float(np.mean(b)) for b in blocks])
