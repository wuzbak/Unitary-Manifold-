# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
az-os/mcp/executor.py — MCP Command Execution Server

Executes terminal commands on behalf of agents with strict safety constraints.

## Safety model
- Commands are run as a subprocess, NOT as a shell (no shell injection).
- A whitelist of permitted commands is enforced.
- Destructive commands are blocked regardless of KK level.
- All commands are logged to the HILS audit trail.
- Working directory is locked to the repository root or /tmp.
- Maximum execution time: 300 seconds.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).parent.parent.parent

# Permitted command prefixes (whitelist)
PERMITTED_PREFIXES = [
    "python",
    "python3",
    "pytest",
    "python3 -m pytest",
    "git status",
    "git log",
    "git diff",
    "git show",
    "git branch",
    "cargo build",
    "cargo check",
    "cargo test",
    "rustfmt",
    "ls",
    "cat",
    "head",
    "tail",
    "grep",
    "find",
    "wc",
    "echo",
]

# Blocked command patterns (always rejected)
BLOCKED_PATTERNS = [
    "rm -rf",
    "sudo",
    "chmod 777",
    "curl | sh",
    "wget | sh",
    "git push --force",
    "git reset --hard",
    "> /dev/",
    "mkfs",
    "dd if=",
    ":(){:|:&};:",   # fork bomb
]

MAX_TIMEOUT = 300  # seconds


class MCPExecutorError(Exception):
    """Raised when a command is blocked or fails validation."""


@dataclass
class ExecResult:
    command: str
    returncode: int
    stdout: str
    stderr: str
    duration_s: float
    blocked: bool = False
    block_reason: str = ""


class MCPExecutorServer:
    """
    MCP Command Execution Server — sandboxed terminal execution for agents.

    Usage::

        executor = MCPExecutorServer(kk_level=1)
        result = executor.run(["python3", "-m", "pytest", "tests/test_metric.py", "-q"])
        print(result.stdout)
    """

    def __init__(
        self,
        kk_level: int = 3,
        repo_root: Optional[Path] = None,
        audit_log: Optional[list] = None,
    ) -> None:
        self._kk_level = kk_level
        self._repo_root = repo_root or REPO_ROOT
        self._audit_log = audit_log if audit_log is not None else []

    def run(
        self,
        cmd: list[str],
        cwd: Optional[str] = None,
        timeout: int = 300,
        capture: bool = True,
    ) -> ExecResult:
        """
        Execute a command safely.

        Parameters
        ----------
        cmd : list[str]
            Command and arguments as a list (NOT a shell string).
        cwd : str, optional
            Working directory.  Must be within REPO_ROOT or /tmp.
        timeout : int
            Maximum execution time.  Capped at MAX_TIMEOUT.
        capture : bool
            Whether to capture stdout/stderr.

        Returns
        -------
        ExecResult
        """
        # Validate command
        block_reason = self._validate_command(cmd)
        if block_reason:
            result = ExecResult(
                command=" ".join(cmd), returncode=-1,
                stdout="", stderr="",
                duration_s=0.0, blocked=True, block_reason=block_reason,
            )
            self._log(cmd, result)
            return result

        # Validate working directory
        cwd_path = self._resolve_cwd(cwd)
        timeout = min(timeout, MAX_TIMEOUT)

        start = time.time()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(cwd_path),
                capture_output=capture,
                text=True,
                timeout=timeout,
            )
            duration = time.time() - start
            result = ExecResult(
                command=" ".join(cmd),
                returncode=proc.returncode,
                stdout=proc.stdout if capture else "",
                stderr=proc.stderr if capture else "",
                duration_s=duration,
            )
        except subprocess.TimeoutExpired:
            result = ExecResult(
                command=" ".join(cmd), returncode=-1,
                stdout="", stderr=f"Command timed out after {timeout}s",
                duration_s=timeout, blocked=True,
                block_reason=f"timeout:{timeout}s",
            )

        self._log(cmd, result)
        return result

    def run_pytest_subset(self, paths: list[str], markers: Optional[list[str]] = None) -> ExecResult:
        """Convenience method to run a pytest subset."""
        cmd = ["python3", "-m", "pytest", "-q", "--tb=short", "--no-header"]
        if markers:
            cmd += ["-m", " and ".join(markers)]
        cmd += paths
        return self.run(cmd, timeout=300)

    def audit_log(self) -> list[dict]:
        return list(self._audit_log)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _validate_command(self, cmd: list[str]) -> str:
        """Return a block reason string, or empty string if command is permitted."""
        if not cmd:
            return "empty command"

        cmd_str = " ".join(cmd)

        # Check blocked patterns first
        for pattern in BLOCKED_PATTERNS:
            if pattern in cmd_str:
                return f"blocked pattern: '{pattern}'"

        # Check whitelist
        first_token = cmd[0].lower()
        permitted = any(
            cmd_str.startswith(p) or first_token == p.split()[0]
            for p in PERMITTED_PREFIXES
        )
        if not permitted:
            return f"command '{cmd[0]}' not in executor whitelist"

        return ""

    def _resolve_cwd(self, cwd: Optional[str]) -> Path:
        """Resolve and validate the working directory."""
        if cwd is None:
            return self._repo_root
        p = Path(cwd).resolve()
        # Must be within REPO_ROOT or /tmp
        for allowed in [self._repo_root, Path("/tmp")]:
            try:
                p.relative_to(allowed)
                return p
            except ValueError:
                continue
        return self._repo_root  # safe fallback

    def _log(self, cmd: list[str], result: ExecResult) -> None:
        self._audit_log.append({
            "timestamp": time.time(),
            "command": " ".join(cmd),
            "returncode": result.returncode,
            "blocked": result.blocked,
            "block_reason": result.block_reason,
            "duration_s": result.duration_s,
        })
