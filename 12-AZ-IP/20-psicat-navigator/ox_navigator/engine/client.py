# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Async OpenRouter client for PsiCat Navigator."""

from __future__ import annotations

import os
from typing import Any

import httpx

from .constants import API_BASE, DEFAULT_TEMPERATURE, MODEL_ID
from .session import OxSession


class OxApiKeyMissingError(RuntimeError):
    """Raised when OPENROUTER_API_KEY is required but missing."""


LOCAL_BACKEND_DEFAULT_BASES = {
    'vllm': 'http://127.0.0.1:8000/v1',
    'sglang': 'http://127.0.0.1:30000/v1',
    'flashinfer': 'http://127.0.0.1:8010',
}


class OxClient:
    """Minimal OpenRouter chat client for the stealth/ox-alpha model."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = MODEL_ID,
        backend: str | None = None,
        endpoint: str | None = None,
    ) -> None:
        runtime_backend = (backend or os.environ.get('MERLIN_RUNTIME_BACKEND', 'openrouter')).strip().lower()
        if runtime_backend not in {'openrouter', 'vllm', 'sglang', 'flashinfer'}:
            runtime_backend = 'openrouter'
        self.backend = runtime_backend
        self.model = model
        self.base_url = endpoint or os.environ.get('MERLIN_RUNTIME_ENDPOINT', '')
        if not self.base_url:
            if self.backend == 'openrouter':
                self.base_url = API_BASE
            else:
                self.base_url = LOCAL_BACKEND_DEFAULT_BASES[self.backend]

        resolved = api_key or os.environ.get('OPENROUTER_API_KEY', '')
        if self.backend == 'openrouter' and not resolved:
            raise OxApiKeyMissingError('OPENROUTER_API_KEY is not set.')
        self.api_key = resolved

    async def query(self, prompt: str, temperature: float = DEFAULT_TEMPERATURE, session: OxSession | None = None) -> str:
        if self.backend == 'openrouter':
            return await self._query_openrouter(prompt=prompt, temperature=temperature, session=session)
        return await self._query_local_runtime(prompt=prompt, temperature=temperature, session=session)

    async def _query_openrouter(self, prompt: str, temperature: float = DEFAULT_TEMPERATURE, session: OxSession | None = None) -> str:
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
            'X-Title': 'PsiCat Navigator',
        }
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            response = await client.post('/chat/completions', json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return self._extract_text_content(data)

    async def _query_local_runtime(self, prompt: str, temperature: float = DEFAULT_TEMPERATURE, session: OxSession | None = None) -> str:
        session = session or OxSession()
        compact_prompt = (
            "System: You are OX Alpha for the Unitary Manifold.\n"
            "Rules: Respect HARDGATE / ADJACENT_TRACK / OPEN_GAP / ARCHITECTURE_LIMIT / GOVERNANCE labels.\n"
            f"Context:\n{session.to_prompt_context()}\n"
            f"User:\n{prompt}\n"
            "Assistant:"
        )
        timeout = float(os.environ.get('MERLIN_RUNTIME_TIMEOUT_SECONDS', '60') or '60')
        headers = {'Content-Type': 'application/json'}
        if self.api_key:
            headers['Authorization'] = 'Bearer ' + self.api_key
        async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
            fp8_enabled = str(os.environ.get('MERLIN_RUNTIME_ENABLE_FP8', '1')).strip().lower() not in {'0', 'false', 'no'}
            if self.backend == 'flashinfer':
                payload = {
                    'prompt': compact_prompt,
                    'temperature': float(temperature),
                    'max_new_tokens': int(os.environ.get('MERLIN_RUNTIME_MAX_NEW_TOKENS', '512')),
                    'model': self.model,
                    'dtype': 'fp8' if fp8_enabled else 'bf16',
                }
                response = await client.post('/generate', json=payload, headers=headers)
            else:
                payload = {
                    'model': self.model,
                    'temperature': float(temperature),
                    'messages': [{'role': 'user', 'content': compact_prompt}],
                    'extra_body': {'dtype': 'fp8'} if fp8_enabled else {},
                }
                response = await client.post('/chat/completions', json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return self._extract_text_content(data)

    @staticmethod
    def _extract_text_content(data: dict[str, Any]) -> str:
        choices = data.get('choices') or []
        if choices:
            message = choices[0].get('message', {})
            content = message.get('content', '')
            if isinstance(content, list):
                return ''.join(part.get('text', '') for part in content if isinstance(part, dict))
            return str(content)
        for key in ('text', 'output_text', 'response'):
            value = data.get(key)
            if isinstance(value, str):
                return value
        if isinstance(data.get('outputs'), list) and data['outputs']:
            first = data['outputs'][0]
            if isinstance(first, dict) and isinstance(first.get('text'), str):
                return first.get('text', '')
        return ''

    async def check_status(self) -> dict:
        headers = {'Authorization': 'Bearer ' + self.api_key} if self.api_key else {}
        timeout = float(os.environ.get('MERLIN_RUNTIME_TIMEOUT_SECONDS', '30') or '30')
        async with httpx.AsyncClient(base_url=self.base_url, timeout=timeout) as client:
            if self.backend == 'flashinfer':
                response = await client.get('/health', headers=headers)
                response.raise_for_status()
                return {'ok': True, 'model': self.model, 'backend': self.backend}
            response = await client.get('/models', headers=headers)
            response.raise_for_status()
            data = response.json()
        available = any(item.get('id') == self.model for item in (data.get('data') or []))
        return {'ok': available, 'model': self.model, 'model_count': len(data.get('data') or []), 'backend': self.backend}
