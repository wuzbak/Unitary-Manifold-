# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Independent source counts, controls, and provenance mutation regressions."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

import pytest

from src.neuroscience import empirical_benchmark as benchmark


@pytest.fixture
def partner_tables():
    return [
        benchmark.parse_partner_table_html(
            (benchmark.FIXTURE_DIRECTORY / f"lplc2_{direction}_table.html").read_text(
                encoding="utf-8"
            )
        )
        for direction in ("upstream", "downstream")
    ]


def test_independent_published_attribute_counts():
    """Reference extraction does not use the production parser or panel JSON."""
    weights = []
    for direction, count, mass, top5 in (
        ("upstream", 536, 350542, 127817),
        ("downstream", 692, 182982, 86491),
    ):
        contents = (
            benchmark.FIXTURE_DIRECTORY / f"lplc2_{direction}_table.html"
        ).read_bytes()
        assert hashlib.sha256(contents).hexdigest() == benchmark.SNAPSHOT_SHA256[direction]
        text = contents.decode("utf-8")
        names = re.findall(r"<a href=[^>]+>([^<]+)</a>", text)
        masses = [
            int(value.replace(",", ""))
            for value in re.findall(r"∑ connections: ([0-9,]+)", text)
        ]
        assert len(names) == len(masses) == len(set(names)) == count
        assert sum(masses) == mass
        assert sum(sorted(masses, reverse=True)[:5]) == top5
        assert dict(zip(names, masses))["LPLC2"] == 46178
        weights.append(dict(zip(names, masses)))
    assert len(weights[0].keys() & weights[1].keys()) == 440
    assert len(weights[0].keys() | weights[1].keys()) == 788


def test_offline_reproduction():
    report = benchmark.reproduce_lplc2_source_summary()
    assert report["reproduced"] is True
    assert report["observed"] == report["expected"] == {
        "upstream_partner_types": 536,
        "downstream_partner_types": 692,
        "input_synapses": 350542,
        "output_synapses": 182982,
        "reciprocal_partner_types": 440,
        "union_partner_types": 788,
        "top5_input_synapses": 127817,
        "top5_output_synapses": 86491,
        "same_type_input_synapses": 46178,
        "same_type_output_synapses": 46178,
        "roi_rows": 8,
    }
    assert report["mismatches"] == report["panel_mismatches"] == {}
    assert report["claim_class"] == "published_source_summary_reproduction"
    assert report["provenance"]["full_page_hash_verified"] is False
    assert report["provenance"]["new_external_data_copied"] is False
    assert len(report["provenance"]["verified_extract_sha256"]) == 3
    assert any("Gardner" in limit and "pending" in limit for limit in report["limits"])
    assert any("experimental replication remain pending" in limit for limit in report["limits"])


def test_result_does_not_depend_on_working_directory(monkeypatch):
    monkeypatch.chdir(benchmark.FIXTURE_DIRECTORY)
    assert benchmark.reproduce_lplc2_source_summary()["reproduced"]


def test_report_returns_detached_expected_and_provenance():
    report = benchmark.reproduce_lplc2_source_summary()
    report["expected"]["input_synapses"] = 0
    report["provenance"]["verified_extract_sha256"]["roi"] = "bad"
    assert benchmark.reproduce_lplc2_source_summary()["reproduced"]


@pytest.mark.parametrize("direction", ["upstream", "downstream", "roi"])
def test_snapshot_byte_mutations_fail_closed(monkeypatch, direction):
    read_bytes = Path.read_bytes
    target = f"lplc2_{direction}_table.html"

    def mutated_bytes(path):
        contents = read_bytes(path)
        return contents + b" " if path.name == target else contents

    monkeypatch.setattr(Path, "read_bytes", mutated_bytes)
    with pytest.raises(ValueError, match="snapshot SHA-256 mismatch"):
        benchmark.reproduce_lplc2_source_summary()


