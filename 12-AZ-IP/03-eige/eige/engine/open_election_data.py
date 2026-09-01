# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Open election-data accessors and integrity scoring helpers."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

OPEN_ELECTIONS_BASE = "https://openelections.net/results/"
HARVARD_DATAVERSE_BASE = "https://dataverse.harvard.edu/api/access/datafile/"
ANOMALY_DETECTORS = ["turnout_spike", "undervote_rate", "precinct_variance", "timestamp_gaps"]
_PENTAD_COUPLING = 35 / 74


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


def _fallback_payload(state: str, year: int, reason: str) -> dict[str, Any]:
    return {
        "state": state.upper(),
        "year": int(year),
        "source": "fallback",
        "fetched": False,
        "results": [],
        "metrics": {
            "turnout_change_pct": 0.0,
            "undervote_rate": 0.01,
            "precinct_variance": 0.02,
            "max_timestamp_gap_minutes": 0.0,
        },
        "urls": {
            "open_elections": f"{OPEN_ELECTIONS_BASE}{year}/{state.lower()}/",
            "harvard_dataverse": f"{HARVARD_DATAVERSE_BASE}{year}-{state.lower()}",
        },
        "error": reason,
    }


def _read_json(url: str, timeout: int = 5) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw)


def fetch_election_results(state: str, year: int) -> dict[str, Any]:
    """Fetch election results with graceful network fallback."""
    state_code = state.strip().lower()
    open_url = f"{OPEN_ELECTIONS_BASE}{year}/{state_code}/"
    dataverse_url = f"{HARVARD_DATAVERSE_BASE}{year}-{state_code}"
    errors: list[str] = []

    for source, url in (("open_elections", open_url), ("harvard_dataverse", dataverse_url)):
        try:
            payload = _read_json(url)
            if not isinstance(payload, dict):
                payload = {"results": payload}
            results = payload.get("results", payload.get("elections", []))
            metrics = payload.get("metrics", {})
            return {
                "state": state_code.upper(),
                "year": int(year),
                "source": source,
                "fetched": True,
                "results": results if isinstance(results, list) else [results],
                "metrics": metrics if isinstance(metrics, dict) else {},
                "urls": {
                    "open_elections": open_url,
                    "harvard_dataverse": dataverse_url,
                },
                "error": None,
            }
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError, ValueError) as exc:
            errors.append(f"{source}: {exc}")
        except Exception as exc:  # pragma: no cover - defensive
            errors.append(f"{source}: {exc}")

    return _fallback_payload(state_code, year, "; ".join(errors) or "unavailable")


def detect_anomaly(anomaly_type: str, data: dict[str, Any]) -> dict[str, Any]:
    """Detect a specific election-integrity anomaly."""
    key = anomaly_type.strip().lower()
    if key == "turnout_spike":
        delta = float(data.get("turnout_change_pct", 0.0))
        detected = delta > 15.0
        severity = _clamp(delta / 30.0)
        description = f"Turnout change {delta:.2f}% exceeds expected baseline." if detected else f"Turnout change {delta:.2f}% remains within expected bounds."
    elif key == "undervote_rate":
        rate = float(data.get("undervote_rate", 0.0))
        detected = rate > 0.05
        severity = _clamp(rate / 0.15)
        description = f"Undervote rate {rate:.2%} is elevated." if detected else f"Undervote rate {rate:.2%} is nominal."
    elif key == "precinct_variance":
        variance = float(data.get("precinct_variance", 0.0))
        detected = variance > 0.12
        severity = _clamp(variance / 0.3)
        description = f"Precinct variance {variance:.3f} suggests non-uniform reporting." if detected else f"Precinct variance {variance:.3f} is stable."
    elif key == "timestamp_gaps":
        gap = float(data.get("max_timestamp_gap_minutes", 0.0))
        missing = int(data.get("missing_batch_count", 0))
        detected = gap > 60.0 or missing > 0
        severity = _clamp(max(gap / 180.0, missing / 5.0))
        description = (
            f"Timestamp continuity gap {gap:.1f} minutes with {missing} missing batches."
            if detected else
            f"Timestamp continuity gap {gap:.1f} minutes with no missing batches."
        )
    else:
        return {
            "type": anomaly_type,
            "detected": False,
            "severity": 0.0,
            "description": f"Unknown detector: {anomaly_type}",
        }

    return {
        "type": key,
        "detected": detected,
        "severity": round(severity, 4),
        "description": description,
    }


def compute_integrity_score(results: dict[str, Any]) -> dict[str, Any]:
    """Aggregate anomaly detectors into a 0–1 integrity score."""
    metrics = results.get("metrics", results)
    detected: list[dict[str, Any]] = []
    severities = []
    for detector in ANOMALY_DETECTORS:
        finding = detect_anomaly(detector, metrics)
        if finding["detected"]:
            detected.append(finding)
        severities.append(float(finding["severity"]) if finding["detected"] else 0.0)

    penalty = sum(severities) / len(ANOMALY_DETECTORS) if ANOMALY_DETECTORS else 0.0
    score = round(_clamp(1.0 - penalty), 4)
    if score >= 0.85:
        verdict = "Integrity checks nominal"
    elif score >= 0.65:
        verdict = "Review recommended"
    else:
        verdict = "Escalate for manual audit"
    return {
        "score": score,
        "anomalies": detected,
        "pentad_coupling": _PENTAD_COUPLING,
        "pillar_ref": "P018-governance",
        "verdict": verdict,
    }
