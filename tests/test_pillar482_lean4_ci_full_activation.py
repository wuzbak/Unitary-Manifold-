# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 482 — Lean4 CI Full Activation."""
from __future__ import annotations

from src.core.pillar482_lean4_ci_full_activation import (
    PILLAR_STATUS,
    PILLAR_NUMBER,
    PILLAR_TITLE,
    N_W,
    K_CS,
    CI_WORKFLOW_PATH,
    LEAN4_DIR,
    LAKEFILE_MATHLIB_TAG,
    TRIGGER_BRANCHES,
    workflow_trigger_spec,
    workflow_steps_spec,
    ci_activation_certificate,
    local_reproduction_script,
    tier2_activation_status,
    full_ci_report,
)


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'LEAN4_CI_FULLY_ACTIVATED'

    def test_pillar_number(self):
        assert PILLAR_NUMBER == 482

    def test_n_w(self):
        assert N_W == 5

    def test_k_cs(self):
        assert K_CS == 74

    def test_workflow_path(self):
        assert CI_WORKFLOW_PATH == '.github/workflows/lean4-check.yml'

    def test_lean4_dir(self):
        assert LEAN4_DIR == 'lean4'

    def test_mathlib_tag_present(self):
        assert 'v4' in LAKEFILE_MATHLIB_TAG

    def test_trigger_branches_all(self):
        assert '**' in TRIGGER_BRANCHES


class TestWorkflowTriggerSpec:
    def setup_method(self):
        self.spec = workflow_trigger_spec()

    def test_returns_dict(self):
        assert isinstance(self.spec, dict)

    def test_has_on(self):
        assert 'on' in self.spec

    def test_push_trigger(self):
        assert 'push' in self.spec['on']

    def test_pr_trigger(self):
        assert 'pull_request' in self.spec['on']

    def test_trigger_branches_all(self):
        assert self.spec['on']['push']['branches'] == ['**']

    def test_current_trigger_is_all_branches(self):
        assert 'all branches' in self.spec['current_trigger']

    def test_previous_trigger_documented(self):
        assert 'previous_trigger' in self.spec
        assert 'lean4' in self.spec['previous_trigger']

    def test_change_status(self):
        assert 'ACTIVATED' in self.spec['change_status']


class TestWorkflowStepsSpec:
    def setup_method(self):
        self.steps = workflow_steps_spec()

    def test_returns_list(self):
        assert isinstance(self.steps, list)

    def test_seven_steps(self):
        assert len(self.steps) == 7

    def test_steps_have_step_numbers(self):
        for i, step in enumerate(self.steps, 1):
            assert step['step'] == i

    def test_steps_have_names(self):
        for step in self.steps:
            assert 'name' in step
            assert isinstance(step['name'], str)

    def test_lake_build_present(self):
        step_names = [s['name'] for s in self.steps]
        assert any('Lake build' in n for n in step_names)

    def test_elan_install_present(self):
        step_names = [s['name'] for s in self.steps]
        assert any('elan' in n.lower() for n in step_names)

    def test_mathlib_cache_present(self):
        step_names = [s['name'] for s in self.steps]
        assert any('Mathlib' in n for n in step_names)

    def test_numerical_checks_present(self):
        step_names = [s['name'] for s in self.steps]
        assert any('NumericalChecks' in n for n in step_names)

    def test_estimated_minutes_positive(self):
        for step in self.steps:
            if 'estimated_minutes' in step:
                assert step['estimated_minutes'] > 0


