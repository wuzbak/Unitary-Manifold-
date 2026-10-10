# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""ox_navigator/engine/merlin_hosting_retention_guard.py — External-Hosting
Retention Detector and Tokenpot Canary (ADJACENT TRACK / GOVERNANCE).

See ``PSICAT_EXTERNAL_HOSTING_PROTOCOL.md`` for the full governance
document. This module provides two separate, bounded capabilities:

1. ``evaluate_retention_posture`` — compares declared hosting-provider
   clauses (loaded from
   ``12-AZ-IP/08-axiom-journalist/output/base44_terms_intake_investigation.json``,
   an existing Tier-3/investigator-supplied source; nothing here re-scrapes
   or re-verifies that source) against caller-supplied observed-signal
   records, producing a triage-shaped finding list
   (``psicat-external-intake``-style: evidence tier, triage status
   ``pending``/``accepted``/``rejected``/``incomplete``, never a silent
   verdict).
2. ``embed_tokenpot_marker`` / ``scan_for_tokenpot_reappearance`` — a
   canary/honeypot mechanism: a deterministic, per-session HMAC marker is
   embedded in an exported session; its later reappearance in text the
   caller supplies for comparison is affirmative evidence of retention
   beyond the original session. This module does not, and cannot, scan any
   third-party host's live infrastructure — "observed" text must always be
   supplied by the caller.

Honest scope limit (see the governance doc for the full statement): this
is a detection and evidence-generation tool, not a prevention mechanism.
It cannot stop a host's own servers from retaining data its own terms
already permit. Everything here is default-off, offline, deterministic
Python — no network calls.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Sequence

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PRODUCT_ROOT.parents[1]

DECLARED_TERMS_PATH = (
    REPO_ROOT
    / "12-AZ-IP"
    / "08-axiom-journalist"
    / "output"
    / "base44_terms_intake_investigation.json"
)

GOVERNANCE_LABEL = "GOVERNANCE"
STATUS_LABEL = "ADJACENT_TRACK"

# Flag naming matches the existing Navigator convention
# (MERLIN_<FEATURE>) — OFF by default, same as every other opt-in flag in
# this lane. This module's functions are pure and safe to call directly
# regardless of the flag; the flag only gates whether a future caller (e.g.
# a server route) surfaces this guard by default.
HOSTING_RETENTION_GUARD_FLAG = "MERLIN_HOSTING_RETENTION_GUARD"


def hosting_retention_guard_enabled() -> bool:
    """Return True only if the Navigator-side opt-in flag is explicitly set."""
    return os.environ.get(HOSTING_RETENTION_GUARD_FLAG, "").strip().lower() in {"1", "true", "yes", "on"}


# ---------------------------------------------------------------------------
# Declared-terms loading (Part 1: declared vs. observed)
# ---------------------------------------------------------------------------


def load_declared_terms(path: Path | None = None) -> dict[str, Any]:
    """Load the existing investigator-supplied base44/Wix terms excerpts.

    Returns ``{"ok": False, ...}`` if the intake file is unavailable in this
    checkout, so callers can skip gracefully rather than fail.
    """
    terms_path = path or DECLARED_TERMS_PATH
    try:
        raw = terms_path.read_text(encoding="utf-8")
    except OSError as exc:
        return {"ok": False, "status": STATUS_LABEL, "error": f"declared terms unavailable: {exc}"}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return {"ok": False, "status": STATUS_LABEL, "error": f"declared terms malformed: {exc}"}
    return {"ok": True, "status": STATUS_LABEL, "path": str(terms_path), "document": data}


def declared_clauses(path: Path | None = None) -> list[dict[str, Any]]:
    """Flatten the declared-terms document's ``sources`` into comparison clauses.

    Each clause keeps the source document's own evidence tier
    (``base44_terms_intake_investigation.json``'s ``tier`` field) rather than
    asserting a new one.
    """
    loaded = load_declared_terms(path)
    if not loaded.get("ok"):
        return []
    sources = list(loaded["document"].get("sources") or [])
    clauses: list[dict[str, Any]] = []
    for index, source in enumerate(sources):
        clauses.append({
            "clause_id": f"declared::{index}",
            "title": str(source.get("title", "")),
            "tier": str(source.get("tier", "")),
            "excerpt": str(source.get("excerpt", "")),
            "source_type": str(source.get("source_type", "")),
        })
    return clauses


