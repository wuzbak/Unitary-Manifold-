# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero mcp/execution_server.py — Safety-wrapped Command Execution Server

Wraps shell/PowerShell with a strict safety layer:
  - Commands matched against an explicit whitelist
  - Destructive commands BLOCKED and LOGGED (never silently rejected)
  - Path traversal patterns (.., absolute paths outside repo) rejected
  - All executions logged to the state DB for audit
  - No command runs without passing the safety check

Blocked command examples: rm -rf, git reset --hard, git push --force,
                          sudo rm, anything with .. path components

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import asyncio
import logging
import re
import shlex
import time
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Safety configuration
# ---------------------------------------------------------------------------

DEFAULT_WHITELIST = [
    # pytest / testing
    r"^pytest\b", r"^python\s+-m\s+pytest\b", r"^python3?\s+-m\s+pytest\b",
    # Python execution (restricted)
    r"^python3?\s+-c\s+", r"^python3?\s+\S+\.py\b",
    # git read-only operations
    r"^git\s+(status|diff|log|show|branch|tag|stash list|remote -v)\b",
    r"^git\s+diff\b", r"^git\s+log\b",
    # file inspection
    r"^cat\s+", r"^head\s+", r"^tail\s+", r"^grep\s+", r"^find\s+",
    r"^ls\s+", r"^wc\s+",
    # system info (read-only)
    r"^nvidia-smi\b", r"^df\s+", r"^free\b", r"^uname\b",
    # ollama
    r"^ollama\s+(list|show|ps)\b",
]

BLOCKED_PATTERNS = [
    # Destructive file operations
    r"rm\s+-r", r"rm\s+--recursive", r"rmdir",
    r"shred\b", r"wipe\b", r"mkfs\b", r"dd\s+if=", r"\bdd\b.*of=",
    # Dangerous git operations
    r"git\s+reset\s+--hard", r"git\s+push\s+--force", r"git\s+push\s+-f\b",
    r"git\s+clean\s+-f", r"git\s+checkout\s+--",
    # Privilege escalation
    r"\bsudo\b", r"\bsu\s+-\b", r"\bdoas\b", r"\bchmod\s+777\b",
    # Network misuse
    r"\bcurl\b.*\|\s*(bash|sh|python)", r"\bwget\b.*\|\s*(bash|sh|python)",
    # Path traversal outside repo
    r"\.\./", r"/etc/", r"/proc/", r"/sys/", r"/boot/", r"/dev/",
    # Shell expansion abuse
    r";\s*rm\b", r"&&\s*rm\b", r"\|\s*sh\b", r"`.*`",
    # Fork bombs / resource exhaustion
    r":\(\)\{", r"yes\s*\|", r"while\s+true",
    # System-level commands
    r"\bkill\s+-9\s+1\b", r"\bpkill\b", r"\bhalt\b", r"\breboot\b", r"\bpoweroff\b",
    r"\biptables\b", r"\bnftables\b",
]

BLOCKED_PATTERN_RE = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]
WHITELIST_RE = [re.compile(p, re.IGNORECASE) for p in DEFAULT_WHITELIST]


class ExecutionServer:
    """
    Safety-wrapped command execution for AxiomZero agents.

    Usage::

        server = ExecutionServer(repo_root=repo_root)
        result = await server.run("pytest tests/test_metric.py -q")
    """

    def __init__(
        self,
        repo_root: Path,
        extra_whitelist: Optional[List[str]] = None,
        timeout: int = 120,
        log_db=None,
    ):
        self.repo_root = repo_root
        self.timeout = timeout
        self.log_db = log_db  # Optional StateDB instance

        # Extend whitelist if provided
        self._whitelist = list(WHITELIST_RE)
        if extra_whitelist:
            self._whitelist += [re.compile(p, re.IGNORECASE) for p in extra_whitelist]

        self._exec_log: List[Dict] = []

    async def run(
        self,
        command: str,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> Dict:
        """
        Run a shell command after safety validation.

        Returns dict with: ok, stdout, stderr, returncode, blocked_reason
        """
        start = time.time()
        check = self._safety_check(command)

        if not check["allowed"]:
            reason = check["reason"]
            logger.warning("BLOCKED command: %s — reason: %s", command, reason)
            self._audit_log(command, blocked=True, reason=reason)
            return {
                "ok": False,
                "blocked": True,
                "blocked_reason": reason,
                "stdout": "",
                "stderr": f"BLOCKED: {reason}",
                "returncode": -99,
                "command": command,
            }

        logger.info("EXEC: %s", command)
        self._audit_log(command, blocked=False)

        # Sandbox the working directory to within the repo root
        if cwd:
            requested_cwd = Path(cwd).resolve()
            if not str(requested_cwd).startswith(str(self.repo_root)):
                cwd = str(self.repo_root)
                logger.warning("CWD outside repo root; redirected to %s", cwd)
        work_dir = cwd or str(self.repo_root)

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work_dir,
                env=env,
            )
            try:
                stdout_b, stderr_b = await asyncio.wait_for(
                    proc.communicate(), timeout=self.timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                return {
                    "ok": False,
                    "blocked": False,
                    "stdout": "",
                    "stderr": f"TIMEOUT after {self.timeout}s",
                    "returncode": -1,
                    "command": command,
                    "elapsed": time.time() - start,
                }

            return {
                "ok": proc.returncode == 0,
                "blocked": False,
                "stdout": stdout_b.decode(errors="replace")[-10000:],
                "stderr": stderr_b.decode(errors="replace")[-3000:],
                "returncode": proc.returncode,
                "command": command,
                "elapsed": time.time() - start,
            }
        except Exception as exc:
            logger.error("Execution failed: %s — %s", command, exc)
            return {
                "ok": False,
                "blocked": False,
                "error": str(exc),
                "stdout": "",
                "stderr": str(exc),
                "returncode": -2,
                "command": command,
                "elapsed": time.time() - start,
            }

    def _safety_check(self, command: str) -> Dict:
        """
        Check a command against blocked and whitelist patterns.
        Returns: {"allowed": bool, "reason": str}
        """
        cmd_stripped = command.strip()

        # Step 1: Check for blocked patterns (highest priority)
        for pat in BLOCKED_PATTERN_RE:
            if pat.search(cmd_stripped):
                return {
                    "allowed": False,
                    "reason": f"Matched blocked pattern: {pat.pattern!r}",
                }

        # Step 2: Check whitelist
        for pat in self._whitelist:
            if pat.match(cmd_stripped):
                return {"allowed": True, "reason": "Matches whitelist"}

        # Step 3: Default deny
        return {
            "allowed": False,
            "reason": "Command not on whitelist — default deny",
        }

    def _audit_log(self, command: str, blocked: bool, reason: str = "") -> None:
        entry = {
            "ts": time.time(),
            "command": command[:500],
            "blocked": blocked,
            "reason": reason,
        }
        self._exec_log.append(entry)
        if self.log_db:
            try:
                self.log_db.log(
                    "MCP_Execution",
                    f"{'BLOCKED' if blocked else 'EXEC'}: {command[:200]} — {reason}",
                    level="WARN" if blocked else "INFO",
                )
            except Exception:
                pass

    def get_execution_log(self) -> List[Dict]:
        return list(self._exec_log)

    def get_blocked_attempts(self) -> List[Dict]:
        return [e for e in self._exec_log if e.get("blocked")]
