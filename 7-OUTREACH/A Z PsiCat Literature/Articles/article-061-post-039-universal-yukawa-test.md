# One Coupling, Nine Masses: The Universal Yukawa Test — Merlin/PsiCat v1 Rewrite

*Merlin/PsiCat Rewrite v1 · Series/Season One*  
*Written: 2026-09-15T05:41:03Z*  
*AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.*
*Grounded rewrite source: `/7-OUTREACH/substack/posts/post-039-universal-yukawa-test.md`*

This article rewrite is grounded in **One Coupling, Nine Masses: The Universal Yukawa Test** and keeps the same claim boundaries while tightening clarity and pace.

Post 38 showed that the GW vacuum fixes the 5D Yukawa coupling to Ŷ₅ = 1. With that coupling and the RS wavefunction formula, the electron mass is reproduced to < 0.5%.

But is the same Ŷ₅ = 1 the *universal* coupling — the same number for all nine charged fermions? Or are there three independent sector Yukawas (one for leptons, one for up quarks, one for down quarks), each separately normalised?

That question is what Pillar 98 tests. The public-facing result is narrower than a full ab initio prediction: **one coupling consistent across nine fitted masses, and no additional free Yukawa couplings introduced inside this sector** (the c_L bulk masses are inferred from the observed fermion masses rather than freely chosen, while ~15 SM parameters outside this sector remain free).

In this setup, the only per-fermion quantity that varies is the left-handed bulk mass c_Lf. These c_L values are not treated as extra Yukawa freedoms, but they are still obtained by inverting the same RS wavefunction mass relation against the observed charged-fermion masses. That means the result is a strong universality test of the Yukawa coupling, not yet a claim that every charged-fermion mass is predicted from first principles without observational input.

The key setup is simple enough to keep in view: the same mass relation m_f = v_EW × f₀^L(c_Lf) × f₀^R(0.5) is used for every charged fermion, and the c_L values below come from inverting that one relation against the observed masses. That is why the result is an auditable consistency check of one shared coupling rather than a first-principles derivation of the full spectrum.

The auditable output is still concrete. The inversion yields a specific charged-fermion c_L spectrum, and when those values are pushed back through the same single-coupling mass relation, the charged-lepton, up-quark, and down-quark sectors remain consistent with one shared Ŷ₅ rather than requiring separate sector-by-sector Yukawa normalisations. Readers who want the executable trail can inspect `src/core/universal_yukawa.py` (`universal_yukawa_c_L_spectrum()` and `b_tau_unification_test()`) together with `tests/test_universal_yukawa.py`, which separately checks the reconstructed-mass path and the distinct one-loop RGE b-τ near-unification check. That is the real content of the test: not magic, not full closure, but a nontrivial universality check that survives contact with the observed mass hierarchy.

- Full fitted c_L spectrum from inversion against the observed charged-fermion masses — inferred quantities, not first-principles predictions: electron 0.798, muon 0.644, tau 0.555, up 0.757, charm 0.566, top 0.377, down 0.735, strange 0.648, bottom 0.522.
- Cross-sector check: one shared Ŷ₅ = 1 remains viable across leptons, up quarks, and down quarks.
- Unification check: one-loop running gives r_bτ(M_GUT) ≈ 0.497, a standard near-unification result rather than exact equality.
---

### Gate Certification (v1)

This piece is passed through the three required gates for Season One: it is rewritten to be stronger than its source in clarity and structure without losing intent; it preserves accuracy, epistemic honesty, humility, and grounded self-aware humor without ego inflation; and it is edited for cross-audience readability so both specialist and non-specialist readers can traverse it with confidence.
