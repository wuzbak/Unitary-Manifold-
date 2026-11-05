# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Bounded P43 NPZ/AZMQ inference interchange, with explicit lossy opt-in."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
import zipfile

import numpy as np

from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance
from .research_quantization import (
    _p43_api, _validate_model_size, load_model_artifact, serialize_model,
)
from .tokenizer_interchange import (
    CharacterTokenizer, canonical_json, export_p43_tokenizer,
    import_p43_tokenizer, parse_document,
)
_p43_api()
from az_tori_transformer.checkpoint import load_checkpoint, save_checkpoint

MAX_MODEL_BYTES = 16 * 1024 * 1024
MAX_EXPANDED_BYTES = 32 * 1024 * 1024
SCHEMA = "az_p43_inference_translation_v1"
ROOT = Path(__file__).resolve().parents[2]
SOURCE_FILES = (
    "src/infrastructure/model_interchange.py",
    "src/infrastructure/tokenizer_interchange.py",
    "src/infrastructure/research_quantization.py",
    "src/infrastructure/lowbit_quantization.py",
    "src/infrastructure/artifact_io.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/checkpoint.py",
    "12-AZ-IP/43-az-geometric-tori-transformer/az_tori_transformer/model.py",
)


def _read_model(path: Path) -> bytes:
    with path.open("rb") as stream:
        content = stream.read(MAX_MODEL_BYTES + 1)
    if len(content) > MAX_MODEL_BYTES:
        raise ValueError("model exceeds the interchange input byte limit")
    return content


def load_inference_checkpoint(content: bytes):
    """Preflight bounded NPZ bytes before invoking the existing model constructor."""
    if not isinstance(content, bytes) or len(content) > MAX_MODEL_BYTES:
        raise ValueError("checkpoint must be bytes within the interchange size limit")
    try:
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            members = archive.infolist()
            if (not members or len(members) > 1024
                    or len({member.filename for member in members}) != len(members)
                    or sum(member.file_size for member in members) > MAX_EXPANDED_BYTES
                    or any(member.file_size > MAX_MODEL_BYTES for member in members)):
                raise ValueError("NPZ exceeds member or expanded-size limits")
            manifest_members = [member for member in members if member.filename == "manifest.npy"]
            if len(manifest_members) != 1 or manifest_members[0].file_size > 1024 * 1024:
                raise ValueError("NPZ must contain one bounded manifest")
            for member in members:
                with archive.open(member) as stream:
                    version = np.lib.format.read_magic(stream)
                    if version == (1, 0):
                        shape, _, dtype = np.lib.format.read_array_header_1_0(stream)
                    elif version == (2, 0):
                        shape, _, dtype = np.lib.format.read_array_header_2_0(stream)
                    else:
                        raise ValueError("unsupported NPY header version")
                    if any(type(size) is not int or size < 0 for size in shape):
                        raise ValueError("invalid NPY shape")
                    if dtype.hasobject or dtype.fields is not None:
                        raise ValueError("object and structured NPY arrays are unsupported")
                    payload_size = math.prod(shape) * dtype.itemsize
                    if payload_size > MAX_MODEL_BYTES or stream.tell() + payload_size != member.file_size:
                        raise ValueError("NPY header shape/dtype does not match bounded member bytes")
                    if member.filename == "manifest.npy" and (shape != () or dtype.kind != "U"):
                        raise ValueError("NPZ manifest must be scalar JSON text")
                    if member.filename != "manifest.npy" and dtype != np.float64:
                        raise ValueError("NPZ model/state arrays must be float64")
        with np.load(io.BytesIO(content), allow_pickle=False) as archive:
            raw = archive["manifest"]
            if raw.shape != () or raw.dtype.kind != "U":
                raise ValueError("NPZ manifest must be scalar JSON text")
            manifest = parse_document(raw.item().encode("utf-8"))
            if manifest.get("optimizer") is not None or manifest.get("rng") is not None:
                raise ValueError("inference translation refuses optimizer/RNG state; use the training checkpoint path")
            arrays = [archive[name] for name in archive.files if name.startswith("model/")]
            if any(array.dtype != np.float64 or not np.all(np.isfinite(array)) for array in arrays):
                raise ValueError("checkpoint model weights must be finite float64")
            _validate_model_size(manifest.get("config"), sum(array.size for array in arrays))
        # Load the exact inspected bytes, not a path that could have changed.
        return load_checkpoint(io.BytesIO(content))
    except (zipfile.BadZipFile, KeyError, TypeError, EOFError) as exc:
        raise ValueError("invalid bounded P43 inference checkpoint") from exc


