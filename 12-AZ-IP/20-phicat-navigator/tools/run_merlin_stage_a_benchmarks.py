# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Run Stage A incumbent-vs-Merlin benchmark gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ox_navigator.engine.merlin_benchmark import run_stage_a_head_to_head_receipts_sync


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Merlin Stage A benchmark promotion gates.")
    parser.add_argument("--json", action="store_true", help="Emit JSON only")
    args = parser.parse_args()

    payload = run_stage_a_head_to_head_receipts_sync()
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))
    else:
        print(json.dumps(payload, ensure_ascii=False, indent=2))

    if not payload["summary"]["promotion_gate_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
