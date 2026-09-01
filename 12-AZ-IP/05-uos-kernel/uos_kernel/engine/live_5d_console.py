# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Live 5D console helpers for the UOS kernel."""
from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

WINDING_NUMBER = 5
K_CS = 74
BRAIDED_SOUND_SPEED = 12 / 37
PHI_0 = 1.0
N_S = 0.9635
R_BRAIDED = 0.0315

_REPO_ROOT = Path(__file__).resolve().parents[4]
_AXIOM_PATH = _REPO_ROOT / 'COMPACTIFICATION' / 'axioms.py'
_FALLBACK_AXIOMS = [
    {'name': f'A{i}', 'label': f'Axiom {i}', 'status': 'POSTULATED' if i == 0 else 'DERIVED', 'lean4_ref': None, 'pillars': [1 + i]}
    for i in range(22)
]


def compute_5d_state(winding: int = 5) -> dict[str, float | int]:
    """Compute a compact 5D state summary from a winding number."""
    winding_value = int(winding)
    if winding_value <= 0:
        raise ValueError('winding must be positive')
    metric_curvature = winding_value * BRAIDED_SOUND_SPEED / K_CS
    kk_mass = math.sqrt(winding_value / K_CS)
    braided_speed = BRAIDED_SOUND_SPEED * winding_value / WINDING_NUMBER
    return {
        'winding': winding_value,
        'metric_curvature': round(metric_curvature, 8),
        'kk_mass': round(kk_mass, 8),
        'braided_speed': round(braided_speed, 8),
        'phi_0': PHI_0,
        'n_s': N_S,
        'r_braided': R_BRAIDED,
    }


def _load_axiom_registry() -> list[dict[str, object]]:
    if not _AXIOM_PATH.exists():
        return [dict(item) for item in _FALLBACK_AXIOMS]
    try:
        spec = importlib.util.spec_from_file_location('um_axioms', _AXIOM_PATH)
        if spec is None or spec.loader is None:
            raise ImportError('Could not load axiom module spec')
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        registry = []
        for axiom in getattr(module, 'AXIOM_REGISTRY', [])[:22]:
            registry.append({
                'name': axiom.name,
                'label': axiom.label,
                'status': axiom.status.value,
                'lean4_ref': axiom.lean4_ref,
                'pillars': list(axiom.pillars),
            })
        return registry or [dict(item) for item in _FALLBACK_AXIOMS]
    except Exception:
        return [dict(item) for item in _FALLBACK_AXIOMS]


def get_axiom_registry() -> list[dict[str, object]]:
    """Return the external COMPACTIFICATION axiom registry or a hardcoded fallback."""
    return _load_axiom_registry()


def parameter_sensitivity(param: str, delta: float) -> dict[str, object]:
    """Perturb one console parameter and report downstream changes."""
    baseline = compute_5d_state(WINDING_NUMBER)
    delta_value = float(delta)
    key = param.strip().lower()
    if key == 'winding':
        perturbed = compute_5d_state(max(1, round(WINDING_NUMBER + delta_value)))
    elif key == 'k_cs':
        perturbed_kcs = K_CS + delta_value
        if perturbed_kcs <= 0:
            raise ValueError('k_cs perturbation must keep K_CS positive')
        perturbed = dict(baseline)
        perturbed['metric_curvature'] = round(WINDING_NUMBER * BRAIDED_SOUND_SPEED / perturbed_kcs, 8)
        perturbed['kk_mass'] = round(math.sqrt(WINDING_NUMBER / perturbed_kcs), 8)
    elif key == 'braided_sound_speed':
        speed = BRAIDED_SOUND_SPEED + delta_value
        if speed <= 0:
            raise ValueError('braided_sound_speed perturbation must stay positive')
        perturbed = dict(baseline)
        perturbed['metric_curvature'] = round(WINDING_NUMBER * speed / K_CS, 8)
        perturbed['braided_speed'] = round(speed, 8)
    elif key == 'phi_0':
        perturbed = dict(baseline)
        perturbed['phi_0'] = round(PHI_0 + delta_value, 8)
    elif key == 'n_s':
        perturbed = dict(baseline)
        perturbed['n_s'] = round(N_S + delta_value, 8)
    elif key == 'r_braided':
        perturbed = dict(baseline)
        perturbed['r_braided'] = round(R_BRAIDED + delta_value, 8)
    else:
        raise KeyError(f'Unknown parameter: {param}')
    downstream = {
        metric: round(float(perturbed[metric]) - float(baseline[metric]), 8)
        for metric in ('metric_curvature', 'kk_mass', 'braided_speed', 'phi_0', 'n_s', 'r_braided')
    }
    return {
        'parameter': key,
        'delta': delta_value,
        'baseline': baseline,
        'perturbed': perturbed,
        'downstream_changes': downstream,
    }
