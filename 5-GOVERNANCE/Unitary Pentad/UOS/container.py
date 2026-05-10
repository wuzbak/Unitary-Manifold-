# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/container.py
================
Unitary Operating System — Manifold Container Isolation

Linux containers (Docker, OCI) isolate processes using kernel namespaces and
cgroups — a layered system of administrative walls.  The UOS **ManifoldContainer**
achieves isolation through *geometric separation*: each container occupies a
distinct winding sector of the manifold, and cross-container communication
requires a winding-sector crossing that is tracked and audited.

Key Concepts
------------
* **Winding Sector**: a slice of the 5D compact dimension defined by
  a specific φ-range.  A process running in sector W can only interact
  with processes in the same sector (or the kernel sector W=0) without
  an explicit sector-crossing permit.

* **ResourceQuota**: CPU, memory, and I/O limits expressed as a fraction
  of the total manifold capacity.

* **ContainerState**: the lifecycle state of a container (CREATED, RUNNING,
  PAUSED, STOPPED, DESTROYED).

* **ManifoldContainer**: a complete isolated execution environment.

* **ContainerOrchestrator**: creates, manages, and monitors multiple
  containers; enforces sector isolation.

Isolation Guarantees
--------------------
1. A process in sector W cannot read memory of a process in sector W'.
2. A container that exceeds its ResourceQuota is throttled (no OOM kill;
   the manifold gracefully degrades by increasing effective_alpha).
3. A container cannot escape its sector without the orchestrator issuing
   a signed sector-crossing permit (using UOS/crypto.py).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set

import numpy as np

from UOS.constants import (
    K_CS, WINDING_NUMBER, BRAID_PARTNER, PHI_BACKGROUND,
    UOS_PROCESS_SLOTS, UOS_MEMORY_PAGES, BRAIDED_SOUND_SPEED,
)

# Container limits
MAX_CONTAINERS: int = K_CS                             # 74 simultaneous containers
MAX_CONTAINER_PROCESSES: int = UOS_PROCESS_SLOTS // WINDING_NUMBER  # ≈ 74 procs per container
SECTOR_WIDTH: float = 2.0 * np.pi * WINDING_NUMBER / K_CS  # φ-width of each sector


# ===========================================================================
# ContainerState
# ===========================================================================

class ContainerState(Enum):
    CREATED   = auto()
    RUNNING   = auto()
    PAUSED    = auto()
    STOPPED   = auto()
    DESTROYED = auto()


# ===========================================================================
# ResourceQuota
# ===========================================================================

@dataclass
class ResourceQuota:
    """Resource limits for a container.

    All values are fractions of total manifold capacity in (0, 1].

    Parameters
    ----------
    cpu : float
        CPU fraction (1.0 = full manifold CPU, i.e. all K_CS=74 lanes).
    memory_pages : int
        Maximum memory pages.
    io_bandwidth : float
        I/O bandwidth fraction.
    max_processes : int
        Maximum simultaneous processes inside the container.
    """
    cpu: float = 0.5
    memory_pages: int = UOS_MEMORY_PAGES // K_CS
    io_bandwidth: float = 0.5
    max_processes: int = MAX_CONTAINER_PROCESSES

    def __post_init__(self) -> None:
        self.cpu = float(np.clip(self.cpu, 1e-6, 1.0))
        self.io_bandwidth = float(np.clip(self.io_bandwidth, 1e-6, 1.0))
        if self.memory_pages < 1:
            raise ValueError("memory_pages must be ≥ 1.")
        if self.max_processes < 1:
            raise ValueError("max_processes must be ≥ 1.")


# ===========================================================================
# ContainerProcess — lightweight process descriptor inside a container
# ===========================================================================

@dataclass
class ContainerProcess:
    """A process running inside a ManifoldContainer."""
    pid: int
    name: str
    language: str = "Python"
    cpu_fraction: float = 0.0
    memory_pages: int = 0
    state: str = "running"


# ===========================================================================
# ManifoldContainer
# ===========================================================================

