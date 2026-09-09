# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Polyglot stack dependency and toolchain health checks."""

from __future__ import annotations

import importlib
import os
import shutil
import subprocess
from typing import Dict


_EXTRA_PATHS = [
    str(os.path.expanduser("~/.local/bin")),
    str(os.path.expanduser("~/.cargo/bin")),
]


def _env_with_extra_path() -> dict:
    base = dict(os.environ)
    current = base.get("PATH", "")
    prefix = ":".join(p for p in _EXTRA_PATHS if p)
    base["PATH"] = f"{prefix}:{current}" if current else prefix
    return base


def _import_probe(module_name: str) -> Dict[str, object]:
    try:
        mod = importlib.import_module(module_name)
        return {
            "available": True,
            "version": str(getattr(mod, "__version__", "unknown")),
        }
    except Exception as exc:
        return {"available": False, "error": str(exc)}


def _binary_probe(binary: str, *args: str) -> Dict[str, object]:
    env = _env_with_extra_path()
    exe = shutil.which(binary, path=env.get("PATH"))
    if exe is None:
        return {"available": False, "path": None}
    try:
        proc = subprocess.run(
            [exe, *args],
            check=False,
            capture_output=True,
            text=True,
            timeout=12,
            env=env,
        )
        out = (proc.stdout or proc.stderr or "").strip().splitlines()
        version = out[0] if out else ""
        return {
            "available": proc.returncode == 0,
            "path": exe,
            "version": version,
        }
    except Exception as exc:
        return {"available": False, "path": exe, "error": str(exc)}


def _zig_probe() -> Dict[str, object]:
    direct = _binary_probe("zig", "version")
    if direct.get("available"):
        return direct
    # pip ziglang installs a `python-zig` executable in ~/.local/bin
    alt = _binary_probe("python-zig", "version")
    if alt.get("available"):
        return {
            "available": True,
            "path": alt.get("path"),
            "version": alt.get("version"),
            "invocation": "python-zig",
        }
    return direct


def polyglot_stack_health_report() -> Dict[str, object]:
    """Return machine-readable readiness for requested language+data stack."""
    languages = {
        "python": _binary_probe("python", "--version"),
        "julia": _binary_probe("julia", "--version"),
        "mojo": _binary_probe("mojo", "--version"),
        "rust": _binary_probe("rustc", "--version"),
        "zig": _zig_probe(),
        "lean4": _binary_probe("lean", "--version"),
        "typescript": _binary_probe("tsc", "--version"),
    }
    data_storage = {
        "zarr": _import_probe("zarr"),
        "pyarrow": _import_probe("pyarrow"),
        "duckdb": _import_probe("duckdb"),
        "polars": _import_probe("polars"),
    }
    execution_compute = {
        "jax": _import_probe("jax"),
        "wasm_runtime": _binary_probe("wasmtime", "--version"),
        "wasm_pack": _binary_probe("wasm-pack", "--version"),
        "webgpu_shader_tools": _binary_probe("naga", "--version"),
    }
    verification_logic = {
        "z3": _import_probe("z3"),
        "lean4": languages["lean4"],
    }
    docs_pipelines = {
        "quarto": _binary_probe("quarto", "--version"),
        "latex": _binary_probe("pdflatex", "--version"),
        "dvc": _binary_probe("dvc", "--version"),
        "wandb": _import_probe("wandb"),
    }
    parquet = {
        "supported_via_pyarrow": bool(data_storage["pyarrow"].get("available")),
        "supported_via_polars": bool(data_storage["polars"].get("available")),
    }
    return {
        "languages": languages,
        "data_storage": {**data_storage, "parquet": parquet},
        "execution_compute": execution_compute,
        "verification_logic": verification_logic,
        "docs_pipelines": docs_pipelines,
    }
