# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: LicenseRef-DefensivePublicCommons-1.0
"""Pillar 523 — Architecture limit upgrade certificates.

🔵 ADJACENT TRACK — ARCHITECTURE_LIMIT_UPGRADED

Issues formal machine-readable upgrade certificates for Pillars 517 and 518:

  P517 upgrade:
    P_R_ARCHITECTURE_LIMIT_CERTIFIED (Pillar 517)
    → P_R_CONDITIONAL_DERIVATION_11D (Pillar 520)
    p_R is now derivable from 11D E8 gauge threshold + CY₃ volume geometry.
    Remaining open condition: Vol(CY₃) fixed by Pillar 521 moduli stabilization.
    Certificate names the remaining open condition explicitly.

  P518 upgrade:
    CMB_AMPLITUDE_ARCHITECTURE_LIMIT_CERTIFIED (Pillar 518)
    → CMB_AMPLITUDE_11D_PARTIAL_CLOSURE (Pillar 519)
    G₄-flux correction (Pillar 519) reduces the irreducible residual fraction.
    The remaining gap is bounded quantitatively as the true 5D-EFT floor,
    not an artifact of missing field content.

This is an epistemic audit step: it does not change hardgate scores but
formally closes the "ARCHITECTURE_LIMIT with no path forward" classification
and replaces it with bounded conditional status, which is stronger.

Status: ARCHITECTURE_LIMIT_UPGRADED
"""

from __future__ import annotations

from typing import Any, Dict

from src.eleventd.g4_flux_zphi_correction import g4_zphi_correction_report
from src.eleventd.e8_gauge_pr_derivation import e8_gauge_pr_report, VOL_CY3_FIDUCIAL
from src.eleventd.moduli_stabilization_nlo import moduli_stabilization_nlo_report

__all__ = [
    "p517_upgrade_certificate",
    "p518_upgrade_certificate",
    "architecture_limit_upgrade_report",
    "UPGRADE_REGISTRY",
]

# ── Prior status records ───────────────────────────────────────────────────────
PRIOR_STATUS_P517: str = "P_R_ARCHITECTURE_LIMIT_CERTIFIED"
PRIOR_STATUS_P518: str = "CMB_AMPLITUDE_ARCHITECTURE_LIMIT_CERTIFIED"
NEW_STATUS_P517: str = "P_R_CONDITIONAL_DERIVATION_11D"
NEW_STATUS_P518: str = "CMB_AMPLITUDE_11D_PARTIAL_CLOSURE"


def p517_upgrade_certificate(
    vol_cy3: float = VOL_CY3_FIDUCIAL,
    n_w: int = 5,
    k_cs: int = 74,
) -> Dict[str, Any]:
    """Issue the formal upgrade certificate for Pillar 517.

    Upgrades P_R_ARCHITECTURE_LIMIT_CERTIFIED → P_R_CONDITIONAL_DERIVATION_11D.

    Parameters
    ----------
    vol_cy3 : float
        CY₃ volume in Planck units (from Pillar 521 moduli stabilization).
    n_w : int
        Winding number.
    k_cs : int
        Chern-Simons level.

    Returns
    -------
    dict
        Machine-readable upgrade certificate with all transition metadata.
    """
    fiducial_report = e8_gauge_pr_report(VOL_CY3_FIDUCIAL, n_w, k_cs)
    cert_fiducial = fiducial_report["certificate"]

    vol_nlo = vol_cy3
    e8_nlo_report = e8_gauge_pr_report(vol_nlo, n_w, k_cs)
    cert_nlo = e8_nlo_report["certificate"]

    return {
        "pillar_upgraded": 517,
        "upgrading_pillar": 520,
        "prior_status": PRIOR_STATUS_P517,
        "new_status": NEW_STATUS_P517,
        "transition": (
            f"{PRIOR_STATUS_P517} → {NEW_STATUS_P517}"
        ),
        "physical_basis": (
            "11D E8 gauge threshold corrections on the Hořava-Witten UV brane "
            "provide the missing backreaction coupling identified as the obstruction "
            "in Pillar 517. With CY₃ volume from Pillar 521, p_R is conditionally derived."
        ),
        "p_r_conditional": cert_nlo["p_r_conditional"],
        "p_r_at_fiducial_vol": cert_fiducial["p_r_conditional"],
        "p_r_at_nlo_vol": cert_nlo["p_r_conditional"],
        "e8_threshold_correction": cert_nlo["e8_threshold_correction"],
        "vol_cy3_used": vol_nlo,
        "remaining_open_condition": cert_nlo["open_condition"],
        "upon_closure": cert_nlo["upon_closure"],
        "consistency_checks": cert_nlo["consistency_checks"],
        "upgrade_is_valid": bool(
            cert_nlo["consistency_checks"]["within_geometric_bounds"]
        ),
        "no_hardgate_score_change": True,
        "status": "ARCHITECTURE_LIMIT_UPGRADED",
    }


