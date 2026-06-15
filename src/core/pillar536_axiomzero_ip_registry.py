# Copyright (C) 2026  AxiomZero Technologies & Consulting, SPC
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 536 — AXIOMZERO_IP_REGISTRY.

══════════════════════════════════════════════════════════════════════════════
STATUS: AXIOMZERO_IP_REGISTRY
══════════════════════════════════════════════════════════════════════════════

PURPOSE
══════════════════════════════════════════════════════════════════════════════

Pillar 536 formally registers and fingerprints the complete AxiomZero
intellectual property (IP) stack as a machine-readable, tamper-evident
provenance record within the Unitary Manifold framework.

AxiomZero IP comprises:
  1. The AxiomZero Operating System (AZ-OS) — Python 3.12 cognitive layer
     implementing a 7-manager × 5-sub-agent AI network whose architecture
     is derived directly from the 5D Kaluza-Klein metric ansatz.
  2. The AZ-KERNEL — a Rust no_std / UEFI bare-metal kernel for x86-64 and
     ARM64 whose every primitive (scheduler, IPC, memory management, security
     descriptor) is a direct geometric derivation from the 5D KK constants
     (n_w = 5, k_cs = 74, φ⁻¹ = 0.618, πkR = 37).
  3. The AxiomZero Guard (src/core/axiomzero_guard.py) — the runtime audit
     module that enforces the Zero-Parameter status of the Unitary Manifold
     by scanning derivation-path sources for forbidden Standard Model seeds.
  4. All supporting infrastructure: test suites, CI/CD, SLSA provenance,
     Substack outreach corpus, arXiv preprint, governance documentation.

FINGERPRINTING METHODOLOGY
══════════════════════════════════════════════════════════════════════════════

Each registered asset receives a SHA-256 fingerprint computed from its exact
byte content at registration time (2026-06-15). The registry is committed to
the repository under 12-AZ-IP/IP_REGISTRY.json. Any subsequent modification
to a registered asset changes its fingerprint and is detectable by any
downstream consumer who recomputes the hash.

The registry schema is 'axiomzero-ip-registry-v1'. It is machine-readable
(JSON), human-readable (12-AZ-IP/FINGERPRINT_MANIFEST.md), and anchored
to this pillar.

AUTHORSHIP
══════════════════════════════════════════════════════════════════════════════

Primary author / IP owner: ThomasCory Walker-Pearson (2026)
Code architecture, test suites, document engineering: GitHub Copilot (AI)

All assets were produced under the HILS (Human-in-the-Loop Systems) framework
documented in 5-GOVERNANCE/co-emergence/. Scientific direction and judgment:
ThomasCory Walker-Pearson. Code and document synthesis: GitHub Copilot.

PHYSICS-TO-OS MAPPING (AZ-OS / AZ-KERNEL)
══════════════════════════════════════════════════════════════════════════════

  Physics concept              │ OS primitive
  ─────────────────────────────┼────────────────────────────────────────
  Fiber bundle (5 KK dims)     │ 5 privilege rings (KK levels 0–4)
  Winding number n_w = 5       │ 5 interrupt priority rings
  k_cs = 74 = 5² + 7²         │ 74 pages/compactification domain
  Geodesic equations           │ CPU scheduler (process = spacetime point)
  φ-debt entropy (Pillar 16)   │ Memory reclamation + FS eviction
  Holographic boundary (P4)    │ IPC channel interface
  KK adjacency rule            │ IPC security: adjacent levels only
  Pentad clearance bits        │ Process security descriptor
  φ⁻¹ = 0.618                 │ Debt decay rate in MM and FS layers

OPEN FOLDER: 12-AZ-IP/
══════════════════════════════════════════════════════════════════════════════

  12-AZ-IP/README.md               — Overview and authorship
  12-AZ-IP/FINGERPRINT_MANIFEST.md — Human-readable SHA-256 manifest
  12-AZ-IP/IP_REGISTRY.json        — Machine-readable registry (Pillar 536)

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, document engineering, and synthesis:
GitHub Copilot (AI).
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ──────────────────────────────────────────────────────────────────────────────
# Pillar metadata
# ──────────────────────────────────────────────────────────────────────────────

PILLAR_NUMBER: int = 536
PILLAR_STATUS: str = "AXIOMZERO_IP_REGISTRY"
PILLAR_TITLE: str = "AxiomZero IP Registry — Fingerprinted Provenance Record"
PILLAR_DATE: str = "2026-06-15"
PILLAR_AUTHOR: str = "ThomasCory Walker-Pearson"

