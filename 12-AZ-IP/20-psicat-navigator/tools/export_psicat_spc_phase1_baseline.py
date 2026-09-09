# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export PsiCat SPC phase-1 baseline execution receipts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_memory import MerlinSession
from ox_navigator.engine.merlin_program import run_psicat_spc_phase1_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Export PsiCat SPC phase-1 baseline execution packet.")
    parser.add_argument("--limit", type=int, default=5, help="Optional benchmark receipt limit")
    parser.add_argument("--training-limit", type=int, default=9, help="Optional retained training cycle limit")
    parser.add_argument(
        "--output",
        type=str,
        default=str(PRODUCT_ROOT / "training" / "training_execution" / "psicat_spc_phase1_baseline_receipts.json"),
        help="Output JSON path",
    )
    args = parser.parse_args()

    payload = run_psicat_spc_phase1_baseline(
        session=MerlinSession(),
        limit=args.limit,
        training_limit=args.training_limit,
    )
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_path)
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
