#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
TOOLS/ox_regression_watchdog.py — OX Alpha PR Regression Watchdog

Semantic regression analysis for pull requests using OX Alpha's extended memory.
Feeds OX: the PR diff + the full ox_full_context.md pack + the pytest failure list,
and returns a structured JSON report identifying cross-pillar impact, risk level,
and recommended additional tests.

Usage (standalone):
  export OPENROUTER_API_KEY=...
  python TOOLS/ox_regression_watchdog.py \\
      --diff path/to/diff.patch \\
      --failures path/to/failures.txt \\
      --out ox_watchdog_report.json

Usage (GitHub Actions — reads GITHUB_ env vars):
  python TOOLS/ox_regression_watchdog.py --ci

Output JSON schema:
  {
    "affected_pillars": [<int>, ...],
    "risk_level": "low" | "medium" | "high",
    "recommended_tests": ["tests/test_foo.py", ...],
    "summary": "<plain text>",
    "governance_note": "...",
    "model": "stealth/ox-alpha",
    "timestamp": "ISO-8601"
  }

GOVERNANCE: All outputs are AI-generated suggestions. No pillar status or test
gating changes are binding without steward (wuzbak) approval.

Theory & scientific direction: ThomasCory Walker-Pearson.
Code, engineering: GitHub Copilot (AI).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import httpx
    HTTPX_OK = True
except ImportError:
    HTTPX_OK = False

REPO_ROOT = Path(__file__).parent.parent
OX_CONTEXT_PACK = REPO_ROOT / "9-INFRASTRUCTURE" / "ox_full_context.md"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OX_MODEL_ID = "stealth/ox-alpha"
OX_MAX_TOKENS = 2048

GOVERNANCE_NOTE = (
    "OX Regression Watchdog output is AI-generated. Affected pillar identification, "
    "risk level, and test recommendations are suggestions only. No hardgate claim, "
    "pillar status, or test gating change is binding without steward approval "
    "(HILS framework — SEPARATION.md)."
)

WATCHDOG_SYSTEM_PROMPT = """You are the AxiomZero Regression Watchdog, an AI assistant integrated
into the Unitary Manifold CI pipeline. Your job is to analyse a pull request diff and
a list of test failures (if any), then identify which physics pillars are affected and
what additional tests should be run.

You have access to the full repository context in your system prompt.

RULES:
1. Return ONLY valid JSON — no prose before or after the JSON object.
2. Never invent pillar numbers not mentioned in the context.
3. Use gate labels correctly: HARDGATE, ADJACENT_TRACK, OPEN_GAP.
4. risk_level must be exactly "low", "medium", or "high".
5. recommended_tests must be relative paths (e.g. "tests/test_metric.py").
6. summary must be plain text, max 300 chars.
7. Never claim to prove or disprove a hardgate claim.

Return exactly this JSON schema:
{
  "affected_pillars": [<integer>, ...],
  "risk_level": "low" | "medium" | "high",
  "recommended_tests": ["<path>", ...],
  "summary": "<string max 300 chars>"
}"""


def load_context() -> str:
    """Load ox_full_context.md, fall back to a minimal inline stub."""
    if OX_CONTEXT_PACK.exists():
        return OX_CONTEXT_PACK.read_text(encoding="utf-8", errors="replace")
    return (
        "Full context pack not found. Run 9-INFRASTRUCTURE/ox_context_pack.py first. "
        "Core pillars: 1=5D metric, 2=EFE, 3=orbifold, 4=holography, 5=FTUM. "
        "Key files: src/core/, src/holography/, tests/."
    )


def build_query(diff_text: str, failures_text: str) -> str:
    """Compose the user query for OX."""
    failures_section = (
        f"\n\n## Test failures\n```\n{failures_text.strip()[:3000]}\n```"
        if failures_text.strip()
        else "\n\n## Test failures\nNone reported."
    )
    diff_section = f"\n\n## PR diff (first 6000 chars)\n```diff\n{diff_text.strip()[:6000]}\n```"

    return (
        "Analyse this pull request for cross-pillar regression risk.\n"
        + diff_section
        + failures_section
        + "\n\nRespond with the JSON schema specified in your system prompt."
    )


