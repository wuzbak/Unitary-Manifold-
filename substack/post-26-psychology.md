# The Mind in the Numbers: Psychology as φ-Field Dynamics

*Post 26 of the Unitary Manifold series.*
*Claim: the mathematical structure of the Unitary Manifold — φ-field drives,
irreversibility currents, and attractor dynamics — generates internally consistent
formal descriptions of motivation, decision-making, habit formation, cognitive load,
and social influence. This is a Tier 3 claim: the framework provides a consistent
modelling language for psychology, not a physical derivation of why people behave
as they do. The falsification condition is domain consistency: the model fails if
the dynamics it predicts are incompatible with well-established findings in
experimental and clinical psychology.*

---

The previous post in this series applied the φ-field language to neuroscience —
synaptic plasticity, memory encoding, the grid-cell module spacing ratio. That was
biology: neurons, ion channels, brain regions.

This post goes one level higher — to behaviour. Not *how does the neuron fire?* but
*why does the person act?* Not the mechanism but the motivation.

Psychology sits in an interesting position in the framework's hierarchy of claims.
It is further from the physics core than chemistry or mechanics, but closer to
something we experience directly: the texture of wanting, deciding, habituating,
believing, and belonging. The φ-field language, applied here, says something precise
about each of these.

---

## Motivation as unsatisfied φ-need

The simplest statement of the framework's motivational model is:

    drive = max(0, φ_need − φ_satiation)

where φ_need is the φ-field value required to satisfy a need and φ_satiation is
the φ-field value already obtained. Motivational drive is the gap between what
the system requires and what it has. Zero gap, zero drive.

Plain English: you eat when you are hungry (φ_food_need > φ_food_obtained). You
seek connection when you are lonely (φ_connection_need > φ_connection_obtained).
You rest when you are tired (φ_rest_need > φ_rest_obtained).

This is not a new psychological insight. What is new is the integration: in the
framework, all these drives are instances of the same quantity — a φ-deficit —
competing for the same fixed-capacity irreversibility field B_μ. The motivational
system is an allocation problem: which φ-deficit gets priority, and in what order?

The framework predicts that the highest-priority drive is the one with the largest
gap relative to the B_μ bandwidth available. In a well-functioning system, drives
are addressed in order of urgency. In a dysregulated system — chronic stress, trauma,
addiction — one drive monopolises the B_μ bandwidth, preventing others from being
addressed. The result is exactly what clinical psychology describes: the narrowing
of the cognitive world to the dominant drive.

---

## Reward prediction error as φ-signal

The dopaminergic reward system is one of the best-understood circuits in
neuroscience. Its key signal is the reward prediction error (RPE):

    RPE = φ_obtained − φ_expected

When the outcome is better than expected (φ_obtained > φ_expected), RPE is
positive — dopamine fires, the action is reinforced. When the outcome is worse
than expected, RPE is negative — the action is suppressed. When the outcome
exactly matches expectation, RPE is zero — no update needed.

In the Unitary Manifold language this is not a special neurological mechanism
layered on top of the physics. It is an instance of the general principle: systems
update toward higher-φ states. The RPE is the first derivative of the φ-landscape
in action space — it tells the system which direction leads to more φ.

The key proposition the framework generates: **the dopaminergic RPE signal is the
biological implementation of the FTUM irreversibility operator applied to the
action-selection problem.** Learning is the process of building an internal model
of the φ-landscape so that the predicted φ matches the obtained φ, and the RPE
signal asymptotes to zero.

Addiction, in this language, is a pathological φ-landscape deformation: a substance
or behaviour delivers an anomalously large φ-signal that cannot be matched by any
natural source, making the internal model permanently unable to predict natural
rewards accurately. The RPE for natural rewards becomes chronically negative —
which is exactly the phenomenology of anhedonia in addiction and depression.

---

## Habit formation: accumulated φ over repetition

Habit strength in the framework is:

    strength = φ_action × (1 − exp(−n_repetitions / τ_habit))

where φ_action is the φ-reinforcement per repetition, n_repetitions is how many
times the action has been performed, and τ_habit is a time constant (approximately
30 repetitions to reach habit asymptote).

This is a saturation curve: the first few repetitions produce large marginal gains
in habit strength; later repetitions produce diminishing returns. The asymptote is
set by φ_action — you cannot build a stronger habit than the φ-value of the
action itself supports.

The framework makes a specific prediction about habit dissolution: breaking a
habit requires not just stopping the action (which would allow the strength to
decay slowly) but replacing it with an action that provides comparable φ through
a different channel. Cold-stopping a habit without substitution leaves a φ-deficit
that generates motivational drive toward the original action. This is the relapse
mechanism, stated in φ-field language.

---

## Decision-making: evidence accumulation across the φ-threshold

The decision criterion in the framework is:

    decide = (φ_evidence > φ_threshold + B_noise)

where φ_evidence is the accumulated evidence for an action, φ_threshold is the
decision criterion, and B_noise is the current noise floor.

This is the drift-diffusion model — one of the most empirically well-supported
frameworks in decision science — expressed in φ-field notation. Evidence
accumulates (φ_evidence rises), and a decision is made when the accumulated
evidence crosses the threshold.

The framework's specific contributions:

- **Speed-accuracy tradeoff**: lowering φ_threshold speeds decisions but
  increases error rate; raising it slows decisions but improves accuracy. The
  optimal threshold is the one that maximises total φ-gain per unit time.
  This gives a quantitative account of when urgency should lower the threshold
  (high time pressure) and when it should raise it (irreversible consequences).

