# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Reproduce bounded MaleCNS LPLC2 published source-table summaries offline.

This is source-summary reproduction, not experimental replication, whole-CNS
simulation, or reproduction of Gardner's activity-space topology. Only the
three already committed LPLC2 HTML table extracts are verified here; the
recorded full-page hash cannot be verified from those extracts.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from src.core.pillar1129_malecns_connectome_empirical_bridge import (
    parse_partner_table_html,
    parse_roi_table_html,
)


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIRECTORY = REPOSITORY_ROOT / "tests/fixtures/malecns"
PANEL_PATH = REPOSITORY_ROOT / "data/malecns/benchmark_panel.json"
SOURCE_URL = (
    "https://raw.githubusercontent.com/reiserlab/"
    "celltype-explorer-drosophila-male-cns/main/types/LPLC2.html"
)
RECORDED_PAGE_SHA256 = "4f375a926ed8a5186eb197158db1a66d86ac5f56647eb44c500146b5f71c1025"
SNAPSHOT_SHA256 = {
    "upstream": "cc46da74a73fea46dbe7822df1a5a177127c5976171150bc1a55343add222682",
    "downstream": "8d162e9e8121068be9410bc985c3fb534a5c0214170e2da4aef054555cce431c",
    "roi": "c8d78287187e48db8a14bf3251798884251ebe576beef0b2d599fca13efdeb04",
}

