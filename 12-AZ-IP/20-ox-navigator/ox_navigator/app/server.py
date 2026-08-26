# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Standalone static and API server for the OX Navigator product."""

from __future__ import annotations

import asyncio
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ox_navigator.engine.client import OxApiKeyMissingError, OxClient
from ox_navigator.engine.constants import DEFAULT_TEMPERATURE, MODEL_ID
from ox_navigator.engine.session import OxSession

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
UI_ROOT = PRODUCT_ROOT / 'ui'
REPO_ROOT = PRODUCT_ROOT.parents[1]
CONTEXT_PACK = REPO_ROOT / '9-INFRASTRUCTURE' / 'ox_full_context.md'
SHORT_CONTEXT = (
    'Unitary Manifold v23.2. Respect HARDGATE / ADJACENT_TRACK / OPEN_GAP / '
    'ARCHITECTURE_LIMIT / GOVERNANCE boundaries. Provide steward caution when relevant.'
)
_SESSION = OxSession()


class OxRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_ROOT), **kwargs)

    def log_message(self, format, *args):  # noqa: A003
        return

    def _json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == '/api/ox/status':
            self._json({
                'ox_available': bool(os.environ.get('OPENROUTER_API_KEY')),
                'model': MODEL_ID,
                'context_pack_exists': CONTEXT_PACK.exists(),
                'api_base': 'local',
            })
            return
        if parsed.path in ('', '/'):
            self.path = '/ox-navigator.html'
        return super().do_GET()

    def do_POST(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != '/api/ox':
            self._json({'error': 'Not found'}, status=404)
            return
        length = int(self.headers.get('Content-Length', '0'))
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw or b'{}')
        except json.JSONDecodeError:
            self._json({'error': 'Invalid JSON body'}, status=400)
            return
        query = str(payload.get('query') or '').strip()
        if not query:
            self._json({'error': 'query is required'}, status=400)
            return
        use_full_context = bool(payload.get('use_full_context', True))
        temperature = float(payload.get('temperature', DEFAULT_TEMPERATURE))
        try:
            answer = asyncio.run(_run_ox_query(query, temperature, use_full_context))
        except OxApiKeyMissingError as exc:
            self._json({'error': str(exc), 'hint': 'Set OPENROUTER_API_KEY before using /api/ox.'}, status=503)
            return
        except Exception as exc:  # pragma: no cover
            self._json({'error': f'Unhandled OX error: {exc}'}, status=500)
            return
        self._json({
            'answer': answer,
            'model': MODEL_ID,
            'context_source': 'full_context_pack' if use_full_context and CONTEXT_PACK.exists() else 'embedded_context',
        })


async def _run_ox_query(query: str, temperature: float, use_full_context: bool) -> str:
    context = SHORT_CONTEXT
    if use_full_context and CONTEXT_PACK.exists():
        context = CONTEXT_PACK.read_text(encoding='utf-8')
    prompt = f"{context}\n\nUser query: {query}"
    client = OxClient()
    answer = await client.query(prompt=prompt, temperature=temperature, session=_SESSION)
    _SESSION.add_turn(query, answer)
    return answer


def serve(host: str = '127.0.0.1', port: int = 8020, no_open: bool = True) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), OxRequestHandler)
