"""
FilmersCompanion — Knowledge Base
===================================
Static knowledge base for film production. Used as offline fallback.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Axiom Omega Principles
# ---------------------------------------------------------------------------

AXIOM_OMEGA_PRINCIPLES: dict[int, str] = {
    1: "Prepare thoroughly. Every dollar of prep saves 3-10x on set.",
    2: "Protect the day length. Ten hours maximum.",
    3: "Honor turnaround. Twelve hours minimum between shifts.",
    4: "Maintain the feedback loops. Dailies reviewed, call sheets distributed daily.",
    5: "Build in slack. Ten to fifteen percent schedule contingency.",
    6: "Pay fairly. Retention is cheaper than replacement.",
    7: "Keep information moving. No information silos.",
    8: "Protect the irreversible decisions. Location/cast/technical commitments chosen carefully.",
    9: "Make the problem visible early. Day-5 problem is negotiation; day-45 is crisis.",
    10: "Align the incentives. Crew, cast, studio, distributor all benefit from efficient production.",
}

# ---------------------------------------------------------------------------
# Feedback Loop Metrics
# ---------------------------------------------------------------------------

FEEDBACK_LOOP_METRICS: dict[int, str] = {
    1: "Daily page count vs. schedule",
    2: "Daily hour count (actual vs. 10-hour target)",
    3: "Weekly budget vs. actual (burn rate)",
    4: "Number of setups completed per day vs. plan",
    5: "Turnaround compliance rate (% days with ≥12h turnaround)",
    6: "Dailies review latency (hours from wrap to review completion)",
}

# ---------------------------------------------------------------------------
# Budget Allocation Defaults (percentages)
# ---------------------------------------------------------------------------

BUDGET_ALLOCATION_DEFAULTS: dict[str, dict] = {
    "above_the_line":      {"pct": 35.0, "description": "Director, writers, producers, lead cast"},
    "camera_lighting":     {"pct":  9.0, "description": "Camera, grip, electric packages"},
    "art_department":      {"pct":  7.0, "description": "Production design, set dec, props"},
    "locations":           {"pct":  5.0, "description": "Location fees, permits, scouts"},
    "post_production":     {"pct": 10.0, "description": "Edit, VFX, color, sound mix"},
    "contingency":         {"pct": 12.0, "description": "Budget and schedule buffer"},
    "overtime":            {"pct":  4.0, "description": "Anticipated overtime and turnaround costs"},
    "sound":               {"pct":  3.0, "description": "Production sound, music, SFX"},
    "hair_makeup_wardrobe":{"pct":  4.0, "description": "HMW department"},
    "insurance_legal":     {"pct":  3.0, "description": "E&O, production insurance, legal"},
    "misc":                {"pct":  8.0, "description": "Catering, travel, comms, office"},
}

# ---------------------------------------------------------------------------
# Guild Minimums (rough estimates, verify with current CBA)
# ---------------------------------------------------------------------------

GUILD_MINIMUMS: dict[str, dict] = {
    "SAG": {
        "description": "Screen Actors Guild — AFTRA",
        "day_rate_low": 1030,
        "day_rate_high": 3500,
        "weekly_low": 3575,
        "weekly_high": 9000,
        "notes": "Rates vary by budget tier (ultra-low, modified, basic). Verify current CBA.",
    },
    "DGA": {
        "description": "Directors Guild of America",
        "day_rate_low": 0,
        "weekly_low": 8500,
        "weekly_high": 25000,
        "notes": "Director minimums scale with budget. AD rates vary by category.",
    },
    "WGA": {
        "description": "Writers Guild of America",
        "day_rate_low": 0,
        "weekly_low": 4086,
        "weekly_high": 15000,
        "notes": "Script minimums vary by format and budget tier.",
    },
    "IATSE": {
        "description": "International Alliance of Theatrical Stage Employees",
        "day_rate_low": 350,
        "day_rate_high": 1200,
        "weekly_low": 1750,
        "weekly_high": 6000,
        "notes": "Rates vary significantly by local and job classification.",
    },
}

# ---------------------------------------------------------------------------
# Knowledge Base Entries
# ---------------------------------------------------------------------------

KB_ENTRIES: list[dict] = [
    {
        "keyword": "turnaround",
        "content": (
            "Turnaround is the minimum rest period between an actor or crew member's wrap time "
            "and their next call time. SAG-AFTRA and most union agreements require a minimum of "
            "12 hours. Axiom Omega Principle 3: Honor turnaround. Violations result in penalties "
            "and burned-out crew. Track with: gap_hours = call_time - wrap_time (if overnight, add 24h)."
        ),
        "source": "Axiom Omega Principles + SAG-AFTRA CBA",
    },
    {
        "keyword": "budget",
        "content": (
            "A production budget allocates funds across departments. Standard categories: "
            "above-the-line (ATL: 35%), camera/lighting (9%), art dept (7%), locations (5%), "
            "post-production (10%), contingency (12%), overtime (4%), sound (3%), HMW (4%), "
            "insurance/legal (3%), misc (8%). Always include 10-15% contingency. "
            "Track burn rate weekly: (actual/budgeted) × 100 = % used."
        ),
        "source": "Axiom Omega Budget Defaults",
    },
    {
        "keyword": "call sheet",
        "content": (
            "A call sheet is the daily production schedule distributed to cast and crew. "
            "It includes: general call time, scene numbers, location address, nearest hospital, "
            "individual department calls, equipment needs, and production notes. "
            "Must be distributed by midnight the night before shooting."
        ),
        "source": "Industry Standard AD Practice",
    },
    {
        "keyword": "coverage",
        "content": (
            "Scene coverage is the set of shots filmed to ensure adequate material in the edit. "
            "Standard coverage: Master shot (full scene, wide), Coverage (medium shots per character), "
            "Close-ups (CU, BCU), Cutaways, Inserts. Missing master = editorial risk. "
            "Coverage type codes: master, MS (medium shot), CU (close-up), BCU (big close-up), "
            "OTS (over the shoulder), POV, insert, cutaway, aerial, dolly."
        ),
        "source": "Cinematography Best Practice",
    },
    {
        "keyword": "location scout",
        "content": (
            "Location scouting evaluates potential filming sites for: "
            "1) Permit availability (some municipalities restrict filming), "
            "2) Electrical capacity for lighting packages, "
            "3) Sound environment (ambient noise, reverb), "
            "4) Parking/base camp space, "
            "5) Proximity to other locations, "
            "6) Owner cooperation and fee. "
            "Always have a backup location for exterior shots."
        ),
        "source": "Location Department Standard Practice",
    },
    {
        "keyword": "permit",
        "content": (
            "Filming permits are required by most municipalities for exterior shooting. "
            "Statuses: confirmed (permit in hand), pending (application submitted), "
            "rejected (denied — must find alternative), expired (permit lapsed). "
            "Plan 4-6 weeks for major city permits. Film commission contacts can expedite."
        ),
        "source": "Production Management Guidelines",
    },
    {
        "keyword": "f-stop",
        "content": (
            "F-stop (aperture) controls depth of field and exposure. "
            "Lower f-stop = more light, shallower DOF (e.g., f/1.4 for cinematic look). "
            "Higher f-stop = less light, deeper DOF (e.g., f/11 for daylight exteriors). "
            "Inverse square law: doubling light-to-subject distance quarters the intensity. "
            "Exposure = ISO × aperture × shutter speed (reciprocity principle)."
        ),
        "source": "Cinematography Reference",
    },
    {
        "keyword": "EV",
        "content": (
            "Exposure Value (EV) measures the combination of aperture and shutter speed "
            "that produces a given exposure. EV 0 = f/1.0 at 1 second. "
            "Daylight exteriors: EV 14-16. Interior with lighting: EV 6-10. "
            "Inverse square law: EV drops by 2 for every doubling of distance from source."
        ),
        "source": "Cinematography Reference",
    },
    {
        "keyword": "DOOD",
        "content": (
            "Day Out Of Days (DOOD) is the scheduling tool showing when each cast member "
            "works (W), holds (H), travels (T), or is on turnaround (R). "
            "Used to calculate actor fees, minimise hold days, and plan shooting order. "
            "A well-optimised DOOD reduces cast costs 15-30%."
        ),
        "source": "AD Department Practice",
    },
    {
        "keyword": "one-liner",
        "content": (
            "The one-liner (or stripboard one-liner) is a condensed scene list showing "
            "scene number, INT/EXT, location, day/night, and brief synopsis on a single line. "
            "Used by ADs to plan shooting order and identify groupings by location/time-of-day."
        ),
        "source": "AD Department Practice",
    },
    {
        "keyword": "ROI",
        "content": (
            "Return on Investment for film: ROI = (net_revenue - total_budget) / total_budget × 100%. "
            "Net revenue = projected_revenue × distribution_pct (typically 0.5-0.7 after distributor). "
            "Breakeven multiple = projected_revenue / total_budget. "
            "Most films need 2-3x budget in gross revenue to break even after P&A."
        ),
        "source": "Film Finance Reference",
    },
    {
        "keyword": "burn rate",
        "content": (
            "Burn rate = total_actual / total_budgeted × 100%. "
            "Alert threshold: >80% of budget spent before shoot completion. "
            "Days remaining = (total_budgeted - total_actual) / daily_burn_rate. "
            "Review weekly against schedule completion percentage."
        ),
        "source": "Production Finance Practice",
    },
    {
        "keyword": "dailies",
        "content": (
            "Dailies (rushes) are the raw footage from each day's shoot, reviewed by director, "
            "DP, and editor. Feedback loop metric: review latency should be <24 hours. "
            "Late dailies = slower editorial feedback = problems discovered late. "
            "Modern pipelines: DITs deliver proxies same night; LUTs applied for viewing."
        ),
        "source": "Axiom Omega Principle 4",
    },
    {
        "keyword": "contingency",
        "content": (
            "Contingency is a budget reserve for unforeseen costs. "
            "Axiom Omega default: 12%. Industry standard: 10-15%. "
            "Never raid contingency before week 3. "
            "Contingency should cover: weather delays, equipment failure, reshoots, "
            "cost overruns in any department."
        ),
        "source": "Axiom Omega Budget Defaults",
    },
    {
        "keyword": "color temperature",
        "content": (
            "Color temperature (Kelvin) describes light's warmth/coolness. "
            "Daylight: 5600K. Tungsten: 3200K. LED panels: tunable 2700-6500K. "
            "Mixed sources create color casts — match or use gels. "
            "Camera white balance should match dominant source. "
            "Warm light (<4000K) = golden/sunset. Cool light (>5000K) = daylight/blue."
        ),
        "source": "Cinematography Reference",
    },
    {
        "keyword": "above the line",
        "content": (
            "Above-the-line (ATL) costs are the key creative talent: director, producers, "
            "writers, and principal cast. ATL is negotiated before production begins. "
            "Below-the-line (BTL) covers crew, equipment, locations, and post. "
            "ATL typically 30-40% of total budget. Axiom Omega default: 35%."
        ),
        "source": "Film Finance Reference",
    },
    {
        "keyword": "SAG",
        "content": (
            "SAG-AFTRA is the union representing on-screen talent. "
            "Productions must sign a SAG agreement to hire union actors. "
            "Tiers: Ultra-Low Budget (<$250K), Modified Low Budget (<$700K), "
            "Low Budget (<$2.75M), Basic Agreement (all others). "
            "Violations incur fines and can result in strike action."
        ),
        "source": "SAG-AFTRA CBA Reference",
    },
    {
        "keyword": "inverse square law",
        "content": (
            "The inverse square law states that light intensity is inversely proportional "
            "to the square of the distance from the source: E = P / (4π × d²). "
            "Practical rule: doubling the distance from source to subject reduces light by 75% (2 stops). "
            "Used in cinematography to calculate exposure falloff and position lights."
        ),
        "source": "Cinematography Physics",
    },
    {
        "keyword": "shot list",
        "content": (
            "A shot list is the detailed plan of every shot in a scene: "
            "shot number, coverage type, lens, camera movement, frame rate, and notes. "
            "Required elements per scene: master, coverage (MS/OTS), close-ups. "
            "Shot lists are created by the director and DP during prep; "
            "reviewed by the 1st AD to estimate setup time per shot."
        ),
        "source": "Director/DP Prep Practice",
    },
]


# ---------------------------------------------------------------------------
# Search function
# ---------------------------------------------------------------------------

def search_kb(term: str) -> list[dict]:
    """Search KB_ENTRIES by keyword or content (case-insensitive, multi-word OR)."""
    if not term or not term.strip():
        return []
    # Split into words; try full phrase first then any-word match
    words = [w.lower() for w in term.strip().split() if len(w) >= 3]
    phrase = term.lower().strip()
    results = []
    seen = set()
    for entry in KB_ENTRIES:
        key = entry.get("keyword", "").lower()
        content = entry.get("content", "").lower()
        # Full phrase match (highest priority)
        if phrase in key or phrase in content:
            if id(entry) not in seen:
                seen.add(id(entry))
                results.append(entry)
            continue
        # Any-word match
        if words and any(w in key or w in content for w in words):
            if id(entry) not in seen:
                seen.add(id(entry))
                results.append(entry)
    return results
