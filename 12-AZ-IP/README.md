# 12-AZ-IP — Canonical AxiomZero IP Folder

All scattered AxiomZero software assets have been copied into `/home/runner/work/Unitary-Manifold-/Unitary-Manifold-/12-AZ-IP/` and consolidated here as the canonical software registry. The shared library at `12-AZ-IP/lib/az_ip_common/` remains in place for cross-product imports.

## Product registry (15 canonical software products / surfaces)

| Product | Version | TRL | Port / Endpoint | Test Count | Description | Folder |
|---|---:|---|---|---:|---|---|
| Axiom OS Core Suite | 1.0.0 | TRL-5 | http://localhost:8000 | 162 | Canonical merge of AxiomZero full-stack plus az-os legacy agent/φ infrastructure. | [01-axiom-os/](01-axiom-os/) |
| AZ-KERNEL Rust Kernel | 0.1.0 | TRL-3 | UEFI / QEMU | 1 | Bare-metal Rust kernel with merged fuller az-kernel tree and legacy kk_channel IPC primitive. | [02-az-kernel/](02-az-kernel/) |
| EIGE Governance Engine | 21.0.0 | TRL-7 | CLI / Docker / notebook | 449 | Deterministic election integrity and governance stack with full source, infra, schemas, and tests. | [03-eige/](03-eige/) |
| UM-SOS Scientific OS | 15.8 | TRL-6 | /api/v1/* | 1 | Seven-layer scientific operating system with backend, frontend, DAG explorer, and preregistration registry. | [04-um-sos/](04-um-sos/) |
| UOS Kernel Prototype | 0.1 | TRL-3 | Python library | 566 | Geometric OS prototype copied from the Pentad with dedicated UOS regression tests. | [05-uos-kernel/](05-uos-kernel/) |
| Omega Synthesis Engine | 20.1 | TRL-5 | Python library | 170 | Universal mechanics calculator spanning cosmology, particle physics, HILS, and falsifiers. | [06-omega-synthesis/](06-omega-synthesis/) |
| Holon Zero Engine | 1.0 | TRL-5 | Python library | 347 | Ground-state engine merged from holon-zero and holon_zero, including subpillars and repo-root tests. | [07-holon-zero/](07-holon-zero/) |
| AxiomZero REST API | 1.0.0 | TRL-4 | http://localhost:8000/api | 162 inherited | FastAPI service exposing orchestrator status, governance gates, and provenance endpoints. | [01-axiom-os/api/](01-axiom-os/api/) |
| AxiomZero Android Client | 1.0.0 | TRL-3 | Thin client → API | 162 inherited | Android/Termux client for mobile access to the Axiom OS API and dashboard workflows. | [01-axiom-os/android/](01-axiom-os/android/) |
| AxiomZero Web Dashboard | 1.0.0 | TRL-4 | http://localhost:8000 | 162 inherited | Browser dashboard for live manager status, HILS checkpoints, and system telemetry. | [01-axiom-os/ui/](01-axiom-os/ui/) |
| AxiomZero MCP Stack | 1.0.0 | TRL-4 | Filesystem / execution / browser MCP | 162 inherited | Merged MCP implementations preserving both AxiomZero server classes and az-os legacy classes. | [01-axiom-os/mcp/](01-axiom-os/mcp/) |
| AxiomZero Memory Stack | 1.0.0 | TRL-4 | SQLite / vector store | 162 inherited | Persistent state DB, vector store, and session audit trail for the canonical OS layer. | [01-axiom-os/memory/](01-axiom-os/memory/) |
| UM-SOS Frontend & Graph | 15.8 | TRL-5 | Static frontend / GitHub Pages | 1 inherited | Static frontend plus derivation graph assets extracted into the canonical UM-SOS folder. | [04-um-sos/frontend/](04-um-sos/frontend/) |
| AZ IP Common Library | 1.0.0 | TRL-6 | Python import | shared | Shared canonical helper library retained in place for all products under 12-AZ-IP/lib/az_ip_common/. | [lib/az_ip_common/](lib/az_ip_common/) |
| IP & Products Catalog | 2026-08-18 | TRL-7 | Registry docs | manifest-backed | Master registry surfaces, manifests, and catalog tooling for the consolidated canonical IP folder. | [tools/](tools/) |

## Canonical consolidated folders

- `01-axiom-os/` — merged `AxiomZero/` + `az-os/`
- `02-az-kernel/` — merged `az-kernel/` + `11-AZ-OS/ax-kernel/`
- `03-eige/` — copied from `EIGE/`
- `04-um-sos/` — copied from `10-UM-SOS/`
- `05-uos-kernel/` — copied from Pentad `UOS/` plus UOS tests
- `06-omega-synthesis/` — copied from Pentad `omega/`
- `07-holon-zero/` — merged `holon-zero/` + `holon_zero/` plus root Holon tests

## Shared assets retained

- `LICENSE-AGPL`
- `NOTICE`
- `IP_REGISTRY.json`
- `FINGERPRINT_MANIFEST.md`
- `lib/az_ip_common/`
- `tools/`
- `engines/`
- `calculators/`

Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.
Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).
