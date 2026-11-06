# Shared Evidence Ledger

Use this ledger to keep application claims traceable. It records what repository evidence supports—and what it does not support. A citation in a grant narrative should identify a dated public source or a repository path, and the PI should approve its use.

| Candidate claim | Current evidence | Safe wording | Not established; do not claim |
|---|---|---|---|
| Applicant is AxiomZero Technologies & Consulting, SPC, a Washington SPC based in Duvall | `docs/policy/AXIOMZERO_SPC.md` §§1–2; `AXIOMZERO_SPC.md` | “A Washington State Social Purpose Corporation based in Duvall, Washington” | Good standing, SAM.gov registration, UEI, tax status, ownership percentages, U.S. citizenship/residency of owners, employee count, or SBIR eligibility |
| Corporate purpose includes responsible AI, open science, public good, and environmental stewardship | `docs/policy/AXIOMZERO_SPC.md` §2 | Quote the filed purpose exactly after authorized corporate review | Impact already achieved, beneficiaries reached, or independently measured social outcomes |
| UM Geo Monitor is a research-stage software product using external hazard/environment data sources | `12-AZ-IP/README.md` product 21; `12-AZ-IP/21-geo-monitor/README.md` | “A prototype integrating selected public geophysical/environmental feeds” | NOAA endorsement, operational forecast, validated warning capability, climate-service performance, or customer adoption |
| EIGE and AxiomZero SGE have repository-reported test counts and maturity levels | `12-AZ-IP/README.md` products 03 and 22 | “The product registry lists …; tests cover repository-defined behavior” | Independent security audit, certification, vulnerability-free status, effectiveness against real attacks, or TRL independently assessed |
| PsiCat Navigator is a repository product with control-plane interfaces | `12-AZ-IP/README.md` product 20; product-specific docs | “An AI-assisted research/governance software prototype” | Autonomous reliability, external deployment, user adoption, or validated scientific conclusions |
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
- Customer discovery notes, pilot interest/letters, market size methodology, and commercialization plan.
- External contributor/adoption metrics for OSS ecosystem proposals.
- Independent security/scientific reviews and reproducible benchmark protocols.

## Source integrity

The program facts live in each opportunity brief. Recheck all live pages at the official funder link before applying. Third-party listings are leads only; they are not eligibility determinations or authoritative deadline evidence.
