# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/intrusion_detector.py — Network & Process Anomaly Intrusion Detection
=============================================================================

Provides a two-mode IDS:

  Rule-Based Detection (RuleEngine)
  ----------------------------------
  • Signature rules expressed as Python callable predicates
  • Built-in rule set covers: port scanning, brute-force, SQL injection,
    XSS, directory traversal, LDAP injection, command injection, RCE probes,
    XXE, SSRF, protocol anomalies

  Statistical Anomaly Detection (AnomalyBaseline)
  -------------------------------------------------
  • Maintains a rolling baseline of per-source event rates (events/minute)
  • Triggers on Z-score > threshold (default 3.0 σ)
  • Exponential moving average for long-lived session tracking

  NetworkEvent / ProcessEvent
  ----------------------------
  Normalised event types consumed by both engines.

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import math
import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

from .threat_intel import Severity


# ---------------------------------------------------------------------------
# Event types
# ---------------------------------------------------------------------------

class Protocol(str, Enum):
    TCP  = "tcp"
    UDP  = "udp"
    ICMP = "icmp"
    HTTP = "http"
    HTTPS = "https"
    DNS  = "dns"
    SMTP = "smtp"
    FTP  = "ftp"
    SSH  = "ssh"
    SMB  = "smb"
    OTHER = "other"


@dataclass
class NetworkEvent:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: Protocol
    payload_size: int
    timestamp: float = field(default_factory=time.time)
    payload_snippet: bytes = b""     # first 512 bytes of payload
    http_method: Optional[str] = None
    http_path: Optional[str] = None
    http_headers: Dict[str, str] = field(default_factory=dict)
    dns_query: Optional[str] = None
    flags: str = ""                  # TCP flags: SYN, ACK, RST, FIN, …
    extra: Dict[str, object] = field(default_factory=dict)


@dataclass
class ProcessEvent:
    pid: int
    name: str
    cmdline: str
    parent_pid: int
    parent_name: str
    user: str
    timestamp: float = field(default_factory=time.time)
    file_path: Optional[str] = None
    network_dst: Optional[str] = None
    extra: Dict[str, object] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Alert
# ---------------------------------------------------------------------------

class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH     = "high"
    MEDIUM   = "medium"
    LOW      = "low"
    INFO     = "info"


@dataclass
class IDSAlert:
    rule_name: str
    severity: AlertSeverity
    score: float              # 0–100
    description: str
    evidence: str
    timestamp: float = field(default_factory=time.time)
    src_ip: Optional[str] = None
    dst_ip: Optional[str] = None
    src_port: Optional[int] = None
    dst_port: Optional[int] = None
    pid: Optional[int] = None
    process_name: Optional[str] = None
    anomaly_zscore: Optional[float] = None
    extra: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "rule_name": self.rule_name,
            "severity": self.severity.value,
            "score": self.score,
            "description": self.description,
            "evidence": self.evidence[:512],
            "timestamp": self.timestamp,
            "src_ip": self.src_ip,
            "dst_ip": self.dst_ip,
            "src_port": self.src_port,
            "dst_port": self.dst_port,
            "pid": self.pid,
            "process_name": self.process_name,
            "anomaly_zscore": self.anomaly_zscore,
        }


# ---------------------------------------------------------------------------
# Built-in signature rules — Network
# ---------------------------------------------------------------------------

# Pattern helpers
_SQL_INJECT_PATTERNS = re.compile(
    r"(\bunion\b.*\bselect\b|'?\s*(or|and)\s+1\s*=\s*1|"
    r"--\s*$|;\s*(drop|insert|update|delete)\b|"
    r"'\s*;\s*--|xp_cmdshell|exec\s*\(|cast\s*\(|char\s*\()",
    re.IGNORECASE,
)
_XSS_PATTERNS = re.compile(
    r"(<script|javascript:|onerror\s*=|onload\s*=|"
    r"<iframe|<object|<embed|alert\s*\(|document\.cookie|"
    r"eval\s*\(|String\.fromCharCode)",
    re.IGNORECASE,
)
_DIR_TRAVERSAL = re.compile(r"\.\./|\.\.\\|%2e%2e%2f|%2e%2e\\|%252e", re.IGNORECASE)
_CMD_INJECT = re.compile(
    r"(;|\||\|\||&&|\+)\s*(ls|cat|id|whoami|nc|wget|curl|bash|sh|cmd|powershell|python)",
    re.IGNORECASE,
)
_LDAP_INJECT = re.compile(r"(\*\)|\(\*|\\00|=\*\))", re.IGNORECASE)
_XXE_PATTERNS = re.compile(r"<!ENTITY\s+\w+\s+SYSTEM|<!DOCTYPE.*ENTITY", re.IGNORECASE)
_SSRF_PATTERNS = re.compile(
    r"(localhost|127\.0\.0\.1|0\.0\.0\.0|169\.254\.169\.254|"
    r"metadata\.google\.internal|fd00:|::1)",
    re.IGNORECASE,
)

