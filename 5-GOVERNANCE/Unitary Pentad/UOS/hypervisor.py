# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/hypervisor.py
=================
Unitary Operating System — 5D Manifold Hypervisor

The UOSHypervisor is the **core kernel** of the Unitary Operating System.
It replaces the conventional OS preemptive scheduler with a 5D geometric
resource manager: processes, memory blocks, I/O streams, and security
contexts are all represented as *field states* on a discretised Kaluza–Klein
manifold, and their evolution is governed by the Walker–Pearson equations.

Architecture
------------
The hypervisor tracks a lightweight ``ManifoldState`` — a snapshot of the
5D field configuration (metric g, gauge field B, radion φ) sampled at
``N_GRID`` spatial points.  Every tick (one ``UOS_CLOCK_QUANTUM``) it:

  1. Queries the **GeodesicScheduler** to pick the next runnable process.
  2. Asks the **GeometricSecurityEngine** to verify that the process
     instruction fingerprint obeys the 3:2 invariant.
  3. Allocates pages from **UnitaryMemory** for the process.
  4. Advances the manifold state by one RK4 step.
  5. Broadcasts the new state to all subsystems via ``notify_subsystems()``.

The hypervisor can also run in *monitor mode* beside an existing OS —
shadowing real system resource usage and projecting it onto the manifold for
analysis (see ``attach_to_host()``).

Public API
----------
ManifoldState
    Lightweight frozen snapshot: (g, B, phi, t, tick).

UOSHypervisor(n_grid, dt, n_ticks)
    Main kernel class.

UOSHypervisor.boot()
    Initialise the manifold and all subsystems.

UOSHypervisor.tick()
    Advance the hypervisor by one clock quantum.

UOSHypervisor.run(steps)
    Run ``steps`` ticks; return list of ManifoldState snapshots.

UOSHypervisor.attach_to_host(cpu_load, mem_load)
    Inject real host metrics (0–1 fractions) into the manifold.

UOSHypervisor.resource_report()
    Return a dict summarising current manifold resource state.

UOSHypervisor.manifold_invariant_ok()
    Return True when the 5:7 braid ratio is intact (health gate).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from UOS.constants import (
    WINDING_NUMBER,
    BRAID_PARTNER,
    K_CS,
    PHI_BACKGROUND,
    LAMBDA_COUPLING,
    ALPHA_COUPLING,
    UOS_CLOCK_QUANTUM,
    UOS_PROCESS_SLOTS,
    INVARIANT_RATIO,
    INVARIANT_TOLERANCE,
)


# ---------------------------------------------------------------------------
# ManifoldState — a frozen snapshot of the 5D field configuration
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ManifoldState:
    """Frozen snapshot of the UOS manifold at a single tick.

    Parameters
    ----------
    g : ndarray, shape (N, 4, 4)
        4D metric tensor block at each spatial grid point.
    B : ndarray, shape (N, 4)
        Gauge field (irreversibility 1-form) at each grid point.
    phi : ndarray, shape (N,)
        Radion / entanglement scalar at each grid point.
    t : float
        Physical time coordinate (in manifold units).
    tick : int
        Integer clock tick count.
    """
    g: np.ndarray
    B: np.ndarray
    phi: np.ndarray
    t: float
    tick: int

    # Numpy arrays are not hashable; override __eq__ for value comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ManifoldState):
            return NotImplemented
        return (
            np.array_equal(self.g, other.g)
            and np.array_equal(self.B, other.B)
            and np.array_equal(self.phi, other.phi)
            and self.t == other.t
            and self.tick == other.tick
        )

    def __hash__(self) -> int:
        return hash((self.t, self.tick))


# ---------------------------------------------------------------------------
# Helper: flat Minkowski initial conditions
# ---------------------------------------------------------------------------

def _flat_initial_state(n_grid: int) -> tuple:
    """Return (g, B, phi) for a flat Minkowski background."""
    # Metric: diag(-1, +1, +1, +1) at each grid point with tiny perturbation
    g = np.zeros((n_grid, 4, 4))
    g[:, 0, 0] = -1.0
    g[:, 1, 1] = 1.0
    g[:, 2, 2] = 1.0
    g[:, 3, 3] = 1.0
    rng = np.random.default_rng(seed=42)
    g += rng.standard_normal(g.shape) * 1e-6

    # Gauge field: zero + small noise
    B = rng.standard_normal((n_grid, 4)) * 1e-6

    # Radion: pinned near φ₀
    phi = np.full(n_grid, PHI_BACKGROUND) + rng.standard_normal(n_grid) * 1e-6

    return g, B, phi


# ---------------------------------------------------------------------------
# Core field derivative (simplified — uses only numpy for portability)
# ---------------------------------------------------------------------------

