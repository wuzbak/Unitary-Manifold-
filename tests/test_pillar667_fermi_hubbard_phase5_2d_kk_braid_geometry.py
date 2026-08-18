# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 667 — Fermi-Hubbard Phase 5 2D KK braid geometry."""
from __future__ import annotations

import math

from src.core.pillar667_fermi_hubbard_phase5_2d_kk_braid_geometry_adjacent import (
    ADJACENT_TRACK,
    C_S,
    PARTICLE_HOLE_SYMMETRY_BROKEN,
    PHASE4_CONSISTENCY,
    PILLAR_NUMBER,
    ROUTING_L4,
    ROUTING_L6,
    T_PRIME_NNN,
    U_KK,
    VERSION,
    asymmetric_mott_lobe,
    braid_geometry_parameters,
    fermi_velocity_cs_limit,
    pillar_report,
)

PARAMS = braid_geometry_parameters()
LOBE = asymmetric_mott_lobe()
FERMI = fermi_velocity_cs_limit()
REPORT = pillar_report()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 667

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_t_prime_value(self) -> None:
        assert math.isclose(T_PRIME_NNN, C_S**2, rel_tol=0.0, abs_tol=1e-15)

    def test_symmetry_broken(self) -> None:
        assert PARTICLE_HOLE_SYMMETRY_BROKEN is True

    def test_routes(self) -> None:
        assert ROUTING_L4 == "um_exact_dense"
        assert ROUTING_L6 == "bridge_crosscheck"


class TestParameters:
    def test_parameter_fields(self) -> None:
        assert PARAMS["l_sizes"] == [4, 6]
        assert PARAMS["particle_hole_symmetry_broken"] is True

    def test_c_s_matches_t_kk_ratio(self) -> None:
        assert math.isclose(LOBE["asymmetry_ratio"], C_S, rel_tol=0.0, abs_tol=1e-15)

    def test_phase4_consistency(self) -> None:
        assert LOBE["phase4_consistency"] == PHASE4_CONSISTENCY


class TestAsymmetricMottLobe:
    def test_asymmetric_flag(self) -> None:
        assert LOBE["mott_lobe_asymmetric"] is True

    def test_critical_u_over_t_braid(self) -> None:
        assert 45.5 < LOBE["critical_u_over_t"]["braid_geometry_estimate"] < 45.7

    def test_t_prime_over_u_positive(self) -> None:
        assert 0.0 < LOBE["t_prime_over_u"] < LOBE["t_over_u"]


class TestFermiVelocity:
    def test_limit_equals_c_s(self) -> None:
        assert math.isclose(FERMI["fermi_velocity_limit"], C_S, rel_tol=0.0, abs_tol=1e-15)

    def test_u_over_t_large(self) -> None:
        assert FERMI["u_over_t"] > 40.0

    def test_consistency_flag(self) -> None:
        assert FERMI["consistency"] is True


class TestReport:
    def test_report_core_fields(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["version"] == "v21.0"
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0

    def test_report_contains_sections(self) -> None:
        assert set(REPORT).issuperset(
            {
                "braid_geometry_parameters",
                "asymmetric_mott_lobe",
                "fermi_velocity_cs_limit",
            }
        )
