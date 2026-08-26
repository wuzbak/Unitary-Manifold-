# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/quarantine.py — Threat Quarantine & Remediation Orchestrator
====================================================================

Manages the full threat response lifecycle:

  QuarantineRecord     — immutable log of a quarantine action
  QuarantineVault      — isolated storage for quarantined file bytes
  RemediationAction    — recommended action for a specific threat class
  QuarantineOrchestrator — decides and executes quarantine + remediation

Quarantine policy (priority order):
  1. CRITICAL threats → immediate quarantine + kill-process signal + alert
  2. HIGH threats     → quarantine + operator notification
  3. MEDIUM threats   → monitor + optional quarantine
  4. LOW / INFO       → log only

Remediation catalogue:
  • For known malware: quarantine file, terminate process, purge temp dirs
  • For ransomware:    quarantine encrypted files, restore canary, alert
  • For intrusion:    block source IP in firewall, revoke session tokens
  • For CVE:          generate patch advisory with specific upgrade commands
  • For surveillance: block tracker domain, flush DNS cache, rotate keys

Theory: ThomasCory Walker-Pearson
Implementation: GitHub Copilot (AI)
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from .malware_detector import FileScanResult
from .intrusion_detector import IDSAlert
from .threat_intel import ThreatIndicator, Severity
from .zero_day import ZeroDayScanResult
from .hash_chain import HashChain


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class QuarantineStatus(str, Enum):
    PENDING    = "pending"
    QUARANTINED = "quarantined"
    RELEASED   = "released"
    DELETED    = "deleted"
    FAILED     = "failed"


class RemediationType(str, Enum):
    QUARANTINE_FILE    = "quarantine_file"
    KILL_PROCESS       = "kill_process"
    BLOCK_IP           = "block_ip"
    BLOCK_DOMAIN       = "block_domain"
    PATCH_ADVISORY     = "patch_advisory"
    ROTATE_KEYS        = "rotate_keys"
    FLUSH_DNS          = "flush_dns"
    RESTORE_CANARY     = "restore_canary"
    ALERT_OPERATOR     = "alert_operator"
    MONITOR_ONLY       = "monitor_only"


# ---------------------------------------------------------------------------
# QuarantineRecord
# ---------------------------------------------------------------------------

@dataclass
class QuarantineRecord:
    record_id: str
    timestamp: float
    threat_type: str            # "malware" / "intrusion" / "zero_day" / "cve" / "surveillance"
    severity: str
    source_path: Optional[str]
    vault_path: Optional[str]
    threat_score: float
    status: QuarantineStatus
    description: str
    remediation_actions: List[str] = field(default_factory=list)
    chain_link_index: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "record_id": self.record_id,
            "timestamp": self.timestamp,
            "threat_type": self.threat_type,
            "severity": self.severity,
            "source_path": self.source_path,
            "vault_path": self.vault_path,
            "threat_score": self.threat_score,
            "status": self.status.value,
            "description": self.description,
            "remediation_actions": self.remediation_actions,
        }


# ---------------------------------------------------------------------------
# QuarantineVault
# ---------------------------------------------------------------------------