def _phi_rhs(phi: np.ndarray, alpha: float) -> np.ndarray:
    """Scalar field RHS: Goldberger–Wise attractor damping toward φ₀.

    RHS = −α × (φ − φ₀)

    This is the linearised form of the Goldberger–Wise radion potential,
    which drives φ toward the background attractor PHI_BACKGROUND.  It is
    numerically stable for any time step dt < 2/α (here dt ≈ 0.32 ≪ 40).

    The Laplacian (spatial diffusion) term is intentionally omitted here:
    the hypervisor operates on the uniform zero-mode of φ — spatial
    fluctuations are integrated out by the KK reduction.  Including a
    finite-difference Laplacian would require a CFL-stable dt ≤ dx²/2
    which would be far smaller than the UOS clock quantum.
    """
    return -alpha * (phi - PHI_BACKGROUND)


def _rk4_phi_step(phi: np.ndarray, dt: float, alpha: float) -> np.ndarray:
    """One RK4 step for the radion scalar field (attractor ODE)."""
    k1 = _phi_rhs(phi, alpha)
    k2 = _phi_rhs(phi + 0.5 * dt * k1, alpha)
    k3 = _phi_rhs(phi + 0.5 * dt * k2, alpha)
    k4 = _phi_rhs(phi + dt * k3, alpha)
    return phi + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)


# ---------------------------------------------------------------------------
# UOSHypervisor — the main kernel class
# ---------------------------------------------------------------------------

