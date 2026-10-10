# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 851 — 9D → 10D moduli/flux counting bridge."""
from __future__ import annotations

from src.nined.pillar851_9d_to_10d_moduli_flux_bridge import (
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    MINIMAL_FLUX_QUANTUM,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    TORSION_ORDER,
    minimal_discrete_charges_match,
    moduli_flux_bridge_summary,
)


def test_pillar_number():
    assert PILLAR_NUMBER == 851


def test_gate():
    assert PILLAR_GATE == "NINED_TO_TEND_MODULI_FLUX_BRIDGE_PARTIAL"


def test_title_mentions_dims():
    assert "9D" in PILLAR_TITLE and "10D" in PILLAR_TITLE


def test_torsion_order():
    assert TORSION_ORDER == 3


def test_minimal_flux_quantum():
    assert MINIMAL_FLUX_QUANTUM == 1


def test_lean4_zero():
    assert LEAN4_THEOREM_COUNT == 0
    assert LEAN4_TOTAL_AFTER == 2046


def test_minimal_discrete_charges_match():
    assert minimal_discrete_charges_match() is True


class TestSummary:
    def test_pillar(self):
        assert moduli_flux_bridge_summary()["pillar"] == 851

    def test_bridges_pillars(self):
        assert moduli_flux_bridge_summary()["bridges_pillars"] == [850, 853]

    def test_acceptance_gate_passed(self):
        assert moduli_flux_bridge_summary()["acceptance_gate_passed"] is True

    def test_epistemic_status_partial(self):
        assert "PARTIAL" in moduli_flux_bridge_summary()["epistemic_status"]

    def test_remaining_open_present(self):
        assert len(moduli_flux_bridge_summary()["remaining_open"]) >= 1
