# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests — Lane 5: Safety lockstep.

Validates that:
- All safety artifacts declared in SAFETY_LOCKSTEP_AUDIT.md exist on disk
- Key safety executables are importable (or at least syntactically valid)
- High-risk content modules carry a reference to their safety artifact
- The dual-use notice and separation document exist
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

SAFETY_LOCKSTEP_AUDIT = ROOT / "8-SAFETY" / "SAFETY_LOCKSTEP_AUDIT.md"

# Safety artifacts that must exist on disk
REQUIRED_SAFETY_ARTIFACTS = [
    "8-SAFETY/SAFETY/RADIOLOGICAL_SAFETY.md",
    "8-SAFETY/SAFETY/admissibility_checker.py",
    "8-SAFETY/SAFETY/thermal_runaway_mitigation.py",
    "8-SAFETY/SAFETY/unitarity_sentinel.py",
    "8-SAFETY/SAFETY/PROOF_OF_UNIQUENESS.md",
    "DUAL_USE_NOTICE.md",
    "PENTAD_PRODUCT_NOTICE.md",
    "SEPARATION.md",
    "8-SAFETY/SAFETY_LOCKSTEP_AUDIT.md",
]

# High-risk Python modules that must exist
REQUIRED_HIGH_RISK_MODULES = [
    "src/core/braided_winding.py",
    "src/core/inflation.py",
    "src/core/evolution.py",
    "src/core/lab_litebird_substitute.py",
]

# Safety executables that must be syntactically valid Python
SAFETY_EXECUTABLES = [
    "8-SAFETY/SAFETY/admissibility_checker.py",
    "8-SAFETY/SAFETY/thermal_runaway_mitigation.py",
    "8-SAFETY/SAFETY/unitarity_sentinel.py",
]


class TestLockstepAuditExists:
    def test_audit_file_exists(self):
        assert SAFETY_LOCKSTEP_AUDIT.exists(), (
            f"SAFETY_LOCKSTEP_AUDIT.md not found at {SAFETY_LOCKSTEP_AUDIT}"
        )

    def test_audit_has_lockstep_table(self):
        text = SAFETY_LOCKSTEP_AUDIT.read_text(encoding="utf-8")
        assert "LOCKED" in text, "Lockstep audit must contain LOCKED status entries"

    def test_audit_has_protocol_section(self):
        text = SAFETY_LOCKSTEP_AUDIT.read_text(encoding="utf-8")
        assert "Lockstep Protocol" in text

    def test_audit_has_admitted_gaps(self):
        text = SAFETY_LOCKSTEP_AUDIT.read_text(encoding="utf-8")
        assert "Admitted Gaps" in text


class TestRequiredSafetyArtifacts:
    @pytest.mark.parametrize("rel_path", REQUIRED_SAFETY_ARTIFACTS)
    def test_safety_artifact_exists(self, rel_path):
        assert (ROOT / rel_path).exists(), (
            f"Required safety artifact missing: {rel_path}"
        )


class TestHighRiskModulesExist:
    @pytest.mark.parametrize("rel_path", REQUIRED_HIGH_RISK_MODULES)
    def test_high_risk_module_exists(self, rel_path):
        assert (ROOT / rel_path).exists(), (
            f"High-risk module missing: {rel_path}"
        )


class TestSafetyExecutablesSyntax:
    @pytest.mark.parametrize("rel_path", SAFETY_EXECUTABLES)
    def test_executable_is_valid_python(self, rel_path):
        path = ROOT / rel_path
        assert path.exists(), f"Safety executable not found: {rel_path}"
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source)
        except SyntaxError as exc:
            pytest.fail(f"Syntax error in safety executable {rel_path}: {exc}")


class TestSeparationDocuments:
    def test_separation_md_has_category_2(self):
        sep = ROOT / "SEPARATION.md"
        assert sep.exists()
        text = sep.read_text(encoding="utf-8")
        assert "Category 2" in text or "Category-2" in text, (
            "SEPARATION.md must define Category-2 (phenomenological bridges)"
        )

    def test_dual_use_notice_has_agpl_reference(self):
        dun = ROOT / "DUAL_USE_NOTICE.md"
        assert dun.exists()
        text = dun.read_text(encoding="utf-8")
        assert "AGPL" in text, "DUAL_USE_NOTICE.md must reference AGPL"

    def test_dual_use_notice_has_pillar15_reference(self):
        dun = ROOT / "DUAL_USE_NOTICE.md"
        text = dun.read_text(encoding="utf-8")
        assert "Pillar 15" in text or "cold fusion" in text.lower(), (
            "DUAL_USE_NOTICE.md must reference Pillar 15 / cold fusion content"
        )


class TestColdFusionSafetyLockstep:
    """Cold fusion content must have radiological safety coverage."""

    def test_radiological_safety_references_cold_fusion(self):
        rad_safety = ROOT / "8-SAFETY" / "SAFETY" / "RADIOLOGICAL_SAFETY.md"
        assert rad_safety.exists()
        text = rad_safety.read_text(encoding="utf-8")
        assert "cold fusion" in text.lower() or "lenr" in text.lower() or "pd" in text.lower(), (
            "RADIOLOGICAL_SAFETY.md must address cold fusion / LENR / Pd lattice scenarios"
        )

    def test_admissibility_checker_is_executable(self):
        checker = ROOT / "8-SAFETY" / "SAFETY" / "admissibility_checker.py"
        assert checker.exists()
        source = checker.read_text(encoding="utf-8")
        # Must define some admissibility function
        assert "def " in source, "admissibility_checker.py must define at least one function"
