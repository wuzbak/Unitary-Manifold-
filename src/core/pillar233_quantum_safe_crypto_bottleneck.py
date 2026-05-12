# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026  ThomasCory Walker-Pearson
"""
Pillar 233 — Quantum-Safe Cryptography Transition Bottleneck Calculator.

ADJACENT RESEARCH TRACK (non-hardgate): a deterministic calculator for three
strategic hurdles and eight technical/operational bottlenecks that impede
enterprise migration from classical (RSA/ECC) cryptography to post-quantum
cryptography (PQC) as standardised by NIST FIPS 203, 204, and 205.

Unlike narrative assessments, every score is computed from explicit, measurable
inputs so that readiness gaps are reproducible and auditable.  All cryptographic
size constants are drawn directly from the published NIST FIPS standards:

    FIPS 203 (2024) — ML-KEM (Module-Lattice Key-Encapsulation Mechanism)
    FIPS 204 (2024) — ML-DSA (Module-Lattice Digital Signature Algorithm)
    FIPS 205 (2024) — SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)

Gap scores are in [0.0, 1.0] where 0.0 = bottleneck fully resolved and
1.0 = bottleneck is completely blocking migration.

🔵 ADJACENT TRACK — This module does NOT affect the Unitary Manifold ToE score.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

__provenance__ = {
    "pillar": 233,
    "title": "Quantum-Safe Cryptography Transition Bottleneck Calculator",
    "author": "ThomasCory Walker-Pearson",
    "dba": "AxiomZero Technologies",
    "github": "@wuzbak",
    "zenodo_doi": "https://doi.org/10.5281/zenodo.19584531",
    "license_software": "AGPL-3.0-or-later",
    "license_theory": "Defensive Public Commons v1.0",
    "fingerprint": "(5, 7, 74)",
    "status": (
        "ADJACENT RESEARCH TRACK — quantum-safe migration bottleneck calculator, "
        "not a claim that PQC transition barriers are solved"
    ),
}

# ---------------------------------------------------------------------------
# Unitary Manifold framework constants
# ---------------------------------------------------------------------------

N_W: int = 5                            # braided winding number
K_CS: int = 74                          # 5² + 7² = k_cs (birefringence resonance)
C_S: float = 12.0 / 37.0               # braided sound speed
PHI0: float = 0.7390851332151607        # Banach fixed-point of cos(x)

CURRENT_YEAR: int = 2026

# ---------------------------------------------------------------------------
# NIST FIPS 203 — ML-KEM (Module-Lattice Key-Encapsulation Mechanism)
# All values in bytes, exact per FIPS 203 Table 2.
# ---------------------------------------------------------------------------

ML_KEM_512_PK: int = 800        # ML-KEM-512  encapsulation key
ML_KEM_512_CT: int = 768        # ML-KEM-512  ciphertext
ML_KEM_512_SK: int = 1632       # ML-KEM-512  decapsulation key

ML_KEM_768_PK: int = 1184       # ML-KEM-768  encapsulation key
ML_KEM_768_CT: int = 1088       # ML-KEM-768  ciphertext
ML_KEM_768_SK: int = 2400       # ML-KEM-768  decapsulation key

ML_KEM_1024_PK: int = 1568      # ML-KEM-1024 encapsulation key
ML_KEM_1024_CT: int = 1568      # ML-KEM-1024 ciphertext
ML_KEM_1024_SK: int = 3168      # ML-KEM-1024 decapsulation key

# ---------------------------------------------------------------------------
# NIST FIPS 204 — ML-DSA (Module-Lattice Digital Signature Algorithm)
# All values in bytes, exact per FIPS 204 Table 2.
# ---------------------------------------------------------------------------

ML_DSA_44_PK: int = 1312        # ML-DSA-44  public key
ML_DSA_44_SIG: int = 2420       # ML-DSA-44  signature
ML_DSA_44_SK: int = 2528        # ML-DSA-44  private key

ML_DSA_65_PK: int = 1952        # ML-DSA-65  public key
ML_DSA_65_SIG: int = 3293       # ML-DSA-65  signature
ML_DSA_65_SK: int = 4000        # ML-DSA-65  private key

ML_DSA_87_PK: int = 2592        # ML-DSA-87  public key
ML_DSA_87_SIG: int = 4595       # ML-DSA-87  signature
ML_DSA_87_SK: int = 4864        # ML-DSA-87  private key

# ---------------------------------------------------------------------------
# NIST FIPS 205 — SLH-DSA (Stateless Hash-Based Digital Signature Algorithm)
# All values in bytes, exact per FIPS 205 Table 2.
# ---------------------------------------------------------------------------

SLH_DSA_128S_PK: int = 32       # SHA2-128s  public key
SLH_DSA_128S_SIG: int = 7856    # SHA2-128s  signature  (small/slow variant)

SLH_DSA_128F_PK: int = 32       # SHA2-128f  public key
SLH_DSA_128F_SIG: int = 17088   # SHA2-128f  signature  (fast/large variant)

SLH_DSA_256S_PK: int = 64       # SHA2-256s  public key
SLH_DSA_256S_SIG: int = 29792   # SHA2-256s  signature

# ---------------------------------------------------------------------------
# Classical cryptography baseline sizes (bytes)
# ---------------------------------------------------------------------------

RSA_2048_PK: int = 256          # RSA-2048 public key  (PKCS#1 DER, modulus only)
RSA_2048_SIG: int = 256         # RSA-2048 signature

ECDSA_256_PK: int = 64          # ECDSA P-256 public key  (uncompressed, minus prefix)
ECDSA_256_SIG: int = 64         # ECDSA P-256 signature   (DER, typical)

ECDH_X25519_PK: int = 32        # X25519 public key

# ---------------------------------------------------------------------------
# IoT / embedded resource constants (derived from NIST specs + MCU benchmarks)
# ---------------------------------------------------------------------------

# Working stack + key-material storage for ML-KEM-512 during keygen/encap.
_PQC_KEM_STACK_KB: float = 5.5
_PQC_KEM_KEYMEM_KB: float = (ML_KEM_512_PK + ML_KEM_512_SK + ML_KEM_512_CT) / 1024.0

# Stack headroom for SLH-DSA-128s verification (not generation) on an MCU.
_PQC_SIG_STACK_KB: float = 5.0

# Minimum total working memory for full PQC support (KEM + sig verification).
PQC_MIN_STACK_KB: float = _PQC_KEM_STACK_KB + _PQC_KEM_KEYMEM_KB + _PQC_SIG_STACK_KB

# Peak sustained power draw during SLH-DSA-128s signature *generation* on a
# Cortex-M4 at 48 MHz.  SLH-DSA-128s requires ~2 M hash evaluations; the
# device runs at near-100 % duty cycle for ~500 ms, yielding ~200 mW peak.
PQC_SIGN_POWER_PEAK_MW: float = 200.0

# ---------------------------------------------------------------------------
# Scoring threshold constants
# ---------------------------------------------------------------------------

_MAX_COMPLACENCY_GAP_YEARS: float = 10.0   # beyond 10-year overestimate → full score
_MAX_REVIEW_CADENCE_YEARS: float = 10.0    # beyond 10-year cadence → full permanence myth
_MAX_SWAP_DAYS: float = 365.0              # beyond 365 days to swap algo → full rigidity

# ---------------------------------------------------------------------------
# Named bottlenecks and strategic hurdles
# ---------------------------------------------------------------------------

STRATEGIC_HURDLES: Tuple[str, ...] = (
    "harvest_now_decrypt_later_exposure",   # HNDL: retrospective vulnerability
    "governance_executive_blindspot",        # crypto as IT chore vs exec risk
    "algorithm_permanence_myth",             # belief PQC algos are permanent
)

BOTTLENECK_ORDER: Tuple[str, ...] = (
    "cryptographic_blindspot",          # unknown RSA/ECC inventory
    "key_size_performance_bloat",       # PQC size explosion
    "supply_chain_dependency",          # vendor cascade failure
    "hybrid_protocol_complexity",       # dual TLS/SSH/VPN overhead
    "iot_embedded_constraints",         # memory/power limits on edge
    "migration_timeline_complacency",   # overconfidence in 2029+ timeline
    "talent_expertise_shortage",        # PQC engineers scarce
    "crypto_agility_readiness",         # lack of swappable crypto
)

# ---------------------------------------------------------------------------
# Scenario dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class CryptoTransitionScenario:
    """Measured or assumed inputs that fully characterise one PQC migration scenario.

    All fraction fields are in [0.0, 1.0] unless the docstring says otherwise.
    Byte-count fields use SI bytes; memory is in KB; power in mW; time in years
    or days as noted.
    """

    # ── Strategic hurdle fields ──────────────────────────────────────────────

    secret_longevity_years: float
    """Years that sensitive data must remain confidential from ``CURRENT_YEAR``."""

    quantum_threat_year: int
    """Pessimistic year a cryptographically-relevant quantum computer (CRQC) arrives."""

    data_sensitivity_level: float
    """Data classification: 0.0 = public information, 1.0 = top-secret equivalent."""

    crypto_in_exec_risk_reports: bool
    """True if cryptographic risk is formally tracked in executive risk registers."""

    crypto_agility_policy_exists: bool
    """True if a formal, enforced crypto-agility policy document exists."""

    pqc_algorithm_review_cadence_years: float
    """How frequently PQC algorithm choices are formally re-evaluated (years)."""

    # ── Bottleneck fields ────────────────────────────────────────────────────

    systems_audited: int
    """Number of systems with a completed cryptographic inventory."""

    total_systems: int
    """Total in-scope systems requiring PQC migration assessment."""

    avg_system_age_years: float
    """Mean age of in-scope systems; older systems are harder to inventory."""

    network_bandwidth_available_gbps: float
    """Available backbone network bandwidth (Gbps) today."""

    network_bandwidth_required_gbps: float
    """Required bandwidth after PQC migration (Gbps); must account for PQC overhead
    (see :func:`kem_bloat_ratio` ≈ 35.5× and :func:`signature_bloat_ratio` ≈ 41.0×)."""

    iot_available_memory_kb: float
    """Available RAM on representative IoT/embedded devices (KB).
    Use 256.0 for medium-constrained devices (Cortex-M4 class)."""

    iot_power_budget_mw: float
    """Peak power budget available for cryptographic operations on IoT/embedded (mW)."""

    vendor_readiness_fractions: Tuple[float, ...]
    """PQC readiness 0.0–1.0 for each critical vendor in the supply chain.
    Typically 3–8 vendors; default scenario uses 5."""

    simultaneous_protocol_versions: int
    """Number of protocol versions concurrently deployed during hybrid migration
    (e.g. TLS 1.2 + TLS 1.3 + TLS 1.3+ML-KEM = 3)."""

    assumed_crqc_threat_year: int
    """Year the organisation uses internally for CRQC threat planning.
    If this is later than ``quantum_threat_year``, complacency is active."""

    pqc_skilled_engineers: int
    """Engineers with verified PQC expertise (lattice/hash-based cryptography)."""

    required_pqc_engineers: int
    """Engineers required to execute full migration on schedule."""

    can_swap_algo_without_code_change: bool
    """True if the architecture allows algorithm substitution without source changes
    (crypto-agility architectural property)."""

    time_to_swap_algo_days: float
    """Elapsed calendar days to replace a cryptographic algorithm in production,
    end-to-end including testing and deployment."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _validate_fraction(name: str, value: float) -> None:
    if not (0.0 <= value <= 1.0):
        raise ValueError(f"{name} must be in [0, 1], got {value!r}")


