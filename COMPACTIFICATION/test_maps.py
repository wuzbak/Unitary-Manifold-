# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Regression tests for the compact and repository navigation maps."""

import json

from COMPACTIFICATION import build_maps


def test_maps_match_repository_inventory():
    paths = build_maps.tracked_paths()
    monorepo = json.loads((build_maps.COMPACT / "monorepo_map.json").read_text())
    compact = json.loads((build_maps.COMPACT / "kernel_map.json").read_text())
    assert monorepo == build_maps.build_monorepo_map(paths)
    assert compact == build_maps.build_kernel_map(paths)
    assert monorepo["file_count"] == len(paths) == len(set(paths))
    assert {entry["path"] for entry in monorepo["files"]} == set(paths)


def test_ip_and_editorial_catalogues_are_complete():
    paths = build_maps.tracked_paths()
    monorepo = build_maps.build_monorepo_map(paths)
    books = monorepo["psicat_literature"]["books"]
    articles = monorepo["psicat_literature"]["articles"]
    assert books == [path for path in paths if path.startswith(build_maps.BOOKS)]
    assert articles == [path for path in paths if path.startswith(build_maps.ARTICLES)]
    assert len(monorepo["az_ip_products"]) == 25
    assert set().union(*map(set, monorepo["az_ip_products"].values())) <= set(paths)
    assert monorepo["lanes"]["az_ip"] == sum(
        path.startswith("12-AZ-IP/") for path in paths
    )


def test_dynamic_radion_metric_has_canonical_schur_complement():
    import numpy as np
    from COMPACTIFICATION.kernel import assemble_5d_metric

    g = np.diag([-1.0, 1.0, 1.0, 1.0])[None, :, :]
    B = np.array([[0.5, 0.25, 0.1, 0.0]])
    phi = np.array([2.0])
    metric = assemble_5d_metric(g, B, phi, lam=0.7)[0]
    horizontal = metric[:4, :4] - np.outer(metric[:4, 4], metric[4, :4]) / metric[4, 4]
    np.testing.assert_allclose(horizontal, g[0])
    np.testing.assert_allclose(np.linalg.det(metric), phi[0] ** 2 * np.linalg.det(g[0]))


def test_axiom_registry_does_not_claim_unavailable_lean_proofs():
    from COMPACTIFICATION.axioms import AXIOM_REGISTRY, AxiomStatus

    axioms = {axiom.name: axiom for axiom in AXIOM_REGISTRY}
    assert axioms["A1_METRIC"].status is AxiomStatus.POSTULATED
    assert axioms["A1_METRIC"].lean4_ref is None
    assert axioms["A5_AXIOM_A"].lean4_ref is None
