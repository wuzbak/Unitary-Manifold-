# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for src/sixd/neutrino_overlap_integrals_nlo.py — Track 3 (Neutrinos NLO)."""
from __future__ import annotations

import math
import pytest

from src.sixd.neutrino_overlap_integrals_nlo import (
    C_RNU_SPECTRUM,
    DM2_21_PDG,
    DM2_31_PDG,
    KK_MASS_RATIO,
    RESIDUAL_31_LO_PCT,
    SIGMA_LO,
    SIGMA_NLO_FACTOR,
    dirac_yukawa_nlo,
    dm2_residuals_nlo,
    effective_nlo_enhancement_factor,
    neutrino_mass_splittings_nlo,
    neutrino_nlo_summary,
    nlo_correction_factor,
    nlo_gate_check,
    overlap_integral_lo,
    overlap_integral_nlo,
)


class TestConstants:
    def test_sigma_lo(self):
        assert SIGMA_LO == pytest.approx(1.0 / 3.0, rel=1e-9)

    def test_sigma_nlo_factor(self):
        assert SIGMA_NLO_FACTOR == pytest.approx(0.15, rel=1e-9)

    def test_kk_mass_ratio(self):
        assert KK_MASS_RATIO == pytest.approx(0.10, rel=1e-9)

    def test_residual_31_lo_pct(self):
        assert RESIDUAL_31_LO_PCT == pytest.approx(10.5, rel=1e-6)

    def test_c_rnu_spectrum_length(self):
        assert len(C_RNU_SPECTRUM) == 3

    def test_c_rnu_ordered(self):
        assert C_RNU_SPECTRUM[0] < C_RNU_SPECTRUM[1] < C_RNU_SPECTRUM[2]

    def test_dm2_21_pdg(self):
        assert DM2_21_PDG == pytest.approx(7.53e-5, rel=1e-6)

    def test_dm2_31_pdg(self):
        assert DM2_31_PDG == pytest.approx(2.453e-3, rel=1e-6)


class TestOverlapIntegralLO:
    def test_diagonal_is_one(self):
        for i in range(3):
            assert overlap_integral_lo(i, i) == pytest.approx(1.0, rel=1e-9)

    def test_off_diagonal_less_than_one(self):
        assert overlap_integral_lo(0, 1) < 1.0
        assert overlap_integral_lo(0, 2) < 1.0

    def test_symmetric(self):
        assert overlap_integral_lo(0, 1) == pytest.approx(overlap_integral_lo(1, 0), rel=1e-9)
        assert overlap_integral_lo(0, 2) == pytest.approx(overlap_integral_lo(2, 0), rel=1e-9)

    def test_positive(self):
        for i in range(3):
            for j in range(3):
                assert overlap_integral_lo(i, j) > 0

    def test_invalid_index_raises(self):
        with pytest.raises(ValueError):
            overlap_integral_lo(3, 0)
        with pytest.raises(ValueError):
            overlap_integral_lo(0, -1)

    def test_farther_points_smaller_overlap(self):
        # |0-2| > |0-1| → I_02 < I_01
        assert overlap_integral_lo(0, 2) < overlap_integral_lo(0, 1)


class TestOverlapIntegralNLO:
    def test_larger_than_lo(self):
        # NLO adds positive corrections → I_NLO >= I_LO
        for i in range(3):
            for j in range(3):
                assert overlap_integral_nlo(i, j) >= overlap_integral_lo(i, j)

    def test_diagonal_nlo_positive(self):
        for i in range(3):
            assert overlap_integral_nlo(i, i) > 0

    def test_symmetric(self):
        # Symmetric corrections → still symmetric
        assert overlap_integral_nlo(0, 1) == pytest.approx(overlap_integral_nlo(1, 0), rel=1e-6)

    def test_returns_float(self):
        assert isinstance(overlap_integral_nlo(0, 1), float)


class TestNLOCorrectionFactor:
    def test_greater_than_one(self):
        for i in range(3):
            for j in range(3):
                assert nlo_correction_factor(i, j) >= 1.0

    def test_off_diagonal_larger_correction(self):
        # Z₃ mixing adds extra correction for i ≠ j
        f_diag = nlo_correction_factor(0, 0)
        f_offdiag = nlo_correction_factor(0, 1)
        assert f_offdiag > f_diag

    def test_returns_float(self):
        assert isinstance(nlo_correction_factor(1, 2), float)


class TestEffectiveNLOEnhancementFactor:
    def test_greater_than_diagonal_average(self):
        diag = sum(nlo_correction_factor(i, i) for i in range(3)) / 3.0
        assert effective_nlo_enhancement_factor() > diag

    def test_returns_float(self):
        assert isinstance(effective_nlo_enhancement_factor(), float)


