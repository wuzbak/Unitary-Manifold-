# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from az_awareness_creation_toolkit.citations import (
    parse_citation_string,
    verify_citation_string,
)


def test_parse_single_citation():
    tokens = parse_citation_string("src/core/metric.py:33-41")
    assert tokens == [("src/core/metric.py", "33-41")]


def test_parse_multiple_citations_in_one_string():
    text = (
        "src/core/regression_supervision_plan.py:151-152, "
        "tests/test_regression_supervision_plan.py:223-252"
    )
    tokens = parse_citation_string(text)
    assert tokens == [
        ("src/core/regression_supervision_plan.py", "151-152"),
        ("tests/test_regression_supervision_plan.py", "223-252"),
    ]


def test_parse_citation_with_multiple_ranges_same_file():
    tokens = parse_citation_string("TOOLS/checks/run_supervised_pytest_batch.py:96-123,257-265,503-515")
    assert len(tokens) == 1
    assert tokens[0][1] == "96-123,257-265,503-515"


def test_verify_citation_real_file_and_valid_range():
    results = verify_citation_string("src/core/metric.py:1-5")
    assert len(results) == 1
    result = results[0]
    assert result.file_exists is True
    assert result.verified is True
    assert result.line_ranges == ((1, 5),)


def test_verify_citation_out_of_range_line():
    results = verify_citation_string("src/core/metric.py:999999-1000000")
    result = results[0]
    assert result.file_exists is True
    assert result.verified is False
    assert result.invalid_ranges


def test_verify_citation_missing_file():
    results = verify_citation_string("src/core/this_file_does_not_exist_anywhere.py:1")
    result = results[0]
    assert result.file_exists is False
    assert result.verified is False


def test_verify_citation_path_escape_rejected():
    results = verify_citation_string("../../etc/passwd:1")
    # A path with no recognizable extension before ':' may not even match the
    # citation pattern; if it does, it must never be reported as verified.
    for result in results:
        assert result.verified is False


def test_verify_citation_string_with_no_citation_returns_empty():
    assert verify_citation_string("no citation here at all") == []


def test_verify_citation_single_line_number():
    results = verify_citation_string("src/core/metric.py:10")
    assert results[0].line_ranges == ((10, 10),)
