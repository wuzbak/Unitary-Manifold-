# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
9-INFRASTRUCTURE/generate_live_status.py — Live Status JSON Generator

Produces um_live_status.json: a compact, machine-readable JSON document
containing all values that Base44 (or any frontend) needs to display live
repository status without maintaining its own parallel copy.

Designed for fetching from:
  https://raw.githubusercontent.com/wuzbak/Unitary-Manifold-/main/9-INFRASTRUCTURE/um_live_status.json

Cache recommendation: 1 hour (values change only on sprint merges).

Structure:
  meta            — version, sprint, date, source_of_truth
  tests           — passed, skipped, deselected, failed
  lean4           — theorem_count
  pillars         — next_slot, hardgate_count, total_slots
  physics         — static constants (never change)
  predictions     — live falsification-window verdicts
  open_gates      — active non-PASS gates (honest tension inventory)
  fetch_targets   — URLs for the two context files Base44 should fetch

Usage:
  python 9-INFRASTRUCTURE/generate_live_status.py          # writes um_live_status.json
  python 9-INFRASTRUCTURE/generate_live_status.py --check  # validate only, exit non-zero if invalid

Theory & scientific direction: ThomasCory Walker-Pearson.
Code, engineering, synthesis: GitHub Copilot (AI).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
STATUS_PATH = REPO_ROOT / "STATUS.md"
OUTPUT_PATH = REPO_ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"

# ---------------------------------------------------------------------------
# Static physics constants — these never change; they are geometric derivations
# ---------------------------------------------------------------------------
PHYSICS_CONSTANTS = {
    "winding_number_n_w": 5,
    "cs_level_k_cs": 74,
    "braided_sound_speed_numerator": 12,
    "braided_sound_speed_denominator": 37,
    "braided_sound_speed_decimal": round(12 / 37, 6),
    "cmb_spectral_index_n_s": 0.9635,
    "tensor_to_scalar_ratio_r": 0.0315,
    "birefringence_low_branch_deg": 0.273,
    "birefringence_high_branch_deg": 0.331,
    "birefringence_derived_low_deg": 0.290,
    "birefringence_derived_high_deg": 0.351,
    "birefringence_admissible_window": [0.22, 0.38],
    "birefringence_gap_forbidden": [0.29, 0.31],
    "xi_c_consciousness_coupling": round(35 / 74, 6),
    "sentinel_capacity": round(12 / 37, 6),
    "kk_graviton_mass_tev": 1.0,
    "dark_matter_mass_window_tev": [0.8, 1.3],
    "quark_lepton_cl_split": round(-4 / 222, 6),
    "dimensions": 5,
    "planck_units": True,
}

