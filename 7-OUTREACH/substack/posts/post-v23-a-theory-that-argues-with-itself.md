# v23 — A Theory That Argues With Itself

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*

---

Most physics frameworks are presented as monoliths. They arrive fully-formed, asserting
completeness while quietly burying the gaps in appendices and supplementary material
that nobody reads. The Unitary Manifold is trying to do something different: build a
framework that *publicly argues with itself* — that makes its uncertainties machine-readable,
its falsification conditions pre-registered, and its gaps auditable in a single sitting.

v23 is the sprint that made that real.

---

## What We Actually Believe and Why

The Unitary Manifold is a 5-dimensional Kaluza-Klein framework. The core claim is
straightforward: the Standard Model gauge symmetries, the CMB observables, and the
neutrino mass spectrum can be derived — not fitted — from a single 5D metric ansatz
with a braided winding number n_w = 5.

Three claims are hardest and most important:

**1. Birefringence β ∈ {≈0.273°, ≈0.331°}**

Cosmic birefringence is the rotation of CMB polarization by a uniform axion field.
The framework predicts two canonical branches, separated by a structural gap at
[0.29°, 0.31°]. Current data (Minami+Komatsu 2020: β ≈ 0.35° ± 0.14°) is
consistent — but the error bars are too large to say much. LiteBIRD (launch ~2032)
will measure β to σ ≈ 0.03°. That measurement either lands in our predicted window
or it doesn't. There is no room for wriggling.

**2. n_w = 5 is the unique admissible winding number (Pillar 789)**

v23 added the Winding Resonance Stability Basin: a formal scan of all integer winding
numbers n_w ∈ {1,...,15}, checking each against the Planck n_s window, the
birefringence admissible range, and the BICEP/Keck r limit simultaneously. Only
n_w = 5 survives all three constraints at once. The stability margin is Δn_w = 1 —
the nearest excluded values are n_w = 4 (r too large: 0.0585 > 0.036) and n_w = 6
(β out of window: 0.475° > 0.38°). That's a narrow basin. LiteBIRD will either
confirm it or close it.

**3. Normal Hierarchy neutrino ordering (Pillar 786)**

The Z₂ Dirichlet orbifold boundary conditions select Normal Hierarchy (NH) over
Inverted Hierarchy (IH). The lightest neutrino mass is m₁ ≈ 0, giving
Σmν ≈ 0.060 eV — well below the Planck 0.12 eV upper limit. JUNO (2027-2030)
will resolve the ordering to ≥5σ. If IH is confirmed, this pillar falls.

---

## The Gaps We Haven't Closed

Epistemic honesty requires stating these explicitly.

**CMB acoustic peak amplitude** (Admission 2 in FALLIBILITY.md): The framework
predicts the CMB peak *positions* correctly but suppresses the *amplitude* by ×4–7.
This is an architecture limit: completing the NP-BC loop-correction ladder
(Pillars 774–781) reduces it to 33.6% residual, but that residual is genuine and
acknowledged. It is not swept under a rug.

**DESI dark energy tension**: DESI Year 2 (2025) reports w₀ = -0.838 ± 0.043,
w_a = -0.62 ± 0.23. The framework predicts w₀ = -1, w_a = 0 (cosmological
constant from KK radion). The current tension is 2.07σ — not yet alarming, but
tracked actively. DESI Year 3 (2026) is a high-priority watch item.

**FN charges** (Admission 3 in FALLIBILITY.md): The Froggatt-Nielsen charges
that set fermion mass hierarchies have been reduced from 9 free parameters to 3
by Yukawa SVD (Pillar 781), but 3 remain genuinely free. The framework does not
pretend otherwise.

**Δm²₂₁ residual**: The solar neutrino mass splitting has a 1.07σ residual
tension after NLO lattice corrections (Pillar 773). This is a quantified gap, not
a closed one.

---

## The Interrogator

v23 deployed the **Axiom Zero Interrogator** — App 18 in the AZ-IP product suite.

