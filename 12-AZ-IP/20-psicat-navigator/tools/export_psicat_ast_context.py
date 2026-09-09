# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Export deterministic AST-dense training context for PsiCat."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_tools import get_toolkit_view

SKIP_PARTS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "node_modules",
}


def _iter_python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*.py")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        files.append(path)
    return files


def _extract_symbol_record(path: Path) -> dict[str, Any] | None:
    try:
        source = path.read_text(encoding="utf-8")
    except OSError:
        return None
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    module_doc = ast.get_docstring(tree) or ""
    funcs: list[dict[str, Any]] = []
    classes: list[dict[str, Any]] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            funcs.append(
                {
                    "name": node.name,
                    "lineno": int(getattr(node, "lineno", 0) or 0),
                    "end_lineno": int(getattr(node, "end_lineno", 0) or 0),
                    "arg_count": len(list(getattr(node.args, "args", []) or [])),
                }
            )
        elif isinstance(node, ast.ClassDef):
            method_count = sum(
                1
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            )
            classes.append(
                {
                    "name": node.name,
                    "lineno": int(getattr(node, "lineno", 0) or 0),
                    "end_lineno": int(getattr(node, "end_lineno", 0) or 0),
                    "method_count": method_count,
                }
            )
    rel = path.relative_to(REPO_ROOT).as_posix()
    text_loop = " ".join(
        token
        for token in [
            f"path:{rel}",
            f"functions:{','.join(item['name'] for item in funcs[:40]) or 'none'}",
            f"classes:{','.join(item['name'] for item in classes[:30]) or 'none'}",
            f"doc:{module_doc.strip().replace(chr(10), ' ')[:240] or 'none'}",
        ]
        if token
    )
    return {
        "record_id": f"ast:{hashlib.sha256(rel.encode('utf-8')).hexdigest()[:16]}",
        "record_type": "repository_ast_symbol_context",
        "relative_path": rel,
        "symbol_counts": {
            "functions": len(funcs),
            "classes": len(classes),
        },
        "symbol_table": {
            "functions": funcs[:200],
            "classes": classes[:120],
        },
        "deterministic_token_loop": text_loop,
        "instruction": f"Extract governed implementation context from {rel} without boilerplate.",
        "response_target": {
            "path": rel,
            "function_names": [item["name"] for item in funcs[:60]],
            "class_names": [item["name"] for item in classes[:60]],
            "counts": {"functions": len(funcs), "classes": len(classes)},
        },
        "required_gates": ["GOVERNANCE", "ADJACENT_TRACK"],
        "provenance_sources": [rel],
    }


def _tool_records() -> list[dict[str, Any]]:
    toolkit = get_toolkit_view("full")
    functions = list(toolkit.get("functions") or [])
    rows: list[dict[str, Any]] = []
    for item in sorted(functions, key=lambda row: str(row.get("name") or "")):
        name = str(item.get("name") or "")
        if not name:
            continue
        summary = str(item.get("summary") or "")
        rows.append(
            {
                "record_id": f"tool:{hashlib.sha256(name.encode('utf-8')).hexdigest()[:16]}",
                "record_type": "axiomzero_tool_definition_context",
                "tool_name": name,
                "tool_summary": summary,
                "deterministic_token_loop": f"tool:{name} summary:{summary}",
                "instruction": f"Route tool {name} with boundary-safe contracts.",
                "response_target": {
                    "tool_name": name,
                    "summary": summary,
                    "risk_level": str(item.get("risk_level") or ""),
                    "capability_class": str(item.get("capability_class") or ""),
                },
                "required_gates": ["GOVERNANCE"],
                "provenance_sources": ["12-AZ-IP/20-psicat-navigator/ox_navigator/engine/merlin_tools.py"],
            }
        )
    return rows


def export_ast_context(*, output: Path, file_limit: int | None = None) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    files = _iter_python_files(REPO_ROOT)
    if file_limit is not None:
        files = files[: max(0, int(file_limit))]
    for path in files:
        row = _extract_symbol_record(path)
        if row:
            rows.append(row)
    rows.extend(_tool_records())
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {
        "ok": True,
        "output": str(output),
        "record_count": len(rows),
        "python_file_count": len(files),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export deterministic AST/token-dense PsiCat training context.")
    parser.add_argument("--output", default=str(PRODUCT_ROOT / "training" / "training_jsonl" / "ast_context.jsonl"))
    parser.add_argument("--file-limit", type=int, default=None)
    args = parser.parse_args()
    payload = export_ast_context(output=Path(args.output), file_limit=args.file_limit)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
