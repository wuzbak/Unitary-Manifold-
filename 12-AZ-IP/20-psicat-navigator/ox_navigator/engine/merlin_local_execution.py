# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Fail-closed local execution loop for sovereign PsiCat runtime checks."""

from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import shlex
import shutil
import subprocess
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
_DEFAULT_ALLOWED_COMMANDS = (
    "python",
    "python3",
    "pytest",
    "ruff",
    "mypy",
)


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def _env_bool(name: str, default: bool = True) -> bool:
    raw = str(os.environ.get(name) or "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def _max_timeout_seconds() -> int:
    raw = str(os.environ.get("MERLIN_LOCAL_EXECUTION_MAX_TIMEOUT") or "").strip()
    if not raw:
        return 120
    try:
        value = int(raw)
    except ValueError:
        return 120
    return max(5, min(value, 600))


def _allowed_commands() -> tuple[str, ...]:
    raw = str(os.environ.get("MERLIN_LOCAL_EXECUTION_ALLOWED_COMMANDS") or "").strip()
    if not raw:
        return _DEFAULT_ALLOWED_COMMANDS
    candidates = tuple(
        sorted(
            {
                token.strip().lower()
                for token in raw.split(",")
                if token.strip()
            }
        )
    )
    return candidates or _DEFAULT_ALLOWED_COMMANDS


def _resolve_cwd(candidate: str | None) -> Path:
    base = REPO_ROOT.resolve()
    if not candidate:
        return base
    raw = Path(candidate).expanduser()
    path = raw.resolve() if raw.is_absolute() else (base / raw).resolve()
    path.relative_to(base)
    return path


def _safe_subprocess_env() -> dict[str, str]:
    keep = {
        "PATH",
        "HOME",
        "LANG",
        "LC_ALL",
        "LC_CTYPE",
        "PYTHONPATH",
        "PYTHONHOME",
        "VIRTUAL_ENV",
    }
    return {
        key: value
        for key, value in os.environ.items()
        if key in keep and isinstance(value, str)
    }


def get_local_execution_status() -> dict[str, Any]:
    enabled = _env_bool("MERLIN_LOCAL_EXECUTION_ENABLED", True)
    return {
        "enabled": enabled,
        "mode": "fail_closed_local_execution_loop",
        "repo_root": str(REPO_ROOT),
        "max_timeout_seconds": _max_timeout_seconds(),
        "allowed_commands": list(_allowed_commands()),
        "policy": {
            "default": "deny_on_unallowlisted_command_or_out_of_repo_cwd",
            "execution_shell": "disabled",
            "external_token_path": "local_first_before_external_fallback",
        },
        "checked_at": _utcnow(),
    }


def run_local_execution_loop(
    *,
    command: str,
    cwd: str | None = None,
    timeout_seconds: int | None = None,
) -> dict[str, Any]:
    status = get_local_execution_status()
    if not status["enabled"]:
        return {
            "ok": False,
            "error": "Local execution loop is disabled by policy.",
            "governance": {"fail_closed": True, "reason": "local_execution_disabled"},
            "status": status,
            "contract": {
                "body": "Local execution denied: execution loop disabled by policy.",
                "followups": [
                    "Enable MERLIN_LOCAL_EXECUTION_ENABLED to allow local execution.",
                    "Retry the command using the local lane once policy is enabled.",
                ],
                "sources": [
                    "env:MERLIN_LOCAL_EXECUTION_ENABLED | GOVERNANCE | local execution control switch",
                ],
            },
        }
    raw_command = str(command or "").strip()
    if not raw_command:
        return {
            "ok": False,
            "error": "command is required",
            "governance": {"fail_closed": True, "reason": "missing_command"},
            "status": status,
            "contract": {
                "body": "Local execution denied: command was empty.",
                "followups": [
                    "Provide a non-empty command string.",
                    "Use only allowlisted command prefixes.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | non-empty command requirement",
                ],
            },
        }
    try:
        argv = shlex.split(raw_command)
    except ValueError as exc:
        return {
            "ok": False,
            "error": f"Unable to parse command: {exc}",
            "governance": {"fail_closed": True, "reason": "command_parse_failure"},
            "status": status,
            "contract": {
                "body": "Local execution denied: command parsing failed.",
                "followups": [
                    "Fix command quoting and retry.",
                    "Prefer explicit arguments over shell-style chaining.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | command parser fail-closed path",
                ],
            },
        }
    if not argv:
        return {
            "ok": False,
            "error": "command is required",
            "governance": {"fail_closed": True, "reason": "missing_command"},
            "status": status,
            "contract": {
                "body": "Local execution denied: command tokenization produced no executable.",
                "followups": [
                    "Provide a concrete executable and arguments.",
                    "Keep execution inside repository boundaries.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | executable token required",
                ],
            },
        }
    command_name = Path(argv[0]).name.lower()
    if Path(argv[0]).name != argv[0]:
        return {
            "ok": False,
            "error": "Path-qualified executables are not allowed.",
            "governance": {"fail_closed": True, "reason": "path_qualified_executable_forbidden"},
            "status": status,
            "contract": {
                "body": "Local execution denied: executable must be referenced by allowlisted command name only.",
                "followups": [
                    "Use an allowlisted executable name (for example `python` or `pytest`).",
                    "Do not pass absolute or relative executable paths.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | executable path hardening",
                ],
            },
        }
    allowed = set(_allowed_commands())
    if command_name not in allowed:
        return {
            "ok": False,
            "error": f"Command not allowlisted: {command_name}",
            "governance": {"fail_closed": True, "reason": "command_not_allowlisted"},
            "status": status,
            "contract": {
                "body": f"Local execution denied: `{command_name}` is not allowlisted.",
                "followups": [
                    "Use an allowlisted executable for local validation.",
                    "If truly required, update MERLIN_LOCAL_EXECUTION_ALLOWED_COMMANDS explicitly.",
                ],
                "sources": [
                    "env:MERLIN_LOCAL_EXECUTION_ALLOWED_COMMANDS | GOVERNANCE | command allowlist",
                ],
            },
        }
    resolved_exec = shutil.which(command_name)
    if not resolved_exec:
        return {
            "ok": False,
            "error": f"Executable not available on PATH: {command_name}",
            "governance": {"fail_closed": True, "reason": "executable_not_found"},
            "status": status,
            "contract": {
                "body": f"Local execution denied: `{command_name}` is not available on PATH.",
                "followups": [
                    "Install the required tool in the local environment.",
                    "Retry once the executable is available.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | executable availability check",
                ],
            },
        }
    argv = [resolved_exec, *argv[1:]]
    try:
        exec_cwd = _resolve_cwd(cwd)
    except Exception:
        return {
            "ok": False,
            "error": "cwd must resolve inside repository root",
            "governance": {"fail_closed": True, "reason": "cwd_outside_repo"},
            "status": status,
            "contract": {
                "body": "Local execution denied: cwd is outside repository scope.",
                "followups": [
                    "Set cwd to a path under the repository root.",
                    "Retry with repository-scoped execution.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | repository-boundary enforcement",
                ],
            },
        }

    max_timeout = _max_timeout_seconds()
    timeout = max_timeout if timeout_seconds is None else max(5, int(timeout_seconds))
    timeout = min(timeout, max_timeout)
    started_at = _utcnow()
    try:
        completed = subprocess.run(
            argv,
            cwd=str(exec_cwd),
            shell=False,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=_safe_subprocess_env(),
        )
        stdout = str(completed.stdout or "")
        stderr = str(completed.stderr or "")
        output_cap = 12_000
        summary = (
            f"Local execution {'passed' if completed.returncode == 0 else 'failed'} "
            f"(exit={completed.returncode}) for `{command_name}`."
        )
        return {
            "ok": completed.returncode == 0,
            "error": "" if completed.returncode == 0 else f"Command exited with code {completed.returncode}",
            "status": status,
            "execution": {
                "command": raw_command,
                "argv": argv,
                "cwd": str(exec_cwd),
                "returncode": completed.returncode,
                "timeout_seconds": timeout,
                "stdout": stdout[:output_cap],
                "stderr": stderr[:output_cap],
                "started_at": started_at,
                "finished_at": _utcnow(),
            },
            "governance": {
                "fail_closed": completed.returncode != 0,
                "reason": "command_failed" if completed.returncode != 0 else "command_passed",
                "external_token_fallback_recommended": completed.returncode != 0,
            },
            "contract": {
                "body": summary,
                "followups": [
                    "Use this local receipt before escalating to any external model lane.",
                    "If failed, fix locally first and rerun the same command.",
                ],
                "sources": [
                    "runtime:local_execution | HARDGATE | local-first deterministic execution receipt",
                    "policy:fail_closed | GOVERNANCE | external fallback is gated behind local result",
                ],
            },
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "error": f"Command timed out after {timeout} seconds",
            "status": status,
            "governance": {"fail_closed": True, "reason": "command_timeout"},
            "contract": {
                "body": f"Local execution failed closed: timeout after {timeout} seconds.",
                "followups": [
                    "Narrow command scope or increase timeout policy explicitly.",
                    "Retry with smaller validation slices.",
                ],
                "sources": [
                    "runtime:local_execution | GOVERNANCE | timeout fail-closed enforcement",
                ],
            },
            "execution": {
                "command": raw_command,
                "argv": argv,
                "cwd": str(exec_cwd),
                "timeout_seconds": timeout,
                "started_at": started_at,
                "finished_at": _utcnow(),
            },
        }
