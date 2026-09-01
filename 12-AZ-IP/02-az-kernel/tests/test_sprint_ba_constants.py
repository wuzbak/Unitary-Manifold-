# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

from az_kernel_sprint_ba import (
    SPRINT_BA_CONSTANTS,
    get_sprint_ba_constants,
    validate_constants,
)


def test_constants_payload_metadata():
    assert SPRINT_BA_CONSTANTS["app"] == "02-az-kernel"
    assert SPRINT_BA_CONSTANTS["repository_version"] == "v25.5"
    assert SPRINT_BA_CONSTANTS["sprint"] == "BA"


def test_status_labels_are_supported():
    assert SPRINT_BA_CONSTANTS["status_labels"] == ["CLOSED", "PARTIAL", "OPEN"]


def test_k_cs_constant_value_and_status():
    k_cs = SPRINT_BA_CONSTANTS["constants"]["k_cs"]
    assert k_cs["value"] == 74
    assert k_cs["pillar"] == "P849"
    assert k_cs["status"] == "CLOSED"


def test_phi0_constant_value_and_status():
    phi0 = SPRINT_BA_CONSTANTS["constants"]["phi0"]
    assert phi0["value"] == 1.0
    assert phi0["pillar"] == "P853"
    assert phi0["status"] == "PARTIAL"


def test_dimensional_chain_value_and_status():
    chain = SPRINT_BA_CONSTANTS["constants"]["dimensional_chain"]
    assert chain["value"] == [11, 10, 9, 8, 7, 6, 5, 4]
    assert chain["step_count"] == 7
    assert chain["pillar"] == "P858"
    assert chain["status"] == "CLOSED"


def test_braided_sound_speed_is_12_over_37():
    c_s = SPRINT_BA_CONSTANTS["constants"]["braided_sound_speed"]
    assert str(c_s["value"]) == "12/37"


def test_getter_returns_deep_copy():
    payload = get_sprint_ba_constants()
    payload["constants"]["k_cs"]["value"] = 0
    assert SPRINT_BA_CONSTANTS["constants"]["k_cs"]["value"] == 74


def test_validate_constants_passes_for_default_payload():
    result = validate_constants()
    assert result["valid"] is True
    assert all(result["checks"].values())


def test_validate_constants_checks_k_cs_identity():
    payload = get_sprint_ba_constants()
    payload["constants"]["k_cs"]["value"] = 75
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["k_cs_identity"] is False


def test_validate_constants_checks_braided_sound_speed_identity():
    payload = get_sprint_ba_constants()
    payload["constants"]["braided_sound_speed"]["value"] = "1/2"
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["braided_sound_speed_identity"] is False


def test_validate_constants_checks_phi0_normalisation():
    payload = get_sprint_ba_constants()
    payload["constants"]["phi0"]["value"] = 0.99
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["phi0_unit_normalised"] is False


def test_validate_constants_checks_phi0_status_honesty():
    payload = get_sprint_ba_constants()
    payload["constants"]["phi0"]["status"] = "CLOSED"
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["phi0_status_honest"] is False


def test_validate_constants_checks_chain_endpoints():
    payload = get_sprint_ba_constants()
    payload["constants"]["dimensional_chain"]["value"] = [10, 9, 8, 7, 6, 5, 4, 3]
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["dimensional_chain_endpoints"] is False


def test_validate_constants_checks_chain_monotonicity():
    payload = get_sprint_ba_constants()
    payload["constants"]["dimensional_chain"]["value"] = [11, 10, 8, 7, 6, 5, 4]
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["dimensional_chain_monotonic"] is False


def test_validate_constants_checks_chain_step_count():
    payload = get_sprint_ba_constants()
    payload["constants"]["dimensional_chain"]["step_count"] = 6
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["dimensional_chain_step_count"] is False


def test_validate_constants_checks_status_labels():
    payload = get_sprint_ba_constants()
    payload["status_labels"] = ["CLOSED", "OPEN"]
    result = validate_constants(payload)
    assert result["valid"] is False
    assert result["checks"]["status_labels_supported"] is False


def test_cli_self_test_succeeds():
    script = APP_ROOT / "az_kernel_sprint_ba.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, check=False)
    assert result.returncode == 0
    assert '"valid": true' in result.stdout.lower()
    assert "PASS" in result.stdout


def test_markdown_documents_sprint_ba_constants():
    content = (APP_ROOT / "SPRINT_BA_CONSTANTS.md").read_text(encoding="utf-8")
    assert "P849" in content
    assert "P853" in content
    assert "P858" in content
    assert "CLOSED" in content
    assert "PARTIAL" in content


def test_readme_mentions_sprint_ba_integration():
    content = (APP_ROOT / "README.md").read_text(encoding="utf-8")
    assert "Sprint BA" in content
    assert "v25.5" in content
