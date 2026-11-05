# Pillar 1134 — Rare B-meson decay probes and the “zeptoverse”

🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM

**Status:** Adjacent research track; no Unitary Manifold (UM) prediction is
implemented or tested here.
**Date:** 2026-11-05
**Source module:** `src/core/pillar_1132_1134/pillar1134_rare_decay_probes.py`

The public import remains `src.core.pillar1134_rare_decay_probes`.
The source is sharded for directory hygiene; no implementation is duplicated.
**Tests:** `tests/test_pillar1134_rare_decay_probes.py`
**Article:** `7-OUTREACH/A Z PsiCat Literature/Articles/article-356-post-1134-the-zeptoverse-and-rare-b-decays.md`
**Tracker:** `docs/mas_tracker.yml`

## Scope and evidence

On 3 November 2026, LHCb reported **evidence**, not observation or discovery,
for the rare decay \(B^0\to\mu^+\mu^-\): 3.0σ using Run 3 data and 3.2σ when
combined with Run 1 and Run 2. The collaboration reports that the measurements
are consistent with Standard Model (SM) expectations. The statistical labels
“evidence” around 3σ and “observation” around 5σ are conventional thresholds,
not physical laws. Neither label establishes a new particle or a departure
from the SM.

The paper also reports improved measurements of \(B_s^0\to\mu^+\mu^-\),
including its effective lifetime. Branching fractions, the effective lifetime,
and the \(B^0/B_s^0\) branching-fraction ratio can provide complementary future
tests of beyond-SM physics. Rare leptonic decays constrain Wilson coefficients
in the weak effective theory (WET); interpreting them requires specifying the
operator basis, coefficients, and matching assumptions.

“Zeptoverse” is a popular-science framing used in University of Manchester
coverage distributed by Phys.org. It is not terminology used to establish a
new physical sector in the LHCb paper. The framing refers to the short-distance
scales that rare decays can indirectly probe.

## What this pillar implements

`src/core/pillar_1132_1134/pillar1134_rare_decay_probes.py` provides:

- a small classifier that distinguishes below-threshold results, conventional
  3σ-level evidence, and conventional 5σ-level observation;
- a generic prediction-versus-measurement residual using caller-supplied
  independent uncertainties in common units.

There are no hard-coded UM model predictions, rates, or branching-fraction
decimal values. The reported LHCb significances are provenance metadata only.
The generic comparison does not account for correlations, non-Gaussian
likelihoods, nuisance parameters, or a full goodness-of-fit procedure.

## What is missing before a UM test

A quantitative comparison with UM/KK physics cannot be made from this result
alone. It first needs an explicit, independently reviewable:

1. KK/new-state spectrum and parameter values;
2. couplings to the relevant quark and lepton currents;
3. matching calculation into a stated WET operator basis, with scale and
   renormalization conventions;
4. predicted branching fractions, effective lifetime and/or ratio, with
   theoretical uncertainties and correlations;
5. comparison protocol against the experimental likelihood and SM inputs.

These ingredients have not been derived in this pillar. Therefore this work
does **not** claim evidence for UM, test UM against LHCb, or discover a new
particle.

## Provenance and references

- LHCb collaboration paper (submitted for publication): [arXiv:2611.00230](https://arxiv.org/abs/2611.00230)
- LHCb result summary, 3 November 2026: [Evidence for the decay \(B^0\to\mu^+\mu^-\) and improved measurements of \(B_s^0\to\mu^+\mu^-\)](https://lhcb-outreach.web.cern.ch/2026/11/03/evidence-for-the-decay-b0%e2%86%92%ce%bc%ce%bc-and-improved-measurements-of-bs0%e2%86%92%ce%bc%ce%bc/)
- CERN public release, 3 November 2026: [LHCb finds evidence of one-in-ten-billion particle decay](https://home.cern/lhcb-finds-evidence-of-one-in-ten-billion-particle-decay/)
- University of Manchester coverage via Phys.org (source of the “zeptoverse” framing): [Physicists step closer to the ‘Zeptoverse’ after 42-year particle search](https://phys.org/news/2026-11-physicists-closer-zeptoverse-year-particle.html)

The module’s experimental significance examples follow the LHCb summary and
paper. Public-facing “zeptoverse” language is attributed to the university
coverage, not to the collaboration’s technical terminology.
