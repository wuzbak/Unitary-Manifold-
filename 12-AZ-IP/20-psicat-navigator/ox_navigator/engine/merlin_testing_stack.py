# SPDX-License-Identifier: LicenseRef-Defensive-Public-Commons-1.0
# Copyright (C) 2026  ThomasCory Walker-Pearson

"""Testing-stack registry helpers for PsiCat and browser-facing AxiomZero products."""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
from typing import Any

PRODUCT_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PRODUCT_ROOT.parents[1]
MANIFEST_PATH = REPO_ROOT / "12-AZ-IP" / "tools" / "testing_stack_manifest.json"
PROMPT_CONTRACTS_PATH = PRODUCT_ROOT / "testing" / "psicat_prompt_contracts.json"


def _load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


@lru_cache(maxsize=1)
def _load_manifest() -> dict[str, Any]:
    return _load_json(MANIFEST_PATH)


@lru_cache(maxsize=1)
def _load_prompt_contracts() -> dict[str, Any]:
    return _load_json(PROMPT_CONTRACTS_PATH)


def get_psicat_prompt_contracts() -> dict[str, Any]:
    return dict(_load_prompt_contracts())


def get_psicat_testing_stack() -> dict[str, Any]:
    manifest = _load_manifest()
    prompt_contracts = get_psicat_prompt_contracts()
    cases = list(prompt_contracts.get("cases") or [])
    required_sections = sorted(
        {
            str(section)
            for case in cases
            for section in list(case.get("required_contract_sections") or [])
            if str(section).strip()
        }
    )
    observability_endpoints = sorted(
        {
            str(endpoint)
            for case in cases
            for endpoint in list(case.get("observability_endpoints") or [])
            if str(endpoint).strip()
        }
    )
    return {
        "shared_doctrine_path": "12-AZ-IP/tools/BROWSER_TESTING_DOCTRINE.md",
        "shared_manifest_path": "12-AZ-IP/tools/testing_stack_manifest.json",
        "product24_parallel_branch_role": (
            "Product 24's Playwright and Node validation lane is merged and now "
            "serves as the reference proving ground for conventions adopted here."
        ),
        "browser_default": dict(manifest.get("browser_default") or {}),
        "integration_classes": dict(manifest.get("integration_classes") or {}),
        "visual_regression_policy": dict(manifest.get("visual_regression_policy") or {}),
        "mobile_native_policy": dict(manifest.get("mobile_native_policy") or {}),
        "target_operating_model": dict(manifest.get("target_operating_model") or {}),
        "psicat": {
            "browser_lane": {
                "product_path": "12-AZ-IP/20-psicat-navigator",
                "ui_entrypoint": "ui/ox-navigator.html",
                "focus": [
                    "page_load_and_shell_render",
                    "prompt_submission",
                    "followup_chip_rendering",
                    "typed_source_card_rendering",
                    "session_continuity",
                    "offline_compat_failure_messaging",
                ],
            },
            "api_lane": {
                "required_endpoints": [
                    "/api/psicat",
                    "/api/psicat/status",
                    "/api/agentToolkit",
                    "/api/agentInvoke",
                    "/api/agentOrchestrate",
                    "/api/psicat/memory",
                    "/api/psicat/telemetry",
                    "/api/psicat/replacement-readiness",
                    "/api/psicat/frontier-readiness",
                    "/api/psicat/testing-stack",
                ],
            },
            "ai_evaluation_lane": {
                "tool_family": ["Promptfoo", "DeepEval"],
                "prompt_contract_manifest_path": "12-AZ-IP/20-psicat-navigator/testing/psicat_prompt_contracts.json",
                "prompt_contract_case_count": len(cases),
                "required_contract_sections": required_sections,
                "quality_dimensions": list(prompt_contracts.get("quality_dimensions") or []),
                "observability_endpoints": observability_endpoints,
            },
        },
        "product23": {
            "browser_lane": {
                "product_path": "12-AZ-IP/23-psicat-dm-assistant",
                "focus": [
                    "dm_dashboard_flow",
                    "invite_code_journey",
                    "player_dashboard_flow",
                    "standalone_solo_flow",
                    "embedded_psicat_contract_visibility",
                ],
            },
            "api_lane": {
                "required_endpoints": [
                    "/api/health",
                    "/api/campaigns",
                    "/api/join-campaign",
                    "/api/campaigns/<id>/dm-dashboard",
                    "/api/campaigns/<id>/player-dashboard",
                    "/api/player-dashboard/standalone",
                ],
            },
        },
    }