class TestCIActivationCertificate:
    def setup_method(self):
        self.cert = ci_activation_certificate()

    def test_returns_dict(self):
        assert isinstance(self.cert, dict)

    def test_pillar_number(self):
        assert self.cert['pillar'] == 482

    def test_status(self):
        assert self.cert['status'] == 'LEAN4_CI_FULLY_ACTIVATED'

    def test_tier1_operational(self):
        assert self.cert['tier1_status'] == 'OPERATIONAL'

    def test_tier2_operational(self):
        assert self.cert['tier2_status'] == 'OPERATIONAL_VIA_WORKFLOW'

    def test_trigger_all_branches(self):
        assert 'ALL_BRANCHES' in self.cert['trigger']

    def test_epistemic_delta_documented(self):
        assert 'CI_BLOCKED' in self.cert['epistemic_delta']
        assert 'LEAN4_CI_FULLY_ACTIVATED' in self.cert['epistemic_delta']

    def test_certificate_hash_is_hex(self):
        h = self.cert['certificate_hash']
        assert len(h) == 64
        assert all(c in '0123456789abcdef' for c in h)

    def test_mathlib_tag(self):
        assert 'v4' in self.cert['mathlib_tag']

    def test_expected_minutes_reasonable(self):
        assert self.cert['expected_ci_minutes'] > 5
        assert self.cert['expected_ci_minutes'] < 30

    def test_steps_count(self):
        assert self.cert['steps'] == 7


class TestLocalReproductionScript:
    def setup_method(self):
        self.script = local_reproduction_script()

    def test_returns_string(self):
        assert isinstance(self.script, str)

    def test_has_shebang(self):
        assert '#!/usr/bin/env bash' in self.script

    def test_has_elan_install(self):
        assert 'elan-init.sh' in self.script

    def test_has_lake_build(self):
        assert 'lake build' in self.script

    def test_has_mathlib_cache(self):
        assert 'lake exe cache get' in self.script

    def test_has_success_message(self):
        assert 'SUCCESSFUL' in self.script or 'successful' in self.script.lower()

    def test_has_pillar_reference(self):
        assert '482' in self.script

    def test_set_euo_pipefail(self):
        assert 'set -euo pipefail' in self.script

    def test_multiple_steps(self):
        assert self.script.count('echo') >= 4


class TestTier2ActivationStatus:
    def setup_method(self):
        self.t2 = tier2_activation_status()

    def test_returns_dict(self):
        assert isinstance(self.t2, dict)

    def test_tier_is_2(self):
        assert self.t2['tier'] == 2

    def test_current_status_activated(self):
        assert 'ACTIVATED' in self.t2['current_status']

    def test_previous_status_blocked(self):
        assert 'BLOCKED' in self.t2['previous_status']

    def test_mechanism_documented(self):
        assert 'lean4-check.yml' in self.t2['mechanism']

    def test_expected_time_positive(self):
        assert self.t2['expected_wall_time_minutes'] > 0
        assert self.t2['expected_wall_time_cached_minutes'] > 0

    def test_cached_faster_than_uncached(self):
        assert (
            self.t2['expected_wall_time_cached_minutes']
            < self.t2['expected_wall_time_minutes']
        )

    def test_blocking_issue_resolved(self):
        assert 'P458' in self.t2['blocking_issue_resolved']
        assert 'P482' in self.t2['blocking_issue_resolved']


class TestFullCIReport:
    def setup_method(self):
        self.report = full_ci_report()

    def test_returns_dict(self):
        assert isinstance(self.report, dict)

    def test_pillar_number(self):
        assert self.report['pillar'] == 482

    def test_status(self):
        assert self.report['status'] == 'LEAN4_CI_FULLY_ACTIVATED'

    def test_has_tier1(self):
        assert 'tier1' in self.report
        assert self.report['tier1']['status'] == 'OPERATIONAL'

    def test_has_tier2(self):
        assert 'tier2' in self.report

    def test_has_certificate(self):
        assert 'certificate' in self.report

    def test_has_workflow_trigger(self):
        assert 'workflow_trigger' in self.report

    def test_has_workflow_steps(self):
        assert 'workflow_steps' in self.report
        assert len(self.report['workflow_steps']) == 7

    def test_verdict_contains_key_info(self):
        v = self.report['verdict']
        assert 'fully activated' in v.lower() or 'Fully activated' in v

    def test_local_script_lines_positive(self):
        assert self.report['local_script_lines'] > 10

    def test_n_w_correct(self):
        assert self.report['n_w'] == 5

    def test_k_cs_correct(self):
        assert self.report['k_cs'] == 74
