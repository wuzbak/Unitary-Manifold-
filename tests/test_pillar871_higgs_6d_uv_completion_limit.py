# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 871 — 6D Higgs UV-completion architecture limit."""
from __future__ import annotations

import pytest

from src.sixd.pillar871_higgs_6d_uv_completion_limit import (
    BOUND_FRACTION,
    BOUND_SATISFIED,
    DELTA_MH_GEV,
    DELTA_MH_OVER_MH,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    LIMIT_CERTIFICATE,
    NDA_CUTOFF_OVER_MKK,
    N_KK_BELOW_CUTOFF,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    higgs_mass_band_gev,
    higgs_uv_completion_limit_summary,
    kk_levels_below_cutoff,
    nda_cutoff_ratio,
    one_loop_relative_shift,
)


class TestPillar871Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 871
    def test_gate(self): assert PILLAR_GATE == "HIGGS_6D_UV_COMPLETION_ARCHITECTURE_LIMIT"
    def test_limit_certificate(self):
        assert LIMIT_CERTIFICATE == "NON_PERTURBATIVE_ARCHITECTURE_LIMIT_6D"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 20
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2431
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2451
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_bound_fraction(self): assert BOUND_FRACTION == pytest.approx(0.05)
    def test_bound_is_five_percent(self): assert BOUND_FRACTION * 100.0 == pytest.approx(5.0)


class TestPillar871NDACutoff:
    def test_cutoff_value(self): assert NDA_CUTOFF_OVER_MKK == pytest.approx(19.332878, rel=1e-6)
    def test_cutoff_function(self):
        assert nda_cutoff_ratio() == pytest.approx(NDA_CUTOFF_OVER_MKK, rel=1e-12)
    def test_cutoff_above_one(self): assert NDA_CUTOFF_OVER_MKK > 1.0
    def test_cutoff_rejects_nonpositive_coupling(self):
        with pytest.raises(ValueError):
            nda_cutoff_ratio(g=0.0)
    def test_levels_below_cutoff(self): assert N_KK_BELOW_CUTOFF == 19
    def test_levels_function(self): assert kk_levels_below_cutoff() == N_KK_BELOW_CUTOFF
    def test_levels_floor_of_cutoff(self): assert N_KK_BELOW_CUTOFF == int(NDA_CUTOFF_OVER_MKK)
    def test_levels_rejects_nonpositive_coupling(self):
        with pytest.raises(ValueError):
            kk_levels_below_cutoff(g=0.0)


class TestPillar871Shift:
    def test_relative_shift(self): assert DELTA_MH_OVER_MH == pytest.approx(0.016053075, rel=1e-7)
    def test_shift_function(self):
        assert one_loop_relative_shift() == pytest.approx(DELTA_MH_OVER_MH, rel=1e-12)
    def test_shift_below_bound(self): assert DELTA_MH_OVER_MH < BOUND_FRACTION
    def test_shift_positive(self): assert DELTA_MH_OVER_MH > 0.0
    def test_absolute_shift(self): assert DELTA_MH_GEV == pytest.approx(1.6524595, rel=1e-6)
    def test_bound_satisfied(self): assert BOUND_SATISFIED is True
    def test_shift_rejects_zero_shell(self):
        with pytest.raises(ValueError):
            one_loop_relative_shift(n_shell=0)
    def test_shift_grows_with_shell(self):
        assert one_loop_relative_shift(n_shell=8) > one_loop_relative_shift(n_shell=4)


class TestPillar871Band:
    def test_band_ordered(self): assert higgs_mass_band_gev()[0] < higgs_mass_band_gev()[1]
    def test_band_low(self): assert higgs_mass_band_gev()[0] == pytest.approx(101.284797, rel=1e-6)
    def test_band_high(self): assert higgs_mass_band_gev()[1] == pytest.approx(104.589716, rel=1e-6)
    def test_band_width_is_twice_shift(self):
        low, high = higgs_mass_band_gev()
        assert high - low == pytest.approx(2.0 * DELTA_MH_GEV, rel=1e-9)
    def test_pdg_outside_band_reported_honestly(self):
        assert higgs_uv_completion_limit_summary()["pdg_inside_band"] is False


class TestPillar871Summary:
    def test_summary_gate(self): assert higgs_uv_completion_limit_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert higgs_uv_completion_limit_summary()["pillar"] == 871
    def test_summary_lean4(self):
        assert higgs_uv_completion_limit_summary()["lean4_total_after"] == 2451
    def test_summary_certificate(self):
        assert higgs_uv_completion_limit_summary()["limit_certificate"] == LIMIT_CERTIFICATE
    def test_summary_bound_satisfied(self):
        assert higgs_uv_completion_limit_summary()["bound_satisfied"] is True
    def test_remaining_open_has_pdg_offset(self):
        assert any("PDG_OFFSET" in item for item in REMAINING_OPEN)
    def test_remaining_open_count(self): assert len(REMAINING_OPEN) >= 3
    def test_epistemic_status_architecture_limit(self):
        assert "ARCHITECTURE_LIMIT" in higgs_uv_completion_limit_summary()["epistemic_status"].upper()
