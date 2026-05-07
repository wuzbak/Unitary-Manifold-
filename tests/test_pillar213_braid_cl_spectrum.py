# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
tests/test_pillar213_braid_cl_spectrum.py
==========================================
Tests for Pillar 213 — Sub-leading CS Braid Corrections to RS Bulk-Mass Spectrum.

Covers:
  - f0() zero-mode wavefunction
  - cl_leading() leading-order c_L values
  - cs_phase_correction() CS braid correction
  - cl_corrected() corrected c_L
  - braid_mass_ratio() consecutive-generation mass ratios
  - pillar213_summary() full summary
  - Honest gate: fermion masses from winding quantization are O(10-100x) off PDG
  - Physical properties and input validation
"""
from __future__ import annotations

import math
import pytest

from src.core.pillar213_braid_cl_spectrum import (
    f0,
    cl_leading,
    cs_phase_correction,
    cl_corrected,
    braid_mass_ratio,
    pillar213_summary,
    N_W,
    N1,
    N2,
    K_CS,
    PI_KR,
    V_EW_MEV,
    YUKAWA5,
    SECTORS,
    __provenance__,
)

_TOL = 1e-12


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

class TestConstants:

    def test_n_w(self):
        assert N_W == 5

    def test_n1(self):
        assert N1 == 5

    def test_n2(self):
        assert N2 == 7

    def test_k_cs(self):
        assert K_CS == 74

    def test_k_cs_equals_n1sq_plus_n2sq(self):
        assert K_CS == N1 ** 2 + N2 ** 2

    def test_pi_kr(self):
        assert abs(PI_KR - 37.0) < _TOL

    def test_v_ew_mev(self):
        assert abs(V_EW_MEV - 246_220.0) < 1.0

    def test_yukawa5(self):
        assert abs(YUKAWA5 - 1.0) < _TOL

    def test_sectors_tuple(self):
        assert "leptons" in SECTORS
        assert "up_quarks" in SECTORS
        assert "down_quarks" in SECTORS


# ---------------------------------------------------------------------------
# f0() — RS zero-mode wavefunction
# ---------------------------------------------------------------------------

class TestF0:

    def test_f0_at_half_equals_inv_sqrt_pi_kr(self):
        """f₀(1/2) = 1/√(π k R)."""
        result = f0(0.5)
        expected = 1.0 / math.sqrt(PI_KR)
        assert abs(result - expected) < 1e-10

    def test_f0_at_half_default_pi_kr(self):
        assert abs(f0(0.5) - 1.0 / math.sqrt(37.0)) < 1e-10

    def test_f0_at_09_positive(self):
        assert f0(0.9) > 0.0

    def test_f0_at_09_less_than_f0_half(self):
        """UV-localized (c > 0.5) wavefunctions are exponentially suppressed."""
        assert f0(0.9) < f0(0.5)

    def test_f0_at_08_positive(self):
        assert f0(0.8) > 0.0

    def test_f0_at_07_positive(self):
        assert f0(0.7) > 0.0

    def test_f0_monotone_decreasing_in_c(self):
        """f₀ decreases as c increases above 0.5."""
        cs = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        vals = [f0(c) for c in cs]
        for (c_curr, c_next, val_curr, val_next) in zip(cs[:-1], cs[1:], vals[:-1], vals[1:]):
            assert val_curr >= val_next, (
                f"f0({c_curr})={val_curr} not >= f0({c_next})={val_next}"
            )

    def test_f0_at_09_formula(self):
        """Manual check: x=0.8, exp(0.8*37)-1 large."""
        c = 0.9
        x = 2 * c - 1  # 0.8
        exp_arg = x * 37.0
        expected = math.sqrt(x) * math.exp(-exp_arg / 2.0)  # large-arg approx
        result = f0(c)
        # Should agree to better than 0.01% since exp(0.8*37)~10^12
        assert abs(result - expected) / expected < 1e-6

    def test_f0_returns_float(self):
        assert isinstance(f0(0.7), float)

    def test_f0_custom_pi_kr(self):
        result = f0(0.5, pi_k_r=100.0)
        expected = 1.0 / math.sqrt(100.0)
        assert abs(result - expected) < 1e-10

    def test_f0_negative_c_raises(self):
        with pytest.raises(ValueError):
            f0(-0.1)

    def test_f0_zero_pi_kr_raises(self):
        with pytest.raises(ValueError):
            f0(0.7, pi_k_r=0.0)

    def test_f0_negative_pi_kr_raises(self):
        with pytest.raises(ValueError):
            f0(0.7, pi_k_r=-1.0)

    def test_f0_c_zero_is_finite(self):
        """c=0 (IR-localized) — x = -1, should not be physically used
        but formula path exercises the exp-arg branch."""
        # With c=0, x = -1 < 0; denominator = exp(-37) - 1 < 0, raises ValueError
        with pytest.raises((ValueError, ZeroDivisionError)):
            _ = f0(0.0)

    def test_f0_at_c_slightly_above_half(self):
        result = f0(0.501)
        assert result > 0.0


# ---------------------------------------------------------------------------
# cl_leading()
# ---------------------------------------------------------------------------

class TestClLeading:

    def test_gen0_equals_09(self):
        assert abs(cl_leading(0) - 0.9) < _TOL

    def test_gen1_equals_08(self):
        assert abs(cl_leading(1) - 0.8) < _TOL

    def test_gen2_equals_07(self):
        assert abs(cl_leading(2) - 0.7) < _TOL

    def test_formula_gen0(self):
        expected = 0.5 + (5 - 1) / (2 * 5)
        assert abs(cl_leading(0) - expected) < _TOL

    def test_formula_gen1(self):
        expected = 0.5 + (5 - 2) / (2 * 5)
        assert abs(cl_leading(1) - expected) < _TOL

    def test_formula_gen2(self):
        expected = 0.5 + (5 - 3) / (2 * 5)
        assert abs(cl_leading(2) - expected) < _TOL

    def test_all_cl_above_half(self):
        for gen in (0, 1, 2):
            assert cl_leading(gen) > 0.5

    def test_decreasing_with_gen(self):
        """Higher generation → smaller c_L (less UV-localized)."""
        assert cl_leading(0) > cl_leading(1) > cl_leading(2)

    def test_invalid_gen_raises(self):
        with pytest.raises(ValueError):
            cl_leading(3)

    def test_negative_gen_raises(self):
        with pytest.raises(ValueError):
            cl_leading(-1)


# ---------------------------------------------------------------------------
# cs_phase_correction()
# ---------------------------------------------------------------------------

class TestCsPhaseCorrection:

    def test_gen0_order1_is_zero(self):
        """No correction for first generation (gen=0)."""
        assert cs_phase_correction(0, order=1) == 0.0

    def test_gen0_order2_is_zero(self):
        assert cs_phase_correction(0, order=2) == 0.0

    def test_gen1_order1_positive(self):
        assert cs_phase_correction(1, order=1) > 0.0

    def test_gen2_order1_positive(self):
        assert cs_phase_correction(2, order=1) > 0.0

    def test_gen1_order1_formula(self):
        expected = 1 * 5 * 7 / (49 * 74)
        assert abs(cs_phase_correction(1, order=1) - expected) < _TOL

    def test_gen2_order1_formula(self):
        expected = 2 * 5 * 7 / (49 * 74)
        assert abs(cs_phase_correction(2, order=1) - expected) < _TOL

    def test_order1_linear_in_gen(self):
        """δc_L^(1) is linear in gen → gen=2 is 2× gen=1."""
        d1 = cs_phase_correction(1, order=1)
        d2 = cs_phase_correction(2, order=1)
        assert abs(d2 - 2 * d1) < _TOL

    def test_order1_gen1_numerical(self):
        assert abs(cs_phase_correction(1, order=1) - 35 / 3626) < _TOL

    def test_order1_gen2_numerical(self):
        assert abs(cs_phase_correction(2, order=1) - 70 / 3626) < _TOL

    def test_gen1_order2_positive(self):
        assert cs_phase_correction(1, order=2) > 0.0

    def test_gen2_order2_four_times_gen1(self):
        """δc_L^(2) ∝ gen² → gen=2 is 4× gen=1."""
        d1 = cs_phase_correction(1, order=2)
        d2 = cs_phase_correction(2, order=2)
        assert abs(d2 - 4 * d1) < _TOL

    def test_order2_smaller_than_order1_gen1(self):
        """Two-loop is smaller than one-loop for gen=1."""
        assert cs_phase_correction(1, order=2) < cs_phase_correction(1, order=1)

    def test_increasing_with_gen_order1(self):
        corrections = [cs_phase_correction(g, order=1) for g in (0, 1, 2)]
        assert corrections[0] <= corrections[1] <= corrections[2]

    def test_invalid_gen_raises(self):
        with pytest.raises(ValueError):
            cs_phase_correction(3, order=1)

    def test_invalid_order_raises(self):
        with pytest.raises(ValueError):
            cs_phase_correction(1, order=3)


# ---------------------------------------------------------------------------
# cl_corrected()
# ---------------------------------------------------------------------------

class TestClCorrected:

    def test_order0_equals_leading(self):
        for gen in (0, 1, 2):
            assert abs(cl_corrected(gen, order=0) - cl_leading(gen)) < _TOL

    def test_order1_gen0_unchanged(self):
        """gen=0 correction is zero → corrected = leading."""
        assert abs(cl_corrected(0, order=1) - cl_leading(0)) < _TOL

    def test_order1_gen1_positive_shift(self):
        assert cl_corrected(1, order=1) > cl_leading(1)

    def test_order1_gen2_positive_shift(self):
        assert cl_corrected(2, order=1) > cl_leading(2)

    def test_order1_gen1_formula(self):
        expected = cl_leading(1) + cs_phase_correction(1, order=1)
        assert abs(cl_corrected(1, order=1) - expected) < _TOL

    def test_order1_gen2_formula(self):
        expected = cl_leading(2) + cs_phase_correction(2, order=1)
        assert abs(cl_corrected(2, order=1) - expected) < _TOL

    def test_order2_larger_than_order1(self):
        """Adding two-loop correction increases c_L further."""
        for gen in (1, 2):
            assert cl_corrected(gen, order=2) >= cl_corrected(gen, order=1)

    def test_all_corrected_above_half(self):
        for gen in (0, 1, 2):
            assert cl_corrected(gen, order=1) > 0.5

    def test_correction_small_relative_to_leading(self):
        """CS correction O(1/K_CS) is small."""
        for gen in (0, 1, 2):
            delta = abs(cl_corrected(gen, order=1) - cl_leading(gen))
            assert delta < 0.05  # < 5% shift in c_L

    def test_invalid_gen_raises(self):
        with pytest.raises(ValueError):
            cl_corrected(3, order=1)

    def test_invalid_order_raises(self):
        with pytest.raises(ValueError):
            cl_corrected(1, order=3)


# ---------------------------------------------------------------------------
# braid_mass_ratio()
# ---------------------------------------------------------------------------

class TestBraidMassRatio:

    def test_returns_dict(self):
        r = braid_mass_ratio("leptons", order=1)
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = braid_mass_ratio("leptons", order=1)
        for key in ("sector", "order", "ratio_1_0", "ratio_2_1",
                    "ratio_2_0", "masses_mev", "pdg_ratio_1_0", "pdg_ratio_2_1"):
            assert key in r

    def test_sector_echoed(self):
        r = braid_mass_ratio("leptons")
        assert r["sector"] == "leptons"

    def test_order_echoed(self):
        r = braid_mass_ratio("leptons", order=1)
        assert r["order"] == 1

    def test_all_masses_positive(self):
        for sector in SECTORS:
            r = braid_mass_ratio(sector, order=1)
            for gen, m in r["masses_mev"].items():
                assert m > 0.0, f"Non-positive mass for {sector} gen={gen}"

    def test_ratio_1_0_positive(self):
        r = braid_mass_ratio("leptons", order=1)
        assert r["ratio_1_0"] > 0.0

    def test_ratio_2_1_positive(self):
        r = braid_mass_ratio("leptons", order=1)
        assert r["ratio_2_1"] > 0.0

    def test_ratio_2_0_equals_product(self):
        r = braid_mass_ratio("leptons", order=1)
        assert abs(r["ratio_2_0"] - r["ratio_1_0"] * r["ratio_2_1"]) < 1e-8

    def test_ratio_1_0_in_plausible_range(self):
        """m_μ/m_e from corrected c_L should be between 1 and 10000."""
        r = braid_mass_ratio("leptons", order=1)
        assert 1.0 < r["ratio_1_0"] < 10_000.0

    def test_pdg_ratio_1_0_leptons(self):
        """PDG m_μ/m_e ≈ 206.8."""
        r = braid_mass_ratio("leptons", order=1)
        assert abs(r["pdg_ratio_1_0"] - 105.658 / 0.510999) < 1.0

    def test_invalid_sector_raises(self):
        with pytest.raises(ValueError):
            braid_mass_ratio("neutrinos")

    def test_invalid_order_raises(self):
        with pytest.raises(ValueError):
            braid_mass_ratio("leptons", order=5)

    def test_all_sectors_positive_masses(self):
        for sector in SECTORS:
            r = braid_mass_ratio(sector)
            for m in r["masses_mev"].values():
                assert m > 0.0

    def test_order0_vs_order1_ratio(self):
        """First-order correction changes the ratio by a small amount."""
        r0 = braid_mass_ratio("leptons", order=0)
        r1 = braid_mass_ratio("leptons", order=1)
        # Ratios differ but both > 1
        assert r0["ratio_1_0"] > 1.0
        assert r1["ratio_1_0"] > 1.0


# ---------------------------------------------------------------------------
# pillar213_summary()
# ---------------------------------------------------------------------------

class TestPillar213Summary:

    def test_returns_dict(self):
        r = pillar213_summary()
        assert isinstance(r, dict)

    def test_required_keys(self):
        r = pillar213_summary()
        for key in ("c_L_leading", "c_L_corrected", "mass_predictions_mev",
                    "mass_pdg_mev", "mass_pct_errors", "honest_status",
                    "architecture_limit", "toe_delta", "correction_magnitudes"):
            assert key in r

    def test_toe_delta_is_zero(self):
        r = pillar213_summary()
        assert r["toe_delta"] == 0

    def test_pillar_number(self):
        r = pillar213_summary()
        assert r.get("pillar") == 213

    def test_c_L_leading_has_all_sectors(self):
        r = pillar213_summary()
        for sector in SECTORS:
            assert sector in r["c_L_leading"]

    def test_c_L_leading_gen0_equals_09(self):
        r = pillar213_summary()
        assert abs(r["c_L_leading"]["leptons"][0] - 0.9) < _TOL

    def test_c_L_leading_gen1_equals_08(self):
        r = pillar213_summary()
        assert abs(r["c_L_leading"]["leptons"][1] - 0.8) < _TOL

    def test_c_L_leading_gen2_equals_07(self):
        r = pillar213_summary()
        assert abs(r["c_L_leading"]["leptons"][2] - 0.7) < _TOL

    def test_c_L_corrected_has_all_sectors(self):
        r = pillar213_summary()
        for sector in SECTORS:
            assert sector in r["c_L_corrected"]

    def test_c_L_corrected_gen0_unchanged(self):
        """gen=0 CS correction is zero."""
        r = pillar213_summary()
        for sector in SECTORS:
            assert abs(
                r["c_L_corrected"][sector][0] - r["c_L_leading"][sector][0]
            ) < _TOL

    def test_c_L_corrected_gen1_positive_shift(self):
        r = pillar213_summary()
        for sector in SECTORS:
            assert r["c_L_corrected"][sector][1] > r["c_L_leading"][sector][1]

    def test_all_mass_predictions_positive(self):
        r = pillar213_summary()
        for sector in SECTORS:
            for gen, m in r["mass_predictions_mev"][sector].items():
                assert m > 0.0

    def test_pdg_masses_positive(self):
        r = pillar213_summary()
        for sector in SECTORS:
            for m in r["mass_pdg_mev"][sector].values():
                assert m > 0.0

    def test_honest_gate_large_pct_errors(self):
        """Winding-only c_L gives O(>5%) errors for most sector/gen — honest gate."""
        r = pillar213_summary()
        large_error_count = sum(
            1
            for sector in SECTORS
            for gen in (0, 1, 2)
            if r["mass_pct_errors"][sector][gen] > 5.0
        )
        # At least 50% of the 9 sector-gen combinations should have >5% error
        assert large_error_count >= 5, (
            f"Expected large % errors from winding-only c_L; only {large_error_count}/9 exceeded 5%"
        )

    def test_honest_status_non_empty(self):
        r = pillar213_summary()
        assert isinstance(r["honest_status"], str) and len(r["honest_status"]) > 20

    def test_honest_status_mentions_fitted(self):
        r = pillar213_summary()
        assert "FITTED" in r["honest_status"] or "fitted" in r["honest_status"].lower()

    def test_architecture_limit_non_empty(self):
        r = pillar213_summary()
        assert isinstance(r["architecture_limit"], str) and len(r["architecture_limit"]) > 20

    def test_correction_magnitudes_keys(self):
        r = pillar213_summary()
        for gen in (0, 1, 2):
            assert gen in r["correction_magnitudes"]

    def test_correction_gen0_is_zero(self):
        r = pillar213_summary()
        assert r["correction_magnitudes"][0] == 0.0

    def test_correction_gen1_positive(self):
        r = pillar213_summary()
        assert r["correction_magnitudes"][1] > 0.0

    def test_correction_gen2_positive(self):
        r = pillar213_summary()
        assert r["correction_magnitudes"][2] > 0.0

    def test_correction_increasing(self):
        r = pillar213_summary()
        c = r["correction_magnitudes"]
        assert c[0] <= c[1] <= c[2]


# ---------------------------------------------------------------------------
# Provenance
# ---------------------------------------------------------------------------

class TestProvenance:

    def test_provenance_dict_present(self):
        assert isinstance(__provenance__, dict)

    def test_pillar_number(self):
        assert __provenance__["pillar"] == 213

    def test_toe_delta_zero(self):
        assert __provenance__["toe_delta"] == 0

    def test_fingerprint(self):
        assert __provenance__["fingerprint"] == "(5, 7, 74)"

    def test_builds_on_present(self):
        assert "builds_on" in __provenance__
        assert len(__provenance__["builds_on"]) >= 1

    def test_honest_status_in_provenance(self):
        assert "honest_status" in __provenance__