def call_ox_sync(query: str, context: str) -> dict:
    """Synchronous OX call (for CI scripts)."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return _error_result("OPENROUTER_API_KEY not set — OX watchdog disabled.")

    if not HTTPX_OK:
        return _error_result("httpx not installed — run: pip install httpx")

    sys_content = WATCHDOG_SYSTEM_PROMPT + "\n\n--- REPOSITORY CONTEXT ---\n" + context

    payload = {
        "model": OX_MODEL_ID,
        "messages": [
            {"role": "system", "content": sys_content},
            {"role": "user",   "content": query},
        ],
        "max_tokens": OX_MAX_TOKENS,
        "temperature": 0.1,  # near-deterministic for CI
    }

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"******",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://axiomzerospc.org",
                    "X-Title": "AxiomZero Regression Watchdog",
                },
                json=payload,
            )
            if resp.status_code != 200:
                return _error_result(f"OX HTTP {resp.status_code}: {resp.text[:300]}")

            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return _error_result("OX returned no choices.")

            raw = choices[0].get("message", {}).get("content", "").strip()
            return _parse_ox_json(raw)

    except Exception as exc:
        return _error_result(f"OX call failed: {exc}")


def _parse_ox_json(raw: str) -> dict:
    """Extract and validate JSON from OX response."""
    # Strip markdown code fences if present
    raw = re.sub(r"^```(?:json)?\s*", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\s*```$", "", raw, flags=re.MULTILINE).strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        return _error_result(f"OX returned invalid JSON: {exc}. Raw: {raw[:300]}")

    # Validate and coerce schema
    pillars = [int(p) for p in data.get("affected_pillars", []) if str(p).isdigit()]
    risk = data.get("risk_level", "low")
    if risk not in ("low", "medium", "high"):
        risk = "low"
    tests = [str(t) for t in data.get("recommended_tests", []) if isinstance(t, str)]
    summary = str(data.get("summary", ""))[:300]

    return {
        "affected_pillars": pillars,
        "risk_level": risk,
        "recommended_tests": tests,
        "summary": summary,
        "governance_note": GOVERNANCE_NOTE,
        "model": OX_MODEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _error_result(msg: str) -> dict:
    return {
        "affected_pillars": [],
        "risk_level": "low",
        "recommended_tests": [],
        "summary": f"Watchdog error: {msg}",
        "governance_note": GOVERNANCE_NOTE,
        "model": OX_MODEL_ID,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "error": msg,
    }


def _ci_mode() -> None:
    """GitHub Actions CI mode — reads env vars, posts comment via gh CLI."""
    diff_text = os.environ.get("OX_PR_DIFF", "")
    failures_text = os.environ.get("OX_TEST_FAILURES", "")

    if not diff_text:
        # Try reading from a file dropped by a prior CI step
        diff_file = Path(os.environ.get("OX_DIFF_FILE", ""))
        if diff_file.exists():
            diff_text = diff_file.read_text(encoding="utf-8", errors="replace")

    context = load_context()
    query = build_query(diff_text, failures_text)
    result = call_ox_sync(query, context)

    out_path = Path(os.environ.get("OX_REPORT_FILE", "ox_watchdog_report.json"))
    out_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"OX Watchdog report → {out_path}", file=sys.stderr)
    print(json.dumps(result, indent=2))


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="OX Alpha PR Regression Watchdog")
    parser.add_argument("--diff",     type=str, default="", help="Path to diff.patch file")
    parser.add_argument("--failures", type=str, default="", help="Path to test failures text file")
    parser.add_argument("--out",      type=str, default="ox_watchdog_report.json", help="Output JSON path")
    parser.add_argument("--ci",       action="store_true", help="GitHub Actions CI mode")
    args = parser.parse_args(argv)

    if args.ci:
        _ci_mode()
        return

    diff_text = Path(args.diff).read_text(encoding="utf-8") if args.diff and Path(args.diff).exists() else ""
    failures_text = Path(args.failures).read_text(encoding="utf-8") if args.failures and Path(args.failures).exists() else ""

    context = load_context()
    query = build_query(diff_text, failures_text)
    result = call_ox_sync(query, context)

    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"✅ OX Watchdog report → {out}")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
