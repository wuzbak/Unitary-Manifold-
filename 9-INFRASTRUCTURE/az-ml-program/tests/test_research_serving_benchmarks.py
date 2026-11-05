# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Executable serving parity evidence, not inference from a supervisor count."""

import hashlib
import json
from pathlib import Path

from src.infrastructure.research_serving_benchmarks import benchmark_serving, main
from az_tori_transformer.checkpoint import save_checkpoint
from az_tori_transformer.model import GeometricToriTransformer, GeometricToriTransformerConfig


def test_actual_cached_batch_measurements_match_full_prefix():
    model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=7, dim=8, num_heads=2, num_layers=1, ff_hidden_dim=16,
    ))
    report = benchmark_serving(model)
    assert all(report["gates"].values())
    assert report["maximum_prefill_logit_absolute_error"] < 1e-10
    assert report["continuous_batch_samples"][0]["maximum_batch_size"] == 4
    assert report["continuous_batch_samples"][0]["decoded_token_rows"] == 45
    assert report["full_prefix"]["evaluated_token_positions"] == 248
    assert report["promotion_eligible"] is False
    assert report["environment"]["gpu"] == "unmeasured"
    assert report["observed_median_serial_to_batch_ratio"] > 0


def test_checkpoint_cli_pins_sources_and_publishes_immutable_receipt(tmp_path, capsys):
    model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=7, dim=8, num_heads=2, num_layers=1, ff_hidden_dim=16,
    ))
    checkpoint = tmp_path / "model.npz"
    save_checkpoint(checkpoint, model)
    assert main(["--checkpoint", str(checkpoint), "--output-dir", str(tmp_path)]) == 0
    evidence = Path(capsys.readouterr().out.strip())
    assert evidence.stem == hashlib.sha256(evidence.read_bytes()).hexdigest()
    report = json.loads(evidence.read_bytes())
    assert report["checkpoint_sha256"] == hashlib.sha256(checkpoint.read_bytes()).hexdigest()
    assert report["execution_spine"]["promotion"]["eligible"] is False


def test_checkpoint_cli_loads_the_exact_bytes_it_hashes(tmp_path, capsys, monkeypatch):
    original_model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=7, dim=8, num_heads=2, num_layers=1, ff_hidden_dim=16,
    ))
    replacement_model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=7, dim=12, num_heads=3, num_layers=1, ff_hidden_dim=24,
    ))
    checkpoint = tmp_path / "model.npz"
    replacement = tmp_path / "replacement.npz"
    save_checkpoint(checkpoint, original_model)
    save_checkpoint(replacement, replacement_model)
    hashed_bytes = checkpoint.read_bytes()
    replacement_bytes = replacement.read_bytes()
    original_read_bytes = Path.read_bytes
    reads = 0
    observed_configs = []
    original_benchmark = benchmark_serving

    def replace_after_hash(path):
        nonlocal reads
        if path == checkpoint:
            reads += 1
            data = original_read_bytes(path)
            checkpoint.write_bytes(replacement_bytes)
            return data
        return original_read_bytes(path)

    def record_model(model):
        observed_configs.append(model.cfg)
        return original_benchmark(model)

    monkeypatch.setattr(Path, "read_bytes", replace_after_hash)
    monkeypatch.setattr(
        "src.infrastructure.research_serving_benchmarks.benchmark_serving",
        record_model,
    )
    assert main(["--checkpoint", str(checkpoint), "--output-dir", str(tmp_path)]) == 0
    evidence = Path(capsys.readouterr().out.strip())
    report = json.loads(evidence.read_bytes())
    assert reads == 1
    assert report["checkpoint_sha256"] == hashlib.sha256(hashed_bytes).hexdigest()
    assert observed_configs == [original_model.cfg]


def test_original_packed_model_is_loadable_by_the_actual_serving_benchmark(tmp_path, capsys):
    from src.infrastructure.research_quantization import serialize_model

    model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=7, dim=8, num_heads=2, num_layers=1, ff_hidden_dim=16,
    ))
    packed = tmp_path / "model.azmq"
    packed.write_bytes(serialize_model(model, bit_width=3))
    assert main(["--quantized-model", str(packed), "--output-dir", str(tmp_path)]) == 0
    evidence = Path(capsys.readouterr().out.strip())
    report = json.loads(evidence.read_bytes())
    assert report["model_input"]["format"] == "azmq"
    assert report["model_input"]["sha256"] == hashlib.sha256(packed.read_bytes()).hexdigest()
    assert all(report["gates"].values())
    assert "checkpoint_sha256" not in report
