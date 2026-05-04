# Copyright (C) 2026  ThomasCory Walker-Pearson
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Pillar STEWARD — Self-executing birefringence falsification check.

This module encodes the primary falsification condition of the Unitary Manifold
in a form that any competent physicist can execute without understanding the full
167-pillar framework.

Usage (command line):
    python src/core/falsification_check.py --beta VALUE --sigma UNCERTAINTY

    Example:
        python src/core/falsification_check.py --beta 0.331 --sigma 0.02
        # Returns: CONFIRMED (5,7) PRIMARY SECTOR

    Returns one of four verdicts:
        FALSIFIED        — β outside [0.22°, 0.38°] or in gap [0.29°, 0.31°] at ≥ 3σ
        DISFAVOURED      — β in gap [0.29°, 0.31°] at 1–3σ, or in tension but not falsified
        CONFIRMED        — β consistent with a specific predicted sector at ≥ 1σ proximity
        CONSISTENT       — β in window but not near a specific sector prediction

    See:
        3-FALSIFICATION/OBSERVATION_TRACKER.md  — living prediction registry
        STEWARDSHIP.md §5                       — falsification protocol
        FALLIBILITY.md Admission 1–2            — epistemic status of predictions
        src/core/inflation.py                   — birefringence_angle() derivation
