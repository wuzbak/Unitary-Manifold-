# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 422 — Baryogenesis Exhaustion Certificate."""
import pytest

from src.core.pillar422_baryogenesis_exhaustion_certificate import (
    PILLAR_STATUS,
    ETA_B_OBSERVED,
    N_PATHS_AUDITED,
    baryogenesis_paths_registry,
    all_paths_architecture_limit,
    baryogenesis_exhaustion_verdict,
    extension_requirements,
)

PATHS = baryogenesis_paths_registry()


class TestConstants:
    def test_status(self):
        assert PILLAR_STATUS == 'ALL_BARYOGENESIS_PATHS_EXHAUSTED'

    def test_eta_b_observed_order_of_magnitude(self):
        assert 1e-12 < ETA_B_OBSERVED < 1e-8

    def test_n_paths_five(self):
        assert N_PATHS_AUDITED == 5


class TestBaryogenesisPathsRegistry:
    def test_returns_five_entries(self):
        assert len(PATHS) == 5

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4])
    def test_each_has_path_number(self, idx):
        assert 'path' in PATHS[idx]
        assert PATHS[idx]['path'] == idx + 1

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4])
    def test_each_has_name(self, idx):
        assert 'name' in PATHS[idx]
        assert len(PATHS[idx]['name']) > 5

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4])
    def test_each_has_blocker(self, idx):
        assert 'blocker' in PATHS[idx]

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4])
    def test_each_is_architecture_limit(self, idx):
        assert PATHS[idx]['status'] == 'ARCHITECTURE_LIMIT'

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4])
    def test_each_has_source_pillar(self, idx):
        assert 'source_pillar' in PATHS[idx]

    @pytest.mark.parametrize('idx', [0, 1, 2, 3, 4])
    def test_each_has_closed_by(self, idx):
        assert 'closed_by' in PATHS[idx]

    def test_path_names_unique(self):
        names = [p['name'] for p in PATHS]
        assert len(set(names)) == 5

    def test_path2_central_estimate_low(self):
        path2 = PATHS[1]
        assert path2['eta_b_estimate'] < ETA_B_OBSERVED * 1e-2


class TestAllPathsArchitectureLimit:
    def test_returns_true(self):
        assert all_paths_architecture_limit() is True


class TestExtensionRequirements:
    def test_returns_dict(self):
        assert isinstance(extension_requirements(), dict)

    def test_status_extension_required(self):
        ext = extension_requirements()
        assert ext['status'] == 'EXTENSION_REQUIRED'

    def test_minimal_eft_exhausted(self):
        ext = extension_requirements()
        assert ext['minimal_5d_eft'] == 'ALL_PATHS_EXHAUSTED'

    def test_has_possible_extensions(self):
        ext = extension_requirements()
        assert 'possible_extensions' in ext
        assert len(ext['possible_extensions']) >= 3

    def test_has_honest_statement(self):
        ext = extension_requirements()
        assert 'honest_statement' in ext
        assert len(ext['honest_statement']) > 100


class TestBaryogenesisExhaustionVerdict:
    def test_returns_dict(self):
        assert isinstance(baryogenesis_exhaustion_verdict(), dict)

    def test_status(self):
        assert baryogenesis_exhaustion_verdict()['status'] == 'ALL_BARYOGENESIS_PATHS_EXHAUSTED'

    @pytest.mark.parametrize('key', ['n_paths_audited', 'all_exhausted', 'eta_b_observed',
                                     'paths', 'extension', 'verdict'])
    def test_expected_keys(self, key):
        assert key in baryogenesis_exhaustion_verdict()

    def test_n_paths_correct(self):
        assert baryogenesis_exhaustion_verdict()['n_paths_audited'] == 5

    def test_all_exhausted(self):
        assert baryogenesis_exhaustion_verdict()['all_exhausted'] is True

    def test_verdict_is_string(self):
        assert isinstance(baryogenesis_exhaustion_verdict()['verdict'], str)

    def test_verdict_mentions_architecture_limit(self):
        verdict_text = baryogenesis_exhaustion_verdict()['verdict']
        assert 'ARCHITECTURE_LIMIT' in verdict_text
