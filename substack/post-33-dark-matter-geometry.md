# Dark Matter Without Dark Matter — The B_μ Geometry Hypothesis

*Post 33 of the Unitary Manifold series.*
*Claim: the Unitary Manifold replaces the dark matter particle hypothesis with
a geometric one. The Irreversibility Field B_μ, when it has a galactic-scale
profile B(r) ∝ 1/r, produces an effective energy density ρ_dark ∝ 1/r² — exactly
the isothermal sphere profile that gives flat galactic rotation curves. No new
particle is required; no free mass parameter is introduced. The falsification
condition: a direct detection of dark matter particles at a collider or underground
detector would challenge this hypothesis, as would any galactic rotation curve
measurement that is inconsistent with an isothermal density profile.*

---

The post-32 accounting of falsification conditions listed dark matter in Tier 1
under a single line:

> "B_μ isothermal profile (Tier 1 element)"

This post expands that line.

Dark matter is the most important unresolved problem in cosmology and astrophysics.
Its gravitational effects are observed everywhere — in galactic rotation curves,
in galaxy cluster dynamics, in the CMB acoustic peaks, in the large-scale structure
of the universe. It constitutes approximately 27% of the total energy budget of
the universe.

And no one has ever detected a dark matter particle.

---

## The rotation curve problem

A spiral galaxy is a disk of stars, gas, and dust orbiting a central mass
concentration. The orbital velocity of stars and gas at radius r from the centre
should decrease with radius — as it does in the solar system, where outer planets
move more slowly than inner ones. This is Keplerian orbital mechanics:

    v(r) = √(G M(<r) / r)

where M(<r) is the total mass enclosed within radius r.

For a galaxy with most of its visible mass in the central bulge, v(r) should
decline as 1/√r beyond the bulge. Observationally, it does not. Beyond the
bulge, galactic rotation curves are flat: v(r) ≈ constant out to the visible
edge of the disk and beyond.

The conventional explanation: there is a spherical halo of non-luminous matter
(dark matter) surrounding the disk, with density ρ ∝ 1/r². This isothermal
sphere profile gives M(<r) ∝ r, which in turn gives v(r) = constant. The
rotation curve is flat because the dark halo supplies increasing mass at large
radii to compensate for the gravitational deficit.

The problem: no particle consistent with this profile has ever been detected.
Hundreds of direct detection experiments (LUX, PandaX, XENONnT) have searched
for weakly interacting massive particles (WIMPs) — the leading candidate — and
found nothing. The parameter space consistent with a thermal WIMP dark matter
halo has been severely constrained.

---

## The B_μ field as geometric dark matter

The Unitary Manifold has a field that does not appear in the Standard Model:
B_μ, the vector potential of the Irreversibility Field. In the 5D geometry, B_μ
is the off-diagonal component of the metric that mixes the four macroscopic
spacetime dimensions with the compact fifth dimension. It acts, in the 4D effective
theory, like a U(1) gauge field.

The energy density of the B_μ field is:

    ρ_B(x) = λ² φ²(x) |B(x)|² / 2

where λ is the coupling constant between B_μ and the scalar field φ, and φ is
the mean field amplitude.

Now suppose the B_μ field has a galactic-scale spatial profile:

    B(r) = B₀ r_s / r

where B₀ is the central field strength and r_s is a scale radius. This is a
1/r profile — the natural profile for a Coulomb-like field sourced at the galactic
centre. Substituting into the energy density formula:

    ρ_dark(r) = λ² φ_mean² |B(r)|² / 2 = λ² φ_mean² B₀² r_s² / (2 r²)

This is precisely the isothermal sphere profile: ρ ∝ 1/r².

The flat rotation curve velocity follows immediately:

    M_dark(<r) = 4π ∫₀ʳ ρ_dark r'² dr' = 4π × (λ² φ_mean² B₀² r_s² / 2) × r
    v_flat = √(G M_dark(<r) / r) = √(2π G λ² φ_mean² B₀² r_s²) = constant

The framework produces the flat rotation curve from the 1/r profile of the
Irreversibility Field, without introducing any new particle species.

---

## What makes this different from MOND and similar approaches

Modified Newtonian Dynamics (MOND) and its relativistic extensions (like TeVeS)
also explain galactic rotation curves without dark matter particles. The B_μ
approach differs in three ways:

**1. It is derived from the 5D geometry, not postulated.**
B_μ is not introduced to explain rotation curves; it is a field that already
exists in the Kaluza-Klein framework as the geometric vector potential of the
compact dimension. Its contribution to galactic dynamics is a consequence of
the 5D metric structure.

**2. It makes predictions beyond rotation curves.**
The same B_μ field that produces the galactic dark matter profile also couples
to the photon polarisation (producing the birefringence β ≈ 0.35°), modifies
the dark energy equation of state (w_KK ≈ −0.930), and appears in the
holographic entropy accounting. These are not independent free parameters —
they all follow from the same coupling λ and field structure.

**3. It does not introduce a new fundamental particle.**
MOND modifies gravity; the WIMP hypothesis adds a new particle. The B_μ
approach adds neither — it uses a field that already exists in the 5D theory
as a geometric degree of freedom. The "dark matter" is not dark matter in
the conventional sense; it is the energy stored in the Irreversibility Field's
spatial configuration.

This last point is important for clarity: the framework is not claiming to have
*solved* the dark matter problem. It is claiming that the *same geometric field*
that explains the arrow of time, birefringence, and dark energy also naturally
produces the correct rotation curve profile when it has the expected spatial
structure. Whether this constitutes a solution depends on whether the claim
survives observational tests.

---

