# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Async OpenRouter client for Merlin Navigator."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .constants import API_BASE, DEFAULT_TEMPERATURE, MODEL_ID
from .session import OxSession


class OxApiKeyMissingError(RuntimeError):
    """Raised when OPENROUTER_API_KEY is required but missing."""


class OxClient:
    """Minimal OpenRouter chat client for the stealth/ox-alpha model."""

    def __init__(self, api_key: str | None = None, model: str = MODEL_ID) -> None:
        resolved = api_key or os.environ.get('OPENROUTER_API_KEY', '')
        if not resolved:
            raise OxApiKeyMissingError('OPENROUTER_API_KEY is not set.')
        self.api_key = resolved
        self.model = model

    async def query(self, prompt: str, temperature: float = DEFAULT_TEMPERATURE, session: OxSession | None = None) -> str:
        session = session or OxSession()
        history = session.to_prompt_context()
        system_prompt = (
            'You are OX Alpha for the Unitary Manifold. '
            'Respect HARDGATE / ADJACENT_TRACK / OPEN_GAP / ARCHITECTURE_LIMIT / GOVERNANCE labels. '
            'Do not invent steward approval. Cite pillars when possible.'
        )
        payload: dict[str, Any] = {
            'model': self.model,
            'temperature': float(temperature),
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'system', 'content': history},
                {'role': 'user', 'content': prompt},
            ],
        }
        headers = {
            'Authorization': 'Bearer ' + self.api_key,
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8020',
            'X-Title': 'Merlin Navigator',
        }
        async with httpx.AsyncClient(base_url=API_BASE, timeout=60.0) as client:
            response = await client.post('/chat/completions', json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        choices = data.get('choices') or []
        if not choices:
            return ''
        message = choices[0].get('message', {})
        content = message.get('content', '')
        if isinstance(content, list):
            return ''.join(part.get('text', '') for part in content if isinstance(part, dict))
        return str(content)

    async def check_status(self) -> dict:
        headers = {'Authorization': 'Bearer ' + self.api_key}
        async with httpx.AsyncClient(base_url=API_BASE, timeout=30.0) as client:
            response = await client.get('/models', headers=headers)
            response.raise_for_status()
            data = response.json()
        available = any(item.get('id') == self.model for item in (data.get('data') or []))
        return {'ok': available, 'model': self.model, 'model_count': len(data.get('data') or [])}
