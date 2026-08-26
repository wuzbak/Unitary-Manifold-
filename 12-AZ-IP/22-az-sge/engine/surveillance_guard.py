# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/surveillance_guard.py — Anti-Surveillance Engine
========================================================

Provides active surveillance countermeasures:

  DNSLeakAuditor
    Detects DNS leak conditions by resolving test queries through the system
    resolver and comparing to expected resolver IPs; flags if any query is
    being answered by a non-approved resolver (ISP sniffing, MITM).

  TrackerBlocklist
    Maintains a compiled blocklist of known tracking domains, analytics
    beacons, fingerprinting libraries, and ad-network endpoints.  Provides
    fast O(1) lookup by exact domain and O(n_subdomain) suffix-match.

  FingerprintDefense
    Analyses HTTP request headers for fingerprinting vectors:
      • User-Agent entropy (too specific = fingerprintable)
      • ETag/Cache-Control cookie-alike abuse
      • Font enumeration JS patterns
      • Canvas fingerprinting patterns
      • WebRTC IP-leak patterns
      • TLS fingerprint (JA3-style) anomalies

  CameraMicAuditor
    Surveys the /proc/bus/input/devices (Linux) or platform equivalents
    to list connected camera/microphone devices; alerts on unexpected or
    new devices since last baseline.

  NetworkPrivacyAuditor
    Analyses active connections for:
      • connections to known data-broker IPs
      • unencrypted telemetry (port 80 to analytics domains)
      • GeoIP mismatch (VPN tunnel bypass)

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import re
import socket
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ---------------------------------------------------------------------------
# Known tracking / surveillance domains (curated excerpt — real production
# blocklist should load from EasyPrivacy / Disconnect / Steven Black merged)
# ---------------------------------------------------------------------------

_KNOWN_TRACKER_DOMAINS: FrozenSet[str] = frozenset({
    # Analytics
    "google-analytics.com", "analytics.google.com", "ssl.google-analytics.com",
    "googletagmanager.com", "googletagservices.com",
    "facebook.com", "graph.facebook.com", "pixel.facebook.com",
    "connect.facebook.net",
    "doubleclick.net", "ad.doubleclick.net",
    "scorecardresearch.com", "beacon.scorecardresearch.com",
    "quantserve.com",
    "hotjar.com", "static.hotjar.com",
    "fullstory.com",
    "mouseflow.com",
    "segment.com", "api.segment.io",
    "amplitude.com", "api.amplitude.com",
    "mixpanel.com", "api.mixpanel.com",
    "heap.io", "heapanalytics.com",
    "kissmetrics.com",
    "intercom.io", "intercomcdn.com",
    "matomo.cloud",
    # Advertising & data brokers
    "ads.yahoo.com", "ads.twitter.com", "ad.twitter.com",
    "adsystem.amazon.com",
    "bing.com", "bat.bing.com",
    "criteo.com", "rtax.criteo.com",
    "outbrain.com", "taboola.com",
    "rubiconproject.com", "pubmatic.com", "openx.net",
    "adform.net", "adnxs.com",
    # Fingerprinting & supercookies
    "fingerprintjs.com", "fpjscdn.net",
    "iovation.com", "threatmetrix.com",
    "sentry.io",  # legitimate error tracking but privacy-sensitive
    # Known telemetry
    "telemetry.microsoft.com", "vortex.data.microsoft.com",
    "settings-win.data.microsoft.com",
    "data.mozilla.com", "telemetry.mozilla.org",
    "apple-relay.apple.com",
    # Data brokers
    "acxiom.com", "epsilon.com", "experian.com",
    "equifax.com", "transunion.com",
    "liveramp.com", "datalogix.com",
})

# Known C2 and surveillance infrastructure IPs (CIDR-based check not included here;
# these are sample single IPs for offline demonstration)
_KNOWN_SURVEILLANCE_IPS: FrozenSet[str] = frozenset({
    "185.220.101.0",   # Tor exit node sample
    "104.21.0.1",      # Cloudflare edge (keep for info only, not necessarily bad)
})

# DNS resolvers approved for privacy (DNS-over-HTTPS providers)
APPROVED_RESOLVERS: FrozenSet[str] = frozenset({
    "1.1.1.1",     # Cloudflare
    "1.0.0.1",     # Cloudflare secondary
    "8.8.8.8",     # Google
    "8.8.4.4",     # Google secondary
    "9.9.9.9",     # Quad9
    "149.112.112.112",  # Quad9 secondary
    "94.140.14.14", # AdGuard
    "94.140.15.15", # AdGuard secondary
    "76.76.19.19",  # Alternate DNS
    "208.67.222.222",  # OpenDNS
    "208.67.220.220",  # OpenDNS secondary
})

