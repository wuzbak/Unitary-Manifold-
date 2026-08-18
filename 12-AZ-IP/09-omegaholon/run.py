#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""OmegaHolon — launcher."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from app.main import build_ui

if __name__ == "__main__":
    ui = build_ui()
    ui.launch(server_name="0.0.0.0", server_port=7871, share=False, inbrowser=True)
