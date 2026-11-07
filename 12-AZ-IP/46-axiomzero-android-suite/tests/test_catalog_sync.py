# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson

import importlib.util
from pathlib import Path


def test_android_catalog_is_the_canonical_portfolio_catalog():
    suite = Path(__file__).resolve().parents[1]
    script = suite / "scripts" / "build_catalog.py"
    spec = importlib.util.spec_from_file_location("build_android_catalog", script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = suite.parents[1] / "12-AZ-IP" / "45-axiomzero-pc-suite" / "catalog" / "products.json"
    target = suite / "app" / "src" / "main" / "assets" / "products.json"
    assert target.read_bytes() == source.read_bytes()
