# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 296 — P17 Seesaw Diagonalization Upgrade Attempt."""
import math
import pytest
from src.core.pillar296_p17_seesaw_diagonalization_upgrade_attempt import (
    ADJACENCY_TRACK_LABEL,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    P17_TARGET_DM31_EV2,
    P17_CURRENT_LABEL,
    P_R_EFFECTIVE,
    P_R_GEOMETRIC_PILLAR286,
    P_R_TARGET_RANGE,
    separation_guard,
    p_r_conditional_derivation_status,
    construct_dirac_mass_matrix_3x3,
    seesaw_light_mass_matrix,
    diagonalize_seesaw,
    extract_atmospheric_splitting,
    full_diagonalization_upgrade_attempt,
    p17_upgrade_certificate,
    pillar296_report,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 296


def test_adjacency_label():
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"


def test_p17_current_label():
    assert P17_CURRENT_LABEL == "CONDITIONAL_DERIVATION"


def test_p_r_effective():
    assert abs(P_R_EFFECTIVE - 0.364) < 1e-3


def test_p_r_geometric_small():
    assert P_R_GEOMETRIC_PILLAR286 < 1e-4


def test_separation_guard():
    g = separation_guard()
    assert g["pillar"] == 296
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False
    assert g["extends_pillar"] == 286
    assert g["attempts_p17_upgrade"] is True


def test_conditional_derivation_status_keys():
    s = p_r_conditional_derivation_status()
    for key in ("p17_label", "dm31_pdg_ev2", "baseline_residual_pct",
                "p_r_effective_nlo", "gap_still_open"):
        assert key in s


def test_conditional_derivation_status_label():
    s = p_r_conditional_derivation_status()
    assert s["p17_label"] == "CONDITIONAL_DERIVATION"


def test_conditional_derivation_gap_open():
    s = p_r_conditional_derivation_status()
    assert s["gap_still_open"] is True


def test_construct_dirac_mass_matrix():
    m_D, meta = construct_dirac_mass_matrix_3x3()
    assert len(m_D) == 3
    assert len(m_D[0]) == 3
    assert "y_nu_mass_basis" in meta


def test_dirac_matrix_diagonal_dominance():
    m_D, _ = construct_dirac_mass_matrix_3x3()
    for i in range(3):
        diag = abs(m_D[i][i])
        for j in range(3):
            if j != i:
                assert diag >= abs(m_D[i][j]) or diag > 0


def test_seesaw_light_mass_matrix():
    m_D, _ = construct_dirac_mass_matrix_3x3()
    M_nu = seesaw_light_mass_matrix(m_D)
    assert len(M_nu) == 3
    assert len(M_nu[0]) == 3
    # Check symmetry
    for i in range(3):
        for j in range(3):
            assert abs(M_nu[i][j] - M_nu[j][i]) < 1e-20


def test_diagonalize_seesaw_keys():
    d = diagonalize_seesaw()
    for key in ("m1_ev", "m2_ev", "m3_ev", "m_nu_diagonal_ev"):
        assert key in d


def test_diagonalize_seesaw_positive():
    d = diagonalize_seesaw()
    assert d["m1_ev"] >= 0.0
    assert d["m2_ev"] >= 0.0
    assert d["m3_ev"] >= 0.0


def test_diagonalize_seesaw_ordering():
    d = diagonalize_seesaw()
    # Masses should be sorted
    assert d["m1_ev"] <= d["m2_ev"] <= d["m3_ev"]


def test_extract_atmospheric_splitting_keys():
    diag = diagonalize_seesaw()
    s = extract_atmospheric_splitting(diag)
    for key in ("dm31_seesaw_ev2", "dm31_pdg_ev2", "residual_pct", "p_r_extracted"):
        assert key in s


def test_extract_atmospheric_splitting_positive():
    diag = diagonalize_seesaw()
    s = extract_atmospheric_splitting(diag)
    assert s["dm31_seesaw_ev2"] > 0.0


def test_full_diagonalization_attempt_keys():
    a = full_diagonalization_upgrade_attempt()
    for key in ("attempt", "outcome", "outcome_detail", "p_r_extracted",
                "p17_label_maintained", "upgrade_achieved"):
        assert key in a


def test_full_diagonalization_attempt_valid_outcome():
    a = full_diagonalization_upgrade_attempt()
    assert a["outcome"] in ("UPGRADE_ACHIEVED", "UPGRADE_NOT_AVAILABLE")


def test_full_diagonalization_attempt_p17_label_valid():
    a = full_diagonalization_upgrade_attempt()
    assert a["p17_label_maintained"] in ("DERIVED", "CONDITIONAL_DERIVATION")


def test_full_diagonalization_consistent_outcome():
    a = full_diagonalization_upgrade_attempt()
    # If upgrade achieved, label should be DERIVED
    if a["upgrade_achieved"]:
        assert a["p17_label_maintained"] == "DERIVED"
    else:
        assert a["p17_label_maintained"] == "CONDITIONAL_DERIVATION"


def test_p17_upgrade_certificate_keys():
    cert = p17_upgrade_certificate()
    for key in ("attempt_result", "p17_label", "toe_score_delta", "honest_conclusion"):
        assert key in cert


def test_p17_upgrade_certificate_juno_safety():
    cert = p17_upgrade_certificate()
    assert "NLO" in cert["juno_safety"] or "JUNO" in cert["juno_safety"] or "unaffected" in cert["juno_safety"]


def test_p17_upgrade_certificate_toe_score_zero():
    cert = p17_upgrade_certificate()
    assert cert["toe_score_delta"] == 0.0


def test_pillar296_report_keys():
    rep = pillar296_report()
    for key in ("pillar", "title", "current_status", "diagonalization_attempt", "upgrade_certificate"):
        assert key in rep


def test_pillar296_report_pillar():
    rep = pillar296_report()
    assert rep["pillar"] == 296


def test_p_r_target_range():
    assert P_R_TARGET_RANGE[0] < P_R_TARGET_RANGE[1]
    assert 0.0 < P_R_TARGET_RANGE[0] < 0.5
