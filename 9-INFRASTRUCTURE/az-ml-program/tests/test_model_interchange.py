# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Verify exact supported formats and explicitly opt-in lossy transformations."""

import hashlib
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pytest

from src.infrastructure.model_interchange import (
    load_inference_checkpoint, main, translate_model,
)
from src.infrastructure.research_quantization import load_model_artifact
from src.infrastructure.tokenizer_interchange import CharacterTokenizer, export_p43_tokenizer
from az_tori_transformer.checkpoint import save_checkpoint
from az_tori_transformer.model import GeometricToriTransformer, GeometricToriTransformerConfig
from az_tori_transformer.optim import Adam


@pytest.fixture
def checkpoint(tmp_path):
    model = GeometricToriTransformer(GeometricToriTransformerConfig(
        vocab_size=4, dim=8, num_heads=2, num_layers=1, ff_hidden_dim=16,
    ))
    path = tmp_path / "source.npz"
    tokenizer = CharacterTokenizer(("b", "a", "🙂", "\n"))
    save_checkpoint(path, model, metadata=export_p43_tokenizer(tokenizer))
    return model, tokenizer, path


def test_full_supported_roundtrip_preserves_quantized_weights_not_original_weights(checkpoint):
    original, tokenizer, path = checkpoint
    with pytest.raises(ValueError, match="allow_lossy"):
        translate_model(path.read_bytes(), source_format="p43_npz", target_format="azmq")
    forward = translate_model(path.read_bytes(), source_format="p43_npz",
                              target_format="azmq", allow_lossy=True)
    encoded = json.loads(forward.manifest)
    assert encoded["weight_conversion"]["additional_loss"] is True
    assert encoded["weight_conversion"]["max_absolute_weight_error"] > 0
    assert encoded["semantics"]["quality_measured"] is False
    assert encoded["execution_spine"]["promotion"]["eligible"] is False
    packed = load_model_artifact(forward.model)
    reverse = translate_model(forward.model, source_format="azmq", target_format="p43_npz",
                              tokenizer=tokenizer)
    restored = load_inference_checkpoint(reverse.model).model
    for a, b in zip(packed.parameters(), restored.parameters(), strict=True):
        np.testing.assert_array_equal(a.data, b.data)
    payload = json.loads(reverse.manifest)
    assert payload["weight_conversion"]["additional_loss"] is False
    assert payload["weight_conversion"]["max_absolute_weight_error"] == 0
    assert payload["semantics"]["original_prequantization_weights_restored"] is False
    assert np.any(original.head.weight.data != restored.head.weight.data)
    assert forward.tokenizer == reverse.tokenizer


def test_optimizer_and_rng_states_cannot_be_silently_discarded(checkpoint, tmp_path):
    model, tokenizer, _ = checkpoint
    for state in ("optimizer", "rng"):
        path = tmp_path / f"{state}.npz"
        kwargs = {"optimizer": Adam(model.parameters())} if state == "optimizer" else {"rng": np.random.default_rng(1)}
        save_checkpoint(path, model, metadata=export_p43_tokenizer(tokenizer), **kwargs)
        with pytest.raises(ValueError, match="optimizer/RNG"):
            translate_model(path.read_bytes(), source_format="p43_npz",
                            target_format="azmq", allow_lossy=True)


def test_missing_conflicting_or_unsupported_tokenizer_never_guessed(checkpoint, tmp_path):
    model, tokenizer, path = checkpoint
    with pytest.raises(ValueError, match="conflicts"):
        translate_model(path.read_bytes(), source_format="p43_npz", target_format="azmq",
                        allow_lossy=True, tokenizer=CharacterTokenizer(("a", "b", "🙂", "\n")))
    forward = translate_model(path.read_bytes(), source_format="p43_npz",
                              target_format="azmq", allow_lossy=True)
    with pytest.raises(ValueError, match="explicit"):
        translate_model(forward.model, source_format="azmq", target_format="p43_npz")
    with pytest.raises(ValueError, match="vocab_size"):
        translate_model(forward.model, source_format="azmq", target_format="p43_npz",
                        tokenizer=CharacterTokenizer(("a",)))
    save_checkpoint(path, model, metadata={})
    with pytest.raises(ValueError, match="algorithm"):
        translate_model(path.read_bytes(), source_format="p43_npz", target_format="azmq", allow_lossy=True)


