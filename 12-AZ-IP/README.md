# 12-AZ-IP — AxiomZero Intellectual Property Registry

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

## What Is AxiomZero IP?

**AxiomZero** is the intellectual property name for the full Unitary Manifold
technology stack — comprising the 5D physics framework, the AxiomZero Operating
System, interactive calculators, development tools, and all derived artefacts.
This folder contains the machine-readable IP registry, SHA-256 fingerprint manifest,
and provenance declarations for all AxiomZero assets, organized by category.

---

## IP Categories

| Subfolder | Asset class | Description |
|-----------|-------------|-------------|
| [`apps/`](apps/README.md) | **Applications** | Android client, web dashboards, AxiomZero full-stack app, EIGE governance app, UM-SOS frontend |
| [`engines/`](engines/README.md) | **Physics & AI Engines** | Walker-Pearson integrator, KK metric engine, CMB engine, birefringence engine, FTUM engine, holographic engine, cognitive AI engine (14 engines total) |
| [`os/`](os/README.md) | **Operating Systems** | AZ-OS (cognitive Python OS), AZ-KERNEL (Rust bare-metal UEFI), UM-SOS (Scientific OS), AxiomZero full-stack environment |
| [`tools/`](tools/README.md) | **Development Tools** | Lean4/Z3 formal verification bridges, audit tools, JAX/W&B integrations, SLSA provenance, CI/CD suite, MCP server, RAG/Copilot extension (13 tools total) |
| [`calculators/`](calculators/README.md) | **Interactive Calculators** | KK Mass Calculator, Birefringence Predictor, ToE Dashboard, CMB Parameters, DESI Tracker, Lean4 Progress, Pentad Simulator, 5D Explorer, HILS Interface (9 calculators total) |

---

## Assets Pending Integration from `wuzbak/Private`

The repository `wuzbak/Private` contains additional apps, engines, and OS assets.
To integrate them:
1. Grant access to the repository
2. Copy source files into the relevant subfolder (`apps/`, `engines/`, `os/`, `tools/`, `calculators/`)
3. Register each asset in `IP_REGISTRY.json` with SHA-256 fingerprint and description
4. Update `FINGERPRINT_MANIFEST.md`

---

## Scope Summary

| Asset class | Description |
|-------------|-------------|
| **Physics framework** | 5D Kaluza-Klein metric ansatz, 590 pillars, ToE derivation chain |
| **AxiomZero OS (AZ-OS)** | Python cognitive layer — 7-manager × 5-sub-agent AI network |
| **AZ-KERNEL** | Rust no_std UEFI bare-metal kernel, physics-derived primitives |
| **UM-SOS** | 7-layer Unitary Manifold Scientific Operating System |
| **Interactive calculators** | 9 browser-based physics calculators, zero installation required |
| **Development tools** | 13 tools: Lean4, Z3, SymPy, JAX, W&B, SLSA, CI/CD, MCP, RAG |
| **Applications** | Android client, web dashboards, governance apps |
| **Test infrastructure** | 49,850+ passing tests, CI/CD, SLSA provenance |
| **Outreach corpus** | Substack posts, monograph, arXiv preprint, governance docs |

---

## Authorship

**Primary author / IP owner:** ThomasCory Walker-Pearson (2026)

All work produced in this repository was created under a documented human-AI
collaboration under the HILS (Human-in-the-Loop Systems) framework:

- **Scientific direction, theory, and judgment:** ThomasCory Walker-Pearson
- **Code architecture, test suites, document engineering:** GitHub Copilot (AI)

The legal copyright is carried by the
`# Copyright (C) 2026  ThomasCory Walker-Pearson` SPDX header at the top of
every `.py` file. This authorship declaration is authoritative.

---

## Files in This Folder

| File / Folder | Purpose |
|---------------|---------|
| `README.md` | This file — overview, categories, and authorship |
| `FINGERPRINT_MANIFEST.md` | Human-readable SHA-256 fingerprints of key IP assets |
| `IP_REGISTRY.json` | Machine-readable IP provenance registry (Pillar 536) |
| `apps/` | Application IP registry — Android, web dashboards, EIGE |
| `engines/` | Physics & AI engine IP registry — 14 registered engines |
| `os/` | Operating system IP registry — AZ-OS, AZ-KERNEL, UM-SOS |
| `tools/` | Development tool IP registry — 13 registered tools |
| `calculators/` | Interactive calculator IP registry — 9 registered calculators |

---

## License

All AxiomZero IP is irrevocably dedicated to the public domain under the
**Defensive Public Commons License v1.0 (2026)**. Commercial patents on the
Walker-Pearson field equations, AxiomZero OS kernel architecture, or FTUM
operator are explicitly prohibited. Attribution is requested but not legally
required.

Preferred citation:

```
Walker-Pearson, T. (2026). The Unitary Manifold: A 5D Gauge Geometry of
Emergent Irreversibility (v18.0). Zenodo.
https://doi.org/10.5281/zenodo.19584531
```

---

## Pillar 536 — AXIOMZERO_IP_REGISTRY

Pillar 536 is the formal machine-readable registry of all AxiomZero IP assets,
authored by ThomasCory Walker-Pearson and fingerprinted at commit time. The
registry is implemented in `src/core/pillar536_axiomzero_ip_registry.py` and
tested in `tests/test_pillar536_axiomzero_ip_registry.py`.

The SHA-256 fingerprints in `IP_REGISTRY.json` and `FINGERPRINT_MANIFEST.md`
constitute a tamper-evident provenance record. Any modification to a registered
asset will produce a different fingerprint and is detectable.

---

*AxiomZero IP Registry v1.0 — 2026-06-15*
