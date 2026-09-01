# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 843 — 7D CKM SVD mixing-angle partial closure."""
from __future__ import annotations

from pathlib import Path

import pytest

from src.sevend.pillar843_7d_ckm_svd_mixing_angles import (
    DELTA_CP_DEG,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    PI_KR,
    PILLAR_GATE,
    PILLAR_NUMBER,
    THETA_12_DEG,
    THETA_12_PDG_DEG,
    THETA_13_DEG,
    THETA_13_PDG_DEG,
    THETA_23_DEG,
    THETA_23_PDG_DEG,
    ckm_7d_mixing_summary,
    left_bulk_mass_ladder,
    mixing_angle_deg,
    yukawa_ratio,
)


class TestPillar843Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 843
    def test_gate(self): assert PILLAR_GATE == "CKM_7D_SVD_MIXING_PARTIAL_CLOSURE"
    def test_pi_kr(self): assert PI_KR == 37.0
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 25
    def test_lean4_total(self): assert LEAN4_TOTAL_AFTER == 1976
    def test_delta_cp(self): assert DELTA_CP_DEG == pytest.approx(60.0)


class TestBulkMassLadder:
    def test_three_entries(self):
        assert len(left_bulk_mass_ladder()) == 3

    def test_values_match_spec(self):
        c1, c2, c3 = left_bulk_mass_ladder()
        assert c1 == pytest.approx(5 / 74)
        assert c2 == pytest.approx(10 / 74)
        assert c3 == pytest.approx(15 / 74)

    def test_strictly_increasing(self):
        c1, c2, c3 = left_bulk_mass_ladder()
        assert c1 < c2 < c3


class TestYukawaRatios:
    def test_delta_12_ratio(self):
        assert yukawa_ratio(5 / 74) == pytest.approx(0.0820849986238988)

    def test_larger_gap_smaller_ratio(self):
        assert yukawa_ratio(10 / 74) < yukawa_ratio(5 / 74)

    def test_nonpositive_gap_raises(self):
        with pytest.raises(ValueError):
            yukawa_ratio(0.0)


class TestMixingAngles:
    def test_theta12_reasonable(self):
        assert THETA_12_DEG == pytest.approx(16.648818540483596)

    def test_theta23_reasonable(self):
        assert THETA_23_DEG == pytest.approx(4.708421627809821)

    def test_theta13_reasonable(self):
        assert THETA_13_DEG == pytest.approx(0.38605884684210096)

    def test_hierarchy(self):
        assert THETA_12_DEG > THETA_23_DEG > THETA_13_DEG > 0.0

    def test_all_within_factor_two(self):
        assert 0.5 <= THETA_12_DEG / THETA_12_PDG_DEG <= 2.0
        assert 0.5 <= THETA_23_DEG / THETA_23_PDG_DEG <= 2.0
        assert 0.5 <= THETA_13_DEG / THETA_13_PDG_DEG <= 2.0

    def test_helper_matches_theta12(self):
        assert mixing_angle_deg(5 / 74) == pytest.approx(THETA_12_DEG)


class TestSummary:
    def test_returns_dict(self):
        assert isinstance(ckm_7d_mixing_summary(), dict)

    def test_summary_gate(self):
        assert ckm_7d_mixing_summary()["gate"] == PILLAR_GATE

    def test_summary_hierarchy(self):
        assert ckm_7d_mixing_summary()["hierarchy_correct"] is True

    def test_summary_factor_two(self):
        assert ckm_7d_mixing_summary()["all_within_factor_two_of_pdg"] is True

    def test_summary_open_items(self):
        assert len(ckm_7d_mixing_summary()["remaining_open"]) >= 1


class TestLean4File:
    LEAN_FILE = Path(__file__).resolve().parents[1] / "lean4" / "UnitaryManifold" / "CKM7DMixingAngles.lean"

    def test_exists(self):
        assert self.LEAN_FILE.exists()

    def test_no_sorry(self):
        assert "sorry" not in self.LEAN_FILE.read_text()

    def test_theorem_count(self):
        content = self.LEAN_FILE.read_text()
        assert content.count("theorem ") >= 20