def evaluate_retention_posture(
    observed_signals: Sequence[dict[str, Any]] | None = None,
    *,
    path: Path | None = None,
) -> dict[str, Any]:
    """Compare declared clauses against caller-supplied observed signals.

    ``observed_signals`` is a sequence of dicts, each
    ``{"clause_id": ..., "category": "consistent"|"contradicts", "description": ..., "tier": ...}``.
    A declared clause with no matching observed signal is reported
    ``unverified`` (no evidence either way) rather than assumed safe or
    assumed violated — this module makes no inference beyond the evidence
    it is given.
    """
    clauses = declared_clauses(path)
    if not clauses:
        return {"ok": False, "status": STATUS_LABEL, "error": "no declared clauses available"}

    by_clause: dict[str, list[dict[str, Any]]] = {}
    for signal in list(observed_signals or []):
        clause_id = str(signal.get("clause_id", ""))
        by_clause.setdefault(clause_id, []).append(signal)

    findings = []
    for clause in clauses:
        signals = by_clause.get(clause["clause_id"], [])
        contradicting = [s for s in signals if str(s.get("category", "")).strip().lower() == "contradicts"]
        if contradicting:
            triage_status = "pending"
            posture = "flagged"
        elif signals:
            triage_status = "accepted"
            posture = "consistent"
        else:
            triage_status = "incomplete"
            posture = "unverified"
        findings.append({
            "clause_id": clause["clause_id"],
            "clause_title": clause["title"],
            "declared_tier": clause["tier"],
            "posture": posture,
            "triage_status": triage_status,
            "observed_signal_count": len(signals),
            "observed_signals": signals,
        })

    counts = {"flagged": 0, "consistent": 0, "unverified": 0}
    for finding in findings:
        counts[finding["posture"]] += 1

    return {
        "ok": True,
        "status": STATUS_LABEL,
        "governance_label": GOVERNANCE_LABEL,
        "declared_clause_count": len(clauses),
        "findings": findings,
        "counts": counts,
        "caveat": (
            "Declared-clause evidence is Tier 3 / investigator-supplied per the source "
            "document's own 'lead' field, not independently re-verified here. A 'flagged' "
            "posture requires caller-supplied observed-signal evidence contradicting the "
            "declared clause; it is not itself proof of misuse, and nothing here performs "
            "live scanning of any third-party host."
        ),
    }


# ---------------------------------------------------------------------------
# Tokenpot canary (Part 2: embed + detect reappearance)
# ---------------------------------------------------------------------------

_TOKENPOT_PREFIX = "um-tokenpot"
_TOKENPOT_RE = re.compile(r"um-tokenpot-[0-9a-f]{32}")


def _tokenpot_secret() -> bytes:
    """Return the HMAC key for marker derivation.

    Uses an environment-supplied secret if present (``UM_TOKENPOT_SECRET``)
    so deployments can rotate it; falls back to a fixed, publicly-known
    constant otherwise. The fallback is intentionally NOT cryptographically
    secret -- this is a detection/evidence canary, not an access-control
    mechanism, and the governance doc states explicitly that this cannot
    prevent retention, only provide evidence of it after the fact.
    """
    return os.environ.get("UM_TOKENPOT_SECRET", "psicat-tokenpot-default").encode("utf-8")


def embed_tokenpot_marker(session_text: str, session_id: str, *, timestamp: float | None = None) -> tuple[str, str]:
    """Return ``(session_text_with_marker, marker)``.

    The marker is a deterministic HMAC-SHA256 digest of ``session_id`` and a
    timestamp, truncated to 32 hex characters and wrapped in a recognisable,
    human-readable, inert prefix. It is appended as a trailing line, not
    hidden -- a tokenpot is disclosed canary evidence, not a covert beacon.
    """
    ts = timestamp if timestamp is not None else time.time()
    payload = f"{session_id}:{ts:.6f}".encode("utf-8")
    digest = hmac.new(_tokenpot_secret(), payload, hashlib.sha256).hexdigest()[:32]
    marker = f"{_TOKENPOT_PREFIX}-{digest}"
    marked_text = f"{session_text}\n\n<!-- {marker} -->"
    return marked_text, marker


