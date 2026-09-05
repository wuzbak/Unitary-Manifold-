# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Standalone static and API server for the Merlin Product 20 shell."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from ox_navigator.engine.constants import DEFAULT_TEMPERATURE, MODEL_ID
from ox_navigator.engine.merlin_benchmark import get_benchmark_corpus
from ox_navigator.engine.merlin_engine import query_merlin
from ox_navigator.engine.merlin_identity import get_identity_policy
from ox_navigator.engine.merlin_local_inference import get_inference_health, get_inference_providers
from ox_navigator.engine.merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MerlinSession
from ox_navigator.engine.merlin_memory_store import MerlinMemoryStore
from ox_navigator.engine.merlin_reasoning_graph import get_reasoning_chain
from ox_navigator.engine.merlin_runtime import get_client_blind_ingestion_contract, get_observatory_ingestion_lane
from ox_navigator.engine.merlin_research_cycle import run_research_cycle
from ox_navigator.engine.merlin_program import (
    build_training_artifact_bundle,
    build_training_dataset_bundle,
    get_mlflow_experiment_manifests,
    get_competitive_benchmark_plan,
    get_merlin_benchmark_suite,
    get_merlin_execution_graph,
    get_merlin_optimization_priorities,
    get_mythos_astra_contract,
    get_open_science_resource_registry,
    get_frontier_readiness_packet,
    get_full_program_blueprint,
    get_identity_and_trust_policy,
    get_training_architecture,
    get_program_office,
    get_sentinel_enforcement_policy,
    run_sync_checks,
)
from ox_navigator.engine.merlin_counterexample import build_counterexample_digest
from ox_navigator.engine.merlin_router import get_router_policy
from ox_navigator.engine.merlin_telemetry import build_energy_ledger
from ox_navigator.engine.merlin_tools import get_toolkit_view, orchestrate_steps, route_tool
from ox_navigator.engine.session import OxSession

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PRODUCT_ROOT / 'ui'
REPO_ROOT = PRODUCT_ROOT.parents[1]
CONTEXT_PACK = REPO_ROOT / '9-INFRASTRUCTURE' / 'ox_full_context.md'
_SESSION = OxSession()
_MERLIN_SESSIONS: dict[str, MerlinSession] = {}
_MERLIN_SESSION_LAST_SEEN: dict[str, float] = {}
_MERLIN_SESSIONS_LOCK = threading.Lock()
_MERLIN_SESSION_LOCKS: dict[str, threading.RLock] = {}
_MERLIN_SESSION_CAP = 128
_PROFILE_STORE = MerlinMemoryStore()
_HANDSHAKE_TTL_SECONDS = 300.0
_MERLIN_HANDSHAKE_STATE: dict[str, dict[str, float | str | bool]] = {}
_MERLIN_HANDSHAKE_LOCK = threading.Lock()
_MERLIN_SESSION_HANDSHAKE: dict[str, str] = {}
_MERLIN_GATE_LABELS = [
    "HARDGATE",
    "ADJACENT_TRACK",
    "OPEN_GAP",
    "ARCHITECTURE_LIMIT",
    "GOVERNANCE",
]
_MERLIN_SESSION_SECRET = (
    str(os.environ.get('MERLIN_SESSION_SECRET') or '').encode('utf-8')
    or uuid4().hex.encode('utf-8')
)
_MERLIN_PROFILE_SHARED_KEY = str(os.environ.get("MERLIN_PROFILE_SHARED_KEY") or "")


def _sign_session_id(session_id: str) -> str:
    signature = hmac.new(_MERLIN_SESSION_SECRET, session_id.encode('utf-8'), hashlib.sha256).hexdigest()
    return f'{session_id}.{signature}'


def _extract_session_id(token: str) -> str:
    session_id, _, signature = str(token or '').partition('.')
    if not session_id or not signature:
        return ''
    expected = hmac.new(_MERLIN_SESSION_SECRET, session_id.encode('utf-8'), hashlib.sha256).hexdigest()
    return session_id if hmac.compare_digest(signature, expected) else ''


def _profile_store_key(session_id: str) -> str:
    return hmac.new(_MERLIN_SESSION_SECRET, str(session_id).encode("utf-8"), hashlib.sha256).hexdigest()


