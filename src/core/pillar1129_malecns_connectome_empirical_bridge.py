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

import html
import json
import math
import re
from copy import deepcopy
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
BRIDGE_DOMAIN_THRESHOLD: int = 100
PUBLIC_TYPE_PAGE_TABLE_IDS: tuple[str, str, str] = ("upstream-table", "downstream-table", "roi-table")
PRIMARY_REGIONS: tuple[str, ...] = (
    "central brain",
    "optic lobes",
    "ventral nerve cord",
)

DEFAULT_BENCHMARK_PATH = Path("data") / "malecns" / "benchmark_panel.json"


def _repository_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / DEFAULT_BENCHMARK_PATH).exists():
            return candidate
    raise FileNotFoundError("Could not locate repository root for MaleCNS benchmark payload")


def _resolve_benchmark_path(path: Path | str) -> Path:
    payload_path = Path(path)
    if payload_path.is_absolute():
        if payload_path.exists():
            return payload_path
        raise FileNotFoundError(f"MaleCNS benchmark payload not found: {payload_path}")
    resolved = _repository_root() / payload_path
    if resolved.exists():
        return resolved
    raise FileNotFoundError(f"MaleCNS benchmark payload not found: {resolved}")

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


def _attribute_value(fragment: str, name: str) -> str | None:
    match = re.search(
        rf"""\b{re.escape(name)}\s*=\s*(?:"([^"]*)"|'([^']*)'|([^>\s]+))""",
        fragment,
        re.I,
    )
    if not match:
        return None
    return html.unescape(next(group for group in match.groups() if group is not None))


def _extract_table(html: str, table_id: str) -> str:
    table_matches = list(re.finditer(r"<table\b[^>]*>", html, re.I))
    token_pattern = re.compile(r"<table\b[^>]*>|</table>", re.I)
    for match in table_matches:
        opening_tag = match.group(0)
        if _attribute_value(opening_tag, "id") == table_id:
            depth = 1
            for token in token_pattern.finditer(html, match.end()):
                token_html = token.group(0)
                if token_html.lower().startswith("</table"):
                    depth -= 1
                    if depth == 0:
                        return html[match.start() : token.end()]
                else:
                    sibling_id = _attribute_value(token_html, "id")
                    if depth == 1 and sibling_id in PUBLIC_TYPE_PAGE_TABLE_IDS and sibling_id != table_id:
                        return html[match.start() : token.start()]
                    depth += 1
            return html[match.start() :]
    raise ValueError(f"table {table_id!r} not found")


def _iter_table_rows(table_html: str) -> Iterable[List[tuple[str, str]]]:
    for row_html in re.findall(r"<tr\b[^>]*>(.*?)(?=<tr\b|</tr>|$)", table_html, re.S | re.I):
        cells = re.findall(r"<td\b([^>]*)>(.*?)(?=<td\b|</td>|$)", row_html, re.S | re.I)
        if cells:
            yield cells


def _numeric_cell_value(cell_html: str) -> float:
    return float(_clean_text(cell_html).replace(",", ""))


def _parse_float_token(text: str) -> float:
    cleaned = (
        _clean_text(text)
        .replace(",", "")
        .replace("%", "")
        .replace("−", "-")
        .replace("∞", "inf")
    )
    lowered = cleaned.lower()
    if lowered in {"-inf", "-infinity"}:
        return float("-inf")
    if lowered in {"inf", "+inf", "infinity", "+infinity"}:
        return float("inf")
    if lowered == "nan":
        return float("nan")
    return float(cleaned)


def _finite_metric(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"ranking field {field_name!r} must be finite, got {value!r}")
    numeric = float(value)
    if not math.isfinite(numeric):
        raise ValueError(f"ranking field {field_name!r} must be finite, got {value!r}")
    return numeric


def parse_partner_table_html(table_html: str) -> List[Dict[str, Any]]:
    """Parse a MaleCNS upstream/downstream partner table into row dictionaries.

    Supported rows must contain at least six ``<td>`` cells in the public MaleCNS
    order: partner link, cell count, neurotransmitter, synapse summary,
    percentage, and CV. Any trailing columns are ignored. The parser prefers
    neurotransmitter names from an inner ``title`` attribute and synapse totals
    from a ``∑ connections: ...`` attribute inside the synapse-summary cell.
    Rows with fewer than six cells raise ``ValueError`` so malformed or shifted
    table shapes fail deterministically.
    """
    rows: List[Dict[str, Any]] = []
    for cells in _iter_table_rows(table_html):
        if len(cells) < 6:
            raise ValueError(f"partner table row has {len(cells)} cells; expected at least 6")
        partner_match = re.search(r"<a\b[^>]*>([^<]+)</a>", cells[0][1], re.I)
        partner = partner_match.group(1) if partner_match else _clean_text(cells[0][1])
        href = _attribute_value(partner_match.group(0), "href") if partner_match else None
        nt_value = _attribute_value(cells[2][1], "title")
        synapse_match = re.search(r"∑ connections: ([0-9,]+)", f"{cells[3][0]} {cells[3][1]}")
        percent_title = _attribute_value(cells[4][0], "title")
        neurotransmitter = nt_value.lower() if nt_value else _clean_text(cells[2][1]).lower()
        rows.append(
            {
                "partner": partner,
                "href": href,
                "cell_count": int(_numeric_cell_value(cells[1][1])),
                "neurotransmitter": neurotransmitter,
                "synapses": int(synapse_match.group(1).replace(",", "")) if synapse_match else int(round(_numeric_cell_value(cells[3][1]))),
                "percentage": float(percent_title.rstrip("%")) if percent_title else _numeric_cell_value(cells[4][1]),
            }
        )
    return rows


