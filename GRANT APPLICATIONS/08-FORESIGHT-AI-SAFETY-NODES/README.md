# Foresight Institute — AI for Science & Safety Nodes

**Status at 2026-11-06:** the published AI for Science & Safety Nodes RFP closed **October 31, 2026 at 23:59 PDT**. The official pages found do not publish a next-cycle date. This is a future-cycle watch, not an open application.

## Why it merits monitoring

The 2026 RFP included a “Coordination and accountability” track with areas including human empowerment and AI insurance/open governance. The call describes improving interaction among people and AI systems and supporting independent assessment of AI risk. These themes are relevant to AxiomZero's HILS/Unitary Pentad governance work, but thematic overlap is not evidence that the framework reduces AI risk or meets a specific future RFP.

Foresight says typical grants for the RFP range from **$30,000 to $100,000**, with smaller amounts for some focus areas, including open governance. Applications were accepted from individuals, teams, and organizations, including for-profit organizations. The program also prioritizes applicants who will contribute in person to its San Francisco or Berlin Nodes. These were terms of the closed 2026 call and must be reconfirmed for any future round.

## Future concept — not a current proposal

Do not submit or pre-commit to a project before a new RFP is published. If a future call retains an open-governance or human-empowerment track, consider one bounded evaluation of a specific HILS/Unitary Pentad process or software artifact. The proposal would need to define an operational governance question, an appropriate comparison or evaluation method, independent reviewers, failure criteria, and a public artifact. The theory's physics claims must remain separate from governance claims.

### Public-evidence-backed research concept

**Working title:** *Reproducible Evaluation of Human-Approval and Escalation Rules for AI-Assisted Decisions.*

**Existing artifact:** the public [governance lane classifier](../../src/core/governance_lane_classifier.py), including classification/escalation logic (lines 58–102) and lane-dependent quorum, dissent, and review rules (lines 166–188). The [Pentad Lane Audit](../../5-GOVERNANCE/PENTAD_LANE_AUDIT.md) describes the implementation and its epistemic boundaries. This is a more specific starting artifact than a claim that the entire framework ensures AI safety.

**Draft research narrative:** AxiomZero proposes to evaluate whether a documented, lane-based decision protocol makes human-approval and escalation decisions more reproducible across controlled AI-assisted decision scenarios. The study would examine routine, sensitive, and critical cases, including conflicting instructions and proposed scope changes. A public scenario corpus would distinguish the protocol's expected classifications from independent reviewers' judgments; neither would be presented as objective ground truth merely because the software produced it. The evaluation would compare classifier-assisted review with review of the same written policy without the classifier, using a preregistered assignment and analysis plan.

**Proposed work and outputs:**

1. Define the decision-policy specification, synthetic non-sensitive cases, independent annotation procedure, and intended use before selecting evaluation cases.
2. Freeze the classifier version and comparison procedure; separate development cases from held-out cases.
3. Measure reviewer agreement, missed escalations, unnecessary escalations, and incomplete approval/dissent records. Define error categories, reference labels, denominators, and decision thresholds before evaluation; no baseline results or improvement targets are asserted here.
4. Publish the corpus, reproducible evaluation harness, disagreement analysis, limitations, and a transparent go/no-go recommendation for further research.

**Novelty gate:** a prior-art review must compare existing approval workflows, policy engines, and human-oversight research. The current evidence supports an implemented artifact to evaluate, not a claim that lane classification, quorum rules, or human oversight is new. A useful negative result is an acceptable research outcome.

**Limits:** this would be a controlled governance-engineering evaluation, not proof of deception detection, deployment safety, regulatory compliance, or catastrophic-risk reduction. A classifier recommendation does not establish that a downstream system actually enforces human approval. Independent reviewers and any human-participant approvals, consent arrangements, and data protections remain to be confirmed; none is represented as secured.

## Gates

- Monitor Foresight's official grants page; no next deadline or recurrence is confirmed.
- Map the future call's exact work areas and award terms before drafting.
- Confirm availability for any in-person participation the call prioritizes.
- Obtain independent subject-matter review; do not claim external governance outcomes or AI-risk reduction without evidence.

**Official sources:** [AI for Science & Safety Nodes RFP](https://foresight.org/grants/ai-science-safety-nodes-rfp/); [Coordination and accountability RFP](https://foresight.org/grants/ai-science-safety-nodes-rfp-coordination-and-accountability/).