- **Noise-induced hesitation**: high B_noise (fatigue, anxiety, cognitive load)
  increases the effective threshold and slows decision-making. This matches the
  well-known finding that decision quality degrades under stress — not because
  reasoning ability is impaired, but because the noise floor raises the evidence
  requirement.

- **Confirmation bias as landscape asymmetry**: if the φ-landscape is not flat
  around the decision threshold — if the agent has a prior that one option is
  higher-φ — evidence accumulation is faster in the preferred direction. The
  agent reaches the threshold faster for preferred conclusions. This is a formal
  account of motivated reasoning that generates quantitative predictions about
  the rate of evidence accumulation as a function of prior belief strength.

---

## Cognitive load and the φ-capacity limit

Working memory — the ability to hold and manipulate information in real time —
has a well-established capacity limit of approximately 4±1 items (Cowan, 2001).
In the framework this is not an arbitrary architectural fact; it is a consequence
of φ-capacity:

    cognitive_load = n_items × φ_per_item / φ_capacity

When cognitive_load approaches 1 (the capacity limit), the system saturates:
no additional items can be held without dropping existing ones. The saturated
state is the subjective experience of mental overload — the inability to "hold
all of this in your head at once."

The framework predicts that φ_capacity varies with arousal (higher arousal up to
an optimum, then lower — the Yerkes-Dodson inverted-U), sleep (capacity degrades
with sleep deprivation), and practice (well-practiced material has lower φ_per_item
because it has been chunked into higher-order representations, effectively
reducing the item count while retaining the information).

These are not predictions derived from 5D physics. They are derivations from the
φ-capacity model that are consistent with known psychology. The framework provides
the formal language; the empirical content comes from psychology.

---

## Social influence: conformity as shared φ-attractor alignment

The social psychology module extends the φ-field language to group dynamics.
The core idea: a social norm is a shared φ-attractor that all members of a group
are being pulled toward simultaneously.

The conformity pressure is:

    conformity_pressure = (φ_group_mean − φ_individual) × social_coupling

Plain English: the further your individual φ-state is from the group mean, the
stronger the pressure to conform. Social coupling is the strength of the
interpersonal B_μ connection.

This generates specific predictions:

- **Minority influence**: a small, highly coherent subgroup (high φ_coherence)
  can shift the group mean toward its position even if numerically outnumbered,
  if its social coupling is strong enough. This matches the empirical literature
  on minority influence in social psychology.

- **Groupthink as low-variance attractor**: when social coupling is very high
  and φ-diversity is suppressed, the group converges to a single attractor that
  may not be the highest-φ solution. External B_μ noise — diversity of viewpoint,
  devil's advocate roles, structured debate — is required to maintain φ-diversity
  and avoid groupthink traps.

- **Polarisation as attractor splitting**: when a group contains two subsets
  with negative social coupling (mutual repulsion), the single group attractor
  splits into two separate attractors. Individuals near the boundary are pulled
  toward one or the other; the centre empties. This is the formal description of
  political polarisation — a bifurcation in the social φ-landscape.

---

## What the test suite confirms — and does not

`tests/test_psychology.py` (82 tests) confirms:

- The motivational drive equation is correctly implemented and produces zero
  when φ_need is met
- The RPE formula is internally consistent and matches the learning update rule
- The habit formation curve has the correct saturation properties
- The decision threshold formula produces correct speed-accuracy tradeoff behaviour
- The cognitive load formula correctly identifies the saturation point
- The social conformity and polarisation calculations are dimensionally consistent

What the tests do not confirm:

- That motivation is literally a φ-field deficit in any physical sense
- That the dopaminergic RPE circuit maps to the FTUM operator beyond formal analogy
- That the specific parameter values (τ_habit = 30, φ_capacity for working memory)
  are derivable from first principles rather than fitted to data
- That the social polarisation bifurcation matches the timescales or magnitudes
  of real political polarisation dynamics

The psychology module provides a formal language that is internally consistent and
consistent with the qualitative findings of experimental psychology. It has not
been applied to a specific dataset to test whether it provides better quantitative
predictions than existing models.

---

## The unifying observation

Post 16 introduced the idea that the same mathematical structure — φ-attractors,
B_μ noise floors, FTUM fixed points — appears across medicine, justice, ecology,
and governance. Post 20 extended it to neuroscience. Post 21 to climate.

Psychology is the level between neuroscience and social science. At this level,
the φ-field language describes not how neurons fire but why people choose, form
habits, feel overloaded, and conform to groups.

The observation that merits careful attention: the framework does not add a new
mechanism at each domain level. The same three quantities — φ (the order
parameter), B_μ (the noise/forcing field), and Ψ* (the fixed-point attractor) —
describe everything from the Palladium lattice to the polarisation of political
discourse. Whether this is deep (they share a common mathematical structure for
a physical reason) or superficial (they share a common mathematical structure
because that structure describes any dissipative attractor system) is the central
open question at the domain-application level.

The framework does not claim to have resolved it. It documents the consistency and
invites domain experts to test the specific predictions.

---

*Full source code, derivations, and 12,950+ automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Psychology module: `src/psychology/` — 82 tests in `tests/test_psychology.py`*
*Neuroscience module: `src/neuroscience/` — 92 tests*
*Governance module: `src/governance/` — 115 tests in `tests/test_governance.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