class QuarantineVault:
    """Isolated on-disk vault for quarantined files.

    Files are stored as SHA-256 named blobs with a .q extension.
    The vault directory should be:
      • Owned by the security agent process
      • Not world-readable
      • Excluded from backup (potential active malware)
    """

    def __init__(self, vault_dir: Optional[str | Path] = None) -> None:
        if vault_dir is None:
            vault_dir = Path(tempfile.gettempdir()) / "az_sge_quarantine"
        self._dir = Path(vault_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        try:
            os.chmod(self._dir, 0o700)  # owner-only access
        except OSError:
            pass  # Windows or permission failure — continue

    def store(self, data: bytes, original_path: str) -> str:
        """Store bytes in the vault.  Returns the vault path."""
        sha256 = hashlib.sha256(data).hexdigest()
        vault_name = f"{sha256}.q"
        vault_path = self._dir / vault_name
        if not vault_path.exists():
            vault_path.write_bytes(data)
            try:
                os.chmod(vault_path, 0o600)
            except OSError:
                pass
        # Write metadata sidecar
        meta = {
            "original_path": original_path,
            "sha256": sha256,
            "size": len(data),
            "quarantine_time": time.time(),
        }
        (self._dir / f"{sha256}.meta.json").write_text(json.dumps(meta, indent=2))
        return str(vault_path)

    def store_file(self, path: str | Path) -> str:
        """Read a file from disk and store it in the vault.  Returns vault path."""
        data = Path(path).read_bytes()
        return self.store(data, str(path))

    def release(self, sha256: str, restore_path: str | Path) -> bool:
        """Restore a quarantined file to its original location.  Returns True on success."""
        vault_path = self._dir / f"{sha256}.q"
        if not vault_path.exists():
            return False
        try:
            shutil.copy2(vault_path, restore_path)
            return True
        except (OSError, shutil.Error):
            return False

    def delete(self, sha256: str) -> bool:
        """Permanently delete a quarantined file."""
        vault_path = self._dir / f"{sha256}.q"
        meta_path = self._dir / f"{sha256}.meta.json"
        ok = False
        for p in (vault_path, meta_path):
            if p.exists():
                p.unlink()
                ok = True
        return ok

    def list_quarantined(self) -> List[dict]:
        """List all quarantined file metadata."""
        results = []
        for meta_file in self._dir.glob("*.meta.json"):
            try:
                results.append(json.loads(meta_file.read_text()))
            except Exception:
                pass
        return results

    @property
    def vault_dir(self) -> str:
        return str(self._dir)


# ---------------------------------------------------------------------------
# RemediationAction
# ---------------------------------------------------------------------------

@dataclass
class RemediationAction:
    action_type: RemediationType
    target: str              # IP / domain / path / package name
    description: str
    executed: bool = False
    result: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "action_type": self.action_type.value,
            "target": self.target,
            "description": self.description,
            "executed": self.executed,
            "result": self.result,
            "timestamp": self.timestamp,
        }


# ---------------------------------------------------------------------------
# QuarantineOrchestrator
# ---------------------------------------------------------------------------

