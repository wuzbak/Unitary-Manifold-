# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
src/quantum/xdiag_bridge/routing.py
===================================
Deterministic routing rules for UM-only, bridge, and XDiag-heavy workloads.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

RouteName = Literal["um_exact_dense", "bridge_crosscheck", "xdiag_sparse"]


@dataclass(frozen=True)
class RoutingThresholds:
    exact_dense_max_modes: int = 12
    sparse_min_modes: int = 14


@dataclass(frozen=True)
class RoutingDecision:
    route: RouteName
    preferred_engine: str
    reason: str



def choose_route(
    n_modes: int,
    thresholds: RoutingThresholds = RoutingThresholds(),
    force_engine: str | None = None,
) -> RoutingDecision:
    if n_modes <= 0:
        raise ValueError("n_modes must be positive")

    if force_engine is not None:
        allowed = {"um", "xdiag"}
        if force_engine not in allowed:
            raise ValueError(f"force_engine must be one of {sorted(allowed)}")
        if force_engine == "um":
            return RoutingDecision(
                route="um_exact_dense",
                preferred_engine="um",
                reason="forced_um",
            )
        return RoutingDecision(
            route="xdiag_sparse",
            preferred_engine="xdiag",
            reason="forced_xdiag",
        )

    if n_modes <= thresholds.exact_dense_max_modes:
        return RoutingDecision(
            route="um_exact_dense",
            preferred_engine="um",
            reason="small_dense_exact_lane",
        )

    if n_modes >= thresholds.sparse_min_modes:
        return RoutingDecision(
            route="xdiag_sparse",
            preferred_engine="xdiag",
            reason="large_sparse_production_lane",
        )

    return RoutingDecision(
        route="bridge_crosscheck",
        preferred_engine="um+xdiag",
        reason="intermediate_cross_validation_lane",
    )
