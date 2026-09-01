# Copyright (C) 2026  ThomasCory Walker-Pearson
"""UM visual-language helpers for Filmers Companion."""
from __future__ import annotations

UM_VISUAL_LANGUAGE = {
    'pillar_1_5d_metric': {
        'texture': 'crystalline lattice',
        'color_family': 'deep blue-violet',
        'motion': 'spiral compactification',
        'phi_value': 0.618,
    },
    'pillar_4_holography': {
        'texture': 'glass boundary shimmer',
        'color_family': 'silver-cyan',
        'motion': 'breathing edge light',
        'phi_value': 0.664,
    },
    'pillar_5_fixed_point': {
        'texture': 'nested recursion rings',
        'color_family': 'amber-indigo',
        'motion': 'iterative orbital drift',
        'phi_value': 0.702,
    },
    'pillar_9_consciousness': {
        'texture': 'neuronal filaments',
        'color_family': 'gold-magenta',
        'motion': 'phase-locked pulsing',
        'phi_value': 0.746,
    },
    'pillar_21_ecology': {
        'texture': 'living canopy mesh',
        'color_family': 'verdant teal',
        'motion': 'fractal ecosystem sway',
        'phi_value': 0.789,
    },
}

PHI_TONE_MAP = {
    (0.0, 0.25): ('fractured', 'steel blue', 'wide locked-off'),
    (0.25, 0.5): ('searching', 'indigo', 'slow dolly'),
    (0.5, 0.75): ('coherent', 'violet-gold', 'medium tracking'),
    (0.75, 1.01): ('transcendent', 'luminous teal-gold', 'floating close-up'),
}

_EMOTION_TO_PILLAR = {
    'awe': 'pillar_4_holography',
    'wonder': 'pillar_4_holography',
    'focus': 'pillar_5_fixed_point',
    'tension': 'pillar_1_5d_metric',
    'conflict': 'pillar_1_5d_metric',
    'intimacy': 'pillar_9_consciousness',
    'empathy': 'pillar_9_consciousness',
    'renewal': 'pillar_21_ecology',
    'hope': 'pillar_21_ecology',
}


def _tone_for(phi_value: float) -> tuple[str, str, str]:
    for (low, high), tone in PHI_TONE_MAP.items():
        if low <= phi_value < high:
            return tone
    return list(PHI_TONE_MAP.values())[-1]


def map_scene_to_phi(emotion: str, intensity: float) -> dict:
    """Map a scene's emotional vector onto a φ-informed visual state."""
    pillar_key = _EMOTION_TO_PILLAR.get(emotion.lower(), 'pillar_5_fixed_point')
    profile = UM_VISUAL_LANGUAGE[pillar_key]
    bounded_intensity = min(1.0, max(0.0, float(intensity)))
    phi_state = round(min(1.0, max(0.0, profile['phi_value'] * 0.6 + bounded_intensity * 0.4)), 3)
    tone, color, shot_type = _tone_for(phi_state)
    return {
        'phi_state': phi_state,
        'pillar_key': pillar_key,
        'suggested_texture': profile['texture'],
        'color': color,
        'motion': profile['motion'],
        'base_color_family': profile['color_family'],
        'emotional_tone': tone,
        'suggested_shot_type': shot_type,
    }


def generate_shot_list_entry(scene_description: str, phi_state: dict) -> dict:
    """Generate a single shot-list entry from the mapped φ state."""
    return {
        'scene_description': scene_description,
        'coverage_type': phi_state.get('suggested_shot_type', 'medium tracking'),
        'texture': phi_state.get('suggested_texture', ''),
        'color': phi_state.get('color', ''),
        'motion': phi_state.get('motion', ''),
        'notes': f"{phi_state.get('emotional_tone', 'coherent').title()} tone aligned to {phi_state.get('pillar_key', 'pillar_5_fixed_point')}",
    }
