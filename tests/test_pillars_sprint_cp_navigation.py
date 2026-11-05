# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_sprint_cp_pillar_navigation_stubs_exist() -> None:
    for pillar in range(1097, 1103):
        readme = REPO_ROOT / "PILLARS" / f"P{pillar}" / "README.md"
        assert readme.exists()
        text = readme.read_text(encoding="utf-8")
        assert f"# Pillar {pillar} —" in text
        assert "**Framework version:** v37.2" in text
        assert "docs/mas_tracker.yml" in text


def test_pillars_index_lists_sprint_cp_entries() -> None:
    text = (REPO_ROOT / "PILLARS" / "README.md").read_text(encoding="utf-8")
    assert "**Unitary Manifold v" in text
    assert re.search(
        r"\*\*Unitary Manifold v[^|]+\| Generated: \d{4}-\d{2}-\d{2} "
        r"\| Total pillars: \d+\*\*",
        text,
    )
    for pillar in range(1097, 1103):
        assert f"| [{pillar}](P{pillar}/README.md) |" in text
    for pillar in (1133, 1134):
        assert f"| [{pillar}](P{pillar}/README.md) |" in text
