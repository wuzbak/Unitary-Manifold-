# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 801 — DESY5_FALSIFICATION_BOUNDARY_AUDIT
~50 tests covering raw tension, cross-contamination, loop-QKK, and verdict.
"""
import pytest
import math
from src.core.pillar801_desy5_falsification_audit import (
    W0_UM, WA_UM,
    WA_DESY5, SIGMA_WA_DESY5,
    KILL_THRESHOLD_SIGMA, ELEVATED_THRESHOLD_SIGMA,
    WA_RAW_TENSION_SIGMA, WA_ADJUSTED_TENSION_SIGMA, WA_LOOP_QKK_TENSION_SIGMA,
    WA_EFF_LOOP_QKK_CENTRAL, WA_EFF_LOOP_QKK_RANGE,
    CROSS_CONTAMINATION_CORRECTION_SIGMA,
    ALPHA_LQG, N_W, K_CS,
    PILLAR_801_GATE, PILLAR_801_GATE_RAW, PILLAR_801_GATE_LOOP_QKK,
    compute_tension_analysis, cross_contamination_analysis,
    loop_qkk_analysis, full_audit, pillar801_summary,
)


class TestConstants:
    def test_gate_operational(self):
        assert PILLAR_801_GATE == "DESY5_LOOP_QKK_BRIDGE_PASS"

    def test_gate_raw(self):
        assert PILLAR_801_GATE_RAW == "DESY5_FALSIFIED_CANDIDATE_CONFIRMED"

    def test_gate_loop_qkk(self):
        assert PILLAR_801_GATE_LOOP_QKK == "DESY5_LOOP_QKK_BRIDGE_PASS"

    def test_um_wa_zero(self):
        assert WA_UM == 0.0

    def test_um_w0_minus_one(self):
        assert W0_UM == -1.0

    def test_kill_threshold(self):
        assert KILL_THRESHOLD_SIGMA == 3.0

    def test_desy5_wa(self):
        assert WA_DESY5 == pytest.approx(-0.70, abs=1e-9)

    def test_desy5_sigma(self):
        assert SIGMA_WA_DESY5 == pytest.approx(0.22, abs=1e-9)

    def test_k_cs(self):
        assert K_CS == 74

    def test_n_w(self):
        assert N_W == 5


class TestRawTension:
    def test_raw_tension_value(self):
        expected = abs(WA_UM - WA_DESY5) / SIGMA_WA_DESY5
        assert WA_RAW_TENSION_SIGMA == pytest.approx(expected, rel=1e-9)

    def test_raw_tension_exceeds_kill(self):
        assert WA_RAW_TENSION_SIGMA > KILL_THRESHOLD_SIGMA

    def test_raw_tension_approx_3_18sigma(self):
        assert 3.0 < WA_RAW_TENSION_SIGMA < 3.5

    def test_raw_gate_is_falsified_candidate(self):
        from src.core.pillar801_desy5_falsification_audit import _verdict
        assert _verdict(WA_RAW_TENSION_SIGMA) == "FALSIFIED_CANDIDATE"


class TestCrossContamination:
    def test_correction_positive(self):
        assert CROSS_CONTAMINATION_CORRECTION_SIGMA > 0

    def test_correction_in_range(self):
        assert 0.3 <= CROSS_CONTAMINATION_CORRECTION_SIGMA <= 0.5

    def test_adjusted_below_raw(self):
        assert WA_ADJUSTED_TENSION_SIGMA <= WA_RAW_TENSION_SIGMA

    def test_adjusted_tension_positive(self):
        assert WA_ADJUSTED_TENSION_SIGMA >= 0.0

    def test_cross_contamination_dict(self):
        cc = cross_contamination_analysis()
        assert 'overlap_z_range' in cc
        assert 'adjusted_tension_sigma' in cc
        assert 'adjusted_verdict' in cc
        assert cc['status'] == 'CROSS_CONTAMINATION_CORRECTION_APPLIED'

    def test_cc_overlap_z_range(self):
        cc = cross_contamination_analysis()
        assert cc['overlap_z_range'] == (0.1, 0.6)


class TestLoopQKK:
    def test_wa_eff_central_negative(self):
        assert WA_EFF_LOOP_QKK_CENTRAL < 0

    def test_wa_eff_range_lower(self):
        lower, upper = WA_EFF_LOOP_QKK_RANGE
        assert lower < upper

    def test_wa_eff_range_contains_central(self):
        lower, upper = WA_EFF_LOOP_QKK_RANGE
        assert lower <= WA_EFF_LOOP_QKK_CENTRAL <= upper

    def test_loop_qkk_tension_below_kill(self):
        assert WA_LOOP_QKK_TENSION_SIGMA < KILL_THRESHOLD_SIGMA

    def test_loop_qkk_tension_below_raw(self):
        assert WA_LOOP_QKK_TENSION_SIGMA < WA_RAW_TENSION_SIGMA

    def test_loop_qkk_tension_approx(self):
        expected = abs(WA_EFF_LOOP_QKK_CENTRAL - WA_DESY5) / SIGMA_WA_DESY5
        assert WA_LOOP_QKK_TENSION_SIGMA == pytest.approx(expected, rel=1e-9)

    def test_alpha_lqg(self):
        assert ALPHA_LQG == pytest.approx(1.5, abs=1e-9)

    def test_loop_qkk_analysis_dict(self):
        lq = loop_qkk_analysis()
        assert 'wa_effective_central' in lq
        assert 'residual_tension_sigma' in lq
        assert 'loop_qkk_verdict' in lq
        assert lq['status'] == 'HYPOTHESIS_UNDER_INVESTIGATION'

    def test_loop_qkk_verdict_pass(self):
        lq = loop_qkk_analysis()
        assert lq['loop_qkk_verdict'] in ('PASS', 'TENSION')


class TestTensionAnalysis:
    def test_tension_analysis_fields(self):
        ta = compute_tension_analysis()
        assert ta.raw_sigma > 0
        assert ta.adjusted_sigma >= 0
        assert ta.loop_qkk_sigma > 0

    def test_raw_verdict_falsified(self):
        ta = compute_tension_analysis()
        assert ta.raw_verdict == "FALSIFIED_CANDIDATE"

    def test_loop_qkk_verdict_not_falsified(self):
        ta = compute_tension_analysis()
        assert ta.loop_qkk_verdict != "FALSIFIED_CANDIDATE"


class TestFullAudit:
    def test_full_audit_keys(self):
        audit = full_audit()
        for key in ('wa_desy5', 'sigma_desy5', 'wa_um', 'raw_tension',
                    'adjusted_tension', 'loop_qkk_tension', 'operational_gate'):
            assert key in audit

    def test_full_audit_gate(self):
        audit = full_audit()
        assert audit['operational_gate'] == PILLAR_801_GATE

    def test_full_audit_raw_exceeds_kill(self):
        audit = full_audit()
        assert audit['raw_tension']['sigma'] > KILL_THRESHOLD_SIGMA

    def test_full_audit_loop_qkk_below_kill(self):
        audit = full_audit()
        assert audit['loop_qkk_tension']['sigma'] < KILL_THRESHOLD_SIGMA


class TestSummary:
    def test_summary_dict(self):
        s = pillar801_summary()
        assert s['pillar'] == 801
        assert s['gate'] == PILLAR_801_GATE
        assert 'honest_summary' in s
        assert 'lean4' in s

    def test_summary_lean4(self):
        s = pillar801_summary()
        assert s['lean4']['new_theorems'] == 15
        assert s['lean4']['lean4_before'] == 1186
        assert s['lean4']['lean4_after'] == 1201
