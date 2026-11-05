# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Exact interchange for supported Unicode-scalar character tokenizers only."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .artifact_io import publish_immutable
from .execution_spine import ExecutionSpineRecord, build_fail_closed_governance

SCHEMA = "az_character_tokenizer_v1"
MAX_VOCABULARY = 4096
MAX_DOCUMENT_BYTES = 1024 * 1024


class UnsupportedTokenizerError(ValueError):
    """Source semantics cannot be preserved by this supported representation."""


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"nonfinite JSON value: {value}")


def parse_document(content: bytes) -> dict[str, object]:
    if not isinstance(content, bytes) or len(content) > MAX_DOCUMENT_BYTES:
        raise ValueError("tokenizer JSON must be bytes within the document limit")
    try:
        payload = json.loads(content.decode("utf-8"), object_pairs_hook=_unique_pairs,
                             parse_constant=_reject_constant)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError("invalid tokenizer JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("tokenizer document must be a JSON object")
    return payload


@dataclass(frozen=True)
class CharacterTokenizer:
    """Identity normalization, no added/special tokens, unknown scalars rejected."""

    vocabulary: tuple[str, ...]

    def __post_init__(self) -> None:
        if (not isinstance(self.vocabulary, tuple) or not 1 <= len(self.vocabulary) <= MAX_VOCABULARY
                or any(type(char) is not str or len(char) != 1
                       or 0xD800 <= ord(char) <= 0xDFFF for char in self.vocabulary)
                or len(set(self.vocabulary)) != len(self.vocabulary)):
            raise ValueError("vocabulary must contain unique Unicode scalars in token-ID order")

    def encode(self, text: str) -> tuple[int, ...]:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        mapping = {char: index for index, char in enumerate(self.vocabulary)}
        try:
            return tuple(mapping[char] for char in text)
        except KeyError as exc:
            raise ValueError(f"unknown Unicode scalar: {exc.args[0]!r}") from exc

    def decode(self, tokens: tuple[int, ...]) -> str:
        if not isinstance(tokens, tuple) or any(
            type(token) is not int or not 0 <= token < len(self.vocabulary) for token in tokens
        ):
            raise ValueError("token IDs must be a tuple of vocabulary integers")
        return "".join(self.vocabulary[token] for token in tokens)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA, "algorithm": "unicode_scalar_character",
            "normalization": "identity", "pretokenization": "none", "special_tokens": [],
            "unknown_policy": "error", "vocabulary": list(self.vocabulary),
        }

    @property
    def identity(self) -> str:
        return hashlib.sha256(canonical_json(self.to_dict())).hexdigest()

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> CharacterTokenizer:
        if not isinstance(payload, dict):
            raise ValueError("canonical tokenizer must be an object")
        expected = {
            "schema_version": SCHEMA, "algorithm": "unicode_scalar_character",
            "normalization": "identity", "pretokenization": "none",
            "special_tokens": [], "unknown_policy": "error",
        }
        if set(payload) != set(expected) | {"vocabulary"}:
            raise UnsupportedTokenizerError("unknown or missing tokenizer semantics")
        if any(payload[key] != value for key, value in expected.items()):
            raise UnsupportedTokenizerError("unsupported algorithm, normalization, special-token or unknown semantics")
        if not isinstance(payload["vocabulary"], list):
            raise ValueError("vocabulary must be a token-ID-ordered list")
        return cls(tuple(payload["vocabulary"]))


def import_p43_tokenizer(metadata: dict[str, object], *, vocab_size: int) -> CharacterTokenizer:
    """Read the two actual P43 metadata layouts without guessing token semantics."""
    if not isinstance(metadata, dict) or type(vocab_size) is not int or vocab_size < 1:
        raise ValueError("metadata and positive integer vocab_size are required")
    semantic_keys = {"normalizer", "normalization", "pretokenizer", "pretokenization",
                     "special_tokens", "added_tokens", "added_special_tokens",
                     "special_tokens_map", "added_tokens_decoder", "post_processor",
                     "decoder", "bos_token", "eos_token", "unk_token", "pad_token",
                     "unknown_policy", "merges"}
    if semantic_keys.intersection(metadata):
        raise UnsupportedTokenizerError("P43 metadata contains unsupported tokenizer overrides")
    descriptor = metadata.get("tokenizer")
    if descriptor == "unicode_codepoint":
        vocabulary = metadata.get("vocabulary")
    elif isinstance(descriptor, dict):
        if set(descriptor) != {"algorithm", "vocabulary"} or descriptor["algorithm"] != "sorted Unicode code points":
            raise UnsupportedTokenizerError("unsupported P43 tokenizer descriptor")
        vocabulary = descriptor["vocabulary"]
        if "vocabulary" in metadata and metadata["vocabulary"] != vocabulary:
            raise UnsupportedTokenizerError("conflicting P43 vocabulary declarations")
    else:
        raise UnsupportedTokenizerError("P43 tokenizer algorithm must be explicitly supported")
    if not isinstance(vocabulary, list):
        raise ValueError("P43 vocabulary must be a token-ID-ordered list")
    tokenizer = CharacterTokenizer(tuple(vocabulary))
    if len(tokenizer.vocabulary) != vocab_size:
        raise ValueError("tokenizer vocabulary does not match model vocab_size")
    return tokenizer


