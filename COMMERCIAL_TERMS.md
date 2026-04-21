# Commercial Terms of Service — AxiomZero Technologies

**Document version:** 1.0 — April 2026  
**Effective date:** March 26, 2026  
**Jurisdiction:** United States

> **⚠ NOT LEGAL ADVICE.**  This document establishes the commercial framework under which AxiomZero
> Technologies offers paid services.  Nothing herein constitutes legal, financial, or scientific
> advice.  Consult a licensed attorney before entering any commercial agreement.

---

## § 1 · Preamble — Open-Core Commitment

The **Unitary Manifold** (theory, equations, software, datasets, and all materials in this
repository) is and remains irrevocably dedicated to the public domain under the
**Defensive Public Commons License v1.0** (`LICENSE`) and is available as free, copyleft
open-source software under the **GNU Affero General Public License v3.0** (`LICENSE-AGPL`).

These Commercial Terms of Service ("Commercial ToS") govern only the *additional*, value-added
services that **AxiomZero Technologies** ("AxiomZero," "we," "us") offers to clients
("Client," "you") on a paid basis.  Nothing in this document alters, limits, or supersedes
the rights granted by DPC v1.0 or AGPL-3.0 to any person.

The open-core architecture is permanent:

| Layer | What it covers | Always free? |
|-------|---------------|-------------|
| **Open Core** | Theory, equations, `src/`, `tests/`, `recycling/`, `Unitary Pentad/`, manuscripts, notebooks, datasets | **Yes — irrevocably** |
| **AxiomZero Commercial Services** | Consulting, custom engineering, governance deployments, expert reports, training | **No — governed by this ToS** |

---

## § 2 · Definitions

**"Open Core"** means all intellectual content, source code, manuscripts, datasets, and
derivative materials in the Unitary Manifold repository licensed under DPC v1.0 and/or
AGPL-3.0, including but not limited to:

- `src/`, `tests/`, `recycling/`, `Unitary Pentad/` (Python source and test suites)
- The Walker-Pearson field equations, FTUM framework, and all 26 Geometric Pillars
- All manuscripts, LaTeX sources (`arxiv/`), notebooks (`notebooks/`), and the full monograph
- The Unitary Pentad HILS governance framework and all associated modules

**"AxiomZero Commercial Services"** means services offered by AxiomZero Technologies
*beyond* the Open Core, including:

- Scientific consulting and technical advisory engagements
- Custom software engineering on systems built *around* (not solely implementing) the Open Core
- Bespoke governance-layer deployments and AI-systems integration
- Authored expert reports, white papers, and technical analyses prepared for a specific client
- Training workshops, seminars, and structured educational programs
- Any other service explicitly described as a "Commercial Service" in a signed Statement of Work

**"Proprietary Output"** means any document, software module, dataset, architecture design,
analysis, or other deliverable created by AxiomZero *for a specific Client* under a paid
engagement, where that deliverable:

1. is not a verbatim or lightly modified copy of the Open Core; and  
2. embodies substantial original work by AxiomZero beyond what is contained in the Open Core.

Merely running the Open Core on a client's data and delivering the result does **not** constitute
a Proprietary Output; see § 4.

**"Statement of Work" ("SoW")** means a written document, signed by both parties, describing the
scope, deliverables, timeline, and pricing of a specific Commercial Service engagement.

**"DPC v1.0"** means the Defensive Public Commons License v1.0 (file: `LICENSE`).

**"AGPL-3.0"** means the GNU Affero General Public License v3.0 (file: `LICENSE-AGPL`).

---

## § 3 · License Boundary — Protecting Public Rights

### 3.1 Public rights are not diminished

No Commercial Service, Proprietary Output, or obligation under this ToS:

- restricts any person's rights under DPC v1.0 or AGPL-3.0;
- places any paywall, subscription barrier, or access control on the Open Core;
- grants a Client exclusive rights over any idea, equation, algorithm, or method that is part
  of the Open Core; or
- constitutes a patent, trade-secret claim, or exclusive IP assertion over the Walker-Pearson
  field equations, the FTUM framework, or any content that is part of the Open Core.

### 3.2 Client license to Proprietary Outputs

Upon receipt of full payment for a Commercial Service, AxiomZero grants the Client a
**non-exclusive, non-transferable, royalty-free license** to use the Proprietary Output
delivered under that engagement for the Client's internal and commercial purposes.

