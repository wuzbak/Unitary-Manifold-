# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Incremental and batched inference must match the existing full P43 forward."""

import numpy as np
import pytest

from src.infrastructure.research_serving import ResearchServingSession, ToriCPUDecoder
from az_tori_transformer.model import GeometricToriTransformer, GeometricToriTransformerConfig


def model(**kwargs):
    return GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=11, dim=8, num_heads=2, num_layers=2, ff_hidden_dim=16, seed=3, **kwargs,
    ))


def service(**kwargs):
    decoder = ToriCPUDecoder(model(), max_context_tokens=100)
    return ResearchServingSession(decoder, max_cache_bytes=1_000_000, **kwargs)


@pytest.mark.parametrize("length", [1, 2, 8, 39, 77])
def test_incremental_logits_match_full_prefix_across_wraparound(length):
    original = model()
    decoder = ToriCPUDecoder(original, max_context_tokens=100)
    cache = decoder.empty_cache()
    tokens = tuple(index % 11 for index in range(length))
    for index, token in enumerate(tokens):
        logits, (cache,) = decoder.decode_batch((token,), (cache,))
    reference, _ = original(np.array([tokens]))
    np.testing.assert_allclose(logits[0], reference.data[0, -1], rtol=1e-10, atol=1e-10)
    assert cache.length == length
    assert cache.nbytes == length * decoder.bytes_per_cached_token


def test_heterogeneous_true_batch_masks_padding_and_preserves_input_caches():
    original = model()
    decoder = ToriCPUDecoder(original, max_context_tokens=100)
    prefixes = [(2, 4), (7,), (1, 0, 3, 5)]
    caches = []
    for prefix in prefixes:
        cache = decoder.empty_cache()
        for token in prefix:
            _, (cache,) = decoder.decode_batch((token,), (cache,))
        caches.append(cache)
    before_calls = decoder.calls
    next_tokens = (3, 6, 9)
    logits, updated = decoder.decode_batch(next_tokens, tuple(caches))
    assert decoder.calls == before_calls + 1
    for row, (prefix, token, old, new) in enumerate(zip(prefixes, next_tokens, caches, updated)):
        full, _ = original(np.array([prefix + (token,)]))
        np.testing.assert_allclose(logits[row], full.data[0, -1], atol=1e-10)
        assert old.length == len(prefix)
        assert new.length == len(prefix) + 1
        assert not new.keys[0].flags.writeable


def test_weight_snapshot_is_not_changed_by_later_training():
    original = model()
    decoder = ToriCPUDecoder(original)
    before, _ = decoder.decode_batch((1,), (decoder.empty_cache(),))
    for parameter in original.parameters():
        parameter.data[:] = 0
    after, _ = decoder.decode_batch((1,), (decoder.empty_cache(),))
    np.testing.assert_array_equal(before, after)
    assert decoder.model_sha256 != ToriCPUDecoder(original).model_sha256


def test_kv_caches_cannot_be_reused_after_loading_different_weights():
    original = model()
    before = ToriCPUDecoder(original)
    _, (cache,) = before.decode_batch((1,), (before.empty_cache(),))
    original.head.weight.data[:] += 0.1
    after = ToriCPUDecoder(original)
    with pytest.raises(ValueError, match="model identity"):
        after.decode_batch((2,), (cache,))


def test_continuous_batch_generation_matches_independent_full_forward():
    runtime = service(max_batch_size=3)
    prompts = ((1, 2, 4), (6,), (0, 7))
    ids = [runtime.submit(prompt, owner_scope=f"owner-{row}", max_new_tokens=4)
           for row, prompt in enumerate(prompts)]
    ticks = []
    while any(runtime.result(identifier, owner_scope=f"owner-{row}")["status"] != "completed"
              for row, identifier in enumerate(ids)):
        ticks.append(runtime.tick())
    assert max(tick["batch_size"] for tick in ticks) == 3
    original = model()
    for row, (identifier, prompt) in enumerate(zip(ids, prompts)):
        output = ()
        for _ in range(4):
            logits, _ = original(np.array([prompt + output]))
            output += (int(logits.data[0, -1].argmax()),)
        result = runtime.result(identifier, owner_scope=f"owner-{row}")
        assert result["tokens"] == output
        assert result["cache_bytes"] == 0
    assert ticks[-1]["reserved_cache_bytes"] == 0
    assert runtime.receipt().to_dict()["promotion"]["eligible"] is False


def test_round_robin_admits_arrivals_and_does_not_starve():
    runtime = service(max_batch_size=1)
    first = runtime.submit((1, 2, 3), owner_scope="a", max_new_tokens=2)
    runtime.tick()
    second = runtime.submit((5,), owner_scope="b", max_new_tokens=2)
    runtime.tick()
    runtime.tick()
    assert runtime.result(second, owner_scope="b")["consumed_tokens"] == 1
    assert runtime.result(first, owner_scope="a")["consumed_tokens"] == 2


def test_scope_cancel_forget_and_released_reservations():
    runtime = service(max_requests=1)
    identifier = runtime.submit((1, 2), owner_scope="a", max_new_tokens=2)
    for action in (runtime.result, runtime.cancel, runtime.forget):
        with pytest.raises(PermissionError):
            action(identifier, owner_scope="b")
    with pytest.raises(ValueError, match="terminal"):
        runtime.forget(identifier, owner_scope="a")
    with pytest.raises(BufferError):
        runtime.submit((1,), owner_scope="a", max_new_tokens=1)
    runtime.tick()
    assert runtime.result(identifier, owner_scope="a")["cache_bytes"] > 0
    runtime.cancel(identifier, owner_scope="a")
    assert runtime.result(identifier, owner_scope="a")["cache_bytes"] == 0
    assert runtime.tick()["batch_size"] == 0
    runtime.forget(identifier, owner_scope="a")
    runtime.submit((1,), owner_scope="a", max_new_tokens=1)


