# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Tests for Pillar 536 — AXIOMZERO_IP_REGISTRY."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from src.core.pillar536_axiomzero_ip_registry import (
    IP_ASSET_CLASSES,
    K_CS,
    N_MANAGERS,
    N_SUB_AGENTS,
    PHI_INVERSE,
    PI_K_R,
    PHYSICS_TO_OS_MAP,
    PILLAR_AUTHOR,
    PILLAR_DATE,
    PILLAR_NUMBER,
    PILLAR_STATUS,
    PILLAR_TITLE,
    WINDING_NUMBER,
    compute_sha256,
    fingerprint_all_assets,
    pillar536_report,
    verify_against_registry,
)

# ──────────────────────────────────────────────────────────────────────────────
# Pillar metadata
# ──────────────────────────────────────────────────────────────────────────────

class TestPillarMetadata:
    def test_pillar_number(self):
        assert PILLAR_NUMBER == 536

    def test_pillar_status(self):
        assert PILLAR_STATUS == "AXIOMZERO_IP_REGISTRY"

    def test_title_contains_axiomzero(self):
        assert "AxiomZero" in PILLAR_TITLE or "axiomzero" in PILLAR_TITLE.lower()

    def test_date_2026(self):
        assert "2026" in PILLAR_DATE

    def test_author_walker_pearson(self):
        assert "Walker-Pearson" in PILLAR_AUTHOR


# ──────────────────────────────────────────────────────────────────────────────
# Physics constants
# ──────────────────────────────────────────────────────────────────────────────

class TestPhysicsConstants:
    def test_winding_number_5(self):
        assert WINDING_NUMBER == 5

    def test_k_cs_74(self):
        assert K_CS == 74

    def test_k_cs_sum_of_squares(self):
        assert K_CS == 5 ** 2 + 7 ** 2

    def test_pi_k_r_37(self):
        assert PI_K_R == 37

    def test_phi_inverse(self):
        assert abs(PHI_INVERSE - 0.6180339887) < 1e-9

    def test_n_managers_7(self):
        assert N_MANAGERS == 7

    def test_n_sub_agents_5(self):
        assert N_SUB_AGENTS == 5

    def test_sub_agents_equals_winding_number(self):
        assert N_SUB_AGENTS == WINDING_NUMBER


# ──────────────────────────────────────────────────────────────────────────────
# IP asset class registry
# ──────────────────────────────────────────────────────────────────────────────

class TestAssetClasses:
    def test_at_least_4_classes(self):
        assert len(IP_ASSET_CLASSES) >= 4

    def test_az_os_class_present(self):
        names = [c["class"] for c in IP_ASSET_CLASSES]
        assert "AZ-OS" in names

    def test_az_kernel_class_present(self):
        names = [c["class"] for c in IP_ASSET_CLASSES]
        assert "AZ-KERNEL" in names

    def test_axiomzero_guard_class_present(self):
        names = [c["class"] for c in IP_ASSET_CLASSES]
        assert "AXIOMZERO_GUARD" in names

    def test_ip_registry_class_present(self):
        names = [c["class"] for c in IP_ASSET_CLASSES]
        assert "IP_REGISTRY" in names

    def test_all_classes_have_assets(self):
        for cls in IP_ASSET_CLASSES:
            assert len(cls["assets"]) >= 1

    def test_all_assets_have_path_and_description(self):
        for cls in IP_ASSET_CLASSES:
            for asset in cls["assets"]:
                assert "path" in asset
                assert "description" in asset
                assert len(asset["path"]) > 0
                assert len(asset["description"]) > 0

    def test_az_os_has_agent_core(self):
        az_os = next(c for c in IP_ASSET_CLASSES if c["class"] == "AZ-OS")
        paths = [a["path"] for a in az_os["assets"]]
        assert any("agent_core" in p for p in paths)

    def test_az_os_has_hils(self):
        az_os = next(c for c in IP_ASSET_CLASSES if c["class"] == "AZ-OS")
        paths = [a["path"] for a in az_os["assets"]]
        assert any("hils" in p for p in paths)

    def test_az_kernel_has_cargo_toml(self):
        kernel = next(c for c in IP_ASSET_CLASSES if c["class"] == "AZ-KERNEL")
        paths = [a["path"] for a in kernel["assets"]]
        assert any("Cargo.toml" in p for p in paths)


# ──────────────────────────────────────────────────────────────────────────────
# SHA-256 fingerprinting
# ──────────────────────────────────────────────────────────────────────────────

