# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Bounded in-process CPU decoding for P43, not a production or network server."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
import sys
import time
from typing import Callable
from uuid import uuid4

import numpy as np

from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance

_PRODUCT = Path(__file__).resolve().parents[2] / "12-AZ-IP/43-az-geometric-tori-transformer"
if str(_PRODUCT) not in sys.path:
    sys.path.insert(0, str(_PRODUCT))

from az_tori_transformer.model import GeometricToriTransformer
from az_tori_transformer.positional import relative_distance, toroidal_rotation_table
from az_tori_transformer.tensor import Tensor, gelu, layer_norm


def _positive(value: int, name: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a nonempty string")
    return value


@dataclass(frozen=True)
class _Cache:
    keys: tuple[np.ndarray, ...]
    values: tuple[np.ndarray, ...]
    model_sha256: str

    @property
    def length(self) -> int:
        return self.keys[0].shape[1]

    @property
    def nbytes(self) -> int:
        return sum(array.nbytes for array in (*self.keys, *self.values))


class ToriCPUDecoder:
    """Snapshot model weights once; evaluate true heterogeneous-length CPU batches."""

    def __init__(self, model: GeometricToriTransformer, *, max_context_tokens: int = 256):
        if not isinstance(model, GeometricToriTransformer):
            raise TypeError("model must be a P43 GeometricToriTransformer")
        self.cfg = model.cfg
        if not self.cfg.causal or self.cfg.positional_mode != "toroidal" or self.cfg.num_layers < 1:
            raise ValueError("only causal toroidal P43 models with at least one layer are supported")
        self.max_context_tokens = _positive(max_context_tokens, "max_context_tokens")
        if self.max_context_tokens > 4096:
            raise ValueError("research decoder context limit is 4096")
        self._weights = {}
        identity = hashlib.sha256(json.dumps(asdict(self.cfg), sort_keys=True).encode())
        for name, parameter in model.named_parameters().items():
            array = np.array(parameter.data, dtype=np.float64, copy=True)
            if not np.all(np.isfinite(array)):
                raise ValueError(f"nonfinite model parameter: {name}")
            array.setflags(write=False)
            self._weights[name] = array
            identity.update(name.encode())
            identity.update(json.dumps(array.shape).encode())
            identity.update(array.astype("<f8").tobytes())
        self.model_sha256 = identity.hexdigest()
        self.bytes_per_cached_token = 2 * self.cfg.num_layers * self.cfg.dim * 8
        self.calls = 0
        self.decoded_rows = 0

    def empty_cache(self) -> _Cache:
        shape = (self.cfg.num_heads, 0, self.cfg.dim // self.cfg.num_heads)
        return _Cache(
            tuple(np.empty(shape, dtype=np.float64) for _ in range(self.cfg.num_layers)),
            tuple(np.empty(shape, dtype=np.float64) for _ in range(self.cfg.num_layers)),
            self.model_sha256,
        )

    def _norm(self, data: np.ndarray, prefix: str) -> np.ndarray:
        return layer_norm(
            Tensor(data), Tensor(self._weights[prefix + ".gamma"]),
            Tensor(self._weights[prefix + ".beta"]),
        ).data

    def _linear(self, data: np.ndarray, prefix: str) -> np.ndarray:
        out = data @ self._weights[prefix + ".weight"]
        bias = self._weights.get(prefix + ".bias")
        return out if bias is None else out + bias

    def decode_batch(
        self, tokens: tuple[int, ...], caches: tuple[_Cache, ...],
    ) -> tuple[np.ndarray, tuple[_Cache, ...]]:
        """One new token per row; caches are staged and never modified on failure."""
        if not tokens or len(tokens) != len(caches):
            raise ValueError("nonempty tokens and caches must have matching lengths")
        if any(type(token) is not int or not 0 <= token < self.cfg.vocab_size for token in tokens):
            raise ValueError("token IDs must be integers within the vocabulary")
        heads, width, layers = self.cfg.num_heads, self.cfg.dim // self.cfg.num_heads, self.cfg.num_layers
        for cache in caches:
            if not isinstance(cache, _Cache) or len(cache.keys) != layers or len(cache.values) != layers:
                raise ValueError("invalid KV cache")
            if cache.model_sha256 != self.model_sha256:
                raise ValueError("KV cache model identity mismatch")
            for array in (*cache.keys, *cache.values):
                if (array.dtype != np.float64 or array.shape != (heads, cache.length, width)
                        or not np.all(np.isfinite(array))):
                    raise ValueError("invalid KV cache shape or values")
            if cache.length >= self.max_context_tokens:
                raise ValueError("context budget exhausted")
        lengths = np.array([cache.length for cache in caches], dtype=np.int64)
        batch, longest = len(tokens), int(lengths.max()) + 1
        cos, sin = toroidal_rotation_table(longest, width)
        cos, sin = cos[lengths, None, :], sin[lengths, None, :]
        x = self._weights["token_embedding.weight"][list(tokens)]
        next_keys: list[list[np.ndarray]] = [[] for _ in tokens]
        next_values: list[list[np.ndarray]] = [[] for _ in tokens]
        for layer in range(layers):
            prefix = f"blocks.{layer}"
            normed = self._norm(x, prefix + ".ln1")
            q, k, v = (
                self._linear(normed, prefix + ".attn." + name).reshape(batch, heads, width)
                for name in ("wq", "wk", "wv")
            )
            rotated = []
            for projected in (q, k):
                result = np.empty_like(projected)
                result[..., 0::2] = projected[..., 0::2] * cos - projected[..., 1::2] * sin
                result[..., 1::2] = projected[..., 0::2] * sin + projected[..., 1::2] * cos
                rotated.append(result)
            q, k = rotated
            keys = np.zeros((batch, heads, longest, width), dtype=np.float64)
            values = np.zeros_like(keys)
            bias = np.zeros((batch, heads, longest), dtype=np.float64)
            for row, cache in enumerate(caches):
                length = cache.length
                next_k = np.concatenate((cache.keys[layer], k[row, :, None, :]), axis=1)
                next_v = np.concatenate((cache.values[layer], v[row, :, None, :]), axis=1)
                keys[row, :, :length + 1] = next_k
                values[row, :, :length + 1] = next_v
                distances = [relative_distance(length, position) for position in range(length + 1)]
                bias[row, :, :length + 1] = self._weights[prefix + ".attn.relative_bias"][:, distances]
                next_k.setflags(write=False)
                next_v.setflags(write=False)
                next_keys[row].append(next_k)
                next_values[row].append(next_v)
            scores = np.einsum("bhd,bhtd->bht", q, keys) / np.sqrt(width) + bias
            mask = np.arange(longest)[None, None, :] <= lengths[:, None, None]
            scores = np.where(mask, scores, -np.inf)
            probability = np.exp(scores - scores.max(axis=-1, keepdims=True))
            probability /= probability.sum(axis=-1, keepdims=True)
            attended = np.einsum("bht,bhtd->bhd", probability, values).reshape(batch, self.cfg.dim)
            x = x + self._linear(attended, prefix + ".attn.wo")
            ff = self._linear(self._norm(x, prefix + ".ln2"), prefix + ".ff.fc1")
            x = x + self._linear(gelu(Tensor(ff)).data, prefix + ".ff.fc2")
        logits = self._linear(self._norm(x, "ln_final"), "head")
        if not np.all(np.isfinite(logits)):
            raise ValueError("nonfinite decoding output")
        self.calls += 1
        self.decoded_rows += batch
        return logits, tuple(_Cache(tuple(k), tuple(v), self.model_sha256) for k, v in zip(next_keys, next_values))


@dataclass
class _Request:
    request_id: str
    owner_scope: str
    prompt: tuple[int, ...]
    max_new_tokens: int
    deadline: float | None
    cache: _Cache | None
    generated: tuple[int, ...] = ()
    consumed: int = 0
    status: str = "queued"
    error: str | None = None


class ResearchServingSession:
    """Single-threaded explicit-tick scheduler; no tool, network or approval authority."""

    TERMINAL = frozenset(("completed", "cancelled", "expired", "failed"))

    def __init__(
        self, decoder: ToriCPUDecoder, *, max_cache_bytes: int,
        max_requests: int = 64, max_batch_size: int = 8,
        max_batch_padding_tokens: int = 512, clock: Callable[[], float] = time.monotonic,
    ):
        if not isinstance(decoder, ToriCPUDecoder) or not callable(clock):
            raise TypeError("a ToriCPUDecoder and callable monotonic clock are required")
        self.decoder = decoder
        self.max_cache_bytes = _positive(max_cache_bytes, "max_cache_bytes")
        self.max_requests = _positive(max_requests, "max_requests")
        self.max_batch_size = _positive(max_batch_size, "max_batch_size")
        self.max_batch_padding_tokens = _positive(max_batch_padding_tokens, "max_batch_padding_tokens")
        if self.max_batch_padding_tokens < decoder.max_context_tokens:
            raise ValueError("padding budget must permit a longest-context singleton")
        self._clock = clock
        self._requests: dict[str, _Request] = {}
        self._queue: deque[str] = deque()

    def _now(self) -> float:
        now = self._clock()
        if type(now) not in (int, float) or not math.isfinite(now):
            raise ValueError("clock must return finite monotonic seconds")
        return float(now)

    def _owned(self, request_id: str, owner_scope: str) -> _Request:
        _text(owner_scope, "owner_scope")
        request = self._requests[request_id]
        if request.owner_scope != owner_scope:
            raise PermissionError("request owner_scope mismatch")
        return request

    def _reserve(self, request: _Request) -> int:
        if request.status in self.TERMINAL:
            return 0
        return (len(request.prompt) + request.max_new_tokens - 1) * self.decoder.bytes_per_cached_token

    def submit(
        self, prompt: tuple[int, ...], *, owner_scope: str,
        max_new_tokens: int, deadline: float | None = None,
    ) -> str:
        _text(owner_scope, "owner_scope")
        _positive(max_new_tokens, "max_new_tokens")
        if not isinstance(prompt, tuple) or not prompt or any(
            type(token) is not int or not 0 <= token < self.decoder.cfg.vocab_size for token in prompt
        ):
            raise ValueError("prompt must be a nonempty tuple of vocabulary token IDs")
        if len(prompt) + max_new_tokens - 1 > self.decoder.max_context_tokens:
            raise ValueError("prompt and generation exceed context budget")
        now = self._now()
        if deadline is not None:
            if type(deadline) not in (float, int) or not math.isfinite(deadline):
                raise ValueError("deadline must be finite monotonic seconds")
            if deadline <= now:
                raise TimeoutError("deadline expired before admission")
        if len(self._requests) >= self.max_requests:
            raise BufferError("request capacity reached; explicitly forget terminal requests")
        request = _Request(uuid4().hex, owner_scope, prompt, max_new_tokens, deadline, self.decoder.empty_cache())
        if request.request_id in self._requests:
            raise RuntimeError("request identifier collision; existing request was not replaced")
        if sum(self._reserve(item) for item in self._requests.values()) + self._reserve(request) > self.max_cache_bytes:
            raise BufferError("KV reservation capacity exhausted")
        self._requests[request.request_id] = request
        self._queue.append(request.request_id)
        return request.request_id

    def result(self, request_id: str, *, owner_scope: str) -> dict[str, object]:
        request = self._owned(request_id, owner_scope)
        return {
            "request_id": request_id, "owner_scope": owner_scope, "status": request.status,
            "tokens": request.generated, "consumed_tokens": request.consumed,
            "cache_bytes": request.cache.nbytes if request.cache else 0,
            "error": request.error, "model_sha256": self.decoder.model_sha256,
        }

    def _finish(self, request: _Request, status: str, error: str | None = None) -> None:
        request.status, request.error, request.cache = status, error, None

    def cancel(self, request_id: str, *, owner_scope: str) -> None:
        request = self._owned(request_id, owner_scope)
        if request.status not in self.TERMINAL:
            self._finish(request, "cancelled")
            self._queue.remove(request_id)

    def forget(self, request_id: str, *, owner_scope: str) -> None:
        request = self._owned(request_id, owner_scope)
        if request.status not in self.TERMINAL:
            raise ValueError("only terminal requests can be forgotten")
        del self._requests[request_id]

    def tick(self) -> dict[str, object]:
        now = self._now()
        for identifier in tuple(self._queue):
            request = self._requests[identifier]
            if request.deadline is not None and request.deadline <= now:
                self._finish(request, "expired")
                self._queue.remove(identifier)
        selected: list[_Request] = []
        padded_length = 0
        for identifier in tuple(self._queue):
            request = self._requests[identifier]
            length = request.consumed + 1
            candidate_length = max(padded_length, length)
            if (len(selected) < self.max_batch_size
                    and candidate_length * (len(selected) + 1) <= self.max_batch_padding_tokens):
                selected.append(request)
                padded_length = candidate_length
        if not selected:
            return {"batch_size": 0, "padded_token_slots": 0}
        tokens = tuple(
            request.prompt[request.consumed] if request.consumed < len(request.prompt)
            else request.generated[-1] for request in selected
        )
        active_caches: list[_Cache] = []
        for request in selected:
            if request.cache is None:
                raise RuntimeError("active request has no KV cache")
            active_caches.append(request.cache)
        try:
            logits, next_caches = self.decoder.decode_batch(tokens, tuple(active_caches))
        except (ValueError, FloatingPointError, MemoryError) as exc:
            for request in selected:
                self._finish(request, "failed", f"{type(exc).__name__}: {exc}")
                self._queue.remove(request.request_id)
            raise
        finished_at = self._now()
        for row, (request, cache) in enumerate(zip(selected, next_caches)):
            self._queue.remove(request.request_id)
            if request.deadline is not None and request.deadline <= finished_at:
                self._finish(request, "expired")
                continue
            request.cache, request.status = cache, "running"
            request.consumed += 1
            if request.consumed >= len(request.prompt):
                request.generated += (int(np.argmax(logits[row])),)
            if len(request.generated) >= request.max_new_tokens:
                self._finish(request, "completed")
            else:
                self._queue.append(request.request_id)
        return {
            "batch_size": len(selected), "padded_token_slots": padded_length * len(selected),
            "cache_bytes": sum(item.cache.nbytes for item in self._requests.values() if item.cache),
            "reserved_cache_bytes": sum(self._reserve(item) for item in self._requests.values()),
        }

    def receipt(self) -> ExecutionSpineRecord:
        return ExecutionSpineRecord(
            surface_id="az-ml-research-serving", surface_kind="research_runtime_observation",
            lane="az_ml_infrastructure", status="research_only",
            summary="Bounded P43 CPU incremental KV decoding and continuous batch scheduling.",
            canonical_paths=["src/infrastructure/research_serving.py"],
            governance=build_fail_closed_governance(
                epistemic_label="in-process CPU reference",
                promotion_rule="No production, authentication or performance qualification from this reference.",
                residual_blockers=[
                    "No accelerator, pretrained-model, multi-process or network service validation.",
                    "Caller owner scopes are consistency checks, not authenticated identity.",
                    "Cache limits cover KV payload, not model, scratch arrays, Python or process memory.",
                    "Cancellation/deadlines are checked between CPU calls, not preemptively.",
                ],
            ),
            compatibility={
                "model_sha256": self.decoder.model_sha256,
                "backend_calls": self.decoder.calls, "decoded_token_rows": self.decoder.decoded_rows,
                "max_cache_bytes": self.max_cache_bytes, "max_batch_size": self.max_batch_size,
                "max_batch_padding_tokens": self.max_batch_padding_tokens,
            },
            promotion={"eligible": False, "effects_authorized": False, "physics_claim": False},
        )
