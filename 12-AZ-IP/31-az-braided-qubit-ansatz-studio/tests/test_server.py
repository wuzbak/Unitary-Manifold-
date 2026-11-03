# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Live HTTP contract tests for the studio server."""

import json
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_braided_qubit_ansatz_studio.app.server import build_server


def test_live_server_serves_qasm_and_rejects_invalid_queries():
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{base_url}/api/circuit?n_qubits=2&n_layers=1&seed=7") as response:
            payload = json.load(response)
            assert response.status == 200
            assert payload["openqasm2"].startswith("OPENQASM 2.0;")
            assert payload["validation"]["matches_kk_vqe"] is True

        with urlopen(f"{base_url}/") as response:
            page = response.read().decode("utf-8")
            assert "Download OpenQASM 2.0" in page

        try:
            urlopen(f"{base_url}/api/circuit?n_qubits=1000000")
        except HTTPError as error:
            assert error.code == 400
            assert "n_qubits" in json.load(error)["error"]
        else:
            raise AssertionError("invalid query unexpectedly succeeded")
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
