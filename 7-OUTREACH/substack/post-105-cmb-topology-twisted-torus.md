# The Shape of Everything: CMB Topology and the Twisted Torus

*Post 105 of the Unitary Manifold series.*  
*Pillars 114–120 — CMB Spatial Topology, Twisted Torus Signatures, Topological Hierarchy, Parity Selection, Anisotropic Birefringence, TB/EB Kernels, Holonomy–Orbifold Equivalence.*  
*Epistemic category: **P** for observational predictions and the EFT decoupling proof / **A** for the topological interpretation.*  
*v9.32, May 2026.*

---

Imagine standing inside a hall of mirrors. Every direction you look, you see yourself
reflected back — but the reflections are not identical. Each one is rotated slightly,
or flipped. The geometry of the room has an internal twist that changes what you see
depending on where you look.

Now scale that image up to the size of the observable universe.

In 2025, a reanalysis of Planck CMB data (reported by the American Physical Society)
examined eighteen possible shapes for the universe. Not the shape of spacetime in the
sense of curvature — Planck has confirmed the universe is flat to better than 0.1%.
The *topology* of space: whether space wraps back on itself, and if so, how.

The result was striking. One of the three most carefully studied topologies —
the simple untwisted torus — was **ruled out**, at least for torus sizes within
our observable horizon. Two others — the half-turn space and the quarter-turn space —
were not only not ruled out, they could not be ruled out with the existing data.
They leave a different imprint, one that the search methods were not designed to find.

Pillars 114 through 120 of the Unitary Manifold map precisely this landscape.

---

## Pillar 114 — The Three Topologies: E1, E2, E3 *[P]*

The Planck analysis focused on three flat Euclidean topologies
(`src/core/cmb_spatial_topology.py`):

**E1 — The 3-Torus (untwisted).** Space wraps back on itself in all three directions,
like a video game where walking off one edge brings you back on the other. If the
torus is smaller than the distance to the last-scattering surface — the "recombination
distance" χ_rec ≈ 14 Gpc — you should see identical matched circles in the CMB sky:
arc pairs where the two views are the same because they are literally the same
patch of the early universe seen from two sides. No such circles have been found.
**E1 is ruled out if the torus size L < χ_rec.**

**E2 — The Half-Turn Space.** A 3-torus with one face identified under a 180° rotation.
If you walk through that face, you come back rotated by 180°. The matched circles that
E2 produces are *correlated but not identical* — the twist changes the view. The
standard matched-circle search (looking for identical pairs) cannot exclude this.
E2 symmetry group: **Z₂**.

**E3 — The Quarter-Turn Space.** Same structure, but with a 90° identification.
E3 symmetry group: **Z₄**. Also not excluded by matched-circle searches.

The key numbers:
- E2 twist holonomy: θ = 180°; twisted-loop correlation C(θ) = cos(π) = −1
- E3 twist holonomy: θ = 90°; twisted-loop correlation C(θ) = cos(π/2) = 0

The Unitary Manifold is agnostic about which of these (or simply-connected space)
describes the universe's large-scale topology. Its CMB predictions — nₛ, r, β —
are **independent** of this choice. That independence has a precise proof, and
it matters enough to cover explicitly in the next pillar.

---

## Pillar 115 — What a Twisted Torus Writes in the Sky *[P]*

If E2 or E3 holds, the CMB carries specific imprints that are *different from*
what matched-circle searches look for (`src/core/twisted_torus_cmb.py`).

**Low-ℓ power suppression.** When the torus size L is smaller than χ_rec, modes
with wavelengths longer than L cannot exist. Power is suppressed at multipoles
ℓ < ℓ_cut ≈ π/(*L*/χ_rec). This produces a deficit at low multipoles. Observers
have long noted an unexplained low-ℓ deficit in the Planck CMB power spectrum;
a torus topology with L ~ 0.5 χ_rec would produce exactly this.

The cut-off multipole formula:

$$\ell_{\text{cut}} \approx \frac{\pi \chi_{\text{rec}}}{L_{\text{torus}}}$$

For L_torus = 0.5 χ_rec: ℓ_cut ≈ 6. Power at the quadrupole (ℓ = 2) through
the hexapole (ℓ = 6) would be suppressed. The Planck data shows this suppression.
The framework does not claim to explain it — it notes the signature is consistent.

**Twisted circle correlations.** The CMB cross-correlation between two circles
related by the topology's twist is:

$$C(\alpha, \theta) = C_{\text{self}}(\alpha) \times \cos(\theta_{\text{rad}})$$

For E2 (θ = 180°): C = −C_self(α). The circles are *anti-correlated*, not identical.
For E3 (θ = 90°): C = 0. The circles are uncorrelated — orthogonal, not identical.
Neither of these is the "identical circle" signal that was searched for and not found.

