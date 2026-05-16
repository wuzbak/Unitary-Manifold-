# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests — Lane 6: HILS governance boundary.

Validates that:
- The Pentad README declares independent governance status (not physics proof)
- No Pentad Python file asserts DERIVED/ALGEBRAIC for Pentad-specific constructs
- SEPARATION.md hard boundary is present and current
- The HILS session protocol non-negotiables are in place
- The Pentad lane audit document exists
- ToE score denominator isolation: Pentad tests are not in the ToE denominator
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PENTAD_DIR = ROOT / "5-GOVERNANCE" / "Unitary Pentad"
SEPARATION_MD = ROOT / "SEPARATION.md"
HILS_SESSION = ROOT / "HILS_SESSION_CURRENT.md"
PENTAD_LANE_AUDIT = ROOT / "5-GOVERNANCE" / "PENTAD_LANE_AUDIT.md"
CLAIM_MASTER_BOARD = ROOT / "docs" / "CLAIM_MASTER_BOARD.md"

# Patterns that are prohibited in Pentad .py docstrings when coupled to Pentad claims
# Case-sensitive: only uppercase epistemic labels (DERIVED, PROVED, ALGEBRAIC) are violations
PHYSICS_CLAIM_PATTERNS = [
    re.compile(
        r"\b(DERIVED|ALGEBRAIC|PROVED)\b.*\bPentad\b"
        r"|\bPentad\b.*\b(DERIVED|ALGEBRAIC|PROVED)\b",
        # No re.IGNORECASE — lowercase "derived"/"proved" is acceptable English
    ),
    re.compile(
        r"physics\s+proof\s+of\s+Pentad|Pentad\s+is\s+a\s+physics\s+proof",
        re.IGNORECASE,
    ),
]

# Required phrases in Pentad README (governance declaration)
# Note: "itself a physics claim" may span two lines in the blockquote
PENTAD_README_REQUIRED = [
    "independent governance",
    "physics claim",  # deliberately broad — covers "not itself a physics claim" or similar
]

# Non-negotiables that must appear in HILS_SESSION_CURRENT.md
HILS_NON_NEGOTIABLES = [
    "Epistemic separation",
    "Human intent-control",
    "Pillar set CLOSED",
]


class TestPentadLaneAuditExists:
    def test_audit_exists(self):
        assert PENTAD_LANE_AUDIT.exists(), f"PENTAD_LANE_AUDIT.md not found"

    def test_audit_has_mislabeling_section(self):
        text = PENTAD_LANE_AUDIT.read_text(encoding="utf-8")
        assert "Mislabeling Prevention" in text

    def test_audit_has_human_intent_control_section(self):
        text = PENTAD_LANE_AUDIT.read_text(encoding="utf-8")
        assert "Human Intent-Control" in text


class TestPentadReadmeDeclaration:
    def test_pentad_readme_exists(self):
        readme = PENTAD_DIR / "README.md"
        assert readme.exists()

    def test_pentad_readme_has_governance_declaration(self):
        readme = PENTAD_DIR / "README.md"
        text = readme.read_text(encoding="utf-8").lower()
        missing = [p for p in PENTAD_README_REQUIRED if p.lower() not in text]
        assert not missing, (
            f"Pentad README missing required governance declarations: {missing}"
        )

    def test_pentad_readme_has_separation_reference(self):
        readme = PENTAD_DIR / "README.md"
        text = readme.read_text(encoding="utf-8")
        assert "SEPARATION.md" in text, (
            "Pentad README must reference SEPARATION.md"
        )


class TestPentadFilesNoPhysicsClaimForPentad:
    """No Pentad .py file may assert DERIVED/PROVED for Pentad constructs."""

    def test_pentad_python_files_no_physics_claims(self):
        violations = []
        for py_file in PENTAD_DIR.rglob("*.py"):
            try:
                text = py_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat in PHYSICS_CLAIM_PATTERNS:
                matches = pat.findall(text)
                if matches:
                    rel = str(py_file.relative_to(ROOT))
                    violations.append(f"[{rel}] Prohibited physics claim pattern found")
        assert not violations, (
            "Pentad Python files with physics claim violations:\n"
            + "\n".join(violations)
        )


class TestSeparationDocumentIsAuthoritative:
    def test_separation_exists(self):
        assert SEPARATION_MD.exists()

    def test_separation_has_category_boundary(self):
        text = SEPARATION_MD.read_text(encoding="utf-8")
        assert "Category 1" in text and ("Category 2" in text or "Category-2" in text), (
            "SEPARATION.md must define both Category 1 and Category 2"
        )

    def test_separation_has_pentad_or_governance(self):
        text = SEPARATION_MD.read_text(encoding="utf-8")
        assert "Pentad" in text or "governance" in text.lower() or "phenomenological" in text, (
            "SEPARATION.md should reference governance or phenomenological bridge scope"
        )


class TestHILSSessionNonNegotiables:
    def test_session_current_exists(self):
        assert HILS_SESSION.exists(), "HILS_SESSION_CURRENT.md not found"

    def test_session_has_non_negotiables(self):
        text = HILS_SESSION.read_text(encoding="utf-8")
        missing = [n for n in HILS_NON_NEGOTIABLES if n not in text]
        assert not missing, (
            f"HILS session non-negotiables missing: {missing}"
        )

    def test_session_has_human_override(self):
        text = HILS_SESSION.read_text(encoding="utf-8")
        assert "override" in text.lower() or "Human intent-control" in text, (
            "HILS session must declare human override authority"
        )


class TestToEScoreIsolation:
    """The Pentad must not contribute to the ToE denominator."""

    def test_claim_board_toe_denominator_is_physics_only(self):
        board = CLAIM_MASTER_BOARD.read_text(encoding="utf-8")
        # The ToE score denominator line should reference physics parameters, not Pentad
        toe_lines = [l for l in board.splitlines() if "ToE Score" in l or "28.0/28" in l]
        assert toe_lines, "CLAIM_MASTER_BOARD.md must have a ToE Score line"
        # None of those lines should mention Pentad
        for line in toe_lines:
            assert "Pentad" not in line, (
                f"ToE Score line must not reference Pentad: {line}"
            )

    def test_claim_board_toe_denominator_is_28(self):
        board = CLAIM_MASTER_BOARD.read_text(encoding="utf-8")
        # Find the denominator — should be 28 (physics parameters only)
        match = re.search(r"(\d+\.\d+)\s*/\s*(\d+)", board)
        if match:
            denominator = int(match.group(2))
            assert denominator == 28, (
                f"ToE denominator must be 28 (physics parameters only); got {denominator}"
            )
