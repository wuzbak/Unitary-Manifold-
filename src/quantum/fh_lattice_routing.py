# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/fh_lattice_routing.py
==================================
Geometry-aware routing and memory-budget enforcement for the
Fermi–Hubbard adjacent research lane.

EPISTEMIC STATUS — ADJACENT ENGINEERING LANE (NON-HARDGATE)
------------------------------------------------------------
This module provides deterministic pre-flight routing for multi-dimensional
FH lattice simulations.  It does NOT make physics claims and does NOT alter
the core ToE score.

Routing decisions
-----------------
Three execution routes are possible for any given lattice model:

um_exact_dense
    UM's own exact diagonalisation (``fh_solver.exact_diagonalize``).
    Valid when the full Hilbert space fits comfortably in memory and the
    matrix can be diagonalised within a reasonable wall-clock budget.
    Default threshold: n_modes ≤ ``RoutingConfig.exact_dense_max_modes``
    (default 12, i.e. 6 spinful sites → dim = 2^12 = 4 096).

bridge_crosscheck
    Intermediate regime where both UM and XDiag engines can compute the
    result.  Run both and compare via the parity gate.
    Default threshold: exact_dense_max_modes < n_modes < sparse_min_modes.

xdiag_sparse
    XDiag sparse eigensolver — mandatory for large lattices.
    Default threshold: n_modes ≥ ``RoutingConfig.sparse_min_modes``
    (default 24, i.e. 12 spinful sites → dim = 2^24 ≈ 16.8 M).

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal

from .fh_lattice import (
    FermiHubbardLattice,
    LatticeGeometry,
    memory_estimate_gb,
    hilbert_space_dimension,
    ADJACENCY_TRACK_LABEL,
)

__all__ = [
    "RoutingConfig",
    "MemoryBudget",
    "LatticeRoutingDecision",
    "LatticeRoutingReport",
    "lattice_route",
    "preflight_check",
    "geometry_routing_thresholds",
    "scaling_estimate",
    "ROUTE_UM_EXACT_DENSE",
    "ROUTE_BRIDGE_CROSSCHECK",
    "ROUTE_XDIAG_SPARSE",
]

RouteName = Literal["um_exact_dense", "bridge_crosscheck", "xdiag_sparse"]

ROUTE_UM_EXACT_DENSE: str = "um_exact_dense"
ROUTE_BRIDGE_CROSSCHECK: str = "bridge_crosscheck"
ROUTE_XDIAG_SPARSE: str = "xdiag_sparse"

# Memory constants
_BYTES_PER_GB = 1024 ** 3
_COMPLEX128_BYTES = 16  # bytes per complex128 element


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RoutingConfig:
    """Thresholds for the three-zone routing decision.

    Attributes
    ----------
    exact_dense_max_modes:
        Maximum number of spin-orbital modes (= 2·n_sites) for UM exact-dense
        ED.  Default 12 (= 6 spinful sites, dim = 2^12 = 4 096).
    sparse_min_modes:
        Minimum number of modes for XDiag-sparse-only regime.
        Default 24 (= 12 spinful sites, dim = 2^24 ≈ 16.8 M).
    max_dense_gb:
        Hard memory ceiling (GB) for UM dense ED.  Default 1.0 GB.
    """

    exact_dense_max_modes: int = 12
    sparse_min_modes: int = 24
    max_dense_gb: float = 1.0

    def __post_init__(self) -> None:
        if self.exact_dense_max_modes >= self.sparse_min_modes:
            raise ValueError(
                "exact_dense_max_modes must be strictly less than sparse_min_modes"
            )
        if self.max_dense_gb <= 0:
            raise ValueError("max_dense_gb must be positive")


@dataclass(frozen=True)
class MemoryBudget:
    """Per-run memory budget for a lattice FH simulation.

    Attributes
    ----------
    max_dense_gb:
        Maximum memory allowed for the dense Hamiltonian matrix.
    max_sector_gb:
        Maximum memory per sector sub-block (default = max_dense_gb / 4).
    warn_gb:
        Issue a warning in the routing report above this memory estimate.
    """

    max_dense_gb: float = 1.0
    max_sector_gb: float = 0.25
    warn_gb: float = 0.1

    def fits_dense(self, n_sites: int) -> bool:
        """True if the full dense Hamiltonian fits within the budget."""
        return memory_estimate_gb(n_sites) <= self.max_dense_gb

    def memory_warning(self, n_sites: int) -> str | None:
        """Return a warning string if memory exceeds warn_gb, else None."""
        est = memory_estimate_gb(n_sites)
        if est > self.warn_gb:
            return (
                f"Dense Hamiltonian for n_sites={n_sites} requires "
                f"~{est:.3f} GB (budget warn_gb={self.warn_gb:.2f} GB)."
            )
        return None


