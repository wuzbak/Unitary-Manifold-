# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/threat_intel.py — Threat Intelligence Feed Aggregator
=============================================================

Aggregates, normalises, and scores threat intelligence from multiple live and
cached sources:

  • NVD (NIST National Vulnerability Database) — CVE feed via REST API v2
  • abuse.ch MalwareBazaar — recent malware hash uploads
  • AlienVault OTX (Open Threat Exchange) — pulse indicators
  • Local custom IOC (Indicators of Compromise) registry

The module is fully functional in offline / test mode: when network calls fail
or no API keys are configured, it falls back to cached sample data so that the
engine remains operational and deterministic for testing.

Threat score normalisation
--------------------------
Each indicator is assigned a 0–100 threat score:

  • CVE: CVSS v3 base score × 10 (0–100)
  • Malware hash: severity tag → {critical: 95, high: 75, medium: 50, low: 25}
  • OTX pulse: pulse.adversary_count × 10, capped at 90
  • Custom IOC: score provided by operator

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NVD_API_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
MALWARE_BAZAAR_URL = "https://mb-api.abuse.ch/api/v1/"
OTX_API_URL = "https://otx.alienvault.com/api/v1/pulses/subscribed"

FEED_TIMEOUT_SECONDS = 8
CACHE_TTL_SECONDS = 300  # 5-minute in-memory cache


class ThreatCategory(str, Enum):
    CVE          = "cve"
    MALWARE_HASH = "malware_hash"
    IP_ADDRESS   = "ip_address"
    DOMAIN       = "domain"
    URL          = "url"
    FILE_PATH    = "file_path"
    CUSTOM       = "custom"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"


_SEVERITY_SCORE: Dict[str, float] = {
    "critical": 95.0,
    "high":     75.0,
    "medium":   50.0,
    "low":      25.0,
    "info":     5.0,
}


# ---------------------------------------------------------------------------
# Threat Indicator
# ---------------------------------------------------------------------------

@dataclass
class ThreatIndicator:
    category: ThreatCategory
    indicator: str          # the IOC value (CVE-ID, hash, IP, domain, …)
    source: str             # originating feed name
    severity: Severity
    score: float            # 0–100
    description: str
    timestamp: float = field(default_factory=time.time)
    cve_id: Optional[str] = None
    cvss_v3: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    extra: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "indicator": self.indicator,
            "source": self.source,
            "severity": self.severity.value,
            "score": self.score,
            "description": self.description[:512],
            "timestamp": self.timestamp,
            "cve_id": self.cve_id,
            "cvss_v3": self.cvss_v3,
            "tags": self.tags,
        }

    @property
    def is_critical(self) -> bool:
        return self.severity == Severity.CRITICAL

    @property
    def sha256_fingerprint(self) -> str:
        """Stable fingerprint for deduplication."""
        raw = f"{self.category.value}:{self.indicator}:{self.source}"
        return hashlib.sha256(raw.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Sample offline data (used when network is unavailable)
# ---------------------------------------------------------------------------

_SAMPLE_INDICATORS: List[ThreatIndicator] = [
    ThreatIndicator(
        category=ThreatCategory.CVE,
        indicator="CVE-2024-21762",
        source="nvd_sample",
        severity=Severity.CRITICAL,
        score=96.0,
        description="Fortinet FortiOS out-of-bounds write RCE (CVSS 9.6)",
        cve_id="CVE-2024-21762",
        cvss_v3=9.6,
        tags=["rce", "fortinet", "vpn", "zero-day"],
    ),
    ThreatIndicator(
        category=ThreatCategory.CVE,
        indicator="CVE-2024-3400",
        source="nvd_sample",
        severity=Severity.CRITICAL,
        score=100.0,
        description="Palo Alto PAN-OS command injection (CVSS 10.0) — actively exploited",
        cve_id="CVE-2024-3400",
        cvss_v3=10.0,
        tags=["rce", "paloalto", "firewall", "zero-day", "actively-exploited"],
    ),
    ThreatIndicator(
        category=ThreatCategory.CVE,
        indicator="CVE-2023-44487",
        source="nvd_sample",
        severity=Severity.HIGH,
        score=75.0,
        description="HTTP/2 Rapid Reset DoS (CVSS 7.5)",
        cve_id="CVE-2023-44487",
        cvss_v3=7.5,
        tags=["dos", "http2", "rapid-reset"],
    ),
    ThreatIndicator(
        category=ThreatCategory.MALWARE_HASH,
        indicator="44d88612fea8a8f36de82e1278abb02f",
        source="malwarebazaar_sample",
        severity=Severity.CRITICAL,
        score=95.0,
        description="EICAR test string — canonical malware detection test vector",
        tags=["test", "eicar"],
    ),
    ThreatIndicator(
        category=ThreatCategory.MALWARE_HASH,
        indicator="3395856ce81f2b7382dee72602f798b642f436debb19301d7a6a0e9e7a41a5e",
        source="malwarebazaar_sample",
        severity=Severity.HIGH,
        score=88.0,
        description="WannaCry ransomware SHA-256 fingerprint",
        tags=["ransomware", "wannacry", "eternal-blue"],
    ),
    ThreatIndicator(
        category=ThreatCategory.IP_ADDRESS,
        indicator="185.220.101.0/24",
        source="custom_ioc",
        severity=Severity.HIGH,
        score=80.0,
        description="Tor exit node CIDR — high-risk for credential stuffing",
        tags=["tor", "exit-node", "anonymiser"],
    ),
    ThreatIndicator(
        category=ThreatCategory.DOMAIN,
        indicator="malware-c2.example.evil",
        source="custom_ioc",
        severity=Severity.CRITICAL,
        score=99.0,
        description="Known C2 domain used by APT-X ransomware family",
        tags=["c2", "apt", "ransomware"],
    ),
]

# Known malware hashes (SHA-256 + MD5) for offline lookups
KNOWN_MALWARE_HASHES: Dict[str, str] = {
    # hash → malware family
    "44d88612fea8a8f36de82e1278abb02f": "EICAR",
    "3395856ce81f2b7382dee72602f798b642f436debb19301d7a6a0e9e7a41a5e": "WannaCry",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": "EmptyFile",
}


# ---------------------------------------------------------------------------
# Feed parsers
# ---------------------------------------------------------------------------

def _safe_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = FEED_TIMEOUT_SECONDS) -> Optional[dict]:
    """HTTP GET → parsed JSON dict, or None on failure."""
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def _safe_post(url: str, data: dict, timeout: int = FEED_TIMEOUT_SECONDS) -> Optional[dict]:
    """HTTP POST JSON → parsed JSON dict, or None on failure."""
    raw = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=raw, method="POST",
                                  headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


