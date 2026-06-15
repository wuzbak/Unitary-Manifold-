# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero mcp/filesystem_server.py — Sandboxed MCP Filesystem Server

Provides secure read/write access to declared root paths only.
Any path outside the declared roots is rejected with a permission error.
Read-only mode is applied to paths outside explicitly allowed write roots.

Security properties:
  - Path traversal attacks blocked (.. components normalized away)
  - Symlink following restricted to within allowed roots
  - No access outside declared paths regardless of user input

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class FilesystemServer:
    """
    Sandboxed filesystem R/W server for MCP agents.

    Usage::

        fs = FilesystemServer(
            allowed_roots=["/home/user/Unitary-Manifold-"],
            write_roots=["/home/user/Unitary-Manifold-/AxiomZero"],
        )
        content = fs.read("src/core/metric.py")
        fs.write("AxiomZero/output.md", "# Result\n...")
    """

    def __init__(
        self,
        allowed_roots: Optional[List[str]] = None,
        write_roots: Optional[List[str]] = None,
        repo_root: Optional[Path] = None,
    ):
        # Default allowed root is the repository
        self.repo_root = repo_root or Path(__file__).parent.parent.parent
        self.allowed_roots: List[Path] = [
            Path(r).resolve() for r in (allowed_roots or [str(self.repo_root)])
        ]
        self.write_roots: List[Path] = [
            Path(r).resolve() for r in (write_roots or [str(self.repo_root / "AxiomZero")])
        ]
        logger.info("FilesystemServer: allowed=%s write=%s", self.allowed_roots, self.write_roots)

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    def read(self, rel_or_abs_path: str) -> str:
        """Read a file.  Path must be within allowed_roots."""
        target = self._resolve(rel_or_abs_path)
        self._check_read(target)
        if not target.exists():
            raise FileNotFoundError(f"File not found: {rel_or_abs_path}")
        if target.is_dir():
            raise IsADirectoryError(f"Path is a directory: {rel_or_abs_path}")
        return target.read_text(errors="replace")

    def write(self, rel_or_abs_path: str, content: str) -> None:
        """Write a file.  Path must be within write_roots."""
        target = self._resolve(rel_or_abs_path)
        self._check_write(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        logger.info("FilesystemServer.write: %s (%d chars)", target, len(content))

    def list_dir(self, rel_or_abs_path: str) -> List[Dict]:
        """List directory contents.  Path must be within allowed_roots."""
        target = self._resolve(rel_or_abs_path)
        self._check_read(target)
        if not target.is_dir():
            raise NotADirectoryError(f"Not a directory: {rel_or_abs_path}")
        entries = []
        for child in sorted(target.iterdir()):
            entries.append({
                "name": child.name,
                "type": "dir" if child.is_dir() else "file",
                "size": child.stat().st_size if child.is_file() else None,
            })
        return entries

    def exists(self, rel_or_abs_path: str) -> bool:
        """Check if a path exists (within allowed_roots)."""
        try:
            target = self._resolve(rel_or_abs_path)
            self._check_read(target)
            return target.exists()
        except PermissionError:
            return False

    def stat(self, rel_or_abs_path: str) -> Dict:
        """Get file metadata."""
        target = self._resolve(rel_or_abs_path)
        self._check_read(target)
        s = target.stat()
        return {
            "path": str(target),
            "size": s.st_size,
            "mtime": s.st_mtime,
            "is_file": target.is_file(),
            "is_dir": target.is_dir(),
        }

    def search(self, root: str, pattern: str) -> List[str]:
        """Recursive glob search within allowed_roots."""
        target = self._resolve(root)
        self._check_read(target)
        if not target.is_dir():
            return []
        return [str(p.relative_to(self.repo_root)) for p in target.rglob(pattern)
                if self._within_any(p, self.allowed_roots)]

    # ------------------------------------------------------------------
    # Security helpers
    # ------------------------------------------------------------------

    def _resolve(self, path_str: str) -> Path:
        """Resolve a relative or absolute path, stripping traversal."""
        p = Path(path_str)
        if p.is_absolute():
            resolved = p.resolve()
        else:
            resolved = (self.repo_root / p).resolve()
        return resolved

    def _within_any(self, path: Path, roots: List[Path]) -> bool:
        try:
            for root in roots:
                path.relative_to(root)
                return True
        except ValueError:
            pass
        return False

    def _check_read(self, path: Path) -> None:
        if not self._within_any(path, self.allowed_roots):
            raise PermissionError(
                f"Access denied: {path} is outside allowed roots {self.allowed_roots}"
            )

    def _check_write(self, path: Path) -> None:
        if not self._within_any(path, self.write_roots):
            raise PermissionError(
                f"Write access denied: {path} is outside write roots {self.write_roots}"
            )
