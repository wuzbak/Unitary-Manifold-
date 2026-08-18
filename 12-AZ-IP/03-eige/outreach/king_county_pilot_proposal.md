# King County Elections — Shadow-Mode Pilot Proposal

**AxiomZero EIGE v21.0**  
**Proposal type:** Observational Shadow-Mode Technical Trial  
**Jurisdiction:** King County Elections, Washington State  
**Proposing organization:** AxiomZero Technologies & Consulting, SPC  
**Contact:** ThomasCory Walker-Pearson, Scientific Director

---

## Executive Summary

AxiomZero Technologies proposes a **shadow-mode observational trial** of the Election Integrity Governance Engine (EIGE) v21.0 in King County during an upcoming election cycle.

**Shadow mode means:** EIGE runs in parallel with the existing King County counting system. It receives the same integer ballot data already produced by the existing scanner and tabulation infrastructure. It produces its own independent integrity record. It has **zero operational impact** on the existing process — it does not modify, redirect, or delay any existing workflow.

The goal is to produce a publicly available comparison: the existing chain-of-custody record versus the EIGE mathematical invariant record, across a full election cycle, with all data published post-certification.

This is not a replacement. It is a verification layer.

---

## 1. Why King County

King County is the ideal pilot jurisdiction for four reasons:

1. **Scale:** King County processes approximately 700,000–900,000 ballots per election cycle — large enough to stress-test multi-county mathematical aggregation
2. **Technical infrastructure:** King County Elections operates one of the most technically sophisticated election administrations in the country and has the engineering capacity to evaluate EIGE independently
3. **Public transparency culture:** King County has a strong track record of public transparency and citizen-accessible audit processes — EIGE's philosophy aligns with this culture
4. **Geographic position:** Washington State's all-mail ballot system provides a well-defined ingestion pipeline that maps cleanly to EIGE's integer intake model

---

## 2. Technical Integration (Shadow Mode)

### What EIGE needs from King County

EIGE requires a single data feed: **integer ballot selection vectors** — the same data already produced by the existing optical scanner and tabulation system. Specifically:

```
Per ballot:
  - selection_vector: list[int]  (one integer per race, encoding the selected candidate)
  - sequence_index: int          (sequential position in the counting stream)

No voter identity information is needed or accepted.
```

This data is already produced by existing tabulation software. Integration requires connecting one integer output stream from the existing system to the EIGE county node API. No modification of the existing system is required.

### What EIGE produces

- Real-time closure status: STABLE | DRIFTED | VIOLATED
- OSCAL 1.5.0 dossier record (for any override attempt, drift event, or anomaly)
- Holon Zero Certificate (post-count)
- Plain-English Public Trust Report

### Deployment

EIGE runs on hardware provided and operated by King County. AxiomZero has no access to King County infrastructure during or after the election. All source code is open-source and independently auditable.

---

## 3. Proposed Scope and Timeline

| Phase | Activity | Duration |
|-------|----------|----------|
| Technical assessment | King County IT team reviews EIGE source code and integration specification | 4 weeks |
| Integration development | Shadow data feed from existing tabulation system | 4–6 weeks |
| Pre-election testing | EIGE run against historical ballot data (already public record) | 2 weeks |
| Election day shadow run | EIGE processes ballots in parallel, zero operational impact | Election cycle |
| Post-certification publication | Both records compared and published | 4 weeks post-certification |

---

## 4. Data Privacy and Sovereignty

EIGE is designed from the ground up for data sovereignty:

- **No voter identity data** is ever accepted, processed, or stored by EIGE
- **Raw ballot data never leaves King County infrastructure** — EIGE is county-tier only in this pilot
- **King County controls all infrastructure** — AxiomZero operates nothing
- **All source code is open-source** — King County IT can verify every line before and after deployment
- **Zero network calls** from EIGE to external systems — the system is fully air-gappable

---

## 5. Compliance

EIGE maps to the following standards relevant to Washington State election administration:

- **WAC 434** — ballot audit log retention requirements (22 months minimum)
- **RCW 29A** — elections administration and canvassing
- **NIST VVSG 2.0** — voting system verification and validation
- **NIST SP-800-53 Rev 5** — security controls (AC, SI, AU, CA, PS families)
- **OSCAL 1.5.0** — machine-readable security posture documentation

Full mapping: [EIGE/COMPLIANCE.md](../COMPLIANCE.md)

---

## 6. What King County Gets

1. **An independent verification layer** that complements existing audit processes at zero operational cost
2. **A publicly publishable record** that demonstrates commitment to transparency and technical rigor
3. **Early access** to a novel tamper-detection approach before wider deployment
4. **Academic co-authorship** on any published evaluation of the pilot results

---

## 7. Next Steps

We propose a 30-minute technical briefing with King County Elections IT staff and the County Auditor's Office to discuss:

1. Integration feasibility assessment
2. Legal review under WAC 434 / RCW 29A
3. Pilot scope and timeline confirmation

**Contact:**  
ThomasCory Walker-Pearson  
Scientific Director, AxiomZero Technologies & Consulting, SPC  
GitHub: https://github.com/wuzbak/Unitary-Manifold-  
Email: [to be added]

---

*Theory, framework, and scientific direction: ThomasCory Walker-Pearson.*  
*Code architecture, test suites, document engineering, and synthesis: GitHub Copilot (AI).*
