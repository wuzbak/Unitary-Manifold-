# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar 395 — Derivation Graph Acyclicity (DAG Module)
Epistemological Deep Audit — v12.9

Builds a directed acyclic graph (DAG) of the primary claim-dependency
relationships in the Unitary Manifold and verifies that no claim depends on
itself, directly or transitively.

A cycle in a derivation graph is a logical error — it means at least one claim
is circularly justified.  This module makes the graph executable and adds a
machine-verifiable acyclicity gate.

Three outputs:
1. DERIVATION GRAPH — nodes = claims; directed edges = "X is derived from Y".
   ~35 most-connected claims from the canonical claim set.
2. ACYCLICITY CHECK — DAG cycle detection via DFS.  Any cycle is reported as a
   logical error.
3. CENTRALITY AND SENSITIVITY RANKING — which claim has the most downstream
   dependents (most structurally central)?  Which postulate, if falsified, would
   break the most predictions?

Epistemic status: EPISTEMOLOGICAL_INFRASTRUCTURE — structural audit of existing
documented derivation relationships; does not make new physics claims.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# Graph node
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class ClaimNode:
    """A node in the derivation DAG."""
    name: str
    kind: str           # "POSTULATE", "DERIVED", "ADMISSION", "FREE_PARAMETER"
    status: str         # "PROVED", "DERIVED_CONDITIONAL", "POSTULATED", "OPEN_GAP", etc.
    citation: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# Canonical node definitions
# ──────────────────────────────────────────────────────────────────────────────

