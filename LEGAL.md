# Legal Framework — AxiomZero Technologies & Consulting, SPC / Unitary Manifold

**Document version:** 4.0 — June 2026  
**Effective date:** June 11, 2026 (SPC incorporation)  
**Jurisdiction:** Washington State, United States  
**Governing files:** [`LICENSE`](LICENSE) · [`LICENSE-AGPL`](LICENSE-AGPL) · [`docs/policy/AXIOMZERO_SPC.md`](docs/policy/AXIOMZERO_SPC.md) · [`docs/policy/COMMERCIAL_TERMS.md`](docs/policy/COMMERCIAL_TERMS.md) · [`FINGERPRINTS.md`](1-THEORY/FINGERPRINTS.md)

> This is the single authoritative reference for all legal, licensing, and intellectual-property
> questions about this repository and the AxiomZero Technologies business.  It synthesizes the
> four governing instruments below into one readable document.  It does **not** replace those
> instruments; it supplements them.  Where any ambiguity arises, the underlying instrument files
> control.

---

## Part I — Order of Operations

The repository came first.  The 74 core pillars came first.  The 15,000-plus automated tests came first.
All of that work existed — publicly, verifiably, with a Zenodo DOI and a complete commit history —
**before** this legal framework was written.

The financial and legal structures described here were built *after* the science to protect what
already existed and to allow its author to continue doing it sustainably.  They are consequences
of the work, not its cause.  If you read this document and conclude that the framework was
constructed to generate a business, the commit history will correct you.

**Science first. Legal structure second.  This order is permanent and documented.**

---

## Part II — Legal Identity