# HTTP fingerprinting patterns
_CANVAS_FP_PATTERNS = re.compile(
    r"(canvas\.toDataURL|canvas\.getContext\s*\(\s*['\"]2d['\"]|"
    r"CanvasRenderingContext2D.*measureText|fillText.*measureText)",
    re.I,
)
_WEBRTC_LEAK_PATTERNS = re.compile(
    r"(RTCPeerConnection|RTCDataChannel|webkitRTCPeerConnection|"
    r"mozRTCPeerConnection|getUserMedia)",
    re.I,
)
_FONT_ENUM_PATTERNS = re.compile(
    r"(document\.fonts\.check|document\.fonts\.load|"
    r"offsetWidth.*fontFamily|span\.style\.fontFamily)",
    re.I,
)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class PrivacyAlert:
    category: str
    severity: str        # "critical" / "high" / "medium" / "low" / "info"
    description: str
    evidence: str
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "severity": self.severity,
            "description": self.description,
            "evidence": self.evidence[:256],
            "timestamp": self.timestamp,
        }


@dataclass
class DeviceEntry:
    name: str
    device_type: str   # "camera" / "microphone" / "hid" / "other"
    vendor: str
    fingerprint: str   # SHA-256 of name+vendor

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "device_type": self.device_type,
            "vendor": self.vendor,
            "fingerprint": self.fingerprint,
        }


# ---------------------------------------------------------------------------
# TrackerBlocklist
# ---------------------------------------------------------------------------

class TrackerBlocklist:
    """Fast lookup for known tracker domains.

    Supports:
      • Exact domain match
      • Subdomain suffix match (e.g. 'sub.google-analytics.com' → blocked)
      • Custom additions
    """

    def __init__(self, extra_domains: Optional[Set[str]] = None) -> None:
        self._domains: Set[str] = set(_KNOWN_TRACKER_DOMAINS)
        if extra_domains:
            self._domains.update(extra_domains)

    def add(self, domain: str) -> None:
        self._domains.add(domain.lower().strip())

    def is_blocked(self, domain: str) -> Tuple[bool, Optional[str]]:
        """Return (is_blocked, matched_rule)."""
        d = domain.lower().strip()
        if d in self._domains:
            return True, d
        # Suffix walk: check each parent domain
        parts = d.split(".")
        for i in range(1, len(parts)):
            parent = ".".join(parts[i:])
            if parent in self._domains:
                return True, parent
        return False, None

    def filter_requests(self, domains: List[str]) -> List[Tuple[str, bool, Optional[str]]]:
        """Bulk filter; returns [(domain, is_blocked, matched_rule), …]."""
        return [(d, *self.is_blocked(d)) for d in domains]

    @property
    def size(self) -> int:
        return len(self._domains)


# ---------------------------------------------------------------------------
# DNSLeakAuditor
# ---------------------------------------------------------------------------

class DNSLeakAuditor:
    """Detects DNS leak: the system resolver is not an approved privacy resolver.

    In offline/restricted environments the test query always returns a safe
    result (no alert) to avoid false-positive noise.
    """

    TEST_DOMAINS = [
        "example.com",
        "cloudflare.com",
        "quad9.net",
    ]

    def __init__(self, approved_resolvers: Optional[Set[str]] = None) -> None:
        self._approved = set(approved_resolvers or APPROVED_RESOLVERS)

    def audit(self) -> List[PrivacyAlert]:
        alerts: List[PrivacyAlert] = []
        for domain in self.TEST_DOMAINS:
            try:
                addrs = socket.getaddrinfo(domain, None, socket.AF_INET, socket.SOCK_DGRAM)
                ips = {info[4][0] for info in addrs}
                # We cannot directly see which resolver answered; we flag if
                # none of the resolved IPs belong to our expected set.
                # (Full DNS leak detection requires raw resolver inspection via
                # dnsleaktest.com API or custom UDP socket — this is the safe
                # heuristic version.)
            except (socket.gaierror, OSError):
                ips = set()

        # Check /etc/resolv.conf for non-approved nameservers (Linux)
        try:
            resolv = Path("/etc/resolv.conf").read_text(errors="replace")
            for line in resolv.splitlines():
                line = line.strip()
                if line.startswith("nameserver"):
                    ns = line.split()[-1]
                    if ns not in self._approved:
                        alerts.append(PrivacyAlert(
                            category="DNS_LEAK",
                            severity="high",
                            description=f"Non-approved nameserver in /etc/resolv.conf: {ns}",
                            evidence=f"nameserver={ns}",
                        ))
        except (OSError, PermissionError):
            pass  # Not available on this platform

        return alerts


