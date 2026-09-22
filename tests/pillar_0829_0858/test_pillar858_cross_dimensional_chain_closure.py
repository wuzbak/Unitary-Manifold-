# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 858 — cross-dimensional chain closure."""
from __future__ import annotations

from src.core.pillar858_cross_dimensional_chain_closure import (
    CHAIN_COMPLETENESS_FRACTION,
    CHAIN_STEPS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    N_CHAIN_STEPS,
    N_CLOSED_STEPS,
    N_OPEN_STEPS,
    N_PARTIAL_STEPS,
    PILLAR_GATE,
    PILLAR_NUMBER,
    chain_closure_summary,
)


class TestPillar858Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 858
    def test_gate(self): assert PILLAR_GATE == "CROSS_DIMENSIONAL_CHAIN_CLOSED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 30
    def test_lean4_total(self): assert LEAN4_TOTAL_AFTER == 2146
    def test_step_count(self): assert N_CHAIN_STEPS == 7
    def test_closed_count(self): assert N_CLOSED_STEPS == 7
    def test_partial_count(self): assert N_PARTIAL_STEPS == 5
    def test_open_count(self): assert N_OPEN_STEPS == 0
    def test_completeness(self): assert CHAIN_COMPLETENESS_FRACTION == 1.0


class TestPillar858Steps:
    def test_chain_steps_length(self): assert len(CHAIN_STEPS) == 7

    def test_all_have_gate(self):
        for step in CHAIN_STEPS:
            assert "gate" in step

    def test_all_have_open_item(self):
        for step in CHAIN_STEPS:
            assert "open_item" in step

    def test_first_step(self):
        assert CHAIN_STEPS[0]["gate"] == "HW_UV_VACUUM_SELECTED"

    def test_second_step(self):
        assert CHAIN_STEPS[1]["gate"] == "PHI0_FLUX_STABILIZATION_PARTIAL"

    def test_last_step(self):
        assert CHAIN_STEPS[-1]["to_dimension"] == 4


class TestPillar858Summary:
    def test_returns_dict(self): assert isinstance(chain_closure_summary(), dict)
    def test_summary_gate(self): assert chain_closure_summary()["gate"] == PILLAR_GATE
    def test_summary_fraction(self): assert chain_closure_summary()["chain_completeness_fraction"] == 1.0
    def test_summary_honest_note(self): assert "conditional or partial" in chain_closure_summary()["honest_note"]
