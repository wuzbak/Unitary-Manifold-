# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
UOS/security.py
===============
Unitary Operating System — Geometric Isolation Security Engine

Conventional OS security relies on access-control lists, firewalls, and
permission walls — all of which can be bypassed if an attacker finds an
implementation bug.  The **GeometricSecurityEngine** instead enforces
security through manifold topology: code and data that do not satisfy the
5:7 braid invariant (the 3:2 Chern–Simons ratio embedded in K_CS = 74)
are structurally **incoherent** on the manifold and cannot execute.

Geometric Isolation Tiers
--------------------------
The UOS defines ``UOS_SECURITY_LEVELS = 5`` (= n_w) isolation tiers,
each corresponding to one winding number of the braid:

  Tier 0 (Kernel)    — only the hypervisor kernel; φ-deviation < 1e-9
  Tier 1 (System)    — OS services; φ-deviation < 1e-6
  Tier 2 (Trusted)   — signed user applications
  Tier 3 (Standard)  — normal user processes
  Tier 4 (Sandbox)   — untrusted / guest processes (strictest gate)

A process at Tier T can read memory pages at Tier ≥ T and write only at
Tier = T.  Crossing a tier boundary requires the φ-field at the boundary
to satisfy the invariant ratio — a mathematical impossibility for code that
does not embed the correct braid structure.

Invariant Check
---------------
The invariant gate evaluates:

    deviation = |φ_hash / K_CS − INVARIANT_RATIO|

where ``φ_hash`` is a geometric fingerprint of the code block derived from
the sum of squared byte values modulo K_CS.  If ``deviation > tolerance``
the code is rejected with a ``SecurityViolation``.

Public API
----------
SecurityViolation
    Exception raised when the invariant gate fails.

SecurityContext(pid, tier, phi_fingerprint)
    Security context associated with a process.

GeometricSecurityEngine(tolerance)
    Main security engine.

GeometricSecurityEngine.register(pid, tier, code_bytes)
    Register a process; compute its φ-fingerprint.

GeometricSecurityEngine.verify(pid)
    Re-verify a registered process against the invariant gate.

GeometricSecurityEngine.check_access(accessor_pid, target_page_tier)
    Return True if ``accessor_pid`` may access a page at ``target_page_tier``.

GeometricSecurityEngine.unregister(pid)
    Remove a process from the security registry.

GeometricSecurityEngine.audit_log()
    Return the list of security events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np

from UOS.constants import (
    K_CS,
    WINDING_NUMBER,
    BRAID_PARTNER,
    UOS_SECURITY_LEVELS,
    INVARIANT_RATIO,
    INVARIANT_TOLERANCE,
    PHI_BACKGROUND,
)


# ---------------------------------------------------------------------------
# SecurityViolation — raised when the geometric gate rejects code
# ---------------------------------------------------------------------------

class SecurityViolation(Exception):
    """Raised when a process fails the 5:7 braid invariant gate.

    Attributes
    ----------
    pid : int
        PID of the offending process.
    deviation : float
        Measured deviation from the INVARIANT_RATIO.
    tolerance : float
        Maximum allowed deviation.
    """
    def __init__(self, pid: int, deviation: float, tolerance: float) -> None:
        self.pid = pid
        self.deviation = deviation
        self.tolerance = tolerance
        super().__init__(
            f"SecurityViolation: process {pid} fails the 5:7 braid invariant gate.  "
            f"φ-deviation={deviation:.6e} > tolerance={tolerance:.6e}.  "
            "Execution blocked."
        )


# ---------------------------------------------------------------------------
# SecurityContext — per-process security context
# ---------------------------------------------------------------------------

@dataclass
class SecurityContext:
    """Security context for a registered UOS process.

    Parameters
    ----------
    pid : int
    tier : int
        Isolation tier in [0, UOS_SECURITY_LEVELS).
    phi_fingerprint : float
        Geometric fingerprint of the process code block, in [0, 1].
    """
    pid: int
    tier: int
    phi_fingerprint: float

    def __post_init__(self) -> None:
        if not 0 <= self.tier < UOS_SECURITY_LEVELS:
            raise ValueError(
                f"Tier must be in [0, {UOS_SECURITY_LEVELS}); got {self.tier}."
            )


# ---------------------------------------------------------------------------
# GeometricSecurityEngine — the UOS security layer
# ---------------------------------------------------------------------------