_NODES: List[ClaimNode] = [
    # Foundational postulates (no upstream in the UM derivation chain)
    ClaimNode("P1: Z₂ orbifold (S¹/Z₂)",              "POSTULATE",      "POSTULATED",           "Pillar 39"),
    ClaimNode("P2: 5D KK metric ansatz",               "POSTULATE",      "DERIVED_CONDITIONAL",  "Pillar 344, 384"),
    ClaimNode("P3: B_μ irreversibility 1-form",        "POSTULATE",      "POSTULATED",           "src/core/evolution.py"),
    ClaimNode("P4: Goldberger-Wise potential",         "POSTULATE",      "POSTULATED",           "Pillar 68"),
    ClaimNode("P5: FTUM operator U=I+H+T",             "POSTULATE",      "POSTULATED",           "src/multiverse/fixed_point.py"),
    ClaimNode("P6: Holographic S=A/4G",                "POSTULATE",      "DERIVED_CONDITIONAL",  "Pillar 379"),
    ClaimNode("P7: Braid n₁=n_w n₂=n_w+2",            "POSTULATE",      "DERIVED_STRUCTURAL",   "Pillar 377"),
    ClaimNode("P8: (5,7) braid stability",             "POSTULATE",      "DERIVED_STRUCTURAL",   "Pillar 377"),
    ClaimNode("Λ₅<0 (AdS₅ bulk)",                     "FREE_PARAMETER", "ARCHITECTURE_LIMIT",   "Pillar 363"),
    ClaimNode("N_e≈60 e-folds",                       "FREE_PARAMETER", "OPEN_GAP",             "Pillar 346 (partial)"),
    ClaimNode("λ_GW (GW coupling)",                   "FREE_PARAMETER", "ARCHITECTURE_LIMIT",   "Pillar 68; Admission 6"),
    ClaimNode("c_L/c_R (fermion bulk mass)",           "FREE_PARAMETER", "OPEN_GAP",             "Pillar 189-B"),

    # Core geometric derived results
    ClaimNode("Z₂-odd B_μ / G_{μ5}",                  "DERIVED",        "DERIVED_FROM_5D_LAGRANGIAN", "Pillar 387"),
    ClaimNode("n_w∈{5,7} selection",                  "DERIVED",        "PROVED",               "Pillar 67"),
    ClaimNode("η̄(5)=½ APS",                          "DERIVED",        "DERIVED_STRUCTURAL",   "Pillar 70-B"),
    ClaimNode("n_w=5 pure theorem",                   "DERIVED",        "PROVED",               "Pillar 70-D"),
    ClaimNode("k_CS=74 algebraic",                    "DERIVED",        "PROVED",               "Pillars 58, 99-B"),
    ClaimNode("c_s=12/37 braided sound speed",        "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/braided_winding.py"),
    ClaimNode("N_gen=3 (T²/Z₃ orbifold)",             "DERIVED",        "PROVED",               "Pillar 42"),
    ClaimNode("SU(3)×SU(2)×U(1) gauge group",        "DERIVED",        "DERIVED_CONDITIONAL",  "Pillars 70-D, 94"),
    ClaimNode("φ₀ self-consistency (Pillar 56)",      "DERIVED",        "CLOSED",               "Pillar 56"),
    ClaimNode("φ₀=1 Planck unit (FTUM bridge)",       "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 56-B"),

    # CMB predictions
    ClaimNode("nₛ=0.9635",                            "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/inflation.py"),
    ClaimNode("r_bare=0.097",                         "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/inflation.py"),
    ClaimNode("r_braided=0.0315",                     "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/braided_winding.py"),
    ClaimNode("β∈{0.273°,0.331°} birefringence",      "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/inflation.py"),
    ClaimNode("f_NL≈−0.5 (DBI+KK)",                  "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 375"),
    ClaimNode("Ω_GW~10⁻¹⁵",                          "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 353"),

    # SM parameters
    ClaimNode("sin²θ_W=0.2313",                       "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/ew_unification.py"),
    ClaimNode("α_s(M_Z)≈0.113",                       "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 272"),
    ClaimNode("Λ_QCD≈332 MeV",                        "DERIVED",        "DERIVED",              "Pillar 153"),
    ClaimNode("m_H=125.25 GeV",                       "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 271"),
    ClaimNode("m_p/m_e≈1825.3",                       "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/proton_electron_mass.py"),
    ClaimNode("PMNS angles (braid-lock)",              "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 208"),
    ClaimNode("Yukawa couplings y_t,y_b,y_τ,y_e",    "DERIVED",        "DERIVED_CONDITIONAL",  "Pillar 271"),

    # Holographic and multiverse
    ClaimNode("Arrow of time (geometric identity)",   "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/evolution.py"),
    ClaimNode("BH information conservation",          "DERIVED",        "DERIVED_CONDITIONAL",  "1-THEORY/QUANTUM_THEOREMS.md"),
    ClaimNode("FTUM basin contractivity",             "DERIVED",        "CONTRACTIVE_IN_PHYSICAL_REGIME", "Pillar 309"),
    ClaimNode("w₀=−1 dark energy",                   "DERIVED",        "DERIVED_CONDITIONAL",  "src/core/kk_dark_energy.py"),
    ClaimNode("Neutrino-radion identity (M_KK~110meV)", "DERIVED",     "DERIVED_CONDITIONAL",  "src/core/zero_point_vacuum.py"),

    # High-tension items (active)
    ClaimNode("r=0.0315 vs ACT DR6 r<0.016 (HIGH_TENSION)", "TENSION", "IRREDUCIBLE_IN_BRAIDED_5D_EFT", "Pillar 303"),
    ClaimNode("wₐ=0 vs DESI 2.82σ (HIGH_TENSION)",         "TENSION", "ARCHITECTURE_LIMIT_CERTIFIED", "Pillar 301"),
]


# ──────────────────────────────────────────────────────────────────────────────
# Canonical directed edges: (child, parent) meaning "child is derived from parent"
# ──────────────────────────────────────────────────────────────────────────────