def _validate_positive(name: str, value: float) -> None:
    if value <= 0:
        raise ValueError(f"{name} must be > 0, got {value!r}")


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0:
        raise ValueError(f"{name} must be >= 0, got {value!r}")


def ratio_deficit(actual: float, target: float) -> float:
    """Normalised shortfall: ``max(0, 1 - actual/target)``, clamped to [0, 1].

    Returns 0.0 when ``actual >= target`` (no gap) and approaches 1.0 as
    ``actual`` approaches zero relative to ``target``.
    """
    _validate_non_negative("actual", actual)
    _validate_positive("target", target)
    return _clamp01(1.0 - actual / target)


# ---------------------------------------------------------------------------
# Key-size bloat helpers — exact NIST FIPS numbers
# ---------------------------------------------------------------------------


def kem_bloat_ratio() -> float:
    """Byte-count ratio of ML-KEM-768 (PK + CT) vs X25519 (PK × 2).

    ML-KEM-768 is the NIST-recommended general-purpose KEM.  X25519 is the
    dominant classical ephemeral key-exchange primitive in TLS 1.3.

    A TLS handshake's key-exchange bytes grow by approximately this factor
    when migrating from ECDH to ML-KEM.

        (ML_KEM_768_PK + ML_KEM_768_CT) / (ECDH_X25519_PK * 2)
        = (1184 + 1088) / (32 * 2)
        = 2272 / 64
        ≈ 35.5

    Returns:
        float: approximately 35.5
    """
    pqc_bytes = ML_KEM_768_PK + ML_KEM_768_CT        # 2272 bytes
    classical_bytes = ECDH_X25519_PK * 2              # 64 bytes
    return pqc_bytes / classical_bytes


