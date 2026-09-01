# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 840 — 6D to 5D reduction chain."""
from __future__ import annotations

import math

import pytest

from src.core.pillar840_6d_to_5d_reduction_chain import (
    GATE,
    G_NEWTON_RATIO,
    K_CS_PRESERVED,
    LEAN4_COUNT,
    LEAN4_PRIOR,
    LEAN4_TOTAL,
    N_GEN_PRESERVED,
    NW_PRESERVED,
    PILLAR,
    kk_mass_squared_6d,
    reduction_chain_summary,
    zero_mode_sector,
)


class TestPillar840Constants:
    def test_pillar_number(self): assert PILLAR == 840
    def test_gate(self): assert GATE == "SIXD_TO_5D_REDUCTION_CHAIN_CLOSED"
    def test_lean4_count(self): assert LEAN4_COUNT == 20
    def test_lean4_total(self): assert LEAN4_TOTAL == 1931
    def test_lean4_accumulates(self): assert LEAN4_TOTAL == LEAN4_PRIOR + LEAN4_COUNT
    def test_preservation_flags(self):
        assert N_GEN_PRESERVED and K_CS_PRESERVED and NW_PRESERVED


class TestKKSpectrum:
    def test_zero_mode_massless(self):
        assert kk_mass_squared_6d(0, 0, 0) == 0.0

    def test_excited_mode_positive(self):
        assert kk_mass_squared_6d(1, 0, 0) > 0.0

    def test_transverse_excited_mode_positive(self):
        assert kk_mass_squared_6d(0, 1, 1) > 0.0

    def test_gnewton_ratio(self):
        assert G_NEWTON_RATIO == pytest.approx(1.0 / (4.0 * math.pi**3), rel=1e-12)


class TestZeroModeSector:
    def test_fields_recovered(self):
        fields = zero_mode_sector()["fields_recovered"]
        assert fields == ["g_munu", "B_mu", "phi_radion"]

    def test_ngen_preserved(self):
        data = zero_mode_sector()
        assert data["n_gen_6d"] == data["n_gen_5d_constraint"] == 3


class TestReductionSummary:
    def test_summary_pillar(self):
        assert reduction_chain_summary()["pillar"] == 840

    def test_summary_closed(self):
        summary = reduction_chain_summary()
        assert summary["n_gen_preserved"] and summary["k_cs_preserved"] and summary["n_w_preserved"]

    def test_summary_honest_status(self):
        assert "backreaction" in reduction_chain_summary()["honest_status"].lower()

    def test_summary_remaining_open(self):
        assert "BACKREACTION" in reduction_chain_summary()["remaining_open"][0]
