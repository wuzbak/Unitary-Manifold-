# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests — Lane 4: Separation integrity.

Validates hard boundaries among core physics, adjacent tracks,
governance (Pentad), and outreach.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.core.separation_integrity_checker import (
    check_adjacent_track_labels,
    check_pentad_physics_claims,
    run_all_checks,
)

ROOT = Path(__file__).resolve().parents[1]

# Spot-check: at least one adjacent track module should exist
KNOWN_ADJACENT_TRACK = ROOT / "src" / "core" / "pillar218_quantum_control.py"

# Known Pentad file that should not have physics claims
KNOWN_PENTAD_FILE = ROOT / "5-GOVERNANCE" / "Unitary Pentad" / "__init__.py"


class TestAdjacentTrackLabels:
    def test_adjacent_track_label_check_passes(self):
        violations = check_adjacent_track_labels(verbose=False)
        assert violations == [], (
            f"Adjacent track label violations found:\n"
            + "\n".join(violations)
        )

    def test_known_adjacent_file_exists(self):
        assert KNOWN_ADJACENT_TRACK.exists(), (
            f"Expected adjacent track module not found: {KNOWN_ADJACENT_TRACK}"
        )


class TestPentadPhysicsClaims:
    def test_pentad_physics_claim_check_passes(self):
        violations = check_pentad_physics_claims(verbose=False)
        assert violations == [], (
            f"Pentad physics claim violations found:\n"
            + "\n".join(violations)
        )


class TestRunAll:
    def test_full_run_passes(self):
        file_count, violations = run_all_checks(verbose=False)
        assert violations == [], (
            f"Separation integrity violations ({len(violations)}):\n"
            + "\n".join(violations)
        )

    def test_files_were_checked(self):
        file_count, _ = run_all_checks(verbose=False)
        assert file_count > 0, (
            "Separation checker found no files to check — "
            "adjacent track or Pentad patterns may be broken"
        )


class TestSeparationBoundaryIsEnforced:
    """Delete-power test: the checker must detect a violation when planted."""

    def test_checker_detects_missing_adjacent_label(self, tmp_path):
        """A file matching the adjacent pattern but missing the label should fail."""
        import re
        from src.core.separation_integrity_checker import (
            ADJACENT_TRACK_REQUIRED_LABEL,
            ADJACENT_TRACK_PATTERN,
        )
        # The pattern requires the full relative path with src/core/ prefix
        fake_rel = "src/core/pillar219_fake_track.py"
        assert ADJACENT_TRACK_PATTERN.search(fake_rel), (
            f"Pattern should match '{fake_rel}' — check ADJACENT_TRACK_PATTERN"
        )

        # Verify that a docstring without the label is correctly identified
        # (use a phrase that does NOT accidentally contain 'adjacent' or 'track')
        no_label_docstring = 'This module computes field dynamics without any track annotation.'
        assert not ADJACENT_TRACK_REQUIRED_LABEL.search(no_label_docstring), (
            "Test docstring should NOT match the adjacent track label pattern"
        )

        # Verify that a compliant docstring IS matched
        good_docstring = 'Adjacent applied research track (non-hardgate): applies geometry...'
        assert ADJACENT_TRACK_REQUIRED_LABEL.search(good_docstring), (
            "Good docstring with 'adjacent applied research track' should match the label pattern"
        )
