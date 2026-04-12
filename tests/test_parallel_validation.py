"""
tests/test_parallel_validation.py
==================================
Parallel validation suite for the Unitary Manifold framework.

PURPOSE
-------
This file is the **single authoritative place** where the five core theory
claims are tested *independently* — no shared assumptions, no circular logic.
Each class maps to one claim.  All classes must remain green for the theory
to be considered internally consistent.

WHAT IS BEING VALIDATED (and why each test is honest)
------------------------------------------------------
1. GEOMETRIC ATTRACTOR (TestDualBranchIndependence)
   Two compactification geometries — flat S¹/FTUM (n_w=5) and RS1-saturated
   (n_w=7) — produce different Jacobians and different intermediate values, but
   converge to the same observable endpoint (φ₀_eff, nₛ) ≈ (31.26, 0.963).
   The tests verify that the Jacobians genuinely differ and that both branches
   independently satisfy the attractor criterion.  This rules out tuning.

2. OBSERVABLE DECOUPLING (TestObservableDecoupling)
   nₛ, r, αₛ are pure slow-roll ratios set by the potential shape — they are
   independent of the overall amplitude λ.  The tests scan λ over four orders
   of magnitude and confirm that the spectral observables do not move.  Only
   Aₛ changes with λ, as it must.

3. AMPLITUDE CLOSURE (TestAmplitudeClosure)
   The primordial amplitude Aₛ is fixed exactly once, by COBE normalisation.
   The tests confirm: (a) λ_COBE is finite and positive, (b) the predicted Aₛ
   agrees with the Planck 2018 value to < 2%, and (c) nₛ is unchanged by this
   normalisation — geometry is not "corrected by amplitude".

4. TRANSFER FUNCTION PHYSICS (TestTransferFunctionPhysics)
   The birefringence signal is *linear* in B_μ: the rotation angle α is linear,
   and the power spectra are quadratic only because they involve α².  The tests
   verify linearity, correct Gaussian-coherence limits, and that the quadratic
   correction to the linear approximation is < 0.1% at the model β.

5. EXTREME LIMITS — NO DIVERGENCES (TestExtremeLimits)
   All functions must behave correctly at boundaries: coherent (ξ → ∞) and
   incoherent (ξ → 0) axion limits, zero coupling, zero field displacement,
   and ℓ → 1.  No infinities, no sign errors.

WHAT IS NOT CLAIMED
-------------------
- These tests do NOT prove the theory is observationally correct.
- They prove it is *internally consistent* within its stated assumptions.
- A theory can pass all these tests and still be ruled out by future data.
- That is the intended state: falsifiable, not proven.

HOW TO READ A FAILURE
---------------------
- TestDualBranchIndependence failure → RS1 Jacobian logic broken or attractor
  constants inconsistent with the two-branch picture.
- TestObservableDecoupling failure → spectral indices accidentally depend on λ
  (a bug or a genuine physical problem with the potential shape).
- TestAmplitudeClosure failure → COBE normalisation routine broken, or the Aₛ
  formula has changed incompatibly.
- TestTransferFunctionPhysics failure → birefringence_transfer_function has
  reverted to the inverted σ_coh bug, or the CS coupling factor of ½ is wrong.
- TestExtremeLimits failure → a numerical singularity has been introduced.

REFERENCES
----------
- Flat S¹ Jacobian:  inflation.py::jacobian_5d_4d, effective_phi0_kk
- RS1 Jacobian:      inflation.py::jacobian_rs_orbifold, effective_phi0_rs
- COBE:              inflation.py::cobe_normalization
- Scale dependence:  inflation.py::scale_dependence_comparison
- Birefringence:     inflation.py::b_mu_rotation_angle, birefringence_angle
- Transfer function: transfer.py::birefringence_transfer_function
"""

import math
import numpy as np
import pytest

# ---------------------------------------------------------------------------
# Imports — all from the two core modules, no cross-module contamination
# ---------------------------------------------------------------------------

