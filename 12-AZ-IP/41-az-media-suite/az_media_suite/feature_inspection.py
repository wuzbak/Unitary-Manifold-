# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Evidence-cited, source-only feature inspection for web/Electron-style apps.

This module adapts the *evidence-based feature discovery* workflow made
popular by github.com/morluto/rea ("REA") for PsiCat/Merlin's own use,
without depending on that project's npm package or MCP server:

- REA inspects native binaries (via Hopper/Ghidra/IDA), compiled
  JS/Electron bundles, .NET assemblies, and live websites, and returns
  pseudocode/assembly plus evidence.
- This module only reads locally available, plain-text HTML/JS/TS source
  files already on disk (no binary disassembly, no execution of foreign
  code, no network calls), and reports pattern-matched "feature evidence"
  (file, line number, and the matched line text) so a reader — human or
  PsiCat — can independently verify every finding, exactly as REA's own
  docs describe ("results include the evidence and limitations behind
  each conclusion").

Every finding is conservative pattern matching, not semantic analysis: a
match means the signature text is present, not that the feature is
necessarily wired up correctly or still live.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

_SOURCE_SUFFIXES = (".js", ".jsx", ".ts", ".tsx", ".html", ".mjs", ".cjs")

# (feature label, signature substring) — intentionally small and legible so
# every entry's provenance is obvious at a glance; extend as needed.
_FEATURE_SIGNATURES: tuple[tuple[str, str], ...] = (
    ("fetch_network_call", "fetch("),
    ("xhr_network_call", "XMLHttpRequest"),
    ("websocket", "WebSocket("),
    ("event_listener", "addEventListener("),
    ("local_storage", "localStorage"),
    ("indexed_db", "indexedDB"),
    ("service_worker", "serviceWorker"),
    ("canvas_rendering", "getContext("),
    ("media_devices", "navigator.mediaDevices"),
    ("electron_ipc_renderer", "ipcRenderer"),
    ("electron_ipc_main", "ipcMain"),
    ("electron_context_bridge", "contextBridge"),
    ("web_worker", "new Worker("),
    ("clipboard_api", "navigator.clipboard"),
    ("notifications_api", "new Notification("),
    ("file_system_access", "showOpenFilePicker"),
)


@dataclass(frozen=True)
class InspectionFinding:
    feature: str
    file: str
    line: int
    snippet: str


@dataclass(frozen=True)
class FeatureInspectionReport:
    root: str
    files_scanned: int
    findings: list[InspectionFinding] = field(default_factory=list)

    def features_present(self) -> list[str]:
        return sorted({finding.feature for finding in self.findings})

    def findings_for(self, feature: str) -> list[InspectionFinding]:
        return [f for f in self.findings if f.feature == feature]


def _iter_source_files(root: Path) -> list[Path]:
    return sorted(
        p
        for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() in _SOURCE_SUFFIXES
    )


def scan_app_features(
    root_dir: str | Path,
    signatures: tuple[tuple[str, str], ...] = _FEATURE_SIGNATURES,
) -> FeatureInspectionReport:
    """Scan local HTML/JS/TS source under `root_dir` for known feature signatures.

    Returns an evidence report: every finding cites the exact file, line
    number, and matched line text, so the result can be independently
    re-verified against the source on disk.
    """
    root = Path(root_dir)
    if not root.is_dir():
        raise NotADirectoryError(f"{root_dir} is not a directory")

    files = _iter_source_files(root)
    findings: list[InspectionFinding] = []
    for file_path in files:
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        relative = str(file_path.relative_to(root))
        for line_no, line in enumerate(text.splitlines(), start=1):
            for feature, signature in signatures:
                if signature in line:
                    findings.append(
                        InspectionFinding(
                            feature=feature,
                            file=relative,
                            line=line_no,
                            snippet=line.strip()[:200],
                        )
                    )

    return FeatureInspectionReport(root=str(root), files_scanned=len(files), findings=findings)