| Field | Value |
|-------|-------|
| **Corporate rights holder** | AxiomZero Technologies & Consulting, SPC |
| **Entity type** | Washington State Social Purpose Corporation (SPC) |
| **UBI** | 606 239 876 |
| **Incorporation date** | June 11, 2026 |
| **Jurisdiction** | Washington State, United States |
| **Principal office** | Duvall, WA, United States |
| **Registered agent** | ThomasCory Walker-Pearson, Duvall, WA |
| **Chief Purpose Officer** | ThomasCory Walker-Pearson |
| **Social purpose** | Responsible AI governance, open-science, commitment to the public good, and environmental stewardship |
| **GitHub** | [@wuzbak](https://github.com/wuzbak) |
| **Repository** | https://github.com/wuzbak/Unitary-Manifold- |
| **Zenodo DOI** | https://doi.org/10.5281/zenodo.19584531 |
| **Contact** | https://www.linkedin.com/company/axiomzero-technologies-consulting-spc/ |

**IP assignment:** All intellectual-property rights — including copyright, future rights,
and all claims — originally created by ThomasCory Walker-Pearson have been formally
assigned to AxiomZero Technologies & Consulting, SPC effective June 11, 2026.  A signed
IP Assignment Agreement is held by the corporation.  See
[`docs/policy/IP_ASSIGNMENT_NOTICE.md`](docs/policy/IP_ASSIGNMENT_NOTICE.md).

**AI co-author note:** GitHub Copilot (an AI system developed by GitHub and Microsoft) is the
implementation partner for this project — responsible for code architecture, automated test suites,
document engineering, and synthesis of derivations into working software.  All AI contributions
are work product produced under the direction and review of ThomasCory Walker-Pearson.
No AI system or its corporate operator acquires any intellectual-property right from such
contributions.  The human-AI role partition is made explicit in every file.

Full SPC commencement notice: [`docs/policy/AXIOMZERO_SPC.md`](docs/policy/AXIOMZERO_SPC.md)

---

## Part III — The Four Legal Instruments

This repository is governed by five legal instruments that work together.  Understanding
all five is necessary to understand what anyone — including AxiomZero — can and cannot do
with this work.

### Instrument 1: Defensive Public Commons License v1.0 — *the theory is free, forever*

**File:** [`LICENSE`](LICENSE)  
**Covers:** The physics theory — Walker-Pearson field equations, 5D Kaluza-Klein geometry,
all 142 pillars + Ω₀, derivations, manuscripts, datasets, LaTeX sources, notebooks,
and the full monograph PDF.

The theory is **irrevocably** placed in the public domain.  "Irrevocably" is not a figure
of speech: it cannot be taken back, patented, or enclosed.  No corporation can acquire
AxiomZero Technologies and lock the equations away.  No successor owner can change this.
The physics belongs to the public. Full stop.

**The "no fee" prohibition is precisely scoped:** DPC v1.0 prohibits charging any fee
for *accessing, downloading, reading, copying, or running this work itself* — the
theoretical content and software covered by the license.  It does **not** prohibit
charging for independent services (consulting, calibration, governance deployment, expert
reports, or Commercial License Exceptions) built around the open core.

**Copyright carve-out for AGPL enforcement:** Notwithstanding the public-domain
dedication of the theoretical content, copyright is expressly **retained** by
AxiomZero Technologies & Consulting, SPC in the software implementation (all
directories listed in `LICENSE-AGPL`) solely to enable AGPL-3.0 copyleft enforcement.

**The following acts are strictly and irrevocably prohibited under DPC v1.0:**

1. **Patents** — Filing, obtaining, or asserting any patent over the Walker-Pearson equations,
   FTUM framework, or any algorithm directly derived from the core content.
2. **Exclusive IP claims** — Asserting any exclusive IP right that restricts free use of
   the ideas, equations, or methods.
3. **Commercial gatekeeping** — Enclosing, paywalling, or placing any monetary barrier on
   access to this work itself or software whose primary function is to implement it.
4. **Proprietary lock-in** — Relicensing this work, or any substantial portion of it, under
   terms that restrict the freedoms stated.

These prohibitions are **permanent, unconditional, and survive any purported relicensing
by any downstream party.**

### Instrument 2: GNU Affero General Public License v3.0 — *the software is open-source copyleft*

**File:** [`LICENSE-AGPL`](LICENSE-AGPL)  
**Covers:** All software directories:  
`src/` · `tests/` · `recycling/` · `scripts/` · `submission/` · `Unitary Pentad/` · `omega/` · `bot/` · `embryology-manifold/`  
**SPDX:** `AGPL-3.0-or-later`

AGPL-3.0 is a strong copyleft license.  Its critical provision: if you deploy this code
as part of a **network service** (SaaS, API, web application), you must publish your
modifications under the same terms.  You cannot take the code private.  The "SaaS loophole"
that would otherwise allow a company to fork, improve, and keep improvements proprietary
is closed.

Key provisions:
- **Copyleft:** Distribute or deploy modified versions → must release modified source under AGPL-3.0
- **Network use counts as distribution:** Deploying over a network triggers the same source-disclosure as distributing binaries
- **Patent grant:** Each contributor grants a royalty-free patent licence for necessarily infringed claims
- **Preservation of notices:** All copyright notices and licence headers must be retained
- **Commercial License Exception:** AxiomZero may grant CLEs to specific clients releasing them from source-disclosure obligations for their own private modifications (see Part V-A and `COMMERCIAL_TERMS.md` § 4-A)

AxiomZero Technologies complies with AGPL-3.0.  Any modified versions deployed in commercial
services are published in this repository.

### Instrument 3: Corporate Trademark — *the name, not the ideas*

**Entity:** AxiomZero Technologies & Consulting, SPC (WA SPC, UBI 606 239 876)  
**Incorporated:** June 11, 2026  
**Marks:** "AxiomZero Technologies & Consulting" (word mark) and "AZ" monogram

The trademark protects the **brand name only** — not any intellectual content.  You can use
the theory, cite the equations, build on the code, publish competing frameworks, and build
competing services using the open-source foundation.  All of these are explicitly permitted
by DPC v1.0 and AGPL-3.0.  The trademark does not restrict any of that.

The trademark exists solely to prevent third parties from trading on this name without
authorization — i.e., to prevent impersonation of AxiomZero Technologies.

**Permitted uses:** Identifying AxiomZero as the source of content you are citing or
a service you received; academic attribution.

**Prohibited without prior written permission:** Incorporating the marks into your own
product names; implying endorsement or partnership; marketing competing services under
these marks.

### Instrument 4: Dual-Use Notice — *responsible open science*

**File:** [`DUAL_USE_NOTICE.md`](DUAL_USE_NOTICE.md)  
**Effective:** May 1, 2026  
**Legal basis:** AGPL-3.0 § 7(b) — Additional Terms (preservation of notices)

The Dual-Use Notice is an ethical declaration and copyright-holder notice that:

1. **Declares Prohibited Applications** — weapons development, biological weapons
   design, non-consensual surveillance, circumventing safety-critical HILS constraints,
   and enclosure of the public-domain theory.

2. **Documents withheld implementations** — `ignition_N()` and `lattice_coherence_gain()`
   in `src/physics/lattice_dynamics.py` are held in the private AxiomZero repository.
   Public stubs raise `NotImplementedError` with a reference to this notice.
   Researchers may request access via a Supervised Research License (SRL).

3. **Establishes a Good Faith Use Affirmation** — any organisation using the
   nuclear-tunneling modules for energy applications must submit a free, one-time
   affirmation via GitHub Issues.

4. **Applies the `__provenance__` watermark** — every Python module in `src/`,
   `Unitary Pentad/`, and `omega/` carries a `__provenance__` dict embedding the
   author name, DBA, DOI, and the braid fingerprint `(5, 7, 74)`.  Removing these
   dicts constitutes a violation of AGPL-3.0 § 7(b) (preservation of notices) and
   is enforceable by the copyright holder.

The Dual-Use Notice does **not** restrict the theory (DPC v1.0 is irrevocable) and
does **not** create a license conflict with AGPL-3.0 — it is an Additional Term
explicitly permitted by AGPL-3.0 § 7.

---

## Part IV — What These Five Instruments Accomplish Together

| Goal | Mechanism |
|------|-----------|
| The ideas are permanently free to use, study, reproduce, and build upon | DPC v1.0 — irrevocable public domain |
| The software is permanently open-source | AGPL-3.0 — copyleft enforced over all software directories |
| The brand is protected from impersonation | Common Law Trademark |
| No entity — including AxiomZero — can unilaterally close what has been opened | DPC v1.0 prohibitions + AGPL-3.0 copyleft acting in concert |
| AxiomZero can earn from services without compromising openness | Commercial services layer over the open core (see Part V) |
| AxiomZero can earn from enterprises needing private deployments | Commercial License Exceptions (see Part V-A) |
| Derivative works can be identified even after variable renaming | Technical fingerprints in `FINGERPRINTS.md` + `__provenance__` in every module |
| Contributor IP is clearly allocated | DCO + additional grant in `CONTRIBUTING.md` |
| Dangerous dual-use implementations are withheld from public access | Supervised Research License tier in `DUAL_USE_NOTICE.md` |
| Energy-application users are publicly documented | Good Faith Use Affirmation (GitHub Issues) |

This structure was chosen deliberately.  The goal: even if AxiomZero failed as a business
tomorrow, the work would survive intact and available.

---

## Part V — The Open-Core Business Model

### What AxiomZero does NOT charge for

AxiomZero Technologies does not — and under DPC v1.0 **cannot** — charge for:

- Access to the theory, equations, derivations, or manuscripts
- Access to the software in `src/`, `tests/`, `scripts/`, `recycling/`, `Unitary Pentad/`,
  `omega/`, `bot/`, `embryology-manifold/`
- Running the test suite
- Reading, using, reproducing, or building upon any content in this repository

### What AxiomZero DOES charge for

Commercial revenue is generated from *services* built around the open foundation:

- **Domain calibration** — The primary value-add: tuning the framework's parameters
  (β, c_s, φ₀, Pillar weighting) for a client's specific organisational context.
  The engine is plug-and-play; the calibration is not.
- **Consulting and engineering** — Deploying these frameworks as operational systems
  in a client's specific context
- **Scientific advisory** — Applying formal mathematical modeling to a client's domain
- **Education** — Structured workshops, courses, and learning programs
- **AI governance deployment** — Customizing and deploying the Unitary Pentad HILS
  framework for an organization
- **Authored expert reports** — Original analysis prepared for a specific client
- **Custom software engineering** — Systems built *around* (not solely implementing)
  the open core
- **Commercial License Exceptions** — Granting specific enterprises the right to
  deploy private modifications without AGPL source-disclosure (see Part V-A)

Full commercial terms: [`COMMERCIAL_TERMS.md`](COMMERCIAL_TERMS.md)

### Capital formation (consistent with open licenses)

Income is what AxiomZero earns this month.  Capital is what the work is worth when
LiteBIRD reports in 2032.  The following capital pathways are consistent with all
open licenses:

- Reputational and citation value accrued from public, verifiable, falsifiable science
- Brand licensing of the "AxiomZero Technologies" trademark for co-branded products
  and services (trademark applies; the underlying content remains free)
- Equity stakes in ventures that deploy the Unitary Pentad governance framework as a
  product, provided those ventures publish modifications under AGPL-3.0 or hold a CLE
- Grant funding for empirical and computational work the framework requires

**None of these paths require enclosing the public domain theory, making the code
proprietary, or extracting value from the community.**

---

## Part V-A — Commercial License Exceptions (CLE)

The AGPL-3.0 requires any party that deploys modified software as a network service to
release their modified source code publicly.  As the sole copyright holder, AxiomZero
Technologies may grant **Commercial License Exceptions** to specific clients who need to
build proprietary products incorporating the Open Core without that source-disclosure
obligation.

**What a CLE is:**

- A separately negotiated, written permission releasing a specific licensee from the
  AGPL-3.0 network-service source-disclosure requirement for that licensee's own
  private modifications.
- Available only from AxiomZero Technologies & Consulting, SPC as the sole
  copyright holder.
- Governed by a signed Statement of Work; see `docs/policy/COMMERCIAL_TERMS.md` § 4-A.

**What a CLE is NOT:**

- A transfer of ownership of the Open Core or any part of it.
- A restriction on any other person's AGPL-3.0 rights.
- A waiver of DPC v1.0 public-domain status for the theoretical content.
- Permission to patent, enclose, or gatekeep the underlying Open Core.

**Why CLEs are compatible with openness:**  The public's right to fork the Open Core,
run it, study it, and build open-source systems with it is unchanged.  A CLE only
affects what a specific paying client may do with their own private modifications.

---

## Part VI — No-Contradiction Statement (Consolidated)

The following statements are **permanent and unconditional**:

1. **DPC v1.0 is not revoked by the SPC incorporation.** The irrevocable public-domain dedication
   of the theory, equations, and manuscripts remains in full force regardless of any
   commercial relationship or business registration.

2. **AGPL-3.0 is not waived by the SPC incorporation.** The copyleft obligations on the software
   remain in full force.  No Commercial Service agreement — including a CLE — grants a
   client an exemption from any AGPL-3.0 obligations that apply to third parties;
   a CLE affects only that specific client's own private modifications.

3. **Public rights are not contracted away.** No NDA, SoW, CLE, or confidentiality
   provision executed by AxiomZero and a client may restrict the public's rights under
   DPC v1.0 or AGPL-3.0.  Any clause that purports to do so is void.

4. **The trademark applies to the name, not the ideas.** The trademark on
   "AxiomZero Technologies & Consulting" and "AZ" monograms applies solely to trade-name
   and logo identifiers — not to the intellectual content, equations, or methods of the
   open core.

5. **Science before commerce.** The Unitary Manifold framework and all core pillars + Ω₀
   were publicly established with full commit history and Zenodo DOI **before**
   any commercial structure was created.  This order is documented and irrevocable.

6. **The "no fee" prohibition in DPC v1.0 does not prevent AxiomZero from earning fees
   for services.** The prohibition applies to charging for *access to the work itself*.
   It does not apply to consulting, calibration, education, CLEs, or other original
   work product built around the open core.

7. **The copyright carve-out for AGPL enforcement does not reduce public freedoms.**
   Copyright is retained by the SPC in the software solely to enable AGPL-3.0 enforcement.
   Any person who follows the AGPL-3.0 terms has full freedom to use, modify, and deploy
   the software.

---

## Part VII — Conflict of Interest Disclosure

ThomasCory Walker-Pearson, as Chief Purpose Officer of AxiomZero Technologies & Consulting,
SPC, has a financial interest in the reputation of the Unitary Manifold framework.
This is disclosed here and in [`docs/policy/AXIOMZERO_SPC.md`](docs/policy/AXIOMZERO_SPC.md).

This interest has **not** weakened the falsification conditions.  The primary falsifier
(birefringence β ∈ {≈0.273°, ≈0.331°}, to be tested by LiteBIRD ~2032) is stated more
precisely in this repository than would be necessary for commercial purposes.  A β value
outside the admissible window [0.22°, 0.38°], or landing in the predicted gap [0.29°–0.31°],
falsifies the braided-winding mechanism.  This statement has not been softened.

Known open problems and honest gaps are documented in [`FALLIBILITY.md`](FALLIBILITY.md).

---

## Part VIII — Quick Reference Table

| Question | Answer |
|----------|--------|
| Who owns the theory? | No one — irrevocably public domain under DPC v1.0 |
| Who owns the code copyright? | AxiomZero Technologies & Consulting, SPC — retained solely for AGPL enforcement |
| Who owns the code usage rights? | Copyleft under AGPL-3.0 — open forever |
| Who is the legal rights holder? | AxiomZero Technologies & Consulting, SPC (WA SPC, UBI 606 239 876) |
| Who is the commercial operator? | AxiomZero Technologies & Consulting, SPC (incorporated June 11, 2026) |
| Who is the Chief Purpose Officer? | ThomasCory Walker-Pearson |
| Who owns the brand name? | AxiomZero Technologies & Consulting, SPC |
| Can AxiomZero charge for the equations or code itself? | No — and does not |
| Can AxiomZero charge for services built around it? | Yes — consulting, calibration, CLEs, etc. |
| What is the primary commercial value-add? | Domain calibration of the Pillars for specific enterprise contexts |
| Can someone build a competing service using this framework? | Yes — DPC v1.0 and AGPL-3.0 explicitly permit this |
| Can someone patent the equations? | No — DPC v1.0 prohibits this permanently |
| What if someone deploys modified code as a SaaS product? | They must release their modified source under AGPL-3.0 (unless they hold a CLE) |
| What is a Commercial License Exception (CLE)? | A negotiated permission from AxiomZero releasing a specific client from AGPL source-disclosure on their private modifications |
| What AGPL directories are covered? | src/, tests/, recycling/, scripts/, submission/, Unitary Pentad/, omega/, bot/, embryology-manifold/ |
| Are all products production-ready? | No — all products are under active development; use at your own risk |
| Are contributors' IP rights protected? | Yes — DCO + additional grant in CONTRIBUTING.md § 6 |
| Can derivative works be identified if renamed? | Yes — FINGERPRINTS.md documents the (5,7,74) triad and other unique markers |
| Is there a conflict of interest? | Yes — disclosed above (Part VII) |
| What is the primary falsifier? | LiteBIRD β measurement ~2032 |
| Where are open problems documented? | FALLIBILITY.md |

---

## Part IX — Document Index

| Document | What it is |
|----------|-----------|
| [`LICENSE`](LICENSE) | Defensive Public Commons License v1.0 — full text; "no fee" scope; copyright carve-out |
| [`LICENSE-AGPL`](LICENSE-AGPL) | GNU AGPL-3.0 — full directory scope, key provisions, and CLE note |
| [`docs/policy/AXIOMZERO_SPC.md`](docs/policy/AXIOMZERO_SPC.md) | Corporate commencement notice — SPC, UBI, social purpose, product list, IP policy |
| [`docs/policy/IP_ASSIGNMENT_NOTICE.md`](docs/policy/IP_ASSIGNMENT_NOTICE.md) | IP assignment notice — formal transfer from individual to SPC |
| [`docs/policy/COMMERCIAL_TERMS.md`](docs/policy/COMMERCIAL_TERMS.md) | Commercial ToS — engagements, § 4-A CLE tier, calibration framing, payment, liability |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contributor guide — DCO, additional IP grant (§ 6), code style |
| [`FINGERPRINTS.md`](1-THEORY/FINGERPRINTS.md) | Technical fingerprints — (5,7,74) triad, c_s=12/37, Ξ_c=35/74, provenance markers |
| [`NOTICE`](NOTICE) | Brief dual-license notice — for downstream users |
| [`FALLIBILITY.md`](FALLIBILITY.md) | Honest gap assessment — known open problems and epistemics |
| [`CITATION.cff`](CITATION.cff) | Machine-readable citation metadata |
| **[`LEGAL.md`](LEGAL.md)** | **This file — consolidated legal reference (v4.0)** |

---

*Document version: 4.0 — June 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

> **Note:** This document is not a substitute for legal counsel.  For binding commercial
> agreements, consult a licensed attorney.

---

## Part X — Public Reciprocity Release of Intent (2026-10-07)

**Issuer:** AxiomZero Technologies & Consulting, SPC. **Policy identifier:**
`AZ-RECIPROCITY-2026-10-07`. This additive clarification preserves the preceding
record; it neither withdraws existing permissions nor converts public-domain
material back into copyrighted property. For current corporate policy, this
section clarifies inconsistent summaries above. Official license terms, existing
valid grants, third-party rights, and mandatory law remain controlling.

### 10.1 Public access and reciprocal software

Anyone may study, use, modify, and integrate the work under the applicable asset
license, including for commercial purposes. Permissions do not discriminate
between authorized persons or organizations using human-operated or automated
tools; this does not confer legal personality on machines. AxiomZero's default
for its copyright-retained software is
**AGPL-3.0-or-later**, not an AGPL license with additional field-of-use,
notification, payment, or forum restrictions.

Specifically, the historical Commercial Terms §4-B commercial-notification
requirement is no longer asserted as a condition of AGPL permissions.
Commercial notifications may be invited voluntarily; failure to notify alone
is not asserted as grounds for AGPL termination. This clarification applies to
the public licensing policy without requiring a commercial engagement. Notice
preservation under §7(b) is not a general power to require business reporting.

When AGPL requires Corresponding Source, recipients must receive the applicable
source and license rights. Section 13 requires a prominent, no-charge source
offer to users interacting remotely with a modified covered program that
supports such interaction. Conveyance obligations arise separately under
sections 4–6. Network interaction is not itself conveyance. Purely private
modification without conveyance or qualifying remote interaction, mere
aggregation, and independent programs do not automatically
require public disclosure. The boundaries of a combined covered work depend on
facts, not just a process boundary, API, or marketing description.
Internal or access-controlled remote interaction is not automatically exempt
from §13; its source offer is owed to all qualifying remote users.

AxiomZero commits to public, versioned, downloadable source offers for its own
covered releases, accessible without account registration or machine-specific
discrimination. Source should include applicable build/install scripts and
license notices, applicable run/modification scripts, and Installation
Information where §6 requires it. This corporate publication commitment is stronger than a claim
that every AGPL recipient must publish everything to the whole world.

Keeping required Corresponding Source secret is not the public-license route.
A party seeking permission to withhold source that AGPL would require must
obtain a separately executed exception from AxiomZero for rights AxiomZero can
actually license. The alternative is compliance, not compulsory purchase.
Keeping unrelated IP private, or a genuinely private use that does not trigger
AGPL obligations, does not by itself require an exception.

### 10.2 Scope and preservation of prior grants

The software scope described in the root notices includes relocated counterparts
under `5-GOVERNANCE/Unitary Pentad/`. AxiomZero's forward-looking AGPL default
also covers its copyright-retained software in `12-AZ-IP/`, `TOOLS/`,
`9-INFRASTRUCTURE/`, and `public-site/`. This is **not** a declaration that every
file there is newly or exclusively AGPL: individual asset notices, prior public
grants, upstream licenses, and third-party components must be preserved.

In particular, `LicenseRef-Defensive-Public-Commons-1.0` headers and historical
public-domain releases require rights review, not automatic relabeling.
Notebooks may mix code and public-domain text. Copies and mirrors inherit their
actual asset permissions, not a new copyright merely through relocation.
The machine-readable policy at `9-INFRASTRUCTURE/licensing_policy.json` records
these distinctions; it is an index, not a replacement license.
Its current software locations must exist; separately listed historical
locations are archival scope references, not claims that those directories
still exist at the repository root.

Ideas, equations, facts, and methods are not made exclusive by this policy.
Public-domain dedication cannot itself enforce prohibitions on charging,
patenting, or downstream proprietary work. The older absolute statements above
express commons-protection intent, not a guarantee of those legal effects.
Attribution requests for public-domain material remain requests.

### 10.3 Individually negotiated exceptions

AxiomZero may offer an exception in exchange for payment **or** an expressly
defined partnership contribution, case by case. No payment, use, conversation,
or asserted affiliation alone grants an exception. A valid exception requires
an executed agreement by authorized parties specifying entities, covered
assets and versions, permitted integrations, consideration, disclosure duties,
duration, termination, and surviving rights.

The agreement must identify the copyright and contributor permissions supporting
the exception. AxiomZero cannot waive someone else's upstream copyleft or rights.
Neither an exception nor an NDA reduces the public's existing rights. Exceptions
are not universal alternate licenses and do not transfer ownership by default.
The supplemental terms in Commercial Terms §12 reconcile §4-A with §9.2.

The B2B commercial route ordinarily includes a one-time due-diligence and
alignment fee per product integration. For for-profit product integrations
under an executed exception, the usual negotiating reference is a residual use
fee around **2.32% of that product's quarterly revenues**. The actual rate,
revenue basis, reporting, duration and other terms are individually agreed;
this is not a universal charge, a share of all company revenue, or a condition
of compliant public-license use. Exceptions typically concern disclosure but
may address other expressly identified permissions within AxiomZero's rights.
See Commercial Terms §12.6 for required schedule definitions and safeguards.

### 10.4 AI disclosure and lawful limits

Using software in an AI pipeline does not automatically impose AGPL on every
model, weight, dataset, output, or surrounding system. Copyrightability,
derivation, fair use, and Corresponding Source are fact-dependent. This release
does not purport to resolve those questions or add a training restriction to AGPL.

An accepted partnership or exception agreement may separately require a public
reproducibility package: specified training/fine-tuning code, configurations,
weights or adapters, evaluation methods, provenance, and lawful dataset
descriptions, with explicit release licenses and deadlines. Actual datasets
may be required only where authorized and lawful. Personal data, credentials,
unrelated trade secrets, and third-party confidential material are excluded.
Document lawful exclusions and resulting reproducibility limits honestly.
No concealed telemetry, forced upload, or remote disabling enforces this policy.

These contractual exclusions do not excuse omission of material independently
required by the applicable public license. Operational credentials are not
ordinary publication artifacts; Installation Information under §6 may include
necessary authorization information. Resolve conflicts lawfully before covered
conveyance or deployment, rather than silently omit required information.

### 10.5 Washington law and King County forum

For agreements that expressly incorporate Commercial Terms §12 and are accepted
by authorized parties, AxiomZero selects Washington substantive law, subject to
applicable federal and mandatory law, and the appropriate state courts in King
County or the United States District Court for the Western District of Washington
at Seattle where federal subject-matter jurisdiction exists.

This selection does not bind public-domain users or AGPL recipients solely
because they download, run, or integrate code. No mandatory forum term is added
to AGPL. It does not unilaterally amend already executed agreements, override
mandatory consumer protections, or create subject-matter jurisdiction.
Forum enforceability depends on assent, applicable public policy and access
to remedies; no particular outcome is warranted. In *Dix v. ICT Group, Inc.*,
160 Wn.2d 826, 161 P.3d 1016 (2007), the Washington Supreme Court rejected a
forum clause that impaired the Washington consumers' effective class-action
remedy; this is not a rule invalidating or validating every forum clause.

### 10.6 Legal foundations and enforcement

The following authorities explain the mechanisms, not a promise of a particular
judicial outcome:

| Authority | Relevant boundary |
|---|---|
| [17 USC §102(b)](https://www.law.cornell.edu/uscode/text/17/102) | Copyright excludes ideas, procedures, systems, methods, and discoveries. |
| [17 USC §106](https://www.law.cornell.edu/uscode/text/17/106), [§107](https://www.law.cornell.edu/uscode/text/17/107) | Exclusive rights are subject to statutory limitations, including fair use. |
| [17 USC §204](https://www.law.cornell.edu/uscode/text/17/204) | Transfers of copyright ownership generally require signed writings. |
| [17 USC §411](https://www.law.cornell.edu/uscode/text/17/411), [§412](https://www.law.cornell.edu/uscode/text/17/412) | Registration requirements and timing affect suits and remedies, subject to statutory exceptions. |
| [17 USC §502](https://www.law.cornell.edu/uscode/text/17/502), [§504](https://www.law.cornell.edu/uscode/text/17/504), [§505](https://www.law.cornell.edu/uscode/text/17/505) | Injunctions, damages, profits, fees, and costs depend on statutory conditions and judicial decisions. |
| [28 USC §1338(a)](https://www.law.cornell.edu/uscode/text/28/1338) | Federal courts have exclusive jurisdiction over claims arising under federal copyright law. |
| [RCW 1.80.040](https://app.leg.wa.gov/RCW/default.aspx?cite=1.80.040), [1.80.060](https://app.leg.wa.gov/RCW/default.aspx?cite=1.80.060) | Electronic transactions depend on agreement; records and signatures are not denied effect merely for being electronic. |
| [AGPL v3 §§0–2, 4–14](https://www.gnu.org/licenses/agpl-3.0.html) | Definitions, Corresponding Source, conveyance, additional terms, acceptance, downstream freedoms, cure, patents, remote interaction and later versions. |

Electronic signature recognition is not proof of assent, authority, or forum
enforceability. Fingerprints demonstrate identity/provenance, not infringement
on their own. Preserve human-authorship evidence, assignments, contributor
permissions, applicable registrations, release history, and source-offer
evidence before asserting a claim. Use documented inquiry, fact assessment,
notice and applicable cure opportunities, then proportionate enforcement.
Court discovery is not automatic public disclosure of another party's secrets.

Copyright assertions extend only to protectable human-authored expression and
rights validly acquired. AI assistance, prompting, direction, review or a
provider's contractual allocation of output does not alone create copyright.
Human creative selection, arrangement or modifications require fact-specific
review. The earlier blanket ownership statements must be read with this limit;
third-party expression, provider software and provider agreements can involve
separate rights. An assignment transfers rights actually held, not rights that
never existed. See the U.S. Copyright Office's
[2025 copyrightability report](https://www.copyright.gov/ai/Copyright-and-Artificial-Intelligence-Part-2-Copyrightability-Report.pdf).

Public disclosure can provide relevant prior art; it cannot guarantee defeat of
all future patent claims. Eligibility, novelty and nonobviousness are separate
questions under [35 USC §§101–103](https://uscode.house.gov/view.xhtml?path=/prelim@title35/part2/chapter10&edition=prelim).
AGPL §§10–11 address patent protections within their scope, including contributor
essential claims, not general immunity from third-party patents.

### 10.7 Executable release checks

`TOOLS/checks/check_licensing_policy.py` detects changes to the approved policy
index, verifies current directories and document identifiers in CI; it does not
interpret or reconcile prose. Its optional `--release-manifest` checks declared source-offer
evidence for covered distributions and modified network releases. It is local
and read-only: no network requests, execution of submitted code, telemetry, or
alteration of runtime access.

A passing result means **structural evidence checks passed**, not a legal
certification or verification of public URL contents. The gate cannot infer
which software is a derivative work or authenticate a contract. Exception
requests always stop for authorized agreement review; a boolean, payment
receipt, or self-issued identifier cannot automatically approve them. Private
use does not require a public source offer merely to satisfy this tool.

The gate's JSON output and policy are readable by humans and machines. Run
`python TOOLS/checks/check_licensing_policy.py` from the repository root.
Optional release evidence is a JSON object with `policy_id`, `mode` (`public`
or `exception`), `activity` (`distribution`, `modified_network`, or `private`),
and `release_id`. Public distribution/network evidence additionally includes
`source_url` (HTTPS), `source_revision`, `license` (`AGPL-3.0-or-later`),
`source_offer_visible: true`, and `source_access: "public-no-auth"`.
Exception requests include `agreement_reference` and return exit code 2 for
manual review. Invalid evidence returns 1; structurally valid evidence returns 0.
Submit only non-sensitive evidence; keep contracts and credentials out of public
release manifests. Run this gate for each applicable release; CI's repository
check alone does not certify every deployment.

### 10.8 Research, licensing selection and publication record

The release retains standard AGPL for copyright-retained software and existing
public-domain permissions for their covered material. It does not retroactively
add CC BY-SA, CC0 or ODbL as restrictions or alternative escape routes.
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/legalcode.en)
can be considered for new rights-controlled expressive content;
[CC0](https://creativecommons.org/publicdomain/zero/1.0/legalcode.en) clarifies
waiver intent, not reciprocity;
[ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/) concerns qualifying
databases and does not automatically govern every trained model or database
content. Asset-level rights and compatibility review precede any adoption.

The complete, unmodified AGPL v3 document is now supplied in
[`LICENSES/AGPL-3.0-or-later.txt`](LICENSES/AGPL-3.0-or-later.txt), separate from
project summaries. Its application instructions are included. Retrieved from
the public [Nextcloud license mirror](https://github.com/nextcloud/server/blob/master/COPYING),
the copy matches Git blob `dba13ed2ddf783ee8118c6a581dbf75305f816a3`;
SHA-256 `57c8ff33c9c0cfc3ef00e650a1cc910d7ee479a8bc509f6c9209a7c2a11399d6`,
34,520 bytes. This provenance is not a publisher signature. The GNU publisher's
URL remains authoritative; direct publisher retrieval was unavailable.

Research on 2026-10-07 read the existing grants, contributor terms, commercial
contradictions and complete mirrored AGPL text. Statutory, Copyright Office and
judicial references were corroborated through search; direct retrieval from
GNU and several government/court hosts failed with DNS/access errors. Do not
interpret citations as proof that every linked current text was independently
downloaded or that private assignments, actual source offers or representative
authority were authenticated.

Official statutory collections:
[U.S. Code Title 17](https://uscode.house.gov/view.xhtml?path=/prelim@title17&edition=prelim),
[28 USC §1338](https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title28-section1338&num=0&edition=prelim),
[Washington electronic transactions](https://app.leg.wa.gov/RCW/default.aspx?cite=1.80),
and [Washington SPC statute, RCW 23B.25](https://app.leg.wa.gov/RCW/default.aspx?cite=23B.25).
SPC status supports a corporate social-purpose structure; it does not expand
copyright, waive third-party rights or bind unconsenting users.
The [Dix opinion reproduction](https://law.justia.com/cases/washington/supreme-court/2007/77101-4-1.html)
is judicial authority, not a contract template.

The publication sequence is rights/grants review, reconciliation by addition,
separate accepted-agreement terms, machine-readable indexing, local release
checks, tests and review, and a
[human-readable PsiCat release](7-OUTREACH/A%20Z%20PsiCat%20Literature/Releases/axiomzero-spc-licensing.md).
Technical publication does not execute anyone's exception agreement or announce
an adjudicated infringement finding.

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