# Independently counted <a> labels and integer "∑ connections" attributes in
# the committed public-page extracts, not loaded from benchmark_panel.json.
EXPECTED_SUMMARY = {
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


def _partner_weights(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    weights: dict[str, int] = {}
    for row in rows:
        name, mass = row["partner"], row["synapses"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError("partner labels must be nonempty strings")
        if name in weights:
            raise ValueError(f"duplicate partner label: {name}")
        if isinstance(mass, bool) or not isinstance(mass, int) or mass < 0:
            raise ValueError("synapse counts must be nonnegative integers")
        weights[name] = mass
    if not weights or sum(weights.values()) == 0:
        raise ValueError("partner table must have positive total synapse mass")
    if "LPLC2" not in weights:
        raise ValueError("LPLC2 same-type partner is missing")
    return weights


def summarize_partner_tables(
    upstream: Sequence[Mapping[str, Any]],
    downstream: Sequence[Mapping[str, Any]],
) -> dict[str, int]:
    """Count displayed type-level partners, including the same-type connection."""
    inputs, outputs = _partner_weights(upstream), _partner_weights(downstream)
    return {
        "upstream_partner_types": len(inputs),
        "downstream_partner_types": len(outputs),
        "input_synapses": sum(inputs.values()),
        "output_synapses": sum(outputs.values()),
        "reciprocal_partner_types": len(inputs.keys() & outputs.keys()),
        "union_partner_types": len(inputs.keys() | outputs.keys()),
        "top5_input_synapses": sum(sorted(inputs.values(), reverse=True)[:5]),
        "top5_output_synapses": sum(sorted(outputs.values(), reverse=True)[:5]),
        "same_type_input_synapses": inputs["LPLC2"],
        "same_type_output_synapses": outputs["LPLC2"],
    }


def same_type_label_shuffle_control(
    downstream: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Exact marginal of uniformly permuting weights over downstream labels.

    Every displayed weight is assigned to the LPLC2 label once, so no Monte
    Carlo seed or invented neurons are needed. This preserves the labels, mass,
    degree, and weight multiset. Exchangeable type labels are a descriptive
    sensitivity assumption, not a biological null or an inferential test.
    A type-to-itself connection is not necessarily a single-neuron autapse.
    """
    weights = _partner_weights(downstream)
    mass = sum(weights.values())
    observed = weights["LPLC2"]
    at_least_observed = sum(value >= observed for value in weights.values())
    return {
        "kind": "exact_downstream_weight_label_permutation",
        "assignments": len(weights),
        "preserved_output_synapses": mass,
        "observed_same_type_share": observed / mass,
        "mean_shuffled_same_type_share": 1 / len(weights),
        "assignments_at_least_observed": at_least_observed,
        "fraction_at_least_observed": at_least_observed / len(weights),
        "interpretation": "descriptive label sensitivity only; not a biological p-value",
    }


def reproduce_lplc2_source_summary(
    fixture_directory: Path | str = FIXTURE_DIRECTORY,
    panel_path: Path | str = PANEL_PATH,
) -> dict[str, Any]:
    """Verify committed extract provenance, then recompute and compare counts.

    Byte mutations fail closed before parsing. The panel is only a secondary
    consistency check, never the source of the observed or expected counts.
    """
    tables: dict[str, str] = {}
    for direction, digest in SNAPSHOT_SHA256.items():
        path = Path(fixture_directory) / f"lplc2_{direction}_table.html"
        contents = path.read_bytes()
        if hashlib.sha256(contents).hexdigest() != digest:
            raise ValueError(f"snapshot SHA-256 mismatch: {path.name}")
        tables[direction] = contents.decode("utf-8")

    panel = json.loads(Path(panel_path).read_text(encoding="utf-8"))
    manifest = panel["manifest"]
    if (
        manifest["dataset"] != "male-cns:v1.0"
        or manifest["dataset_uuid"] != "4b2087c0fbe046bfaf0d60bc970e3e5d"
    ):
        raise ValueError("MaleCNS dataset provenance mismatch")
    entries = [row for row in panel["benchmark_panel"] if row["name"] == "LPLC2"]
    if len(entries) != 1:
        raise ValueError("panel must contain exactly one LPLC2 entry")
    entry = entries[0]
    if entry["source_url"] != SOURCE_URL or entry["source_sha256"] != RECORDED_PAGE_SHA256:
        raise ValueError("LPLC2 source provenance mismatch")

    upstream = parse_partner_table_html(tables["upstream"])
    downstream = parse_partner_table_html(tables["downstream"])
    observed = summarize_partner_tables(upstream, downstream)
    observed["roi_rows"] = len(parse_roi_table_html(tables["roi"]))
    mismatches = {
        key: {"expected": expected, "observed": observed[key]}
        for key, expected in EXPECTED_SUMMARY.items()
        if observed[key] != expected
    }
    panel_counts = {
        "upstream_partner_types": entry["table_row_counts"]["upstream_partners"],
        "downstream_partner_types": entry["table_row_counts"]["downstream_partners"],
        "input_synapses": entry["synapse_totals"]["input"],
        "output_synapses": entry["synapse_totals"]["output"],
        "reciprocal_partner_types": entry["reciprocity"]["reciprocal_partner_count"],
        "union_partner_types": entry["reciprocity"]["union_partner_count"],
        "roi_rows": entry["table_row_counts"]["roi_rows"],
    }
    panel_mismatches = {
        key: {"panel": value, "observed": observed[key]}
        for key, value in panel_counts.items()
        if value != observed[key]
    }
    return {
        "claim_class": "published_source_summary_reproduction",
        "neuron_type": "LPLC2",
        "reproduced": not mismatches and not panel_mismatches,
        "provenance": {
            "dataset": manifest["dataset"],
            "dataset_uuid": manifest["dataset_uuid"],
            "source_url": SOURCE_URL,
            "recorded_full_page_sha256": RECORDED_PAGE_SHA256,
            "full_page_hash_verified": False,
            "verified_extract_sha256": dict(SNAPSHOT_SHA256),
            "new_external_data_copied": False,
        },
        "observed": observed,
        "expected": deepcopy(EXPECTED_SUMMARY),
        "mismatches": mismatches,
        "panel_mismatches": panel_mismatches,
        "control": same_type_label_shuffle_control(downstream),
        "limits": [
            "One neuron type's displayed partner tables, not the full connectome.",
            "Type-level same-type connections are not individual-neuron autapses.",
            "ROI row count only; overlapping ROI totals are not summed.",
            "Extract hashes verify committed bytes, not independent source authenticity.",
            "No activity data: Gardner topology reproduction remains pending.",
            "Full paper replication and experimental replication remain pending.",
            "No physics validation or full connectivity simulation is claimed.",
        ],
    }


if __name__ == "__main__":
    report = reproduce_lplc2_source_summary()
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(0 if report["reproduced"] else 1)
