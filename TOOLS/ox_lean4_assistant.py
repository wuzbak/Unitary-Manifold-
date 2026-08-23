#!/usr/bin/env python3
# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
TOOLS/ox_lean4_assistant.py — OX Alpha Lean4 Theorem Draft Generator

Given a new pillar's Python module, OX Alpha drafts the corresponding Lean4
theorem stubs. The steward (human) reviews and hardens them before acceptance.

This keeps the HILS governance intact: OX suggests, steward decides.

Usage:
  export OPENROUTER_API_KEY=...
  python TOOLS/ox_lean4_assistant.py src/core/pillar795_example.py
  python TOOLS/ox_lean4_assistant.py src/core/pillar795_example.py --out lean4/UnitaryManifold/Pillar795Example.lean

Output: a .lean file with theorem stubs annotated with
  -- OX-GENERATED STUB: requires steward review and hardening before acceptance

GOVERNANCE: OX outputs are AI suggestions. No Lean4 theorem is accepted into the
formal proof chain without steward (wuzbak) review and approval.

Theory & scientific direction: ThomasCory Walker-Pearson.
Code, engineering: GitHub Copilot (AI).
"""

from __future__ import annotations

import argparse
import ast
import os
import sys
import textwrap
from pathlib import Path
from datetime import datetime, timezone

try:
    import httpx
    HTTPX_OK = True
except ImportError:
    HTTPX_OK = False

REPO_ROOT = Path(__file__).parent.parent
LEAN4_DIR = REPO_ROOT / "lean4" / "UnitaryManifold"

# Sprint AT: minimum theorem count below which proxy stubs are acceptable.
# Above this threshold, OX should attempt genuine proofs, not new sorry stubs.
LEAN4_THEOREM_COUNT_SORRY_GATE: int = 1246  # set at Sprint AT end total
OX_CONTEXT_PACK = REPO_ROOT / "9-INFRASTRUCTURE" / "ox_full_context.md"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
OX_MODEL_ID = "stealth/ox-alpha"
OX_MAX_TOKENS = 4096

# ── Load example Lean4 files for few-shot context ─────────────────────────────
def _load_lean4_examples(n: int = 2) -> str:
    """Load first n .lean files as few-shot examples."""
    if not LEAN4_DIR.exists():
        return ""
    examples = []
    for lean_file in sorted(LEAN4_DIR.glob("*.lean"))[:n]:
        text = lean_file.read_text(encoding="utf-8", errors="replace")
        examples.append(f"-- Example: {lean_file.name}\n" + text[:3000])
    return "\n\n".join(examples)


LEAN4_SYSTEM_PROMPT = """\
You are a Lean4 formal proof assistant for the Unitary Manifold physics framework.
You draft Lean4 theorem stubs for new physics pillars.

RULES:
1. Every theorem stub must end with `sorry` (placeholder proof).
2. Add the comment `-- OX-GENERATED STUB: requires steward review and hardening` above each theorem.
3. Use the module header format shown in the examples.
4. Import UnitaryManifold.Basic at the top.
5. Use descriptive camelCase theorem names that match the pillar content.
6. Do NOT claim the stubs are proved — they are drafts for steward review.
7. Output valid Lean4 syntax only. No prose outside Lean4 comments.
8. Add a module-level comment: `-- GOVERNANCE: OX-generated stubs. Steward review required.`

