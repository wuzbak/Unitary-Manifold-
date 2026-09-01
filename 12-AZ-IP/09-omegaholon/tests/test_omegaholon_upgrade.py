# Copyright (C) 2026  ThomasCory Walker-Pearson
import json
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from omegaholon.engine.pillar_live_feeds import (
    PILLAR_CLIMATE_REF,
    PILLAR_ECOLOGY_REF,
    PILLAR_MARINE_REF,
    PILLAR_PSYCHOLOGY_REF,
    build_holon_map,
    export_holon_as_jsonld,
    get_climate_status,
    get_ecology_status,
)
from omegaholon.engine.wellbeing_metrics import PHI, PSYCHOLOGY_PILLARS, compute_phi_coherence


def test_pillar_refs_are_defined():
    assert (PILLAR_ECOLOGY_REF, PILLAR_CLIMATE_REF, PILLAR_MARINE_REF, PILLAR_PSYCHOLOGY_REF) == ('P021', 'P022', 'P023', 'P024')


def test_get_ecology_status_shape():
    status = get_ecology_status()
    assert status['pillar'] == 'P021'
    assert status['status'] == 'HARDGATE'


def test_get_ecology_status_phi_coupling():
    assert get_ecology_status()['phi_coupling'] == 35 / 74


def test_get_climate_status_shape():
    status = get_climate_status()
    assert status['pillar'] == 'P022'
    assert status['status'] == 'HARDGATE'


def test_build_holon_map_preserves_root_name():
    holon = build_holon_map(['self', 'family', 'community', 'biosphere'])
    assert holon['root']['name'] == 'self'


def test_build_holon_map_builds_all_levels():
    holon = build_holon_map(['self', 'family', 'community', 'biosphere'])
    assert len(holon['levels']) == 4


def test_build_holon_map_nests_children():
    holon = build_holon_map(['self', 'family'])
    assert holon['root']['children'][0]['name'] == 'family'


def test_build_holon_map_phi_coupling_decreases_by_level():
    holon = build_holon_map(['self', 'family', 'community'])
    assert holon['levels'][0]['phi_coupling'] > holon['levels'][1]['phi_coupling'] > holon['levels'][2]['phi_coupling']


def test_build_holon_map_empty_input_uses_default_root():
    holon = build_holon_map([])
    assert holon['root']['name'] == 'self'
    assert len(holon['levels']) == 1


def test_export_holon_as_jsonld_round_trips():
    payload = json.loads(export_holon_as_jsonld(build_holon_map(['self', 'family'])))
    assert payload['@type'] == 'HolonMap'
    assert payload['root']['name'] == 'self'


def test_export_holon_as_jsonld_includes_context():
    payload = json.loads(export_holon_as_jsonld(build_holon_map(['self'])))
    assert '@context' in payload
    assert 'phiCoupling' in payload['@context']


def test_phi_constant_is_golden_ratio():
    assert round(PHI, 6) == 1.618034


def test_psychology_pillars_share_reference():
    assert set(PSYCHOLOGY_PILLARS.values()) == {'P024'}


def test_compute_phi_coherence_empty_metrics_is_zero():
    assert compute_phi_coherence({}) == 0.0


def test_compute_phi_coherence_is_bounded():
    score = compute_phi_coherence({'sleep': 10, 'mood': 8, 'focus': 9})
    assert 0.0 <= score <= 1.0


def test_compute_phi_coherence_rewards_balance():
    balanced = compute_phi_coherence({'sleep': 8, 'mood': 8, 'focus': 8})
    imbalanced = compute_phi_coherence({'sleep': 10, 'mood': 1, 'focus': 10})
    assert balanced > imbalanced


def test_compute_phi_coherence_accepts_fractional_inputs():
    score = compute_phi_coherence({'sleep': 0.8, 'mood': 0.6})
    assert 0.0 <= score <= 1.0