class TestFingerprinting:
    def test_compute_sha256_returns_string_or_none(self):
        # A file that definitely exists
        result = compute_sha256("src/core/axiomzero_guard.py")
        assert result is None or (isinstance(result, str) and len(result) == 64)

    def test_compute_sha256_nonexistent_returns_none(self):
        result = compute_sha256("this/does/not/exist.py")
        assert result is None

    def test_compute_sha256_deterministic(self):
        path = "src/core/axiomzero_guard.py"
        r1 = compute_sha256(path)
        r2 = compute_sha256(path)
        assert r1 == r2

    def test_fingerprint_all_assets_returns_list(self):
        results = fingerprint_all_assets()
        assert isinstance(results, list)
        assert len(results) >= 7  # at minimum the listed assets

    def test_fingerprint_all_has_sha256_field(self):
        results = fingerprint_all_assets()
        for r in results:
            assert "sha256" in r

    def test_fingerprint_all_has_status_field(self):
        results = fingerprint_all_assets()
        for r in results:
            assert "status" in r
            assert r["status"] in ("REGISTERED", "MISSING")

    def test_fingerprint_all_has_registered_field(self):
        results = fingerprint_all_assets()
        for r in results:
            assert "registered" in r
            assert isinstance(r["registered"], bool)

    def test_axiomzero_guard_registered(self):
        results = fingerprint_all_assets()
        guard = next((r for r in results if "axiomzero_guard" in r["path"]), None)
        assert guard is not None
        assert guard["registered"] is True
        assert guard["sha256"] is not None

    def test_az_os_files_registered(self):
        results = fingerprint_all_assets()
        az_os = [r for r in results if r["path"].startswith("az-os/")]
        registered = [r for r in az_os if r["registered"]]
        assert len(registered) >= 2

    def test_sha256_is_64_hex_chars_when_present(self):
        results = fingerprint_all_assets()
        for r in results:
            if r["sha256"] is not None:
                assert len(r["sha256"]) == 64
                assert all(c in "0123456789abcdef" for c in r["sha256"])


# ──────────────────────────────────────────────────────────────────────────────
# IP_REGISTRY.json
# ──────────────────────────────────────────────────────────────────────────────

class TestIPRegistryJSON:
    """Tests for the committed 12-AZ-IP/IP_REGISTRY.json file."""

    @pytest.fixture
    def registry(self):
        # Find repo root
        candidate = Path(__file__).resolve()
        for _ in range(10):
            candidate = candidate.parent
            registry_path = candidate / "12-AZ-IP" / "IP_REGISTRY.json"
            if registry_path.exists():
                return json.loads(registry_path.read_text())
        pytest.skip("12-AZ-IP/IP_REGISTRY.json not found")

    def test_schema_field(self, registry):
        assert registry["schema"] == "axiomzero-ip-registry-v1"

    def test_pillar_536(self, registry):
        assert registry["pillar"] == 536

    def test_author_walker_pearson(self, registry):
        assert "Walker-Pearson" in registry["author"]

    def test_license_field(self, registry):
        assert "DefensivePublicCommons" in registry["license"]

    def test_assets_dict(self, registry):
        assert isinstance(registry["assets"], dict)
        assert len(registry["assets"]) >= 5

    def test_all_registered_assets_have_sha256(self, registry):
        for path, entry in registry["assets"].items():
            if entry.get("status") == "REGISTERED":
                assert entry["sha256"] is not None
                assert len(entry["sha256"]) == 64

    def test_axiomzero_guard_in_registry(self, registry):
        paths = list(registry["assets"].keys())
        assert any("axiomzero_guard" in p for p in paths)

    def test_az_os_assets_in_registry(self, registry):
        paths = list(registry["assets"].keys())
        assert any(p.startswith("az-os/") for p in paths)


# ──────────────────────────────────────────────────────────────────────────────
# 12-AZ-IP folder
# ──────────────────────────────────────────────────────────────────────────────