@pytest.mark.parametrize("formats", [("gguf", "azmq"), ("p43_npz", "onnx"), ("p43_npz", "p43_npz")])
def test_unsupported_format_pairs_fail_explicitly(checkpoint, formats):
    with pytest.raises(ValueError, match="only p43_npz"):
        translate_model(checkpoint[2].read_bytes(), source_format=formats[0], target_format=formats[1])


def test_checksum_corruption_fails_before_publication(checkpoint):
    forward = translate_model(checkpoint[2].read_bytes(), source_format="p43_npz",
                              target_format="azmq", allow_lossy=True)
    with pytest.raises(ValueError, match="SHA-256"):
        translate_model(forward.model[:-1] + bytes([forward.model[-1] ^ 1]),
                        source_format="azmq", target_format="p43_npz", tokenizer=checkpoint[1])


def test_inconsistent_npz_config_rejected_without_allocating_large_model(checkpoint):
    with np.load(checkpoint[2], allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
    manifest = json.loads(arrays["manifest"].item())
    manifest["config"]["vocab_size"] = 10_000_000
    arrays["manifest"] = np.array(json.dumps(manifest))
    stream = io.BytesIO()
    np.savez_compressed(stream, **arrays)
    with pytest.raises(ValueError, match="parameter count"):
        load_inference_checkpoint(stream.getvalue())


def test_expanded_size_limit_precedes_array_loading(checkpoint, monkeypatch):
    monkeypatch.setattr("src.infrastructure.model_interchange.MAX_EXPANDED_BYTES", 1)
    with pytest.raises(ValueError, match="expanded-size"):
        load_inference_checkpoint(checkpoint[2].read_bytes())


@pytest.mark.parametrize("shape,dtype", [((500_000_000,), "<f8"), ((), "<U500000000")])
def test_forged_npy_headers_rejected_before_numpy_allocates(checkpoint, monkeypatch, shape, dtype):
    source = io.BytesIO(checkpoint[2].read_bytes())
    forged = io.BytesIO()
    header = io.BytesIO()
    np.lib.format.write_array_header_1_0(header, {
        "descr": dtype, "fortran_order": False, "shape": shape,
    })
    replaced = "manifest.npy" if shape == () else "model/head.weight.npy"
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(forged, "w") as target:
        for member in original.infolist():
            target.writestr(member.filename, header.getvalue() if member.filename == replaced
                            else original.read(member.filename))

    def forbidden(*args, **kwargs):
        pytest.fail("NPY array loading happened before header validation")

    monkeypatch.setattr("src.infrastructure.model_interchange.np.load", forbidden)
    with pytest.raises(ValueError, match="header shape/dtype"):
        load_inference_checkpoint(forged.getvalue())


def test_publish_is_hash_named_and_idempotent(checkpoint, tmp_path):
    forward = translate_model(checkpoint[2].read_bytes(), source_format="p43_npz",
                              target_format="azmq", allow_lossy=True)
    first = forward.publish(tmp_path)
    assert forward.publish(tmp_path) == first
    for value in first.values():
        path = Path(value)
        assert path.stem == hashlib.sha256(path.read_bytes()).hexdigest()


def test_cli_runs_both_actual_format_directions(checkpoint, tmp_path, capsys):
    _, _, path = checkpoint
    assert main(["--source", str(path), "--source-format", "p43_npz", "--target-format", "azmq",
                 "--allow-lossy", "--output-dir", str(tmp_path)]) == 0
    forward = json.loads(capsys.readouterr().out)
    assert main(["--source", forward["model"], "--source-format", "azmq", "--target-format", "p43_npz",
                 "--tokenizer", forward["tokenizer"], "--output-dir", str(tmp_path)]) == 0
    reverse = json.loads(capsys.readouterr().out)
    assert load_inference_checkpoint(Path(reverse["model"]).read_bytes()).model.cfg.vocab_size == 4
    assert json.loads(Path(reverse["manifest"]).read_bytes())["semantics"]["token_id_mapping_preserved"]