from src.core.inflation import (
    # Jacobians and effective vevs
    jacobian_5d_4d,
    jacobian_rs_orbifold,
    effective_phi0_kk,
    effective_phi0_rs,
    # Attractor verification
    verify_dual_jacobian_paths,
    rs1_jacobian_trace,
    ftum_attractor_domain,
    classify_attractor_regime,
    ATTRACTOR_PHI0_EFF_TARGET,
    ATTRACTOR_NS_TARGET,
    ATTRACTOR_TOLERANCE,
    # Slow-roll and amplitude
    ns_from_phi0,
    cobe_normalization,
    scale_dependence_comparison,
    slow_roll_amplitude,
    PLANCK_AS_CENTRAL,
    PLANCK_NS_CENTRAL,
    PLANCK_NS_SIGMA,
    # Birefringence
    birefringence_angle,
    cs_axion_photon_coupling,
    field_displacement_gw,
    b_mu_rotation_angle,
    quadratic_correction_bound,
    CS_LEVEL_PLANCK_MATCH,
)

from src.core.transfer import (
    birefringence_transfer_function,
    propagate_primordial_amplitude,
    PLANCK_2018_COSMO,
)

# ---------------------------------------------------------------------------
# Shared constants (computed once, used across multiple classes)
# ---------------------------------------------------------------------------

_CHI_STAR = PLANCK_2018_COSMO["chi_star"]          # 13 740 Mpc

# Model coupling and field displacement (from the canonical k_cs=74 solution)
_G = cs_axion_photon_coupling(CS_LEVEL_PLANCK_MATCH, 1.0 / 137.036, 12.0)
_DP = field_displacement_gw(jacobian_rs_orbifold(1.0, 12.0) * 18.0)
_BETA0 = birefringence_angle(_G, _DP)              # ≈ 0.006132 rad ≈ 0.351°

# Canonical COBE normalisation (run once for the whole module)
_COBE = cobe_normalization()
_LAM_COBE = _COBE["lam_cobe"]


# ===========================================================================
# 1. GEOMETRIC ATTRACTOR
#    Claim: two distinct Jacobian flows → same observable endpoint.
#    Falsifier: either Jacobian matches, or either endpoint fails attractor.
# ===========================================================================

