# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 305 — Fermi-Hubbard Braid Ring Phase Diagram."""
import math
import pytest
from src.core.pillar305_fh_braid_ring_phase_diagram import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_SITES,
    N1,
    N2,
    K_CS,
    N_W,
    C_S,
    LAMBDA_KK,
    U_T_UM_NATURAL,
    U_CRITICAL_FLAT,
    U_CRITICAL_KK,
    J_SUPEREXCHANGE,
    DOUBLE_OCCUPANCY,
    CHARGE_GAP_UM_NATURAL,
    PHASE_METALLIC,
    PHASE_CORRELATED,
    PHASE_MOTT,
    separation_guard,
    kk_hopping_modulation,
    effective_hoppings,
    mott_transition_U_critical,
    double_occupancy_strong_coupling,
    charge_gap,
    spin_gap,
    superexchange_J,
    heisenberg_ground_energy,
    phase_label,
    phase_diagram_point,
    phase_diagram_scan,
    flat_vs_kk_comparison,
    phase_diagram_report,
)


# ── Module identity ────────────────────────────────────────────────────────────

def test_pillar_number():
    assert PILLAR_NUMBER == 305

def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


# ── Ring geometry constants ────────────────────────────────────────────────────

def test_n_sites():
    assert N_SITES == 12
    assert N_SITES == N1 + N2

def test_n1_n2():
    assert N1 == 5
    assert N2 == 7

def test_k_cs():
    assert K_CS == 74

def test_n_w():
    assert N_W == 5

def test_c_s_12_37():
    assert C_S == pytest.approx(12.0 / 37.0, rel=1e-10)

def test_lambda_kk():
    expected = C_S / N_W
    assert LAMBDA_KK == pytest.approx(expected, rel=1e-10)

def test_lambda_kk_small():
    assert 0 < LAMBDA_KK < 0.2


# ── UM-natural parameters ──────────────────────────────────────────────────────

def test_u_t_um_natural():
    assert U_T_UM_NATURAL == pytest.approx(61.7, rel=1e-3)

def test_u_critical_flat():
    assert U_CRITICAL_FLAT == pytest.approx(4.0, rel=1e-6)

def test_u_critical_kk_less_flat():
    # KK curvature reduces t_eff → reduces U_c slightly
    assert U_CRITICAL_KK <= U_CRITICAL_FLAT

def test_j_superexchange_positive():
    assert J_SUPEREXCHANGE > 0

def test_j_superexchange_small():
    # J = 4/U_t = 4/61.7 ≈ 0.0648
    assert J_SUPEREXCHANGE == pytest.approx(4.0 / U_T_UM_NATURAL, rel=1e-6)

def test_double_occupancy_small():
    # D ~ 2/U_t² ≪ 1 for U_t = 61.7
    assert DOUBLE_OCCUPANCY < 0.01

def test_charge_gap_um_natural_large():
    # Deep in Mott phase: Δ_charge >> 1 (in units of t)
    assert CHARGE_GAP_UM_NATURAL > 50.0


# ── Phase labels ───────────────────────────────────────────────────────────────

def test_phase_labels_distinct():
    assert PHASE_METALLIC != PHASE_CORRELATED
    assert PHASE_CORRELATED != PHASE_MOTT
    assert PHASE_METALLIC != PHASE_MOTT


# ── separation_guard ───────────────────────────────────────────────────────────

def test_separation_guard_pillar():
    g = separation_guard()
    assert g["pillar"] == 305

def test_separation_guard_not_hardgate():
    g = separation_guard()
    assert g["is_hardgate"] is False

def test_separation_guard_lane():
    g = separation_guard()
    assert g["lane"] == "QUANTUM_SIMULATION"


# ── kk_hopping_modulation ─────────────────────────────────────────────────────

def test_hopping_modulation_range():
    for i in range(N_SITES):
        j = (i + 1) % N_SITES
        h = kk_hopping_modulation(i, j)
        assert 0 < h <= 1.0

def test_hopping_modulation_positive():
    h = kk_hopping_modulation(0, 1)
    assert h > 0

