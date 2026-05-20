# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for FH Braid Ring Energy Spectrum (v11.9 quantum lane)."""
import math
import pytest
from src.quantum.fh_braid_spectrum import (
    ADJACENCY_TRACK_LABEL,
    UM_BRAID_N1,
    UM_BRAID_N2,
    UM_BRAID_SITES,
    KK_U_OVER_T,
    KK_RADION_COUPLING,
    PHI0,
    E0_CURVED_REF,
    E0_FLAT_REF,
    separation_guard,
    build_radion_profile,
    curved_hopping_amplitude,
    build_braid_ring_hopping_table,
    braid_spectrum_analytical_estimate,
    extract_mott_gaps,
    braid_ring_spectrum_report,
)


def test_adjacency_label():
    assert "NOT a hardgate" in ADJACENCY_TRACK_LABEL


def test_braid_geometry():
    assert UM_BRAID_N1 == 5
    assert UM_BRAID_N2 == 7
    assert UM_BRAID_SITES == 12


def test_kk_u_over_t():
    expected = 74 ** 2 / (2 * 5 * 7)
    assert abs(KK_U_OVER_T - expected) < 1e-6


def test_radion_coupling():
    c_s = 12.0 / 37.0
    expected = c_s / 5
    assert abs(KK_RADION_COUPLING - expected) < 1e-10


def test_e0_curved_ref():
    assert E0_CURVED_REF < 0.0
    assert abs(E0_CURVED_REF - (-0.704)) < 1e-3


def test_e0_flat_ref():
    assert E0_FLAT_REF < 0.0
    assert abs(E0_FLAT_REF - (-0.843)) < 1e-3


def test_curved_vs_flat_ordering():
    # Curved ground state is higher (less negative) than flat
    assert E0_CURVED_REF > E0_FLAT_REF


def test_separation_guard():
    g = separation_guard()
    assert g["is_hardgate"] is False
    assert g["alters_toe_score"] is False
    assert g["status"] == "FIRST_PHYSICS_OUTPUT"


def test_radion_profile_length():
    profile = build_radion_profile()
    assert len(profile) == UM_BRAID_SITES


def test_radion_profile_values():
    profile = build_radion_profile(phi0=1.0)
    # All values should be positive
    assert all(p > 0 for p in profile)
    # Should include PHI0 ≈ 1.0 as baseline
    assert min(profile) <= 1.0 + 0.5  # within braid amplitude


def test_radion_profile_kink_at_junction():
    profile = build_radion_profile(n1=5, phi0=1.0)
    # Profile should have a kink at site 5 (junction between n1 and n2 segments)
    # The value at site 4 (last of n1) and site 5 (first of n2) should differ
    n1 = 5
    assert abs(profile[n1] - profile[n1 - 1]) > 0.0  # kink exists


def test_curved_hopping_amplitude_flat():
    # When phi_i = phi_j, hopping = t0
    t = curved_hopping_amplitude(1.0, 1.0, t0=1.0)
    assert abs(t - 1.0) < 1e-10


def test_curved_hopping_amplitude_suppressed():
    t = curved_hopping_amplitude(1.0, 2.0, t0=1.0)
    assert t < 1.0  # suppressed by radion gradient


def test_curved_hopping_amplitude_symmetric():
    t1 = curved_hopping_amplitude(1.0, 1.5)
    t2 = curved_hopping_amplitude(1.5, 1.0)
    assert abs(t1 - t2) < 1e-10


def test_build_braid_ring_hopping_table_bonds():
    ht = build_braid_ring_hopping_table()
    assert ht["n_bonds"] == UM_BRAID_SITES


def test_build_braid_ring_hopping_table_suppression():
    ht = build_braid_ring_hopping_table()
    assert ht["mean_suppression"] < 1.0  # curved < flat
    assert ht["mean_suppression"] > 0.8  # not too suppressed


def test_build_braid_ring_hopping_table_keys():
    ht = build_braid_ring_hopping_table()
    for key in ("t_min", "t_max", "t_mean", "braid_junction_bond"):
        assert key in ht


def test_braid_ring_hopping_min_max():
    ht = build_braid_ring_hopping_table()
    assert ht["t_min"] <= ht["t_mean"] <= ht["t_max"]


def test_braid_spectrum_analytical_estimate_keys():
    s = braid_spectrum_analytical_estimate()
    for key in ("t_eff", "U_eff", "spin_gap_j_curved", "charge_gap_estimate_curved",
                "mott_phase_confirmed", "regime"):
        assert key in s


def test_braid_spectrum_mott_insulator():
    s = braid_spectrum_analytical_estimate()
    assert s["mott_phase_confirmed"] is True
    assert s["regime"] == "MOTT_INSULATOR"


def test_braid_spectrum_u_over_t_large():
    s = braid_spectrum_analytical_estimate()
    assert s["u_over_t"] > 50.0  # deep in Mott regime


def test_braid_spectrum_spin_gap_positive():
    s = braid_spectrum_analytical_estimate()
    assert s["spin_gap_j_curved"] > 0.0
    assert s["spin_gap_j_flat"] > 0.0


def test_braid_spectrum_charge_gap_positive():
    s = braid_spectrum_analytical_estimate()
    assert s["charge_gap_estimate_curved"] > 0.0


def test_braid_spectrum_curved_below_flat():
    s = braid_spectrum_analytical_estimate()
    # Curved spin gap should be smaller (reduced t_eff → less superexchange)
    assert s["spin_gap_j_curved"] <= s["spin_gap_j_flat"]


def test_extract_mott_gaps_keys():
    s = braid_spectrum_analytical_estimate()
    g = extract_mott_gaps(s)
    for key in ("spin_gap_curved", "charge_gap_curved", "spin_to_charge_curved",
                "ratio_shift_from_flat", "um_prediction"):
        assert key in g


def test_extract_mott_gaps_um_prediction_string():
    s = braid_spectrum_analytical_estimate()
    g = extract_mott_gaps(s)
    assert isinstance(g["um_prediction"], str)
    assert len(g["um_prediction"]) > 20


def test_braid_ring_spectrum_report_keys():
    rep = braid_ring_spectrum_report()
    for key in ("geometry", "hopping_table_summary", "low_energy_spectrum",
                "mott_gap_structure", "summary"):
        assert key in rep


def test_braid_ring_spectrum_report_geometry():
    rep = braid_ring_spectrum_report()
    g = rep["geometry"]
    assert g["n1"] == UM_BRAID_N1
    assert g["n2"] == UM_BRAID_N2
    assert g["n_sites"] == UM_BRAID_SITES


def test_braid_ring_spectrum_report_summary():
    rep = braid_ring_spectrum_report()
    assert isinstance(rep["summary"], str)
    assert "Mott" in rep["summary"]
