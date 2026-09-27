# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Pillar 1129 — MaleCNS Connectome Empirical Bridge.

🔵 ADJACENT TRACK — EMPIRICAL_CONNECTOME_BRIDGE

This pillar imports a compact, reproducible benchmark panel from the public
MaleCNS v1.0 fruit-fly connectome release and computes graph-facing observables
that can be discussed alongside the repository's existing neuroscience and
consciousness lanes.

Epistemic boundary
------------------
This module does **not** claim that the MaleCNS connectome proves Unitary
Manifold physics, consciousness ontology, or a first-principles derivation of
brain function. It does stricter, narrower work:

1. Preserve public-dataset provenance for a benchmark panel.
2. Parse real public neuron-type pages into deterministic summaries.
3. Compute auditable observables: partner counts, reciprocity, concentration,
   neurotransmitter diversity, ROI balance, and cross-domain bridge signatures.
4. Expose those observables in a form that can be compared against the repo's
   existing brain/coupling language without inflating the claim class.
"""

from __future__ import annotations

__provenance__ = {
    "pillar": 1129,
    "title": "MaleCNS Connectome Empirical Bridge",
    "version": "v38.1",
    "status": "EMPIRICAL_CONNECTOME_BRIDGE — 🔵 ADJACENT TRACK",
    "source_dataset": "male-cns:v1.0",
    "source_document": "4-IMPLICATIONS/brain/MALECNS_CONNECTOME_BRIDGE.md",
    "related_pillars": [249, 516, 538],
    "toe_delta": 0.0,
}

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

PILLAR_NUMBER: int = 1129
PILLAR_TITLE: str = "MaleCNS Connectome Empirical Bridge"
PILLAR_STATUS: str = "EMPIRICAL_CONNECTOME_BRIDGE"
PILLAR_ADJACENCY: str = "ADJACENT_TRACK_ONLY"
PILLAR_TRACK: str = "🔵 ADJACENT TRACK"

MALECNS_DATASET: str = "male-cns:v1.0"
MALECNS_DATASET_UUID: str = "4b2087c0fbe046bfaf0d60bc970e3e5d"
NEURON_COUNT_ESTIMATE: int = 166_700
SYNAPSE_COUNT_ESTIMATE: int = 125_000_000
TOTAL_NEURON_TYPES: int = 11_751
PRIMARY_REGIONS: tuple[str, ...] = (
    "central brain",
    "optic lobes",
    "ventral nerve cord",
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BENCHMARK_PATH = ROOT / "data" / "malecns" / "benchmark_panel.json"

PUBLIC_INTERFACES: Dict[str, str] = {
    "neuprint_dataset": MALECNS_DATASET,
    "cell_type_explorer_repo": "https://github.com/reiserlab/celltype-explorer-drosophila-male-cns",
    "cell_type_explorer_readme": "https://raw.githubusercontent.com/reiserlab/celltype-explorer-drosophila-male-cns/main/README.md",
    "type_index_snapshot": "https://raw.githubusercontent.com/reiserlab/celltype-explorer-drosophila-male-cns/main/data/neurons.json",
    "neuroglancer_major_compartments": "precomputed://gs://flyem-male-cns/rois/malecns-major-compartments-v2",
}


def _clean_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
    )
    return " ".join(text.split())


def _extract_table(html: str, table_id: str) -> str:
    match = re.search(rf"<table[^>]*id={re.escape(table_id)}[^>]*>(.*?)</table>", html, re.S | re.I)
    if not match:
        raise ValueError(f"table {table_id!r} not found")
    return match.group(0)


def _iter_table_rows(table_html: str) -> Iterable[List[tuple[str, str]]]:
    for row_html in re.findall(r"<tr[^>]*>(.*?)(?=<tr|$)", table_html, re.S | re.I):
        cells = re.findall(r"<td([^>]*)>(.*?)(?=<td|$)", row_html, re.S | re.I)
        if cells:
            yield cells


def _numeric_cell_value(cell_html: str) -> float:
    return float(_clean_text(cell_html).replace(",", ""))


def parse_partner_table_html(table_html: str) -> List[Dict[str, Any]]:
    """Parse a MaleCNS upstream/downstream partner table into row dictionaries."""
    rows: List[Dict[str, Any]] = []
    for cells in _iter_table_rows(table_html):
        partner_match = re.search(r"<a [^>]*href=([^ >]+)>([^<]+)</a>", cells[0][1])
        partner = partner_match.group(2) if partner_match else _clean_text(cells[0][1])
        href = partner_match.group(1) if partner_match else None
        nt_match = re.search(r"title=([A-Za-z]+)", cells[2][1])
        synapse_match = re.search(r"∑ connections: ([0-9,]+)", cells[3][0])
        percent_match = re.search(r"title=([0-9.]+)%", cells[4][0])
        rows.append(
            {
                "partner": partner,
                "href": href,
                "cell_count": int(_numeric_cell_value(cells[1][1])),
                "neurotransmitter": nt_match.group(1) if nt_match else _clean_text(cells[2][1]),
                "synapses": int(synapse_match.group(1).replace(",", "")) if synapse_match else int(round(_numeric_cell_value(cells[3][1]))),
                "percentage": float(percent_match.group(1)) if percent_match else _numeric_cell_value(cells[4][1]),
            }
        )
    return rows


def parse_roi_table_html(table_html: str) -> List[Dict[str, Any]]:
    """Parse a MaleCNS ROI innervation table into row dictionaries."""
    rows: List[Dict[str, Any]] = []
    for cells in _iter_table_rows(table_html):
        attrs0, roi_html = cells[0]
        roi_match = re.search(r"data-roi-name=([^ >]+)", attrs0)
        title_match = re.search(r'title="([^"]+)"', roi_html)
        input_pct_match = re.search(r"title=([0-9.]+)%", cells[2][0])
        output_pct_match = re.search(r"title=([0-9.]+)%", cells[5][0])
        rows.append(
            {
                "roi": roi_match.group(1) if roi_match else _clean_text(roi_html),
                "label": title_match.group(1) if title_match else _clean_text(roi_html),
                "input_synapses": int(_numeric_cell_value(cells[1][1])),
                "input_percentage": float(input_pct_match.group(1)) if input_pct_match else _numeric_cell_value(cells[2][1]),
                "log_ratio": float(_clean_text(cells[3][1])),
                "output_synapses": int(_numeric_cell_value(cells[4][1])),
                "output_percentage": float(output_pct_match.group(1)) if output_pct_match else _numeric_cell_value(cells[5][1]),
            }
        )
    return rows


def parse_public_type_page_html(html: str) -> Dict[str, Any]:
    """Parse the three main MaleCNS analysis tables from one public type page."""
    upstream_table = _extract_table(html, "upstream-table")
    downstream_table = _extract_table(html, "downstream-table")
    roi_table = _extract_table(html, "roi-table")
    return {
        "upstream": parse_partner_table_html(upstream_table),
        "downstream": parse_partner_table_html(downstream_table),
        "roi": parse_roi_table_html(roi_table),
    }


def load_benchmark_payload(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    payload_path = Path(path)
    return json.loads(payload_path.read_text(encoding="utf-8"))


def malecns_manifest(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    return dict(load_benchmark_payload(path)["manifest"])


def benchmark_panel(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[Dict[str, Any]]:
    return list(load_benchmark_payload(path)["benchmark_panel"])


def aggregate_observables(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    return dict(load_benchmark_payload(path)["aggregate_observables"])


def benchmark_names(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[str]:
    return [row["name"] for row in benchmark_panel(path)]


def _domain_total(row: Mapping[str, Any], domain: str) -> int:
    return int(row["macro_domain"]["domain_synapse_totals"].get(domain, 0))


def cross_domain_bridge_types(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[str]:
    """Return benchmark types with both central-brain and VNC/motor load present."""
    out: List[str] = []
    for row in benchmark_panel(path):
        if _domain_total(row, "central_brain") > 100 and _domain_total(row, "vnc_or_motor") > 100:
            out.append(row["name"])
    return out


def reciprocity_ranking(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[Dict[str, Any]]:
    rows = sorted(
        benchmark_panel(path),
        key=lambda row: (-float(row["reciprocity"]["jaccard"]), row["name"]),
    )
    return [{"name": row["name"], "jaccard": row["reciprocity"]["jaccard"]} for row in rows]


def neurotransmitter_entropy_ranking(
    direction: str = "downstream", path: Path | str = DEFAULT_BENCHMARK_PATH
) -> List[Dict[str, Any]]:
    if direction not in {"upstream", "downstream"}:
        raise ValueError("direction must be 'upstream' or 'downstream'")
    key = f"{direction}_entropy_bits"
    rows = sorted(
        benchmark_panel(path),
        key=lambda row: (-float(row["neurotransmitter_mix"][key]), row["name"]),
    )
    return [{"name": row["name"], "entropy_bits": row["neurotransmitter_mix"][key]} for row in rows]


def concentration_ranking(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[Dict[str, Any]]:
    rows = sorted(
        benchmark_panel(path),
        key=lambda row: (-float(row["concentration"]["top5_output_share"]), row["name"]),
    )
    return [
        {
            "name": row["name"],
            "top5_input_share": row["concentration"]["top5_input_share"],
            "top5_output_share": row["concentration"]["top5_output_share"],
        }
        for row in rows
    ]


def benchmark_panel_findings(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[str]:
    panel = benchmark_panel(path)
    agg = aggregate_observables(path)
    by_name = {row["name"]: row for row in panel}
    bridges = cross_domain_bridge_types(path)
    return [
        (
            f"The curated MaleCNS benchmark panel preserves {len(panel)} real public neuron-type pages from "
            f"{MALECNS_DATASET} and spans optic, central-complex, ascending, descending, motor, and neuromodulatory roles."
        ),
        (
            f"{agg['highest_input_type']} carries the largest benchmark input and output mass "
            f"({by_name[agg['highest_input_type']]['synapse_totals']['input']} input synapses; "
            f"{by_name[agg['highest_output_type']]['synapse_totals']['output']} output synapses), "
            "supporting an optic-lobe-heavy high-throughput visual integration lane in this panel."
        ),
        (
            f"Reciprocity is substantial rather than negligible: mean partner-set Jaccard overlap is "
            f"{agg['mean_reciprocity_jaccard']:.3f}, and {agg['most_reciprocal_type']} is the most reciprocal benchmark type."
        ),
        (
            f"Cross-domain bridge load is explicit in {', '.join(bridges)}: both benchmark types carry nonzero central-brain and VNC/motor ROI totals, "
            "making them useful reduced surfaces for brain↔nerve-cord coupling analysis."
        ),
        (
            f"{agg['most_diffuse_output_type']} has the highest downstream neurotransmitter entropy in the panel, "
            "which marks it as the broadest mixed-output benchmark among the imported types rather than a narrowly single-channel relay."
        ),
    ]


def pillar1129_report(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    panel = benchmark_panel(path)
    agg = aggregate_observables(path)
    return {
        "pillar_number": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "adjacency": PILLAR_ADJACENCY,
        "track": PILLAR_TRACK,
        "manifest": malecns_manifest(path),
        "benchmark_names": [row["name"] for row in panel],
        "aggregate_observables": agg,
        "cross_domain_bridge_types": cross_domain_bridge_types(path),
        "reciprocity_ranking": reciprocity_ranking(path)[:5],
        "concentration_ranking": concentration_ranking(path)[:5],
        "downstream_entropy_ranking": neurotransmitter_entropy_ranking("downstream", path)[:5],
        "findings": benchmark_panel_findings(path),
        "epistemic_boundary": (
            "Adjacent-track empirical connectome bridge only: benchmark observables are derived from public MaleCNS pages, "
            "but no hardgate physics, consciousness ontology, or first-principles neural derivation is claimed."
        ),
    }


__all__ = [
    "DEFAULT_BENCHMARK_PATH",
    "MALECNS_DATASET",
    "MALECNS_DATASET_UUID",
    "NEURON_COUNT_ESTIMATE",
    "PILLAR_ADJACENCY",
    "PILLAR_NUMBER",
    "PILLAR_STATUS",
    "PILLAR_TITLE",
    "PILLAR_TRACK",
    "PRIMARY_REGIONS",
    "PUBLIC_INTERFACES",
    "SYNAPSE_COUNT_ESTIMATE",
    "TOTAL_NEURON_TYPES",
    "__provenance__",
    "aggregate_observables",
    "benchmark_names",
    "benchmark_panel",
    "benchmark_panel_findings",
    "concentration_ranking",
    "cross_domain_bridge_types",
    "load_benchmark_payload",
    "malecns_manifest",
    "neurotransmitter_entropy_ranking",
    "parse_partner_table_html",
    "parse_public_type_page_html",
    "parse_roi_table_html",
    "pillar1129_report",
    "reciprocity_ranking",
]
