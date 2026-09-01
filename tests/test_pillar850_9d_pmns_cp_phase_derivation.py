# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 850 — 9D PMNS CP phase partial derivation."""
from __future__ import annotations

import pytest

from src.nined.pillar850_9d_pmns_cp_phase_derivation import (
    DELTA_PMNS_GEO_DEG,
    DELTA_PMNS_PDG_DEG,
    DELTA_PMNS_PDG_ERR_DEG,
    IN_PDG_1SIGMA,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    PILLAR_GATE,
    PILLAR_NUMBER,
    SEESAW_CORRECTION,
    pmns_cp_9d_summary,
    pmns_cp_phase_deg,
    seesaw_correction,
)


class TestPillar850Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 850
    def test_gate(self): assert PILLAR_GATE == "PMNS_CP_9D_PARTIAL_DERIVATION"
    def test_lean4(self):
        assert LEAN4_THEOREM_COUNT == 20
        assert LEAN4_TOTAL_AFTER == 2046
    def test_pdg(self):
        assert DELTA_PMNS_PDG_DEG == 197.0
        assert DELTA_PMNS_PDG_ERR_DEG == 25.0


class TestSeesawCorrection:
    def test_value(self):
        assert SEESAW_CORRECTION == pytest.approx(0.17193531629088832)

    def test_helper(self):
        assert seesaw_correction() == pytest.approx(SEESAW_CORRECTION)


class TestPmnsPhase:
    def test_phase_value(self):
        assert DELTA_PMNS_GEO_DEG == pytest.approx(198.73552409018678)

    def test_helper(self):
        assert pmns_cp_phase_deg() == pytest.approx(DELTA_PMNS_GEO_DEG)

    def test_in_one_sigma(self):
        assert IN_PDG_1SIGMA is True


class TestSummary:
    def test_returns_dict(self):
        assert isinstance(pmns_cp_9d_summary(), dict)

    def test_summary_gate(self):
        assert pmns_cp_9d_summary()["gate"] == PILLAR_GATE

    def test_summary_in_sigma(self):
        assert pmns_cp_9d_summary()["in_pdg_1sigma"] is True

    def test_summary_open_items(self):
        assert len(pmns_cp_9d_summary()["remaining_open"]) >= 1
