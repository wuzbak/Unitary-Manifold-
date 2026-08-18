# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 717 — FH braid geometry hardening."""
from __future__ import annotations

import math

import pytest

from src.quantum.pillar717_fh_braid_geometry_hardening import (
    C_S,
    IS_MOTT_INSULATOR,
    K_CS,
    N_W,
    PILLAR_NUMBER,
    T_KK,
    T_PRIME_KK,
    U_KK,
    U_OVER_T_KK,
    braid_bandwidth,
    fh_braid_hamiltonian_params,
    mott_gap_estimate,
    mott_insulator_verdict,
)


PARAMS = fh_braid_hamiltonian_params()
BANDWIDTH = braid_bandwidth()
GAP = mott_gap_estimate()
VERDICT = mott_insulator_verdict()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 717

    def test_canonical_constants(self) -> None:
        assert N_W == 5
        assert K_CS == 74
        assert T_KK == pytest.approx(12.0 / 37.0, rel=1e-12)
        assert U_KK == pytest.approx(74.0 / 5.0, rel=1e-12)
        assert T_PRIME_KK == pytest.approx((12.0 / 37.0) ** 2, rel=1e-12)

    def test_ratio_large(self) -> None:
        assert 45.5 < U_OVER_T_KK < 45.7
        assert C_S == T_KK

    def test_mott_constant(self) -> None:
        assert IS_MOTT_INSULATOR is True


class TestParameterExport:
    def test_params_return_dict(self) -> None:
        assert isinstance(PARAMS, dict)

    def test_params_fields(self) -> None:
        assert PARAMS["n_w"] == 5
        assert PARAMS["k_cs"] == 74
        assert PARAMS["nnn_origin"] == "t_prime = c_s^2"

    def test_hamiltonian_mentions_nnn(self) -> None:
        assert "NNN" in PARAMS["hamiltonian"]


class TestBandwidth:
    def test_bandwidth_formula(self) -> None:
        assert BANDWIDTH["bandwidth_w"] == pytest.approx(4.0 * T_KK, rel=1e-12)

    def test_nnn_bandwidth_is_larger(self) -> None:
        assert BANDWIDTH["bandwidth_w_nnn"] > BANDWIDTH["bandwidth_w"]

    def test_enhancement_factor_above_one(self) -> None:
        assert BANDWIDTH["enhancement_factor"] > 1.0

    def test_cosine_factor(self) -> None:
        expected = math.cos(2.0 * math.pi / 5.0) ** 2
        assert BANDWIDTH["cosine_squared_factor"] == pytest.approx(expected, rel=1e-12)


class TestMottGap:
    def test_gap_positive(self) -> None:
        assert GAP["delta_mott"] > 0.0

    def test_gap_criterion(self) -> None:
        assert GAP["criterion"] == "Delta_Mott = U - W_NNN"

    def test_gap_matches_u_minus_bandwidth(self) -> None:
        assert GAP["delta_mott"] == pytest.approx(U_KK - BANDWIDTH["bandwidth_w_nnn"], rel=1e-12)

    def test_gap_large(self) -> None:
        assert GAP["delta_mott"] > 10.0


class TestVerdict:
    def test_verdict_true(self) -> None:
        assert VERDICT["is_mott_insulator"] is True

    def test_verdict_regime(self) -> None:
        assert VERDICT["regime"] == "STRONG_COUPLING_MOTT"

    def test_verdict_delta_matches_gap(self) -> None:
        assert VERDICT["delta_mott"] == pytest.approx(GAP["delta_mott"], rel=1e-12)

    def test_epistemic_status(self) -> None:
        assert VERDICT["epistemic_status"] == "ANALYTICAL_ESTIMATE"