def scan_for_tokenpot_reappearance(observed_text: str, known_markers: Sequence[str]) -> list[str]:
    """Return every known marker that reappears verbatim in ``observed_text``.

    ``observed_text`` must be supplied by the caller (e.g. a human who found
    suspicious text elsewhere); this function performs no network access and
    does not search any third-party host on its own.
    """
    found_in_text = set(_TOKENPOT_RE.findall(observed_text))
    return [marker for marker in known_markers if marker in found_in_text]


# ---------------------------------------------------------------------------
# Benchmark: detection accuracy on a small synthetic scenario set
# ---------------------------------------------------------------------------

# Each scenario: (session_id, description, observed_text_builder, expected_detect).
# observed_text_builder(marked_text) -> observed_text; expected_detect states
# whether scan_for_tokenpot_reappearance should find THIS session's marker.
_DETECTION_SCENARIOS: tuple[tuple[str, str, Any, bool], ...] = (
    (
        "session-001",
        "Export text pasted back verbatim, including its footer.",
        lambda marked_text: marked_text,
        True,
    ),
    (
        "session-002",
        "Paraphrase of the export with the canary line stripped before leaking.",
        lambda marked_text: marked_text.split("<!--")[0],
        False,
    ),
    (
        "session-003",
        "Canary footer embedded inside a larger leaked document.",
        lambda marked_text: f"some preamble...\n{marked_text}\n...some trailer",
        True,
    ),
    (
        "session-004",
        "Unrelated text that never saw this session's export.",
        lambda marked_text: "this text has nothing to do with any export",
        False,
    ),
    (
        "session-005",
        "Canary footer lightly re-formatted but the marker substring intact.",
        lambda marked_text: marked_text.replace("<!--", "[canary:").replace("-->", "]"),
        True,
    ),
    (
        "session-006",
        "A different session's tokenpot marker appears, not this session's own.",
        lambda marked_text: embed_tokenpot_marker("unrelated session body", "session-999")[0],
        False,
    ),
)


def evaluate_detection_accuracy() -> dict[str, Any]:
    """Measure tokenpot-reappearance precision/recall on synthetic scenarios.

    Synthetic, not real-world: these scenarios simulate what a human-supplied
    'observed text' comparison would look like, since this module cannot
    perform live scanning of any third-party host. Reported honestly as an
    indicative, small-sample benchmark -- see ``PSICAT_EXTERNAL_HOSTING_PROTOCOL.md``.
    """
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0
    rows = []

    for session_id, description, build_observed_text, should_detect in _DETECTION_SCENARIOS:
        marked_text, marker = embed_tokenpot_marker(f"session body for {session_id}", session_id)
        observed_text = build_observed_text(marked_text)
        detected = bool(scan_for_tokenpot_reappearance(observed_text, [marker]))
        if should_detect and detected:
            true_positives += 1
        elif should_detect and not detected:
            false_negatives += 1
        elif not should_detect and detected:
            false_positives += 1
        else:
            true_negatives += 1
        rows.append({
            "session_id": session_id,
            "description": description,
            "expected_detect": should_detect,
            "detected": detected,
        })

    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) else 0.0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) else 0.0
    return {
        "ok": True,
        "status": STATUS_LABEL,
        "governance_label": GOVERNANCE_LABEL,
        "scenario_count": len(_DETECTION_SCENARIOS),
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "true_negatives": true_negatives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "rows": rows,
        "caveat": (
            "Synthetic, hand-authored scenarios (6 cases), not real-world hosting-provider "
            "behavior. Measures only the string-matching detector's own robustness to "
            "paraphrase/stripping/re-formatting of a known marker, not any claim about "
            "actual base44 or hosting-provider conduct."
        ),
    }


__all__ = [
    "DECLARED_TERMS_PATH",
    "GOVERNANCE_LABEL",
    "HOSTING_RETENTION_GUARD_FLAG",
    "STATUS_LABEL",
    "declared_clauses",
    "embed_tokenpot_marker",
    "evaluate_detection_accuracy",
    "evaluate_retention_posture",
    "hosting_retention_guard_enabled",
    "load_declared_terms",
    "scan_for_tokenpot_reappearance",
]
