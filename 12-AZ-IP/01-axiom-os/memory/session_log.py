# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero memory/session_log.py — Machine-readable audit trail

Extends bot/session_bootstrap.py with AxiomZero-specific structured logging.
Every agent action that crosses a threshold writes a machine-readable entry:
  - Pillar modified
  - Test suite result
  - Paper found that threatens/confirms predictions
  - HILS decision made

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

LOG_FILE = Path.home() / ".axiomzero" / "agent_audit.jsonl"
MAX_LOG_SIZE_BYTES: int = 50 * 1024 * 1024  # 50 MB


def _rotate_log_if_needed(log_path: Path) -> None:
    """Rotate the log file if it exceeds MAX_LOG_SIZE_BYTES, compressing the old file."""
    import gzip
    import shutil

    if not log_path.exists() or log_path.stat().st_size < MAX_LOG_SIZE_BYTES:
        return

    # Find a non-colliding archive name
    import datetime
    ts = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    archive = log_path.with_suffix(f".{ts}.jsonl.gz")
    with open(log_path, "rb") as f_in, gzip.open(archive, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)
    log_path.unlink()
    logger.info("Rotated audit log → %s", archive)


def log_event(
    event_type: str,
    manager: str,
    task_id: str,
    data: Dict,
    human_notified: bool = False,
) -> None:
    """
    Write a single audit event to the JSONL log.
    Rotates the log file at 50 MB, compressing the old file with gzip.

    event_type: one of 'pillar_modified', 'test_result', 'paper_found',
                'hils_decision', 'agent_error', 'task_complete'
    """
    entry = {
        "ts": time.time(),
        "event_type": event_type,
        "manager": manager,
        "task_id": task_id,
        "human_notified": human_notified,
        **data,
    }
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    _rotate_log_if_needed(LOG_FILE)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")


def log_test_result(
    task_id: str,
    passed: bool,
    summary: str,
    test_paths: List[str],
    elapsed_s: float = 0.0,
) -> None:
    log_event(
        "test_result", "M4_Test", task_id,
        {"passed": passed, "summary": summary,
         "test_paths": test_paths, "elapsed_s": elapsed_s},
        human_notified=not passed,
    )


def log_hils_decision(
    task_id: str,
    decision: str,
    human: str,
    note: str = "",
) -> None:
    log_event(
        "hils_decision", "M7_Executive", task_id,
        {"decision": decision, "human": human, "note": note},
        human_notified=True,
    )


def log_paper_found(
    task_id: str,
    paper_title: str,
    paper_id: str,
    relevance: str,
    threatens_prediction: bool = False,
) -> None:
    log_event(
        "paper_found", "M6_Web", task_id,
        {"paper_title": paper_title, "paper_id": paper_id,
         "relevance": relevance, "threatens_prediction": threatens_prediction},
        human_notified=threatens_prediction,
    )


def get_recent_events(n: int = 50, event_type: Optional[str] = None) -> List[Dict]:
    """Read the most recent N audit events from the JSONL log."""
    if not LOG_FILE.exists():
        return []
    entries = []
    with open(LOG_FILE) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                if event_type is None or entry.get("event_type") == event_type:
                    entries.append(entry)
            except json.JSONDecodeError:
                pass
    return entries[-n:]


def get_human_notifications() -> List[Dict]:
    """Return all events that required human notification."""
    if not LOG_FILE.exists():
        return []
    notifs = []
    with open(LOG_FILE) as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("human_notified"):
                    notifs.append(entry)
            except json.JSONDecodeError:
                pass
    return notifs[-20:]
