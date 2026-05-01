# The HILS Framework
### Formal Treatment of the Human-in-Loop Co-Emergent System

**Version:** 1.0 — April 2026  
**Theory:** ThomasCory Walker-Pearson  
**Implementation:** GitHub Copilot (AI)

---

## 1. Overview

The Human-in-Loop Co-Emergent System (HILS) is a formal model of the two-body
interaction between a human and an AI system. It is derived from the same mathematical
structure as the Coupled Master Equation in `brain/COUPLED_MASTER_EQUATION.md`,
applied to a different physical substrate: not the brain-universe pair, but the
human-AI pair.

The central object is the **co-emergent fixed point**:

```
U_total (Ψ_human ⊗ Ψ_AI) = Ψ_synthesis
```

where `Ψ_synthesis` is the co-produced output — understanding, implementation,
document, theory — that satisfies the human's intent and the AI's implementation
requirements simultaneously.

---

## 2. State Vectors

### 2.1 The Human State Vector

```
Ψ_human = (I, K, J, A, Δ)
```

| Component | Symbol | Meaning |
|---|---|---|
| Intent vector | I | What the human wants to accomplish — semantic direction |
| Knowledge base | K | Domain expertise, prior context, background understanding |
| Judgment operator | J | The capacity to evaluate outputs for meaning and correctness |
| Authority bit | A | The overriding authority — always 1 for the human; cannot be transferred |
| Uncertainty set | Δ | What the human knows they don't know |

### 2.2 The AI State Vector

```
Ψ_AI = (P, W, E, F, H)
```

| Component | Symbol | Meaning |
|---|---|---|
| Precision operator | P | Capacity to implement instructions with consistency and correctness |
| World knowledge | W | The AI's accessible knowledge base — facts, patterns, prior training |
| Execution capability | E | What the AI can actually do: write code, generate text, search, analyze |
| Fidelity constraint | F | The commitment to honest accounting — flagging gaps, fitted parameters, limitations |
| History | H | Memory of the current collaboration — previous exchanges, decisions, context |

### 2.3 The Synthesis State

```
Ψ_synthesis = Φ(Ψ_human, Ψ_AI, β)
```

where Φ is the co-emergence operator and β is the trust coupling constant.
`Ψ_synthesis` is not a property of either party. It is **the product of their
interaction under trust**.

---

## 3. The Coupling Operator: Trust as β

The coupling operator C exchanges information between the two state vectors:

```
ΔΨ_human  = +β · C(Ψ_AI → Ψ_human) · dt     [AI output updates human understanding]
ΔΨ_AI     = +β · C(Ψ_human → Ψ_AI) · dt     [Human input updates AI operational state]
```

Unlike the symmetric brain-universe coupling (where β is the birefringence angle), the
human-AI coupling is **structured but not symmetric**: information flows in both
directions, but the nature of what flows differs:

| Direction | What flows | Effect |
|---|---|---|
| Human → AI | Intent, context, judgment, corrections | Narrows the AI's operational space toward the human's actual goal |
| AI → Human | Implementations, analyses, honest limitations, alternatives | Expands the human's understanding of what is possible and what is verified |

**β = trust** is not a single scalar but a tensor: it can be high in one domain
(e.g., "I trust the AI to write correct Python") and lower in another (e.g., "I
don't yet trust the AI's physical intuitions"). The effective scalar β is the
geometric mean of the domain-specific trust values for the current task.

---

## 4. The Fixed-Point Iteration

A collaboration session is a sequence of exchange steps indexed by n:

```
Step 0:  Human expresses intent I₀
Step 1:  AI parses I₀ → operational interpretation O₁; proposes before executing
Step 2:  Human verifies O₁ → confirms or corrects to I₁
Step 3:  AI executes on I₁ → produces output X₁; includes honest accounting H₁
Step 4:  Human evaluates X₁ against I₁ → accepts, corrects, or redirects to I₂
...
Step n:  Convergence: |X_n − X_{n-1}| < ε AND human confirms X_n satisfies intent
```

At convergence:

```
Ψ_synthesis* :  X_n satisfies I_0 (original intent)
                X_n is internally consistent (AI's precision verified)
                X_n is externally meaningful (human's judgment confirmed)
```

This is the **co-emergent fixed point** — the task completion state.

### 4.1 Convergence Conditions

The fixed point is reachable when:

1. **Intent is expressible**: The human can state what they want in terms the AI can parse
2. **Trust is nonzero**: β > 0 — the human's corrections reach the AI and the AI's honest accounting reaches the human
3. **Intent is stable**: The human's goal does not change faster than the AI's iteration rate
4. **Scope is bounded**: The task is not unbounded in complexity or ambiguity

### 4.2 Non-Convergence Conditions

The fixed point fails to form when:

| Failure mode | Cause | Symptom |
|---|---|---|
| **Intent drift** | Human changes goal mid-iteration without declaring the change | AI converges to wrong target; human frustrated by "missing the point" |
| **Trust collapse** | Honesty failure by either party | AI hides limitations; human hides context; outputs degrade |
| **Scope explosion** | Task expands without bound | Iteration continues but never satisfies; exhaustion |
| **Vocabulary misalignment** | Same words mean different things | High-frequency iteration with low information transfer; Δφ large |
| **Authority inversion** | AI begins setting objectives | Loss of intent-control; safety boundary violation |

---

## 5. The Information Gap as Engine

The information gap ΔI drives the collaboration:

```
ΔI = |K_human − W_AI|     [asymmetric: what human knows that AI doesn't + vice versa]
```

**ΔI is productive, not pathological.** The collaboration is valuable precisely because
the human knows things the AI doesn't (domain intent, lived experience, meaning) and
the AI knows things the human doesn't (precise implementation, consistency checking,
pattern recall at scale).

