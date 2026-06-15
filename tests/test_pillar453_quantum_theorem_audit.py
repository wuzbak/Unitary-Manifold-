# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 453 — Quantum Theorem Proof Audit."""
import pytest
from src.core.pillar453_quantum_theorem_audit import (
    PILLAR_STATUS, VERSION, THEOREM_AUDIT,
    audit_bh_information, audit_ccr, audit_hawking_temperature, audit_er_epr,
    run_full_audit, derivation_status_update, pillar_report,
)


class TestTheoremAuditRegistry:
    def test_four_theorems_registered(self):
        assert len(THEOREM_AUDIT) == 4

    def test_theorem_keys_present(self):
        expected = {
            'bh_information_unitarity', 'ccr_from_um_geometry',
            'hawking_temperature_ftum', 'er_epr_holographic',
        }
        assert set(THEOREM_AUDIT.keys()) == expected

    def test_all_had_prior_proved_label(self):
        for key, val in THEOREM_AUDIT.items():
            assert val['prior_label'] == 'PROVED', f"{key}: prior_label should be PROVED"

    def test_all_have_new_labels(self):
        for key, val in THEOREM_AUDIT.items():
            assert val['new_label'] in ('PROVED', 'DERIVED', 'DERIVED_CONDITIONAL', 'CONJECTURAL')


class TestBHInformationAudit:
    def test_label_downgraded(self):
        r = audit_bh_information()
        assert r['epistemic_label'] == 'DERIVED_CONDITIONAL'

    def test_prior_label_proved(self):
        r = audit_bh_information()
        assert r['prior_label'] == 'PROVED'

    def test_has_hidden_assumption(self):
        r = audit_bh_information()
        assert r['has_gap'] is True
        assert r['hidden_assumption'] is not None

    def test_premises_present(self):
        r = audit_bh_information()
        assert len(r['premises']) >= 2

    def test_steps_justified(self):
        r = audit_bh_information()
        assert r['steps_justified'] is True

    def test_grade_downgrade(self):
        r = audit_bh_information()
        assert r['grade'] == 'DOWNGRADE'


class TestCCRAudit:
    def test_label_conjectural(self):
        r = audit_ccr()
        assert r['epistemic_label'] == 'CONJECTURAL'

    def test_prior_label_proved(self):
        r = audit_ccr()
        assert r['prior_label'] == 'PROVED'

    def test_has_gap(self):
        r = audit_ccr()
        assert r['has_gap'] is True

    def test_grade_downgrade(self):
        r = audit_ccr()
        assert r['grade'] == 'DOWNGRADE'


class TestHawkingTAudit:
    def test_label_derived(self):
        r = audit_hawking_temperature()
        assert r['epistemic_label'] == 'DERIVED'

    def test_prior_label_proved(self):
        r = audit_hawking_temperature()
        assert r['prior_label'] == 'PROVED'

    def test_maintained_not_downgraded(self):
        r = audit_hawking_temperature()
        assert 'MAINTAINED' in r['grade']

    def test_has_kms_step(self):
        r = audit_hawking_temperature()
        steps_text = ' '.join(r['proof_steps'])
        assert 'KMS' in steps_text or 'kms' in steps_text.lower()


class TestERPEPRAudit:
    def test_label_conjectural(self):
        r = audit_er_epr()
        assert r['epistemic_label'] == 'CONJECTURAL'

    def test_prior_label_proved(self):
        r = audit_er_epr()
        assert r['prior_label'] == 'PROVED'

    def test_rt_assumption_identified(self):
        r = audit_er_epr()
        assert r['hidden_assumption'] is not None
        assert 'RT' in r['hidden_assumption'] or 'Ryu' in r['hidden_assumption']

    def test_grade_downgrade(self):
        r = audit_er_epr()
        assert r['grade'] == 'DOWNGRADE'


class TestFullAudit:
    def test_four_theorems(self):
        r = run_full_audit()
        assert r['theorems_audited'] == 4

    def test_one_derived_theorem(self):
        r = run_full_audit()
        assert r['new_derived_count'] == 1

    def test_one_derived_conditional(self):
        r = run_full_audit()
        assert r['new_derived_conditional_count'] == 1

    def test_two_conjectural(self):
        r = run_full_audit()
        assert r['new_conjectural_count'] == 2

    def test_zero_proved_after_audit(self):
        r = run_full_audit()
        assert r['new_proved_count'] == 0

    def test_two_downgrades(self):
        r = run_full_audit()
        assert len(r['downgrades']) >= 2

    def test_honest_rationale_present(self):
        r = run_full_audit()
        assert 'honest' in r['honest_downgrade_rationale'].lower()


class TestDerivationStatusUpdate:
    def test_all_four_keys_present(self):
        r = derivation_status_update()
        assert 'QUANTUM_BH_INFORMATION' in r
        assert 'QUANTUM_CCR' in r
        assert 'QUANTUM_HAWKING_T' in r
        assert 'QUANTUM_ER_EPR' in r

    def test_hawking_maintained(self):
        r = derivation_status_update()
        assert 'DERIVED' in r['QUANTUM_HAWKING_T']


class TestPillarReport:
    def test_pillar_number(self):
        r = pillar_report()
        assert r['pillar'] == 453

    def test_status(self):
        r = pillar_report()
        assert r['status'] == PILLAR_STATUS

    def test_label_upgrades_present(self):
        r = pillar_report()
        assert 'QUANTUM_THEOREMS' in r['label_upgrades']
