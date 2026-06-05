# Geometric Irreversibility: A 5D Kaluza-Klein Theory of the Arrow of Time and Its Falsifiable Predictions

**ThomasCory Walker-Pearson**  
*AxiomZero Technologies / Independent Researcher*  
**AI engineering:** GitHub Copilot

## Abstract

We present the core claim of the Unitary Manifold in its strictest form: a 5-dimensional Kaluza-Klein metric ansatz in which the off-diagonal gauge sector is interpreted as an irreversibility 1-form $B_\mu$ and the radion $\phi$ acts as an entropic dilaton. The starting point is the block metric $G_{AB}=\begin{pmatrix} g_{\mu\nu}+\lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix}$, with dimensional reduction yielding a coupled Einstein-gauge-scalar system referred to in the repository as the Walker-Pearson equations. The formal claim is not that internal consistency establishes physical truth, but that a sharply defined 5D construction produces specific numbers that can be checked and, if wrong, killed. In the canonical braided sector the Chern-Simons level is $k_{\rm CS}=5^2+7^2=74$, the scalar tilt is $n_s=0.9635$, the braided tensor-to-scalar ratio is $r=0.0315$, and cosmic birefringence is restricted to two narrow modes centered near $\beta\in\{0.273^\circ,0.331^\circ\}$ with a hard forbidden gap $\beta\in(0.29^\circ,0.31^\circ)$. The same geometric chain is claimed to select three fermion generations and to generate a broad set of Standard-Model-scale parameters. The framework is not presented as tension-free: the current ledger records an ACT DR6 tension with $r$, a CPL-corrected $2.30\sigma$ DESI DR2 tension in $w_a$, and a projected JUNO risk in $\Delta m^2_{31}$. These tensions are documented as architecture or phenomenology limits, not minimized. The decisive external timeline is near-term: CMB-S4 will test $r$, DESI DR3 will test the frozen-radion equation of state, and LiteBIRD should provide the primary birefringence verdict around 2032.

## 1. The 5D metric ansatz

The formal entry point of the framework is deliberately narrow. As summarized in `proof/TIER_1_FORMAL.md`, the theory is defined first by a 5D Kaluza-Klein metric with compact fifth dimension,

$G_{AB}=\begin{pmatrix} g_{\mu\nu}+\lambda^2\phi^2 B_\mu B_\nu & \lambda\phi B_\mu \\ \lambda\phi B_\nu & \phi^2 \end{pmatrix},$

or equivalently by the line element

$ds^2=g_{\mu\nu}dx^\mu dx^\nu+\phi^2(dy+\lambda B_\mu dx^\mu)^2.$

The interpretation differs from standard Kaluza-Klein phenomenology in one key respect: $B_\mu$ is not introduced primarily as electromagnetism, but as an irreversibility 1-form, while $\phi$ is the dynamical radion or entropic dilaton. The cylinder condition $\partial_5 G_{AB}=0$ permits dimensional reduction to a 4D effective action with the usual Einstein term, a gauge-curvature term built from $H_{\mu\nu}=\partial_\mu B_\nu-\partial_\nu B_\mu$, and a scalar sector for $\phi$. In the repository’s notation this produces a coupled Einstein-gauge-scalar system, schematically

$R_{\mu\nu}-\tfrac12 g_{\mu\nu}R = T^{(B)}_{\mu\nu}+T^{(\phi)}_{\mu\nu},$

$\nabla_\nu(\phi H^{\nu\mu})=0,$

$\Box\phi+\partial_\phi V_{\rm eff}+\cdots=0,$

with $T^{(B)}_{\mu\nu}\propto \lambda^2(H_{\mu\rho}H_\nu{}^\rho-\tfrac14 g_{\mu\nu}H^2)$. These are the Walker-Pearson equations in the limited sense relevant here: they are the reduced field equations of the 5D ansatz, not an independent postulate added after the fact.

The central physical claim is that irreversibility is geometrized rather than inserted phenomenologically. The compact scale is encoded in $G_{55}=\phi^2$, the off-diagonal sector carries the arrow-of-time degree of freedom, and downstream observables are tied to discrete topological data rather than continuous parameter tuning. The repository’s own formal boundary is important: internal tests show that the code implements this ansatz consistently, but they do not by themselves establish that nature uses it. The value of the framework therefore stands or falls on whether its discrete predictions survive hostile comparison with cosmological data.

