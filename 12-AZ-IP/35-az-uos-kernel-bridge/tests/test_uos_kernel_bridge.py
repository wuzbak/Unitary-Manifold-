# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_uos_kernel_bridge import (
    WindingAddress,
    GEODESIC_SCHEDULABLE_RUST_CONTRACT,
    validate_schedulable,
    parse_rust_adjacency_pairs,
    winding_adjacency_pairs,
    validate_against_kk_channel_rs,
)


def test_winding_address_rejects_out_of_range_ring():
    with pytest.raises(ValueError):
        WindingAddress(5)
    with pytest.raises(ValueError):
        WindingAddress(-1)


def test_winding_address_adjacent_neighbors():
    assert WindingAddress(1).is_adjacent_to(WindingAddress(2))
    assert WindingAddress(2).is_adjacent_to(WindingAddress(1))


def test_winding_address_wraparound_adjacency():
    assert WindingAddress(0).is_adjacent_to(WindingAddress(4))
    assert WindingAddress(4).is_adjacent_to(WindingAddress(0))


def test_winding_address_non_adjacent_rings():
    assert not WindingAddress(0).is_adjacent_to(WindingAddress(2))


def test_winding_address_neighbors_returns_both_sides():
    neighbors = WindingAddress(2).neighbors()
    assert {n.ring for n in neighbors} == {1, 3}


def test_parse_rust_adjacency_pairs_from_real_kk_channel_rs():
    pairs = parse_rust_adjacency_pairs()
    assert (0, 1) in pairs
    assert (4, 0) in pairs
    assert len(pairs) == 10  # 5 rings * 2 directions


def test_winding_adjacency_pairs_matches_parsed_rust_source():
    result = validate_against_kk_channel_rs()
    assert result["matches"] is True
    assert result["rust_only"] == []
    assert result["python_only"] == []


def test_geodesic_schedulable_contract_has_five_fields():
    assert len(GEODESIC_SCHEDULABLE_RUST_CONTRACT) == 5
    names = {f.name for f in GEODESIC_SCHEDULABLE_RUST_CONTRACT}
    assert names == {"pid", "priority", "phi_weight", "state_vector", "affinity_score"}


def test_validate_schedulable_against_real_uos_process_geodesic():
    from az_uos_kernel_bridge._repo import ensure_repo_on_path

    ensure_repo_on_path()
    uos_root = PRODUCT_ROOT.parents[1] / "05-uos-kernel"
    if str(uos_root) not in sys.path:
        sys.path.insert(0, str(uos_root))
    from UOS.scheduler import ProcessGeodesic

    proc = ProcessGeodesic(pid=1)
    assert validate_schedulable(proc)