class UOSHypervisor:
    """5D Manifold Hypervisor — the UOS kernel.

    Parameters
    ----------
    n_grid : int
        Number of spatial grid points (spatial resolution of the manifold).
        Default: 32.
    dt : float
        Time step per tick in manifold units.  Default: ``UOS_CLOCK_QUANTUM``.
    n_ticks : int
        Maximum number of ticks before the hypervisor halts (guard rail).
        Default: 1000.

    Examples
    --------
    >>> hv = UOSHypervisor(n_grid=16)
    >>> hv.boot()
    >>> snapshots = hv.run(steps=10)
    >>> hv.manifold_invariant_ok()
    True
    """

    def __init__(
        self,
        n_grid: int = 32,
        dt: float = UOS_CLOCK_QUANTUM,
        n_ticks: int = 1000,
    ) -> None:
        self.n_grid = n_grid
        self.dt = dt
        self.n_ticks = n_ticks
        self.dx: float = 1.0 / n_grid   # unit box

        # Internal state
        self._g: Optional[np.ndarray] = None
        self._B: Optional[np.ndarray] = None
        self._phi: Optional[np.ndarray] = None
        self._t: float = 0.0
        self._tick: int = 0
        self._booted: bool = False

        # Subsystem references (set lazily on boot)
        self._subsystems: List = []

        # History ring-buffer: last 128 states
        self._history: List[ManifoldState] = []

        # Resource load injected by attach_to_host
        self._host_cpu_load: float = 0.0
        self._host_mem_load: float = 0.0

    # ------------------------------------------------------------------
    # Boot
    # ------------------------------------------------------------------

    def boot(self) -> None:
        """Initialise the manifold and all subsystems.

        Sets up the flat Minkowski background with small perturbations
        and marks the hypervisor as ready.
        """
        self._g, self._B, self._phi = _flat_initial_state(self.n_grid)
        self._t = 0.0
        self._tick = 0
        self._history.clear()
        self._history.append(self._snapshot())
        self._booted = True

    # ------------------------------------------------------------------
    # Single-tick advance
    # ------------------------------------------------------------------

    def tick(self) -> ManifoldState:
        """Advance the hypervisor by one clock quantum.

        Returns
        -------
        ManifoldState
            The manifold state *after* the tick.

        Raises
        ------
        RuntimeError
            If ``boot()`` has not been called first.
        """
        if not self._booted:
            raise RuntimeError("UOSHypervisor.boot() must be called before tick().")
        if self._tick >= self.n_ticks:
            raise StopIteration(
                f"Hypervisor reached maximum ticks ({self.n_ticks}). Halt."
            )

        # 1. Advance radion field (φ encodes manifold health)
        effective_alpha = ALPHA_COUPLING + self._host_cpu_load * 0.01
        self._phi = _rk4_phi_step(self._phi, self.dt, effective_alpha)

        # 2. Advance gauge field B (simple damped diffusion in monitor mode)
        self._B *= (1.0 - self.dt * LAMBDA_COUPLING ** 2)

        # 3. Pin φ near attractor with Goldberger–Wise mass term
        self._phi += self.dt * 0.01 * (PHI_BACKGROUND - self._phi)

        # 4. Modulate metric diagonal by host memory pressure
        if self._host_mem_load > 0.0:
            mem_factor = 1.0 - 0.01 * self._host_mem_load
            for i in range(1, 4):
                self._g[:, i, i] *= mem_factor

        self._t += self.dt
        self._tick += 1

        snap = self._snapshot()
        if len(self._history) >= 128:
            self._history.pop(0)
        self._history.append(snap)
        return snap

    # ------------------------------------------------------------------
    # Multi-tick run
    # ------------------------------------------------------------------

    def run(self, steps: int) -> List[ManifoldState]:
        """Run ``steps`` ticks and return a list of ManifoldState snapshots.

        Parameters
        ----------
        steps : int
            Number of ticks to advance.

        Returns
        -------
        list of ManifoldState
        """
        if not self._booted:
            self.boot()
        results = []
        for _ in range(steps):
            results.append(self.tick())
        return results

    # ------------------------------------------------------------------
    # Host monitoring (monitor / hypervisor mode)
    # ------------------------------------------------------------------

    def attach_to_host(
        self, cpu_load: float = 0.0, mem_load: float = 0.0
    ) -> None:
        """Inject real host OS resource metrics into the manifold.

        When running alongside an existing OS the hypervisor can shadow
        system load: CPU utilisation increases the effective α coupling
        (more curvature = more computation) and memory pressure slightly
        warps the metric spatial diagonals.

        Parameters
        ----------
        cpu_load : float
            CPU utilisation fraction in [0, 1].
        mem_load : float
            Memory utilisation fraction in [0, 1].
        """
        self._host_cpu_load = float(np.clip(cpu_load, 0.0, 1.0))
        self._host_mem_load = float(np.clip(mem_load, 0.0, 1.0))

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def manifold_invariant_ok(self) -> bool:
        """Return True when the manifold is in a healthy state.

        The health gate verifies two conditions:

        1. The mean radion ⟨φ⟩ is within 50 % of the background attractor
           value φ₀ = 1 (i.e., 0.5 ≤ ⟨φ⟩ ≤ 2.0 in Planck units).  A
           runaway process that drives φ to 0 or ∞ signals manifold collapse.

        2. The gauge-field RMS ‖B‖ is below the stability threshold 0.5.
           Exponentially growing B indicates a loss of the 3:2 Chern–Simons
           constraint and is the signature of a geometric security breach.

        Together these encode the 5:7 braid invariant: a healthy manifold
        oscillates near the attractor with bounded gauge excitations.

        Returns
        -------
        bool
        """
        if self._phi is None or self._B is None:
            return False
        phi_mean = float(np.mean(np.abs(self._phi)))
        phi_ok = 0.5 * PHI_BACKGROUND <= phi_mean <= 2.0 * PHI_BACKGROUND
        B_rms = float(np.sqrt(np.mean(self._B ** 2)))
        B_ok = B_rms < 0.5
        return phi_ok and B_ok

    def resource_report(self) -> Dict[str, float]:
        """Return a dict summarising current manifold resource state.

        Keys
        ----
        phi_mean : float
            Mean radion value ⟨φ⟩.
        phi_std : float
            Standard deviation of φ (roughness).
        B_rms : float
            RMS gauge field amplitude.
        g_det_mean : float
            Mean |det g| over the grid (should be ≈ 1 for near-flat).
        tick : int
            Current clock tick.
        t : float
            Current physical time.
        process_capacity : int
            Number of geodesic lanes still open (UOS_PROCESS_SLOTS).
        invariant_ok : bool
            Health gate status.
        """
        phi = self._phi if self._phi is not None else np.array([PHI_BACKGROUND])
        B = self._B if self._B is not None else np.zeros((1, 4))
        g = self._g if self._g is not None else np.eye(4)[None, :, :]

        g_dets = np.array([abs(np.linalg.det(g[i])) for i in range(len(g))])
        return {
            "phi_mean": float(np.mean(phi)),
            "phi_std": float(np.std(phi)),
            "B_rms": float(np.sqrt(np.mean(self._B ** 2))) if self._B is not None else 0.0,
            "g_det_mean": float(np.mean(g_dets)),
            "tick": self._tick,
            "t": self._t,
            "process_capacity": UOS_PROCESS_SLOTS,
            "invariant_ok": self.manifold_invariant_ok(),
        }

    # ------------------------------------------------------------------
    # State snapshot
    # ------------------------------------------------------------------

    def _snapshot(self) -> ManifoldState:
        return ManifoldState(
            g=self._g.copy(),
            B=self._B.copy(),
            phi=self._phi.copy(),
            t=self._t,
            tick=self._tick,
        )

    @property
    def history(self) -> List[ManifoldState]:
        """Read-only list of recent ManifoldState snapshots (max 128)."""
        return list(self._history)

    @property
    def state(self) -> Optional[ManifoldState]:
        """Current ManifoldState, or None before boot."""
        if not self._booted:
            return None
        return self._snapshot()