def signature_bloat_ratio() -> float:
    """Byte-count ratio of ML-DSA-65 (PK + SIG) vs ECDSA-P256 (PK + SIG).

    ML-DSA-65 is the NIST-recommended signature scheme for most enterprise use
    cases (NIST security level 3).  ECDSA-P256 is the dominant classical scheme.

        (ML_DSA_65_PK + ML_DSA_65_SIG) / (ECDSA_256_PK + ECDSA_256_SIG)
        = (1952 + 3293) / (64 + 64)
        = 5245 / 128
        ≈ 41.0

    Returns:
        float: approximately 41.0
    """
    pqc_bytes = ML_DSA_65_PK + ML_DSA_65_SIG          # 5245 bytes
    classical_bytes = ECDSA_256_PK + ECDSA_256_SIG     # 128 bytes
    return pqc_bytes / classical_bytes


# ---------------------------------------------------------------------------
# Bottleneck score functions — 0.0 = no gap; 1.0 = fully blocked
# ---------------------------------------------------------------------------


def cryptographic_blindspot_score(scenario: CryptoTransitionScenario) -> float:
    """Inventory gap: extent of unknown RSA/ECC usage across the estate.

    Audit coverage is penalised for system age via a PHI0-derived decay:
    older systems are harder to reach and more likely to harbour shadow
    cryptographic dependencies (e.g. hardcoded TLS stacks in appliances).

    Formula::

        age_decay      = PHI0 ** (avg_system_age_years / 10)
        audit_fraction = systems_audited / total_systems
        gap            = 1 - audit_fraction * age_decay

    At age 0 the decay factor is 1.0 (full credit); at 10 years it is
    PHI0 ≈ 0.739; at 20 years it is PHI0² ≈ 0.546.

    Returns:
        float in [0.0, 1.0].
    """
    if scenario.total_systems <= 0:
        raise ValueError("total_systems must be > 0")
    if not (0 <= scenario.systems_audited <= scenario.total_systems):
        raise ValueError("systems_audited must be in [0, total_systems]")
    _validate_non_negative("avg_system_age_years", scenario.avg_system_age_years)

    audit_fraction = scenario.systems_audited / scenario.total_systems
    age_decay = PHI0 ** (scenario.avg_system_age_years / 10.0)
    effective_coverage = audit_fraction * age_decay
    return _clamp01(1.0 - effective_coverage)


