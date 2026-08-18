"""
FilmersCompanion — Cinematography Advisor Agent
"""
from __future__ import annotations

import math
from .base import BaseAgent


class CinematographyAdvisor(BaseAgent):
    """AI-powered cinematography advisor for coverage, lighting, and shot planning."""

    def suggest_coverage(self, synopsis: str, scene_type: str = "drama") -> list[dict]:
        """Return a list of shot suggestions for a scene."""
        scene_lower = (synopsis + " " + scene_type).lower()

        suggestions = [
            {
                "shot_number": 1,
                "coverage_type": "master",
                "description": "Wide establishing master shot covering the full scene.",
                "lens": "24-35mm",
                "movement": "static or slow push",
            },
            {
                "shot_number": 2,
                "coverage_type": "MS",
                "description": "Medium shot coverage of primary character(s).",
                "lens": "50mm",
                "movement": "static",
            },
            {
                "shot_number": 3,
                "coverage_type": "OTS",
                "description": "Over-the-shoulder shot for dialogue scenes.",
                "lens": "85mm",
                "movement": "static",
            },
            {
                "shot_number": 4,
                "coverage_type": "CU",
                "description": "Close-up on face/reaction.",
                "lens": "85mm",
                "movement": "static",
            },
        ]

        if any(w in scene_lower for w in ["action", "chase", "fight", "run"]):
            suggestions.append({
                "shot_number": 5,
                "coverage_type": "insert",
                "description": "Insert: hands, weapon, prop detail.",
                "lens": "100mm macro",
                "movement": "static",
            })
            suggestions.append({
                "shot_number": 6,
                "coverage_type": "cutaway",
                "description": "Cutaway: environment reaction or obstacle.",
                "lens": "35mm",
                "movement": "handheld",
            })

        if any(w in scene_lower for w in ["exterior", "ext", "outdoor"]):
            suggestions.append({
                "shot_number": len(suggestions) + 1,
                "coverage_type": "aerial",
                "description": "Aerial/drone establishing shot (if permitted).",
                "lens": "drone wide",
                "movement": "aerial",
            })

        return suggestions

    def calc_lighting(
        self,
        distance_ft: float = 10.0,
        fixture_power_w: float = 1000.0,
        subject_distance_ft: float | None = None,
    ) -> dict:
        """
        Calculate lighting at subject using inverse square law.
        Returns EV at distance, f-stop recommendation, and color temp.
        Accepts distance_ft or subject_distance_ft (alias).
        """
        d = subject_distance_ft if subject_distance_ft is not None else distance_ft
        # Luminous flux approximation: 1W ≈ 15 lumens (LED fixture)
        lumens = fixture_power_w * 15.0
        # Illuminance (lux) = lumens / (4π × d²)  — d in meters
        distance_m = d * 0.3048
        if distance_m <= 0:
            distance_m = 0.01
        lux = lumens / (4 * math.pi * distance_m ** 2)

        # EV = log2(lux / 2.5)  (calibrated lux-to-EV for ISO 100, incident)
        ev = math.log2(max(lux, 0.001) / 2.5)

        # f-stop recommendation from EV (ISO 100, 1/48s shutter)
        shutter = 1.0 / 48.0
        n_sq = (2 ** ev) * shutter
        f_stop = math.sqrt(max(n_sq, 0.0001))
        f_stop = max(0.7, min(f_stop, 22.0))

        # Color temp: LED fixtures default to 5600K (daylight)
        color_temp_k = 5600

        return {
            "lux": round(lux, 2),
            "lux_at_distance": round(lux, 2),
            "ev": round(ev, 2),
            "ev_at_distance": round(ev, 2),
            "f_stop": round(f_stop, 2),
            "f_stop_recommendation": round(f_stop, 2),
            "color_temp_k": color_temp_k,
            "distance_ft": d,
            "fixture_power_w": fixture_power_w,
        }

    def validate_shot_list(self, shots: list[dict]) -> dict:
        """
        Validate a shot list for editorial completeness.
        Valid if master shot is present.  Returns {valid, issues, warnings}.
        """
        warnings = []
        issues = []

        if not shots:
            issues.append("missing master")
            return {"valid": False, "issues": issues, "warnings": ["Shot list is empty."]}

        coverage_types = [s.get("coverage_type", "").lower() for s in shots]

        has_master = "master" in coverage_types
        if not has_master:
            issues.append("missing master")
            warnings.append("Missing master shot — editorial risk.")

        has_cu = any(ct in ("cu", "bcu", "close-up", "close up") for ct in coverage_types)
        if not has_cu:
            warnings.append("No close-up (CU) shots — limited reaction coverage.")

        has_ms = any(ct in ("ms", "medium shot", "medium", "ots", "over the shoulder") for ct in coverage_types)
        if not has_ms:
            warnings.append("No medium shot (MS/OTS) coverage — may struggle in edit.")

        # Valid iff master is present; other gaps are advisories only
        return {"valid": has_master, "issues": issues, "warnings": warnings}
