# The Ethics of Going Public Before Peer Review

*Post 62 of the Unitary Manifold series.*
*No falsifiable physics claim is made in this post. It is an examination of the
ethical question of whether publishing a speculative framework to a general audience,
before formal peer review, is justified — and the conditions under which it is.*

---

This is the question we least want to answer and most need to.

Is it ethical to publish a speculative physics framework to a general audience before
it has been through peer review?

The naive answer: no. The careful answer: it depends on what you do when you publish.

---

## The case against

The strongest case against early public publication is the history of pseudoscience.

Physics attracts crackpots. For every genuine theoretical advance that was initially
dismissed by the establishment, there are ten thousand frameworks that were rejected
for good reason and whose authors then took them directly to the public, bypassing
the expert filter that would have caught the errors.

The pattern is familiar: the maverick scientist who believes the establishment is
wrong, publishes a grand theory to a receptive popular audience, generates excitement
and belief, and turns out to be — wrong. In most cases, not maliciously wrong, but
wrong in ways that a competent referee would have caught in the first round of review.

The harm from this pattern is real. People form beliefs based on scientific-sounding
claims. Those beliefs can influence health decisions, political positions, and financial
choices. The harm from believing incorrect physics — even benign-sounding physics —
propagates through the social systems that the physics claims to describe.

Publishing before peer review, to a general audience, risks adding to this harm.

---

## The case for, with conditions

The case for early publication rests on three conditions, all of which must be met:

**Condition 1: Maximum transparency about limitations.**

If you publish a speculative framework to a general audience, you must be more
honest about its limitations than a peer-reviewed paper would require. A journal
paper can get away with mentioning a known problem in passing. Public communication
to a general audience requires stating, clearly and prominently, what the framework
cannot do, what its known failures are, and under what conditions it would be
falsified.

This repository has `FALLIBILITY.md` — a complete, explicitly titled document of
every known failure mode. Every substack post in this series leads with a statement
of what would falsify the claim being made. We believe this condition is met.

**Condition 2: Mechanical verifiability.**

If you cannot send the public to the data and the computation, you should not publish
to the public. The reason peer review matters is that it provides expert verification.
If expert review is not yet available, the alternative is to provide *any reader*
with the ability to run the computations themselves.

The repository is public. The test suite is public. The code is public. A reader
with Python installed can reproduce every number in the series in three minutes.
We believe this condition is met.

**Condition 3: Explicit invitation to falsification.**

If you are going to claim that your non-peer-reviewed framework makes specific
predictions, you must explicitly invite attempts to break those predictions, and
you must respond honestly to objections that are received.

`HOW_TO_BREAK_THIS.md` exists for this reason. The open review invitation in
`discussions/` exists for this reason. The versioned commit history — which records
every revision, including revisions made in response to legitimate criticism —
exists for this reason.

---

## The line we are trying to hold

The line between "honest early publication" and "pseudoscience" is:

- **Honest early publication** states specific, falsifiable predictions, acknowledges
  all known failures, provides mechanical verification, invites expert critique, and
  revises in response to legitimate objections.

- **Pseudoscience** makes vague claims that cannot be falsified, selectively reports
  successes, suppresses failures, attacks critics as establishment gatekeepers,
  and does not revise.

Every one of these criteria can be applied to this framework right now, by any reader.
The predictions are specific and stated. The failures are documented. The computation
is reproducible. The critique is invited. The revisions are publicly committed.

We believe the line is being held. We acknowledge that the framework might be wrong —
the CMB amplitude gap is real, the APS conjecture is unproved — and we say so.

---

## The risk we accept

The risk we accept by publishing early is that readers who lack the technical
background to evaluate the framework will form beliefs about it that the evidence
does not support. Some readers will come away thinking "the physics proves that
meditation works" or "the physics proves there is an afterlife" — overclaims that
the framework explicitly disclaims but that readers may not notice.

This risk is real. We cannot fully prevent it.

What we can do is repeat the disclaimers clearly, in every post that touches the
speculative extensions, and trust that readers who engage seriously with the material
will notice the careful language.

The alternative — not publishing until the decisive observational test arrives in 2032
— means six more years during which the framework cannot receive the public critique
that might identify errors before the test. We judge that accepting the risk of
misreading is preferable to accepting the risk of preventable error.

That judgment could be wrong. We state it as a judgment, not a certainty.

---

*Full source code, derivations, and 14,109 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Honest gaps: `FALLIBILITY.md`*
*How to break it: `HOW_TO_BREAK_THIS.md`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