def key_size_bloat_score(scenario: CryptoTransitionScenario) -> float:
    """Key / signature size explosion: bandwidth exhaustion after PQC migration.

    The ``network_bandwidth_required_gbps`` field should already incorporate the
    PQC size overhead.  Use :func:`kem_bloat_ratio` (≈ 35.5×) and
    :func:`signature_bloat_ratio` (≈ 41.0×) to derive the PQC-adjusted
    requirement from current traffic volumes.

    Score = ``ratio_deficit(available, required)``.

    Returns:
        float in [0.0, 1.0].
    """
    _validate_positive(
        "network_bandwidth_required_gbps", scenario.network_bandwidth_required_gbps
    )
    _validate_non_negative(
        "network_bandwidth_available_gbps", scenario.network_bandwidth_available_gbps
    )
    return ratio_deficit(
        scenario.network_bandwidth_available_gbps,
        scenario.network_bandwidth_required_gbps,
    )


def supply_chain_cascade_score(scenario: CryptoTransitionScenario) -> float:
    """Vendor PQC readiness gap: probability at least one critical vendor fails.

    Models supply-chain risk as a *series reliability system*: the entire
    chain succeeds only when every vendor is PQC-ready.

    Formula::

        P(at least one failure) = 1 - prod(vendor_readiness_i)

    With five vendors at readiness (0.3, 0.5, 0.4, 0.6, 0.2) the product
    is 0.0072, giving a gap of ≈ 0.993 — a very high cascade risk.

    Returns:
        float in [0.0, 1.0].
    """
    if not scenario.vendor_readiness_fractions:
        raise ValueError("vendor_readiness_fractions must be non-empty")
    for i, v in enumerate(scenario.vendor_readiness_fractions):
        _validate_fraction(f"vendor_readiness_fractions[{i}]", v)

    product = 1.0
    for v in scenario.vendor_readiness_fractions:
        product *= v
    return _clamp01(1.0 - product)


def hybrid_protocol_complexity_score(scenario: CryptoTransitionScenario) -> float:
    """Dual-stack overhead: running hybrid classical+PQC TLS/SSH/VPN concurrently.

    During migration organisations must maintain multiple protocol versions
    simultaneously (e.g. TLS 1.2, TLS 1.3, TLS 1.3+ML-KEM).  Each additional
    version adds operational complexity, certificate management burden, and
    potential downgrade-attack surface.

    The K_CS denominator (5² + 7² = 74, the braided-winding resonance constant)
    naturally normalises scores so that the realistic enterprise range of 2–10
    simultaneous versions maps to approximately 0.07–0.61.

    Formula::

        gap = clamp(N_W * (versions - 1) / K_CS, 0, 1)

    Returns:
        float in [0.0, 1.0].
    """
    if scenario.simultaneous_protocol_versions < 1:
        raise ValueError("simultaneous_protocol_versions must be >= 1")
    raw = N_W * (scenario.simultaneous_protocol_versions - 1) / K_CS
    return _clamp01(raw)


def iot_constraint_score(scenario: CryptoTransitionScenario) -> float:
    """IoT / embedded PQC feasibility gap: memory and power constraints.

    **Memory gap** — ML-KEM-512 stack + key material + SLH-DSA-128s
    verification stack totals ``PQC_MIN_STACK_KB`` ≈ 13.6 KB.
    Deeply-embedded 8 KB MCUs fail immediately; 256 KB devices pass.

    **Power gap** — SLH-DSA-128s signature *generation* peaks at
    ``PQC_SIGN_POWER_PEAK_MW`` ≈ 200 mW on a Cortex-M4 at 48 MHz.
    Battery-powered sensors with 50 mW budgets face a severe power gap.

    Combined score::

        0.30 * memory_gap + 0.70 * power_gap

    The power component is weighted higher because SLH-DSA power demands
    exceed memory demands on typical constrained hardware.

    Returns:
        float in [0.0, 1.0].
    """
    _validate_positive("iot_available_memory_kb", scenario.iot_available_memory_kb)
    _validate_positive("iot_power_budget_mw", scenario.iot_power_budget_mw)

    memory_gap = ratio_deficit(scenario.iot_available_memory_kb, PQC_MIN_STACK_KB)
    power_gap = ratio_deficit(scenario.iot_power_budget_mw, PQC_SIGN_POWER_PEAK_MW)
    return _clamp01(0.30 * memory_gap + 0.70 * power_gap)


