#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""10-UM-SOS — Scientific Operating System launcher."""
import os
import sys
from pathlib import Path

import uvicorn

PRODUCT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PRODUCT_ROOT.parents[2]
sys.path[:0] = [str(REPO_ROOT), str(PRODUCT_ROOT)]

from backend.app import app


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=os.environ.get("UM_SOS_HOST", "127.0.0.1"),
        port=int(os.environ.get("UM_SOS_PORT", "8000")),
        reload=False,
    )