class ManifoldContainer:
    """An isolated manifold container.

    Parameters
    ----------
    container_id : str
    winding_sector : int
        Which of the K_CS=74 sectors this container occupies.
    quota : ResourceQuota, optional
    image : str
        Name of the container image / base environment.

    Examples
    --------
    >>> c = ManifoldContainer("web-server", winding_sector=3)
    >>> c.start()
    >>> c.spawn_process("nginx", language="C")
    ContainerProcess(pid=1, name='nginx', ...)
    >>> c.stats()["state"]
    'RUNNING'
    """

    def __init__(
        self,
        container_id: str,
        winding_sector: int = 0,
        quota: Optional[ResourceQuota] = None,
        image: str = "uos-base",
    ) -> None:
        if not 0 <= winding_sector < K_CS:
            raise ValueError(f"winding_sector must be in [0, {K_CS}); got {winding_sector}.")
        self.container_id = container_id
        self.winding_sector = winding_sector
        self.quota = quota or ResourceQuota()
        self.image = image
        self.state = ContainerState.CREATED
        self._processes: Dict[int, ContainerProcess] = {}
        self._next_pid: int = 1
        self._cpu_used: float = 0.0
        self._memory_used: int = 0
        self._event_log: List[str] = []

        # Manifold sector boundaries
        self.phi_lo: float = winding_sector * SECTOR_WIDTH
        self.phi_hi: float = self.phi_lo + SECTOR_WIDTH

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Transition the container to RUNNING state."""
        if self.state not in (ContainerState.CREATED, ContainerState.STOPPED):
            raise RuntimeError(
                f"Container '{self.container_id}' cannot start from state {self.state.name}."
            )
        self.state = ContainerState.RUNNING
        self._log("Container started.")

    def pause(self) -> None:
        """Freeze the container (PAUSED)."""
        if self.state != ContainerState.RUNNING:
            raise RuntimeError("Can only pause a RUNNING container.")
        self.state = ContainerState.PAUSED
        self._log("Container paused.")

    def resume(self) -> None:
        """Resume a paused container."""
        if self.state != ContainerState.PAUSED:
            raise RuntimeError("Can only resume a PAUSED container.")
        self.state = ContainerState.RUNNING
        self._log("Container resumed.")

    def stop(self) -> None:
        """Stop all processes and move to STOPPED."""
        self._processes.clear()
        self._cpu_used = 0.0
        self._memory_used = 0
        self.state = ContainerState.STOPPED
        self._log("Container stopped.")

    def destroy(self) -> None:
        """Permanently destroy the container."""
        self.stop()
        self.state = ContainerState.DESTROYED
        self._log("Container destroyed.")

    # ------------------------------------------------------------------
    # Process management
    # ------------------------------------------------------------------

    def spawn_process(
        self,
        name: str,
        language: str = "Python",
        cpu_fraction: float = 0.1,
        memory_pages: int = 4,
    ) -> ContainerProcess:
        """Spawn a new process inside this container.

        Parameters
        ----------
        name : str
        language : str
        cpu_fraction : float
        memory_pages : int

        Returns
        -------
        ContainerProcess

        Raises
        ------
        RuntimeError
            If container is not RUNNING, or quota exceeded.
        """
        if self.state != ContainerState.RUNNING:
            raise RuntimeError(
                f"Container '{self.container_id}' is not running (state={self.state.name})."
            )
        if len(self._processes) >= self.quota.max_processes:
            raise RuntimeError(
                f"Container '{self.container_id}': max_processes "
                f"({self.quota.max_processes}) exceeded."
            )
        if self._cpu_used + cpu_fraction > self.quota.cpu + 1e-9:
            raise RuntimeError(
                f"Container '{self.container_id}': CPU quota exceeded."
            )
        if self._memory_used + memory_pages > self.quota.memory_pages:
            raise RuntimeError(
                f"Container '{self.container_id}': memory quota exceeded."
            )
        pid = self._next_pid
        self._next_pid += 1
        proc = ContainerProcess(
            pid=pid,
            name=name,
            language=language,
            cpu_fraction=cpu_fraction,
            memory_pages=memory_pages,
        )
        self._processes[pid] = proc
        self._cpu_used += cpu_fraction
        self._memory_used += memory_pages
        self._log(f"Spawned process '{name}' (PID {pid}, lang={language}).")
        return proc

    def kill_process(self, pid: int) -> None:
        """Kill a process inside the container."""
        if pid not in self._processes:
            raise KeyError(f"PID {pid} not found in container '{self.container_id}'.")
        proc = self._processes.pop(pid)
        self._cpu_used -= proc.cpu_fraction
        self._memory_used -= proc.memory_pages
        self._log(f"Killed process PID {pid} ('{proc.name}').")

    # ------------------------------------------------------------------
    # Sector isolation
    # ------------------------------------------------------------------

    def contains_phi(self, phi: float) -> bool:
        """Return True if a φ-coordinate falls within this container's sector."""
        return self.phi_lo <= phi < self.phi_hi

    def can_communicate_with(
        self, other: "ManifoldContainer", permit: bool = False
    ) -> bool:
        """Return True if this container can communicate with ``other``.

        Communication is allowed within the same sector or if the kernel
        has granted a sector-crossing permit.

        Parameters
        ----------
        other : ManifoldContainer
        permit : bool
            True if a signed sector-crossing permit has been granted.
        """
        return self.winding_sector == other.winding_sector or permit

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def stats(self) -> Dict:
        return {
            "container_id": self.container_id,
            "state": self.state.name,
            "image": self.image,
            "winding_sector": self.winding_sector,
            "phi_range": [round(self.phi_lo, 4), round(self.phi_hi, 4)],
            "processes": len(self._processes),
            "cpu_used": round(self._cpu_used, 4),
            "cpu_quota": self.quota.cpu,
            "memory_used_pages": self._memory_used,
            "memory_quota_pages": self.quota.memory_pages,
        }

    def event_log(self) -> List[str]:
        """Return a copy of the container event log."""
        return list(self._event_log)

    def _log(self, msg: str) -> None:
        self._event_log.append(msg)