@pytest.mark.parametrize(
    "field,value",
    [
        ("dataset", "female-cns:v1.0"),
        ("dataset_uuid", "different-release"),
        ("source_url", "https://example.org/LPLC2.html"),
        ("source_sha256", "0" * 64),
        ("input_synapses", 1),
        ("duplicate_entry", True),
        ("missing_entry", True),
    ],
)
def test_panel_provenance_and_count_mutations(monkeypatch, field, value):
    payload = json.loads(benchmark.PANEL_PATH.read_text(encoding="utf-8"))
    entry = next(row for row in payload["benchmark_panel"] if row["name"] == "LPLC2")
    if field in {"dataset", "dataset_uuid"}:
        payload["manifest"][field] = value
    elif field == "input_synapses":
        entry["synapse_totals"]["input"] = value
    elif field == "duplicate_entry":
        payload["benchmark_panel"].append(deepcopy(entry))
    elif field == "missing_entry":
        payload["benchmark_panel"].remove(entry)
    else:
        entry[field] = value
    read_text = Path.read_text

    def mutated_text(path, *args, **kwargs):
        if path == benchmark.PANEL_PATH:
            return json.dumps(payload)
        return read_text(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", mutated_text)
    if field == "input_synapses":
        report = benchmark.reproduce_lplc2_source_summary()
        assert report["reproduced"] is False
        assert report["observed"]["input_synapses"] == 350542
        assert report["expected"]["input_synapses"] == 350542
        assert report["panel_mismatches"] == {
            "input_synapses": {"panel": 1, "observed": 350542}
        }
    else:
        with pytest.raises(ValueError, match="provenance mismatch|exactly one LPLC2"):
            benchmark.reproduce_lplc2_source_summary()


def test_parser_count_mutation_is_not_success(monkeypatch):
    parser = benchmark.parse_partner_table_html

    def mutated_parser(text):
        rows = parser(text)
        rows[0]["synapses"] += 1
        return rows

    monkeypatch.setattr(benchmark, "parse_partner_table_html", mutated_parser)
    report = benchmark.reproduce_lplc2_source_summary()
    assert report["reproduced"] is False
    assert report["mismatches"]["input_synapses"]["observed"] == 350543
    assert report["mismatches"]["output_synapses"]["observed"] == 182983
    assert report["expected"]["input_synapses"] == 350542


def test_order_shuffle_preserves_source_summary(partner_tables):
    inputs, outputs = partner_tables
    assert benchmark.summarize_partner_tables(inputs, outputs) == (
        benchmark.summarize_partner_tables(list(reversed(inputs)), outputs[1:] + outputs[:1])
    )


def test_exact_label_shuffle_control(partner_tables):
    downstream = partner_tables[1]
    control = benchmark.same_type_label_shuffle_control(downstream)
    assert control["assignments"] == 692
    assert control["preserved_output_synapses"] == 182982
    assert control["observed_same_type_share"] == pytest.approx(46178 / 182982)
    assert control["mean_shuffled_same_type_share"] == pytest.approx(1 / 692)
    assert control["assignments_at_least_observed"] == 1
    assert control["fraction_at_least_observed"] == pytest.approx(1 / 692)
    assert "not a biological p-value" in control["interpretation"]
    exhaustive_shares = [row["synapses"] / 182982 for row in downstream]
    assert sum(exhaustive_shares) / len(exhaustive_shares) == pytest.approx(
        control["mean_shuffled_same_type_share"]
    )
    assert sum(
        share >= control["observed_same_type_share"] for share in exhaustive_shares
    ) == control["assignments_at_least_observed"]


def test_label_weight_shuffle_changes_same_type_share_not_mass(partner_tables):
    inputs, outputs = deepcopy(partner_tables)
    baseline = benchmark.summarize_partner_tables(inputs, outputs)
    outputs[0]["synapses"], outputs[-1]["synapses"] = (
        outputs[-1]["synapses"], outputs[0]["synapses"]
    )
    shuffled = benchmark.summarize_partner_tables(inputs, outputs)
    assert shuffled["same_type_output_synapses"] != baseline["same_type_output_synapses"]
    for key in ("output_synapses", "downstream_partner_types", "reciprocal_partner_types",
                "top5_output_synapses"):
        assert shuffled[key] == baseline[key]
    control = benchmark.same_type_label_shuffle_control(outputs)
    assert control["observed_same_type_share"] < 46178 / 182982
    assert control["preserved_output_synapses"] == 182982


@pytest.mark.parametrize("mass", [-1, 1.5, float("nan"), float("inf"), True])
def test_invalid_synapse_masses_are_rejected(partner_tables, mass):
    inputs, outputs = partner_tables
    outputs[0]["synapses"] = mass
    with pytest.raises(ValueError, match="nonnegative integers"):
        benchmark.summarize_partner_tables(inputs, outputs)


def test_duplicate_labels_are_not_silently_collapsed(partner_tables):
    inputs, outputs = partner_tables
    outputs.append(deepcopy(outputs[0]))
    with pytest.raises(ValueError, match="duplicate partner label"):
        benchmark.summarize_partner_tables(inputs, outputs)


def test_missing_same_type_is_rejected(partner_tables):
    inputs, outputs = partner_tables
    with pytest.raises(ValueError, match="same-type partner is missing"):
        benchmark.summarize_partner_tables(inputs, outputs[1:])


@pytest.mark.parametrize("rows", [[], [{"partner": "LPLC2", "synapses": 0}]])
def test_empty_or_zero_mass_null_is_rejected(rows):
    with pytest.raises(ValueError, match="positive total"):
        benchmark.same_type_label_shuffle_control(rows)