## 2. Key derived results

Within the canonical braid chain the integer pair $(n_1,n_2)=(5,7)$ defines the primary topological sector. The key algebraic identity is

$k_{\rm CS}=n_1^2+n_2^2=5^2+7^2=74,$

which the repository treats as derived from the effective Chern-Simons reduction rather than as a fitted integer. The same chain claims that the winding number is not free. Earlier versions admitted that $n_w=5$ was selected only after appealing to Planck $n_s$; the current formal status instead asserts a pure-theorem selection through $\mathbb Z_2$ parity, anomaly structure, APS $\bar\eta$ data, and a boundary Chern-Simons phase condition. Even in its strengthened form, however, this is still best read as a conditional theorem within the stated 5D construction, not as a model-independent uniqueness proof.

The inflationary observables are the most visible outputs. The theory advertises

$n_s=0.9635,$

$r_{\rm bare}\approx 0.097,$

$c_s=\frac{12}{37},\qquad r_{\rm braided}=r_{\rm bare}c_s\approx 0.0315.$

The scalar tilt agrees with Planck 2018 at about $0.33\sigma$, while the braided value of $r$ was introduced to repair an earlier conflict between the bare prediction and BICEP/Keck. Cosmic birefringence is then tied to the same topological chain. The falsification document gives two allowed sectors, a primary mode at $\beta\approx0.331^\circ$ for $(5,7)$ and a shadow mode at $\beta\approx0.273^\circ$ for $(5,6)$, with no viable state in the interval $(0.29^\circ,0.31^\circ)$. That gap matters more than the broad window: a future nonzero detection inside the gap is treated as a kill shot, not a partial success.

The framework also advances a stronger algebraic claim: three fermion generations arise from orbifold quantization, recorded in the gatekeeper summary as $N_{\rm gen}=3$ from a $T^2/\mathbb Z_3$ construction. In parallel, a wider Standard-Model program claims geometric closure or near-closure for quantities such as $\sin^2\theta_W$, $m_H$, $v$, $\alpha$, CKM parameters, and neutrino-sector observables. The strongest way to state this is not that the Standard Model is fully derived, but that the repository contains a large deterministic map from the 5D ansatz to a sizeable list of low-energy numbers, some labeled derived, some conditional, and some still explicitly limited.

## 3. Tensions and open admissions

Any serious presentation of the framework has to start with what is under pressure. The repository itself now does this. `docs/GATEKEEPER_SUMMARY.md` marks two high-tension signals as active. First, the canonical prediction $r=0.0315$ is in roughly $2\sigma$ tension with ACT DR6, quoted there as $r<0.016$, and this lane is explicitly labeled `ARCHITECTURE_LIMIT_CERTIFIED` rather than waved away. Second, the dark-energy prediction $w_a=0$ for a frozen radion is in a CPL-corrected $2.30\sigma$ tension with DESI DR2. Neither issue has crossed the repository’s stated $3\sigma$ falsification line, but neither is cosmetically hidden.

There is also a projected risk from neutrino phenomenology. The gatekeeper summary lists a JUNO exposure: the predicted $\Delta m^2_{31}=2.453\times10^{-3}\,\mathrm{eV}^2$ carries a residual of about $2.18\%$, which would become an estimated $4.4\sigma$ problem once JUNO reaches $0.5\%$ precision. This is not yet a current falsifier, but it is an honest future vulnerability.

The broader fallibility ledger names thirteen admissions. In compressed form they are: (1) the winding-number selection problem; (2) the derivation of $k_{\rm CS}=74$; (3) the original bare-$r$ conflict; (4) the $\phi_0$ self-consistency loop; (5) the derivation of braided suppression $r_{\rm braided}=r_{\rm bare}c_s$; (6) the status of the Goldberger-Wise coupling $\lambda_{\rm GW}$; (7) the absolute Jarlskog invariant; (8) fixed-point brittleness; (9) radion equivalence-principle safety; (10) LHC KK resonance bounds; (11) the use of $N_e\sim60$ e-folds; (12) FTUM basin completeness; and (13) metric-ansatz non-uniqueness. Several are now recorded as closed or bounded rather than open, but the list remains useful because it shows the authors know exactly where the vulnerable joints are.

