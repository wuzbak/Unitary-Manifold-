# Project Meridian: The Influence Map

**A Federal Commission, the Firms on Both Sides of the Table, and the Money Layer Behind It**

*An AXIOM Journalist case file — prepared at the desk of PsiCat, resident journalist, AxiomZero Technologies & Consulting, SPC. Published under the institution's name; no private individual is credited or named.*

---

## How this file was built, and what it is not

**Method — the AXIOM OSINT Triangulation Chain.** Three evidence tiers: **Tier 1** primary records (the statutory company register, the parliamentary record, the federal campaign-finance record, agency releases, court dockets); **Tier 2** institutional reporting (Reuters, The New York Times, the BBC); **Tier 3** curated and compiled material. Every edge in this file carries its confidence label and its own sources.

**The rule that governs the whole file:** linkage requires an identifier — a company number, a director or officer appointment, an award ID — or a document that names both parties. Two entities are never joined because their names resemble each other, because they share a sector, or because the join would be interesting. Word collision is not evidence.

**What this file is not.** It is not an accusation, a finding of illegality, or a claim about anyone's state of mind. It maps documented roles and documented money, and it says plainly where the record stops.

---

## I. The announcement

On **26 September 2026**, Defense Secretary **Pete Hegseth** announced **Project Meridian** at a Marine Corps event at **Quantico, Virginia**. Meridian is presented as a federal effort to accelerate defence industrial capacity. The department is referred to in the announcement's own framing as the **Department of War** — the naming in use for the Pentagon under the current administration.

**Why the date matters procedurally.** The body is being constituted from private-sector executives while the agencies it is convened to advise are, at the same time, the counterparties of the firms those executives run. That is a structural fact about the arrangement, not an allegation about any person.

---

## II. The three co-directors and the companies they carry into the room

| Co-director | Documented commercial position |
| --- | --- |
| **Palmer Luckey** | Founder of **Anduril Industries** (defence autonomy, the Lattice platform). Anduril holds Department of Defense contracts and has publicly positioned itself for the **Golden Dome** missile-defence architecture. |
| **Emil Michael** | Former Uber executive; founder of the investment vehicle **Build American**; currently an executive at **xAI**. |
| **Michael Kratsios** | Former United States Chief Technology Officer; previously a principal at **Thiel Capital**. |

**The documented structural note.** **Peter Thiel** founded **Founders Fund**, which was an **early investor in Anduril**, and Thiel co-founded **Palantir Technologies**, a DoD prime contractor. The commission therefore contains, in its chair and in its co-directorship, personnel whose commercial interests sit on the contracting side of the relationships the body exists to rationalise. This is documented structure. It is not, on its own, misconduct.

---

## III. The edge this file does not close

The commission's chair is identified in public reporting as **Trae Stephens** — a **Founders Fund** partner, and co-founder and executive chairman of **Anduril**.

**GAP — the central one.** The record does not establish a dated document in which Founders Fund or Anduril was consulted on, or benefited from, the creation of Project Meridian itself. The structural proximity is documented. The causal edge is not. It is held open here rather than closed by reasoning.

**What would close it:** an award, task order or contract modification naming Anduril or a Founders Fund portfolio company under a Meridian-aligned programme; the commission's own charter, membership roster and recusal record; contracting-officer documentation of any competitive process that preceded an award.

---

## IV. The money layer — the political-data question

A separate documented layer, set out here on its own evidence and **not joined** to section II:

- **Robert Mercer** provided **$15 million** to Cambridge Analytica. The House of Commons Digital, Culture, Media and Sport Committee recorded **Christopher Wylie's** account that funding the capability privately and then selling it to a campaign at nominal price was a route around electoral finance law. — **CORROBORATED** (The New York Times; House of Commons DCMS Committee report).
- **Cambridge Analytica** drew on data obtained without consent and was the subject of regulatory action in the United Kingdom and the United States. — **CORROBORATED** (Information Commissioner's Office; Federal Trade Commission).
- **Emerdata Limited** was incorporated in the United Kingdom on **11 August 2017**, company number **10911848**. — **CORROBORATED** (Companies House, the statutory register).
- Officers of Emerdata recorded in the register included **Rebekah Mercer**, **Jennifer Mercer** and **Alexander Nix**. — **CORROBORATED** (Companies House).
- **Nigel Oakes**, founder of SCL Group, later served as a chair of Emerdata. — **ALLEGED** (press reporting; not confirmed in the register).
- Political committees **Make America Number 1** and its successor vehicle were funded substantially by the **Mercer** family. — **CORROBORATED** (Federal Election Commission records).
- **Article 1** was formed in 2015, with a reported purpose of building a data and media capability outside conventional party structures. — **ALLEGED** (reporting).
- **Stephen Bannon's** described strategy of "flooding the zone" with provocation is documented in his own words across interviews and books. — **CORROBORATED** (the strategy is documented; its application to any specific entity in this file is not).

**GAP.** No primary record in this file ties Emerdata, the Article 1 vehicles or the Mercer-funded committees to any named current or former officer of the defence firms in section II. The two layers are documented separately and are **not joined by an identifier** here.

**What would close it:** itemised FEC Schedule A and Schedule B records showing shared vendors or consultants across the two layers; corporate filings showing a shared director; court or subpoena records naming both.

**A note on method learned in this case.** An earlier pass of this investigation searched by *name* and produced a high rate of false positives — "Meridian", "Mercer" and "Emerdata" are not distinctive strings. Name matching is why. Every claim admitted to this file since has been admitted on an identifier: a company number, a UEI, an award ID, a docket number.

---

## V. The gaps this file names

1. Meridian's founding instrument — charter, membership roster, and any conflict-of-interest or recusal policy.
2. Any documented recusal by the chair or by a co-director.
3. Any dated document linking Meridian's creation to a specific firm's lobbying or advocacy.
4. Any award, task order or contract modification issued under a Meridian-aligned programme to a firm whose executive sits on the commission.
5. Any identifier-linked edge joining the political-money layer (section IV) to the defence-procurement layer (sections II–III).
6. The full beneficial-ownership chain of the vehicles named in section IV beyond the filing officers.

---

## VI. Instrument readings

Every live-fetch source in this case reports its own state, so that a silence is never read as an absence.

| Instrument | Reading |
| --- | --- |
| **USAspending** (federal awards) | **DEAD** — neither the recipient reading nor the award aggregation answered from this environment. The award reading has to be taken through the public portal by hand. |
| **Federal Election Commission** | **LIVE** — committee and contribution records. |
| **SEC EDGAR** | **LIVE** — filer and filing index. |
| **CourtListener** | **LIVE** — docket and opinion search. |
| **Wayback Machine** | **LIVE** — archived pages, for statements since edited. |
| **GOVINFO** | **LIVE** — Federal Register, U.S. Code, CFR, congressional publications. |
| **OpenSanctions** | **DEGRADED** — the API token was rejected; OFAC and OpenSanctions deep-links supplied in its place. |
| **OCCRP Aleph / ICIJ Offshore Leaks** | **DEGRADED** — a web application firewall blocks server-side search; pre-filled deep-links supplied instead. |
| **Corporate registry (aggregator)** | **DEGRADED** — returned nothing for a company that demonstrably exists. The register reading in section IV was taken directly from Companies House by hand. |

---

## VII. Right of reply and legal posture

**Posture: pre-publication, research stage.** This file is a research instrument. It is not a published article, it has not been cleared for publication, and it carries no legal review.

Every person named in this file is named in their public or professional role, on the record, and by the document that carries their name. Nothing here describes private life, personal identifiers, location or family.

**Right of reply.** Any subject named in this file is invited to respond. A response received is recorded in the case file alongside the claim it addresses, and the claim is amended in the open if the response meets it — not deleted.

---

## VIII. What comes next

- Request the Meridian charter, membership roster and recusal policy under the Freedom of Information Act.
- Take the award history for each contracting firm by hand through the USAspending portal, and copy the award IDs back into the case.
- Cross-check every officer of Emerdata and the Article 1 vehicles against corporate filings for the defence firms — identifier-keyed, not name-matched.
- Hold the central edge open until a document closes it. If no document closes it, report the edge as an open question — not as a finding.

---

*Provenance: this file traces to the **Project Meridian — Influence Map** case in the AXIOM Journalist Case Library, where every claim above appears with its own sources, tier and confidence label. It is the readable companion to the working case, not a substitute for it.*

*AxiomZero Technologies & Consulting, SPC maintains no political stance, endorsement or partisan alignment. The same methodology is applied to any subject regardless of party. A methodology that produces the conclusion the analyst wanted is not a methodology — it is an argument wearing one.*
