#!/usr/bin/env python3
"""Build the offline product directory from the canonical AxiomZero catalog."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PRODUCT_ROW = re.compile(r"^\|\s*(\d{2})\s*\|")
FOLDER_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
def parse_catalog(readme: str) -> list[dict[str, str]]:
    products: list[dict[str, str]] = []
    for line in readme.splitlines():
        match = PRODUCT_ROW.match(line)
        if not match:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            raise ValueError(f"Malformed product catalog row: {line}")
        folder_match = FOLDER_LINK.search(cells[7])
        if not folder_match:
            raise ValueError(f"Product {cells[0]} has no folder link.")
        name = cells[1].replace("**", "").strip()
        endpoint = cells[4].replace("<br>", " · ").replace("**", "").replace("`", "")
        products.append(
            {
                "id": cells[0],
                "name": name,
                "version": cells[2],
                "trl": cells[3],
                "endpoint": endpoint,
                "description": cells[6],
                "folder": "12-AZ-IP/" + folder_match.group(1).rstrip("/") + "/",
            }
        )
    expected_ids = [f"{number:02d}" for number in range(1, 47)]
    actual_ids = [product["id"] for product in products]
    if actual_ids != expected_ids:
        raise ValueError(
            "The canonical catalog must contain Products 01-46 in order; "
            f"found {actual_ids!r}."
        )
    return products


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the bundled catalog is stale")
    args = parser.parse_args()
    suite_dir = Path(__file__).resolve().parents[1]
    repository_root = suite_dir.parents[1]
    source = repository_root / "12-AZ-IP" / "README.md"
    destination = suite_dir / "catalog" / "products.json"
    try:
        output = json.dumps(parse_catalog(source.read_text(encoding="utf-8")), indent=2, ensure_ascii=False) + "\n"
    except (OSError, ValueError) as error:
        print(f"Catalog generation failed: {error}", file=sys.stderr)
        return 1
    if args.check:
        try:
            current = destination.read_text(encoding="utf-8")
        except OSError as error:
            print(f"Bundled catalog is unavailable: {error}", file=sys.stderr)
            return 1
        if current != output:
            print(f"{destination} is stale; run python scripts/build_catalog.py.", file=sys.stderr)
            return 1
        print(f"Catalog is current ({len(parse_catalog(source.read_text(encoding='utf-8')))} products).")
        return 0
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8")
    print(f"Wrote {len(parse_catalog(source.read_text(encoding='utf-8')))} products to {destination}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
