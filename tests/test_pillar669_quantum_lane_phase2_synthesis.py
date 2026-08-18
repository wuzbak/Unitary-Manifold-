# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 669 — Quantum lane Phase 2 synthesis."""
from __future__ import annotations

from src.core.pillar669_quantum_lane_phase2_synthesis_adjacent import (
    ADJACENT_TRACK,
    BRAID_SOUND_SPEED_CONTROLS_FERMI_VELOCITY,
    MOTT_U_OVER_T,
    PHASE2_PILLARS,
    PILLAR_NUMBER,
    VERSION,
    XDIAG_PRODUCTION_INSTALL_REQUIRED,
    pillar_report,
    synthesis_certificate,
    what_is_NOT_claimed,
    what_is_claimed,
)

CERTIFICATE = synthesis_certificate()
REPORT = pillar_report()
CLAIMS = what_is_claimed()
NONCLAIMS = what_is_NOT_claimed()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 669

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_phase2_pillars(self) -> None:
        assert PHASE2_PILLARS == [666, 667, 668]

    def test_mott_ratio(self) -> None:
        assert MOTT_U_OVER_T == 45.6


class TestSynthesis:
    def test_certificate_flags(self) -> None:
        assert CERTIFICATE["phase2_certified"] is True
        assert CERTIFICATE["xdiag_production_install_required"] is True

    def test_velocity_control_flag(self) -> None:
        assert (
            CERTIFICATE["braid_sound_speed_controls_fermi_velocity"]
            is BRAID_SOUND_SPEED_CONTROLS_FERMI_VELOCITY
            is True
        )


class TestClaims:
    def test_claim_counts(self) -> None:
        assert len(CLAIMS) >= 4
        assert len(NONCLAIMS) >= 3

    def test_nonclaim_mentions_no_live_xdiag(self) -> None:
        assert any("No live XDiag" in item for item in NONCLAIMS)

    def test_install_required_constant(self) -> None:
        assert XDIAG_PRODUCTION_INSTALL_REQUIRED is True


class TestReport:
    def test_report_core_fields(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0

    def test_report_sections(self) -> None:
        assert set(REPORT).issuperset(
            {"synthesis_certificate", "what_is_claimed", "what_is_NOT_claimed"}
        )
