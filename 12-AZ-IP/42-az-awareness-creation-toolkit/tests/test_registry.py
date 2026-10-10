# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_awareness_creation_toolkit.registry import (
    ProductRecord,
    get_product,
    load_product_registry,
    route_capability_request,
)


def test_load_product_registry_finds_all_products():
    records = load_product_registry()
    assert len(records) >= 41
    assert all(isinstance(record, ProductRecord) for record in records)
    numbers = [record.number for record in records]
    assert numbers == sorted(numbers)
    assert numbers[0] == 1


def test_records_have_well_formed_fields():
    records = load_product_registry()
    media_suite = next(record for record in records if record.number == 41)
    assert media_suite.name == "AZ Media & Feature-Inspection Suite"
    assert media_suite.folder == "41-az-media-suite/"
    assert media_suite.tests == "28"


def test_get_product_by_number():
    record = get_product(41)
    assert record is not None
    assert record.number == 41


def test_get_product_by_name_substring():
    record = get_product("media suite")
    assert record is not None
    assert record.number == 41


def test_get_product_missing_returns_none():
    assert get_product(9999) is None
    assert get_product("no such product at all") is None


def test_route_capability_request_finds_media_suite():
    results = route_capability_request("comic video audio media", limit=5)
    assert results
    top = results[0]["product"]
    assert top["number"] == 41
    assert "comic" in results[0]["matched_terms"]


def test_route_capability_request_name_match_scores_higher():
    results = route_capability_request("Falsification Observatory", limit=5)
    assert results
    assert results[0]["product"]["number"] == 19


def test_route_capability_request_no_terms_returns_limited_list():
    results = route_capability_request("   ", limit=3)
    assert len(results) == 3
    assert all(result["score"] == 0 for result in results)


def test_route_capability_request_no_match_returns_empty():
    assert route_capability_request("zzzznonexistentzzzz") == []


def test_product_record_as_dict_roundtrip():
    record = get_product(41)
    data = record.as_dict()
    assert data["number"] == 41
    assert set(data.keys()) == {
        "number", "name", "version", "trl", "port", "tests", "description", "folder",
    }
