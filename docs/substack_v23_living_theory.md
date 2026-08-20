# v23 — A Theory That Argues With Itself

*Posted on Substack — AxiomZero / The Unitary Manifold*
*ThomasCory Walker-Pearson · August 2026*

---

Most physics frameworks are presented as finished arguments. Here is the theory. Here is the evidence. Believe it.

The Unitary Manifold does not work that way.

v23 is the sprint that made that explicit — not just in documentation, but in a tool you can open in your browser right now and use to argue back.

---

## What We Actually Believe, and Why

The framework rests on a single geometric ansatz: five-dimensional Kaluza-Klein compactification with a braided winding number n_w = 5. Everything else — the spectral index, the tensor-to-scalar ratio, the birefringence angle, the Higgs mass range, the neutrino mass ordering preference — follows from that choice.

Three claims carry the most weight:

**1. The birefringence angle β ∈ {0.273°, 0.331°}**

This is the primary falsifier. The braided winding mechanism predicts that the CMB polarization plane rotates by one of two specific angles, and that neither falls in the gap [0.29°, 0.31°]. LiteBIRD launches around 2032. When it measures β, the framework either survives or it doesn't. There is no wiggle room in the admissible window [0.22°, 0.38°].

We do not soften this. β outside the window, or landing in the predicted gap, falsifies the braided-winding mechanism. Full stop.

**2. n_w = 5 is the unique winding number**

Pillar 786, new in v23, formalises what we've claimed informally for years: n_w = 5 is the *only* integer from 1 to 15 that simultaneously passes the Planck spectral index window (n_s ∈ [0.9565, 0.9733] at 2σ), the BICEP/Keck tensor bound (r < 0.036), and the birefringence admissible range. The stability basin is a singleton.

We're honest about the caveat: "uniqueness from first principles alone" is not yet proved. Steps 1–3 in Pillar 67 narrow the field to {5, 7}. Planck data makes the final selection. That's empirical selection, not pure derivation.

**3. Normal neutrino hierarchy preferred**

The orbifold boundary conditions of the 5D geometry prefer normal hierarchy. Pillars 772 and 773 reduced the Δm²₂₁ tension from 2.98σ to 1.07σ through Lepton Jarlskog lattice derivation and three NLO corrections. JUNO (2027) will test this. 1.07σ is honest: it's an improvement, not a closure.

---

## The Gaps We Haven't Closed

Here is where a normal physics preprint would quietly move on. We don't.

**CMB acoustic peak amplitudes.** The framework suppresses acoustic peak amplitudes by a factor of 4–7 relative to observation. This is documented as Admission 2 in FALLIBILITY.md and has been there since v1. Pillars 57 and 63 address it partially. It is not resolved. We call it an ARCHITECTURE_LIMIT, which means the current geometry cannot reproduce the observed amplitude without additional structure we haven't identified.

**Froggatt-Nielsen charges — 9 free parameters.** The Yukawa sector of the Standard Model requires flavour hierarchy. We generate this via FN charges assigned to fields under a U(1)_FN symmetry. The charges are consistent with geometry, but 9 of them remain free. This is an architecture limit, not a prediction. We say so.

**DESI Year 1 tension.** The KK compactification predicts a cosmological constant: dark energy equation of state wₐ = 0. DESI Year 1 measured wₐ ≈ −0.65 at 2.1σ tension with this. We are watching. DESI Year 3 results in 2026 will be decisive. If wₐ ≠ 0 is confirmed at >3σ, we have a serious problem.

These are not footnotes. They are the living edge of the framework.

---

## The Interrogator

The v23 application is called the Axiom Zero Interrogator. You can open it now in any modern browser — no server, no login, no API key.

The premise is simple: every claim the Unitary Manifold makes should be interrogable. You should be able to type "the Higgs mass is derived from geometry" and immediately see: what pillar, what epistemic gate (DERIVED / FITTED / ARCHITECTURE_LIMIT), what the honest prediction is, what observation currently says, and what experiment will settle it.

