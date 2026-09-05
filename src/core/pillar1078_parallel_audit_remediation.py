# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1078 — post-merge audit remediation certificate.

Adjacency / scope:
    Repository-integrity and epistemic-hardening artifact.
    It does not promote new hardgate physics claims.

Purpose:
    1) verify observation-status surfaces no longer present stale sprint state
       as canonical,
    2) verify live-status JSON/reporting lanes match the current open-lane
       ledger,
    3) verify evolution/radion documentation fixes are explicit,
    4) verify selected Lean proxy surfaces now disclose their scope honestly,
    5) verify the sprint report + article packet exists.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from typing import Any
from uuid import uuid4

PILLAR_NUMBER = 1078
PILLAR_TITLE = "Post-Merge Audit Remediation Certificate"
PILLAR_STATUS = "POST_MERGE_AUDIT_REMEDIATION_COMPLETE"
VERSION = "v36.3"
SPRINT = "CG"
NEXT_PILLAR_SLOT = 1079
ADJACENCY_LABEL = "NON_HARDGATE_AUDIT_REMEDIATION"

_ROOT = Path(__file__).resolve().parents[2]
_OBS_TRACKER = _ROOT / "3-FALSIFICATION" / "OBSERVATION_TRACKER.md"
_EVOLUTION = _ROOT / "src" / "core" / "evolution.py"
_PILLAR_833 = _ROOT / "src" / "core" / "pillar833_radion_two_loop_stability.py"
_LIVE_STATUS_JSON = _ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"
_LIVE_STATUS_PY = _ROOT / "9-INFRASTRUCTURE" / "generate_live_status.py"
_PUBLIC_STATUS = _ROOT / "public-site" / "data" / "status.json"
_PORTAL_STATUS = _ROOT / "public-site" / "portal" / "knowledge" / "status.json"
_SELF_RUN_REPORT = _ROOT / "7-OUTREACH" / "self-run-reports" / "FINDINGS_REPORT_2026-09-05_SRR-20260905-P1078-R1.md"
_SUBSTACK_POST = _ROOT / "7-OUTREACH" / "substack" / "posts" / "post-302-s04e005-v36-2-parallel-audit-remediation.md"

_LEAN_DISCLOSURE_TARGETS = {
    "OrbifoldBCUniqueness.lean": "not a constructive Lean derivation of the full 5D Dirac/orbifold boundary",
    "BirefringenceACTDR6.lean": "These are arithmetic checks on millidegree proxy integers.",
    "RadionTwoLoopStability.lean": "They do not by themselves construct the full two-loop field theory",
    "SprintCAFormalTraceability.lean": "proof-structure scaffolding only",
    "SprintBDITheoryBridge.lean": "markers (`True := trivial`)",
}

