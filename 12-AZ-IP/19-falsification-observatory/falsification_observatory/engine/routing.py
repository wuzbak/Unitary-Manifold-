# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Routing functions and lightweight API dispatch for the Falsification Observatory."""

from __future__ import annotations

from dataclasses import asdict

from .constants import (
    BETA_C1,
    BETA_C2,
    BETA_GAP_HI,
    BETA_GAP_LO,
    BETA_KILL_SIGMA,
    BETA_WIN_MAX,
    BETA_WIN_MIN,
    DM21_PRED,
    DM21_WIN_HI,
    DM21_WIN_LO,
    KK_DM_CS,
    MG_KILL_TEV,
    MG_PRED_TEV,
    NEDM_KILL,
    NEDM_PRED,
    NEDM_TENSION,
    N_S_KILL_SIGMA,
    N_S_PRED,
    WA_KILL_SIGMA,
    WA_PRED,
    XENON_SENS,
)
from .desi_tracker import DESI_DR3_PREREGISTRATION, check_desi_tension, get_falsification_status
from .litebird_countdown import BIREFRINGENCE_PREDICTION, assess_birefringence_measurement, days_to_litebird
from .verdict import VerdictResult

PASS = 'PASS'
TENSION = 'TENSION'
FALSIFIED = 'FALSIFIED'
AWAITING = 'AWAITING_DATA'


def _result(exp_id: str, name: str, verdict: str, prediction: str, measured, sigma_deviation, kill_condition: str, pillar_refs: tuple[int, ...], note: str) -> VerdictResult:
    return VerdictResult(
        exp_id=exp_id,
        name=name,
        verdict=verdict,
        prediction=prediction,
        measured=measured,
        sigma_deviation=sigma_deviation,
        kill_condition=kill_condition,
        pillar_refs=pillar_refs,
        note=note,
    )


def _coerce_float(query: dict[str, list[str]], key: str) -> float | None:
    values = query.get(key)
    if not values or values[0] == '':
        return None
    try:
        return float(values[0])
    except ValueError:
        return None


def route_litebird(beta: float | None = None, beta_sigma: float | None = None) -> VerdictResult:
    prediction = f'β ∈ {{≈{BETA_C1}°, ≈{BETA_C2}°}}'
    kill = f'β outside [{BETA_WIN_MIN}°, {BETA_WIN_MAX}°] or inside ({BETA_GAP_LO}°, {BETA_GAP_HI}°) at ≥{BETA_KILL_SIGMA}σ'
    if beta is None:
        return _result('EXP-1', 'LiteBIRD Cosmic Birefringence', AWAITING, prediction, None, None, kill, (11, 13, 765, 771, 787), 'Primary falsifier for the braided-winding mechanism.')

    dist1 = abs(beta - BETA_C1)
    dist2 = abs(beta - BETA_C2)
    dist_nearest = min(dist1, dist2)
    nearest = BETA_C1 if dist1 <= dist2 else BETA_C2
    sigma_deviation = dist_nearest / beta_sigma if beta_sigma and beta_sigma > 0 else None
    outside = beta < BETA_WIN_MIN or beta > BETA_WIN_MAX
    in_gap = BETA_GAP_LO < beta < BETA_GAP_HI
    if (outside or in_gap) and sigma_deviation is not None and sigma_deviation >= BETA_KILL_SIGMA:
        verdict = FALSIFIED
    elif outside or in_gap or (sigma_deviation is not None and sigma_deviation > 1.5):
        verdict = TENSION
    else:
        verdict = PASS
    return _result('EXP-1', 'LiteBIRD Cosmic Birefringence', verdict, prediction, beta, sigma_deviation, kill, (11, 13, 765, 771, 787), f'Nearest canonical branch: {nearest}°; Δ={dist_nearest:.4f}°.')


