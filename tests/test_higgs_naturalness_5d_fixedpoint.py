# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Higgs naturalness 5D KK fixed-point module (Gap A3 partial closure)."""

from __future__ import annotations

import math

import pytest

from src.core.higgs_naturalness_5d_fixedpoint import (
    M_H_GEV,
    NATURALNESS_THRESHOLD,
    kk_higgs_naturalness,
    kk_loop_sum_converges,
    kk_mode_mass,
)

_EXPECTED_KEYS = frozenset(
    [
        "k",
        "R",
        "N_modes",
        "M_KK_GeV",
        "delta_mH2_GeV2",
        "m_H2_GeV2",
        "tuning_Delta",
        "naturalness_partial_closure",
        "status",
        "mode_contributions",
        "convergence_ratio",
    ]
)

_VALID_STATUSES = {"DERIVED_PARTIAL", "ARCHITECTURE_LIMIT_CERTIFIED"}

# Canonical RS1 radius: k*R = 14.16/π so that exp(-π k R) ≈ TeV/M_Pl at k=0.1
R_CANONICAL: float = 14.16 / math.pi / 0.1


# ---------------------------------------------------------------------------
# kk_mode_mass tests
# ---------------------------------------------------------------------------

def test_kk_mode_mass_n1_positive() -> None:
    assert kk_mode_mass(1, 1e3, 0.1) > 0


def test_kk_mode_mass_increases_with_n() -> None:
    masses = [kk_mode_mass(n, 1e3, 0.1) for n in range(1, 6)]
    assert all(masses[i] < masses[i + 1] for i in range(len(masses) - 1))


def test_kk_mode_mass_positive_all_n() -> None:
    for n in range(1, 20):
        assert kk_mode_mass(n, 1e3, 0.05) > 0


def test_kk_mode_mass_warp_correction_applied() -> None:
    bare = 1.0 * 1e3  # n=1, no correction
    corrected = kk_mode_mass(1, 1e3, 0.1)
    assert corrected > bare


# ---------------------------------------------------------------------------
# kk_higgs_naturalness — dict structure tests
# ---------------------------------------------------------------------------

def test_naturalness_dict_has_all_keys() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert _EXPECTED_KEYS.issubset(result.keys())


def test_delta_mH2_positive() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert result["delta_mH2_GeV2"] > 0


def test_m_H2_correct() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert result["m_H2_GeV2"] == pytest.approx(M_H_GEV ** 2, rel=1e-10)


def test_tuning_is_nonnegative() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert result["tuning_Delta"] >= 0.0


def test_tuning_present_in_result() -> None:
    result = kk_higgs_naturalness(k=0.05, R=30.0)
    assert "tuning_Delta" in result


def test_mode_contributions_list_length() -> None:
    N = 7
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL, N_modes=N)
    assert len(result["mode_contributions"]) == N


def test_mode_contributions_all_positive() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL, N_modes=10)
    assert all(c > 0 for c in result["mode_contributions"])


def test_convergence_ratio_finite() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert math.isfinite(result["convergence_ratio"])


def test_status_valid_string() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert result["status"] in _VALID_STATUSES


def test_more_modes_larger_sum() -> None:
    R = R_CANONICAL
    small = kk_higgs_naturalness(k=0.1, R=R, N_modes=5)
    large = kk_higgs_naturalness(k=0.1, R=R, N_modes=20)
    assert large["delta_mH2_GeV2"] > small["delta_mH2_GeV2"]


def test_larger_k_smaller_m_kk() -> None:
    R = R_CANONICAL
    res_small_k = kk_higgs_naturalness(k=0.05, R=R)
    res_large_k = kk_higgs_naturalness(k=0.15, R=R)
    assert res_large_k["M_KK_GeV"] < res_small_k["M_KK_GeV"]


def test_naturalness_partial_closure_is_bool() -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL)
    assert isinstance(result["naturalness_partial_closure"], bool)


# ---------------------------------------------------------------------------
# kk_loop_sum_converges
# ---------------------------------------------------------------------------

def test_kk_loop_converges_returns_bool() -> None:
    assert isinstance(kk_loop_sum_converges(k=0.1, R=R_CANONICAL), bool)


def test_kk_loop_converges_standard_params() -> None:
    assert kk_loop_sum_converges(k=0.1, R=R_CANONICAL) is True


# ---------------------------------------------------------------------------
# Parametric: tuning_Delta is finite positive for a range of (k, R)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "k,R",
    [
        (0.05, 40.0),
        (0.10, R_CANONICAL),
        (0.12, 25.0),
        (0.08, 35.0),
        (0.15, 20.0),
    ],
)
def test_tuning_delta_finite_positive(k: float, R: float) -> None:
    result = kk_higgs_naturalness(k=k, R=R, N_modes=10)
    delta = result["tuning_Delta"]
    assert math.isfinite(delta)
    assert delta > 0.0


@pytest.mark.parametrize(
    "k,R",
    [
        (0.05, 40.0),
        (0.10, R_CANONICAL),
        (0.12, 25.0),
    ],
)
def test_mkk_positive_and_finite(k: float, R: float) -> None:
    result = kk_higgs_naturalness(k=k, R=R)
    assert result["M_KK_GeV"] > 0
    assert math.isfinite(result["M_KK_GeV"])


@pytest.mark.parametrize("N_modes", [5, 10, 15, 20])
def test_mode_contributions_length_parametric(N_modes: int) -> None:
    result = kk_higgs_naturalness(k=0.1, R=R_CANONICAL, N_modes=N_modes)
    assert len(result["mode_contributions"]) == N_modes