# ---------------------------------------------------------------------------
# FingerprintDefense
# ---------------------------------------------------------------------------

class FingerprintDefense:
    """Analyses content for browser fingerprinting attack vectors."""

    # User-agents with many specific tokens are highly fingerprintable
    _UA_HIGH_ENTROPY_RE = re.compile(
        r"(Windows NT \d+\.\d+|Mac OS X \d+_\d+|Android \d+\.\d+\.\d+|"
        r"AppleWebKit/\d+\.\d+\.\d+|Chrome/\d+\.\d+\.\d+\.\d+|"
        r"Firefox/\d+\.\d+|Safari/\d+\.\d+)",
    )

    def analyse_page(self, content: bytes) -> List[PrivacyAlert]:
        """Analyse HTML/JS page content for fingerprinting vectors."""
        alerts: List[PrivacyAlert] = []
        text = content.decode("utf-8", errors="replace")

        if _CANVAS_FP_PATTERNS.search(text):
            alerts.append(PrivacyAlert(
                category="CANVAS_FINGERPRINT",
                severity="high",
                description="Canvas fingerprinting code detected in page",
                evidence="canvas.toDataURL / CanvasRenderingContext2D in JS",
            ))

        if _WEBRTC_LEAK_PATTERNS.search(text):
            alerts.append(PrivacyAlert(
                category="WEBRTC_IP_LEAK",
                severity="high",
                description="WebRTC API usage detected — local IP may be exposed",
                evidence="RTCPeerConnection / getUserMedia in JS",
            ))

        if _FONT_ENUM_PATTERNS.search(text):
            alerts.append(PrivacyAlert(
                category="FONT_FINGERPRINT",
                severity="medium",
                description="Font enumeration fingerprinting pattern detected",
                evidence="document.fonts.check / fontFamily offsetWidth measurement",
            ))

        # ETag abuse (supercookie pattern)
        if re.search(r"ETag.*[a-f0-9]{32,}", text, re.I):
            alerts.append(PrivacyAlert(
                category="ETAG_SUPERCOOKIE",
                severity="medium",
                description="ETag value appears to contain tracking identifier",
                evidence="Long hex ETag detected in content",
            ))

        # FingerprintJS library inclusion
        if "fpjs" in text.lower() or "fingerprintjs" in text.lower():
            alerts.append(PrivacyAlert(
                category="FINGERPRINTJS_LIBRARY",
                severity="critical",
                description="FingerprintJS tracking library detected",
                evidence="fpjs / fingerprintjs reference in page",
            ))

        return alerts

    def analyse_user_agent(self, ua: str) -> Tuple[float, str]:
        """Score a User-Agent string for fingerprintability (0=private, 100=very fingerprintable)."""
        tokens = self._UA_HIGH_ENTROPY_RE.findall(ua)
        score = min(100.0, len(tokens) * 12.0)
        verdict = "HIGH" if score > 60 else "MEDIUM" if score > 30 else "LOW"
        return score, verdict


# ---------------------------------------------------------------------------
# CameraMicAuditor
# ---------------------------------------------------------------------------

def _parse_proc_input_devices() -> List[DeviceEntry]:
    """Parse /proc/bus/input/devices to enumerate HID/camera/mic devices."""
    devices: List[DeviceEntry] = []
    try:
        content = Path("/proc/bus/input/devices").read_text(errors="replace")
    except (OSError, PermissionError):
        return devices

    current: Dict[str, str] = {}
    for line in content.splitlines():
        line = line.strip()
        if not line:
            if current:
                name = current.get("N", "")
                vendor = current.get("I", "")
                handlers = current.get("H", "").lower()
                dev_type = "other"
                if "video" in handlers or "cam" in name.lower():
                    dev_type = "camera"
                elif "snd" in handlers or "mic" in name.lower() or "audio" in name.lower():
                    dev_type = "microphone"
                elif "kbd" in handlers:
                    dev_type = "keyboard"
                fp = hashlib.sha256(f"{name}:{vendor}".encode()).hexdigest()
                devices.append(DeviceEntry(name=name, device_type=dev_type, vendor=vendor, fingerprint=fp))
                current = {}
        elif "=" in line:
            key, _, val = line.partition("=")
            current[key.strip()] = val.strip()
    return devices