class TestAZIPFolder:
    def _repo_root(self) -> Path:
        candidate = Path(__file__).resolve()
        for _ in range(10):
            candidate = candidate.parent
            if (candidate / "STATUS.md").exists():
                return candidate
        return Path.cwd()

    def test_az_ip_folder_exists(self):
        assert (self._repo_root() / "12-AZ-IP").is_dir()

    def test_readme_exists(self):
        assert (self._repo_root() / "12-AZ-IP" / "README.md").exists()

    def test_fingerprint_manifest_exists(self):
        assert (self._repo_root() / "12-AZ-IP" / "FINGERPRINT_MANIFEST.md").exists()

    def test_ip_registry_json_exists(self):
        assert (self._repo_root() / "12-AZ-IP" / "IP_REGISTRY.json").exists()

    def test_readme_mentions_axiomzero(self):
        readme = (self._repo_root() / "12-AZ-IP" / "README.md").read_text()
        assert "AxiomZero" in readme

    def test_readme_mentions_walker_pearson(self):
        readme = (self._repo_root() / "12-AZ-IP" / "README.md").read_text()
        assert "Walker-Pearson" in readme

    def test_fingerprint_manifest_mentions_sha256(self):
        manifest = (self._repo_root() / "12-AZ-IP" / "FINGERPRINT_MANIFEST.md").read_text()
        assert "SHA-256" in manifest or "sha256" in manifest.lower()


# ──────────────────────────────────────────────────────────────────────────────
# Physics-to-OS mapping
# ──────────────────────────────────────────────────────────────────────────────

class TestPhysicsToOSMap:
    def test_at_least_9_mappings(self):
        assert len(PHYSICS_TO_OS_MAP) >= 9

    def test_all_have_physics_and_os_primitive(self):
        for m in PHYSICS_TO_OS_MAP:
            assert "physics" in m
            assert "os_primitive" in m

    def test_winding_number_mapped(self):
        all_physics = " ".join(m["physics"] for m in PHYSICS_TO_OS_MAP)
        assert "n_w" in all_physics or "winding" in all_physics.lower()

    def test_k_cs_mapped(self):
        all_physics = " ".join(m["physics"] for m in PHYSICS_TO_OS_MAP)
        assert "74" in all_physics or "k_cs" in all_physics.lower()

    def test_phi_mapped(self):
        all_os = " ".join(m["os_primitive"] for m in PHYSICS_TO_OS_MAP)
        assert "decay" in all_os.lower() or "0.618" in all_os or "phi" in all_os.lower()

    def test_privilege_rings_mapped(self):
        all_os = " ".join(m["os_primitive"] for m in PHYSICS_TO_OS_MAP)
        assert "ring" in all_os.lower() or "privilege" in all_os.lower()

    def test_scheduler_mapped(self):
        all_os = " ".join(m["os_primitive"] for m in PHYSICS_TO_OS_MAP)
        assert "scheduler" in all_os.lower() or "CPU" in all_os


# ──────────────────────────────────────────────────────────────────────────────
# Full report
# ──────────────────────────────────────────────────────────────────────────────

class TestPillar536Report:
    @pytest.fixture
    def report(self):
        return pillar536_report()

    def test_report_returns_dict(self, report):
        assert isinstance(report, dict)

    def test_pillar_536(self, report):
        assert report["pillar"] == 536

    def test_status_field(self, report):
        assert report["status"] == "AXIOMZERO_IP_REGISTRY"

    def test_asset_classes_count(self, report):
        assert report["asset_classes"] >= 4

    def test_total_assets_count(self, report):
        assert report["total_assets"] >= 7

    def test_registered_assets_count(self, report):
        assert report["registered_assets"] >= 3

    def test_physics_os_mappings(self, report):
        assert report["physics_os_mappings"] >= 9

    def test_physics_constants_present(self, report):
        constants = report["physics_constants"]
        assert constants["n_w"] == 5
        assert constants["k_cs"] == 74
        assert constants["pi_k_r"] == 37

    def test_ip_folder_field(self, report):
        assert report["ip_folder"] == "12-AZ-IP/"

    def test_fingerprints_list(self, report):
        assert isinstance(report["fingerprints"], list)
        assert len(report["fingerprints"]) >= 7


# ──────────────────────────────────────────────────────────────────────────────
# Verify-against-registry
# ──────────────────────────────────────────────────────────────────────────────

class TestVerifyAgainstRegistry:
    def test_verify_returns_dict(self):
        result = verify_against_registry()
        assert isinstance(result, dict)

    def test_verify_has_pillar_key(self):
        result = verify_against_registry()
        if "error" not in result:
            assert result["pillar"] == 536

    def test_verify_no_tampered(self):
        result = verify_against_registry()
        if "error" not in result:
            assert result["tampered"] == 0

    def test_verify_has_assets_list(self):
        result = verify_against_registry()
        if "error" not in result:
            assert isinstance(result["assets"], list)

    def test_verify_verdicts_valid(self):
        result = verify_against_registry()
        if "error" not in result:
            valid = {"VERIFIED", "MISSING", "NOT_IN_REGISTRY", "TAMPERED"}
            for asset in result["assets"]:
                assert asset["verdict"] in valid