def migration_complacency_score(scenario: CryptoTransitionScenario) -> float:
    """Timeline complacency: the organisation's planning horizon lags the real threat.

    If ``assumed_crqc_threat_year > quantum_threat_year`` the organisation will
    under-resource migration.  The gap is normalised by
    ``_MAX_COMPLACENCY_GAP_YEARS`` (10 years) so that a 10-year overestimate
    scores 1.0.

    Formula::

        gap = clamp((assumed - pessimistic) / 10, 0, 1)

    Returns:
        float in [0.0, 1.0].
    """
    raw_gap = scenario.assumed_crqc_threat_year - scenario.quantum_threat_year
    return _clamp01(max(0.0, raw_gap) / _MAX_COMPLACENCY_GAP_YEARS)


def talent_gap_score(scenario: CryptoTransitionScenario) -> float:
    """PQC engineer shortage: ratio of available to required expertise.

    Formula::

        gap = ratio_deficit(pqc_skilled_engineers, required_pqc_engineers)

    Returns:
        float in [0.0, 1.0].
    """
    if scenario.required_pqc_engineers <= 0:
        raise ValueError("required_pqc_engineers must be > 0")
    _validate_non_negative(
        "pqc_skilled_engineers", float(scenario.pqc_skilled_engineers)
    )
    return ratio_deficit(
        float(scenario.pqc_skilled_engineers),
        float(scenario.required_pqc_engineers),
    )


def crypto_agility_readiness_score(scenario: CryptoTransitionScenario) -> float:
    """Crypto-agility gap: inability to swap algorithms safely and quickly.

    Two components contribute equally (0.50 weight each):

    * **Architectural rigidity** — 1.0 if algorithm replacement requires source
      changes; 0.0 if it can be done via configuration or plugin swap.
    * **Time-to-swap penalty** — ``time_to_swap_algo_days / _MAX_SWAP_DAYS``
      (capped at 1.0).  ``_MAX_SWAP_DAYS`` = 365 days.

    Formula::

        gap = 0.50 * rigidity + 0.50 * (swap_days / 365)

    Returns:
        float in [0.0, 1.0].
    """
    _validate_non_negative("time_to_swap_algo_days", scenario.time_to_swap_algo_days)
    rigidity = 0.0 if scenario.can_swap_algo_without_code_change else 1.0
    time_penalty = _clamp01(scenario.time_to_swap_algo_days / _MAX_SWAP_DAYS)
    return _clamp01(0.50 * rigidity + 0.50 * time_penalty)


# ---------------------------------------------------------------------------
# Strategic hurdle score functions
# ---------------------------------------------------------------------------


def hndl_exposure_score(scenario: CryptoTransitionScenario) -> float:
    """Harvest-Now-Decrypt-Later (HNDL) retrospective vulnerability exposure.

    Adversaries harvesting ciphertext today can decrypt it the moment a CRQC
    becomes available.  HNDL is active whenever a CRQC is expected before the
    data's confidentiality period expires.

    Formula::

        time_to_crqc = quantum_threat_year - CURRENT_YEAR
        overlap      = secret_longevity_years - max(0, time_to_crqc)
        if overlap <= 0: score = 0          # no HNDL window
        else:
            overlap_fraction = min(1, overlap / secret_longevity_years)
            score = data_sensitivity_level * overlap_fraction

    Example (baseline): CRQC in 2030, data must stay secret 15 years →
    overlap = 15 − 4 = 11 years → fraction = 0.73 → score ≈ 0.51.

    Returns:
        float in [0.0, 1.0].
    """
    _validate_fraction("data_sensitivity_level", scenario.data_sensitivity_level)
    _validate_positive("secret_longevity_years", scenario.secret_longevity_years)

    time_to_crqc = scenario.quantum_threat_year - CURRENT_YEAR
    overlap = scenario.secret_longevity_years - max(0.0, float(time_to_crqc))
    if overlap <= 0.0:
        return 0.0
    overlap_fraction = min(1.0, overlap / scenario.secret_longevity_years)
    return _clamp01(scenario.data_sensitivity_level * overlap_fraction)