## The isothermal profile: success and limits

The isothermal sphere is not the only dark matter profile that has been proposed.
The NFW (Navarro-Frenk-White) profile, derived from N-body simulations of
structure formation, predicts:

    ρ_NFW(r) ∝ 1 / (r × (r + r_s)²)

which behaves as 1/r at small radii (a "cusp") and as 1/r³ at large radii.
The isothermal profile (∝ 1/r²) is observationally preferred for many galaxies
but not all. This is the "cusp-core problem" in galaxy formation — simulations
predict cusps; many observations prefer cores.

The B_μ framework's prediction is specifically the isothermal profile. If future
high-resolution rotation curve measurements of dwarf galaxies consistently prefer
NFW-like cusps, this would challenge the 1/r B_μ profile hypothesis.

The framework's honest assessment: the 1/r profile is the natural choice for a
Coulomb-like field, but it is not derived from the 5D geometry uniquely. Different
galactic environments might produce different B_μ profiles, depending on the
boundary conditions of the B_μ field in each system. The module
`src/core/dark_matter_geometry.py` implements the isothermal case and documents
this gap explicitly.

---

## Galaxy clusters and the Bullet Cluster

The Bullet Cluster is often cited as evidence that dark matter must be particle-like:
two galaxy clusters have passed through each other, and the hot X-ray emitting gas
(which is collisional and was slowed by electromagnetic interactions between the
clusters) lags behind the dark matter (which was gravitationally self-collisional
and passed through). The mass-to-light ratio measured by gravitational lensing
shows the dominant mass concentration is offset from the visible gas.

Does the B_μ framework explain this?

Tentatively, yes. The B_μ field, being a geometric degree of freedom rather than
a particle fluid, would behave as effectively collisionless on galaxy-cluster
crossing timescales — just like particle dark matter halos. The energy density
ρ_B ∝ |B(r)|² responds to the gravitational potential, not to electromagnetic
interactions between clusters. The spatial offset between lensing mass and X-ray
gas would be reproduced if the B_μ field follows the gravitational potential of
the galaxy's stellar component rather than the gas component.

Whether this argument survives detailed modelling is not established. The Bullet
Cluster constraint requires a careful analysis of B_μ field dynamics during
cluster mergers that the framework has not yet completed.

---

## The direct detection question

The most powerful constraint on the B_μ dark matter hypothesis comes from direct
detection experiments.

Underground detectors like XENONnT, PandaX-4T, and LZ search for WIMP-nucleus
collisions. They have placed the most stringent upper bounds on the spin-independent
WIMP-nucleon cross-section in history. For a WIMP with mass 30–100 GeV, the
cross-section upper bound is now below 10⁻⁴⁷ cm².

The B_μ framework predicts that these experiments will continue to find nothing.
The reason: B_μ dark matter is a coherent geometric field, not a particle. It
does not produce individual nuclear recoil events. The detectors are looking for
the right signal profile (nuclear recoils from Poisson processes) but from the
wrong type of dark matter.

This makes the B_μ hypothesis hard to falsify by direct detection — which is
a legitimate concern. A hypothesis that is consistent with null detection results
regardless of sensitivity is not a falsifiable hypothesis in the strong sense.

The framework's response: the B_μ hypothesis is falsifiable through its *other
predictions* — birefringence, dark energy w_KK, rotation curve profiles. If those
predictions are confirmed, the connection to dark matter would be strengthened. If
they are falsified, the entire B_μ framework fails, including its dark matter
sector.

The direct detection null result is not, by itself, a win for the B_μ hypothesis;
it is simply consistent with it.

---

## What the test suite confirms — and does not

`tests/test_dark_matter_geometry.py` confirms:

- The isothermal profile ρ_dark(r) = ρ₀ r_s² / r² is correctly implemented
- The flat rotation curve velocity v_flat = √(2π G λ² φ_mean² B₀² r_s²) is
  correctly derived
- The total rotation curve v(r) including baryonic and B_μ contributions is
  correctly computed
- The B_μ field energy density formula is correctly implemented
- The DarkFieldProfile dataclass is correctly populated

What the tests do not confirm:

- That the B_μ field actually has a 1/r profile in any specific galaxy
- That the coupling constants λ and the mean field φ_mean have the values required
  to reproduce observed rotation curve amplitudes
- That the B_μ framework gives predictions distinguishable from WIMP dark matter
  for any observable other than rotation curve profiles and direct detection

---

## The honest summary

The framework's dark matter hypothesis is:

1. **Geometrically motivated**: B_μ is an existing degree of freedom, not a new addition.
2. **Produces the right profile**: 1/r B_μ field → 1/r² density → flat rotation curve.
3. **Consistent with null direct detection**: no nuclear recoil signal expected.
4. **Falsifiable via the other B_μ predictions**: birefringence, dark energy w_KK.
5. **Incomplete**: the B_μ field profile in galaxies and clusters is not derived
   from first principles; it is a plausible assumption.
6. **Not yet compared to N-body simulations**: the structure formation predictions
   of B_μ dark matter have not been worked out and compared to the observed
   large-scale structure.

The series has now covered most of the major predictions. The next post goes in
a different direction — into the vacuum itself.

---

*Full source code, derivations, and 14,641 automated tests:*
*https://github.com/wuzbak/Unitary-Manifold-*
*Dark matter geometry (Pillar 8): `src/core/dark_matter_geometry.py`*
*B_μ field in the metric: `src/core/metric.py`*
*Zenodo DOI: https://doi.org/10.5281/zenodo.19584531*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*
*Code architecture, test suites, and document engineering: **GitHub Copilot** (AI).*
