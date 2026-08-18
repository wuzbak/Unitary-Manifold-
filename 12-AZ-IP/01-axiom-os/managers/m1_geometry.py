# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/managers/m1_geometry.py — Manager 1: Differential Geometry & Manifold Topology

Interfaces with the core physics modules:
  src/core/metric.py          (5D metric, Christoffel symbols)
  src/core/evolution.py       (Walker-Pearson integrator)
  src/sixd/ through src/eleventd/  (extra-dimension reductions)

Sub-agents:
  1. MetricAgent       — compute 5D KK metric tensor
  2. ChristoffelAgent  — compute Christoffel symbols
  3. RiemannAgent      — compute Riemann/Ricci tensors
  4. CompactAgent      — extra-dimension compactification checks
  5. BoundaryAgent     — boundary condition validator
"""
from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).parent.parent.parent


@dataclass
class GeometryResult:
    """Result from a geometry sub-agent."""
    agent: str
    status: str          # "ok" | "error" | "unverified"
    value: Any = None
    error: Optional[str] = None


class M1GeometryManager:
    """
    Manager 1 — Differential Geometry & Manifold Topology.

    Ensures that all agent-generated physics code is geometrically consistent
    with the 5D KK ansatz.  Any agent in M2–M7 that generates a physics claim
    must route it through M1 for geometric consistency verification.
    """

    MANAGER_ID = "M1"
    KK_LEVEL = 0   # highest privilege — kernel geometry ring

    def __init__(self) -> None:
        self._metric_module = self._try_import("src.core.metric")
        self._evolution_module = self._try_import("src.core.evolution")

    # ------------------------------------------------------------------
    # Sub-agent 1: Metric
    # ------------------------------------------------------------------

    def compute_metric(self, phi: float = 1.0, r5: float = 1.0) -> GeometryResult:
        """Compute the 5D KK metric tensor components."""
        if self._metric_module is None:
            return GeometryResult("MetricAgent", "error", error="src.core.metric unavailable")
        try:
            # Call the existing UM metric module
            metric = self._metric_module.KaluzaKleinMetric(phi=phi, R5=r5)
            g = metric.metric_tensor()
            return GeometryResult("MetricAgent", "ok", value=g)
        except Exception as exc:
            return GeometryResult("MetricAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 2: Christoffel
    # ------------------------------------------------------------------

    def compute_christoffel(self, phi: float = 1.0, r5: float = 1.0) -> GeometryResult:
        """Compute Christoffel symbols of the second kind."""
        if self._metric_module is None:
            return GeometryResult("ChristoffelAgent", "error", error="metric module unavailable")
        try:
            metric = self._metric_module.KaluzaKleinMetric(phi=phi, R5=r5)
            gamma = metric.christoffel_symbols()
            return GeometryResult("ChristoffelAgent", "ok", value=gamma)
        except Exception as exc:
            return GeometryResult("ChristoffelAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 3: Riemann
    # ------------------------------------------------------------------

    def compute_riemann(self, phi: float = 1.0, r5: float = 1.0) -> GeometryResult:
        """Compute Riemann and Ricci tensors."""
        if self._metric_module is None:
            return GeometryResult("RiemannAgent", "error", error="metric module unavailable")
        try:
            metric = self._metric_module.KaluzaKleinMetric(phi=phi, R5=r5)
            ricci = metric.ricci_tensor()
            return GeometryResult("RiemannAgent", "ok", value=ricci)
        except Exception as exc:
            return GeometryResult("RiemannAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Sub-agent 4: Compactification
    # ------------------------------------------------------------------

    def verify_compactification(
        self,
        winding_number: int = 5,
        k_cs: int = 74,
    ) -> GeometryResult:
        """Verify that the compactification topology is consistent with n_w and k_cs."""
        # Geometric constraint: k_cs == winding_number^2 + 7^2
        expected_kcs = winding_number**2 + 7**2
        if k_cs != expected_kcs:
            return GeometryResult(
                "CompactAgent", "error",
                error=f"k_cs={k_cs} != {winding_number}²+7²={expected_kcs}"
            )
        return GeometryResult(
            "CompactAgent", "ok",
            value={"winding_number": winding_number, "k_cs": k_cs, "consistent": True}
        )

    # ------------------------------------------------------------------
    # Sub-agent 5: Boundary
    # ------------------------------------------------------------------

    def verify_boundary_conditions(self, field_state: Any = None) -> GeometryResult:
        """Verify that field boundary conditions are satisfied at the KK boundary."""
        if self._evolution_module is None:
            return GeometryResult("BoundaryAgent", "unverified",
                                  error="evolution module unavailable")
        try:
            if field_state is None:
                field_state = self._evolution_module.FieldState.default()
            ok = self._evolution_module.check_constraints(field_state)
            return GeometryResult("BoundaryAgent", "ok" if ok else "error",
                                  value={"constraints_satisfied": ok})
        except Exception as exc:
            return GeometryResult("BoundaryAgent", "error", error=str(exc))

    # ------------------------------------------------------------------
    # Master geometry audit (all 5 sub-agents)
    # ------------------------------------------------------------------

    def full_audit(self, phi: float = 1.0, r5: float = 1.0) -> list[GeometryResult]:
        """Run all 5 sub-agents and return a consolidated geometry audit."""
        return [
            self.compute_metric(phi, r5),
            self.compute_christoffel(phi, r5),
            self.compute_riemann(phi, r5),
            self.verify_compactification(),
            self.verify_boundary_conditions(),
        ]

    def all_ok(self, results: list[GeometryResult]) -> bool:
        """True if all sub-agent results are 'ok' (no errors)."""
        return all(r.status == "ok" for r in results)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _try_import(module_path: str) -> Optional[Any]:
        """Import a module from the UM repository, returning None on failure."""
        repo_str = str(REPO_ROOT)
        if repo_str not in sys.path:
            sys.path.insert(0, repo_str)
        try:
            return importlib.import_module(module_path)
        except ImportError:
            return None
