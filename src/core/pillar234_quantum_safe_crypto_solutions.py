# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 234 — Quantum-Safe Cryptography Solutions Engine (2026).

Adjacent applied research track (non-hardgate): computes solution pathways for
the three strategic hurdles and eight technical/operational bottlenecks
identified in Pillar 233.  Provides intervention ROI ranking, readiness
trajectory projection using the PHI0 attractor, bandwidth overhead calculations,
IoT feasibility assessment, and enterprise CBOM planning.

Depends on Pillar 233 for bottleneck definitions and the baseline 2026 scenario.

🔵 ADJACENT TRACK — This module does NOT affect the Unitary Manifold ToE score.
"""
from __future__ import annotations

import math
from typing import Dict, List, Tuple

try:
    from src.core.pillar233_quantum_safe_crypto_bottleneck import (
        BOTTLENECK_ORDER,
        STRATEGIC_HURDLES,
        CryptoTransitionScenario,
        baseline_enterprise_scenario,
        bottleneck_scores,
        strategic_hurdle_scores,
        migration_readiness_report,
        migration_readiness_index,
        ML_KEM_512_PK,
        ML_KEM_768_PK,
        ML_KEM_1024_PK,
        ML_DSA_44_SIG,
        ML_DSA_65_SIG,
        ML_DSA_87_SIG,
        SLH_DSA_128S_SIG,
        SLH_DSA_128F_SIG,
        ECDH_X25519_PK,
        ECDSA_256_SIG,
        CURRENT_YEAR,
    )
except ImportError:
    from .pillar233_quantum_safe_crypto_bottleneck import (  # type: ignore[no-redef]
        BOTTLENECK_ORDER,
        STRATEGIC_HURDLES,
        CryptoTransitionScenario,
        baseline_enterprise_scenario,
        bottleneck_scores,
        strategic_hurdle_scores,
        migration_readiness_report,
        migration_readiness_index,
        ML_KEM_512_PK,
        ML_KEM_768_PK,
        ML_KEM_1024_PK,
        ML_DSA_44_SIG,
        ML_DSA_65_SIG,
        ML_DSA_87_SIG,
        SLH_DSA_128S_SIG,
        SLH_DSA_128F_SIG,
        ECDH_X25519_PK,
        ECDSA_256_SIG,
        CURRENT_YEAR,
    )

__provenance__ = {
    "pillar": 234,
    "title": "Quantum-Safe Cryptography Solutions Engine",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — solution pathway calculator; no claim that"
        " any bottleneck is solved"
    ),
}

# ---------------------------------------------------------------------------
# Framework constants (identical to Pillar 233 for cross-module consistency)
# ---------------------------------------------------------------------------
N_W: int = 5
K_CS: int = 74
C_S: float = 12.0 / 37.0
PHI0: float = 0.7390851332151607

# ---------------------------------------------------------------------------
# Intervention registry
# cost_denominator (USD): capital required to fully close a gap of 1.0.
# Formula: reduction_fraction = min(1, investment_usd / (gap * cost_denominator))
# ---------------------------------------------------------------------------

# USD to fully close a gap of 1.0 — realistic 2026 industry estimates.
_COST_DENOMINATORS: Dict[str, int] = {
    # --- 8 bottlenecks ---
    "cryptographic_blindspot": 2_500_000,
    "key_size_performance_bloat": 8_000_000,
    "supply_chain_dependency": 15_000_000,
    "hybrid_protocol_complexity": 5_000_000,
    "iot_embedded_constraints": 12_000_000,
    "migration_timeline_complacency": 500_000,
    "talent_expertise_shortage": 3_000_000,
    "crypto_agility_readiness": 20_000_000,
    # --- 3 hurdles ---
    "harvest_now_decrypt_later_exposure": 4_000_000,
    "governance_executive_blindspot": 750_000,
    "algorithm_permanence_myth": 1_000_000,
}

_INTERVENTION_DESCRIPTIONS: Dict[str, str] = {
    "cryptographic_blindspot": "CBOM scanning and cryptographic discovery platform",
    "key_size_performance_bloat": "Hardware upgrades and CDN offload for PQC overhead",
    "supply_chain_dependency": "Vendor orchestration and CBOM mandate programme",
    "hybrid_protocol_complexity": "Dual-stack hybrid TLS 1.3 infrastructure",
    "iot_embedded_constraints": "Firmware redesign and embedded hardware refresh",
    "migration_timeline_complacency": "Executive awareness and HNDL risk audit",
    "talent_expertise_shortage": "PQC training pipeline and specialist hiring",
    "crypto_agility_readiness": "Abstract Cryptographic Layer (ACL) architecture rebuild",
    "harvest_now_decrypt_later_exposure": "Immediate hybrid KEM deployment for long-lived secrets",
    "governance_executive_blindspot": "Board-level crypto risk framework and CCO appointment",
    "algorithm_permanence_myth": "Agility policy and 18-month algorithm review cadence",
}

_SOLUTION_APPROACHES: Dict[str, str] = {
    "cryptographic_blindspot": (
        "Deploy automated Cryptographic Bill of Materials (CBOM) scanning using tools "
        "like IBM Guardium, Keyfactor, or open-source Syft. Follow NIST NCCoE SP 1800-38 "
        "discovery playbook. Target: complete inventory within 90 days for Tier 1 systems."
    ),
    "key_size_performance_bloat": (
        "Upgrade network infrastructure for PQC overhead. ML-KEM-768 adds ~2.2 KB/handshake "
        "vs 64 B for ECDH — measurable but manageable with TLS 1.3 session resumption. "
        "Deploy hardware crypto accelerators (e.g., Intel QAT). Use ML-KEM-512 for "
        "bandwidth-constrained paths (800 B pk vs 1184 B). Implement TLS certificate "
        "compression (RFC 8879) to offset bloat."
    ),
    "supply_chain_dependency": (
        "Mandate CBOM submission from all Tier 1 vendors. Require quantum-readiness "
        "attestation in procurement contracts (NSA CISA Quantum Readiness roadmap). "
        "Implement automated vendor CBOM ingestion and compliance scoring dashboard. "
        "Create contractual SLAs with migration deadlines."
    ),
    "hybrid_protocol_complexity": (
        "Adopt X25519MLKEM768 hybrid KEM (IETF draft-connolly-tls-mlkem-key-agreement). "
        "Run hybrid TLS 1.3 as default NOW: both ECDH and ML-KEM in combined key exchange. "
        "Use OpenSSL 3.4+ or BoringSSL's PQC branch. Hybrid approach: if CRQC breaks PQC "
        "math, classical portion is still safe; if classical is broken by quantum, PQC "
        "portion is still safe. Win-win bridge strategy."
    ),
    "iot_embedded_constraints": (
        "Use ML-KEM-512 (pk=800 B, ct=768 B, ~5.5 KB RAM peak) for key exchange on "
        "constrained devices. Use SLH-DSA-128s (pk=32 B, sig=7856 B) for firmware signing "
        "— small keys, stateless, good for verification. Partition crypto operations to "
        "TEE/secure enclave when available. Hardware refresh cycle: ML-KEM-512 runs on "
        "Cortex-M4 @ 3 MHz in ~500 ms — feasible for many IoT update scenarios."
    ),
    "migration_timeline_complacency": (
        "Conduct HNDL Risk Assessment: classify all data by required confidentiality "
        "lifetime. Any data needing >4 years of secrecy is ALREADY at risk. Deploy hybrid "
        "KEM for all Tier 1 data immediately. Educate board: the quantum threat is "
        "retrospective, not future. Reference: NSA CNSA 2.0 requires ML-KEM and ML-DSA "
        "by 2030 for national security systems."
    ),
    "talent_expertise_shortage": (
        "Fund NIST-aligned PQC training through SANS, Coursera PQ Crypto specialization, "
        "and university partnerships. Create internal PQC Center of Excellence. "
        "Hire cryptographers with lattice/hash-based background. Aim for 1 PQC specialist "
        "per 50 developers in migration teams."
    ),
    "crypto_agility_readiness": (
        "Implement Abstract Cryptographic Layer (ACL) pattern: all crypto operations go "
        "through a unified interface where the algorithm is a runtime configuration, not "
        "hardcoded. Follow NIST NCCoE Crypto-Agility SP 1800-38 series. This means: "
        "algorithm negotiation via config file, automated certificate lifecycle management, "
        "A/B testing of new algorithms without code deployment. Target: <1 day to swap "
        "any algorithm enterprise-wide."
    ),
    "harvest_now_decrypt_later_exposure": (
        "Immediately encrypt all Tier 1 long-lived secrets with hybrid KEM (X25519+ML-KEM-768). "
        "Re-encrypt at-rest data stores. Rotate TLS certificates to hybrid. "
        "This provides 'store now, can't decrypt later' protection: even if a CRQC arrives "
        "tomorrow, the hybrid-encrypted data is safe because the ML-KEM component requires "
        "a quantum computer AND breaking the NIST lattice problem."
    ),
    "governance_executive_blindspot": (
        "Elevate cryptography to board-level risk register. Mandate quarterly Crypto Risk "
        "Report (CRR) alongside cyber risk report. Appoint a Chief Cryptography Officer "
        "(CCO) or assign to CISO directly. Include PQC migration status in 10-K/annual "
        "report risk factors. Reference: SEC cybersecurity disclosure rules require material "
        "risk disclosure."
    ),
    "algorithm_permanence_myth": (
        "Implement mandatory Algorithm Review Cadence: every 18 months, cryptographic "
        "committee reviews NIST/IETF updates and assesses whether deployed algorithms "
        "remain secure. Crypto-agility architecture (see above) makes this review "
        "actionable. Budget for 'algorithm obsolescence' as a standard IT lifecycle cost. "
        "Maintain candidate replacement algorithms on standby in the ACL library."
    ),
}

_TIMELINES_MONTHS: Dict[str, int] = {
    "cryptographic_blindspot": 3,
    "key_size_performance_bloat": 12,
    "supply_chain_dependency": 24,
    "hybrid_protocol_complexity": 6,
    "iot_embedded_constraints": 36,
    "migration_timeline_complacency": 1,
    "talent_expertise_shortage": 18,
    "crypto_agility_readiness": 30,
    "harvest_now_decrypt_later_exposure": 6,
    "governance_executive_blindspot": 2,
    "algorithm_permanence_myth": 3,
}

# Canonical ordering: bottlenecks first (matching BOTTLENECK_ORDER), then hurdles.
ALL_INTERVENTIONS: Tuple[str, ...] = tuple(BOTTLENECK_ORDER) + tuple(STRATEGIC_HURDLES)

# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _compute_all_gaps(scenario: CryptoTransitionScenario) -> Dict[str, float]:
    """Return combined dict of all 11 gap scores (bottlenecks + hurdles)."""
    gaps: Dict[str, float] = {}
    gaps.update(bottleneck_scores(scenario))
    gaps.update(strategic_hurdle_scores(scenario))
    return gaps


def _readiness_from_gaps(
    gaps: Dict[str, float],
    strategic_weight: float = 0.50,
) -> float:
    """Recompute migration readiness index from a mutable gap dict.

    [CALCULATED] Reproduces Pillar 233 formula:
        total_gap = w * mean(hurdle_gaps) + (1-w) * mean(bottleneck_gaps)
        readiness  = 1 - total_gap
    """
    hurdle_gaps = [gaps[h] for h in STRATEGIC_HURDLES]
    bottleneck_gaps = [gaps[b] for b in BOTTLENECK_ORDER]
    hurdle_mean = sum(hurdle_gaps) / len(hurdle_gaps)
    bottleneck_mean = sum(bottleneck_gaps) / len(bottleneck_gaps)
    total_gap = strategic_weight * hurdle_mean + (1.0 - strategic_weight) * bottleneck_mean
    return _clamp01(1.0 - total_gap)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def intervention_roi(
    gap_name: str,
    investment_usd: float,
    gap_score: float,
) -> Dict:
    """Return the return-on-investment breakdown for a single intervention.

    [CALCULATED] reduction_fraction = min(1, investment_usd / (gap_score * cost_denominator)).
    cost_per_gap_point = investment_usd / actual_gap_closed (inf when gap_closed == 0).

    Parameters
    ----------
    gap_name : str
        One of the 11 bottleneck/hurdle keys in ALL_INTERVENTIONS.
    investment_usd : float
        Capital committed to this intervention (USD, non-negative).
    gap_score : float
        Current gap in [0, 1] from Pillar 233.

    Returns
    -------
    dict
        Keys: gap_name, investment_usd, initial_gap, reduction_fraction,
        residual_gap, solution_approach, timeline_months, cost_per_gap_point.
    """
    if gap_name not in _COST_DENOMINATORS:
        raise ValueError(
            f"Unknown intervention: {gap_name!r}. "
            f"Valid names: {sorted(_COST_DENOMINATORS)}"
        )
    if not (0.0 <= gap_score <= 1.0):
        raise ValueError(f"gap_score must be in [0, 1], got {gap_score}")
    if investment_usd < 0:
        raise ValueError(f"investment_usd must be non-negative, got {investment_usd}")

    if gap_score <= 0.0 or investment_usd <= 0.0:
        reduction_fraction = 0.0
    else:
        cost_denom = _COST_DENOMINATORS[gap_name]
        reduction_fraction = _clamp01(investment_usd / (gap_score * cost_denom))

    actual_gap_closed = gap_score * reduction_fraction
    residual_gap = _clamp01(gap_score - actual_gap_closed)
    cost_per_gap_point = (
        investment_usd / actual_gap_closed if actual_gap_closed > 0.0 else float("inf")
    )

    return {
        "gap_name": gap_name,
        "investment_usd": investment_usd,
        "initial_gap": gap_score,
        "reduction_fraction": reduction_fraction,
        "residual_gap": residual_gap,
        "solution_approach": _SOLUTION_APPROACHES[gap_name],
        "timeline_months": _TIMELINES_MONTHS[gap_name],
        "cost_per_gap_point": cost_per_gap_point,
    }


def prioritized_interventions(
    scenario: CryptoTransitionScenario,
    total_budget_usd: float,
) -> List[Dict]:
    """Rank all 11 interventions by ROI and allocate budget in priority order.

    [CALCULATED] Each intervention is scored on (gap_closed / dollar) using
    an equal per-intervention budget slice for the ranking comparison.
    Budget is then allocated greedily in descending ROI order; a partially-
    funded intervention receives whatever remains of the budget.

    Parameters
    ----------
    scenario : CryptoTransitionScenario
        Pillar 233 baseline scenario.
    total_budget_usd : float
        Total available investment (USD, non-negative).

    Returns
    -------
    list of dict
        Sorted descending by roi_per_dollar.  Each entry includes:
        gap_name, description, current_gap, reduction_fraction, gap_closed,
        investment_usd, roi_per_dollar, cost_to_fully_close_usd,
        timeline_months, cumulative_budget_usd.
    """
    if total_budget_usd < 0:
        raise ValueError(f"total_budget_usd must be non-negative, got {total_budget_usd}")

    gaps = _compute_all_gaps(scenario)
    n = len(ALL_INTERVENTIONS)
    slice_usd = total_budget_usd / n if (total_budget_usd > 0 and n > 0) else 0.0

    ranked: List[Dict] = []
    for name in ALL_INTERVENTIONS:
        gap = gaps[name]
        cost_denom = _COST_DENOMINATORS[name]
        if gap > 0.0 and slice_usd > 0.0:
            reduction_fraction = _clamp01(slice_usd / (gap * cost_denom))
        else:
            reduction_fraction = 0.0
        gap_closed = gap * reduction_fraction
        roi = gap_closed / slice_usd if slice_usd > 0 else 0.0
        cost_to_close = gap * cost_denom if gap > 0 else 0.0
        ranked.append(
            {
                "gap_name": name,
                "description": _INTERVENTION_DESCRIPTIONS[name],
                "current_gap": gap,
                "reduction_fraction": reduction_fraction,
                "gap_closed": gap_closed,
                "investment_usd": 0.0,   # filled in allocation pass below
                "roi_per_dollar": roi,
                "cost_to_fully_close_usd": cost_to_close,
                "timeline_months": _TIMELINES_MONTHS[name],
                "cumulative_budget_usd": 0.0,
            }
        )

    ranked.sort(key=lambda d: d["roi_per_dollar"], reverse=True)

    # Greedy budget allocation in priority order.
    remaining = total_budget_usd
    cumulative = 0.0
    for entry in ranked:
        name = entry["gap_name"]
        gap = entry["current_gap"]
        cost_denom = _COST_DENOMINATORS[name]
        needed = gap * cost_denom if gap > 0 else 0.0
        alloc = min(remaining, needed) if needed > 0 else 0.0
        entry["investment_usd"] = alloc
        remaining -= alloc
        cumulative += alloc
        entry["cumulative_budget_usd"] = cumulative
        # Recompute reduction_fraction with actual allocation.
        if gap > 0.0 and alloc > 0.0:
            entry["reduction_fraction"] = _clamp01(alloc / (gap * cost_denom))
            entry["gap_closed"] = gap * entry["reduction_fraction"]
        else:
            entry["reduction_fraction"] = 0.0
            entry["gap_closed"] = 0.0

    return ranked


def hndl_immediate_risk_band(scenario: CryptoTransitionScenario) -> str:
    """Classify Harvest-Now-Decrypt-Later exposure into a risk band.

    [CALCULATED] Uses the HNDL hurdle gap score from Pillar 233.
    Score >= 0.75 → CRITICAL, >= 0.50 → HIGH, >= 0.25 → MEDIUM, else LOW.

    Returns
    -------
    str
        One of "CRITICAL", "HIGH", "MEDIUM", "LOW".
    """
    hurdles = strategic_hurdle_scores(scenario)
    hndl_score = hurdles.get("harvest_now_decrypt_later_exposure", 0.0)
    if hndl_score >= 0.75:
        return "CRITICAL"
    if hndl_score >= 0.50:
        return "HIGH"
    if hndl_score >= 0.25:
        return "MEDIUM"
    return "LOW"


def crypto_agility_score_from_scenario(scenario: CryptoTransitionScenario) -> float:
    """Return a 0–1 score of how crypto-agile the organisation currently is.

    [CALCULATED] Derived as 1 minus the crypto_agility_readiness bottleneck gap.
    A score of 1.0 means full ACL-based agility; 0.0 means fully hardcoded
    algorithms with no swap capability.

    Returns
    -------
    float
        Crypto-agility score in [0, 1].
    """
    b_scores = bottleneck_scores(scenario)
    agility_gap = b_scores.get("crypto_agility_readiness", 1.0)
    return _clamp01(1.0 - agility_gap)


def migration_trajectory(
    scenario: CryptoTransitionScenario,
    annual_budget_usd: float,
    years: int = 10,
) -> List[Dict]:
    """Project year-by-year migration readiness under a fixed annual budget.

    [CALCULATED] Uses a PHI0-bounded exponential convergence model:
        readiness(t) = PHI0 * (1 − exp(−k * t))
    where k is calibrated from the budget relative to the total gap-closing
    cost across all 11 interventions.  PHI0 (≈ 0.739) is treated as the
    asymptotic attractor of achievable readiness given real-world friction.

    The baseline readiness from Pillar 233 is used as the starting point,
    and the trajectory is scaled so that t=0 yields the baseline exactly.

    Parameters
    ----------
    scenario : CryptoTransitionScenario
        Pillar 233 baseline.
    annual_budget_usd : float
        Budget invested each year (USD, non-negative).
    years : int
        Projection horizon in years (default 10, must be > 0).

    Returns
    -------
    list of dict
        {year, readiness_index, budget_spent} for year 0 through ``years``.
    """
    if annual_budget_usd < 0:
        raise ValueError(f"annual_budget_usd must be non-negative, got {annual_budget_usd}")
    if years <= 0:
        raise ValueError(f"years must be > 0, got {years}")

    gaps = _compute_all_gaps(scenario)
    baseline_readiness = _readiness_from_gaps(gaps)

    # Total cost to close all gaps fully.
    total_gap_cost = sum(
        gaps[name] * _COST_DENOMINATORS[name]
        for name in ALL_INTERVENTIONS
        if gaps[name] > 0.0
    )

    # k calibrated so that spending total_gap_cost in one year achieves PHI0.
    # k = -ln(1 - baseline/PHI0) / 0  is degenerate, so we anchor to budget ratio.
    if total_gap_cost > 0 and annual_budget_usd > 0:
        budget_ratio = annual_budget_usd / total_gap_cost
        k = budget_ratio * 2.0   # scaling factor: 50 % annual funding → ~50 % speed
    else:
        k = 0.0

    # Compute t_offset so trajectory starts exactly at baseline_readiness.
    # PHI0 * (1 - exp(-k * t_offset)) = baseline_readiness
    # → t_offset = -ln(1 - baseline_readiness / PHI0) / k  (when PHI0 > baseline and k>0)
    if k > 0 and PHI0 > baseline_readiness:
        try:
            t_offset = -math.log(1.0 - baseline_readiness / PHI0) / k
        except (ValueError, ZeroDivisionError):
            t_offset = 0.0
    else:
        t_offset = 0.0

    trajectory: List[Dict] = []
    for yr in range(years + 1):
        t = t_offset + yr
        if k > 0:
            r = PHI0 * (1.0 - math.exp(-k * t))
        else:
            r = baseline_readiness
        trajectory.append(
            {
                "year": CURRENT_YEAR + yr,
                "readiness_index": round(_clamp01(r), 6),
                "budget_spent": round(annual_budget_usd * yr, 2),
            }
        )

    return trajectory


def hybrid_kem_bandwidth_overhead(
    bandwidth_gbps: float,
    connections_per_second: float,
) -> Dict:
    """Compute TLS bandwidth overhead of migrating to hybrid X25519+ML-KEM-768.

    [CALCULATED] Classical TLS 1.3 key share: X25519 = 32 bytes.
    Hybrid addition: ML-KEM-768 public key = 1184 bytes.
    Net additional bytes per TLS ClientHello key_share extension: 1152 bytes.
    Total overhead gbps = connections_per_second × 1152 × 8 / 1e9.

    Parameters
    ----------
    bandwidth_gbps : float
        Total available network bandwidth in Gbps (positive).
    connections_per_second : float
        TLS handshakes per second (non-negative).

    Returns
    -------
    dict
        Keys: classical_key_share_bytes, hybrid_key_share_bytes,
        overhead_bytes_per_connection, overhead_gbps, overhead_percent,
        recommendation.
    """
    if bandwidth_gbps <= 0:
        raise ValueError(f"bandwidth_gbps must be positive, got {bandwidth_gbps}")
    if connections_per_second < 0:
        raise ValueError(f"connections_per_second must be non-negative, got {connections_per_second}")

    classical_bytes = ECDH_X25519_PK           # 32 bytes
    hybrid_bytes = ECDH_X25519_PK + ML_KEM_768_PK   # 32 + 1184 = 1216 bytes
    overhead_per_conn = hybrid_bytes - classical_bytes   # 1184 bytes

    overhead_gbps = connections_per_second * overhead_per_conn * 8 / 1e9
    overhead_percent = (overhead_gbps / bandwidth_gbps) * 100.0

    if overhead_percent < 1.0:
        recommendation = (
            "Overhead is negligible (<1 %). Proceed with hybrid KEM migration immediately."
        )
    elif overhead_percent < 5.0:
        recommendation = (
            f"Overhead is {overhead_percent:.1f} % — acceptable. Enable TLS session "
            "resumption and certificate compression (RFC 8879) to partially offset."
        )
    elif overhead_percent < 15.0:
        recommendation = (
            f"Overhead is {overhead_percent:.1f} % — moderate. Deploy hardware crypto "
            "accelerators and TLS offload before migrating high-volume endpoints. "
            "Consider ML-KEM-512 for most bandwidth-constrained paths."
        )
    else:
        recommendation = (
            f"Overhead is {overhead_percent:.1f} % — significant. Conduct traffic "
            "analysis to identify top-10 bandwidth consumers; prioritise hardware "
            "offload there. Use ML-KEM-512 (pk=800 B) as interim KEM to halve overhead."
        )

    return {
        "classical_key_share_bytes": classical_bytes,
        "hybrid_key_share_bytes": hybrid_bytes,
        "overhead_bytes_per_connection": overhead_per_conn,
        "overhead_gbps": round(overhead_gbps, 6),
        "overhead_percent": round(overhead_percent, 4),
        "recommendation": recommendation,
    }


def iot_pqc_feasibility(
    memory_kb: float,
    power_mw: float,
    mcu_freq_mhz: float,
) -> Dict:
    """Assess PQC algorithm feasibility on a constrained IoT device.

    [CALCULATED] Reference cycle counts from open-source PQC benchmarks
    (pqm4 / NIST PQC benchmarking 2024):
        ML-KEM-512 KeyGen+Encap: ~300 k cycles peak RAM ~5.5 KB
        SLH-DSA-128s Verify:     ~1 M cycles, peak RAM ~2 KB
    time_ms = cycles / (freq_mhz × 1000)

    Parameters
    ----------
    memory_kb : float
        Available SRAM in kilobytes.
    power_mw : float
        Active power budget in milliwatts (informational; not used in feasibility gate).
    mcu_freq_mhz : float
        MCU clock frequency in MHz (must be > 0).

    Returns
    -------
    dict
        Keys: ml_kem_512_feasible, slh_dsa_verify_feasible,
        recommended_algo, time_ms, notes.
    """
    if mcu_freq_mhz <= 0:
        raise ValueError(f"mcu_freq_mhz must be positive, got {mcu_freq_mhz}")
    if memory_kb < 0:
        raise ValueError(f"memory_kb must be non-negative, got {memory_kb}")
    if power_mw < 0:
        raise ValueError(f"power_mw must be non-negative, got {power_mw}")

    ML_KEM_512_RAM_KB = 5.5
    SLH_DSA_VERIFY_RAM_KB = 2.0
    ML_KEM_512_CYCLES = 300_000
    SLH_DSA_VERIFY_CYCLES = 1_000_000

    ml_kem_feasible = memory_kb >= ML_KEM_512_RAM_KB
    slh_dsa_feasible = memory_kb >= SLH_DSA_VERIFY_RAM_KB

    # Time for the primary operation if feasible.
    if ml_kem_feasible:
        time_ms = ML_KEM_512_CYCLES / (mcu_freq_mhz * 1_000)
    elif slh_dsa_feasible:
        time_ms = SLH_DSA_VERIFY_CYCLES / (mcu_freq_mhz * 1_000)
    else:
        time_ms = float("inf")

    if ml_kem_feasible:
        recommended = "ML-KEM-512 (key exchange) + SLH-DSA-128s (firmware verification)"
    elif slh_dsa_feasible:
        recommended = (
            "SLH-DSA-128s signature verification only — insufficient RAM for ML-KEM-512 "
            "key exchange. Consider hardware-assisted KEM or external secure element."
        )
    else:
        recommended = (
            "Insufficient RAM for standalone PQC. Use a dedicated secure element "
            "(e.g., ATECC608B or similar) to offload crypto operations."
        )

    notes = (
        f"Memory: {memory_kb} KB available; ML-KEM-512 needs {ML_KEM_512_RAM_KB} KB, "
        f"SLH-DSA verify needs {SLH_DSA_VERIFY_RAM_KB} KB. "
        f"At {mcu_freq_mhz} MHz, ML-KEM-512 completes in "
        f"~{ML_KEM_512_CYCLES / (mcu_freq_mhz * 1_000):.0f} ms. "
        f"Power draw ({power_mw} mW) is informational — PQC typically adds "
        "<10 % active-mode power over classical ECC on equivalent hardware."
    )

    return {
        "ml_kem_512_feasible": ml_kem_feasible,
        "slh_dsa_verify_feasible": slh_dsa_feasible,
        "recommended_algo": recommended,
        "time_ms": round(time_ms, 2) if math.isfinite(time_ms) else time_ms,
        "notes": notes,
    }


def enterprise_cbom_plan(
    total_systems: int,
    tier1_systems: int,
    tier2_systems: int,
) -> Dict:
    """Return a phased Cryptographic Bill of Materials discovery plan.

    [CALCULATED] Three phases based on NIST NCCoE SP 1800-38 discovery playbook.
    Cost estimate: $50 per system for automated scanning tooling and labour.

    Parameters
    ----------
    total_systems : int
        Total number of IT systems in scope.
    tier1_systems : int
        Critical / production systems (highest priority).
    tier2_systems : int
        Secondary systems.

    Returns
    -------
    dict
        Keys: phases (list of phase dicts), total_estimated_cost_usd,
        total_systems, tier1_systems, tier2_systems, tier3_systems,
        cost_per_system_usd.
    """
    if total_systems < 0:
        raise ValueError(f"total_systems must be non-negative, got {total_systems}")
    if tier1_systems < 0 or tier2_systems < 0:
        raise ValueError("tier1_systems and tier2_systems must be non-negative")
    if tier1_systems + tier2_systems > total_systems:
        raise ValueError(
            "tier1_systems + tier2_systems cannot exceed total_systems"
        )

    tier3_systems = total_systems - tier1_systems - tier2_systems
    cost_per_system = 50  # USD

    phases = [
        {
            "phase": 1,
            "name": "Tier 1 Critical Systems Inventory",
            "duration_days": 30,
            "systems_in_scope": tier1_systems,
            "activities": [
                "Deploy CBOM scanning agent on all Tier 1 systems",
                "Identify all cryptographic libraries and certificates",
                "Classify algorithms: vulnerable (RSA/ECC) vs quantum-safe",
                "Produce Tier 1 CBOM report with gap heat-map",
            ],
            "estimated_cost_usd": tier1_systems * cost_per_system,
            "milestone": "Complete Tier 1 CBOM; know your highest-risk exposure",
        },
        {
            "phase": 2,
            "name": "Tier 2 Systems + Vendor CBOM Collection",
            "duration_days": 60,
            "systems_in_scope": tier2_systems,
            "activities": [
                "Extend scanning to all Tier 2 systems",
                "Issue CBOM attestation requests to all Tier 1 vendors",
                "Ingest and normalise vendor CBOMs into central dashboard",
                "Identify supply-chain cryptographic dependencies",
            ],
            "estimated_cost_usd": tier2_systems * cost_per_system,
            "milestone": "Complete Tier 2 CBOM; vendor dependency map produced",
        },
        {
            "phase": 3,
            "name": "Full Enterprise Inventory + Gap Report",
            "duration_days": 90,
            "systems_in_scope": tier3_systems,
            "activities": [
                "Complete scanning of remaining Tier 3 / legacy systems",
                "Merge all CBOMs into unified enterprise cryptographic inventory",
                "Generate prioritised migration roadmap with cost estimates",
                "Present executive summary and board-level risk disclosure",
            ],
            "estimated_cost_usd": tier3_systems * cost_per_system,
            "milestone": "Full enterprise CBOM; migration roadmap approved by CISO",
        },
    ]

    total_cost = total_systems * cost_per_system

    return {
        "phases": phases,
        "total_estimated_cost_usd": total_cost,
        "total_systems": total_systems,
        "tier1_systems": tier1_systems,
        "tier2_systems": tier2_systems,
        "tier3_systems": tier3_systems,
        "cost_per_system_usd": cost_per_system,
    }


def full_solution_plan(
    scenario: CryptoTransitionScenario,
    total_budget_usd: float,
) -> Dict:
    """Comprehensive quantum-safe migration solution plan.

    [CALCULATED] Combines all Pillar 234 analysis functions into a single
    actionable plan.  All sub-computations are deterministic.

    Parameters
    ----------
    scenario : CryptoTransitionScenario
        Pillar 233 baseline scenario.
    total_budget_usd : float
        Total available investment (USD).

    Returns
    -------
    dict
        Keys: hndl_risk_band, crypto_agility_score, prioritized_interventions,
        trajectory (5-year), cbom_plan, bandwidth_overhead, iot_feasibility,
        migration_readiness_baseline.
    """
    if total_budget_usd < 0:
        raise ValueError(f"total_budget_usd must be non-negative, got {total_budget_usd}")

    # Baseline readiness from Pillar 233.
    report = migration_readiness_report(scenario)
    baseline_readiness = report["readiness_index"]

    hndl_band = hndl_immediate_risk_band(scenario)
    agility_score = crypto_agility_score_from_scenario(scenario)
    interventions = prioritized_interventions(scenario, total_budget_usd)
    trajectory = migration_trajectory(scenario, annual_budget_usd=total_budget_usd / 5.0, years=5)

    # CBOM plan: derive system counts from scenario where available.
    total_sys = getattr(scenario, "total_it_systems", 500)
    tier1 = max(1, int(total_sys * 0.10))
    tier2 = max(1, int(total_sys * 0.30))
    cbom = enterprise_cbom_plan(total_sys, tier1, tier2)

    # Bandwidth overhead: assume 10 Gbps and 5 000 TLS conn/s as defaults.
    bw_gbps = getattr(scenario, "network_bandwidth_gbps", 10.0)
    conns = getattr(scenario, "tls_connections_per_second", 5_000.0)
    bw_overhead = hybrid_kem_bandwidth_overhead(
        bandwidth_gbps=max(0.001, bw_gbps),
        connections_per_second=max(0.0, conns),
    )

    # IoT feasibility: representative constrained device (Cortex-M4 class).
    iot = iot_pqc_feasibility(memory_kb=8.0, power_mw=15.0, mcu_freq_mhz=64.0)

    return {
        "hndl_risk_band": hndl_band,
        "crypto_agility_score": round(agility_score, 4),
        "migration_readiness_baseline": round(baseline_readiness, 4),
        "prioritized_interventions": interventions,
        "trajectory": trajectory,
        "cbom_plan": cbom,
        "bandwidth_overhead": bw_overhead,
        "iot_feasibility": iot,
    }


def baseline_solution_plan() -> Dict:
    """Apply full_solution_plan to baseline_enterprise_scenario() with $5 M budget.

    [CALCULATED] Convenience entry-point for the canonical 2026 enterprise
    baseline defined in Pillar 233.

    Returns
    -------
    dict
        Full solution plan keys; see full_solution_plan() for details.
    """
    return full_solution_plan(
        scenario=baseline_enterprise_scenario(),
        total_budget_usd=5_000_000,
    )


# ---------------------------------------------------------------------------
# __all__
# ---------------------------------------------------------------------------

__all__ = [
    # Constants
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "ALL_INTERVENTIONS",
    # Registries (read-only)
    "_COST_DENOMINATORS",
    "_SOLUTION_APPROACHES",
    "_TIMELINES_MONTHS",
    # Core functions
    "intervention_roi",
    "prioritized_interventions",
    "hndl_immediate_risk_band",
    "crypto_agility_score_from_scenario",
    "migration_trajectory",
    "hybrid_kem_bandwidth_overhead",
    "iot_pqc_feasibility",
    "enterprise_cbom_plan",
    "full_solution_plan",
    "baseline_solution_plan",
    # Provenance
    "__provenance__",
]


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def main() -> None:
    """Print the baseline solution plan to stdout."""
    import json

    plan = baseline_solution_plan()

    print("=" * 72)
    print("Pillar 234 — Quantum-Safe Cryptography Solutions Engine")
    print("=" * 72)
    print(f"HNDL Risk Band          : {plan['hndl_risk_band']}")
    print(f"Crypto Agility Score    : {plan['crypto_agility_score']:.4f}")
    print(f"Migration Readiness (0) : {plan['migration_readiness_baseline']:.4f}")
    print()

    print("── Top-5 Prioritised Interventions (by ROI) ──")
    for entry in plan["prioritized_interventions"][:5]:
        print(
            f"  {entry['gap_name']:<38}  gap={entry['current_gap']:.3f}"
            f"  alloc=${entry['investment_usd']:>10,.0f}"
            f"  months={entry['timeline_months']}"
        )
    print()

    print("── 5-Year Readiness Trajectory ──")
    for row in plan["trajectory"]:
        bar_len = int(row["readiness_index"] * 40)
        bar = "█" * bar_len + "░" * (40 - bar_len)
        print(
            f"  {row['year']}  [{bar}]  {row['readiness_index']:.4f}"
            f"  (${row['budget_spent']:>12,.0f} spent)"
        )
    print()

    print("── Bandwidth Overhead (hybrid TLS) ──")
    bw = plan["bandwidth_overhead"]
    print(f"  Overhead per connection : {bw['overhead_bytes_per_connection']} bytes")
    print(f"  Overhead                : {bw['overhead_gbps']:.4f} Gbps  ({bw['overhead_percent']:.2f} %)")
    print(f"  Recommendation          : {bw['recommendation']}")
    print()

    print("── IoT PQC Feasibility (8 KB RAM, 64 MHz) ──")
    iot = plan["iot_feasibility"]
    print(f"  ML-KEM-512 feasible     : {iot['ml_kem_512_feasible']}")
    print(f"  SLH-DSA verify feasible : {iot['slh_dsa_verify_feasible']}")
    print(f"  Recommended algo        : {iot['recommended_algo']}")
    print(f"  Time estimate           : {iot['time_ms']} ms")
    print()

    print("── CBOM Discovery Plan ──")
    cbom = plan["cbom_plan"]
    print(f"  Total systems           : {cbom['total_systems']}")
    print(f"  Total estimated cost    : ${cbom['total_estimated_cost_usd']:,}")
    for phase in cbom["phases"]:
        print(
            f"  Phase {phase['phase']} ({phase['duration_days']} days)"
            f" — {phase['name']}"
            f" — ${phase['estimated_cost_usd']:,}"
        )
    print()
    print("Plan keys:", list(plan.keys()))


if __name__ == "__main__":
    main()
