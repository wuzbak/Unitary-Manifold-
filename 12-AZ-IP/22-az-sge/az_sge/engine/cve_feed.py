# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Live CVE and KEV feed helpers with offline-safe failure handling."""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

NVD_API_BASE = "https://services.nvd.nist.gov/rest/json/cves/2.0"
CISA_KEV_URL = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"


def _load_json(url: str, timeout: int = 8) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_recent_cves(days_back: int = 7, cvss_min: float = 7.0) -> list[dict]:
    """Fetch recent NVD CVEs, returning an empty list on failure."""
    now = datetime.now(timezone.utc)
    start = now - timedelta(days=max(1, int(days_back)))
    query = urllib.parse.urlencode({
        "pubStartDate": start.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "pubEndDate": now.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "resultsPerPage": 50,
    })
    try:
        payload = _load_json(f"{NVD_API_BASE}?{query}")
    except urllib.error.HTTPError as exc:
        if exc.code == 429:
            return []
        return []
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError, ValueError):
        return []
    except Exception:  # pragma: no cover - defensive
        return []

    items: list[dict] = []
    for vuln in payload.get("vulnerabilities", []):
        cve = vuln.get("cve", {})
        metrics = cve.get("metrics", {})
        score = 0.0
        for bucket in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
            entries = metrics.get(bucket, [])
            if entries:
                score = float(entries[0].get("cvssData", {}).get("baseScore", 0.0))
                break
        if score < float(cvss_min):
            continue
        descriptions = cve.get("descriptions", [])
        description = next((entry.get("value", "") for entry in descriptions if entry.get("lang") == "en"), "")
        items.append({
            "cve_id": cve.get("id", "UNKNOWN"),
            "cvss_score": score,
            "description": description,
            "published": cve.get("published"),
        })
    return items


def fetch_cisa_kev() -> list[dict]:
    """Fetch the CISA KEV feed, returning [] on failure."""
    try:
        payload = _load_json(CISA_KEV_URL)
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, TimeoutError, ValueError):
        return []
    except Exception:  # pragma: no cover - defensive
        return []
    if isinstance(payload, dict):
        vulns = payload.get("vulnerabilities", [])
        return vulns if isinstance(vulns, list) else []
    return payload if isinstance(payload, list) else []


def assess_threat(cve_id: str, cvss_score: float) -> dict:
    """Map a CVE to response urgency plus a compactification-topology metaphor."""
    score = float(cvss_score)
    if score >= 9.0:
        threat_level = "CRITICAL"
        remediation_priority = "IMMEDIATE"
        um_topology_note = "Compactification topology singularity metaphor: exposed surface requires immediate closure."
    elif score >= 8.0:
        threat_level = "HIGH"
        remediation_priority = "URGENT"
        um_topology_note = "High-curvature topology metaphor: patch before the exposed manifold widens."
    elif score >= 7.0:
        threat_level = "ELEVATED"
        remediation_priority = "SCHEDULED"
        um_topology_note = "Moderate topology surface-curvature metaphor: harden the boundary on the next maintenance window."
    else:
        threat_level = "MODERATE"
        remediation_priority = "MONITOR"
        um_topology_note = "Low-curvature topology metaphor: monitor local drift and preserve closure evidence."
    return {
        "cve_id": cve_id,
        "cvss_score": score,
        "threat_level": threat_level,
        "remediation_priority": remediation_priority,
        "um_topology_note": um_topology_note,
    }
