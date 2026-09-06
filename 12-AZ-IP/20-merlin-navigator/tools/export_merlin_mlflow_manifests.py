# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export MLflow-ready Merlin experiment manifests."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ox_navigator.engine.merlin_program import get_mlflow_experiment_manifests


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Merlin MLflow experiment manifests.")
    parser.add_argument("--limit", type=int, default=12, help="Optional seed example limit")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    payload = get_mlflow_experiment_manifests(limit=args.limit)
    if not payload.get("ok"):
        print(json.dumps({
            "ok": False,
            "error": payload.get("error", "Unable to build MLflow manifests."),
        }, ensure_ascii=False))
        return 1
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / "mlflow_manifests.json"
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