# ---------------------------------------------------------------------------
# Result dataclasses
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class LatticeRoutingDecision:
    """Routing decision for a single FH lattice model.

    Attributes
    ----------
    route:
        One of ``"um_exact_dense"``, ``"bridge_crosscheck"``, or
        ``"xdiag_sparse"``.
    preferred_engine:
        Human-readable engine label.
    reason:
        Machine-readable routing reason tag.
    geometry:
        The geometry string from the lattice spec.
    n_sites:
        Number of lattice sites.
    n_modes:
        Number of spin-orbital modes (= 2·n_sites).
    hilbert_dim:
        Full Hilbert space dimension (2^n_modes).
    memory_estimate_gb:
        Estimated dense Hamiltonian memory in GB.
    memory_warning:
        Non-empty string if memory exceeds warning threshold.
    status:
        Adjacent-track status label.
    """

    route: RouteName
    preferred_engine: str
    reason: str
    geometry: str
    n_sites: int
    n_modes: int
    hilbert_dim: int
    memory_estimate_gb: float
    memory_warning: str
    status: str = ADJACENCY_TRACK_LABEL


@dataclass(frozen=True)
class LatticeRoutingReport:
    """Full routing pre-flight report for a lattice model.

    Attributes
    ----------
    decision:
        The routing decision.
    preflight_ok:
        True if the lattice is safe to run on the chosen engine.
    warnings:
        List of non-fatal advisory strings.
    errors:
        List of fatal blocking strings.
    """

    decision: LatticeRoutingDecision
    preflight_ok: bool
    warnings: list[str]
    errors: list[str]


# ---------------------------------------------------------------------------
# Core routing logic
# ---------------------------------------------------------------------------


def lattice_route(
    model: FermiHubbardLattice,
    config: RoutingConfig = RoutingConfig(),
    budget: MemoryBudget = MemoryBudget(),
    force_engine: str | None = None,
) -> LatticeRoutingDecision:
    """Route a FermiHubbardLattice to the appropriate execution engine.

    Parameters
    ----------
    model:
        The lattice model to route.
    config:
        Routing thresholds.
    budget:
        Memory budget constraints.
    force_engine:
        If provided, override automatic routing.  Accepted values are
        ``"um"``, ``"xdiag"``, or ``"bridge"``.

    Returns
    -------
    LatticeRoutingDecision
    """
    n_modes = model.n_modes
    n_sites = model.n_sites
    dim = hilbert_space_dimension(n_sites)
    mem_gb = memory_estimate_gb(n_sites)
    mem_warn = budget.memory_warning(n_sites) or ""

    if force_engine is not None:
        allowed = {"um", "xdiag", "bridge"}
        if force_engine not in allowed:
            raise ValueError(f"force_engine must be one of {sorted(allowed)}")
        if force_engine == "um":
            return LatticeRoutingDecision(
                route="um_exact_dense",
                preferred_engine="um_exact_dense",
                reason="forced_um",
                geometry=model.geometry.geometry,
                n_sites=n_sites,
                n_modes=n_modes,
                hilbert_dim=dim,
                memory_estimate_gb=mem_gb,
                memory_warning=mem_warn,
            )
        if force_engine == "xdiag":
            return LatticeRoutingDecision(
                route="xdiag_sparse",
                preferred_engine="xdiag_sparse",
                reason="forced_xdiag",
                geometry=model.geometry.geometry,
                n_sites=n_sites,
                n_modes=n_modes,
                hilbert_dim=dim,
                memory_estimate_gb=mem_gb,
                memory_warning=mem_warn,
            )
        # bridge
        return LatticeRoutingDecision(
            route="bridge_crosscheck",
            preferred_engine="um+xdiag",
            reason="forced_bridge",
            geometry=model.geometry.geometry,
            n_sites=n_sites,
            n_modes=n_modes,
            hilbert_dim=dim,
            memory_estimate_gb=mem_gb,
            memory_warning=mem_warn,
        )

    # Memory override: if dense memory exceeds budget, go to XDiag regardless
    if not budget.fits_dense(n_sites) or n_modes >= config.sparse_min_modes:
        return LatticeRoutingDecision(
            route="xdiag_sparse",
            preferred_engine="xdiag_sparse",
            reason="large_lattice_xdiag_required",
            geometry=model.geometry.geometry,
            n_sites=n_sites,
            n_modes=n_modes,
            hilbert_dim=dim,
            memory_estimate_gb=mem_gb,
            memory_warning=mem_warn,
        )

    if n_modes <= config.exact_dense_max_modes:
        return LatticeRoutingDecision(
            route="um_exact_dense",
            preferred_engine="um_exact_dense",
            reason="small_lattice_dense_exact",
            geometry=model.geometry.geometry,
            n_sites=n_sites,
            n_modes=n_modes,
            hilbert_dim=dim,
            memory_estimate_gb=mem_gb,
            memory_warning=mem_warn,
        )

    # Intermediate zone
    return LatticeRoutingDecision(
        route="bridge_crosscheck",
        preferred_engine="um+xdiag",
        reason="intermediate_bridge_crosscheck",
        geometry=model.geometry.geometry,
        n_sites=n_sites,
        n_modes=n_modes,
        hilbert_dim=dim,
        memory_estimate_gb=mem_gb,
        memory_warning=mem_warn,
    )


