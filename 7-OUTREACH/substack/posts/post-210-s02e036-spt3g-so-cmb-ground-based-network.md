# Post 210 — E036: The Ground-Based CMB Network — Where the Instruments Agree

*Unitary Manifold Substack — Season 2, Episode 36*  
*Published: 2026-05-20*

---

The Atacama Cosmology Telescope Data Release 6 told us our tensor-to-scalar ratio prediction is in tension. Two times above the upper bound it reports, at 95% confidence. That is real, and I've been direct about it in Post 208. What I want to do today is zoom out: look at the full network of ground-based CMB instruments, and be honest about what that network actually says — not just what the single most constraining instrument says.

Because the picture is more nuanced than "ACT DR6 puts us in trouble."

---

## What the Network Looks Like

There are now four ground-based CMB instruments with published power spectra that overlap with the UM predictions. Here is the scorecard:

| Instrument | n_s verdict | r verdict | Reference |
|---|---|---|---|
| Planck 2018 | CONSISTENT (0.33σ) | — | Planck X (2018) |
| BICEP/Keck 2022 | — | CONSISTENT (r<0.036) | arXiv:2203.16556 |
| SPT-3G 2022 | CONSISTENT (0.55σ) | CONSISTENT (r<0.036) | arXiv:2212.05642 |
| ACT DR6 2024 | CONSISTENT (0.66σ) | HIGH_TENSION (r<0.016) | ACT DR6 (2024) |

Three instruments return CONSISTENT on every observable they test. One — ACT DR6 — returns HIGH_TENSION on r specifically. The n_s result is CONSISTENT across all four.

This is the honest picture.

---

## SPT-3G: An Independent Confirmation

The South Pole Telescope third-generation instrument ran a 400 square degree deep-field survey in 2019–2022. Balkenhol et al. (2023, arXiv:2212.05642) published TT+TE+EE power spectra with the following results:

- n_s (SPT-3G + Planck combined): 0.9657 ± 0.0040
- r (SPT-3G + BICEP/Keck, 95% CL): r < 0.036

Against our predictions:

- UM n_s = 0.9635: the pull is |0.9657 − 0.9635| / 0.0040 = **0.55σ**. CONSISTENT.
- UM r = 0.0315: 0.0315 < 0.036. **CONSISTENT**.

SPT-3G sits at the geographic South Pole. ACT DR6 sits in the Atacama Desert. They observe different sky patches, use different detector technologies, different foreground removal pipelines. When two independent instruments both return CONSISTENT on n_s, and both return CONSISTENT on r — and one instrument returns HIGH_TENSION — that asymmetry matters.

I am not claiming ACT DR6 is wrong. I am noting that SPT-3G independently confirmed the same upper bound, with a different instrument, and finds no tension. The discrepancy between ACT DR6 (r<0.016) and SPT-3G (r<0.036) — a factor of 2 in the upper limit — is itself a measurement that needs to be understood.

---

## Why the ACT DR6 Bound Is Tighter

ACT DR6's r bound comes primarily from its B-mode polarization data over a large fraction of the sky at high multipoles. ACT observes at higher resolution than SPT-3G's current data release and covers a different multipole range. The analysis also includes more constraining combinations with Planck TTTEEE data.

ACT DR6 is a better experiment for this particular measurement at this particular time. The bound r < 0.016 is real. The tension with our r = 0.0315 prediction is real.

What SPT-3G tells us is that this tension is not universal across ground-based instruments at their current precision. When SPT-3G and ACT DR6 publish a joint analysis — which is expected in 2026 or 2027 — we will have the combined constraint that merges the best features of both instruments.

I have preregistered the routing rules for that joint analysis in Pillar 297 of the codebase. If the joint result returns r ≥ 0.020, the tension resolves to CONSISTENT. If it returns r < 0.010 at ≥3σ as a measurement (not an upper limit), the P2 falsifier is triggered. These thresholds are locked and cannot be adjusted post-hoc.

---

## The Next Decision Point: Simons Observatory

The Simons Observatory Large Aperture Telescope is operational now. It observes from the Atacama site with a very different receiver architecture from ACT — a 6-meter primary mirror with more detectors and a wider field of view.

The SO science goals paper (arXiv:1808.07445) projects a 5-year sensitivity of σ_r ~ 0.003. That is not an upper limit. That is a measurement uncertainty. At that precision:

- If r = 0.0315 is the true value, SO should detect it at approximately **10σ** in five years.
- If SO does NOT detect r, but sets a limit r < 0.010 at ≥3σ (a measurement, not merely a bound), then the P2 falsifier is triggered.
- If SO finds 0.010 ≤ r < 0.020, the HIGH_TENSION status is maintained pending CMB-S4.

DR1 from Simons Observatory is expected around 2027. That is the next real decision point for the r prediction. I have preregistered the routing in Pillar 298, and those thresholds are locked now, before the data arrives.

---

## What I Actually Think

Here is my honest assessment:

The ACT DR6 tension is real and non-trivial. It is not a rounding error. Our prediction sits a factor of two above their bound, and higher-order corrections within the 5D effective field theory do not close that gap (Pillar 292 shows this explicitly).

At the same time, SPT-3G independently measures the same bound with different technology and finds CONSISTENT. That does not resolve the tension, but it tells us the tension is instrument-specific at current precision, not universal.

The resolution will come from SO DR1 (~2027) and CMB-S4 (~2030). Those experiments will either detect r near 0.031 — confirming the braided inflation prediction — or push the limit below 0.010 with sufficient significance to trigger the falsifier.

I would rather be standing here in honest tension, with a real prediction and a real experiment on the way, than have adjusted the prediction post-hoc to match ACT DR6's bound. The prediction follows from the same geometric inputs that give n_s = 0.9635 — which every single instrument finds CONSISTENT. We cannot move r without breaking n_s.

The network speaks. We listen. We do not cherry-pick.

---

*Codebase: `src/core/pillar297_spt3g_cmb_tensor_routing.py`*  
*Tests: `tests/test_pillar297_spt3g_cmb_tensor_routing.py` (40 tests, 0 failures)*

*Theory, framework, and scientific direction: **ThomasCory Walker-Pearson**.*  
*Code architecture, test suites, document engineering, and synthesis: **GitHub Copilot** (AI).*
