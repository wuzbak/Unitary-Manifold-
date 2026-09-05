# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""Pillar 1062 — parallel audit remediation certificate.

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
from typing import Any

PILLAR_NUMBER = 1062
PILLAR_TITLE = "Parallel Audit Remediation Certificate"
PILLAR_STATUS = "PARALLEL_AUDIT_REMEDIATION_COMPLETE"
VERSION = "v36.2"
SPRINT = "CF"
NEXT_PILLAR_SLOT = 1063
ADJACENCY_LABEL = "NON_HARDGATE_AUDIT_REMEDIATION"

_ROOT = Path(__file__).resolve().parents[2]
_OBS_TRACKER = _ROOT / "3-FALSIFICATION" / "OBSERVATION_TRACKER.md"
_EVOLUTION = _ROOT / "src" / "core" / "evolution.py"
_PILLAR_833 = _ROOT / "src" / "core" / "pillar833_radion_two_loop_stability.py"
_LIVE_STATUS_JSON = _ROOT / "9-INFRASTRUCTURE" / "um_live_status.json"
_LIVE_STATUS_PY = _ROOT / "9-INFRASTRUCTURE" / "generate_live_status.py"
_PUBLIC_STATUS = _ROOT / "public-site" / "data" / "status.json"
_PORTAL_STATUS = _ROOT / "public-site" / "portal" / "knowledge" / "status.json"
_SELF_RUN_REPORT = _ROOT / "7-OUTREACH" / "self-run-reports" / "FINDINGS_REPORT_2026-09-05_SRR-20260905-P1062-R1.md"
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


@dataclass(frozen=True)
class CheckResult:
    name: str
    status: str
    details: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_module(path: Path, name: str) -> Any:
    spec = spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    module = _load_module(_PILLAR_833, "pillar1062_p833")
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
    generator = _load_module(_LIVE_STATUS_PY, "pillar1062_live_status")
    built = generator.build_live_status()
    repo_json = json.loads(_LIVE_STATUS_JSON.read_text(encoding="utf-8"))
    predictions = {row["id"]: row for row in built["predictions"]}
    open_gate_names = {row["gate"] for row in built["open_gates"]}
    return {
        "json_matches_generator": repo_json == built,
        "exp2_status": predictions["EXP-2"]["status"],
        "exp4_status": predictions["EXP-4"]["status"],
        "required_open_gates_present": sorted(_REQUIRED_OPEN_GATES - open_gate_names) == [],
        "status": "PASS" if (
            repo_json == built
            and predictions["EXP-2"]["status"] == "HIGH_TENSION"
            and predictions["EXP-4"]["status"] == "HIGH_TENSION"
            and _REQUIRED_OPEN_GATES.issubset(open_gate_names)
        ) else "FAIL",
    }


def public_status_sync_check() -> dict[str, Any]:
    public = json.loads(_PUBLIC_STATUS.read_text(encoding="utf-8"))
    portal = json.loads(_PORTAL_STATUS.read_text(encoding="utf-8"))
    live_status = json.loads(_LIVE_STATUS_JSON.read_text(encoding="utf-8"))
    aligned = (
        public["version"] == portal["version"]
        and public["version"] == VERSION
        and public["next_pillar_slot"] == portal["next_pillar_slot"]
        and public["next_pillar_slot"] == NEXT_PILLAR_SLOT
        and public["tests_passed"] == portal["tests_passed"]
        and public["tests_passed"] == live_status["tests"]["passed"]
        and public["tests_skipped"] == portal["tests_skipped"] == live_status["tests"]["skipped"]
        and public["tests_deselected"] == portal["tests_deselected"] == live_status["tests"]["deselected"]
        and public["tests_failed"] == portal["tests_failed"] == live_status["tests"]["failed"]
    )
    return {
        "public_version": public["version"],
        "portal_version": portal["version"],
        "live_status_version": f"v{live_status['meta']['version']}",
        "aligned": aligned,
        "status": "PASS" if aligned else "FAIL",
    }


def publication_packet_check() -> dict[str, Any]:
    return {
        "self_run_report_exists": _SELF_RUN_REPORT.exists(),
        "substack_post_exists": _SUBSTACK_POST.exists(),
        "status": "PASS" if _SELF_RUN_REPORT.exists() and _SUBSTACK_POST.exists() else "FAIL",
    }


def pillar1062_parallel_audit_report() -> dict[str, Any]:
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


def pillar1062_summary() -> dict[str, Any]:
    report = pillar1062_parallel_audit_report()
    return {
        "pillar": report["pillar"],
        "status": report["status"],
        "overall_status": report["overall_status"],
        "failing_checks": report["failing_checks"],
    }
