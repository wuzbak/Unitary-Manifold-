#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies / ThomasCory Walker-Pearson
"""LithosOS — Mineral & Gemstone Identifier launcher."""
import os

import uvicorn
from app.main import create_app

if __name__ == "__main__":
    app = create_app()
    uvicorn.run(
        app,
        host=os.environ.get("AZ_SERVICE_HOST", "127.0.0.1"),
        port=int(os.environ.get("AZ_SERVICE_PORT", "7861")),
        reload=False,
    )