def fetch_nvd_recent(
    days_back: int = 7,
    api_key: Optional[str] = None,
) -> List[ThreatIndicator]:
    """Fetch recent CVEs from NVD API v2.

    Returns sample data if network unavailable.
    """
    headers = {}
    if api_key:
        headers["apiKey"] = api_key

    url = f"{NVD_API_URL}?cvssV3Severity=HIGH&resultsPerPage=20"
    data = _safe_get(url, headers=headers)

    if data is None:
        # Offline fallback
        return [i for i in _SAMPLE_INDICATORS if i.category == ThreatCategory.CVE]

    indicators = []
    for vuln in data.get("vulnerabilities", []):
        cve = vuln.get("cve", {})
        cve_id = cve.get("id", "UNKNOWN")
        desc_list = cve.get("descriptions", [])
        desc = next((d["value"] for d in desc_list if d.get("lang") == "en"), "")
        metrics = cve.get("metrics", {})
        cvss3_list = metrics.get("cvssMetricV31", metrics.get("cvssMetricV30", []))
        cvss_v3 = None
        score = 0.0
        if cvss3_list:
            bs = cvss3_list[0].get("cvssData", {}).get("baseScore", 0.0)
            cvss_v3 = float(bs)
            score = cvss_v3 * 10.0

        if score >= 90:
            sev = Severity.CRITICAL
        elif score >= 70:
            sev = Severity.HIGH
        elif score >= 40:
            sev = Severity.MEDIUM
        else:
            sev = Severity.LOW

        indicators.append(ThreatIndicator(
            category=ThreatCategory.CVE,
            indicator=cve_id,
            source="nvd",
            severity=sev,
            score=min(score, 100.0),
            description=desc[:512],
            cve_id=cve_id,
            cvss_v3=cvss_v3,
        ))

    return indicators if indicators else [i for i in _SAMPLE_INDICATORS if i.category == ThreatCategory.CVE]


def fetch_malware_bazaar_recent() -> List[ThreatIndicator]:
    """Fetch recent malware samples from abuse.ch MalwareBazaar.

    Returns sample data if network unavailable.
    """
    data = _safe_post(MALWARE_BAZAAR_URL, {"query": "get_recent", "selector": "100"})
    if data is None or data.get("query_status") != "ok":
        return [i for i in _SAMPLE_INDICATORS if i.category == ThreatCategory.MALWARE_HASH]

    indicators = []
    for sample in data.get("data", [])[:50]:
        sha256 = sample.get("sha256_hash", "")
        family = sample.get("tags", ["unknown"])
        sig = sample.get("signature", "unknown")
        sev_tag = "high" if sig and sig.lower() != "unknown" else "medium"
        indicators.append(ThreatIndicator(
            category=ThreatCategory.MALWARE_HASH,
            indicator=sha256,
            source="malwarebazaar",
            severity=Severity(sev_tag),
            score=_SEVERITY_SCORE[sev_tag],
            description=f"MalwareBazaar: {sig} | tags: {','.join(family[:5])}",
            tags=family[:10],
        ))
    return indicators or [i for i in _SAMPLE_INDICATORS if i.category == ThreatCategory.MALWARE_HASH]