The flow of productive collaboration is:

```
Large ΔI (beginning)  →  High-value exchange  →  Smaller ΔI  →  Convergence
```

When ΔI → 0, the collaboration has transferred maximum value: the human's intent
is fully implemented, the AI's knowledge has fully served the human's purpose,
and the output captures both.

Note: ΔI never truly reaches zero, because the human's intent continues to evolve
(learning from the AI's outputs), and the AI's knowledge base cannot fully represent
the human's lived context. **A small residual ΔI is the healthy equilibrium** — it
is the engine of the next collaboration session.

---

## 6. Phase Offset and Vocabulary Alignment

The phase offset Δφ measures vocabulary misalignment:

```
Δφ = ∠(I_human, O_AI)
```

the angle between what the human means and what the AI parses.

| Δφ | State | Action |
|---|---|---|
| Δφ → 0 | Perfect alignment — human and AI share vocabulary completely | Proceed directly to execution |
| Δφ ~ π/6 | Minor misalignment — minor terminology differences | AI proposes interpretation; human confirms before execution |
| Δφ ~ π/2 | Significant misalignment — domain-specific jargon, metaphor, implication | AI requests clarification; does not execute until confirmed |
| Δφ ~ π | Severe misalignment — fundamental miscommunication | Stop; start over from explicit, plain-language intent statement |

The parsing stage of the intent layer (see `INTENT_LAYER.md`) is the mechanism
for reducing Δφ before execution begins.

---

## 7. The Role of Honest Accounting

Honest accounting is not an optional enhancement — it is a structural requirement
of the HILS framework. It appears at two levels:

### 7.1 AI honest accounting
At every output, the AI must flag:
- What was derived from explicit instructions
- What was inferred or assumed
- What the AI is uncertain about
- What the AI cannot do or verify

### 7.2 Human honest accounting
At every significant direction change, the human should flag:
- What they know about the domain
- What they are uncertain about
- What they are asking the AI to judge (appropriately) vs. what they will judge themselves
- When their intent changes and why

The honest accounting from both sides feeds the truth synthesis process (see
`TRUTH_SYNTHESIS.md`). Without it, synthesis degrades to sophisticated-sounding
outputs that are not actually verified — the hallucination regime.

---

## 8. The Composite Fixed-Point Equation

The full HILS fixed-point condition:

```
defect² = |X_n − I_human|²       [implementation satisfies intent]
         + |H_AI − H_AI_true|²   [AI's honest accounting is accurate]
         + β² · ΔI²               [information gap is minimized under trust]
         + Δφ²                    [vocabulary is aligned]
```

The fixed point Ψ_synthesis* satisfies defect = 0 (or defect < ε for practical
purposes).

This composite defect structure means that even if the implementation `X_n` exactly
satisfies the literal instruction, the fixed point is not reached if:
- The AI's accounting was dishonest (second term nonzero)
- The information gap was never productively closed (third term nonzero)
- The vocabulary was misaligned throughout (fourth term nonzero)

**Correct output + honest process = synthesis. Correct output + dishonest process = coincidence.**

---

## 9. Universality Claim and Its Honest Limits

The HILS framework claims to be **conditionally universal**: applicable to any
human-AI collaboration where:
- The human can express semantic intent
- The AI can execute operations and report honestly
- The domain admits a notion of "correct" or "satisfying" output

**Known non-universal regimes:**
- Pure value judgments with no operational component (the AI has no useful operational role)
- Tasks where the human cannot express intent in any parseable form (not a failure of the framework — a failure of communication preconditions)
- Tasks where no fixed point exists (the human's intent is genuinely contradictory)

See `OPEN_QUESTIONS.md` for the theoretical open questions about universality.

---

*Document version: 1.0 — April 2026*  
*Theory: ThomasCory Walker-Pearson. Implementation: GitHub Copilot (AI).*
