# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Standalone static and API server for the Merlin Product 20 shell."""

from __future__ import annotations

import asyncio
import json
import os
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from ox_navigator.engine.constants import DEFAULT_TEMPERATURE, MODEL_ID
from ox_navigator.engine.merlin_engine import query_merlin
from ox_navigator.engine.merlin_identity import get_identity_policy
from ox_navigator.engine.merlin_memory import MERLIN_ACTIVE_SESSION_KEY, MerlinSession
from ox_navigator.engine.merlin_program import (
    get_merlin_benchmark_suite,
    get_merlin_execution_graph,
    get_merlin_optimization_priorities,
    get_mythos_astra_contract,
    get_full_program_blueprint,
    get_identity_and_trust_policy,
    get_sentinel_enforcement_policy,
    run_sync_checks,
)
from ox_navigator.engine.merlin_router import get_router_policy
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
_MERLIN_SESSION_CAP = 128


class OxRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    def log_message(self, format, *args):  # noqa: A003
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        pending_cookie = getattr(self, '_pending_session_cookie', '')
        if pending_cookie:
            self.send_header('Set-Cookie', f'merlin_session_id={pending_cookie}; Path=/; HttpOnly; SameSite=Lax')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _merlin_session(self) -> MerlinSession:
        candidate_id = ""
        raw_cookie = str(self.headers.get('Cookie') or '')
        for part in raw_cookie.split(';'):
            key, _, value = part.strip().partition('=')
            if key == 'merlin_session_id' and value.strip():
                candidate_id = value.strip()
                break
        with _MERLIN_SESSIONS_LOCK:
            session_id = candidate_id if candidate_id in _MERLIN_SESSIONS else ''
            if not session_id:
                session_id = uuid4().hex
                _MERLIN_SESSIONS[session_id] = MerlinSession()
                self._pending_session_cookie = session_id
            _MERLIN_SESSION_LAST_SEEN[session_id] = time.time()
            while len(_MERLIN_SESSIONS) > _MERLIN_SESSION_CAP:
                stale_candidates = [key for key in _MERLIN_SESSION_LAST_SEEN if key != session_id]
                if not stale_candidates:
                    break
                stale_id = min(stale_candidates, key=_MERLIN_SESSION_LAST_SEEN.get)
                _MERLIN_SESSIONS.pop(stale_id, None)
                _MERLIN_SESSION_LAST_SEEN.pop(stale_id, None)
            return _MERLIN_SESSIONS[session_id]

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        merlin_session = self._merlin_session()
        if parsed.path == '/api/merlin/status':
            self._json({
                'service': 'Merlin — the Quantum Cat',
                'merlin_available': True,
                'live_model_available': bool(os.environ.get('OPENROUTER_API_KEY')),
                'openrouter_compat_enabled': bool(os.environ.get('MERLIN_ENABLE_OPENROUTER_COMPAT')),
                'model': MODEL_ID,
                'context_pack_exists': CONTEXT_PACK.exists(),
                'active_session_key': MERLIN_ACTIVE_SESSION_KEY,
                'capability_views': ['index', 'domain', 'tool', 'full', 'state'],
                'router_policy': get_router_policy(),
                'live_status': route_tool('fetchRepoContext').get('result', {}).get('data', {}),
                'memory': merlin_session.get_public_memory_state(),
                'telemetry': merlin_session.get_telemetry_summary(public=True),
                'compatibility': {
                    'legacy_query_endpoint': '/api/ox',
                    'legacy_status_endpoint': '/api/ox/status',
                },
            })
            return
        if parsed.path == '/api/merlin/program':
            self._json({'ok': True, 'program': get_full_program_blueprint()})
            return
        if parsed.path == '/api/merlin/memory':
            self._json({'ok': True, 'memory': merlin_session.get_public_memory_state()})
            return
        if parsed.path == '/api/merlin/telemetry':
            self._json({'ok': True, 'telemetry': merlin_session.get_telemetry_summary(public=True)})
            return
        if parsed.path == '/api/merlin/runtime':
            self._json({
                'ok': True,
                'runtime': {
                    'mythos_astra_contract': get_mythos_astra_contract(),
                    'optimization_priorities': get_merlin_optimization_priorities(),
                    'execution_graph': get_merlin_execution_graph(),
                },
            })
            return
        if parsed.path == '/api/merlin/benchmarks':
            self._json({
                'ok': True,
                'benchmarks': get_merlin_benchmark_suite(),
                'telemetry': merlin_session.get_telemetry_summary(public=True),
            })
            return
        if parsed.path == '/api/merlin/identity':
            self._json({'ok': True, 'identity': get_identity_policy()})
            return
        if parsed.path == '/api/merlin/policy':
            self._json({
                'ok': True,
                'policy': {
                    'identity_trust': get_identity_and_trust_policy(),
                    'sentinel': get_sentinel_enforcement_policy(),
                },
            })
            return
        if parsed.path == '/api/merlin/sync-checks':
            self._json({'ok': True, 'sync_checks': run_sync_checks()})
            return
        if parsed.path == '/api/agentToolkit':
            self._json(get_toolkit_view(
                view=str(params.get('view', ['index'])[0]),
                domain=str(params.get('domain', [''])[0] or '') or None,
                tool=str(params.get('tool', [''])[0] or '') or None,
            ))
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
            })
            return
        if parsed.path in ('', '/'):
            self.path = '/ox-navigator.html'
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        merlin_session = self._merlin_session()
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw or b'{}')
        except json.JSONDecodeError:
            self._json({'error': 'Invalid JSON body'}, status=400)
            return

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
        self._json({'error': 'Not found'}, status=404)


def serve(host: str = '127.0.0.1', port: int = 8020, no_open: bool = True) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), OxRequestHandler)
