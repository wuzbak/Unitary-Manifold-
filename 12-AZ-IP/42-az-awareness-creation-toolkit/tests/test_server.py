# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Live HTTP contract tests for user-created knowledge decks."""

import json
from http.client import HTTPConnection
import sys
import threading
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_awareness_creation_toolkit.app.server import build_server


def _post(url, payload, content_type="application/json"):
    request = Request(
        url,
        data=payload if isinstance(payload, bytes) else json.dumps(payload).encode(),
        headers={"Content-Type": content_type},
        method="POST",
    )
    try:
        return urlopen(request)
    except HTTPError as error:
        return error


def test_live_server_creates_and_reviews_custom_deck():
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(f"{base_url}/") as response:
            page = response.read().decode()
        assert "Create a custom knowledge deck" in page
        assert 'id="deck-status"' in page
        assert "no cards due today" in page

        created_response = _post(
            f"{base_url}/api/cards/deck",
            {"cards": [{"question": "What is H2O?", "answer": "Water", "category": "chemistry"}]},
        )
        assert created_response.status == 200
        card = json.load(created_response)["deck"][0]
        reviewed_response = _post(
            f"{base_url}/api/cards/review",
            {"card": card, "quality": 4},
        )
        reviewed = json.load(reviewed_response)["card"]
        assert reviewed["repetitions"] == 1
        assert reviewed["due_date"] > card["due_date"]

        invalid_response = _post(f"{base_url}/api/cards/deck", {"cards": []})
        assert invalid_response.code == 400

        wrong_type = _post(f"{base_url}/api/cards/deck", b"{}", "text/plain")
        assert wrong_type.code == 400

        connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
        try:
            connection.request(
                "POST",
                "/api/cards/deck",
                headers={
                    "Content-Length": str(1024 * 1024 + 1),
                    "Content-Type": "application/json",
                },
            )
            assert connection.getresponse().status == 400
        finally:
            connection.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
