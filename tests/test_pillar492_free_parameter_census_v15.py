# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 492 — free-parameter final census v15."""
from __future__ import annotations

import pytest

from src.core.pillar492_free_parameter_census_v15 import (
    DERIVED_QUANTITIES,
    OBSERVATIONAL_ANCHORS,
    PILLAR_LABEL,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    STRUCTURAL_FREE_PARAMETERS,
    VERSION,
    derived_quantity_names,
    free_parameter_census,
    observational_anchor_names,
    status_report,
    structural_free_parameter_count,
)


class TestConstants:
    def test_label(self):
        assert PILLAR_LABEL == 'FREE_PARAMETER_FINAL_CENSUS_V15'

    def test_status(self):
        assert PILLAR_STATUS == PILLAR_LABEL

    def test_number(self):
        assert PILLAR_NUMBER == 492

    def test_version(self):
        assert VERSION == 'v15.0'

    def test_structural_free_parameters_empty(self):
        assert STRUCTURAL_FREE_PARAMETERS == ()

    def test_anchor_count(self):
        assert len(OBSERVATIONAL_ANCHORS) == 3

    def test_derived_quantity_count(self):
        assert len(DERIVED_QUANTITIES) == 6


@pytest.mark.parametrize('name', ['n_w', 'k_CS', 'M_5D'])
def test_anchor_names_present(name):
    assert name in OBSERVATIONAL_ANCHORS


@pytest.mark.parametrize('name', DERIVED_QUANTITIES)
def test_derived_quantity_names_present(name):
    assert name in derived_quantity_names()


class TestCensus:
    def test_structural_free_parameter_count(self):
        assert structural_free_parameter_count() == 0

    def test_census_structural_count(self):
        assert free_parameter_census()['structural_free_parameter_count'] == 0

    def test_census_anchor_count(self):
        assert free_parameter_census()['observational_anchor_count'] == 3

    def test_census_mentions_zero_free(self):
        assert '0 structural free parameters' in free_parameter_census()['framework_statement']

    def test_anchor_names_roundtrip(self):
        assert observational_anchor_names() == ['n_w', 'k_CS', 'M_5D']

    def test_nw_source(self):
        assert OBSERVATIONAL_ANCHORS['n_w']['source'] == 'Planck n_s selection'

    def test_kcs_source(self):
        assert OBSERVATIONAL_ANCHORS['k_CS']['source'] == 'birefringence selection'

    def test_m5d_source(self):
        assert OBSERVATIONAL_ANCHORS['M_5D']['source'] == 'GW normalization'


class TestStatusReport:
    def test_report_pillar(self):
        assert status_report()['pillar'] == 492

    def test_report_label(self):
        assert status_report()['label'] == PILLAR_LABEL

    def test_report_status(self):
        assert status_report()['status'] == PILLAR_STATUS

    def test_report_version(self):
        assert status_report()['version'] == VERSION

    def test_report_structural_zero(self):
        assert status_report()['census']['structural_free_parameter_count'] == 0

    def test_report_census(self):
        assert status_report()['census']['observational_anchor_count'] == 3