_EDGES: List[Tuple[str, str]] = [
    # Z₂ orbifold → multiple derived results
    ("n_w∈{5,7} selection",         "P1: Z₂ orbifold (S¹/Z₂)"),
    ("N_gen=3 (T²/Z₃ orbifold)",    "P1: Z₂ orbifold (S¹/Z₂)"),
    ("Z₂-odd B_μ / G_{μ5}",         "P1: Z₂ orbifold (S¹/Z₂)"),
    ("Z₂-odd B_μ / G_{μ5}",         "P2: 5D KK metric ansatz"),

    # APS + CS phase → n_w uniqueness
    ("η̄(5)=½ APS",                  "n_w∈{5,7} selection"),
    ("η̄(5)=½ APS",                  "P1: Z₂ orbifold (S¹/Z₂)"),
    ("n_w=5 pure theorem",           "η̄(5)=½ APS"),
    ("n_w=5 pure theorem",           "Z₂-odd B_μ / G_{μ5}"),

    # Braid pair → k_CS, c_s
    ("k_CS=74 algebraic",            "n_w=5 pure theorem"),
    ("k_CS=74 algebraic",            "P7: Braid n₁=n_w n₂=n_w+2"),
    ("k_CS=74 algebraic",            "P8: (5,7) braid stability"),
    ("c_s=12/37 braided sound speed","k_CS=74 algebraic"),
    ("c_s=12/37 braided sound speed","P7: Braid n₁=n_w n₂=n_w+2"),

    # Orbifold → SM gauge group + generations
    ("SU(3)×SU(2)×U(1) gauge group","n_w=5 pure theorem"),
    ("SU(3)×SU(2)×U(1) gauge group","N_gen=3 (T²/Z₃ orbifold)"),
    ("sin²θ_W=0.2313",              "SU(3)×SU(2)×U(1) gauge group"),
    ("α_s(M_Z)≈0.113",              "k_CS=74 algebraic"),
    ("α_s(M_Z)≈0.113",              "SU(3)×SU(2)×U(1) gauge group"),
    ("Λ_QCD≈332 MeV",               "α_s(M_Z)≈0.113"),
    ("m_p/m_e≈1825.3",              "k_CS=74 algebraic"),
    ("m_p/m_e≈1825.3",              "N_gen=3 (T²/Z₃ orbifold)"),

    # FTUM → φ₀, holographic bound, dark energy
    ("φ₀ self-consistency (Pillar 56)","P4: Goldberger-Wise potential"),
    ("φ₀ self-consistency (Pillar 56)","P5: FTUM operator U=I+H+T"),
    ("φ₀=1 Planck unit (FTUM bridge)", "φ₀ self-consistency (Pillar 56)"),
    ("FTUM basin contractivity",        "P5: FTUM operator U=I+H+T"),
    ("P6: Holographic S=A/4G",         "P5: FTUM operator U=I+H+T"),
    ("BH information conservation",    "P6: Holographic S=A/4G"),
    ("BH information conservation",    "P5: FTUM operator U=I+H+T"),
    ("w₀=−1 dark energy",             "P5: FTUM operator U=I+H+T"),
    ("w₀=−1 dark energy",             "P4: Goldberger-Wise potential"),
    ("Neutrino-radion identity (M_KK~110meV)", "P6: Holographic S=A/4G"),
    ("Neutrino-radion identity (M_KK~110meV)", "k_CS=74 algebraic"),

    # CMB predictions
    ("nₛ=0.9635",                   "φ₀=1 Planck unit (FTUM bridge)"),
    ("nₛ=0.9635",                   "N_e≈60 e-folds"),
    ("r_bare=0.097",                "φ₀=1 Planck unit (FTUM bridge)"),
    ("r_bare=0.097",                "N_e≈60 e-folds"),
    ("r_braided=0.0315",            "r_bare=0.097"),
    ("r_braided=0.0315",            "c_s=12/37 braided sound speed"),
    ("β∈{0.273°,0.331°} birefringence", "k_CS=74 algebraic"),
    ("β∈{0.273°,0.331°} birefringence", "P2: 5D KK metric ansatz"),
    ("f_NL≈−0.5 (DBI+KK)",         "c_s=12/37 braided sound speed"),
    ("Ω_GW~10⁻¹⁵",                 "r_braided=0.0315"),
    ("Ω_GW~10⁻¹⁵",                 "k_CS=74 algebraic"),

    # Higgs, Yukawa
    ("m_H=125.25 GeV",              "P4: Goldberger-Wise potential"),
    ("m_H=125.25 GeV",              "φ₀ self-consistency (Pillar 56)"),
    ("Yukawa couplings y_t,y_b,y_τ,y_e", "c_L/c_R (fermion bulk mass)"),
    ("Yukawa couplings y_t,y_b,y_τ,y_e", "P2: 5D KK metric ansatz"),
    ("PMNS angles (braid-lock)",    "k_CS=74 algebraic"),
    ("PMNS angles (braid-lock)",    "c_s=12/37 braided sound speed"),

    # Arrow of time
    ("Arrow of time (geometric identity)", "P3: B_μ irreversibility 1-form"),
    ("Arrow of time (geometric identity)", "P2: 5D KK metric ansatz"),

    # Active tensions depend on predictions
    ("r=0.0315 vs ACT DR6 r<0.016 (HIGH_TENSION)", "r_braided=0.0315"),
    ("wₐ=0 vs DESI 2.82σ (HIGH_TENSION)",          "w₀=−1 dark energy"),
]


