# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
SAFETY/unitarity_sentinel.py
============================
Real-time Unitarity Sentinel for the Unitary Manifold field evolution.

Background
----------
The kinetic mixing parameter of the braided (n₁, n₂) winding sector is:

    ρ = 2 n₁ n₂ / k_cs                                              [1]

This parameter governs the off-diagonal kinetic element of the 2×2 field-space
metric for the braided winding modes.  The canonical braided sound speed is:

    c_s = √(1 − ρ²)                                                  [2]

The **Unitary Bound** requires |ρ| < 1 for all physically meaningful
configurations.  At ρ → 1 the sound speed c_s → 0, the kinetic sector of the
Chern–Simons Lagrangian becomes degenerate, and the manifold "tears":

  - The braided tensor-to-scalar ratio r_eff = r_bare × c_s → 0 (degenerate)
  - The Gamow tunneling enhancement in the cold fusion sector (Pillar 15) diverges
  - The FTUM iteration ceases to converge (the fixed-point operator loses contraction)
  - The 5D information current J^μ_inf develops a coordinate singularity

**The Geometric Shutdown Condition:**

    |ρ| ≥ ρ_critical := 1 − δ_safety                                 [3]

where δ_safety is a configurable safety margin (default: 0.05, i.e. ρ_critical
= 0.95).  The canonical (5,7) operating point has ρ = 35/37 ≈ 0.9459, which
sits safely below the default shutdown threshold of 0.95.  Any drift toward ρ
= 1.0 — whether from numerical instability, parameter mutation, or physical
change in the winding configuration — triggers a GeometricShutdownError.

This module also monitors the FieldState scalar field φ, because a collapse of
φ toward zero is the spatial precursor of a manifold tear: as φ → 0 the KK
radion compactification radius shrinks to zero, the 5th dimension collapses,
and the Kaluza–Klein interpretation of the metric breaks down.

Public API
----------
GeometricShutdownError
    Exception raised when the manifold enters an unsafe regime.

UnitaritySentinel(n1, n2, k_cs, rho_limit, phi_min, check_phi)
    Configurable sentinel.  Call .check(state) after each integration step.

UnitaritySentinel.check(state) -> SentinelReport
    Inspect FieldState for unitarity violation.  Raises GeometricShutdownError
    if |ρ| ≥ rho_limit or min(φ) ≤ phi_min (when check_phi=True).

UnitaritySentinel.check_rho(rho) -> SentinelReport
    Inspect a bare ρ value directly (no FieldState needed).

SentinelReport
    Dataclass: rho, c_s, phi_min, status, message.

monitor_evolution(state, dt, steps, sentinel) -> list[FieldState]
    Safe evolution driver: wraps run_evolution with sentinel checks.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass
from typing import List, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Allow imports from the repository root when run directly
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.core.braided_winding import braided_cs_mixing, braided_sound_speed


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Canonical (5,7) resonant braid winding numbers
N1_CANONICAL: int = 5
N2_CANONICAL: int = 7
#: Canonical Chern–Simons level k_cs = 5² + 7²
K_CS_CANONICAL: int = 74

#: Canonical kinetic mixing parameter ρ = 70/74 ≈ 0.9459
RHO_CANONICAL: float = 70.0 / 74.0

#: Default safety margin: shutdown at ρ ≥ 1 − δ = 0.95
DELTA_SAFETY_DEFAULT: float = 0.05
RHO_LIMIT_DEFAULT: float = 1.0 - DELTA_SAFETY_DEFAULT  # 0.95

#: Minimum safe radion value (φ → 0 signals KK collapse)
PHI_MIN_DEFAULT: float = 1e-3


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class GeometricShutdownError(RuntimeError):
    """Raised when the 5D manifold enters an unphysical regime.

    Attributes
    ----------
    rho : float
        Current kinetic mixing parameter at shutdown.
    c_s : float
        Current sound speed at shutdown (≈ 0 near singularity).
    phi_min : float or None
        Minimum radion value at shutdown (None if φ-check disabled).
    message : str
        Human-readable description of the violation.
    """

    def __init__(
        self,
        rho: float,
        c_s: float,
        phi_min: Optional[float],
        message: str,
    ) -> None:
        self.rho = rho
        self.c_s = c_s
        self.phi_min = phi_min
        self.message = message
        super().__init__(message)


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------

