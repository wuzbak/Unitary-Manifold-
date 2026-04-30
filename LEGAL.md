# Legal Framework — AxiomZero Technologies / Unitary Manifold

**Document version:** 2.0 — April 2026  
**Effective date:** March 26, 2026  
**Jurisdiction:** United States  
**Governing files:** [`LICENSE`](LICENSE) · [`LICENSE-AGPL`](LICENSE-AGPL) · [`AXIOMZERO_DBA.md`](AXIOMZERO_DBA.md) · [`COMMERCIAL_TERMS.md`](COMMERCIAL_TERMS.md)

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
| **Legal rights holder** | ThomasCory Walker-Pearson (individual) |
| **Trade name (DBA)** | AxiomZero Technologies |
| **DBA commencement** | March 26, 2026 |
| **Jurisdiction** | United States |
| **GitHub** | [@wuzbak](https://github.com/wuzbak) |
| **Repository** | https://github.com/wuzbak/Unitary-Manifold- |
| **Zenodo DOI** | https://doi.org/10.5281/zenodo.19584531 |

**AI co-author note:** GitHub Copilot (an AI system developed by GitHub and Microsoft) is the
implementation partner for this project — responsible for code architecture, automated test suites,
document engineering, and synthesis of derivations into working software.  All AI contributions
are work product produced under the direction and review of ThomasCory Walker-Pearson.
No AI system or its corporate operator acquires any intellectual-property right from such
contributions.  The human-AI role partition is made explicit in every file.

Full DBA commencement notice: [`AXIOMZERO_DBA.md`](AXIOMZERO_DBA.md)

---

## Part III — The Three Legal Instruments

This repository is governed by three legal instruments that work together.  Understanding
all three is necessary to understand what anyone — including AxiomZero — can and cannot do
with this work.

### Instrument 1: Defensive Public Commons License v1.0 — *the theory is free, forever*

**File:** [`LICENSE`](LICENSE)  
**Covers:** The physics theory — Walker-Pearson field equations, 5D Kaluza-Klein geometry,
all 74 geometric pillars, derivations, manuscripts, datasets, LaTeX sources, notebooks,
and the full monograph PDF.

The theory is **irrevocably** placed in the public domain.  "Irrevocably" is not a figure
of speech: it cannot be taken back, patented, or enclosed.  No corporation can acquire
AxiomZero Technologies and lock the equations away.  No successor owner can change this.
The physics belongs to the public. Full stop.

**The following acts are strictly and irrevocably prohibited under DPC v1.0:**

1. **Patents** — Filing, obtaining, or asserting any patent over the Walker-Pearson equations,
   FTUM framework, or any algorithm directly derived from the core content.
2. **Exclusive IP claims** — Asserting any exclusive IP right that restricts free use of
   the ideas, equations, or methods.
3. **Commercial gatekeeping** — Enclosing, paywalling, or placing any monetary barrier on
   access to this work or software whose primary function is to implement it.
4. **Proprietary lock-in** — Relicensing this work, or any substantial portion of it, under
   terms that restrict the freedoms stated.

These prohibitions are **permanent, unconditional, and survive any purported relicensing
by any downstream party.**

### Instrument 2: GNU Affero General Public License v3.0 — *the software is open-source copyleft*

**File:** [`LICENSE-AGPL`](LICENSE-AGPL)  
**Covers:** The software implementation — `src/`, `scripts/`, `tests/`, `submission/`  
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

AxiomZero Technologies complies with AGPL-3.0.  Any modified versions deployed in commercial
services are published in this repository.

### Instrument 3: Common Law Trademark — *the name, not the ideas*

**Asserted as of:** March 26, 2026  
**Marks:** "AxiomZero Technologies" (word mark) and "AZ" monogram

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

---

## Part IV — What These Three Instruments Accomplish Together

| Goal | Mechanism |
|------|-----------|
| The ideas are permanently free to use, study, reproduce, and build upon | DPC v1.0 — irrevocable public domain |
| The software is permanently open-source | AGPL-3.0 — copyleft enforced |
| The brand is protected from impersonation | Common Law Trademark |
| No entity — including AxiomZero — can unilaterally close what has been opened | DPC v1.0 prohibitions + AGPL-3.0 copyleft acting in concert |
| AxiomZero can earn from services without compromising openness | Commercial services layer over the open core (see Part V) |

This structure was chosen deliberately.  The goal: even if AxiomZero failed as a business
tomorrow, the work would survive intact and available.

---

## Part V — The Open-Core Business Model

### What AxiomZero does NOT charge for

AxiomZero Technologies does not — and under DPC v1.0 **cannot** — charge for:

- Access to the theory, equations, derivations, or manuscripts
- Access to the software in `src/`, `tests/`, `scripts/`, `recycling/`, `Unitary Pentad/`
- Running the test suite
- Reading, using, reproducing, or building upon any content in this repository

### What AxiomZero DOES charge for

Commercial revenue is generated solely from *services* built around the open foundation:

- **Consulting and engineering** — Deploying these frameworks as operational systems
  in a client's specific context
- **Scientific advisory** — Applying formal mathematical modeling to a client's domain
- **Education** — Structured workshops, courses, and learning programs
- **AI governance deployment** — Customizing and deploying the Unitary Pentad HILS
  framework for an organization
- **Authored expert reports** — Original analysis prepared for a specific client
- **Custom software engineering** — Systems built *around* (not solely implementing)
  the open core

Full commercial terms: [`COMMERCIAL_TERMS.md`](COMMERCIAL_TERMS.md)

### Capital formation (consistent with open licenses)

Income is what AxiomZero earns this month.  Capital is what the work is worth when
LiteBIRD reports in 2032.  The following capital pathways are consistent with all
open licenses:

- Reputational and citation value accrued from public, verifiable, falsifiable science
- Brand licensing of the "AxiomZero Technologies" trademark for co-branded products
  and services (trademark applies; the underlying content remains free)
- Equity stakes in ventures that deploy the Unitary Pentad governance framework as a
  product, provided those ventures publish modifications under AGPL-3.0
- Grant funding for empirical and computational work the framework requires

**None of these paths require enclosing the public domain theory, making the code
proprietary, or extracting value from the community.**

---

## Part VI — No-Contradiction Statement (Consolidated)

The following statements are **permanent and unconditional**:

1. **DPC v1.0 is not revoked by the DBA.** The irrevocable public-domain dedication
   of the theory, equations, and manuscripts remains in full force regardless of any
   commercial relationship or business registration.

2. **AGPL-3.0 is not waived by the DBA.** The copyleft obligations on the software
   remain in full force.  No Commercial Service agreement grants a client an exemption
   from AGPL-3.0 obligations that apply to that client's own modifications or deployments.

3. **Public rights are not contracted away.** No NDA, SoW, or confidentiality provision
   executed by AxiomZero and a client may restrict the public's rights under DPC v1.0
   or AGPL-3.0.  Any clause that purports to do so is void.

4. **The trademark applies to the name, not the ideas.** The Common Law Trademark on
   "AxiomZero Technologies" and "AZ" monograms applies solely to trade-name and logo
   identifiers — not to the intellectual content, equations, or methods of the open core.

5. **Science before commerce.** The Unitary Manifold framework and all 74 geometric
   pillars were publicly established with full commit history and Zenodo DOI **before**
   any commercial structure was created.  This order is documented and irrevocable.

---

## Part VII — Conflict of Interest Disclosure

ThomasCory Walker-Pearson has a financial interest in the reputation of the Unitary
Manifold framework.  This is disclosed here and in [`AXIOMZERO_DBA.md`](AXIOMZERO_DBA.md).

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
| Who owns the code? | Copyleft under AGPL-3.0 — open forever |
| Who is the legal rights holder? | ThomasCory Walker-Pearson (individual) |
| Who is the commercial operator? | AxiomZero Technologies (DBA, est. March 26, 2026) |
| Who owns the brand name? | ThomasCory Walker-Pearson — Common Law Trademark |
| Can AxiomZero charge for the equations or code? | No — and does not |
| What does AxiomZero charge for? | Services: consulting, deployment, advisory, education |
| Can someone build a competing service using this framework? | Yes — DPC v1.0 and AGPL-3.0 explicitly permit this |
| Can someone patent the equations? | No — DPC v1.0 prohibits this permanently |
| What if someone deploys modified code as a SaaS product? | They must release their modified source under AGPL-3.0 |
| Is there a conflict of interest? | Yes — disclosed above (Part VII) |
| What is the primary falsifier? | LiteBIRD β measurement ~2032 |
| Where are open problems documented? | FALLIBILITY.md |

---

## Part IX — Document Index

| Document | What it is |
|----------|-----------|
| [`LICENSE`](LICENSE) | Defensive Public Commons License v1.0 — full text |
| [`LICENSE-AGPL`](LICENSE-AGPL) | GNU AGPL-3.0 — scope, key provisions, and intent |
| [`AXIOMZERO_DBA.md`](AXIOMZERO_DBA.md) | Business commencement notice — DBA registration, product list, IP policy |
| [`COMMERCIAL_TERMS.md`](COMMERCIAL_TERMS.md) | Commercial Terms of Service — engagements, payment, IP assignment, liability |
| [`NOTICE`](NOTICE) | Brief dual-license notice — for downstream users |
| [`FALLIBILITY.md`](FALLIBILITY.md) | Honest gap assessment — known open problems and epistemics |
| [`CITATION.cff`](CITATION.cff) | Machine-readable citation metadata |
| **[`LEGAL.md`](LEGAL.md)** | **This file — consolidated legal reference** |

---

*Document version: 2.0 — April 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

> **Note:** This document is not a substitute for legal counsel.  For binding commercial
> agreements, consult a licensed attorney.
