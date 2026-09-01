# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Upgrade tests for the EIGE governance app."""

from __future__ import annotations

import json
import os
import sys
import urllib.error

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from eige.engine.hils_audit_trail import AuditEntry, create_audit_entry, format_audit_log
from eige.engine.open_election_data import (
    ANOMALY_DETECTORS,
    HARVARD_DATAVERSE_BASE,
    OPEN_ELECTIONS_BASE,
    compute_integrity_score,
    detect_anomaly,
    fetch_election_results,
)


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


def test_constants_are_stable():
    assert OPEN_ELECTIONS_BASE == "https://openelections.net/results/"
    assert HARVARD_DATAVERSE_BASE == "https://dataverse.harvard.edu/api/access/datafile/"
    assert ANOMALY_DETECTORS == ["turnout_spike", "undervote_rate", "precinct_variance", "timestamp_gaps"]


def test_legacy_eige_import_path_works():
    from EIGE.src.public_trust_index import PublicTrustIndexBuilder

    assert PublicTrustIndexBuilder is not None


def test_fetch_election_results_from_primary(monkeypatch):
    def fake_urlopen(url, timeout=5):
        assert url == f"{OPEN_ELECTIONS_BASE}2024/wa/"
        return _FakeResponse({"results": [{"candidate": "A"}], "metrics": {"undervote_rate": 0.02}})

    monkeypatch.setattr("eige.engine.open_election_data.urllib.request.urlopen", fake_urlopen)
    result = fetch_election_results("wa", 2024)
    assert result["source"] == "open_elections"
    assert result["fetched"] is True
    assert result["results"][0]["candidate"] == "A"


def test_fetch_election_results_falls_back_to_harvard(monkeypatch):
    calls = []

    def fake_urlopen(url, timeout=5):
        calls.append(url)
        if len(calls) == 1:
            raise urllib.error.URLError("offline")
        return _FakeResponse({"results": [{"candidate": "B"}]})

    monkeypatch.setattr("eige.engine.open_election_data.urllib.request.urlopen", fake_urlopen)
    result = fetch_election_results("TX", 2022)
    assert result["source"] == "harvard_dataverse"
    assert len(calls) == 2
    assert calls[1] == f"{HARVARD_DATAVERSE_BASE}2022-tx"


def test_fetch_election_results_returns_fallback_on_total_failure(monkeypatch):
    def fake_urlopen(url, timeout=5):
        raise urllib.error.URLError("down")

    monkeypatch.setattr("eige.engine.open_election_data.urllib.request.urlopen", fake_urlopen)
    result = fetch_election_results("ca", 2020)
    assert result["source"] == "fallback"
    assert result["fetched"] is False
    assert result["results"] == []
    assert "open_elections" in result["error"]


def test_fetch_election_results_wraps_non_dict_payload(monkeypatch):
    monkeypatch.setattr(
        "eige.engine.open_election_data.urllib.request.urlopen",
        lambda url, timeout=5: _FakeResponse([{"candidate": "C"}]),
    )
    result = fetch_election_results("ny", 2024)
    assert result["results"] == [{"candidate": "C"}]


def test_fetch_election_results_handles_invalid_json(monkeypatch):
    monkeypatch.setattr(
        "eige.engine.open_election_data.urllib.request.urlopen",
        lambda url, timeout=5: _FakeResponse(b"not-json"),
    )
    result = fetch_election_results("fl", 2024)
    assert result["source"] == "fallback"
    assert result["fetched"] is False


def test_turnout_spike_detected():
    finding = detect_anomaly("turnout_spike", {"turnout_change_pct": 21.0})
    assert finding["detected"] is True
    assert finding["severity"] > 0.0


def test_turnout_spike_not_detected():
    finding = detect_anomaly("turnout_spike", {"turnout_change_pct": 4.5})
    assert finding["detected"] is False


