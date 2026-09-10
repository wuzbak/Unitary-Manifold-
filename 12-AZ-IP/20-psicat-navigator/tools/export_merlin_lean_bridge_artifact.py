# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export Merlin's Python↔Lean bridge artifact as JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_lean_bridge import get_merlin_lean_bridge_artifact


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Merlin Python↔Lean bridge artifact.")
    parser.add_argument("--limit", type=int, default=0, help="Optional formal-unit preview limit; 0 exports full governed view")
    parser.add_argument(
        "--output",
        type=str,
        default=str(PRODUCT_ROOT / "training" / "training_artifacts" / "lean_bridge_artifact.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()
    payload = get_merlin_lean_bridge_artifact(limit=args.limit)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