# ---------------------------------------------------------------------------
# Live falsification-window verdicts — updated each sprint
# Keep aligned with STATUS.md, FALLIBILITY.md, CLAIM_MASTER_BOARD.md,
# GATEKEEPER_SUMMARY.md, TRUTH_LAYER.md, and the observation-gated freeze lanes.
# ---------------------------------------------------------------------------
PREDICTIONS = [
    {
        "id": "EXP-1",
        "name": "LiteBIRD CMB birefringence β",
        "status": "EXTERNAL_WAIT_ONLY",
        "sigma": 4.8,
        "measured_value": "β=0.277°±0.057° (ACT+Planck DR6)",
        "predicted_range": "[0.22°, 0.38°] excl. [0.29°–0.31°]",
        "verdict": "ACT+Planck DR6 remains consistent with the low branch, but the live lane stays external-wait-only pending LiteBIRD/SO discrimination.",
        "kill_condition": "β outside [0.22°,0.38°] OR β in [0.29°,0.31°]",
        "decision_window": "LiteBIRD ~2032 / Simons Observatory ~2028",
        "pillar": 795,
    },
    {
        "id": "EXP-2",
        "name": "DESI dark energy w_a",
        "status": "HIGH_TENSION",
        "verdict": "DESI DR2/Year 3 leaves the frozen-radion lane under high tension: BAO-only ≈2.07σ on w_a, combined BAO+CMB+SNe ≈2.75σ, 2D correlated tension ≈2.30σ; below the 3σ falsifier.",
        "kill_condition": "w_a ≠ 0 confirmed >3σ by ≥3 independent datasets",
        "decision_window": "DESI DR3 / late-2026 publication window",
        "pillar": 797,
    },
    {
        "id": "EXP-3",
        "name": "JUNO neutrino mass ordering + Δm²₁₂",
        "status": "TENSION_ESCALATED",
        "sigma": 1.71,
        "measured_value": "sin²θ₁₂=0.3092±0.0087",
        "verdict": "G4 tension 1.07σ→1.71σ (JUNO 2026 first data); NH preferred 2.2–2.3σ",
        "kill_condition": "IH confirmed >3σ OR Δm²₂₁ measured value excludes UM window",
        "decision_window": "JUNO Year 2 ~2027",
        "pillar": 796,
    },
    {
        "id": "EXP-4",
        "name": "CMB-S4 / ACT tensor-to-scalar ratio r",
        "status": "HIGH_TENSION",
        "verdict": "BICEP/Keck and SPT-3G remain consistent, but ACT DR6 reports r<0.016 (95% CL), placing the UM r=0.0315 prediction under high tension; the measured-value falsifier is not yet triggered.",
        "kill_condition": "r < 0.010 at >3σ (CMB-S4 ~2030)",
        "decision_window": "Simons Observatory ~2027 / CMB-S4 ~2028-2030",
        "pillar": 793,
    },
    {
        "id": "EXP-5",
        "name": "HL-LHC KK graviton M_G*",
        "status": "PASS",
        "verdict": "M_G*(n=1)≈1.0 TeV predicted; HL-LHC exclusion <4.0 TeV — PASS (within reach)",
        "kill_condition": "M_G* excluded up to 10 TeV",
        "decision_window": "HL-LHC Run 4 2029–2033",
        "pillar": 793,
    },
    {
        "id": "EXP-6",
        "name": "nEDM@SNS neutron EDM",
        "status": "PASS",
        "verdict": "d_n≈7.8×10⁻²⁷ e·cm; current bound 1.8×10⁻²⁶ e·cm — PASS",
        "kill_condition": "d_n > 10⁻²⁶ e·cm confirmed",
        "decision_window": "nEDM@SNS ~2028",
        "pillar": 540,
    },
    {
        "id": "EXP-7",
        "name": "XENON-nT dark matter σ_SI",
        "status": "PASS",
        "verdict": "σ_SI≈6×10⁻⁴⁷ cm² below XENON-nT limit — PASS",
        "kill_condition": "σ_SI excluded above 10⁻⁴⁷ cm²",
        "decision_window": "XENON-nT ongoing",
        "pillar": 790,
    },
]

# ---------------------------------------------------------------------------
# Active open gates (honest tension inventory — not failures, honest status)
# ---------------------------------------------------------------------------
OPEN_GATES = [
    {
        "gate": "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
        "description": "Flavor shared-root blocker remains open after proof-first contraction.",
        "pillar": 1081,
    },
    {
        "gate": "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
        "description": "Species-resolved RI geometry with bundle-moduli lock remains unresolved.",
        "pillar": 1081,
    },
    {
        "gate": "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
        "description": "Global CKM phase geometry remains architecture-limited after contraction.",
        "pillar": 1081,
    },
    {
        "gate": "ALPHA_S_TYPE_B_FLOOR",
        "description": "Shared UV compactification object remains open; joint α_s/Higgs residual persists.",
        "pillar": 1081,
    },
    {
        "gate": "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
        "description": "Shared UV compactification object remains open; joint α_s/Higgs residual persists.",
        "pillar": 1081,
    },
    {
        "gate": "CMB_AMP_CONFIRMED_IRREDUCIBLE",
        "description": "CMB amplitude lane remains internally irreducible absent the missing UV object.",
        "pillar": 1081,
    },
    {
        "gate": "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
        "description": "Non-perturbative QG remains bounded by the declared O1–O4 obstructions.",
        "pillar": 1081,
    },
    {
        "gate": "DESI_DR3_MONITORING",
        "description": "External wait only; frozen-radion dark-energy lane awaits DESI DR3.",
        "pillar": 1081,
    },
    {
        "gate": "LITEBIRD_BIREFRINGENCE",
        "description": "External wait only; birefringence lane awaits LiteBIRD.",
        "pillar": 1081,
    },
]