def governance_blindspot_score(scenario: CryptoTransitionScenario) -> float:
    """Executive governance gap: cryptography treated as IT chore vs board-level risk.

    Two binary indicators:

    * **60 % weight** — whether crypto risk appears in executive risk reports.
    * **40 % weight** — whether a formal crypto-agility policy exists.

    Formula::

        exec_gap   = 0.0 if crypto_in_exec_risk_reports else 1.0
        policy_gap = 0.0 if crypto_agility_policy_exists else 1.0
        score      = 0.60 * exec_gap + 0.40 * policy_gap

    Returns:
        float in [0.0, 1.0].
    """
    exec_gap = 0.0 if scenario.crypto_in_exec_risk_reports else 1.0
    policy_gap = 0.0 if scenario.crypto_agility_policy_exists else 1.0
    return _clamp01(0.60 * exec_gap + 0.40 * policy_gap)


def algorithm_permanence_risk_score(scenario: CryptoTransitionScenario) -> float:
    """Algorithm permanence myth: belief that today's NIST PQC selections are final.

    NIST itself expects continued cryptanalysis; organisations that infrequently
    review their PQC algorithm selections risk being caught by future breaks.
    The score rises with review cadence, saturating at
    ``_MAX_REVIEW_CADENCE_YEARS`` (10 years).

    Formula::

        score = clamp(cadence / 10, 0, 1)

    A 2-year review cadence → score = 0.20 (low risk).
    A 5-year cadence → score = 0.50 (moderate myth exposure).
    10+ year cadence → score = 1.0 (full permanence myth).

    Returns:
        float in [0.0, 1.0].
    """
    _validate_positive(
        "pqc_algorithm_review_cadence_years",
        scenario.pqc_algorithm_review_cadence_years,
    )
    return _clamp01(
        scenario.pqc_algorithm_review_cadence_years / _MAX_REVIEW_CADENCE_YEARS
    )


# ---------------------------------------------------------------------------
# Aggregate functions
# ---------------------------------------------------------------------------


def bottleneck_scores(scenario: CryptoTransitionScenario) -> Dict[str, float]:
    """Compute all 8 normalised bottleneck gap scores (0 = no gap, 1 = severe).

    Returns a dict whose keys match ``BOTTLENECK_ORDER``.
    """
    return {
        "cryptographic_blindspot": cryptographic_blindspot_score(scenario),
        "key_size_performance_bloat": key_size_bloat_score(scenario),
        "supply_chain_dependency": supply_chain_cascade_score(scenario),
        "hybrid_protocol_complexity": hybrid_protocol_complexity_score(scenario),
        "iot_embedded_constraints": iot_constraint_score(scenario),
        "migration_timeline_complacency": migration_complacency_score(scenario),
        "talent_expertise_shortage": talent_gap_score(scenario),
        "crypto_agility_readiness": crypto_agility_readiness_score(scenario),
    }


def strategic_hurdle_scores(scenario: CryptoTransitionScenario) -> Dict[str, float]:
    """Compute normalised scores for the 3 major strategic hurdles.

    Returns a dict whose keys match ``STRATEGIC_HURDLES``.
    """
    return {
        "harvest_now_decrypt_later_exposure": hndl_exposure_score(scenario),
        "governance_executive_blindspot": governance_blindspot_score(scenario),
        "algorithm_permanence_myth": algorithm_permanence_risk_score(scenario),
    }


def migration_readiness_index(scores: Dict[str, float]) -> float:
    """Aggregate a gap-score dict into a single migration readiness index.

    Formula::

        readiness = 1 - mean(gap_scores)

    All gaps are weighted equally.  The result is in [0.0, 1.0] where 1.0
    means no gaps remain and 0.0 means all gaps are maximal.

    Args:
        scores: A dict of ``{name: gap_value}`` pairs, each value in [0, 1].

    Returns:
        float in [0.0, 1.0].
    """
    if not scores:
        raise ValueError("scores dict must be non-empty")
    for name, val in scores.items():
        if not (0.0 <= val <= 1.0):
            raise ValueError(f"Score '{name}' = {val!r} is not in [0, 1]")
    mean_gap = sum(scores.values()) / len(scores)
    return _clamp01(1.0 - mean_gap)


