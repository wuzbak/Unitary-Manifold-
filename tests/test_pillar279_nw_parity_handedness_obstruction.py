# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 279 — n_w Parity / Handedness Obstruction (Planck-free)."""
from __future__ import annotations

import pytest

from src.core.pillar279_nw_parity_handedness_obstruction import (
    ADJACENCY_TRACK_LABEL,
    FINALIST_PAIR,
    K_CS,
    ORDERED_BRAID_PAIR_SELECTED,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    convention_279_3_derivation_attempt,
    fallibility_admission3_summary,
    is_unique_unordered_decomposition_of_K_CS,
    nw_obstruction_report,
    ordered_pair_chirality_label,
    planck_free_obstruction_certificate,
    remaining_first_principles_residual,
    selected_ordered_pair_from_convention,
    separation_guard,
    sum_of_squares_decompositions,
    two_radius_gw_potential,
)


def test_identity_and_separation():
    assert PILLAR_NUMBER == 279
    assert PILLAR_TITLE
    assert ADJACENCY_TRACK_LABEL == "NON_HARDGATE_ADJACENT"
    assert separation_guard()["complements_existing_chi2_selection"] is True


def test_canonical_constants():
    assert K_CS == 74
    assert FINALIST_PAIR == (5, 7)
    assert ORDERED_BRAID_PAIR_SELECTED == (5, 7)


def test_sum_of_squares_K_CS_unique_unordered():
    assert is_unique_unordered_decomposition_of_K_CS() is True
    pairs = sum_of_squares_decompositions(K_CS)
    # ordered pairs: (5,7) and (7,5)
    assert set(pairs) == {(5, 7), (7, 5)}


def test_sum_of_squares_input_validation():
    with pytest.raises(ValueError):
        sum_of_squares_decompositions(1)


def test_sum_of_squares_known_cases():
    # 50 = 1 + 49 = 25 + 25; unordered pairs {(1,7),(5,5)}
    pairs = set(tuple(sorted(p)) for p in sum_of_squares_decompositions(50))
    assert (1, 7) in pairs
    assert (5, 5) in pairs
    # 13 = 2² + 3²; ordered pairs {(2,3),(3,2)}
    pairs13 = set(sum_of_squares_decompositions(13))
    assert pairs13 == {(2, 3), (3, 2)}


def test_chirality_labels():
    assert ordered_pair_chirality_label((5, 7)) == "LEFT_HANDED_SHORT_CYCLE_PRIMARY"
    assert ordered_pair_chirality_label((7, 5)) == "RIGHT_HANDED_LONG_CYCLE_PRIMARY"
    assert ordered_pair_chirality_label((5, 5)) == "CHIRAL_NEUTRAL"


def test_convention_selects_5_7():
    sel = selected_ordered_pair_from_convention()
    assert sel == (5, 7)
    # Sanity: arbitrary swap still selected the smaller first
    assert selected_ordered_pair_from_convention((7, 5)) == (5, 7)


def test_planck_free_certificate_keys_and_correctness():
    c = planck_free_obstruction_certificate()
    for key in (
        "K_CS",
        "ordered_sum_of_squares_decompositions",
        "unique_unordered_pair",
        "convention_279_3",
        "selected_ordered_pair",
        "selected_chirality_label",
        "rejected_ordered_pair",
        "rejected_chirality_label",
        "planck_data_used",
        "obstruction_complete_under_named_convention",
    ):
        assert key in c
    assert c["planck_data_used"] is False
    assert c["selected_ordered_pair"] == (5, 7)
    assert c["rejected_ordered_pair"] == (7, 5)
    assert c["obstruction_complete_under_named_convention"] is True


def test_remaining_residual_is_named_explicitly():
    r = remaining_first_principles_residual()
    assert r["id"] == "SHORT_LONG_CYCLE_ASSIGNMENT_DERIVATION"
    assert "radion" in r["blocker"].lower()


def test_fallibility_admission3_summary_structure():
    s = fallibility_admission3_summary()
    assert "Planck-free" in s["headline"]
    assert s["selected_ordered_pair"] == (5, 7)
    assert s["planck_data_used"] is False
    assert s["obstruction_complete_under_named_convention"] is True
    assert s["remaining_residual"]["id"] == "SHORT_LONG_CYCLE_ASSIGNMENT_DERIVATION"


def test_full_report_has_no_hardgate_drift():
    r = nw_obstruction_report()
    g = r["separation_guard"]
    assert g["is_hardgate"] is False
    assert g["alters_falsifier_window"] is False


# ---------------------------------------------------------------------------
# Sprint 3 — Convention 279.3 derivation tests
# ---------------------------------------------------------------------------