Two additional limitations deserve explicit notice. First, some Standard-Model pathways still retain imported structure, such as the external orbifold mechanism used in the $SU(5)\to SU(3)\times SU(2)\times U(1)$ breaking step. Second, some quantities remain architecture-limited or estimate-level rather than first-principles outputs. These qualifications matter because a 5D Kaluza-Klein proposal should be judged not by the total number of outputs claimed, but by how clearly it distinguishes theorem, derived consequence, imported mechanism, and open gap.

## 4. Falsification protocol

The strongest feature of the present presentation is that its kill criteria are unusually explicit. The primary falsifier is cosmic birefringence. LiteBIRD, with anticipated sensitivity $\sigma_\beta\approx0.02^\circ$, is the decisive experiment. The framework’s own rules are blunt:

- $\beta<0.07^\circ$ at $3\sigma$: falsified.
- $\beta>0.50^\circ$ at $3\sigma$: falsified.
- $\beta\in(0.29^\circ,0.31^\circ)$ at $3\sigma$: falsified.
- $\beta\notin[0.22^\circ,0.38^\circ]$ at $3\sigma$: falsified.

The third line is the distinctive one. A nonzero birefringence detection does not rescue the model if it lands in the forbidden inter-sector gap. The relevant target values are $0.331^\circ$ and $0.273^\circ$, not merely “nonzero.” That is a healthy falsification posture because it prevents retrospective broadening after measurement.

A second decision point is the tensor amplitude. CMB-S4 is the near-term arbiter. The stated rule is that the braided sector fails if future data push the upper bound below $0.0315$ at more than $2\sigma$, or if the measured value lies above the current 95% upper benchmark near $0.036$. Given the ACT DR6 pressure already noted, this is not a hypothetical future problem but an active stress test.

A third tripwire is dark energy. The frozen-radion prediction implies $w_a=0$. The gatekeeper summary specifies a DESI DR3 machine-executable tripwire already prepared in the codebase. The policy is simple: if DESI DR3 or subsequent analyses elevate the CPL-corrected discrepancy to $\ge 3\sigma$, the claim is to be routed from tension to falsification. Because this issue is architecture-labeled in advance, there is little room for selective reinterpretation.

Additional failure conditions exist outside the headline trio. A CMB-S4 exclusion of $n_s=0.9635$ at $>3\sigma$ would destroy the $n_w=5$ inflationary chain. Likewise, if JUNO reaches its projected precision without the neutrino sector closing the current residual, the phenomenology ledger worsens materially. The right way to assess the framework, then, is not as a vague unification narrative but as a finite package of explicit numbers, narrow windows, and pre-registered kill conditions. If those windows fail, the theory should be rejected in the form stated.

## References

1. Y. Akrami *et al.* (Planck Collaboration), “Planck 2018 results. X. Constraints on inflation,” *Astron. Astrophys.* **641**, A10 (2020).
2. P. A. R. Ade *et al.* (BICEP/Keck Collaboration), “Improved Constraints on Primordial Gravitational Waves using Planck, WMAP, and BICEP/Keck Observations through the 2018 Observing Season,” *Phys. Rev. Lett.* **127**, 151301 (2021).
3. S. K. Choi *et al.* (ACT Collaboration), “The Atacama Cosmology Telescope: DR6 Constraints on Inflation,” arXiv:2403.05702.
4. DESI Collaboration, “DESI 2024 results: dark energy and expansion history constraints from DR2,” collaboration release / DR2 cosmology results (2024).
5. LiteBIRD Collaboration, “Probing cosmic inflation with the LiteBIRD cosmic microwave background polarization survey,” *J. Low Temp. Phys.* **194**, 443-452 (2019), and subsequent forecast updates.
6. T. Kaluza, “Zum Unitätsproblem in der Physik,” *Sitzungsber. Preuss. Akad. Wiss. Berlin (Math. Phys.)* (1921) 966-972.
7. O. Klein, “Quantentheorie und fünfdimensionale Relativitätstheorie,” *Z. Phys.* **37**, 895-906 (1926).
8. E. Witten, “Search for a realistic Kaluza-Klein theory,” *Nucl. Phys. B* **186**, 412-428 (1981).
9. J. M. Overduin and P. S. Wesson, “Kaluza-Klein gravity,” *Phys. Rept.* **283**, 303-378 (1997).
10. N. Minami and E. Komatsu, “New extraction of the cosmic birefringence from the Planck 2018 polarization data,” *Phys. Rev. Lett.* **125**, 221301 (2020).