def migration_readiness_report(
    scenario: CryptoTransitionScenario,
    strategic_weight: float = 0.45,
) -> Dict[str, object]:
    """Aggregate 3 strategic hurdles + 8 bottlenecks into a full migration report.

    Args:
        scenario: A :class:`CryptoTransitionScenario` instance.
        strategic_weight: Weight assigned to the strategic-hurdle mean when
            computing the overall gap (default 0.45).  Bottleneck mean receives
            weight ``1 - strategic_weight``.

    Returns a dict with keys:

    * ``hurdle_scores``           — per-hurdle gap values
    * ``bottleneck_scores``       — per-bottleneck gap values
    * ``strategic_gap_mean``      — mean gap across the 3 strategic hurdles
    * ``bottleneck_gap_mean``     — mean gap across the 8 bottlenecks
    * ``total_gap``               — weighted blend of hurdle + bottleneck means
    * ``readiness_index``         — ``1 - total_gap``
    * ``top_bottlenecks``         — top-5 bottlenecks ranked by severity
    * ``kem_bloat_ratio``         — ML-KEM-768 vs X25519 byte ratio (≈ 35.5)
    * ``signature_bloat_ratio``   — ML-DSA-65 vs ECDSA-P256 byte ratio (≈ 41.0)
    * ``nist_constants_summary``  — selected NIST FIPS byte-count constants
    """
    _validate_fraction("strategic_weight", strategic_weight)

    hurdles = strategic_hurdle_scores(scenario)
    bottlenecks = bottleneck_scores(scenario)

    hurdle_mean = sum(hurdles.values()) / len(hurdles)
    bottleneck_mean = sum(bottlenecks.values()) / len(bottlenecks)

    total_gap = (
        strategic_weight * hurdle_mean
        + (1.0 - strategic_weight) * bottleneck_mean
    )
    readiness = _clamp01(1.0 - total_gap)

    ranked: List[Tuple[str, float]] = sorted(
        bottlenecks.items(), key=lambda kv: kv[1], reverse=True
    )

    return {
        "hurdle_scores": hurdles,
        "bottleneck_scores": bottlenecks,
        "strategic_gap_mean": hurdle_mean,
        "bottleneck_gap_mean": bottleneck_mean,
        "total_gap": total_gap,
        "readiness_index": readiness,
        "top_bottlenecks": ranked[:5],
        "kem_bloat_ratio": kem_bloat_ratio(),
        "signature_bloat_ratio": signature_bloat_ratio(),
        "nist_constants_summary": {
            "ML_KEM_768_PK": ML_KEM_768_PK,
            "ML_KEM_768_CT": ML_KEM_768_CT,
            "ML_DSA_65_PK": ML_DSA_65_PK,
            "ML_DSA_65_SIG": ML_DSA_65_SIG,
            "SLH_DSA_128S_SIG": SLH_DSA_128S_SIG,
            "ECDH_X25519_PK": ECDH_X25519_PK,
            "ECDSA_256_SIG": ECDSA_256_SIG,
        },
    }


# ---------------------------------------------------------------------------
# Baseline enterprise scenario (Fortune-500, 2026)
# ---------------------------------------------------------------------------