_REQUIRED_OPEN_GATES = {
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

_PRIMARY_FALSIFIER = "LiteBIRD β ∈ {0.273°, 0.331°} (~2032)"
_EPISTEMIC_STATUS = "foundation reassessment: historical test and theorem counts do not establish physical derivations; photon origin, flavor uniqueness, independent CMB normalization and UV predictivity remain open; external empirical confirmation pending"
_ORG_NAME = "AxiomZero Technologies & Consulting, SPC"
_ORG_UBI = "606 239 876"
_FLAVOR_STATUS = "CKM_SHADOW_ARCHITECTURE_LIMIT_CERTIFIED / FERMION_MAGNITUDE_RADII_ARCHITECTURE_LIMIT_CERTIFIED / JARLSKOG_LAYER2_ARCHITECTURE_LIMIT_CERTIFIED"
_OPEN_TENSIONS = [
    {"name": "Flavor family boundary", "status": _FLAVOR_STATUS},
    {"name": "α_s Type-B floor", "status": "ALPHA_S_TYPE_B_FLOOR"},
    {"name": "CMB amplitude floor", "status": "CMB_AMP_CONFIRMED_IRREDUCIBLE"},
    {"name": "DESI dark-energy lane", "status": "HIGH_TENSION"},
    {"name": "Tensor-to-scalar ratio r", "status": "HIGH_TENSION"},
]


def _canonical_status_surface_fields(live_status: dict[str, Any]) -> dict[str, Any]:
    live_version = str((live_status.get("meta") or {}).get("version", "")).strip()
    if live_version:
        version_label = live_version if live_version.startswith("v") else f"v{live_version}"
    else:
        version_label = VERSION
    return {
        "version": version_label,
        "tests_passed": live_status["tests"]["passed"],
        "tests_skipped": live_status["tests"]["skipped"],
        "tests_deselected": live_status["tests"]["deselected"],
        "tests_failed": live_status["tests"]["failed"],
        "lean4_theorems": live_status["lean4"]["theorem_count"],
        "pillars_hardgate": live_status["pillars"]["hardgate_count"],
        "pillars_total": live_status["pillars"]["total_slots"],
        "next_pillar_slot": live_status["pillars"]["next_slot"],
        "primary_falsifier": _PRIMARY_FALSIFIER,
        "open_tensions": [row.copy() for row in _OPEN_TENSIONS],
        "epistemic_status": _EPISTEMIC_STATUS,
        "organization": _ORG_NAME,
        "ubi": _ORG_UBI,
    }


def _shared_public_prediction_fragments() -> dict[str, Any]:
    return {
        "r": {"um": 0.0315, "bound": 0.036, "status": "HIGH_TENSION"},
        "w_a": {"um": 0.0, "status": "HIGH_TENSION"},
    }


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    details: str


def _normalize_live_status(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload)
    normalized.pop("_comment", None)
    normalized.pop("_fetch_url", None)
    normalized.pop("_cache_ttl_seconds", None)
    meta = dict(normalized.get("meta") or {})
    normalized["meta"] = {
        "version": meta.get("version"),
        "sprint": meta.get("sprint"),
        "date": meta.get("date"),
    }
    return normalized


def _expected_public_status(live_status: dict[str, Any]) -> dict[str, Any]:
    expected = _canonical_status_surface_fields(live_status)
    expected["date"] = live_status["meta"]["date"]
    expected["predictions"] = _shared_public_prediction_fragments()
    return expected


def _expected_portal_status(live_status: dict[str, Any]) -> dict[str, Any]:
    expected = _canonical_status_surface_fields(live_status)
    expected.update({
        "generated": live_status["meta"]["date"],
        "pillars": live_status["pillars"]["hardgate_count"],
        "adjacent_tracks": live_status["pillars"]["total_slots"] - live_status["pillars"]["hardgate_count"],
        "regression": f"{live_status['tests']['passed']:,} passed · {live_status['tests']['skipped']} skipped · {live_status['tests']['deselected']} deselected · {live_status['tests']['failed']} failed",
        "predictions": {
            "n_s": {
                "um": 0.9635,
                "planck": 0.9649,
                "sigma": 0.0042,
                "tension_sigma": 0.3,
                "gate": "HARDGATE",
            },
            "r": {
                **_shared_public_prediction_fragments()["r"],
                "gate": "OPEN_GAP",
            },
            "beta": {
                "um": [0.273, 0.331],
                "window": [0.22, 0.38],
                "gap": [0.29, 0.31],
                "test": "LiteBIRD ~2032 / Simons Observatory ~2028",
                "gate": "HARDGATE",
                "status": "EXTERNAL_WAIT_ONLY",
            },
            "higgs_mass_GeV": {
                "um": 125.25,
                "lhc": 125.25,
                "lhc_sigma": 0.17,
                "gate": "OPEN_GAP",
                "status": "HIGGS_MASS_ARCHITECTURE_LIMIT_WINDOW",
            },
            "w_a": {
                "um": _shared_public_prediction_fragments()["w_a"]["um"],
                "desi_status": "HIGH_TENSION",
                "verdict": "DESI DR2/Year 3 leaves the frozen-radion lane under high tension but below the 3σ falsifier.",
                "gate": "OPEN_GAP",
                "test": "DESI DR3 / late-2026 publication window",
            },
            "flavor_family": {
                "value": _FLAVOR_STATUS,
                "gate": "OPEN_GAP",
                "pillar": PILLAR_NUMBER,
            },
            "alpha_s_floor": {
                "value": "Shared UV compactification object remains unresolved",
                "gate": "OPEN_GAP",
                "pillar": PILLAR_NUMBER,
            },
        },
        "open_tensions": [row.copy() for row in _OPEN_TENSIONS],
        "open_gaps": [
            "Flavor-family residuals remain architecture-limited under the shared-root blocker map",
            "α_s Type-B floor remains outside the shared UV compactification solution surface",
            "w_a tension remains tracked below the hard falsification threshold",
            "CMB amplitude mismatch remains an explicit irreducible architecture limit",
            "Non-perturbative QG remains bounded by named O1–O4 obstructions",
        ],
        "constants": {
            "N_W": 5,
            "K_CS": 74,
            "C_S": 0.324324,
            "XI_C": 0.472973,
            "SENTINEL_CAPACITY": 0.324324,
            "HIL_THRESHOLD": 15,
        },
        "portal": {
            "home": "https://axiomzerospc.org/portal/",
            "knowledge": "https://axiomzerospc.org/portal/knowledge/",
            "gym": "https://axiomzerospc.org/portal/gym/",
            "engine": "https://axiomzerospc.org/portal/engine/",
            "library": "https://axiomzerospc.org/portal/library/",
        },
    })
    return expected


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_module(path: Path, name: str) -> Any:
    unique_name = f"{name}_{uuid4().hex}"
    spec = spec_from_file_location(unique_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {path}")
    module = module_from_spec(spec)
    sys.modules[unique_name] = module
    try:
        spec.loader.exec_module(module)
        return module
    except Exception:
        sys.modules.pop(unique_name, None)
        raise
    finally:
        sys.modules.pop(unique_name, None)


def observation_tracker_status_check() -> dict[str, Any]:
    text = _read_text(_OBS_TRACKER)
    return {
        "historical_banner_present": "Historical routing ledger + active decision procedures." in text,
        "canonical_source_notice_present": "it is **not** the canonical current sprint/status source" in text,
        "current_architecture_note_present": "the checked-in sprint protocol now" in text,
        "freshness_note_present": "Freshness note (audit remediation)" in text,
        "desi_wait_language_current": "await DESI DR3 publication" in text,
        "status": "PASS" if all(
            marker in text for marker in (
                "Historical routing ledger + active decision procedures.",
                "it is **not** the canonical current sprint/status source",
                "the checked-in sprint protocol now",
                "Freshness note (audit remediation)",
                "await DESI DR3 publication",
            )
        ) else "FAIL",
    }


def evolution_doc_honesty_check() -> dict[str, Any]:
    text = _read_text(_EVOLUTION)
    required = {
        "optional_stabilization": "This stabilization is available but disabled by default",
        "adm_closure": "was closed in v13.7 by Pillar 434",
        "kk_lower_bound": "zero-mode entropy production is a lower bound on the full KK tower",
    }
    found = {key: phrase in text for key, phrase in required.items()}
    return {
        "markers": found,
        "status": "PASS" if all(found.values()) else "FAIL",
    }


def radion_proxy_honesty_check() -> dict[str, Any]:
    text = _read_text(_PILLAR_833)
    module = _load_module(_PILLAR_833, "pillar1078_p833")
    mass = module.radion_mass_two_loop()
    required_phrases = {
        "threshold_honesty": "satisfies the implemented 0.2% stability bound but not",
        "gradient_proxy_note": "mass_proxy_uses_gradient_not_exact_hessian",
        "curvature_proxy_exported": "potential_curvature_proxy",
    }
    found = {key: phrase in text for key, phrase in required_phrases.items()}
    return {
        "doc_markers": found,
        "positive_local_curvature": bool(mass["positive_local_curvature"]),
        "gradient_proxy_flag": bool(mass["mass_proxy_uses_gradient_not_exact_hessian"]),
        "status": "PASS" if all(found.values()) and mass["positive_local_curvature"] and mass["mass_proxy_uses_gradient_not_exact_hessian"] else "FAIL",
    }


def lean_proxy_disclosure_check() -> dict[str, Any]:
    base = _ROOT / "lean4" / "UnitaryManifold"
    checks = {}
    for filename, needle in _LEAN_DISCLOSURE_TARGETS.items():
        text = _read_text(base / filename)
        checks[filename] = needle in text
    return {
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def live_status_alignment_check() -> dict[str, Any]:
    generator = _load_module(_LIVE_STATUS_PY, "pillar1078_live_status")
    built = generator.build_live_status()
    repo_json = json.loads(_LIVE_STATUS_JSON.read_text(encoding="utf-8"))
    normalized_built = _normalize_live_status(built)
    normalized_repo = _normalize_live_status(repo_json)
    repo_predictions = {row["id"]: row for row in repo_json["predictions"]}
    built_predictions = {row["id"]: row for row in built["predictions"]}
    repo_open_gate_names = {row["gate"] for row in repo_json["open_gates"]}
    built_open_gate_names = {row["gate"] for row in built["open_gates"]}
    return {
        "json_matches_generator": normalized_repo == normalized_built,
        "repo_exp2_status": repo_predictions["EXP-2"]["status"],
        "repo_exp4_status": repo_predictions["EXP-4"]["status"],
        "built_exp2_status": built_predictions["EXP-2"]["status"],
        "built_exp4_status": built_predictions["EXP-4"]["status"],
        "required_open_gates_present": sorted(_REQUIRED_OPEN_GATES - repo_open_gate_names) == [],
        "generator_required_open_gates_present": sorted(_REQUIRED_OPEN_GATES - built_open_gate_names) == [],
        "status": "PASS" if (
            normalized_repo == normalized_built
            and repo_predictions["EXP-2"]["status"] == "HIGH_TENSION"
            and repo_predictions["EXP-4"]["status"] == "HIGH_TENSION"
            and built_predictions["EXP-2"]["status"] == "HIGH_TENSION"
            and built_predictions["EXP-4"]["status"] == "HIGH_TENSION"
            and _REQUIRED_OPEN_GATES.issubset(repo_open_gate_names)
            and _REQUIRED_OPEN_GATES.issubset(built_open_gate_names)
        ) else "FAIL",
    }


def public_status_sync_check() -> dict[str, Any]:
    public = json.loads(_PUBLIC_STATUS.read_text(encoding="utf-8"))
    portal = json.loads(_PORTAL_STATUS.read_text(encoding="utf-8"))
    live_status = json.loads(_LIVE_STATUS_JSON.read_text(encoding="utf-8"))
    expected_public = _expected_public_status(live_status)
    expected_portal = _expected_portal_status(live_status)
    aligned = public == expected_public and portal == expected_portal
    return {
        "public_version": public["version"],
        "portal_version": portal["version"],
        "live_status_version": f"v{live_status['meta']['version']}",
        "public_matches_expected": public == expected_public,
        "portal_matches_expected": portal == expected_portal,
        "aligned": aligned,
        "status": "PASS" if aligned else "FAIL",
    }


def publication_packet_check() -> dict[str, Any]:
    return {
        "self_run_report_exists": _SELF_RUN_REPORT.exists(),
        "substack_post_exists": _SUBSTACK_POST.exists(),
        "status": "PASS" if _SELF_RUN_REPORT.exists() and _SUBSTACK_POST.exists() else "FAIL",
    }


def pillar1078_parallel_audit_report() -> dict[str, Any]:
    checks = {
        "observation_tracker": observation_tracker_status_check(),
        "evolution_docs": evolution_doc_honesty_check(),
        "radion_proxy": radion_proxy_honesty_check(),
        "lean_proxy_disclosures": lean_proxy_disclosure_check(),
        "live_status": live_status_alignment_check(),
        "public_status": public_status_sync_check(),
        "publication_packet": publication_packet_check(),
    }
    failures = [name for name, row in checks.items() if row["status"] != "PASS"]
    return {
        "pillar": PILLAR_NUMBER,
        "title": PILLAR_TITLE,
        "status": PILLAR_STATUS,
        "version": VERSION,
        "sprint": SPRINT,
        "next_pillar_slot": NEXT_PILLAR_SLOT,
        "adjacency_label": ADJACENCY_LABEL,
        "checks": checks,
        "failing_checks": failures,
        "overall_status": "PASS_WITH_FIXES" if not failures else "FAIL",
        "non_hardgate_statement": "This certificate hardens documentation, auditability, and live-status honesty without promoting new hardgate physics claims.",
    }


def pillar1078_summary() -> dict[str, Any]:
    report = pillar1078_parallel_audit_report()
    return {
        "pillar": report["pillar"],
        "status": report["status"],
        "overall_status": report["overall_status"],
        "failing_checks": report["failing_checks"],
    }
