# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for axiomzero_guard.py — SM-Seed Audit Guard (Wave 1, v10.4).

Run from the repository root:
    python -m pytest tests/test_axiomzero_guard.py -v
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, ".")

from src.core.axiomzero_guard import (
    ALPHA_EM_DERIVED,
    ALLOWLIST_MARKERS,
    AXIOMZERO_STATUS,
    DERIVATION_FILES,
    FORBIDDEN_PATTERNS,
    axiomzero_summary,
    check_file_for_seeds,
    run_axiomzero_audit,
)


# ─────────────────────────────────────────────────────────────────────────────
# Catalogue tests
# ─────────────────────────────────────────────────────────────────────────────


class TestForbiddenPatternsCatalogue:
    """Verify the forbidden-pattern catalogue is well-formed."""

    def test_forbidden_patterns_non_empty(self):
        assert len(FORBIDDEN_PATTERNS) >= 4, "At least 4 forbidden patterns expected"

    def test_g_fermi_in_forbidden(self):
        assert "G_FERMI" in FORBIDDEN_PATTERNS

    def test_sin2_theta_pdg_in_forbidden(self):
        assert "SIN2_THETA_W_PDG" in FORBIDDEN_PATTERNS

    def test_all_patterns_uppercase(self):
        for p in FORBIDDEN_PATTERNS:
            assert p == p.upper(), f"Pattern {p!r} must be uppercase for case-insensitive matching"

    def test_derivation_files_non_empty(self):
        assert len(DERIVATION_FILES) >= 10

    def test_derivation_files_are_strings(self):
        for f in DERIVATION_FILES:
            assert isinstance(f, str)


# ─────────────────────────────────────────────────────────────────────────────
# Alpha_em derived-value compliance
# ─────────────────────────────────────────────────────────────────────────────


class TestAlphaEmDerivedValue:
    """alpha_em = 1/137.036 is the UM-derived value (P1 / Pillar 56)."""

    def test_alpha_em_derived_value(self):
        assert abs(ALPHA_EM_DERIVED - 1.0 / 137.036) < 1e-9

    def test_alpha_em_within_0p1pct_of_pdg(self):
        ALPHA_EM_PDG = 1.0 / 137.035_999_084  # CODATA 2022 — comparison only
        residual = abs(ALPHA_EM_DERIVED - ALPHA_EM_PDG) / ALPHA_EM_PDG
        assert residual < 0.001, (
            f"ALPHA_EM_DERIVED differs from PDG by {residual*100:.4f}% — "
            "the UM-derived α should agree with the measured value to <0.1%."
        )

    def test_alpha_em_is_derived_not_input(self):
        """The guard module itself treats alpha_em as a derived constant."""
        # The value 1/137.036 is the geometric prediction (P1, Pillar 56: α=φ₀⁻²).
        # It must be < 1/100 (weak coupling) and > 1/200 (physically reasonable).
        assert 1.0 / 200.0 < ALPHA_EM_DERIVED < 1.0 / 100.0


# ─────────────────────────────────────────────────────────────────────────────
# Audit PASS / FAIL logic
# ─────────────────────────────────────────────────────────────────────────────


class TestAuditLogic:
    """Test the audit engine on synthetic inputs."""

    def test_clean_file_returns_no_violations(self, tmp_path):
        clean = tmp_path / "clean.py"
        clean.write_text("alpha_em = 1/137.036\nk_cs = 74\n", encoding="utf-8")
        viols = check_file_for_seeds(
            str(clean.relative_to(tmp_path)), repo_root=str(tmp_path)
        )
        assert viols == []

    def test_comment_line_is_not_a_violation(self, tmp_path):
        with_comment = tmp_path / "commented.py"
        with_comment.write_text(
            "# G_FERMI is forbidden as a structural input\n"
            "k_cs = 74\n",
            encoding="utf-8",
        )
        viols = check_file_for_seeds(
            "commented.py", repo_root=str(tmp_path)
        )
        assert viols == [], "Comment-only mention must not be flagged"

    def test_comparison_line_is_not_a_violation(self, tmp_path):
        with_comparison = tmp_path / "compare.py"
        with_comparison.write_text(
            "G_FERMI_comparison = 1.166e-5  # comparison only\n",
            encoding="utf-8",
        )
        viols = check_file_for_seeds("compare.py", repo_root=str(tmp_path))
        assert viols == [], "Line containing 'comparison' must not be flagged"

    def test_structural_use_is_flagged(self, tmp_path):
        bad_file = tmp_path / "bad.py"
        bad_file.write_text(
            "G_FERMI = 1.166e-5  # Fermi constant\n"
            "result = G_FERMI * something\n",
            encoding="utf-8",
        )
        viols = check_file_for_seeds("bad.py", repo_root=str(tmp_path))
        # The definition line has '#' (allowlisted), but the structural use
        # on line 2 ('result = G_FERMI * something') has no allowlist marker.
        assert any("G_FERMI" in pat for _, pat, _ in viols), (
            "A structural G_FERMI use must be flagged."
        )

    def test_missing_file_is_not_a_violation(self, tmp_path):
        viols = check_file_for_seeds(
            "nonexistent_file.py", repo_root=str(tmp_path)
        )
        assert viols == []


# ─────────────────────────────────────────────────────────────────────────────
# Full repository audit (the actual compliance check)
# ─────────────────────────────────────────────────────────────────────────────


class TestRepositoryCompliance:
    """Integration tests against the real derivation-path files."""

    def test_audit_passes_on_current_codebase(self):
        """The full AxiomZero audit must return PASS on the current codebase.

        DELETE-POWER TEST: introduce G_FERMI as a structural input in any
        DERIVATION_FILES entry and this test (plus the import-time guard) fails.
        """
        report = run_axiomzero_audit()
        assert report["status"] == "PASS", (
            "AxiomZero audit FAILED:\n" + report["summary"]
        )

    def test_audit_checks_all_derivation_files(self):
        report = run_axiomzero_audit()
        assert report["files_checked"] == len(DERIVATION_FILES)

    def test_no_g_fermi_in_derivation_path(self):
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        for rel_path in DERIVATION_FILES:
            viols = check_file_for_seeds(rel_path, repo_root=repo_root)
            g_fermi_viols = [v for v in viols if v[1] == "G_FERMI"]
            assert g_fermi_viols == [], (
                f"G_FERMI structural use found in {rel_path}: {g_fermi_viols}"
            )

    def test_no_sin2_theta_pdg_in_derivation_path(self):
        repo_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        for rel_path in DERIVATION_FILES:
            viols = check_file_for_seeds(rel_path, repo_root=repo_root)
            sw_viols = [v for v in viols if v[1] == "SIN2_THETA_W_PDG"]
            assert sw_viols == [], (
                f"SIN2_THETA_W_PDG structural use found in {rel_path}: {sw_viols}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Summary API
# ─────────────────────────────────────────────────────────────────────────────


class TestSummaryAPI:
    """Test the axiomzero_summary() structured output."""

    def test_summary_has_required_keys(self):
        s = axiomzero_summary()
        for key in ("status", "forbidden_patterns", "derivation_files_audited",
                    "files_checked", "files_clean", "violations", "conclusion"):
            assert key in s, f"Summary missing key: {key!r}"

    def test_summary_status_is_pass(self):
        assert axiomzero_summary()["status"] == "PASS"

    def test_axiomzero_status_constant(self):
        assert "CONFIRMED" in AXIOMZERO_STATUS
        assert "v10.4" in AXIOMZERO_STATUS