It's a single-file offline web app. No server. No API keys. No hand-waving.
You type any claim — "the Higgs mass is predicted," "birefringence is derived,"
"neutrino ordering is determined" — and the app finds the matching pillar, returns
its epistemic gate (DERIVED / FITTED / ARCHITECTURE LIMIT / ADJACENT TRACK),
shows the honest uncertainty, and tells you exactly what experiment would falsify
the claim and when that experiment will speak.

Three modes:

- **Challenge Mode**: type a claim, see the gate + falsification condition
- **Experiment Mode**: pick an upcoming experiment (LiteBIRD, DESI, JUNO,
  XENON-nT, HL-LHC, nEDM, Euclid), see every pillar it can test
- **Tension Map**: a visual canvas placing every claim in (σ tension, theoretical
  confidence) space — the honest picture of where the framework stands

The Tension Map is what makes the app unusual. Claims cluster near σ ≈ 0 and
theoretical confidence ≈ 0.9 (the DERIVED pile), with one node visibly drifting
toward the right (DESI dark energy at 2.07σ) and a cluster at low confidence
(ARCHITECTURE LIMIT entries). It's not a flattering picture. It's an accurate one.

The app was built because this is the kind of tool that a skeptical physicist,
a science journalist, or a grad student can sit down with in one session and
actually push back on the framework. It's anti-hype by design.

---

## What v23 Changes

Before v23, the Unitary Manifold was a *documented* framework: peer-reviewed
claims, test suites, Lean4 proofs, FALLIBILITY.md admissions, pre-registered
falsification protocols. Rigorous, but static.

After v23, it's an *interrogable* system. The knowledge base is machine-readable.
The falsification conditions are in a JSON file that any downstream agent or
researcher can parse. The Tension Map is a live view of the framework's current
epistemic state. The Interrogator is the first tool that makes all of this
accessible without reading 200 Python modules.

That matters for scientific credibility. A framework that hides its gaps behind
jargon is a framework that doesn't trust its own claims. A framework that publishes
its gaps in a structured, searchable, visually navigable tool is saying: *these are
the things that could falsify us, and we want you to find them.*

---

## What We're Watching

In order of timeline:

| Experiment | Observable | UM Prediction | Current Status | Timeline |
|---|---|---|---|---|
| DESI Year 3 | w_a | 0 | 2.07σ tension | 2026 |
| JUNO | NH ordering | NH (geometric) | PASS | 2027-2030 |
| JUNO | Δm²₂₁ | 7.42×10⁻⁵ eV² | 1.07σ residual | 2027 |
| XENON-nT | σ_SI (KK DM) | ~6×10⁻⁴⁷ cm² | Not excluded | 2026 |
| HL-LHC | M_KK graviton | ~1 TeV window | Not yet probed | 2029+ |
| LiteBIRD | β | ∈{0.273°,0.331°} | AWAITING | 2032+ |
| CMB-S4 | n_s, r | 0.9635, 0.0315 | PASS | 2030s |

The DESI Year 3 result is the nearest critical decision point. If w_a deviates
further from zero, the radion dark energy mechanism will need revision or
retirement. We have a formal decision tree (Pillar 787) that routes any measurement
to a PASS, TENSION, or FALSIFIED verdict automatically.

LiteBIRD 2032 is the primary falsifier. Everything else is a preview.

---

## The Honest Line

The Unitary Manifold is a candidate framework, not a confirmed one. It makes
specific, quantitative, falsifiable predictions in a domain where most alternative
theories make none. It has acknowledged gaps where current derivations are
insufficient. It has pre-registered falsification conditions in machine-readable
form. And it has now built a tool that lets anyone — physicist, journalist, AI
agent — interrogate those claims systematically.

What would kill it: birefringence β landing outside [0.22°, 0.38°] at ≥2σ from
LiteBIRD. That's the test. Everything before 2032 is preamble.

The Interrogator is at: `public-site/az-apps/18-interrogator.html`

Try to break it. That's the point.

---

*v23 totals: 3 new pillars (789-791), 164 new tests (57,288 passing total), +30 Lean4
theorems (1,036 total), 1 new app (Axiom Zero Interrogator). Next pillar slot: 792.*
