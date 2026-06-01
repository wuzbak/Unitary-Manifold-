from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from src.core.pillar395_derivation_dag import build_canonical_dag


def export_derivation_graph() -> Dict[str, Any]:
    dag = build_canonical_dag()
    raw = json.loads(dag.to_json())

    name_to_id = {node["name"]: idx for idx, node in enumerate(raw["nodes"])}
    nodes = []
    for idx, node in enumerate(raw["nodes"]):
        nodes.append(
            {
                "id": idx,
                "name": node["name"],
                "kind": node["kind"],
                "status": node["status"],
                "citation": node["citation"],
                "group": node["kind"],
            }
        )

    links = []
    for edge in raw["edges"]:
        links.append(
            {
                "source": name_to_id[edge["parent"]],
                "target": name_to_id[edge["child"]],
                "source_name": edge["parent"],
                "target_name": edge["child"],
            }
        )

    report = dag.full_report()
    return {
        "metadata": {
            "node_count": report["node_count"],
            "edge_count": report["edge_count"],
            "acyclicity_verdict": report["acyclicity_verdict"],
            "most_central_node": report["most_central_node"],
            "most_critical_postulate": report["most_critical_postulate"],
        },
        "nodes": nodes,
        "links": links,
    }


def write_graph_json(output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = export_derivation_graph()
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out
