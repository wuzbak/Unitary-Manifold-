# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Serialization and aggregation helpers for UM overlay results."""

from __future__ import annotations

from typing import Any

from .physics import GeoEvent, UMGeoOverlay, UMOverlayResult



def _event_to_dict(event: GeoEvent) -> dict[str, Any]:
    return {
        "kind": event.kind,
        "magnitude": event.magnitude,
        "lat": event.lat,
        "lon": event.lon,
        "depth_km": event.depth_km,
        "area_ha": event.area_ha,
        "energy_J": event.energy_J,
        "energy_si": event.energy_si,
        "energy_planck": event.energy_planck,
    }



def format_result_json(result: UMOverlayResult) -> dict[str, Any]:
    """Serialize a UMOverlayResult into a JSON-safe dictionary."""
    event_payload = _event_to_dict(result.event)
    return {
        **event_payload,
        "event": event_payload,
        "phi_debt_injection": result.phi_debt_injection,
        "phi_alignment": result.phi_alignment,
        "radion_amplitude": result.radion_amplitude,
        "radion_suppression_factor": result.radion_suppression_factor,
        "winding_stability": result.winding_stability,
        "basin_perturbation": result.basin_perturbation,
        "w_a_local": result.w_a_local,
        "epistemic_label": result.epistemic_label,
        "confidence": result.confidence,
        "pillar_sources": list(result.pillar_sources),
        "summary": result.summary,
    }



def compute_overlay(events: list[GeoEvent]) -> list[dict[str, Any]]:
    """Run UMGeoOverlay analysis for each event and return serialized dictionaries."""
    overlay = UMGeoOverlay()
    return [format_result_json(overlay.analyse(event)) for event in events]



def summary_stats(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute lightweight aggregate statistics for serialized overlay results."""
    if not results:
        return {
            "total": 0,
            "by_kind": {},
            "avg_phi_debt": 0.0,
            "avg_winding_stability": 0.0,
            "high_severity_count": 0,
        }

    by_kind: dict[str, int] = {}
    total_phi = 0.0
    total_stability = 0.0
    high_severity_count = 0

    for result in results:
        kind = str(result.get("kind", "unknown"))
        by_kind[kind] = by_kind.get(kind, 0) + 1
        total_phi += float(result.get("phi_debt_injection", 0.0))
        stability = float(result.get("winding_stability", 0.0))
        total_stability += stability
        if result.get("confidence") == "HIGH" or stability < 0.25:
            high_severity_count += 1

    count = len(results)
    return {
        "total": count,
        "by_kind": by_kind,
        "avg_phi_debt": total_phi / count,
        "avg_winding_stability": total_stability / count,
        "high_severity_count": high_severity_count,
    }