# Privileged ports targeted by reconnaissance
_RECON_PORTS = {21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 389, 443,
                445, 993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 6379,
                8080, 8443, 27017}

# Common brute-force targets
_BRUTEFORCE_PORTS = {22, 23, 25, 110, 143, 3389, 5900, 21}


@dataclass
class NetworkRule:
    name: str
    description: str
    severity: AlertSeverity
    score: float
    predicate: Callable[[NetworkEvent], bool]

    def check(self, event: NetworkEvent) -> Optional[IDSAlert]:
        try:
            if self.predicate(event):
                snippet = event.payload_snippet[:128].decode("utf-8", errors="replace")
                path = event.http_path or ""
                return IDSAlert(
                    rule_name=self.name,
                    severity=self.severity,
                    score=self.score,
                    description=self.description,
                    evidence=f"src={event.src_ip}:{event.src_port} "
                             f"dst={event.dst_ip}:{event.dst_port} "
                             f"path={path[:64]} payload={snippet[:64]}",
                    timestamp=event.timestamp,
                    src_ip=event.src_ip,
                    dst_ip=event.dst_ip,
                    src_port=event.src_port,
                    dst_port=event.dst_port,
                )
        except Exception:
            pass
        return None


def _path_or_payload(e: NetworkEvent) -> str:
    parts = []
    if e.http_path:
        parts.append(e.http_path)
    if e.payload_snippet:
        parts.append(e.payload_snippet.decode("utf-8", errors="replace"))
    return " ".join(parts)