def p518_upgrade_certificate(
    chi: int = -200,
    pi_kr: float = 37.0,
    k_cs: int = 74,
) -> Dict[str, Any]:
    """Issue the formal upgrade certificate for Pillar 518.

    Upgrades CMB_AMPLITUDE_ARCHITECTURE_LIMIT_CERTIFIED
    → CMB_AMPLITUDE_11D_PARTIAL_CLOSURE.

    Parameters
    ----------
    chi : int
        CY₃ Euler characteristic.
    pi_kr : float
        πkR parameter.
    k_cs : int
        Chern-Simons level.

    Returns
    -------
    dict
        Machine-readable upgrade certificate with all transition metadata.
    """
    g4_report = g4_zphi_correction_report(chi, pi_kr, k_cs)
    cmb = g4_report["cmb_amplitude_residual"]

    return {
        "pillar_upgraded": 518,
        "upgrading_pillar": 519,
        "prior_status": PRIOR_STATUS_P518,
        "new_status": NEW_STATUS_P518,
        "transition": (
            f"{PRIOR_STATUS_P518} → {NEW_STATUS_P518}"
        ),
        "physical_basis": (
            "G₄-flux complex-structure moduli zero-point fluctuations (Pillar 519) "
            "contribute a quantitative additive correction δZ_φ^{G4} to the radion "
            "kinetic term, partially resolving the CMB acoustic peak amplitude gap. "
            "The remaining residual is the true 5D-EFT irreducible floor."
        ),
        "zphi_0": g4_report["zphi_0"],
        "zphi_nlo": g4_report["zphi_nlo"],
        "delta_zphi_g4": g4_report["delta_zphi_g4"],
        "sigma_residual_baseline_pct": cmb["sigma_at_zphi_0_pct"],
        "sigma_residual_nlo_pct": cmb["sigma_at_zphi_nlo_pct"],
        "fraction_resolved": cmb["fraction_resolved"],
        "pct_resolved": cmb["pct_resolved"],
        "irreducible_floor_label": "5D_IRREDUCIBLE_FLOOR",
        "irreducible_floor_interpretation": (
            "The remaining amplitude gap after 11D G4 correction is irreducible "
            "in any Kaluza-Klein EFT without new physics at a different scale. "
            "It is not an artifact of missing 11D field content — 11D G4 moduli "
            "have been exhausted. This is the 5D architecture floor."
        ),
        "upgrade_is_valid": bool(cmb["fraction_resolved"] > 0),
        "no_hardgate_score_change": True,
        "status": "ARCHITECTURE_LIMIT_UPGRADED",
    }


# ── Registry ──────────────────────────────────────────────────────────────────

def _build_upgrade_registry() -> Dict[str, str]:
    """Return the upgrade registry mapping old → new status."""
    return {
        PRIOR_STATUS_P517: NEW_STATUS_P517,
        PRIOR_STATUS_P518: NEW_STATUS_P518,
    }


#: Static registry of architecture limit upgrades issued by Pillar 523.
UPGRADE_REGISTRY: Dict[str, str] = _build_upgrade_registry()


def architecture_limit_upgrade_report(
    vol_cy3: float = VOL_CY3_FIDUCIAL,
    chi: int = -200,
    pi_kr: float = 37.0,
    k_cs: int = 74,
    n_w: int = 5,
) -> Dict[str, Any]:
    """Return the full Pillar 523 architecture limit upgrade report.

    Issues both upgrade certificates and verifies their validity.

    Returns
    -------
    dict
        Both upgrade certificates, summary status, and epistemic classification.
    """
    cert_p517 = p517_upgrade_certificate(vol_cy3, n_w, k_cs)
    cert_p518 = p518_upgrade_certificate(chi, pi_kr, k_cs)

    both_valid = cert_p517["upgrade_is_valid"] and cert_p518["upgrade_is_valid"]

    return {
        "pillar": 523,
        "title": "Architecture limit upgrade certificates for Pillars 517 and 518",
        "status": "ARCHITECTURE_LIMIT_UPGRADED",
        "track": "🔵 ADJACENT TRACK",
        "upgrade_registry": UPGRADE_REGISTRY,
        "p517_certificate": cert_p517,
        "p518_certificate": cert_p518,
        "summary": {
            "p517_upgrade_valid": cert_p517["upgrade_is_valid"],
            "p518_upgrade_valid": cert_p518["upgrade_is_valid"],
            "both_valid": both_valid,
            "upgrades_issued": 2,
        },
        "epistemic_note": (
            "This is an epistemic reclassification step only. "
            "No hardgate physics scores change. The prior ARCHITECTURE_LIMIT "
            "classifications were correct — they accurately identified what the "
            "5D-EFT alone cannot resolve. The upgrade acknowledges that 11D geometry "
            "provides a concrete partial resolution path, replacing 'no path forward' "
            "with a bounded conditional status. This is a stronger, not weaker, claim."
        ),
        "no_hardgate_score_change": True,
        "upstream_pillars": [517, 518, 519, 520, 521],
        "downstream_pillars": [522, 524],
    }