"""

from __future__ import annotations

import argparse
import sys

# ──────────────────────────────────────────────────────────────────────────────
# Prediction constants (Pillar 27 / Pillar 95 / FALLIBILITY.md)
# ──────────────────────────────────────────────────────────────────────────────

# Predicted birefringence angles (degrees)
BETA_PRIMARY = 0.331    # (5,7) primary sector, k_CS = 74
BETA_SHADOW = 0.273     # (5,6) shadow sector, k_CS = 61

# Internal theory uncertainty (quadrature of r_c and φ_min_bare sources)
BETA_THEORY_UNCERTAINTY = 0.007  # degrees

# Falsification window: β must fall in [BETA_MIN, BETA_MAX]
BETA_MIN = 0.22   # degrees — below this at ≥ 3σ: FALSIFIED
BETA_MAX = 0.38   # degrees — above this at ≥ 3σ: FALSIFIED

# Forbidden gap: β in (BETA_GAP_LO, BETA_GAP_HI) at ≥ 3σ: FALSIFIED
BETA_GAP_LO = 0.29  # degrees
BETA_GAP_HI = 0.31  # degrees

# Standard sigma thresholds
SIGMA_FALSIFICATION = 3.0  # σ required for falsification claim
SIGMA_DISFAVOUR = 1.0      # σ at which we begin to disfavour
SIGMA_CONFIRM = 1.0        # proximity in σ to a specific prediction to say "confirmed"


# ──────────────────────────────────────────────────────────────────────────────
# Core logic
# ──────────────────────────────────────────────────────────────────────────────

class FalsificationResult:
    """Container for the verdict and human-readable explanation."""

    VERDICTS = ("FALSIFIED", "DISFAVOURED", "CONFIRMED", "CONSISTENT")

    def __init__(
        self,
        verdict: str,
        message: str,
        sector: str | None = None,
        sigma_from_window_edge: float | None = None,
        sigma_from_prediction: float | None = None,
    ):
        if verdict not in self.VERDICTS:
            raise ValueError(f"Unknown verdict: {verdict!r}. Must be one of {self.VERDICTS}")
        self.verdict = verdict
        self.message = message
        self.sector = sector
        self.sigma_from_window_edge = sigma_from_window_edge
        self.sigma_from_prediction = sigma_from_prediction

    def __str__(self) -> str:
        lines = [f"VERDICT: {self.verdict}"]
        if self.sector:
            lines.append(f"SECTOR:  {self.sector}")
        lines.append(f"DETAIL:  {self.message}")
        return "\n".join(lines)

    def is_falsified(self) -> bool:
        return self.verdict == "FALSIFIED"

    def is_confirmed(self) -> bool:
        return self.verdict == "CONFIRMED"


def check_falsification(beta: float, sigma: float) -> FalsificationResult:
    """
    Apply the primary falsification conditions of the Unitary Manifold.

    Parameters
    ----------
    beta : float
        Measured birefringence angle in degrees.
    sigma : float
        1σ measurement uncertainty in degrees. Must be positive.

    Returns
    -------
    FalsificationResult
        Verdict with explanation. See module docstring for verdict definitions.

    Raises
    ------
    ValueError
        If sigma is not positive.
    """
    if sigma <= 0:
        raise ValueError(f"sigma must be positive, got {sigma}")

    # ── 1. Check if β is outside the admissible window ────────────────────────
    # "below minimum" case: β + N*σ < BETA_MIN  (i.e. the upper end of the
    #  measurement range is still below the minimum) is handled by asking whether
    #  beta < BETA_MIN and the distance to BETA_MIN is > 3σ.
    dist_below_min = BETA_MIN - beta          # positive if beta < BETA_MIN
    dist_above_max = beta - BETA_MAX          # positive if beta > BETA_MAX

    if dist_below_min > 0:
        sigmas_below = dist_below_min / sigma
        if sigmas_below >= SIGMA_FALSIFICATION:
            return FalsificationResult(
                verdict="FALSIFIED",
                message=(
                    f"β = {beta:.4f}° is {sigmas_below:.1f}σ below the minimum admissible "
                    f"value {BETA_MIN}°. The braided-winding mechanism is excluded. "
                    "See STEWARDSHIP.md §5 for the falsification protocol."
                ),
                sigma_from_window_edge=sigmas_below,
            )
        else:
            return FalsificationResult(
                verdict="DISFAVOURED",
                message=(
                    f"β = {beta:.4f}° is {sigmas_below:.1f}σ below the minimum admissible "
                    f"value {BETA_MIN}°. Below 3σ — not yet falsified, but disfavoured. "
                    "Monitor as uncertainty decreases."
                ),
                sigma_from_window_edge=sigmas_below,
            )

    if dist_above_max > 0:
        sigmas_above = dist_above_max / sigma
        if sigmas_above >= SIGMA_FALSIFICATION:
            return FalsificationResult(
                verdict="FALSIFIED",
                message=(
                    f"β = {beta:.4f}° is {sigmas_above:.1f}σ above the maximum admissible "
                    f"value {BETA_MAX}°. The braided-winding mechanism is excluded. "
                    "See STEWARDSHIP.md §5 for the falsification protocol."
                ),
                sigma_from_window_edge=sigmas_above,
            )
        else:
            return FalsificationResult(
                verdict="DISFAVOURED",
                message=(
                    f"β = {beta:.4f}° is {sigmas_above:.1f}σ above the maximum admissible "
                    f"value {BETA_MAX}°. Below 3σ — not yet falsified, but disfavoured. "
                    "Monitor as uncertainty decreases."
                ),
                sigma_from_window_edge=sigmas_above,
            )

    # ── 2. Check if β is in the forbidden inter-sector gap ────────────────────
    # Gap: (BETA_GAP_LO, BETA_GAP_HI). The measurement lands in the gap when
    # the 3σ interval is entirely within the gap, i.e.
    #   beta > BETA_GAP_LO + 3σ   AND   beta < BETA_GAP_HI - 3σ
    # For disfavour: beta is central in the gap region regardless.
    in_gap_center = BETA_GAP_LO < beta < BETA_GAP_HI
    dist_gap_lo = beta - BETA_GAP_LO         # positive if beta > BETA_GAP_LO
    dist_gap_hi = BETA_GAP_HI - beta         # positive if beta < BETA_GAP_HI

    if in_gap_center:
        # How many σ from either gap edge?
        sigmas_from_lo = dist_gap_lo / sigma
        sigmas_from_hi = dist_gap_hi / sigma
        # Fully in gap at 3σ means the measurement 3σ interval doesn't touch either edge
        fully_in_gap = (sigmas_from_lo >= SIGMA_FALSIFICATION and
                        sigmas_from_hi >= SIGMA_FALSIFICATION)
        if fully_in_gap:
            return FalsificationResult(
                verdict="FALSIFIED",
                message=(
                    f"β = {beta:.4f}° lands in the predicted inter-sector gap "
                    f"({BETA_GAP_LO}°, {BETA_GAP_HI}°) at ≥ 3σ from both edges "
                    f"({sigmas_from_lo:.1f}σ from lower, {sigmas_from_hi:.1f}σ from upper). "
                    "Neither the (5,7) nor the (5,6) sector is consistent. "
                    "See STEWARDSHIP.md §5 for the falsification protocol."
                ),
            )
        else:
            return FalsificationResult(
                verdict="DISFAVOURED",
                message=(
                    f"β = {beta:.4f}° is in the predicted inter-sector gap "
                    f"({BETA_GAP_LO}°, {BETA_GAP_HI}°), but the 3σ interval overlaps "
                    "with at least one sector edge. Not yet falsified, but disfavoured. "
                    "Monitor as uncertainty decreases."
                ),
            )

    # ── 3. β is in the admissible window and not in the gap ──────────────────
    # Check proximity to each sector prediction.
    sigma_from_primary = abs(beta - BETA_PRIMARY) / sigma
    sigma_from_shadow = abs(beta - BETA_SHADOW) / sigma

    if sigma_from_primary <= SIGMA_CONFIRM:
        return FalsificationResult(
            verdict="CONFIRMED",
            message=(
                f"β = {beta:.4f}° is {sigma_from_primary:.2f}σ from the (5,7) primary "
                f"sector prediction ({BETA_PRIMARY}°). "
                "PRIMARY SECTOR SUPPORTED. Note: the (5,6) shadow sector is not yet "
                "excluded — this is not a proof of the full framework."
            ),
            sector="(5,7) primary — k_CS=74, β=0.331°",
            sigma_from_prediction=sigma_from_primary,
        )

    if sigma_from_shadow <= SIGMA_CONFIRM:
        return FalsificationResult(
            verdict="CONFIRMED",
            message=(
                f"β = {beta:.4f}° is {sigma_from_shadow:.2f}σ from the (5,6) shadow "
                f"sector prediction ({BETA_SHADOW}°). "
                "SHADOW SECTOR SUPPORTED. The (5,7) primary sector is disfavoured by "
                f"{sigma_from_primary:.1f}σ."
            ),
            sector="(5,6) shadow — k_CS=61, β=0.273°",
            sigma_from_prediction=sigma_from_shadow,
        )

    # ── 4. In window but not near a prediction ────────────────────────────────
    return FalsificationResult(
        verdict="CONSISTENT",
        message=(
            f"β = {beta:.4f}° ± {sigma:.4f}° is within the admissible window "
            f"[{BETA_MIN}°, {BETA_MAX}°] and not in the forbidden gap, but is "
            f"{sigma_from_primary:.1f}σ from the (5,7) primary prediction and "
            f"{sigma_from_shadow:.1f}σ from the (5,6) shadow prediction. "
            "CONSISTENT but not discriminating — the framework survives this measurement."
        ),
        sigma_from_prediction=min(sigma_from_primary, sigma_from_shadow),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Convenience summary
# ──────────────────────────────────────────────────────────────────────────────

def summary() -> str:
    """Return a one-screen summary of all falsification conditions."""
    return (
        "Unitary Manifold — Birefringence Falsification Conditions\n"
        "==========================================================\n"
        f"  Primary prediction:  β = {BETA_PRIMARY}° ± {BETA_THEORY_UNCERTAINTY}°  [(5,7) sector, k_CS=74]\n"
        f"  Shadow prediction:   β = {BETA_SHADOW}° ± {BETA_THEORY_UNCERTAINTY}°  [(5,6) sector, k_CS=61]\n"
        f"  Admissible window:   β ∈ [{BETA_MIN}°, {BETA_MAX}°]\n"
        f"  Forbidden gap:       β ∈ ({BETA_GAP_LO}°, {BETA_GAP_HI}°)\n"
        f"  Falsification σ:     ≥ {SIGMA_FALSIFICATION}σ outside window or fully in gap\n"
        "\n"
        "  Experiments:\n"
        "    LiteBIRD (~2032)  σ_β ≈ 0.02° — PRIMARY TEST\n"
        "    CMB-S4 (~2030)    σ_β ≈ 0.01°\n"
        "    Simons Obs (~2028) σ_β ≈ 0.05°\n"
        "\n"
        "  Full prediction registry: 3-FALSIFICATION/OBSERVATION_TRACKER.md\n"
        "  Falsification protocol:   STEWARDSHIP.md §5\n"
    )


# ──────────────────────────────────────────────────────────────────────────────
# Command-line interface
# ──────────────────────────────────────────────────────────────────────────────

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="falsification_check.py",
        description=(
            "Self-executing Unitary Manifold birefringence falsification check. "
            "Provide a measured β value and its 1σ uncertainty to receive a verdict."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python src/core/falsification_check.py --beta 0.331 --sigma 0.02\n"
            "  python src/core/falsification_check.py --beta 0.28 --sigma 0.02\n"
            "  python src/core/falsification_check.py --beta 0.15 --sigma 0.01\n"
            "  python src/core/falsification_check.py --summary\n"
        ),
    )
    parser.add_argument(
        "--beta",
        type=float,
        default=None,
        metavar="DEGREES",
        help="Measured birefringence angle in degrees.",
    )
    parser.add_argument(
        "--sigma",
        type=float,
        default=None,
        metavar="DEGREES",
        help="1σ measurement uncertainty in degrees (must be positive).",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a summary of all falsification conditions and exit.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns 0 on success, 1 on FALSIFIED verdict."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.summary:
        print(summary())
        return 0

    if args.beta is None or args.sigma is None:
        parser.error("--beta and --sigma are both required unless --summary is used.")

    result = check_falsification(args.beta, args.sigma)
    print(result)
    print()
    print(summary())

    # Exit code 1 if falsified — useful for CI/automation
    return 1 if result.is_falsified() else 0


if __name__ == "__main__":
    sys.exit(main())
