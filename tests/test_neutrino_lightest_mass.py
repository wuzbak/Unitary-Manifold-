# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 140: Lightest Neutrino Mass RS (src/core/neutrino_lightest_mass.py).

IMPORTANT: m_nu1 ≈ 1.097 eV — this VIOLATES the Planck Σm_ν < 0.12 eV bound.
planck_consistent = False by design; this is honestly documented as an open constraint.
"""

import math
import pytest

from src.core.neutrino_lightest_mass import (
    c_right_neutrino_lightest,
    rs_dirac_zero_mode_profile_local,
    neutrino_lightest_mass_rs,
    lightest_neutrino_closure_status,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def result():
    return neutrino_lightest_mass_rs()


@pytest.fixture(scope="module")
def status():
    return lightest_neutrino_closure_status()


# ---------------------------------------------------------------------------
# c_right_neutrino_lightest
# ---------------------------------------------------------------------------

def test_c_rnu1_returns_float():
    val = c_right_neutrino_lightest()
    assert isinstance(val, float)


def test_c_rnu1_exact_value():
    assert abs(c_right_neutrino_lightest() - 23 / 25) < 1e-12


def test_c_rnu1_equals_0920():
    assert abs(c_right_neutrino_lightest() - 0.920) < 1e-12


def test_c_rnu1_in_physical_range():
    c = c_right_neutrino_lightest()
    assert 0.5 < c < 1.0


# ---------------------------------------------------------------------------
# rs_dirac_zero_mode_profile_local
# ---------------------------------------------------------------------------

def test_profile_at_c_rnu1_positive():
    c = c_right_neutrino_lightest()
    assert rs_dirac_zero_mode_profile_local(c) > 0


def test_profile_at_c_rnu1_small():
    c = c_right_neutrino_lightest()
    val = rs_dirac_zero_mode_profile_local(c)
    # For c=0.92 with piKR=37, profile is exponentially suppressed: ~1.6e-7
    assert val < 1e-5


def test_profile_at_c_rnu1_value():
    c = c_right_neutrino_lightest()
    val = rs_dirac_zero_mode_profile_local(c)
    assert abs(val - 1.6338e-07) < 1e-10


def test_profile_c_051():
    # c=0.51 is just above the singular c=0.5 point
    val = rs_dirac_zero_mode_profile_local(0.51)
    assert val > 0


def test_profile_c_051_value():
    val = rs_dirac_zero_mode_profile_local(0.51)
    assert abs(val - 0.135089) < 0.0001


def test_profile_c_070():
    val = rs_dirac_zero_mode_profile_local(0.70)
    assert 0.0001 < val < 0.01


def test_profile_decreases_with_increasing_c():
    # Higher c → more peaked toward UV → smaller profile at IR end
    val_07 = rs_dirac_zero_mode_profile_local(0.70)
    val_09 = rs_dirac_zero_mode_profile_local(0.90)
    assert val_09 < val_07


def test_profile_returns_float():
    val = rs_dirac_zero_mode_profile_local(0.80)
    assert isinstance(val, float)


def test_profile_positive_for_c_above_half():
    for c in [0.51, 0.60, 0.70, 0.80, 0.90, 0.92]:
        assert rs_dirac_zero_mode_profile_local(c) > 0


# ---------------------------------------------------------------------------
# neutrino_lightest_mass_rs — return type and keys
# ---------------------------------------------------------------------------

def test_result_is_dict(result):
    assert isinstance(result, dict)


def test_result_has_c_rnu1(result):
    assert "c_rnu1" in result


def test_result_has_c_lnu1(result):
    assert "c_lnu1" in result


def test_result_has_f0_rnu1(result):
    assert "f0_rnu1" in result


def test_result_has_f0_lnu1(result):
    assert "f0_lnu1" in result


def test_result_has_m_nu1_ev(result):
    assert "m_nu1_ev" in result


def test_result_has_planck_consistent(result):
    assert "planck_consistent" in result


def test_result_has_status(result):
    assert "status" in result


def test_result_has_honest_note(result):
    assert "honest_note" in result


# ---------------------------------------------------------------------------
# c_R and c_L values
# ---------------------------------------------------------------------------

def test_c_rnu1_in_result(result):
    assert abs(result["c_rnu1"] - 0.920) < 1e-12


def test_c_lnu1_in_result(result):
    assert abs(result["c_lnu1"] - 0.776) < 0.001


def test_c_rnu1_gt_c_lnu1(result):
    assert result["c_rnu1"] > result["c_lnu1"]


# ---------------------------------------------------------------------------
# Zero-mode profiles
# ---------------------------------------------------------------------------

def test_f0_rnu1_positive(result):
    assert result["f0_rnu1"] > 0


def test_f0_lnu1_positive(result):
    assert result["f0_lnu1"] > 0


def test_f0_lnu1_gt_f0_rnu1(result):
    # c_L < c_R → left-handed profile larger (less UV-suppressed)
    assert result["f0_lnu1"] > result["f0_rnu1"]


def test_f0_rnu1_value(result):
    assert abs(result["f0_rnu1"] - 1.6338e-07) < 1e-10


def test_f0_lnu1_value(result):
    assert abs(result["f0_lnu1"] - 2.7287e-05) < 1e-8


# ---------------------------------------------------------------------------
# m_nu1 mass — CRITICAL: ~1.097 eV, NOT meV
# ---------------------------------------------------------------------------

def test_m_nu1_positive(result):
    assert result["m_nu1_ev"] > 0


def test_m_nu1_above_half_ev(result):
    # It's ~1.097 eV, clearly above 0.5 eV
    assert result["m_nu1_ev"] > 0.5


def test_m_nu1_below_two_ev(result):
    assert result["m_nu1_ev"] < 2.0


def test_m_nu1_value(result):
    assert abs(result["m_nu1_ev"] - 1.0977) < 0.001


def test_m_nu1_exceeds_planck_bound(result):
    planck_bound = result.get("planck_limit_ev", 0.12)
    assert result["m_nu1_ev"] > planck_bound


# ---------------------------------------------------------------------------
# planck_consistent = False (honest documentation)
# ---------------------------------------------------------------------------

def test_planck_consistent_false(result):
    assert result["planck_consistent"] is False


def test_planck_limit_is_012_ev(result):
    assert abs(result.get("planck_limit_ev", 0.12) - 0.12) < 0.001


# ---------------------------------------------------------------------------
# Status and honest_note
# ---------------------------------------------------------------------------

def test_status_contains_constrained(result):
    assert "CONSTRAINED" in result["status"]


def test_honest_note_non_empty(result):
    assert len(result["honest_note"]) > 0


def test_honest_note_mentions_planck(result):
    note = result["honest_note"].lower()
    assert "planck" in note


def test_honest_note_mentions_violation_or_bound(result):
    note = result["honest_note"].lower()
    assert "bound" in note or "violat" in note or "exceed" in note


# ---------------------------------------------------------------------------
# lightest_neutrino_closure_status
# ---------------------------------------------------------------------------

def test_closure_status_is_dict(status):
    assert isinstance(status, dict)


def test_closure_status_pillar_140(status):
    assert status["pillar"] == 140


def test_closure_status_constrained(status):
    assert "CONSTRAINED" in status["status"]


def test_closure_status_planck_consistent_false(status):
    assert status["planck_consistent"] is False


def test_closure_status_predicted_ev(status):
    assert abs(status["predicted_ev"] - 1.0977) < 0.001


def test_closure_status_has_honest_note(status):
    assert "honest_note" in status


def test_closure_status_honest_note_non_empty(status):
    assert len(status["honest_note"]) > 0


def test_closure_status_closed_false(status):
    # Planck-violating → not fully closed
    assert status.get("closed") is False


# ---------------------------------------------------------------------------
# neutrino_mass_pillar135_140_consistency — cross-pillar inconsistency tracker
# ---------------------------------------------------------------------------

from src.core.neutrino_lightest_mass import neutrino_mass_pillar135_140_consistency


@pytest.fixture(scope="module")
def cross_check():
    return neutrino_mass_pillar135_140_consistency()


def test_cross_check_is_dict(cross_check):
    assert isinstance(cross_check, dict)


def test_cross_check_pillar135_mass_ev(cross_check):
    # Pillar 135 implied m_ν₁ ≈ 1.49 meV
    assert 1.0 < cross_check["m_nu1_pillar135_meV"] < 2.0


def test_cross_check_pillar140_mass_ev(cross_check):
    # Pillar 140 RS Dirac m_ν₁ ≈ 1.086 eV — close to documented value
    assert 0.9 < cross_check["m_nu1_pillar140_ev"] < 1.3


def test_cross_check_inconsistency_flag_true(cross_check):
    # The two estimates differ by > 2 orders of magnitude
    assert cross_check["inconsistency_flag"] is True


def test_cross_check_log10_ratio_above_2(cross_check):
    # At least 2 orders of magnitude difference
    assert cross_check["log10_ratio"] > 2.0


def test_cross_check_status_is_string(cross_check):
    assert isinstance(cross_check["status"], str)


def test_cross_check_status_mentions_open_inconsistency(cross_check):
    assert "OPEN INCONSISTENCY" in cross_check["status"]


def test_cross_check_has_pillar_notes(cross_check):
    assert "pillar_135_note" in cross_check
    assert "pillar_140_note" in cross_check
