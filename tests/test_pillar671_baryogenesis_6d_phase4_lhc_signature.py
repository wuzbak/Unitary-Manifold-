# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 671 — Baryogenesis 6D Phase 4 LHC signature."""
from __future__ import annotations

import math

from src.core.pillar671_baryogenesis_6d_phase4_lhc_signature_adjacent import (
    ADJACENT_TRACK,
    D_N_NLO_ECM,
    D_N_TRIGGER_ECM,
    LHC_PRIORITY,
    N_EVENTS_HLLHC,
    PILLAR_NUMBER,
    PYTHIA8_REQUIRED,
    SIGMA_DRELL_YAN_FB,
    SIGNAL,
    VERSION,
    drell_yan_production,
    lhc_priority_preregistration,
    pillar_report,
)

PRODUCTION = drell_yan_production()
PRIORITY = lhc_priority_preregistration()
REPORT = pillar_report()


class TestConstants:
    def test_pillar_number(self) -> None:
        assert PILLAR_NUMBER == 671

    def test_version(self) -> None:
        assert VERSION == "v21.0"

    def test_event_yield(self) -> None:
        assert math.isclose(N_EVENTS_HLLHC, 1200.0, rel_tol=0.1, abs_tol=0.0)

    def test_priority(self) -> None:
        assert LHC_PRIORITY == "TIER_1_PRIORITY"

    def test_trigger_exceeded(self) -> None:
        assert D_N_NLO_ECM >= D_N_TRIGGER_ECM

    def test_sigma_positive(self) -> None:
        assert SIGMA_DRELL_YAN_FB > 0.0

    def test_pythia_required(self) -> None:
        assert PYTHIA8_REQUIRED is True


class TestProductionSummary:
    def test_production_fields(self) -> None:
        assert PRODUCTION["signal"] == SIGNAL
        assert PRODUCTION["n_events_hllhc"] == N_EVENTS_HLLHC

    def test_coupling_mechanism(self) -> None:
        assert PRODUCTION["coupling_mechanism"] == "electroweak_drell_yan_pair_production"


class TestPrioritySummary:
    def test_priority_flag(self) -> None:
        assert PRIORITY["d_n_exceeds_trigger"] is True

    def test_priority_value(self) -> None:
        assert PRIORITY["lhc_priority"] == "TIER_1_PRIORITY"


class TestReport:
    def test_report_core_fields(self) -> None:
        assert REPORT["adjacent_track"] is ADJACENT_TRACK is True
        assert REPORT["toe_score_delta"] == 0.0
        assert REPORT["hardgate_score_delta"] == 0.0

    def test_report_sections(self) -> None:
        assert set(REPORT).issuperset(
            {"drell_yan_production", "lhc_priority_preregistration"}
        )
