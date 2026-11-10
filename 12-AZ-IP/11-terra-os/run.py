#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""TerraOS — Soil & Water Expert System launcher (loopback by default)."""
import argparse
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _alias_terra_package() -> None:
    # The sources import ``terra.app.*`` while the tree ships as ``app/``.
    if "terra" not in sys.modules:
        pkg = types.ModuleType("terra")
        pkg.__path__ = [str(ROOT)]
        sys.modules["terra"] = pkg


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve TerraOS.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    _alias_terra_package()
    import uvicorn
    from terra.app.main import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
