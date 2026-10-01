# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Build deterministic path inventories for the compact kernel and the monorepo."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPACT = ROOT / "COMPACTIFICATION"
BOOKS = "7-OUTREACH/A Z PsiCat Literature/Books/"
ARTICLES = "7-OUTREACH/A Z PsiCat Literature/Articles/"
PRODUCT = re.compile(r"^(0[1-9]|1[0-9]|2[0-5])-[^/]+$")


def tracked_paths() -> list[str]:
    """Use Git's index, plus new non-ignored files, rather than walking build outputs."""
    result = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files", "--cached", "--others",
         "--exclude-standard", "-z"],
        check=True, capture_output=True,
    )
    paths = {path for path in result.stdout.decode("utf-8").split("\0") if path}
    # The maps must index themselves even on the first build, before they exist.
    paths.update({"COMPACTIFICATION/kernel_map.json", "COMPACTIFICATION/monorepo_map.json"})
    return sorted(paths)


def classify(path: str) -> dict[str, str]:
    """Assign a navigational lane without inferring scientific or legal status."""
    parts = path.split("/")
    entry = {
        "path": path,
        "top_level": parts[0],
        "kind": "symlink" if (ROOT / path).is_symlink() else "file",
    }
    if path.startswith(BOOKS):
        entry["lane"] = "psicat_books"
    elif path.startswith(ARTICLES):
        entry["lane"] = "psicat_articles"
    elif path.startswith("12-AZ-IP/"):
        entry["lane"] = "az_ip"
        if len(parts) > 2 and PRODUCT.fullmatch(parts[1]):
            entry["product"] = parts[1]
    elif path.startswith("COMPACTIFICATION/"):
        entry["lane"] = "compactification"
    else:
        entry["lane"] = "other"
    return entry


def build_monorepo_map(paths: list[str]) -> dict:
    files = [classify(path) for path in paths]
    lanes = Counter(entry["lane"] for entry in files)
    top_levels = Counter(entry["top_level"] for entry in files)
    products = {
        product: [entry["path"] for entry in files if entry.get("product") == product]
        for product in sorted({entry["product"] for entry in files if "product" in entry})
    }
    return {
        "format": "unitary-monorepo-map-v1",
        "scope": "repository entries in Git index and non-ignored new entries at generation time, including symlinks",
        "source": "git ls-files --cached --others --exclude-standard",
        "file_count": len(files),
        "lanes": dict(sorted(lanes.items())),
        "top_levels": dict(sorted(top_levels.items())),
        "az_ip_products": products,
        "psicat_literature": {
            "books": [entry["path"] for entry in files if entry["lane"] == "psicat_books"],
            "articles": [entry["path"] for entry in files if entry["lane"] == "psicat_articles"],
        },
        "files": files,
    }


def build_kernel_map(paths: list[str]) -> dict:
    anchors = {
        "standalone_kernel": "COMPACTIFICATION/kernel.py",
        "axiom_registry": "COMPACTIFICATION/axioms.py",
        "kernel_tests": "COMPACTIFICATION/kernel_test.py",
        "snapshot_ledger": "COMPACTIFICATION/ledger.json",
        "kernel_guide": "COMPACTIFICATION/KERNEL_README.md",
        "current_status": "STATUS.md",
        "current_limitations": "FALLIBILITY.md",
        "foundation_reassessment": "docs/TRUTH_LAYER.md",
        "claim_registry": "docs/CLAIM_MASTER_BOARD.md",
        "pillar_tracker": "docs/mas_tracker.yml",
        "formal_gate": "proof/TIER_1_FORMAL.md",
        "product_registry": "12-AZ-IP/README.md",
        "ip_asset_registry": "12-AZ-IP/IP_REGISTRY.json",
        "editorial_index": "7-OUTREACH/A Z PsiCat Literature/README.md",
        "monorepo_map": "COMPACTIFICATION/monorepo_map.json",
        "map_builder": "COMPACTIFICATION/build_maps.py",
    }
    missing = sorted(set(anchors.values()) - set(paths))
    if missing:
        raise ValueError(f"Missing kernel-map anchors: {missing}")
    return {
        "format": "unitary-compact-kernel-map-v1",
        "scope": "standalone historical calculation surface plus live repository pointers",
        "not_a_claim": "This inventory is not a derivation, formal proof, or validation of every repo asset.",
        "anchors": anchors,
        "entrypoint": {
            "command": "python3 COMPACTIFICATION/kernel_test.py",
            "test_scope": "standalone kernel assertions, not the full monorepo regression",
        },
        "catalogues": {
            "az_ip": "COMPACTIFICATION/monorepo_map.json#az_ip_products",
            "books": "COMPACTIFICATION/monorepo_map.json#psicat_literature/books",
            "articles": "COMPACTIFICATION/monorepo_map.json#psicat_literature/articles",
            "all_files": "COMPACTIFICATION/monorepo_map.json#files",
        },
        "epistemic_boundary": {
            "snapshot": "COMPACTIFICATION/ledger.json",
            "superseding_assessment": "docs/TRUTH_LAYER.md",
            "live_gaps": "FALLIBILITY.md",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if committed maps are stale")
    args = parser.parse_args()
    paths = tracked_paths()
    output = {
        COMPACT / "kernel_map.json": build_kernel_map(paths),
        COMPACT / "monorepo_map.json": build_monorepo_map(paths),
    }
    stale = []
    for filename, payload in output.items():
        serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.check:
            if not filename.is_file() or filename.read_text(encoding="utf-8") != serialized:
                stale.append(filename.name)
        else:
            filename.write_text(serialized, encoding="utf-8")
    if stale:
        parser.exit(1, f"Stale maps: {', '.join(stale)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