def baseline_enterprise_scenario() -> CryptoTransitionScenario:
    """Return a representative 2026 Fortune-500 enterprise PQC migration scenario.

    The organisation modelled is a large financial-services or healthcare
    conglomerate with mixed-age infrastructure spanning on-premise data centres,
    public cloud, IoT sensors, and a diverse vendor ecosystem.

    Key assumptions and their sources
    ----------------------------------
    * ``quantum_threat_year=2030`` — pessimistic CRQC estimate per McKinsey
      (2022) and NIST IR 8547 (2023); organisations should plan for this window.
    * ``secret_longevity_years=15`` — typical retention for financial and
      health records under HIPAA / SEC regulations.
    * ``data_sensitivity_level=0.7`` — a mix of personal financial data,
      protected health information, and internal IP.
    * ``systems_audited=350`` of ``total_systems=2000`` — 17.5 % inventory
      completion is optimistic for a large enterprise in 2026 per CISA surveys.
    * ``vendor_readiness_fractions=(0.3, 0.5, 0.4, 0.6, 0.2)`` — five critical
      vendors (HSM vendor, TLS library maintainer, VPN provider, PKI CA,
      IoT firmware vendor) at realistic 2026 PQC readiness levels.
    * Required bandwidth: derived from ``kem_bloat_ratio()`` applied to the
      ~1 % of backbone traffic that is TLS handshake key material.
    * ``assumed_crqc_threat_year=2035`` — a common 2026 planning assumption
      that underestimates the pessimistic risk window.
    * ``pqc_skilled_engineers=12`` of ``required_pqc_engineers=40`` — a 70 %
      talent gap reflecting the global scarcity of lattice-cryptography expertise.
    """
    _base_bw_gbps = 10.0
    _handshake_fraction = 0.01  # ~1 % of backbone traffic is TLS key exchange
    _pqc_required_bw = _base_bw_gbps * (
        1.0 + _handshake_fraction * (kem_bloat_ratio() - 1.0)
    )  # ≈ 10.345 Gbps

    return CryptoTransitionScenario(
        # Strategic hurdle fields
        secret_longevity_years=15.0,
        quantum_threat_year=2030,
        data_sensitivity_level=0.7,
        crypto_in_exec_risk_reports=False,
        crypto_agility_policy_exists=False,
        pqc_algorithm_review_cadence_years=5.0,
        # Bottleneck fields
        systems_audited=350,
        total_systems=2000,
        avg_system_age_years=8.5,
        network_bandwidth_available_gbps=_base_bw_gbps,
        network_bandwidth_required_gbps=_pqc_required_bw,
        iot_available_memory_kb=256.0,
        iot_power_budget_mw=50.0,
        vendor_readiness_fractions=(0.3, 0.5, 0.4, 0.6, 0.2),
        simultaneous_protocol_versions=3,
        assumed_crqc_threat_year=2035,
        pqc_skilled_engineers=12,
        required_pqc_engineers=40,
        can_swap_algo_without_code_change=False,
        time_to_swap_algo_days=180.0,
    )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Print the baseline enterprise migration readiness report to stdout."""
    scenario = baseline_enterprise_scenario()
    report = migration_readiness_report(scenario)

    width = 70
    print("=" * width)
    print("Pillar 233 — Quantum-Safe Cryptography Transition Bottleneck")
    print("ADJACENT RESEARCH TRACK | Unitary Manifold v10.52")
    print("=" * width)

    print(
        f"\n  {'KEM bloat ratio  (ML-KEM-768 vs X25519):':<46}"
        f" {report['kem_bloat_ratio']:.2f}x"
    )
    print(
        f"  {'Sig bloat ratio  (ML-DSA-65 vs ECDSA-P256):':<46}"
        f" {report['signature_bloat_ratio']:.2f}x"
    )

    print("\n\u2500\u2500 Strategic Hurdles " + "\u2500" * (width - 20))
    for name, score in report["hurdle_scores"].items():
        bar = "\u2588" * int(score * 24)
        print(f"  {name:<46} {score:.3f}  {bar}")

    print("\n\u2500\u2500 Bottleneck Scores " + "\u2500" * (width - 20))
    for name, score in report["bottleneck_scores"].items():
        bar = "\u2588" * int(score * 24)
        print(f"  {name:<46} {score:.3f}  {bar}")

    print("\n\u2500\u2500 Aggregate " + "\u2500" * (width - 12))
    print(f"  {'Strategic hurdle mean:':<46} {report['strategic_gap_mean']:.3f}")
    print(f"  {'Bottleneck gap mean:':<46} {report['bottleneck_gap_mean']:.3f}")
    print(f"  {'Total gap:':<46} {report['total_gap']:.3f}")
    print(f"  {'Migration readiness index:':<46} {report['readiness_index']:.3f}")

    print("\n\u2500\u2500 Top 5 Bottlenecks by Severity " + "\u2500" * (width - 32))
    for rank, (name, score) in enumerate(report["top_bottlenecks"], 1):
        print(f"  {rank}. {name:<44} {score:.3f}")

    print("\n\u2500\u2500 NIST FIPS Constants Reference " + "\u2500" * (width - 31))
    for key, val in report["nist_constants_summary"].items():
        print(f"  {key:<46} {val} bytes")

    print("=" * width)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    # Framework constants
    "N_W",
    "K_CS",
    "C_S",
    "PHI0",
    "CURRENT_YEAR",
    # NIST FIPS 203 — ML-KEM
    "ML_KEM_512_PK",
    "ML_KEM_512_CT",
    "ML_KEM_512_SK",
    "ML_KEM_768_PK",
    "ML_KEM_768_CT",
    "ML_KEM_768_SK",
    "ML_KEM_1024_PK",
    "ML_KEM_1024_CT",
    "ML_KEM_1024_SK",
    # NIST FIPS 204 — ML-DSA
    "ML_DSA_44_PK",
    "ML_DSA_44_SIG",
    "ML_DSA_44_SK",
    "ML_DSA_65_PK",
    "ML_DSA_65_SIG",
    "ML_DSA_65_SK",
    "ML_DSA_87_PK",
    "ML_DSA_87_SIG",
    "ML_DSA_87_SK",
    # NIST FIPS 205 — SLH-DSA
    "SLH_DSA_128S_PK",
    "SLH_DSA_128S_SIG",
    "SLH_DSA_128F_PK",
    "SLH_DSA_128F_SIG",
    "SLH_DSA_256S_PK",
    "SLH_DSA_256S_SIG",
    # Classical baselines
    "RSA_2048_PK",
    "RSA_2048_SIG",
    "ECDSA_256_PK",
    "ECDSA_256_SIG",
    "ECDH_X25519_PK",
    # Derived IoT constants
    "PQC_MIN_STACK_KB",
    "PQC_SIGN_POWER_PEAK_MW",
    # Named collections
    "STRATEGIC_HURDLES",
    "BOTTLENECK_ORDER",
    # Dataclass
    "CryptoTransitionScenario",
    # Helpers
    "ratio_deficit",
    "kem_bloat_ratio",
    "signature_bloat_ratio",
    # Bottleneck score functions
    "cryptographic_blindspot_score",
    "key_size_bloat_score",
    "supply_chain_cascade_score",
    "hybrid_protocol_complexity_score",
    "iot_constraint_score",
    "migration_complacency_score",
    "talent_gap_score",
    "crypto_agility_readiness_score",
    # Strategic hurdle score functions
    "hndl_exposure_score",
    "governance_blindspot_score",
    "algorithm_permanence_risk_score",
    # Aggregates
    "bottleneck_scores",
    "strategic_hurdle_scores",
    "migration_readiness_index",
    "migration_readiness_report",
    # Scenarios
    "baseline_enterprise_scenario",
    # Entry point
    "main",
]


if __name__ == "__main__":
    main()
