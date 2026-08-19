# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 719 — quantum lane Phase 3 synthesis."""
from __future__ import annotations

from src.quantum.pillar719_quantum_lane_phase3_synthesis import (
    LEAN4_FORMAL_BRIDGE_STATUS,
    PILLAR_NUMBER,
    QUANTUM_LANE_PHASE3_SYNTHESIZED,
    quantum_lane_full_status,
    quantum_lane_phase3_synthesis,
)


SYNTHESIS = quantum_lane_phase3_synthesis()
FULL = quantum_lane_full_status()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 719

    def test_phase3_constant(self) -> None:
        assert QUANTUM_LANE_PHASE3_SYNTHESIZED is True

    def test_lean4_honesty(self) -> None:
        assert LEAN4_FORMAL_BRIDGE_STATUS == "NOT_YET_FORMALISED"


class TestSynthesis:
    def test_phase_lists(self) -> None:
        assert SYNTHESIS["phase2_pillars"] == [666, 667, 668, 669]
        assert SYNTHESIS["sprint_dd_pillars"] == [716, 717, 718]

    def test_phase2_valid(self) -> None:
        assert SYNTHESIS["phase2_certifications_valid"] is True

    def test_stub_health_passes(self) -> None:
        assert SYNTHESIS["stub_health_passes"] is True

    def test_phase3_synthesized(self) -> None:
        assert SYNTHESIS["quantum_lane_phase3_synthesized"] is True

    def test_component_statuses(self) -> None:
        assert SYNTHESIS["components"]["p716_xdiag_production_stub"] == "REQUIRES_PRODUCTION_INSTALL"
        assert SYNTHESIS["components"]["p718_kk_vqe_hardening"] == "CERTIFIED"

    def test_epistemic_status(self) -> None:
        assert SYNTHESIS["epistemic_status"] == "SCAFFOLD"


class TestFullStatus:
    def test_overall_status(self) -> None:
        assert FULL["overall_status"] == "PHASE3_SYNTHESIZED"

    def test_counts(self) -> None:
        assert FULL["n_certified_components"] == 7
        assert FULL["n_requires_production_install"] == 1

    def test_production_install_component(self) -> None:
        assert FULL["requires_production_install_components"] == ["p716_xdiag_production_stub"]

    def test_certified_contains_phase2_and_sprint_dd(self) -> None:
        assert "p666_phase2_kk_mott_benchmark" in FULL["certified_components"]
        assert "p717_fh_braid_geometry_hardening" in FULL["certified_components"]

    def test_full_carries_lean4_status(self) -> None:
        assert FULL["lean4_formal_bridge_status"] == "NOT_YET_FORMALISED"