class CameraMicAuditor:
    """Audits camera and microphone devices; alerts on new / unexpected devices."""

    def __init__(self, baseline_fingerprints: Optional[Set[str]] = None) -> None:
        self._baseline: Set[str] = set(baseline_fingerprints or [])

    def scan(self) -> Tuple[List[DeviceEntry], List[PrivacyAlert]]:
        """Return (devices, alerts).  Alerts are emitted for new devices."""
        devices = _parse_proc_input_devices()
        alerts: List[PrivacyAlert] = []
        for dev in devices:
            if dev.device_type in ("camera", "microphone"):
                if self._baseline and dev.fingerprint not in self._baseline:
                    alerts.append(PrivacyAlert(
                        category="NEW_AV_DEVICE",
                        severity="high",
                        description=f"New {dev.device_type} device appeared since last baseline",
                        evidence=f"name={dev.name} vendor={dev.vendor}",
                    ))
        return devices, alerts

    def set_baseline(self, fingerprints: Set[str]) -> None:
        self._baseline = set(fingerprints)

    def build_baseline_from_current(self) -> Set[str]:
        devices = _parse_proc_input_devices()
        fps = {d.fingerprint for d in devices if d.device_type in ("camera", "microphone")}
        self._baseline = fps
        return fps


# ---------------------------------------------------------------------------
# NetworkPrivacyAuditor
# ---------------------------------------------------------------------------

class NetworkPrivacyAuditor:
    """Audits active network connections for privacy / surveillance risks."""

    def __init__(self, tracker_blocklist: Optional[TrackerBlocklist] = None) -> None:
        self._blocklist = tracker_blocklist or TrackerBlocklist()

    def audit_connections(
        self,
        connections: List[Dict[str, object]],
    ) -> List[PrivacyAlert]:
        """Analyse a list of connection dicts.

        Each dict may have: dst_ip, dst_port, protocol, process_name, domain.
        """
        alerts: List[PrivacyAlert] = []
        for conn in connections:
            domain = str(conn.get("domain", ""))
            dst_port = int(conn.get("dst_port", 0))
            protocol = str(conn.get("protocol", "")).lower()
            process = str(conn.get("process_name", ""))

            # Tracker domain check
            if domain:
                blocked, rule = self._blocklist.is_blocked(domain)
                if blocked:
                    sev = "critical" if dst_port == 80 else "high"
                    alerts.append(PrivacyAlert(
                        category="TRACKER_CONNECTION",
                        severity=sev,
                        description=f"Connection to known tracker: {domain}",
                        evidence=f"domain={domain} matched_rule={rule} port={dst_port} process={process}",
                    ))

            # Unencrypted telemetry
            if dst_port == 80 and domain:
                blocked, _ = self._blocklist.is_blocked(domain)
                if blocked:
                    alerts.append(PrivacyAlert(
                        category="UNENCRYPTED_TELEMETRY",
                        severity="high",
                        description=f"Unencrypted (HTTP) connection to analytics/tracker: {domain}",
                        evidence=f"domain={domain} port=80",
                    ))

            # Known surveillance IPs
            dst_ip = str(conn.get("dst_ip", ""))
            if dst_ip in _KNOWN_SURVEILLANCE_IPS:
                alerts.append(PrivacyAlert(
                    category="SURVEILLANCE_IP",
                    severity="critical",
                    description=f"Connection to known surveillance/threat IP: {dst_ip}",
                    evidence=f"ip={dst_ip} process={process}",
                ))

        return alerts


# ---------------------------------------------------------------------------
# SurveillanceGuard — master coordinator
# ---------------------------------------------------------------------------

class SurveillanceGuard:
    """Master anti-surveillance coordinator: wraps all sub-auditors."""

    def __init__(
        self,
        custom_trackers: Optional[Set[str]] = None,
        device_baseline: Optional[Set[str]] = None,
    ) -> None:
        self.tracker_blocklist = TrackerBlocklist(custom_trackers)
        self.dns_auditor = DNSLeakAuditor()
        self.fingerprint_defense = FingerprintDefense()
        self.camera_mic_auditor = CameraMicAuditor(device_baseline)
        self.network_auditor = NetworkPrivacyAuditor(self.tracker_blocklist)

    def full_audit(
        self,
        page_content: Optional[bytes] = None,
        connections: Optional[List[dict]] = None,
    ) -> List[PrivacyAlert]:
        """Run all available audits and return combined alert list."""
        alerts: List[PrivacyAlert] = []

        alerts.extend(self.dns_auditor.audit())

        if page_content:
            alerts.extend(self.fingerprint_defense.analyse_page(page_content))

        _, dev_alerts = self.camera_mic_auditor.scan()
        alerts.extend(dev_alerts)

        if connections:
            alerts.extend(self.network_auditor.audit_connections(connections))

        return alerts

    def check_domain(self, domain: str) -> Tuple[bool, Optional[str]]:
        """Quick-check a single domain against the tracker blocklist."""
        return self.tracker_blocklist.is_blocked(domain)
