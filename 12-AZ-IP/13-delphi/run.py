#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""DelPhi Oracle Suite — launcher (loopback by default)."""
import argparse
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve the DelPhi Oracle Suite.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    # Sources import ``delphi.app.*`` while the application tree is ``app/``.
    delphi = importlib.import_module("delphi")
    app_pkg = importlib.import_module("app")
    sys.modules["delphi.app"] = app_pkg
    delphi.app = app_pkg
    import uvicorn
    from delphi.app.main import app

    uvicorn.run(app, host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
