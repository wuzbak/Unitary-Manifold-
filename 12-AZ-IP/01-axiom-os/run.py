#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""AXIOM OS — launcher (delegates to axiomzero_bootstrap)."""
import sys
from pathlib import Path


def serve(argv):
    """Serve the AxiomZero API/dashboard on loopback: ``run.py serve --port 8001``."""
    import argparse

    parser = argparse.ArgumentParser(prog="run.py serve")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args(argv)
    if args.host not in ("127.0.0.1", "localhost"):
        parser.error("Serve mode binds to loopback only.")
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import uvicorn
    from api.server import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    if sys.argv[1:2] == ["serve"]:
        serve(sys.argv[2:])
    else:
        from axiomzero_bootstrap import main

        main()
