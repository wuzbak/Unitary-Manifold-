# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Tests for Pillar 167 — MAS Wave Engine."""

import pytest
from src.meta.mas_wave_engine import (
    MASWaveEngine, PillarSpec, GapItem, WaveValidationResult,
    FrameworkScore, AutodataReport, VALID_STATUSES
)


# --- Import / instantiation ---

def test_import_all():
    assert MASWaveEngine is not None
    assert PillarSpec is not None
    assert GapItem is not None
    assert WaveValidationResult is not None
    assert FrameworkScore is not None
    assert AutodataReport is not None

def test_instantiate():
    e = MASWaveEngine()
    assert e is not None

def test_version_contains_v9():
    assert 'v9' in MASWaveEngine.VERSION

def test_n_pillars():
    assert MASWaveEngine.N_PILLARS == 167

def test_known_gaps_nonempty():
    assert len(MASWaveEngine.KNOWN_GAPS) > 5

def test_quality_criteria_zero_failures():
    assert MASWaveEngine.QUALITY_CRITERIA['zero_failures'] is True

def test_quality_criteria_min_tests():
    assert MASWaveEngine.QUALITY_CRITERIA['min_tests'] == 40

def test_quality_criteria_epistemic_label():
    assert MASWaveEngine.QUALITY_CRITERIA['epistemic_label'] is True


# --- audit_open_gaps ---

def test_audit_open_gaps_returns_list():
    e = MASWaveEngine()
    result = e.audit_open_gaps()
    assert isinstance(result, list)

def test_audit_open_gaps_all_open_or_partially():
    e = MASWaveEngine()
    for g in e.audit_open_gaps():
        assert g.epistemic_status in ('OPEN', 'PARTIALLY_CLOSED')

def test_audit_open_gaps_nonempty():
    e = MASWaveEngine()
    assert len(e.audit_open_gaps()) > 0


# --- audit_all_gaps ---

def test_audit_all_gaps_returns_list():
    e = MASWaveEngine()
    assert isinstance(e.audit_all_gaps(), list)

def test_audit_all_gaps_gte_open():
    e = MASWaveEngine()
    assert len(e.audit_all_gaps()) >= len(e.audit_open_gaps())

def test_audit_all_gaps_contains_birefringence():
    e = MASWaveEngine()
    ids = [g.gap_id for g in e.audit_all_gaps()]
    assert 'birefringence' in ids


# --- get_gap_by_id ---

def test_get_gap_by_id_found():
    e = MASWaveEngine()
    g = e.get_gap_by_id('birefringence')
    assert g is not None
    assert g.gap_id == 'birefringence'

def test_get_gap_by_id_not_found():
    e = MASWaveEngine()
    assert e.get_gap_by_id('nonexistent') is None

def test_get_gap_by_id_w0():
    e = MASWaveEngine()
    g = e.get_gap_by_id('w0_tension')
    assert g is not None
    assert g.epistemic_status == 'PARTIALLY_CLOSED'

def test_get_gap_by_id_lambda_qcd():
    e = MASWaveEngine()
    g = e.get_gap_by_id('lambda_qcd')
    assert g.severity == 'minor'


# --- generate_pillar_spec ---

def test_generate_pillar_spec_lambda_qcd():
    e = MASWaveEngine()
    spec = e.generate_pillar_spec('lambda_qcd')
    assert isinstance(spec, PillarSpec)
    assert spec.pillar_number > 0
    assert spec.min_tests >= 40

def test_generate_pillar_spec_w0_tension():
    e = MASWaveEngine()
    spec = e.generate_pillar_spec('w0_tension')
    assert spec.epistemic_target == 'PARTIALLY_CLOSED'

def test_generate_pillar_spec_A_s():
    e = MASWaveEngine()
    spec = e.generate_pillar_spec('A_s_normalization')
    assert spec.epistemic_target == 'NATURALLY_BOUNDED'

def test_generate_pillar_spec_generic_fallback():
    e = MASWaveEngine()
    spec = e.generate_pillar_spec('g4_flux_embedding')
    assert isinstance(spec, PillarSpec)
    assert spec.pillar_number > 0

def test_generate_pillar_spec_invalid():
    e = MASWaveEngine()
    with pytest.raises(ValueError):
        e.generate_pillar_spec('does_not_exist_xyz')

def test_generate_pillar_spec_inputs_nonempty():
    e = MASWaveEngine()
    spec = e.generate_pillar_spec('lambda_qcd')
    assert len(spec.inputs) > 0

def test_generate_pillar_spec_outputs_nonempty():
    e = MASWaveEngine()
    spec = e.generate_pillar_spec('w0_tension')
    assert len(spec.expected_outputs) > 0


# --- validate_wave_output ---

def test_validate_valid():
    e = MASWaveEngine()
    r = e.validate_wave_output(167, 65, 0, 'DERIVED', True)
    assert r.overall_valid is True
    assert r.issues == []

def test_validate_one_failure():
    e = MASWaveEngine()
    r = e.validate_wave_output(167, 65, 1, 'DERIVED', True)
    assert r.overall_valid is False
    assert len(r.issues) > 0

