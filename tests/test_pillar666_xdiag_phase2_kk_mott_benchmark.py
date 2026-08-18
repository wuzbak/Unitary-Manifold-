# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 666 — XDiag Phase 2 KK Mott benchmark."""
from __future__ import annotations

import math

from src.core.pillar666_xdiag_phase2_kk_mott_benchmark_adjacent import (
    ADJACENT_TRACK,
    BRAID_CONDENSATE_CONSISTENT,
    IS_MOTT_INSULATOR,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    ROUTING_ZONE,
    SCHEMA_VERSION,
    U_OVER_T_MOTT,
    VERSION,
    XDIAG_PRODUCTION_INSTALL_REQUIRED,
    analytical_mott_prediction,
    kk_mott_parameters,
    parity_gate_spec,
    pillar_report,
    schema_round_trip_spec,
)

PARAMS = kk_mott_parameters()
PREDICTION = analytical_mott_prediction()
SCHEMA_SPEC = schema_round_trip_spec()
PARITY = parity_gate_spec()
REPORT = pillar_report()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 666

    def test_status(self) -> None:
        assert PILLAR_STATUS == "XDIAG_PHASE2_KK_MOTT_BENCHMARK_CERTIFIED"

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_u_over_t_mott(self) -> None:
        assert math.isclose(U_OVER_T_MOTT, 45.63333333333333, rel_tol=0.0, abs_tol=0.1)

    def test_mott_flag(self) -> None:
        assert IS_MOTT_INSULATOR is True

    def test_routing_zone(self) -> None:
        assert ROUTING_ZONE == "um_exact_dense"

    def test_schema_version(self) -> None:
        assert SCHEMA_VERSION == "1.0.0"

    def test_xdiag_required(self) -> None:
        assert XDIAG_PRODUCTION_INSTALL_REQUIRED is True


class TestParameters:
    def test_parameter_keys(self) -> None:
        assert set(PARAMS) == {
            "l_sites",
            "t_kk",
            "u_kk",
            "u_over_t",
            "mott_transition_threshold",
            "is_mott_insulator",
            "routing_zone",
            "schema_version",
        }

    def test_parameter_values(self) -> None:
        assert PARAMS["l_sites"] == 8
        assert PARAMS["is_mott_insulator"] is True
        assert PARAMS["routing_zone"] == "um_exact_dense"


class TestAnalyticalPrediction:
    def test_j_eff_window(self) -> None:
        assert 0.0 < PREDICTION["j_eff"] < 0.1

    def test_spin_gap_matches_j_eff(self) -> None:
        assert math.isclose(
            PREDICTION["spin_gap_estimate"],
            PREDICTION["j_eff"],
            rel_tol=0.0,
            abs_tol=1e-15,
        )

    def test_mott_confirmed(self) -> None:
        assert PREDICTION["mott_insulator_confirmed"] is True

    def test_p412_consistency(self) -> None:
        assert PREDICTION["p412_consistency"] is BRAID_CONDENSATE_CONSISTENT


class TestSchemaAndParity:
    def test_required_fields_count(self) -> None:
        assert len(SCHEMA_SPEC["required_fields"]) == 3

    def test_optional_fields_count(self) -> None:
        assert len(SCHEMA_SPEC["optional_fields"]) == 3

    def test_required_fields_content(self) -> None:
        assert SCHEMA_SPEC["required_fields"] == [
            "ground_energy",
            "first_gap",
            "staggered_magnetization",
        ]

    def test_optional_fields_content(self) -> None:
        assert SCHEMA_SPEC["optional_fields"] == [
            "charge_gap",
            "spin_gap",
            "double_occupancy",
        ]

    def test_parity_zone(self) -> None:
        assert PARITY["routing_zone"] == "um_exact_dense"

    def test_parity_counts(self) -> None:
        assert PARITY["required_pass_count"] == 3
        assert PARITY["optional_pass_count_if_present"] == 3


class TestReport:
    def test_report_core_keys(self) -> None:
        assert set(REPORT).issuperset(
            {
                "pillar",
                "title",
                "status",
                "version",
                "adjacent_track",
                "toe_score_delta",
                "hardgate_score_delta",
            }
        )

    def test_report_values(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0
