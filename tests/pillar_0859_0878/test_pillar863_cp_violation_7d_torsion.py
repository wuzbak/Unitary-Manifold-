# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 863 — 7D discrete-torsion CP violation."""
from __future__ import annotations

import math

import pytest

from src.sevend.pillar863_cp_violation_7d_torsion import (
    BRAID_CORRECTION,
    DELTA_CP_LO_DEG,
    DELTA_CP_LO_RAD,
    DELTA_CP_NLO_DEG,
    DELTA_CP_NLO_RAD,
    DELTA_CP_PDG_ERR_RAD,
    DELTA_CP_PDG_RAD,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SIGMA_LO,
    SIGMA_NLO,
    TORSION_ORDER,
    WITHIN_2SIGMA_LO,
    WITHIN_2SIGMA_NLO,
    braid_corrected_phase_rad,
    cp_violation_7d_summary,
    supplementary_phase_rad,
    tension_sigma,
    torsion_holonomy_rad,
)


class TestPillar863Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 863
    def test_gate(self): assert PILLAR_GATE == "CP_VIOLATION_7D_PARTIAL_DERIVATION"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 25
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2251
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2276
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_torsion_order(self): assert TORSION_ORDER == 3
    def test_braid_correction(self): assert BRAID_CORRECTION == pytest.approx(5.0 / 74.0)
    def test_braid_correction_small(self): assert BRAID_CORRECTION < 0.1


class TestPillar863Geometry:
    def test_holonomy_value(self): assert torsion_holonomy_rad() == pytest.approx(2.0 * math.pi / 3.0)
    def test_holonomy_rejects_zero_order(self):
        with pytest.raises(ValueError):
            torsion_holonomy_rad(0)
    def test_supplementary_phase(self): assert supplementary_phase_rad() == pytest.approx(math.pi / 3.0)
    def test_supplementary_plus_holonomy_is_pi(self):
        assert supplementary_phase_rad() + torsion_holonomy_rad() == pytest.approx(math.pi)
    def test_braid_correction_increases_phase(self):
        assert braid_corrected_phase_rad() > supplementary_phase_rad()


class TestPillar863Phases:
    def test_delta_lo_rad(self): assert DELTA_CP_LO_RAD == pytest.approx(math.pi / 3.0)
    def test_delta_lo_deg(self): assert DELTA_CP_LO_DEG == pytest.approx(60.0)
    def test_delta_nlo_rad(self): assert DELTA_CP_NLO_RAD == pytest.approx(1.1179541, rel=1e-6)
    def test_delta_nlo_deg(self): assert DELTA_CP_NLO_DEG == pytest.approx(64.054054, rel=1e-6)
    def test_nlo_exceeds_lo(self): assert DELTA_CP_NLO_RAD > DELTA_CP_LO_RAD
    def test_nlo_ratio(self):
        assert DELTA_CP_NLO_RAD / DELTA_CP_LO_RAD == pytest.approx(1.0 + BRAID_CORRECTION)


class TestPillar863Tension:
    def test_pdg_central(self): assert DELTA_CP_PDG_RAD == pytest.approx(1.20)
    def test_pdg_error(self): assert DELTA_CP_PDG_ERR_RAD == pytest.approx(0.08)
    def test_sigma_lo(self): assert SIGMA_LO == pytest.approx(1.910031, rel=1e-5)
    def test_sigma_nlo(self): assert SIGMA_NLO == pytest.approx(1.025573, rel=1e-5)
    def test_nlo_improves(self): assert SIGMA_NLO < SIGMA_LO
    def test_lo_within_2sigma(self): assert WITHIN_2SIGMA_LO is True
    def test_nlo_within_2sigma(self): assert WITHIN_2SIGMA_NLO is True
    def test_tension_sigma_zero(self): assert tension_sigma(1.2) == pytest.approx(0.0)
    def test_tension_rejects_zero_error(self):
        with pytest.raises(ValueError):
            tension_sigma(1.0, 1.0, 0.0)


class TestPillar863Summary:
    def test_summary_gate(self): assert cp_violation_7d_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert cp_violation_7d_summary()["pillar"] == 863
    def test_summary_nlo_improves(self): assert cp_violation_7d_summary()["nlo_improves"] is True
    def test_summary_lean4(self): assert cp_violation_7d_summary()["lean4_total_after"] == 2276
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_partial(self):
        assert "PARTIAL" in cp_violation_7d_summary()["epistemic_status"].upper()