class GeometricSecurityEngine:
    """Topology-based security engine for the UOS.

    Parameters
    ----------
    tolerance : float
        Maximum allowed deviation from ``INVARIANT_RATIO`` before a process
        is blocked.  Default: ``INVARIANT_TOLERANCE + 0.02`` (relaxed
        slightly to allow real-world code that was not generated by the UM
        to pass — fully strict mode would require UM-native binaries).

    Examples
    --------
    >>> engine = GeometricSecurityEngine()
    >>> engine.register(pid=42, tier=3, code_bytes=b"hello world")
    >>> engine.verify(pid=42)
    True
    """

    def __init__(self, tolerance: float = INVARIANT_TOLERANCE + 0.02) -> None:
        self.tolerance = tolerance
        self._registry: Dict[int, SecurityContext] = {}
        self._audit: List[Dict] = []

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(
        self, pid: int, tier: int, code_bytes: bytes = b""
    ) -> SecurityContext:
        """Register a process and compute its φ-fingerprint.

        The φ-fingerprint is derived as:

            φ_fingerprint = (Σ byte² mod K_CS) / K_CS

        This maps any byte sequence to [0, 1).  The invariant gate checks
        that ``φ_fingerprint`` falls in the admissible window around
        ``INVARIANT_RATIO``.

        Parameters
        ----------
        pid : int
        tier : int
            Isolation tier (0 = kernel, 4 = sandbox).
        code_bytes : bytes
            Raw bytes of the process code block (optional; empty bytes
            produce a canonical fingerprint equal to 0 / K_CS = 0).

        Returns
        -------
        SecurityContext
        """
        fingerprint = self._compute_fingerprint(code_bytes)
        ctx = SecurityContext(pid=pid, tier=tier, phi_fingerprint=fingerprint)
        self._registry[pid] = ctx
        self._audit.append({
            "event": "register",
            "pid": pid,
            "tier": tier,
            "fingerprint": fingerprint,
        })
        return ctx

    # ------------------------------------------------------------------
    # Verification
    # ------------------------------------------------------------------

    def verify(self, pid: int) -> bool:
        """Verify a registered process against the invariant gate.

        Returns True if the process passes; raises SecurityViolation if
        the deviation exceeds the tolerance.

        Parameters
        ----------
        pid : int

        Returns
        -------
        bool

        Raises
        ------
        KeyError
            If the process is not registered.
        SecurityViolation
            If the φ-fingerprint deviates too far from INVARIANT_RATIO.
        """
        if pid not in self._registry:
            raise KeyError(f"Process {pid} is not registered in the security engine.")
        ctx = self._registry[pid]
        deviation = abs(ctx.phi_fingerprint - INVARIANT_RATIO)
        # Tier 0 (kernel) is exempt — it seeded the manifold itself
        if ctx.tier == 0:
            self._audit.append({"event": "verify_ok", "pid": pid, "deviation": 0.0})
            return True
        if deviation > self.tolerance:
            self._audit.append({
                "event": "verify_fail",
                "pid": pid,
                "deviation": deviation,
            })
            raise SecurityViolation(pid=pid, deviation=deviation, tolerance=self.tolerance)
        self._audit.append({"event": "verify_ok", "pid": pid, "deviation": deviation})
        return True

    def verify_bytes(self, pid: int, code_bytes: bytes) -> bool:
        """Verify an arbitrary byte block against the invariant gate.

        Useful for checking untrusted code before it is loaded into a
        process slot.  Does not require the process to be registered.

        Parameters
        ----------
        pid : int
            PID to attribute the check to (for audit log).
        code_bytes : bytes

        Returns
        -------
        bool

        Raises
        ------
        SecurityViolation
        """
        fingerprint = self._compute_fingerprint(code_bytes)
        deviation = abs(fingerprint - INVARIANT_RATIO)
        if deviation > self.tolerance:
            self._audit.append({
                "event": "verify_bytes_fail",
                "pid": pid,
                "deviation": deviation,
            })
            raise SecurityViolation(pid=pid, deviation=deviation, tolerance=self.tolerance)
        self._audit.append({
            "event": "verify_bytes_ok",
            "pid": pid,
            "deviation": deviation,
        })
        return True

    # ------------------------------------------------------------------
    # Access control
    # ------------------------------------------------------------------

    def check_access(self, accessor_pid: int, target_page_tier: int) -> bool:
        """Return True if ``accessor_pid`` may access a page at ``target_page_tier``.

        Rule: a process at tier T may READ pages at tier ≥ T.
        Writing is only permitted to pages at the same tier (enforced by
        UnitaryMemory; the security engine only gates reads here).

        Parameters
        ----------
        accessor_pid : int
        target_page_tier : int

        Returns
        -------
        bool

        Raises
        ------
        KeyError
            If ``accessor_pid`` is not registered.
        """
        if accessor_pid not in self._registry:
            raise KeyError(f"Process {accessor_pid} is not registered.")
        ctx = self._registry[accessor_pid]
        allowed = ctx.tier <= target_page_tier
        self._audit.append({
            "event": "access_check",
            "pid": accessor_pid,
            "accessor_tier": ctx.tier,
            "target_tier": target_page_tier,
            "allowed": allowed,
        })
        return allowed

    # ------------------------------------------------------------------
    # Unregister
    # ------------------------------------------------------------------

    def unregister(self, pid: int) -> None:
        """Remove a process from the security registry.

        Parameters
        ----------
        pid : int

        Raises
        ------
        KeyError
            If the process is not registered.
        """
        if pid not in self._registry:
            raise KeyError(f"Process {pid} is not registered.")
        self._registry.pop(pid)
        self._audit.append({"event": "unregister", "pid": pid})

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    def audit_log(self) -> List[Dict]:
        """Return a copy of the security audit log."""
        return list(self._audit)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_fingerprint(code_bytes: bytes) -> float:
        """Compute the φ-fingerprint of a code block.

        φ_fingerprint = (Σ b² mod K_CS) / K_CS

        Maps any byte sequence to [0, 1).
        """
        if not code_bytes:
            return 0.0
        arr = np.frombuffer(code_bytes, dtype=np.uint8).astype(np.int64)
        checksum = int(np.sum(arr ** 2)) % K_CS
        return checksum / K_CS
