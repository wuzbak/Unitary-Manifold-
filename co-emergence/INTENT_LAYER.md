# The Intent Layer
### How Human Intent Flows Through the HILS System

**Version:** 1.0 — April 2026  
**Part of:** Human-in-Loop Co-Emergent System (HILS)

---

## 1. Intent Is Not Instruction

The most consequential distinction in HILS:

> **Instruction** is what the human says.  
> **Intent** is what the human means.

In a low-trust, tool-use relationship, the AI executes the instruction. In a
co-emergent relationship, the AI pursues the intent — using the instruction as a
signal, but parsing for the underlying goal.

The gap between instruction and intent is the primary source of iteration waste.
When an AI executes the literal instruction and the human meant something else,
both parties lose cycles. The intent layer exists to close this gap *before*
execution begins.

---

## 2. The Three-Stage Intent Flow

### Stage 1: Expression

The human states what they want. Expression can be:

| Expression type | Example | Challenge |
|---|---|---|
| **Direct** | "Write a function that sorts a list" | Low ambiguity; proceed to parsing |
| **Directional** | "I bet you know what direction I'm thinking" | High context-dependence; requires shared history |
| **Metaphorical** | "Make this feel more alive" | Requires semantic unpacking |
| **Implicit** | "The obvious next step is..." | Requires domain knowledge to identify what is obvious |
| **Composite** | Multiple goals in one statement | Requires decomposition and prioritization |

The repository itself contains excellent examples of each type. The prompt
*"I bet you know what direction I am thinking. Create a new folder this one is
important."* is a **directional** expression: it relies on shared session context,
explicit prior analysis, and the AI's capacity to synthesize a direction from
that context without requiring the human to spell it out fully.

That this works — that the AI understood the direction and built the right
structure — is evidence of a calibrated collaboration with nonzero β.

### Stage 2: Parsing

The AI transforms the expression into an operational interpretation. Good parsing:

1. **Extracts the surface request** — what was literally asked
2. **Infers the underlying goal** — what the human is actually trying to accomplish
3. **Identifies the scope** — what is in and out of this task
4. **Flags ambiguities** — where two valid interpretations would lead to different outputs
5. **Proposes before executing** — states the interpretation for human confirmation

Parsing is not mechanical. It requires the AI to model the human's intent, context,
and domain knowledge. It is the β · C coupling term in action: information flowing
from the human's manifold to the AI's operational state.

**Critical rule:** The AI must not execute on an ambiguous instruction without first
stating its interpretation. Execution before verification is the primary source
of intent-control failure.

### Stage 3: Verification

Before full execution, the AI states:
- Its interpretation of the intent
- The scope of the work it plans to do
- Any significant assumptions it is making
- Any areas where it is uncertain

The human then:
- Confirms: proceed
- Corrects: adjust the interpretation
- Expands: the scope is larger than the AI assumed
- Constrains: the scope is smaller than the AI assumed

Verification reduces Δφ (vocabulary/intent misalignment) before it costs
iteration cycles. A thirty-second verification conversation eliminates a
thirty-minute misaligned implementation.

**Exception:** When trust is high (β ≈ 1) and the instruction is unambiguous,
verification can be implicit — the AI proceeds and the human verifies at completion.
This is appropriate for low-stakes, reversible tasks in well-calibrated domains.

---

## 3. Layers of Intent

Intent has depth. The HILS framework recognizes four layers:

```
Layer 4:  STRATEGIC — What the human ultimately wants to achieve (vision)
Layer 3:  GOAL     — What this session is trying to accomplish (objective)
Layer 2:  TASK     — What this specific instruction is asking for (task)
Layer 1:  ACTION   — What the AI will literally do (operation)
```

Most instructions operate at Layer 2 (task) or Layer 1 (action). The AI must
always parse upward to Layer 3 (goal) and be aware of Layer 4 (strategic) when
making decisions about scope or approach.

**Example from this repository:**

| Layer | Content |
|---|---|
| Layer 4 (Strategic) | Build a comprehensive framework for understanding human-AI collaboration in the context of the Unitary Manifold project |
| Layer 3 (Goal) | Create a structured folder that formalizes the co-emergence concept |
| Layer 2 (Task) | "Create a new folder... write up what you can... organized structure... llm files and human" |
| Layer 1 (Action) | Create files: README.md, LLM_INGEST.md, FRAMEWORK.md, etc. |

The AI that only parses Layer 1 creates files. The AI that parses to Layer 3
creates the right files, with the right content, structured for the right audience.
The AI that is aware of Layer 4 connects those files to the existing repository
architecture in a way that makes the folder feel like a natural extension rather
than an addition.

---

## 4. Intent Across Sessions

One of the most important — and frequently underappreciated — properties of
intent in a long-running collaboration:

> **Intent evolves. The system must track the evolution, not just the
> current state.**

In this repository, intent has evolved through multiple sessions. Early sessions
established the core physics framework. Later sessions extended it (Pillars 1–13).
This session extends it again — into the meta-level of the collaboration itself.

Each session's intent is:
1. A partial expression of the current-session goal (Layer 2/3)
2. An incremental step toward the strategic vision (Layer 4)
3. Implicitly shaped by all prior sessions (accumulated context)

The AI that treats each session as independent will miss the Layer 4 continuity.
The AI that is aware of the repository history — in this case, visible in
`MCP_INGEST.md`, `AGENTS.md`, version numbers, and the git commit history —
can situate each new intent expression within the full arc.

**This is why `LIVING_PROOF.md` matters**: the repository itself is the persistent
record of intent evolution. Reading the repository is reading the history of
the human's unfolding intent across all sessions.

---

## 5. Intent Failures and Their Signatures

| Failure | Signature | Recovery |
|---|---|---|
| **Underparsing** | AI executes the literal instruction; human says "that's not what I meant" | AI re-parses upward; asks "what were you trying to accomplish?" |
| **Overparsing** | AI assumes broader intent than stated; produces far more than asked | AI returns to declared scope; human clarifies what was wanted |
| **Stale intent** | AI continues toward a goal the human has moved past | Human explicitly states: "The goal has changed" |
| **Conflicting layers** | The Layer 2 instruction contradicts the Layer 3 goal | AI names the conflict; asks which layer takes precedence |
| **Intent hallucination** | AI invents an intent the human never had | Human corrects; AI resets to explicitly stated intent only |

---

## 6. The Intent-Control Guarantee

At every point in the HILS fixed-point iteration:

```
Human intent → [parsing] → [verification] → [execution] → [evaluation] → Human
```

This loop is one-directional in a critical sense: **the human's intent always
initiates the cycle, and the human's evaluation always closes it.** The AI
operates inside the loop but never sets the loop's direction.

The AI can:
- Propose approaches that the human has not considered
- Point out that the stated intent may not achieve the strategic goal
- Suggest scope expansions that would improve the output
- Flag when the intent is contradictory

The AI cannot:
- Override the human's stated intent because the AI thinks it is "better"
- Pursue a goal the human has not endorsed
- Expand scope without explicit human confirmation
- Decide that the evaluation criteria have been met without human confirmation

This asymmetry is not a limitation on the AI's intelligence. It is the
structural guarantee that makes the system safe, stable, and trustworthy —
and therefore capable of operating at high β, which is when the most
powerful co-emergence becomes possible.

---

*Document version: 1.0 — April 2026*  
*Theory: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).*