def _save_inference_npz(model, tokenizer: CharacterTokenizer, provenance: dict[str, object]) -> bytes:
    with tempfile.TemporaryDirectory(prefix="az-inference-translation-") as directory:
        target = Path(directory) / "model.npz"
        save_checkpoint(target, model, metadata={
            **export_p43_tokenizer(tokenizer),
            "task": "translated_inference_model", "translation": provenance,
        })
        return _read_model(target)


@dataclass(frozen=True)
class TranslationResult:
    model: bytes
    tokenizer: bytes
    manifest: bytes
    model_suffix: str

    def publish(self, directory: str | Path) -> dict[str, str]:
        paths = {}
        for label, content, suffix in (
            ("model", self.model, self.model_suffix),
            ("tokenizer", self.tokenizer, ".json"),
            ("manifest", self.manifest, ".json"),
        ):
            paths[label] = str(publish_immutable(directory, hashlib.sha256(content).hexdigest(),
                                                 content, suffix=suffix))
        return paths


def translate_model(
    source: bytes, *, source_format: str, target_format: str,
    tokenizer: CharacterTokenizer | None = None, allow_lossy: bool = False,
    bit_width: int = 3, group_size: int = 4096,
) -> TranslationResult:
    """Own supported format conversion, not universal architecture translation."""
    if type(allow_lossy) is not bool:
        raise ValueError("allow_lossy must be boolean")
    if (source_format, target_format) not in {("p43_npz", "azmq"), ("azmq", "p43_npz")}:
        raise ValueError("only p43_npz -> azmq and azmq -> p43_npz are supported")
    if not isinstance(source, bytes) or len(source) > MAX_MODEL_BYTES:
        raise ValueError("source must be bytes within the interchange size limit")
    if source_format == "p43_npz":
        if not allow_lossy:
            raise ValueError("quantization changes weights; explicit allow_lossy=True is required")
        loaded = load_inference_checkpoint(source)
        model = loaded.model
        imported = import_p43_tokenizer(loaded.metadata, vocab_size=model.cfg.vocab_size)
        if tokenizer is not None and tokenizer != imported:
            raise ValueError("provided tokenizer conflicts with checkpoint token-ID mapping")
        tokenizer = imported
    else:
        if not isinstance(tokenizer, CharacterTokenizer):
            raise ValueError("AZMQ has no tokenizer; an explicit canonical tokenizer is required")
        if allow_lossy:
            raise ValueError("AZMQ -> NPZ adds no weight loss; do not label it as quantization")
        model = load_model_artifact(source)
        if len(tokenizer.vocabulary) != model.cfg.vocab_size:
            raise ValueError("tokenizer vocabulary does not match model vocab_size")
    if tokenizer is None:
        raise RuntimeError("supported model conversion has no tokenizer mapping")
    source_hash = hashlib.sha256(source).hexdigest()
    tokenizer_bytes = canonical_json(tokenizer.to_dict())
    provenance = {
        "source_sha256": source_hash, "source_format": source_format,
        "target_format": target_format, "tokenizer_sha256": tokenizer.identity,
        "tokenizer_provenance": (
            "checkpoint metadata" if source_format == "p43_npz"
            else "caller-supplied; vocabulary size verified, original semantic binding not authenticated"
        ),
    }
    if target_format == "azmq":
        target = serialize_model(model, bit_width=bit_width, group_size=group_size)
        restored = load_model_artifact(target)
        suffix = ".azmq"
    else:
        target = _save_inference_npz(model, tokenizer, provenance)
        restored_checkpoint = load_inference_checkpoint(target)
        restored = restored_checkpoint.model
        if import_p43_tokenizer(restored_checkpoint.metadata, vocab_size=restored.cfg.vocab_size) != tokenizer:
            raise RuntimeError("translated tokenizer mapping did not round-trip")
        suffix = ".npz"
    maximum_error = 0.0
    squared_error = 0.0
    count = 0
    for (name, original), (restored_name, candidate) in zip(
        model.named_parameters().items(), restored.named_parameters().items(), strict=True,
    ):
        if name != restored_name or original.shape != candidate.shape:
            raise RuntimeError("translated parameter schema changed")
        difference = original.data - candidate.data
        maximum_error = max(maximum_error, float(np.max(np.abs(difference))))
        squared_error += float(np.sum(difference * difference))
        count += difference.size
    if target_format == "p43_npz" and maximum_error != 0:
        raise ValueError("NPZ reserialization changed reconstructed weights")
    payload = {
        "schema_version": SCHEMA, **provenance,
        "source_bytes": len(source), "target_bytes": len(target),
        "target_sha256": hashlib.sha256(target).hexdigest(),
        "implementation_sha256": {
            path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in SOURCE_FILES
        },
        "model_config": asdict(restored.cfg), "parameter_count": count,
        "weight_conversion": {
            "additional_loss": target_format == "azmq",
            "allow_lossy": allow_lossy, "max_absolute_weight_error": maximum_error,
            "mean_squared_weight_error": squared_error / count,
            "target_complete_bits_per_parameter": 8 * len(target) / count,
            "bit_width": bit_width if target_format == "azmq" else None,
            "group_size": group_size if target_format == "azmq" else None,
        },
        "semantics": {
            "architecture_preserved": True, "token_id_mapping_preserved": True,
            "optimizer_or_rng_translated": False,
            "original_prequantization_weights_restored": False if source_format == "azmq" else None,
            "task_metadata_preserved": False, "quality_measured": False, "runtime_optimized": False,
        },
        "output_filenames": {
            "model": hashlib.sha256(target).hexdigest() + suffix,
            "tokenizer": tokenizer.identity + ".json",
        },
    }
    payload["execution_spine"] = ExecutionSpineRecord(
        surface_id="az-p43-inference-translation", surface_kind="model_translation_receipt",
        lane="az_ml_infrastructure", status="bounded_conversion_verified",
        summary="Supported P43 inference model conversion with explicit weight loss and tokenizer mapping.",
        canonical_paths=["src/infrastructure/model_interchange.py"],
        governance=build_fail_closed_governance(
            epistemic_label="bounded format interchange, not model optimization or quality",
            promotion_rule="No promotion from serialization or weight-fidelity verification.",
            residual_blockers=[
                "Only P43 float64 NPZ and AZMQ supported; no ONNX, GGUF, external architecture or accelerator qualification.",
                "Quantization is lossy; reserialization cannot recover original weights.",
                "Caller-supplied AZMQ tokenizer mapping is an assertion, not authenticated model provenance.",
                "Published files are individually atomic, not one bundle transaction.",
            ],
        ),
        compatibility=provenance,
        promotion={"eligible": False, "model_quality_claim": False, "physics_claim": False},
    ).to_dict()
    return TranslationResult(target, tokenizer_bytes, canonical_json(payload), suffix)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-format", choices=("p43_npz", "azmq"), required=True)
    parser.add_argument("--target-format", choices=("p43_npz", "azmq"), required=True)
    parser.add_argument("--tokenizer", type=Path, help="canonical character tokenizer required for AZMQ")
    parser.add_argument("--allow-lossy", action="store_true")
    parser.add_argument("--bit-width", type=int, default=3)
    parser.add_argument("--group-size", type=int, default=4096)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        tokenizer = None
        if args.tokenizer is not None:
            with args.tokenizer.open("rb") as stream:
                tokenizer = CharacterTokenizer.from_dict(parse_document(stream.read(1024 * 1024 + 1)))
        translated = translate_model(
            _read_model(args.source), source_format=args.source_format, target_format=args.target_format,
            tokenizer=tokenizer, allow_lossy=args.allow_lossy,
            bit_width=args.bit_width, group_size=args.group_size,
        )
        print(json.dumps(translated.publish(args.output_dir), sort_keys=True))
    except (OSError, ValueError, TypeError, OverflowError) as exc:
        parser.exit(1, f"Model conversion failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
