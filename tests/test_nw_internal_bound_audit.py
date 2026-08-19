# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Sprint AJ Wave 2: Axiom SW independence audit (n_w internal bound)."""
import pytest
from src.core.nw_internal_bound_audit import (
    mechanism_a_gw_stability,
    mechanism_b_unitarity,
    mechanism_c_compactification,
    internal_bound_audit,
    axiom_sw_independence_certificate,
    generate_audit_document,
    NW_INTERNAL_BOUND_STATUS,
)


def test_status_token():
    assert NW_INTERNAL_BOUND_STATUS == "AXIOM_SW_IRREDUCIBLE_POSTULATE"


def test_mechanism_a_returns_dict():
    r = mechanism_a_gw_stability()
    assert "mechanism" in r
    assert r["mechanism"] == "A"


def test_mechanism_a_has_bound():
    r = mechanism_a_gw_stability()
    assert "n_w_bound" in r


def test_mechanism_a_not_reliable():
    r = mechanism_a_gw_stability()
    assert r["reliable"] is False


def test_mechanism_b_returns_dict():
    r = mechanism_b_unitarity()
    assert "mechanism" in r
    assert r["mechanism"] == "B"


def test_mechanism_b_bound_much_weaker_than_sw():
    r = mechanism_b_unitarity()
    assert r["bound_much_weaker_than_sw"] is True


def test_mechanism_b_bound_large():
    r = mechanism_b_unitarity()
    assert r["n_w_bound"] > 100


def test_mechanism_c_returns_dict():
    r = mechanism_c_compactification()
    assert "mechanism" in r
    assert r["mechanism"] == "C"


def test_mechanism_c_conclusion_not_constraining():
    r = mechanism_c_compactification()
    assert "NOT_CONSTRAINING" in r["conclusion"]


def test_internal_bound_audit_no_internal_bound():
    audit = internal_bound_audit()
    assert audit["any_internal_bound_found"] is False


def test_internal_bound_audit_status():
    audit = internal_bound_audit()
    assert audit["NW_INTERNAL_BOUND_STATUS"] == "AXIOM_SW_IRREDUCIBLE_POSTULATE"


def test_internal_bound_audit_has_three_mechanisms():
    audit = internal_bound_audit()
    assert "mechanism_a" in audit
    assert "mechanism_b" in audit
    assert "mechanism_c" in audit


def test_certificate_status():
    cert = axiom_sw_independence_certificate()
    assert cert["NW_INTERNAL_BOUND_STATUS"] == "AXIOM_SW_IRREDUCIBLE_POSTULATE"


def test_certificate_no_internal_bound():
    cert = axiom_sw_independence_certificate()
    assert cert["any_internal_bound_found"] is False


def test_generate_audit_document_returns_string():
    doc = generate_audit_document()
    assert isinstance(doc, str)
    assert len(doc) > 100


def test_generate_audit_document_contains_result():
    doc = generate_audit_document()
    assert "AXIOM_SW_IRREDUCIBLE_POSTULATE" in doc
