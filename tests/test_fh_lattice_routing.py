# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_fh_lattice_routing.py
=================================
Tests for src/quantum/fh_lattice_routing.py — geometry-aware routing and
memory-budget enforcement (adjacent engineering lane, non-hardgate).
"""
from __future__ import annotations

import pytest

from src.quantum.fh_lattice import (
    build_fermi_hubbard_braid_kk,
    build_fermi_hubbard_chain,
    build_fermi_hubbard_cubic_3d,
    build_fermi_hubbard_square_2d,
)
from src.quantum.fh_lattice_routing import (
    ADJACENCY_TRACK_LABEL,
    ROUTE_BRIDGE_CROSSCHECK,
    ROUTE_UM_EXACT_DENSE,
    ROUTE_XDIAG_SPARSE,
    LatticeRoutingDecision,
    LatticeRoutingReport,
    MemoryBudget,
    RoutingConfig,
    geometry_routing_thresholds,
    lattice_route,
    preflight_check,
    scaling_estimate,
)


# ===========================================================================
# RoutingConfig validation
# ===========================================================================


def test_routing_config_defaults() -> None:
    cfg = RoutingConfig()
    assert cfg.exact_dense_max_modes == 12
    assert cfg.sparse_min_modes == 24
    assert cfg.max_dense_gb == 1.0


def test_routing_config_invalid_raises() -> None:
    with pytest.raises(ValueError, match="strictly less"):
        RoutingConfig(exact_dense_max_modes=24, sparse_min_modes=12)


def test_routing_config_max_dense_gb_zero_raises() -> None:
    with pytest.raises(ValueError, match="max_dense_gb"):
        RoutingConfig(max_dense_gb=0.0)


# ===========================================================================
# MemoryBudget
# ===========================================================================


def test_memory_budget_fits_dense_small() -> None:
    budget = MemoryBudget(max_dense_gb=10.0)
    assert budget.fits_dense(2)  # tiny
    assert budget.fits_dense(4)  # 2^8 states → negligible


def test_memory_budget_fits_dense_large_false() -> None:
    budget = MemoryBudget(max_dense_gb=0.001)
    assert not budget.fits_dense(10)  # 2^20 = 1M × 16 bytes × 2^20 >> 1 MB


def test_memory_budget_warning_returned() -> None:
    budget = MemoryBudget(warn_gb=0.0)  # always warn
    warn = budget.memory_warning(2)
    assert warn is not None
    assert "Dense Hamiltonian" in warn


def test_memory_budget_no_warning_below_threshold() -> None:
    budget = MemoryBudget(warn_gb=100.0)  # never warn for small systems
    assert budget.memory_warning(2) is None


# ===========================================================================
# lattice_route — small chain (dense)
# ===========================================================================


def test_route_chain_2site_dense() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    dec = lattice_route(m)
    assert dec.route == ROUTE_UM_EXACT_DENSE
    assert dec.n_sites == 2
    assert dec.n_modes == 4


def test_route_chain_4site_dense() -> None:
    m = build_fermi_hubbard_chain(4, 1.0, 4.0)
    dec = lattice_route(m)
    assert dec.route == ROUTE_UM_EXACT_DENSE
    assert dec.preferred_engine == "um_exact_dense"


def test_route_chain_returns_decision_dataclass() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    dec = lattice_route(m)
    assert isinstance(dec, LatticeRoutingDecision)


def test_route_status_label() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    dec = lattice_route(m)
    assert ADJACENCY_TRACK_LABEL in dec.status


# ===========================================================================
# lattice_route — large chain (XDiag)
# ===========================================================================


def test_route_large_chain_xdiag() -> None:
    m = build_fermi_hubbard_chain(14, 1.0, 4.0)
    dec = lattice_route(m)
    assert dec.route == ROUTE_XDIAG_SPARSE


def test_route_large_memory_forces_xdiag() -> None:
    m = build_fermi_hubbard_chain(10, 1.0, 4.0)
    budget = MemoryBudget(max_dense_gb=1e-10)  # force memory failure
    dec = lattice_route(m, budget=budget)
    assert dec.route == ROUTE_XDIAG_SPARSE
    assert "xdiag" in dec.reason


# ===========================================================================
# lattice_route — bridge crosscheck
# ===========================================================================


def test_route_intermediate_bridge() -> None:
    # n_modes=14 (7 sites) → between exact_dense_max_modes=12 and sparse_min_modes=24.
    # With default MemoryBudget(1 GB) memory check fails (7 sites needs ~4 GB).
    # Use a large budget to exercise the intermediate bridge_crosscheck zone.
    m = build_fermi_hubbard_chain(7, 1.0, 4.0)  # n_modes=14
    budget = MemoryBudget(max_dense_gb=100.0)
    dec = lattice_route(m, budget=budget)
    assert dec.route == ROUTE_BRIDGE_CROSSCHECK


# ===========================================================================
# lattice_route — force_engine overrides
# ===========================================================================


def test_route_force_um() -> None:
    m = build_fermi_hubbard_chain(14, 1.0, 4.0)
    dec = lattice_route(m, force_engine="um")
    assert dec.route == ROUTE_UM_EXACT_DENSE
    assert dec.reason == "forced_um"


def test_route_force_xdiag() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 0.0)
    dec = lattice_route(m, force_engine="xdiag")
    assert dec.route == ROUTE_XDIAG_SPARSE
    assert dec.reason == "forced_xdiag"


def test_route_force_bridge() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 0.0)
    dec = lattice_route(m, force_engine="bridge")
    assert dec.route == ROUTE_BRIDGE_CROSSCHECK
    assert dec.reason == "forced_bridge"


def test_route_force_invalid_raises() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 0.0)
    with pytest.raises(ValueError, match="force_engine must be one of"):
        lattice_route(m, force_engine="invalid")


# ===========================================================================
# lattice_route — geometry fields
# ===========================================================================


def test_route_decision_geometry_chain() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 0.0)
    dec = lattice_route(m)
    assert dec.geometry == "chain_1d"


def test_route_decision_geometry_2d() -> None:
    m = build_fermi_hubbard_square_2d(2, 2, 1.0, 0.0)
    dec = lattice_route(m)
    assert dec.geometry == "square_2d"


def test_route_decision_geometry_3d() -> None:
    m = build_fermi_hubbard_cubic_3d(2, 2, 2, 1.0, 0.0)
    dec = lattice_route(m)
    assert dec.geometry == "cubic_3d"


def test_route_decision_hilbert_dim() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    dec = lattice_route(m)
    assert dec.hilbert_dim == 2 ** 4  # = 16 for 2 sites → n_modes=4


def test_route_decision_memory_estimate_positive() -> None:
    m = build_fermi_hubbard_chain(3, 1.0, 4.0)
    dec = lattice_route(m)
    assert dec.memory_estimate_gb > 0.0


# ===========================================================================
# preflight_check
# ===========================================================================


def test_preflight_ok_small_chain() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    report = preflight_check(m)
    assert isinstance(report, LatticeRoutingReport)
    assert report.preflight_ok


def test_preflight_xdiag_route_has_warning() -> None:
    m = build_fermi_hubbard_chain(14, 1.0, 4.0)
    report = preflight_check(m)
    # Should warn about XDiag requirement
    xdiag_warn = any("xdiag" in w.lower() or "XDiag" in w for w in report.warnings)
    assert xdiag_warn


def test_preflight_3d_large_has_warning() -> None:
    m = build_fermi_hubbard_cubic_3d(2, 2, 3, 1.0, 0.0)  # 12 sites
    report = preflight_check(m)
    cubic_warn = any("cubic" in w.lower() or "3D" in w or "3d" in w.lower() for w in report.warnings)
    assert cubic_warn


def test_preflight_no_errors_normal_chain() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    report = preflight_check(m)
    assert len(report.errors) == 0


def test_preflight_braid_kk_reports() -> None:
    m = build_fermi_hubbard_braid_kk()
    report = preflight_check(m)
    assert isinstance(report, LatticeRoutingReport)
    assert report.decision.geometry == "braid_kk"


# ===========================================================================
# geometry_routing_thresholds
# ===========================================================================


def test_geometry_thresholds_chain_1d() -> None:
    cfg = geometry_routing_thresholds("chain_1d")
    assert cfg.exact_dense_max_modes == 12
    assert cfg.sparse_min_modes == 24


def test_geometry_thresholds_square_2d_tighter() -> None:
    cfg_chain = geometry_routing_thresholds("chain_1d")
    cfg_2d = geometry_routing_thresholds("square_2d")
    assert cfg_2d.exact_dense_max_modes <= cfg_chain.exact_dense_max_modes


def test_geometry_thresholds_cubic_3d_tightest() -> None:
    cfg_2d = geometry_routing_thresholds("square_2d")
    cfg_3d = geometry_routing_thresholds("cubic_3d")
    assert cfg_3d.exact_dense_max_modes <= cfg_2d.exact_dense_max_modes


def test_geometry_thresholds_custom_returns_config() -> None:
    cfg = geometry_routing_thresholds("custom")
    assert isinstance(cfg, RoutingConfig)


def test_geometry_thresholds_braid_kk() -> None:
    cfg = geometry_routing_thresholds("braid_kk")
    assert isinstance(cfg, RoutingConfig)
    assert cfg.exact_dense_max_modes < cfg.sparse_min_modes


# ===========================================================================
# scaling_estimate
# ===========================================================================


def test_scaling_estimate_returns_list() -> None:
    result = scaling_estimate([2, 4, 6, 8, 10, 12])
    assert len(result) == 6


def test_scaling_estimate_dict_keys() -> None:
    result = scaling_estimate([2])
    r = result[0]
    for key in ("n_sites", "n_modes", "hilbert_dim", "memory_dense_gb", "route_1d_chain", "status"):
        assert key in r


def test_scaling_estimate_routes_monotone() -> None:
    result = scaling_estimate([2, 6, 7, 14])
    routes = [r["route_1d_chain"] for r in result]
    # 2 sites → dense, 6 sites → dense, 7 sites → bridge, 14 → xdiag
    assert routes[0] == ROUTE_UM_EXACT_DENSE
    assert routes[-1] == ROUTE_XDIAG_SPARSE


def test_scaling_estimate_memory_grows() -> None:
    result = scaling_estimate([2, 4, 6])
    mem = [r["memory_dense_gb"] for r in result]
    assert mem[1] > mem[0]
    assert mem[2] > mem[1]


def test_scaling_estimate_status_adjacent_track() -> None:
    result = scaling_estimate([4])
    assert ADJACENCY_TRACK_LABEL in result[0]["status"]
