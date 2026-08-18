#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""FilmersCompanion — Desktop App launcher."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from desktop.app.main import main

if __name__ == "__main__":
    main()
