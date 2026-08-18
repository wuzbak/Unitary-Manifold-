#!/usr/bin/env python3
# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: DPCO-1.0
"""
PILLARS/build_index.py — Auto-generate PILLARS/README.md from the filesystem.

Run from the repository root:
    python3 PILLARS/build_index.py

Reads: PILLARS/P*/README.md stubs
Writes: PILLARS/README.md (master index table)
"""
import os, re

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILLARS_DIR = os.path.join(REPO, "PILLARS")

rows_hardgate = []
rows_adjacent = []

for folder in sorted(os.listdir(PILLARS_DIR)):
    m = re.match(r'P(\d+)$', folder)
    if not m:
        continue
    n = int(m.group(1))
    readme = os.path.join(PILLARS_DIR, folder, "README.md")
    if not os.path.exists(readme):
        continue
    with open(readme) as f:
        content = f.read()
    # Extract name from first heading
    name_m = re.search(r'^# Pillar \d+ — (.+)$', content, re.MULTILINE)
    name = name_m.group(1) if name_m else "—"
    is_adjacent = "🔵 ADJACENT" in content
    status = "🟡 ADJACENT" if is_adjacent else "🟢 HARDGATE"
    src_m = re.search(r'\*\*Source module\(s\):\*\* `(.+?)`', content)
    src = src_m.group(1) if src_m else "—"
    row = f"| [{n}]({folder}/README.md) | {name} | {status} | `{src}` |"
    if is_adjacent:
        rows_adjacent.append((n, row))
    else:
        rows_hardgate.append((n, row))

header = """| Pillar # | Name / Claim | Status | Primary Source |
|---|---|---|---|"""

out = f"""# PILLARS — Master Index

**Unitary Manifold v20.9 | Generated: 2026-08-18 | Total pillars: {len(rows_hardgate)+len(rows_adjacent)}**

This is the auto-generated master navigation index for all pillars.
For full claim details, see [`docs/mas_tracker.yml`](../docs/mas_tracker.yml).

> **Regenerate this file:** `python3 PILLARS/build_index.py` from the repository root.

---

## Foundation & Core Hardgate Pillars (P001–P208)

These {len(rows_hardgate)} pillars are formally closed (hardgate). Each has passing test suite.

{header}
""" + "\n".join(r for _, r in rows_hardgate) + f"""

---

## Adjacent Research Tracks (P209+)

These {len(rows_adjacent)} pillars are 🔵 ADJACENT TRACK — **not hardgate physics claims**.
They are quantitative explorations connecting UM geometry to applied domains.
They have full test suites and markdown documentation but do NOT affect the core ToE score.

{header}
""" + "\n".join(r for _, r in rows_adjacent) + """

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
"""

out_path = os.path.join(PILLARS_DIR, "README.md")
with open(out_path, "w") as f:
    f.write(out)
print(f"Written: {out_path}")
print(f"  {len(rows_hardgate)} hardgate pillars")
print(f"  {len(rows_adjacent)} adjacent track pillars")