def route_desi(w_a: float | None = None, w_a_sigma: float | None = None) -> VerdictResult:
    prediction = f'w_a = {WA_PRED}'
    kill = f'w_a ≠ 0 at ≥{WA_KILL_SIGMA}σ'
    if w_a is None:
        return _result('EXP-2', 'DESI Dark Energy', AWAITING, prediction, None, None, kill, (5, 29, 38, 727, 739, 771, 787), 'Awaiting a user-supplied or live DESI constraint.')
    sigma_deviation = abs(w_a - WA_PRED) / w_a_sigma if w_a_sigma and w_a_sigma > 0 else None
    if sigma_deviation is not None and sigma_deviation >= WA_KILL_SIGMA:
        verdict = FALSIFIED
    elif w_a != WA_PRED or (sigma_deviation is not None and sigma_deviation >= 1.5):
        verdict = TENSION
    else:
        verdict = PASS
    return _result('EXP-2', 'DESI Dark Energy', verdict, prediction, w_a, sigma_deviation, kill, (5, 29, 38, 727, 739, 771, 787), 'w_a=0 is the compactification lock condition in the Product 19 routing view.')


def route_juno(dm21: float | None = None, dm21_sigma: float | None = None) -> VerdictResult:
    prediction = f'Δm²₂₁ ∈ [{DM21_WIN_LO:.2e}, {DM21_WIN_HI:.2e}] eV²'
    kill = 'Δm²₂₁ outside the allowed window at ≥2σ'
    if dm21 is None:
        return _result('EXP-3', 'JUNO Neutrino Mass', AWAITING, prediction, None, None, kill, (772, 773, 786, 787), 'Awaiting a JUNO precision measurement.')
    sigma_deviation = abs(dm21 - DM21_PRED) / dm21_sigma if dm21_sigma and dm21_sigma > 0 else None
    outside = dm21 < DM21_WIN_LO or dm21 > DM21_WIN_HI
    if outside and sigma_deviation is not None and sigma_deviation >= 2.0:
        verdict = FALSIFIED
    elif outside or (sigma_deviation is not None and sigma_deviation >= 1.0):
        verdict = TENSION
    else:
        verdict = PASS
    return _result('EXP-3', 'JUNO Neutrino Mass', verdict, prediction, dm21, sigma_deviation, kill, (772, 773, 786, 787), 'Normal-ordering window encoded as the Product 19 survivability band.')


def route_act(n_s: float | None = None, n_s_sigma: float | None = None) -> VerdictResult:
    prediction = f'n_s = {N_S_PRED}'
    kill = f'n_s inconsistent with {N_S_PRED} at ≥{N_S_KILL_SIGMA}σ'
    if n_s is None:
        return _result('EXP-4', 'ACT CMB Spectral Index', AWAITING, prediction, None, None, kill, (11, 67, 787), 'Awaiting an ACT or related spectral-index update.')
    sigma_deviation = abs(n_s - N_S_PRED) / n_s_sigma if n_s_sigma and n_s_sigma > 0 else None
    abs_delta = abs(n_s - N_S_PRED)
    if sigma_deviation is not None and sigma_deviation >= N_S_KILL_SIGMA:
        verdict = FALSIFIED
    elif abs_delta >= 0.001:
        verdict = TENSION
    else:
        verdict = PASS
    return _result('EXP-4', 'ACT CMB Spectral Index', verdict, prediction, n_s, sigma_deviation, kill, (11, 67, 787), 'The Planck-selected winding prediction is represented here by n_s = 0.9635.')


def route_hllhc(mass_tev: float | None = None, observed: bool = False) -> VerdictResult:
    prediction = f'M_G ≳ {MG_KILL_TEV:.1f} TeV survives; detection near {MG_PRED_TEV:.1f} TeV creates tension'
    kill = 'No bright-line kill in Product 19; discovery below the heavy-scale expectation is routed as TENSION'
    if mass_tev is None:
        return _result('EXP-5', 'HL-LHC KK Gluon', AWAITING, prediction, None, None, kill, (709, 787), 'Awaiting an HL-LHC exclusion or discovery mass scale.')
    if observed:
        verdict = TENSION if mass_tev < MG_KILL_TEV else PASS
        note = 'Observed resonance supplied by caller.'
    else:
        verdict = PASS if mass_tev >= MG_KILL_TEV or mass_tev < MG_PRED_TEV else TENSION
        note = 'Mass interpreted as the current exclusion reach with no confirmed detection.'
    return _result('EXP-5', 'HL-LHC KK Gluon', verdict, prediction, {'mass_tev': mass_tev, 'observed': observed}, None, kill, (709, 787), note)


