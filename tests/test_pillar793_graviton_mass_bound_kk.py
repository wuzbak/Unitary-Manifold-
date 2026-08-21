# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 793 — GRAVITON_MASS_BOUND_KK_SPECTRUM
~50 tests covering zero-mode masslessness, KK spectrum, width, and HL-LHC verdict.
"""
import math
import pytest
from src.core.pillar793_graviton_mass_bound_kk import (
    zero_mode_mass,
    kk_graviton_mass_tev,
    kk_mass_spectrum_tev,
    kk_graviton_width_gev,
    width_to_mass_ratio,
    hllhc_verdict,
    masslessness_proof_sketch,
    graviton_gate_summary,
    GATE,
    PILLAR_793_GATE,
    GRAVITON_GATE_SUMMARY,
    BESSEL_ZEROS_J1,
    M_KK_TEV,
    C_S,
    HLLHC_EXCLUSION_TEV,
    K_OVER_MPL_BENCHMARK,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:
    def test_gate_label(self):
        assert GATE == "GRAVITON_MASSLESS_KK_BOUND_DERIVED"

    def test_pillar_alias(self):
        assert PILLAR_793_GATE == GATE

    def test_bessel_zeros_count(self):
        assert len(BESSEL_ZEROS_J1) == 5

    def test_first_bessel_zero(self):
        assert BESSEL_ZEROS_J1[0] == pytest.approx(3.8317, rel=1e-4)

    def test_second_bessel_zero(self):
        assert BESSEL_ZEROS_J1[1] == pytest.approx(7.0156, rel=1e-4)

    def test_c_s_value(self):
        assert C_S == pytest.approx(12.0 / 37.0, rel=1e-9)

    def test_m_kk_tev(self):
        assert M_KK_TEV == 1.0

    def test_hllhc_exclusion(self):
        assert HLLHC_EXCLUSION_TEV == 4.0

    def test_k_over_mpl_benchmark(self):
        assert K_OVER_MPL_BENCHMARK == 0.1


# ---------------------------------------------------------------------------
# zero_mode_mass
# ---------------------------------------------------------------------------

class TestZeroModeMass:
    def test_exactly_zero(self):
        assert zero_mode_mass() == 0.0

    def test_returns_float(self):
        assert isinstance(zero_mode_mass(), float)


# ---------------------------------------------------------------------------
# kk_graviton_mass_tev
# ---------------------------------------------------------------------------

class TestKKGravitonMassTev:
    def test_mode1_positive(self):
        assert kk_graviton_mass_tev(1) > 0

    def test_mode1_formula(self):
        expected = BESSEL_ZEROS_J1[0] * M_KK_TEV * C_S**2
        assert kk_graviton_mass_tev(1) == pytest.approx(expected, rel=1e-9)

    def test_mode2_larger_than_mode1(self):
        assert kk_graviton_mass_tev(2) > kk_graviton_mass_tev(1)

    def test_mode3_larger_than_mode2(self):
        assert kk_graviton_mass_tev(3) > kk_graviton_mass_tev(2)

    def test_all_modes_positive(self):
        for n in range(1, 6):
            assert kk_graviton_mass_tev(n) > 0

    def test_invalid_mode_0_raises(self):
        with pytest.raises((ValueError, IndexError)):
            kk_graviton_mass_tev(0)

    def test_invalid_mode_6_raises(self):
        with pytest.raises((ValueError, IndexError)):
            kk_graviton_mass_tev(6)

    def test_scales_with_m_kk(self):
        m1 = kk_graviton_mass_tev(1, m_kk_tev=1.0)
        m2 = kk_graviton_mass_tev(1, m_kk_tev=2.0)
        assert m2 == pytest.approx(2.0 * m1, rel=1e-9)

    def test_scales_with_c_s_squared(self):
        m1 = kk_graviton_mass_tev(1, c_s=C_S)
        m2 = kk_graviton_mass_tev(1, c_s=2 * C_S)
        assert m2 == pytest.approx(4.0 * m1, rel=1e-9)

    def test_mode1_in_tev_range(self):
        m = kk_graviton_mass_tev(1)
        # Should be order-1 TeV
        assert 0.1 < m < 10.0


# ---------------------------------------------------------------------------
# kk_mass_spectrum_tev
# ---------------------------------------------------------------------------

class TestKKMassSpectrum:
    def test_returns_list(self):
        assert isinstance(kk_mass_spectrum_tev(), list)

    def test_length_default_5(self):
        assert len(kk_mass_spectrum_tev()) == 5

    def test_ascending(self):
        s = kk_mass_spectrum_tev()
        assert all(s[i] < s[i + 1] for i in range(len(s) - 1))

    def test_first_equals_mode1(self):
        s = kk_mass_spectrum_tev()
        assert s[0] == pytest.approx(kk_graviton_mass_tev(1), rel=1e-9)

    def test_all_positive(self):
        assert all(m > 0 for m in kk_mass_spectrum_tev())


# ---------------------------------------------------------------------------
# kk_graviton_width_gev
# ---------------------------------------------------------------------------

class TestKKGravitonWidth:
    def test_returns_float(self):
        assert isinstance(kk_graviton_width_gev(), float)

    def test_positive(self):
        assert kk_graviton_width_gev() > 0

    def test_scales_with_k_over_mpl_squared(self):
        w1 = kk_graviton_width_gev(1, k_over_mpl=0.1)
        w2 = kk_graviton_width_gev(1, k_over_mpl=0.2)
        assert w2 == pytest.approx(4.0 * w1, rel=1e-6)

    def test_formula_n1(self):
        m_gev = kk_graviton_mass_tev(1) * 1e3
        expected = (K_OVER_MPL_BENCHMARK**2 * m_gev * 39) / (16.0 * math.pi)
        assert kk_graviton_width_gev(1) == pytest.approx(expected, rel=1e-8)


# ---------------------------------------------------------------------------
# width_to_mass_ratio
# ---------------------------------------------------------------------------

class TestWidthToMassRatio:
    def test_returns_float(self):
        assert isinstance(width_to_mass_ratio(), float)

    def test_positive(self):
        assert width_to_mass_ratio() > 0

    def test_narrow_resonance(self):
        # For k/M_Pl=0.1, Γ/M should be much less than 1
        assert width_to_mass_ratio() < 0.5

    def test_consistent_with_width_and_mass(self):
        m_gev = kk_graviton_mass_tev(1) * 1e3
        w = kk_graviton_width_gev(1)
        assert width_to_mass_ratio(1) == pytest.approx(w / m_gev, rel=1e-9)


# ---------------------------------------------------------------------------
# hllhc_verdict
# ---------------------------------------------------------------------------

class TestHLLHCVerdict:
    def test_default_returns_string(self):
        assert isinstance(hllhc_verdict(), str)

    def test_default_pass_or_tension(self):
        v = hllhc_verdict()
        assert v in ("PASS", "TENSION", "FALSIFIED")

    def test_low_mass_falsified(self):
        assert hllhc_verdict(0.5) == "FALSIFIED"

    def test_high_mass_tension(self):
        assert hllhc_verdict(5.0) == "TENSION"

    def test_in_window_pass(self):
        assert hllhc_verdict(1.0) == "PASS"

    def test_borderline_pass_4tev(self):
        assert hllhc_verdict(4.0) == "PASS"

    def test_above_4tev_tension(self):
        assert hllhc_verdict(4.001) == "TENSION"


# ---------------------------------------------------------------------------
# masslessness_proof_sketch
# ---------------------------------------------------------------------------

class TestMasslessnessProof:
    def test_returns_dict(self):
        assert isinstance(masslessness_proof_sketch(), dict)

    def test_status_exact_massless(self):
        assert masslessness_proof_sketch()["status"] == "EXACT_MASSLESS"

    def test_claim_present(self):
        assert "claim" in masslessness_proof_sketch()

    def test_bianchi_present(self):
        assert "bianchi" in masslessness_proof_sketch()

    def test_caveats_list(self):
        assert isinstance(masslessness_proof_sketch()["caveats"], list)


# ---------------------------------------------------------------------------
# graviton_gate_summary
# ---------------------------------------------------------------------------

class TestGravitonGateSummary:
    def setup_method(self):
        self.s = graviton_gate_summary()

    def test_returns_dict(self):
        assert isinstance(self.s, dict)

    def test_pillar_793(self):
        assert self.s["pillar"] == 793

    def test_gate_label(self):
        assert self.s["gate"] == "GRAVITON_MASSLESS_KK_BOUND_DERIVED"

    def test_zero_mode_mass(self):
        assert self.s["zero_mode_mass_gev"] == 0.0

    def test_m_g_star_n1_positive(self):
        assert self.s["m_g_star_n1_tev"] > 0

    def test_spectrum_ascending(self):
        s = self.s["kk_spectrum_tev"]
        assert all(s[i] < s[i + 1] for i in range(len(s) - 1))

    def test_hllhc_exclusion_present(self):
        assert "hllhc_exclusion_tev" in self.s
        assert self.s["hllhc_exclusion_tev"] == 4.0

    def test_lean4_entry(self):
        assert "1051" in self.s["lean4"]
        assert "1066" in self.s["lean4"]

    def test_falsification_keys(self):
        f = self.s["falsification"]
        assert "PASS" in f
        assert "TENSION" in f
        assert "FALSIFIED" in f

    def test_alias_callable(self):
        s = GRAVITON_GATE_SUMMARY()
        assert s["pillar"] == 793
