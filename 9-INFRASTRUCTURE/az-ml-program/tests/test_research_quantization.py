# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Contract tests for the in-memory P43 research quantization adapter."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

import numpy as np
import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "12-AZ-IP/43-az-geometric-tori-transformer"))

from src.infrastructure.research_quantization import (  # noqa: E402
    build_trained_reference_baseline,
    load_model_artifact,
    main,
    run_research_quantization,
    serialize_model,
)
from az_tori_transformer.checkpoint import load_checkpoint  # noqa: E402


def _replace_metadata(encoded: bytes, update):
    magic = b"AZMQ\x01"
    metadata_size = struct.unpack_from("<I", encoded, len(magic))[0]
    start = len(magic) + 4
    metadata = json.loads(encoded[start:start + metadata_size])
    update(metadata)
    encoded_metadata = json.dumps(
        metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
    ).encode("ascii")
    body = magic + struct.pack("<I", len(encoded_metadata)) + encoded_metadata
    body += encoded[start + metadata_size:-32]
    return body + hashlib.sha256(body).digest()


def test_complete_model_artifact_roundtrips_into_fresh_model():
    model, report = build_trained_reference_baseline(steps=1)
    encoded = serialize_model(model, bit_width=3)
    restored = load_model_artifact(encoded)
    assert restored is not model
    assert restored.cfg == model.cfg
    assert list(restored.named_parameters()) == list(model.named_parameters())
    assert report["vocabulary"] == sorted(report["character_to_token_id"])
    assert set(report["split_identities"]) == {"train", "validation", "test"}
    assert all(
        actual.shape == expected.shape
        for actual, expected in zip(restored.parameters(), model.parameters())
    )
    assert any(
        not np.array_equal(actual.data, expected.data)
        for actual, expected in zip(restored.parameters(), model.parameters())
    )


def test_model_artifact_rejects_tampering_and_resigned_schema_mismatch():
    model, _ = build_trained_reference_baseline(steps=1)
    encoded = serialize_model(model, bit_width=3)
    tampered = bytearray(encoded)
    tampered[-33] ^= 0x01
    with pytest.raises(ValueError, match="integrity"):
        load_model_artifact(bytes(tampered))
    with pytest.raises(ValueError, match="schema"):
        load_model_artifact(_replace_metadata(
            encoded, lambda metadata: metadata.update(parameter_names=["not-a-model-parameter"]),
        ))
    with pytest.raises(ValueError, match="config"):
        load_model_artifact(_replace_metadata(
            encoded, lambda metadata: metadata["config"].update(num_heads=True),
        ))


def test_evaluation_reports_all_fixed_splits_and_complete_size_accounting(tmp_path):
    report = run_research_quantization(tmp_path, steps=1)
    evaluations = report["evaluations"]
    assert set(evaluations) == {
        "float64_native", "fp16_roundtrip", "original_quantizer_3bit",
        "original_quantizer_4bit",
    }
    for arm in evaluations.values():
        assert set(arm["metrics"]) == {"train", "validation", "test"}
        test = arm["metrics"]["test"]
        assert test["tokens"] > 0
        assert np.isfinite(test["cross_entropy_nats"])
        assert 0.0 <= test["greedy_accuracy"] <= 1.0
        assert 0.0 <= test["answer_digit_accuracy"] <= 1.0
        assert np.isfinite(test["answer_digit_cross_entropy_nats"])
        assert type(arm["quality_tolerance"]["passed"]) is bool
    accounting = evaluations["original_quantizer_3bit"]["size_accounting"]
    assert accounting["artifact_bytes"] == sum((
        accounting["wrapper_header_bytes"],
        accounting["model_metadata_bytes"],
        accounting["quantizer_framing_metadata_checksum_bytes"],
        accounting["packed_weight_bytes"],
        accounting["outer_checksum_bytes"],
    ))
    assert 3.0 < accounting["effective_bits_per_parameter"] < 4.0
    assert report["model_artifact"]["published_as_binary"] is False
    assert report["data"]["splits"]["test"]["sha256"]
    assert report["training"]["validation_or_test_used_for_training_or_quantizer_fitting"] is False
    assert report["execution_spine"]["promotion"]["eligible"] is False
    evidence = report["published_evidence"]
    assert evidence["filename_is_sha256_of_complete_json_bytes"] is True
    content = (json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                          allow_nan=False) + "\n").encode("ascii")
    published = tmp_path / f"{hashlib.sha256(content).hexdigest()}.json"
    assert published.stem == hashlib.sha256(published.read_bytes()).hexdigest()
    assert json.loads(published.read_text(encoding="utf-8")) == report