def test_hopping_modulation_symmetric():
    # Same bond traversed in both directions
    h1 = kk_hopping_modulation(0, 1)
    h2 = kk_hopping_modulation(1, 0)
    # Note: |φ_0 - φ_1| = |φ_1 - φ_0| → same modulation
    assert h1 == pytest.approx(h2, rel=1e-10)

def test_hopping_flat_lambda_zero():
    # With λ=0, all hoppings are 1
    h = kk_hopping_modulation(0, 1, lambda_kk=0.0)
    assert h == pytest.approx(1.0)


# ── effective_hoppings ────────────────────────────────────────────────────────

def test_effective_hoppings_dict():
    hops = effective_hoppings()
    assert isinstance(hops, dict)
    assert "t_min" in hops
    assert "t_max" in hops
    assert "t_mean" in hops

def test_hoppings_range():
    hops = effective_hoppings()
    assert 0 < hops["t_min"] <= hops["t_max"] <= 1.0

def test_hoppings_n_bonds():
    hops = effective_hoppings()
    assert hops["n_bonds"] == N_SITES

def test_hoppings_mean_between_min_max():
    hops = effective_hoppings()
    assert hops["t_min"] <= hops["t_mean"] <= hops["t_max"]

def test_hoppings_spread_positive():
    hops = effective_hoppings()
    assert hops["t_spread"] > 0  # KK geometry breaks translational symmetry


# ── mott_transition_U_critical ────────────────────────────────────────────────

def test_u_c_flat():
    u_c = mott_transition_U_critical(curved=False)
    assert u_c == pytest.approx(4.0, rel=1e-6)

def test_u_c_curved_less():
    u_c_flat = mott_transition_U_critical(curved=False)
    u_c_kk = mott_transition_U_critical(curved=True)
    assert u_c_kk <= u_c_flat

def test_u_c_positive():
    assert mott_transition_U_critical() > 0


# ── double_occupancy_strong_coupling ──────────────────────────────────────────

def test_double_occ_um_natural():
    D = double_occupancy_strong_coupling(61.7)
    assert D == pytest.approx(2.0 / 61.7**2, rel=1e-6)

def test_double_occ_small_at_large_u():
    D = double_occupancy_strong_coupling(100.0)
    assert D < 0.001

def test_double_occ_positive():
    assert double_occupancy_strong_coupling(10.0) > 0

def test_double_occ_invalid():
    with pytest.raises(ValueError):
        double_occupancy_strong_coupling(0.0)


# ── charge_gap ────────────────────────────────────────────────────────────────

def test_charge_gap_metallic():
    # U/t < bandwidth: no gap
    assert charge_gap(2.0, bandwidth=4.0) == 0.0

def test_charge_gap_mott():
    # U/t > bandwidth: gap opens
    assert charge_gap(10.0, bandwidth=4.0) > 0

def test_charge_gap_um_natural():
    # At U/t = 61.7, gap ≈ 61.7 - 4 = 57.7t
    g = charge_gap(U_T_UM_NATURAL, bandwidth=4.0)
    assert g == pytest.approx(U_T_UM_NATURAL - 4.0, rel=1e-6)

def test_charge_gap_monotone():
    g1 = charge_gap(10.0, bandwidth=4.0)
    g2 = charge_gap(20.0, bandwidth=4.0)
    assert g2 > g1


# ── spin_gap ─────────────────────────────────────────────────────────────────

def test_spin_gap_zero():
    # Half-filled 1D Hubbard: spin gap = 0 (SU(2) symmetry)
    for U_t in [1.0, 4.0, 10.0, 61.7, 100.0]:
        assert spin_gap(U_t) == 0.0


# ── superexchange_J ───────────────────────────────────────────────────────────

def test_superexchange_um_natural():
    J = superexchange_J(61.7)
    assert J == pytest.approx(4.0 / 61.7, rel=1e-6)

def test_superexchange_decreasing():
    J1 = superexchange_J(10.0)
    J2 = superexchange_J(100.0)
    assert J1 > J2

def test_superexchange_positive():
    assert superexchange_J(10.0) > 0

def test_superexchange_invalid():
    with pytest.raises(ValueError):
        superexchange_J(0.0)


# ── heisenberg_ground_energy ──────────────────────────────────────────────────

