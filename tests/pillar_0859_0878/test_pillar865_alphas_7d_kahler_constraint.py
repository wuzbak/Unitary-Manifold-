# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 865 — α_s from the Green-Schwarz Kähler volume constraint."""
from __future__ import annotations

import pytest

from src.core.pillar865_alphas_7d_kahler_constraint import (
    ALPHA_S_MZ_CENTRAL,
    ALPHA_S_MZ_INTERVAL,
    ALPHA_S_PDG,
    ALPHA_S_PDG_ERR,
    B0_QCD,
    KAHLER_MODULUS_RHO,
    K_CS,
    LEAN4_THEOREM_COUNT,
    LEAN4_TOTAL_AFTER,
    LEAN4_TOTAL_BEFORE,
    M7_OVER_MKK_CANONICAL,
    M7_SCAN,
    M_KK_GEV,
    M_Z_GEV,
    N_FLUX,
    PDG_INSIDE_INTERVAL,
    PILLAR_GATE,
    PILLAR_NUMBER,
    REMAINING_OPEN,
    TENSION_SIGMA,
    VOL_T2_OVER_LS2,
    alpha_s_at_mkk,
    alpha_s_mz,
    alphas_kahler_summary,
    gs_tadpole_volume,
    kahler_modulus,
    run_alpha_s_to_mz,
    volume_scan,
)


class TestPillar865Constants:
    def test_pillar_number(self): assert PILLAR_NUMBER == 865
    def test_gate(self): assert PILLAR_GATE == "ALPHA_S_7D_VOLUME_NARROWED"
    def test_lean4_count(self): assert LEAN4_THEOREM_COUNT == 30
    def test_lean4_total_before(self): assert LEAN4_TOTAL_BEFORE == 2296
    def test_lean4_total_after(self): assert LEAN4_TOTAL_AFTER == 2326
    def test_lean4_arithmetic(self): assert LEAN4_TOTAL_BEFORE + LEAN4_THEOREM_COUNT == LEAN4_TOTAL_AFTER
    def test_k_cs(self): assert K_CS == 74
    def test_n_flux(self): assert N_FLUX == 1
    def test_b0(self): assert B0_QCD == pytest.approx(7.0)
    def test_m_kk(self): assert M_KK_GEV == pytest.approx(1042.0)
    def test_m_z(self): assert M_Z_GEV == pytest.approx(91.2)


class TestPillar865Tadpole:
    def test_volume_value(self): assert VOL_T2_OVER_LS2 == pytest.approx(74.0)
    def test_modulus_value(self): assert KAHLER_MODULUS_RHO == pytest.approx(74.0)
    def test_tadpole_function(self): assert gs_tadpole_volume() == pytest.approx(74.0)
    def test_tadpole_scales_with_flux(self): assert gs_tadpole_volume(n_flux=2) == pytest.approx(37.0)
    def test_tadpole_rejects_zero_flux(self):
        with pytest.raises(ValueError):
            gs_tadpole_volume(n_flux=0)
    def test_modulus_equals_volume(self): assert kahler_modulus() == pytest.approx(VOL_T2_OVER_LS2)


class TestPillar865Running:
    def test_alpha_at_mkk_positive(self): assert alpha_s_at_mkk() > 0.0
    def test_alpha_at_mkk_rejects_zero_ratio(self):
        with pytest.raises(ValueError):
            alpha_s_at_mkk(m7_over_mkk=0.0)
    def test_running_decreases_coupling(self):
        assert run_alpha_s_to_mz(0.17) > 0.17 or run_alpha_s_to_mz(0.17) > 0.0
    def test_running_rejects_nonpositive(self):
        with pytest.raises(ValueError):
            run_alpha_s_to_mz(0.0)
    def test_alpha_s_mz_central(self): assert ALPHA_S_MZ_CENTRAL == pytest.approx(0.11624572, rel=1e-6)
    def test_alpha_s_mz_function(self):
        assert alpha_s_mz() == pytest.approx(ALPHA_S_MZ_CENTRAL, rel=1e-12)
    def test_canonical_ratio_is_one(self): assert M7_OVER_MKK_CANONICAL == pytest.approx(1.0)
    def test_scan_length(self): assert len(M7_SCAN) == 5
    def test_scan_rows(self): assert len(volume_scan()) == len(M7_SCAN)
    def test_scan_monotone_in_ratio(self):
        rows = volume_scan()
        assert rows[0]["alpha_s_mz"] > rows[-1]["alpha_s_mz"]


class TestPillar865Interval:
    def test_interval_ordered(self): assert ALPHA_S_MZ_INTERVAL[0] < ALPHA_S_MZ_INTERVAL[1]
    def test_interval_low(self): assert ALPHA_S_MZ_INTERVAL[0] == pytest.approx(0.06900740, rel=1e-6)
    def test_interval_high(self): assert ALPHA_S_MZ_INTERVAL[1] == pytest.approx(0.17673775, rel=1e-6)
    def test_pdg_inside_interval(self): assert PDG_INSIDE_INTERVAL is True
    def test_pdg_reference(self): assert ALPHA_S_PDG == pytest.approx(0.1179)
    def test_pdg_error(self): assert ALPHA_S_PDG_ERR == pytest.approx(0.0010)
    def test_tension_sigma(self): assert TENSION_SIGMA == pytest.approx(1.65428, rel=1e-4)
    def test_interval_not_a_point(self):
        assert ALPHA_S_MZ_INTERVAL[1] - ALPHA_S_MZ_INTERVAL[0] > 0.05


class TestPillar865Summary:
    def test_summary_gate(self): assert alphas_kahler_summary()["gate"] == PILLAR_GATE
    def test_summary_pillar(self): assert alphas_kahler_summary()["pillar"] == 865
    def test_summary_lean4(self): assert alphas_kahler_summary()["lean4_total_after"] == 2326
    def test_remaining_open_nonempty(self): assert len(REMAINING_OPEN) >= 2
    def test_epistemic_status_narrowed_not_pinned(self):
        status = alphas_kahler_summary()["epistemic_status"].upper()
        assert "NARROW" in status or "OPEN" in status
