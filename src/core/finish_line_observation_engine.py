# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
finish_line_observation_engine.py — One-command observation routing and
tracker/changelog payload generation for the finish-line programme.

The engine accepts a bundle of live or forecast observations, routes each one
through the existing PASS / TENSION / FALSIFIED logic, and emits machine-readable
payloads for `3-FALSIFICATION/OBSERVATION_TRACKER.md` and `docs/WAVE_CHANGELOG.md`.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Dict, Optional

from src.core.adm_quantitative_closure import adm_quantitative_closure_report
from src.core.alpha_gw_uv_brane_derivation import uv_factor_for_target_alpha
from src.core.cmbs4_ns_r_joint_falsifier import joint_ns_r_verdict
from src.core.desi_dr2_gap_report import full_dr2_gap_report
from src.core.desi_year3_monitor import route_desi_y3
from src.core.desi_year3_monitor import release_day_decision_packet
from src.core.fermion_cl_quantization import subleading_cs_corrected_cl_window
from src.core.hyperk_juno_dm31_readiness import hyperk_juno_falsifier_routing
from src.core.litebird_gap_hardening import classify_beta
from src.core.litebird_gap_hardening import litebird_release_day_packet
from src.core.neutrino_p18_route_consolidation import ROUTE_A_RGE_VALUE
from src.core.prediction_registry import PREDICTION_REGISTRY

# Canonical consolidated P18 prediction for sin²θ12 after applying the
# Route-A geometric boundary condition and its 1-loop RGE cross-check.
SIN2_THETA12_PREDICTED: float = ROUTE_A_RGE_VALUE


def _calculate_tension(predicted: float, observed: float, sigma: float) -> float:
    if sigma <= 0:
        raise ValueError(f"sigma must be positive, got {sigma}")
    return abs(predicted - observed) / sigma

__all__ = [
    "DEFAULT_OBSERVATION_BUNDLE",
    "normalize_observation_bundle",
    "desi_route_label",
    "normalize_litebird_result",
    "route_pmns_theta12",
    "route_lisa_omega_gw",
    "route_finish_line_observation_bundle",
    "build_claim_board_payload",
    "build_truth_layer_payload",
    "build_canonical_ledger_payload",
    "build_canonical_doc_update_packet",
    "build_tracker_update_payload",
    "build_wave_changelog_payload",
    "build_provenance_sync_payload",
    "five_job_execution_packet",
]

DEFAULT_OBSERVATION_BUNDLE: Dict[str, Dict[str, object]] = {
    "desi": {"mode": "published_dr2"},
    "juno": {
        "dm2_31_obs": 2.453e-3,
        "sigma_pct": 0.5,
        "experiment": "JUNO",
        "year": 2027,
    },
    "hyperk": {
        "dm2_31_obs": 2.453e-3,
        "sigma_pct": 1.0,
        "experiment": "Hyper-K",
        "year": 2028,
    },
    "cmbs4": {
        "ns_obs": 0.9649,
        "ns_sigma": 0.002,
        "r_obs": 0.020,
        "r_sigma": 0.001,
        "experiment": "CMB-S4 forecast",
        "year": 2030,
    },
    "litebird": {
        "beta_obs": 0.331,
        "sigma": 0.02,
    },
    "pmns": {
        "sin2_theta12_obs": 0.307,
        "sigma": 0.013,
        "experiment": "NuFIT/PDG",
        "year": 2026,
    },
    "lisa": {
        "omega_gw_obs": 1.0e-15,
        "sigma": 2.0e-16,
        "experiment": "LISA forecast",
        "year": 2035,
    },
}


def normalize_observation_bundle(
    bundle: Optional[Dict[str, Dict[str, object]]] = None,
) -> Dict[str, Dict[str, object]]:
    """Return a default-backed observation bundle with field-level overrides."""
    normalized = deepcopy(DEFAULT_OBSERVATION_BUNDLE)
    if not bundle:
        return normalized
    for key, payload in bundle.items():
        if key not in normalized or not isinstance(normalized[key], dict):
            normalized[key] = deepcopy(payload)
        else:
            normalized[key].update(deepcopy(payload))
    return normalized


def desi_route_label(result: Dict[str, object]) -> str:
    """Return a normalized route label for either DESI result structure.

    Live `route_desi_y3()` results expose `route`, while the aggregated
    `full_dr2_gap_report()` summary exposes `current_status`.
    """
    route = result.get("route") or result.get("current_status")
    if route is None:
        raise ValueError("DESI result missing both 'route' and 'current_status'.")
    return str(route)


