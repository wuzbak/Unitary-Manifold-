# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 432 — 6D UV Completion Baryogenesis Scoping."""
from __future__ import annotations

import math
import pytest

from src.core.pillar432_sixd_baryogenesis_scope import (
    PILLAR_STATUS,
    ADJACENCY_TRACK_LABEL,
    N_W,
    K_CS,
    PHI_STAR,
    C_S,
    PI_KR,
    M_KK_TEV,
    T_EW_GEV,
    ETA_B_OBSERVED,
    ETA_B_5D_BEST,
    M_6D_TEV,
    M_SIGMA_GEV,
    six_d_field_content,
    um_constraints_on_6d,
    baryogenesis_mechanism_6d,
    sixd_eta_b_estimate,
    discriminating_observables,
    sixd_baryogenesis_scope_report,
)


class TestConstants:
    def test_pillar_status(self):
        assert PILLAR_STATUS == 'SIXD_BARYOGENESIS_EXTENSION_SCOPED'

    def test_adjacency_label(self):
        assert '🔵' in ADJACENCY_TRACK_LABEL
        assert 'ADJACENT TRACK' in ADJACENCY_TRACK_LABEL

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_phi_star(self):
        assert abs(PHI_STAR - 2.0 * math.pi * N_W) < 1e-10

    def test_c_s(self):
        assert abs(C_S - 12.0 / 37.0) < 1e-12

    def test_pi_kr(self):
        assert PI_KR == 37

    def test_m_kk_tev(self):
        assert M_KK_TEV == pytest.approx(1.04, rel=0.01)

    def test_t_ew_gev(self):
        assert T_EW_GEV == pytest.approx(100.0, rel=0.01)

    def test_eta_b_observed(self):
        assert ETA_B_OBSERVED == pytest.approx(6.1e-10, rel=0.01)

    def test_eta_b_5d_best_less_than_observed(self):
        assert ETA_B_5D_BEST < ETA_B_OBSERVED

    def test_m_6d_tev_positive(self):
        assert M_6D_TEV > 0.0

    def test_m_sigma_gev_in_range(self):
        # Should be O(100) – O(1000) GeV
        assert 100.0 < M_SIGMA_GEV < 5000.0


class TestSixDFieldContent:
    def setup_method(self):
        self.fc = six_d_field_content()

    def test_returns_dict(self):
        assert isinstance(self.fc, dict)

    def test_required_keys(self):
        for key in ['new_field', 'dimensions', 'quantum_numbers', 'spin',
                    'mass_range_GeV', 'role', 'cp_source', 'n_new_free_parameters']:
            assert key in self.fc

    def test_new_field_name(self):
        assert 'Σ' in self.fc['new_field']

    def test_six_dimensions(self):
        assert '6D' in self.fc['dimensions']

    def test_baryon_number_one(self):
        qn = self.fc['quantum_numbers']
        assert qn['U1_B'] == 1

    def test_spin_zero(self):
        assert self.fc['spin'] == 0

    def test_mass_range_reasonable(self):
        lo, hi = self.fc['mass_range_GeV']
        assert lo > 0 and hi > lo and hi < 10000

    def test_cp_source_mentioned(self):
        assert 'CP' in self.fc['cp_source'] or 'Levi-Civita' in self.fc['cp_source']

    def test_n_new_parameters_small(self):
        # Minimal extension should have ≤ 3 new parameters
        assert self.fc['n_new_free_parameters'] <= 3


class TestUmConstraintsOn6d:
    def setup_method(self):
        self.constraints = um_constraints_on_6d()

    def test_returns_list(self):
        assert isinstance(self.constraints, list)

    def test_three_constraints(self):
        assert len(self.constraints) == 3

    def test_labels_c1_c2_c3(self):
        labels = {c['label'] for c in self.constraints}
        assert labels == {'C1', 'C2', 'C3'}

    def test_each_has_required_keys(self):
        for c in self.constraints:
            assert 'label' in c
            assert 'name' in c
            assert 'constraint' in c
            assert 'UM_inputs' in c

    def test_c1_uses_n_w_k_cs(self):
        c1 = next(c for c in self.constraints if c['label'] == 'C1')
        inputs_str = str(c1['UM_inputs'])
        assert 'n_w' in inputs_str or '5' in inputs_str

    def test_c2_uses_phi0(self):
        c2 = next(c for c in self.constraints if c['label'] == 'C2')
        inputs_str = str(c2['UM_inputs'])
        assert 'φ₀' in inputs_str or 'phi' in inputs_str.lower()

    def test_c3_uses_c_s(self):
        c3 = next(c for c in self.constraints if c['label'] == 'C3')
        inputs_str = str(c3['UM_inputs'])
        assert 'c_s' in inputs_str or '12/37' in inputs_str


