# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for allow-listed open-data fetching and CSV parsing."""

import hashlib

import pytest

from eige.data.open_data import (
    OpenDataError, dataverse_url, fetch, openelections_url,
    parse_medsl_county_csv, parse_openelections_csv,
)


def test_url_builders_and_allow_list_rejections():
    assert openelections_url("WA", "2020/results.csv", ref="main") == "https://raw.githubusercontent.com/openelections/openelections-data-wa/main/2020/results.csv"
    assert dataverse_url(123) == "https://dataverse.harvard.edu/api/access/datafile/123"
    for args in [("w", "x.csv"), ("wa", "../x.csv"), ("wa", "x.txt")]:
        with pytest.raises(OpenDataError):
            openelections_url(*args)
    with pytest.raises(OpenDataError):
        dataverse_url(0)
    with pytest.raises(OpenDataError):
        fetch("http://raw.githubusercontent.com/x/y", "bad", opener=lambda u, t: b"")
    with pytest.raises(OpenDataError):
        fetch("https://example.com/file.csv", "bad", opener=lambda u, t: b"")


def test_fetch_uses_injected_opener_and_checks_sha_without_network():
    data = b"county,office,candidate,votes\nA,Mayor,Alice,10\n"
    url = openelections_url("wa", "2020/results.csv")
    calls = []
    def opener(u, timeout):
        calls.append((u, timeout)); return data
    fetched = fetch(url, "OpenElections", expected_sha256=hashlib.sha256(data).hexdigest(), timeout=1.5, opener=opener)
    assert fetched.data == data
    assert fetched.provenance.sha256 == hashlib.sha256(data).hexdigest()
    assert calls == [(url, 1.5)]
    with pytest.raises(OpenDataError):
        fetch(url, "OpenElections", expected_sha256="0" * 64, opener=opener)


def test_openelections_csv_parser_and_malformed_rows_fail_loudly():
    rows = parse_openelections_csv(b"county,office,district,party,candidate,votes\nKing,Mayor,,D,Alice,1,234\n".replace(b"1,234", b"1234"))
    assert rows[0].jurisdiction == "King" and rows[0].votes == 1234
    precinct = parse_openelections_csv(b"precinct,office,candidate,votes\nP1,Mayor,Bob,5\n", level="precinct")
    assert precinct[0].jurisdiction == "P1"
    for bad in [b"county,office,candidate\nA,Mayor,Alice\n", b"county,office,candidate,votes\nA,Mayor,Alice,nope\n"]:
        with pytest.raises(OpenDataError):
            parse_openelections_csv(bad)
    with pytest.raises(OpenDataError):
        parse_openelections_csv(b"", level="ward")


def test_medsl_csv_parser_and_malformed_rows_fail_loudly():
    data = b"year,state,state_po,county_name,county_fips,office,candidate,party,candidatevotes,totalvotes\n2020,Washington,WA,King,53033,President,Alice,D,100,200\n"
    row = parse_medsl_county_csv(data)[0]
    assert row.jurisdiction == "WA:King" and row.total_votes == 200
    with pytest.raises(OpenDataError):
        parse_medsl_county_csv(b"state_po,county_name,office,candidate,party,candidatevotes,totalvotes\nWA,King,President,Alice,D,xx,200\n")
    with pytest.raises(OpenDataError):
        parse_medsl_county_csv(b"\xff\xff")