# ──────────────────────────────────────────────────────────────────────────────
# AxiomZero physics constants (shared with AZ-OS / AZ-KERNEL)
# ──────────────────────────────────────────────────────────────────────────────

WINDING_NUMBER: int = 5            # n_w; KK winding number → 5 privilege rings
K_CS: int = 74                     # k_cs = 5² + 7²; pages per KK domain
PI_K_R: int = 37                   # πkR = 37; radion canonical geometry
PHI_INVERSE: float = 0.6180339887  # φ⁻¹; debt decay rate
N_MANAGERS: int = 7                # cognitive-layer managers = WINDING × braided pair
N_SUB_AGENTS: int = 5             # sub-agents per manager = n_w

# ──────────────────────────────────────────────────────────────────────────────
# Registered IP assets
# ──────────────────────────────────────────────────────────────────────────────

IP_ASSET_CLASSES: List[Dict] = [
    {
        "class": "AZ-OS",
        "description": "AxiomZero Cognitive Operating Layer",
        "assets": [
            {
                "path": "az-os/agent_core.py",
                "description": "7-manager × 5-sub-agent AI network core",
                "layer": "cognitive",
            },
            {
                "path": "az-os/hils.py",
                "description": "HILS framework — Human-in-the-Loop Systems",
                "layer": "cognitive",
            },
            {
                "path": "az-os/state.py",
                "description": "Shared state machine — kernel-cognitive bridge",
                "layer": "cognitive",
            },
            {
                "path": "11-AZ-OS/README.md",
                "description": "AxiomZero OS top-level documentation",
                "layer": "documentation",
            },
        ],
    },
    {
        "class": "AZ-KERNEL",
        "description": "AxiomZero Bare-Metal Rust Kernel",
        "assets": [
            {
                "path": "az-kernel/Cargo.toml",
                "description": "Rust no_std UEFI kernel manifest",
                "layer": "kernel",
            },
            {
                "path": "az-kernel/rust-toolchain.toml",
                "description": "Deterministic toolchain pin",
                "layer": "kernel",
            },
        ],
    },
    {
        "class": "AXIOMZERO_GUARD",
        "description": "Zero-Parameter Status Enforcement",
        "assets": [
            {
                "path": "src/core/axiomzero_guard.py",
                "description": "SM-seed audit — enforces AxiomZero derivation integrity",
                "layer": "physics",
            },
        ],
    },
    {
        "class": "IP_REGISTRY",
        "description": "This Pillar 536 Registration Artefacts",
        "assets": [
            {
                "path": "12-AZ-IP/README.md",
                "description": "AxiomZero IP folder overview",
                "layer": "provenance",
            },
            {
                "path": "12-AZ-IP/FINGERPRINT_MANIFEST.md",
                "description": "Human-readable SHA-256 manifest",
                "layer": "provenance",
            },
            {
                "path": "12-AZ-IP/IP_REGISTRY.json",
                "description": "Machine-readable IP registry",
                "layer": "provenance",
            },
        ],
    },
]

# ──────────────────────────────────────────────────────────────────────────────
# Fingerprinting functions
# ──────────────────────────────────────────────────────────────────────────────

_REPO_ROOT: Optional[Path] = None


def _find_repo_root() -> Path:
    """Locate repository root by searching upward for STATUS.md."""
    global _REPO_ROOT
    if _REPO_ROOT is not None:
        return _REPO_ROOT
    candidate = Path(__file__).resolve()
    for _ in range(10):
        candidate = candidate.parent
        if (candidate / "STATUS.md").exists():
            _REPO_ROOT = candidate
            return _REPO_ROOT
    # Fallback: current working directory
    _REPO_ROOT = Path.cwd()
    return _REPO_ROOT


def compute_sha256(path: str) -> Optional[str]:
    """Return SHA-256 hex digest of file, or None if the file does not exist."""
    full = _find_repo_root() / path
    if not full.exists():
        return None
    return hashlib.sha256(full.read_bytes()).hexdigest()


def fingerprint_asset(asset: Dict) -> Dict:
    """Compute fingerprint for a single asset dict."""
    sha = compute_sha256(asset["path"])
    return {
        **asset,
        "sha256": sha,
        "registered": sha is not None,
        "status": "REGISTERED" if sha is not None else "MISSING",
    }


def fingerprint_all_assets() -> List[Dict]:
    """Return all registered assets with SHA-256 fingerprints."""
    result: List[Dict] = []
    for cls in IP_ASSET_CLASSES:
        for asset in cls["assets"]:
            fp = fingerprint_asset(asset)
            fp["class"] = cls["class"]
            result.append(fp)
    return result