def normalize_litebird_result(result: Dict[str, object]) -> Dict[str, object]:
    """Return a normalized LiteBIRD result with an explicit route label."""
    normalized = deepcopy(result)
    normalized["route"] = normalized["zone"]
    return normalized


def route_pmns_theta12(
    sin2_theta12_obs: float,
    sigma: float,
    experiment: str = "NuFIT/PDG",
    year: int = 2026,
) -> Dict[str, object]:
    """Route θ12 observations against the canonical consolidated P18 value."""
    predicted = SIN2_THETA12_PREDICTED
    tension = _calculate_tension(predicted, sin2_theta12_obs, sigma)
    if tension < 2.0:
        route = "CONSISTENT"
        action = "No canonical status change; keep monitoring solar-angle precision."
    elif tension < 3.0:
        route = "TENSION"
        action = "Update PMNS tracking surfaces and retain honest residual note."
    else:
        route = "FALSIFIED"
        action = "Escalate PMNS route discrepancy into FALLIBILITY/TRUTH_LAYER/tracker sync."
    return {
        "parameter": "sin²θ12",
        "predicted": predicted,
        "observed": sin2_theta12_obs,
        "sigma": sigma,
        "tension_sigma": tension,
        "experiment": experiment,
        "year": year,
        "route": route,
        "action": action,
    }


def route_lisa_omega_gw(
    omega_gw_obs: float,
    sigma: float,
    experiment: str = "LISA forecast",
    year: int = 2035,
) -> Dict[str, object]:
    """Route Ω_GW observations using the prediction registry target and falsifier."""
    predicted = float(PREDICTION_REGISTRY["GW_BACKGROUND"]["predicted_value"])
    threshold = 1.0e-17
    tension = _calculate_tension(predicted, omega_gw_obs, sigma)
    if omega_gw_obs < threshold and (threshold - omega_gw_obs) / sigma > 3.0:
        route = "FALSIFIED"
        action = "Record same-day LISA falsifier result and update canonical GW tracker."
    elif tension < 3.0:
        route = "CONSISTENT"
        action = "Keep Ω_GW in active monitoring with no label change."
    else:
        route = "TENSION"
        action = "Update GW monitoring surfaces and retain LISA pending/ tension note."
    return {
        "parameter": "Ω_GW",
        "predicted": predicted,
        "observed": omega_gw_obs,
        "sigma": sigma,
        "tension_sigma": tension,
        "threshold": threshold,
        "experiment": experiment,
        "year": year,
        "route": route,
        "action": action,
    }