class TestBaryogenesisMechanism6d:
    def setup_method(self):
        self.mech = baryogenesis_mechanism_6d()

    def test_returns_dict(self):
        assert isinstance(self.mech, dict)

    def test_required_keys(self):
        assert 'steps' in self.mech
        assert 'sakharov_conditions' in self.mech

    def test_four_steps(self):
        assert len(self.mech['steps']) == 4

    def test_steps_numbered(self):
        step_nums = {s['step'] for s in self.mech['steps']}
        assert step_nums == {1, 2, 3, 4}

    def test_sakharov_conditions_present(self):
        sk = self.mech['sakharov_conditions']
        assert 'baryon_number_violation' in sk
        assert 'cp_violation' in sk
        assert 'out_of_equilibrium' in sk

    def test_all_sakharov_conditions_satisfied(self):
        sk = self.mech['sakharov_conditions']
        for key, val in sk.items():
            assert '✅' in val, f"Sakharov condition {key} not marked satisfied"

    def test_each_step_has_temperature_and_process(self):
        for step in self.mech['steps']:
            assert 'T' in step
            assert 'process' in step


class TestSixdEtaBEstimate:
    def setup_method(self):
        self.eta = sixd_eta_b_estimate()

    def test_returns_dict(self):
        assert isinstance(self.eta, dict)

    def test_required_keys(self):
        for key in ['eta_b_6d', 'eta_b_observed', 'eta_b_5d_best',
                    'ratio_to_observed', 'improvement_over_5d', 'within_order_of_magnitude']:
            assert key in self.eta

    def test_eta_b_6d_positive(self):
        assert self.eta['eta_b_6d'] > 0.0

    def test_eta_b_6d_larger_than_5d(self):
        assert self.eta['eta_b_6d'] > ETA_B_5D_BEST

    def test_improvement_factor_greater_than_one(self):
        assert self.eta['improvement_over_5d'] > 1.0

    def test_ratio_to_observed_positive(self):
        assert self.eta['ratio_to_observed'] > 0.0

    def test_note_present(self):
        assert len(self.eta['note']) > 0

    def test_theta_6_assumed(self):
        assert 'theta_6_assumed' in self.eta
        assert self.eta['theta_6_assumed'] > 0

    def test_m_6d_tev(self):
        assert 'm_6D_TeV' in self.eta


class TestDiscriminatingObservables:
    def setup_method(self):
        self.obs = discriminating_observables()

    def test_returns_list(self):
        assert isinstance(self.obs, list)

    def test_at_least_three_observables(self):
        assert len(self.obs) >= 3

    def test_each_has_required_keys(self):
        for o in self.obs:
            assert 'observable' in o
            assert 'prediction' in o
            assert 'experiment' in o
            assert 'timeline' in o
            assert 'discrimination_power' in o

    def test_nedm_present(self):
        names = [o['observable'] for o in self.obs]
        assert any('EDM' in n or 'edm' in n for n in names)

    def test_lhc_or_fcc_present(self):
        experiments = [o['experiment'] for o in self.obs]
        assert any('LHC' in e or 'FCC' in e for e in experiments)

    def test_timelines_are_future(self):
        for o in self.obs:
            timeline = o['timeline']
            # Should mention a year ≥ 2027; extract 4-digit year integers from string
            import re
            years = [int(y) for y in re.findall(r'\b2\d{3}\b', timeline)]
            if years:
                assert all(y >= 2027 for y in years), f"Timeline {timeline} appears past"


class TestSixdBaryogenesisScopeReport:
    def setup_method(self):
        self.report = sixd_baryogenesis_scope_report()

    def test_pillar_number(self):
        assert self.report['pillar'] == 432

    def test_status(self):
        assert self.report['status'] == 'SIXD_BARYOGENESIS_EXTENSION_SCOPED'

    def test_adjacency(self):
        assert '🔵' in self.report['adjacency']

    def test_parent_pillar(self):
        assert self.report['parent_pillar'] == 422

    def test_parent_status(self):
        assert self.report['parent_status'] == 'ALL_BARYOGENESIS_PATHS_EXHAUSTED'

    def test_field_content_present(self):
        assert 'field_content' in self.report
        assert 'new_field' in self.report['field_content']

    def test_um_constraints_present(self):
        assert 'um_constraints' in self.report
        assert len(self.report['um_constraints']) == 3

    def test_mechanism_present(self):
        assert 'mechanism' in self.report
        assert 'steps' in self.report['mechanism']

    def test_eta_b_estimate_present(self):
        assert 'eta_b_estimate' in self.report
        assert self.report['eta_b_estimate']['eta_b_6d'] > 0

    def test_observables_present(self):
        assert 'observables' in self.report
        assert len(self.report['observables']) >= 3

    def test_summary_string(self):
        assert len(self.report['summary']) > 50
        assert 'SIXD_BARYOGENESIS_EXTENSION_SCOPED' in self.report['summary']
