# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Tests for the braided gut-brain/microbiome bridge (ADJACENT TRACK).

Covers: the Pillar 537 (5,7)/(5,6) pair contract, determinism of the
hemisphere/microbiome phase-sketch braid, bounded coherence scores, the
honesty-boundary note, and tool/server/flag_ab wiring.
"""

from __future__ import annotations

import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PRODUCT_ROOT.parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from ox_navigator.engine.merlin_braided_gut_microbiome import (
    FIRMICUTES_BACTEROIDETES_RATIO,
    GUT_PHYLA_TOKENS,
    OBSERVABLE_PAIR,
    PARENT_PAIR,
    STATUS_LABEL,
    braided_gut_microbiome_report,
    braided_hemisphere_report,
)
from ox_navigator.engine.merlin_toroidal_geometry import LATTICE_ORDER


def test_observable_pair_matches_pillar_537_contract() -> None:
    from src.core.pillar537_shadow_pair_parent_derivation import (
        N_BEFORE,
        N_SHADOW_OBSERVED,
        N_W_OBSERVED,
    )

    assert OBSERVABLE_PAIR == (N_W_OBSERVED, N_SHADOW_OBSERVED) == (5, 7)
    assert OBSERVABLE_PAIR[0] ** 2 + OBSERVABLE_PAIR[1] ** 2 == LATTICE_ORDER == 74
    assert PARENT_PAIR == (N_W_OBSERVED, N_BEFORE) == (5, 6)


def test_hemisphere_report_is_deterministic() -> None:
    first = braided_hemisphere_report("gut brain cognition")
    second = braided_hemisphere_report("gut brain cognition")
    assert first == second


def test_hemisphere_report_shape_and_status() -> None:
    report = braided_hemisphere_report("")
    assert report["status"] == STATUS_LABEL == "ADJACENT_TRACK"
    assert report["observable_pair"] == {"n_w": 5, "n_shadow": 7, "k_cs": 74}
    assert report["parent_pair"]["n_w"] == 5
    assert report["parent_pair"]["n_before"] == 6
    assert 0.0 <= report["braid_coherence"] <= 1.0
    assert report["braid_bank_delta"] >= 0
    assert "left_hemisphere" in report and "right_hemisphere" in report
    assert len(report["left_hemisphere"]["code"]) == len(report["right_hemisphere"]["code"])
    assert "not a new physics claim" in report["note"]


def test_left_and_right_hemisphere_codes_differ() -> None:
    report = braided_hemisphere_report("digestion signalling")
    assert report["left_hemisphere"]["code"] != report["right_hemisphere"]["code"]
    assert report["left_hemisphere"]["bank"] != report["right_hemisphere"]["bank"] or (
        report["left_hemisphere"]["code"] != report["right_hemisphere"]["code"]
    )


def test_microbiome_report_extends_hemisphere_report() -> None:
    report = braided_gut_microbiome_report("microbiome diversity")
    assert report["status"] == STATUS_LABEL
    assert "microbiome_strand" in report
    assert report["microbiome_strand"]["seed_tokens"][:5] == list(GUT_PHYLA_TOKENS)
    assert 0.0 <= report["microbiome_vs_gut_coherence"] <= 1.0
    assert 0.0 <= report["microbiome_vs_cranial_coherence"] <= 1.0
    assert report["firmicutes_bacteroidetes_ratio"] == FIRMICUTES_BACTEROIDETES_RATIO
    assert "neural_crest_migration" in report
    assert "per-subject measurement" in report["note"]


def test_microbiome_report_is_deterministic() -> None:
    first = braided_gut_microbiome_report("the second brain")
    second = braided_gut_microbiome_report("the second brain")
    assert first == second


def test_microbiome_strand_closer_to_gut_than_cranial() -> None:
    # The microbiome strand shares tokens (n_before=6, gut-adjacent vocabulary)
    # with the gut/parent hemisphere; it should not be farther from it than
    # from the cranial/observable hemisphere on a query with no bias tokens.
    report = braided_gut_microbiome_report("")
    assert report["microbiome_vs_gut_coherence"] >= report["microbiome_vs_cranial_coherence"]


def test_empty_query_still_produces_valid_report() -> None:
    report = braided_gut_microbiome_report()
    assert report["status"] == STATUS_LABEL
    assert report["left_hemisphere"]["seed_tokens"][:3] == ["cranial", "cortex", "observable"]


def test_tool_registration() -> None:
    from ox_navigator.engine.merlin_tools import _tool_manifest, route_tool

    names = {item["name"]: item for item in _tool_manifest()["functions"]}
    assert "getMerlinBraidedGutMicrobiome" in names
    assert "args_schema" in names["getMerlinBraidedGutMicrobiome"]
    result = route_tool("getMerlinBraidedGutMicrobiome", {"query": "gut brain"})
    assert result["ok"] is True
    assert result["result"]["data"]["status"] == STATUS_LABEL


def test_server_exposes_braided_gut_microbiome_endpoint() -> None:
    import ox_navigator.app.server as server_module

    assert "/api/psicat/braided-gut-microbiome" in Path(server_module.__file__).read_text(encoding="utf-8")


def test_flag_ab_rrf_fusion_variant_present() -> None:
    from ox_navigator.engine.merlin_flag_ab import OPT_IN_FLAGS, run_flag_ab

    report = run_flag_ab(stages=["stage_a_parity_capture"], limit_per_stage=1)
    assert report["ok"] is True
    assert "rrf_fusion" in report["summary"]
    from ox_navigator.engine.merlin_rag import RRF_FUSION_RANKING_FLAG

    assert RRF_FUSION_RANKING_FLAG in OPT_IN_FLAGS