# ──────────────────────────────────────────────────────────────────────────────
# DAG construction
# ──────────────────────────────────────────────────────────────────────────────

class DerivationDAG:
    """Directed graph of claim dependencies with cycle-detection and analysis."""

    def __init__(
        self,
        nodes: Optional[List[ClaimNode]] = None,
        edges: Optional[List[Tuple[str, str]]] = None,
    ) -> None:
        self._nodes: Dict[str, ClaimNode] = {}
        self._children: Dict[str, List[str]] = defaultdict(list)   # child → [parents]
        self._parents: Dict[str, List[str]] = defaultdict(list)    # parent → [children derived from it]

        for node in (nodes or _NODES):
            self._nodes[node.name] = node
        for child, parent in (edges or _EDGES):
            if child not in self._nodes:
                self._nodes[child] = ClaimNode(child, "UNKNOWN", "UNKNOWN")
            if parent not in self._nodes:
                self._nodes[parent] = ClaimNode(parent, "UNKNOWN", "UNKNOWN")
            if parent not in self._children[child]:
                self._children[child].append(parent)
            if child not in self._parents[parent]:
                self._parents[parent].append(child)

    @property
    def node_names(self) -> List[str]:
        return list(self._nodes.keys())

    @property
    def node_count(self) -> int:
        return len(self._nodes)

    @property
    def edge_count(self) -> int:
        return sum(len(v) for v in self._children.values())

    def parents_of(self, node: str) -> List[str]:
        """Nodes that *node* directly depends on (upstream)."""
        return list(self._children.get(node, []))

    def children_of(self, node: str) -> List[str]:
        """Nodes that directly depend on *node* (downstream)."""
        return list(self._parents.get(node, []))

    # ── Cycle detection (DFS) ──────────────────────────────────────────────

    def find_cycles(self) -> List[List[str]]:
        """
        Detect cycles in the graph using iterative DFS with a recursion stack.

        Returns a list of cycles found.  Each cycle is a list of node names
        forming a directed cycle.  An empty list means the graph is acyclic.
        """
        visited: Set[str] = set()
        on_stack: Set[str] = set()
        cycles: List[List[str]] = []

        def dfs(node: str, path: List[str]) -> None:
            visited.add(node)
            on_stack.add(node)
            path.append(node)

            for parent in self._children.get(node, []):
                if parent not in visited:
                    dfs(parent, path)
                elif parent in on_stack:
                    # Found a cycle.  Extract the cyclic portion.
                    cycle_start = path.index(parent)
                    cycles.append(path[cycle_start:] + [parent])

            path.pop()
            on_stack.discard(node)

        for name in self._nodes:
            if name not in visited:
                dfs(name, [])

        return cycles

    def is_acyclic(self) -> bool:
        """Return True if the graph contains no cycles."""
        return len(self.find_cycles()) == 0

    # ── Topological order ─────────────────────────────────────────────────

    def topological_order(self) -> Optional[List[str]]:
        """
        Return nodes in topological order (leaf postulates first, derived claims last).
        Returns None if the graph contains a cycle.
        """
        if not self.is_acyclic():
            return None

        in_degree: Dict[str, int] = {n: len(self._children[n]) for n in self._nodes}
        queue: deque[str] = deque([n for n, d in in_degree.items() if d == 0])
        order: List[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)
            for child in self._parents.get(node, []):
                in_degree[child] -= 1
                if in_degree[child] == 0:
                    queue.append(child)

        return order if len(order) == len(self._nodes) else None

    # ── Downstream reachability ───────────────────────────────────────────

    def downstream(self, node: str) -> Set[str]:
        """Return all nodes that depend (directly or transitively) on *node*."""
        visited: Set[str] = set()
        queue: deque[str] = deque([node])
        while queue:
            current = queue.popleft()
            for child in self._parents.get(current, []):
                if child not in visited:
                    visited.add(child)
                    queue.append(child)
        return visited

    def upstream(self, node: str) -> Set[str]:
        """Return all nodes on which *node* depends (directly or transitively)."""
        visited: Set[str] = set()
        queue: deque[str] = deque([node])
        while queue:
            current = queue.popleft()
            for parent in self._children.get(current, []):
                if parent not in visited:
                    visited.add(parent)
                    queue.append(parent)
        return visited

    # ── Centrality and sensitivity ranking ───────────────────────────────

    def centrality_ranking(self) -> List[Tuple[str, int]]:
        """
        Rank nodes by number of downstream dependents.

        The most central node — the one whose falsification would break the most
        derived results — appears first.
        """
        ranking = [(name, len(self.downstream(name))) for name in self._nodes]
        ranking.sort(key=lambda x: x[1], reverse=True)
        return ranking

    def postulate_sensitivity_ranking(self) -> List[Tuple[str, int]]:
        """
        Among nodes of kind POSTULATE or FREE_PARAMETER, rank by downstream impact.
        """
        results = []
        for name, node in self._nodes.items():
            if node.kind in ("POSTULATE", "FREE_PARAMETER"):
                results.append((name, len(self.downstream(name))))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    # ── JSON export ───────────────────────────────────────────────────────

    def to_json(self) -> str:
        """Serialise the DAG to a JSON string."""
        data = {
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "nodes": [
                {
                    "name": n.name,
                    "kind": n.kind,
                    "status": n.status,
                    "citation": n.citation,
                }
                for n in self._nodes.values()
            ],
            "edges": [
                {"child": child, "parent": parent}
                for child, parents in self._children.items()
                for parent in parents
            ],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    # ── Full DAG report ───────────────────────────────────────────────────

    def full_report(self) -> Dict[str, object]:
        """Return the complete Pillar 395 DAG analysis report."""
        cycles = self.find_cycles()
        centrality = self.centrality_ranking()
        sensitivity = self.postulate_sensitivity_ranking()
        top_order = self.topological_order()

        return {
            "pillar": 395,
            "title": "Derivation Graph Acyclicity",
            "version": "v12.9",
            "node_count": self.node_count,
            "edge_count": self.edge_count,
            "is_acyclic": len(cycles) == 0,
            "cycles_found": cycles,
            "most_central_node": centrality[0] if centrality else None,
            "centrality_top5": centrality[:5],
            "most_critical_postulate": sensitivity[0] if sensitivity else None,
            "postulate_sensitivity_top5": sensitivity[:5],
            "topological_order_available": top_order is not None,
            "topological_order": top_order,
            "acyclicity_verdict": "PASS" if len(cycles) == 0 else "FAIL",
        }


# ──────────────────────────────────────────────────────────────────────────────
# Module-level convenience constructor
# ──────────────────────────────────────────────────────────────────────────────

def build_canonical_dag() -> DerivationDAG:
    """Construct and return the canonical Unitary Manifold derivation DAG."""
    return DerivationDAG(nodes=_NODES, edges=_EDGES)


def pillar_395_status() -> Dict[str, str]:
    """Machine-readable pillar status summary."""
    dag = build_canonical_dag()
    report = dag.full_report()
    return {
        "pillar": "395",
        "name": "Derivation Graph Acyclicity",
        "status": "EPISTEMOLOGICAL_INFRASTRUCTURE",
        "node_count": str(report["node_count"]),
        "edge_count": str(report["edge_count"]),
        "is_acyclic": str(report["is_acyclic"]),
        "cycles_found": str(len(report["cycles_found"])),
        "most_central_node": str(report["most_central_node"]),
        "acyclicity_verdict": report["acyclicity_verdict"],
    }