def parse_roi_table_html(table_html: str) -> List[Dict[str, Any]]:
    """Parse a MaleCNS ROI innervation table into row dictionaries."""
    rows: List[Dict[str, Any]] = []
    for cells in _iter_table_rows(table_html):
        if len(cells) < 6:
            raise ValueError(f"ROI table row has {len(cells)} cells; expected at least 6")
        attrs0, roi_html = cells[0]
        roi_value = _attribute_value(attrs0, "data-roi-name")
        title_value = _attribute_value(roi_html, "title")
        input_pct_title = _attribute_value(cells[2][0], "title")
        output_pct_title = _attribute_value(cells[5][0], "title")
        label = title_value if title_value else _clean_text(roi_html)
        rows.append(
            {
                "roi": roi_value if roi_value else _clean_text(roi_html),
                "label": label,
                "input_synapses": int(_numeric_cell_value(cells[1][1])),
                "input_percentage": float(input_pct_title.rstrip("%")) if input_pct_title else _numeric_cell_value(cells[2][1]),
                "log_ratio": _parse_float_token(cells[3][1]),
                "output_synapses": int(_numeric_cell_value(cells[4][1])),
                "output_percentage": float(output_pct_title.rstrip("%")) if output_pct_title else _numeric_cell_value(cells[5][1]),
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
    payload_path = _resolve_benchmark_path(path)
    return json.loads(payload_path.read_text(encoding="utf-8"))


def _manifest_from_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return deepcopy(payload["manifest"])


def _panel_from_payload(payload: Mapping[str, Any]) -> List[Dict[str, Any]]:
    return deepcopy(payload["benchmark_panel"])


def _aggregate_from_payload(payload: Mapping[str, Any]) -> Dict[str, Any]:
    return deepcopy(payload["aggregate_observables"])


def malecns_manifest(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    return _manifest_from_payload(load_benchmark_payload(path))


def benchmark_panel(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[Dict[str, Any]]:
    return _panel_from_payload(load_benchmark_payload(path))


def aggregate_observables(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    return _aggregate_from_payload(load_benchmark_payload(path))


def benchmark_names(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[str]:
    return [row["name"] for row in benchmark_panel(path)]


def _domain_total(row: Mapping[str, Any], domain: str) -> int:
    return int(row["macro_domain"]["domain_synapse_totals"].get(domain, 0))


def _domain_label(row: Mapping[str, Any]) -> str:
    dominant = str(row["macro_domain"].get("dominant_domain", "mixed")).strip().lower()
    return {
        "optic_lobe": "optic-lobe",
        "central_brain": "central-brain",
        "vnc_or_motor": "VNC/motor",
    }.get(dominant, dominant.replace("_", "-"))


def _cross_domain_bridge_types_from_panel(panel: List[Mapping[str, Any]]) -> List[str]:
    out: List[str] = []
    for row in panel:
        if (
            _domain_total(row, "central_brain") >= BRIDGE_DOMAIN_THRESHOLD
            and _domain_total(row, "vnc_or_motor") >= BRIDGE_DOMAIN_THRESHOLD
        ):
            out.append(row["name"])
    return out


def cross_domain_bridge_types(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[str]:
    """Return benchmark types with both central-brain and VNC/motor load present."""
    return _cross_domain_bridge_types_from_panel(benchmark_panel(path))


def _reciprocity_ranking_from_panel(panel: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows = [
        {
            "name": row["name"],
            "jaccard": _finite_metric(row["reciprocity"]["jaccard"], "reciprocity.jaccard"),
        }
        for row in panel
    ]
    return sorted(rows, key=lambda row: (-row["jaccard"], row["name"]))


def reciprocity_ranking(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[Dict[str, Any]]:
    return _reciprocity_ranking_from_panel(benchmark_panel(path))


def _neurotransmitter_entropy_ranking_from_panel(
    panel: List[Mapping[str, Any]], direction: str = "downstream"
) -> List[Dict[str, Any]]:
    if direction not in {"upstream", "downstream"}:
        raise ValueError("direction must be 'upstream' or 'downstream'")
    key = f"{direction}_entropy_bits"
    rows = [
        {
            "name": row["name"],
            "entropy_bits": _finite_metric(row["neurotransmitter_mix"][key], f"neurotransmitter_mix.{key}"),
        }
        for row in panel
    ]
    return sorted(rows, key=lambda row: (-row["entropy_bits"], row["name"]))


def neurotransmitter_entropy_ranking(
    direction: str = "downstream", path: Path | str = DEFAULT_BENCHMARK_PATH
) -> List[Dict[str, Any]]:
    return _neurotransmitter_entropy_ranking_from_panel(benchmark_panel(path), direction)


def _concentration_ranking_from_panel(panel: List[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows = [
        {
            "name": row["name"],
            "top5_input_share": _finite_metric(row["concentration"]["top5_input_share"], "concentration.top5_input_share"),
            "top5_output_share": _finite_metric(row["concentration"]["top5_output_share"], "concentration.top5_output_share"),
        }
        for row in panel
    ]
    rows.sort(key=lambda row: (-row["top5_output_share"], row["name"]))
    return [
        dict(row) for row in rows
    ]


def concentration_ranking(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[Dict[str, Any]]:
    return _concentration_ranking_from_panel(benchmark_panel(path))


def _benchmark_panel_findings_from_parts(
    panel: List[Mapping[str, Any]],
    agg: Mapping[str, Any],
    bridges: List[str],
) -> List[str]:
    by_name = {row["name"]: row for row in panel}
    input_row = by_name[agg["highest_input_type"]]
    output_row = by_name[agg["highest_output_type"]]
    input_domain = _domain_label(input_row)
    output_domain = _domain_label(output_row)
    if agg["highest_input_type"] == agg["highest_output_type"]:
        throughput_finding = "".join(
            [
                f"{agg['highest_input_type']} carries the largest benchmark input and output mass ",
                f"({input_row['synapse_totals']['input']} input synapses; ",
                f"{output_row['synapse_totals']['output']} output synapses), ",
                f"supporting a {input_domain}-dominant high-throughput lane in this panel.",
            ]
        )
    else:
        throughput_finding = "".join(
            [
                f"{agg['highest_input_type']} carries the largest benchmark input mass ",
                f"({input_row['synapse_totals']['input']} input synapses), while ",
                f"{agg['highest_output_type']} carries the largest benchmark output mass ",
                f"({output_row['synapse_totals']['output']} output synapses), ",
                f"supporting a split {input_domain}-input / {output_domain}-output high-throughput lane in this panel.",
            ]
        )
    bridge_count = len(bridges)
    if bridge_count == 0:
        bridge_finding = (
            "No benchmark types cross the current brain↔VNC bridge threshold in this payload, "
            "so the imported panel behaves as a set of compartment-specialized surfaces under this criterion."
        )
    else:
        bridge_noun = "type" if bridge_count == 1 else "types"
        bridge_verb = "carries" if bridge_count == 1 else "carry"
        bridge_pronoun = "it" if bridge_count == 1 else "them"
        bridge_names = ", ".join(bridges)
        bridge_finding = (
            f"Cross-domain bridge load is explicit in {bridge_names}: {bridge_count} benchmark {bridge_noun} {bridge_verb} nonzero central-brain and VNC/motor ROI totals, "
            f"making {bridge_pronoun} useful reduced surfaces for brain↔nerve-cord coupling analysis."
        )
    return [
        (
            f"The curated MaleCNS benchmark panel preserves {len(panel)} real public neuron-type pages from "
            f"{MALECNS_DATASET} and spans optic, central-complex, ascending, descending, motor, and neuromodulatory roles."
        ),
        throughput_finding,
        (
            f"Reciprocity is substantial rather than negligible: mean partner-set Jaccard overlap is "
            f"{agg['mean_reciprocity_jaccard']:.3f}, and {agg['most_reciprocal_type']} is the most reciprocal benchmark type."
        ),
        bridge_finding,
        (
            f"{agg['most_diffuse_output_type']} has the highest downstream neurotransmitter entropy in the panel, "
            "which marks it as the broadest mixed-output benchmark among the imported types rather than a narrowly single-channel relay."
        ),
    ]


def benchmark_panel_findings(path: Path | str = DEFAULT_BENCHMARK_PATH) -> List[str]:
    payload = load_benchmark_payload(path)
    panel = _panel_from_payload(payload)
    agg = _aggregate_from_payload(payload)
    bridges = _cross_domain_bridge_types_from_panel(panel)
    return _benchmark_panel_findings_from_parts(panel, agg, bridges)


def pillar1129_report(path: Path | str = DEFAULT_BENCHMARK_PATH) -> Dict[str, Any]:
    payload = load_benchmark_payload(path)
    manifest = _manifest_from_payload(payload)
    panel = _panel_from_payload(payload)
    agg = _aggregate_from_payload(payload)
    bridges = _cross_domain_bridge_types_from_panel(panel)
    return {
        "pillar_number": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "adjacency": PILLAR_ADJACENCY,
        "track": PILLAR_TRACK,
        "manifest": manifest,
        "benchmark_names": [row["name"] for row in panel],
        "aggregate_observables": agg,
        "cross_domain_bridge_types": bridges,
        "reciprocity_ranking": _reciprocity_ranking_from_panel(panel)[:5],
        "concentration_ranking": _concentration_ranking_from_panel(panel)[:5],
        "downstream_entropy_ranking": _neurotransmitter_entropy_ranking_from_panel(panel, "downstream")[:5],
        "findings": _benchmark_panel_findings_from_parts(panel, agg, bridges),
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
