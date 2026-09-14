# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

from __future__ import annotations

import threading

import httpx

from ox_navigator.app.server import serve
from ox_navigator.engine.merlin_kernel_runtime import (
    get_compactification_sanity_receipt,
    get_kernel_execution_receipts,
    get_kernel_runtime_board,
)


def test_kernel_runtime_board_contract():
    board = get_kernel_runtime_board()
    assert board["ok"] is True
    assert board["board_id"] == "psicat_kernel_runtime_board_v1"
    assert board["policy"]["hard_bypass_forbidden"] is True
    assert "kernel_contracts" in board


def test_kernel_execution_receipts_fail_closed_contract():
    payload = get_kernel_execution_receipts(points=6, seed=4)
    assert payload["ok"] is True
    assert "receipt" in payload
    assert payload["governance"]["unchecked_or_unlogged_execution_forbidden"] is True


def test_compactification_sanity_receipt_surface():
    payload = get_compactification_sanity_receipt()
    assert "checks" in payload
    assert "policy" in payload
    assert payload["policy"]["unchecked_bypass_forbidden"] is True


def test_server_kernel_runtime_endpoints():
    httpd = serve(port=0)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        port = httpd.server_address[1]
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=15.0) as client:
            runtime_resp = client.get("/api/psicat/kernel-runtime")
            assert runtime_resp.status_code == 200
            assert runtime_resp.json()["ok"] is True

            receipts_resp = client.get("/api/psicat/kernel-receipts?points=6&seed=4")
            assert receipts_resp.status_code == 200
            assert receipts_resp.json()["ok"] is True

            sanity_resp = client.get("/api/psicat/compactification-sanity")
            assert sanity_resp.status_code in {200, 422}
            payload = sanity_resp.json()
            assert "compactification_sanity" in payload

            compat_resp = client.get("/api/merlin/kernel-runtime")
            assert compat_resp.status_code == 200
            assert compat_resp.json()["ok"] is True
    finally:
        httpd.shutdown()
        httpd.server_close()
        thread.join(timeout=2)
