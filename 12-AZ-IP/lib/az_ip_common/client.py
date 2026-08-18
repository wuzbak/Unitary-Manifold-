# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""az_ip_common/client.py — Authenticated HTTP client with retry."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

_MAX_RETRIES = 3
_BACKOFF_BASE = 1.0


class AuthenticatedHTTPClient:
    """httpx async client with JWT bearer auth and exponential-backoff retry."""

    def __init__(
        self,
        base_url: str,
        jwt_token: str = "",
        timeout: float = 30.0,
        max_retries: int = _MAX_RETRIES,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.jwt_token = jwt_token
        self.timeout = timeout
        self.max_retries = max_retries
        self._client: Any = None

    def _headers(self) -> Dict[str, str]:
        h: Dict[str, str] = {"Content-Type": "application/json"}
        if self.jwt_token:
            h["Authorization"] = "Bearer " + self.jwt_token
        return h

    async def __aenter__(self):
        try:
            import httpx  # type: ignore
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self._headers(),
                timeout=self.timeout,
            )
            await self._client.__aenter__()
        except ImportError:
            self._client = None
        return self

    async def __aexit__(self, *args):
        if self._client is not None:
            await self._client.__aexit__(*args)

    async def get(self, path: str, **kwargs) -> Any:
        return await self._request("GET", path, **kwargs)

    async def post(self, path: str, json: Optional[Dict] = None, **kwargs) -> Any:
        return await self._request("POST", path, json=json, **kwargs)

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        if self._client is None:
            raise RuntimeError("httpx not installed — HTTP client unavailable")
        last_exc: Exception = RuntimeError("No attempts made")
        for attempt in range(self.max_retries):
            try:
                resp = await self._client.request(method, path, **kwargs)
                resp.raise_for_status()
                return resp
            except Exception as exc:
                last_exc = exc
                if attempt < self.max_retries - 1:
                    backoff = _BACKOFF_BASE * (2 ** attempt)
                    logger.warning(
                        "HTTP %s %s failed (attempt %d/%d): %s — retrying in %.1fs",
                        method, path, attempt + 1, self.max_retries, exc, backoff,
                    )
                    import asyncio
                    await asyncio.sleep(backoff)
        raise last_exc