def test_heisenberg_energy_negative():
    J = superexchange_J(61.7)
    E = heisenberg_ground_energy(12, J)
    assert E < 0  # antiferromagnet: negative ground energy

def test_heisenberg_energy_per_site():
    J = superexchange_J(61.7)
    E = heisenberg_ground_energy(12, J)
    E_per_site = E / 12
    # Bethe ansatz: ε₀ ≈ -J × 0.4431 per bond
    expected_per_bond = -J * (math.log(2) - 0.25)
    assert E_per_site == pytest.approx(expected_per_bond, rel=1e-6)

def test_heisenberg_scales_with_J():
    J1, J2 = 0.1, 0.2
    E1 = heisenberg_ground_energy(12, J1)
    E2 = heisenberg_ground_energy(12, J2)
    assert abs(E2 / E1 - 2.0) < 0.01


# ── phase_label ───────────────────────────────────────────────────────────────

def test_phase_label_metallic():
    p = phase_label(0.5, curved=False)
    assert p == PHASE_METALLIC

def test_phase_label_mott():
    p = phase_label(61.7, curved=False)
    assert p == PHASE_MOTT

def test_phase_label_correlated():
    p = phase_label(3.0, curved=False)
    assert p in (PHASE_CORRELATED, PHASE_METALLIC)  # near transition


# ── phase_diagram_point ───────────────────────────────────────────────────────

def test_phase_point_returns_dict():
    p = phase_diagram_point(61.7)
    assert isinstance(p, dict)

def test_phase_point_um_natural_mott():
    p = phase_diagram_point(61.7)
    assert p["phase"] == PHASE_MOTT
    assert p["is_mott"] is True

def test_phase_point_spin_gap_zero():
    p = phase_diagram_point(61.7)
    assert p["spin_gap_t"] == 0.0

def test_phase_point_double_occ_small():
    p = phase_diagram_point(61.7)
    assert p["double_occupancy"] < 0.01

def test_phase_point_geometry_field():
    p_kk = phase_diagram_point(10.0, curved=True)
    p_flat = phase_diagram_point(10.0, curved=False)
    assert p_kk["geometry"] == "KK_CURVED"
    assert p_flat["geometry"] == "FLAT"


# ── phase_diagram_scan ────────────────────────────────────────────────────────

def test_scan_returns_list():
    scan = phase_diagram_scan()
    assert isinstance(scan, list)
    assert len(scan) > 0

def test_scan_all_dicts():
    for p in phase_diagram_scan():
        assert isinstance(p, dict)

def test_scan_custom_u_values():
    scan = phase_diagram_scan([1.0, 10.0, 61.7])
    assert len(scan) == 3

def test_scan_mott_at_high_u():
    scan = phase_diagram_scan([61.7, 100.0])
    for p in scan:
        assert p["phase"] == PHASE_MOTT


# ── flat_vs_kk_comparison ─────────────────────────────────────────────────────

def test_comparison_returns_list():
    comp = flat_vs_kk_comparison()
    assert isinstance(comp, list)
    assert len(comp) > 0

def test_comparison_all_dicts():
    for c in flat_vs_kk_comparison():
        assert isinstance(c, dict)
        assert "U_t" in c
        assert "flat_phase" in c
        assert "kk_phase" in c

def test_comparison_um_natural_both_mott():
    comp = flat_vs_kk_comparison([61.7])
    assert comp[0]["flat_phase"] == PHASE_MOTT
    assert comp[0]["kk_phase"] == PHASE_MOTT

def test_comparison_kk_t_eff_less_one():
    for c in flat_vs_kk_comparison():
        assert 0 < c["kk_t_eff"] <= 1.0


# ── phase_diagram_report ──────────────────────────────────────────────────────

def test_report_returns_string():
    r = phase_diagram_report()
    assert isinstance(r, str)

def test_report_contains_mott():
    r = phase_diagram_report()
    assert "MOTT" in r or "Mott" in r

def test_report_contains_um_natural():
    r = phase_diagram_report()
    assert "61.7" in r or "UM" in r

def test_report_contains_kk():
    r = phase_diagram_report()
    assert "KK" in r

def test_report_contains_complete():
    r = phase_diagram_report()
    assert "COMPLETE" in r
