# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
bot/session_bootstrap.py — Top-of-session identity and context loader.

Reads HILS_SESSION_CURRENT.md and HILS_SESSION_LOG.md from the repository
root and returns structured boot-block data so that every agent session
begins with a deterministic identity/context snapshot.

Usage (at the very start of a session)::

    from bot.session_bootstrap import load_boot_block, summarise_intent_history
    boot = load_boot_block()
    print(boot["active_wave"])
    print(boot["non_negotiables"])
    history = summarise_intent_history(max_entries=5)

This module has zero external dependencies beyond the standard library.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

__all__ = [
    "load_boot_block",
    "summarise_intent_history",
    "current_intent_snapshot",
    "append_session_entry",
    "CURRENT_DOC",
    "LOG_DOC",
]

# ---------------------------------------------------------------------------
# Canonical file paths (relative to repo root)
# ---------------------------------------------------------------------------
_REPO_ROOT = Path(__file__).parent.parent
CURRENT_DOC: Path = _REPO_ROOT / "HILS_SESSION_CURRENT.md"
LOG_DOC: Path = _REPO_ROOT / "HILS_SESSION_LOG.md"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_boot_block(current_doc: Optional[Path] = None) -> Dict:
    """Load the identity/context boot block from HILS_SESSION_CURRENT.md.

    Returns a dict with keys:
        session_opened, active_wave, prior_wave,
        non_negotiables (list[str]),
        strategic_intent (list[dict]),
        open_loops (list[str]),
        key_coordinates (dict[str, str]),
        raw_text (str),
        source (str)

    Falls back to safe defaults if the file does not exist.
    """
    path = current_doc or CURRENT_DOC
    if not path.exists():
        return _default_boot_block(str(path))

    raw = path.read_text(encoding="utf-8", errors="replace")
    return _parse_current_doc(raw, str(path))


def summarise_intent_history(
    log_doc: Optional[Path] = None,
    max_entries: int = 10,
) -> List[Dict]:
    """Return a list of parsed session log entries (most recent first).

    Parameters
    ----------
    log_doc : Path, optional
        Path to HILS_SESSION_LOG.md.  Defaults to repo-root canonical.
    max_entries : int
        Maximum number of entries to return.

    Returns
    -------
    list of dicts, each with keys:
        entry_number, timestamp, wave, intents (list[str]),
        decisions (list[str]), open_loops (list[str]),
        regression_result (str)
    """
    path = log_doc or LOG_DOC
    if not path.exists():
        return []
    raw = path.read_text(encoding="utf-8", errors="replace")
    entries = _parse_log_entries(raw)
    # Most recent first
    entries.sort(key=lambda e: _parse_timestamp(e.get("timestamp", "")), reverse=True)
    return entries[:max_entries]


def current_intent_snapshot(
    current_doc: Optional[Path] = None,
    log_doc: Optional[Path] = None,
    max_history: int = 3,
) -> Dict:
    """Return a deterministic summary of current intent plus recent history.

    Combines the canonical current-session boot block with the most recent
    session-log entries, then computes a de-duplicated unresolved-loop view:
    current open loops plus carried-forward loops, minus recently resolved loops.
    """
    boot = load_boot_block(current_doc=current_doc)
    history = summarise_intent_history(log_doc=log_doc, max_entries=max_history)

    resolved_recent = _dedupe_preserve_order(
        loop
        for entry in history
        for loop in entry.get("resolved_loops", [])
    )
    carried_recent = _dedupe_preserve_order(
        loop
        for entry in history
        for loop in entry.get("open_loops", [])
    )
    trigger_recent = _dedupe_preserve_order(
        trigger
        for entry in history
        for trigger in entry.get("next_triggers", [])
    )
    decision_recent = _dedupe_preserve_order(
        decision
        for entry in history
        for decision in entry.get("decisions", [])
    )

    unresolved = [
        loop for loop in _dedupe_preserve_order(
            list(boot.get("open_loops", [])) + carried_recent
        )
        if loop not in resolved_recent
    ]

    return {
        "active_wave": boot.get("active_wave", "UNKNOWN"),
        "strategic_intent": boot.get("strategic_intent", []),
        "open_loops": boot.get("open_loops", []),
        "unresolved_loops": unresolved,
        "resolved_recently": resolved_recent,
        "recent_decisions": decision_recent,
        "next_triggers": trigger_recent,
        "recent_history_count": len(history),
        "sources": [boot.get("source", str(current_doc or CURRENT_DOC)), str(log_doc or LOG_DOC)],
    }


