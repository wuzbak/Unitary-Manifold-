# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 876 — NLO stability of the leptonic CP phase."""
from __future__ import annotations

import pytest

from src.nined.pillar876_pmns_cp_nlo_tightened import (
    DELTA_LO_DEG,
    DELTA_NLO_DEG,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    NLO_IMPROVES,
    NLO_SHIFT_DEG,
    NLO_STABLE,
    NLO_SUPPRESSION,
    NLO_WITHIN_1SIGMA,
    N_W,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SIGMA_LO,
    SIGMA_NLO,
    STABILITY_THRESHOLD_DEG,
    delta_pmns_nlo_deg,
    nlo_correction_factor,
    pmns_cp_nlo_summary,
    tension_sigma,
)


class TestPillar876Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 876
    def test_gate(self): assert PILLAR_GATE == "PMNS_CP_NLO_STABLE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2531
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2551
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_threshold(self): assert STABILITY_THRESHOLD_DEG == pytest.approx(5.0)


class TestPillar876Correction:
    def test_suppression_value(self): assert NLO_SUPPRESSION == pytest.approx((5.0 / 74.0) ** 2)
    def test_suppression_small(self): assert NLO_SUPPRESSION < 0.01
    def test_correction_factor(self):
        assert nlo_correction_factor() == pytest.approx(1.0 + NLO_SUPPRESSION)
    def test_correction_above_one(self): assert nlo_correction_factor() > 1.0
    def test_correction_rejects_zero_kcs(self):
        with pytest.raises(ValueError):
            nlo_correction_factor(k_cs=0)
    def test_delta_nlo_function(self):
        assert delta_pmns_nlo_deg(DELTA_LO_DEG) == pytest.approx(DELTA_NLO_DEG, rel=1e-12)
    def test_delta_nlo_scales_linearly(self):
        assert delta_pmns_nlo_deg(100.0) == pytest.approx(100.0 * nlo_correction_factor())


class TestPillar876Phases:
    def test_delta_lo(self): assert DELTA_LO_DEG == pytest.approx(198.735524, rel=1e-7)
    def test_delta_nlo(self): assert DELTA_NLO_DEG == pytest.approx(199.642827, rel=1e-7)
    def test_nlo_shift(self): assert NLO_SHIFT_DEG == pytest.approx(0.907302, rel=1e-5)
    def test_shift_below_threshold(self): assert NLO_SHIFT_DEG < STABILITY_THRESHOLD_DEG
    def test_nlo_stable(self): assert NLO_STABLE is True
    def test_nlo_shift_is_difference(self):
        assert NLO_SHIFT_DEG == pytest.approx(abs(DELTA_NLO_DEG - DELTA_LO_DEG), rel=1e-12)
    def test_phases_in_second_half_plane(self): assert 180.0 < DELTA_NLO_DEG < 270.0


class TestPillar876Tension:
    def test_sigma_lo(self): assert SIGMA_LO == pytest.approx(0.069421, rel=1e-4)
    def test_sigma_nlo(self): assert SIGMA_NLO == pytest.approx(0.105713, rel=1e-4)
    def test_nlo_does_not_improve_reported_honestly(self): assert NLO_IMPROVES is False
    def test_nlo_within_one_sigma(self): assert NLO_WITHIN_1SIGMA is True
    def test_both_below_one_sigma(self): assert max(SIGMA_LO, SIGMA_NLO) < 1.0
    def test_tension_sigma_zero(self):
        assert tension_sigma(pmns_cp_nlo_summary()["delta_pdg_deg"]) == pytest.approx(0.0)
    def test_tension_rejects_zero_sigma(self):
        with pytest.raises(ValueError):
            tension_sigma(1.0, 1.0, 0.0)


class TestPillar876Summary:
    def test_summary_gate(self): assert pmns_cp_nlo_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert pmns_cp_nlo_summary()["pillar"] == 876
    def test_summary_lean4(self): assert pmns_cp_nlo_summary()["lean4_total_after"] == 2551
    def test_summary_nlo_stable(self): assert pmns_cp_nlo_summary()["nlo_stable"] is True
    def test_summary_nlo_improves_false(self): assert pmns_cp_nlo_summary()["nlo_improves"] is False
    def test_summary_shift(self):
        assert pmns_cp_nlo_summary()["nlo_shift_deg"] == pytest.approx(NLO_SHIFT_DEG)
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_stable(self):
        assert "STABLE" in pmns_cp_nlo_summary()["epistemic_status"].upper()
