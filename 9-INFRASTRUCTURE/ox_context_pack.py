# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
9-INFRASTRUCTURE/ox_context_pack.py — OX Alpha Full-Repository Context Builder

Builds ox_full_context.md: a single Markdown document containing a curated
summary of the entire Unitary Manifold repository, optimised for injection
into OX Alpha's extended-memory context window.

Sections assembled:
  1. Repository identity & framework constants (from MCP_INGEST.md)
  2. Live status snapshot (STATUS.md)
  3. All open/closed claims (docs/CLAIM_MASTER_BOARD.md)
  4. Honest admitted gaps (FALLIBILITY.md)
  5. Pillar docstrings auto-extracted from src/core/*.py
  6. Lean4 theorem names from lean4/UnitaryManifold/*.lean
  7. Key predictions summary

Usage:
  python 9-INFRASTRUCTURE/ox_context_pack.py            # writes ox_full_context.md
  python 9-INFRASTRUCTURE/ox_context_pack.py --stats    # print token estimate only

The output file is checked in; rebuild whenever major pillar additions land.

Theory & scientific direction: ThomasCory Walker-Pearson.
Code, engineering, synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
OUTPUT_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "ox_full_context.md"

# ── Source files included verbatim (trimmed to first 8 KB each) ───────────────
VERBATIM_SOURCES: list[tuple[str, Path]] = [
    ("Repository Summary (MCP_INGEST)",   REPO_ROOT / "6-MONOGRAPH" / "MCP_INGEST.md"),
    ("Live Status (STATUS.md)",           REPO_ROOT / "STATUS.md"),
    ("Claim Master Board",                REPO_ROOT / "docs" / "CLAIM_MASTER_BOARD.md"),
    ("Admitted Gaps (FALLIBILITY.md)",    REPO_ROOT / "FALLIBILITY.md"),
]

VERBATIM_CHAR_LIMIT = 8_000   # per section, to stay within token budget

# ── Pillar docstring extraction ────────────────────────────────────────────────
PILLAR_CORE_DIR = REPO_ROOT / "src" / "core"

def _extract_module_docstring(path: Path) -> str:
    """Return the module-level docstring from a Python file, or empty string."""
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source)
        first = ast.get_docstring(tree)
        return (first or "").strip()
    except Exception:
        return ""


def _extract_pillar_docstrings() -> str:
    """Extract docstrings from all pillar*.py modules in src/core/."""
    if not PILLAR_CORE_DIR.exists():
        return "_src/core/ not found — skipping pillar docstring extraction._\n"

    files = sorted(PILLAR_CORE_DIR.glob("pillar*.py"))
    lines: list[str] = []
    for f in files:
        doc = _extract_module_docstring(f)
        if doc:
            # Keep first 400 chars per pillar to stay within budget
            snippet = doc[:400].replace("\n", " ").strip()
            lines.append(f"- **{f.stem}**: {snippet}")

    if not lines:
        return "_No pillar*.py docstrings found._\n"
    return "\n".join(lines) + "\n"


# ── Lean4 theorem name extraction ─────────────────────────────────────────────
LEAN4_DIR = REPO_ROOT / "lean4" / "UnitaryManifold"
_THEOREM_RE = re.compile(r"^(?:theorem|lemma|def)\s+(\w+)", re.MULTILINE)


def _extract_lean4_theorems() -> str:
    """Extract theorem/lemma names from all .lean files."""
    if not LEAN4_DIR.exists():
        return "_lean4/UnitaryManifold/ not found._\n"

    names: list[str] = []
    for lean_file in sorted(LEAN4_DIR.glob("*.lean")):
        text = lean_file.read_text(encoding="utf-8", errors="replace")
        found = _THEOREM_RE.findall(text)
        if found:
            names.extend(f"{lean_file.stem}::{n}" for n in found)

    if not names:
        return "_No Lean4 theorems found._\n"
    return ", ".join(names) + "\n"


# ── Key predictions block ──────────────────────────────────────────────────────
PREDICTIONS_BLOCK = """\
## Key UM Predictions & Epistemic Status

| Prediction | Value | Observation | Status |
|------------|-------|-------------|--------|
| CMB spectral index n_s | 0.9635 | 0.9649 ± 0.0042 (Planck) | ✅ 0.3σ — HARDGATE |
| Tensor-to-scalar r | 0.0315 | < 0.036 (BICEP/Keck) | ✅ within bound — HARDGATE |
| Birefringence β | {0.273°, 0.331°} | untested | ⏳ LiteBIRD ~2032 — PRIMARY FALSIFIER |
| Higgs mass | ~126.2 GeV | 125.25 ± 0.17 GeV (LHC) | ✅ one-loop consistent |
| Dark energy w_a | 0 | ~2σ tension (DESI Y1) | ⚠️ OPEN_GAP |
| Δm²₂₁ tension | 1.07σ residual | NLO gate active | ⚠️ OPEN_GAP |
| K_cs resonance | 74 = 5²+7² | — | HARDGATE selection |
| Winding number n_w | 5 | Planck n_s selects n_w=5 | HARDGATE (not proved from first principles alone) |

**Falsification conditions:**
- Any birefringence β outside [0.22°, 0.38°] falsifies the braided-winding mechanism.
- Any β landing in gap [0.29°–0.31°] falsifies the mechanism.
- DESI Year 2 result will adjudicate the w_a=0 tension.

**GOVERNANCE NOTE:** OX outputs are AI-generated suggestions. No hardgate status change,
pillar numbering, or Lean4 theorem acceptance is valid without steward (wuzbak) approval
(HILS framework — see SEPARATION.md).
"""

# ── Assemble ───────────────────────────────────────────────────────────────────

def build_pack() -> str:
    """Assemble the full context pack string."""
    sections: list[str] = [
        "# Unitary Manifold — OX Alpha Full Repository Context Pack",
        "<!-- Auto-generated by 9-INFRASTRUCTURE/ox_context_pack.py — do not edit manually -->",
        "",
        PREDICTIONS_BLOCK,
    ]

    # Verbatim sections
    for title, path in VERBATIM_SOURCES:
        sections.append(f"\n## {title}\n")
        if path.exists():
            text = path.read_text(encoding="utf-8", errors="replace")
            if len(text) > VERBATIM_CHAR_LIMIT:
                text = text[:VERBATIM_CHAR_LIMIT] + f"\n\n_... (truncated at {VERBATIM_CHAR_LIMIT} chars)_"
            sections.append(text)
        else:
            sections.append(f"_File not found: {path.relative_to(REPO_ROOT)}_")

    # Pillar docstrings
    sections.append("\n## Pillar Module Docstrings (auto-extracted from src/core/pillar*.py)\n")
    sections.append(_extract_pillar_docstrings())

    # Lean4 theorem names
    sections.append("\n## Lean4 Theorem Names (lean4/UnitaryManifold/*.lean)\n")
    sections.append(_extract_lean4_theorems())

    return "\n".join(sections)


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token."""
    return len(text) // 4


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build OX Alpha full-repository context pack.")
    parser.add_argument("--stats", action="store_true", help="Print token estimate only, do not write file.")
    parser.add_argument("--output", type=str, default=str(OUTPUT_PATH), help="Output file path.")
    args = parser.parse_args(argv)

    pack = build_pack()
    tokens = estimate_tokens(pack)
    chars = len(pack)

    if args.stats:
        print(f"Context pack stats: {chars:,} chars · ~{tokens:,} tokens")
        return

    out = Path(args.output)
    out.write_text(pack, encoding="utf-8")
    print(f"✅ OX context pack written → {out}")
    print(f"   {chars:,} chars · ~{tokens:,} tokens")


if __name__ == "__main__":
    main()
