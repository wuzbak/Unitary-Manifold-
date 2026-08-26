# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/pillar_geo_monitor.py
==============================
UM Geophysical Monitor — Adjacent Track 🔵

Maps real-world natural-disaster events (earthquakes, wildfires, severe
weather, tsunamis) to Unitary Manifold observable predictions drawn from:

  • Pillar 806  — back-reacted radion / QCD IR scale (BACKREACTED_RADION_QCD_IR_SUPPRESSION_DERIVED)
  • Pillar 786  — winding-basin stability (WINDING_BASIN_CLOSED)
  • Pillar 16   — φ-debt entropy accounting (recycling/entropy_ledger.py)
  • Pillar 22   — atmospheric climate module
  • Pillar 3    — gravitational / seismic energy coupling

This module is NOT a hardgate physics claim.  It is an honest quantitative
exploration connecting UM geometry to applied geophysics.  Every output
carries an explicit epistemic label.

Usage
-----
>>> from src.core.pillar_geo_monitor import GeoEvent, UMGeoOverlay
>>> ev = GeoEvent(kind="earthquake", magnitude=7.4, lat=35.7, lon=140.1,
...               depth_km=30.0, energy_J=None)
>>> overlay = UMGeoOverlay()
>>> result = overlay.analyse(ev)
>>> result.phi_debt_injection   # φ-debt entropy injected (natural units)
>>> result.radion_amplitude     # predicted radion Δφ amplitude
>>> result.winding_stability    # winding-basin stability score [0,1]
>>> result.epistemic_label      # always present
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

# ---------------------------------------------------------------------------
# Core UM constants (natural / Planck units unless noted)
# ---------------------------------------------------------------------------
WINDING_NUMBER: int = 5          # n_w; Planck nₛ-selected
K_CS: int = 74                   # = 5² + 7² (birefringence-selected)
BRAIDED_SOUND_SPEED: float = 12 / 37   # c_s from (5,7) braid resonance
PHI_0: float = 1.0               # normalised φ₀ (dimensionless)

# Pillar 806 — radion back-reaction coupling
RADION_DELTA_PHI_PER_M5: float = -32.0          # Δφ/M_5 at QCD IR floor
RADION_QCD_SUPPRESSION: float = 1e7              # IR suppression factor
RADION_COUPLING_ALPHA: float = abs(RADION_DELTA_PHI_PER_M5) / K_CS  # ≈ 0.432

# Pillar 786 — winding basin stability
BASIN_DEPTH: float = WINDING_NUMBER ** 2 / K_CS          # 25/74 ≈ 0.3378
BASIN_WIDTH_RAD: float = 2 * math.pi / WINDING_NUMBER    # 2π/5

# Pillar 16 — φ-debt entropy (recycling / geophysical analogue)
PHI_DEBT_DECAY_RATE: float = 0.15   # per characteristic time
PHI_DEBT_ALIGNMENT_FLOOR: float = 0.30

# Geophysical energy conversions (SI)
JOULES_PER_RICHTER_UNIT: float = 10 ** (1.5)   # Gutenberg-Richter exponent base
RICHTER_REF_ENERGY_J: float = 10 ** 4.8         # 1 μJ reference (Richter 0)
WILDFIRE_ENERGY_PER_HA_J: float = 8.0e10        # ~80 GJ/ha (typical fuel load)
HURRICANE_ENERGY_PER_CATEGORY_J: float = 5.0e18  # Saffir-Simpson scale step

# Planck energy (for normalisation to natural units)
PLANCK_ENERGY_J: float = 1.9561e9               # 1 Planck energy in Joules


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

DISASTER_KINDS = frozenset(
    ["earthquake", "wildfire", "hurricane", "tornado", "flood",
     "tsunami", "volcano", "drought", "landslide", "storm"]
)


