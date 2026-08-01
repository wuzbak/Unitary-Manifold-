from __future__ import annotations

import hashlib

import pytest

from src.core.pillar582_desi_dr3_preregistration_v2 import (
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PREREGISTRATION_HASH,
    PREREGISTRATION_STRING,
    VERSION,
    desi_decision_timeline,
    hash_verification,
    pillar_report,
    preregistration_record,
    v1_to_v2_upgrade,
)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("PILLAR_NUMBER", PILLAR_NUMBER),
        ("PILLAR_STATUS", PILLAR_STATUS),
        ("VERSION", VERSION),
        ("PREREGISTRATION_STRING", PREREGISTRATION_STRING),
        ("PREREGISTRATION_HASH", PREREGISTRATION_HASH),
    ],
)
def test_constants_are_present(label, value):
    assert value is not None, label


def test_constant_values_are_exact():
    assert PILLAR_NUMBER == 582
    assert PILLAR_STATUS == "DESI_DR3_PREREGISTRATION_V2_CERTIFIED"
    assert VERSION == "v20.1"
    assert PREREGISTRATION_STRING.startswith("DESI_DR3_PREREGISTRATION_V2|")
    assert len(PREREGISTRATION_HASH) == 64


@pytest.mark.parametrize(
    "fragment",
    [
        "w0=-1.0",
        "wa=0.0",
        "sigma_falsified=3.0",
        "sigma_pass=2.0",
        "euclid_w0_window=0.05",
        "euclid_wa_window=0.3",
        "hyperK_nmo_coupling=True",
        "spherex_fnl=True",
        "date=2026-08-01",
    ],
)
def test_preregistration_string_contains_required_fragments(fragment):
    assert fragment in PREREGISTRATION_STRING


def test_hash_matches_direct_hashlib_computation():
    assert PREREGISTRATION_HASH == hashlib.sha256(PREREGISTRATION_STRING.encode()).hexdigest()


@pytest.mark.parametrize(
    "key",
    ["version", "string", "hash", "hash_algorithm", "all_three_branches_locked", "date"],
)
def test_preregistration_record_keys(key):
    record = preregistration_record()
    assert key in record


def test_preregistration_record_values():
    record = preregistration_record()
    assert record["version"] == "v2"
    assert record["string"] == PREREGISTRATION_STRING
    assert record["hash"] == PREREGISTRATION_HASH
    assert record["hash_algorithm"] == "sha256"
    assert record["all_three_branches_locked"] is True
    assert record["date"] == "2026-08-01"


@pytest.mark.parametrize("key", ["stored_hash", "recomputed_hash", "match"])
def test_hash_verification_keys(key):
    verification = hash_verification()
    assert key in verification


def test_hash_verification_values():
    verification = hash_verification()
    assert verification["stored_hash"] == PREREGISTRATION_HASH
    assert verification["recomputed_hash"] == PREREGISTRATION_HASH
    assert verification["match"] is True


@pytest.mark.parametrize(
    "key",
    ["from_version", "to_version", "v1_source", "v2_hash", "new_items", "canonical_now"],
)
def test_v1_to_v2_upgrade_keys(key):
    upgrade = v1_to_v2_upgrade()
    assert key in upgrade


def test_v1_to_v2_upgrade_values():
    upgrade = v1_to_v2_upgrade()
    assert upgrade["from_version"] == "v1"
    assert upgrade["to_version"] == "v2"
    assert upgrade["v1_source"] == "Pillar 467"
    assert upgrade["v2_hash"] == PREREGISTRATION_HASH
    assert upgrade["canonical_now"] is True
    assert len(upgrade["new_items"]) == 4


@pytest.mark.parametrize(
    "addition",
    [
        "Explicit Euclid cross-check protocol",
        "Extension-branch activation criteria",
        "Hyper-K NMO coupling",
        "SPHEREx f_NL coupling",
    ],
)
def test_v1_to_v2_upgrade_lists_all_additions(addition):
    upgrade = v1_to_v2_upgrade()
    assert addition in upgrade["new_items"]


@pytest.mark.parametrize(
    "key",
    [
        "preregistration_lock_date",
        "expected_dr3_window",
        "year5_projection_context",
        "future_cross_checks",
        "v2_hash",
    ],
)
def test_desi_decision_timeline_keys(key):
    timeline = desi_decision_timeline()
    assert key in timeline


def test_desi_decision_timeline_values():
    timeline = desi_decision_timeline()
    assert timeline["preregistration_lock_date"] == "2026-08-01"
    assert "2026-2027" in timeline["expected_dr3_window"]
    assert "3.64σ" in timeline["year5_projection_context"]
    assert timeline["future_cross_checks"] == ["Euclid", "Hyper-K", "SPHEREx"]
    assert timeline["v2_hash"] == PREREGISTRATION_HASH


@pytest.mark.parametrize(
    "key",
    [
        "pillar",
        "title",
        "status",
        "version",
        "preregistration_record",
        "hash_verification",
        "v1_to_v2_upgrade",
        "desi_decision_timeline",
    ],
)
def test_pillar_report_keys(key):
    report = pillar_report()
    assert key in report


def test_pillar_report_values():
    report = pillar_report()
    assert report["pillar"] == 582
    assert report["preregistration_record"]["hash"] == PREREGISTRATION_HASH
    assert report["hash_verification"]["match"] is True
    assert report["v1_to_v2_upgrade"]["to_version"] == "v2"
    assert report["desi_decision_timeline"]["v2_hash"] == PREREGISTRATION_HASH
