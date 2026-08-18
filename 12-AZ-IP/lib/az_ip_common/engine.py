# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
az_ip_common/engine.py — Engine base class for AZ-IP engines.

Every engine in 12-AZ-IP/engines/ should subclass Engine and implement
run() and health().  The base class provides:
  - Prometheus instrumentation (optional)
  - HILS gate check before run()
  - Structured result schema (EngineResult)
  - In-memory LRU cache keyed by input hash

Theory: ThomasCory Walker-Pearson.  Code: GitHub Copilot (AI).
"""
from __future__ import annotations

import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram  # type: ignore
    _PROM = True
except ImportError:
    _PROM = False


@dataclass
class EngineResult:
    engine_name: str
    version: str
    ok: bool
    data: Any
    error: Optional[str] = None
    elapsed_s: float = 0.0
    cache_hit: bool = False
    hils_approved: bool = True
    epistemic_label: str = "UNCLASSIFIED"
    result_hash: str = ""

    def __post_init__(self):
        if not self.result_hash:
            self.result_hash = hashlib.sha256(
                json.dumps(self.data, default=str, sort_keys=True).encode()
            ).hexdigest()[:16]

    def to_dict(self) -> Dict:
        return asdict(self)


class Engine:
    """
    Base class for all AZ-IP engines.

    Subclasses must implement:
      - name: str
      - version: str
      - async def _execute(self, **kwargs) -> Any
      - async def health(self) -> Dict
    """

    name: str = "base_engine"
    version: str = "0.0.0"
    epistemic_label: str = "UNCLASSIFIED"

    def __init__(self, config: Optional[Dict] = None) -> None:
        self.config = config or {}
        self._cache: Dict[str, EngineResult] = {}
        self._cache_size: int = self.config.get("cache_size", 128)

        if _PROM:
            prefix = self.name.replace("-", "_").replace(" ", "_")
            try:
                self._run_counter = Counter(
                    f"azip_{prefix}_runs_total", f"{self.name} total runs", ["status"]
                )
                self._latency = Histogram(
                    f"azip_{prefix}_latency_seconds", f"{self.name} run latency",
                    buckets=[0.1, 0.5, 1.0, 5.0, 30.0],
                )
            except Exception:
                self._run_counter = None  # type: ignore
                self._latency = None  # type: ignore
        else:
            self._run_counter = None  # type: ignore
            self._latency = None  # type: ignore

    async def run(self, hils_approved: bool = True, **kwargs) -> EngineResult:
        if not hils_approved:
            return EngineResult(
                engine_name=self.name, version=self.version, ok=False, data=None,
                error="HILS gate rejected — human approval required", hils_approved=False,
            )

        cache_key = hashlib.sha256(
            json.dumps(kwargs, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            cached.cache_hit = True
            return cached

        start = time.time()
        try:
            data = await self._execute(**kwargs)
            elapsed = time.time() - start
            result = EngineResult(
                engine_name=self.name, version=self.version, ok=True,
                data=data, elapsed_s=elapsed, epistemic_label=self.epistemic_label,
            )
            if _PROM and self._run_counter:
                self._run_counter.labels(status="ok").inc()
            if _PROM and self._latency:
                self._latency.observe(elapsed)
        except Exception as exc:
            elapsed = time.time() - start
            logger.error("%s.run failed: %s", self.name, exc)
            result = EngineResult(
                engine_name=self.name, version=self.version, ok=False,
                data=None, error=str(exc), elapsed_s=elapsed,
            )
            if _PROM and self._run_counter:
                self._run_counter.labels(status="error").inc()

        if len(self._cache) >= self._cache_size:
            del self._cache[next(iter(self._cache))]
        self._cache[cache_key] = result
        return result

    async def _execute(self, **kwargs) -> Any:
        raise NotImplementedError

    async def health(self) -> Dict:
        return {"ok": True, "engine": self.name, "version": self.version}
