# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 794 — SPRINT_AR_REGRESSION_CERTIFICATE
~15 tests verifying sprint integrity.
"""
import pytest
from src.core.pillar794_sprint_ar_regression_certificate import (
    sprint_ar_summary,
    verify_pillar_modules,
    verify_lean4_files,
    verify_app_files,
    SPRINT_AR_PILLARS,
    SPRINT_AR_LEAN4_START,
    SPRINT_AR_LEAN4_END,
    SPRINT_AR_LEAN4_DELTA,
    SPRINT_AR_NEXT_SLOT,
    SPRINT_AR_STATUS,
    PILLAR_794_GATE,
    SPRINT_AR_SUMMARY,
)


class TestSprintARCertificate:
    def test_status_correct(self):
        assert SPRINT_AR_STATUS == "SPRINT_AR_REGRESSION_PASSED"

    def test_pillars_list(self):
        assert SPRINT_AR_PILLARS == [792, 793, 794]

    def test_lean4_start(self):
        assert SPRINT_AR_LEAN4_START == 1036

    def test_lean4_end(self):
        assert SPRINT_AR_LEAN4_END == 1066

    def test_lean4_delta(self):
        assert SPRINT_AR_LEAN4_DELTA == 30

    def test_lean4_arithmetic(self):
        assert SPRINT_AR_LEAN4_START + SPRINT_AR_LEAN4_DELTA == SPRINT_AR_LEAN4_END

    def test_next_slot(self):
        assert SPRINT_AR_NEXT_SLOT == 795

    def test_gate_alias(self):
        assert PILLAR_794_GATE == SPRINT_AR_STATUS

    def test_module_imports(self):
        results = verify_pillar_modules()
        for num in [792, 793]:
            assert results[num]['status'] == 'OK', f"Pillar {num} import failed: {results[num]}"

    def test_lean4_files_exist(self):
        files = verify_lean4_files()
        for name, info in files.items():
            assert info['exists'], f"Lean4 file missing: {name}"

    def test_app_files_exist(self):
        files = verify_app_files()
        for k, info in files.items():
            assert info['exists'], f"App file missing: {k}"

    def test_summary_dict(self):
        s = sprint_ar_summary()
        assert s['sprint'] == 'AR'
        assert s['status'] == SPRINT_AR_STATUS
        assert s['next_slot'] == 795

    def test_epistemic_deltas(self):
        s = sprint_ar_summary()
        assert len(s['epistemic_deltas']) >= 3

    def test_alias_callable(self):
        s = SPRINT_AR_SUMMARY()
        assert s['sprint'] == 'AR'

    def test_version_field(self):
        s = sprint_ar_summary()
        assert 'v23' in s['version']