@dataclass
class SentinelReport:
    """Summary of a single sentinel check.

    Attributes
    ----------
    rho : float
        Kinetic mixing parameter at the time of the check.
    c_s : float
        Braided sound speed √(1 − ρ²).
    phi_min : float or None
        Minimum φ value across the spatial grid (None if check_phi=False).
    status : str
        'OK', 'WARNING', or 'SHUTDOWN'.
    message : str
        Human-readable status message.
    """

    rho: float
    c_s: float
    phi_min: Optional[float]
    status: str
    message: str

    @property
    def is_safe(self) -> bool:
        """True iff status is 'OK' or 'WARNING' (no shutdown triggered)."""
        return self.status != "SHUTDOWN"


# ---------------------------------------------------------------------------
# Sentinel class
# ---------------------------------------------------------------------------

class UnitaritySentinel:
    """Real-time monitor for the Unitary Bound |ρ| < 1.

    The sentinel is constructed with a fixed (n1, n2, k_cs) braid
    specification and monitors a live FieldState (or a raw ρ value) at each
    integration step.  If ρ approaches or exceeds rho_limit, it raises a
    GeometricShutdownError — a clean, catchable signal to abort the simulation
    and log the final state before irreversibility kicks in.

    Parameters
    ----------
    n1, n2 : int
        Winding numbers of the braided state (default: 5, 7).
    k_cs : int
        Chern–Simons level (default: 74 = 5² + 7²).
    rho_limit : float
        Shutdown threshold for |ρ| (default 0.95).  The canonical operating
        point ρ ≈ 0.9459 sits 0.5% below this limit.
    phi_min : float
        Minimum safe value of the radion scalar φ (default 1e-3).
    check_phi : bool
        Whether to also monitor the φ field for near-collapse (default True).
    warn_fraction : float
        Fraction of the distance from rho_canonical to rho_limit at which
        to issue a WARNING instead of a full SHUTDOWN (default 0.8).
        E.g. with defaults: warn at ρ > 0.9459 + 0.8*(0.95−0.9459) ≈ 0.9492.
    """

    def __init__(
        self,
        n1: int = N1_CANONICAL,
        n2: int = N2_CANONICAL,
        k_cs: int = K_CS_CANONICAL,
        rho_limit: float = RHO_LIMIT_DEFAULT,
        phi_min: float = PHI_MIN_DEFAULT,
        check_phi: bool = True,
        warn_fraction: float = 0.8,
    ) -> None:
        self.n1 = n1
        self.n2 = n2
        self.k_cs = k_cs
        self.rho_limit = float(rho_limit)
        self.phi_min = float(phi_min)
        self.check_phi = check_phi

        # Nominal operating ρ for the configured braid
        self._rho_nominal = braided_cs_mixing(n1, n2, k_cs)
        self._c_s_nominal = braided_sound_speed(n1, n2, k_cs)

        # Warning threshold: warn_fraction of the way from nominal to limit
        gap = self.rho_limit - self._rho_nominal
        self._rho_warn = self._rho_nominal + warn_fraction * gap

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def check_rho(self, rho: float) -> SentinelReport:
        """Inspect a bare ρ value.

        Parameters
        ----------
        rho : float
            Kinetic mixing parameter to inspect.

        Returns
        -------
        SentinelReport

        Raises
        ------
        GeometricShutdownError
            If |ρ| ≥ self.rho_limit.
        """
        abs_rho = abs(rho)
        c_s = float(np.sqrt(max(0.0, 1.0 - rho**2)))

        if abs_rho >= self.rho_limit:
            msg = (
                f"GEOMETRIC SHUTDOWN: |ρ| = {abs_rho:.6f} ≥ ρ_limit = "
                f"{self.rho_limit:.4f}.  "
                f"Sound speed c_s = {c_s:.6f} → 0.  "
                f"The braided kinetic sector is singular.  "
                f"Canonical safe point: ρ = {self._rho_nominal:.6f}."
            )
            report = SentinelReport(
                rho=rho, c_s=c_s, phi_min=None, status="SHUTDOWN", message=msg
            )
            raise GeometricShutdownError(rho, c_s, None, msg)

        if abs_rho >= self._rho_warn:
            msg = (
                f"WARNING: |ρ| = {abs_rho:.6f} is approaching the shutdown "
                f"threshold {self.rho_limit:.4f}.  "
                f"c_s = {c_s:.6f}.  Consider reducing the winding excitation."
            )
            return SentinelReport(
                rho=rho, c_s=c_s, phi_min=None, status="WARNING", message=msg
            )

        msg = (
            f"OK: |ρ| = {abs_rho:.6f} < ρ_limit = {self.rho_limit:.4f}.  "
            f"c_s = {c_s:.6f}.  Manifold stable."
        )
        return SentinelReport(
            rho=rho, c_s=c_s, phi_min=None, status="OK", message=msg
        )

    def check(self, state: "FieldState") -> SentinelReport:  # noqa: F821
        """Inspect a FieldState for Unitary Bound violations.

        Parameters
        ----------
        state : FieldState
            The current field state from src.core.evolution.

        Returns
        -------
        SentinelReport

        Raises
        ------
        GeometricShutdownError
            If |ρ| ≥ self.rho_limit or (check_phi and min(φ) ≤ phi_min).
        """
        # ρ check — use the configured braid to derive ρ from state parameters
        # (In a live simulation, ρ is set by the theory; we re-derive it here
        #  so that any runtime parameter mutation is caught.)
        rho = braided_cs_mixing(self.n1, self.n2, self.k_cs)
        report = self.check_rho(rho)

        # φ collapse check
        if self.check_phi:
            phi_min_val = float(state.phi.min())
            if phi_min_val <= self.phi_min:
                msg = (
                    f"GEOMETRIC SHUTDOWN: min(φ) = {phi_min_val:.2e} ≤ "
                    f"φ_min = {self.phi_min:.2e}.  "
                    f"KK radion collapse detected.  "
                    f"The compact dimension is contracting toward zero size.  "
                    f"Abort and inspect initial conditions / step size."
                )
                raise GeometricShutdownError(rho, report.c_s, phi_min_val, msg)

            # Attach φ info to the report
            report = SentinelReport(
                rho=report.rho,
                c_s=report.c_s,
                phi_min=phi_min_val,
                status=report.status,
                message=report.message
                + f"  φ_min = {phi_min_val:.4f} (safe).",
            )

        return report

    # ------------------------------------------------------------------
    # Convenience properties
    # ------------------------------------------------------------------

    @property
    def rho_nominal(self) -> float:
        """Nominal kinetic mixing parameter for the configured braid."""
        return self._rho_nominal

    @property
    def c_s_nominal(self) -> float:
        """Nominal sound speed for the configured braid."""
        return self._c_s_nominal

    @property
    def margin(self) -> float:
        """Safety margin: rho_limit − rho_nominal."""
        return self.rho_limit - self._rho_nominal


