# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Live HTTP contract tests for the cosmology slider."""

import json
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_cosmology_slider.app.server import build_server


def test_live_server_reports_bounds_and_optional_jax_status():
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{base_url}/api/status") as response:
            status = json.load(response)
            assert response.status == 200
            assert isinstance(status["jax_available"], bool)

        try:
            urlopen(f"{base_url}/api/slider?phi0=nan")
        except HTTPError as error:
            assert error.code == 400
            assert "phi0" in json.load(error)["error"]
        else:
            raise AssertionError("non-finite input unexpectedly succeeded")

        try:
            with urlopen(f"{base_url}/api/slider?phi0=10&n_w=5") as response:
                assert status["jax_available"]
                assert response.status == 200
        except HTTPError as error:
            assert not status["jax_available"]
            assert error.code == 503
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