def route_nedm(d_e: float | None = None, d_e_sigma: float | None = None) -> VerdictResult:
    prediction = f'd_n ≈ {NEDM_PRED:.0e} e·cm'
    kill = f'd_n ≥ {NEDM_KILL:.0e} e·cm, or a precision-bound style result at/under 1e-29 e·cm with ≥3σ mismatch'
    if d_e is None:
        return _result('EXP-6', 'nEDM Electric Dipole Moment', AWAITING, prediction, None, None, kill, (731, 786, 787), 'Awaiting a reported EDM measurement or bound.')
    sigma_deviation = abs(d_e - NEDM_PRED) / d_e_sigma if d_e_sigma and d_e_sigma > 0 else None
    precision_kill = d_e <= 1e-29 and sigma_deviation is not None and sigma_deviation >= 3.0
    if d_e >= NEDM_KILL or precision_kill:
        verdict = FALSIFIED
    elif d_e >= 5e-29 or d_e >= NEDM_TENSION or (sigma_deviation is not None and sigma_deviation >= 1.5):
        verdict = TENSION
    else:
        verdict = PASS
    return _result('EXP-6', 'nEDM Electric Dipole Moment', verdict, prediction, d_e, sigma_deviation, kill, (731, 786, 787), 'Residual CP-phase route encoded for Product 19.')


def route_xenon(sigma_cm2: float | None = None) -> VerdictResult:
    prediction = f'σ ≈ {KK_DM_CS:.0e} cm² with kill threshold {XENON_SENS:.0e} cm²'
    kill = f'Detection or limit below {XENON_SENS:.0e} cm²'
    if sigma_cm2 is None:
        return _result('EXP-7', 'XENON-nT Dark Matter', AWAITING, prediction, None, None, kill, (717, 787), 'Awaiting a reported XENON-nT cross-section result.')
    if sigma_cm2 < XENON_SENS:
        verdict = FALSIFIED
    elif sigma_cm2 < KK_DM_CS:
        verdict = TENSION
    else:
        verdict = PASS
    return _result('EXP-7', 'XENON-nT Dark Matter', verdict, prediction, sigma_cm2, None, kill, (717, 787), 'Values below the design sensitivity line are routed as falsifiers in Product 19.')


def route_all(observations: dict) -> list[VerdictResult]:
    observations = observations or {}
    return [
        route_litebird(observations.get('beta'), observations.get('beta_sigma')),
        route_desi(observations.get('w_a'), observations.get('w_a_sigma')),
        route_juno(observations.get('dm21'), observations.get('dm21_sigma')),
        route_act(observations.get('n_s'), observations.get('n_s_sigma')),
        route_hllhc(observations.get('mass_tev'), observations.get('observed', False)),
        route_nedm(observations.get('d_e'), observations.get('d_e_sigma')),
        route_xenon(observations.get('sigma_cm2')),
    ]


def api_litebird(query: dict[str, list[str]] | None = None) -> dict:
    query = query or {}
    beta = _coerce_float(query, 'beta')
    beta_sigma = _coerce_float(query, 'beta_sigma')
    response = {
        'endpoint': '/api/litebird',
        'countdown_days': days_to_litebird(),
        'prediction': dict(BIREFRINGENCE_PREDICTION),
        'observatory_status': get_falsification_status(),
    }
    if beta is not None:
        response['assessment'] = assess_birefringence_measurement(beta)
        response['route'] = asdict(route_litebird(beta, beta_sigma))
    else:
        response['route'] = asdict(route_litebird())
    return response


def api_desi(query: dict[str, list[str]] | None = None) -> dict:
    query = query or {}
    w0 = _coerce_float(query, 'w0')
    wa = _coerce_float(query, 'wa')
    wa_sigma = _coerce_float(query, 'wa_sigma')
    response = {
        'endpoint': '/api/desi',
        'preregistration': dict(DESI_DR3_PREREGISTRATION),
        'observatory_status': get_falsification_status(),
    }
    if wa is not None:
        response['route'] = asdict(route_desi(wa, wa_sigma))
    else:
        response['route'] = asdict(route_desi())
    if w0 is not None and wa is not None:
        response['assessment'] = check_desi_tension(w0, wa)
    return response


API_ENDPOINTS = {
    '/api/desi': api_desi,
    '/api/litebird': api_litebird,
}


def dispatch_api_request(path: str, query: dict[str, list[str]] | None = None) -> dict:
    handler = API_ENDPOINTS.get(path)
    if handler is None:
        raise KeyError(path)
    return handler(query)
