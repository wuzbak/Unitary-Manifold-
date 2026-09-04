# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Shared Merlin package bootstrap helpers for Sprint BX/BY audits."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def ensure_merlin_package_loaded(product_root: Path) -> None:
    package_root = product_root / "ox_navigator"
    existing = sys.modules.get("ox_navigator")
    if existing is not None:
        existing_paths = [Path(p).resolve() for p in getattr(existing, "__path__", [])]
        existing_file = Path(getattr(existing, "__file__", package_root / "__init__.py")).resolve()
        if existing_file == (package_root / "__init__.py").resolve() or package_root.resolve() in existing_paths:
            return
        sys.modules.pop("ox_navigator", None)
    spec = importlib.util.spec_from_file_location(
        "ox_navigator",
        package_root / "__init__.py",
        submodule_search_locations=[str(package_root)],
    )
    if spec is None or spec.loader is None:
        raise ImportError("Unable to load ox_navigator package")
    module = importlib.util.module_from_spec(spec)
    sys.modules["ox_navigator"] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop("ox_navigator", None)
        raise
