# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 797 — DESI_DR2_WA_FALSIFICATION_AUDIT
~50 tests covering dataset-dependent verdict, tension computation,
loop QKK alternative, and honest summary.
"""
import pytest
from src.core.pillar797_desi_dr2_wa_falsification_audit import (
    W0_UM,
    WA_UM,
    KILL_THRESHOLD_SIGMA,
    TENSION_THRESHOLD_SIGMA,
    DESI_DR2_BAO_ONLY,
    DESI_DR2_BAO_PANTHEON_PLUS,
    DESI_DR2_BAO_UNION3,
    DESI_DR2_BAO_DESY5,
    ACT_DR6_WA,
    PILLAR_797_GATE,
    compute_tension,
    route_dataset,
    full_audit,
    loop_qkk_wa_effective,
    pillar797_summary,
    PILLAR_797_SUMMARY,
)


class TestConstants:
    def test_gate(self):
        assert PILLAR_797_GATE == "DESI_DR2_DATASET_DEPENDENT"

    def test_um_wa_zero(self):
        assert WA_UM == 0.0

    def test_um_w0_minus_one(self):
        assert W0_UM == -1.0

    def test_kill_threshold(self):
        assert KILL_THRESHOLD_SIGMA == 3.0

    def test_tension_threshold(self):
        assert TENSION_THRESHOLD_SIGMA == 2.0


class TestTensionComputation:
    def test_bao_only_tension_keys(self):
        t = compute_tension(DESI_DR2_BAO_ONLY)
        assert 'tension_wa_sigma' in t
        assert 'tension_w0_sigma' in t
        assert 'combined_sigma' in t

    def test_bao_only_wa_tension_positive(self):
        t = compute_tension(DESI_DR2_BAO_ONLY)
        assert t['tension_wa_sigma'] > 0.0

    def test_bao_only_wa_below_kill(self):
        t = compute_tension(DESI_DR2_BAO_ONLY)
        assert t['tension_wa_sigma'] < KILL_THRESHOLD_SIGMA

    def test_desy5_wa_tension_above_kill(self):
        t = compute_tension(DESI_DR2_BAO_DESY5)
        assert t['tension_wa_sigma'] > KILL_THRESHOLD_SIGMA

    def test_act_dr6_wa_near_zero(self):
        t = compute_tension(ACT_DR6_WA)
        assert t['tension_wa_sigma'] < 1.0   # consistent with wₐ=0

    def test_um_wa_tension_zero_when_perfect(self):
        ds = {'wa': 0.0, 'sigma_wa': 0.3, 'w0': -1.0, 'sigma_w0': 0.1,
               'dataset': 'test', 'reference': ''}
        t = compute_tension(ds)
        assert t['tension_wa_sigma'] == 0.0

    def test_combined_sigma_gte_individual(self):
        t = compute_tension(DESI_DR2_BAO_DESY5)
        assert t['combined_sigma'] >= t['tension_wa_sigma']
        assert t['combined_sigma'] >= t['tension_w0_sigma']

    def test_dataset_key_preserved(self):
        t = compute_tension(DESI_DR2_BAO_ONLY)
        assert t['dataset'] == 'DESI_DR2_BAO_ONLY'


class TestRouting:
    def test_bao_only_below_kill(self):
        t = compute_tension(DESI_DR2_BAO_ONLY)
        v = route_dataset(t)
        assert v in ('TENSION', 'PASS')

    def test_pantheon_below_kill(self):
        t = compute_tension(DESI_DR2_BAO_PANTHEON_PLUS)
        v = route_dataset(t)
        assert v in ('TENSION', 'PASS')

    def test_desy5_falsified_candidate(self):
        t = compute_tension(DESI_DR2_BAO_DESY5)
        v = route_dataset(t)
        assert v == 'FALSIFIED_CANDIDATE'

    def test_act_dr6_pass(self):
        t = compute_tension(ACT_DR6_WA)
        v = route_dataset(t)
        assert v == 'PASS'

    def test_pass_below_tension_threshold(self):
        t = {'tension_wa_sigma': 1.5, 'tension_w0_sigma': 0.5,
             'dataset': 'test', 'wa_obs': -0.4, 'sigma_wa': 0.5,
             'w0_obs': -0.95, 'sigma_w0': 0.1, 'reference': ''}
        assert route_dataset(t) == 'PASS'


class TestFullAudit:
    def test_overall_gate_dataset_dependent(self):
        a = full_audit()
        assert a['overall_gate'] == PILLAR_797_GATE

    def test_some_falsified(self):
        a = full_audit()
        assert a['n_falsified_candidate'] > 0

    def test_some_pass_or_tension(self):
        a = full_audit()
        assert a['n_pass'] + a['n_tension'] > 0

    def test_per_dataset_keys(self):
        a = full_audit()
        assert 'DESI_DR2_BAO_ONLY' in a['per_dataset']
        assert 'DESI_DR2_BAO_DESY5' in a['per_dataset']
        assert 'ACT_DR6_CMB' in a['per_dataset']

    def test_per_dataset_verdicts_present(self):
        a = full_audit()
        for k, v in a['per_dataset'].items():
            assert 'verdict' in v, f"No verdict for {k}"

    def test_desy5_falsified(self):
        a = full_audit()
        assert 'FALSIFIED' in a['per_dataset']['DESI_DR2_BAO_DESY5']['verdict']

    def test_act_passes(self):
        a = full_audit()
        assert a['per_dataset']['ACT_DR6_CMB']['verdict'] == 'PASS'


class TestLoopQKK:
    def test_loop_wa_nonzero(self):
        r = loop_qkk_wa_effective()
        assert r['fundamental_wa'] == 0.0
        assert r['wa_effective_lqk'] != 0.0

    def test_loop_wa_negative(self):
        r = loop_qkk_wa_effective()
        assert r['wa_effective_lqk'] < 0.0

    def test_loop_wa_smaller_than_desy5(self):
        r = loop_qkk_wa_effective()
        assert abs(r['wa_effective_lqk']) < abs(DESI_DR2_BAO_DESY5['wa'])

    def test_status_hypothesis(self):
        r = loop_qkk_wa_effective()
        assert 'HYPOTHESIS' in r['status']

    def test_reference_present(self):
        r = loop_qkk_wa_effective()
        assert '2508.07962' in r['reference']

    def test_interpretation_present(self):
        r = loop_qkk_wa_effective()
        assert len(r['interpretation']) > 50


class TestSummary:
    def test_summary_pillar(self):
        s = pillar797_summary()
        assert s['pillar'] == 797

    def test_summary_gate(self):
        s = pillar797_summary()
        assert s['gate'] == PILLAR_797_GATE

    def test_summary_um_prediction(self):
        s = pillar797_summary()
        assert s['um_prediction']['wa'] == 0.0

    def test_summary_has_honest(self):
        s = pillar797_summary()
        assert 'honest_summary' in s

    def test_summary_honest_mentions_dataset_dependence(self):
        s = pillar797_summary()
        assert 'DATASET' in s['honest_summary'].upper()

    def test_summary_counterweight(self):
        s = pillar797_summary()
        assert 'counterweight' in s
        assert 'ACT' in s['counterweight']['experiment']

    def test_summary_alias(self):
        s = PILLAR_797_SUMMARY()
        assert s['pillar'] == 797

    def test_epistemic_status_key(self):
        s = pillar797_summary()
        assert 'epistemic_status' in s
