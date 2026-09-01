# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 879 — DESI DR3 routing-infrastructure update."""
from __future__ import annotations

import pytest

from src.core.pillar879_desi_dr3_routing_update import (
    DESI_DR3_EXPECTED_YEAR,
    DR2_TENSION_SIGMA,
    DR3_DATA_AVAILABLE,
    EUCLID_DR1_EXPECTED_YEAR,
    EUCLID_DR1_WA_SIGMA,
    GATE_STATUS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    PILLAR_GATE,
    PILLAR_NUMBER,
    PROJECTED_TENSION_SIGMA,
    PROJECTED_VERDICT,
    REMAINING_OPEN,
    SIGMA_COMBINED,
    SIGMA_IMPROVEMENT_FACTOR,
    TENSION_SHARPENED,
    THRESHOLDS_UNCHANGED,
    combine_sigmas,
    desi_dr3_routing_summary,
    projected_tension,
    projected_verdict,
)


class TestPillar879Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 879
    def test_gate(self): assert PILLAR_GATE == "DESI_DR3_ROUTING_INFRASTRUCTURE_UPDATED"
    def test_gate_status_open(self): assert GATE_STATUS == "OPEN"
    def test_no_lean4_theorems(self): assert LEAN4_THEOREM_COUNT == 0
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2591
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2591
    def test_lean4_ledger_unchanged(self): assert LEAN4_TOTAL_BEFORE == LEAN4_TOTAL_AFTER
    def test_dr3_year(self): assert DESI_DR3_EXPECTED_YEAR == 2027
    def test_euclid_year(self): assert EUCLID_DR1_EXPECTED_YEAR == 2026
    def test_dr3_data_not_available(self): assert DR3_DATA_AVAILABLE is False


class TestPillar879Combination:
    def test_euclid_sigma(self): assert EUCLID_DR1_WA_SIGMA == pytest.approx(0.20)
    def test_combined_sigma(self): assert SIGMA_COMBINED == pytest.approx(0.14977401, rel=1e-7)
    def test_combined_below_each(self): assert SIGMA_COMBINED < EUCLID_DR1_WA_SIGMA
    def test_improvement_factor(self):
        assert SIGMA_IMPROVEMENT_FACTOR == pytest.approx(1.50894003, rel=1e-7)
    def test_improvement_above_one(self): assert SIGMA_IMPROVEMENT_FACTOR > 1.0
    def test_combine_sigmas_equal(self):
        assert combine_sigmas(1.0, 1.0) == pytest.approx(1.0 / (2.0**0.5))
    def test_combine_sigmas_rejects_zero(self):
        with pytest.raises(ValueError):
            combine_sigmas(0.0, 1.0)
    def test_combine_sigmas_symmetric(self):
        assert combine_sigmas(0.2, 0.3) == pytest.approx(combine_sigmas(0.3, 0.2))


class TestPillar879Projection:
    def test_dr2_tension(self): assert DR2_TENSION_SIGMA == pytest.approx(2.74336283, rel=1e-7)
    def test_projected_tension(self):
        assert PROJECTED_TENSION_SIGMA == pytest.approx(4.13956998, rel=1e-7)
    def test_projection_function(self):
        assert projected_tension() == pytest.approx(PROJECTED_TENSION_SIGMA, rel=1e-12)
    def test_tension_sharpened(self): assert TENSION_SHARPENED is True
    def test_projected_exceeds_dr2(self): assert PROJECTED_TENSION_SIGMA > DR2_TENSION_SIGMA
    def test_projected_verdict(self): assert PROJECTED_VERDICT == "HIGH_TENSION"
    def test_verdict_function(self): assert projected_verdict() == PROJECTED_VERDICT
    def test_verdict_low_tension(self): assert projected_verdict(0.5) != "HIGH_TENSION"
    def test_thresholds_unchanged(self): assert THRESHOLDS_UNCHANGED is True


class TestPillar879Summary:
    def test_summary_gate(self): assert desi_dr3_routing_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert desi_dr3_routing_summary()["pillar"] == 879
    def test_summary_gate_status(self): assert desi_dr3_routing_summary()["gate_status"] == "OPEN"
    def test_summary_no_data(self): assert desi_dr3_routing_summary()["dr3_data_available"] is False
    def test_summary_lean4_zero(self): assert desi_dr3_routing_summary()["lean4_theorem_count"] == 0
    def test_summary_thresholds_present(self): assert desi_dr3_routing_summary()["thresholds"]
    def test_summary_um_prediction(self):
        assert desi_dr3_routing_summary()["um_wa_prediction"] == pytest.approx(0.0)
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_open(self):
        assert "OPEN" in desi_dr3_routing_summary()["epistemic_status"].upper()
    def test_no_premature_falsification_claim(self):
        assert "FALSIFIED" not in desi_dr3_routing_summary()["epistemic_status"].upper()
