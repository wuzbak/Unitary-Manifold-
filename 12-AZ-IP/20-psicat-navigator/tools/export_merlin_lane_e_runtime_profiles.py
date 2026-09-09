# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export Lane E runtime profile evidence payload as JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ox_navigator.engine.merlin_training_execution import get_merlin_lane_e_runtime_profiles


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Lane E runtime profile evidence.")
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Force benchmark recapture instead of reusing persisted Lane E profiles.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=str(ROOT / "training" / "training_execution" / "lane_e_runtime_profiles.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    payload = get_merlin_lane_e_runtime_profiles(refresh=bool(args.refresh))
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