BUILTIN_NETWORK_RULES: List[NetworkRule] = [
    NetworkRule(
        name="SQL_INJECTION",
        description="SQL injection payload detected in HTTP request",
        severity=AlertSeverity.CRITICAL,
        score=92.0,
        predicate=lambda e: bool(_SQL_INJECT_PATTERNS.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="XSS_ATTACK",
        description="Cross-site scripting (XSS) payload in HTTP request",
        severity=AlertSeverity.HIGH,
        score=82.0,
        predicate=lambda e: bool(_XSS_PATTERNS.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="DIRECTORY_TRAVERSAL",
        description="Path traversal attempt detected",
        severity=AlertSeverity.HIGH,
        score=80.0,
        predicate=lambda e: bool(_DIR_TRAVERSAL.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="COMMAND_INJECTION",
        description="OS command injection payload in HTTP request",
        severity=AlertSeverity.CRITICAL,
        score=94.0,
        predicate=lambda e: bool(_CMD_INJECT.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="LDAP_INJECTION",
        description="LDAP injection payload detected",
        severity=AlertSeverity.HIGH,
        score=78.0,
        predicate=lambda e: bool(_LDAP_INJECT.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="XXE_ATTACK",
        description="XML External Entity (XXE) injection detected",
        severity=AlertSeverity.HIGH,
        score=85.0,
        predicate=lambda e: bool(_XXE_PATTERNS.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="SSRF_PROBE",
        description="Server-Side Request Forgery (SSRF) probe in request",
        severity=AlertSeverity.HIGH,
        score=83.0,
        predicate=lambda e: bool(_SSRF_PATTERNS.search(_path_or_payload(e))),
    ),
    NetworkRule(
        name="NULL_BYTE_INJECTION",
        description="Null byte injection attempt",
        severity=AlertSeverity.MEDIUM,
        score=65.0,
        predicate=lambda e: b"\x00" in e.payload_snippet,
    ),
    NetworkRule(
        name="SMB_LATERAL_MOVEMENT",
        description="SMB connection to unusual destination — possible lateral movement",
        severity=AlertSeverity.HIGH,
        score=75.0,
        predicate=lambda e: e.protocol == Protocol.SMB and e.dst_port == 445,
    ),
    NetworkRule(
        name="UNENCRYPTED_CREDENTIAL_HTTP",
        description="HTTP (plaintext) login attempt — credentials may be exposed",
        severity=AlertSeverity.MEDIUM,
        score=55.0,
        predicate=lambda e: (
            e.protocol == Protocol.HTTP
            and e.http_method in ("POST", "PUT")
            and bool(re.search(r"(password|passwd|pwd|credential)", _path_or_payload(e), re.I))
        ),
    ),
    NetworkRule(
        name="DNS_TUNNEL_LONG_LABEL",
        description="DNS query with unusually long label — possible DNS tunnelling",
        severity=AlertSeverity.HIGH,
        score=77.0,
        predicate=lambda e: (
            e.protocol == Protocol.DNS
            and e.dns_query is not None
            and any(len(p) > 63 for p in (e.dns_query or "").split("."))
        ),
    ),
    NetworkRule(
        name="FTP_ANON_LOGIN",
        description="Anonymous FTP login attempt",
        severity=AlertSeverity.MEDIUM,
        score=50.0,
        predicate=lambda e: (
            e.protocol == Protocol.FTP
            and b"anonymous" in e.payload_snippet.lower()
        ),
    ),
]


@dataclass
class ProcessRule:
    name: str
    description: str
    severity: AlertSeverity
    score: float
    predicate: Callable[[ProcessEvent], bool]

    def check(self, event: ProcessEvent) -> Optional[IDSAlert]:
        try:
            if self.predicate(event):
                return IDSAlert(
                    rule_name=self.name,
                    severity=self.severity,
                    score=self.score,
                    description=self.description,
                    evidence=f"pid={event.pid} name={event.name} cmd={event.cmdline[:128]}",
                    timestamp=event.timestamp,
                    pid=event.pid,
                    process_name=event.name,
                )
        except Exception:
            pass
        return None


BUILTIN_PROCESS_RULES: List[ProcessRule] = [
    ProcessRule(
        name="SUSPICIOUS_CHILD_SHELL",
        description="Office/browser spawning a shell — possible macro/RCE",
        severity=AlertSeverity.CRITICAL,
        score=95.0,
        predicate=lambda e: (
            any(p in e.parent_name.lower() for p in ("word", "excel", "chrome", "firefox", "acrobat"))
            and any(s in e.name.lower() for s in ("cmd", "powershell", "bash", "sh", "wscript"))
        ),
    ),
    ProcessRule(
        name="PROCESS_INJECTION_TOOL",
        description="Known process injection tool detected (Mimikatz, Meterpreter, …)",
        severity=AlertSeverity.CRITICAL,
        score=98.0,
        predicate=lambda e: any(
            t in e.name.lower() or t in e.cmdline.lower()
            for t in ("mimikatz", "meterpreter", "cobalt", "empire", "covenant", "sliver")
        ),
    ),
    ProcessRule(
        name="CRED_DUMP_LSASS",
        description="Process accessing LSASS memory — credential dumping",
        severity=AlertSeverity.CRITICAL,
        score=97.0,
        predicate=lambda e: "lsass" in e.cmdline.lower() or "lsass" in e.extra.get("target_process", "").lower(),
    ),
    ProcessRule(
        name="ENCODED_POWERSHELL",
        description="PowerShell with -EncodedCommand flag — obfuscated execution",
        severity=AlertSeverity.HIGH,
        score=85.0,
        predicate=lambda e: (
            "powershell" in e.name.lower()
            and re.search(r"-[Ee]nc(odedCommand)?", e.cmdline)
        ),
    ),
    ProcessRule(
        name="NETWORK_FROM_UNUSUAL_PROCESS",
        description="Network connection from process that should not be network-facing",
        severity=AlertSeverity.MEDIUM,
        score=60.0,
        predicate=lambda e: (
            e.network_dst is not None
            and any(s in e.name.lower() for s in ("calc", "notepad", "mspaint", "explorer"))
        ),
    ),
    ProcessRule(
        name="SCHEDULED_TASK_PERSISTENCE",
        description="schtasks or cron modification — possible persistence mechanism",
        severity=AlertSeverity.HIGH,
        score=78.0,
        predicate=lambda e: any(
            t in e.cmdline.lower()
            for t in ("schtasks /create", "crontab -e", "at ", "launchctl load")
        ),
    ),
    ProcessRule(
        name="ROOTKIT_LOAD_KERNEL_MODULE",
        description="Unexpected kernel module load — rootkit persistence risk",
        severity=AlertSeverity.CRITICAL,
        score=92.0,
        predicate=lambda e: any(
            t in e.name.lower() or t in e.cmdline.lower()
            for t in ("insmod", "modprobe", "kextload")
        ) and e.user != "root",
    ),
]


# ---------------------------------------------------------------------------
# Statistical Anomaly Baseline
# ---------------------------------------------------------------------------

class AnomalyBaseline:
    """Per-source event rate baseline using exponential moving statistics.

    Maintains a rolling window of event timestamps per source key and
    computes Z-score of the current minute's rate against the historical
    mean ± std.

    Parameters
    ----------
    window_minutes : int
        Length of the rolling history window.
    z_threshold : float
        Z-score above which an anomaly alert is raised.
    min_samples : int
        Minimum number of historical samples before alerts are emitted.
    """

    def __init__(
        self,
        window_minutes: int = 60,
        z_threshold: float = 3.0,
        min_samples: int = 5,
    ) -> None:
        self._window = window_minutes * 60.0  # seconds
        self._z_thresh = z_threshold
        self._min_samples = min_samples
        # Per-source: deque of event timestamps
        self._events: Dict[str, deque] = defaultdict(lambda: deque())
        # Per-source: list of historical 1-minute rates
        self._rates: Dict[str, List[float]] = defaultdict(list)
        self._last_rate_ts: Dict[str, float] = {}

    def record(self, source_key: str, timestamp: Optional[float] = None) -> Optional[IDSAlert]:
        """Record one event for source_key.  Returns an alert if anomalous."""
        ts = timestamp if timestamp is not None else time.time()
        q = self._events[source_key]
        q.append(ts)

        # Prune old events outside the rolling window
        cutoff = ts - self._window
        while q and q[0] < cutoff:
            q.popleft()

        # Compute current rate every 60 seconds
        last = self._last_rate_ts.get(source_key, 0.0)
        if ts - last >= 60.0:
            rate = len(q) / (self._window / 60.0)  # events per minute
            self._rates[source_key].append(rate)
            self._last_rate_ts[source_key] = ts
            # Trim history to window
            max_hist = int(self._window / 60) * 2
            if len(self._rates[source_key]) > max_hist:
                self._rates[source_key] = self._rates[source_key][-max_hist:]

            return self._check_anomaly(source_key, rate, ts)

        return None

    def _check_anomaly(self, source_key: str, current_rate: float, ts: float) -> Optional[IDSAlert]:
        hist = self._rates[source_key]
        if len(hist) < self._min_samples:
            return None
        # Exclude current rate from baseline stats
        baseline = hist[:-1]
        mean = sum(baseline) / len(baseline)
        variance = sum((x - mean) ** 2 for x in baseline) / len(baseline)
        std = math.sqrt(variance) if variance > 0 else 1.0
        z = (current_rate - mean) / std

        if z > self._z_thresh:
            sev = AlertSeverity.CRITICAL if z > 6 else AlertSeverity.HIGH if z > 4 else AlertSeverity.MEDIUM
            score = min(90.0, 50.0 + z * 5)
            return IDSAlert(
                rule_name="STATISTICAL_ANOMALY",
                severity=sev,
                score=score,
                description=(
                    f"Event rate anomaly for source '{source_key}': "
                    f"current={current_rate:.1f}/min, baseline={mean:.1f}±{std:.1f}/min, "
                    f"Z={z:.2f}"
                ),
                evidence=f"source={source_key} rate={current_rate:.1f} mean={mean:.1f} std={std:.1f}",
                timestamp=ts,
                src_ip=source_key if "." in source_key else None,
                anomaly_zscore=z,
            )
        return None


# ---------------------------------------------------------------------------
# Port scan / brute-force detectors (stateful)
# ---------------------------------------------------------------------------

class PortScanDetector:
    """Detects port scanning: many distinct destination ports from one source.

    Trigger: ≥ port_threshold distinct dst_ports from one src_ip within
    time_window_seconds.
    """

    def __init__(self, port_threshold: int = 15, time_window_seconds: float = 60.0) -> None:
        self._threshold = port_threshold
        self._window = time_window_seconds
        # src_ip → deque of (timestamp, dst_port)
        self._log: Dict[str, deque] = defaultdict(deque)

    def record(self, event: NetworkEvent) -> Optional[IDSAlert]:
        key = event.src_ip
        q = self._log[key]
        q.append((event.timestamp, event.dst_port))
        cutoff = event.timestamp - self._window
        while q and q[0][0] < cutoff:
            q.popleft()
        distinct_ports = len({p for _, p in q})
        if distinct_ports >= self._threshold:
            return IDSAlert(
                rule_name="PORT_SCAN",
                severity=AlertSeverity.HIGH,
                score=80.0,
                description=f"Port scan from {event.src_ip}: {distinct_ports} distinct ports in {self._window}s",
                evidence=f"src={event.src_ip} distinct_ports={distinct_ports}",
                timestamp=event.timestamp,
                src_ip=event.src_ip,
            )
        return None


class BruteForceDetector:
    """Detects brute-force: many connections to the same dst_ip:port from one src.

    Trigger: ≥ attempt_threshold connections within time_window_seconds.
    """

    def __init__(self, attempt_threshold: int = 10, time_window_seconds: float = 60.0) -> None:
        self._threshold = attempt_threshold
        self._window = time_window_seconds
        # (src_ip, dst_ip, dst_port) → deque of timestamps
        self._log: Dict[Tuple[str, str, int], deque] = defaultdict(deque)

    def record(self, event: NetworkEvent) -> Optional[IDSAlert]:
        if event.dst_port not in _BRUTEFORCE_PORTS:
            return None
        key = (event.src_ip, event.dst_ip, event.dst_port)
        q = self._log[key]
        q.append(event.timestamp)
        cutoff = event.timestamp - self._window
        while q and q[0] < cutoff:
            q.popleft()
        if len(q) >= self._threshold:
            return IDSAlert(
                rule_name="BRUTE_FORCE",
                severity=AlertSeverity.HIGH,
                score=85.0,
                description=(
                    f"Brute-force detected: {event.src_ip} → "
                    f"{event.dst_ip}:{event.dst_port} "
                    f"({len(q)} attempts in {self._window}s)"
                ),
                evidence=f"src={event.src_ip} dst={event.dst_ip}:{event.dst_port} attempts={len(q)}",
                timestamp=event.timestamp,
                src_ip=event.src_ip,
                dst_ip=event.dst_ip,
                dst_port=event.dst_port,
            )
        return None


# ---------------------------------------------------------------------------
# IntrusionDetector — top-level IDS
# ---------------------------------------------------------------------------

class IntrusionDetector:
    """Full IDS combining signature rules, anomaly detection, and stateful detectors."""

    def __init__(
        self,
        extra_network_rules: Optional[List[NetworkRule]] = None,
        extra_process_rules: Optional[List[ProcessRule]] = None,
        anomaly_z_threshold: float = 3.0,
        port_scan_threshold: int = 15,
        brute_force_threshold: int = 10,
    ) -> None:
        self._net_rules: List[NetworkRule] = (
            BUILTIN_NETWORK_RULES + (extra_network_rules or [])
        )
        self._proc_rules: List[ProcessRule] = (
            BUILTIN_PROCESS_RULES + (extra_process_rules or [])
        )
        self._anomaly = AnomalyBaseline(z_threshold=anomaly_z_threshold)
        self._port_scan = PortScanDetector(port_threshold=port_scan_threshold)
        self._brute_force = BruteForceDetector(attempt_threshold=brute_force_threshold)
        self._alerts: List[IDSAlert] = []

    def inspect_network(self, event: NetworkEvent) -> List[IDSAlert]:
        """Inspect a network event.  Returns any new alerts."""
        new_alerts: List[IDSAlert] = []

        # Signature rules
        for rule in self._net_rules:
            alert = rule.check(event)
            if alert:
                new_alerts.append(alert)

        # Port scan
        a = self._port_scan.record(event)
        if a:
            new_alerts.append(a)

        # Brute force
        a = self._brute_force.record(event)
        if a:
            new_alerts.append(a)

        # Statistical anomaly
        a = self._anomaly.record(event.src_ip, event.timestamp)
        if a:
            new_alerts.append(a)

        self._alerts.extend(new_alerts)
        return new_alerts

    def inspect_process(self, event: ProcessEvent) -> List[IDSAlert]:
        """Inspect a process event.  Returns any new alerts."""
        new_alerts: List[IDSAlert] = []
        for rule in self._proc_rules:
            alert = rule.check(event)
            if alert:
                new_alerts.append(alert)
        self._alerts.extend(new_alerts)
        return new_alerts

    def all_alerts(self) -> List[IDSAlert]:
        return list(self._alerts)

    def critical_alerts(self) -> List[IDSAlert]:
        return [a for a in self._alerts if a.severity == AlertSeverity.CRITICAL]

    def clear_alerts(self) -> int:
        n = len(self._alerts)
        self._alerts.clear()
        return n

    def summary(self) -> dict:
        by_sev: Dict[str, int] = {s.value: 0 for s in AlertSeverity}
        for a in self._alerts:
            by_sev[a.severity.value] += 1
        return {
            "total_alerts": len(self._alerts),
            "by_severity": by_sev,
            "rules_loaded": len(self._net_rules) + len(self._proc_rules),
        }