def test_validate_invalid_label():
    e = MASWaveEngine()
    r = e.validate_wave_output(167, 65, 0, 'UNKNOWN_STATUS', True)
    assert r.has_epistemic_label is False

def test_validate_too_few_tests():
    e = MASWaveEngine()
    r = e.validate_wave_output(167, 10, 0, 'DERIVED', True)
    assert any('LOW_COVERAGE' in i for i in r.issues)
    assert r.overall_valid is False

def test_validate_no_fallibility():
    e = MASWaveEngine()
    r = e.validate_wave_output(167, 65, 0, 'DERIVED', False)
    assert r.has_fallibility_entry is False
    assert r.overall_valid is False

def test_validate_returns_correct_pillar():
    e = MASWaveEngine()
    r = e.validate_wave_output(42, 50, 0, 'CONSTRAINED', True)
    assert r.pillar_number == 42

def test_validate_has_honest_accounting_when_valid():
    e = MASWaveEngine()
    r = e.validate_wave_output(167, 65, 0, 'DERIVED', True)
    assert r.has_honest_accounting is True


# --- compute_framework_score ---

def test_framework_score_returns():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert isinstance(s, FrameworkScore)

def test_framework_score_closed_fraction_positive():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert s.closed_fraction > 0

def test_framework_score_open_fraction_nonneg():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert s.open_fraction >= 0

def test_framework_score_total_positive():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert s.total_pillars > 0

def test_framework_score_fractions_sum():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert s.closed_fraction + s.open_fraction <= 1.0

def test_framework_score_n_derived_positive():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert s.n_derived > 0

def test_framework_score_n_open_nonneg():
    e = MASWaveEngine()
    s = e.compute_framework_score()
    assert s.n_open >= 0


# --- autodata_quality_report ---

def test_autodata_report_returns():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert isinstance(r, AutodataReport)

def test_autodata_coverage_score_range():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert 0 <= r.coverage_score <= 1.0

def test_autodata_depth_score_range():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert 0 <= r.derivation_depth_score <= 1.0

def test_autodata_falsifiability_range():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert 0 <= r.falsifiability_score <= 1.0

def test_autodata_honest_accounting_range():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert 0 <= r.honest_accounting_score <= 1.0

def test_autodata_overall_quality_positive():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert r.overall_quality > 0

def test_autodata_n_pillars():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert r.n_pillars == 167

def test_autodata_version_matches():
    e = MASWaveEngine()
    r = e.autodata_quality_report()
    assert r.version == e.version


# --- wave_protocol_summary ---

def test_wave_protocol_summary_returns_dict():
    e = MASWaveEngine()
    s = e.wave_protocol_summary()
    assert isinstance(s, dict)

def test_wave_protocol_has_version():
    e = MASWaveEngine()
    assert 'version' in e.wave_protocol_summary()

def test_wave_protocol_has_n_pillars():
    e = MASWaveEngine()
    assert 'n_pillars' in e.wave_protocol_summary()

def test_wave_protocol_has_framework_score():
    e = MASWaveEngine()
    assert 'framework_score' in e.wave_protocol_summary()

def test_wave_protocol_has_quality_report():
    e = MASWaveEngine()
    assert 'quality_report' in e.wave_protocol_summary()

def test_wave_protocol_has_open_gaps():
    e = MASWaveEngine()
    assert 'open_gaps' in e.wave_protocol_summary()

def test_wave_protocol_epistemic_label_meta_closed():
    e = MASWaveEngine()
    assert e.wave_protocol_summary()['epistemic_label'] == 'META-CLOSED'

def test_wave_protocol_open_gaps_list():
    e = MASWaveEngine()
    assert isinstance(e.wave_protocol_summary()['open_gaps'], list)


# --- pillar167_summary ---

def test_pillar167_summary_pillar_number():
    e = MASWaveEngine()
    s = e.pillar167_summary()
    assert s['pillar'] == 167

def test_pillar167_summary_status():
    e = MASWaveEngine()
    assert e.pillar167_summary()['status'] == 'META-CLOSED'

def test_pillar167_summary_epistemic_label():
    e = MASWaveEngine()
    assert e.pillar167_summary()['epistemic_label'] == 'META-CLOSED'

def test_pillar167_summary_n_pillars():
    e = MASWaveEngine()
    assert e.pillar167_summary()['n_pillars'] == 167


# --- Dataclass creation ---

def test_gap_item_creation():
    g = GapItem('test', 'desc', 'OPEN', 'LiteBIRD', None, 'minor')
    assert g.gap_id == 'test'

def test_pillar_spec_creation():
    p = PillarSpec(168, 'test', 'method', ['a'], ['b'], 'strategy', 40, 'honest', 'DERIVED')
    assert p.pillar_number == 168

def test_wave_validation_result_creation():
    r = WaveValidationResult(167, 65, 0, True, True, True, True, [])
    assert r.overall_valid is True


# --- VALID_STATUSES ---

def test_valid_statuses_contains_derived():
    assert 'DERIVED' in VALID_STATUSES

def test_valid_statuses_contains_open():
    assert 'OPEN' in VALID_STATUSES

def test_valid_statuses_contains_constrained():
    assert 'CONSTRAINED' in VALID_STATUSES