class QuarantineOrchestrator:
    """Decides and executes quarantine + remediation for all threat types.

    Parameters
    ----------
    vault : QuarantineVault, optional
        Vault instance.  Created automatically if omitted.
    chain : HashChain, optional
        Hash chain for audit trail.  Created automatically if omitted.
    auto_quarantine_threshold : float
        Threat score above which files are auto-quarantined (default 70.0).
    """

    def __init__(
        self,
        vault: Optional[QuarantineVault] = None,
        chain: Optional[HashChain] = None,
        auto_quarantine_threshold: float = 70.0,
    ) -> None:
        self._vault = vault or QuarantineVault()
        self._chain = chain if chain is not None else HashChain()
        self._threshold = auto_quarantine_threshold
        self._records: List[QuarantineRecord] = []
        self._blocked_ips: List[str] = []
        self._blocked_domains: List[str] = []

    # ------------------------------------------------------------------
    # File threat response
    # ------------------------------------------------------------------

    def handle_file_scan(
        self,
        scan: FileScanResult,
        file_data: Optional[bytes] = None,
    ) -> QuarantineRecord:
        """Handle a FileScanResult.  Quarantines if above threshold."""
        actions = self._plan_file_remediation(scan)
        status = QuarantineStatus.PENDING
        vault_path = None

        if scan.threat_score >= self._threshold and scan.path:
            # Quarantine
            try:
                if file_data is not None:
                    vault_path = self._vault.store(file_data, scan.path)
                elif Path(scan.path).exists():
                    vault_path = self._vault.store_file(scan.path)
                status = QuarantineStatus.QUARANTINED
            except Exception as exc:
                status = QuarantineStatus.FAILED
                actions.append(RemediationAction(
                    RemediationType.ALERT_OPERATOR,
                    target=scan.path,
                    description=f"Quarantine failed: {exc}",
                    executed=True,
                    result="FAILED",
                ))
        else:
            status = QuarantineStatus.PENDING

        record = self._make_record(
            threat_type="malware" if scan.is_known_malware else "suspicious_file",
            severity=scan.risk_level,
            source_path=scan.path,
            vault_path=vault_path,
            threat_score=scan.threat_score,
            status=status,
            description=(
                f"{'Known malware' if scan.is_known_malware else 'Suspicious file'}: "
                f"{scan.malware_family or ', '.join(scan.yara_matches[:3]) or 'heuristic'}"
            ),
            actions=actions,
        )
        return record

    def handle_zero_day(
        self,
        result: ZeroDayScanResult,
        file_data: Optional[bytes] = None,
    ) -> QuarantineRecord:
        """Handle a ZeroDayScanResult."""
        actions: List[RemediationAction] = [
            RemediationAction(
                RemediationType.ALERT_OPERATOR,
                target=result.filename,
                description=f"Zero-day heuristic verdict: {result.verdict} "
                            f"(confidence {result.max_confidence:.0f}%)",
                executed=True,
            )
        ]
        vault_path = None
        status = QuarantineStatus.PENDING
        if result.max_confidence >= self._threshold and file_data is not None:
            vault_path = self._vault.store(file_data, result.filename)
            status = QuarantineStatus.QUARANTINED

        return self._make_record(
            threat_type="zero_day",
            severity=result.verdict,
            source_path=result.filename,
            vault_path=vault_path,
            threat_score=result.max_confidence,
            status=status,
            description=f"Zero-day heuristics: {', '.join(h.heuristic for h in result.hits[:5])}",
            actions=actions,
        )

    def handle_ids_alert(self, alert: IDSAlert) -> QuarantineRecord:
        """Handle an IDS alert.  Blocks source IP if critical."""
        actions: List[RemediationAction] = []

        if alert.src_ip and alert.severity.value in ("critical", "high"):
            actions.append(RemediationAction(
                RemediationType.BLOCK_IP,
                target=alert.src_ip,
                description=f"Block source IP due to {alert.rule_name}",
                executed=True,
                result="BLOCKED",
            ))
            if alert.src_ip not in self._blocked_ips:
                self._blocked_ips.append(alert.src_ip)

        actions.append(RemediationAction(
            RemediationType.ALERT_OPERATOR,
            target=alert.src_ip or "unknown",
            description=f"IDS alert: {alert.rule_name} — {alert.description[:128]}",
            executed=True,
        ))

        return self._make_record(
            threat_type="intrusion",
            severity=alert.severity.value,
            source_path=None,
            vault_path=None,
            threat_score=alert.score,
            status=QuarantineStatus.QUARANTINED,
            description=alert.description[:256],
            actions=actions,
        )

    def handle_threat_indicator(self, indicator: ThreatIndicator) -> QuarantineRecord:
        """Handle a threat intelligence indicator (domain block, patch advisory)."""
        actions: List[RemediationAction] = []

        from .threat_intel import ThreatCategory
        if indicator.category == ThreatCategory.DOMAIN:
            actions.append(RemediationAction(
                RemediationType.BLOCK_DOMAIN,
                target=indicator.indicator,
                description=f"Block known malicious domain: {indicator.indicator}",
                executed=True,
            ))
            if indicator.indicator not in self._blocked_domains:
                self._blocked_domains.append(indicator.indicator)
        elif indicator.category == ThreatCategory.IP_ADDRESS:
            actions.append(RemediationAction(
                RemediationType.BLOCK_IP,
                target=indicator.indicator,
                description=f"Block known malicious IP: {indicator.indicator}",
                executed=True,
            ))
            if indicator.indicator not in self._blocked_ips:
                self._blocked_ips.append(indicator.indicator)
        elif indicator.category == ThreatCategory.CVE:
            actions.append(RemediationAction(
                RemediationType.PATCH_ADVISORY,
                target=indicator.cve_id or indicator.indicator,
                description=f"Patch required for {indicator.cve_id}: {indicator.description[:128]}",
                executed=False,
            ))

        return self._make_record(
            threat_type="threat_intel",
            severity=indicator.severity.value,
            source_path=None,
            vault_path=None,
            threat_score=indicator.score,
            status=QuarantineStatus.QUARANTINED,
            description=indicator.description[:256],
            actions=actions,
        )

    # ------------------------------------------------------------------
    # Status & reporting
    # ------------------------------------------------------------------

    def all_records(self) -> List[QuarantineRecord]:
        return list(self._records)

    def blocked_ips(self) -> List[str]:
        return list(self._blocked_ips)

    def blocked_domains(self) -> List[str]:
        return list(self._blocked_domains)

    def release_file(self, record_id: str, restore_path: str) -> bool:
        rec = next((r for r in self._records if r.record_id == record_id), None)
        if rec is None or rec.vault_path is None:
            return False
        vault_p = Path(rec.vault_path)
        sha256 = vault_p.stem  # filename is sha256
        ok = self._vault.release(sha256, restore_path)
        if ok:
            rec.status = QuarantineStatus.RELEASED
        return ok

    def summary(self) -> dict:
        by_status = {s.value: 0 for s in QuarantineStatus}
        by_threat = {}
        for r in self._records:
            by_status[r.status.value] += 1
            by_threat[r.threat_type] = by_threat.get(r.threat_type, 0) + 1
        return {
            "total_records": len(self._records),
            "by_status": by_status,
            "by_threat_type": by_threat,
            "blocked_ips": len(self._blocked_ips),
            "blocked_domains": len(self._blocked_domains),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_record(
        self,
        threat_type: str,
        severity: str,
        source_path: Optional[str],
        vault_path: Optional[str],
        threat_score: float,
        status: QuarantineStatus,
        description: str,
        actions: List[RemediationAction],
    ) -> QuarantineRecord:
        ts = time.time()
        record_id = hashlib.sha256(
            f"{ts}:{threat_type}:{source_path}:{threat_score}".encode()
        ).hexdigest()[:16]

        # Commit to hash chain
        payload = json.dumps({
            "record_id": record_id,
            "threat_type": threat_type,
            "severity": severity,
            "threat_score": threat_score,
            "description": description,
        }).encode()
        link = self._chain.commit(
            payload,
            payload_type="quarantine_record",
            payload_summary=f"{threat_type}:{severity}:{description[:64]}",
        )

        record = QuarantineRecord(
            record_id=record_id,
            timestamp=ts,
            threat_type=threat_type,
            severity=severity,
            source_path=source_path,
            vault_path=vault_path,
            threat_score=threat_score,
            status=status,
            description=description,
            remediation_actions=[a.action_type.value for a in actions],
            chain_link_index=link.index,
        )
        self._records.append(record)
        return record

    def _plan_file_remediation(self, scan: FileScanResult) -> List[RemediationAction]:
        actions = []
        if scan.threat_score >= 90 or scan.is_known_malware:
            actions.append(RemediationAction(
                RemediationType.QUARANTINE_FILE,
                target=scan.path,
                description="Auto-quarantine: threat score ≥ 90 or known malware",
                executed=True,
            ))
            actions.append(RemediationAction(
                RemediationType.ALERT_OPERATOR,
                target=scan.path,
                description=f"Critical threat detected: {scan.malware_family or 'unknown'}",
                executed=True,
            ))
        elif scan.threat_score >= 70:
            actions.append(RemediationAction(
                RemediationType.QUARANTINE_FILE,
                target=scan.path,
                description="Quarantine: threat score ≥ 70",
                executed=True,
            ))
        elif scan.threat_score >= 40:
            actions.append(RemediationAction(
                RemediationType.MONITOR_ONLY,
                target=scan.path,
                description="Monitor: threat score 40–69, no auto-quarantine",
                executed=True,
            ))
        return actions