# ---------------------------------------------------------------------------
# Fetch targets for Base44
# ---------------------------------------------------------------------------
BASE_RAW_URL = "https://raw.githubusercontent.com/wuzbak/Unitary-Manifold-/main"
FETCH_TARGETS = {
    "live_status_json": f"{BASE_RAW_URL}/9-INFRASTRUCTURE/um_live_status.json",
    "ox_full_context_md": f"{BASE_RAW_URL}/9-INFRASTRUCTURE/ox_full_context.md",
    "status_md": f"{BASE_RAW_URL}/STATUS.md",
    "fallibility_md": f"{BASE_RAW_URL}/FALLIBILITY.md",
    "claim_master_board_md": f"{BASE_RAW_URL}/docs/CLAIM_MASTER_BOARD.md",
    "interrogator_kb_json": f"{BASE_RAW_URL}/public-site/data/interrogator-kb.json",
}


# ---------------------------------------------------------------------------
# Parser — extract live counts from STATUS.md
# ---------------------------------------------------------------------------

def _parse_status_md() -> dict:
    """Parse the canonical values from the first sprint entry in STATUS.md."""
    text = STATUS_PATH.read_text(encoding="utf-8")
    sprint_start = text.find("*v")
    sprint_entry = text[sprint_start:].split("\n\n", 1)[0].strip() if sprint_start >= 0 else text

    # Version + sprint label
    version_match = re.search(r"\*v([\d.]+) Sprint (\w+)", sprint_entry)
    version = version_match.group(1) if version_match else "unknown"
    sprint = version_match.group(2) if version_match else "unknown"

    # Date
    date_match = re.search(r"\((\d{4}-\d{2}-\d{2})\)", sprint_entry)
    date = date_match.group(1) if date_match else "unknown"

    # Test counts — first occurrence
    tests_match = re.search(
        r"~?([\d,]+)\s+passed\s*[·•]\s*(\d+)\s+skipped\s*[·•]\s*(\d+)\s+deselected\s*[·•]\s*(\d+)\s+failed",
        sprint_entry,
    )
    tests = {
        "passed": int(tests_match.group(1).replace(",", "")) if tests_match else 0,
        "skipped": int(tests_match.group(2)) if tests_match else 0,
        "deselected": int(tests_match.group(3)) if tests_match else 0,
        "failed": int(tests_match.group(4)) if tests_match else 0,
    }

    # Lean4 theorem count — first occurrence = latest sprint's final total
    lean4_matches = re.findall(r"Lean4[^)]*?(?:total\s+|→|\u2192)(\d{3,5})", sprint_entry)
    lean4_count = int(lean4_matches[0]) if lean4_matches else 0

    # Next pillar slot
    next_slot_match = re.search(r"next slot (\d+)", sprint_entry)
    next_slot = int(next_slot_match.group(1)) if next_slot_match else 0

    return {
        "version": version,
        "sprint": sprint,
        "date": date,
        "tests": tests,
        "lean4_theorem_count": lean4_count,
        "next_pillar_slot": next_slot,
    }