The Client does **not** acquire:

- copyright ownership of the Proprietary Output (unless explicitly assigned in the SoW);
- any right to sub-license the Proprietary Output as if it were their own original work; or
- any right to restrict third parties from using the underlying Open Core.

### 3.3 Identification of origin

All Proprietary Outputs shall clearly identify:

- which portions derive from or depend on the Open Core (citing the applicable license); and
- which portions constitute original AxiomZero work product.

---

## § 4 · Permitted Use of the Open Core in Commercial Services

AxiomZero may use the Open Core as a computational substrate, reference framework, or
analytical tool when performing Commercial Services, subject to the following conditions:

1. **No paywall on the Open Core itself.**  Fees charged to Clients are for AxiomZero's *labor,
   expertise, and original work product* — not for access to the Open Core.

2. **AGPL-3.0 compliance.**  If AxiomZero deploys a modified version of any AGPL-covered source
   file as part of delivering a service (including as a network service), AxiomZero shall
   publish the modified source code under AGPL-3.0, consistent with the obligations in
   `LICENSE-AGPL`.

3. **Clear attribution and distinction.**  Client deliverables shall distinguish AxiomZero's
   original work from the Open Core.  The Open Core shall be cited per the preferred citation
   in `CITATION.cff`.

4. **No repackaging as a primary implementation.**  AxiomZero shall not charge fees for a
   service whose *primary function* is solely to implement, reproduce, or execute the Open Core
   on behalf of a client without adding substantial original work.  Running `python -m pytest`
   or `python -c "from src.core.evolution import FieldState"` on a client's hardware is not a
   Commercial Service.

---

## § 5 · Payment, Scope, and Statements of Work

### 5.1 Engagement commencement

No Commercial Service engagement commences until both parties have executed a Statement of Work
that specifies:

- the scope of deliverables and any exclusions;
- the timeline and milestone dates;
- the fee structure (fixed-fee, time-and-materials, or retainer); and
- any IP-assignment provisions for purely new work (see § 5.3).

### 5.2 Payment terms

Unless otherwise stated in the SoW:

- invoices are due **net-30** from the invoice date;
- late payments accrue interest at **1.5% per month** (18% per annum) or the maximum rate
  permitted by applicable law, whichever is lower;
- AxiomZero may suspend work on a Commercial Service after **15 days** of non-payment without
  liability; and
- all fees are denominated in **United States Dollars (USD)**.

### 5.3 Intellectual property assignment for new work

By default, copyright in Proprietary Outputs remains with **ThomasCory Walker-Pearson /
AxiomZero Technologies**.  Full copyright assignment to the Client requires:

- an explicit "IP Assignment" clause in the SoW signed by both parties; and
- payment in full of all invoices under that SoW.

Regardless of any IP assignment, the rights of the public under DPC v1.0 and AGPL-3.0
(see § 3.1) are never transferred or restricted.

### 5.4 Change orders

Material changes to scope, timeline, or deliverables require a written change-order addendum
signed by both parties.  Verbal agreements do not constitute binding changes to an SoW.

---

## § 6 · Warranties and Liability

### 6.1 "As-is" provision

All Commercial Services and Proprietary Outputs are provided **"AS IS"**, consistent with the
disclaimer in DPC v1.0.  AxiomZero makes no warranty, express or implied, including any
implied warranty of merchantability, fitness for a particular purpose, or non-infringement.

### 6.2 No warranty on physics predictions

The Unitary Manifold is a research-stage theoretical framework.  AxiomZero makes no
representation that any prediction, model output, or numerical result derived from the
framework is accurate, complete, or fit for any particular engineering, medical, financial,
or safety-critical application.  The primary falsifier (birefringence β prediction, LiteBIRD
~2032) and all known open problems are documented in `FALLIBILITY.md`.

### 6.3 Limitation of liability

To the fullest extent permitted by applicable law, AxiomZero's aggregate liability to a Client
for any and all claims arising from a Commercial Service shall not exceed the **total fees paid
by the Client under the applicable SoW** in the **twelve (12) months** preceding the claim.

AxiomZero shall not be liable for any indirect, incidental, consequential, punitive, or
special damages, even if advised of the possibility of such damages.

### 6.4 Indemnification