def preflight_check(
    model: FermiHubbardLattice,
    config: RoutingConfig = RoutingConfig(),
    budget: MemoryBudget = MemoryBudget(),
    force_engine: str | None = None,
) -> LatticeRoutingReport:
    """Run the full pre-flight routing check for a lattice model.

    Returns a ``LatticeRoutingReport`` with warnings and errors.
    A run is safe to proceed when ``report.preflight_ok is True``.

    Parameters
    ----------
    model, config, budget, force_engine:
        Forwarded to ``lattice_route``.
    """
    decision = lattice_route(model, config, budget, force_engine)
    warnings: list[str] = []
    errors: list[str] = []

    # Memory warnings
    if decision.memory_warning:
        warnings.append(decision.memory_warning)

    # XDiag required but no actual XDiag library present (advisory)
    if decision.route == "xdiag_sparse":
        warnings.append(
            "Route is xdiag_sparse.  Ensure the XDiag library is installed "
            "and accessible before submitting the job."
        )

    # Very large lattice: error if dense is attempted
    if decision.route == "um_exact_dense" and decision.memory_estimate_gb > 4.0:
        errors.append(
            f"UM exact-dense requested but estimated memory "
            f"{decision.memory_estimate_gb:.1f} GB exceeds 4 GB hard cap."
        )

    # Geometry-specific advisory
    if model.geometry.geometry == "cubic_3d" and model.n_sites > 8:
        warnings.append(
            f"3D cubic lattice with n_sites={model.n_sites} is very large. "
            "Consider XDiag sparse or a sub-lattice."
        )

    preflight_ok = len(errors) == 0
    return LatticeRoutingReport(
        decision=decision,
        preflight_ok=preflight_ok,
        warnings=warnings,
        errors=errors,
    )


# ---------------------------------------------------------------------------
# Geometry-specific default thresholds
# ---------------------------------------------------------------------------


def geometry_routing_thresholds(geometry: str) -> RoutingConfig:
    """Return suggested RoutingConfig defaults for a given geometry type.

    These are conservative defaults to prevent accidental OOM situations.
    Users may override via explicit RoutingConfig instances.

    Parameters
    ----------
    geometry:
        One of ``"chain_1d"``, ``"square_2d"``, ``"cubic_3d"``,
        ``"braid_kk"``, or ``"custom"``.

    Returns
    -------
    RoutingConfig with geometry-appropriate thresholds.
    """
    if geometry == "chain_1d":
        # 1D chains are well-understood; allow up to 12 modes (6 sites) dense
        return RoutingConfig(exact_dense_max_modes=12, sparse_min_modes=24, max_dense_gb=2.0)
    if geometry == "square_2d":
        # 2D: bond count grows faster; be more conservative
        return RoutingConfig(exact_dense_max_modes=8, sparse_min_modes=16, max_dense_gb=0.5)
    if geometry == "cubic_3d":
        # 3D: extremely fast growth; tight limits
        return RoutingConfig(exact_dense_max_modes=6, sparse_min_modes=12, max_dense_gb=0.25)
    if geometry == "braid_kk":
        # 12-site ring: n_modes = 24 → XDiag required
        return RoutingConfig(exact_dense_max_modes=8, sparse_min_modes=20, max_dense_gb=0.5)
    # custom: conservative defaults
    return RoutingConfig(exact_dense_max_modes=8, sparse_min_modes=16, max_dense_gb=0.5)


# ---------------------------------------------------------------------------
# Scaling estimate helper
# ---------------------------------------------------------------------------


def scaling_estimate(n_sites_list: list[int]) -> list[dict[str, object]]:
    """Return memory and Hilbert-space estimates for a list of system sizes.

    Useful for planning XDiag scale-up campaigns.

    Parameters
    ----------
    n_sites_list:
        List of system sizes to estimate.

    Returns
    -------
    List of dicts with keys: n_sites, n_modes, hilbert_dim, memory_gb,
    route_1d_chain (default RoutingConfig).
    """
    default_cfg = RoutingConfig()
    result = []
    for n_sites in n_sites_list:
        n_modes = 2 * n_sites
        dim = hilbert_space_dimension(n_sites)
        mem_gb = memory_estimate_gb(n_sites)
        if n_modes <= default_cfg.exact_dense_max_modes:
            route = ROUTE_UM_EXACT_DENSE
        elif n_modes < default_cfg.sparse_min_modes:
            route = ROUTE_BRIDGE_CROSSCHECK
        else:
            route = ROUTE_XDIAG_SPARSE
        result.append(
            {
                "n_sites": n_sites,
                "n_modes": n_modes,
                "hilbert_dim": dim,
                "memory_dense_gb": mem_gb,
                "route_1d_chain": route,
                "status": ADJACENCY_TRACK_LABEL,
            }
        )
    return result
