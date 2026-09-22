# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 854 — Hořava-Witten UV vacuum selection."""
from __future__ import annotations

from src.core.pillar854_horava_witten_uv_vacuum_selection import (
    E8_BREAKING_CONSISTENT,
    G_S_HW_PROXY,
    HW_Z2_COMPATIBLE,
    K_CS_E8_LEVEL_MATCH,
    L11_OVER_LS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    NW_Z2_COMPATIBLE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    R11_INTERVAL_PLANCK,
    UV_VACUUM,
    hw_uv_vacuum_summary,
)


class TestPillar854Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 854
    def test_gate(self): assert PILLAR_GATE == "HW_UV_VACUUM_SELECTED"
    def test_uv_vacuum(self): assert UV_VACUUM == "VISIBLE_SECTOR_BRANE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 25
    def test_lean4_total(self): assert LEAN4_TOTAL_AFTER == 2096
    def test_l11_ratio_small_positive(self): assert 0.0 < L11_OVER_LS < 1.0
    def test_gs_proxy_positive(self): assert G_S_HW_PROXY > 0.0
    def test_r11_positive(self): assert R11_INTERVAL_PLANCK > 0.0
    def test_e8_breaking_consistent(self): assert E8_BREAKING_CONSISTENT is True
    def test_hw_z2_compatible(self): assert HW_Z2_COMPATIBLE is True
    def test_kcs_e8_match(self): assert K_CS_E8_LEVEL_MATCH is True
    def test_nw_z2_compatible(self): assert NW_Z2_COMPATIBLE is True


class TestPillar854Summary:
    def test_returns_dict(self):
        assert isinstance(hw_uv_vacuum_summary(), dict)

    def test_visible_sector_selected(self):
        assert hw_uv_vacuum_summary()["visible_sector_selected"] is True

    def test_summary_gate(self):
        assert hw_uv_vacuum_summary()["gate"] == PILLAR_GATE

    def test_summary_rung6_hard_gate(self):
        assert hw_uv_vacuum_summary()["rung6_hard_gate"]["hard_gate_pass"] is True

    def test_summary_gauge_group(self):
        assert hw_uv_vacuum_summary()["visible_sector_gauge_group"] == ("SU(3)", "SU(2)", "U(1)")

    def test_summary_open_item(self):
        assert hw_uv_vacuum_summary()["remaining_open"] == ["E8_BREAKING_PATTERN_OPEN"]

    def test_summary_honest_note(self):
        assert "Wilson-line" in hw_uv_vacuum_summary()["honest_note"]
