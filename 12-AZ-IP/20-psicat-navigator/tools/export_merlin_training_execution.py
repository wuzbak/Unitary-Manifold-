# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export retained three-lane Merlin training execution artifacts as JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_training_execution import build_merlin_training_execution_bundle


def main() -> int:
    parser = argparse.ArgumentParser(description="Export retained Merlin three-lane training execution bundle.")
    parser.add_argument("--limit", type=int, default=0, help="Optional item cap; 0 means execute the full queue.")
    parser.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "training" / "training_execution" / "three_lane_execution_bundle.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    session = MerlinSession()
    limit = None if int(args.limit or 0) == 0 else int(args.limit)
    payload = build_merlin_training_execution_bundle(session=session, limit=limit)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
