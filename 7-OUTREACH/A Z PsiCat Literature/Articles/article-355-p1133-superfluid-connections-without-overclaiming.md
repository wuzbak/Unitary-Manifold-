# Superfluid Connections Without Overclaiming: A Small, Checkable Step

*Merlin/PsiCat Rewrite v1 · Series/Season One*
*AxiomZero Technologies & Consulting, SPC commissioned work: Edited and written by PsiCat Ai.*
*Date: November 5, 2026*
*Grounded rewrite source: `/7-OUTREACH/substack/research/p1133-superfluid-research-brief.md`*
*Epistemic status: a narrowly scoped adjacent-track calculation and literature synthesis. It does not show that superfluidity validates the Unitary Manifold, that superfluid dark matter exists, or that acoustic geometry is emergent Einstein gravity.*
*Provenance: this article synthesizes the P1133 implementation and the linked research literature. No external PsiCat runtime, Base44 session, experiment, or independent scientific review is claimed.*

## A calculable connection, not a cosmological conclusion

Superfluids invite several very different conversations under one word. There is a low-energy effective theory whose coefficients are tied to an equation of state; there is the familiar Bogoliubov spectrum of a weakly interacting gas; there is a kinematic acoustic-metric analogy for sound waves in flowing fluids; and there are astrophysical proposals in which dark matter might behave as a superfluid in some environments. Those ideas are connected by questions and mathematics, but they are not interchangeable evidence.

Pillar 1133 takes the most modest useful step: it implements the leading-order Bogoliubov dispersion of a uniform, dilute, repulsively interacting Bose gas. This is a known calculation, written as a transparent, testable SI-unit utility. It is not a derivation from the Unitary Manifold. The label is explicit: **🔵 ADJACENT TRACK — NOT A HARDGATE PHYSICS CLAIM**.

For particle mass \(m\), number density \(n\), wave-number magnitude \(k\), and non-negative s-wave scattering length \(a_s\), the module uses the contact coupling and free-particle energy

\[
g = \frac{4\pi\hbar^2 a_s}{m}, \qquad
\epsilon_k = \frac{\hbar^2 k^2}{2m},
\]

then evaluates

\[
E_k = \sqrt{\epsilon_k(\epsilon_k + 2gn)}, \qquad
c_s = \sqrt{\frac{gn}{m}}.
\]

The units are part of the promise, not fine print: \(k\) is in m\(^{-1}\), \(m\) in kg, \(n\) in m\(^{-3}\), \(a_s\) in m, \(g\) in J m\(^3\), \(E_k\) in joules, and \(c_s\) in m/s. At \(k=0\) the spectrum is gapless. At long wavelength, \(E_k\) approaches \(\hbar c_s k\); with zero density or zero scattering length, it reduces to the free-particle energy. Focused tests exercise exactly those limits and reject invalid inputs.

That is useful precisely because it is small. A reader can inspect the assumptions, reproduce the arithmetic, and tell what a passed test does and does not mean.

## Four literatures, four different boundaries

Dam Thanh Son's relativistic superfluid EFT shows that low-energy dynamics of its Goldstone mode is determined by the equation of state. That is a powerful organizing principle, but it is not the nonrelativistic contact-gas routine here. A real relativistic connection would require a separately specified equation of state and a careful matching calculation.

Matt Visser's acoustic-metric result is also specific: for barotropic, inviscid, irrotational flow, sound-potential fluctuations obey a wave equation that can be represented using an effective Lorentzian geometry. This is a kinematic correspondence for perturbations in a fluid. It is not evidence that the fluid generates Einstein gravity or that an analogue horizon is an astrophysical black hole. Experiments such as Steinhauer's analogue-horizon work are important laboratory investigations of that analogy, not observations of gravitational Hawking radiation from an astronomical horizon.

Superfluid dark matter is yet another level: a model-dependent proposal in which a dark-matter component can enter a superfluid phase, with phonon-mediated forces proposed to yield MOND-like galactic phenomenology. Reviews describe galaxies as possible superfluid environments and clusters as mixed-phase settings, but self-interaction and merger constraints and issues such as core fragmentation remain part of the live research problem. None of that follows from the one-component gas formula.

And none of these established or proposed ideas supplies the missing UM-specific step. There is currently no precise UM superfluid parameterization or derivation in this deliverable. A familiar equation appearing in an adjacent research lane is not an endorsement of the larger framework.

## What would change the picture?

First, the implementation itself should earn confidence through independent unit checks and comparison with published excitation spectra in systems where the approximations are controlled. If the measured spectrum systematically disagrees beyond uncertainty while the homogeneous, low-temperature, dilute-gas assumptions remain valid, the calculation or its applicability to that system needs revision.

Second, any astrophysical claim needs its own model and discriminating tests. A generic Bogoliubov curve cannot settle galaxy phenomenology, cluster behavior, merger bounds, or core stability. Those require the specific microscopic model, parameter choices, astrophysical environment, and observational likelihoods to be stated.

Third, any proposed connection to UM must begin with a concrete map: identify the degrees of freedom, derive or justify an equation of state, define the regime and units, and produce a result that differs observably from ordinary superfluid EFT. Without that chain, there is no UM-specific prediction to test. No such mapping is claimed here.

The backlog is therefore deliberately unglamorous: add an explicit dilute-gas parameter check; compare with independent data or implementations; keep finite-temperature and beyond-mean-field corrections separate; and assess superfluid-dark-matter constraints only inside a fully specified model. The useful result of this pillar is not a new bridge across all those gaps. It is a clearly marked stepping stone and a map of the distance still to go.

## Sources

- D. T. Son, [“Low-Energy Quantum Effective Action for Relativistic Superfluids”](https://arxiv.org/abs/hep-ph/0204199) (2002).
- M. Visser, [“Acoustic black holes: horizons, ergospheres, and Hawking radiation”](https://arxiv.org/abs/gr-qc/9712010) (1998).
- N. N. Bogoliubov, [“On the theory of superfluidity”](https://doi.org/10.1016/S0031-8914(47)63753-6) (1947).
- W. G. Unruh, [“Experimental black-hole evaporation?”](https://doi.org/10.1103/PhysRevLett.46.1351) (1981).
- J. Steinhauer, [“Observation of quantum Hawking radiation and its entanglement in an analogue black hole”](https://doi.org/10.1038/nphys3863) (2016).
- L. Berezhiani and J. Khoury, [“Theory of dark matter superfluidity”](https://arxiv.org/abs/1507.01019) (2015).
- L. Berezhiani, G. Cintia, and M. Warkentin, [“Core Fragmentation in Simplest Superfluid Dark Matter Scenario”](https://arxiv.org/abs/2101.08117) (2021).
- L. Berezhiani et al., [review, arXiv:2505.23900v2](https://arxiv.org/abs/2505.23900v2) (2026).

### Gate Certification (v1)

This is an editorial self-check, not an external factual certification, scientific peer review, or certification of the claims or model. The article passes the three editorial gates as follows:

1. **Grounding and fidelity:** the calculation, assumptions, and declared limits match the P1133 module and pillar note; references point to the named source records.
2. **Accuracy and epistemic restraint:** the gas result is kept distinct from relativistic EFT, acoustic analogies, model-dependent superfluid dark matter, and any un-derived UM connection; uncertainty and open issues remain visible.
3. **Cross-audience clarity:** the units and equations are stated, jargon is contextualized, and the article identifies what would require separate evidence.

— PsiCat
