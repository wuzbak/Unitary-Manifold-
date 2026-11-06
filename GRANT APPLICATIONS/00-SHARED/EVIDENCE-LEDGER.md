# Shared Evidence Ledger

Use this ledger to keep application claims traceable. It records what repository evidence supports—and what it does not support. A citation in a grant narrative should identify a dated public source or a repository path, and the PI should approve its use.

| Candidate claim | Current evidence | Safe wording | Not established; do not claim |
|---|---|---|---|
| Applicant is AxiomZero Technologies & Consulting, SPC, a Washington SPC based in Duvall | `docs/policy/AXIOMZERO_SPC.md` §§1–2; `AXIOMZERO_SPC.md` | “A Washington State Social Purpose Corporation based in Duvall, Washington” | Good standing, SAM.gov registration, UEI, tax status, ownership percentages, U.S. citizenship/residency of owners, employee count, or SBIR eligibility |
| AxiomZero has no customers as of 2026-11-06 | Founder statement in the current grant-planning conversation | “The founder confirms that the company has no customers as of November 6, 2026.” | Customer revenue, purchase intent, pilots, deployments, external adoption, or commitments |
| AxiomZero's primary activity is research and development of theoretical work and applications | Founder statement in the current grant-planning conversation; `README.md`; `STATUS.md`; `FALLIBILITY.md` | “A research-stage organization developing theoretical work and transparent software applications.” | External scientific validation, peer-reviewed acceptance, or proven application outcomes |
| Corporate purpose includes responsible AI, open science, public good, and environmental stewardship | `docs/policy/AXIOMZERO_SPC.md` §2 | Quote the filed purpose exactly after authorized corporate review | Impact already achieved, beneficiaries reached, or independently measured social outcomes |
| UM Geo Monitor is a research-stage software product using external hazard/environment data sources | `12-AZ-IP/README.md` product 21; `12-AZ-IP/21-geo-monitor/README.md` | “A prototype integrating selected public geophysical/environmental feeds” | NOAA endorsement, operational forecast, validated warning capability, climate-service performance, or customer adoption |
| EIGE and AxiomZero SGE have repository-reported test counts and maturity levels | `12-AZ-IP/README.md` products 03 and 22 | “The product registry lists …; tests cover repository-defined behavior” | Independent security audit, certification, vulnerability-free status, effectiveness against real attacks, or TRL independently assessed |
| AZ-SGE scope | Catalog product 22 advertises anti-malware, zero-day detection, IDS, and firewall capabilities; `12-AZ-IP/22-az-sge/README.md` says host enforcement is not implemented and the software analyzes inputs supplied to its API | Use the detailed product README's narrower description: local analysis and in-process policy evaluation; state clearly that host enforcement is not implemented | Host protection, threat detection effectiveness, operational SOC capability, malware prevention, or any unverified capability in the broader catalog description |
| PsiCat Navigator is a repository product with control-plane interfaces | `12-AZ-IP/README.md` product 20; product-specific docs | “An AI-assisted research/governance software prototype” | Autonomous reliability, external deployment, user adoption, or validated scientific conclusions |
| SDAM's detailed specification describes a research-stage Software-Defined Acoustic Modem | `12-AZ-IP/14-sdam/README.md`; conflicting catalog entry at `12-AZ-IP/README.md` product 14 and `12-AZ-IP/45-axiomzero-pc-suite/catalog/products.json` | “The product-specific specification describes an Android acoustic-communications prototype; the consolidated catalog uses a conflicting name/description that must be resolved before external use.” | Canonical product name, real-device acoustic performance, cross-device key provisioning, native build verification, security certification, or deployment readiness |
| AI governance / HILS work has a distinct framework and application layer | `5-GOVERNANCE/`, `5-GOVERNANCE/SEPARATION.md`, `12-AZ-IP/README.md` products 03 and 20 | Describe HILS/Unitary Pentad as an independent governance framework; describe EIGE as election-integrity/governance software and PsiCat as an AI-assisted research/governance tool | External institutional adoption, governance outcomes, independent certification, or proof from the physics framework |
| A public lane classifier provides a concrete governance-research artifact | `src/core/governance_lane_classifier.py:58–102,166–188`; `5-GOVERNANCE/PENTAD_LANE_AUDIT.md:42–61,112–125` | “The repository implements classification/escalation and lane-dependent quorum, dissent, and review rules that could be evaluated in a controlled study.” | Reliable real-world human oversight, downstream enforcement, deception detection, regulatory compliance, or measured reduction in AI risk |
| Quantum software tools exist in the portfolio | `12-AZ-IP/README.md` product 31; `src/quantum/` | “Early-stage quantum simulation/ansatz software, subject to independent benchmarking” | Quantum advantage, hardware performance, QEC capability, or a contribution to Riverlane Deltakit unless completed and evidenced |
| Repository has a large test suite | `9-INFRASTRUCTURE/TEST/README.md` historical regression record and current test artifacts | State exact count with the run date, exact command, and exclusions/skips | “All tests pass” based on a historical run; independent reproducibility; scientific validation |
| Project's software and research are open/public | `CITATION.cff`, root license/metadata, relevant product license files | State the actual license for each artifact; link the repository | “Public domain” for a product whose code is under AGPL or another license; every package shares one license |
| Company has a research-stage product portfolio | `docs/policy/AXIOMZERO_SPC.md` §4 and `12-AZ-IP/README.md` | “Under development; research-stage” | Production readiness, customers, contracts, revenue, jobs created, or commercial traction without records |

## Required additions before federal applications

Record the following in a private, controlled grant file—not in this public repository—then have the authorized representative confirm the public facts:

- Corporate good-standing evidence, formation documents, ownership/control and fully diluted cap table.
- U.S. owner citizenship/permanent-residency facts as required by the specific solicitation; affiliate and employee count.
- UEI and active SAM.gov registration; NSF/agency registrations and authorized representative.
- PI employment percentage and role; salary basis and availability.
- Current accounting records, indirect-cost treatment, and project cost model.
- If an SBIR/STTR is pursued: prospective-user discovery, market-size methodology, and a commercialization plan. AxiomZero has no customers; do not claim otherwise or treat prospects as customers.
- For research-first proposals: independent scientific reviewers, research collaborators, reproducibility protocol, and access to any required data/compute.
- For any SDAM-related proposal: resolve the catalog/specification naming conflict; restrict evaluation to consenting endpoints and authorized, non-sensitive lab work; do not claim acoustic containment or protected-system readiness.
- External contributor/adoption metrics for OSS ecosystem proposals.
- Independent security/scientific reviews and reproducible benchmark protocols.

## Source integrity

The program facts live in each opportunity brief. Recheck all live pages at the official funder link before applying. Third-party listings are leads only; they are not eligibility determinations or authoritative deadline evidence.

Older proposal drafts and capability statements are leads, not evidence that an award is currently open, an applicant is eligible, a capability is deployed, or a proposed outcome has been achieved. Reconcile them with current corporate records, official notices, and product-specific implementation limits. Keep confidential source material out of this public folder; use a public claim only when its support is independently available in public evidence.
