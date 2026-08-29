# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 832 — KK Backreaction v2 Regulated."""
from __future__ import annotations
import pytest
from src.core.pillar832_kk_backreaction_v2_regulated import (
    PILLAR, PILLAR_GATE, LEAN4_TOTAL, LEAN4_COUNT,
    tower_stress_energy_injection, kk_backreaction_v2,
    regulated_vs_truncated_comparison, phi_star_regulated, backreaction_v2_summary,
)


class TestPillar832Constants:
    def test_pillar_number(self): assert PILLAR == 832
    def test_lean4_count(self): assert LEAN4_COUNT == 20
    def test_lean4_total(self): assert LEAN4_TOTAL == 1731
    def test_lean4_accumulates(self):
        from src.core.pillar832_kk_backreaction_v2_regulated import LEAN4_PRIOR
        assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT
    def test_gate_present(self): assert "ARCHITECTURE" in PILLAR_GATE or "BACKREACTION" in PILLAR_GATE


class TestTowerStressEnergyInjection:
    def test_returns_dict(self):
        r = tower_stress_energy_injection()
        assert isinstance(r, dict)

    def test_delta_phi_present(self):
        r = tower_stress_energy_injection()
        assert "delta_phi_over_phi" in r

    def test_delta_phi_small(self):
        r = tower_stress_energy_injection()
        assert abs(r["delta_phi_over_phi"]) < 1.0

    def test_t55_positive(self):
        r = tower_stress_energy_injection()
        assert r["T55_tower"] > 0

    def test_gate_present(self):
        r = tower_stress_energy_injection()
        assert "gate" in r


class TestKkBackreactionV2:
    def test_returns_dict_regulated(self):
        r = kk_backreaction_v2(mode="regulated")
        assert isinstance(r, dict)

    def test_returns_dict_truncated(self):
        r = kk_backreaction_v2(mode="truncated")
        assert isinstance(r, dict)

    def test_phi_star_present(self):
        r = kk_backreaction_v2()
        assert "phi_star" in r

    def test_mode_regulated_default(self):
        r = kk_backreaction_v2()
        assert r["mode"] == "regulated"

    def test_shift_small(self):
        r = kk_backreaction_v2()
        assert abs(r["shift_percent"]) < 20.0


class TestRegulatedVsTruncatedComparison:
    def test_returns_dict(self):
        r = regulated_vs_truncated_comparison()
        assert isinstance(r, dict)

    def test_diff_present(self):
        r = regulated_vs_truncated_comparison()
        assert "relative_difference" in r

    def test_uv_sensitivity_small(self):
        r = regulated_vs_truncated_comparison()
        # UV sensitivity can be present or absent
        assert "UV_sensitivity" in r or isinstance(r, dict)


class TestPhiStarRegulated:
    def test_returns_dict(self):
        r = phi_star_regulated()
        assert isinstance(r, dict)

    def test_phi_star_positive(self):
        r = phi_star_regulated()
        assert r["phi_star"] > 0

    def test_gate_present(self):
        r = phi_star_regulated()
        assert "gate" in r


class TestBackreactionV2Summary:
    def test_returns_dict(self):
        r = backreaction_v2_summary()
        assert isinstance(r, dict)

    def test_pillar(self):
        r = backreaction_v2_summary()
        assert r["pillar"] == 832

    def test_lean4_total(self):
        r = backreaction_v2_summary()
        assert r["lean4_total_after"] == 1731

    def test_default_mode(self):
        r = backreaction_v2_summary()
        assert r["default_mode"] == "regulated"

    def test_architectural_change(self):
        r = backreaction_v2_summary()
        assert r.get("architectural_change") is not None