def test_convention_279_3_derivation_status():
    """Status must be CONDITIONAL_DERIVATION — not PROVED and not CONVENTION."""
    d = convention_279_3_derivation_attempt()
    assert d["derivation_status"] == "CONDITIONAL_DERIVATION"


def test_convention_not_arbitrary():
    """convention_needed must be False and honesty_note must be present."""
    d = convention_279_3_derivation_attempt()
    assert d["convention_needed"] is False
    assert "honesty_note" in d
    assert len(d["honesty_note"]) > 20


def test_convention_279_3_selects_nw5_as_short():
    """The derivation must place n_w = 5 on the short (smaller R) cycle."""
    d = convention_279_3_derivation_attempt()
    assert d["selected_nw_on_short_cycle"] == 5
    assert d["selected_nw_on_short_cycle_correct"] is True
    assert d["R_a_lt_R_b"] is True


def test_convention_279_3_reasoning_chain_length():
    """Reasoning chain must have at least 5 entries covering each step."""
    d = convention_279_3_derivation_attempt()
    chain = d["reasoning_chain"]
    assert isinstance(chain, list)
    assert len(chain) >= 5


def test_convention_279_3_residual_gap_named():
    """The residual gap must mention the two-radius GW analysis."""
    d = convention_279_3_derivation_attempt()
    assert "two-radius" in d["residual_gap"].lower() or "two_radius" in d["residual_gap"]
    assert "residual_gap" in d


def test_two_radius_gw_winding_asymmetry():
    """n_w=5 cycle must have a smaller effective R_min than n_w=7 cycle."""
    phi0 = 1.0
    r = two_radius_gw_potential(phi0, phi0, phi0=phi0, n_w_a=5, n_w_b=7)
    assert r["R_a_eff_min"] < r["R_b_eff_min"]
    # Both effective minima must lie above phi0 (winding tension pushes R upward)
    assert r["R_a_eff_min"] > phi0
    assert r["R_b_eff_min"] > phi0


def test_winding_energy_favors_larger_radius():
    """Higher winding number produces a larger equilibrium radius (winding tension)."""
    phi0 = 1.0
    r5 = two_radius_gw_potential(phi0, phi0, phi0, n_w_a=5, n_w_b=5)
    r7 = two_radius_gw_potential(phi0, phi0, phi0, n_w_a=7, n_w_b=7)
    # Cycle with n=7 should sit at larger R_eff_min than n=5
    assert r7["R_a_eff_min"] > r5["R_a_eff_min"]


def test_two_radius_gw_potential_keys():
    """Return dict must contain all expected keys."""
    r = two_radius_gw_potential(1.0, 1.2, 1.0, 5, 7)
    for key in (
        "R_a", "R_b", "phi0", "n_w_a", "n_w_b", "lam_gw",
        "V_a", "V_b", "delta_V_a", "delta_V_b",
        "V_eff_a", "V_eff_b", "R_a_eff_min", "R_b_eff_min",
        "nw_on_short_cycle",
    ):
        assert key in r, f"Missing key: {key}"


def test_two_radius_gw_bare_minimum_at_phi0():
    """With zero winding the effective minimum should equal phi0 exactly."""
    phi0 = 1.5
    r = two_radius_gw_potential(phi0, phi0, phi0, n_w_a=0, n_w_b=0)
    assert abs(r["R_a_eff_min"] - phi0) < 1e-8
    assert abs(r["R_b_eff_min"] - phi0) < 1e-8


def test_two_radius_gw_winding_correction_positive():
    """Winding corrections delta_V must be non-negative."""
    r = two_radius_gw_potential(1.0, 1.0, 1.0, n_w_a=5, n_w_b=7)
    assert r["delta_V_a"] >= 0.0
    assert r["delta_V_b"] >= 0.0
    # More windings → larger winding correction at same R
    assert r["delta_V_b"] > r["delta_V_a"]


def test_two_radius_gw_lambda_scaling():
    """Doubling lam_gw should move R_eff_min closer to phi0 (stiffer potential)."""
    phi0 = 1.0
    r1 = two_radius_gw_potential(phi0, phi0, phi0, n_w_a=5, n_w_b=7, lam_gw=1.0)
    r2 = two_radius_gw_potential(phi0, phi0, phi0, n_w_a=5, n_w_b=7, lam_gw=4.0)
    # Stiffer GW ⇒ winding shifts R_min less far from phi0
    assert abs(r2["R_a_eff_min"] - phi0) < abs(r1["R_a_eff_min"] - phi0)
    assert abs(r2["R_b_eff_min"] - phi0) < abs(r1["R_b_eff_min"] - phi0)

