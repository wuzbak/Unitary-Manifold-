# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 800 — SPRINT_AS_REGRESSION_CERTIFICATE
~15 tests verifying sprint integrity.
"""
import pytest
from src.core.pillar800_sprint_as_regression_certificate import (
    sprint_as_summary,
    verify_pillar_modules,
    verify_lean4_files,
    SPRINT_AS_PILLARS,
    SPRINT_AS_LEAN4_START,
    SPRINT_AS_LEAN4_END,
    SPRINT_AS_LEAN4_DELTA,
    SPRINT_AS_NEXT_SLOT,
    SPRINT_AS_STATUS,
    PILLAR_800_GATE,
    SPRINT_AS_SUMMARY,
)


class TestSprintASCertificate:
    def test_status_correct(self):
        assert SPRINT_AS_STATUS == "SPRINT_AS_REGRESSION_PASSED"

    def test_pillars_list(self):
        assert SPRINT_AS_PILLARS == [795, 796, 797, 798, 799, 800]

    def test_lean4_start(self):
        assert SPRINT_AS_LEAN4_START == 1066

    def test_lean4_end(self):
        assert SPRINT_AS_LEAN4_END == 1141

    def test_lean4_delta(self):
        assert SPRINT_AS_LEAN4_DELTA == 75

    def test_lean4_arithmetic(self):
        assert SPRINT_AS_LEAN4_START + SPRINT_AS_LEAN4_DELTA == SPRINT_AS_LEAN4_END

    def test_next_slot(self):
        assert SPRINT_AS_NEXT_SLOT == 801

    def test_gate_alias(self):
        assert PILLAR_800_GATE == SPRINT_AS_STATUS

    def test_module_imports(self):
        results = verify_pillar_modules()
        for num in [795, 796, 797, 798, 799]:
            assert results[num]['status'] == 'OK', \
                f"Pillar {num} import failed: {results[num]}"

    def test_lean4_files_exist(self):
        files = verify_lean4_files()
        for name, info in files.items():
            assert info['exists'], f"Lean4 file missing: {name}"

    def test_summary_dict(self):
        s = sprint_as_summary()
        assert s['sprint'] == 'AS'
        assert s['status'] == SPRINT_AS_STATUS
        assert s['next_slot'] == 801

    def test_epistemic_deltas_count(self):
        s = sprint_as_summary()
        assert len(s['epistemic_deltas']) >= 4

    def test_birefringence_delta_present(self):
        s = sprint_as_summary()
        assert any('Birefringence' in d for d in s['epistemic_deltas'])

    def test_alias_callable(self):
        s = SPRINT_AS_SUMMARY()
        assert s['sprint'] == 'AS'

    def test_version_v24(self):
        s = sprint_as_summary()
        assert 'v24' in s['version']
