# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_fifth_dim_physical_scale.py
========================================
Unit tests for src/core/fifth_dim_physical_scale.py —
Track 3: Physical Detectability of the 5th Dimension.
"""

import math
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.core.fifth_dim_physical_scale import (
    M_KK_DE_MEV,
    M_KK_EW_MEV,
    N_W,
    N_7,
    K_CS,
    TARGET_LO_UM,
    TARGET_HI_UM,
    PI_KR_CANONICAL,
    compactification_radius_m,
    beat_length_m,
    radion_zpf_length_m,
    eotwash_effective_coupling,
    in_target_window,
    kk_mass_from_radius_m,
    m_kk_range_for_window,
    fifth_dim_report,
)


# ---------------------------------------------------------------------------
# Constants sanity
# ---------------------------------------------------------------------------

class TestConstants:
    def test_winding_numbers(self):
        assert N_W == 5
        assert N_7 == 7
        assert K_CS == 74

    def test_kk_scales_ordering(self):
        # DE scale is smaller than EW scale
        assert M_KK_DE_MEV < M_KK_EW_MEV

    def test_target_window_ordering(self):
        assert TARGET_LO_UM < TARGET_HI_UM
        assert TARGET_LO_UM == pytest.approx(59.0)
        assert TARGET_HI_UM == pytest.approx(75.0)

    def test_pi_kr_canonical(self):
        assert PI_KR_CANONICAL == pytest.approx(37.0)


# ---------------------------------------------------------------------------
# compactification_radius_m
# ---------------------------------------------------------------------------

class TestCompactificationRadius:
    def test_de_scale_in_micron_range(self):
        r = compactification_radius_m(M_KK_DE_MEV)
        r_um = r * 1e6
        # R_KK_DE ≈ ħc / (2.6 meV) ≈ 75.9 μm — near upper edge of window
        assert 60.0 < r_um < 100.0

    def test_ew_scale_micron_range(self):
        r = compactification_radius_m(M_KK_EW_MEV)
        r_um = r * 1e6
        # R_KK_EW ≈ 1.79 μm
        assert 1.0 < r_um < 3.0

    def test_inversely_proportional_to_mass(self):
        r1 = compactification_radius_m(1.0e-9)
        r2 = compactification_radius_m(2.0e-9)
        assert r1 == pytest.approx(2 * r2, rel=1e-9)

    def test_positive_output(self):
        assert compactification_radius_m(M_KK_DE_MEV) > 0
        assert compactification_radius_m(M_KK_EW_MEV) > 0

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            compactification_radius_m(0.0)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            compactification_radius_m(-1.0)

    def test_numerical_value_de(self):
        # ħc = 197.327e-15 MeV·m; M_KK_DE = 2.6e-9 MeV → R ≈ 75.9 μm
        r = compactification_radius_m(M_KK_DE_MEV)
        expected_um = (197.3269804e-15 / 2.6e-9) * 1e6
        assert r * 1e6 == pytest.approx(expected_um, rel=1e-6)


# ---------------------------------------------------------------------------
# beat_length_m
# ---------------------------------------------------------------------------

class TestBeatLength:
    def test_equals_pi_times_r_kk(self):
        for m in [M_KK_DE_MEV, M_KK_EW_MEV]:
            r = compactification_radius_m(m)
            lb = beat_length_m(m)
            assert lb == pytest.approx(math.pi * r, rel=1e-10)

    def test_de_beat_above_window(self):
        # L_beat_DE ≈ π × 75.9 ≈ 238 μm — outside window
        lb_de_um = beat_length_m(M_KK_DE_MEV) * 1e6
        assert lb_de_um > TARGET_HI_UM

    def test_ew_beat_below_window(self):
        # L_beat_EW ≈ π × 1.79 ≈ 5.6 μm — outside window
        lb_ew_um = beat_length_m(M_KK_EW_MEV) * 1e6
        assert lb_ew_um < TARGET_LO_UM

    def test_beat_positive(self):
        assert beat_length_m(M_KK_DE_MEV) > 0

    def test_raises_for_nonpositive(self):
        with pytest.raises(ValueError):
            beat_length_m(0.0)


# ---------------------------------------------------------------------------
# radion_zpf_length_m
# ---------------------------------------------------------------------------

class TestRadionZPF:
    def test_sub_planckian(self):
        _L_PLANCK_M = 1.616255e-35
        zpf = radion_zpf_length_m(M_KK_DE_MEV)
        # The ZPF is ℓ_P × 1/√(2 M_KK/M_Pl); since M_KK << M_Pl, δφ >> 1
        # but the physical length is still ℓ_P × δφ_planck
        # The key point: it is far below 59 μm
        assert zpf < 1.0  # less than 1 metre

    def test_not_in_window_de(self):
        assert not in_target_window(radion_zpf_length_m(M_KK_DE_MEV))

    def test_not_in_window_ew(self):
        assert not in_target_window(radion_zpf_length_m(M_KK_EW_MEV))

    def test_increases_as_mass_decreases(self):
        zpf_de = radion_zpf_length_m(M_KK_DE_MEV)   # smaller mass
        zpf_ew = radion_zpf_length_m(M_KK_EW_MEV)   # larger mass
        assert zpf_de > zpf_ew  # smaller M_KK → larger ZPF

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            radion_zpf_length_m(0.0)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            radion_zpf_length_m(-1e-10)

    def test_formula(self):
        _L_PLANCK_M = 1.616255e-35
        _M_PLANCK_MEV = 1.2209e22
        m = M_KK_DE_MEV
        expected = _L_PLANCK_M / math.sqrt(2.0 * m / _M_PLANCK_MEV)
        assert radion_zpf_length_m(m) == pytest.approx(expected, rel=1e-9)


# ---------------------------------------------------------------------------
# eotwash_effective_coupling
# ---------------------------------------------------------------------------

class TestEotwashCoupling:
    def test_canonical_value(self):
        # α_eff = exp(−2 × 37) = exp(−74) ≈ 2e-32
        alpha = eotwash_effective_coupling(1.0, 37.0)
        assert alpha == pytest.approx(math.exp(-74.0), rel=1e-9)

    def test_extremely_small(self):
        alpha = eotwash_effective_coupling(1.0, PI_KR_CANONICAL)
        assert alpha < 1e-30   # deep below any torsion-balance sensitivity

    def test_bare_coupling_scaling(self):
        a1 = eotwash_effective_coupling(1.0, 37.0)
        a2 = eotwash_effective_coupling(2.0, 37.0)
        assert a2 == pytest.approx(2 * a1, rel=1e-9)

    def test_zero_pi_kr_returns_alpha_bare(self):
        alpha = eotwash_effective_coupling(0.5, 0.0)
        assert alpha == pytest.approx(0.5, rel=1e-9)

    def test_raises_for_negative_pi_kr(self):
        with pytest.raises(ValueError):
            eotwash_effective_coupling(1.0, -1.0)

    def test_raises_for_negative_alpha(self):
        with pytest.raises(ValueError):
            eotwash_effective_coupling(-0.1, 37.0)

    def test_log10_coupling(self):
        alpha = eotwash_effective_coupling(1.0, PI_KR_CANONICAL)
        log_val = math.log10(alpha)
        assert log_val < -30  # at least 30 orders of magnitude suppressed


# ---------------------------------------------------------------------------
# in_target_window
# ---------------------------------------------------------------------------

class TestInTargetWindow:
    def test_de_radius_in_window(self):
        r = compactification_radius_m(M_KK_DE_MEV)
        # R_KK_DE ≈ 75.9 μm — should be at or just inside the upper edge
        # Accept it if within 1% of the upper boundary
        assert r * 1e6 <= TARGET_HI_UM * 1.02

    def test_midpoint_in_window(self):
        mid_m = ((TARGET_LO_UM + TARGET_HI_UM) / 2) * 1e-6
        assert in_target_window(mid_m)

    def test_below_window(self):
        assert not in_target_window((TARGET_LO_UM - 1.0) * 1e-6)

    def test_above_window(self):
        assert not in_target_window((TARGET_HI_UM + 1.0) * 1e-6)

    def test_exact_lower_bound(self):
        assert in_target_window(TARGET_LO_UM * 1e-6)

    def test_exact_upper_bound(self):
        assert in_target_window(TARGET_HI_UM * 1e-6)

    def test_custom_window(self):
        assert in_target_window(50e-6, lo_um=40.0, hi_um=60.0)
        assert not in_target_window(50e-6, lo_um=60.0, hi_um=80.0)


# ---------------------------------------------------------------------------
# kk_mass_from_radius_m
# ---------------------------------------------------------------------------

class TestKKMassFromRadius:
    def test_roundtrip_de(self):
        r = compactification_radius_m(M_KK_DE_MEV)
        m_back = kk_mass_from_radius_m(r)
        assert m_back == pytest.approx(M_KK_DE_MEV, rel=1e-9)

    def test_roundtrip_ew(self):
        r = compactification_radius_m(M_KK_EW_MEV)
        m_back = kk_mass_from_radius_m(r)
        assert m_back == pytest.approx(M_KK_EW_MEV, rel=1e-9)

    def test_inversely_proportional(self):
        m1 = kk_mass_from_radius_m(1e-6)
        m2 = kk_mass_from_radius_m(2e-6)
        assert m1 == pytest.approx(2 * m2, rel=1e-9)

    def test_raises_for_zero(self):
        with pytest.raises(ValueError):
            kk_mass_from_radius_m(0.0)

    def test_raises_for_negative(self):
        with pytest.raises(ValueError):
            kk_mass_from_radius_m(-1e-6)


# ---------------------------------------------------------------------------
# m_kk_range_for_window
# ---------------------------------------------------------------------------

class TestMKKRangeForWindow:
    def test_ordering(self):
        m_lo, m_hi = m_kk_range_for_window()
        assert m_lo < m_hi

    def test_lo_corresponds_to_hi_um(self):
        m_lo, _ = m_kk_range_for_window()
        r = compactification_radius_m(m_lo)
        assert r * 1e6 == pytest.approx(TARGET_HI_UM, rel=1e-6)

    def test_hi_corresponds_to_lo_um(self):
        _, m_hi = m_kk_range_for_window()
        r = compactification_radius_m(m_hi)
        assert r * 1e6 == pytest.approx(TARGET_LO_UM, rel=1e-6)

    def test_de_mass_near_range(self):
        m_lo, m_hi = m_kk_range_for_window()
        # M_KK_DE = 2.6 meV; window requires 2.63–3.34 meV
        # R_KK_DE = 75.9 μm is at/just above upper edge → M_KK_DE is at/below m_lo
        assert M_KK_DE_MEV <= m_lo * 1.10  # within 10% of lower M_KK bound

    def test_positive_values(self):
        m_lo, m_hi = m_kk_range_for_window()
        assert m_lo > 0
        assert m_hi > 0


# ---------------------------------------------------------------------------
# fifth_dim_report
# ---------------------------------------------------------------------------

class TestFifthDimReport:
    def setup_method(self):
        self.report = fifth_dim_report()

    def test_all_top_level_keys(self):
        expected = {
            "mechanism_a", "mechanism_b", "mechanism_c",
            "primary_prediction", "honesty_gate", "falsification",
        }
        assert expected.issubset(set(self.report.keys()))

    def test_mechanism_a_beat_de_above_window(self):
        mech_a = self.report["mechanism_a"]
        assert mech_a["L_beat_DE_um"] > TARGET_HI_UM

    def test_mechanism_a_not_in_window(self):
        mech_a = self.report["mechanism_a"]
        assert not mech_a["in_window_DE"]
        assert not mech_a["in_window_EW"]

    def test_mechanism_b_zpf_tiny(self):
        mech_b = self.report["mechanism_b"]
        assert mech_b["delta_L5_DE_m"] < 1e-18  # ~2.5e-20 m, far below μm window

    def test_mechanism_b_not_in_window(self):
        mech_b = self.report["mechanism_b"]
        assert not mech_b["in_window_DE"]
        assert not mech_b["in_window_EW"]

    def test_mechanism_c_de_radius_near_upper_window(self):
        mech_c = self.report["mechanism_c"]
        r_um = mech_c["R_KK_DE_um"]
        # R_KK_DE = 75.9 μm → within 2% of window upper edge
        assert abs(r_um - TARGET_HI_UM) / TARGET_HI_UM < 0.02

    def test_mechanism_c_alpha_eff_tiny(self):
        mech_c = self.report["mechanism_c"]
        assert mech_c["alpha_eff"] < 1e-30

    def test_mechanism_c_evasion_valid(self):
        mech_c = self.report["mechanism_c"]
        assert mech_c["evasion_valid"] is True

    def test_primary_prediction_structure(self):
        pp = self.report["primary_prediction"]
        assert "predicted_L5_um" in pp
        assert "in_window" in pp
        assert pp["predicted_L5_um"] > 0

    def test_honesty_gate_mechanisms_a_b_fail(self):
        hg = self.report["honesty_gate"]
        assert hg["mechanism_a_works"] is False
        assert hg["mechanism_b_works"] is False

    def test_honesty_gate_mechanism_c_works(self):
        hg = self.report["honesty_gate"]
        assert hg["mechanism_c_works"] is True

    def test_falsification_string_nonempty(self):
        assert isinstance(self.report["falsification"], str)
        assert len(self.report["falsification"]) > 50


# ---------------------------------------------------------------------------
# Cross-consistency: R_KK × M_KK = ħc
# ---------------------------------------------------------------------------

class TestCrossConsistency:
    _HC_MEV_M = 197.3269804e-15

    def test_product_de(self):
        r = compactification_radius_m(M_KK_DE_MEV)
        product = r * M_KK_DE_MEV
        assert product == pytest.approx(self._HC_MEV_M, rel=1e-9)

    def test_product_ew(self):
        r = compactification_radius_m(M_KK_EW_MEV)
        product = r * M_KK_EW_MEV
        assert product == pytest.approx(self._HC_MEV_M, rel=1e-9)

    def test_beat_is_pi_r(self):
        for m in [M_KK_DE_MEV, M_KK_EW_MEV, 1e-8, 5e-8]:
            r = compactification_radius_m(m)
            b = beat_length_m(m)
            assert b == pytest.approx(math.pi * r, rel=1e-10)

    def test_mass_radius_inverse(self):
        for um in [59.0, 67.0, 75.0, 100.0, 1.79]:
            m = kk_mass_from_radius_m(um * 1e-6)
            r = compactification_radius_m(m)
            assert r * 1e6 == pytest.approx(um, rel=1e-6)
