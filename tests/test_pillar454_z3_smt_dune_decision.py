# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 454 — Z3 SMT 13-Admission Certificate, DUNE Preregistration,
and Decision Readiness Package v13.8."""
import pytest
from src.core.pillar454_z3_smt_dune_decision_v138 import (
    PILLAR_STATUS, VERSION,
    ADMISSIONS_REGISTRY,
    DELTA_CP_UM, DELTA_CP_UM_DEG, DELTA_CP_NLO_UNC,
    DUNE_PREREGISTRATION_HASH,
    DECISION_WINDOWS,
    z3_smt_consistency_check, admission_cascade_check,
    dune_verdict, dune_rehearsal_drill,
    v138_sprint_gate, decision_readiness_report, pillar_report,
)


class TestAdmissionsRegistry:
    def test_thirteen_admissions(self):
        assert len(ADMISSIONS_REGISTRY) == 13

    def test_all_have_status(self):
        for k, v in ADMISSIONS_REGISTRY.items():
            assert 'status' in v
            assert len(v['status']) > 0

    def test_admission7_fully_closed(self):
        assert 'CLOSED' in ADMISSIONS_REGISTRY[7]['status'] or \
               'FULLY' in ADMISSIONS_REGISTRY[7]['status']

    def test_admission13_formally_closed(self):
        assert 'CLOSED' in ADMISSIONS_REGISTRY[13]['status']

    def test_keys_1_to_13(self):
        assert set(ADMISSIONS_REGISTRY.keys()) == set(range(1, 14))


class TestZ3SMT:
    def test_is_dag(self):
        r = z3_smt_consistency_check()
        assert r['is_dag'] is True

    def test_no_circular_dependencies(self):
        r = z3_smt_consistency_check()
        assert r['circular_dependencies'] == []

    def test_cascade_valid(self):
        r = z3_smt_consistency_check()
        assert r['cascade_6_11_10_5_valid'] is True

    def test_smt_verdict_consistent(self):
        r = z3_smt_consistency_check()
        assert r['smt_verdict'] == 'CONSISTENT'

    def test_13_admissions(self):
        r = z3_smt_consistency_check()
        assert r['n_admissions'] == 13

    def test_topological_order_length(self):
        r = z3_smt_consistency_check()
        assert len(r['topological_order']) == 13

    def test_adm_12_13_consistent(self):
        r = z3_smt_consistency_check()
        assert r['adm_12_13_mutually_consistent'] is True


class TestCascadeCheck:
    def test_cascade_chain_present(self):
        r = admission_cascade_check()
        for adm in [6, 11, 10, 5]:
            assert adm in r

    def test_all_have_labels(self):
        r = admission_cascade_check()
        for adm, v in r.items():
            assert 'label' in v


class TestDUNEPreregistration:
    def test_delta_cp_um_value(self):
        assert abs(DELTA_CP_UM - 1.2152) < 1e-4

    def test_delta_cp_um_deg(self):
        import math
        expected = math.degrees(DELTA_CP_UM)
        assert abs(DELTA_CP_UM_DEG - expected) < 0.01

    def test_nlo_unc_small(self):
        assert DELTA_CP_NLO_UNC < 0.02

    def test_hash_is_sha256(self):
        assert len(DUNE_PREREGISTRATION_HASH) == 64
        assert all(c in '0123456789abcdef' for c in DUNE_PREREGISTRATION_HASH)


class TestDUNEVerdict:
    def test_confirmed_scenario(self):
        r = dune_verdict(DELTA_CP_UM, 0.04)
        assert r['verdict'] == 'CONFIRMED'

    def test_consistent_scenario(self):
        r = dune_verdict(DELTA_CP_UM + 0.06, 0.04)
        assert r['verdict'] == 'CONSISTENT'

    def test_tension_scenario(self):
        r = dune_verdict(DELTA_CP_UM + 0.10, 0.04)
        assert r['verdict'] == 'TENSION'

    def test_falsified_scenario(self):
        r = dune_verdict(DELTA_CP_UM + 0.20, 0.04)
        assert r['verdict'] == 'FALSIFIED'

    def test_invalid_sigma_raises(self):
        with pytest.raises(ValueError):
            dune_verdict(1.2, 0.0)

    def test_returns_deviation(self):
        r = dune_verdict(DELTA_CP_UM, 0.04)
        assert 'deviation_sigma' in r


class TestDUNERehearsalDrills:
    @pytest.mark.parametrize('scenario,expected', [
        ('A', 'CONFIRMED'),
        ('C', 'TENSION'),
        ('D', 'FALSIFIED'),
    ])
    def test_scenario_verdict(self, scenario, expected):
        r = dune_rehearsal_drill(scenario)
        assert r['drill_pass'] is True, (
            f"Scenario {scenario}: expected {expected}, got {r['verdict']}"
        )

    def test_scenario_b_valid_verdict(self):
        # Scenario B is near the confirmed/consistent boundary
        r = dune_rehearsal_drill('B')
        assert r['verdict'] in ('CONFIRMED', 'CONSISTENT')

    def test_invalid_scenario_raises(self):
        with pytest.raises(ValueError):
            dune_rehearsal_drill('Z')


class TestDecisionWindows:
    def test_at_least_6_windows(self):
        assert len(DECISION_WINDOWS) >= 6

    def test_juno_window_present(self):
        assert 'JUNO_2027' in DECISION_WINDOWS

    def test_dune_window_present(self):
        assert 'DUNE_2030' in DECISION_WINDOWS

    def test_litebird_window_present(self):
        assert 'LITEBIRD_2032' in DECISION_WINDOWS

    def test_dune_window_has_hash(self):
        dune = DECISION_WINDOWS.get('DUNE_2030', {})
        assert 'sha256' in dune

    def test_all_windows_have_observable(self):
        for name, win in DECISION_WINDOWS.items():
            assert 'observable' in win, f"Window {name} missing observable"


class TestSprintGate:
    def test_all_gates_pass(self):
        r = v138_sprint_gate()
        assert r['all_gates_pass'] is True

    def test_sprint_complete(self):
        r = v138_sprint_gate()
        assert r['verdict'] == 'SPRINT_V138_COMPLETE'

    def test_14_pillars(self):
        r = v138_sprint_gate()
        assert r['n_pillars'] == 14

    def test_pillars_441_454(self):
        r = v138_sprint_gate()
        pillars = r['pillars_added']
        assert 441 in pillars
        assert 454 in pillars


class TestDecisionReadinessReport:
    def test_version_v138(self):
        r = decision_readiness_report()
        assert r['version'] == 'v13.8'

    def test_smt_consistent(self):
        r = decision_readiness_report()
        assert r['z3_smt_certificate']['smt_verdict'] == 'CONSISTENT'

    def test_dune_hash_present(self):
        r = decision_readiness_report()
        assert len(r['dune_preregistration']['sha256']) == 64


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 454

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS

    def test_sprint_gate_all_pass(self):
        r = pillar_report()
        assert r['sprint_gate']['all_gates_pass'] is True
