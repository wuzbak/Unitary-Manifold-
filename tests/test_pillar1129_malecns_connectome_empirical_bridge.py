# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
"""Tests for Pillar 1129 — MaleCNS Connectome Empirical Bridge."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.pillar1129_malecns_connectome_empirical_bridge import (
    DEFAULT_BENCHMARK_PATH,
    MALECNS_DATASET,
    MALECNS_DATASET_UUID,
    NEURON_COUNT_ESTIMATE,
    PILLAR_ADJACENCY,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TRACK,
    PRIMARY_REGIONS,
    PUBLIC_INTERFACES,
    SYNAPSE_COUNT_ESTIMATE,
    TOTAL_NEURON_TYPES,
    __provenance__,
    aggregate_observables,
    benchmark_names,
    benchmark_panel,
    benchmark_panel_findings,
    concentration_ranking,
    cross_domain_bridge_types,
    load_benchmark_payload,
    malecns_manifest,
    neurotransmitter_entropy_ranking,
    parse_partner_table_html,
    parse_public_type_page_html,
    parse_roi_table_html,
    pillar1129_report,
    reciprocity_ranking,
)


FIXTURE_DIR = Path(__file__).resolve().parent / 'fixtures' / 'malecns'


class TestModuleConstants:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 1129

    def test_pillar_status(self):
        assert PILLAR_STATUS == 'EMPIRICAL_CONNECTOME_BRIDGE'

    def test_adjacency(self):
        assert PILLAR_ADJACENCY == 'ADJACENT_TRACK_ONLY'
        assert 'ADJACENT TRACK' in PILLAR_TRACK

    def test_dataset_constants(self):
        assert MALECNS_DATASET == 'male-cns:v1.0'
        assert MALECNS_DATASET_UUID == '4b2087c0fbe046bfaf0d60bc970e3e5d'
        assert NEURON_COUNT_ESTIMATE == 166700
        assert SYNAPSE_COUNT_ESTIMATE == 125000000
        assert TOTAL_NEURON_TYPES == 11751

    def test_primary_regions(self):
        assert PRIMARY_REGIONS == ('central brain', 'optic lobes', 'ventral nerve cord')

    def test_public_interfaces(self):
        assert PUBLIC_INTERFACES['neuprint_dataset'] == 'male-cns:v1.0'
        assert 'github.com/reiserlab/celltype-explorer-drosophila-male-cns' in PUBLIC_INTERFACES['cell_type_explorer_repo']
        assert 'flyem-male-cns/rois/malecns-major-compartments-v2' in PUBLIC_INTERFACES['neuroglancer_major_compartments']


class TestProvenance:
    def test_provenance_fields(self):
        assert __provenance__['pillar'] == 1129
        assert __provenance__['toe_delta'] == 0.0
        assert __provenance__['source_dataset'] == 'male-cns:v1.0'
        assert 'MALECNS_CONNECTOME_BRIDGE.md' in __provenance__['source_document']


class TestFixtureParsers:
    def test_parse_upstream_partner_table(self):
        table = (FIXTURE_DIR / 'lplc2_upstream_table.html').read_text(encoding='utf-8')
        rows = parse_partner_table_html(table)
        assert len(rows) == 536
        assert rows[0]['partner'] == 'LPLC2'
        assert rows[0]['synapses'] == 46178
        assert rows[0]['neurotransmitter'] == 'acetylcholine'

    def test_parse_downstream_partner_table(self):
        table = (FIXTURE_DIR / 'lplc2_downstream_table.html').read_text(encoding='utf-8')
        rows = parse_partner_table_html(table)
        assert len(rows) == 692
        assert rows[0]['partner'] == 'LPLC2'
        assert rows[0]['synapses'] == 46178
        assert rows[1]['partner'] == 'PVLP111'

    def test_parse_roi_table(self):
        table = (FIXTURE_DIR / 'lplc2_roi_table.html').read_text(encoding='utf-8')
        rows = parse_roi_table_html(table)
        assert len(rows) == 8
        assert rows[0]['roi'] == 'LOP'
        assert rows[0]['input_synapses'] == 159999
        assert rows[2]['roi'] == 'PVLP'
        assert rows[2]['output_synapses'] == 48310

    def test_parse_public_page_composition(self):
        html = '\n'.join([
            (FIXTURE_DIR / 'lplc2_upstream_table.html').read_text(encoding='utf-8'),
            (FIXTURE_DIR / 'lplc2_downstream_table.html').read_text(encoding='utf-8'),
            (FIXTURE_DIR / 'lplc2_roi_table.html').read_text(encoding='utf-8'),
        ])
        parsed = parse_public_type_page_html(html)
        assert set(parsed) == {'upstream', 'downstream', 'roi'}
        assert len(parsed['upstream']) == 536
        assert len(parsed['downstream']) == 692
        assert len(parsed['roi']) == 8

    def test_parse_public_page_missing_table_raises(self):
        html = '\n'.join([
            (FIXTURE_DIR / 'lplc2_upstream_table.html').read_text(encoding='utf-8'),
            (FIXTURE_DIR / 'lplc2_roi_table.html').read_text(encoding='utf-8'),
        ])
        with pytest.raises(ValueError, match='downstream-table'):
            parse_public_type_page_html(html)


class TestBenchmarkPayload:
    def test_benchmark_payload_exists(self):
        assert DEFAULT_BENCHMARK_PATH.exists()

    def test_load_payload(self):
        payload = load_benchmark_payload()
        assert 'manifest' in payload
        assert 'benchmark_panel' in payload
        assert 'aggregate_observables' in payload

    def test_manifest(self):
        manifest = malecns_manifest()
        assert manifest['dataset'] == 'male-cns:v1.0'
        assert manifest['dataset_uuid'] == '4b2087c0fbe046bfaf0d60bc970e3e5d'
        assert manifest['benchmark_panel_size'] == 7
        assert manifest['total_neuron_types'] == 11751

    def test_benchmark_names(self):
        assert benchmark_names() == ['LPLC2', 'LC4', 'EPG', 'AN01B004', 'DNa02', 'MN5', '5-HTPLP01']

    def test_panel_rows_have_required_keys(self):
        row = benchmark_panel()[0]
        for key in ['name', 'role', 'synapse_totals', 'reciprocity', 'concentration', 'macro_domain', 'top_partners', 'top_rois']:
            assert key in row

    def test_aggregate_observables(self):
        agg = aggregate_observables()
        assert agg['highest_input_type'] == 'LPLC2'
        assert agg['highest_output_type'] == 'LPLC2'
        assert agg['most_reciprocal_type'] == 'LC4'
        assert agg['most_diffuse_output_type'] == 'EPG'
        assert agg['dominant_domain_counts']['optic_lobe'] == 2
        assert agg['dominant_domain_counts']['central_brain'] == 4
        assert agg['dominant_domain_counts']['vnc_or_motor'] == 1


class TestDerivedRankings:
    def test_cross_domain_bridge_types(self):
        assert cross_domain_bridge_types() == ['AN01B004', 'DNa02']

    def test_reciprocity_ranking(self):
        ranking = reciprocity_ranking()
        assert ranking[0]['name'] == 'LC4'
        assert ranking[-1]['name'] == 'DNa02'
        assert ranking[0]['jaccard'] > ranking[-1]['jaccard']
        assert isinstance(ranking[0]['jaccard'], float)

    def test_entropy_ranking(self):
        ranking = neurotransmitter_entropy_ranking('downstream')
        assert ranking[0]['name'] == 'EPG'
        assert ranking[-1]['name'] == '5-HTPLP01'
        assert isinstance(ranking[0]['entropy_bits'], float)

    def test_entropy_bad_direction_raises(self):
        with pytest.raises(ValueError):
            neurotransmitter_entropy_ranking('sideways')

    def test_concentration_ranking(self):
        ranking = concentration_ranking()
        assert ranking[0]['name'] == 'EPG'
        assert ranking[1]['name'] == 'LPLC2'
        assert ranking[0]['top5_output_share'] > ranking[-1]['top5_output_share']
        assert isinstance(ranking[0]['top5_input_share'], float)
        assert isinstance(ranking[0]['top5_output_share'], float)


class TestReport:
    def test_findings(self):
        findings = benchmark_panel_findings()
        assert len(findings) == 5
        assert '7 real public neuron-type pages' in findings[0]
        assert 'LPLC2 carries the largest benchmark input and output mass' in findings[1]
        assert 'mean partner-set Jaccard overlap is 0.440' in findings[2]
        assert 'AN01B004, DNa02' in findings[3]
        assert findings[4].startswith('EPG has the highest downstream neurotransmitter entropy')

    def test_report_shape(self):
        report = pillar1129_report()
        assert report['pillar_number'] == 1129
        assert report['status'] == 'EMPIRICAL_CONNECTOME_BRIDGE'
        assert report['benchmark_names'][0] == 'LPLC2'
        assert report['cross_domain_bridge_types'] == ['AN01B004', 'DNa02']
        assert report['reciprocity_ranking'][0]['name'] == 'LC4'
        assert report['downstream_entropy_ranking'][0]['name'] == 'EPG'
        assert 'Adjacent-track empirical connectome bridge only' in report['epistemic_boundary']
