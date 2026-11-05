# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Supported mapping preservation, not universal segmentation conversion."""

import hashlib
import itertools
import json
from pathlib import Path

import pytest

from src.infrastructure.tokenizer_interchange import (
    CharacterTokenizer, UnsupportedTokenizerError, canonical_json,
    conversion_receipt, convert_document, export_p43_tokenizer, import_p43_tokenizer,
    main, parse_document,
)


def test_unicode_scalar_roundtrip_preserves_id_order_and_identity_normalization():
    tokenizer = CharacterTokenizer(("é", "e", "\u0301", "🙂", "\x00", "\n"))
    text = "é" + "e\u0301" + "🙂\x00\n"
    assert tokenizer.encode(text) == (0, 1, 2, 3, 4, 5)
    assert tokenizer.decode(tokenizer.encode(text)) == text
    assert tokenizer.encode("é") != tokenizer.encode("e\u0301")
    assert CharacterTokenizer.from_dict(tokenizer.to_dict()) == tokenizer


def test_two_serializations_preserve_all_supported_short_strings():
    tokenizer = CharacterTokenizer(("β", "a", "\n"))
    source = canonical_json(export_p43_tokenizer(tokenizer))
    target = convert_document(source, source_format="p43_metadata", target_format="az_character")
    restored = CharacterTokenizer.from_dict(parse_document(target))
    for length in range(5):
        for chars in itertools.product(tokenizer.vocabulary, repeat=length):
            text = "".join(chars)
            assert restored.encode(text) == tokenizer.encode(text)
            assert restored.decode(restored.encode(text)) == text
    assert convert_document(target, source_format="az_character", target_format="p43_metadata") == source
    assert conversion_receipt(source, target, source_format="p43_metadata",
                              target_format="az_character")["promotion"]["eligible"] is False


@pytest.mark.parametrize("vocabulary", [(), ("a", "a"), ("ab",), ("\ud800",), ("",), (True,), ["a"]])
def test_invalid_vocabulary_fails(vocabulary):
    with pytest.raises(ValueError):
        CharacterTokenizer(vocabulary)


@pytest.mark.parametrize("tokens", [(True,), (-1,), (1,), (0.0,), [0]])
def test_invalid_ids_fail_without_lossy_replacement(tokens):
    with pytest.raises(ValueError):
        CharacterTokenizer(("a",)).decode(tokens)


def test_unknown_character_is_explicit_error_not_an_unknown_replacement():
    with pytest.raises(ValueError, match="unknown"):
        CharacterTokenizer(("a",)).encode("b")


@pytest.mark.parametrize("key,value", [
    ("normalization", "NFC"), ("special_tokens", ["<eos>"]),
    ("algorithm", "bpe"), ("unknown_policy", "replace"),
    ("pretokenization", "whitespace"), ("merges", []),
])
def test_semantic_changes_rejected(key, value):
    payload = CharacterTokenizer(("a",)).to_dict()
    payload[key] = value
    with pytest.raises(UnsupportedTokenizerError):
        CharacterTokenizer.from_dict(payload)


def test_both_actual_p43_metadata_dialects_preserve_mapping():
    expected = CharacterTokenizer(("b", "a", "🙂"))
    assert import_p43_tokenizer(export_p43_tokenizer(expected), vocab_size=3) == expected
    assert import_p43_tokenizer({
        "task": "local_research_arithmetic_fixture",
        "tokenizer": {"algorithm": "sorted Unicode code points", "vocabulary": ["b", "a", "🙂"]},
    }, vocab_size=3) == expected
    with pytest.raises(ValueError, match="vocab_size"):
        import_p43_tokenizer(export_p43_tokenizer(expected), vocab_size=4)
    with pytest.raises(UnsupportedTokenizerError):
        import_p43_tokenizer({"tokenizer": "bpe", "vocabulary": ["a"]}, vocab_size=1)


@pytest.mark.parametrize("key", [
    "added_tokens", "added_special_tokens", "special_tokens", "post_processor",
    "bos_token", "eos_token", "unk_token", "pad_token", "special_tokens_map",
])
def test_p43_special_token_overrides_cannot_be_silently_discarded(key):
    with pytest.raises(UnsupportedTokenizerError, match="overrides"):
        import_p43_tokenizer({
            "tokenizer": "unicode_codepoint", "vocabulary": ["a"], key: ["<eos>"],
        }, vocab_size=1)


@pytest.mark.parametrize("content", [
    b'{"a":1,"a":2}', b'{"a":NaN}', b"[]", b"\xff",
])
def test_json_is_strict(content):
    with pytest.raises(ValueError):
        parse_document(content)


def test_unsupported_format_and_inexact_target_fail():
    content = canonical_json(CharacterTokenizer(("a",)).to_dict())
    with pytest.raises(UnsupportedTokenizerError):
        convert_document(content, source_format="az_character", target_format="sentencepiece")
    with pytest.raises(ValueError, match="target bytes"):
        conversion_receipt(content, b"{}", source_format="az_character", target_format="az_character")


def test_cli_publishes_actual_target_and_receipt_under_full_byte_hashes(tmp_path, capsys):
    path = tmp_path / "source.json"
    path.write_bytes(canonical_json(export_p43_tokenizer(CharacterTokenizer(("a", "\n")))))
    assert main(["--source", str(path), "--source-format", "p43_metadata",
                 "--target-format", "az_character", "--output-dir", str(tmp_path)]) == 0
    result = json.loads(capsys.readouterr().out)
    for name in ("tokenizer", "receipt"):
        output = Path(result[name])
        assert output.stem == hashlib.sha256(output.read_bytes()).hexdigest()
    assert json.loads(Path(result["receipt"]).read_bytes())["promotion"]["eligible"] is False
