# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export Merlin training and benchmark corpora as JSONL files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ox_navigator.engine.merlin_program import build_training_dataset_bundle


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Export Merlin training JSONL files.")
    parser.add_argument("--limit", type=int, default=12, help="Optional seed example limit")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    payload = build_training_dataset_bundle(limit=args.limit)
    dataset = dict(payload.get("dataset") or {})
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for split_name, rows in dict(dataset.get("splits") or {}).items():
        _write_jsonl(out_dir / f"{split_name}.jsonl", list(rows or []))
    for kernel_id, per_split in dict(dataset.get("kernel_splits") or {}).items():
        for split_name, rows in dict(per_split or {}).items():
            _write_jsonl(out_dir / "kernels" / kernel_id / f"{split_name}.jsonl", list(rows or []))

    benchmark_dir = out_dir / "benchmarks"
    for stage_name, rows in dict(dataset.get("benchmark_corpora") or {}).items():
        _write_jsonl(benchmark_dir / f"{stage_name}.jsonl", list(rows or []))
    for stage_name, per_kernel in dict(dataset.get("kernel_benchmark_corpora") or {}).items():
        for kernel_id, rows in dict(per_kernel or {}).items():
            _write_jsonl(benchmark_dir / "kernels" / stage_name / f"{kernel_id}.jsonl", list(rows or []))

    manifest_path = out_dir / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
