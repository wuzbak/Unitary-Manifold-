# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 881 — NLO update of the 6D baryogenesis neutron EDM."""
from __future__ import annotations

import pytest

from src.sixd.pillar881_baryogenesis_dn_update import (
    ABOVE_SNS_SENSITIVITY,
    BELOW_CURRENT_BOUND,
    D_N_LO_ECM,
    D_N_NLO_ECM,
    D_N_NLO_LOWER_ECM,
    D_N_NLO_UPPER_ECM,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    NLO_RELATIVE_SHIFT,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    SHIFT_INSIDE_BAND,
    STILL_FALSIFIABLE,
    baryogenesis_dn_nlo_summary,
    dn_nlo_band_ecm,
    dn_nlo_ecm,
)


class TestPillar881Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 881
    def test_gate(self): assert PILLAR_GATE == "BARYOGENESIS_6D_DN_NLO_UPDATED"
    def test_no_lean4_theorems(self): assert LEAN4_THEOREM_COUNT == 0
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2606
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2606
    def test_lean4_ledger_unchanged(self): assert LEAN4_TOTAL_BEFORE == LEAN4_TOTAL_AFTER


class TestPillar881NLOShift:
    def test_shift_value(self): assert NLO_RELATIVE_SHIFT == pytest.approx(0.016053075, rel=1e-7)
    def test_shift_positive(self): assert NLO_RELATIVE_SHIFT > 0.0
    def test_shift_below_five_percent(self): assert NLO_RELATIVE_SHIFT < 0.05
    def test_shift_inside_band(self): assert SHIFT_INSIDE_BAND is True
    def test_shift_percent(self):
        assert baryogenesis_dn_nlo_summary()["nlo_relative_shift_percent"] == pytest.approx(
            NLO_RELATIVE_SHIFT * 100.0
        )


class TestPillar881EDM:
    def test_lo_value(self): assert D_N_LO_ECM == pytest.approx(7.8e-27)
    def test_nlo_value(self): assert D_N_NLO_ECM == pytest.approx(7.925214e-27, rel=1e-6)
    def test_nlo_exceeds_lo(self): assert D_N_NLO_ECM > D_N_LO_ECM
    def test_nlo_function(self): assert dn_nlo_ecm() == pytest.approx(D_N_NLO_ECM, rel=1e-12)
    def test_nlo_rejects_nonpositive_lo(self):
        with pytest.raises(ValueError):
            dn_nlo_ecm(d_n_lo=0.0)
    def test_nlo_scales_with_lo(self):
        assert dn_nlo_ecm(d_n_lo=2.0 * D_N_LO_ECM) == pytest.approx(2.0 * D_N_NLO_ECM, rel=1e-12)
    def test_nlo_ratio_is_shift(self):
        assert D_N_NLO_ECM / D_N_LO_ECM == pytest.approx(1.0 + NLO_RELATIVE_SHIFT, rel=1e-12)


class TestPillar881Band:
    def test_band_lower(self): assert D_N_NLO_LOWER_ECM == pytest.approx(6.340171e-27, rel=1e-6)
    def test_band_upper(self): assert D_N_NLO_UPPER_ECM == pytest.approx(9.510257e-27, rel=1e-6)
    def test_band_ordered(self): assert D_N_NLO_LOWER_ECM < D_N_NLO_UPPER_ECM
    def test_central_inside_band(self): assert D_N_NLO_LOWER_ECM < D_N_NLO_ECM < D_N_NLO_UPPER_ECM
    def test_band_function(self):
        low, high = dn_nlo_band_ecm()
        assert low == pytest.approx(D_N_NLO_LOWER_ECM) and high == pytest.approx(D_N_NLO_UPPER_ECM)
    def test_band_rejects_bad_fraction(self):
        with pytest.raises(ValueError):
            dn_nlo_band_ecm(frac=1.5)
    def test_band_symmetric(self):
        assert D_N_NLO_UPPER_ECM - D_N_NLO_ECM == pytest.approx(D_N_NLO_ECM - D_N_NLO_LOWER_ECM)


class TestPillar881Falsifiability:
    def test_below_current_bound(self): assert BELOW_CURRENT_BOUND is True
    def test_above_sns_sensitivity(self): assert ABOVE_SNS_SENSITIVITY is True
    def test_still_falsifiable(self): assert STILL_FALSIFIABLE is True
    def test_current_bound_larger(self):
        assert baryogenesis_dn_nlo_summary()["current_bound_ecm"] > D_N_NLO_UPPER_ECM
    def test_sns_sensitivity_smaller(self):
        assert baryogenesis_dn_nlo_summary()["sns_sensitivity_ecm"] < D_N_NLO_LOWER_ECM


class TestPillar881Summary:
    def test_summary_gate(self): assert baryogenesis_dn_nlo_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert baryogenesis_dn_nlo_summary()["pillar"] == 881
    def test_summary_lean4_zero(self):
        assert baryogenesis_dn_nlo_summary()["lean4_theorem_count"] == 0
    def test_summary_lean4_total(self): assert baryogenesis_dn_nlo_summary()["lean4_total_after"] == 2606
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_falsifiable(self):
        assert "FALSIFIABLE" in baryogenesis_dn_nlo_summary()["epistemic_status"].upper()