def append_session_entry(
    *,
    wave: str,
    session_trigger: str,
    intents: List[str],
    decisions: List[str],
    loops_resolved: List[str],
    loops_forward: List[str],
    regression_result: str,
    next_triggers: List[str],
    log_doc: Optional[Path] = None,
    timestamp: Optional[str] = None,
) -> str:
    """Append a structured entry to HILS_SESSION_LOG.md.

    Parameters
    ----------
    wave : str
        Active wave identifier, e.g. "Wave A2".
    session_trigger : str
        One-sentence description of what caused this session.
    intents : list[str]
        Strategic intents this session.
    decisions : list[str]
        Numbered decisions made.
    loops_resolved : list[str]
        Open loops from the previous entry that were resolved.
    loops_forward : list[str]
        Open loops carried forward to the next entry.
    regression_result : str
        Human-readable regression gate outcome.
    next_triggers : list[str]
        Conditions that should open the next session.
    log_doc : Path, optional
        Path to HILS_SESSION_LOG.md.
    timestamp : str, optional
        ISO-8601 timestamp.  Defaults to UTC now.

    Returns
    -------
    str — the formatted entry text that was appended.
    """
    path = log_doc or LOG_DOC
    ts = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.parent.mkdir(parents=True, exist_ok=True)

    # Determine next entry number
    entry_number = 1
    if path.exists():
        raw = path.read_text(encoding="utf-8", errors="replace")
        existing = re.findall(r"## Entry (\d+)", raw)
        if existing:
            entry_number = max(int(n) for n in existing) + 1

    entry = _format_entry(
        entry_number=entry_number,
        ts=ts,
        wave=wave,
        session_trigger=session_trigger,
        intents=intents,
        decisions=decisions,
        loops_resolved=loops_resolved,
        loops_forward=loops_forward,
        regression_result=regression_result,
        next_triggers=next_triggers,
    )

    # Append before the template comment block
    if path.exists():
        existing_text = path.read_text(encoding="utf-8", errors="replace")
        # Insert before the closing template comment
        marker = "<!-- Add new entries above this line"
        if marker in existing_text:
            new_text = _insert_entry_before_marker(existing_text, entry, marker)
        else:
            new_text = existing_text.rstrip() + "\n\n---\n\n" + entry
        path.write_text(new_text, encoding="utf-8")
    else:
        path.write_text(entry, encoding="utf-8")

    return entry


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _default_boot_block(source: str) -> Dict:
    return {
        "session_opened": "UNKNOWN",
        "active_wave": "UNKNOWN",
        "prior_wave": "UNKNOWN",
        "non_negotiables": [
            "0 test failures",
            "Epistemic separation (SEPARATION.md)",
            "Pillar set CLOSED",
            "Authorship standard",
            "Human intent-control is non-negotiable",
            "Substack assets out of scope",
            "No secret/credential commits",
        ],
        "strategic_intent": [],
        "open_loops": [],
        "key_coordinates": {},
        "raw_text": "",
        "source": source,
        "warning": "HILS_SESSION_CURRENT.md not found; defaults applied.",
    }


def _parse_current_doc(raw: str, source: str) -> Dict:
    """Parse HILS_SESSION_CURRENT.md into structured data."""
    result: Dict = {
        "session_opened": _extract_table_value(raw, "Session opened"),
        "active_wave": _extract_table_value(raw, "Active wave"),
        "prior_wave": _extract_table_value(raw, "Prior wave"),
        "non_negotiables": _extract_list_section(raw, "Non-Negotiables"),
        "strategic_intent": _extract_intent_table(raw),
        "open_loops": _extract_list_section(raw, "Open Loops"),
        "key_coordinates": _extract_coordinates_table(raw),
        "raw_text": raw,
        "source": source,
    }
    return result


def _extract_table_value(text: str, field_name: str) -> str:
    """Extract a value from a markdown table row like | field_name | value |."""
    pattern = rf"\|\s*\*?\*?{re.escape(field_name)}\*?\*?\s*\|\s*(.+?)\s*\|"
    m = re.search(pattern, text, re.IGNORECASE)
    return m.group(1).strip() if m else "UNKNOWN"


def _extract_list_section(text: str, section_header: str) -> List[str]:
    """Extract numbered or bulleted list items under a markdown heading."""
    # Find the section
    pattern = rf"##\s+{re.escape(section_header)}.*?\n(.*?)(?=\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    block = m.group(1)
    items = re.findall(r"^\s*[-*\d.]+\s+(.+)$", block, re.MULTILINE)
    return [item.strip() for item in items if item.strip()]


def _extract_intent_table(text: str) -> List[Dict]:
    """Parse the Current Strategic Intent table."""
    pattern = r"##\s+Current Strategic Intent.*?\n(.*?)(?=\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not m:
        return []
    block = m.group(1)
    rows = re.findall(r"\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|", block)
    return [
        {"priority": int(r[0]), "intent": r[1].strip(), "status": r[2].strip()}
        for r in rows
    ]


def _extract_coordinates_table(text: str) -> Dict[str, str]:
    """Parse the Key Repository Coordinates table."""
    pattern = r"##\s+Key Repository Coordinates.*?\n(.*?)(?=\n##|\Z)"
    m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    if not m:
        return {}
    block = m.group(1)
    rows = re.findall(r"\|\s*(.+?)\s*\|\s*(.+?)\s*\|", block)
    coords = {}
    for label, value in rows:
        label = label.strip().strip("*")
        value = value.strip()
        if label and value and label.lower() not in ("resource", "---"):
            coords[label] = value
    return coords


