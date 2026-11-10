#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""AXIOM Investigative Journalist AI — launcher."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.main import build_ui

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(
        server_name=os.environ.get("AZ_SERVICE_HOST", "127.0.0.1"),
        server_port=int(os.environ.get("AZ_SERVICE_PORT", "7870")),
        share=False,
        inbrowser=os.environ.get("AZ_SERVICE_NO_BROWSER") != "1",
    )
