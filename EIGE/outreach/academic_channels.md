# EIGE Academic Launch — Channel Guide

**AxiomZero EIGE v21.0**  
*Scientific community engagement plan*

---

## Primary Academic Venues

### 1. EVT/WOTE — Electronic Voting Technology / Workshop on Trustworthy Elections

**URL:** https://www.usenix.org/conference/evtwote  
**Why:** The premier academic venue for election security research. Directly targets election security researchers, computer scientists, and policy makers. Papers are peer-reviewed and widely cited in election integrity discussions.  
**Target submission:** Full paper on EIGE system design and security properties  
**Key message:** Real-time deterministic tamper-detection invariant vs. retroactive probabilistic auditing; direct comparison to RLAs  
**Preparation needed:** Convert arXiv preprint to EVT/WOTE format; add user study or pilot data if available

### 2. arXiv — cs.CR (Cryptography and Security) and cs.CY (Computers and Society)

**URL:** https://arxiv.org  
**Why:** Immediate public availability; indexed by Google Scholar; standard for establishing priority  
**Action:** Submit `paper/eige_arxiv_preprint.md` (converted to LaTeX/PDF)  
**Cross-list:** cs.CR (primary) + cs.CY (cross-list) + cs.DC (distributed computing, for 3-tier architecture)  
**Expected timeline:** 1–2 business days to appear

### 3. IEEE Security & Privacy (Oakland)

**URL:** https://sp2027.ieee-security.org (upcoming)  
**Why:** Top-tier security conference; broad cryptography community audience  
**Target submission:** Focused paper on CS hash security properties (non-commutativity, sequence-position encoding) vs. Merkle-tree approaches  
**Key message:** New class of tamper-detection primitive with different threat model than CRH or Merkle trees  
**Preparation needed:** Formal security analysis (or disclaimer that it is in progress); comparison table vs. standard hash security definitions

### 4. USENIX Security

**URL:** https://www.usenix.org/conference/usenixsecurity  
**Why:** Strong tradition of election security and systems security papers  
**Target submission:** System paper on EIGE implementation; adversarial test suite evaluation  
**Key message:** 449-test adversarial evaluation methodology; chaos injection as election security testing framework

### 5. ACM CCS (Conference on Computer and Communications Security)

**URL:** https://www.sigsac.org/ccs  
**Why:** Top-tier venue for new cryptographic primitives and security protocols  
**Target submission:** CS hash security properties + zero-knowledge compliance architecture  
**Key message:** Zero-knowledge federal compliance without a central ballot database

---

## Secondary Venues

| Venue | Focus | Notes |
|-------|-------|-------|
| **NDSS** | Network and Distributed System Security | Good for three-tier sovereignty architecture |
| **Financial Cryptography** | Crypto + applied | CS hash as new commitment primitive |
| **Voting '26 / VoteID** | International voting systems | European election technology community |
| **IACR ePrint** | Cryptography preprints | Submit CS hash analysis separately as a short note |

---

## NGO and Policy Channels

| Organization | Contact | Approach |
|-------------|---------|----------|
| **MIT Election Data and Science Lab** | electionlab.mit.edu | Submit preprint; request inclusion in working paper series |
| **Verified Voting Foundation** | verifiedvoting.org | Technical review request; RLA comparison framing |
| **OSET Institute** | osetinstitute.org | Open-source technology registry submission |
| **Center for Democracy and Technology** | cdt.org | Policy framing; federal data access architecture |
| **Stanford Internet Observatory** | io.stanford.edu | Mis/disinformation and election integrity lens |
| **Shorenstein Center** | shorensteincenter.org | Media and public communication framing |

---

## Researcher Outreach — Cryptanalysis Partners

The following research groups have published relevant work on election security, RLAs, or applied cryptography:

| Researcher | Institution | Relevance |
|-----------|------------|-----------|
| **Philip Stark** | UC Berkeley | Invented risk-limiting audits — compare EIGE vs. RLA directly |
| **J. Alex Halderman** | University of Michigan | Electronic voting security; EVT/WOTE community |
| **Ron Rivest** | MIT CSAIL | Election security; cryptographic protocol design |
| **Vanessa Teague** | Australian National University | Helios/e-voting; open-source election security |
| **Matthew Bernhard** | University of Michigan | STAR-Vote, voting system security |

**Recommended approach:** Send a brief 2-paragraph email with the arXiv preprint link, explicitly inviting critique of the CS hash security analysis. Requesting critique (not validation) is the correct framing for a research community introduction.

---

## Public Launch Channels

| Channel | Audience | Message |
|---------|----------|---------|
| **GitHub release (v21.0.0 tag)** | Developers | 449 tests, full docs, runnable demo |
| **Hacker News (Show HN)** | Technical public | "Show HN: Open-source deterministic election integrity engine" |
| **r/netsec, r/crypto** | Security researchers | CS hash cryptanalysis challenge |
| **r/programming, r/Python** | General developers | "We built an election auditing engine in Python — here's how the math works" |
| **LinkedIn (policy audience)** | Election officials, policy makers | Plain-English explainer link |
| **Twitter/X @elections_nerd** | Election security community | Tag EVT/WOTE, Verified Voting, election security researchers |

---

## Press and Media

| Outlet | Beat | Angle |
|--------|------|-------|
| **MIT Technology Review** | Election security + AI | "Can a physics equation make elections tamper-proof?" |
| **Wired** | Technology + democracy | Open-source election integrity; AI-assisted software development |
| **Ars Technica** | Technical depth | Deep dive on CS hash and three-tier architecture |
| **The Markup** | Data and democracy | Federal data access design; privacy architecture |
| **StateScoop** | State government IT | Washington State pilot proposal; NIST compliance |
| **FCW / FedScoop** | Federal technology | CISA engagement; EAC notification |

**Press kit checklist:**
- [ ] One-page explainer ([EXPLAINER.md](../EXPLAINER.md))
- [ ] Demo GIF or screenshot of Public Trust Report output
- [ ] Quote from ThomasCory Walker-Pearson on the core insight
- [ ] Link to the arXiv preprint for technical journalists
- [ ] Contact email for technical questions

---

## Submission Preparation Checklist

- [ ] Convert `paper/eige_arxiv_preprint.md` to LaTeX (use `arxiv-style.cls`)
- [ ] Add author ORCID identifiers
- [ ] Generate PDF with all figures (architecture diagrams from ARCHITECTURE.md)
- [ ] Submit to arXiv cs.CR
- [ ] Submit to EVT/WOTE (check CFP deadline)
- [ ] Open GitHub Discussions for community questions
- [ ] Tag v21.0.0 release on GitHub
- [ ] Publish Zenodo companion DOI (linked to main Unitary Manifold DOI)

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
