# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
SAFETY/admissibility_checker.py
================================
Z-Admissibility Checker for the Unitary Manifold scalar curvature proxy.

Background
----------
The Walker–Pearson field equations enforce a constraint on the scalar curvature
proxy Z — the dimensionless combination of the Ricci scalar R, the irreversibility
field-strength norm ‖H‖², and the radion scalar φ:

    Z = |R| / (φ² + ε)                                               [1]

where ε is a small regulariser that prevents division by zero as φ → 0.

**The Z-Admissibility Bound:**

    Z < Z_max                                                         [2]

When Z exceeds Z_max the scalar curvature proxy is no longer small compared
to the compactification scale set by φ, and the effective 4D description
obtained by integrating out the compact dimension breaks down.  Physically:

  - At Z ~ Z_max the back-reaction of the scalar curvature on the KK radion
    destabilises the moduli, allowing φ to drift away from its fixed point φ*.
  - At Z >> Z_max the higher-derivative corrections to the 4D effective action
    — suppressed by inverse powers of the compactification scale — become
    comparable to the leading-order terms, and the truncated field equations
    are no longer a valid approximation.
  - In the extreme limit (sometimes called "Pentagonal Collapse" in the
    internal literature) the scalar curvature proxy diverges faster than φ²,
    the FTUM iteration ceases to converge, and the attractor structure of the
    theory is destroyed.

**The Pentagonal Collapse Threshold:**

The name "Pentagonal Collapse" refers to the five-sided structure of the
constraint surface in (R, H, φ, ∇φ, ∂_t φ) space.  The five edges of the
admissible polytope are:

  1.  |R| / φ² < Z_max          (scalar curvature proxy bound)
  2.  ‖H‖ / φ  < H_max          (field-strength norm bound)
  3.  ‖∇φ‖    < grad_max        (radion gradient bound — prevents shock formation)
  4.  φ        > φ_floor         (radion positivity — prevents KK collapse)
  5.  |det g|  ≈ 1               (metric volume-preservation)

Violating any one of these five conditions places the system outside the
admissible polytope and into "Pentagonal Collapse" territory.  The first
condition (curvature proxy) is the most commonly approached in numerical
simulations; this module monitors all five.

Reference
---------
The admissibility framework is implicit in the constraint_monitor() function
of src/core/evolution.py and the volume-preservation projection applied after
each RK4 step.  This module makes those constraints explicit, configurable,
and testable.

Public API
----------
PentagonalCollapseError
    Exception raised when the scalar curvature proxy exits the admissible region.

AdmissibilityReport
    Dataclass: z_proxy, h_norm, grad_phi, phi_min, det_g_dev, edges, status.

AdmissibilityChecker(z_max, h_max, grad_max, phi_floor, det_tol)
    Configurable checker.  Call .check(state) after each integration step.

AdmissibilityChecker.check(state) -> AdmissibilityReport
    Inspect FieldState.  Raises PentagonalCollapseError if any edge is violated.

AdmissibilityChecker.check_raw(R, phi, H_norm, grad_phi, det_g_dev)
    Inspect pre-computed scalars directly.