def test_undervote_rate_detected():
    finding = detect_anomaly("undervote_rate", {"undervote_rate": 0.09})
    assert finding["detected"] is True
    assert "elevated" in finding["description"]


def test_undervote_rate_not_detected():
    finding = detect_anomaly("undervote_rate", {"undervote_rate": 0.01})
    assert finding["detected"] is False


def test_precinct_variance_detected():
    finding = detect_anomaly("precinct_variance", {"precinct_variance": 0.22})
    assert finding["detected"] is True


def test_precinct_variance_not_detected():
    finding = detect_anomaly("precinct_variance", {"precinct_variance": 0.05})
    assert finding["detected"] is False


def test_timestamp_gaps_detected_by_gap():
    finding = detect_anomaly("timestamp_gaps", {"max_timestamp_gap_minutes": 120.0})
    assert finding["detected"] is True


def test_timestamp_gaps_detected_by_missing_batches():
    finding = detect_anomaly("timestamp_gaps", {"max_timestamp_gap_minutes": 5.0, "missing_batch_count": 2})
    assert finding["detected"] is True


def test_timestamp_gaps_not_detected():
    finding = detect_anomaly("timestamp_gaps", {"max_timestamp_gap_minutes": 15.0, "missing_batch_count": 0})
    assert finding["detected"] is False


def test_unknown_detector_returns_safe_result():
    finding = detect_anomaly("mystery", {})
    assert finding == {
        "type": "mystery",
        "detected": False,
        "severity": 0.0,
        "description": "Unknown detector: mystery",
    }


def test_compute_integrity_score_nominal_case():
    score = compute_integrity_score({"metrics": {"turnout_change_pct": 2.0, "undervote_rate": 0.01, "precinct_variance": 0.02, "max_timestamp_gap_minutes": 10.0}})
    assert score["score"] == 1.0
    assert score["anomalies"] == []
    assert score["verdict"] == "Integrity checks nominal"


def test_compute_integrity_score_detects_multiple_anomalies():
    score = compute_integrity_score({"metrics": {"turnout_change_pct": 20.0, "undervote_rate": 0.08, "precinct_variance": 0.19, "max_timestamp_gap_minutes": 150.0}})
    assert score["score"] < 0.65
    assert len(score["anomalies"]) == 4
    assert score["pillar_ref"] == "P018-governance"
    assert score["pentad_coupling"] == pytest.approx(35 / 74)


def test_compute_integrity_score_accepts_flat_input():
    score = compute_integrity_score({"turnout_change_pct": 16.0})
    assert score["anomalies"][0]["type"] == "turnout_spike"


def test_audit_entry_is_dataclass_instance():
    entry = create_audit_entry("publish-report", {"county": "King"})
    assert isinstance(entry, AuditEntry)
    assert len(entry.data_hash) == 64


def test_audit_entry_hash_is_order_independent():
    left = create_audit_entry("publish", {"a": 1, "b": 2})
    right = create_audit_entry("publish", {"b": 2, "a": 1})
    assert left.data_hash == right.data_hash


def test_audit_entry_reviewer_required_for_manual_override():
    entry = create_audit_entry("manual-override", {"reviewer": "needed"})
    assert entry.reviewer_required is True


def test_audit_entry_reviewer_optional_for_automatic_action():
    entry = create_audit_entry("nightly-sync", {"batch": 4})
    assert entry.reviewer_required is False


def test_format_audit_log_empty_message():
    assert format_audit_log([]) == "HILS audit log: no entries"


def test_format_audit_log_renders_entries():
    entries = [
        AuditEntry("2026-01-01T00:00:00+00:00", "certify", "a" * 64, True),
        AuditEntry("2026-01-01T01:00:00+00:00", "publish", "b" * 64, False),
    ]
    formatted = format_audit_log(entries)
    assert formatted.startswith("HILS audit log")
    assert "certify" in formatted
    assert "REVIEW" in formatted
    assert "AUTO" in formatted
