"""
build_graph.py — Build the UM-SOS derivation DAG.

Usage::
    python build_graph.py           # write dag.json
    python build_graph.py --svg     # also export a static SVG snapshot
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Walk up from the resolved path until we find the repo root (contains src/core/).
# Using .resolve() avoids symlink confusion when this script is invoked through
# the 10-UM-SOS → 12-AZ-IP/04-um-sos symlink chain.
_here = Path(__file__).resolve().parent
root = _here
while root != root.parent:
    if (root / "src" / "core").is_dir():
        break
    root = root.parent
sys.path.insert(0, str(root))

from src.core.um_sos_graph import write_graph_json  # type: ignore


def export_svg(dag_json_path: Path) -> Path:
    """Export a static SVG snapshot of the derivation DAG using matplotlib."""
    import json

    try:
        import matplotlib  # type: ignore
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt  # type: ignore
        import matplotlib.patches as mpatches  # type: ignore
        import networkx as nx  # type: ignore
    except ImportError as e:
        raise RuntimeError(
            f"matplotlib and networkx are required for SVG export: {e}"
        ) from e

    data = json.loads(dag_json_path.read_text())
    G = nx.DiGraph()

    # Build graph from DAG JSON
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    for node in nodes:
        G.add_node(node.get("id", str(node)), label=node.get("label", str(node)))
    for edge in edges:
        src, tgt = edge.get("source"), edge.get("target")
        if src and tgt:
            G.add_edge(src, tgt)

    fig, ax = plt.subplots(figsize=(max(16, len(G.nodes) * 0.8), 10))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx(
        G, pos, ax=ax,
        node_size=600, node_color="#58a6ff",
        font_size=7, font_color="#0d1117",
        edge_color="#8b949e", arrows=True,
        arrowsize=15,
    )
    ax.set_title("Unitary Manifold — Derivation DAG", fontsize=14)
    ax.axis("off")
    plt.tight_layout()

    svg_path = dag_json_path.with_suffix(".svg")
    fig.savefig(svg_path, format="svg", bbox_inches="tight")
    plt.close(fig)
    return svg_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build UM-SOS derivation graph")
    parser.add_argument("--svg", action="store_true",
                        help="Also export a static SVG snapshot")
    parser.add_argument("--out", type=Path,
                        default=root / "10-UM-SOS" / "graph" / "dag.json",
                        help="Output path for dag.json")
    args = parser.parse_args()

    out: Path = args.out
    write_graph_json(out)
    print(f"✓ Written: {out}")

    if args.svg:
        try:
            svg_path = export_svg(out)
            print(f"✓ SVG snapshot: {svg_path}")
        except Exception as exc:
            print(f"⚠  SVG export failed: {exc}", file=sys.stderr)
            sys.exit(1)