def verify_against_registry(registry_path: str = "12-AZ-IP/IP_REGISTRY.json") -> Dict:
    """Compare live fingerprints against the committed IP_REGISTRY.json.

    Returns a verification report with per-asset status.
    """
    full_registry = _find_repo_root() / registry_path
    if not full_registry.exists():
        return {"error": f"Registry not found: {registry_path}", "verified": False}

    committed: Dict = json.loads(full_registry.read_text())
    committed_assets: Dict = committed.get("assets", {})

    live = fingerprint_all_assets()
    report: Dict = {
        "pillar": PILLAR_NUMBER,
        "registry_path": registry_path,
        "total": len(live),
        "verified": 0,
        "missing": 0,
        "tampered": 0,
        "assets": [],
    }

    for asset in live:
        path = asset["path"]
        live_sha = asset.get("sha256")
        committed_entry = committed_assets.get(path, {})
        committed_sha = committed_entry.get("sha256")

        if live_sha is None:
            verdict = "MISSING"
            report["missing"] += 1
        elif committed_sha is None:
            verdict = "NOT_IN_REGISTRY"
        elif live_sha == committed_sha:
            verdict = "VERIFIED"
            report["verified"] += 1
        else:
            verdict = "TAMPERED"
            report["tampered"] += 1

        report["assets"].append({
            "path": path,
            "verdict": verdict,
            "live_sha": live_sha,
            "committed_sha": committed_sha,
        })

    report["all_verified"] = (
        report["tampered"] == 0
        and report["missing"] == 0
        and report["verified"] > 0
    )
    return report


# ──────────────────────────────────────────────────────────────────────────────
# Physics-to-OS mapping table
# ──────────────────────────────────────────────────────────────────────────────

PHYSICS_TO_OS_MAP: List[Dict] = [
    {"physics": "Fiber bundle — 5 KK extra dimensions", "os_primitive": "5 privilege rings (KK levels 0–4)"},
    {"physics": f"Winding number n_w = {WINDING_NUMBER}", "os_primitive": f"{WINDING_NUMBER} interrupt priority rings"},
    {"physics": f"k_cs = {K_CS} = 5² + 7²", "os_primitive": f"{K_CS} pages per compactification domain"},
    {"physics": "Geodesic equations", "os_primitive": "CPU scheduler (process = point in metric space)"},
    {"physics": "φ-debt entropy (Pillar 16)", "os_primitive": "Memory reclamation + filesystem eviction"},
    {"physics": "Holographic boundary (Pillar 4)", "os_primitive": "IPC channel interface"},
    {"physics": "KK adjacency rule", "os_primitive": "IPC security: only adjacent levels may communicate"},
    {"physics": "Pentad clearance bits", "os_primitive": "Process security descriptor"},
    {"physics": f"φ⁻¹ = {PHI_INVERSE:.3f}", "os_primitive": "Debt decay rate in MM and FS layers"},
    {"physics": f"πkR = {PI_K_R}", "os_primitive": "Radion stability → kernel watchdog timeout period"},
    {"physics": f"{N_MANAGERS} braided winding pairs", "os_primitive": f"{N_MANAGERS} cognitive-layer managers"},
    {"physics": f"n_w = {N_SUB_AGENTS} (sub-fibration)", "os_primitive": f"{N_SUB_AGENTS} sub-agents per manager"},
]


# ──────────────────────────────────────────────────────────────────────────────
# Report generator
# ──────────────────────────────────────────────────────────────────────────────

def pillar536_report() -> Dict:
    """Return the full Pillar 536 report."""
    fingerprints = fingerprint_all_assets()
    registered = [f for f in fingerprints if f["registered"]]
    missing = [f for f in fingerprints if not f["registered"]]

    return {
        "pillar": PILLAR_NUMBER,
        "status": PILLAR_STATUS,
        "title": PILLAR_TITLE,
        "date": PILLAR_DATE,
        "author": PILLAR_AUTHOR,
        "asset_classes": len(IP_ASSET_CLASSES),
        "total_assets": len(fingerprints),
        "registered_assets": len(registered),
        "missing_assets": len(missing),
        "physics_os_mappings": len(PHYSICS_TO_OS_MAP),
        "physics_constants": {
            "n_w": WINDING_NUMBER,
            "k_cs": K_CS,
            "pi_k_r": PI_K_R,
            "phi_inverse": PHI_INVERSE,
            "n_managers": N_MANAGERS,
            "n_sub_agents": N_SUB_AGENTS,
        },
        "fingerprints": fingerprints,
        "ip_folder": "12-AZ-IP/",
    }