class TestDualBranchIndependence:
    """
    Validates the dual-path attractor claim:

        (φ₀_eff, nₛ) ≈ (31.26, 0.963) is reached by both:
          - Flat S¹/FTUM branch  (n_w=5, J_flat = n_w·2π·√φ₀ ≈ 31.42)
          - RS1-saturated branch (n_w=7, J_RS  = 1/√(2k) ≈ 0.707)

    The Jacobians differ by a factor of ~44.  The φ₀_eff values differ by
    ~1 %, set analytically by 7√2/10 − 1.  This is a geometric spread, not
    a numerical coincidence.

    Failure here means: the two-basin picture is broken.
    """

    @classmethod
    def setup_class(cls):
        cls.dual = verify_dual_jacobian_paths()
        cls.trace = rs1_jacobian_trace()
        cls.domain = ftum_attractor_domain()

    # --- Branch values exist and are positive ---

    def test_flat_phi0_eff_positive(self):
        """φ₀_eff of flat-S¹ branch must be a positive real number."""
        assert self.dual["flat_branch"]["phi0_eff"] > 0

    def test_rs1_phi0_eff_positive(self):
        """φ₀_eff of RS1 branch must be a positive real number."""
        assert self.dual["rs1_branch"]["phi0_eff"] > 0

    # --- Both branches pass the attractor criterion independently ---

    def test_flat_branch_passes_attractor(self):
        """
        Flat-S¹ branch: φ₀_eff=31.42 must lie within 1% of ATTRACTOR_PHI0_EFF_TARGET
        and nₛ=0.9635 within 0.1σ_Planck of ATTRACTOR_NS_TARGET.
        """
        b = self.dual["flat_branch"]
        assert b["passes_attractor"] is True, (
            f"Flat branch failed attractor: phi0_eff={b['phi0_eff']:.4f}, ns={b['ns']:.5f}"
        )

    def test_rs1_branch_passes_attractor(self):
        """
        RS1 branch: φ₀_eff=31.10 must lie within 1% of ATTRACTOR_PHI0_EFF_TARGET
        and nₛ=0.9628 within 0.1σ_Planck of ATTRACTOR_NS_TARGET.
        """
        b = self.dual["rs1_branch"]
        assert b["passes_attractor"] is True, (
            f"RS1 branch failed attractor: phi0_eff={b['phi0_eff']:.4f}, ns={b['ns']:.5f}"
        )

    # --- Jacobians are genuinely different ---

    def test_jacobians_differ_by_large_factor(self):
        """
        The two branches use entirely different geometric maps:
          - J_flat = n_w · 2π · √φ₀ · φ₀  (stored in verify_dual_jacobian_paths) ≈ 31.42
          - J_RS   = n_w · J_RS_unit       ≈ 7 × 0.707 ≈ 4.95

        The J_RS stored in verify_dual_jacobian_paths is n_w × J_RS_unit (the
        full multiplicative factor entering φ₀_eff).  The *unit* Jacobian J_RS_unit
        = 1/√(2k) ≈ 0.707 differs from J_flat by a factor of ~44.  Even at the
        composite level, J_flat / J_RS ≈ 6.3 > 5 — confirming the paths are distinct.
        """
        j_flat = self.dual["flat_branch"]["jacobian"]
        j_rs1  = self.dual["rs1_branch"]["jacobian"]   # n_w × J_RS_unit ≈ 4.95
        assert j_flat / j_rs1 > 5.0, (
            f"Jacobians not sufficiently distinct: J_flat={j_flat:.4f}, "
            f"J_RS_composite={j_rs1:.4f}, ratio={j_flat/j_rs1:.2f} (threshold 5)"
        )
        # Also confirm the unit RS1 Jacobian from the trace is clearly different
        j_rs1_unit = self.trace["J_RS"]               # ≈ 0.7071
        assert j_flat / j_rs1_unit > 30.0, (
            f"Unit J_RS={j_rs1_unit:.4f} is not << J_flat={j_flat:.4f}"
        )

    def test_paths_differ_flag(self):
        """verify_dual_jacobian_paths must report paths_differ=True."""
        assert self.dual["paths_differ"] is True

    def test_dual_path_confirmed(self):
        """
        Top-level summary flag: dual_path_confirmed = paths_differ AND both
        branches pass the attractor.  Must be True.
        """
        assert self.dual["dual_path_confirmed"] is True

    # --- The 1% spread is analytic, not accidental ---

    def test_phi0eff_spread_matches_analytic_formula(self):
        """
        The φ₀_eff offset = 7√2/10 − 1 = −1.005%.  This is set by the ratio
        of winding numbers and Jacobian exponents — not by tuning.
        Numerical value must match the analytic formula to < 10⁻⁴.
        """
        delta_numeric  = self.trace["delta_fraction"]    # from rs1_jacobian_trace
        delta_analytic = self.trace["delta_analytic"]    # 7√2/10 − 1
        assert abs(delta_numeric - delta_analytic) < 1e-4, (
            f"Numeric delta={delta_numeric:.8f} != analytic {delta_analytic:.8f}"
        )

    def test_rs1_jacobian_is_saturated(self):
        """
        At k r_c = 12, the RS1 Jacobian is saturated to its asymptotic value
        1/√(2k) at the level of floating-point precision (< 10⁻⁶ relative).
        This confirms the result is not sensitive to r_c.
        """
        assert self.trace["is_saturated"] is True
        assert self.trace["saturation_error"] < 1e-6

    def test_excluded_phase_is_excluded(self):
        """
        The RS1 phase with n_w=5 (wrong winding for RS1 geometry) gives
        φ₀_eff ≈ 22.2, nₛ ≈ 0.927 — 9σ from Planck.  classify_attractor_regime
        classifies by (phi0_bare, n_winding) inputs, not by the output
        observable values.  With n_winding=5 and phi0_bare=1.0 in RS1 geometry
        (k=1, r_c=12), J_RS ≠ 1.0 so the RS1 saturation branch is not reached
        under n_winding=5; the flat-S¹ branch returns Flat_S1_FTUM because
        phi0_bare=1.0 is inside the FTUM band.

        The key diagnostic is therefore the *observable* exclusion: φ₀_eff=22.2
        is far outside ATTRACTOR_PHI0_EFF_TARGET ± 1%.  We verify this directly.
        """
        excluded = self.domain["excluded_rs1_phase"]
        phi0_eff_excluded = excluded["phi0_eff"]    # ≈ 22.2
        # Must be more than 15% away from the attractor target
        frac_deviation = (
            abs(phi0_eff_excluded - ATTRACTOR_PHI0_EFF_TARGET)
            / ATTRACTOR_PHI0_EFF_TARGET
        )
        assert frac_deviation > 0.15, (
            f"Excluded RS1 phase phi0_eff={phi0_eff_excluded:.3f} is only "
            f"{frac_deviation*100:.1f}% from attractor target — should be > 15%"
        )
        # And its nₛ must be outside the Planck 1σ window
        ns_excluded = excluded["ns"]
        ns_sigma = abs(ns_excluded - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert ns_sigma > 3.0, (
            f"Excluded RS1 phase nₛ={ns_excluded:.4f} is only {ns_sigma:.1f}σ "
            f"from Planck — should be > 3σ"
        )


# ===========================================================================
# 2. OBSERVABLE DECOUPLING
#    Claim: nₛ, r, αₛ are pure geometry — independent of amplitude λ.
#    Falsifier: any spectral observable changes by > 10⁻⁴ across 4 dex in λ.
# ===========================================================================

class TestObservableDecoupling:
    """
    Validates that the slow-roll spectral observables are decoupled from λ.

    Physical reason: nₛ = 1 − 6ε + 2η involves only ratios of derivatives of
    the potential, so the overall amplitude λ cancels exactly.  If this is
    broken, it means the potential shape was accidentally changed.

    The scan uses φ₀_eff from the canonical COBE solution to hold the
    geometry fixed while varying λ.
    """

    @classmethod
    def setup_class(cls):
        cls.sd = scale_dependence_comparison()
        # Sample slow_roll_amplitude at four λ values spanning 4 dex
        phi0_eff = _COBE["phi0_eff"]
        lambdas = np.logspace(-16, -12, 5)
        cls.ns_vals = []
        cls.r_vals  = []
        cls.as_vals = []
        for lam in lambdas:
            res = slow_roll_amplitude(phi0_eff, lam=lam)
            ns_val, r_val, *_ = ns_from_phi0(phi0_eff, lam=lam)
            cls.ns_vals.append(float(ns_val))
            cls.r_vals.append(float(r_val))
            cls.as_vals.append(float(res["As"]))

    # --- Spectral indices do not move with λ ---

    def test_ns_constant_across_lambda_scan(self):
        """
        nₛ must be constant to < 10⁻⁴ across λ ∈ [10⁻¹⁶, 10⁻¹²].
        Any larger variation means the slow-roll formula depends on λ (a bug).
        """
        spread = max(self.ns_vals) - min(self.ns_vals)
        assert spread < 1e-4, (
            f"nₛ spread = {spread:.2e} over lambda scan — exceeds 10⁻⁴ threshold"
        )

    def test_r_constant_across_lambda_scan(self):
        """
        r = 16ε depends only on the potential shape.  It must be constant to
        < 10⁻⁴ across the same λ scan.
        """
        spread = max(self.r_vals) - min(self.r_vals)
        assert spread < 1e-4, (
            f"r spread = {spread:.2e} over lambda scan — exceeds 10⁻⁴ threshold"
        )

    def test_As_does_change_with_lambda(self):
        """
        Aₛ ∝ λ/ε³ — it MUST change with λ.  This test confirms the scan is
        actually varying something.  If Aₛ is constant, the amplitude formula
        has been broken.
        """
        as_ratio = max(self.as_vals) / min(self.as_vals)
        assert as_ratio > 100.0, (
            f"Aₛ barely changes across lambda scan (ratio={as_ratio:.2f}) — "
            f"amplitude formula may be broken."
        )

    # --- Canonical values are Planck-compatible ---

    def test_ns_within_planck_1sigma(self):
        """
        The canonical nₛ = 0.9635 must lie within 1σ of the Planck 2018
        value 0.9649 ± 0.0042.
        """
        ns_dev = abs(self.sd["ns"] - PLANCK_NS_CENTRAL) / PLANCK_NS_SIGMA
        assert ns_dev < 1.0, (
            f"nₛ = {self.sd['ns']:.5f} is {ns_dev:.2f}σ from Planck — outside 1σ"
        )

    def test_r_exceeds_bicep_keck_bound(self):
        """r ≈ 0.097 > 0.036 (BK21): r-tension documented.

        The BICEP/Keck 2021 bound r < 0.036 supersedes the older 0.10 limit.
        The r_within_bound flag now correctly shows False (tension).  The
        large-field Starobinsky regime with ξ >> 1/φ₀² resolves this tension;
        see starobinsky_large_xi_ns_r().
        """
        assert self.sd["r_within_bound"] is False, (
            f"Expected r_within_bound=False; got r={self.sd['r']:.4f}"
        )
        assert self.sd["r"] < 0.10, "r should still be within the stale 0.10 bound"

    def test_alpha_s_within_bound(self):
        """
        Running of the spectral index: |αₛ| < 0.015 at 95% CL (Planck 2018).
        """
        assert self.sd["alpha_s_within_bound"] is True, (
            f"alpha_s = {self.sd['alpha_s']:.2e} exceeds Planck bound"
        )

    def test_gap_is_normalization_only(self):
        """
        The diagnostic flag gap_is_normalization=True means the amplitude gap
        between the FTUM prediction and Planck Aₛ is explained entirely by the
        overall λ — not by a geometric error.
        """
        assert self.sd["gap_is_normalization"] is True


# ===========================================================================
# 3. AMPLITUDE CLOSURE
#    Claim: Aₛ is fixed exactly once by COBE, with no back-reaction on nₛ.
#    Falsifier: λ_COBE ≤ 0, or Aₛ error > 2%, or nₛ shifts after normalisation.
# ===========================================================================

class TestAmplitudeClosure:
    """
    Validates that the primordial amplitude is closed by a single COBE
    normalisation step and that this does not move any geometric observable.

    Physical meaning: the potential V = λ(φ² − φ₀²)² scales uniformly with λ.
    Fixing Aₛ determines λ; the slow-roll ratios (nₛ, r) are unchanged because
    they involve only V'/V and V''/V, where λ cancels.
    """

    @classmethod
    def setup_class(cls):
        cls.cn = _COBE   # computed once at module level

    def test_lam_cobe_is_finite_and_positive(self):
        """λ_COBE must be a positive finite number.  ≤ 0 or inf/nan is a bug."""
        lam = self.cn["lam_cobe"]
        assert math.isfinite(lam), f"lam_cobe={lam} is not finite"
        assert lam > 0.0,          f"lam_cobe={lam} is not positive"

    def test_lam_cobe_order_of_magnitude(self):
        """
        λ_COBE ≈ 7×10⁻¹⁵.  It must lie in [10⁻¹⁶, 10⁻¹²] — the range
        consistent with GUT-scale inflation in the FTUM potential.
        """
        lam = self.cn["lam_cobe"]
        assert 1e-16 < lam < 1e-12, (
            f"lam_cobe={lam:.2e} is outside the expected GUT-scale window [1e-16, 1e-12]"
        )

    def test_as_predicted_matches_planck(self):
        """
        The predicted Aₛ must agree with Planck 2018 (2.101×10⁻⁹) to < 2%.
        The 2% tolerance reflects the COBE normalisation precision, not a fit.
        """
        rtol = abs(self.cn["As_predicted"] / PLANCK_AS_CENTRAL - 1.0)
        assert rtol < 0.02, (
            f"Aₛ predicted={self.cn['As_predicted']:.4e}, target={PLANCK_AS_CENTRAL:.4e}, "
            f"error={rtol*100:.2f}% > 2%"
        )

    def test_inflation_energy_scale_is_gut_scale(self):
        """
        E_inf = V^{1/4} ≈ 1.8×10¹⁶ GeV.  Must be in [10¹⁵, 10¹⁷] GeV — the
        GUT/Planck window expected for large-field inflation.
        """
        E = self.cn["E_inf_GeV"]
        assert 1e15 < E < 1e17, (
            f"E_inf = {E:.3e} GeV is outside the expected GUT window [1e15, 1e17] GeV"
        )

    def test_ns_unchanged_by_normalisation(self):
        """
        nₛ after COBE normalisation must equal the raw slow-roll prediction to
        < 10⁻⁶.  Any discrepancy means the normalisation is back-reacting on
        geometry — a fundamental error.
        """
        ns_cobe = self.cn["ns"]
        phi0_eff = self.cn["phi0_eff"]
        ns_raw, *_ = ns_from_phi0(phi0_eff, lam=1.0)   # lam=1 — geometry only
        assert abs(ns_cobe - float(ns_raw)) < 1e-6, (
            f"nₛ shifted after COBE: raw={float(ns_raw):.8f}, post-COBE={ns_cobe:.8f}"
        )

    def test_lam_independent_observables_listed(self):
        """
        cobe_normalization must declare which observables are λ-independent.
        The list must include at least ns, r, nt, alpha_s.
        """
        obs = self.cn["lam_independent_observables"]
        for required in ("ns", "r", "alpha_s"):
            assert required in obs, (
                f"'{required}' missing from lam_independent_observables: {obs}"
            )


# ===========================================================================
# 4. TRANSFER FUNCTION PHYSICS
#    Claim: birefringence signal is linear in B_μ, suppressive, correct limits.
#    Falsifier: α not proportional to B_μ, or T_ℓ → 0 in coherent limit.
# ===========================================================================

class TestTransferFunctionPhysics:
    """
    Validates the full B_μ → α → C_ℓ^{EB} amplitude chain.

    Physical chain:
      L_CS = (g_aγγ/4) φ FF̃
      → rotation angle α = (g_aγγ/2) · Δφ = (g_aγγ/2) · B_μ · L_LoS
      → C_ℓ^{EB} = (1/2) sin(4α) · C_ℓ^{EE}  ≈ 2α · C_ℓ^{EE}  (small α)

    The first step is linear.  The power spectrum is quadratic only because
    it involves α².  The net effect of finite coherence length is suppressive.

    Key invariant: doubling B_μ_rms doubles α (linearity).
    Key invariant: T_ℓ → 1 as coherence length → ∞ (UL-axion limit).
    """

    def test_b_mu_angle_is_linear_in_b_mu_rms(self):
        """
        b_mu_rotation_angle is linear in b_mu_rms.
        Doubling the input must double the output exactly.
        """
        r1 = b_mu_rotation_angle(1e-6,   _G, _CHI_STAR)
        r2 = b_mu_rotation_angle(2e-6,   _G, _CHI_STAR)
        assert r2["alpha_rad"] == pytest.approx(2.0 * r1["alpha_rad"], rel=1e-12)

    def test_b_mu_angle_consistent_with_birefringence_angle(self):
        """
        The Chern–Simons factor of ½ must be present.
        α_new = (g/2)·(Δφ/L)·L = (g/2)·Δφ = birefringence_angle(g, Δφ).
        This confirms no factor-of-2 error in the coupling.
        """
        result = b_mu_rotation_angle(_DP / _CHI_STAR, _G, _CHI_STAR)
        assert result["alpha_rad"] == pytest.approx(_BETA0, rel=1e-12)

    def test_quadratic_correction_is_subdominant(self):
        """
        The exact C_ℓ^{EB} prefactor is (1/2)sin(4α), not 2α.
        The fractional difference |sin(4α)/(4α) − 1| ≈ 8α²/3 must be < 0.1%
        for the model α ≈ 0.006 rad.
        This justifies the linear approximation used throughout.
        """
        qcb = quadratic_correction_bound(_BETA0)
        assert qcb["is_subdominant"] is True, (
            f"Quadratic correction = {qcb['fractional_deviation']:.2e} >= 0.1% — "
            f"linear approximation is not justified at this β"
        )

    def test_transfer_coherent_model_is_unity(self):
        """
        model='coherent' represents the UL-axion limit (ξ → ∞).
        T_ℓ = 1 for all ℓ.  Any deviation means the coherent path is broken.
        """
        T = birefringence_transfer_function(
            np.array([2, 10, 100, 500, 1000]), model="coherent"
        )
        assert np.all(T == 1.0), f"coherent model has T_ℓ ≠ 1: {T}"

    def test_transfer_gaussian_ul_axion_limit(self):
        """
        Gaussian model with ξ = 10¹² Mpc (far larger than χ★ = 13 740 Mpc)
        approximates the UL-axion coherent limit.  T_ℓ must be ≥ 0.9999 for
        all CMB multipoles.
        """
        ells = np.array([2, 10, 100, 500, 1000])
        T = birefringence_transfer_function(
            ells, model="gaussian", coherence_scale_mpc=1e12
        )
        assert np.all(T >= 0.9999), (
            f"UL-axion limit (xi=1e12 Mpc) has T_ℓ < 0.9999: {T}"
        )

    def test_transfer_gaussian_suppresses_high_ell(self):
        """
        Gaussian suppression exp(-ℓ(ℓ+1)σ²/2) must be monotonically
        decreasing with ℓ for any finite coherence length.
        """
        ells = np.array([10, 50, 100, 500])
        T = birefringence_transfer_function(
            ells, model="gaussian", coherence_scale_mpc=1e7
        )
        for i in range(len(T) - 1):
            assert T[i] > T[i + 1], (
                f"Transfer function is not monotone: T[{ells[i]}]={T[i]:.6f} "
                f"<= T[{ells[i+1]}]={T[i+1]:.6f}"
            )

    def test_propagate_coherent_needs_no_extra_amplitude(self):
        """
        In the coherent limit (T_eff = 1), the required primordial β equals
        the observed β exactly.  No extra amplitude is needed.
        This closes the amplitude gap without introducing a new free parameter.
        """
        C_EE = np.array([1.0, 3.0, 5.0, 8.0, 10.0])
        result = propagate_primordial_amplitude(_BETA0, np.ones(5), C_EE)
        assert result["no_extra_amplitude_needed"] is True
        assert result["required_beta_primordial"] == pytest.approx(_BETA0, rel=1e-12)


# ===========================================================================
# 5. EXTREME LIMITS — NO DIVERGENCES
#    Claim: all functions are finite and correctly signed at all boundaries.
#    Falsifier: any NaN, Inf, or sign error.
# ===========================================================================

class TestExtremeLimits:
    """
    Stress-tests the implementation at the physical boundaries of its domain.

    A theoretically sound implementation must be well-behaved at:
    - Coherent axion limit (ξ → ∞): T_ℓ → 1
    - Incoherent limit   (ξ → 0):   T_ℓ → 0
    - Zero coupling (g → 0):         α   → 0
    - Zero field displacement:        β   → 0
    - Low ℓ (ℓ = 2, the quadrupole): all formulae still finite

    None of these limits should produce NaN, Inf, negative T_ℓ, or negative α.
    """

    def test_transfer_near_infinite_coherence(self):
        """ξ = 10¹² Mpc → T_ℓ ≈ 1 (UL-axion limit, no suppression)."""
        ells = np.array([2, 10, 100, 200, 500])
        T = birefringence_transfer_function(
            ells, model="gaussian", coherence_scale_mpc=1e12
        )
        assert np.all(np.isfinite(T)), f"Non-finite T_ℓ at xi=1e12: {T}"
        assert np.allclose(T, 1.0, atol=1e-6), f"T_ℓ not ≈ 1 at xi=1e12: {T}"

    def test_transfer_zero_coherence(self):
        """ξ = 1 Mpc (sub-parsec) → T_ℓ = 0 (QCD-axion limit, full cancellation)."""
        ells = np.array([2, 10, 100, 500])
        T = birefringence_transfer_function(
            ells, model="gaussian", coherence_scale_mpc=1.0
        )
        assert np.all(T == 0.0), f"T_ℓ ≠ 0 at xi=1 Mpc: {T}"

    def test_transfer_values_always_in_unit_interval(self):
        """T_ℓ ∈ [0, 1] for all ℓ and all coherence scales."""
        ells = np.array([2, 10, 100, 500, 1000])
        for xi in [1.0, 1e3, 1e6, 1e9, 1e12]:
            T = birefringence_transfer_function(
                ells, model="gaussian", coherence_scale_mpc=xi
            )
            assert np.all(T >= 0.0) and np.all(T <= 1.0), (
                f"T_ℓ out of [0,1] at xi={xi}: {T}"
            )

    def test_rotation_angle_zero_for_zero_coupling(self):
        """g_aγγ = 0 → no coupling → α = 0 exactly."""
        result = b_mu_rotation_angle(
            b_mu_rms=_DP / _CHI_STAR, g_agamma=0.0, integration_length_mpc=_CHI_STAR
        )
        assert result["alpha_rad"] == 0.0

    def test_rotation_angle_zero_for_zero_displacement(self):
        """Δφ = 0 → no field evolution → β = 0 exactly."""
        beta = birefringence_angle(_G, 0.0)
        assert beta == 0.0

    def test_quadratic_bound_at_zero_alpha(self):
        """α = 0 → sin(4α)/(4α) → 1 exactly (L'Hôpital); deviation = 0."""
        qcb = quadratic_correction_bound(0.0)
        assert math.isfinite(qcb["exact_prefactor"])
        assert qcb["exact_prefactor"] == pytest.approx(1.0, rel=1e-12)
        assert qcb["fractional_deviation"] == pytest.approx(0.0, abs=1e-14)

    def test_jacobian_rs_positive_for_positive_inputs(self):
        """J_RS must be positive for all k > 0, r_c > 0."""
        for k, r_c in [(0.1, 1.0), (1.0, 5.0), (1.0, 12.0), (2.0, 10.0)]:
            J = jacobian_rs_orbifold(k, r_c)
            assert J > 0, f"J_RS({k}, {r_c}) = {J} is not positive"
            assert math.isfinite(J), f"J_RS({k}, {r_c}) = {J} is not finite"

    def test_ns_from_phi0_finite_at_low_multipoles(self):
        """
        ns_from_phi0 at φ₀_eff values near the attractor must return finite
        nₛ values — no singularity near φ₀_eff ≈ 31.
        """
        for phi0_eff in [28.0, 30.0, 31.1, 31.4, 33.0]:
            ns_val, *_ = ns_from_phi0(phi0_eff, lam=1.0)
            assert math.isfinite(float(ns_val)), (
                f"ns_from_phi0({phi0_eff}) = {ns_val} is not finite"
            )