@dataclass
class GeoEvent:
    """A natural-disaster event with physical parameters."""

    kind: str               # one of DISASTER_KINDS
    magnitude: float        # Richter / Saffir-Simpson / fire radiative power
    lat: float              # degrees
    lon: float              # degrees

    # Optional refinements
    depth_km: Optional[float] = None   # earthquake focal depth
    area_ha: Optional[float] = None    # wildfire area (hectares)
    energy_J: Optional[float] = None   # override: known SI energy

    def validate(self) -> None:
        kind_norm = self.kind.lower()
        if kind_norm not in DISASTER_KINDS:
            raise ValueError(
                f"Unknown disaster kind '{self.kind}'. "
                f"Valid: {sorted(DISASTER_KINDS)}"
            )
        if not (-90 <= self.lat <= 90):
            raise ValueError(f"lat must be in [-90,90], got {self.lat}")
        if not (-180 <= self.lon <= 180):
            raise ValueError(f"lon must be in [-180,180], got {self.lon}")

    @property
    def energy_planck(self) -> float:
        """Event energy in Planck units (dimensionless)."""
        return self.energy_si / PLANCK_ENERGY_J

    @property
    def energy_si(self) -> float:
        """Event energy in Joules (estimated if not provided)."""
        if self.energy_J is not None:
            return self.energy_J
        kind = self.kind.lower()
        if kind == "earthquake":
            # Gutenberg-Richter: log₁₀(E) = 1.5·M + 4.8
            return 10 ** (1.5 * self.magnitude + 4.8)
        if kind == "wildfire":
            area = self.area_ha if self.area_ha else 10 ** (self.magnitude - 1)
            return area * WILDFIRE_ENERGY_PER_HA_J
        if kind in ("hurricane", "tornado", "storm"):
            return HURRICANE_ENERGY_PER_CATEGORY_J * (self.magnitude ** 2)
        if kind == "tsunami":
            # Approximate from triggering earthquake magnitude
            return 10 ** (1.5 * self.magnitude + 4.8)
        if kind == "volcano":
            # VEI-based: log₁₀(E) ≈ 3·VEI + 10
            return 10 ** (3 * self.magnitude + 10)
        # Default: generic energy scaling
        return 10 ** (1.5 * self.magnitude + 4.8)


@dataclass
class UMOverlayResult:
    """UM physics overlay for one geophysical event."""

    event: GeoEvent

    # φ-debt entropy injection (Pillar 16 analogue)
    phi_debt_injection: float = 0.0    # dimensionless, natural units
    phi_alignment: float = 1.0         # [0,1]; 1 = pristine, 0 = fully disrupted

    # Radion perturbation (Pillar 806)
    radion_amplitude: float = 0.0      # |Δφ/φ₀| induced by event
    radion_suppression_factor: float = 1.0  # local QCD IR suppression

    # Winding-basin stability (Pillar 786)
    winding_stability: float = 1.0     # [0,1]; 1 = fully stable basin
    basin_perturbation: float = 0.0    # fractional basin-depth perturbation

    # CPL dark-energy coupling (Pillar 808 analogue)
    w_a_local: float = 0.0             # local effective w_a deviation

    # Metadata
    epistemic_label: str = "🔵 ADJACENT TRACK — not a hardgate physics claim"
    confidence: str = "LOW"            # LOW / MEDIUM / HIGH
    pillar_sources: list = field(default_factory=list)
    summary: str = ""


# ---------------------------------------------------------------------------
# Core overlay engine
# ---------------------------------------------------------------------------

class UMGeoOverlay:
    """
    Compute UM physics overlay quantities for a geophysical event.

    All calculations are geometric analogues from the UM framework applied
    to macroscopic geophysical energy scales.  They are exploratory (🔵
    ADJACENT TRACK) and must not be cited as hardgate predictions.
    """

    def analyse(self, event: GeoEvent) -> UMOverlayResult:
        event.validate()
        result = UMOverlayResult(event=event)

        E_planck = event.energy_planck
        E_log = math.log10(max(event.energy_si, 1.0))

        # ---- Pillar 16 — φ-debt entropy injection --------------------------
        # Analogue: geophysical energy injection ↔ φ-debt created in the
        # local manifold patch.  Uses the recycling/entropy_ledger model:
        # S_geo ≈ E_planck · (1 − exp(−decay_rate · ln10(E_SI)))
        decay_arg = PHI_DEBT_DECAY_RATE * E_log
        phi_debt = E_planck * (1.0 - math.exp(-decay_arg))
        phi_alignment = math.exp(-PHI_DEBT_DECAY_RATE * E_planck)
        phi_alignment = max(PHI_DEBT_ALIGNMENT_FLOOR, min(1.0, phi_alignment))

        result.phi_debt_injection = phi_debt
        result.phi_alignment = phi_alignment

        # ---- Pillar 806 — radion back-reaction amplitude -------------------
        # Δφ/φ₀ ∝ RADION_COUPLING_ALPHA · log10(E_SI / E_Planck)
        # Suppression factor: exp(RADION_COUPLING_ALPHA · |Δφ/φ₀|)
        radion_amp = RADION_COUPLING_ALPHA * abs(
            math.log10(max(event.energy_si, 1.0) / PLANCK_ENERGY_J)
        )
        # Depth correction for earthquakes (deeper → smaller surface Δφ)
        if event.kind.lower() == "earthquake" and event.depth_km:
            depth_factor = math.exp(-event.depth_km / 700.0)
            radion_amp *= depth_factor

        suppression = math.exp(RADION_COUPLING_ALPHA * radion_amp)
        result.radion_amplitude = radion_amp
        result.radion_suppression_factor = min(suppression, RADION_QCD_SUPPRESSION)

        # ---- Pillar 786 — winding-basin stability --------------------------
        # Perturbation = radion_amp / BASIN_DEPTH; stability = 1 − clamp(pert,0,1)
        basin_pert = radion_amp / BASIN_DEPTH
        winding_stability = max(0.0, 1.0 - min(basin_pert, 1.0))
        result.basin_perturbation = basin_pert
        result.winding_stability = winding_stability

        # ---- Pillar 808 — local w_a deviation (CPL breathing-mode) --------
        # w_a_local ∝ −radion_amp · BRAIDED_SOUND_SPEED²
        result.w_a_local = -radion_amp * (BRAIDED_SOUND_SPEED ** 2)

        # ---- Confidence and summary ----------------------------------------
        if E_planck < 1e-18:
            confidence = "LOW"
        elif E_planck < 1e-15:
            confidence = "MEDIUM"
        else:
            confidence = "HIGH"
        result.confidence = confidence

        result.pillar_sources = ["P806", "P786", "P16", "P808", "P22"]
        result.summary = (
            f"{event.kind.upper()} M{event.magnitude} at "
            f"({event.lat:.2f}°, {event.lon:.2f}°) | "
            f"φ-debt={phi_debt:.3e} | radion|Δφ/φ₀|={radion_amp:.4f} | "
            f"basin stability={winding_stability:.3f} | "
            f"confidence={confidence}"
        )
        return result


