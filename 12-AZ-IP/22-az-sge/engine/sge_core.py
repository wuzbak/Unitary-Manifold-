# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/sge_core.py — AxiomZero System Security Governance Engine — Core Orchestrator
=====================================================================================

SGECore ties together all subsystems into a single unified security runtime:

  Subsystems
  ----------
  • ThreatIntelligenceEngine  — live + offline CVE / malware feeds
  • MalwareDetector           — file scanning, YARA, entropy, baseline
  • ZeroDayEngine             — heuristic zero-day detection
  • IntrusionDetector         — network + process IDS
  • PolicyEngine              — packet-filter firewall
  • SurveillanceGuard         — anti-surveillance, DNS audit, tracker block
  • DependencyAuditor         — dependency vulnerability scanning
  • QuarantineOrchestrator    — quarantine, remediation, audit chain
  • HashChain                 — immutable event audit ledger

  Public API (all synchronous; async wrappers can be added per deployment)
  -----------------------------------------------------------------------
  scan_file(path)              → FileScanResult + QuarantineRecord
  scan_directory(path)         → [FileScanResult]
  inspect_network(event)       → [IDSAlert] + optional QuarantineRecord
  inspect_process(event)       → [IDSAlert]
  check_url(url, payload)      → ZeroDayScanResult
  check_domain(domain)         → (blocked: bool, rule: str|None)
  audit_dependencies(path)     → [VulnerableDependency]
  firewall_evaluate(event)     → FirewallDecision
  full_privacy_audit()         → [PrivacyAlert]
  threat_intel_summary()       → dict
  status()                     → dict (full engine status)

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .hash_chain import HashChain, merkle_root_of_chain
from .encryption import SymmetricCipher, generate_keypair, KeyPair
from .threat_intel import ThreatIntelligenceEngine, ThreatIndicator, Severity
from .malware_detector import MalwareDetector, FileScanResult, YaraRule, create_canary_file, check_canary_file
from .zero_day import ZeroDayEngine, ZeroDayScanResult
from .intrusion_detector import IntrusionDetector, NetworkEvent, ProcessEvent, IDSAlert
from .firewall import PolicyEngine, PolicyRule, FirewallDecision, Direction
from .surveillance_guard import SurveillanceGuard, PrivacyAlert, TrackerBlocklist
from .vuln_scanner import DependencyAuditor, VulnerableDependency, VulnerabilityReport
from .quarantine import QuarantineOrchestrator, QuarantineRecord, QuarantineVault


# ---------------------------------------------------------------------------
# SGEConfig
# ---------------------------------------------------------------------------

@dataclass
class SGEConfig:
    """Runtime configuration for the SGE Core."""

    # Threat intel
    nvd_api_key: Optional[str] = None
    custom_ioc: Optional[List[dict]] = None

    # Malware detection
    custom_yara_rules: Optional[List[YaraRule]] = None
    file_baseline: Optional[Dict[str, str]] = None

    # Quarantine
    quarantine_dir: Optional[str] = None
    auto_quarantine_threshold: float = 70.0

    # Firewall
    custom_firewall_rules: Optional[List[PolicyRule]] = None

    # Surveillance
    custom_trackers: Optional[set] = None
    device_baseline: Optional[set] = None

    # Canary files for ransomware detection
    canary_paths: Optional[List[str]] = None

    # Encryption
    use_hardware_crypto: bool = True    # use cryptography lib if available

    def to_dict(self) -> dict:
        return {
            "nvd_api_key_set": self._nvd_key_set(),
            "auto_quarantine_threshold": self.auto_quarantine_threshold,
            "custom_firewall_rules": len(self.custom_firewall_rules or []),
            "custom_trackers": len(self.custom_trackers or set()),
        }

    def _nvd_key_set(self) -> bool:
        return bool(self.nvd_api_key)


# ---------------------------------------------------------------------------
# SecurityEvent — unified event emitted for dashboard
# ---------------------------------------------------------------------------

@dataclass
class SecurityEvent:
    event_id: str
    timestamp: float
    event_type: str         # "file_scan" / "ids_alert" / "zero_day" / "firewall" / "privacy"
    severity: str
    score: float
    title: str
    detail: str
    source: Optional[str] = None
    chain_index: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "severity": self.severity,
            "score": self.score,
            "title": self.title,
            "detail": self.detail[:512],
            "source": self.source,
        }


