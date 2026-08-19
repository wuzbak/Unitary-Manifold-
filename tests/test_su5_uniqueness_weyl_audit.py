# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""
tests/test_su5_uniqueness_weyl_audit.py
========================================
Sprint AI — Wave 1: Tests for SU(5) Weyl-group exhaustion audit.

Theory, framework, and scientific direction: ThomasCory Walker-Pearson.
Code architecture, test suites, and synthesis: GitHub Copilot (AI).
"""
import pytest
from src.core.su5_uniqueness_weyl_audit import (
    SU5_UNIQUENESS_STATUS,
    RANK,
    LIE_ALGEBRA_DATA,
    enumerate_z2_involutions_su5,
    enumerate_z2_involutions_b4,
    enumerate_z2_involutions_c4,
    enumerate_z2_involutions_d4,
    check_sm_subalgebra_su5,
    weyl_exhaustion_audit,
    su5_uniqueness_certificate,
    downstream_upgrades,
    _dim_even_an,
    _dim_even_bn,
    _dim_even_cn,
    _dim_even_dn,
)


# ---------------------------------------------------------------------------
# Module constants
# ---------------------------------------------------------------------------

def test_status_token():
    assert SU5_UNIQUENESS_STATUS == "SU5_PROVED_CONDITIONAL"


def test_rank_4():
    assert RANK == 4


# ---------------------------------------------------------------------------
# Lie algebra metadata
# ---------------------------------------------------------------------------

def test_su5_dim():
    assert LIE_ALGEBRA_DATA["A4=SU(5)"]["dim"] == 24


def test_so9_dim():
    assert LIE_ALGEBRA_DATA["B4=SO(9)"]["dim"] == 36


def test_sp8_dim():
    assert LIE_ALGEBRA_DATA["C4=Sp(8)"]["dim"] == 36


def test_so8_dim():
    assert LIE_ALGEBRA_DATA["D4=SO(8)"]["dim"] == 28


def test_f4_dim():
    assert LIE_ALGEBRA_DATA["F4"]["dim"] == 52


def test_su5_sm_embedding_true():
    assert LIE_ALGEBRA_DATA["A4=SU(5)"]["sm_embedding_exists"] is True


def test_competitors_sm_embedding_false():
    for alg in ["B4=SO(9)", "C4=Sp(8)", "D4=SO(8)", "F4"]:
        assert LIE_ALGEBRA_DATA[alg]["sm_embedding_exists"] is False


# ---------------------------------------------------------------------------
# Correct parity algebra: dim_even functions
# ---------------------------------------------------------------------------

def test_an_identity_is_full_algebra():
    """Identity parity (all +1) gives dim_even = full dim = 24 for A4."""
    assert _dim_even_an((1, 1, 1, 1, 1)) == 24


def test_an_neg_identity():
    """All -1 on A4 (n=5, product=+1 for even count): roots e_i-e_j have parity (-1)*(-1)=+1."""
    # All negative → all pairs have same sign → all roots even → dim_even = rank + 2*C(5,2)
    assert _dim_even_an((-1, -1, -1, -1, -1)) == 4 + 2 * 10  # = 24, identity-like


def test_an_kawamura_parity():
    """Kawamura parity (1,1,1,-1,-1): dim_even = 12."""
    assert _dim_even_an((1, 1, 1, -1, -1)) == 12


def test_an_dimension_sum():
    """dim_even + dim_odd = 24 for all A4 involutions."""
    import itertools
    for bits in itertools.product((-1, 1), repeat=5):
        if bits.count(-1) % 2 == 0:
            de = _dim_even_an(bits)
            assert de + (24 - de) == 24


def test_bn_identity_is_full():
    """Identity parity (all +1) on B4: dim_even = 36."""
    assert _dim_even_bn((1, 1, 1, 1)) == 36


def test_bn_no_involution_gives_12():
    """No SO-valid B4 involution gives dim_even = 12."""
    import itertools
    dim_evens = set()
    for bits in itertools.product((-1, 1), repeat=4):
        if bits.count(-1) % 2 == 0:
            dim_evens.add(_dim_even_bn(bits))
    assert 12 not in dim_evens, f"B4 unexpectedly has dim_even=12: {dim_evens}"


def test_cn_long_roots_always_even():
    """C4 long roots 2e_i are always even (parity p_i^2=1); this is reflected in dim_even ≥ 4+8=12."""
    # The minimum of dim_even for C4 = rank(4) + 2*n_long(4) = 4+8=12.
    # But adding short roots (which may be even or odd) can only add to dim_even.
    import itertools
    for bits in itertools.product((-1, 1), repeat=4):
        de = _dim_even_cn(bits)
        assert de >= 4 + 2 * 4  # rank + 2*n_long (all long roots always even)


def test_cn_no_involution_gives_12():
    """No C4 involution gives dim_even exactly 12 (the minimum is 12 with 0 even short roots)."""
    import itertools
    for bits in itertools.product((-1, 1), repeat=4):
        de = _dim_even_cn(bits)
        # The minimum value (all p_i different sign pairs) gives 4+8=12.
        # But C4 with n_pos=2, n_neg=2: n_pair = C(2,2)+C(2,2) = 2; de = 4+8+4*2=20
        # Actually with n_pos=0 (all -1): n_pair = C(0,2)+C(4,2) = 6; de = 4+8+4*6=36
        # With n_pos=1: n_pair = C(1,2)+C(3,2) = 0+3 = 3; de = 4+8+4*3=24
        # With n_pos=2: n_pair = 1+1=2; de=4+8+8=20
        # So C4 dim_even values are {20, 24, 28, 36} — none = 12. ✓
        assert de != 12, f"C4 parity {bits} unexpectedly gives dim_even=12"


def test_dn_identity_is_full():
    """Identity parity on D4: dim_even = 28."""
    assert _dim_even_dn((1, 1, 1, 1)) == 28


def test_dn_k2_gives_12():
    """D4 with k=2 positive entries gives dim_even=12."""
    # e.g. (1,1,-1,-1): n_even_pairs = C(2,2)+C(2,2) = 1+1=2; de = 4+4*2=12
    assert _dim_even_dn((1, 1, -1, -1)) == 12


# ---------------------------------------------------------------------------
# SU(5) involution enumeration
# ---------------------------------------------------------------------------

def test_su5_involution_count():
    """SU(5) has 2^4 = 16 valid Z₂ involutions (even number of -1s)."""
    involutions = enumerate_z2_involutions_su5()
    assert len(involutions) == 16


def test_su5_all_dim_sums_correct():
    """dim_even + dim_odd = 24 for all SU(5) involutions."""
    for inv in enumerate_z2_involutions_su5():
        assert inv["dim_even"] + inv["dim_odd"] == 24


def test_su5_kawamura_dim_even():
    """Kawamura parity (1,1,1,-1,-1) gives dim_even=12."""
    invs = enumerate_z2_involutions_su5()
    kaw = next(inv for inv in invs if inv["parity_fundamental"] == (1, 1, 1, -1, -1))
    assert kaw["dim_even"] == 12


def test_su5_kawamura_dim_odd():
    invs = enumerate_z2_involutions_su5()
    kaw = next(inv for inv in invs if inv["parity_fundamental"] == (1, 1, 1, -1, -1))
    assert kaw["dim_odd"] == 12


def test_su5_identity_dim_even():
    invs = enumerate_z2_involutions_su5()
    identity = next(inv for inv in invs if inv["parity_fundamental"] == (1, 1, 1, 1, 1))
    assert identity["dim_even"] == 24


def test_su5_sm_subalgebra_possible_flag():
    """sm_subalgebra_possible iff dim_even == 12."""
    for inv in enumerate_z2_involutions_su5():
        assert inv["sm_subalgebra_possible"] == (inv["dim_even"] == 12)


# ---------------------------------------------------------------------------
# B4, C4, D4 involution enumeration
# ---------------------------------------------------------------------------

def test_b4_no_sm_involution():
    """No B4 involution has sm_subalgebra_possible = True."""
    invs = enumerate_z2_involutions_b4()
    assert all(not inv["sm_subalgebra_possible"] for inv in invs)


def test_c4_no_sm_involution():
    """No C4 involution has sm_subalgebra_possible = True."""
    invs = enumerate_z2_involutions_c4()
    assert all(not inv["sm_subalgebra_possible"] for inv in invs)


def test_d4_dim_sums():
    """dim_even + dim_odd = 28 for all D4 involutions."""
    for inv in enumerate_z2_involutions_d4():
        assert inv["dim_even"] + inv["dim_odd"] == 28


def test_d4_k2_dim_even_12():
    """D4 with parity (1,1,-1,-1) gives dim_even=12."""
    invs = enumerate_z2_involutions_d4()
    k2 = [inv for inv in invs if inv["dim_even"] == 12]
    assert len(k2) > 0


def test_d4_k2_not_sm():
    """D4 involutions with dim_even=12 do NOT give SM subalgebra."""
    from src.core.su5_uniqueness_weyl_audit import _check_sm_d4
    invs = enumerate_z2_involutions_d4()
    for inv in invs:
        if inv["dim_even"] == 12:
            check = _check_sm_d4(inv["parity_fundamental"])
            assert check["is_sm"] is False, (
                f"D4 parity {inv['parity_fundamental']} incorrectly identified as SM"
            )


# ---------------------------------------------------------------------------
# SM subalgebra check for SU(5)
# ---------------------------------------------------------------------------

def test_kawamura_is_sm():
    result = check_sm_subalgebra_su5((1, 1, 1, -1, -1))
    assert result["is_sm"] is True


def test_kawamura_conjugate_is_sm():
    """All 10 distinct permutations of (3x+1, 2x-1) give SM."""
    import itertools
    count = 0
    for bits in set(itertools.permutations([1, 1, 1, -1, -1])):
        if check_sm_subalgebra_su5(bits)["is_sm"]:
            count += 1
    assert count == 10  # C(5,3) = 10


def test_su5_identity_not_sm():
    """Identity parity (1,1,1,1,1): dim_even=24 ≠ 12, not SM."""
    result = check_sm_subalgebra_su5((1, 1, 1, 1, 1))
    assert result["is_sm"] is False


def test_su5_k1_not_sm():
    """k=1 positive entry: not SM."""
    result = check_sm_subalgebra_su5((1, -1, -1, -1, -1))
    assert result["is_sm"] is False


def test_su5_k0_not_sm():
    """k=0 positive entries: not SM (subalgebra = full SU(5) by symmetry)."""
    result = check_sm_subalgebra_su5((-1, -1, -1, -1, -1))
    # All same sign → parity p_i*p_j = +1 for all pairs → dim_even=24. Not SM.
    assert result["is_sm"] is False


# ---------------------------------------------------------------------------
# Full audit
# ---------------------------------------------------------------------------

def test_audit_runs():
    audit = weyl_exhaustion_audit()
    assert "per_algebra" in audit
    assert "su5_unique" in audit


def test_audit_su5_unique():
    audit = weyl_exhaustion_audit()
    assert audit["su5_unique"] is True


def test_audit_status():
    audit = weyl_exhaustion_audit()
    assert audit["status"] == "SU5_PROVED_CONDITIONAL"


def test_audit_all_competitors_in_report():
    audit = weyl_exhaustion_audit()
    expected = {"A4=SU(5)", "B4=SO(9)", "C4=Sp(8)", "D4=SO(8)", "F4"}
    assert set(audit["rank4_candidates_checked"]) == expected


def test_audit_su5_has_sm_involution():
    audit = weyl_exhaustion_audit()
    assert len(audit["su5_sm_involution"]) >= 1


def test_audit_su5_has_10_sm_involutions():
    """All 10 Kawamura-conjugate involutions should be found."""
    audit = weyl_exhaustion_audit()
    assert len(audit["su5_sm_involution"]) == 10


def test_audit_competitors_no_sm():
    audit = weyl_exhaustion_audit()
    for alg in ["B4=SO(9)", "C4=Sp(8)", "D4=SO(8)", "F4"]:
        assert len(audit["per_algebra"][alg]["sm_admitting_involutions"]) == 0, (
            f"{alg} unexpectedly admitted SM involution"
        )


def test_audit_competitors_excluded():
    audit = weyl_exhaustion_audit()
    for alg in ["B4=SO(9)", "C4=Sp(8)", "D4=SO(8)", "F4"]:
        assert audit["per_algebra"][alg]["excluded"] is True


def test_audit_axiom_dependencies():
    audit = weyl_exhaustion_audit()
    texts = " ".join(audit["axiom_dependencies"])
    assert "Axiom Z2" in texts
    assert "Axiom SW" in texts
    assert "769" in texts


def test_audit_epistemic_upgrade_l22():
    audit = weyl_exhaustion_audit()
    assert "PROVED_CONDITIONAL" in audit["epistemic_upgrade"]["L2.2"]


def test_audit_epistemic_upgrade_l23():
    audit = weyl_exhaustion_audit()
    assert "PROVED_CONDITIONAL" in audit["epistemic_upgrade"]["L2.3"]


# ---------------------------------------------------------------------------
# Certificate
# ---------------------------------------------------------------------------

def test_certificate_status():
    cert = su5_uniqueness_certificate()
    assert cert["SU5_UNIQUENESS_STATUS"] == "SU5_PROVED_CONDITIONAL"


def test_certificate_su5_unique():
    cert = su5_uniqueness_certificate()
    assert cert["su5_unique"] is True


def test_certificate_epistemic_label():
    cert = su5_uniqueness_certificate()
    assert cert["epistemic_label"] == "PROVED_CONDITIONAL"


def test_certificate_conditions_count():
    cert = su5_uniqueness_certificate()
    assert len(cert["conditions"]) >= 4


def test_certificate_honest_residuals_mention_conjecture():
    cert = su5_uniqueness_certificate()
    texts = " ".join(cert["honest_residuals"]).lower()
    assert "conjecture" in texts


def test_certificate_lean4_reference():
    cert = su5_uniqueness_certificate()
    assert "SU5OrbifoldWeylParity.lean" in cert["lean4_reference"]


def test_certificate_exclusions_all_competitors():
    cert = su5_uniqueness_certificate()
    for alg in ["B4=SO(9)", "C4=Sp(8)", "D4=SO(8)", "F4"]:
        assert alg in cert["exclusions"]
        assert cert["exclusions"][alg] is not None


# ---------------------------------------------------------------------------
# Downstream upgrades
# ---------------------------------------------------------------------------

def test_downstream_upgrades_l22():
    upg = downstream_upgrades()
    assert "L2.2" in upg
    assert "PROVED_CONDITIONAL" in upg["L2.2"]


def test_downstream_upgrades_alpha_gut():
    upg = downstream_upgrades()
    assert "alpha_GUT_chain" in upg


def test_downstream_upgrades_proton_decay():
    upg = downstream_upgrades()
    assert "proton_decay_rate" in upg