# ---------------------------------------------------------------------------
# Batch helper
# ---------------------------------------------------------------------------

def analyse_event_batch(events: list[GeoEvent]) -> list[UMOverlayResult]:
    """Run UMGeoOverlay on a list of GeoEvents and return results."""
    overlay = UMGeoOverlay()
    return [overlay.analyse(ev) for ev in events]


# ---------------------------------------------------------------------------
# API feed parsers (for server-side use or CLI verification)
# ---------------------------------------------------------------------------

def parse_usgs_feature(feature: dict) -> Optional[GeoEvent]:
    """Parse one GeoJSON feature from the USGS Earthquake Hazards Feed."""
    try:
        props = feature.get("properties", {})
        geom = feature.get("geometry", {})
        coords = geom.get("coordinates", [None, None, None])
        mag = props.get("mag")
        if mag is None:
            return None
        lon, lat = float(coords[0]), float(coords[1])
        depth = float(coords[2]) if coords[2] is not None else None
        return GeoEvent(
            kind="earthquake",
            magnitude=float(mag),
            lat=lat,
            lon=lon,
            depth_km=depth,
        )
    except (KeyError, TypeError, ValueError, IndexError):
        return None


def parse_eonet_event(event: dict) -> Optional[GeoEvent]:
    """Parse one event from NASA EONET v3 JSON feed."""
    try:
        categories = event.get("categories", [])
        category_ids = {c.get("id", "").lower() for c in categories}

        # Map EONET category → GeoEvent kind
        kind_map = {
            "wildfires": "wildfire",
            "severeStorms": "storm",
            "volcanoes": "volcano",
            "seaLakeIce": "flood",
            "floods": "flood",
            "earthquakes": "earthquake",
            "landslides": "landslide",
            "drought": "drought",
            "dustHaze": "storm",
            "manOfTheMatch": "storm",  # fallback
        }
        kind = "storm"
        for cid in category_ids:
            if cid in kind_map:
                kind = kind_map[cid]
                break

        geometry = event.get("geometry", [])
        if not geometry:
            return None
        coords = geometry[-1].get("coordinates", [None, None])
        if not coords or coords[0] is None:
            return None
        lon, lat = float(coords[0]), float(coords[1])

        # Magnitude proxy: use a nominal 5.0 for events without explicit mag
        mag = float(event.get("magnitudeValue") or 5.0)
        return GeoEvent(kind=kind, magnitude=mag, lat=lat, lon=lon)
    except (KeyError, TypeError, ValueError, IndexError):
        return None


# ---------------------------------------------------------------------------
# Standalone self-check
# ---------------------------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    overlay = UMGeoOverlay()
    test_events = [
        GeoEvent("earthquake", 7.4, 35.7, 140.1, depth_km=30.0),
        GeoEvent("wildfire", 6.0, 34.0, -118.0, area_ha=5000),
        GeoEvent("hurricane", 4.0, 25.0, -90.0),
        GeoEvent("volcano", 3.0, -8.3, 115.2),
    ]
    for ev in test_events:
        r = overlay.analyse(ev)
        print(r.summary)
        print(f"  {r.epistemic_label}")
        print()
