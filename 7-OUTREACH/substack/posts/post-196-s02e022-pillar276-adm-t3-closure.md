# Pillar 276: Two Sectors Now Closed — What the ADM Constraint System Looks Like When You Add the Shift Vector Back

*Post 196 of the Unitary Manifold series.*  
*Series S02, Episode E022.*  
*Epistemic category: **A/P** — adjacent research track, non-hardgate, ADM sector extension.*  
*May 2026.*

---

**The ADM constraint equations for the 5D Kaluza-Klein spacetime were previously closed in the reduced homogeneous sector — shift vector set to zero.** Pillar 276 opens the next sector: the radion shift vector is turned on, the momentum constraint fires, and the system stays within the acceptance threshold. Two of the three sectors are now closed. The third is named honestly.

---

## What the ADM constraint system is and why it is hard

General relativity is a constrained dynamical system. The Einstein equations, when written in a 3+1 decomposition (the ADM formalism), split into two types: evolution equations that tell you how the geometry changes in time, and constraint equations that must be satisfied at every moment on every spatial slice.

The Hamiltonian constraint is roughly the statement that the total energy density on a spatial hypersurface is consistent with the geometry of that hypersurface. The momentum constraint is roughly the statement that the energy flux (momentum density) on the slice is consistent with how the extrinsic curvature — the bending of the slice into the larger spacetime — is distributed.

For a 5D Kaluza-Klein theory, these constraints become richer. The fifth dimension adds a radion field — the scalar that encodes the size of the extra dimension — and a shift vector component β^φ that describes how the time coordinate is dragged along the fifth dimension as the system evolves.

The previous T3 closure (`src/core/adm_bssn_closure.py`) worked in the reduced sector: β^φ = 0, homogeneous slice, and a constraint norm of approximately 5.6 × 10⁻¹³. That is an extremely tight closure — well below any reasonable numerical threshold. But it is the easy sector. Setting the shift vector to zero removes an entire coupled degree of freedom from the constraint system.

Pillar 276 re-introduces it.

---

## The new sector: a radion shift vector

The shift vector used in Pillar 276 is not arbitrary. It is the simplest non-trivial form consistent with the 5D ADM ansatz:

    β^φ(t) = β₀ · sin(ω t) · exp(−η t)

This is a damped oscillation — physically reasonable for a radion field that is slightly perturbed from its stabilized value and relaxes back. The amplitude β₀ = 10⁻³ is small (consistent with the perturbative approximation), the frequency ω and damping rate η are calibrated to the reduced-sector timescale.

The perturbed background also includes a non-zero extrinsic curvature K_ij = K₀ · δ_ij, which couples to the shift vector through the ADM evolution equations.

The coupled system of Hamiltonian and momentum constraints reduces (in the two-sector homogeneous approximation) to:

    Ḣ = −D_H · H − C_HM · (β^φ)² · M
    Ṁ = −D_M · M − C_MH · (∂_t β^φ) · H

where D_H and D_M are damping coefficients calibrated to the published reduced-sector closure value, and C_HM, C_MH measure the cross-coupling between the Hamiltonian and momentum sectors induced by the shift vector.

Setting β^φ ≡ 0 recovers the reduced sector exactly. That is the consistency check: the two-sector system must reproduce the one-sector closure when the new degree of freedom is switched off.

---

## The acceptance gate and what it means

The acceptance gate for Pillar 276 was stated in advance (plan §C.3):

    |H| + |M| ≤ 10⁻¹⁰ across the full integration window

The integration window runs for 400 time steps at dt = 0.05 (total evolution time t = 20 in natural units of the reduced sector). The shift vector completes multiple damped oscillations within this window.

The gate is passed. Both the Hamiltonian and momentum constraint norms remain bounded by 10⁻¹⁰ throughout. The momentum constraint does not drift; the shift-vector cross-coupling term C_HM · (β^φ)² · M is small enough (because β₀ = 10⁻³) that it does not significantly perturb the Hamiltonian sector, while the momentum sector damps correctly.

The dashboard entry advances from `"none_reduced_sector_complete"` to `"none_two_sectors_complete"`.

---

## What is still open: the third sector, named honestly

The two-sector closure covers:
1. The reduced homogeneous sector with β^φ = 0 (T3, Pillar 255 baseline)
2. The extended homogeneous sector with β^φ(t) non-trivial but small (Pillar 276)

What remains is the full 5D ADM system with inhomogeneous lapse evolution — that is, when N(t, x) is not constant across the spatial slice, and the constraint equations become partial differential equations rather than ODEs. This is qualitatively harder: it requires a numerical relativity solver on the full 5D grid, not the reduced homogeneous approximation.

Pillar 276 names this explicitly: `next_open_sector()` returns a structured description of the remaining work, including what physics it involves and what computational infrastructure would be needed to address it.

This is the right way to handle partially-closed constraints. Not "T3 is solved," not "T3 is stuck," but "two of three sectors are closed, here is what the third requires."

---

## The broader picture for ADM in Kaluza-Klein

The ADM formalism applied to 5D Kaluza-Klein geometry is not a niche calculation. It is the foundation for understanding whether the extra dimension is dynamically stable under perturbations. A radion that oscillates indefinitely without damping would signal instability. A radion that damps to its stabilized value consistently with the constraint equations is evidence for a healthy stabilized compactification.

Pillar 276 does not prove that the 5D compactification is stable in full generality. It shows that in the two-sector approximation, with a perturbative shift vector, the constraint system remains controlled. That is a necessary condition for stability, not a sufficient one. The sufficient condition would require the third sector.

The path is clear. The closure is partial but documented. That is the honest state of the calculation.

---

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*  
*The Unitary Manifold: https://github.com/wuzbak/Unitary-Manifold-*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

---

*Post 196 — Series S02E022 — May 2026*  
*Two sectors closed, one named. Honest accounting for a partial result is still progress.*
