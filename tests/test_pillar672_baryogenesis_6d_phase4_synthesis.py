# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 672 — Baryogenesis 6D Phase 4 synthesis."""
from __future__ import annotations

from src.core.pillar672_baryogenesis_6d_phase4_synthesis_adjacent import (
    ADJACENT_TRACK,
    ARCHITECTURE_LIMIT_UNCHANGED,
    PHASE4_PILLARS,
    PILLAR_NUMBER,
    PRIMARY_EXPERIMENTAL_DISCRIMINATOR,
    SNS_WINDOW_GEV,
    VERSION,
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
        assert PILLAR_NUMBER == 672

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_phase4_pillars(self) -> None:
        assert PHASE4_PILLARS == [670, 671]

    def test_discriminator(self) -> None:
        assert PRIMARY_EXPERIMENTAL_DISCRIMINATOR == "nEDM_at_SNS_2028"


class TestSynthesis:
    def test_certificate_flags(self) -> None:
        assert CERTIFICATE["phase4_certified"] is True
        assert CERTIFICATE["architecture_limit_unchanged"] is True

    def test_sns_window(self) -> None:
        assert CERTIFICATE["sns_window_gev"] == SNS_WINDOW_GEV == [310.0, 780.0]


class TestClaims:
    def test_claim_counts(self) -> None:
        assert len(CLAIMS) >= 3
        assert len(NONCLAIMS) >= 3

    def test_architecture_limit_nonclaim(self) -> None:
        assert any("architecture limit" in item for item in NONCLAIMS)

    def test_constant_flag(self) -> None:
        assert ARCHITECTURE_LIMIT_UNCHANGED is True


class TestReport:
    def test_report_core_fields(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0

    def test_report_sections(self) -> None:
        assert set(REPORT).issuperset(
            {"synthesis_certificate", "what_is_claimed", "what_is_NOT_claimed"}
        )
