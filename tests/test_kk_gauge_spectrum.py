"""tests/test_kk_gauge_spectrum.py
===================================
Tests for src/core/kk_gauge_spectrum.py

Verifies Gap 5 of UNIFICATION_PROOF.md §XII:
- U(1) IS produced by the 5D KK construction
- SU(2) and SU(3) are NOT produced
- The photon identification is correct
- The SM dimensional requirements are documented accurately
"""

import pytest
import numpy as np

from src.core.kk_gauge_spectrum import (
    kk_mode_mass,
    kk_spectrum_1d,
    gauge_group_from_5d,
    sm_dimensional_requirements,
    photon_identification,
    gap5_status,
    KKMode,
)


# ---------------------------------------------------------------------------
# kk_mode_mass
# ---------------------------------------------------------------------------

class TestKKModeMass:
    def test_zero_mode_massless(self):
        """The n=0 mode must be exactly massless."""
        m = kk_mode_mass(n=0, R=1.0)
        assert m == 0.0

    def test_first_kk_mass(self):
        """m₁ = 1/R."""
        np.testing.assert_allclose(kk_mode_mass(n=1, R=2.0), 0.5)

    def test_negative_n_same_as_positive(self):
        """KK masses are symmetric: m_{-n} = m_n."""
        for n in [1, 2, 3]:
            assert kk_mode_mass(n, R=1.0) == kk_mode_mass(-n, R=1.0)

    def test_mass_scales_with_1_over_R(self):
        """Doubling R halves the KK mass."""
        assert kk_mode_mass(1, R=1.0) == 2 * kk_mode_mass(1, R=2.0)

    def test_planck_scale_for_phi0_equals_1(self):
        """For R = φ₀ ℓ_P = 1 (Planck units), first KK mass = 1 (Planck mass)."""
        m = kk_mode_mass(n=1, R=1.0)
        np.testing.assert_allclose(m, 1.0)


# ---------------------------------------------------------------------------
# kk_spectrum_1d
# ---------------------------------------------------------------------------

class TestKKSpectrum1d:
    def test_returns_list_of_kkmode(self):
        modes = kk_spectrum_1d()
        assert isinstance(modes, list)
        assert all(isinstance(m, KKMode) for m in modes)

    def test_total_count(self):
        modes = kk_spectrum_1d(n_modes=3)
        assert len(modes) == 2 * 3 + 1   # n = -3..+3 → 7 modes

    def test_zero_mode_present_and_massless(self):
        modes = kk_spectrum_1d()
        zero_modes = [m for m in modes if m.n == 0]
        assert len(zero_modes) == 1
        assert zero_modes[0].mass == 0.0

    def test_zero_mode_is_u1(self):
        modes = kk_spectrum_1d()
        zero = [m for m in modes if m.n == 0][0]
        assert 'U(1)' in zero.gauge_group

    def test_massive_modes_are_u1_kk(self):
        """All n≠0 modes should be KK U(1) modes, not SU(2) or SU(3)."""
        modes = kk_spectrum_1d(n_modes=5)
        for m in modes:
            if m.n != 0:
                assert 'SU(2)' not in m.gauge_group
                assert 'SU(3)' not in m.gauge_group

    def test_masses_positive(self):
        modes = kk_spectrum_1d()
        for m in modes:
            assert m.mass >= 0.0

    def test_mass_formula(self):
        """m_n = |n|/R."""
        R = 2.0
        modes = kk_spectrum_1d(R=R, n_modes=3)
        for m in modes:
            np.testing.assert_allclose(m.mass, abs(m.n) / R, rtol=1e-10)


# ---------------------------------------------------------------------------
# gauge_group_from_5d
# ---------------------------------------------------------------------------

class TestGaugeGroupFrom5d:
    def test_returns_dict(self):
        g = gauge_group_from_5d()
        assert isinstance(g, dict)

    def test_produced_is_u1(self):
        """5D KK must produce U(1)."""
        g = gauge_group_from_5d()
        assert 'U(1)' in g['produced']

    def test_su2_not_produced(self):
        """SU(2) must NOT be in the produced gauge group."""
        g = gauge_group_from_5d()
        assert 'SU(2)' in str(g['NOT_produced'])

    def test_su3_not_produced(self):
        """SU(3) must NOT be in the produced gauge group."""
        g = gauge_group_from_5d()
        assert 'SU(3)' in str(g['NOT_produced'])

    def test_correction_statement_present(self):
        """Must contain an honest correction of the overclaim."""
        g = gauge_group_from_5d()
        combined = str(g.get('what_this_means_for_current_theory', ''))
        assert 'overclaim' in combined.lower() or 'corrected' in combined.lower()