def build_live_status() -> dict:
    """Assemble the full live status document."""
    parsed = _parse_status_md()

    return {
        "_comment": "Auto-generated by 9-INFRASTRUCTURE/generate_live_status.py — do not edit manually. Fetch live from GitHub raw URL.",
        "_fetch_url": FETCH_TARGETS["live_status_json"],
        "_cache_ttl_seconds": 3600,
        "meta": {
            "version": parsed["version"],
            "sprint": parsed["sprint"],
            "date": parsed["date"],
            "source_of_truth": "https://github.com/wuzbak/Unitary-Manifold-/blob/main/STATUS.md",
            "generated_by": "9-INFRASTRUCTURE/generate_live_status.py",
        },
        "tests": parsed["tests"],
        "lean4": {
            "theorem_count": parsed["lean4_theorem_count"],
        },
        "pillars": {
            "next_slot": parsed["next_pillar_slot"],
            "hardgate_count": 208,
            "total_slots": parsed["next_pillar_slot"] - 1,
        },
        "physics": PHYSICS_CONSTANTS,
        "predictions": PREDICTIONS,
        "open_gates": OPEN_GATES,
        "fetch_targets": FETCH_TARGETS,
    }


def validate(data: dict) -> list[str]:
    """Return list of validation errors (empty = valid)."""
    errors = []
    if data["tests"]["failed"] != 0:
        errors.append(f"tests.failed = {data['tests']['failed']} (must be 0)")
    if data["tests"]["passed"] < 50000:
        errors.append(f"tests.passed = {data['tests']['passed']} (suspiciously low)")
    if data["lean4"]["theorem_count"] < 1000:
        errors.append(f"lean4.theorem_count = {data['lean4']['theorem_count']} (suspiciously low)")
    if data["pillars"]["next_slot"] < 801:
        errors.append(f"pillars.next_slot = {data['pillars']['next_slot']} (should be ≥ 801)")
    if data["physics"]["winding_number_n_w"] != 5:
        errors.append("physics.winding_number_n_w must be 5")
    if data["physics"]["cs_level_k_cs"] != 74:
        errors.append("physics.cs_level_k_cs must be 74")
    predictions = {row["id"]: row for row in data["predictions"]}
    if predictions.get("EXP-2", {}).get("status") != "HIGH_TENSION":
        errors.append("EXP-2 must remain HIGH_TENSION until canonical truth surfaces change")
    if "DESI DR3" not in predictions.get("EXP-2", {}).get("decision_window", ""):
        errors.append("EXP-2 decision_window must mention DESI DR3")
    if predictions.get("EXP-4", {}).get("status") != "HIGH_TENSION":
        errors.append("EXP-4 must remain HIGH_TENSION until canonical truth surfaces change")
    if "CMB-S4" not in predictions.get("EXP-4", {}).get("decision_window", ""):
        errors.append("EXP-4 decision_window must mention CMB-S4")
    required_open_gates = {
        "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED",
        "FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED",
        "JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED",
        "ALPHA_S_TYPE_B_FLOOR",
        "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
        "CMB_AMP_CONFIRMED_IRREDUCIBLE",
        "NON_PERTURBATIVE_QG_IRREDUCIBLE_LIMIT",
        "DESI_DR3_MONITORING",
        "LITEBIRD_BIREFRINGENCE",
    }
    live_gate_names = {row.get("gate") for row in data.get("open_gates", [])}
    missing_gates = sorted(required_open_gates - live_gate_names)
    if missing_gates:
        errors.append(f"open_gates missing required current lanes: {', '.join(missing_gates)}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate um_live_status.json")
    parser.add_argument("--check", action="store_true", help="Validate only; exit non-zero if invalid")
    parser.add_argument("--output", type=str, default=str(OUTPUT_PATH), help="Output path")
    args = parser.parse_args(argv)

    data = build_live_status()
    errors = validate(data)

    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if args.check:
        print(f"OK: um_live_status.json would be valid (v{data['meta']['version']}, "
              f"{data['tests']['passed']:,} tests, "
              f"{data['lean4']['theorem_count']} Lean4 theorems, "
              f"next slot {data['pillars']['next_slot']})")
        return 0

    out_path = Path(args.output)
    out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Written: {out_path} ({out_path.stat().st_size:,} bytes)")
    print(f"  version: v{data['meta']['version']} Sprint {data['meta']['sprint']}")
    print(f"  tests: {data['tests']['passed']:,} passed · {data['tests']['failed']} failed")
    print(f"  lean4: {data['lean4']['theorem_count']} theorems")
    print(f"  next pillar slot: {data['pillars']['next_slot']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
