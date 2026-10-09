# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Link audits cover repository documents, not installed tools or build output."""

from TOOLS.audit.check_internal_links import iter_markdown_files


def test_document_discovery_prunes_external_and_generated_directories(tmp_path):
    included = ["README.md", "docs/guide.md", ".github/pull_request_template.md"]
    excluded = [
        "lean4/.lake/packages/mathlib/README.md",
        "node_modules/library/README.md",
        ".venv/site-packages/library/README.md",
        "build/generated/README.md",
        "dist/README.md",
        ".um-arts/attempt/source/README.md",
        ".um-arts-test-work/repo/README.md",
    ]
    for relative in included + excluded:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Fixture\n", encoding="utf-8")
    assert {path.relative_to(tmp_path).as_posix() for path in iter_markdown_files(tmp_path)} == set(included)


def test_document_discovery_does_not_follow_directory_symlinks(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "README.md").write_text("# Fixture\n", encoding="utf-8")
    root = tmp_path / "repo"
    root.mkdir()
    (root / "external").symlink_to(outside, target_is_directory=True)
    assert iter_markdown_files(root) == []
