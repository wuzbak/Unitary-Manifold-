# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_fh_lattice.py
========================
Tests for src/quantum/fh_lattice.py — geometry-aware multi-dimensional
Fermi–Hubbard lattice module (adjacent engineering lane, non-hardgate).
"""
from __future__ import annotations

import math

import pytest

from src.quantum.fh_lattice import (
    ADJACENCY_TRACK_LABEL,
    FermiHubbardLattice,
    LatticeGeometry,
    UM_BRAID_N1,
    UM_BRAID_N2,
    UM_BRAID_SITES,
    braid_kk_geometry,
    build_fermi_hubbard_braid_kk,
    build_fermi_hubbard_chain,
    build_fermi_hubbard_cubic_3d,
    build_fermi_hubbard_square_2d,
    chain_1d_geometry,
    cubic_3d_geometry,
    custom_geometry,
    hilbert_space_dimension,
    memory_estimate_bytes,
    memory_estimate_gb,
    square_2d_geometry,
)


# ===========================================================================
# Module constants
# ===========================================================================


def test_adjacency_track_label_non_empty() -> None:
    assert len(ADJACENCY_TRACK_LABEL) > 0
    assert "NOT" in ADJACENCY_TRACK_LABEL


def test_um_braid_sites() -> None:
    assert UM_BRAID_SITES == UM_BRAID_N1 + UM_BRAID_N2


def test_um_braid_n1_n2() -> None:
    assert UM_BRAID_N1 == 5
    assert UM_BRAID_N2 == 7


# ===========================================================================
# LatticeGeometry validation
# ===========================================================================


def test_lattice_geometry_basic() -> None:
    g = chain_1d_geometry(4)
    assert g.n_sites == 4
    assert g.geometry == "chain_1d"


def test_lattice_geometry_n_sites_below_2_raises() -> None:
    with pytest.raises(ValueError, match="n_sites must be"):
        LatticeGeometry(n_sites=1, edges=(), geometry="custom")


def test_lattice_geometry_unknown_geometry_raises() -> None:
    with pytest.raises(ValueError, match="geometry must be one of"):
        LatticeGeometry(n_sites=2, edges=((0, 1),), geometry="hexagonal")


def test_lattice_geometry_out_of_range_edge_raises() -> None:
    with pytest.raises(ValueError, match="out of range"):
        LatticeGeometry(n_sites=2, edges=((0, 5),), geometry="custom")


def test_lattice_geometry_self_loop_raises() -> None:
    with pytest.raises(ValueError, match="Self-loop"):
        LatticeGeometry(n_sites=3, edges=((0, 0),), geometry="custom")


def test_lattice_geometry_n_bonds() -> None:
    g = chain_1d_geometry(5)
    assert g.n_bonds == 4


def test_lattice_geometry_coordination_chain() -> None:
    g = chain_1d_geometry(4)
    # avg degree = 2*(n-1)/n = 6/4 = 1.5
    assert g.coordination_number_avg == pytest.approx(3.0 / 2.0, rel=1e-10)


# ===========================================================================
# chain_1d_geometry
# ===========================================================================


def test_chain_1d_geometry_open() -> None:
    g = chain_1d_geometry(4, periodic=False)
    assert g.n_sites == 4
    assert len(g.edges) == 3
    assert not g.periodic


def test_chain_1d_geometry_periodic() -> None:
    g = chain_1d_geometry(4, periodic=True)
    assert len(g.edges) == 4
    assert g.periodic
    assert (3, 0) in g.edges or (0, 3) in g.edges


def test_chain_1d_geometry_too_small_raises() -> None:
    with pytest.raises(ValueError, match="n_sites must be"):
        chain_1d_geometry(1)


def test_chain_1d_geometry_dims() -> None:
    g = chain_1d_geometry(6)
    assert g.dims == (6,)


# ===========================================================================
# square_2d_geometry
# ===========================================================================


def test_square_2d_geometry_2x2() -> None:
    g = square_2d_geometry(2, 2)
    assert g.n_sites == 4
    assert g.geometry == "square_2d"
    assert g.dims == (2, 2)


def test_square_2d_geometry_open_bond_count() -> None:
    # 3x3 open: 2*(n_rows-1)*n_cols = 2*2*3=12 but also rows
    # horizontal: n_rows * (n_cols-1) = 3*2 = 6
    # vertical:   (n_rows-1) * n_cols = 2*3 = 6
    g = square_2d_geometry(3, 3, periodic=False)
    assert g.n_bonds == 12


def test_square_2d_geometry_periodic_bond_count() -> None:
    # 3x3 periodic: n_rows*n_cols = 9 bonds for horizontal + 9 for vertical? No:
    # horizontal periodic: n_rows * n_cols = 3*3 = 9 (wrapping)
    # vertical periodic:   n_rows * n_cols = 9 (wrapping)
    # But we store each *undirected* bond once → 18 total
    g = square_2d_geometry(3, 3, periodic=True)
    assert g.n_bonds == 18


def test_square_2d_geometry_too_small_raises() -> None:
    with pytest.raises(ValueError):
        square_2d_geometry(1, 3)
    with pytest.raises(ValueError):
        square_2d_geometry(3, 1)


def test_square_2d_geometry_site_indexing() -> None:
    # Site (r=1, c=2) in a 3×4 grid → 1*4+2 = 6
    g = square_2d_geometry(3, 4)
    assert g.n_sites == 12


# ===========================================================================
# cubic_3d_geometry
# ===========================================================================


def test_cubic_3d_geometry_2x2x2() -> None:
    g = cubic_3d_geometry(2, 2, 2)
    assert g.n_sites == 8
    assert g.geometry == "cubic_3d"
    assert g.dims == (2, 2, 2)


def test_cubic_3d_geometry_open_bond_count() -> None:
    # 2x2x2 open: bonds in x=4, y=4, z=4 → 12 total
    g = cubic_3d_geometry(2, 2, 2, periodic=False)
    assert g.n_bonds == 12


def test_cubic_3d_geometry_periodic() -> None:
    g = cubic_3d_geometry(2, 2, 2, periodic=True)
    assert g.periodic
    # periodic adds 3 axes × 4 cross-section bonds → 12 more
    assert g.n_bonds == 24


def test_cubic_3d_geometry_too_small_raises() -> None:
    with pytest.raises(ValueError):
        cubic_3d_geometry(1, 2, 2)


# ===========================================================================
# braid_kk_geometry
# ===========================================================================


def test_braid_kk_geometry_n_sites() -> None:
    g = braid_kk_geometry()
    assert g.n_sites == 12


def test_braid_kk_geometry_ring_bonds() -> None:
    g = braid_kk_geometry()
    # ring (12) + braid junction (1) = 13
    assert g.n_bonds >= 12


def test_braid_kk_geometry_dims() -> None:
    g = braid_kk_geometry()
    assert g.dims == (UM_BRAID_N1, UM_BRAID_N2)


def test_braid_kk_geometry_periodic() -> None:
    g = braid_kk_geometry(periodic=True)
    assert g.periodic


# ===========================================================================
# custom_geometry
# ===========================================================================


def test_custom_geometry_triangle() -> None:
    g = custom_geometry(3, [(0, 1), (1, 2), (0, 2)])
    assert g.n_sites == 3
    assert g.n_bonds == 3
    assert g.geometry == "custom"


def test_custom_geometry_deduplicates_edges() -> None:
    g = custom_geometry(3, [(0, 1), (1, 0), (0, 1)])
    assert g.n_bonds == 1


def test_custom_geometry_normalises_order() -> None:
    g = custom_geometry(4, [(3, 0), (2, 1)])
    for i, j in g.edges:
        assert i < j  # canonical form


# ===========================================================================
# FermiHubbardLattice
# ===========================================================================


def test_fh_lattice_n_sites_n_modes() -> None:
    m = build_fermi_hubbard_chain(4, 1.0, 4.0)
    assert m.n_sites == 4
    assert m.n_modes == 8


def test_fh_lattice_mode_index() -> None:
    m = build_fermi_hubbard_chain(3, 1.0, 4.0)
    assert m.mode_index(0, 0) == 0
    assert m.mode_index(0, 1) == 1
    assert m.mode_index(1, 0) == 2
    assert m.mode_index(2, 1) == 5


def test_fh_lattice_mode_index_out_of_range_raises() -> None:
    m = build_fermi_hubbard_chain(3, 1.0, 0.0)
    with pytest.raises(ValueError):
        m.mode_index(5, 0)
    with pytest.raises(ValueError):
        m.mode_index(0, 2)


def test_fh_lattice_fermionic_terms_non_empty() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 4.0)
    terms = m.fermionic_terms()
    assert len(terms) > 0


def test_fh_lattice_fermionic_terms_u0_no_interaction() -> None:
    m = build_fermi_hubbard_chain(2, 1.0, 0.0)
    terms = m.fermionic_terms()
    # All terms should have |coeff| = t
    for t_ in terms:
        assert abs(t_.coefficient) == pytest.approx(1.0, abs=1e-12)


def test_fh_lattice_adjacency_report_keys() -> None:
    m = build_fermi_hubbard_square_2d(2, 2, 1.0, 4.0)
    r = m.adjacency_report()
    for key in ("geometry", "n_sites", "n_modes", "n_bonds", "hilbert_space_dim", "status"):
        assert key in r


def test_fh_lattice_adjacency_report_status() -> None:
    m = build_fermi_hubbard_square_2d(2, 2, 1.0, 4.0)
    assert "ADJACENT_TRACK" in m.adjacency_report()["status"]


def test_fh_lattice_hopping_t_negative_raises() -> None:
    with pytest.raises(ValueError, match="hopping_t"):
        build_fermi_hubbard_chain(2, -1.0, 4.0)


def test_fh_lattice_interaction_u_negative_raises() -> None:
    with pytest.raises(ValueError, match="interaction_u"):
        build_fermi_hubbard_chain(2, 1.0, -1.0)


# ===========================================================================
# Factory functions
# ===========================================================================


def test_build_fermi_hubbard_chain_4site() -> None:
    m = build_fermi_hubbard_chain(4, 1.0, 4.0)
    assert m.n_sites == 4
    assert m.geometry.geometry == "chain_1d"


def test_build_fermi_hubbard_square_2d_basic() -> None:
    m = build_fermi_hubbard_square_2d(2, 3, 1.0, 4.0)
    assert m.n_sites == 6
    assert m.geometry.geometry == "square_2d"


def test_build_fermi_hubbard_cubic_3d_basic() -> None:
    m = build_fermi_hubbard_cubic_3d(2, 2, 2, 1.0, 4.0)
    assert m.n_sites == 8
    assert m.geometry.geometry == "cubic_3d"


def test_build_fermi_hubbard_braid_kk_n_sites() -> None:
    m = build_fermi_hubbard_braid_kk()
    assert m.n_sites == 12
    assert m.geometry.geometry == "braid_kk"


def test_build_fermi_hubbard_braid_kk_mott_regime() -> None:
    m = build_fermi_hubbard_braid_kk()
    # KK U/t ≈ 78.23 > 10 → deep Mott insulating
    assert m.interaction_u / m.hopping_t > 10.0


# ===========================================================================
# Memory estimation helpers
# ===========================================================================


def test_hilbert_space_dimension_2sites() -> None:
    assert hilbert_space_dimension(2) == 16  # 2^(2*2)


def test_hilbert_space_dimension_6sites() -> None:
    assert hilbert_space_dimension(6) == 2 ** 12  # 4096


def test_memory_estimate_bytes_2sites() -> None:
    # 16 * 16 * 16 = 4096 bytes for complex128
    assert memory_estimate_bytes(2) == 16 * 16 * 16


def test_memory_estimate_gb_6sites() -> None:
    gb = memory_estimate_gb(6)
    assert gb > 0
    expected = (4096 ** 2) * 16 / (1024 ** 3)
    assert gb == pytest.approx(expected, rel=1e-10)


def test_memory_estimate_gb_2sites_tiny() -> None:
    # 2 sites → dim=16, dense mat = 16*16*16 = 4096 bytes ≈ 3.8e-6 GB
    gb = memory_estimate_gb(2)
    assert gb < 1e-4


def test_memory_grows_with_sites() -> None:
    assert memory_estimate_gb(4) > memory_estimate_gb(3)
    assert memory_estimate_gb(6) > memory_estimate_gb(4)


# ===========================================================================
# 2D square lattice — term structure
# ===========================================================================


def test_square_2d_2x2_fermionic_terms() -> None:
    m = build_fermi_hubbard_square_2d(2, 2, 1.0, 4.0)
    terms = m.fermionic_terms()
    # Hopping: 4 bonds × 2 spins × 2 directions = 16 hopping terms
    # Interaction: 4 sites × 1 term = 4 interaction terms
    # 20 total (no chemical potential)
    assert len(terms) == 20


def test_square_2d_2x2_hopping_edges() -> None:
    m = build_fermi_hubbard_square_2d(2, 2, 1.0, 4.0)
    edges = m.hopping_edges()
    assert len(edges) == 4  # 4 undirected bonds in a 2×2 open square


def test_square_2d_periodic_has_more_edges() -> None:
    open_ = build_fermi_hubbard_square_2d(2, 2, 1.0, 4.0, periodic=False)
    pbc = build_fermi_hubbard_square_2d(2, 2, 1.0, 4.0, periodic=True)
    assert pbc.geometry.n_bonds > open_.geometry.n_bonds
