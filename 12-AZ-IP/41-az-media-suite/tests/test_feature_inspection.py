# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_media_suite.feature_inspection import scan_app_features


def test_scan_app_features_finds_signatures(tmp_path):
    (tmp_path / "app.js").write_text(
        "window.addEventListener('click', onClick);\n"
        "fetch('/api/data').then(r => r.json());\n"
        "localStorage.setItem('k', 'v');\n"
    )
    report = scan_app_features(tmp_path)
    assert report.files_scanned == 1
    features = report.features_present()
    assert "event_listener" in features
    assert "fetch_network_call" in features
    assert "local_storage" in features


def test_scan_app_features_findings_cite_file_and_line(tmp_path):
    (tmp_path / "index.html").write_text("<html>\n<body>\n<script>fetch('/x')</script>\n</body>\n</html>\n")
    report = scan_app_features(tmp_path)
    fetch_findings = report.findings_for("fetch_network_call")
    assert len(fetch_findings) == 1
    assert fetch_findings[0].file == "index.html"
    assert fetch_findings[0].line == 3
    assert "fetch(" in fetch_findings[0].snippet


def test_scan_app_features_ignores_non_source_files(tmp_path):
    (tmp_path / "data.json").write_text('{"fetch(": true}')
    report = scan_app_features(tmp_path)
    assert report.files_scanned == 0
    assert report.findings == []


def test_scan_app_features_requires_directory(tmp_path):
    missing = tmp_path / "does-not-exist"
    with pytest.raises(NotADirectoryError):
        scan_app_features(missing)
