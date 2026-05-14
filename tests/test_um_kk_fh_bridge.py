# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/quantum/um_kk_fh_bridge.py — adjacent-track KK↔FH bridge."""
from __future__ import annotations

import pytest

from src.quantum.um_kk_fh_bridge import (
    BRIDGE_STATUS,
    KK_KCS,
    KK_N1,
    KK_N2,
    KK_PHASE,
    KK_RHO,
    KK_U_OVER_T,
    KKFHBridgeResult,
    kk_to_fh_parameters,
    mott_insulator_verdict,
    run_kk_fh_bridge,
)


# ---------------------------------------------------------------------------
# Module-level constants
# ---------------------------------------------------------------------------


def test_kk_n1_n2_kcs() -> None:
    assert KK_N1 == 5
    assert KK_N2 == 7
    assert KK_KCS == 74


def test_kk_rho() -> None:
    assert KK_RHO == pytest.approx(70 / 74, rel=1e-12)


def test_kk_u_over_t() -> None:
    assert KK_U_OVER_T == pytest.approx(74 ** 2 / 70, rel=1e-12)


def test_kk_phase() -> None:
    assert KK_PHASE == "MOTT_INSULATOR"


def test_bridge_status() -> None:
    assert BRIDGE_STATUS == "ADJACENT_TRACK_CLOSED"


# ---------------------------------------------------------------------------
# kk_to_fh_parameters
# ---------------------------------------------------------------------------


def test_kk_to_fh_parameters_defaults() -> None:
    p = kk_to_fh_parameters()
    assert p["t"] == pytest.approx(1.0)
    assert p["U_over_t"] == pytest.approx(KK_U_OVER_T, rel=1e-12)
    assert p["rho"] == pytest.approx(KK_RHO, rel=1e-12)
    assert "phase" in p


def test_kk_to_fh_parameters_hopping_scale() -> None:
    p = kk_to_fh_parameters(hopping_scale=2.0)
    assert p["t"] == pytest.approx(2.0)
    assert p["U"] == pytest.approx(KK_U_OVER_T * 2.0, rel=1e-10)


def test_kk_to_fh_parameters_custom_braid() -> None:
    p = kk_to_fh_parameters(n1=3, n2=5, k_cs=34)
    assert p["rho"] == pytest.approx(2 * 3 * 5 / 34, rel=1e-12)
    assert p["U_over_t"] == pytest.approx(34 ** 2 / (2 * 3 * 5), rel=1e-12)


# ---------------------------------------------------------------------------
# mott_insulator_verdict
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("u_over_t,expected", [
    (0.5, "WEAKLY_CORRELATED"),
    (4.0, "WEAKLY_CORRELATED"),
    (4.1, "MOTT_INSULATING"),
    (10.0, "MOTT_INSULATING"),
    (10.1, "STRONGLY_MOTT_INSULATING"),
    (78.0, "STRONGLY_MOTT_INSULATING"),
])
def test_mott_insulator_verdict(u_over_t: float, expected: str) -> None:
    assert mott_insulator_verdict(u_over_t) == expected


# ---------------------------------------------------------------------------
# run_kk_fh_bridge
# ---------------------------------------------------------------------------


def test_run_kk_fh_bridge_returns_dataclass() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert isinstance(r, KKFHBridgeResult)


def test_run_kk_fh_bridge_constants_correct() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.n1 == 5
    assert r.n2 == 7
    assert r.k_cs == 74


def test_run_kk_fh_bridge_u_over_t() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.u_over_t == pytest.approx(KK_U_OVER_T, rel=1e-12)


def test_run_kk_fh_bridge_strongly_mott() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.phase == "STRONGLY_MOTT_INSULATING"


def test_run_kk_fh_bridge_status_confirmed() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.status == "ADJACENT_TRACK_MOTT_INSULATOR_CONFIRMED"


def test_run_kk_fh_bridge_charge_gap_positive() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.charge_gap > 0.0


def test_run_kk_fh_bridge_ground_energy_negative() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.ground_energy < 0.0


def test_run_kk_fh_bridge_hopping_scale() -> None:
    r1 = run_kk_fh_bridge(n_sites=2, hopping_scale=1.0)
    r2 = run_kk_fh_bridge(n_sites=2, hopping_scale=2.0)
    assert r2.ground_energy == pytest.approx(r1.ground_energy * 2.0, rel=1e-6)
    assert r2.charge_gap == pytest.approx(r1.charge_gap * 2.0, rel=1e-6)


def test_run_kk_fh_bridge_n_sites_stored() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.n_sites == 2


# ---------------------------------------------------------------------------
# Section A (additional) — Imports and constants
# ---------------------------------------------------------------------------


def test_bridge_status_exact_string() -> None:
    assert BRIDGE_STATUS == "ADJACENT_TRACK_CLOSED"


def test_kk_u_over_t_within_1pct_of_78_17() -> None:
    # 74²/70 = 5476/70 ≈ 78.23; this test uses the exact formula as the
    # source of truth to avoid decimal drift.
    assert KK_U_OVER_T == pytest.approx(74 ** 2 / 70, rel=1e-10)