# ---------------------------------------------------------------------------
# sm_dimensional_requirements
# ---------------------------------------------------------------------------

class TestSMDimensionalRequirements:
    def test_returns_list(self):
        r = sm_dimensional_requirements()
        assert isinstance(r, list)
        assert len(r) >= 3

    def test_em_requires_1_extra_dim(self):
        r = sm_dimensional_requirements()
        em = [x for x in r if 'U(1)' in x.get('gauge_group', '')
              and 'Electro' in x.get('force', '')][0]
        assert em['extra_dims_needed'] == 1

    def test_su2_requires_more_than_1_dim(self):
        r = sm_dimensional_requirements()
        su2 = [x for x in r if 'SU(2)' in x.get('gauge_group', '')][0]
        assert su2['extra_dims_needed'] > 1

    def test_su3_requires_more_than_su2(self):
        r = sm_dimensional_requirements()
        su2_dims = [x['extra_dims_needed'] for x in r
                    if 'SU(2)' in x.get('gauge_group', '')]
        su3_dims = [x['extra_dims_needed'] for x in r
                    if 'SU(3)' in x.get('gauge_group', '')]
        if su2_dims and su3_dims:
            assert su3_dims[0] >= su2_dims[0]

    def test_em_present_in_5d_theory(self):
        r = sm_dimensional_requirements()
        em = [x for x in r if 'Electro' in x.get('force', '')][0]
        assert '✓' in em['status_in_5d_theory']

    def test_su2_not_present_in_5d_theory(self):
        r = sm_dimensional_requirements()
        su2 = [x for x in r if 'SU(2)' in x.get('gauge_group', '')][0]
        assert '✗' in su2['status_in_5d_theory']

    def test_su3_not_present_in_5d_theory(self):
        r = sm_dimensional_requirements()
        su3 = [x for x in r if 'SU(3)' in x.get('gauge_group', '')][0]
        assert '✗' in su3['status_in_5d_theory']

    def test_chiral_requires_11d(self):
        """Witten (1981): chirality requires 11D total."""
        r = sm_dimensional_requirements()
        chiral = [x for x in r if 'hiral' in x.get('force', '')]
        if chiral:
            note = chiral[0].get('note', '')
            assert '11' in note


# ---------------------------------------------------------------------------
# photon_identification
# ---------------------------------------------------------------------------

class TestPhotonIdentification:
    def test_returns_dict(self):
        p = photon_identification()
        assert isinstance(p, dict)

    def test_zero_mode_is_massless(self):
        p = photon_identification()
        assert p['zero_mode_mass'] == 0.0

    def test_identification_valid(self):
        p = photon_identification()
        assert p['identification_valid'] is True

    def test_gauge_symmetry_is_u1(self):
        p = photon_identification()
        assert 'U(1)' in p['zero_mode_gauge_symmetry']

    def test_first_kk_mass_planck_scale(self):
        """First KK mode at Planck scale (φ₀ = 1) → m₁ = 1."""
        p = photon_identification(phi0=1.0)
        np.testing.assert_allclose(p['first_kk_mass'], 1.0)

    def test_potential_formula_correct(self):
        p = photon_identification(lam=2.0)
        assert '2' in p['electromagnetic_potential']
        assert 'Bμ' in p['electromagnetic_potential'] or 'B' in p['electromagnetic_potential']

    def test_overclaim_warning_present(self):
        """Must warn that W/Z/gluon identifications are not rigorous."""
        p = photon_identification()
        note = p.get('note', '')
        assert 'W' in note or 'Z' in note or 'gluon' in note


# ---------------------------------------------------------------------------
# gap5_status
# ---------------------------------------------------------------------------

class TestGap5Status:
    def test_returns_string(self):
        assert isinstance(gap5_status(), str)

    def test_mentions_partial_resolution(self):
        s = gap5_status()
        assert 'RESOLVED' in s
        assert 'REMAINS' in s

    def test_mentions_u1(self):
        assert 'U(1)' in gap5_status()

    def test_mentions_witten(self):
        assert 'Witten' in gap5_status() or '11D' in gap5_status() or '11' in gap5_status()
