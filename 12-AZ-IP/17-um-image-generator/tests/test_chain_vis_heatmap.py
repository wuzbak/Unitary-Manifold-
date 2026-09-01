# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from image_generator.engine import compute_mass_hierarchy, export_svg_heatmap, get_chain_json, render_chain_ascii, render_heatmap_ascii
from um_image_generator.engine.dimensional_chain_vis import DIMENSIONAL_CHAIN
from um_image_generator.engine.yukawa_heatmap import PHI


def test_dimensional_chain_length() -> None:
    assert len(DIMENSIONAL_CHAIN) == 8


def test_dimensional_chain_runs_from_4d_to_11d() -> None:
    assert DIMENSIONAL_CHAIN[0]['dim'] == 4
    assert DIMENSIONAL_CHAIN[-1]['dim'] == 11


def test_dimensional_chain_all_reference_p858() -> None:
    assert {item['pillar'] for item in DIMENSIONAL_CHAIN} == {'P858'}


def test_dimensional_chain_statuses_present() -> None:
    assert all(item['status'] for item in DIMENSIONAL_CHAIN)


def test_render_chain_ascii_contains_markers() -> None:
    art = render_chain_ascii(DIMENSIONAL_CHAIN)
    assert '[*]' in art or '[=]' in art


def test_render_chain_ascii_contains_arrows() -> None:
    art = render_chain_ascii(DIMENSIONAL_CHAIN)
    assert 'v' in art


def test_render_chain_ascii_empty_chain() -> None:
    assert render_chain_ascii([]) == ''


def test_get_chain_json_shape() -> None:
    payload = get_chain_json()
    assert payload['pillar'] == 'P858'
    assert payload['step_count'] == 7


def test_get_chain_json_copies_data() -> None:
    payload = get_chain_json()
    payload['chain'][0]['name'] = 'changed'
    assert DIMENSIONAL_CHAIN[0]['name'] != 'changed'


def test_phi_constant_value() -> None:
    assert PHI == pytest.approx((1 + 5 ** 0.5) / 2)


def test_mass_hierarchy_default_dimensions() -> None:
    result = compute_mass_hierarchy()
    assert result['quark_count'] == 6
    assert result['lepton_count'] == 6
    assert len(result['matrix']) == 12


def test_mass_hierarchy_respects_requested_counts() -> None:
    result = compute_mass_hierarchy(n_quarks=3, n_leptons=2)
    assert len(result['labels']) == 5
    assert len(result['matrix']) == 5


def test_mass_hierarchy_diagonal_zero() -> None:
    result = compute_mass_hierarchy(n_quarks=2, n_leptons=2)
    assert all(result['matrix'][i][i] == pytest.approx(0.0) for i in range(4))


def test_mass_hierarchy_is_symmetric() -> None:
    result = compute_mass_hierarchy(n_quarks=2, n_leptons=2)
    assert result['matrix'][0][3] == pytest.approx(result['matrix'][3][0])


def test_mass_hierarchy_ordering_reflects_top_mass() -> None:
    result = compute_mass_hierarchy()
    assert result['masses_mev'][-1] > result['masses_mev'][0]


def test_render_heatmap_ascii_square_lines() -> None:
    art = render_heatmap_ascii([[0.0, 1.0], [1.0, 0.0]])
    lines = art.splitlines()
    assert len(lines) == 2
    assert all(len(line) == 2 for line in lines)


def test_render_heatmap_ascii_empty() -> None:
    assert render_heatmap_ascii([]) == ''


def test_render_heatmap_ascii_uses_multiple_shades() -> None:
    art = render_heatmap_ascii([[0.0, 5.0], [10.0, 2.5]])
    assert len(set(art.replace('\n', ''))) >= 3


def test_export_svg_heatmap_writes_svg() -> None:
    out = PRODUCT_ROOT / 'tests' / 'generated-heatmap.svg'
    try:
        export_svg_heatmap([[0.0, 1.0], [1.0, 0.0]], str(out))
        text = out.read_text(encoding='utf-8')
        assert text.startswith('<svg')
        assert '<rect' in text
    finally:
        if out.exists():
            out.unlink()


def test_export_svg_heatmap_dimensions() -> None:
    out = PRODUCT_ROOT / 'tests' / 'generated-heatmap-2.svg'
    try:
        export_svg_heatmap([[0.0, 1.0, 2.0]], str(out))
        text = out.read_text(encoding='utf-8')
        assert 'width="54"' in text
        assert 'height="18"' in text
    finally:
        if out.exists():
            out.unlink()
