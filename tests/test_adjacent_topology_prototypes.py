# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0

from __future__ import annotations

import numpy as np

from src.core.adjacent_topology_prototypes import (
    braid_word_winding_index,
    commutator_frobenius_norm,
    topology_adjacent_summary,
    truncated_path_signature,
)


def test_truncated_path_signature_depth_two():
    sig = truncated_path_signature([0.0, 1.0, 1.5, 0.5], depth=2)
    assert "S1" in sig
    assert "S2" in sig


def test_braid_word_winding_index_counts_signed_tokens():
    info = braid_word_winding_index("sigma1 sigma2 -sigma1")
    assert info["crossings"] == 3
    assert info["winding_index"] == 1


def test_commutator_frobenius_norm_zero_for_commuting_diagonals():
    a = np.diag([1.0, 2.0])
    b = np.diag([3.0, 4.0])
    assert commutator_frobenius_norm(a, b) == 0.0


def test_topology_adjacent_summary_declares_non_hardgate_scope():
    summary = topology_adjacent_summary()
    assert summary["lane"] == "ADJACENT_TRACK"
    assert summary["hardgate_physics_claim"] is False