# ---------------------------------------------------------------------------
# SGECore
# ---------------------------------------------------------------------------

class SGECore:
    """AxiomZero System Security Governance Engine — unified runtime.

    Instantiate once per deployment:

        sge = SGECore(SGEConfig(nvd_api_key="...", quarantine_dir="/var/quarantine"))
        result = sge.scan_file("/tmp/suspicious.exe")
    """

    ENGINE_VERSION = "1.0.0"
    PRODUCT_ID     = "22-az-sge"

    def __init__(self, config: Optional[SGEConfig] = None) -> None:
        self._cfg = config or SGEConfig()
        self._start_time = time.time()

        # Audit chain (all events committed here)
        self._chain = HashChain()

        # Subsystems
        self._threat_intel = ThreatIntelligenceEngine(
            nvd_api_key=self._cfg.nvd_api_key,
            custom_ioc=self._cfg.custom_ioc,
        )
        self._malware = MalwareDetector(
            threat_engine=self._threat_intel,
            yara_rules=self._cfg.custom_yara_rules,
            baseline=self._cfg.file_baseline,
        )
        self._zero_day = ZeroDayEngine()
        self._ids = IntrusionDetector()
        self._firewall = PolicyEngine(rules=self._cfg.custom_firewall_rules)
        self._surveillance = SurveillanceGuard(
            custom_trackers=self._cfg.custom_trackers,
            device_baseline=self._cfg.device_baseline,
        )
        self._dep_auditor = DependencyAuditor()
        self._quarantine = QuarantineOrchestrator(
            vault=QuarantineVault(self._cfg.quarantine_dir),
            chain=self._chain,
            auto_quarantine_threshold=self._cfg.auto_quarantine_threshold,
        )

        # Encryption key pair for this session
        self._keypair: KeyPair = generate_keypair()

        # Canary registry: {path: expected_sha256}
        self._canaries: Dict[str, str] = {}
        for p in (self._cfg.canary_paths or []):
            try:
                sha = create_canary_file(p)
                self._canaries[p] = sha
            except Exception:
                pass

        # Unified event log for dashboard
        self._events: List[SecurityEvent] = []

        # Commit engine start to chain
        self._chain.commit(
            json.dumps({
                "event": "SGE_START",
                "version": self.ENGINE_VERSION,
                "config": self._cfg.to_dict(),
            }).encode(),
            payload_type="engine_lifecycle",
            payload_summary="SGE Core started",
        )

    # ------------------------------------------------------------------
    # File scanning
    # ------------------------------------------------------------------

    def scan_file(
        self,
        path: str | Path,
        also_zero_day: bool = True,
    ) -> Tuple[FileScanResult, Optional[QuarantineRecord]]:
        """Scan a file for malware, YARA matches, zero-day heuristics.

        Returns (FileScanResult, QuarantineRecord | None).
        QuarantineRecord is None if the file was clean.
        """
        p = Path(path)
        data = p.read_bytes() if p.is_file() else b""
        scan = self._malware.scan_bytes(data, filename=str(path))

        qr = None
        if scan.threat_score > 0:
            qr = self._quarantine.handle_file_scan(scan, data)
            self._emit_event("file_scan", scan.risk_level, scan.threat_score,
                             f"File scan: {p.name}", scan.to_dict().__str__()[:256], str(path))

        # Zero-day pass
        if also_zero_day:
            zd = self._zero_day.scan(data, filename=str(path))
            if zd.is_suspicious and (qr is None or zd.max_confidence > scan.threat_score):
                zd_qr = self._quarantine.handle_zero_day(zd, data)
                self._emit_event("zero_day", zd.verdict, zd.max_confidence,
                                 f"Zero-day: {p.name}", f"hits: {[h.heuristic for h in zd.hits]}", str(path))
                if qr is None:
                    qr = zd_qr

        return scan, qr

    def scan_directory(
        self,
        directory: str | Path,
        recursive: bool = True,
    ) -> List[FileScanResult]:
        """Scan all files in a directory.  Returns all results (clean + flagged)."""
        return self._malware.scan_directory(directory, recursive=recursive)

    def check_canaries(self) -> List[str]:
        """Check all registered canary files.  Returns list of tampered paths."""
        tampered = []
        for path, expected_sha in self._canaries.items():
            if not check_canary_file(path, expected_sha):
                tampered.append(path)
                self._emit_event(
                    "file_scan", "CRITICAL", 95.0,
                    f"Canary tampered: {path}",
                    "Canary file was modified — possible ransomware encryption",
                    path,
                )
        return tampered

    # ------------------------------------------------------------------
    # Network & process inspection
    # ------------------------------------------------------------------

    def inspect_network(
        self,
        event: NetworkEvent,
        direction: Direction = Direction.INBOUND,
    ) -> Tuple[List[IDSAlert], FirewallDecision]:
        """Inspect a network event: IDS + firewall.

        Returns (alerts, firewall_decision).
        """
        decision = self._firewall.evaluate(event, direction)
        alerts = self._ids.inspect_network(event)
        for alert in alerts:
            if alert.score >= 70:
                self._quarantine.handle_ids_alert(alert)
                self._emit_event("ids_alert", alert.severity.value, alert.score,
                                 f"IDS: {alert.rule_name}", alert.description, alert.src_ip)
        return alerts, decision

    def inspect_process(self, event: ProcessEvent) -> List[IDSAlert]:
        """Inspect a process event through the IDS."""
        alerts = self._ids.inspect_process(event)
        for alert in alerts:
            self._emit_event("ids_alert", alert.severity.value, alert.score,
                             f"Process alert: {alert.rule_name}", alert.description,
                             event.name)
        return alerts

    def firewall_evaluate(
        self, event: NetworkEvent, direction: Direction = Direction.INBOUND
    ) -> FirewallDecision:
        """Evaluate firewall policy for one event."""
        return self._firewall.evaluate(event, direction)

    # ------------------------------------------------------------------
    # URL / zero-day scanning
    # ------------------------------------------------------------------

    def check_url_payload(
        self, url: str, data: bytes, content_type: str = ""
    ) -> ZeroDayScanResult:
        """Check a URL's response payload for zero-day / exploit kit patterns."""
        result = self._zero_day.scan_url_payload(url, data, content_type)
        if result.is_suspicious:
            self._quarantine.handle_zero_day(result, data)
            self._emit_event("zero_day", result.verdict, result.max_confidence,
                             f"URL zero-day: {url[:64]}", result.to_dict().__str__()[:256], url)
        return result

    # ------------------------------------------------------------------
    # Domain / IP / tracker checks
    # ------------------------------------------------------------------

    def check_domain(self, domain: str) -> Tuple[bool, Optional[str]]:
        """Check if a domain is a known tracker/C2."""
        return self._surveillance.check_domain(domain)

    def check_threat_intel_domain(self, domain: str) -> Optional[ThreatIndicator]:
        return self._threat_intel.lookup_domain(domain)

    def check_threat_intel_ip(self, ip: str) -> Optional[ThreatIndicator]:
        return self._threat_intel.lookup_ip(ip)

    # ------------------------------------------------------------------
    # Dependency audit
    # ------------------------------------------------------------------

    def audit_dependencies(self, path: str | Path) -> List[VulnerableDependency]:
        """Audit dependency manifests at path (file or directory)."""
        p = Path(path)
        if p.is_file():
            return self._dep_auditor.audit_file(p)
        return self._dep_auditor.audit_directory(p)

    def dependency_report(self, path: str | Path) -> VulnerabilityReport:
        vulns = self.audit_dependencies(path)
        report = VulnerabilityReport(target=str(path), dependency_vulns=vulns)
        report.compute_risk_score()
        return report

    # ------------------------------------------------------------------
    # Privacy / surveillance
    # ------------------------------------------------------------------

    def full_privacy_audit(
        self,
        page_content: Optional[bytes] = None,
        connections: Optional[List[dict]] = None,
    ) -> List[PrivacyAlert]:
        """Run full privacy / anti-surveillance audit."""
        alerts = self._surveillance.full_audit(page_content, connections)
        for a in alerts:
            self._emit_event("privacy", a.severity, 0.0, f"Privacy: {a.category}",
                             a.description, a.evidence[:64])
        return alerts

    # ------------------------------------------------------------------
    # Threat intel
    # ------------------------------------------------------------------

    def refresh_threat_intel(self) -> int:
        """Refresh all threat intel feeds.  Returns count of indicators."""
        return self._threat_intel.refresh()

    def threat_intel_summary(self) -> dict:
        return self._threat_intel.summary()

    def lookup_file_hash(self, file_hash: str) -> Optional[ThreatIndicator]:
        return self._threat_intel.lookup_hash(file_hash)

    def lookup_cve(self, cve_id: str) -> Optional[ThreatIndicator]:
        return self._threat_intel.lookup_cve(cve_id)

    # ------------------------------------------------------------------
    # Audit chain
    # ------------------------------------------------------------------

    def chain_head(self) -> str:
        return self._chain.head()

    def verify_chain(self) -> Tuple[bool, Optional[int], Optional[str]]:
        return self._chain.verify()

    def chain_merkle_root(self) -> str:
        return merkle_root_of_chain(self._chain)

    def export_chain_json(self) -> str:
        return self._chain.export_json()

    # ------------------------------------------------------------------
    # Encryption helpers
    # ------------------------------------------------------------------

    def encrypt(self, plaintext: bytes, aad: bytes = b"") -> Tuple[str, str]:
        """Encrypt bytes with the session AES-256-GCM key derived from the keypair."""
        from .encryption import derive_session_key, SymmetricCipher
        session_key = derive_session_key(self._keypair.private_bytes)
        cipher = SymmetricCipher(session_key)
        return cipher.encrypt(plaintext, aad)

    def decrypt(self, iv_b64: str, ct_b64: str, aad: bytes = b"") -> bytes:
        from .encryption import derive_session_key, SymmetricCipher
        session_key = derive_session_key(self._keypair.private_bytes)
        cipher = SymmetricCipher(session_key)
        return cipher.decrypt(iv_b64, ct_b64, aad)

    # ------------------------------------------------------------------
    # Status / dashboard
    # ------------------------------------------------------------------

    def status(self) -> dict:
        """Full engine status report for dashboard."""
        chain_ok, bad_idx, chain_reason = self.verify_chain()
        ids_summary = self._ids.summary()
        fw_summary = self._firewall.audit_summary()
        ti_summary = self.threat_intel_summary()
        q_summary = self._quarantine.summary()

        return {
            "engine_version": self.ENGINE_VERSION,
            "product_id": self.PRODUCT_ID,
            "uptime_seconds": time.time() - self._start_time,
            "chain_length": len(self._chain),
            "chain_head": self._chain.head()[:16] + "…",
            "chain_integrity": chain_ok,
            "chain_bad_index": bad_idx,
            "threat_intel": ti_summary,
            "ids": ids_summary,
            "firewall": fw_summary,
            "quarantine": q_summary,
            "event_log_size": len(self._events),
            "blocked_ips": self._quarantine.blocked_ips(),
            "blocked_domains": self._quarantine.blocked_domains(),
            "tracker_blocklist_size": self._surveillance.tracker_blocklist.size,
            "keypair_software_mode": self._keypair.software_mode,
        }

    def recent_events(self, n: int = 50) -> List[dict]:
        """Return n most recent security events for dashboard."""
        return [e.to_dict() for e in self._events[-n:]]

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit_event(
        self,
        event_type: str,
        severity: str,
        score: float,
        title: str,
        detail: str,
        source: Optional[str] = None,
    ) -> None:
        import hashlib as _h
        ts = time.time()
        eid = _h.sha256(f"{ts}:{event_type}:{title}".encode()).hexdigest()[:12]
        link = self._chain.commit(
            json.dumps({"event_type": event_type, "title": title, "score": score}).encode(),
            payload_type=event_type,
            payload_summary=title[:64],
        )
        ev = SecurityEvent(
            event_id=eid,
            timestamp=ts,
            event_type=event_type,
            severity=severity,
            score=score,
            title=title,
            detail=detail,
            source=source,
            chain_index=link.index,
        )
        self._events.append(ev)
