# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_uos_kernel_bridge import (
    KKMessage,
    decode_kernel_message,
    decode_kernel_message_json,
    encode_kernel_message,
    parse_runtime_channel_pairs,
    validate_against_kk_channel_rs,
)
from az_uos_kernel_bridge.app.server import build_server


def test_message_round_trips_kernel_shaped_fields():
    message = KKMessage(from_ring=1, to_ring=2, payload=(1 << 64) - 1, seq=(1 << 32) - 1)
    encoded = encode_kernel_message(message)
    assert encoded == '{"from_ring":1,"payload":18446744073709551615,"seq":4294967295,"to_ring":2}'
    assert decode_kernel_message_json(encoded) == message


def test_message_schema_matches_real_rust_kkmessage_fields():
    source = (
        PRODUCT_ROOT.parents[0] / "02-az-kernel" / "src" / "ipc" / "kk_channel.rs"
    ).read_text(encoding="utf-8")
    assert "pub from_ring: usize" in source
    assert "pub to_ring: usize" in source
    assert "pub payload: u64" in source
    assert "pub seq: u32" in source


def test_runtime_channel_pairs_expose_wraparound_implementation_gap():
    result = validate_against_kk_channel_rs()
    assert result["matches"] is True
    assert result["runtime_matches_type_state"] is False
    assert result["type_state_only"] == [(0, 4), (4, 0)]
    assert result["runtime_pairs"] == sorted(parse_runtime_channel_pairs())


@pytest.mark.parametrize(
    "values",
    [
        {"from_ring": 0, "to_ring": 4, "payload": 1, "seq": 0},
        {"from_ring": True, "to_ring": 1, "payload": 1, "seq": 0},
        {"from_ring": 0, "to_ring": 1, "payload": -1, "seq": 0},
        {"from_ring": 0, "to_ring": 1, "payload": 1 << 64, "seq": 0},
        {"from_ring": 0, "to_ring": 1, "payload": 1, "seq": 1 << 32},
        {"from_ring": 0, "to_ring": 1, "payload": 1, "seq": 0, "extra": 1},
    ],
)
def test_message_rejects_non_interoperable_values(values):
    with pytest.raises(ValueError):
        decode_kernel_message(values)


def test_json_decoder_rejects_duplicate_fields_and_nan():
    with pytest.raises(ValueError, match="duplicate"):
        decode_kernel_message_json(
            '{"from_ring":0,"to_ring":1,"payload":1,"seq":0,"seq":1}'
        )
    with pytest.raises(ValueError):
        decode_kernel_message_json(
            '{"from_ring":0,"to_ring":1,"payload":NaN,"seq":0}'
        )


def test_live_post_endpoint_returns_field_compatible_json_record():
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        host, port = server.server_address
        request = urllib.request.Request(
            f"http://{host}:{port}/api/ipc-message",
            data=json.dumps(
                {"from_ring": 0, "to_ring": 1, "payload": 123, "seq": 7}
            ).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            result = json.load(response)
        assert result["kernel_message"] == {
            "from_ring": 0,
            "to_ring": 1,
            "payload": 123,
            "seq": 7,
        }
        assert result["json_adapter_record"] == (
            '{"from_ring":0,"payload":123,"seq":7,"to_ring":1}'
        )
        assert "not a kernel wire ABI" in result["transport_note"]

        invalid = urllib.request.Request(
            f"http://{host}:{port}/api/ipc-message",
            data=b'{"from_ring":0,"to_ring":4,"payload":123,"seq":7}',
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(invalid)
        assert error.value.code == 400
    finally:
        server.shutdown()
        thread.join()
        server.server_close()


@pytest.mark.parametrize("body", [
    b'{"from_ring":0,"to_ring":1,"payload":1,"seq":0,"seq":1}',
    b'{"from_ring":0,"to_ring":1,"payload":NaN,"seq":0}',
    b'{"from_ring":0,"to_ring":1,"payload":1,"seq":0,"extra":2}',
    b'{"from_ring":0,"to_ring":1,"payload":1,"seq":0}\xff',
])
def test_http_adapter_enforces_the_strict_json_contract(body):
    server = build_server(port=0)
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        host, port = server.server_address
        request = urllib.request.Request(
            f"http://{host}:{port}/api/ipc-message", data=body,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request, timeout=5)
        assert error.value.code == 400
        assert json.load(error.value)["error"]
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
