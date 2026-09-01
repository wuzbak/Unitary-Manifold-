# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 878 — extended Swampland duality audit."""
from __future__ import annotations

import pytest

from src.core.pillar878_swampland_extended_duality import (
    AUDIT_COMPLETE,
    H_INF_GEV,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    NON_SUSY_ADS_VERDICT,
    N_EFOLDS_REQUIRED,
    N_FAIL,
    N_PASS,
    N_TENSION,
    N_W,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    R_TENSOR,
    TCC_EFOLD_BOUND,
    TCC_VERDICT,
    VERDICTS,
    WGC_RADION_VERDICT,
    hubble_inflation_gev,
    inflation_scale_gev,
    non_susy_ads_check,
    swampland_extended_summary,
    tcc_check,
    tcc_efold_bound,
    wgc_radion_check,
)


class TestPillar878Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 878
    def test_gate(self): assert PILLAR_GATE == "SWAMPLAND_EXTENDED_DUALITY_AUDIT_COMPLETE"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2571
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2591
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_n_w(self): assert N_W == 5
    def test_k_cs(self): assert K_CS == 74
    def test_r_tensor(self): assert R_TENSOR == pytest.approx(0.0315)
    def test_efolds_required(self): assert N_EFOLDS_REQUIRED == pytest.approx(60.0)


class TestPillar878Inflation:
    def test_scale_positive(self): assert inflation_scale_gev() > 0.0
    def test_scale_rejects_zero_r(self):
        with pytest.raises(ValueError):
            inflation_scale_gev(r=0.0)
    def test_scale_grows_with_r(self): assert inflation_scale_gev(r=0.05) > inflation_scale_gev(r=0.01)
    def test_hubble_value(self): assert H_INF_GEV == pytest.approx(4.728326029e13, rel=1e-6)
    def test_hubble_function(self):
        assert hubble_inflation_gev() == pytest.approx(H_INF_GEV, rel=1e-12)
    def test_hubble_sub_planckian(self): assert H_INF_GEV < 2.4e18
    def test_efold_bound(self): assert TCC_EFOLD_BOUND == pytest.approx(10.849301, rel=1e-6)
    def test_efold_bound_function(self):
        assert tcc_efold_bound() == pytest.approx(TCC_EFOLD_BOUND, rel=1e-12)
    def test_efold_bound_below_required(self): assert TCC_EFOLD_BOUND < N_EFOLDS_REQUIRED


class TestPillar878Checks:
    def test_wgc_conjecture_label(self):
        assert wgc_radion_check()["conjecture"] == "E1_WGC_RADION"
    def test_wgc_verdict(self): assert WGC_RADION_VERDICT == "PASS"
    def test_ads_conjecture_label(self):
        assert non_susy_ads_check()["conjecture"] == "E2_NON_SUSY_ADS"
    def test_ads_verdict(self): assert NON_SUSY_ADS_VERDICT == "PASS"
    def test_ads_vacuum_energy_positive(self):
        assert non_susy_ads_check()["vacuum_energy_sign"] == 1
    def test_tcc_conjecture_label(self): assert tcc_check()["conjecture"] == "E3_TCC"
    def test_tcc_verdict_tension_reported_honestly(self): assert TCC_VERDICT == "TENSION"
    def test_tcc_efold_deficit(self): assert tcc_check()["deficit_efolds"] > 40.0
    def test_every_check_has_verdict(self):
        assert all("verdict" in c for c in (wgc_radion_check(), non_susy_ads_check(), tcc_check()))


class TestPillar878Tallies:
    def test_verdict_keys(self):
        assert set(VERDICTS) == {"E1_WGC_RADION", "E2_NON_SUSY_ADS", "E3_TCC"}
    def test_verdict_values(self):
        assert VERDICTS == {"E1_WGC_RADION": "PASS", "E2_NON_SUSY_ADS": "PASS", "E3_TCC": "TENSION"}
    def test_n_pass(self): assert N_PASS == 2
    def test_n_tension(self): assert N_TENSION == 1
    def test_n_fail(self): assert N_FAIL == 0
    def test_tally_sums_to_three(self): assert N_PASS + N_TENSION + N_FAIL == 3
    def test_no_failures(self): assert N_FAIL == 0
    def test_audit_complete(self): assert AUDIT_COMPLETE is True


class TestPillar878Summary:
    def test_summary_gate(self): assert swampland_extended_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert swampland_extended_summary()["pillar"] == 878
    def test_summary_lean4(self): assert swampland_extended_summary()["lean4_total_after"] == 2591
    def test_summary_checks_length(self): assert len(swampland_extended_summary()["checks"]) == 3
    def test_summary_reports_tension(self): assert swampland_extended_summary()["n_tension"] == 1
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_mentions_tcc(self):
        assert "TCC" in swampland_extended_summary()["epistemic_status"].upper()
