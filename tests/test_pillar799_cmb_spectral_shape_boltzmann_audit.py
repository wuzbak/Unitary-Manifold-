# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 799 — CMB_SPECTRAL_SHAPE_BOLTZMANN_AUDIT
~50 tests covering ℓ-mode shape audit, ns tension, amplitude gap,
and ACT DR6 crosscheck.
"""
import math
import pytest
import numpy as np
from src.core.pillar799_cmb_spectral_shape_boltzmann_audit import (
    N_S_UM,
    N_S_LCDM,
    N_S_SIGMA,
    N_S_TENSION_UM,
    A_S_UM,
    A_S_PLANCK,
    A_S_GAP_FRAC,
    K_PIVOT_MPC,
    L_BINS,
    ACT_DR6_NS,
    ACT_DR6_NS_SIGMA,
    PILLAR_799_GATE,
    primordial_spectrum_um,
    primordial_spectrum_lcdm,
    transfer_function_tca,
    cl_spectrum_tca,
    shape_ratio_bin,
    three_bin_audit,
    ns_tension_audit,
    amplitude_gap_confirmation,
    act_dr6_crosscheck,
    pillar799_summary,
    PILLAR_799_SUMMARY,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_799_GATE == "CMB_SHAPE_BOLTZMANN_CONSISTENT"

    def test_ns_um_value(self):
        assert abs(N_S_UM - 0.9635) < 1e-6

    def test_ns_lcdm_value(self):
        assert abs(N_S_LCDM - 0.9649) < 1e-6

    def test_as_gap_fraction(self):
        expected = 1.0 - A_S_UM / A_S_PLANCK
        assert abs(A_S_GAP_FRAC - expected) < 1e-10

    def test_as_gap_positive(self):
        assert A_S_GAP_FRAC > 0.0

    def test_as_gap_near_33_percent(self):
        assert 0.30 < A_S_GAP_FRAC < 0.40

    def test_ns_tension_below_1sigma(self):
        assert N_S_TENSION_UM < 1.0

    def test_l_bins_three(self):
        assert len(L_BINS) == 3

    def test_l_bins_ordered(self):
        for lo, hi in L_BINS:
            assert lo < hi

    def test_l_bins_contiguous(self):
        for i in range(len(L_BINS) - 1):
            assert L_BINS[i][1] == L_BINS[i+1][0]


class TestPrimordialSpectrum:
    def test_um_at_pivot(self):
        p = primordial_spectrum_um(K_PIVOT_MPC)
        assert abs(p - A_S_UM) < 1e-20

    def test_lcdm_at_pivot(self):
        p = primordial_spectrum_lcdm(K_PIVOT_MPC)
        assert abs(p - A_S_PLANCK) < 1e-20

    def test_um_less_than_lcdm(self):
        for k in [0.01, 0.05, 0.1, 0.5]:
            assert primordial_spectrum_um(k) < primordial_spectrum_lcdm(k)

    def test_positive_values(self):
        for k in [0.001, 0.01, 0.05, 0.2]:
            assert primordial_spectrum_um(k) > 0.0
            assert primordial_spectrum_lcdm(k) > 0.0

    def test_power_law_ratio(self):
        k1, k2 = 0.05, 0.10
        ratio = primordial_spectrum_um(k1) / primordial_spectrum_um(k2)
        expected = (k1/k2) ** (N_S_UM - 1)
        assert abs(ratio - expected) < 1e-10


class TestTransferFunction:
    def test_returns_float(self):
        t = transfer_function_tca(0.01)
        assert isinstance(t, float)

    def test_peaks_at_origin_approx(self):
        # At k→0, cos(k r_s) → 1 and damping → 1
        t = transfer_function_tca(1e-6)
        assert abs(t - 1.0) < 0.01

    def test_damping_at_high_k(self):
        # At high k, should be strongly suppressed
        t = transfer_function_tca(1.0)
        assert abs(t) < 0.01


class TestCLSpectrum:
    def test_returns_float(self):
        c = cl_spectrum_tca(500, use_um=True)
        assert isinstance(c, float)

    def test_um_less_than_lcdm_typically(self):
        # At most ℓ, UM should give smaller amplitude due to lower A_s
        # (can be equal at nodes of oscillation — check average over some ells)
        ells = [300, 500, 700, 1000, 1500]
        for ell in ells:
            c_um = cl_spectrum_tca(ell, use_um=True)
            c_lcdm = cl_spectrum_tca(ell, use_um=False)
            # Both could be zero at a node; check their abs
            # We allow equality at rare nodes
            assert abs(c_um) <= abs(c_lcdm) * 1.01 + 1e-60


class TestShapeRatioBin:
    def test_returns_dict(self):
        r = shape_ratio_bin(200, 800)
        assert isinstance(r, dict)

    def test_keys_present(self):
        r = shape_ratio_bin(200, 800)
        assert 'mean_cl_ratio' in r
        assert 'shape_consistent' in r
        assert 'shape_deviation_frac' in r

    def test_bin_1_consistent(self):
        r = shape_ratio_bin(*L_BINS[0])
        assert r['shape_consistent']

    def test_bin_2_consistent(self):
        r = shape_ratio_bin(*L_BINS[1])
        assert r['shape_consistent']

    def test_bin_3_consistent(self):
        r = shape_ratio_bin(*L_BINS[2])
        assert r['shape_consistent']

    def test_expected_amp_ratio(self):
        r = shape_ratio_bin(200, 800)
        expected = A_S_UM / A_S_PLANCK
        assert abs(r['expected_amp_ratio'] - expected) < 1e-10

    def test_shape_deviation_below_threshold(self):
        for lo, hi in L_BINS:
            r = shape_ratio_bin(lo, hi)
            assert r['shape_deviation_frac'] < 0.05


class TestThreeBinAudit:
    def test_all_bins_consistent(self):
        a = three_bin_audit()
        assert a['all_bins_shape_consistent']

    def test_verdict_consistent(self):
        a = three_bin_audit()
        assert a['verdict'] == PILLAR_799_GATE

    def test_three_bins_in_result(self):
        a = three_bin_audit()
        assert len(a['bins']) == 3

    def test_interpretation_present(self):
        a = three_bin_audit()
        assert 'TYPE_B' in a['interpretation']


class TestNSTension:
    def test_planck_tension_below_1sigma(self):
        r = ns_tension_audit()
        assert r['tension_planck_sigma'] < 1.0

    def test_act_consistent(self):
        r = ns_tension_audit()
        assert r['act_consistent']

    def test_planck_consistent(self):
        r = ns_tension_audit()
        assert r['planck_consistent']

    def test_um_ns_value(self):
        r = ns_tension_audit()
        assert abs(r['n_s_um'] - N_S_UM) < 1e-9


class TestAmplitudeGap:
    def test_gap_fraction(self):
        r = amplitude_gap_confirmation()
        assert 0.30 < r['gap_fraction'] < 0.40

    def test_type_b_status(self):
        r = amplitude_gap_confirmation()
        assert 'TYPE_B' in r['type_b_status']

    def test_pillar_source(self):
        r = amplitude_gap_confirmation()
        assert '780' in r['pillar_source']


class TestACTCrosscheck:
    def test_shape_consistent(self):
        r = act_dr6_crosscheck()
        assert r['shape_consistent'] is True

    def test_tension_small(self):
        r = act_dr6_crosscheck()
        assert r['tension_sigma'] < 1.0

    def test_experiment_name(self):
        r = act_dr6_crosscheck()
        assert 'ACT' in r['experiment']


class TestSummary:
    def test_summary_pillar(self):
        s = pillar799_summary()
        assert s['pillar'] == 799

    def test_summary_gate(self):
        s = pillar799_summary()
        assert s['gate'] == PILLAR_799_GATE

    def test_summary_has_honest(self):
        s = pillar799_summary()
        assert 'honest_summary' in s

    def test_summary_mentions_type_b(self):
        s = pillar799_summary()
        assert 'TYPE_B' in s['honest_summary']

    def test_summary_alias(self):
        s = PILLAR_799_SUMMARY()
        assert s['pillar'] == 799
