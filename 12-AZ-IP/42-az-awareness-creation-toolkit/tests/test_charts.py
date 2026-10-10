# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

import pytest

from az_awareness_creation_toolkit.charts import (
    ChartInputError,
    create_bar_chart_svg,
    create_line_chart_svg,
    create_pie_chart_svg,
)


def test_bar_chart_is_valid_svg_with_all_labels():
    svg = create_bar_chart_svg(["a", "b", "c"], [1, 2, 3], title="Demo")
    assert svg.startswith("<svg")
    assert svg.rstrip().endswith("</svg>")
    for label in ("a", "b", "c"):
        assert f">{label}<" in svg
    assert "Demo" in svg


def test_line_chart_produces_polyline_with_all_points():
    svg = create_line_chart_svg([1, 2, 3, 4], [10, 20, 15, 25])
    assert "<polyline" in svg
    assert svg.count("<circle") == 4


def test_pie_chart_slices_sum_to_full_circle():
    svg = create_pie_chart_svg(["x", "y", "z"], [1, 1, 2])
    assert svg.count("<path") == 3
    assert "x (25.0%)" in svg
    assert "z (50.0%)" in svg


def test_bar_chart_escapes_html_in_labels():
    svg = create_bar_chart_svg(["<script>", "b"], [1, 2])
    assert "<script>" not in svg
    assert "&lt;script&gt;" in svg


@pytest.mark.parametrize(
    "fn, labels, values",
    [
        (create_bar_chart_svg, [], []),
        (create_bar_chart_svg, ["a"], [1, 2]),
        (create_line_chart_svg, [1], []),
    ],
)
def test_mismatched_or_empty_input_raises(fn, labels, values):
    with pytest.raises(ChartInputError):
        fn(labels, values)


def test_pie_chart_rejects_non_positive_total():
    with pytest.raises(ChartInputError):
        create_pie_chart_svg(["a", "b"], [0, 0])


def test_bar_chart_rejects_non_numeric_values():
    with pytest.raises((ValueError, TypeError)):
        create_bar_chart_svg(["a"], ["not-a-number"])