Few-shot Lean4 examples follow in the context.
"""

GOVERNANCE_HEADER = """\
-- SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
-- Copyright (C) 2026  ThomasCory Walker-Pearson
--
-- GOVERNANCE: OX Alpha generated these theorem stubs.
-- They require steward (wuzbak) review and hardening before acceptance
-- into the formal proof chain (HILS framework — SEPARATION.md).
-- Generated: {timestamp}
-- Model: {model}
"""


def lean4_theorem_count_gate() -> dict:
    """
    Query the current Lean4 theorem count and assess whether new sorry stubs
    are acceptable.

    Policy (Sprint AT):
      - If current count < LEAN4_THEOREM_COUNT_SORRY_GATE: proxy stubs OK.
      - If current count >= LEAN4_THEOREM_COUNT_SORRY_GATE: OX must attempt
        genuine proofs (native_decide / norm_num / linarith) rather than new
        sorry stubs. Sorry stubs are still permitted for OPEN gaps explicitly
        documented as architecture limits.

    Returns a dict with the current count, gate threshold, and policy verdict.
    """
    if not LEAN4_DIR.exists():
        return {
            'lean4_dir_exists': False,
            'theorem_count': 0,
            'gate_threshold': LEAN4_THEOREM_COUNT_SORRY_GATE,
            'sorry_stubs_acceptable': True,
            'policy': 'LEAN4_DIR_NOT_FOUND — proxy stubs allowed',
        }

    theorem_count = 0
    for lean_file in LEAN4_DIR.glob("*.lean"):
        text = lean_file.read_text(encoding="utf-8", errors="replace")
        theorem_count += text.count("\ntheorem ")
        theorem_count += text.count("\nlemma ")

    sorry_count = 0
    for lean_file in LEAN4_DIR.glob("*.lean"):
        text = lean_file.read_text(encoding="utf-8", errors="replace")
        sorry_count += text.count(" sorry")

    sorry_acceptable = theorem_count < LEAN4_THEOREM_COUNT_SORRY_GATE

    return {
        'lean4_dir_exists': True,
        'lean4_dir': str(LEAN4_DIR),
        'theorem_count': theorem_count,
        'sorry_count': sorry_count,
        'gate_threshold': LEAN4_THEOREM_COUNT_SORRY_GATE,
        'sorry_stubs_acceptable': sorry_acceptable,
        'policy': (
            'PROXY_STUBS_OK — below gate threshold' if sorry_acceptable
            else 'GENUINE_PROOFS_PREFERRED — at or above gate threshold; '
                 'use native_decide/norm_num/linarith; sorry only for architecture limits'
        ),
        'recommendation': (
            'OX Alpha should generate sorry-free proofs for arithmetic claims. '
            'Reserve sorry for gaps explicitly labelled ARCHITECTURE_LIMIT or '
            'APS_MATHLIB_FORMALIZATION_OPEN.'
        ),
    }


def extract_python_summary(path: Path) -> str:
    """Extract module docstring + top-level function/class names from a Python file."""
    source = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(source)
        doc = ast.get_docstring(tree) or ""
        names = [
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        ]
        # Also extract constants (module-level assignments)
        constants = [
            f"{node.targets[0].id if hasattr(node.targets[0], 'id') else '?'}"
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign) and node.targets
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id.isupper()
        ]
    except SyntaxError:
        doc = ""
        names = []
        constants = []

    lines = [f"File: {path.name}"]
    if doc:
        lines.append("Docstring:\n" + doc[:1200])
    if names:
        lines.append("Functions/classes: " + ", ".join(names[:40]))
    if constants:
        lines.append("Key constants: " + ", ".join(constants[:20]))
    # Also include first 2000 chars of raw source
    lines.append("\nSource excerpt:\n" + source[:2000])
    return "\n".join(lines)


def call_ox_lean4(module_summary: str, examples: str) -> str:
    """Call OX Alpha to draft Lean4 stubs."""
    api_key = os.environ.get("OPENROUTER_API_KEY", "")
    if not api_key:
        return "-- ERROR: OPENROUTER_API_KEY not set. Cannot generate Lean4 stubs.\n"
    if not HTTPX_OK:
        return "-- ERROR: httpx not installed. Run: pip install httpx\n"

    # Load repository context (first 20k chars to stay within budget alongside few-shot)
    repo_ctx = ""
    if OX_CONTEXT_PACK.exists():
        repo_ctx = OX_CONTEXT_PACK.read_text(encoding="utf-8", errors="replace")[:20_000]

    sys_content = (
        LEAN4_SYSTEM_PROMPT
        + "\n\n--- REPOSITORY CONTEXT (excerpt) ---\n" + repo_ctx
        + "\n\n--- LEAN4 EXAMPLES ---\n" + examples
    )

    user_content = (
        "Draft Lean4 theorem stubs for this new pillar module:\n\n"
        + module_summary
        + "\n\nOutput valid Lean4 only."
    )

    payload = {
        "model": OX_MODEL_ID,
        "messages": [
            {"role": "system", "content": sys_content},
            {"role": "user",   "content": user_content},
        ],
        "max_tokens": OX_MAX_TOKENS,
        "temperature": 0.15,
    }

    try:
        with httpx.Client(timeout=120) as client:
            resp = client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"******",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://axiomzerosp.org",
                    "X-Title": "AxiomZero Lean4 Assistant",
                },
                json=payload,
            )
            if resp.status_code != 200:
                return f"-- ERROR: OX HTTP {resp.status_code}: {resp.text[:300]}\n"
            data = resp.json()
            choices = data.get("choices", [])
            if not choices:
                return "-- ERROR: OX returned no choices.\n"
            return choices[0].get("message", {}).get("content", "").strip()
    except Exception as exc:
        return f"-- ERROR: OX call failed: {exc}\n"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="OX Alpha Lean4 theorem stub generator.")
    parser.add_argument("module", type=str, help="Path to Python pillar module")
    parser.add_argument("--out",  type=str, default="", help="Output .lean file path (default: auto-derived)")
    parser.add_argument("--examples", type=int, default=2, help="Number of Lean4 example files for few-shot context")
    args = parser.parse_args(argv)

    module_path = Path(args.module)
    if not module_path.exists():
        print(f"ERROR: Module not found: {module_path}", file=sys.stderr)
        sys.exit(1)

    # Derive output path
    if args.out:
        out_path = Path(args.out)
    else:
        stem = module_path.stem  # e.g. pillar795_example
        # Convert to CamelCase
        camel = "".join(w.title() for w in stem.replace("-", "_").split("_"))
        out_path = LEAN4_DIR / f"{camel}.lean"

    print(f"🔍 Analysing {module_path.name}…", file=sys.stderr)
    summary = extract_python_summary(module_path)
    examples = _load_lean4_examples(args.examples)

    print(f"🧠 Calling OX Alpha ({OX_MODEL_ID}) for Lean4 stub generation…", file=sys.stderr)
    lean_body = call_ox_lean4(summary, examples)

    header = GOVERNANCE_HEADER.format(
        timestamp=datetime.now(timezone.utc).isoformat(),
        model=OX_MODEL_ID,
    )

    full_lean = header + "\n" + lean_body + "\n"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(full_lean, encoding="utf-8")

    print(f"✅ Lean4 stubs → {out_path}", file=sys.stderr)
    print(f"   ⚖️  STEWARD REVIEW REQUIRED before accepting into formal proof chain.")
    print(full_lean)


if __name__ == "__main__":
    main()