**Quadrupole axis anisotropy.** E3's 90° twist picks out a preferred axis, imprinting
a 4-fold (cos 4φ) pattern in the CMB quadrupole. E2 imprints a 2-fold pattern.

LiteBIRD's sensitivity to these topology signatures (as distinct from its primary
birefringence target) is marginal: E2 becomes detectable if L_torus < 0.5 χ_rec,
E3 if L_torus < 0.4 χ_rec. These are not ruled out, but they are not the primary
test either.

---

## Pillar 116 — Why Topology Doesn't Change the CMB Predictions *[P]*

Here is a question worth pausing on. If the universe might be a twisted torus at
scales of 14 gigaparsecs, why don't the UM's predictions for nₛ, r, and β change?

The answer is scale (`src/core/topological_hierarchy.py`). The compact extra dimension
of the Unitary Manifold operates at the Planck scale — roughly 10⁻³⁵ metres. The
large-scale spatial topology operates at the recombination scale — roughly 4 × 10²⁶ metres.
The ratio between these scales is approximately 10⁶¹.

This is the Appelquist-Carazzone decoupling theorem applied to two mass thresholds:

$$m_{\text{KK}} \sim M_{\text{Pl}} \sim 10^{19} \text{ GeV}
\qquad \text{vs} \qquad
m_{\text{topo}} \sim H_0 \sim 2 \times 10^{-33} \text{ eV}$$

The ratio m_KK/m_topo ≈ 10⁶¹ is the decoupling exponent. Any operator connecting
the two sectors is suppressed by (m_IR/m_UV)^n — a factor of 10⁻⁶¹ or smaller.
Numerically, this is zero.

The winding number n_w = 5 is a UV quantity. The Chern-Simons level k_cs = 74 is
a UV quantity. The birefringence angle β ≈ 0.351° is derived from those UV quantities.
The large-scale spatial topology (E1, E2, E3) is an IR quantity. They decouple
completely in the effective 4D theory.

The analogy between E2's Z₂ spatial twist and the UM's Z₂ orbifold is **structural,
not dynamical**: the same abstract group acts at two completely different scales for
two completely different physical reasons. The same way that a traffic roundabout
and a merry-go-round both involve circular motion but are not physically connected.

---

## Pillar 117 — Parity-Odd Selection Rules *[A]*

The E2 and E3 twists break **parity** — the discrete symmetry that maps x → −x.
A universe with a half-turn or quarter-turn spatial identification is not the same
as its mirror image.

This generates parity-odd selection rules in the CMB multipole expansion. Specifically,
even-parity modes (which transform as +1 under parity) and odd-parity modes (which
transform as −1) mix through the topology. This mixing has a distinct multipole
structure: it concentrates at low ℓ (where the topology affects modes directly)
and falls exponentially at high ℓ.

The selection rule is a geometric identity: the twist angle θ determines which
multipole parity modes can scatter off each other through the topological identification.
For E2 (Z₂, θ = 180°): only even harmonics of the twist frequency survive the
projection. For E3 (Z₄, θ = 90°): only harmonics divisible by 4 survive.

This is an analogy-level result in the current framework: the geometric argument
is clean, but the quantitative prediction requires a full CMB transfer function
calculation through the twisted boundary conditions — work that is described in
the framework's roadmap but not yet fully implemented.

---

## Pillar 118 — The Direction-Dependent Birefringence β(n̂) *[P]*

The UM's primary CMB prediction is a **monopole** birefringence — the same rotation
angle β₀ in every direction of the sky. This isotropic signal arises from the
Chern-Simons coupling k_cs = 74 accumulated over all photon paths through the
5D geometry.

But if the large-scale spatial topology is E2 or E3, the CS phase accumulates
differently along paths that pass through twisted spatial regions. The result is
a small **direction-dependent correction** to β (`src/core/anisotropic_birefringence.py`):

$$\beta(\hat{n}) = \beta_0 \times (1 + \delta(\hat{n}))$$

where the modulation δ(n̂) is a dipole pattern aligned with the twist axis:

$$\delta(\hat{n}) = A_{\text{mod}} \times \cos\phi\,\sin\theta$$

The modulation amplitude is fixed by the holonomy geometry — no free parameters
beyond what is already in the isotropic UM:

- **E2 modulation**: A_mod = 0.05 (5% fractional variation across the sky)
- **E3 modulation**: A_mod = 0.03 (3% fractional variation)

With β₀ ≈ 0.351°, this corresponds to peak-to-peak sky variation of about 0.035°
for E2 and 0.021° for E3. LiteBIRD's per-mode sensitivity to β is approximately
10⁻³ rad ≈ 0.057°. The predicted dipole signal (~3 × 10⁻⁴ rad) gives a signal-to-noise
ratio of approximately 0.5 — borderline detectable at full mission sensitivity.

Key property: the modulation is **achromatic**. It is tied to the CS coupling, not
to plasma emission or dust. A chromatic signal (frequency-dependent rotation) would
be identified as foreground contamination. An achromatic dipole pattern surviving
foreground cleaning would be a signature of E2/E3 holonomy.

