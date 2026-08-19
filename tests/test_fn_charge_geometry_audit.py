# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Sprint AL Wave 4: FN charge geometry audit."""
import pytest
from src.core.fn_charge_geometry_audit import (
    fn_charge_table,
    geometric_fn_hypothesis_test,
    free_parameter_count,
    fn_geometry_audit,
    fermion_mass_gap4_certificate,
    FN_AUDIT_STATUS,
    N_FREE_PARAMETERS_EXACT,
)


def test_status_token():
    assert FN_AUDIT_STATUS == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_fn_table_nonempty():
    table = fn_charge_table()
    assert len(table) > 0


def test_fn_table_has_15_entries():
    table = fn_charge_table()
    assert len(table) == 15


def test_fn_table_has_name_field():
    table = fn_charge_table()
    for row in table:
        assert "name" in row


def test_fn_table_has_fn_charge():
    table = fn_charge_table()
    for row in table:
        assert "Q_FN" in row


def test_n_free_params_positive():
    assert N_FREE_PARAMETERS_EXACT > 0


def test_free_parameter_count_returns_dict():
    r = free_parameter_count()
    assert isinstance(r, dict)
    assert "n_independent_free" in r


def test_free_parameter_count_nine_independent():
    r = free_parameter_count()
    assert r["n_independent_free"] == 9


def test_geometric_hypothesis_returns_dict():
    result = geometric_fn_hypothesis_test()
    assert isinstance(result, dict)


def test_geometry_audit_status():
    audit = fn_geometry_audit()
    assert audit["FN_AUDIT_STATUS"] == "ARCHITECTURE_LIMIT_CERTIFIED"


def test_certificate_status():
    cert = fermion_mass_gap4_certificate()
    assert cert["FN_AUDIT_STATUS"] == "ARCHITECTURE_LIMIT_CERTIFIED"
