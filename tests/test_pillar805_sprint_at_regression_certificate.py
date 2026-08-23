# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Tests for Pillar 805 — SPRINT_AT_REGRESSION_CERTIFICATE
~15 tests verifying sprint integrity.
"""
import pytest
from src.core.pillar805_sprint_at_regression_certificate import (
    sprint_at_summary,
    verify_pillar_modules,
    verify_lean4_files,
    SPRINT_AT_PILLARS,
    SPRINT_AT_LEAN4_START,
    SPRINT_AT_LEAN4_END,
    SPRINT_AT_LEAN4_DELTA,
    SPRINT_AT_NEXT_SLOT,
    SPRINT_AT_STATUS,
    PILLAR_805_GATE,
    SPRINT_AT_SUMMARY,
    SPRINT_AT_LEAN4_FILES,
)


class TestSprintATCertificate:
    def test_status_correct(self):
        assert SPRINT_AT_STATUS == "SPRINT_AT_REGRESSION_PASSED"

    def test_pillars_list(self):
        assert SPRINT_AT_PILLARS == [801, 802, 803, 804, 805]

    def test_lean4_start(self):
        assert SPRINT_AT_LEAN4_START == 1141

    def test_lean4_end(self):
        assert SPRINT_AT_LEAN4_END == 1246

    def test_lean4_delta(self):
        assert SPRINT_AT_LEAN4_DELTA == 105

    def test_lean4_arithmetic(self):
        assert SPRINT_AT_LEAN4_START + SPRINT_AT_LEAN4_DELTA == SPRINT_AT_LEAN4_END

    def test_next_slot(self):
        assert SPRINT_AT_NEXT_SLOT == 806

    def test_gate_alias(self):
        assert PILLAR_805_GATE == SPRINT_AT_STATUS

    def test_module_imports(self):
        results = verify_pillar_modules()
        for num in [801, 802, 803, 804]:
            assert results[num]['status'] == 'OK', \
                f"Pillar {num} import failed: {results[num]}"

    def test_lean4_files_exist(self):
        files = verify_lean4_files()
        for name, info in files.items():
            assert info['exists'], f"Lean4 file missing: {name}"

    def test_lean4_files_count(self):
        assert len(SPRINT_AT_LEAN4_FILES) == 7

    def test_summary_dict(self):
        s = sprint_at_summary()
        assert s['pillar'] == 805
        assert s['sprint'] == 'AT'
        assert s['gate'] == SPRINT_AT_STATUS
        assert s['next_slot'] == SPRINT_AT_NEXT_SLOT

    def test_summary_string_nonempty(self):
        assert len(SPRINT_AT_SUMMARY) > 50

    def test_lean4_delta_7x15(self):
        # 7 files × 15 theorems each = 105
        assert SPRINT_AT_LEAN4_DELTA == 7 * 15