The Interrogator has three modes:

**Challenge Mode.** Type any claim or keyword. The engine searches 21 pre-registered claims, scores them for relevance, and returns the full epistemic card: gate status, prediction, observation, tension in σ, and the exact falsification condition. Try "cold fusion" — you'll see a FALSIFIABLE_PREDICTION gate with an explicit note that Pillar 15 is not a confirmation that LENR occurs. Try "consciousness" — you'll see ADJACENT_TRACK with an honest note that this belongs to the Pentad governance framework, not the physics core.

**Experiment Mode.** Select any of seven registered experiments — LiteBIRD, DESI, JUNO, ACTPol, HL-LHC, nEDM, XENON-nT. See every framework claim the experiment can test, the predicted value, and the verdict threshold. All thresholds are pre-registered and locked at Pillar 787 (Falsification Boundary Map).

**Tension Map.** An interactive canvas showing all seven open tensions as a constellation. x-axis is current σ tension; y-axis is theoretical confidence. Click any node. The DESI wₐ tension sits at 2.1σ with moderate confidence. The CMB amplitude suppression sits near zero σ (it's not a measured tension, it's an architecture limit) but at low confidence. The birefringence prediction sits at zero tension (pre-launch) but high confidence. The map tells you what's at stake before you read a single equation.

The Interrogator is honest by design. It shows every gap, every fitted parameter, every admission. It is the anti-hype tool.

---

## What v23 Changes

Before v23, the Unitary Manifold was a documented framework. After v23, it is an interrogable one.

The distinction matters. A documented framework tells you what it claims. An interrogable framework lets you push back, and answers back honestly.

The Falsification Boundary Map (Pillar 787) pre-registers verdict thresholds for seven experiments. Those thresholds are locked. We cannot later say "well, that's not quite what we meant by falsification." The thresholds are in version-controlled Python code with 70+ tests. If we change them, the version increments and the change is visible.

The Winding Stability Basin (Pillar 786) answers the most common challenge we receive: "why n_w = 5?" The answer is now machine-readable: sweep integers 1–15, apply three independent observational constraints, the basin is {5}. You can run the code yourself.

The Interrogator makes this accessible to anyone — physicist, journalist, or curious reader — in one browser tab.

---

## What We're Watching

In rough priority order:

**DESI Year 3 (2026).** Dark energy EoS. If wₐ departs from 0 at >3σ, we have a falsification-level tension. This is the most urgent near-term signal.

**Simons Observatory (2026).** Improved n_s measurement. Currently 0.33σ tension with our prediction. We need this to stay inside 2σ.

**JUNO (2027).** Neutrino mass ordering. Normal hierarchy confirmed at >5σ would be a significant consistency check. Inverted hierarchy at >5σ would be a serious challenge.

**HL-LHC (2027+).** Higgs mass precision. We predict ~126.2 GeV at one-loop; observed 125.20 GeV. The 0.71σ gap is not a crisis, but precision will tighten.

**LiteBIRD (2032).** The primary falsifier. β ∉ [0.22°, 0.38°] or β ∈ [0.29°, 0.31°] ends the braided-winding mechanism. This is the experiment that matters most.

---

## The Honest Close

The Unitary Manifold is a candidate framework for 5D Kaluza-Klein unification. It makes specific, falsifiable predictions. It acknowledges specific gaps and architecture limits. It is internally self-consistent. External confirmation is pending.

Here is exactly what would kill it: LiteBIRD measuring β outside [0.22°, 0.38°], or inside the predicted gap [0.29°, 0.31°]. DESI confirming wₐ ≠ 0 at >3σ. JUNO confirming inverted neutrino hierarchy at >5σ.

We published those conditions before the experiments ran. That is what a serious scientific candidate does.

The Interrogator is open. Challenge anything.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

*v23.0 · 2026-08-20 · 57,000+ passing tests · 0 failures · Lean4 1006 theorems*
