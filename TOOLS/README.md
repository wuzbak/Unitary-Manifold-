# TOOLS — Calculators, Verification Entrypoints, and Maintenance Utilities

This folder is the navigation hub for executable tools, calculators, notebooks, and repository-maintenance utilities.

Some stable entrypoints intentionally remain at the repository root for compatibility with existing docs, badges, notebooks, and external users. They are indexed here so humans and AI agents can find them quickly without breaking established commands.

## Fast verification

| Tool | Path | Use |
|------|------|-----|
| Formal verification script | [`../VERIFY.py`](../VERIFY.py) | Fast observable consistency check used by the README quick start. |
| Isolated proof verifier | [`../proof/VERIFY.py`](../proof/VERIFY.py) | Minimal proof-surface copy for formal review. |
| Algebra proof test/script | [`../ALGEBRA_PROOF.py`](../ALGEBRA_PROOF.py) | Root compatibility entrypoint included by pytest discovery. |
| Proof-surface algebra script | [`../proof/ALGEBRA_PROOF.py`](../proof/ALGEBRA_PROOF.py) | Isolated proof-surface algebra checks. |

## Audit and maintenance tools

| Tool | Path | Use |
|------|------|-----|
| Audit tools | [`../AUDIT_TOOLS.py`](../AUDIT_TOOLS.py) | Repository audit helper retained at root for compatibility. |
| Link checker | [`audit/check_internal_links.py`](audit/check_internal_links.py) | Checks Markdown file links for missing internal targets. |
| Large-directory guard | [`checks/check_large_directories.py`](checks/check_large_directories.py) | Enforces per-directory tracked-entry limits to prevent GitHub 1,000-entry UI truncation risk from growing. |
| Number updater | [`../9-INFRASTRUCTURE/update_numbers.sh`](../9-INFRASTRUCTURE/update_numbers.sh) | Version/count update utility. |
| Archive creator | [`../9-INFRASTRUCTURE/scripts/create_archive.py`](../9-INFRASTRUCTURE/scripts/create_archive.py) | Archive helper script. |

## Calculators and pillar tools

| Tool area | Path | Use |
|-----------|------|-----|
| PCCRE calculator | [`../src/core/pillar242_planetary_coherence_cascade_resilience_engine.py`](../src/core/pillar242_planetary_coherence_cascade_resilience_engine.py) | Pillar 242 executable physics module (calculator docs integrated in module). |
| USIVF calculator | [`../src/core/pillar243_unified_scientific_interoperability_validation_fabric.py`](../src/core/pillar243_unified_scientific_interoperability_validation_fabric.py) | Pillar 243 executable physics module (calculator docs integrated in module). |
| Core Python calculators | [`../src/core/`](../src/core/) | Main executable physics/audit modules. |
| Omega synthesis | [`../5-GOVERNANCE/Unitary Pentad/omega/omega_synthesis.py`](../5-GOVERNANCE/Unitary%20Pentad/omega/omega_synthesis.py) | Governance/summary calculator surface. |

## Notebooks and demos

| Tool | Path | Use |
|------|------|-----|
| Root demo notebook | [`../demo.ipynb`](../demo.ipynb) | Fast interactive repository demonstration. |
| Infrastructure notebooks | [`../9-INFRASTRUCTURE/notebooks/`](../9-INFRASTRUCTURE/notebooks/) | Quickstart, holographic boundary, and FTUM notebooks. |

## Rule

If a tool is a public or tested entrypoint, keep a compatibility path or wrapper when moving it. Do not move root verification scripts without updating README, AGENTS, tests, notebooks, and external-facing docs in the same PR.
