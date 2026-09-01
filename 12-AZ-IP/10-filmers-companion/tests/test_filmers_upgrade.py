# Copyright (C) 2026  ThomasCory Walker-Pearson
import sys
from pathlib import Path

PRODUCT_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ROOT))

from filmers_companion.engine.science_citation_checker import HARDGATE_FACTS, check_script_claims, format_citation_report
from filmers_companion.engine.um_visual_language import PHI_TONE_MAP, UM_VISUAL_LANGUAGE, generate_shot_list_entry, map_scene_to_phi


def test_um_visual_language_has_five_profiles():
    assert len(UM_VISUAL_LANGUAGE) == 5


def test_um_visual_language_entries_have_required_keys():
    assert {'texture', 'color_family', 'motion', 'phi_value'} <= set(UM_VISUAL_LANGUAGE['pillar_1_5d_metric'])


def test_phi_tone_map_has_four_ranges():
    assert len(PHI_TONE_MAP) == 4


def test_map_scene_to_phi_returns_expected_keys():
    result = map_scene_to_phi('awe', 0.8)
    assert {'phi_state', 'suggested_texture', 'color', 'motion'} <= set(result)


def test_map_scene_to_phi_binds_intensity_to_zero_one():
    low = map_scene_to_phi('focus', -1)
    high = map_scene_to_phi('focus', 5)
    assert 0.0 <= low['phi_state'] <= 1.0
    assert 0.0 <= high['phi_state'] <= 1.0


def test_map_scene_to_phi_uses_ecology_profile_for_hope():
    result = map_scene_to_phi('hope', 0.7)
    assert result['pillar_key'] == 'pillar_21_ecology'


def test_map_scene_to_phi_defaults_unknown_emotion_to_fixed_point():
    result = map_scene_to_phi('mystery', 0.4)
    assert result['pillar_key'] == 'pillar_5_fixed_point'


def test_map_scene_to_phi_returns_known_color_family():
    result = map_scene_to_phi('tension', 0.4)
    assert result['base_color_family'] == UM_VISUAL_LANGUAGE['pillar_1_5d_metric']['color_family']


def test_generate_shot_list_entry_carries_scene_description():
    phi_state = map_scene_to_phi('intimacy', 0.6)
    entry = generate_shot_list_entry('A quiet confession', phi_state)
    assert entry['scene_description'] == 'A quiet confession'


def test_generate_shot_list_entry_uses_motion_and_texture():
    phi_state = map_scene_to_phi('intimacy', 0.6)
    entry = generate_shot_list_entry('A quiet confession', phi_state)
    assert entry['motion'] == phi_state['motion']
    assert entry['texture'] == phi_state['suggested_texture']


def test_hardgate_facts_minimum_count():
    assert len(HARDGATE_FACTS) >= 10


def test_hardgate_facts_have_required_fields():
    assert {'fact', 'pillar', 'confidence', 'keywords'} <= set(HARDGATE_FACTS[0])


def test_check_script_claims_finds_multiple_matches():
    text = 'The 5 compact dimensions of the KK model pair with holography and a fixed-point multiverse.'
    matches = check_script_claims(text)
    pillars = {match['pillar'] for match in matches}
    assert {'P001', 'P004', 'P005'} <= pillars


def test_check_script_claims_returns_empty_when_no_matches():
    assert check_script_claims('A family dinner scene with no science dialogue.') == []


def test_check_script_claims_records_keywords():
    matches = check_script_claims('The braided sound speed is 12/37.')
    assert '12/37' in matches[0]['matched_keywords']


def test_format_citation_report_for_matches():
    report = format_citation_report([{'pillar': 'P001', 'confidence': 'HARDGATE', 'fact': 'Fact'}])
    assert 'P001' in report
    assert 'Fact' in report


def test_format_citation_report_for_empty_matches():
    assert format_citation_report([]) == 'No hardgate science citations detected.'