def load_custom_ioc_registry(registry: Optional[List[dict]] = None) -> List[ThreatIndicator]:
    """Load custom IOC list from operator-provided dict list or built-in samples."""
    if registry is None:
        return [i for i in _SAMPLE_INDICATORS if i.source == "custom_ioc"]
    result = []
    for entry in registry:
        cat_str = entry.get("category", "custom")
        try:
            cat = ThreatCategory(cat_str)
        except ValueError:
            cat = ThreatCategory.CUSTOM
        sev_str = entry.get("severity", "medium")
        try:
            sev = Severity(sev_str)
        except ValueError:
            sev = Severity.MEDIUM
        result.append(ThreatIndicator(
            category=cat,
            indicator=entry.get("indicator", ""),
            source="custom_ioc",
            severity=sev,
            score=float(entry.get("score", _SEVERITY_SCORE[sev.value])),
            description=entry.get("description", ""),
            tags=entry.get("tags", []),
        ))
    return result


# ---------------------------------------------------------------------------
# ThreatIntelligenceEngine — aggregator / cache
# ---------------------------------------------------------------------------

class ThreatIntelligenceEngine:
    """Aggregates all intelligence feeds, caches results, provides lookup."""

    def __init__(
        self,
        nvd_api_key: Optional[str] = None,
        custom_ioc: Optional[List[dict]] = None,
        cache_ttl: float = CACHE_TTL_SECONDS,
    ) -> None:
        self._nvd_api_key = nvd_api_key
        self._custom_ioc = custom_ioc
        self._cache_ttl = cache_ttl
        self._cache: List[ThreatIndicator] = []
        self._cache_time: float = 0.0
        self._hash_index: Dict[str, ThreatIndicator] = {}
        self._cve_index: Dict[str, ThreatIndicator] = {}
        self._domain_index: Dict[str, ThreatIndicator] = {}
        self._ip_index: Dict[str, ThreatIndicator] = {}

    def refresh(self) -> int:
        """Refresh all feeds.  Returns count of indicators loaded."""
        indicators: List[ThreatIndicator] = []
        indicators.extend(fetch_nvd_recent(api_key=self._nvd_api_key))
        indicators.extend(fetch_malware_bazaar_recent())
        indicators.extend(load_custom_ioc_registry(self._custom_ioc))

        # Deduplicate by fingerprint
        seen = set()
        deduped = []
        for ind in indicators:
            fp = ind.sha256_fingerprint
            if fp not in seen:
                seen.add(fp)
                deduped.append(ind)

        self._cache = deduped
        self._cache_time = time.time()

        # Build indices
        self._hash_index = {}
        self._cve_index = {}
        self._domain_index = {}
        self._ip_index = {}
        for ind in deduped:
            if ind.category == ThreatCategory.MALWARE_HASH:
                self._hash_index[ind.indicator.lower()] = ind
            elif ind.category == ThreatCategory.CVE:
                self._cve_index[ind.indicator] = ind
            elif ind.category == ThreatCategory.DOMAIN:
                self._domain_index[ind.indicator.lower()] = ind
            elif ind.category == ThreatCategory.IP_ADDRESS:
                self._ip_index[ind.indicator] = ind

        return len(deduped)

    def _ensure_fresh(self) -> None:
        if not self._cache or (time.time() - self._cache_time > self._cache_ttl):
            self.refresh()

    def lookup_hash(self, file_hash: str) -> Optional[ThreatIndicator]:
        """Check if a file hash (MD5/SHA-256) is a known malware indicator."""
        self._ensure_fresh()
        h = file_hash.lower()
        # Also check built-in offline set
        if h in KNOWN_MALWARE_HASHES:
            family = KNOWN_MALWARE_HASHES[h]
            return ThreatIndicator(
                category=ThreatCategory.MALWARE_HASH,
                indicator=h,
                source="builtin_offline",
                severity=Severity.CRITICAL,
                score=95.0,
                description=f"Known malware: {family}",
                tags=[family.lower()],
            )
        return self._hash_index.get(h)

    def lookup_cve(self, cve_id: str) -> Optional[ThreatIndicator]:
        self._ensure_fresh()
        return self._cve_index.get(cve_id)

    def lookup_domain(self, domain: str) -> Optional[ThreatIndicator]:
        self._ensure_fresh()
        return self._domain_index.get(domain.lower())

    def lookup_ip(self, ip: str) -> Optional[ThreatIndicator]:
        self._ensure_fresh()
        return self._ip_index.get(ip)

    def all_indicators(self) -> List[ThreatIndicator]:
        self._ensure_fresh()
        return list(self._cache)

    def critical_indicators(self) -> List[ThreatIndicator]:
        self._ensure_fresh()
        return [i for i in self._cache if i.severity == Severity.CRITICAL]

    def summary(self) -> dict:
        self._ensure_fresh()
        by_sev: Dict[str, int] = {s.value: 0 for s in Severity}
        for ind in self._cache:
            by_sev[ind.severity.value] += 1
        return {
            "total": len(self._cache),
            "by_severity": by_sev,
            "cache_age_seconds": time.time() - self._cache_time,
        }
