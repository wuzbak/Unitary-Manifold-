#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"

echo "[polyglot-bootstrap] root: $ROOT_DIR"
python -m pip install --user --upgrade pip >/dev/null
python -m pip install --user juliacall duckdb polars pyarrow zarr >/dev/null

if command -v cargo >/dev/null 2>&1; then
  cargo install --locked wasm-pack || true
  cargo install --locked naga-cli || true
  cargo install --locked wasmtime-cli || true
fi

if ! command -v quarto >/dev/null 2>&1; then
  python -m pip install --user quarto-cli || true
fi

if ! command -v zig >/dev/null 2>&1 && ! command -v python-zig >/dev/null 2>&1; then
  python -m pip install --user ziglang || true
fi

if ! command -v lean >/dev/null 2>&1 && command -v elan >/dev/null 2>&1; then
  elan default leanprover/lean4:stable || true
fi

echo "[polyglot-bootstrap] completed (best effort, non-root)."