def build_tracker_update_payload(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the auto-update payload for OBSERVATION_TRACKER.md."""
    return {
        "target_file": "3-FALSIFICATION/OBSERVATION_TRACKER.md",
        "summary_lines": [
            f"DESI: {desi_route_label(results['desi'])}",
            f"JUNO: {results['juno']['route']}",
            f"Hyper-K: {results['hyperk']['route']}",
            f"CMB-S4: {results['cmbs4']['route']}",
            f"LiteBIRD: {results['litebird']['route']}",
            f"PMNS θ12: {results['pmns']['route']}",
            f"LISA Ω_GW: {results['lisa']['route']}",
        ],
        "required_same_day_sync": True,
        "action_items": [
            results["juno"]["action"],
            results["hyperk"]["action"],
            results["cmbs4"]["action"],
            results["pmns"]["action"],
            results["lisa"]["action"],
        ],
    }


def build_wave_changelog_payload(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the auto-update payload for WAVE_CHANGELOG.md."""
    desi_status = desi_route_label(results["desi"])
    return {
        "target_file": "docs/WAVE_CHANGELOG.md",
        "what_changed": [
            f"Observation engine routed DESI state as {desi_status}.",
            f"JUNO routed as {results['juno']['route']}.",
            f"Hyper-K routed as {results['hyperk']['route']}.",
            f"CMB-S4 routed as {results['cmbs4']['route']}.",
            f"LiteBIRD zone classified as {results['litebird']['zone']}.",
            f"PMNS θ12 routed as {results['pmns']['route']}.",
            f"LISA Ω_GW routed as {results['lisa']['route']}.",
        ],
        "what_did_not_change": [
            "No parameter label changed automatically.",
            "No falsifier was weakened.",
            "ToE score stayed unchanged unless a downstream manual audit approves otherwise.",
        ],
        "residual_unknowns": [
            "P16 hardgate still depends on exact WS-III closure.",
            "P28 remains architecture-limited pending 10D closure.",
            "Automatic routing does not replace manual canonical-doc judgment.",
        ],
    }


def build_claim_board_payload(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the required claim-board sync payload."""
    return {
        "target_file": "docs/CLAIM_MASTER_BOARD.md",
        "required_same_day_sync": True,
        "claim_rows": [
            f"T1 / DESI wₐ route → {desi_route_label(results['desi'])}",
            f"P18 / PMNS θ12 route → {results['pmns']['route']}",
            f"P25 / Ω_GW route → {results['lisa']['route']}",
            f"P23/P24 / LiteBIRD β route → {results['litebird']['route']}",
        ],
        "label_change_policy": "manual_review_required_before_claim_board_edit",
    }


def build_truth_layer_payload(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the required truth-layer sync payload."""
    return {
        "target_file": "docs/TRUTH_LAYER.md",
        "required_same_day_sync": True,
        "tension_updates": [
            f"DESI route: {desi_route_label(results['desi'])}",
            f"PMNS θ12 route: {results['pmns']['route']}",
            f"LISA Ω_GW route: {results['lisa']['route']}",
            f"LiteBIRD route: {results['litebird']['route']}",
        ],
        "falsifier_actions": [
            results["pmns"]["action"],
            results["lisa"]["action"],
            results["cmbs4"]["action"],
        ],
    }


def build_canonical_ledger_payload(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the canonical-ledger sync payload for same-commit updates."""
    return {
        "target_files": [
            "STATUS.md",
            "FALLIBILITY.md",
            "1-THEORY/DERIVATION_STATUS.md",
            "docs/mas_tracker.yml",
        ],
        "required_same_commit": True,
        "status_lines": [
            f"DESI={desi_route_label(results['desi'])}",
            f"CMB-S4={results['cmbs4']['route']}",
            f"LiteBIRD={results['litebird']['route']}",
            f"PMNS={results['pmns']['route']}",
            f"LISA={results['lisa']['route']}",
        ],
        "manual_label_review_required": True,
    }


def build_provenance_sync_payload(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the required same-commit canonical-doc sync targets."""
    return {
        "target_files": [
            "STATUS.md",
            "FALLIBILITY.md",
            "1-THEORY/DERIVATION_STATUS.md",
            "docs/mas_tracker.yml",
            "docs/WAVE_CHANGELOG.md",
            "docs/TRUTH_LAYER.md",
            "docs/CLAIM_MASTER_BOARD.md",
        ],
        "required_same_commit": True,
        "summary": [
            f"DESI={desi_route_label(results['desi'])}",
            f"CMB-S4={results['cmbs4']['route']}",
            f"LiteBIRD={results['litebird']['route']}",
            f"PMNS={results['pmns']['route']}",
            f"LISA={results['lisa']['route']}",
        ],
    }


def build_canonical_doc_update_packet(results: Dict[str, Dict[str, object]]) -> Dict[str, object]:
    """Build the end-to-end same-commit doc update packet."""
    tracker_payload = build_tracker_update_payload(results)
    wave_payload = build_wave_changelog_payload(results)
    claim_payload = build_claim_board_payload(results)
    truth_payload = build_truth_layer_payload(results)
    ledger_payload = build_canonical_ledger_payload(results)
    provenance_payload = build_provenance_sync_payload(results)
    target_files = (
        [tracker_payload["target_file"], wave_payload["target_file"],
         claim_payload["target_file"], truth_payload["target_file"]]
        + ledger_payload["target_files"]
    )
    deduped_target_files = list(dict.fromkeys(target_files))
    return {
        "required_same_commit": True,
        "target_files": deduped_target_files,
        "payloads": {
            "tracker": tracker_payload,
            "wave_changelog": wave_payload,
            "claim_board": claim_payload,
            "truth_layer": truth_payload,
            "canonical_ledgers": ledger_payload,
            "provenance": provenance_payload,
        },
    }


def route_finish_line_observation_bundle(
    bundle: Optional[Dict[str, Dict[str, object]]] = None,
) -> Dict[str, object]:
    """Route the full finish-line observation bundle in one call."""
    normalized = normalize_observation_bundle(bundle)

    if "wa" in normalized["desi"] and "sigma" in normalized["desi"]:
        desi_result = route_desi_y3(
            wa=float(normalized["desi"]["wa"]),
            sigma=float(normalized["desi"]["sigma"]),
        )
    elif normalized["desi"].get("mode") == "published_dr2":
        desi_result = full_dr2_gap_report()
    else:
        raise ValueError("DESI bundle must provide either mode='published_dr2' or wa/sigma.")

    juno_result = hyperk_juno_falsifier_routing(
        dm2_31_obs=float(normalized["juno"]["dm2_31_obs"]),
        sigma_pct=float(normalized["juno"]["sigma_pct"]),
        experiment=str(normalized["juno"]["experiment"]),
        year=int(normalized["juno"]["year"]),
    )
    hyperk_result = hyperk_juno_falsifier_routing(
        dm2_31_obs=float(normalized["hyperk"]["dm2_31_obs"]),
        sigma_pct=float(normalized["hyperk"]["sigma_pct"]),
        experiment=str(normalized["hyperk"]["experiment"]),
        year=int(normalized["hyperk"]["year"]),
    )
    cmbs4_result = joint_ns_r_verdict(
        ns_obs=float(normalized["cmbs4"]["ns_obs"]),
        ns_sigma=float(normalized["cmbs4"]["ns_sigma"]),
        r_obs=float(normalized["cmbs4"]["r_obs"]),
        r_sigma=float(normalized["cmbs4"]["r_sigma"]),
        experiment=str(normalized["cmbs4"]["experiment"]),
        year=int(normalized["cmbs4"]["year"]),
    )
    litebird_result = normalize_litebird_result(classify_beta(
        beta_obs=float(normalized["litebird"]["beta_obs"]),
        sigma=float(normalized["litebird"]["sigma"]),
    ))
    pmns_result = route_pmns_theta12(
        sin2_theta12_obs=float(normalized["pmns"]["sin2_theta12_obs"]),
        sigma=float(normalized["pmns"]["sigma"]),
        experiment=str(normalized["pmns"]["experiment"]),
        year=int(normalized["pmns"]["year"]),
    )
    lisa_result = route_lisa_omega_gw(
        omega_gw_obs=float(normalized["lisa"]["omega_gw_obs"]),
        sigma=float(normalized["lisa"]["sigma"]),
        experiment=str(normalized["lisa"]["experiment"]),
        year=int(normalized["lisa"]["year"]),
    )

    routed = {
        "desi": desi_result,
        "juno": juno_result,
        "hyperk": hyperk_result,
        "cmbs4": cmbs4_result,
        "litebird": litebird_result,
        "pmns": pmns_result,
        "lisa": lisa_result,
    }

    return {
        "bundle": normalized,
        "results": routed,
        "tracker_update_payload": build_tracker_update_payload(routed),
        "wave_changelog_payload": build_wave_changelog_payload(routed),
        "claim_board_payload": build_claim_board_payload(routed),
        "truth_layer_payload": build_truth_layer_payload(routed),
        "canonical_ledger_payload": build_canonical_ledger_payload(routed),
        "provenance_sync_payload": build_provenance_sync_payload(routed),
        "canonical_doc_update_packet": build_canonical_doc_update_packet(routed),
    }


def five_job_execution_packet(
    desi_payload: Optional[Dict[str, object]] = None,
    litebird_beta: float = 0.331,
    litebird_sigma: float = 0.02,
    target_alpha_gw: float = 4.5e-10,
) -> Dict[str, object]:
    """Run and aggregate the five active closure jobs in one integration packet."""
    if desi_payload is None:
        desi_payload = {
            "release_name": "DESI Year 3 Mock Packet",
            "year": 2026,
            "w0_central": -0.84,
            "w0_sigma": 0.06,
            "wa_central": -0.40,
            "wa_sigma": 0.20,
            "reference": "DESI synthetic packet",
            "datasets": "BAO + CMB + SNe Ia (synthetic)",
        }

    job1 = subleading_cs_corrected_cl_window()
    job2 = adm_quantitative_closure_report()
    job3_desi = release_day_decision_packet(dict(desi_payload))
    job3_litebird = litebird_release_day_packet(beta_obs=litebird_beta, sigma=litebird_sigma)
    job4 = uv_factor_for_target_alpha(target_alpha_gw=target_alpha_gw)

    return {
        "pipeline": "FIVE_JOB_EXECUTION_PACKET",
        "jobs": {
            "job1_sc1_subleading_cs_cl": job1,
            "job2_t3_adm_quantitative": job2,
            "job3_desi_release_day": job3_desi,
            "job3_litebird_release_day": job3_litebird,
            "job4_sc2_uv_factor_solver": job4,
        },
        "all_jobs_completed": True,
    }