def _parse_log_entries(raw: str) -> List[Dict]:
    """Parse all ## Entry blocks from HILS_SESSION_LOG.md."""
    # Split on entry headers
    entry_blocks = re.split(r"(?=## Entry \d{4})", raw)
    results = []
    for block in entry_blocks:
        m = re.match(r"## Entry (\d+)\s*[—–-]\s*(\S+)\s*\|?\s*(.*)", block)
        if not m:
            continue
        entry_num = int(m.group(1))
        ts = m.group(2)
        wave = m.group(3).strip()
        intents = re.findall(r"^-\s+(.+)$", _get_subsection(block, "Strategic intent"), re.MULTILINE)
        decisions = re.findall(r"^\d+\.\s+(.+)$", _get_subsection(block, "Decisions made"), re.MULTILINE)
        resolved = re.findall(r"^-\s+(.+)$", _get_subsection(block, "Open loops resolved"), re.MULTILINE)
        loops_fwd = re.findall(r"^-\s+(.+)$", _get_subsection(block, "Open loops carried forward"), re.MULTILINE)
        triggers = re.findall(r"^-\s+(.+)$", _get_subsection(block, "Next-entry trigger conditions"), re.MULTILINE)
        reg = _get_subsection(block, "Regression gate").strip()
        trigger_lines = re.findall(r"^-\s+Session trigger:\s*(.+)$", _get_subsection(block, "Identity"), re.MULTILINE)
        results.append({
            "entry_number": entry_num,
            "timestamp": ts,
            "wave": wave,
            "intents": [i.strip() for i in intents],
            "decisions": [d.strip() for d in decisions],
            "resolved_loops": [l.strip() for l in resolved],
            "open_loops": [l.strip() for l in loops_fwd],
            "next_triggers": [t.strip() for t in triggers],
            "regression_result": reg,
            "session_trigger": trigger_lines[0].strip() if trigger_lines else "",
        })
    return results


def _get_subsection(block: str, heading: str) -> str:
    """Extract text under a ### heading within an entry block."""
    pattern = rf"###\s+{re.escape(heading)}.*?\n(.*?)(?=\n###|\Z)"
    m = re.search(pattern, block, re.DOTALL | re.IGNORECASE)
    return m.group(1) if m else ""


def _format_entry(
    *,
    entry_number: int,
    ts: str,
    wave: str,
    session_trigger: str,
    intents: List[str],
    decisions: List[str],
    loops_resolved: List[str],
    loops_forward: List[str],
    regression_result: str,
    next_triggers: List[str],
) -> str:
    num_str = str(entry_number).zfill(4)
    intent_lines = "\n".join(f"- {i}" for i in intents) if intents else "- (none)"
    decision_lines = "\n".join(f"{i + 1}. {d}" for i, d in enumerate(decisions)) if decisions else "1. (none)"
    resolved_lines = "\n".join(f"- {l}" for l in loops_resolved) if loops_resolved else "- (none)"
    forward_lines = "\n".join(f"- {l}" for l in loops_forward) if loops_forward else "- (none)"
    trigger_lines = "\n".join(f"- {t}" for t in next_triggers) if next_triggers else "- (none)"

    return f"""\
## Entry {num_str} — {ts} | {wave}

### Identity
- Agent: GitHub Copilot (AI)
- Human: ThomasCory Walker-Pearson
- Session trigger: {session_trigger}

### Strategic intent this session
{intent_lines}

### Decisions made
{decision_lines}

### Open loops resolved
{resolved_lines}

### Open loops carried forward
{forward_lines}

### Regression gate at session close
- Full suite: `python3 -m pytest tests/ recycling/ "5-GOVERNANCE/Unitary Pentad/" -q`
- Result: {regression_result}

### Next-entry trigger conditions
{trigger_lines}
"""


def _parse_timestamp(raw: str) -> datetime:
    """Parse an ISO timestamp; invalid values sort to the epoch."""
    try:
        normalised = raw.replace("Z", "+00:00")
        return datetime.fromisoformat(normalised)
    except ValueError:
        return datetime.fromtimestamp(0, tz=timezone.utc)


def _dedupe_preserve_order(items) -> List[str]:
    """Return non-empty strings in original order without duplicates."""
    seen = set()
    result: List[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _insert_entry_before_marker(existing_text: str, entry: str, marker: str) -> str:
    """Insert a formatted entry immediately before the canonical marker comment."""
    prefix, suffix = existing_text.split(marker, 1)
    prefix = prefix.rstrip()
    joiner = "\n\n---\n\n" if prefix else ""
    return f"{prefix}{joiner}{entry}\n\n{marker}{suffix}"