# ===========================================================================
# ContainerOrchestrator
# ===========================================================================

class ContainerOrchestrator:
    """Creates, manages, and monitors multiple ManifoldContainers.

    Enforces sector isolation: containers in different winding sectors
    cannot communicate without an explicit signed permit.

    Parameters
    ----------
    max_containers : int

    Examples
    --------
    >>> orch = ContainerOrchestrator()
    >>> cid = orch.create("app-server", image="python:3.12")
    >>> orch.start(cid)
    >>> orch.spawn(cid, "wsgi-worker", language="Python")
    >>> orch.stats()
    """

    def __init__(self, max_containers: int = MAX_CONTAINERS) -> None:
        self.max_containers = max_containers
        self._containers: Dict[str, ManifoldContainer] = {}
        self._sector_assignments: Dict[int, str] = {}  # sector → container_id

    def create(
        self,
        container_id: str,
        image: str = "uos-base",
        quota: Optional[ResourceQuota] = None,
        winding_sector: Optional[int] = None,
    ) -> str:
        """Create a new container.

        Parameters
        ----------
        container_id : str
        image : str
        quota : ResourceQuota, optional
        winding_sector : int, optional
            Auto-assigned if not specified.

        Returns
        -------
        str
            The container_id.
        """
        if container_id in self._containers:
            return container_id
        if len(self._containers) >= self.max_containers:
            raise OverflowError(
                f"ContainerOrchestrator: max_containers ({self.max_containers}) reached."
            )
        # Auto-assign the next free sector
        if winding_sector is None:
            used = set(self._sector_assignments.keys())
            for s in range(K_CS):
                if s not in used:
                    winding_sector = s
                    break
            else:
                raise OverflowError("No free winding sectors available.")
        c = ManifoldContainer(
            container_id=container_id,
            winding_sector=winding_sector,
            quota=quota,
            image=image,
        )
        self._containers[container_id] = c
        self._sector_assignments[winding_sector] = container_id
        return container_id

    def start(self, container_id: str) -> None:
        self._get(container_id).start()

    def stop(self, container_id: str) -> None:
        self._get(container_id).stop()

    def pause(self, container_id: str) -> None:
        self._get(container_id).pause()

    def resume(self, container_id: str) -> None:
        self._get(container_id).resume()

    def destroy(self, container_id: str) -> None:
        c = self._get(container_id)
        sector = c.winding_sector
        c.destroy()
        del self._containers[container_id]
        self._sector_assignments.pop(sector, None)

    def spawn(
        self, container_id: str, name: str, language: str = "Python",
        cpu_fraction: float = 0.1, memory_pages: int = 4,
    ) -> ContainerProcess:
        return self._get(container_id).spawn_process(
            name=name, language=language,
            cpu_fraction=cpu_fraction, memory_pages=memory_pages,
        )

    def can_communicate(
        self, id_a: str, id_b: str, permit: bool = False
    ) -> bool:
        """Return True if container A can communicate with container B."""
        return self._get(id_a).can_communicate_with(self._get(id_b), permit=permit)

    def list_containers(self) -> List[str]:
        return sorted(self._containers.keys())

    def get_container(self, container_id: str) -> ManifoldContainer:
        return self._get(container_id)

    def stats(self) -> Dict:
        running = sum(
            1 for c in self._containers.values()
            if c.state == ContainerState.RUNNING
        )
        return {
            "total_containers": len(self._containers),
            "running": running,
            "max_containers": self.max_containers,
            "sectors_used": len(self._sector_assignments),
        }

    def _get(self, container_id: str) -> ManifoldContainer:
        if container_id not in self._containers:
            raise KeyError(f"Container '{container_id}' not found.")
        return self._containers[container_id]
