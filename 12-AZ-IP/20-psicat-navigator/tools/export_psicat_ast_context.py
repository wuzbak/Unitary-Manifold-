# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export deterministic AST-context training rows for PsiCat."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_program import build_ast_context_training_records


def export_ast_context(*, output: Path, file_limit: int | None = None) -> dict[str, object]:
    rows = build_ast_context_training_records(file_limit=file_limit)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {
        "ok": True,
        "output": str(output),
        "record_count": len(rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic AST-context records for PsiCat training.")
    parser.add_argument("--output", default=str(PRODUCT_ROOT / "training" / "training_jsonl" / "ast_context.jsonl"))
    parser.add_argument("--file-limit", type=int, default=None)
    args = parser.parse_args()
    payload = export_ast_context(output=Path(args.output), file_limit=args.file_limit)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
