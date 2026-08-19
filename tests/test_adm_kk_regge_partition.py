# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DPC-1.0
"""Tests for Sprint AK Wave 3: ADM KK Regge partition / arrow of time."""
import pytest
from src.core.adm_kk_regge_partition import (
    regge_edge_length_saddle,
    regge_partition_function_semiclassical,
    entropy_arrow_of_time,
    regge_regularisation_audit,
    adm_gap2_certificate,
    ADM_REGGE_STATUS,
    REGULATOR_CHOICE,
)


def test_status_token():
    assert ADM_REGGE_STATUS == "MECHANISM_IDENTIFIED_WITH_FORMAL_BOUND"


def test_regulator_is_regge():
    assert "REGGE" in REGULATOR_CHOICE


def test_edge_length_saddle_positive():
    r = regge_edge_length_saddle()
    assert r["edge_length_GeV_inv"] > 0


def test_partition_function_positive():
    r = regge_partition_function_semiclassical()
    assert r["Z_positive"] is True


def test_entropy_arrow_positive():
    r = entropy_arrow_of_time()
    assert r["arrow_of_time_demonstrated"] is True


def test_audit_status():
    audit = regge_regularisation_audit()
    assert audit["ADM_REGGE_STATUS"] == "MECHANISM_IDENTIFIED_WITH_FORMAL_BOUND"


def test_audit_arrow_demonstrated():
    audit = regge_regularisation_audit()
    arrow = audit["arrow_of_time"]
    assert arrow["arrow_of_time_demonstrated"] is True


def test_audit_partition_positive():
    audit = regge_regularisation_audit()
    pf = audit["partition_function"]
    assert pf["Z_positive"] is True


def test_certificate_status():
    cert = adm_gap2_certificate()
    assert cert["ADM_REGGE_STATUS"] == "MECHANISM_IDENTIFIED_WITH_FORMAL_BOUND"

def test_edge_length_saddle_dict_with_positive_value():
    r = regge_edge_length_saddle()
    assert isinstance(r, dict)
    assert r["edge_length_GeV_inv"] > 0

def test_partition_function_dict_z_positive():
    r = regge_partition_function_semiclassical()
    assert isinstance(r, dict)
    assert r["Z_positive"] is True

def test_entropy_arrow_is_dict():
    r = entropy_arrow_of_time()
    assert isinstance(r, dict)
    assert r["arrow_of_time_demonstrated"] is True
