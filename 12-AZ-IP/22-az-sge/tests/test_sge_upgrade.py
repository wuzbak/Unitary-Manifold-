# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Upgrade tests for the AxiomZero SGE app."""

from __future__ import annotations

import json
import os
import sys
import urllib.error

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from az_sge.engine.cve_feed import (
    CISA_KEV_URL,
    NVD_API_BASE,
    assess_threat,
    fetch_cisa_kev,
    fetch_recent_cves,
)
from az_sge.engine.sbom_generator import format_sbom_spdx, generate_sbom


class _FakeResponse:
    def __init__(self, payload: object):
        self._payload = payload

    def read(self) -> bytes:
        if isinstance(self._payload, bytes):
            return self._payload
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_feed_constants_are_stable():
    assert NVD_API_BASE == "https://services.nvd.nist.gov/rest/json/cves/2.0"
    assert CISA_KEV_URL.endswith("known_exploited_vulnerabilities.json")


def test_fetch_recent_cves_success(monkeypatch):
    payload = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-1",
                    "published": "2026-01-01",
                    "descriptions": [{"lang": "en", "value": "critical bug"}],
                    "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 9.8}}]},
                }
            },
            {
                "cve": {
                    "id": "CVE-2",
                    "published": "2026-01-02",
                    "descriptions": [{"lang": "en", "value": "low bug"}],
                    "metrics": {"cvssMetricV31": [{"cvssData": {"baseScore": 5.0}}]},
                }
            },
        ]
    }
    seen = {}

    def fake_urlopen(url, timeout=8):
        seen["url"] = url
        return _FakeResponse(payload)

    monkeypatch.setattr("az_sge.engine.cve_feed.urllib.request.urlopen", fake_urlopen)
    results = fetch_recent_cves(days_back=3, cvss_min=7.0)
    assert results == [
        {
            "cve_id": "CVE-1",
            "cvss_score": 9.8,
            "description": "critical bug",
            "published": "2026-01-01",
        }
    ]
    assert seen["url"].startswith(NVD_API_BASE)


def test_fetch_recent_cves_uses_v30_when_needed(monkeypatch):
    payload = {
        "vulnerabilities": [
            {
                "cve": {
                    "id": "CVE-3",
                    "published": "2026-01-03",
                    "descriptions": [{"lang": "en", "value": "mid bug"}],
                    "metrics": {"cvssMetricV30": [{"cvssData": {"baseScore": 8.1}}]},
                }
            }
        ]
    }
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: _FakeResponse(payload),
    )
    results = fetch_recent_cves()
    assert results[0]["cvss_score"] == 8.1


def test_fetch_recent_cves_handles_rate_limit(monkeypatch):
    def fake_urlopen(url, timeout=8):
        raise urllib.error.HTTPError(url, 429, "rate", {}, None)

    monkeypatch.setattr("az_sge.engine.cve_feed.urllib.request.urlopen", fake_urlopen)
    assert fetch_recent_cves() == []


def test_fetch_recent_cves_handles_url_error(monkeypatch):
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: (_ for _ in ()).throw(urllib.error.URLError("offline")),
    )
    assert fetch_recent_cves() == []


def test_fetch_recent_cves_handles_bad_json(monkeypatch):
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: _FakeResponse(b"not-json"),
    )
    assert fetch_recent_cves() == []


def test_fetch_recent_cves_handles_missing_metrics(monkeypatch):
    payload = {"vulnerabilities": [{"cve": {"id": "CVE-4", "descriptions": [], "metrics": {}}}]}
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: _FakeResponse(payload),
    )
    assert fetch_recent_cves(cvss_min=0.1) == []


def test_fetch_cisa_kev_success(monkeypatch):
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: _FakeResponse({"vulnerabilities": [{"cveID": "CVE-5"}]}),
    )
    assert fetch_cisa_kev() == [{"cveID": "CVE-5"}]


def test_fetch_cisa_kev_accepts_list_payload(monkeypatch):
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: _FakeResponse([{"cveID": "CVE-6"}]),
    )
    assert fetch_cisa_kev() == [{"cveID": "CVE-6"}]