def export_p43_tokenizer(tokenizer: CharacterTokenizer) -> dict[str, object]:
    if not isinstance(tokenizer, CharacterTokenizer):
        raise TypeError("tokenizer must be CharacterTokenizer")
    return {"tokenizer": "unicode_codepoint", "vocabulary": list(tokenizer.vocabulary)}


def convert_document(content: bytes, *, source_format: str, target_format: str) -> bytes:
    supported = {"az_character", "p43_metadata"}
    if source_format not in supported or target_format not in supported:
        raise UnsupportedTokenizerError("supported formats are az_character and p43_metadata only")
    source = parse_document(content)
    if source_format == "az_character":
        tokenizer = CharacterTokenizer.from_dict(source)
    else:
        if set(source) != {"tokenizer", "vocabulary"}:
            raise UnsupportedTokenizerError("standalone P43 tokenizer document must contain exactly tokenizer and vocabulary")
        vocabulary = source["vocabulary"]
        if not isinstance(vocabulary, list):
            raise ValueError("P43 vocabulary must be a list")
        tokenizer = import_p43_tokenizer(source, vocab_size=len(vocabulary))
    target = tokenizer.to_dict() if target_format == "az_character" else export_p43_tokenizer(tokenizer)
    restored = (CharacterTokenizer.from_dict(target) if target_format == "az_character"
                else import_p43_tokenizer(target, vocab_size=len(tokenizer.vocabulary)))
    if restored != tokenizer:
        raise RuntimeError("supported conversion did not preserve the token-ID mapping")
    return canonical_json(target)


def conversion_receipt(source: bytes, target: bytes, *, source_format: str, target_format: str) -> dict[str, object]:
    expected = convert_document(source, source_format=source_format, target_format=target_format)
    if target != expected:
        raise ValueError("target bytes do not match the declared conversion")
    return ExecutionSpineRecord(
        surface_id="az-character-tokenizer-conversion", surface_kind="tokenizer_conversion_receipt",
        lane="az_ml_infrastructure", status="supported_conversion_verified",
        summary="Exact Unicode-scalar vocabulary and token-ID preservation for bounded supported formats.",
        canonical_paths=["src/infrastructure/tokenizer_interchange.py"],
        governance=build_fail_closed_governance(
            epistemic_label="supported character tokenizer serialization",
            promotion_rule="No universal tokenizer, external-library or model-quality qualification.",
            residual_blockers=[
                "No BPE, SentencePiece, learned segmentation, normalization changes or added tokens supported.",
                "Lossless mapping preservation is not preservation of arbitrary original JSON bytes.",
            ],
        ),
        compatibility={
            "source_format": source_format, "target_format": target_format,
            "source_sha256": hashlib.sha256(source).hexdigest(),
            "target_sha256": hashlib.sha256(target).hexdigest(),
            "mapping_preserved": True,
            "implementation_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "encode_domain": "All finite strings over the preserved vocabulary; unknown scalars fail.",
        },
        promotion={"eligible": False, "physics_claim": False},
    ).to_dict()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--source-format", choices=("az_character", "p43_metadata"), required=True)
    parser.add_argument("--target-format", choices=("az_character", "p43_metadata"), required=True)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        with args.source.open("rb") as stream:
            source = stream.read(MAX_DOCUMENT_BYTES + 1)
        target = convert_document(source, source_format=args.source_format, target_format=args.target_format)
        receipt = conversion_receipt(source, target, source_format=args.source_format, target_format=args.target_format)
        path = publish_immutable(args.output_dir, hashlib.sha256(target).hexdigest(), target)
        receipt_content = canonical_json(receipt)
        receipt_path = publish_immutable(args.output_dir, hashlib.sha256(receipt_content).hexdigest(), receipt_content)
        print(json.dumps({"tokenizer": str(path), "receipt": str(receipt_path)}))
    except (OSError, ValueError, TypeError) as exc:
        parser.exit(1, f"Tokenizer conversion failed: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
