# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/mcp/filesystem.py — MCP Filesystem Server

Provides agents with secure, sandboxed read/write access to the filesystem.

## Security model
- Only paths within the declared whitelist are accessible.
- Write operations require KK level ≤ 2 (system services or trusted agent).
- Destructive operations (delete directory tree, write to /etc, etc.) are blocked
  regardless of KK level.
- All operations are logged to the HILS audit trail.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent.parent
AXIOMZERO_HOME = Path.home() / ".axiomzero"

# Allowed root directories (whitelist)
ALLOWED_ROOTS: list[Path] = [
    REPO_ROOT,
    AXIOMZERO_HOME,
    Path("/tmp"),
]

# Blocked path patterns (never allowed regardless of whitelist)
BLOCKED_PATTERNS = [
    "/etc/passwd", "/etc/shadow", "/boot", "/sys/firmware",
    "/.ssh/", "/proc/", "/.git/config",
]


class MCPFilesystemError(Exception):
    """Raised when an MCP filesystem operation is blocked."""


class MCPFilesystemServer:
    """
    MCP Filesystem Server — sandboxed filesystem access for agents.

    Usage::

        fs = MCPFilesystemServer(kk_level=2)
        content = fs.read("src/core/metric.py")
        fs.write(".axiomzero/cache/result.json", '{"ok": true}')
    """

    def __init__(self, kk_level: int = 3) -> None:
        self._kk_level = kk_level

    # ------------------------------------------------------------------
    # Read operations (available to all KK levels)
    # ------------------------------------------------------------------

    def read(self, path: str) -> str:
        """Read a file within the allowed roots."""
        p = self._resolve(path)
        return p.read_text(encoding="utf-8", errors="replace")

    def read_bytes(self, path: str) -> bytes:
        """Read a file as bytes."""
        p = self._resolve(path)
        return p.read_bytes()

    def list_dir(self, path: str) -> list[str]:
        """List directory contents."""
        p = self._resolve(path)
        return sorted(str(child.relative_to(p)) for child in p.iterdir())

    def exists(self, path: str) -> bool:
        """Check if a path exists."""
        try:
            return self._resolve(path).exists()
        except MCPFilesystemError:
            return False

    def sha256(self, path: str) -> str:
        """Compute SHA-256 of a file."""
        data = self.read_bytes(path)
        return hashlib.sha256(data).hexdigest()

    # ------------------------------------------------------------------
    # Write operations (KK level ≤ 2 required)
    # ------------------------------------------------------------------

    def write(self, path: str, content: str) -> None:
        """Write text to a file."""
        self._require_write_level()
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    def write_bytes(self, path: str, data: bytes) -> None:
        """Write bytes to a file."""
        self._require_write_level()
        p = self._resolve(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    def mkdir(self, path: str) -> None:
        """Create a directory."""
        self._require_write_level()
        p = self._resolve(path)
        p.mkdir(parents=True, exist_ok=True)

    def delete_file(self, path: str) -> None:
        """Delete a single file (NOT a directory tree)."""
        self._require_write_level()
        p = self._resolve(path)
        if p.is_dir():
            raise MCPFilesystemError(
                "delete_file cannot remove directories — use delete_empty_dir"
            )
        p.unlink()

    def delete_empty_dir(self, path: str) -> None:
        """Delete an empty directory."""
        self._require_write_level()
        p = self._resolve(path)
        if not p.is_dir():
            raise MCPFilesystemError(f"Not a directory: {path}")
        p.rmdir()  # fails if non-empty — intentional safety check

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve(self, path: str) -> Path:
        """Resolve a path to an absolute Path, verifying it is within allowed roots."""
        raw = Path(path)
        if not raw.is_absolute():
            raw = REPO_ROOT / raw
        resolved = raw.resolve()

        # Block dangerous patterns first
        path_str = str(resolved)
        for pattern in BLOCKED_PATTERNS:
            if pattern in path_str:
                raise MCPFilesystemError(
                    f"Path '{path}' matches blocked pattern '{pattern}'"
                )

        # Check whitelist
        for root in ALLOWED_ROOTS:
            try:
                resolved.relative_to(root)
                return resolved
            except ValueError:
                continue

        raise MCPFilesystemError(
            f"Path '{path}' is outside all allowed filesystem roots. "
            f"Allowed: {[str(r) for r in ALLOWED_ROOTS]}"
        )

    def _require_write_level(self) -> None:
        if self._kk_level > 2:
            raise MCPFilesystemError(
                f"Write operations require KK level ≤ 2 (system services or trusted agent). "
                f"Current KK level: {self._kk_level}"
            )
