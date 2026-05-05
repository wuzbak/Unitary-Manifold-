# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
src/core/falsification_calendar.py
=====================================
Pillar 180 — Comparative Falsification Calendar.

Provides a structured, honest comparison of the near-term falsification
windows for five theories: UM, Wolfram Physics, Geometric Unity (GU),
E8-based models, and CDT (Causal Dynamical Triangulations).

Only UM and CDT have near-term falsification windows before 2035.
UM is the only theory with a CMB polarization test (LiteBIRD, 2032).

STATUS: STRATEGIC_ASSET

Theory, scientific direction, and framework: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""

LITEBIRD_LAUNCH = 2032
FCC_EE_LAUNCH = 2041
LISA_LAUNCH = 2034
CMB_S4_LAUNCH = 2028
SKA_LAUNCH = 2028


def um_falsification_profile():
    return {
        "theory": "Unitary Manifold (UM)",
        "key_prediction": "CMB birefringence β ∈ {0.273°, 0.331°}; admissible window [0.22°, 0.38°]",
        "experiment": "LiteBIRD",
        "launch_year": LITEBIRD_LAUNCH,
        "falsification_year_estimate": 2033,
        "has_near_term_falsifier": True,
        "notes": "Primary falsifier; any β outside [0.22°, 0.38°] or in gap [0.29°-0.31°] falsifies UM",
    }


def wolfram_falsification_profile():
    return {
        "theory": "Wolfram Physics",
        "key_prediction": "No specific near-term quantitative experimental prediction published",
        "experiment": "Unknown",
        "launch_year": None,
        "falsification_year_estimate": 9999,
        "has_near_term_falsifier": False,
        "notes": (
            "Wolfram project lacks a specific quantitative prediction testable by "
            "known experiments in the next decade; causal graph convergence has not "
            "been demonstrated to match Standard Model predictions."
        ),
    }


def gu_falsification_profile():
    return {
        "theory": "Geometric Unity (GU)",
        "key_prediction": "No specific near-term quantitative experimental prediction published",
        "experiment": "Unknown",
        "launch_year": None,
        "falsification_year_estimate": 9999,
        "has_near_term_falsifier": False,
        "notes": (
            "Geometric Unity has not yet produced a specific quantitative experimental "
            "prediction that is distinct from the Standard Model and testable by known experiments."
        ),
    }


def e8_falsification_profile():
    return {
        "theory": "E8-based models",
        "key_prediction": "Exotic leptoquarks, mirror fermions, and colored states at ~10 TeV",
        "experiment": "FCC-ee / FCC-hh",
        "launch_year": FCC_EE_LAUNCH,
        "falsification_year_estimate": 2043,
        "has_near_term_falsifier": True,
        "notes": "FCC-ee begins ~2041; discovery or exclusion of E8-specific particles by ~2043",
    }


def cdt_falsification_profile():
    return {
        "theory": "Causal Dynamical Triangulations (CDT)",
        "key_prediction": "Hausdorff dimension d_H ≈ 2 at UV scales, measurable via GW spectrum",
        "experiment": "LISA",
        "launch_year": LISA_LAUNCH,
        "falsification_year_estimate": 2036,
        "has_near_term_falsifier": True,
        "notes": "LISA primordial GW background spectrum encodes UV Hausdorff dimension",
    }


def comparative_calendar():
    profiles = [
        um_falsification_profile(),
        wolfram_falsification_profile(),
        gu_falsification_profile(),
        e8_falsification_profile(),
        cdt_falsification_profile(),
    ]
    return sorted(profiles, key=lambda p: p["falsification_year_estimate"])


def theories_with_near_term_falsifiers():
    return [p["theory"] for p in comparative_calendar() if p["has_near_term_falsifier"]]


def falsification_calendar_audit():
    calendar = comparative_calendar()
    near_term = theories_with_near_term_falsifiers()
    return {
        "profiles": calendar,
        "near_term_theories": near_term,
        "um_strategic_position": (
            "Only UM and CDT have near-term falsification windows before 2035; "
            "UM is the only theory with a CMB polarization test"
        ),
        "earliest_falsifier": calendar[0]["theory"],
        "earliest_year": calendar[0]["falsification_year_estimate"],
        "status": "STRATEGIC_ASSET",
    }


def pillar178_summary():
    audit = falsification_calendar_audit()
    return (
        f"Pillar 178 — Falsification Calendar: "
        f"near-term theories={audit['near_term_theories']}, "
        f"earliest={audit['earliest_falsifier']} ({audit['earliest_year']}), "
        f"status={audit['status']}"
    )
