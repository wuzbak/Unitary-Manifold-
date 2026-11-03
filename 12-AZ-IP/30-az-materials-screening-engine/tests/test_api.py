# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for the Phase-2 JSON API dispatch layer (no live HTTP server)."""
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_materials_screening_engine.api import API_ENDPOINTS, dispatch_api_request


def test_status_endpoint():
    result = dispatch_api_request("/api/status", {})
    assert result["product"] == "AZ Materials Screening Engine"
    assert result["endpoints"] == list(API_ENDPOINTS)


def test_screen_endpoint():
    result = dispatch_api_request(
        "/api/screen",
        {"name": ["demo"], "alpha": ["0.5"], "omega_lo_mev": ["100"], "m_band_me": ["0.2"], "epsilon_r": ["3.0"]},
    )
    assert result["name"] == "demo"
    assert "alpha_divergence_from_um" in result


def test_screen_endpoint_requires_params():
    with pytest.raises(ValueError):
        dispatch_api_request("/api/screen", {"name": ["demo"]})


def test_demo_rank_endpoint():
    result = dispatch_api_request("/api/demo-rank", {})
    assert len(result["candidates"]) == 3
    assert result["candidates"][0]["rank"] == 1


def test_unknown_endpoint_raises_keyerror():
    with pytest.raises(KeyError):
        dispatch_api_request("/api/nope", {})


@pytest.mark.parametrize("change", [
    {"alpha": ["NaN"]},
    {"epsilon_r": ["Infinity"]},
    {"mu_r": ["-Infinity"]},
    {"name": [" "]},
    {"alpha": ["-1"]},
    {"alpha": ["0.5", "1.0"]},
    {"omega_lo_ev": ["0.1"]},
    {"omega_lo_mev": ["5e-324"]},
])
def test_screen_rejects_invalid_input(change):
    query = {
        "name": ["test"], "alpha": ["0.5"], "omega_lo_mev": ["100"],
        "m_band_me": ["0.2"], "epsilon_r": ["3.0"],
    }
    query.update(change)
    with pytest.raises(ValueError):
        dispatch_api_request("/api/screen", query)


def test_live_http_errors_and_screening_notice():
    import json
    from threading import Thread
    from urllib.error import HTTPError
    from urllib.request import urlopen

    from az_materials_screening_engine.app.server import build_server

    server = build_server(port=0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/api/status", timeout=5) as response:
            assert response.status == 200
            assert "not experimental validation" in json.load(response)["screening_notice"]
        with urlopen(base + "/api/demo-rank", timeout=5) as response:
            assert "placeholder" in json.load(response)["data_status"]
        for path, code in [
            ("/api/screen?name=x&alpha=NaN&omega_lo_mev=100&m_band_me=0.2&epsilon_r=3", 400),
            ("/api/nope", 404),
        ]:
            with pytest.raises(HTTPError) as error:
                urlopen(base + path, timeout=5)
            assert error.value.code == code
            assert "error" in json.load(error.value)
            error.value.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