class TestDiracYukawaNLO:
    def test_positive(self):
        y = dirac_yukawa_nlo(0.5, 1.0, 0, 0)
        assert y > 0

    def test_scales_with_g5(self):
        y1 = dirac_yukawa_nlo(0.5, 1.0, 0, 0)
        y2 = dirac_yukawa_nlo(0.5, 2.0, 0, 0)
        assert y2 == pytest.approx(2 * y1, rel=1e-9)

    def test_scales_with_c_rnu(self):
        y1 = dirac_yukawa_nlo(0.5, 1.0, 1, 1)
        y2 = dirac_yukawa_nlo(1.0, 1.0, 1, 1)
        assert y2 == pytest.approx(2 * y1, rel=1e-9)


class TestNeutrinoMassSplittingsNLO:
    def test_returns_dict_with_required_keys(self):
        result = neutrino_mass_splittings_nlo(C_RNU_SPECTRUM)
        for key in ["dm2_21_eV2", "dm2_31_eV2", "masses_eV"]:
            assert key in result

    def test_three_masses(self):
        result = neutrino_mass_splittings_nlo(C_RNU_SPECTRUM)
        assert len(result["masses_eV"]) == 3

    def test_dm2_31_positive(self):
        result = neutrino_mass_splittings_nlo(C_RNU_SPECTRUM)
        assert result["dm2_31_eV2"] > 0

    def test_dm2_21_positive(self):
        result = neutrino_mass_splittings_nlo(C_RNU_SPECTRUM)
        assert result["dm2_21_eV2"] > 0

    def test_scales_with_m_lightest(self):
        r1 = neutrino_mass_splittings_nlo(C_RNU_SPECTRUM, m_lightest=0.01)
        r2 = neutrino_mass_splittings_nlo(C_RNU_SPECTRUM, m_lightest=0.02)
        assert r2["dm2_31_eV2"] == pytest.approx(4 * r1["dm2_31_eV2"], rel=1e-6)


class TestDM2ResidualsNLO:
    def test_residual_31_in_percent(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert 0 <= r["residual_31_pct"] < 100

    def test_residual_21_key_present(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert "dm2_21_pdg_eV2" in r

    def test_residual_31_improved_vs_lo(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert r["residual_31_pct"] < RESIDUAL_31_LO_PCT  # NLO must improve on LO

    def test_pdg_value_returned(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert r["dm2_31_pdg_eV2"] == pytest.approx(DM2_31_PDG, rel=1e-6)

    def test_nlo_factor_greater_than_one(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert r["nlo_avg_diagonal_factor"] > 1.0

    def test_effective_factor_exceeds_diagonal_factor(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert r["nlo_effective_factor"] > r["nlo_avg_diagonal_factor"]

    def test_residual_in_range_7_to_8(self):
        r = dm2_residuals_nlo(C_RNU_SPECTRUM)
        assert 7.0 < r["residual_31_pct"] < 8.5


class TestNLOGateCheck:
    def test_gate_not_passed(self):
        # Expected: still ~8-9%, gate threshold 5%
        gate = nlo_gate_check()
        assert gate["gate_pass"] is False

    def test_improvement_positive(self):
        gate = nlo_gate_check()
        assert gate["improvement_pct"] > 0

    def test_status_geometric_estimate(self):
        gate = nlo_gate_check()
        assert "GEOMETRIC_ESTIMATE_CERTIFIED" in gate["status"]

    def test_threshold_is_five_percent(self):
        gate = nlo_gate_check()
        assert gate["gate_threshold_pct"] == pytest.approx(5.0, rel=1e-9)

    def test_returns_required_keys(self):
        gate = nlo_gate_check()
        for key in ["residual_31_nlo_pct", "residual_31_lo_pct",
                    "improvement_pct", "gate_threshold_pct", "gate_pass", "status"]:
            assert key in gate


class TestNeutrinoNLOSummary:
    def test_returns_dict(self):
        s = neutrino_nlo_summary()
        assert isinstance(s, dict)

    def test_overall_status(self):
        s = neutrino_nlo_summary()
        assert "GEOMETRIC_ESTIMATE_CERTIFIED" in s["overall_status"]

    def test_residual_improved(self):
        s = neutrino_nlo_summary()
        assert s["dm2_31_residual_nlo_pct"] < s["dm2_31_residual_lo_pct"]

    def test_nlo_correction_factors_present(self):
        s = neutrino_nlo_summary()
        assert "nlo_correction_factors" in s
        assert len(s["nlo_correction_factors"]) == 9

    def test_dm2_21_status_present(self):
        s = neutrino_nlo_summary()
        assert "dm2_21_status" in s
        assert "UNCONSTRAINED" in s["dm2_21_status"]