"""

from __future__ import annotations

import sys
import os
from dataclasses import dataclass, field
from typing import Dict, Optional

import numpy as np

# ---------------------------------------------------------------------------
# Allow imports from the repository root when run directly
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from src.core.metric import compute_curvature, field_strength


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

#: Default Z_max — scalar curvature proxy bound
Z_MAX_DEFAULT: float = 10.0

#: Default H_max — field-strength norm bound (units of φ)
H_MAX_DEFAULT: float = 5.0

#: Default gradient bound for ∇φ
GRAD_MAX_DEFAULT: float = 10.0

#: Default φ floor (same as UnitaritySentinel)
PHI_FLOOR_DEFAULT: float = 1e-3

#: Default tolerance for det(g) deviation from −1
DET_TOL_DEFAULT: float = 0.1

#: Small regulariser for Z computation
_EPS: float = 1e-30


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class PentagonalCollapseError(RuntimeError):
    """Raised when the field state exits the Z-admissible polytope.

    Attributes
    ----------
    violated_edges : list[str]
        Names of the polytope edges that were violated.
    report : AdmissibilityReport
        Full diagnostic report at the time of shutdown.
    """

    def __init__(
        self, violated_edges: list, report: "AdmissibilityReport", message: str
    ) -> None:
        self.violated_edges = violated_edges
        self.report = report
        super().__init__(message)


# ---------------------------------------------------------------------------
# Report dataclass
# ---------------------------------------------------------------------------

@dataclass
class AdmissibilityReport:
    """Diagnostic summary of a single admissibility check.

    Attributes
    ----------
    z_proxy : float
        Maximum scalar curvature proxy Z = max(|R|) / (φ² + ε) over the grid.
    h_norm : float
        Maximum field-strength norm ‖H‖ / max(φ) over the grid.
    grad_phi : float
        Maximum ‖∇φ‖ over the grid.
    phi_min : float
        Minimum φ value over the grid.
    det_g_dev : float
        Maximum |det(g) − (−1)| / 1 over the grid (volume-preservation residual).
    edges : dict[str, bool]
        True if the corresponding polytope edge is satisfied.
    status : str
        'OK', 'WARNING', or 'SHUTDOWN'.
    message : str
        Human-readable summary.
    """

    z_proxy: float
    h_norm: float
    grad_phi: float
    phi_min: float
    det_g_dev: float
    edges: Dict[str, bool] = field(default_factory=dict)
    status: str = "OK"
    message: str = ""

    @property
    def is_admissible(self) -> bool:
        """True iff all five polytope edges are satisfied."""
        return all(self.edges.values())


# ---------------------------------------------------------------------------
# Checker class
# ---------------------------------------------------------------------------

class AdmissibilityChecker:
    """Monitor for the Z-admissibility bound and Pentagonal Collapse detection.

    Parameters
    ----------
    z_max : float
        Maximum allowed scalar curvature proxy Z (default 10.0).
    h_max : float
        Maximum allowed field-strength norm ‖H‖/φ (default 5.0).
    grad_max : float
        Maximum allowed ‖∇φ‖ (default 10.0).
    phi_floor : float
        Minimum allowed φ (default 1e-3).
    det_tol : float
        Maximum allowed |det(g) + 1| (volume-preservation tolerance, default 0.1).
    warn_fraction : float
        Fraction of each limit at which to issue a WARNING rather than SHUTDOWN
        (default 0.8).
    """

    def __init__(
        self,
        z_max: float = Z_MAX_DEFAULT,
        h_max: float = H_MAX_DEFAULT,
        grad_max: float = GRAD_MAX_DEFAULT,
        phi_floor: float = PHI_FLOOR_DEFAULT,
        det_tol: float = DET_TOL_DEFAULT,
        warn_fraction: float = 0.8,
    ) -> None:
        self.z_max = float(z_max)
        self.h_max = float(h_max)
        self.grad_max = float(grad_max)
        self.phi_floor = float(phi_floor)
        self.det_tol = float(det_tol)
        self._warn_fraction = float(warn_fraction)

    # ------------------------------------------------------------------

    def check_raw(
        self,
        R: float,
        phi: float,
        H_norm: float,
        grad_phi: float,
        det_g_dev: float,
    ) -> AdmissibilityReport:
        """Inspect pre-computed scalars directly.

        Parameters
        ----------
        R : float        Maximum |R| over the grid.
        phi : float      Minimum φ value.
        H_norm : float   Maximum ‖H‖/φ value.
        grad_phi : float Maximum ‖∇φ‖ value.
        det_g_dev : float Maximum |det(g)+1| value.

        Returns
        -------
        AdmissibilityReport

        Raises
        ------
        PentagonalCollapseError
        """
        z_proxy = abs(R) / (phi**2 + _EPS)
        edges = {
            "curvature_proxy": z_proxy < self.z_max,
            "field_strength": H_norm < self.h_max,
            "gradient": grad_phi < self.grad_max,
            "phi_floor": phi > self.phi_floor,
            "volume_preservation": det_g_dev < self.det_tol,
        }
        violated = [k for k, ok in edges.items() if not ok]

        # Determine warning thresholds
        warning_violations = [
            k for k, ok in edges.items()
            if not ok and self._near_limit(k, z_proxy, H_norm, grad_phi, phi, det_g_dev)
        ]

        if violated:
            status = "SHUTDOWN"
            msg = (
                f"PENTAGONAL COLLAPSE: Admissibility violated on edges: "
                f"{violated}.  "
                f"Z_proxy={z_proxy:.4f} (limit {self.z_max}), "
                f"H_norm={H_norm:.4f} (limit {self.h_max}), "
                f"grad_phi={grad_phi:.4f} (limit {self.grad_max}), "
                f"phi_min={phi:.4e} (floor {self.phi_floor}), "
                f"det_dev={det_g_dev:.4f} (tol {self.det_tol})."
            )
            report = AdmissibilityReport(
                z_proxy=z_proxy,
                h_norm=H_norm,
                grad_phi=grad_phi,
                phi_min=phi,
                det_g_dev=det_g_dev,
                edges=edges,
                status=status,
                message=msg,
            )
            raise PentagonalCollapseError(violated, report, msg)

        # Check warnings
        warn_edges = [
            k for k in edges
            if self._approaching_limit(k, z_proxy, H_norm, grad_phi, phi, det_g_dev)
        ]
        if warn_edges:
            status = "WARNING"
            msg = (
                f"WARNING: Approaching admissibility limits on: {warn_edges}.  "
                f"Z_proxy={z_proxy:.4f}/{self.z_max}, "
                f"H_norm={H_norm:.4f}/{self.h_max}, "
                f"phi_min={phi:.4e}/{self.phi_floor}."
            )
        else:
            status = "OK"
            msg = (
                f"OK: All five admissibility edges satisfied.  "
                f"Z_proxy={z_proxy:.4f} (max {self.z_max}), "
                f"phi_min={phi:.4e}."
            )

        return AdmissibilityReport(
            z_proxy=z_proxy,
            h_norm=H_norm,
            grad_phi=grad_phi,
            phi_min=phi,
            det_g_dev=det_g_dev,
            edges=edges,
            status=status,
            message=msg,
        )

    def check(self, state: "FieldState") -> AdmissibilityReport:  # noqa: F821
        """Inspect a FieldState for Z-admissibility violations.

        Extracts the scalar curvature, field-strength norm, radion gradient,
        and metric volume-preservation residual from the state, then calls
        check_raw().

        Parameters
        ----------
        state : FieldState
            The current field state from src.core.evolution.

        Returns
        -------
        AdmissibilityReport

        Raises
        ------
        PentagonalCollapseError
        """
        Ricci, R, _ = compute_curvature(state.g, state.B, state.phi, state.dx)
        H = field_strength(state.B, state.dx)

        # Scalar curvature: max |R| over the grid
        R_max = float(np.max(np.abs(R)))

        # Field-strength norm ‖H‖_F per site, divided by φ
        H_norm_grid = np.sqrt(np.einsum("nij,nij->n", H, H)) / (
            np.abs(state.phi) + _EPS
        )
        H_norm = float(H_norm_grid.max())

        # Radion gradient
        dphi = np.gradient(state.phi, state.dx, edge_order=2)
        grad_phi = float(np.max(np.abs(dphi)))

        # Min φ
        phi_min = float(state.phi.min())

        # Metric volume-preservation residual
        det_g = np.linalg.det(state.g)  # shape (N,)
        det_g_dev = float(np.max(np.abs(det_g + 1.0)))  # deviation from −1

        return self.check_raw(R_max, phi_min, H_norm, grad_phi, det_g_dev)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _approaching_limit(
        self, edge: str, z_proxy: float, H_norm: float,
        grad_phi: float, phi: float, det_g_dev: float
    ) -> bool:
        """True if the given edge is within warn_fraction of its limit."""
        f = self._warn_fraction
        if edge == "curvature_proxy":
            return z_proxy > f * self.z_max
        if edge == "field_strength":
            return H_norm > f * self.h_max
        if edge == "gradient":
            return grad_phi > f * self.grad_max
        if edge == "phi_floor":
            return phi < self.phi_floor / f  # approaching from above
        if edge == "volume_preservation":
            return det_g_dev > f * self.det_tol
        return False

    def _near_limit(
        self, edge: str, z_proxy: float, H_norm: float,
        grad_phi: float, phi: float, det_g_dev: float
    ) -> bool:
        """True if the edge is violated (synonym for clarity)."""
        return True  # all violated edges pass through here