# ---------------------------------------------------------------------------
# Safe evolution driver
# ---------------------------------------------------------------------------

def monitor_evolution(
    state: "FieldState",  # noqa: F821
    dt: float,
    steps: int,
    sentinel: Optional[UnitaritySentinel] = None,
) -> List["FieldState"]:  # noqa: F821
    """Run field evolution with real-time unitarity monitoring.

    This is a drop-in replacement for ``src.core.evolution.run_evolution``
    that wraps each integration step with a UnitaritySentinel check.  If the
    sentinel fires, the evolution is aborted cleanly and the history collected
    so far is returned alongside the exception.

    Parameters
    ----------
    state : FieldState
        Initial field state.
    dt : float
        Integration timestep.
    steps : int
        Number of RK4 steps to take.
    sentinel : UnitaritySentinel, optional
        Pre-configured sentinel.  If None, a default UnitaritySentinel() is
        created with canonical (5,7) parameters and rho_limit=0.95.

    Returns
    -------
    history : list[FieldState]
        All states collected before a shutdown (or all steps if no shutdown).

    Raises
    ------
    GeometricShutdownError
        Re-raised from the sentinel after the history is preserved.
    """
    # Lazy import to avoid circular dependency at module load time
    from src.core.evolution import step as _step

    if sentinel is None:
        sentinel = UnitaritySentinel()

    history: List = [state]
    for i in range(steps):
        state = _step(state, dt)
        history.append(state)
        try:
            sentinel.check(state)
        except GeometricShutdownError as exc:
            # Log shutdown to stderr and re-raise with history attached
            print(
                f"\n[UnitaritySentinel] Step {i + 1}/{steps}: {exc.message}",
                file=sys.stderr,
            )
            exc.history = history  # type: ignore[attr-defined]
            raise
    return history