Each party agrees to indemnify and hold harmless the other party from claims, losses, or
damages arising from its own breach of this ToS, its own negligence, or its own misuse of the
Open Core in violation of DPC v1.0 or AGPL-3.0.

---

## § 7 · Trademark

The following marks are asserted **Common Law Trademarks** of ThomasCory Walker-Pearson
as of March 26, 2026:

- **AxiomZero Technologies** (word mark)
- **AZ** monogram (when used in the context of the Unitary Manifold or related services)

**Permitted uses:**  Clients may use these marks solely to identify AxiomZero as the provider
of services received under a signed SoW (e.g., "developed in collaboration with AxiomZero
Technologies").

**Prohibited uses without prior written permission:**

- using the marks in a manner that implies endorsement, partnership, or affiliation beyond the
  specific engagement;
- incorporating the marks into the Client's own product or company names; or
- using the marks to market products or services that compete with AxiomZero Commercial Services.

This trademark assertion does **not** restrict any person's right to use the intellectual
content, equations, or source code of the Open Core as granted by DPC v1.0 and AGPL-3.0.

---

## § 8 · Governing Law and Dispute Resolution

### 8.1 Governing law

This ToS and any SoW executed under it shall be governed by and construed in accordance with
the laws of the **United States**, and, to the extent state law applies, the law of the state
in which ThomasCory Walker-Pearson is domiciled at the time of the dispute, without regard to
conflict-of-law principles.

### 8.2 Dispute resolution

The parties shall first attempt to resolve any dispute through good-faith negotiation for a
period of **30 days** after written notice of the dispute.  If negotiation fails, the parties
agree to non-binding mediation before pursuing any legal or arbitral proceeding.

### 8.3 Attorneys' fees

In any proceeding to enforce this ToS, the prevailing party shall be entitled to recover
reasonable attorneys' fees and costs from the non-prevailing party.

---

## § 9 · No-Contradiction Clause

This Commercial ToS is expressly designed to operate in full harmony with the open licenses
governing the Unitary Manifold.  The following statements are permanent and unconditional:

1. **DPC v1.0 is not revoked.**  The irrevocable public-domain dedication of the theory,
   equations, and manuscripts under DPC v1.0 remains in full force, regardless of any
   commercial relationship.

2. **AGPL-3.0 is not waived.**  The copyleft obligations on the software implementation under
   AGPL-3.0 remain in full force.  No Commercial Service agreement grants a Client an exemption
   from AGPL-3.0 obligations that apply to that Client's own modifications or deployments.

3. **Public rights are not contracted away.**  No SoW, NDA, or confidentiality provision
   executed by AxiomZero and a Client may restrict the public's rights under DPC v1.0 or
   AGPL-3.0.  Any clause in an SoW that purports to do so is void.

4. **Trademark applies to the name, not the ideas.**  The Common Law Trademark on
   "AxiomZero Technologies" and "AZ" monograms applies solely to trade-name and logo
   identifiers, not to the intellectual content, equations, or methods of the Open Core.

5. **Mirror of AXIOMZERO_DBA.md § 5.**  This clause is the contractual counterpart to the
   No-Contradiction Statement in `AXIOMZERO_DBA.md § 5`.  Both documents are consistent and
   mutually reinforcing.

---

## § 10 · General Provisions

**Entire agreement.**  For any given engagement, this ToS together with the executed SoW
constitutes the entire agreement between the parties with respect to that engagement and
supersedes all prior negotiations, representations, and understandings.

**Severability.**  If any provision of this ToS is held invalid or unenforceable, the
remaining provisions shall continue in full force.

**Waiver.**  Failure to enforce any provision of this ToS does not constitute a waiver of the
right to enforce that provision in the future.

**Notices.**  All notices under this ToS shall be in writing and delivered by email to the
address specified in the applicable SoW, or via the GitHub Issues tracker at
https://github.com/wuzbak/Unitary-Manifold-/issues.

**Amendment.**  AxiomZero may update this ToS from time to time.  Material changes will be
announced via a commit to the repository's default branch.  Engagements already in progress
under a signed SoW are governed by the version of this ToS in effect at the time of signing.

---

*Document version: 1.0 — April 2026*  
*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*  

> **Reminder:** This document is not a substitute for legal counsel.  Have a licensed attorney
> review all commercial agreements before execution.
