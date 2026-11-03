# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
engine/quarantine.py — Threat Quarantine & Remediation Orchestrator
====================================================================

Maintains local response records and copies flagged content into an owner-only
vault. It does not isolate source files or apply host-level remediation.

  QuarantineRecord     — audit record of a local analysis or recommendation
  QuarantineVault      — owner-only storage for copies of flagged file bytes
  RemediationAction    — recommendation and whether this process performed it
  QuarantineOrchestrator — vault-copy and record coordinator

File policy:
  • Above threshold: store a separate vault copy; leave the source untouched
  • Missing/unreadable content: record a failed vault operation
  • Below threshold: record the finding without a vault copy

Network blocks, process actions, notifications, and patching remain
recommendations; this module has no host-enforcement adapter.

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
    VAULTED    = "vaulted"
    QUARANTINED = "quarantined"
    RECORDED   = "recorded"
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
    remediation_details: List[dict] = field(default_factory=list)
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
            "remediation_details": self.remediation_details,
        }


# ---------------------------------------------------------------------------
# QuarantineVault
# ---------------------------------------------------------------------------

class QuarantineVault:
    """Owner-only on-disk vault for copies of flagged files.

    Files are stored as SHA-256 named blobs with a .q extension.
    This does not remove or disable the original file.
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
        """Read a file from disk and store a copy in the vault."""
        data = Path(path).read_bytes()
        return self.store(data, str(path))

    def release(self, sha256: str, restore_path: str | Path) -> bool:
        """Copy a vaulted file to a restore path.  Returns True on success."""
        vault_path = self._dir / f"{sha256}.q"
        if not vault_path.exists():
            return False
        try:
            shutil.copy2(vault_path, restore_path)
            return True
        except (OSError, shutil.Error):
            return False

    def delete(self, sha256: str) -> bool:
        """Permanently delete a vaulted copy."""
        vault_path = self._dir / f"{sha256}.q"
        meta_path = self._dir / f"{sha256}.meta.json"
        ok = False
        for p in (vault_path, meta_path):
            if p.exists():
                p.unlink()
                ok = True
        return ok

    def list_quarantined(self) -> List[dict]:
        """List stored-copy metadata; malformed entries raise an error."""
        results = []
        for meta_file in sorted(self._dir.glob("*.meta.json")):
            data = json.loads(meta_file.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError(f"Invalid quarantine metadata: {meta_file}")
            results.append(data)
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
    """Vaults flagged content and records local response recommendations.

    Parameters
    ----------
    vault : QuarantineVault, optional
        Vault instance.  Created automatically if omitted.
    chain : HashChain, optional
        Hash chain for audit trail.  Created automatically if omitted.
    auto_quarantine_threshold : float
        Threat score above which supplied/readable content is copied to the
        local vault (default 70.0). The source is not isolated or removed.
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
        """Store flagged bytes in the local vault above threshold.

        The original file is never moved, deleted, or disabled.
        """
        actions = self._plan_file_remediation(scan)
        status = QuarantineStatus.PENDING
        vault_path = None

        if scan.threat_score >= self._threshold:
            try:
                if file_data is not None:
                    vault_path = self._vault.store(file_data, scan.path or "<memory>")
                elif scan.path and Path(scan.path).is_file():
                    vault_path = self._vault.store_file(scan.path)
                else:
                    raise FileNotFoundError("No readable source file or supplied file bytes.")
                status = QuarantineStatus.VAULTED
                for action in actions:
                    if action.action_type == RemediationType.QUARANTINE_FILE:
                        action.executed = True
                        action.result = "Stored a separate vault copy; source bytes were not removed."
            except (OSError, ValueError, TypeError) as exc:
                status = QuarantineStatus.FAILED
                actions.append(RemediationAction(
                    RemediationType.ALERT_OPERATOR,
                    target=scan.path,
                    description=f"Vault copy failed: {exc}",
                    result="No notification transport is configured.",
                ))

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
                result="No notification transport is configured.",
            )
        ]
        vault_path = None
        status = QuarantineStatus.PENDING
        if result.max_confidence >= self._threshold and file_data is not None:
            vault_path = self._vault.store(file_data, result.filename)
            status = QuarantineStatus.VAULTED
            actions.append(RemediationAction(
                RemediationType.QUARANTINE_FILE,
                target=result.filename,
                description="Store flagged content in the local vault.",
                executed=True,
                result="Stored a separate vault copy; source bytes were not removed.",
            ))

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
        """Record an IDS alert and local block recommendation."""
        actions: List[RemediationAction] = []

        if alert.src_ip and alert.severity.value in ("critical", "high"):
            actions.append(RemediationAction(
                RemediationType.BLOCK_IP,
                target=alert.src_ip,
                description=f"Recommend blocking source IP due to {alert.rule_name}",
                result="Local recommendation only; no host firewall adapter is configured.",
            ))
            if alert.src_ip not in self._blocked_ips:
                self._blocked_ips.append(alert.src_ip)

        actions.append(RemediationAction(
            RemediationType.ALERT_OPERATOR,
            target=alert.src_ip or "unknown",
            description=f"IDS alert: {alert.rule_name} — {alert.description[:128]}",
            result="No notification transport is configured.",
        ))

        return self._make_record(
            threat_type="intrusion",
            severity=alert.severity.value,
            source_path=None,
            vault_path=None,
            threat_score=alert.score,
            status=QuarantineStatus.RECORDED,
            description=alert.description[:256],
            actions=actions,
        )

    def handle_threat_indicator(self, indicator: ThreatIndicator) -> QuarantineRecord:
        """Record a threat indicator and local block or patch recommendation."""
        actions: List[RemediationAction] = []

        from .threat_intel import ThreatCategory
        if indicator.category == ThreatCategory.DOMAIN:
            actions.append(RemediationAction(
                RemediationType.BLOCK_DOMAIN,
                target=indicator.indicator,
                description=f"Recommend blocking known malicious domain: {indicator.indicator}",
                result="Local recommendation only; no host DNS/firewall adapter is configured.",
            ))
            if indicator.indicator not in self._blocked_domains:
                self._blocked_domains.append(indicator.indicator)
        elif indicator.category == ThreatCategory.IP_ADDRESS:
            actions.append(RemediationAction(
                RemediationType.BLOCK_IP,
                target=indicator.indicator,
                description=f"Recommend blocking known malicious IP: {indicator.indicator}",
                result="Local recommendation only; no host firewall adapter is configured.",
            ))
            if indicator.indicator not in self._blocked_ips:
                self._blocked_ips.append(indicator.indicator)
        elif indicator.category == ThreatCategory.CVE:
            actions.append(RemediationAction(
                RemediationType.PATCH_ADVISORY,
                target=indicator.cve_id or indicator.indicator,
                description=f"Patch required for {indicator.cve_id}: {indicator.description[:128]}",
            ))

        return self._make_record(
            threat_type="threat_intel",
            severity=indicator.severity.value,
            source_path=None,
            vault_path=None,
            threat_score=indicator.score,
            status=QuarantineStatus.RECORDED,
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
        sha256 = vault_p.stem
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

        payload = json.dumps({
            "record_id": record_id,
            "threat_type": threat_type,
            "severity": severity,
            "threat_score": threat_score,
            "status": status.value,
            "source_path": source_path,
            "vault_path": vault_path,
            "description": description,
            "remediation_details": [action.to_dict() for action in actions],
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
            remediation_details=[a.to_dict() for a in actions],
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
                description="Recommend vaulting: threat score ≥ 90 or known malware",
            ))
            actions.append(RemediationAction(
                RemediationType.ALERT_OPERATOR,
                target=scan.path,
                description=f"Critical threat detected: {scan.malware_family or 'unknown'}",
                result="No notification transport is configured.",
            ))
        elif scan.threat_score >= 70:
            actions.append(RemediationAction(
                RemediationType.QUARANTINE_FILE,
                target=scan.path,
                description="Recommend vaulting: threat score ≥ 70",
            ))
        elif scan.threat_score >= 40:
            actions.append(RemediationAction(
                RemediationType.MONITOR_ONLY,
                target=scan.path,
                description="Monitor: threat score 40–69, no auto-quarantine",
            ))
        return actions
