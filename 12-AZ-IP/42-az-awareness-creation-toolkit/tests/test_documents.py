# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_awareness_creation_toolkit.documents import (
    UnsupportedDocumentFormatError,
    inspect_repository_document,
)


def test_inspect_markdown_document():
    inspection = inspect_repository_document("12-AZ-IP/README.md")
    assert inspection.kind == "markdown"
    assert inspection.summary["heading_count"] > 0
    assert any(h["text"].startswith("Product registry") for h in inspection.summary["headings"])


def test_inspect_json_document():
    inspection = inspect_repository_document("12-AZ-IP/IP_REGISTRY.json")
    assert inspection.kind == "json"
    assert inspection.summary["type"] == "object"
    assert "products" in inspection.summary["top_level_keys"]


def test_inspect_yaml_document(tmp_path, monkeypatch):
    from az_awareness_creation_toolkit import _repo

    yaml_text = "a: 1\nb:\n  - x\n  - y\n"
    target = tmp_path / "sample.yaml"
    target.write_text(yaml_text, encoding="utf-8")
    monkeypatch.setattr(_repo, "_REPO_ROOT", tmp_path)
    inspection = inspect_repository_document("sample.yaml")
    assert inspection.kind == "yaml"
    assert inspection.summary["type"] == "object"
    assert "a" in inspection.summary["top_level_keys"]


def test_inspect_toml_document(tmp_path, monkeypatch):
    from az_awareness_creation_toolkit import _repo

    target = tmp_path / "sample.toml"
    target.write_text('[table]\nkey = "value"\n', encoding="utf-8")
    monkeypatch.setattr(_repo, "_REPO_ROOT", tmp_path)
    inspection = inspect_repository_document("sample.toml")
    assert inspection.kind == "toml"
    assert "table" in inspection.summary["top_level_keys"]


def test_inspect_csv_document(tmp_path, monkeypatch):
    from az_awareness_creation_toolkit import _repo

    target = tmp_path / "sample.csv"
    target.write_text("a,b,c\n1,2,3\n4,5,6\n", encoding="utf-8")
    monkeypatch.setattr(_repo, "_REPO_ROOT", tmp_path)
    inspection = inspect_repository_document("sample.csv")
    assert inspection.kind == "csv"
    assert inspection.summary["column_count"] == 3
    assert inspection.summary["row_count"] == 2


def test_inspect_markdown_front_matter(tmp_path, monkeypatch):
    from az_awareness_creation_toolkit import _repo

    text = "---\ntitle: Hello\ntags: [a, b]\n---\n# Heading\nBody text.\n"
    target = tmp_path / "doc.md"
    target.write_text(text, encoding="utf-8")
    monkeypatch.setattr(_repo, "_REPO_ROOT", tmp_path)
    inspection = inspect_repository_document("doc.md")
    assert "title" in inspection.summary["front_matter_keys"]
    assert inspection.summary["heading_count"] == 1


def test_unsupported_extension_raises():
    with pytest.raises(UnsupportedDocumentFormatError):
        inspect_repository_document("README_unsupported.exe")


def test_path_escape_is_rejected():
    with pytest.raises(UnsupportedDocumentFormatError):
        inspect_repository_document("../../../etc/passwd")


def test_missing_file_raises():
    with pytest.raises(UnsupportedDocumentFormatError):
        inspect_repository_document("12-AZ-IP/this-file-does-not-exist.md")