def test_fetch_cisa_kev_handles_errors(monkeypatch):
    monkeypatch.setattr(
        "az_sge.engine.cve_feed.urllib.request.urlopen",
        lambda url, timeout=8: (_ for _ in ()).throw(urllib.error.URLError("offline")),
    )
    assert fetch_cisa_kev() == []


@pytest.mark.parametrize(
    ("score", "level", "priority"),
    [
        (9.7, "CRITICAL", "IMMEDIATE"),
        (8.4, "HIGH", "URGENT"),
        (7.2, "ELEVATED", "SCHEDULED"),
        (5.9, "MODERATE", "MONITOR"),
    ],
)
def test_assess_threat_thresholds(score, level, priority):
    result = assess_threat("CVE-X", score)
    assert result["threat_level"] == level
    assert result["remediation_priority"] == priority
    assert "topology" in result["um_topology_note"]


def test_assess_threat_echoes_identity():
    result = assess_threat("CVE-2026-0001", 9.0)
    assert result["cve_id"] == "CVE-2026-0001"
    assert result["cvss_score"] == 9.0


def test_generate_sbom_empty_directory(tmp_path):
    sbom = generate_sbom(str(tmp_path))
    assert sbom["packages"] == []
    assert sbom["relationships"] == []
    assert sbom["SPDXID"] == "SPDXRef-DOCUMENT"


def test_generate_sbom_parses_requirements(tmp_path):
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\nflask>=3.0.0\n", encoding="utf-8")
    sbom = generate_sbom(str(tmp_path))
    names = {pkg["name"] for pkg in sbom["packages"]}
    assert {"requests", "flask"} <= names


def test_generate_sbom_parses_package_json(tmp_path):
    (tmp_path / "package.json").write_text(
        json.dumps({"dependencies": {"react": "^19.0.0"}, "devDependencies": {"vite": "5.4.0"}}),
        encoding="utf-8",
    )
    sbom = generate_sbom(str(tmp_path))
    ecosystems = {pkg["ecosystem"] for pkg in sbom["packages"]}
    assert "npm" in ecosystems
    assert {pkg["name"] for pkg in sbom["packages"]} == {"react", "vite"}


def test_generate_sbom_parses_cargo_toml(tmp_path):
    (tmp_path / "Cargo.toml").write_text(
        "[package]\nname='demo'\n[dependencies]\nserde = '1.0.0'\nreqwest = { version = '0.12.0' }\n",
        encoding="utf-8",
    )
    sbom = generate_sbom(str(tmp_path))
    assert {pkg["name"] for pkg in sbom["packages"]} == {"serde", "reqwest"}


def test_generate_sbom_scans_recursively(tmp_path):
    nested = tmp_path / "service"
    nested.mkdir()
    (nested / "requirements.txt").write_text("numpy==1.26.0\n", encoding="utf-8")
    sbom = generate_sbom(str(tmp_path))
    assert sbom["packages"][0]["path"].endswith("requirements.txt")


def test_generate_sbom_assigns_unique_spdx_ids(tmp_path):
    (tmp_path / "requirements.txt").write_text("a==1.0\nb==2.0\n", encoding="utf-8")
    sbom = generate_sbom(str(tmp_path))
    ids = [pkg["SPDXID"] for pkg in sbom["packages"]]
    assert len(ids) == len(set(ids))


def test_relationships_describe_each_package(tmp_path):
    (tmp_path / "requirements.txt").write_text("a==1.0\n", encoding="utf-8")
    sbom = generate_sbom(str(tmp_path))
    assert sbom["relationships"][0]["relationshipType"] == "DESCRIBES"


def test_format_sbom_spdx_contains_document_tags(tmp_path):
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
    spdx = format_sbom_spdx(generate_sbom(str(tmp_path)))
    assert "SPDXVersion: SPDX-2.3" in spdx
    assert "DocumentName:" in spdx
    assert "PackageName: requests" in spdx


def test_format_sbom_spdx_renders_relationships(tmp_path):
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n", encoding="utf-8")
    spdx = format_sbom_spdx(generate_sbom(str(tmp_path)))
    assert "Relationship: SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-1" in spdx


def test_format_sbom_spdx_handles_no_packages(tmp_path):
    spdx = format_sbom_spdx(generate_sbom(str(tmp_path)))
    assert spdx.startswith("SPDXVersion: SPDX-2.3")
