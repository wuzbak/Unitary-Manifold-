# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Tests — Lane 3: Auditability.

Validates that:
- The claim queryability index loads and is structurally valid
- All ledger surface paths referenced in the index actually exist on disk
- All scored claims appear in ≥ 3 ledger surfaces
- Machine-readable surfaces are present for scored claims
- The provenance README is not stale (regression count not dramatically outdated)
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("yaml", reason="pyyaml required for auditability index tests")

import yaml  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "9-INFRASTRUCTURE" / "provenance" / "claim_queryability_index.yml"
PROVENANCE_README = ROOT / "9-INFRASTRUCTURE" / "provenance" / "README.md"

# Ledger surfaces that must exist as files on disk
REQUIRED_LEDGER_FILES = {
    "docs/CLAIM_MASTER_BOARD.md",
    "docs/TRUTH_LAYER.md",
    "docs/GATEKEEPER_SUMMARY.md",
    "docs/mas_tracker.yml",
    "docs/falsification/instrument_registry.yml",
    "docs/closure_quality_gate.yml",
    "3-FALSIFICATION/OBSERVATION_TRACKER.md",
    "3-FALSIFICATION/FALSIFICATION_REGISTER.md",
    "FALLIBILITY.md",
    "docs/CLAIM_LABEL_STANDARD.md",
}

SCORED_CLAIM_IDS = {"P1", "P2", "P3", "P4", "P28", "LITEBIRD-FALSIFIER"}


@pytest.fixture(scope="module")
def index():
    assert INDEX_PATH.exists(), f"Index not found: {INDEX_PATH}"
    data = yaml.safe_load(INDEX_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "Index must be a YAML mapping"
    return data


class TestIndexLoads:
    def test_loads(self, index):
        assert index is not None

    def test_has_version(self, index):
        assert "version" in index

    def test_has_ledger_surfaces(self, index):
        assert "ledger_surfaces" in index
        assert len(index["ledger_surfaces"]) >= 5

    def test_has_claims(self, index):
        assert "claims" in index
        assert len(index["claims"]) >= 5

    def test_has_rules(self, index):
        assert "rules" in index


class TestLedgerSurfacesExistOnDisk:
    def test_required_ledger_files_present(self):
        missing = []
        for rel_path in REQUIRED_LEDGER_FILES:
            if not (ROOT / rel_path).exists():
                missing.append(rel_path)
        assert not missing, (
            "Required ledger surface files missing from disk:\n"
            + "\n".join(missing)
        )

    def test_all_indexed_surfaces_exist(self, index):
        missing = []
        for surface in index.get("ledger_surfaces", []):
            path = ROOT / surface.get("path", "")
            if not path.exists():
                missing.append(surface.get("path", "<no-path>"))
        assert not missing, (
            "Indexed ledger surfaces missing from disk:\n" + "\n".join(missing)
        )


class TestClaimCoverage:
    def test_scored_claims_in_index(self, index):
        claim_ids = {c["id"] for c in index.get("claims", [])}
        missing = SCORED_CLAIM_IDS - claim_ids
        assert not missing, f"Scored claims missing from queryability index: {missing}"

    def test_minimum_surfaces_per_claim(self, index):
        min_surfaces = index.get("rules", {}).get("minimum_surfaces_per_claim", 3)
        violations = []
        for claim in index.get("claims", []):
            surfaces = claim.get("ledger_surfaces", [])
            if len(surfaces) < min_surfaces:
                violations.append(
                    f"[{claim['id']}] Only {len(surfaces)} surfaces (min {min_surfaces})"
                )
        assert not violations, (
            "Claims with insufficient ledger coverage:\n" + "\n".join(violations)
        )

    def test_machine_readable_surface_for_scored_claims(self, index):
        min_mr = index.get("rules", {}).get("minimum_machine_readable_for_scored_claims", 1)
        violations = []
        for claim in index.get("claims", []):
            if claim["id"] in SCORED_CLAIM_IDS:
                mr = claim.get("machine_readable_surfaces", [])
                if len(mr) < min_mr:
                    violations.append(
                        f"[{claim['id']}] Only {len(mr)} machine-readable surfaces (min {min_mr})"
                    )
        assert not violations, (
            "Scored claims missing machine-readable ledger surfaces:\n"
            + "\n".join(violations)
        )


class TestProvenanceReadme:
    def test_readme_exists(self):
        assert PROVENANCE_README.exists(), f"Provenance README not found: {PROVENANCE_README}"

    def test_readme_not_stale(self):
        text = PROVENANCE_README.read_text(encoding="utf-8")
        # The README should reference a regression count > 30000
        # Counts may appear as "32 857 passed" (with space) or "32857 passed"
        import re
        # Match digit groups optionally separated by a single space, followed by "passed"
        counts = re.findall(r"(\d[\d ]{2,6}\d)\s*passed", text)
        # Strip spaces and convert to int
        int_counts = []
        for c in counts:
            try:
                int_counts.append(int(c.replace(" ", "")))
            except ValueError:
                pass
        assert int_counts, "Provenance README does not contain a regression passed count"
        max_count = max(int_counts)
        assert max_count >= 30000, (
            f"Provenance README regression count {max_count} appears stale (< 30000)"
        )
