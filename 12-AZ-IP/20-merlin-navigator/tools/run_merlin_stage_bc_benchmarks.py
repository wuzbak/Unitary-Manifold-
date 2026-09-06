# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Run Stage B/C Merlin benchmark receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_benchmark import (
    run_stage_b_head_to_head_receipts_sync,
    run_stage_c_head_to_head_receipts_sync,
    run_stage_d_head_to_head_receipts_sync,
    run_stage_e_head_to_head_receipts_sync,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Merlin Stage B/C/D/E benchmark receipts.")
    parser.add_argument("--stage", choices=["stage_b", "stage_c", "stage_d", "stage_e"], required=True)
    parser.add_argument("--limit", type=int, default=None, help="Optional benchmark limit")
    parser.add_argument("--output", type=str, help="Optional output JSON path")
    parser.add_argument("--json", action="store_true", help="Emit compact JSON")
    args = parser.parse_args()

    if args.stage == "stage_b":
        payload = run_stage_b_head_to_head_receipts_sync(limit=args.limit)
    elif args.stage == "stage_c":
        payload = run_stage_c_head_to_head_receipts_sync(limit=args.limit)
    elif args.stage == "stage_d":
        payload = run_stage_d_head_to_head_receipts_sync(limit=args.limit)
    else:
        payload = run_stage_e_head_to_head_receipts_sync(limit=args.limit)

    serial = json.dumps(payload, ensure_ascii=False) if args.json else json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(serial + "\n", encoding="utf-8")
        print(out_path)
    else:
        print(serial)

    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
