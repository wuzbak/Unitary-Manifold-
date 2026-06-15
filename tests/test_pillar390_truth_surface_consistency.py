# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests for Pillar 390 — Truth-Surface Consistency Checker.

Validates version-sync detection, test-count-sync detection,
high-tension signal presence, LiteBIRD primary-falsifier presence,
and the full in-memory consistency pipeline.
"""

import pytest

from src.core.truth_surface_consistency_checker import (
    CANONICAL_SURFACES,
    CANONICAL_VERSION,
    DivergenceClass,
    Divergence,
    SurfaceSnapshot,
    ConsistencyReport,
    check_version_sync,
    check_test_count_sync,
    check_high_tension_claims,
    check_litebird_primary_falsifier,
    check_surfaces_from_texts,
    pillar_390_status,
)


# ──────────────────────────────────────────────────────────────────────────────
# Canonical surfaces registry
# ──────────────────────────────────────────────────────────────────────────────

class TestCanonicalSurfaces:

    def test_six_surfaces_defined(self):
        assert len(CANONICAL_SURFACES) >= 6

    def test_status_md_present(self):
        assert "STATUS.md" in CANONICAL_SURFACES

    def test_mas_tracker_present(self):
        assert any("mas_tracker" in s for s in CANONICAL_SURFACES)

    def test_claim_master_board_present(self):
        assert any("CLAIM_MASTER_BOARD" in s for s in CANONICAL_SURFACES)

    def test_truth_layer_present(self):
        assert any("TRUTH_LAYER" in s for s in CANONICAL_SURFACES)

    def test_observation_tracker_present(self):
        assert any("OBSERVATION_TRACKER" in s for s in CANONICAL_SURFACES)

    def test_gatekeeper_summary_present(self):
        assert any("GATEKEEPER_SUMMARY" in s for s in CANONICAL_SURFACES)


# ──────────────────────────────────────────────────────────────────────────────
# SurfaceSnapshot extraction
# ──────────────────────────────────────────────────────────────────────────────

class TestSurfaceSnapshotExtraction:

    def test_extract_version_v128(self):
        snap = SurfaceSnapshot.from_text("STATUS.md", "# Status v12.8\n")
        assert snap.version == "v12.8"

    def test_extract_version_v127(self):
        snap = SurfaceSnapshot.from_text("STATUS.md", "Last updated: v12.7 — sprint\n")
        assert snap.version == "v12.7"

    def test_extract_test_count_with_comma(self):
        snap = SurfaceSnapshot.from_text("STATUS.md", "39,745 passed · 22 skipped")
        assert snap.test_count == 39_745

    def test_extract_test_count_without_comma(self):
        snap = SurfaceSnapshot.from_text("STATUS.md", "38568 passed")
        assert snap.test_count == 38_568

    def test_no_version_returns_none(self):
        snap = SurfaceSnapshot.from_text("STATUS.md", "No version here")
        assert snap.version is None

    def test_no_test_count_returns_none(self):
        snap = SurfaceSnapshot.from_text("STATUS.md", "No count here")
        assert snap.test_count is None

    def test_path_stored_correctly(self):
        snap = SurfaceSnapshot.from_text("docs/TRUTH_LAYER.md", "v12.8")
        assert snap.path == "docs/TRUTH_LAYER.md"

    def test_raw_text_stored(self):
        text = "Full surface content v12.8 39,745 passed"
        snap = SurfaceSnapshot.from_text("STATUS.md", text)
        assert snap.raw_text == text


# ──────────────────────────────────────────────────────────────────────────────
# Version-sync check
# ──────────────────────────────────────────────────────────────────────────────

class TestVersionSync:

    def _snap(self, path: str, text: str) -> SurfaceSnapshot:
        return SurfaceSnapshot.from_text(path, text)

    def test_matching_version_no_divergence(self):
        snaps = [self._snap("STATUS.md", "v12.8")]
        divs  = check_version_sync(snaps, "v12.8")
        blockers = [d for d in divs if d.is_blocking]
        assert len(blockers) == 0

    def test_stale_version_is_blocker(self):
        snaps = [self._snap("STATUS.md", "v12.7")]
        divs  = check_version_sync(snaps, "v12.8")
        blockers = [d for d in divs if d.is_blocking]
        assert len(blockers) == 1
        assert blockers[0].found == "v12.7"
        assert blockers[0].expected == "v12.8"

    def test_missing_version_is_warning_not_blocker(self):
        snaps = [self._snap("STATUS.md", "no version here")]
        divs  = check_version_sync(snaps, "v12.8")
        blockers = [d for d in divs if d.is_blocking]
        warnings = [d for d in divs if d.classification == DivergenceClass.WARNING]
        assert len(blockers) == 0
        assert len(warnings) == 1

    def test_multiple_surfaces_all_matching(self):
        snaps = [
            self._snap("STATUS.md", "v12.8"),
            self._snap("docs/WAVE_CHANGELOG.md", "v12.8"),
        ]
        divs = check_version_sync(snaps, "v12.8")
        assert all(not d.is_blocking for d in divs)

    def test_mixed_versions_produce_blocker(self):
        snaps = [
            self._snap("STATUS.md", "v12.8"),
            self._snap("docs/GATEKEEPER_SUMMARY.md", "v12.7"),
        ]
        divs = check_version_sync(snaps, "v12.8")
        blockers = [d for d in divs if d.is_blocking]
        assert len(blockers) == 1
        assert "GATEKEEPER_SUMMARY.md" in blockers[0].surface


# ──────────────────────────────────────────────────────────────────────────────
# Test-count-sync check
# ──────────────────────────────────────────────────────────────────────────────

class TestTestCountSync:

    def _snap(self, path: str, text: str) -> SurfaceSnapshot:
        return SurfaceSnapshot.from_text(path, text)

    def test_matching_count_no_blocker(self):
        snaps = [self._snap("STATUS.md", "39,745 passed")]
        divs  = check_test_count_sync(snaps, 39_745)
        blockers = [d for d in divs if d.is_blocking]
        assert len(blockers) == 0

    def test_stale_count_is_blocker(self):
        snaps = [self._snap("STATUS.md", "38,421 passed")]
        divs  = check_test_count_sync(snaps, 39_745)
        blockers = [d for d in divs if d.is_blocking]
        assert len(blockers) == 1

    def test_no_count_in_surface_is_info(self):
        snaps = [self._snap("docs/TRUTH_LAYER.md", "No count here")]
        divs  = check_test_count_sync(snaps, 39_745)
        infos = [d for d in divs if d.classification == DivergenceClass.INFO]
        assert len(infos) == 1
        assert not any(d.is_blocking for d in divs)

    def test_tolerance_zero_exact_match(self):
        snaps = [self._snap("STATUS.md", "39,745 passed")]
        divs  = check_test_count_sync(snaps, 39_745, tolerance=0)
        assert not any(d.is_blocking for d in divs)

    def test_count_within_tolerance_ok(self):
        snaps = [self._snap("STATUS.md", "39,740 passed")]
        divs  = check_test_count_sync(snaps, 39_745, tolerance=10)
        assert not any(d.is_blocking for d in divs)

    def test_count_outside_tolerance_blocker(self):
        snaps = [self._snap("STATUS.md", "39,600 passed")]
        divs  = check_test_count_sync(snaps, 39_745, tolerance=100)
        blockers = [d for d in divs if d.is_blocking]
        assert len(blockers) == 1


# ──────────────────────────────────────────────────────────────────────────────
# High-tension signal presence
# ──────────────────────────────────────────────────────────────────────────────

class TestHighTensionCheck:

    def test_gatekeeper_summary_with_tension_ok(self):
        snap = SurfaceSnapshot.from_text(
            "docs/GATEKEEPER_SUMMARY.md",
            "HIGH_TENSION DESI wₐ two active signals",
        )
        divs = check_high_tension_claims([snap])
        assert all(d.classification != DivergenceClass.RELEASE_BLOCKER for d in divs)

    def test_gatekeeper_missing_tension_is_warning(self):
        snap = SurfaceSnapshot.from_text(
            "docs/GATEKEEPER_SUMMARY.md",
            "All signals consistent; nothing to report",
        )
        divs = check_high_tension_claims([snap])
        warnings = [d for d in divs if d.classification == DivergenceClass.WARNING]
        assert len(warnings) > 0

    def test_non_monitored_surface_skipped(self):
        snap = SurfaceSnapshot.from_text(
            "STATUS.md",
            "No tension mentioned",
        )
        divs = check_high_tension_claims([snap])
        # STATUS.md is not in the monitored surfaces for this check
        assert len(divs) == 0


# ──────────────────────────────────────────────────────────────────────────────
# LiteBIRD primary falsifier check
# ──────────────────────────────────────────────────────────────────────────────

class TestLiteBIRDCheck:

    def test_surface_with_litebird_ok(self):
        snap = SurfaceSnapshot.from_text(
            "STATUS.md", "LiteBIRD birefringence β PRIMARY FALSIFIER"
        )
        divs = check_litebird_primary_falsifier([snap])
        warnings = [d for d in divs if d.classification == DivergenceClass.WARNING]
        assert len(warnings) == 0

    def test_surface_without_litebird_warning(self):
        snap = SurfaceSnapshot.from_text(
            "STATUS.md", "Simons Observatory tensor ratio prediction"
        )
        divs = check_litebird_primary_falsifier([snap])
        warnings = [d for d in divs if d.classification == DivergenceClass.WARNING]
        assert len(warnings) == 1


# ──────────────────────────────────────────────────────────────────────────────
# Full in-memory consistency check
# ──────────────────────────────────────────────────────────────────────────────

class TestFullConsistencyCheck:

    def _make_conforming_texts(self, version: str = "v12.8", count: int = 39_745) -> dict:
        base = (
            f"version {version}\n"
            f"{count:,} passed · 22 skipped\n"
            f"LiteBIRD birefringence β PRIMARY FALSIFIER\n"
            f"HIGH_TENSION DESI wₐ signals\n"
        )
        return {
            "STATUS.md": base,
            "docs/mas_tracker.yml": base,
            "docs/CLAIM_MASTER_BOARD.md": base,
            "docs/TRUTH_LAYER.md": base,
            "3-FALSIFICATION/OBSERVATION_TRACKER.md": base,
            "docs/GATEKEEPER_SUMMARY.md": base,
        }

    def test_all_conforming_no_blockers(self):
        texts  = self._make_conforming_texts()
        report = check_surfaces_from_texts(texts, "v12.8", 39_745)
        assert len(report.blockers) == 0
        assert report.is_release_ready

    def test_one_stale_version_creates_blocker(self):
        texts = self._make_conforming_texts()
        texts["docs/GATEKEEPER_SUMMARY.md"] = "version v12.7\n39,745 passed\nLiteBIRD HIGH_TENSION DESI wₐ"
        report = check_surfaces_from_texts(texts, "v12.8", 39_745)
        assert len(report.blockers) >= 1
        assert not report.is_release_ready

    def test_stale_test_count_creates_blocker(self):
        texts = self._make_conforming_texts(count=38_421)
        report = check_surfaces_from_texts(texts, "v12.8", 39_745)
        assert len(report.blockers) >= 1

    def test_summary_structure(self):
        texts  = self._make_conforming_texts()
        report = check_surfaces_from_texts(texts, "v12.8", 39_745)
        s = report.summary()
        assert "surfaces_checked" in s
        assert "blockers" in s
        assert "is_release_ready" in s
        assert s["surfaces_checked"] == 6


# ──────────────────────────────────────────────────────────────────────────────
# Pillar status
# ──────────────────────────────────────────────────────────────────────────────

class TestPillar390Status:

    def test_status_structure(self):
        status = pillar_390_status()
        assert status["pillar"] == 390
        assert status["label"] == "ADJACENT_TRACK"
        assert status["hils_status"] == "ACTIVE"

    def test_six_surfaces_in_status(self):
        status = pillar_390_status()
        assert len(status["surfaces_monitored"]) >= 6

    def test_divergence_classes_listed(self):
        status = pillar_390_status()
        classes = status["divergence_classes"]
        assert "RELEASE_BLOCKER" in classes
        assert "WARNING" in classes
        assert "INFO" in classes

    def test_checks_active_listed(self):
        status = pillar_390_status()
        checks = status["checks_active"]
        assert "version_sync" in checks
        assert "test_count_sync" in checks