def _parse_int_query_param(params: dict[str, list[str]], name: str, default: int) -> tuple[int | None, str | None]:
    raw = params.get(name, [str(default)])[0]
    try:
        return int(raw), None
    except (TypeError, ValueError):
        return None, f"Query parameter '{name}' must be an integer."


def _parse_positive_int_query_param(
    params: dict[str, list[str]],
    name: str,
    default: int,
) -> tuple[int | None, str | None]:
    value, error = _parse_int_query_param(params, name, default)
    if error:
        return None, error
    if value is None or value < 1:
        return None, f"Query parameter '{name}' must be >= 1."
    return value, None


def _tool_data_or_error(tool_payload: dict) -> tuple[int, dict]:
    if not tool_payload.get("ok"):
        return 500, {"ok": False, "error": tool_payload.get("error", "Merlin tool call failed.")}
    result = tool_payload.get("result")
    if not isinstance(result, dict) or "data" not in result:
        return 500, {"ok": False, "error": "Merlin tool returned no data payload."}
    return 200, {"ok": True, "data": result["data"]}


def _secure_cookie_required(host: str) -> bool:
    override = str(os.environ.get('MERLIN_COOKIE_SECURE') or '').strip().lower()
    if override in {'1', 'true', 'yes', 'on'}:
        return True
    if override in {'0', 'false', 'no', 'off'}:
        return False
    return host not in {'127.0.0.1', 'localhost'}


class OxRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    def log_message(self, format, *args):  # noqa: A003
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('X-Merlin-Session-Persistence', 'process_local_memory')
        pending_cookie = getattr(self, '_pending_session_cookie', '')
        if pending_cookie:
            host = str(self.headers.get('Host') or '').split(':', 1)[0]
            secure = '; Secure' if _secure_cookie_required(host) else ''
            self.send_header('Set-Cookie', f'merlin_profile_id={_sign_session_id(pending_cookie)}; Path=/; HttpOnly; SameSite=Lax{secure}')
        if getattr(self, '_session_state', ''):
            self.send_header('X-Merlin-Session-State', str(self._session_state))
        if getattr(self, '_handshake_state', ''):
            self.send_header('X-Merlin-Handshake-State', str(self._handshake_state))
        if getattr(self, '_handshake_challenge', ''):
            self.send_header('X-Merlin-Handshake-Challenge', str(self._handshake_challenge))
        if getattr(self, '_handshake_receipt', ''):
            self.send_header('X-Merlin-Handshake-Receipt', str(self._handshake_receipt))
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _issue_handshake_challenge(self, session_id: str) -> str:
        with _MERLIN_HANDSHAKE_LOCK:
            self._prune_handshake_state()
            active = _MERLIN_SESSION_HANDSHAKE.get(session_id, "")
            active_record = _MERLIN_HANDSHAKE_STATE.get(active, {})
            if isinstance(active_record, dict) and not bool(active_record.get("used")):
                issued_at = float(active_record.get("issued_at") or 0.0)
                if (time.time() - issued_at) <= _HANDSHAKE_TTL_SECONDS:
                    self._handshake_challenge = active
                    self._handshake_receipt = str(active_record.get("receipt") or "")
                    return active
            challenge = uuid4().hex
            _MERLIN_HANDSHAKE_STATE[challenge] = {
                "issued_at": time.time(),
                "used": False,
                "session_id": session_id,
                "receipt": hmac.new(
                    _MERLIN_SESSION_SECRET,
                    f"{challenge}:{session_id}".encode("utf-8"),
                    hashlib.sha256,
                ).hexdigest(),
            }
            _MERLIN_SESSION_HANDSHAKE[session_id] = challenge
        self._handshake_challenge = challenge
        self._handshake_receipt = str((_MERLIN_HANDSHAKE_STATE.get(challenge) or {}).get("receipt") or "")
        return challenge

    def _prune_handshake_state(self) -> None:
        now = time.time()
        stale = []
        for challenge, record in list(_MERLIN_HANDSHAKE_STATE.items()):
            if not isinstance(record, dict):
                stale.append(challenge)
                continue
            used = bool(record.get("used"))
            issued_at = float(record.get("issued_at") or 0.0)
            if used or (now - issued_at) > _HANDSHAKE_TTL_SECONDS:
                stale.append(challenge)
        for challenge in stale:
            record = _MERLIN_HANDSHAKE_STATE.pop(challenge, None)
            if isinstance(record, dict):
                session_id = str(record.get("session_id") or "")
                if _MERLIN_SESSION_HANDSHAKE.get(session_id) == challenge:
                    _MERLIN_SESSION_HANDSHAKE.pop(session_id, None)

    def _validate_handshake(
        self,
        *,
        session_id: str,
        payload: dict | None = None,
        params: dict | None = None,
        required: bool = False,
    ) -> tuple[bool, str]:
        with _MERLIN_HANDSHAKE_LOCK:
            self._prune_handshake_state()
            header_challenge = str(self.headers.get("X-Merlin-Handshake-Challenge") or "").strip()
            body_challenge = str((payload or {}).get("merlin_handshake_challenge") or "").strip()
            query_challenge = str((params or {}).get("merlin_handshake_challenge", [""])[0] or "").strip()
            challenge = body_challenge or header_challenge or query_challenge
            if not challenge:
                return (False, "missing_challenge") if required else (True, "absent")
            record = _MERLIN_HANDSHAKE_STATE.get(challenge)
            if not isinstance(record, dict):
                return False, "invalid"
            if str(record.get("session_id") or "") != str(session_id):
                return False, "session_mismatch"
            if bool(record.get("used")):
                return False, "replayed"
            issued_at = float(record.get("issued_at") or 0.0)
            if (time.time() - issued_at) > _HANDSHAKE_TTL_SECONDS:
                return False, "expired"
            header_proof = str(self.headers.get("X-Merlin-Handshake-Proof") or "").strip()
            header_receipt = str(self.headers.get("X-Merlin-Handshake-Receipt") or "").strip()
            body_proof = str((payload or {}).get("merlin_handshake_proof") or "").strip()
            body_receipt = str((payload or {}).get("merlin_handshake_receipt") or "").strip()
            query_proof = str((params or {}).get("merlin_handshake_proof", [""])[0] or "").strip()
            query_receipt = str((params or {}).get("merlin_handshake_receipt", [""])[0] or "").strip()
            proof = body_proof or header_proof or query_proof
            receipt = body_receipt or header_receipt or query_receipt
            token_query = str((params or {}).get("merlin_profile_token", [""])[0] or "").strip()
            token_header = str(self.headers.get("X-Merlin-Profile-Token") or "").strip()
            token_body = str((payload or {}).get("merlin_handshake_profile_token") or "").strip()
            if not token_body:
                token_body = str((payload or {}).get("memory_profile_token") or "").strip()
            profile_token = token_body or token_header or token_query
            if not proof:
                return False, "missing_proof"
            if not receipt:
                return False, "missing_receipt"
            if not profile_token:
                return False, "missing_profile_token"
            token_session_id = _extract_session_id(profile_token)
            if not token_session_id:
                return False, "invalid_profile_token"
            if token_session_id != str(session_id):
                return False, "profile_session_mismatch"
            expected_receipt = str(record.get("receipt") or "")
            if not expected_receipt or not hmac.compare_digest(receipt, expected_receipt):
                return False, "invalid_receipt"
            expected = hashlib.sha256(f"{challenge}:{profile_token}".encode("utf-8")).hexdigest()
            if not hmac.compare_digest(proof, expected):
                return False, "invalid_proof"
            record["used"] = True
            sid = str(record.get("session_id") or "")
            if _MERLIN_SESSION_HANDSHAKE.get(sid) == challenge:
                _MERLIN_SESSION_HANDSHAKE.pop(sid, None)
            return True, "verified"

    def _profile_hint(self, *, payload: dict | None = None, params: dict | None = None) -> str:
        query_profile = str((params or {}).get("merlin_profile_token", [""])[0] or "").strip()
        header_profile = str(self.headers.get("X-Merlin-Profile-Token") or "").strip()
        body_profile = str((payload or {}).get("memory_profile_token") or "").strip()
        token = body_profile or header_profile or query_profile
        self._profile_token_state = 'none'
        if not token:
            return ""
        key_query = str((params or {}).get("memory_profile_key", [""])[0] or "").strip()
        key_header = str(self.headers.get("X-Merlin-Profile-Key") or "").strip()
        key_body = str((payload or {}).get("memory_profile_key") or "").strip()
        provided_key = key_body or key_header or key_query
        expected_key = str(_MERLIN_PROFILE_SHARED_KEY).strip()
        if not expected_key:
            self._profile_token_state = 'shared_key_not_configured'
            return ""
        if not provided_key:
            self._profile_token_state = 'missing_shared_key'
            return ""
        if not hmac.compare_digest(provided_key, expected_key):
            self._profile_token_state = 'invalid_shared_key'
            return ""
        extracted = _extract_session_id(token)
        self._profile_token_state = 'verified' if extracted else 'invalid_token_signature'
        return extracted

    def _merlin_session(self, *, profile_hint: str = "") -> tuple[str, MerlinSession, threading.RLock]:
        candidate_id = str(profile_hint or "").strip()
        raw_cookie = str(self.headers.get('Cookie') or '')
        for part in raw_cookie.split(';'):
            key, _, value = part.strip().partition('=')
            if key == 'merlin_profile_id' and value.strip():
                candidate_id = candidate_id or _extract_session_id(value.strip())
                break
        self._session_state = ''
        with _MERLIN_SESSIONS_LOCK:
            session_id = candidate_id or uuid4().hex
            if candidate_id and not _PROFILE_STORE.has_profile(_profile_store_key(candidate_id)):
                session_id = uuid4().hex
            if session_id not in _MERLIN_SESSIONS:
                _MERLIN_SESSIONS[session_id] = _PROFILE_STORE.load_profile(_profile_store_key(session_id))
                _MERLIN_SESSION_LOCKS[session_id] = threading.RLock()
                self._session_state = 'new_session' if not candidate_id else 'expired_new_session'
            else:
                self._session_state = 'resumed_session'
            if session_id not in _MERLIN_SESSION_LOCKS:
                _MERLIN_SESSION_LOCKS[session_id] = threading.RLock()
            self._pending_session_cookie = session_id
            _MERLIN_SESSION_LAST_SEEN[session_id] = time.time()
            while len(_MERLIN_SESSIONS) > _MERLIN_SESSION_CAP:
                stale_candidates = [key for key in _MERLIN_SESSION_LAST_SEEN if key != session_id]
                if not stale_candidates:
                    break
                stale_id = min(stale_candidates, key=_MERLIN_SESSION_LAST_SEEN.get)
                stale_session = _MERLIN_SESSIONS.get(stale_id)
                if stale_session is not None:
                    _PROFILE_STORE.save_profile(_profile_store_key(stale_id), stale_session)
                _MERLIN_SESSIONS.pop(stale_id, None)
                _MERLIN_SESSION_LAST_SEEN.pop(stale_id, None)
                _MERLIN_SESSION_LOCKS.pop(stale_id, None)
            return session_id, _MERLIN_SESSIONS[session_id], _MERLIN_SESSION_LOCKS[session_id]

    def _persist_session(self, session_id: str, session: MerlinSession) -> None:
        _PROFILE_STORE.save_profile(_profile_store_key(session_id), session)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        profile_hint = self._profile_hint(params=params)
        session_id, merlin_session, merlin_lock = self._merlin_session(profile_hint=profile_hint)
        self._handshake_state = "not_issued"
        if parsed.path.startswith('/api/merlin') or parsed.path.startswith('/api/ox'):
            self._issue_handshake_challenge(session_id)
            self._handshake_state = "challenge_issued"
        with merlin_lock:
            if parsed.path == '/api/merlin/status':
                self._json({
                'service': 'Merlin — the Quantum Cat',
                'merlin_available': True,
                'live_model_available': bool(os.environ.get('OPENROUTER_API_KEY')),
                'openrouter_compat_enabled': bool(os.environ.get('MERLIN_ENABLE_OPENROUTER_COMPAT')),
                'model': MODEL_ID,
                'context_pack_exists': CONTEXT_PACK.exists(),
                'active_session_key': MERLIN_ACTIVE_SESSION_KEY,
                'memory_profile_token': _sign_session_id(session_id),
                'profile_resume_requires_key': bool(_MERLIN_PROFILE_SHARED_KEY),
                'capability_views': ['index', 'domain', 'tool', 'full', 'state'],
                'router_policy': get_router_policy(),
                'live_status': route_tool('fetchRepoContext').get('result', {}).get('data', {}),
                'memory': merlin_session.get_public_memory_state(),
                'telemetry': merlin_session.get_telemetry_summary(public=True),
                'compatibility': {
                    'legacy_query_endpoint': '/api/ox',
                    'legacy_status_endpoint': '/api/ox/status',
                },
                'session_contract': {
                    'persistence': 'process_local_memory',
                    'signed_cookie_resume_scope': 'same_process_only',
                    'expired_cookie_behavior': 'new_session_id_issued',
                    'client_blind_ingestion_contract': get_client_blind_ingestion_contract(),
                    'handshake': {
                        'state': self._handshake_state,
                        'challenge': self._handshake_challenge,
                        'receipt': self._handshake_receipt,
                        'challenge_ttl_seconds': _HANDSHAKE_TTL_SECONDS,
                        'proof_hash': 'sha256(challenge:memory_profile_token)',
                        'invalid_or_replayed_behavior': 'request_refused',
                    },
                },
                'observatory_ingestion_lane': get_observatory_ingestion_lane(),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/program':
                self._json({'ok': True, 'program': get_full_program_blueprint()})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/program-office':
                self._json({'ok': True, 'program_office': get_program_office()})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/control-tower':
                raw_limit = params.get('limit', ['3'])[0]
                try:
                    limit = max(1, int(raw_limit))
                except (TypeError, ValueError):
                    limit = 3
                raw_history = params.get('gate_history', [''])[0]
                gate_history = None
                if str(raw_history).strip():
                    try:
                        parsed_history = json.loads(str(raw_history))
                    except (TypeError, ValueError, json.JSONDecodeError):
                        self._json({'ok': False, 'error': "Query parameter 'gate_history' must be valid JSON."}, status=400)
                        return
                    if not isinstance(parsed_history, list):
                        self._json({'ok': False, 'error': "Query parameter 'gate_history' must decode to a JSON array."}, status=400)
                        return
                    gate_history = parsed_history
                status, payload = _tool_data_or_error(route_tool(
                    'getMerlinControlTower',
                    {'limit': limit, 'gate_history': gate_history} if gate_history is not None else {'limit': limit},
                    session=merlin_session,
                ))
                self._json({'ok': payload['ok'], 'control_tower': payload.get('data'), 'error': payload.get('error')}, status=status)
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/memory':
                self._json({'ok': True, 'memory': merlin_session.get_public_memory_state()})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/telemetry':
                self._json({'ok': True, 'telemetry': merlin_session.get_telemetry_summary(public=True)})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/inference/providers':
                self._json({'ok': True, 'providers': get_inference_providers()})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/inference/health':
                provider = str(params.get('provider', [''])[0] or '').strip() or None
                payload = get_inference_health(provider_name=provider)
                self._json(payload, status=200 if payload.get('ok') else 404)
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/reasoning-chain':
                query = str(params.get('query', [''])[0] or '').strip()
                if not query:
                    self._json({'ok': False, 'error': "Query parameter 'query' is required."}, status=400)
                    return
                max_hops, error = _parse_positive_int_query_param(params, 'max_hops', 3)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                self._json({'ok': True, 'reasoning_chain': get_reasoning_chain(query, max_hops=max_hops)})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/counterexample-digest':
                limit, error = _parse_positive_int_query_param(params, 'limit', 10)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                self._json({'ok': True, 'counterexample_digest': build_counterexample_digest(session=merlin_session, limit=limit)})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/energy-ledger':
                limit, error = _parse_positive_int_query_param(params, 'limit', 10)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                self._json({'ok': True, 'energy_ledger': build_energy_ledger(merlin_session.telemetry, limit=limit)})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/runtime':
                self._json({
                'ok': True,
                'runtime': {
                    'mythos_astra_contract': get_mythos_astra_contract(),
                    'optimization_priorities': get_merlin_optimization_priorities(),
                    'execution_graph': get_merlin_execution_graph(),
                    'client_blind_ingestion_contract': get_client_blind_ingestion_contract(),
                    'observatory_ingestion_lane': get_observatory_ingestion_lane(),
                    'inference_health': get_inference_health(),
                },
                })
                return
            if parsed.path == '/api/merlin/benchmarks':
                self._json({
                'ok': True,
                'benchmarks': get_merlin_benchmark_suite(),
                'telemetry': merlin_session.get_telemetry_summary(public=True),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/training-architecture':
                limit, error = _parse_int_query_param(params, 'limit', 12)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                self._json({
                'ok': True,
                'training_architecture': get_training_architecture(limit=limit),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/training-dataset':
                limit, error = _parse_int_query_param(params, 'limit', 12)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                compiled = merlin_session.get_compiled_training_insights()
                self._json(build_training_dataset_bundle(limit=limit, compiled_insights=compiled))
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/open-science-registry':
                self._json({
                'ok': True,
                'open_science_registry': get_open_science_resource_registry(),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/mlflow-manifests':
                limit, error = _parse_int_query_param(params, 'limit', 12)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                payload = get_mlflow_experiment_manifests(
                    limit=limit,
                    compiled_insights=merlin_session.get_compiled_training_insights(),
                )
                if payload.get('ok') is False:
                    self._json({'ok': False, 'error': payload.get('error', 'Unable to build MLflow manifests.')}, status=500)
                    self._persist_session(session_id, merlin_session)
                    return
                self._json({
                'ok': True,
                'mlflow_manifests': payload,
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/competitive-benchmarks':
                self._json({
                'ok': True,
                'competitive_benchmarks': get_competitive_benchmark_plan(),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/benchmark-corpora':
                stages = params.get('stage', [])
                if len(stages) > 1:
                    self._json({'ok': False, 'error': "Query parameter 'stage' must not be repeated."}, status=400)
                    self._persist_session(session_id, merlin_session)
                    return
                payload = get_benchmark_corpus(stage=str(stages[0] if stages else 'all'))
                if payload.get('ok') is False:
                    self._json({'ok': False, 'error': payload.get('error'), 'allowed_stages': payload.get('allowed_stages', [])}, status=400)
                    self._persist_session(session_id, merlin_session)
                    return
                self._json({
                'ok': True,
                'benchmark_corpora': payload,
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/stage-a-receipts':
                limit, error = _parse_int_query_param(params, 'limit', 3)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                status, payload = _tool_data_or_error(route_tool(
                    'runMerlinStageAReceipts',
                    {'limit': limit},
                    session=merlin_session,
                ))
                self._json({'ok': payload['ok'], 'receipts': payload.get('data'), 'error': payload.get('error')}, status=status)
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/replacement-readiness':
                limit, error = _parse_int_query_param(params, 'limit', 3)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                status, payload = _tool_data_or_error(route_tool(
                    'getMerlinReplacementReadiness',
                    {'limit': limit},
                    session=merlin_session,
                ))
                self._json({'ok': payload['ok'], 'readiness': payload.get('data'), 'error': payload.get('error')}, status=status)
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/frontier-readiness':
                limit, error = _parse_int_query_param(params, 'limit', 3)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                self._json({
                'ok': True,
                'frontier_readiness': get_frontier_readiness_packet(limit=limit),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/benchmark-artifacts':
                limit, error = _parse_int_query_param(params, 'limit', 3)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                status, payload = _tool_data_or_error(route_tool(
                    'getMerlinStageAArtifacts',
                    {'limit': limit},
                    session=merlin_session,
                ))
                if status != 200:
                    self._json({'ok': payload['ok'], 'error': payload.get('error')}, status=status)
                    self._persist_session(session_id, merlin_session)
                    return
                artifacts_payload = dict(payload.get('data') or {})
                self._json({
                'ok': bool(artifacts_payload.get('ok', True)),
                'artifacts': artifacts_payload.get('artifact_bundle', {}),
                }, status=status)
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/training-artifacts':
                limit, error = _parse_int_query_param(params, 'limit', 12)
                if error:
                    self._json({'ok': False, 'error': error}, status=400)
                    return
                payload = build_training_artifact_bundle(
                    limit=limit,
                    compiled_insights=merlin_session.get_compiled_training_insights(),
                )
                if not payload.get('ok'):
                    self._json({'ok': False, 'error': payload.get('error', 'Unable to build training artifacts.')}, status=500)
                    self._persist_session(session_id, merlin_session)
                    return
                self._json({
                'ok': bool(payload.get('ok')),
                'training_artifacts': payload.get('artifact_bundle', {}),
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/promotion-packet':
                status, payload = _tool_data_or_error(route_tool(
                    'getMerlinPromotionPacket',
                    {},
                    session=merlin_session,
                ))
                if status != 200:
                    self._json({'ok': payload['ok'], 'packet': {}, 'error': payload.get('error')}, status=status)
                    return
                self._json({
                'ok': True,
                'packet': payload['data'],
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/identity':
                self._json({'ok': True, 'identity': get_identity_policy()})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/policy':
                self._json({
                'ok': True,
                'policy': {
                    'identity_trust': get_identity_and_trust_policy(),
                    'sentinel': get_sentinel_enforcement_policy(),
                },
                })
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/merlin/sync-checks':
                self._json({'ok': True, 'sync_checks': run_sync_checks()})
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/agentToolkit':
                self._json(get_toolkit_view(
                view=str(params.get('view', ['index'])[0]),
                domain=str(params.get('domain', [''])[0] or '') or None,
                tool=str(params.get('tool', [''])[0] or '') or None,
                ))
                self._persist_session(session_id, merlin_session)
                return
            if parsed.path == '/api/ox/status':
                self._json({
                'ox_available': bool(os.environ.get('OPENROUTER_API_KEY')),
                'model': MODEL_ID,
                'context_pack_exists': CONTEXT_PACK.exists(),
                'api_base': 'local',
                'merlin_available': True,
                'service': 'Compatibility shim over Merlin Product 20',
                'openrouter_compat_enabled': bool(os.environ.get('MERLIN_ENABLE_OPENROUTER_COMPAT')),
                'session_contract': {
                    'persistence': 'process_local_memory',
                    'signed_cookie_resume_scope': 'same_process_only',
                    'expired_cookie_behavior': 'new_session_id_issued',
                    'client_blind_ingestion_contract': get_client_blind_ingestion_contract(),
                },
                })
                self._persist_session(session_id, merlin_session)
                return
        if parsed.path in ('', '/'):
            self.path = '/ox-navigator.html'
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw or b'{}')
        except json.JSONDecodeError:
            self._json({'error': 'Invalid JSON body'}, status=400)
            return
        profile_hint = self._profile_hint(payload=payload, params=params)
        if parsed.path in ('/api/merlin', '/api/ox') and str(getattr(self, '_profile_token_state', '')) in {'invalid_token_signature', 'invalid_shared_key', 'shared_key_not_configured'}:
            self._handshake_state = "not_checked"
            self._json({
                'ok': False,
                'error': 'Invalid profile resume token.',
                'profile_token_state': self._profile_token_state,
            }, status=401)
            return
        session_id, merlin_session, merlin_lock = self._merlin_session(profile_hint=profile_hint)
        handshake_material_present = any([
            str(self.headers.get("X-Merlin-Handshake-Challenge") or "").strip(),
            str(self.headers.get("X-Merlin-Handshake-Proof") or "").strip(),
            str(self.headers.get("X-Merlin-Handshake-Receipt") or "").strip(),
            str((payload or {}).get("merlin_handshake_challenge") or "").strip(),
            str((payload or {}).get("merlin_handshake_proof") or "").strip(),
            str((payload or {}).get("merlin_handshake_receipt") or "").strip(),
            str(params.get("merlin_handshake_challenge", [""])[0] or "").strip(),
            str(params.get("merlin_handshake_proof", [""])[0] or "").strip(),
            str(params.get("merlin_handshake_receipt", [""])[0] or "").strip(),
        ])
        requires_handshake = parsed.path in ('/api/merlin', '/api/ox')
        if requires_handshake:
            handshake_ok, handshake_state = self._validate_handshake(
                session_id=session_id,
                payload=payload,
                params=params,
                required=True,
            )
        else:
            handshake_ok, handshake_state = True, "not_required"
        self._handshake_state = handshake_state

        with merlin_lock:
            try:
                if not handshake_ok:
                    if requires_handshake and handshake_state == "missing_challenge":
                        self._issue_handshake_challenge(session_id)
                    self._json({
                        'ok': False,
                        'error': 'Client-blind handshake verification failed.',
                        'handshake_state': handshake_state,
                        'handshake_required': requires_handshake,
                        'handshake_material_present': bool(handshake_material_present),
                    }, status=401)
                    return
                if requires_handshake:
                    self._issue_handshake_challenge(session_id)
                if parsed.path == '/api/agentInvoke':
                    tool = str(payload.get('tool') or '').strip()
                    if not tool:
                        self._json({'error': 'tool is required'}, status=400)
                        return
                    self._json(route_tool(tool, dict(payload.get('args') or {}), session=merlin_session))
                    return

                if parsed.path == '/api/agentOrchestrate':
                    steps = list(payload.get('steps') or [])
                    try:
                        self._json(orchestrate_steps(steps, session=merlin_session))
                    except ValueError as exc:
                        self._json({'ok': False, 'error': str(exc)}, status=400)
                    return

                if parsed.path in ('/api/merlin', '/api/ox'):
                    query = str(payload.get('query') or '').strip()
                    if not query:
                        self._json({'error': 'query is required'}, status=400)
                        return
                    temperature = float(payload.get('temperature', DEFAULT_TEMPERATURE))
                    fourth_wall = bool(payload.get('fourth_wall', False))
                    page_context = str(payload.get('page_context') or '')
                    user_context = str(payload.get('user_context') or '')
                    try:
                        result = asyncio.run(query_merlin(
                            text=query,
                            session=merlin_session,
                            on_status=[],
                            model_override=str(payload.get('model') or '') or None,
                            fourth_wall=fourth_wall,
                            page_context=page_context,
                            user_context=user_context,
                            system_override=str(payload.get('system') or ''),
                            force_websearch=payload.get('websearch'),
                            temperature=temperature,
                        ))
                    except Exception as exc:  # pragma: no cover
                        self._json({'error': f'Unhandled Merlin error: {exc}'}, status=500)
                        return

                    if parsed.path == '/api/ox':
                        self._json({
                            'answer': result['answer'],
                            'model': MODEL_ID,
                            'epistemic_note': result['epistemic_note'],
                            'context_source': result['context_source'],
                            'governance_note': (
                                'AI-generated suggestion — steward approval required for any hardgate claim, '
                                'pillar numbering, or Lean4 theorem acceptance.'
                            ),
                            'persona_mode': result['persona_mode'],
                            'gate_badges': result['gate_badges'],
                        })
                        return

                    self._json(result)
                    return
                if parsed.path == '/api/merlin/research-cycle':
                    question = str(payload.get('question') or payload.get('query') or '').strip()
                    if not question:
                        self._json({'ok': False, 'error': 'question is required'}, status=400)
                        return
                    try:
                        budget = int(payload.get('budget', 3))
                    except (TypeError, ValueError):
                        self._json({'ok': False, 'error': 'budget must be an integer'}, status=400)
                        return
                    if budget < 1:
                        self._json({'ok': False, 'error': 'budget must be >= 1'}, status=400)
                        return
                    result = run_research_cycle(
                        question=question,
                        budget=budget,
                        session=merlin_session,
                    )
                    status = 200
                    if not result.get('ok'):
                        if ((result.get('sentinel') or {}).get('blocked')):
                            status = 403
                        else:
                            status = 400
                    self._json({
                        'ok': bool(result.get('ok')),
                        'research_cycle': result,
                    }, status=status)
                    return
            finally:
                self._persist_session(session_id, merlin_session)
        self._json({'error': 'Not found'}, status=404)


def serve(host: str = '127.0.0.1', port: int = 8020, no_open: bool = True) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), OxRequestHandler)
