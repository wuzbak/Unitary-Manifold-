# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import json
import sys
import threading
from datetime import date
from pathlib import Path
from urllib.request import urlopen

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from falsification_observatory import (
    BIREFRINGENCE_PREDICTION,
    DESI_DR3_PREREGISTRATION,
    LITEBIRD_LAUNCH_YEAR,
    api_desi,
    api_litebird,
    assess_birefringence_measurement,
    check_desi_tension,
    days_to_litebird,
    dispatch_api_request,
    get_falsification_status,
)
from falsification_observatory.app.server import ObservatoryRequestHandler


def test_desi_preregistration_fields() -> None:
    assert DESI_DR3_PREREGISTRATION == {
        'preregistration_date': '2026-08-29',
        'w0_prediction': -1.0,
        'wa_prediction': 0.0,
        'pillar': 'P824',
        'status': 'PREREGISTERED',
    }


def test_litebird_launch_year_constant() -> None:
    assert LITEBIRD_LAUNCH_YEAR == 2032


def test_birefringence_prediction_shape() -> None:
    assert BIREFRINGENCE_PREDICTION['canonical'] == [0.273, 0.331]
    assert BIREFRINGENCE_PREDICTION['derived'] == [0.290, 0.351]


def test_birefringence_window_and_gap() -> None:
    assert BIREFRINGENCE_PREDICTION['admissible_window'] == [0.22, 0.38]
    assert BIREFRINGENCE_PREDICTION['falsification_gap'] == [0.29, 0.31]


def test_days_to_litebird_matches_calendar() -> None:
    expected = max(0, (date(2032, 1, 1) - date.today()).days)
    assert days_to_litebird() == expected


def test_desi_tension_zero_offset() -> None:
    result = check_desi_tension(-1.0, 0.0)
    assert result['tension_sigma'] == pytest.approx(0.0)
    assert result['consistent'] is True


def test_desi_tension_mild() -> None:
    result = check_desi_tension(-0.9, 0.1)
    assert 1.0 < result['tension_sigma'] < 1.5
    assert 'Consistent' in result['verdict'] or 'mild tension' in result['verdict']


def test_desi_tension_strong() -> None:
    result = check_desi_tension(-0.7, 0.4)
    assert result['tension_sigma'] == pytest.approx(5.0)
    assert result['consistent'] is False
    assert 'strong tension' in result['verdict']


def test_falsification_status_counts() -> None:
    status = get_falsification_status()
    assert status['total_claims'] == 7
    assert status['open_count'] == 7
    assert status['closed_count'] == 0


def test_falsification_status_contains_desi_preregistration() -> None:
    status = get_falsification_status()
    assert status['desi_dr3_preregistration']['pillar'] == 'P824'


@pytest.mark.parametrize(
    ('beta', 'falsifies'),
    [
        (0.273, False),
        (0.331, False),
        (0.21, True),
        (0.30, True),
        (0.39, True),
    ],
)
def test_birefringence_assessment_falsification(beta: float, falsifies: bool) -> None:
    assert assess_birefringence_measurement(beta)['falsifies'] is falsifies


def test_birefringence_assessment_gap_is_in_window() -> None:
    result = assess_birefringence_measurement(0.30)
    assert result['in_window'] is True
    assert result['in_gap'] is True


def test_birefringence_assessment_outside_window() -> None:
    result = assess_birefringence_measurement(0.40)
    assert result['in_window'] is False
    assert 'outside' in result['verdict']


def test_api_litebird_without_query() -> None:
    payload = api_litebird()
    assert payload['endpoint'] == '/api/litebird'
    assert payload['route']['verdict'] == 'AWAITING_DATA'


def test_api_litebird_with_measurement() -> None:
    payload = api_litebird({'beta': ['0.273'], 'beta_sigma': ['0.01']})
    assert payload['assessment']['falsifies'] is False
    assert payload['route']['verdict'] == 'PASS'


def test_api_desi_without_query() -> None:
    payload = api_desi()
    assert payload['endpoint'] == '/api/desi'
    assert payload['route']['verdict'] == 'AWAITING_DATA'


def test_api_desi_with_measurement() -> None:
    payload = api_desi({'w0': ['-1.0'], 'wa': ['0.0'], 'wa_sigma': ['0.1']})
    assert payload['assessment']['consistent'] is True
    assert payload['route']['verdict'] == 'PASS'


def test_dispatch_api_request_desi() -> None:
    payload = dispatch_api_request('/api/desi', {'w0': ['-0.7'], 'wa': ['0.4']})
    assert payload['endpoint'] == '/api/desi'
    assert payload['assessment']['consistent'] is False


def test_dispatch_api_request_litebird() -> None:
    payload = dispatch_api_request('/api/litebird', {'beta': ['0.30']})
    assert payload['endpoint'] == '/api/litebird'
    assert payload['assessment']['in_gap'] is True


def test_dispatch_api_request_bad_path() -> None:
    with pytest.raises(KeyError):
        dispatch_api_request('/api/missing', {})


def test_handler_class_exists() -> None:
    assert ObservatoryRequestHandler.__name__ == 'ObservatoryRequestHandler'


def test_server_exposes_litebird_endpoint() -> None:
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(('127.0.0.1', 0), ObservatoryRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        with urlopen(f'http://127.0.0.1:{port}/api/litebird?beta=0.273&beta_sigma=0.01', timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        assert data['route']['verdict'] == 'PASS'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_server_exposes_desi_endpoint() -> None:
    from http.server import ThreadingHTTPServer

    server = ThreadingHTTPServer(('127.0.0.1', 0), ObservatoryRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        port = server.server_address[1]
        with urlopen(f'http://127.0.0.1:{port}/api/desi?w0=-1.0&wa=0.0&wa_sigma=0.1', timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        assert data['assessment']['consistent'] is True
        assert data['route']['verdict'] == 'PASS'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_api_payloads_are_json_serializable() -> None:
    json.dumps(api_desi({'w0': ['-1.0'], 'wa': ['0.0']}), sort_keys=True)
    json.dumps(api_litebird({'beta': ['0.273']}), sort_keys=True)


def test_status_open_claim_names_include_litebird() -> None:
    names = {claim['name'] for claim in get_falsification_status()['open_claims']}
    assert 'LiteBIRD Cosmic Birefringence' in names


def test_status_closed_claims_empty_by_default() -> None:
    assert get_falsification_status()['closed_claims'] == []