---

## Pillar 119 — The Forbidden Correlations: TB and EB Kernels *[P]*

In standard cosmology, two CMB cross-correlations are exactly zero: TB (temperature
times B-mode polarisation) and EB (E-mode times B-mode). They vanish because parity
is conserved: B-modes transform oppositely to T and E under a parity flip, so the
cross-correlations average to zero.

The E2/E3 twist breaks parity. TB and EB are no longer zero.

Pillar 119 (`src/core/tb_eb_kernels.py`) computes the topological kernel functions
K_TB(ℓ, θ_twist) and K_EB(ℓ, θ_twist) for E2 and E3. These are distinct from the
TB/EB signal generated by isotropic birefringence:

- **Inflationary birefringence** (from β₀ ≈ 0.351°) generates TB/EB with a smooth
  Gaussian ℓ-profile, tracking the E-mode power spectrum.
- **Topological TB/EB** (from E2/E3 twist) peaks sharply at low ℓ ≲ 30, with
  a characteristic oscillatory pattern tied to the twist angle.

These two signals are distinguishable in ℓ-space. A B-mode experiment that measures
TB/EB with the inflationary profile is seeing primordial gravitational waves or
isotropic birefringence. One that measures the low-ℓ oscillatory topological profile
is seeing the spatial topology of the universe.

The ratio of topology-TB to inflation-TB at multipole ℓ serves as the discriminant.
At LiteBIRD sensitivity (noise floor ~10⁻¹³ in dimensionless power units), the
topological signal is expected to be in the range of signal-to-noise ratio ~1–3
for torus sizes L_torus < 0.5 χ_rec.

---

## Pillar 120 — Holonomy–Orbifold Equivalence *[A]*

The final pillar in this block draws a structural parallel that is worth naming
explicitly.

The UM's compact extra dimension has a Z₂ orbifold boundary condition: as you
traverse the compact circle and return, the fields pick up a Z₂ phase. This phase
is what selects n_w = 5 and generates chirality.

The E2 spatial topology has a Z₂ spatial holonomy: as a photon traverses the
large-scale torus and returns, its frame is rotated by 180°. This holonomy is what
generates the anisotropic birefringence modulation δ(n̂).

These are the **same abstract mathematical structure** — a Z₂ action on a circle
or loop — operating at scales separated by 10⁶¹. The orbifold is UV; the holonomy
is IR. They decouple in the effective theory. But they are isomorphic as mathematical
objects.

This is an analogy, not a causal connection. The universe may or may not have E2
topology. If it does, the holonomy-orbifold equivalence gives a unified description:
the same Z₂ appears at both ends of the scale ladder, for independent but structurally
parallel reasons.

---

## What to Check, What to Break

1. **The E2/E3 constraint** (Pillar 114): The claim that E1 is ruled out and E2/E3
   are viable rests on Planck's matched-circle search. A search algorithm that can
   detect *correlated-but-different* circle pairs (rather than identical ones) would
   place new constraints on E2/E3. This is an active research frontier.

2. **The anisotropic β prediction** (Pillar 118): The 5% and 3% sky modulation
   amplitudes are derived from the holonomy geometry with no free parameters. A
   LiteBIRD measurement of β as a function of sky position would test this. The
   achromatic signature is the key discriminant from foregrounds.

3. **The TB/EB ℓ-profile** (Pillar 119): The claim that topological TB/EB has
   a different ℓ-profile than inflationary TB/EB is the primary falsifier for the
   topology interpretation. If LiteBIRD detects TB/EB with the smooth inflationary
   profile rather than the oscillatory topological one, E2/E3 is constrained.

4. **Scale decoupling** (Pillar 116): The EFT decoupling argument is standard
   physics (Appelquist-Carazzone theorem, 1975), but its application here assumes
   that no non-perturbative effects connect the UV and IR sectors. If a
   non-perturbative coupling between the KK scale and the topology scale could
   be identified, the decoupling would break. The scale ratio 10⁶¹ makes this
   spectacularly unlikely, but "unlikely" and "proved impossible" are different.

5. **The low-ℓ power deficit**: The Planck data shows a real low-ℓ CMB power
   deficit. This framework notes the consistency with a twisted torus topology.
   It is not a prediction made before seeing the data, and should be weighted
   accordingly. The *discriminating* test is the circle cross-correlation shape.

---

*Full source code and tests:*  
*https://github.com/wuzbak/Unitary-Manifold-*  
*Pillar 114: `src/core/cmb_spatial_topology.py`*  
*Pillar 115: `src/core/twisted_torus_cmb.py`*  
*Pillar 116: `src/core/topological_hierarchy.py`*  
*Pillar 118: `src/core/anisotropic_birefringence.py`*  
*Pillar 119: `src/core/tb_eb_kernels.py`*  
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