def test_output_directory_must_already_exist(tmp_path):
    with pytest.raises(ValueError, match="existing directory"):
        run_research_quantization(tmp_path / "not-created", steps=1)


def test_inconsistent_oversized_config_is_rejected_before_model_allocation(monkeypatch):
    import src.infrastructure.research_quantization as research

    model, _ = build_trained_reference_baseline(steps=1)
    encoded = serialize_model(model, bit_width=3)
    invalid = _replace_metadata(encoded, lambda metadata: metadata["config"].update(vocab_size=10_000_000))
    original = research._p43_api

    def forbidden_model(*args, **kwargs):
        pytest.fail("artifact validation constructed an inconsistent model")

    def api():
        adam, _, config, loss = original()
        return adam, forbidden_model, config, loss

    monkeypatch.setattr(research, "_p43_api", api)
    with pytest.raises(ValueError, match="config parameter count"):
        load_model_artifact(invalid)


@pytest.mark.parametrize("mode", ["toroidal", "rope", "rope_matched"])
@pytest.mark.parametrize("layers", [0, 1])
def test_preallocation_count_contract_matches_supported_p43_layouts(mode, layers):
    from az_tori_transformer.model import GeometricToriTransformer, GeometricToriTransformerConfig

    model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=11, dim=8, num_heads=2, num_layers=layers,
        ff_hidden_dim=16, positional_mode=mode,
    ))
    restored = load_model_artifact(serialize_model(model, bit_width=3))
    assert restored.num_parameters() == model.num_parameters()


def test_consistent_config_above_decoded_limit_is_rejected(monkeypatch):
    import src.infrastructure.research_quantization as research

    model, _ = build_trained_reference_baseline(steps=1)
    encoded = serialize_model(model, bit_width=3)
    monkeypatch.setattr(research, "_MAX_PARAMETER_COUNT", 1)
    with pytest.raises(ValueError, match="research parameter limit"):
        load_model_artifact(encoded)


def test_requested_quantized_artifacts_are_persistent_loadable_and_hash_named(tmp_path):
    report = run_research_quantization(tmp_path, artifact_dir=tmp_path, steps=1)
    assert report["model_artifact"]["published_as_binary"] is True
    assert report["published_evidence"]["quantized_model_artifact_published"] is True
    for bits, artifact in report["quantized_artifacts"].items():
        path = tmp_path / artifact["filename"]
        content = path.read_bytes()
        assert path.stem == artifact["sha256"] == hashlib.sha256(content).hexdigest()
        restored = load_model_artifact(content)
        assert restored.num_parameters() == report["model"]["parameter_count"]
        assert artifact["bytes"] == report["evaluations"][f"original_quantizer_{bits}bit"]["serialized_model_bytes"]


@pytest.mark.slow
def test_cli_publishes_loadable_trained_checkpoint_and_quality_report(tmp_path, capsys):
    assert main(["--checkpoint-dir", str(tmp_path)]) == 0
    report = json.loads(capsys.readouterr().out)
    checkpoint = tmp_path / report["trained_checkpoint"]["filename"]
    assert checkpoint.suffix == ".npz"
    assert checkpoint.is_file()
    assert checkpoint.stat().st_size < 1_000_000
    assert hashlib.sha256(checkpoint.read_bytes()).hexdigest() == report["trained_checkpoint"]["sha256"]
    loaded = load_checkpoint(checkpoint)
    assert loaded.model.cfg.vocab_size == report["model"]["config"]["vocab_size"]
    assert loaded.model.cfg.dim == report["model"]["config"]["dim"]
    assert loaded.model.num_parameters() == report["model"]["parameter_count"]
    assert loaded.metadata["fixture_sha256"] == report["data"]["fixture_sha256"]
    assert loaded.metadata["tokenizer"]["vocabulary"] == report["data"]["vocabulary"]
    assert loaded.metadata["source_sha256"] == report["model"]["source_sha256"]
    assert loaded.metadata["model_config"] == report["model"]["config"]
    assert report["trained_checkpoint"]["published"] is True
    assert report["published_evidence"]["quantized_model_artifact_published"] is False
    assert not list(tmp_path.glob(".research-baseline-*.npz"))
