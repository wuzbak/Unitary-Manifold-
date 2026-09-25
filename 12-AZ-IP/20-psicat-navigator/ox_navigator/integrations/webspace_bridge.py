# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Repo/webspace bridge helpers for governed PsiCat investigation exchange."""

from __future__ import annotations

import hashlib
import hmac
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PRODUCT_ROOT.parents[1]
STATE_PATH = REPO_ROOT / '9-INFRASTRUCTURE' / 'psicat_state.json'
AXIOM_ROOT = REPO_ROOT / '12-AZ-IP' / '08-axiom-journalist'
if str(AXIOM_ROOT) not in sys.path:
    sys.path.insert(0, str(AXIOM_ROOT))

from axiom_journalist.engine import build_dossier_packet, build_psicat_training_packet


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _unauthorized() -> tuple[int, dict[str, Any]]:
    return 401, {'ok': False, 'error': 'Unauthorized webspace bridge request.'}


def verify_shared_secret(provided_secret: str, expected_secret: str) -> bool:
    left = str(provided_secret or '').encode('utf-8')
    right = str(expected_secret or '').encode('utf-8')
    return bool(left and right and hmac.compare_digest(left, right))


def load_psicat_state(path: Path = STATE_PATH) -> dict[str, Any]:
    if not path.exists():
        return {'updated_at': None, 'investigations': {}, 'latest_investigation_id': None}
    return json.loads(path.read_text(encoding='utf-8'))


def save_psicat_state(state: dict[str, Any], path: Path = STATE_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding='utf-8')
    return path


def receive_investigation(
    payload: dict[str, Any],
    *,
    provided_secret: str,
    expected_secret: str,
    path: Path = STATE_PATH,
) -> tuple[int, dict[str, Any]]:
    if not verify_shared_secret(provided_secret, expected_secret):
        return _unauthorized()
    investigation = dict(payload.get('investigation') or payload)
    investigation_id = str(
        investigation.get('id')
        or payload.get('investigation_id')
        or investigation.get('title')
        or 'unnamed-investigation'
    ).strip()
    state = load_psicat_state(path)
    state.setdefault('investigations', {})
    state['investigations'][investigation_id] = {
        'investigation': investigation,
        'received_at': _utcnow(),
        'source': 'base44-webspace',
    }
    state['latest_investigation_id'] = investigation_id
    state['updated_at'] = _utcnow()
    save_psicat_state(state, path)
    return 200, {'ok': True, 'investigation_id': investigation_id, 'state_path': str(path)}


def _investigation_from_state(state: dict[str, Any], investigation_id: str | None = None) -> tuple[str | None, dict[str, Any] | None]:
    investigations = state.get('investigations') if isinstance(state.get('investigations'), dict) else {}
    selected_id = investigation_id or state.get('latest_investigation_id')
    if not selected_id or selected_id not in investigations:
        return None, None
    row = investigations.get(selected_id) or {}
    if not isinstance(row, dict):
        return None, None
    investigation = row.get('investigation')
    return selected_id, dict(investigation) if isinstance(investigation, dict) else None


def send_dossier(
    *,
    provided_secret: str,
    expected_secret: str,
    investigation_id: str | None = None,
    path: Path = STATE_PATH,
) -> tuple[int, dict[str, Any]]:
    if not verify_shared_secret(provided_secret, expected_secret):
        return _unauthorized()
    state = load_psicat_state(path)
    selected_id, investigation = _investigation_from_state(state, investigation_id)
    if investigation is None or selected_id is None:
        return 404, {'ok': False, 'error': 'No stored investigation available for dossier generation.'}
    return 200, {'ok': True, 'investigation_id': selected_id, 'dossier': build_dossier_packet(investigation)}


def send_training_packet(
    *,
    provided_secret: str,
    expected_secret: str,
    investigation_id: str | None = None,
    path: Path = STATE_PATH,
) -> tuple[int, dict[str, Any]]:
    if not verify_shared_secret(provided_secret, expected_secret):
        return _unauthorized()
    state = load_psicat_state(path)
    selected_id, investigation = _investigation_from_state(state, investigation_id)
    if investigation is None or selected_id is None:
        return 404, {'ok': False, 'error': 'No stored investigation available for training packet generation.'}
    return 200, {'ok': True, 'investigation_id': selected_id, 'training_packet': build_psicat_training_packet(investigation)}


def handle_webspace_bridge_request(
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None,
    body: dict[str, Any] | None,
    expected_secret: str,
    state_path: Path = STATE_PATH,
) -> tuple[int, dict[str, Any]]:
    normalized_path = str(path or '').strip('/')
    request_headers = {str(key).lower(): str(value) for key, value in (headers or {}).items()}
    provided_secret = request_headers.get('x-psicat-shared-secret', '')
    if method.upper() == 'POST' and normalized_path.endswith('receive_investigation'):
        return receive_investigation(body or {}, provided_secret=provided_secret, expected_secret=expected_secret, path=state_path)
    if method.upper() == 'GET' and normalized_path.endswith('send_dossier'):
        investigation_id = request_headers.get('x-investigation-id') or None
        return send_dossier(provided_secret=provided_secret, expected_secret=expected_secret, investigation_id=investigation_id, path=state_path)
    if method.upper() == 'GET' and normalized_path.endswith('send_training_packet'):
        investigation_id = request_headers.get('x-investigation-id') or None
        return send_training_packet(provided_secret=provided_secret, expected_secret=expected_secret, investigation_id=investigation_id, path=state_path)
    return 404, {'ok': False, 'error': 'Unknown webspace bridge route.'}
