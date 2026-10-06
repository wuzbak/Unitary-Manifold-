# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Open election-data accessors and statistical screening helpers (legacy API).

v22 (red-team finding F6): v21 fetched from URLs that do not exist
(``openelections.net/results/{year}/{state}/``) and, on any failure,
silently returned fixed placeholder metrics that then scored as "nominal".
Now:

* ``fetch_election_results`` takes an explicit OpenElections repository path
  or a Harvard Dataverse file id (MIT Election Data and Science Lab), fetches
  only from allow-listed HTTPS hosts via :mod:`eige.data.open_data`, records
  provenance (URL, SHA-256, time), and raises :class:`OpenDataError` on any
  failure.  There is no fallback data.
* Screening output is an investigation lead, never evidence of fraud.
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from eige.data.open_data import (
    OpenDataError,
    dataverse_url,
    fetch,
    openelections_url,
    parse_medsl_county_csv,
    parse_openelections_csv,
)

OPEN_ELECTIONS_BASE = "https://raw.githubusercontent.com/openelections/"
HARVARD_DATAVERSE_BASE = "https://dataverse.harvard.edu/api/access/datafile/"
ANOMALY_DETECTORS = ["turnout_spike", "undervote_rate", "precinct_variance", "timestamp_gaps"]
_PENTAD_COUPLING = 35 / 74
EVIDENTIARY_STATUS = "investigation_lead_not_evidence"
SCREENING_DISCLAIMER = (
    "Statistical screens flag results for human follow-up. A flag is not evidence "
    "of fraud or error, and the absence of a flag is not evidence of correctness."
)

__all__ = [
    "ANOMALY_DETECTORS",
    "HARVARD_DATAVERSE_BASE",
    "OPEN_ELECTIONS_BASE",
    "OpenDataError",
    "compute_integrity_score",
    "detect_anomaly",
    "fetch_election_results",
]


def _clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, float(value)))


def fetch_election_results(
    state: str,
    year: int,
    *,
    openelections_path: Optional[str] = None,
    dataverse_file_id: Optional[int] = None,
    expected_sha256: Optional[str] = None,
    level: str = "county",
    opener: Optional[Callable[[str, float], bytes]] = None,
) -> dict[str, Any]:
    """Fetch and parse real results for ``state``/``year`` from a named source.

    Exactly one of ``openelections_path`` (a CSV path inside
    ``openelections/openelections-data-{state}``, e.g.
    ``"2020/20201103__wa__general__county.csv"``) or ``dataverse_file_id``
    (an MEDSL county-returns file) must be given.  Raises
    :class:`OpenDataError` on any failure — there is no fallback.
    """
    if (openelections_path is None) == (dataverse_file_id is None):
        raise OpenDataError("specify exactly one of openelections_path or dataverse_file_id")
    kwargs = {"expected_sha256": expected_sha256}
    if opener is not None:
        kwargs["opener"] = opener
    if openelections_path is not None:
        if not openelections_path.startswith(f"{int(year)}/"):
            raise OpenDataError(f"path {openelections_path!r} is not under year {year}")
        url = openelections_url(state, openelections_path)
        fetched = fetch(url, "openelections", **kwargs)
        rows = parse_openelections_csv(fetched.data, level=level)
        source = "open_elections"
    else:
        url = dataverse_url(dataverse_file_id)
        fetched = fetch(url, "medsl", **kwargs)
        prefix = state.strip().upper() + ":"
        rows = [r for r in parse_medsl_county_csv(fetched.data) if r.jurisdiction.startswith(prefix)]
        source = "harvard_dataverse"
    return {
        "state": state.strip().upper(),
        "year": int(year),
        "source": source,
        "fetched": True,
        "results": [dict(r.__dict__) for r in rows],
        "provenance": fetched.provenance.as_dict(),
        "url": url,
        "error": None,
    }


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
    """Aggregate statistical screens into a 0–1 screening score.

    The score summarises how many screens flagged; it is not a measure of
    election integrity.  Missing metrics raise ``ValueError`` rather than
    defaulting to "nominal".
    """
    metrics = results.get("metrics", results)
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("no screening metrics supplied; refusing to score empty data")
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
        verdict = "No screening leads raised"
    elif score >= 0.65:
        verdict = "Screening leads raised: human review recommended"
    else:
        verdict = "Multiple screening leads raised: prioritise for human review"
    return {
        "score": score,
        "anomalies": detected,
        "pentad_coupling": _PENTAD_COUPLING,
        "pillar_ref": "P018-governance",
        "verdict": verdict,
        "evidentiary_status": EVIDENTIARY_STATUS,
        "disclaimer": SCREENING_DISCLAIMER,
    }
