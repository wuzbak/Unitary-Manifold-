# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# AxiomZero — Persistent AI Cognitive Layer for the Unitary Manifold
# Project: https://github.com/wuzbak/Unitary-Manifold-
# Theory & scientific direction: ThomasCory Walker-Pearson
# Code architecture & implementation: GitHub Copilot (AI)
"""
AxiomZero core/model_router.py — VRAM-aware heterogeneous model mesh

Manages loading and unloading of Ollama models to respect the hard constraint:
    never more than 2 heavy models (>4B params) loaded simultaneously.

Sub-agents queue via asyncio rather than blocking.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture: GitHub Copilot (AI).
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Models considered "heavy" (>4B params) — subject to the 2-concurrent limit
_HEAVY_MODELS = {"llama3.1:8b", "qwen2.5-coder:7b", "mistral:7b", "mixtral:8x7b"}

# Param size estimates for reference
_MODEL_PARAMS_B = {
    "llama3.1:8b": 8,
    "qwen2.5-coder:7b": 7,
    "qwen2.5-coder:1.5b": 1.5,
    "nomic-embed-text": 0.137,
}


# ---------------------------------------------------------------------------
# Singleton VRAM capability probe (queries nvidia-smi once per process)
# ---------------------------------------------------------------------------

_VRAM_CAPABILITY: Optional[Dict[str, Any]] = None  # cached result


async def probe_vram_capability() -> Dict[str, Any]:
    """
    Query GPU VRAM capacity once and cache the result.

    Returns a dict with keys:
      - available: bool           — True if GPU is present
      - total_mb: float           — total VRAM in MiB
      - free_mb: float            — free VRAM in MiB
      - recommended_model_tier: str  — 'large' | 'medium' | 'small' | 'cpu'
    """
    global _VRAM_CAPABILITY
    if _VRAM_CAPABILITY is not None:
        return _VRAM_CAPABILITY

    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi",
            "--query-gpu=memory.total,memory.free",
            "--format=csv,noheader,nounits",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        line = stdout.decode().strip().splitlines()[0]
        total, free = (float(x.strip()) for x in line.split(","))

        if free >= 20_000:
            tier = "large"       # 70B+ models
        elif free >= 8_000:
            tier = "medium"      # 13B models
        elif free >= 4_000:
            tier = "small"       # 7B models (quantized)
        else:
            tier = "cpu"         # CPU fallback

        _VRAM_CAPABILITY = {
            "available": True,
            "total_mb": total,
            "free_mb": free,
            "recommended_model_tier": tier,
        }
    except Exception:
        _VRAM_CAPABILITY = {
            "available": False,
            "total_mb": 0.0,
            "free_mb": 0.0,
            "recommended_model_tier": "cpu",
        }

    logger.info("VRAM capability: %s", _VRAM_CAPABILITY)
    return _VRAM_CAPABILITY


# Model selection table keyed by VRAM tier
_TIER_MODEL_DEFAULTS: Dict[str, Dict[str, str]] = {
    "large":  {"strategic": "llama3.1:70b", "math": "qwen2.5-coder:32b",  "test": "qwen2.5-coder:7b",  "embed": "nomic-embed-text"},
    "medium": {"strategic": "llama3.1:8b",  "math": "qwen2.5-coder:7b",   "test": "qwen2.5-coder:1.5b","embed": "nomic-embed-text"},
    "small":  {"strategic": "llama3.1:8b",  "math": "qwen2.5-coder:1.5b", "test": "qwen2.5-coder:1.5b","embed": "nomic-embed-text"},
    "cpu":    {"strategic": "llama3.2:3b",  "math": "qwen2.5-coder:1.5b", "test": "qwen2.5-coder:1.5b","embed": "nomic-embed-text"},
}


class ModelRouter:
    """
    VRAM-aware model router for the AxiomZero agent network.

    Enforces:
    - Max 2 heavy models (>4B params) loaded simultaneously
    - Queuing rather than OOM-crashing when limit is hit
    - nvidia-smi VRAM monitor (pauses inference at >90%)
    - Singleton VRAM probe: GPU capability queried once per process
    - Automatic model tier selection based on available VRAM
    """

    def __init__(self, config: Dict):
        self.config = config
        self.max_concurrent_heavy: int = config.get("max_concurrent_heavy", 2)
        self.vram_pause_threshold: float = config.get("vram_pause_threshold_pct", 90.0)
        self._loaded_heavy: set[str] = set()
        self._lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(self.max_concurrent_heavy)
        self._model_map = {
            "strategic": config.get("strategic", "llama3.1:8b"),
            "math": config.get("math", "qwen2.5-coder:7b"),
            "test": config.get("test", "qwen2.5-coder:1.5b"),
            "embed": config.get("embed", "nomic-embed-text"),
        }
        self._vram_tier: Optional[str] = None  # set after probe

    async def adapt_to_vram(self) -> str:
        """
        Run the singleton VRAM probe (once per process) and update the
        model map to the appropriate tier.  Returns the selected tier name.
        """
        cap = await probe_vram_capability()
        tier = cap["recommended_model_tier"]
        self._vram_tier = tier
        tier_defaults = _TIER_MODEL_DEFAULTS.get(tier, _TIER_MODEL_DEFAULTS["cpu"])
        for key, default_model in tier_defaults.items():
            # Only override if user has not explicitly configured this key
            if key not in self.config:
                self._model_map[key] = default_model
        logger.info("Model map updated for VRAM tier %r: %s", tier, self._model_map)
        return tier

    def resolve(self, model_key: str) -> str:
        """Resolve a logical key ('strategic', 'math', 'test', 'embed') to a model name."""
        return self._model_map.get(model_key, model_key)

    async def acquire_model(self, model_key: str) -> str:
        """
        Acquire access to a model, respecting the heavy-model limit.
        Returns the resolved model name once access is granted.
        """
        model_name = self.resolve(model_key)
        is_heavy = model_name in _HEAVY_MODELS

        if is_heavy:
            await self._semaphore.acquire()
            async with self._lock:
                self._loaded_heavy.add(model_name)
            logger.debug("Acquired heavy model slot: %s (loaded: %s)", model_name, self._loaded_heavy)

        # VRAM check
        await self._wait_for_vram()

        return model_name

    async def release_model(self, model_key: str) -> None:
        """Release a previously acquired model slot."""
        model_name = self.resolve(model_key)
        is_heavy = model_name in _HEAVY_MODELS
        if is_heavy:
            async with self._lock:
                self._loaded_heavy.discard(model_name)
            self._semaphore.release()
            logger.debug("Released heavy model slot: %s", model_name)

    async def _wait_for_vram(self) -> None:
        """Pause inference if VRAM utilisation exceeds the threshold."""
        try:
            vram_pct = await _get_vram_pct()
            while vram_pct > self.vram_pause_threshold:
                logger.warning("VRAM at %.1f%% — pausing model inference (threshold %.0f%%)",
                               vram_pct, self.vram_pause_threshold)
                await asyncio.sleep(5)
                vram_pct = await _get_vram_pct()
        except Exception:
            pass  # No GPU or nvidia-smi absent — continue

    def status(self) -> Dict:
        return {
            "max_concurrent_heavy": self.max_concurrent_heavy,
            "currently_loaded_heavy": list(self._loaded_heavy),
            "heavy_slots_available": self._semaphore._value,  # type: ignore[attr-defined]
            "model_map": self._model_map,
            "vram_tier": self._vram_tier,
        }


# ---------------------------------------------------------------------------
# VRAM query helper
# ---------------------------------------------------------------------------

async def _get_vram_pct() -> float:
    """
    Query GPU VRAM usage via nvidia-smi.
    Returns percentage (0–100), or 0.0 if unavailable.
    """
    try:
        proc = await asyncio.create_subprocess_exec(
            "nvidia-smi",
            "--query-gpu=memory.used,memory.total",
            "--format=csv,noheader,nounits",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.DEVNULL,
        )
        stdout, _ = await proc.communicate()
        line = stdout.decode().strip().splitlines()[0]
        used, total = (float(x.strip()) for x in line.split(","))
        return 100.0 * used / total if total > 0 else 0.0
    except Exception:
        return 0.0


# ---------------------------------------------------------------------------
# Ollama inference helper (used by all managers)
# ---------------------------------------------------------------------------

async def ollama_generate(
    model: str,
    prompt: str,
    ollama_url: str = "http://localhost:11434",
    system: Optional[str] = None,
    temperature: float = 0.1,
    max_tokens: int = 2048,
) -> str:
    """
    Call Ollama /api/generate and return the response text.
    Returns empty string on failure (callers handle degradation).
    """
    try:
        import httpx  # type: ignore
    except ImportError:
        return "[httpx not installed — Ollama inference unavailable]"

    payload: Dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    if system:
        payload["system"] = system

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(f"{ollama_url}/api/generate", json=payload)
            resp.raise_for_status()
            return resp.json().get("response", "")
    except Exception as exc:
        logger.warning("Ollama inference failed: %s", exc)
        return f"[Ollama error: {exc}]"