def test_capacity_is_reserved_without_preallocating_kv():
    decoder = ToriCPUDecoder(model(), max_context_tokens=100)
    runtime = ResearchServingSession(decoder, max_cache_bytes=decoder.bytes_per_cached_token * 3)
    identifier = runtime.submit((1,), owner_scope="a", max_new_tokens=3)
    assert runtime.result(identifier, owner_scope="a")["cache_bytes"] == 0
    with pytest.raises(BufferError, match="reservation"):
        runtime.submit((1,), owner_scope="b", max_new_tokens=1)
    tick = runtime.tick()
    assert tick["cache_bytes"] == decoder.bytes_per_cached_token
    assert tick["reserved_cache_bytes"] == decoder.bytes_per_cached_token * 3
    runtime.cancel(identifier, owner_scope="a")
    runtime.submit((1,), owner_scope="b", max_new_tokens=1)


def test_identifier_collision_never_overwrites_an_admitted_request(monkeypatch):
    class FixedID:
        hex = "a" * 32

    monkeypatch.setattr("src.infrastructure.research_serving.uuid4", FixedID)
    runtime = service()
    identifier = runtime.submit((1,), owner_scope="a", max_new_tokens=2)
    with pytest.raises(RuntimeError, match="collision"):
        runtime.submit((2,), owner_scope="b", max_new_tokens=2)
    assert runtime.result(identifier, owner_scope="a")["status"] == "queued"
    runtime.tick()
    assert runtime.result(identifier, owner_scope="a")["status"] == "running"


def test_deadlines_checked_before_and_after_nonpreemptive_cpu_call(monkeypatch):
    clock = [0.0]
    runtime = service(clock=lambda: clock[0])
    with pytest.raises(TimeoutError):
        runtime.submit((1,), owner_scope="a", max_new_tokens=2, deadline=0)
    identifier = runtime.submit((1,), owner_scope="a", max_new_tokens=2, deadline=2)
    clock[0] = 3
    assert runtime.tick()["batch_size"] == 0
    assert runtime.result(identifier, owner_scope="a")["status"] == "expired"
    identifier = runtime.submit((1,), owner_scope="a", max_new_tokens=2, deadline=4)
    original = runtime.decoder.decode_batch

    def decode(*args):
        result = original(*args)
        clock[0] = 5
        return result

    monkeypatch.setattr(runtime.decoder, "decode_batch", decode)
    runtime.tick()
    result = runtime.result(identifier, owner_scope="a")
    assert result["status"] == "expired"
    assert result["cache_bytes"] == 0 and result["tokens"] == ()


def test_backend_error_is_visible_and_releases_selected_requests(monkeypatch):
    runtime = service()
    identifier = runtime.submit((1,), owner_scope="a", max_new_tokens=2)

    def fail(*args):
        raise ValueError("measured backend failure")

    monkeypatch.setattr(runtime.decoder, "decode_batch", fail)
    with pytest.raises(ValueError, match="backend failure"):
        runtime.tick()
    result = runtime.result(identifier, owner_scope="a")
    assert result["status"] == "failed"
    assert result["error"] == "ValueError: measured backend failure"
    assert result["cache_bytes"] == 0
    assert runtime.tick()["batch_size"] == 0


@pytest.mark.parametrize("prompt,output", [
    ((), 1), ((True,), 1), ((11,), 1), ((-1,), 1), ((1.0,), 1),
    ([1], 1), ((1,), True), ((1,), 0), ((1,), 1000),
])
def test_invalid_requests_rejected_before_registration(prompt, output):
    runtime = service()
    with pytest.raises(ValueError):
        runtime.submit(prompt, owner_scope="a", max_new_tokens=output)
    assert runtime.tick()["batch_size"] == 0


@pytest.mark.parametrize("kwargs", [
    {"max_requests": True}, {"max_batch_size": 0}, {"max_batch_padding_tokens": 99},
])
def test_invalid_limits(kwargs):
    with pytest.raises(ValueError):
        service(**kwargs)


@pytest.mark.parametrize("kwargs", [{"causal": False}, {"positional_mode": "rope"}])
def test_unsupported_architectures_fail_explicitly(kwargs):
    with pytest.raises(ValueError, match="only causal toroidal"):
        ToriCPUDecoder(model(**kwargs))


def test_context_limit_and_invalid_tokens_leave_prior_cache_unchanged():
    decoder = ToriCPUDecoder(model(), max_context_tokens=1)
    _, (cache,) = decoder.decode_batch((1,), (decoder.empty_cache(),))
    for token in (1, -1, True):
        with pytest.raises(ValueError):
            decoder.decode_batch((token,), (cache,))
    assert cache.length == 1


def test_padding_policy_bounds_heterogeneous_batch_scratch():
    runtime = service(max_batch_padding_tokens=100)
    ids = [runtime.submit(tuple(range(10)) * 8, owner_scope="a", max_new_tokens=1) for _ in range(3)]
    for _ in range(240):
        tick = runtime.tick()
        assert tick["padded_token_slots"] <= 100
        if all(runtime.result(identifier, owner_scope="a")["status"] == "completed" for identifier in ids):
            break
    else:
        pytest.fail("padding budget scheduler starved a request")