def test_kk_u_over_t_exact_formula() -> None:
    assert KK_U_OVER_T == pytest.approx(74 ** 2 / (2 * 5 * 7), rel=1e-12)


def test_kk_to_fh_parameters_callable() -> None:
    assert callable(kk_to_fh_parameters)


def test_run_kk_fh_bridge_callable() -> None:
    assert callable(run_kk_fh_bridge)


def test_mott_insulator_verdict_callable() -> None:
    assert callable(mott_insulator_verdict)


# ---------------------------------------------------------------------------
# Section B (additional) — kk_to_fh_parameters
# ---------------------------------------------------------------------------


def test_kk_to_fh_parameters_returns_dict() -> None:
    assert isinstance(kk_to_fh_parameters(), dict)


def test_kk_to_fh_parameters_u_over_t_within_1pct() -> None:
    # Exact formula: 74²/70 = 5476/70 ≈ 78.23; test against the formula, not a rounded literal.
    p = kk_to_fh_parameters()
    assert p["U_over_t"] == pytest.approx(74 ** 2 / 70, rel=1e-10)


def test_kk_to_fh_parameters_t_default_1() -> None:
    p = kk_to_fh_parameters()
    assert p["t"] == pytest.approx(1.0, abs=1e-12)


def test_kk_to_fh_parameters_u_equals_u_over_t_times_t() -> None:
    p = kk_to_fh_parameters()
    assert p["U"] == pytest.approx(p["U_over_t"] * p["t"], rel=1e-12)


def test_kk_to_fh_parameters_phase_mott() -> None:
    p = kk_to_fh_parameters()
    assert p["phase"] == "STRONGLY_MOTT_INSULATING"


def test_kk_to_fh_parameters_hopping_scale_2_t_and_u() -> None:
    p = kk_to_fh_parameters(hopping_scale=2.0)
    assert p["t"] == pytest.approx(2.0, abs=1e-12)
    assert p["U"] == pytest.approx(KK_U_OVER_T * 2.0, rel=1e-10)


def test_kk_to_fh_parameters_rho_exact() -> None:
    p = kk_to_fh_parameters()
    assert p["rho"] == pytest.approx(70 / 74, rel=1e-12)


def test_kk_to_fh_parameters_u_over_t_ratio_exact() -> None:
    p = kk_to_fh_parameters()
    assert p["U"] / p["t"] == pytest.approx(p["U_over_t"], rel=1e-10)


# ---------------------------------------------------------------------------
# Section C (additional) — mott_insulator_verdict
# ---------------------------------------------------------------------------


def test_verdict_78_strongly_mott() -> None:
    assert mott_insulator_verdict(78.0) == "STRONGLY_MOTT_INSULATING"


def test_verdict_5_mott_insulating() -> None:
    assert mott_insulator_verdict(5.0) == "MOTT_INSULATING"


def test_verdict_1_weakly_correlated() -> None:
    assert mott_insulator_verdict(1.0) == "WEAKLY_CORRELATED"


def test_verdict_10_not_weakly_correlated() -> None:
    assert mott_insulator_verdict(10.0) != "WEAKLY_CORRELATED"


def test_verdict_4_point_0001_mott_or_strongly() -> None:
    v = mott_insulator_verdict(4.0001)
    assert v in ("MOTT_INSULATING", "STRONGLY_MOTT_INSULATING")


def test_verdict_returns_string() -> None:
    assert isinstance(mott_insulator_verdict(78.17), str)


# ---------------------------------------------------------------------------
# Section D (additional) — run_kk_fh_bridge
# ---------------------------------------------------------------------------


def test_run_kk_fh_bridge_phase_is_mott() -> None:
    """Phase should be STRONGLY_MOTT_INSULATING (U/t ≈ 78 >> 10)."""
    r = run_kk_fh_bridge(n_sites=2)
    assert r.phase == "STRONGLY_MOTT_INSULATING"


def test_run_kk_fh_bridge_status_contains_confirmed() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert "CONFIRMED" in r.status or "MOTT_INSULATOR" in r.status


def test_run_kk_fh_bridge_rho_correct() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert r.rho == pytest.approx(70 / 74, rel=1e-12)


def test_run_kk_fh_bridge_staggered_mag_is_float() -> None:
    r = run_kk_fh_bridge(n_sites=2)
    assert isinstance(r.staggered_magnetization, float)


# ---------------------------------------------------------------------------
# Section E — Physics consistency
# ---------------------------------------------------------------------------


def test_kk_model_is_mott_insulating() -> None:
    """KK parameters place the FH system in the Mott insulating regime (charge_gap > 0)."""
    r = run_kk_fh_bridge(n_sites=2)
    assert r.charge_gap > 0.0


def test_kk_u_over_t_exact_relationship() -> None:
    assert KK_U_OVER_T == 74 ** 2 / (2 * 5 * 7)
